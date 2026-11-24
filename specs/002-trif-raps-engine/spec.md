# SPEC-002: `ReconCovNet-v4` + Bayesian `MA-PINN` + `RAPS` 3D 위치 추정 엔진

- **배열**: `NANO12_EDGE_M` (`84×84 mm` 4층 PCB, 12+1소자, `d_min=20.1 mm < λ/2 @ 5.85 GHz`)
- **전처리**: 이중 체인 비(`H_B/H_A`) + `CM-RCLPA` 180° 위상 반전 복구 + 턴테이블 캘리브레이션 `C⁻¹`
- **AI 초해상도 (`ReconCovNet-v4`)**: PyTorch 물리 잔차 공분산 복원망 (`457K params`, `0.024 ms`, 가중치 `recon_covnet.pt`). 미학습 4공간 2.45G P90 `-16.8%`, 5.22G P90 `-11.1%`.
- **2기 3D 융합 (`MA-PINN`)**: Bayesian Log-Sum-Exp 1차 가상 거울 앵커(6~12개) + `P_tx` 불변 `ΔP_12` 차분 전력비 + 선택적 0원 스마트폰 5초 보행 경사.
- **10공간 검증 (`n=280/band`)**:
  - 5.22 GHz: `Med 0.19 m / P90 0.54 m / ≤1m 96.4%` (미학습 4공간 `P90 0.64 m`, 사각지대 NLoS `P90 0.63 m`)
  - 2.45 GHz: `Med 0.24 m / P90 0.87 m / ≤1m 92.9%` (+0원 폰 `P90 0.65 m / 96.4%`, 사각지대 NLoS `0.80 m / 96.1%`)
- **AR 신뢰 구간**: `RAPS` Split Conformal Prediction (`≥ 90%` 통계적 커버리지 보장).
