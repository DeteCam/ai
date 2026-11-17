<div align="center">

# 🧠 DeteCam AI

**카메라를 가려내고, 패널이 잰 값에서 카메라의 자리를 내는 모델**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![Sionna RT](https://img.shields.io/badge/Sionna_RT-76B900?style=flat-square&logo=nvidia&logoColor=white)
![상태](https://img.shields.io/badge/상태-스펙_·_규칙_기준선-19C2B0?style=flat-square)

</div>

## 모델 둘

| | 모델 | 입력 → 출력 | 기준선 (규칙·물리) | 지금 알고 있는 것 |
|---|---|---|---|---|
| 🔎 | [**의심 점수**](specs/001-suspicion-score/spec.md) | 기기 하나의 30초 트래픽 겉모습 (주소, 길이, 간격, 방향) → 카메라일 확률과 까닭 셋 | 증거를 더하는 규칙 점수 (`receiver/firmware/core/score.py`) | 규칙으로 잘못 울림 4~5% (계산) |
| 📍 | [**자리 모델**](specs/002-position-model/spec.md) | 패널이 잰 후보 점마다의 점수 → 자리마다의 확률 | 물리 모델 (방향 → 자리) | 물리 × 배운 모델: 책상 위 +3점, 가슴·안경 +9~10점 (교실 계산) |

두 모델 모두 규칙이나 물리로 된 기준선이 수신기에 이미 있다. **모델은 기준선을 이길 때만 넣는다.**

## 학습 자료

- **전파 시뮬레이션.** 교실과 숙소 방을 Sionna RT 로 만들고, 사람의 자세와 카메라의 자리를 바꿔 가며 패널이 받았을 값을 만든다 ([receiver/sim/rt](https://github.com/DeteCam/receiver/tree/main/sim/rt)). 교실 하나에 18,000번을 2분 안에 만든다.
- **실측.** 내 카메라와 폰·노트북의 트래픽 기록, 패널이 잰 값. 원본(pcap)과 MAC 주소 원문은 올리지 않는다 ([data](data/README.md)).

## 관련 연구

몰래카메라를 가려내고 위치를 찾는 데 AI 를 쓴 연구와, 우리가 무엇을 가져오는지: [관련 연구](docs/관련%20연구.md)

## 폴더

```
specs/     스펙: 001 의심 점수, 002 자리 모델
docs/      의심 점수의 설계, 관련 연구
data/      특징 표와 데이터 설명 (원본 캡처는 넣지 않는다)
models/    학습 코드와 내보낸 모델 (구현 단계에서 추가)
eval/      평가 스크립트와 결과
```

## 관련

- 일하는 규칙: [CONTRIBUTING](https://github.com/DeteCam/.github/blob/main/CONTRIBUTING.md)
- 시스템 전체: [docs](https://github.com/DeteCam/docs) · 수신기의 설계도: [receiver](https://github.com/DeteCam/receiver/blob/main/docs/%EC%84%A4%EA%B3%84%EB%8F%84.md)
