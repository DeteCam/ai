# DeteCam 5.0 (Palm-12) — AI · 신호처리 · 위치추정 저장소

> 암호화를 풀지 않고 **수많은 전자기기 중 카메라만 골라내고(`score.py`)**, 손바닥 크기(`120×120 mm`) 벽면 부착 수신기로 **간섭·반사가 심한 실내에서도 90% 통계 보장 구역을 짚어 내는(`trif_v12.py`, `ar_opa.py`)** 알고리즘 설계 및 스펙 저장소입니다.

## 핵심 파이프라인 (3대 모듈)

| 모듈 | 해결하는 질문 | 핵심 원리 | 기준 코드 (receiver) |
|---|---|---|---|
| **1. 3단계 카메라 판별** | 수많은 스마트폰·노트북 중 카메라만 어떻게 찾는가? | ① 수동 MAC/PHY 무늬(업링크 우세·버스트·핫스팟·1×1 칩) → ② 인과적 조명/움직임 자극(`CamLoPA`, IEEE S&P 2025) → ③ 3D 방 경계 필터 + `AD8317×3` LTE/5G 교차 차감 | [`firmware/core/score.py`](https://github.com/DeteCam/receiver/blob/main/firmware/core/score.py) |
| **2. TriF v12 + RAPS 위치 추정** | 간섭·반사·증폭 환경 + 12 cm 소형 배열에서 위치를 어떻게 찾는가? | 이중 체인 비(`H_B/H_A`) + **결합 매니폴드 RCLPA(CM-RCLPA)** + **상호결합 역행렬 `C⁻¹`** + 12소자 Capon + `CV_f` 가중 + 10면 가상 거울 앵커 + **RAPS 90% 통계 보장 AR 구역** | [`firmware/core/trif_v12.py`](https://github.com/DeteCam/receiver/blob/main/firmware/core/trif_v12.py) |
| **3. 벽면 스위블 AR-OPA** | 공간마다 구조가 다른데 최적 수신기 위치·각도를 어떻게 찾는가? | Mixed-LoS/NLoS 3D Fisher Information(`arXiv:2604.00863`) + 벽면 반사 페널티(`arXiv:2412.13208`) 서브모듈러 최적화 → 손 닿는 벽면 3곳 + `Pan ±30° / Tilt -25°` 클릭 각도 + 3초 `Auto-Verify` | [`firmware/core/ar_opa.py`](https://github.com/DeteCam/receiver/blob/main/firmware/core/ar_opa.py) |

## 문서 & 스펙
- 📖 [알고리즘 통합 설계서](docs/알고리즘_설계.md)
- 📋 [스펙 001: 3단계 카메라 판별기](specs/001-camera-classifier/spec.md)
- 📋 [스펙 002: TriF v12 + RAPS + AR-OPA 엔진](specs/002-trif-raps-engine/spec.md)
- 📂 [데이터 수집·비식별화 원칙](data/README.md)
