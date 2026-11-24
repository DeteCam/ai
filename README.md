# DeteCam 6.0 (`Nano-2 AI`) — Physics-Informed Edge-AI & 신호처리 엔진

> **교수님 지적("하드웨어 중심 설계")에 대한 정면 해법**: 수신기를 3기(12 cm)에서 **단 2기 포켓 크기(9.6 cm)**로 줄이면서도 정확도를 오히려 더 끌어올린 핵심은 **4대 실제 학습·검증된 PyTorch AI + 물리 융합 엔진**입니다.

## 1. 4대 핵심 SW/AI 엔진 (`NanoPi R5C` RK3568B2 CPU/0.8T NPU 온디바이스 구동)

| 엔진 | 구현 / 학습 기반 | 핵심 역할 | 정량 검증 결과 (`[시뮬레이션 · 미학습 검증]`) | 추론 속도 (CPU) |
|---|---|---|---|---:|
| **1. `ReconCovNet-v4`** | PyTorch (457K params, Differentiable-Capon 손실) | `84 mm` 초소형 배열의 잔류 상호결합·다중반사 공분산을 Hermitian PSD 초해상도 복원 | 미학습 4공간 2.45G P90 `8.98°→7.47° (-16.8%)`, 5.22G P90 `5.52°→4.91° (-11.1%)` | **`0.024 ms`** |
| **2. `CamGuard-Net`** | PyTorch (24K params, 1D-CNN + 4-Head Self-Attention + 5초 `CamLoPA`) | 암호화된 Wi-Fi 패킷 시계열 + 실내 조명/움직임 인과 반응 융합으로 라이브 방송·클라우드 백업 속 카메라만 식별 | 800대 하드 네거티브: 수동 `F1 75.64%` → **인과 융합 `F1 98.88% · 재현율 99.00% · 오경보 1.25%`** | **`0.124 ms`** |
| **3. `MA-PINN`** | Bayesian Log-Sum-Exp 3D 가상 거울 앵커 + `ΔP_12` 전력비 | AR 스캔 3D 벽·거울·칠판·사물함의 1차 반사를 공짜 가상 앵커 6~12개로 전환 + `P_tx` 불변 전력비로 깊이 모호성 해소 | **단 2기**로 5.22G 10공간 `P90 0.54 m (≤1m 96.4%)` — 3기 고전(`0.84 m`) 압도! NLoS `P90 -67%` | `< 5 ms` |
| **4. `AR-OPA-2` + `RAPS`** | 서브모듈러 1-Swap 최적화 + Split Conformal Prediction | 직선 LoS + 1차 가상 거울 가시성을 동시 최적화해 2기 벽면 위치·각도 추천 + 90% 통계 보장 AR 구역 생성 | 10대 공간 0.1초 최적 배치 + RAPS 90% 커버리지 보장 | `< 120 ms` |

## 2. 문서 및 사양
- [`docs/알고리즘_설계.md`](docs/알고리즘_설계.md) — 4대 AI·물리 융합 알고리즘 수식·아키텍처·미학습 공간 평가표
- [`specs/001-camera-classifier/spec.md`](specs/001-camera-classifier/spec.md) — `CamGuard-Net` + 5초 `CamLoPA` 인과 판별 사양
- [`specs/002-trif-raps-engine/spec.md`](specs/002-trif-raps-engine/spec.md) — `ReconCovNet-v4` + Bayesian `MA-PINN` + `RAPS` 사양
- 실구현 코드 및 학습 가중치: [`DeteCam/receiver/firmware/core/ai_engine.py`](https://github.com/DeteCam/receiver/blob/main/firmware/core/ai_engine.py), [`DeteCam/receiver/sim/train_ai_models.py`](https://github.com/DeteCam/receiver/blob/main/sim/train_ai_models.py)
