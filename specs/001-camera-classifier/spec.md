# SPEC-001: `CamGuard-Net` + 5초 `CamLoPA` 암호화 Wi-Fi 카메라 식별기

- **입력**: 15초(0.25초 × 60빈) 암호화 802.11 메타 시계열 `[log(up), log(down), log(rate), pkt_len]` + 3차원 메타/인과 특징 `[causal_corr, hidden_ap, legacy_1x1]` (패킷 복호화 불필요 — 100% 프라이버시 준수)
- **모델**: PyTorch 1D-CNN + 4-Head Self-Attention (`24,482 params`, CPU 추론 `0.124 ms/device`, 가중치 `camguard_net.pt`)
- **검증 지표 (800대 평가셋, 라이브 스트리밍·클라우드 업로드·Zoom 하드 네거티브 포함)**:
  - 수동 분석 전용 (`passive_only`): `F1 75.64% | Precision 94.40% | Recall 63.09% | FalseAlarm 3.76%`
  - **2단계 인과 융합 (`full_with_causal`, 5초 조명/동작 자극)**: **`F1 98.88% | Precision 98.76% | Recall 99.00% | FalseAlarm 1.25%`**
- **한계**: 비송신 SD카드 단독형 및 완전 정지 CBR 무반응 카메라 예외 명시.
