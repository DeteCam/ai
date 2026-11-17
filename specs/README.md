# 스펙 목록 (ai)

스펙 주도 개발: `spec.md`(무엇을·왜) → `plan.md`(어떻게) → `tasks.md`(할 일) 순서로 쓰고 나서 만든다. 규칙은 [CONTRIBUTING](https://github.com/DeteCam/.github/blob/main/CONTRIBUTING.md).

| 번호 | 스펙 | 상태 | 한 줄 |
|---|---|---|---|
| 001 | [suspicion-score](001-suspicion-score/spec.md) | 설계 | 암호화된 Wi-Fi 트래픽의 겉모습만 보고 '카메라일 가능성'을 점수로 낸다 |
| 002 | [position-model](002-position-model/spec.md) | 설계 | 패널이 잰 값에서 자리 확률을 낸다. 물리 모델에 배운 모델을 곱한다 |

상태: 설계(스펙 작성 중) → 구현 → 검증 → 완료

두 모델 모두 **규칙·물리 기준선이 먼저 있고, 모델은 기준선을 이길 때만 넣는다**는 원칙을 따른다.

돌판 수신기 때의 '곡선 판독' 스펙(002-curve-reader)은 패널로 바뀌면서 뺐다. 지금은 [receiver-legacy](https://github.com/DeteCam/receiver-legacy) 에 옮겨 두었다.
