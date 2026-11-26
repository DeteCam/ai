# 데이터

- 캡처 원본(pcap)과 MAC 주소 원문은 이 저장소에 넣지 않는다 (`ai/AGENTS.md` 5번).
- 여기에는 특징 추출 코드, 익명화된 기기별 집계 평가 결과, 그리고 데이터마다의 설명(어디서, 어떻게, 어떤 조건으로, 라이선스)만 둔다.
- 공개 데이터셋은 이더넷(L2 마스킹) 기반 **V2 이전 수동 트래픽 분류 사전 검증용**이며, 최종 G1 합격 판정은 반드시 **AX210 2.4 · 5 GHz Wi-Fi 모니터 모드 실제 기기 캡처**로 수행한다 (`docs/AGENTS.md` 7.2절).

| 이름 | 종류 | 출처 | 라이선스 | 쓰임 |
|---|---|---|---|---|
| **UNSW IoT Traces** (Sivanathan et al., IEEE TMC 2019) | 실제 기기 이더넷 PCAP (`16-09-23`, `16-09-24`; 카메라 7종 + 노트북 · MacBook · iPhone · Android · Echo · 스피커 · 플러그 등) | https://iotanalytics.unsw.edu.au/iottraces.html | 공개 연구용 (Open Access) | L3/L4 헤더를 가리고 L2(시각 · 길이 · 방향)만으로 기기 분리(LODO) 및 교차 데이터셋 기준선 평가 (`eval/public_lodo_baseline.py`) |
| **Deakin IoT Traffic Dataset (D-IoT)** (Pasquini et al., 2025) | 실제 기기 이더넷 PCAP (`IoT_2023-07-11`, `IoT_2023-07-12`; 현대 Wi-Fi 카메라/도어벨 6종 + Echo Show 8 · 스마트 모니터 · HP Envy · 갤럭시 워치 · 플러그 등) | https://dro.deakin.edu.au/articles/dataset/Deakin_IoT_Traffic_Dataset/28013234 | CC-BY 4.0 (Open Access) | 위와 동일 (기기 분리 LODO 및 UNSW ↔ Deakin 교차 데이터셋 전이 평가) |
