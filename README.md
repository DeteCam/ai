# DeteCam ai — 카메라 판별과 방향 · 위치 추정

수신기가 모은 신호로 ① 여러 전자기기 가운데 2.4 · 5 GHz Wi-Fi 카메라를 골라내고 ② 카메라 방향과 의심 구역을 계산하는 소프트웨어 · AI입니다.

> 상태(2026-11-25): **V0/V1 사전 검증 완료 · AX210 실측 전.** 이전(v6)의 "F1 98.88%", "1 m 이내 96.4%"는 규칙으로 만든 데이터와 같은 모델로 문제를 내고 푼 시뮬레이션 값이라 쓰지 않습니다. 작업 기준은 [docs/AGENTS.md](https://github.com/DeteCam/docs/blob/main/AGENTS.md)입니다.

## 맡는 일

| 단계 | 내용 | 스펙 · 사전 검증 |
|---|---|---|
| S1 카메라 판별 | **수동 802.11 L2/PHY 다중 시간축 분류기** (SoftAP 방향 무관 비대칭성 · 프레임 버스트 · 100 ms FFT GOP · PHY 능력 핑거프린트; 자극은 비시험장 선택 보조) | [`001-camera-classifier`](specs/001-camera-classifier/spec.md) · [`eval/PUBLIC_LODO_RESULTS_20261125.md`](eval/PUBLIC_LODO_RESULTS_20261125.md) |
| S2~S6 방향 · 구역 | AX210 부호 앵커 복원, **비게이팅 복소 비율 시간 평균**, 중심 기준 안테나 9소자 통합, NEC2 1회 보정표, 벽 + 대형 금속 반사체(칠판 · 거울) 지도 반영 강건 방향 추정, 현장 보정, 2위치 비동기 신뢰도 가중 의심 구역 | [`002-map-aware-direction`](specs/002-map-aware-direction/spec.md) · [`receiver/sim/v1_ring/RESULTS_20261125.md`](https://github.com/DeteCam/receiver/blob/main/sim/v1_ring/RESULTS_20261125.md) |

## 코드 구조

- `model/passive_l2.py`: L2 메타데이터 전용 25종 특징 추출기 및 규칙 · 로지스틱 · 얕은 GBDT · 소형 MLP 분류기
- `eval/public_lodo_baseline.py`: 공개 실측 PCAP(UNSW IoT Traces · Deakin IoT) 기기 분리(LODO) 및 교차 데이터셋 기준선 평가
- 설계 설명: [`docs/알고리즘_설계.md`](docs/알고리즘_설계.md) · 데이터 규칙: [`data/README.md`](data/README.md)

## 목표 (docs AGENTS.md G1 · G2)
- 카메라 판별: 실제 기기(AX210 2.4 · 5 GHz 각 별도) 기준 재현율 95% 이상, 오탐률 5% 이하
- 방향: 같은 방(40명 교실 · 금속 칠판 등)에서 DiffLoc 재현 장비보다 평균 방향 오차 3° 이상 감소 및 P95 감소
