# DeteCam ai — 카메라 판별과 방향 · 위치 추정

수신기가 모은 신호로 ① 여러 전자기기 가운데 카메라를 골라내고 ② 카메라 방향과 의심 구역을 계산하는 소프트웨어 · AI입니다.

> 상태(2026-11-24): **명세 · 검증 전.** 이전(v6)의 "F1 98.88%", "1 m 이내 96.4%"는 규칙으로 만든 데이터와 같은 모델로 문제를 내고 푼 시뮬레이션 값이라 쓰지 않습니다. 작업 기준은 [docs/AGENTS.md](https://github.com/DeteCam/docs/blob/main/AGENTS.md)입니다.

## 맡는 일

| 단계 | 내용 | 스펙 |
|---|---|---|
| S1 카메라 판별 | 트래픽 모양 + 조명 · 움직임 자극에 대한 반응 | [`001-camera-classifier`](specs/001-camera-classifier/spec.md) |
| S2~S6 방향 · 구역 | 기준 안테나 위상 비교, 안테나 간섭 보정, 벽 반사를 넣은 방향 추정, 현장 보정, 신뢰도 · 의심 구역 | [`002-map-aware-direction`](specs/002-map-aware-direction/spec.md) |

설계 설명: [`docs/알고리즘_설계.md`](docs/알고리즘_설계.md) · 데이터 규칙: [`data/README.md`](data/README.md)

## 목표 (docs AGENTS.md G1 · G2)
- 카메라 판별: 실제 기기 기준 재현율 95% 이상, 오탐률 5% 이하
- 방향: 같은 방에서 DiffLoc 재현 장비보다 평균 방향 오차 3° 이상 감소
