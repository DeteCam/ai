# 스펙 002: TriF v12 + 상호결합 보정(C⁻¹) + RAPS + 벽면 AR-OPA 엔진

## 목적
`120 × 120 mm` 손바닥 크기 벽면 부착 수신기(`Palm-12`)에서 2.4/5 GHz 이중대역 AoA 정밀도를 확보하고, 6대 실공간(숙소·화장실·목욕탕·탈의실·40석 교실·150석 강당)에서 비전문가가 최적 벽면 위치·각도로 배치하도록 지원한다.

## 요구사항
1. **CM-RCLPA + `C⁻¹`**: AX210 180° 위상 반전(`≤ 20%`)을 결합 매니폴드 `C·a(θ)`에서 먼저 복구한 뒤 `C⁻¹`를 적용한다.
2. **Capon + `CV_f` + 10면 거울 앵커 + RAPS**: 완전 가림 시에만 10면 가상 거울 앵커를 자동 활성화하고, RAPS 보정으로 90% 통계 보장 AR 구역을 반환한다.
3. **벽면 스위블 AR-OPA**: 손 닿는 높이(`≤ 2.0 m`) 벽면 3곳과 15° 클릭 각도(`Pan ±30°`, `Tilt 0°/-15°/-25°`), 한국어 안내 문장 및 3초 `Auto-Verify` 경고를 반환한다.

## 검증 (`[시뮬레이션]` & `[자동 테스트]`)
- `opt_palm_array.py`: 2.45 GHz `1.68°`, 5.2 GHz `0.57°`, `PSL ≤ 0.51`
- `ar_opa_benchmark.py`: 6공간 평균 P90 `1.44 m` (Naive `4.22 m` 대비 `-65.9%`)
- `pytest`: `test_palm12_mutual_coupling_and_rclpa_capon`, `test_virtual_mirror_and_raps_coverage`, `test_ar_opa_wall_swivel_detents_and_autoverify` 통과.
