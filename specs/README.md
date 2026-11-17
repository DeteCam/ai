# 스펙 목록 (ai)

스펙 주도 개발: `spec.md`(무엇을·왜) → `plan.md`(어떻게) → `tasks.md`(할 일) 순서로 쓰고 나서 만든다. 규칙은 [CONTRIBUTING](https://github.com/DeteCam/.github/blob/main/CONTRIBUTING.md), 시스템 전체 명세는 [docs/specs/000-system](https://github.com/DeteCam/docs/tree/main/specs/000-system).

| 번호 | 스펙 | 상태 | 한 줄 |
|---|---|---|---|
| 001 | [suspicion-score](001-suspicion-score/spec.md) | 설계 | 암호화된 Wi-Fi 트래픽의 겉모습만 보고 '카메라일 가능성'을 점수로 낸다 |
| 002 | [curve-reader](002-curve-reader/spec.md) | 설계 | 판을 돌리며 잰 CSI 곡선에서 카메라 방향·자리를 읽는다 (기준선: 곡선 전체 맞추기) |

상태: 설계(스펙 작성 중) → 구현 → 검증 → 완료

두 모델 모두 **규칙 기반 기준선이 먼저 있고, 모델은 기준선을 이길 때만 넣는다**는 원칙을 따른다 (프로젝트 원칙 4).
