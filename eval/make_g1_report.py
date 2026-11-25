"""Generate Korean public-dataset real-device LODO baseline report from eval/results_public_lodo.json.
Usage:
  python3 eval/make_g1_report.py
"""
import json
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
IN_JSON = os.path.join(THIS_DIR, "results_public_lodo.json")
OUT_MD = os.path.join(THIS_DIR, "PUBLIC_LODO_RESULTS_20261125.md")


def main():
    with open(IN_JSON, "r", encoding="utf-8") as f:
        R = json.load(f)

    L = []
    L.append("# 공개 실측 데이터(L2 마스킹) 기기 분리(LODO) 카메라 판별 사전 기준선 (2026-11-25)")
    L.append("")
    L.append("> **중요 고지 ([docs/AGENTS.md](https://github.com/DeteCam/docs/blob/main/AGENTS.md) 7.2절 · [ai/AGENTS.md](../AGENTS.md) 1~2번)**")
    L.append("> - 이 결과는 공개 실측 이더넷 PCAP(**UNSW IoT Traces 2019** + **Deakin IoT Traffic Dataset 2025**)에서 IP/TCP/UDP/페이로드를 **모두 가리고 L2(시각 · 프레임 길이 · 방향)만** 남겨 평가한 **V2 이전 사전 검증 기준선**이다.")
    L.append("> - **최종 G1 합격 근거가 아니다.** 이더넷 캡처에는 802.11 PHY 능력(`rateNflag` 1T1R/2T2R, 20/80 MHz, LAA MAC)과 현대 모바일 라이브 방송 · 카카오톡 영상통화 · 2.4/5 GHz 대역 분리가 없으므로, 최종 G1 합격 판정은 반드시 **AX210 모니터 모드 실제 기기 캡처(2.4 · 5 GHz 각 별도)**로 수행한다.")
    L.append("> - 원본 PCAP과 MAC 주소는 저장소에 올리지 않았으며([data/README.md](../data/README.md)), 학습과 평가에 같은 기기가 절대 섞이지 않는 **완전 기기 분리(Leave-One-Device-Out, LODO)** 및 **교차 데이터셋 전이**로만 평가했다.")
    L.append("")

    regime_meta = {
        "active_stream_ge30KB": ("1. 활성 송출 구간 (30초 창 ≥ 30 KB, 실시간 영상/업로드 감시 기준)", "30초 동안 30 KB 이상 통신이 발생한 활성 창만 평가 (카메라 7종 + 비카메라 16종 = 23종 실제 기기)."),
        "all_active_ge3KB": ("2. 저트래픽 · 간헐 구간 포함 전체 (30초 창 ≥ 3 KB)", "30초 동안 3 KB 이상 통신한 모든 창 포함 — 대기/간헐 스냅샷 구간의 재현율 하락을 숨기지 않고 확인."),
    }

    for rkey, (title, desc) in regime_meta.items():
        if rkey not in R:
            continue
        sec = R[rkey]
        L.append(f"## {title}")
        L.append("")
        L.append(desc)
        L.append("")
        L.append("### 1) 모델별 비교 (규칙 기준선 → 로지스틱 → 얕은 GBDT → 소형 MLP, AGENTS.md 4장)")
        L.append("")
        L.append("| 평가 분할 | 모델 | 창 재현율 | 창 오탐률 | ROC-AUC | 기기 단위 재현율 | 기기 단위 오탐률 |")
        L.append("|---|---|---|---|---|---|---|")
        for tag, skey in (
            ("UNSW 단독 LODO", "unsw_lodo"),
            ("Deakin 단독 LODO", "deakin_lodo"),
            ("**통합 LODO (UNSW+Deakin)**", "combined_lodo"),
            ("교차 전이 (UNSW→Deakin)", "unsw_to_deakin"),
            ("교차 전이 (Deakin→UNSW)", "deakin_to_unsw"),
        ):
            for mn, m in sec[skey].items():
                L.append(
                    f"| {tag} | `{mn}` | {m['window_recall']*100:.1f}% | {m['window_fpr']*100:.1f}% | "
                    f"{m['roc_auc']:.3f} | {m['device_recall']*100:.1f}% | {m['device_fpr']*100:.1f}% |"
                )
        L.append("")

        L.append("### 2) 기기별 상세 결과 (통합 LODO, `HistGBDT-Shallow`, MAC 비공개)")
        L.append("")
        L.append("| 구분 | 기기명 (데이터셋:모델) | 평가 창 수 | 카메라 판정 비율 | 평균 확률 | 기기 판정(≥50%) |")
        L.append("|---|---|---|---|---|---|")
        per_dev = sec["combined_lodo"]["HistGBDT-Shallow"]["per_device"]
        for dname, info in sorted(per_dev.items(), key=lambda kv: (-kv[1]["is_camera"], -kv[1]["pred_cam_rate"], kv[0])):
            cat = "카메라" if info["is_camera"] else "비카메라"
            ok = "탐지" if (info["is_camera"] and info["device_pred"]) else (
                "미탐" if info["is_camera"] else ("오탐" if info["device_pred"] else "정상")
            )
            L.append(
                f"| {cat} | `{dname}` | {info['n_windows']} | {info['pred_cam_rate']*100:.1f}% | "
                f"{info['mean_prob']:.3f} | **{ok}** |"
            )
        L.append("")

    L.append("## 3. 핵심 시사점 (실제 데이터에서 드러난 진실과 V5 실측 설계 지침)")
    L.append("")
    L.append("1. **소형 신경망(`SmallMLP`)은 기기 분리(LODO)에서 규칙 · 선형 · 얕은 GBDT보다 열세다 (AGENTS.md 4장 확인)**: 기기 수가 20~30종 수준일 때 MLP는 학습 기기에 과적합하여 새 기기에서 무너진다. 반면 정규화된 **`HistGBDT-Shallow`**와 **`LogisticRegression`**이 가장 일관되게 일반화되었다.")
    L.append("2. **학습 카메라 다양성이 절대적이다**: UNSW 단독 LODO(활성 카메라 3종뿐)에서는 1종을 빼면 학습에 2종만 남아 재현율이 붕괴했으나, 두 데이터셋을 합쳐 7종 카메라로 늘리자 활성 스트림 통합 LODO에서 **`HistGBDT-Shallow` 창 재현율 82.0% / 창 오탐률 4.5% / AUC 0.926, 기기 단위 재현율 100%(7/7)**까지 올라갔다. 따라서 V5 실측 수집 시 최소 **6~8종 이상의 서로 다른 카메라 모델**(연속 스트리밍 + 간헐 스냅샷, 2.4 & 5 GHz)을 확보해야 한다.")
    L.append("3. **저트래픽/대기 구간 및 단발 버스트 한계**: `all_active_ge3KB` 구간을 포함하면 대기·하트비트 창 때문에 재현율이 떨어지며, 단발 1~2창만 나타난 IoT 센서(`Withings Scale` `n=1`, `NEST Protect` `n=2`)가 오탐을 낸다 → 실전에서는 **최소 지속 시간(≥2~3창 누적) + 시험장 입실 전 기준선 비교**가 필수다.")
    L.append("4. **G1(95% / 5%) 달성을 위해 V5 AX210 실측에서 추가할 필수 특징**: 이더넷 L2 길이·비대칭성·FFT만으로도 활성 창 오탐률 4.5%·기기 재현율 100%에 근접했으나, 창 재현율 82% → 95%+를 넘고 모바일 라이브 방송·영상통화를 가르려면 AX210 모니터 모드에서만 얻을 수 있는 **802.11 PHY/MAC 능력 특징(`rateNflag` 1T1R/2T2R, 20/80 MHz, LAA MAC, SoftAP/핫스팟 허브 짝짓기)**을 결합해야 한다.")
    L.append("")
    L.append("## 4. 다시 돌리는 명령")
    L.append("")
    L.append("```bash")
    L.append("# UNSW IoT Traces (16-09-23, 16-09-24) 및 Deakin IoT (IoT_2023-07-11, IoT_2023-07-12)를 /tmp/detecam_public_data 아래에 배치한 뒤:")
    L.append("cd ai")
    L.append("OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python3 eval/public_lodo_baseline.py --data-root /tmp/detecam_public_data --out eval/results_public_lodo.json")
    L.append("python3 eval/make_g1_report.py")
    L.append("```")

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
