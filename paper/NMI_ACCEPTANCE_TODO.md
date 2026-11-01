# Nature Machine Intelligence — 엄격한 심사자 관점 점검과 Accept 필수 TODO

대상 원고: *Situation engineering: separating evidence applicability from availability in AI systems*
기준: SituationCatch-Bench **v0.2**와 그 위에서 다시 실행한 E5 (2026-11-01). 모든 수치는 저장소의
감사 통과 원자료에서 나온 것이며, 이 문서는 근거 없는 결과를 만들지 않는다.

---

## 1. 심사자 총평 (지금 원고를 그대로 낸다면)

**예상 결정: editorial reject 또는 major revision.** 형식 요건(NMI Article 3,500단어·6개 디스플레이 항목·
150단어 초록, 참고문헌·그림 규격)은 모두 충족한다. 그러나 NMI가 요구하는 "기계지능에 대한 실질적 진전"의
근거가 아직 약하다. 남은 거절 사유는 형식이 아니라 **증거의 범위**다.

### 예상 거절 사유 (심각도순)

| # | 예상 심사 지적 | 현재 상태 | 해소 방법 |
|---|---------------|-----------|-----------|
| R1 | 핵심 증거가 **합성·자기설계(co-designed) 벤치마크**다. oracle 100%는 구성상 당연하다. | 원고가 이를 "conformance suite"로 명시. v0.2에서 정답 편향·최신성 지름길은 제거(통제 baseline 47–54%, 7개 ablation 모두 자기 범주만 300오류). | 독립 저자의 자연어 평가셋 (P0-2) |
| R2 | 제안된 개입(situation prompt)이 **효과가 없다** — 왜 이 프레임워크를 출판하나? | v0.2에서도 situation−structured = −2.9, −14.8, −2.9 %p. 원고는 이를 null-to-negative로 정직하게 보고하고, 예측 실패를 Discussion에 명시. | 다중 패밀리에서 null이 일반적임을 보이거나(P0-1) 이득이 있는 조건을 찾기(P1-1) |
| R3 | **단일 공급자(Gemini)** 결과다. | 3개 Gemini 모델, 한 경로(OpenRouter→Google). | 독립 3개 패밀리 이상 (P0-1) |
| R4 | "병목은 sensing"이라는 결론이 **규칙 기반 센서**에서만 측정됐다. LLM의 sensing 오류는 직접 측정되지 않았다. | 초록은 "consistent with"로 완화되어 있음. | LLM이 출력한 state를 gold slot과 채점 (P1-1, 새 API 호출 불필요) |
| R5 | "RAG" 조건이 실제 검색이 아니다. | **이번에 수정**: 항목당 claim ≤3개라 top-3가 전부이며, 실제 조작은 *메타데이터 제거*임을 본문·표·Methods에 명시. | 방해 문서가 섞인 코퍼스 검색 baseline (P1-2) |
| R6 | 인간 검증(IAA)이 없다. | 70문항 blind 패킷·Kaggle 노트북 준비 완료, v0.2로 재생성. | 주석자 3명 실측 (P0-3) |
| R7 | 통계: 군집이 7개뿐이라 bootstrap CI가 불안정. | **이번에 수정**: Methods에 "7개 군집, 근사·경계값 가능, 서술적 보고" 명시. | 더 많은 시나리오 패밀리 (P0-2와 함께) |
| R8 | "situation engineering"이 기존 개념(situation calculus, DST, belief revision)의 **재명명**이 아닌가. | Methods "Relation to prior formalisms"에서 차이를 명시. | 심사 대응에서 비교표 강조 (P2) |

---

## 2. 제목 결정

**현 제목 유지를 권장한다.** "Situation engineering: separating evidence applicability from availability
in AI systems"는 11단어로 NMI 관행에 맞고, 결과를 과장하지 않는다(효과를 주장하지 않고 개념 분리만
말함). 검토한 대안 — 예: "Evidence applicability, not availability, limits …" — 은 *인과적 병목*을
단정하는데, 현재 증거(규칙 센서, 단일 패밀리)로는 뒷받침되지 않아 오히려 심사 위험을 키운다.
P0-1·P1-1이 끝나 LLM에서 sensing 병목이 직접 확인되면 그때 더 강한 제목을 검토할 수 있다.

---

## 3. 이번에 원고에서 직접 고친 것 (근거 있는 수정만)

- **벤치마크 v0.2**: 범주 내 정답·최신성 균형화, 통제 baseline을 단일 "situation-blind" 계열로 정의,
  불용어 처리로 어휘 누출 제거. v0.1과 결과는 `data/v0.1/`, `results/v0.1/`에 보존.
- **모든 결정적 결과 재계산**: 100.0 → 66.5 → 45.1%, ablation 7/7 범주 특이적, 그림·보충표 재생성.
- **E5 전체 재실행**(같은 3개 모델): 0 실패, 무결성 게이트 PASS, 모든 기록 reasoning token 0.
- 초록·서론·결과·논의·evidence ladder의 E5 서술을 v0.2 감사 수치로 교체.
- 프레임워크 **예측의 성패를 논의에 명시**(통제 예측은 성립, 첫 신경망 예측은 불성립).
- RAG 조건의 실체(메타데이터 제거)를 명시, 7-군집 CI 한계, 분석계획 불변·호스팅 모델 재현성 한계 명시.
- 중복(관찰성 단락, 논의의 계층 목록·중복 수식) 제거 → 본문 3,350/3,500단어.
- 참고문헌 25개 재검증(24개 자동 확인, 1개는 PhilPapers·Stanford 기록으로 확인).

---

## 4. Accept를 위한 필수 TODO (우선순위)

### P0 — 없으면 거절 가능성이 높음 (추가 실험·검증 필요)

**P0-1. 독립 모델 패밀리로 E5 확장** — *R2, R3*
- 내용: 동일 210문항·동일 조건(direct/structured/situation + RAG + agent)을 최소 3개 독립 패밀리에서 실행.
  예: `anthropic/claude-sonnet-5.5`, `openai/gpt-6.1-sol`, 오픈웨이트 `meta-llama/llama-4-maverick`.
- 실행 가능성: 현재 환경의 OpenRouter 키로 **기술적으로 바로 가능**(이번 v0.2 Gemini 전체 실행 실비 $1.22).
  중급 모델은 토큰당 약 10배 → 3개 패밀리 대략 **$10–20 추정**(OpenRouter 가격표 기준, 실행 전 확인).
- 주의: 일부 모델은 reasoning을 끌 수 없음 → 패밀리별 설정을 사전 고정하고 기록. 감사 도구
  `code/audit_multifamily.py`가 ≥3 패밀리를 요구하며 자동 인증.
- 담당: 비용 승인 후 Claude가 실행 가능.

**P0-2. 독립 저자의 자연어 평가** — *R1, R7*
- 내용: 생성기를 모르는 사람이 쓴 자연 질문·증거(목표 1,200 시나리오, 3개 도메인; 보충 Note 14의
  사전 명세). 최소한 SituatedQA 전체 temporal split 등 공개 자연 벤치마크로 12개 스모크 테스트를 대체.
- 담당: 데이터 라이선스·저자 섭외는 사용자, 실행·분석은 Claude 가능.

**P0-3. 인간 주석 일치도(IAA) 실측** — *R6*
- 내용: v0.2 패킷 3개를 독립 주석자 3명이 작성 → Kaggle 노트북으로 Fleiss κ 산출.
- 담당: **사용자**(주석자 섭외). 절차: `paper/annotation_packets/KAGGLE_STEP_BY_STEP.md`.

### P1 — 심사 통과 가능성을 크게 높임

**P1-1. LLM의 state 추출 정확도 직접 측정** — *R4*
- 내용: structured/situation 조건의 JSON 응답에 이미 모델이 추론한 state가 들어 있다. 이를 gold slot과
  채점하면 "sensing이 병목"을 LLM에서 직접 검증할 수 있다. **새 API 호출 불필요**(보관된 원자료 분석).
- 주의: 자유형 JSON 값을 slot에 매핑하는 규칙을 먼저 고정해야 함(사후 조정 금지).

**P1-2. 방해 문서가 포함된 실제 검색 baseline** — *R5*
- 내용: 항목별 claim에 다른 항목의 claim(방해물)을 섞은 코퍼스에서 top-k 검색. "관련성 ≠ 적용성"을 검색 문제로 검증.

**P1-3. 사전 등록**: P0-1·P0-2의 분석계획(주 대비, 판정 규칙)을 실행 전에 타임스탬프로 고정(OSF 등).

### P2 — 권장

- 강한 프롬프트 baseline(few-shot, CoT, self-consistency) 추가.
- R8 대응용 비교표(situation calculus·DST·belief revision 대비 무엇이 새로운가)를 Extended Data로.
- 다국어·다중모달 확장은 범위 밖으로 명시 유지.

---

## 5. 제출 행정 (사용자만 가능)

- [ ] Zenodo로 저장소 아카이브 → **DOI**를 Data/Code availability에 기입 (`.zenodo.json` 준비됨).
- [ ] Nature Portfolio **Reporting Summary**와 Editorial Policy Checklist 작성(제출 시스템에서).
- [ ] 커버레터(`paper/COVER_LETTER.md`)의 추천 심사자·제외 요청·프리프린트 여부 기입.
- [ ] 생성형 AI 사용 고지는 Methods에 있음 — 실제 사용 범위와 일치하는지 저자 확인.

---

## 6. 판단 요약

P0 세 가지가 끝나기 전에 Article로 내면 "합성 진단 + 단일 패밀리 null"로 읽혀 desk reject 위험이 크다.
P0-1은 비용 승인만 있으면 바로 실행할 수 있고, P1-1은 비용 없이 기존 데이터로 가능하다. 이 둘을 먼저 하고,
P0-3(사람)과 P0-2(데이터)를 병행하는 것이 가장 현실적인 경로다. 그 전에 저널의 관심을 확인하려면
커버레터 Version B(presubmission enquiry)를 쓰는 것이 안전하다.
