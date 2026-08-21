<p align="center">
  <img src="assets/sage-logo.png" alt="SAGE research logo" width="360">
</p>

# SAGE

SAGE는 인공지능이 질문에 답하거나 행동을 결정할 때 단순히 관련 정보를 검색하는 데 그치지 않고, 시간, 범위, 정보 출처, 사건의 확정 여부, 관찰자의 지식 및 현실·가상 세계와 같은 현재 상황 상태를 명시적으로 구성하고 검증해야 한다는 **Situation Engineering** 연구입니다. 이 저장소는 상황 인식형 질의응답 구조인 SCQA와 SituationCatch-Bench를 통해 상황 정보의 누락이나 손상이 AI의 판단 정확도에 미치는 영향을 재현 가능하게 분석합니다.

## 현재 연구 산출물

- **SituationCatch-Bench v0.1**: 7개 상황 범주의 통제형 진단
  4,200개와 고정 생성 시드, 항목별 출력을 포함합니다.
- **SCQA 참조 구현**: oracle gold state에서 100.0%, 생성된 claim
  text에서 결정적으로 추정한 state에서 77.9%, 해당 state를
  의도적으로 손상한 조건에서 35.1%의 exact action-and-answer
  accuracy를 기록합니다.
- **Audited E5 pilot**: Gemini-family 3개 모델, 범주별 30개씩
  총 210개 항목에서 direct/structured/explicit-situation prompt를 매칭해
  평가했습니다. Explicit-situation prompt는 structured prompt를 유의하게
  능가하지 못했고, 한 모델에서는 유의하게 낮았습니다.
- **Retrieval 및 natural-text checks**: top-3 lexical RAG가 전체 평균
  91.3%로 structured 83.5%와 situation 80.6%보다 높았습니다. SituatedQA
  12개 스모크 테스트도 포함하지만, 이 결과는 확증 결과가 아닙니다.

이 수치들은 구조화된 통제 환경과 단일 provider-family에서의 진단
결과입니다. 자연적으로 발생한 질문에 대한 일반적 성능 향상,
다중 모델 family 재현, 또는 배치 안전성을 입증하는 결과로 해석하면
안 됩니다.

## 저장소 구성

- `ppt/`: SAGE 연구의 배경, 핵심 개념, 실험 결과를 설명하는 발표자료를 보관합니다.
- `code/`: SCQA 구현, gold/predicted/corrupted-state 실험, 다중 LLM 평가 및 독립 annotation 도구를 포함합니다.
- `paper/`: `main.tex`을 시작 파일로 하는 연구논문, 보충자료, 실험 데이터, 결과와 그림을 포함합니다.

## 빠른 재현

```bash
PYTHONPATH=code python code/run_experiments.py
PYTHONPATH=code python -m pytest -q code/tests
cd paper && ./run.sh
```

실험 산출물을 검사하는 추가 명령은 다음과 같습니다.

```bash
python code/audit_e5.py paper/results/raw/e5_gemini_*.jsonl \
  --data paper/data/situationcatch_llm_sample.jsonl \
  --conditions direct structured situation
python code/make_rag_table.py
cd paper && sha256sum -c SHA256SUMS.txt
```

E5 실행 계획은 API key 없이 `python code/run_e5.py --dry-run`으로
확인할 수 있습니다. 실제 재실행에는 `GEMINI_API_KEY`와 provider
사용료가 필요합니다. 평가 코드는 실제 API 응답을 raw JSONL로
보존하며, 누락된 model call을 가상 결과로 대체하지 않습니다. Human
agreement 또한 세 명 이상의 독립 annotation 파일이 완성되기 전에는
보고하지 않습니다.

## 논문 제출 상태

`paper/main.pdf`와 `paper/supplementary.pdf`는 `paper/run.sh`로 각각
3-pass `pdflatex` build를 수행합니다. 제출 전에는 저자가 다음
항목을 반드시 확인해야 합니다.

- 저자명, ORCID, 소속, 연락처와 blind-review 설정
- funding, competing-interests, 기관·고용주 공개 승인의 정확성
- 제출본을 고정하는 Git commit 또는 release tag
- 실제 archive deposit 후에만 기재할 DOI

다중 독립 model family, 더 큰 독립 natural-text corpus, human
inter-annotator agreement, agentic/tool-use baseline은 아직 완료되지 않은
확증 과제입니다. 저장소는 이를 완료된 실험으로 주장하지 않습니다.
상세한 제출 gate는 [`paper/REVIEWER_READINESS.md`](paper/REVIEWER_READINESS.md),
재현 범위와 제한은 [`paper/README.md`](paper/README.md)에 있습니다.

## 라이선스

코드, 논문 소스와 함께 배포되는 연구 산출물은 저장소 루트의
[`LICENSE`](LICENSE)에 명시된 MIT 라이선스로 재사용할 수 있습니다. 제3자
데이터에는 각 원출처의 라이선스가 별도로 적용됩니다.
