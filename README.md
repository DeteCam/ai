<div align="center">

# 🧠 DeteCam AI

**카메라를 가려내고, 신호 곡선에서 방향을 읽는 모델**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![상태](https://img.shields.io/badge/상태-스펙_작성-19C2B0?style=flat-square)

</div>

## 모델 둘

| | 모델 | 입력 → 출력 | 기준선 (규칙) |
|---|---|---|---|
| 🔎 | **의심 점수** | 기기 하나의 30초 트래픽 겉모습 → 카메라일 확률과 근거 3개 | 증거를 더하는 규칙 점수 |
| 📈 | **곡선 판독** | 판을 돌리며 잰 CSI 곡선 묶음 → 후보 자리마다의 점수 | 곡선 전체 맞추기 |

두 모델 모두 규칙으로 된 기준선이 수신기에 이미 있다. **모델은 기준선을 이길 때만 넣는다.**

## 지금 상태

스펙을 쓰는 단계다. 학습 데이터를 만드는 시뮬레이터(광선 추적 + 수신기 무늬 표)는 [receiver/sim/rt](https://github.com/DeteCam/receiver/tree/main/sim/rt) 에 있고, 기준선의 성능 표는 [검증 보고서](https://github.com/DeteCam/docs/tree/main/verification)에 있다.

## 폴더

```
specs/     스펙: 001 의심 점수, 002 곡선 판독
data/      특징 표와 데이터 설명 (원본 캡처는 넣지 않는다)
models/    학습 코드와 내보낸 모델 (구현 단계에서 추가)
eval/      평가 스크립트와 결과
```

## 관련

- 일하는 규칙: [CONTRIBUTING](https://github.com/DeteCam/.github/blob/main/CONTRIBUTING.md)
- 시스템 전체: [docs](https://github.com/DeteCam/docs)
