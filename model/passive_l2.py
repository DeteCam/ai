"""Passive L2-only multi-timescale traffic feature extractor and classifiers for DeteCam G1.
Strictly uses ONLY L2 observable metadata (timestamp, frame length, device TX/RX direction) —
NO IP/TCP/UDP/DNS/payload inspection, NO active stimulus required (compatible with exam halls R3).

Implements models in AGENTS.md section 4 / SPEC-001 order:
  1. Simple rule baseline
  2. Logistic regression (linear)
  3. Shallow gradient-boosted trees
  4. Small 1-hidden-layer neural network (MLP)
"""
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_NAMES = [
    "tx_byte_ratio",
    "asym_byte_ratio",
    "asym_pkt_ratio",
    "log_dom_bps",
    "log_dom_pps",
    "dom_size_mean",
    "dom_size_std",
    "dom_size_cv",
    "dom_size_p50",
    "dom_size_p90",
    "dom_size_p95",
    "frac_large_gt1000",
    "frac_small_lt120",
    "rev_to_dom_size_ratio",
    "burst_rate_hz",
    "log_burst_bytes_mean",
    "burst_bytes_cv",
    "burst_pkts_mean",
    "iat_p50_ms",
    "iat_p90_ms",
    "iat_cv",
    "fft_peak_ratio",
    "fft_gop_band_frac",
    "active_sec_frac",
    "sec_rate_cv",
]


def extract_window_features(ts, sizes, is_tx, win_start, win_sec=30.0):
    """Extract 25 passive L2-only features from one time window of a single device.
    ts: float64 seconds (sorted), sizes: int32 bytes, is_tx: bool (True=device->network).
    """
    tx_mask = is_tx
    rx_mask = ~is_tx
    tx_bytes = float(sizes[tx_mask].sum())
    rx_bytes = float(sizes[rx_mask].sum())
    tot_bytes = tx_bytes + rx_bytes
    tx_pkts = int(tx_mask.sum())
    rx_pkts = int(rx_mask.sum())
    tot_pkts = tx_pkts + rx_pkts

    tx_byte_ratio = tx_bytes / (tot_bytes + 1.0)
    asym_byte_ratio = max(tx_bytes, rx_bytes) / (tot_bytes + 1.0)
    asym_pkt_ratio = max(tx_pkts, rx_pkts) / (tot_pkts + 1.0)

    # Dominant direction (handles both STA uplink ToDS=1 and SoftAP camera FromDS=1)
    dom_mask = tx_mask if tx_bytes >= rx_bytes else rx_mask
    rev_mask = ~dom_mask
    dom_ts = ts[dom_mask]
    dom_sz = sizes[dom_mask].astype(np.float64)
    rev_sz = sizes[rev_mask].astype(np.float64)

    dom_bytes = float(dom_sz.sum())
    dom_pkts = len(dom_sz)
    if dom_pkts < 2:
        return None

    dom_mean = float(np.mean(dom_sz))
    dom_std = float(np.std(dom_sz))
    dom_cv = dom_std / (dom_mean + 1e-6)
    dom_p50, dom_p90, dom_p95 = [float(x) for x in np.percentile(dom_sz, [50, 90, 95])]
    frac_large = float(np.mean(dom_sz > 1000.0))
    frac_small = float(np.mean(dom_sz < 120.0))
    rev_mean = float(np.mean(rev_sz)) if len(rev_sz) > 0 else 0.0
    rev_to_dom = rev_mean / (dom_mean + 1.0)

    # Sub-second IAT and frame-burst reconstruction (gap >= 20 ms starts a new frame burst)
    iats = np.diff(dom_ts)
    iats = np.maximum(iats, 0.0)
    iat_ms = iats * 1000.0
    iat_p50 = float(np.percentile(iat_ms, 50))
    iat_p90 = float(np.percentile(iat_ms, 90))
    iat_cv = float(np.std(iat_ms) / (np.mean(iat_ms) + 1e-6))

    splits = np.where(iats >= 0.020)[0] + 1
    starts = np.concatenate([[0], splits])
    ends = np.concatenate([splits, [dom_pkts]])
    burst_bytes = np.add.reduceat(dom_sz, starts)
    burst_pkts = (ends - starts).astype(np.float64)
    burst_rate_hz = float(len(burst_bytes) / win_sec)
    burst_bytes_mean = float(np.mean(burst_bytes))
    burst_bytes_cv = float(np.std(burst_bytes) / (burst_bytes_mean + 1e-6))
    burst_pkts_mean = float(np.mean(burst_pkts))

    # 100 ms byte-rate FFT (GOP / frame cadence periodicity vs aperiodic bulk upload)
    n_bins = int(round(win_sec * 10))
    rel = np.clip(((dom_ts - win_start) * 10.0).astype(np.int32), 0, n_bins - 1)
    rate_100ms = np.bincount(rel, weights=dom_sz, minlength=n_bins).astype(np.float64)
    x = (rate_100ms - np.mean(rate_100ms)) * np.hanning(n_bins)
    spec = np.abs(np.fft.rfft(x)) ** 2
    freqs = np.fft.rfftfreq(n_bins, d=0.1)
    if len(spec) > 2 and np.sum(spec[1:]) > 0:
        fft_peak_ratio = float(np.max(spec[1:]) / (np.mean(spec[1:]) + 1e-12))
        gop_mask = (freqs >= 0.2) & (freqs <= 3.0)
        fft_gop_band_frac = float(np.sum(spec[gop_mask]) / (np.sum(spec[1:]) + 1e-12))
    else:
        fft_peak_ratio = 0.0
        fft_gop_band_frac = 0.0

    # 1-second temporal continuity
    n_sec = int(round(win_sec))
    rel_s = np.clip((dom_ts - win_start).astype(np.int32), 0, n_sec - 1)
    rate_1s = np.bincount(rel_s, weights=dom_sz, minlength=n_sec).astype(np.float64)
    active_sec_frac = float(np.mean(rate_1s > 0.0))
    sec_rate_cv = float(np.std(rate_1s) / (np.mean(rate_1s) + 1e-6))

    return np.array([
        tx_byte_ratio,
        asym_byte_ratio,
        asym_pkt_ratio,
        np.log1p(dom_bytes / win_sec),
        np.log1p(dom_pkts / win_sec),
        dom_mean,
        dom_std,
        dom_cv,
        dom_p50,
        dom_p90,
        dom_p95,
        frac_large,
        frac_small,
        rev_to_dom,
        burst_rate_hz,
        np.log1p(burst_bytes_mean),
        burst_bytes_cv,
        burst_pkts_mean,
        iat_p50,
        iat_p90,
        iat_cv,
        fft_peak_ratio,
        fft_gop_band_frac,
        active_sec_frac,
        sec_rate_cv,
    ], dtype=np.float64)


class RuleBaselineClassifier:
    """Simple transparent traffic-physics rule baseline (no ML training; threshold tuned only on train fold)."""
    def __init__(self):
        self.best_thr = 0.5

    @staticmethod
    def _raw_score(X):
        idx = {name: i for i, name in enumerate(FEATURE_NAMES)}
        tx_r = X[:, idx["tx_byte_ratio"]]
        bps = np.expm1(X[:, idx["log_dom_bps"]])
        rev_dom = X[:, idx["rev_to_dom_size_ratio"]]
        act = X[:, idx["active_sec_frac"]]
        mean_sz = X[:, idx["dom_size_mean"]]
        # Camera score: sustained uplink-heavy stream with large frames and small reverse ACKs
        s = (
            1.5 * np.clip((tx_r - 0.55) / 0.35, 0.0, 1.0)
            + 1.0 * np.clip((np.log1p(bps) - np.log1p(1500.0)) / 3.0, 0.0, 1.0)
            + 1.0 * np.clip((0.55 - rev_dom) / 0.40, 0.0, 1.0)
            + 0.8 * np.clip((act - 0.25) / 0.50, 0.0, 1.0)
            + 0.7 * np.clip((mean_sz - 250.0) / 700.0, 0.0, 1.0)
        ) / 5.0
        return s

    def fit(self, X, y):
        scores = self._raw_score(X)
        best_j = -1.0
        for thr in np.linspace(0.25, 0.85, 61):
            pred = scores >= thr
            tp = np.sum(pred & (y == 1))
            fn = np.sum((~pred) & (y == 1))
            fp = np.sum(pred & (y == 0))
            tn = np.sum((~pred) & (y == 0))
            rec = tp / max(tp + fn, 1)
            fpr = fp / max(fp + tn, 1)
            j = rec - 1.5 * fpr  # prioritize low FPR alongside high recall
            if j > best_j:
                best_j = j
                self.best_thr = float(thr)
        return self

    def predict_proba(self, X):
        p = np.clip(self._raw_score(X), 0.0, 1.0)
        return np.stack([1.0 - p, p], axis=1)

    def predict(self, X):
        return (self._raw_score(X) >= self.best_thr).astype(int)


def make_candidate_models(seed=42):
    """Return ordered candidate models per SPEC-001 section 4 (Rule -> Logistic -> GBDT -> Small MLP)."""
    return {
        "Rule-Baseline": RuleBaselineClassifier(),
        "LogisticRegression": Pipeline([
            ("sc", StandardScaler()),
            ("clf", LogisticRegression(C=0.3, class_weight="balanced", max_iter=1000, random_state=seed)),
        ]),
        "HistGBDT-Shallow": HistGradientBoostingClassifier(
            max_depth=3, max_iter=80, learning_rate=0.06, min_samples_leaf=20,
            l2_regularization=2.0, class_weight="balanced", random_state=seed,
        ),
        "SmallMLP": Pipeline([
            ("sc", StandardScaler()),
            ("clf", MLPClassifier(
                hidden_layer_sizes=(32,), alpha=0.5, max_iter=300,
                early_stopping=True, random_state=seed,
            )),
        ]),
    }
