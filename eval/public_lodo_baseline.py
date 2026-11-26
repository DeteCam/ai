"""Public real-device PCAP device-disjoint (LODO) baseline evaluation for DeteCam G1.
Strictly obeys ai/AGENTS.md:
  1. Uses ONLY real-device captures (UNSW IoT Traces & Deakin IoT Traffic Dataset).
  2. Strict Leave-One-Device-Out (LODO) + Cross-Dataset Transfer evaluation (never shares devices across train/test).
  3. Compares simple rule baseline vs LogisticRegression vs shallow GBDT vs small MLP on identical splits.
  4. NEVER stores or prints raw MAC addresses; raw PCAPs remain outside git (e.g. /tmp/detecam_public_data).
  5. Clearly marks results as pre-V2 Ethernet L2-masked proxy (final G1 pass requires real AX210 2.4/5 GHz captures).

Usage:
  python3 eval/public_lodo_baseline.py --data-root /tmp/detecam_public_data --out eval/results_public_lodo.json
"""
import argparse
import csv
import json
import os
import sys
from collections import defaultdict
import dpkt
import numpy as np
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.passive_l2 import FEATURE_NAMES, extract_window_features, make_candidate_models


def _mac_str(b):
    return ":".join(f"{x:02x}" for x in b)


def load_unsw_device_map(list_path):
    """Parse UNSW List_Of_Devices.txt -> {mac_lower: (canonical_name, is_camera)}."""
    cameras_kw = ("camera", "dropcam", "smartcam", "netatmo welcome", "baby monitor")
    skip_kw = ("router", "gateway")
    mapping = {}
    with open(list_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = [p.strip() for p in line.strip().split("\t") if p.strip()]
            if len(parts) < 2:
                continue
            name, mac = parts[0], parts[1].lower()
            if len(mac) != 17 or mac.count(":") != 5:
                continue
            low = name.lower()
            if any(k in low for k in skip_kw):
                continue
            is_cam = any(k in low for k in cameras_kw)
            # Disambiguate multiple Android phones / Insteon cameras cleanly without exposing MAC
            canonical = f"unsw:{name}"
            if canonical in [v[0] for v in mapping.values()]:
                canonical = f"{canonical}_{len(mapping)}"
            mapping[mac] = (canonical, int(is_cam))
    return mapping


def load_deakin_device_map(csv_path):
    """Parse Deakin macAddresses.csv -> {mac_lower: (canonical_name, is_camera)}."""
    cameras_kw = ("camera", "smart cam", "doorbell", "smartdoor bell")
    mapping = {}
    with open(csv_path, "r", encoding="utf-8-sig", errors="ignore") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for idx, row in enumerate(reader):
            if len(row) < 2:
                continue
            mac = row[0].strip().lower()
            name = row[1].strip()
            if len(mac) != 17 or mac.count(":") != 5:
                continue
            low = name.lower()
            is_cam = any(k in low for k in cameras_kw)
            canonical = f"deakin:{name}"
            if canonical in [v[0] for v in mapping.values()]:
                canonical = f"{canonical}_{idx}"
            mapping[mac] = (canonical, int(is_cam))
    return mapping


def extract_windows_from_pcaps(pcap_paths, mac_map, win_sec=30.0, stride_sec=30.0, min_pkts=15, min_bytes=5000):
    """Stream-parse Ethernet PCAPs using ONLY L2 timestamps, frame sizes, and TX/RX direction.
    Strictly discards IP/TCP/UDP/payload bytes. Never retains MAC addresses after mapping to device ID.
    """
    # Collect compact per-device packet arrays: device_name -> list of (ts, size, is_tx)
    dev_pkts = defaultdict(list)
    total_parsed = 0
    for ppath in pcap_paths:
        if not os.path.exists(ppath):
            continue
        with open(ppath, "rb") as f:
            try:
                pcap = dpkt.pcap.Reader(f)
            except Exception:
                f.seek(0)
                pcap = dpkt.pcapng.Reader(f)
            for ts, buf in pcap:
                if len(buf) < 14:
                    continue
                dst = _mac_str(buf[0:6])
                src = _mac_str(buf[6:12])
                plen = len(buf)
                total_parsed += 1
                if src in mac_map:
                    dev_pkts[mac_map[src][0]].append((ts, plen, 1))
                if dst in mac_map:
                    dev_pkts[mac_map[dst][0]].append((ts, plen, 0))

    label_by_dev = {name: lbl for name, lbl in mac_map.values()}
    X_list, y_list, dev_list, bytes_list = [], [], [], []

    for dev_name, pkts in sorted(dev_pkts.items()):
        if len(pkts) < min_pkts:
            continue
        arr = np.array(pkts, dtype=np.float64)
        order = np.argsort(arr[:, 0])
        ts = arr[order, 0]
        sz = arr[order, 1].astype(np.int32)
        tx = arr[order, 2] > 0.5

        t0 = ts[0]
        t_end = ts[-1]
        # Efficiently slice consecutive windows using searchsorted
        w_starts = np.arange(t0, max(t_end - win_sec + 1e-6, t0 + 1e-6), stride_sec)
        i_starts = np.searchsorted(ts, w_starts, side="left")
        i_ends = np.searchsorted(ts, w_starts + win_sec, side="left")

        for ws, i0, i1 in zip(w_starts, i_starts, i_ends):
            if i1 - i0 < min_pkts:
                continue
            w_bytes = int(sz[i0:i1].sum())
            if w_bytes < min_bytes:
                continue
            feat = extract_window_features(ts[i0:i1], sz[i0:i1], tx[i0:i1], ws, win_sec=win_sec)
            if feat is None or not np.all(np.isfinite(feat)):
                continue
            X_list.append(feat)
            y_list.append(label_by_dev[dev_name])
            dev_list.append(dev_name)
            bytes_list.append(w_bytes)

    if not X_list:
        return np.zeros((0, len(FEATURE_NAMES))), np.zeros(0, dtype=int), np.array([]), np.zeros(0)
    return np.vstack(X_list), np.array(y_list, dtype=int), np.array(dev_list), np.array(bytes_list)


def eval_lodo(X, y, devs, max_win_per_dev=250, seed=42):
    """Strict Leave-One-Device-Out (LODO) evaluation across all candidate models.
    Caps windows per device during training & testing so high-traffic devices do not swamp smaller ones.
    """
    rng = np.random.default_rng(seed)
    keep_idx = []
    for d in sorted(set(devs)):
        idx = np.where(devs == d)[0]
        if len(idx) > max_win_per_dev:
            idx = rng.choice(idx, max_win_per_dev, replace=False)
        keep_idx.append(np.sort(idx))
    keep_idx = np.concatenate(keep_idx)
    Xb, yb, db = X[keep_idx], y[keep_idx], devs[keep_idx]

    uniq_devs = sorted(set(db))
    results = {}
    for mname in make_candidate_models(seed=seed).keys():
        y_true_all, y_pred_all, y_prob_all, dev_all = [], [], [], []
        for test_dev in uniq_devs:
            te = db == test_dev
            tr = ~te
            if len(set(yb[tr])) < 2:
                continue
            clf = make_candidate_models(seed=seed)[mname]
            clf.fit(Xb[tr], yb[tr])
            prob = clf.predict_proba(Xb[te])[:, 1]
            pred = clf.predict(Xb[te])
            y_true_all.append(yb[te])
            y_pred_all.append(pred)
            y_prob_all.append(prob)
            dev_all.append(db[te])

        yt = np.concatenate(y_true_all)
        yp = np.concatenate(y_pred_all)
        ypr = np.concatenate(y_prob_all)
        da = np.concatenate(dev_all)

        pos = yt == 1
        neg = yt == 0
        win_recall = float(np.mean(yp[pos] == 1)) if np.any(pos) else float("nan")
        win_fpr = float(np.mean(yp[neg] == 1)) if np.any(neg) else float("nan")
        auc = float(roc_auc_score(yt, ypr)) if len(set(yt)) == 2 else float("nan")

        # Per-device metrics + device-level majority vote (represents screening a room over several windows)
        per_dev = {}
        dev_cam_hits, dev_cam_tot = 0, 0
        dev_neg_fp, dev_neg_tot = 0, 0
        for d in uniq_devs:
            m = da == d
            lbl = int(yt[m][0])
            pos_rate = float(np.mean(yp[m] == 1))
            mean_prob = float(np.mean(ypr[m]))
            per_dev[d] = dict(
                is_camera=lbl,
                n_windows=int(m.sum()),
                pred_cam_rate=round(pos_rate, 4),
                mean_prob=round(mean_prob, 4),
                device_pred=int(pos_rate >= 0.5),
            )
            if lbl == 1:
                dev_cam_tot += 1
                dev_cam_hits += int(pos_rate >= 0.5)
            else:
                dev_neg_tot += 1
                dev_neg_fp += int(pos_rate >= 0.5)

        results[mname] = dict(
            window_recall=round(win_recall, 4),
            window_fpr=round(win_fpr, 4),
            roc_auc=round(auc, 4),
            device_recall=round(dev_cam_hits / max(dev_cam_tot, 1), 4),
            device_fpr=round(dev_neg_fp / max(dev_neg_tot, 1), 4),
            n_cam_devices=dev_cam_tot,
            n_noncam_devices=dev_neg_tot,
            per_device=per_dev,
        )
    return results


def eval_cross_dataset(X_tr, y_tr, d_tr, X_te, y_te, d_te, max_win_per_dev=250, seed=42):
    """Train on one real-device dataset (e.g. UNSW), test on a completely different dataset (e.g. Deakin)."""
    rng = np.random.default_rng(seed)
    def _cap(X, y, d):
        ks = []
        for dn in sorted(set(d)):
            idx = np.where(d == dn)[0]
            if len(idx) > max_win_per_dev:
                idx = rng.choice(idx, max_win_per_dev, replace=False)
            ks.append(np.sort(idx))
        k = np.concatenate(ks)
        return X[k], y[k], d[k]

    X1, y1, _ = _cap(X_tr, y_tr, d_tr)
    X2, y2, d2 = _cap(X_te, y_te, d_te)
    out = {}
    for mname, clf in make_candidate_models(seed=seed).items():
        clf.fit(X1, y1)
        prob = clf.predict_proba(X2)[:, 1]
        pred = clf.predict(X2)
        pos, neg = y2 == 1, y2 == 0
        dev_cam_hits = sum(int(np.mean(pred[d2 == dn]) >= 0.5) for dn in set(d2[pos]))
        dev_neg_fp = sum(int(np.mean(pred[d2 == dn]) >= 0.5) for dn in set(d2[neg]))
        out[mname] = dict(
            window_recall=round(float(np.mean(pred[pos] == 1)), 4),
            window_fpr=round(float(np.mean(pred[neg] == 1)), 4),
            roc_auc=round(float(roc_auc_score(y2, prob)), 4),
            device_recall=round(dev_cam_hits / max(len(set(d2[pos])), 1), 4),
            device_fpr=round(dev_neg_fp / max(len(set(d2[neg])), 1), 4),
        )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default="/tmp/detecam_public_data")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_public_lodo.json"))
    args = ap.parse_args()

    unsw_map = load_unsw_device_map(os.path.join(args.data_root, "unsw", "List_Of_Devices.txt"))
    deakin_map = load_deakin_device_map(os.path.join(args.data_root, "deakin", "macAddresses.csv"))

    unsw_pcaps = [
        os.path.join(args.data_root, "unsw", "16-09-23.pcap"),
        os.path.join(args.data_root, "unsw", "16-09-24.pcap"),
    ]
    deakin_pcaps = [
        os.path.join(args.data_root, "deakin", "pcap", "IoT_2023-07-11.pcap"),
        os.path.join(args.data_root, "deakin", "pcap", "IoT_2023-07-12.pcap"),
    ]

    print("Parsing real-device PCAPs once (L2-only masking; raw MACs discarded immediately)...", flush=True)
    Xu0, yu0, du0, bu0 = extract_windows_from_pcaps(unsw_pcaps, unsw_map, win_sec=30.0, stride_sec=30.0, min_pkts=15, min_bytes=3000)
    Xd0, yd0, dd0, bd0 = extract_windows_from_pcaps(deakin_pcaps, deakin_map, win_sec=30.0, stride_sec=30.0, min_pkts=15, min_bytes=3000)

    summary = {}
    for regime_name, min_bytes in (("active_stream_ge30KB", 30000), ("all_active_ge3KB", 3000)):
        print(f"\n================ Regime: {regime_name} (30s window, >= {min_bytes} B) ================", flush=True)
        mu = bu0 >= min_bytes
        md = bd0 >= min_bytes
        Xu, yu, du = Xu0[mu], yu0[mu], du0[mu]
        Xd, yd, dd = Xd0[md], yd0[md], dd0[md]
        print(f"UNSW windows={len(Xu)} (cam={int(yu.sum())}, noncam={int((yu==0).sum())}, devs={len(set(du))})", flush=True)
        print(f"Deakin windows={len(Xd)} (cam={int(yd.sum())}, noncam={int((yd==0).sum())}, devs={len(set(dd))})", flush=True)

        res_u = eval_lodo(Xu, yu, du)
        res_d = eval_lodo(Xd, yd, dd)
        Xall = np.vstack([Xu, Xd])
        yall = np.concatenate([yu, yd])
        dall = np.concatenate([du, dd])
        res_all = eval_lodo(Xall, yall, dall)
        res_u2d = eval_cross_dataset(Xu, yu, du, Xd, yd, dd)
        res_d2u = eval_cross_dataset(Xd, yd, dd, Xu, yu, du)

        for tag, r in (("UNSW LODO", res_u), ("Deakin LODO", res_d), ("Combined LODO", res_all), ("UNSW->Deakin", res_u2d), ("Deakin->UNSW", res_d2u)):
            print(f"\n--- {tag} ---", flush=True)
            for mn, m in r.items():
                print(
                    f"  {mn:20s} | win Rec={m['window_recall']*100:5.1f}% FPR={m['window_fpr']*100:5.1f}% AUC={m['roc_auc']:.3f} "
                    f"| dev Rec={m['device_recall']*100:5.1f}% FPR={m['device_fpr']*100:5.1f}%",
                    flush=True,
                )

        print("\n--- Per-Device Breakdown (Combined LODO, HistGBDT-Shallow) ---", flush=True)
        for dname, info in sorted(res_all["HistGBDT-Shallow"]["per_device"].items(), key=lambda kv: (-kv[1]["is_camera"], kv[0])):
            tag_c = "CAM   " if info["is_camera"] else "NONCAM"
            print(f"  [{tag_c}] {dname:42s} | n={info['n_windows']:3d} | pred_cam={info['pred_cam_rate']*100:5.1f}% | mean_p={info['mean_prob']:.3f}", flush=True)

        summary[regime_name] = dict(
            unsw_lodo=res_u,
            deakin_lodo=res_d,
            combined_lodo=res_all,
            unsw_to_deakin=res_u2d,
            deakin_to_unsw=res_d2u,
        )

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nSaved LODO results to {args.out}", flush=True)


if __name__ == "__main__":
    main()
