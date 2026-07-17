<p align="center">
  <img src="assets/sage-logo.png" alt="SAGE research logo" width="360">
</p>

# SAGE

SAGE는 인공지능이 질문에 답하거나 행동을 결정할 때 단순히 관련 정보를 검색하는 데 그치지 않고, 시간, 범위, 정보 출처, 사건의 확정 여부, 관찰자의 지식 및 현실·가상 세계와 같은 현재 상황 상태를 명시적으로 구성하고 검증해야 한다는 **Situation Engineering** 연구입니다. 이 저장소는 상황 인식형 질의응답 구조인 SCQA와 SituationCatch-Bench를 통해 상황 정보의 누락이나 손상이 AI의 판단 정확도에 미치는 영향을 재현 가능하게 분석합니다.

## 폴더 구성

- `ppt/`: SAGE 연구의 배경, 핵심 개념, 실험 결과를 설명하는 발표자료를 보관합니다.
- `code/`: SCQA 구현, gold/predicted/corrupted-state 실험, 다중 LLM 평가 및 독립 annotation 도구를 포함합니다.
- `paper/`: `main.tex`을 시작 파일로 하는 연구논문, 보충자료, 실험 데이터, 결과와 그림을 포함합니다.

## 재현

```bash
PYTHONPATH=code python code/run_experiments.py
PYTHONPATH=code pytest -q code/tests
cd paper && ./run.sh
```

통제형 4,200개 실험은 gold state 100.0%, predicted state 77.9%,
corrupted state 35.1%를 기록합니다. 이는 생성 문장에 대한 기계적 진단이며
자연 데이터 또는 최신 LLM의 성능으로 해석해서는 안 됩니다. 다중 LLM과
독립 인간 annotation 도구는 실제 응답이나 완성된 세 명 이상의 평가 파일이
없으면 결과를 생성하지 않습니다.

재사용 라이선스는 기관 승인을 거쳐 확정해야 하며, 현재 저장소 공개만으로
별도의 재사용 허가를 부여하지 않습니다.
