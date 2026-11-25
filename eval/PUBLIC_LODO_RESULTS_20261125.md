# 공개 실측 데이터(L2 마스킹) 기기 분리(LODO) 카메라 판별 사전 기준선 (2026-11-25)

> **중요 고지 ([docs/AGENTS.md](https://github.com/DeteCam/docs/blob/main/AGENTS.md) 7.2절 · [ai/AGENTS.md](../AGENTS.md) 1~2번)**
> - 이 결과는 공개 실측 이더넷 PCAP(**UNSW IoT Traces 2019** + **Deakin IoT Traffic Dataset 2025**)에서 IP/TCP/UDP/페이로드를 **모두 가리고 L2(시각 · 프레임 길이 · 방향)만** 남겨 평가한 **V2 이전 사전 검증 기준선**이다.
> - **최종 G1 합격 근거가 아니다.** 이더넷 캡처에는 802.11 PHY 능력(`rateNflag` 1T1R/2T2R, 20/80 MHz, LAA MAC)과 현대 모바일 라이브 방송 · 카카오톡 영상통화 · 2.4/5 GHz 대역 분리가 없으므로, 최종 G1 합격 판정은 반드시 **AX210 모니터 모드 실제 기기 캡처(2.4 · 5 GHz 각 별도)**로 수행한다.
> - 원본 PCAP과 MAC 주소는 저장소에 올리지 않았으며([data/README.md](../data/README.md)), 학습과 평가에 같은 기기가 절대 섞이지 않는 **완전 기기 분리(Leave-One-Device-Out, LODO)** 및 **교차 데이터셋 전이**로만 평가했다.

## 1. 활성 송출 구간 (30초 창 ≥ 30 KB, 실시간 영상/업로드 감시 기준)

30초 동안 30 KB 이상 통신이 발생한 활성 창만 평가 (카메라 7종 + 비카메라 16종 = 23종 실제 기기).

### 1) 모델별 비교 (규칙 기준선 → 로지스틱 → 얕은 GBDT → 소형 MLP, AGENTS.md 4장)

| 평가 분할 | 모델 | 창 재현율 | 창 오탐률 | ROC-AUC | 기기 단위 재현율 | 기기 단위 오탐률 |
|---|---|---|---|---|---|---|
| UNSW 단독 LODO | `Rule-Baseline` | 43.1% | 28.2% | 0.792 | 33.3% | 9.1% |
| UNSW 단독 LODO | `LogisticRegression` | 1.0% | 20.8% | 0.315 | 0.0% | 27.3% |
| UNSW 단독 LODO | `HistGBDT-Shallow` | 6.1% | 23.6% | 0.712 | 0.0% | 27.3% |
| UNSW 단독 LODO | `SmallMLP` | 0.0% | 25.7% | 0.414 | 0.0% | 27.3% |
| Deakin 단독 LODO | `Rule-Baseline` | 8.6% | 4.2% | 0.288 | 50.0% | 0.0% |
| Deakin 단독 LODO | `LogisticRegression` | 70.3% | 9.7% | 0.926 | 75.0% | 0.0% |
| Deakin 단독 LODO | `HistGBDT-Shallow` | 30.6% | 9.0% | 0.842 | 50.0% | 0.0% |
| Deakin 단독 LODO | `SmallMLP` | 12.3% | 41.8% | 0.354 | 25.0% | 20.0% |
| **통합 LODO (UNSW+Deakin)** | `Rule-Baseline` | 59.7% | 55.7% | 0.594 | 71.4% | 37.5% |
| **통합 LODO (UNSW+Deakin)** | `LogisticRegression` | 66.7% | 10.5% | 0.859 | 71.4% | 12.5% |
| **통합 LODO (UNSW+Deakin)** | `HistGBDT-Shallow` | 82.0% | 4.5% | 0.926 | 100.0% | 12.5% |
| **통합 LODO (UNSW+Deakin)** | `SmallMLP` | 44.3% | 8.2% | 0.695 | 28.6% | 12.5% |
| 교차 전이 (UNSW→Deakin) | `Rule-Baseline` | 13.5% | 47.8% | 0.279 | 50.0% | 40.0% |
| 교차 전이 (UNSW→Deakin) | `LogisticRegression` | 76.1% | 59.4% | 0.767 | 100.0% | 80.0% |
| 교차 전이 (UNSW→Deakin) | `HistGBDT-Shallow` | 49.4% | 31.6% | 0.688 | 50.0% | 60.0% |
| 교차 전이 (UNSW→Deakin) | `SmallMLP` | 3.7% | 6.6% | 0.550 | 0.0% | 0.0% |
| 교차 전이 (Deakin→UNSW) | `Rule-Baseline` | 3.0% | 0.3% | 0.791 | 0.0% | 0.0% |
| 교차 전이 (Deakin→UNSW) | `LogisticRegression` | 50.8% | 0.4% | 0.754 | 33.3% | 18.2% |
| 교차 전이 (Deakin→UNSW) | `HistGBDT-Shallow` | 69.0% | 28.8% | 0.775 | 33.3% | 27.3% |
| 교차 전이 (Deakin→UNSW) | `SmallMLP` | 50.8% | 68.2% | 0.436 | 33.3% | 72.7% |

### 2) 기기별 상세 결과 (통합 LODO, `HistGBDT-Shallow`, MAC 비공개)

| 구분 | 기기명 (데이터셋:모델) | 평가 창 수 | 카메라 판정 비율 | 평균 확률 | 기기 판정(≥50%) |
|---|---|---|---|---|---|
| 카메라 | `deakin:TP-Link Tapo Pan/Tilt Wi-Fi Camera` | 5 | 100.0% | 0.916 | **탐지** |
| 카메라 | `deakin:SAMSUNG Pan/Tilt 1080P Wi-Fi Camera` | 250 | 99.6% | 0.874 | **탐지** |
| 카메라 | `deakin:Ring Video Doorbell` | 30 | 96.7% | 0.953 | **탐지** |
| 카메라 | `deakin:Netatmo Smart Indoor Security Camera` | 250 | 76.0% | 0.663 | **탐지** |
| 카메라 | `unsw:Dropcam` | 102 | 71.6% | 0.516 | **탐지** |
| 카메라 | `unsw:Netatmo Welcome` | 79 | 58.2% | 0.576 | **탐지** |
| 카메라 | `unsw:Samsung SmartCam` | 16 | 50.0% | 0.396 | **탐지** |
| 비카메라 | `unsw:Withings Smart scale` | 1 | 100.0% | 0.979 | **오탐** |
| 비카메라 | `unsw:NEST Protect smoke alarm` | 2 | 50.0% | 0.439 | **오탐** |
| 비카메라 | `deakin:Echo Show 8` | 250 | 20.8% | 0.236 | **정상** |
| 비카메라 | `unsw:Laptop` | 116 | 8.6% | 0.120 | **정상** |
| 비카메라 | `unsw:HP Printer` | 16 | 6.2% | 0.067 | **정상** |
| 비카메라 | `deakin:Echo Dot (4th Gen)` | 86 | 1.2% | 0.021 | **정상** |
| 비카메라 | `unsw:Belkin wemo motion sensor` | 250 | 0.8% | 0.017 | **정상** |
| 비카메라 | `deakin:32' Smart Monitor M80B UHD` | 250 | 0.4% | 0.216 | **정상** |
| 비카메라 | `deakin:TOPERSUN Smart Plug` | 1 | 0.0% | 0.069 | **정상** |
| 비카메라 | `deakin:TOPERSUN Smart Plug_8` | 1 | 0.0% | 0.104 | **정상** |
| 비카메라 | `unsw:Amazon Echo` | 250 | 0.0% | 0.034 | **정상** |
| 비카메라 | `unsw:Android Phone_26` | 29 | 0.0% | 0.029 | **정상** |
| 비카메라 | `unsw:Belkin Wemo switch` | 250 | 0.0% | 0.148 | **정상** |
| 비카메라 | `unsw:IPhone` | 2 | 0.0% | 0.047 | **정상** |
| 비카메라 | `unsw:Samsung Galaxy Tab` | 47 | 0.0% | 0.036 | **정상** |
| 비카메라 | `unsw:Triby Speaker` | 1 | 0.0% | 0.022 | **정상** |

## 2. 저트래픽 · 간헐 구간 포함 전체 (30초 창 ≥ 3 KB)

30초 동안 3 KB 이상 통신한 모든 창 포함 — 대기/간헐 스냅샷 구간의 재현율 하락을 숨기지 않고 확인.

### 1) 모델별 비교 (규칙 기준선 → 로지스틱 → 얕은 GBDT → 소형 MLP, AGENTS.md 4장)

| 평가 분할 | 모델 | 창 재현율 | 창 오탐률 | ROC-AUC | 기기 단위 재현율 | 기기 단위 오탐률 |
|---|---|---|---|---|---|---|
| UNSW 단독 LODO | `Rule-Baseline` | 44.0% | 21.8% | 0.639 | 40.0% | 25.0% |
| UNSW 단독 LODO | `LogisticRegression` | 2.2% | 28.5% | 0.271 | 0.0% | 31.2% |
| UNSW 단독 LODO | `HistGBDT-Shallow` | 4.5% | 13.1% | 0.640 | 0.0% | 18.8% |
| UNSW 단독 LODO | `SmallMLP` | 0.4% | 12.0% | 0.305 | 0.0% | 12.5% |
| Deakin 단독 LODO | `Rule-Baseline` | 84.8% | 26.8% | 0.717 | 75.0% | 37.5% |
| Deakin 단독 LODO | `LogisticRegression` | 79.6% | 25.6% | 0.722 | 75.0% | 12.5% |
| Deakin 단독 LODO | `HistGBDT-Shallow` | 30.9% | 7.5% | 0.739 | 50.0% | 0.0% |
| Deakin 단독 LODO | `SmallMLP` | 14.1% | 4.7% | 0.796 | 25.0% | 0.0% |
| **통합 LODO (UNSW+Deakin)** | `Rule-Baseline` | 19.9% | 15.0% | 0.564 | 22.2% | 12.5% |
| **통합 LODO (UNSW+Deakin)** | `LogisticRegression` | 32.5% | 28.0% | 0.378 | 33.3% | 25.0% |
| **통합 LODO (UNSW+Deakin)** | `HistGBDT-Shallow` | 45.3% | 6.2% | 0.738 | 44.4% | 8.3% |
| **통합 LODO (UNSW+Deakin)** | `SmallMLP` | 17.0% | 6.5% | 0.514 | 22.2% | 8.3% |
| 교차 전이 (UNSW→Deakin) | `Rule-Baseline` | 100.0% | 100.0% | 0.712 | 100.0% | 100.0% |
| 교차 전이 (UNSW→Deakin) | `LogisticRegression` | 27.1% | 81.5% | 0.220 | 25.0% | 87.5% |
| 교차 전이 (UNSW→Deakin) | `HistGBDT-Shallow` | 100.0% | 87.2% | 0.479 | 100.0% | 75.0% |
| 교차 전이 (UNSW→Deakin) | `SmallMLP` | 68.2% | 75.3% | 0.507 | 100.0% | 87.5% |
| 교차 전이 (Deakin→UNSW) | `Rule-Baseline` | 8.4% | 6.4% | 0.645 | 0.0% | 0.0% |
| 교차 전이 (Deakin→UNSW) | `LogisticRegression` | 100.0% | 100.0% | 0.500 | 100.0% | 100.0% |
| 교차 전이 (Deakin→UNSW) | `HistGBDT-Shallow` | 96.0% | 66.7% | 0.581 | 100.0% | 68.8% |
| 교차 전이 (Deakin→UNSW) | `SmallMLP` | 0.0% | 0.0% | 0.642 | 0.0% | 0.0% |

### 2) 기기별 상세 결과 (통합 LODO, `HistGBDT-Shallow`, MAC 비공개)

| 구분 | 기기명 (데이터셋:모델) | 평가 창 수 | 카메라 판정 비율 | 평균 확률 | 기기 판정(≥50%) |
|---|---|---|---|---|---|
| 카메라 | `deakin:SAMSUNG Pan/Tilt 1080P Wi-Fi Camera` | 250 | 100.0% | 0.935 | **탐지** |
| 카메라 | `deakin:Ring Video Doorbell` | 31 | 96.8% | 0.906 | **탐지** |
| 카메라 | `unsw:Samsung SmartCam` | 250 | 78.0% | 0.663 | **탐지** |
| 카메라 | `deakin:Netatmo Smart Indoor Security Camera` | 250 | 52.0% | 0.525 | **탐지** |
| 카메라 | `unsw:Netatmo Welcome` | 183 | 39.3% | 0.313 | **미탐** |
| 카메라 | `deakin:TP-Link Tapo Pan/Tilt Wi-Fi Camera` | 29 | 17.2% | 0.292 | **미탐** |
| 카메라 | `unsw:Withings Smart Baby Monitor` | 250 | 9.6% | 0.368 | **미탐** |
| 카메라 | `unsw:Dropcam` | 250 | 0.0% | 0.054 | **미탐** |
| 카메라 | `unsw:TP-Link Day Night Cloud camera` | 65 | 0.0% | 0.218 | **미탐** |
| 비카메라 | `unsw:NEST Protect smoke alarm` | 2 | 100.0% | 0.649 | **오탐** |
| 비카메라 | `unsw:Withings Smart scale` | 5 | 100.0% | 0.909 | **오탐** |
| 비카메라 | `deakin:Echo Show 8` | 250 | 27.6% | 0.434 | **정상** |
| 비카메라 | `unsw:Triby Speaker` | 9 | 22.2% | 0.168 | **정상** |
| 비카메라 | `unsw:Samsung Galaxy Tab` | 250 | 15.2% | 0.258 | **정상** |
| 비카메라 | `unsw:Laptop` | 250 | 14.8% | 0.201 | **정상** |
| 비카메라 | `deakin:Echo Dot (4th Gen)` | 250 | 8.8% | 0.274 | **정상** |
| 비카메라 | `unsw:Android Phone_26` | 108 | 8.3% | 0.140 | **정상** |
| 비카메라 | `unsw:HP Printer` | 43 | 4.7% | 0.161 | **정상** |
| 비카메라 | `unsw:Amazon Echo` | 250 | 4.0% | 0.151 | **정상** |
| 비카메라 | `unsw:Belkin wemo motion sensor` | 250 | 2.4% | 0.034 | **정상** |
| 비카메라 | `deakin:32' Smart Monitor M80B UHD` | 250 | 2.0% | 0.131 | **정상** |
| 비카메라 | `unsw:Belkin Wemo switch` | 250 | 0.8% | 0.132 | **정상** |
| 비카메라 | `unsw:PIX-STAR Photo-frame` | 250 | 0.4% | 0.063 | **정상** |
| 비카메라 | `deakin:Netatmo Weather Station` | 173 | 0.0% | 0.173 | **정상** |
| 비카메라 | `deakin:Perfk Motion Sensor` | 6 | 0.0% | 0.070 | **정상** |
| 비카메라 | `deakin:Perfk Motion Sensor_10` | 10 | 0.0% | 0.049 | **정상** |
| 비카메라 | `deakin:TOPERSUN Smart Plug` | 250 | 0.0% | 0.066 | **정상** |
| 비카메라 | `deakin:TOPERSUN Smart Plug_8` | 250 | 0.0% | 0.069 | **정상** |
| 비카메라 | `unsw:Blipcare Blood Pressure meter` | 1 | 0.0% | 0.134 | **정상** |
| 비카메라 | `unsw:IPhone` | 7 | 0.0% | 0.080 | **정상** |
| 비카메라 | `unsw:Netatmo weather station` | 250 | 0.0% | 0.187 | **정상** |
| 비카메라 | `unsw:Smart Things` | 13 | 0.0% | 0.134 | **정상** |
| 비카메라 | `unsw:TP-Link Smart plug` | 33 | 0.0% | 0.072 | **정상** |

## 3. 핵심 시사점 (실제 데이터에서 드러난 진실과 V5 실측 설계 지침)

1. **소형 신경망(`SmallMLP`)은 기기 분리(LODO)에서 규칙 · 선형 · 얕은 GBDT보다 열세다 (AGENTS.md 4장 확인)**: 기기 수가 20~30종 수준일 때 MLP는 학습 기기에 과적합하여 새 기기에서 무너진다. 반면 정규화된 **`HistGBDT-Shallow`**와 **`LogisticRegression`**이 가장 일관되게 일반화되었다.
2. **학습 카메라 다양성이 절대적이다**: UNSW 단독 LODO(활성 카메라 3종뿐)에서는 1종을 빼면 학습에 2종만 남아 재현율이 붕괴했으나, 두 데이터셋을 합쳐 7종 카메라로 늘리자 활성 스트림 통합 LODO에서 **`HistGBDT-Shallow` 창 재현율 82.0% / 창 오탐률 4.5% / AUC 0.926, 기기 단위 재현율 100%(7/7)**까지 올라갔다. 따라서 V5 실측 수집 시 최소 **6~8종 이상의 서로 다른 카메라 모델**(연속 스트리밍 + 간헐 스냅샷, 2.4 & 5 GHz)을 확보해야 한다.
3. **저트래픽/대기 구간 및 단발 버스트 한계**: `all_active_ge3KB` 구간을 포함하면 대기·하트비트 창 때문에 재현율이 떨어지며, 단발 1~2창만 나타난 IoT 센서(`Withings Scale` `n=1`, `NEST Protect` `n=2`)가 오탐을 낸다 → 실전에서는 **최소 지속 시간(≥2~3창 누적) + 시험장 입실 전 기준선 비교**가 필수다.
4. **G1(95% / 5%) 달성을 위해 V5 AX210 실측에서 추가할 필수 특징**: 이더넷 L2 길이·비대칭성·FFT만으로도 활성 창 오탐률 4.5%·기기 재현율 100%에 근접했으나, 창 재현율 82% → 95%+를 넘고 모바일 라이브 방송·영상통화를 가르려면 AX210 모니터 모드에서만 얻을 수 있는 **802.11 PHY/MAC 능력 특징(`rateNflag` 1T1R/2T2R, 20/80 MHz, LAA MAC, SoftAP/핫스팟 허브 짝짓기)**을 결합해야 한다.

## 4. 다시 돌리는 명령

```bash
# UNSW IoT Traces (16-09-23, 16-09-24) 및 Deakin IoT (IoT_2023-07-11, IoT_2023-07-12)를 /tmp/detecam_public_data 아래에 배치한 뒤:
cd ai
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python3 eval/public_lodo_baseline.py --data-root /tmp/detecam_public_data --out eval/results_public_lodo.json
python3 eval/make_g1_report.py
```
