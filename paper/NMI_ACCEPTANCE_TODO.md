# Nature Machine Intelligence — 엄격한 심사자 관점 점검과 Accept 필수 TODO

대상 원고: *Situation engineering: separating evidence applicability from availability in AI systems*
기준: SituationCatch-Bench **v0.2**, E5 재실행(2026-11-01), 사전 등록된 E6 다중 패밀리 재현과
E7 LLM 센서 연구(2026-11-02 사전 등록, `paper/PREREGISTRATION_E6_E7.md`, Amendment 1 포함). 모든 수치는 저장소의
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
| R2 | 제안된 개입(situation prompt)이 **효과가 없다** — 왜 이 프레임워크를 출판하나? | v0.2에서도 situation−structured = −2.9, −14.8, −2.9 %p. 원고는 이를 null-to-negative로 정직하게 보고하고, 예측 실패를 Discussion에 명시. | **부분 해소(E6)**: 사전 등록 판정 규칙상 3개 패밀리 중 1개만 CI>0 → "차이 없음". 유일한 양의 대비(Llama +19.5)는 추출기 산물로, 사후 민감도 분석에서 −1.9 [−7.1, +1.9]. 논문의 주장은 "situation 필드는 situation awareness가 아니다"로 유지. |
| R3 | **단일 공급자(Gemini)** 결과다. | **부분 해소(E6)**: 6개 모델·4개 패밀리(Gemini + 사전 등록 Meta·DeepSeek·Qwen), 다중 패밀리 감사 PASS. 남은 공백: Gemini 외 **독점(proprietary) 패밀리 없음**(Anthropic·OpenAI는 크레딧 소진으로 Amendment 1에서 제외, 한계로 명시). | Anthropic·OpenAI 모델로 같은 스크립트 재실행 (P0-1b) |
| R4 | "병목은 sensing"이라는 결론이 **규칙 기반 센서**에서만 측정됐다. LLM의 sensing 오류는 직접 측정되지 않았다. | **해소(E7)**: 4개 LLM이 규칙 센서와 같은 입력으로 state를 채워 같은 엔진에 투입. end-to-end 65.7% → 79.0–87.1%, 비시간 항목 71.1% → 85.6–96.1%, source conflict 0→100%, temporal은 모두 33–40%(텍스트에 시각 정보 없음). 결론을 "규칙 센서 특유의 gap + 텍스트에 없는 정보"로 수정. 사전 등록 해석 규칙의 두 분기 어느 쪽도 깔끔히 적용되지 않음을 그대로 보고. | — |
| R5 | "RAG" 조건이 실제 검색이 아니다. | **이번에 수정**: 항목당 claim ≤3개라 top-3가 전부이며, 실제 조작은 *메타데이터 제거*임을 본문·표·Methods에 명시. | 방해 문서가 섞인 코퍼스 검색 baseline (P1-2) |
| R6 | 인간 검증(IAA)이 없다. | 70문항 blind 패킷·Kaggle 노트북 준비 완료, v0.2로 재생성. | 주석자 3명 실측 (P0-3) |
| R7 | 통계: 군집이 7개뿐이라 bootstrap CI가 불안정. | **이번에 수정**: Methods에 "7개 군집, 근사·경계값 가능, 서술적 보고" 명시. | 더 많은 시나리오 패밀리 (P0-2와 함께) |
| R8 | "situation engineering"이 기존 개념(situation calculus, DST, belief revision)의 **재명명**이 아닌가. | Methods "Relation to prior formalisms"에서 차이를 명시. | 심사 대응에서 비교표 강조 (P2) |

---

## 2. 제목 결정

**현 제목 유지(최종).** "Situation engineering: separating evidence applicability from availability
in AI systems"는 E6/E7 이후에도 정확하다: E6에서 같은 claim이라도 timestamp가 없으면 시간 의존 항목이
23–50%로 무너지고(가용성≠적용성), situation 프롬프트 효과는 주장하지 않는다. 대안 "Evidence
applicability, not availability, limits …"는 E7이 LLM 센서에서 sensing gap 대부분이 사라짐을 보였으므로
*인과적 병목*을 단정하는 제목은 오히려 근거가 약해졌다. 따라서 변경하지 않는다.

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
- **E6 (P0-1)**: 사전 등록 → Amendment 1(비용) → Meta·DeepSeek·Qwen 3,258건 실행, 실패 0, reasoning token 0,
  감사 PASS. Extended Data Table 2·4 추가, 결과 섹션 재작성. 사후 민감도 분석은 별도 표기.
- **E7 (P1-1 재설계)**: LLM 센서 4종, Extended Data Table 5. 보관 JSON을 사후 매핑하는 원안 대신, 사후
  조정 위험이 없는 사전 등록 센서 과제로 바꿈.
- `audit_multifamily.py`가 게이트웨이를 하나의 패밀리로 세던 오류를 개발사 기준으로 수정(테스트 추가).
- 초록 148/150, 본문 3,408/3,500단어, 디스플레이 항목 ≤6, Extended Data 5개(인용 순서), overfull 0.

---

## 4. Accept를 위한 필수 TODO (우선순위)

### P0 — 없으면 거절 가능성이 높음 (추가 실험·검증 필요)

**P0-1. 독립 모델 패밀리로 E5 확장** — *R2, R3* — **완료(오픈웨이트 3개 패밀리)**
- 결과: 판정 규칙 미충족(차이 없음), H2는 모든 패밀리에서 성립. 원고 반영 완료.

**P0-1b. 독점 패밀리 추가(남은 공백)** — *R3*
- `anthropic/claude-sonnet-5.5`, `openai/gpt-6.1-sol`로 `code/run_e6_e7.sh`의 모델 목록만 바꿔 실행.
  새 사전 등록 Amendment로 고정한 뒤 실행할 것. 예상 비용: 원래 실행이 약 $5에서 소진된 점으로 볼 때
  **$15–30 이상**(실행 전 OpenRouter 가격표로 확인). 담당: 크레딧 충전 후 Claude 실행 가능.

**P0-2. 독립 저자의 자연어 평가** — *R1, R7*
- 내용: 생성기를 모르는 사람이 쓴 자연 질문·증거(목표 1,200 시나리오, 3개 도메인; 보충 Note 14의
  사전 명세). 최소한 SituatedQA 전체 temporal split 등 공개 자연 벤치마크로 12개 스모크 테스트를 대체.
- 담당: 데이터 라이선스·저자 섭외는 사용자, 실행·분석은 Claude 가능.

**P0-3. 인간 주석 일치도(IAA) 실측** — *R6*
- 내용: v0.2 패킷 3개를 독립 주석자 3명이 작성 → Kaggle 노트북으로 Fleiss κ 산출.
- 담당: **사용자**(주석자 섭외). 절차: `paper/annotation_packets/KAGGLE_STEP_BY_STEP.md`.

### P1 — 심사 통과 가능성을 크게 높임

**P1-1. LLM의 state 추출 정확도 직접 측정** — *R4* — **완료(E7)**
- 남은 점: claim-level slot 점수는 어휘 차이로 결정 정확도와 잘 맞지 않음(본문에 명시). 의미 기반 slot
  매핑은 새 사전 등록 없이는 하지 않는다.

**P1-2. 방해 문서가 포함된 실제 검색 baseline** — *R5*
- 내용: 항목별 claim에 다른 항목의 claim(방해물)을 섞은 코퍼스에서 top-k 검색. "관련성 ≠ 적용성"을 검색 문제로 검증.

**P1-3. 사전 등록**: E6/E7은 git 커밋으로 완료. P0-2는 실행 전 같은 방식으로 고정하고, 가능하면 OSF에도 등록.

**P1-4. E6 자연어 점검 확대**: 현재 SituatedQA 12문항(스모크 테스트). 전체 temporal split으로 확대.

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

## 6. 판단 요약 (E6/E7 이후)

**예상 결정: major revision 가능 수준, 단 desk reject 위험은 여전히 중간.** R3·R4는 상당 부분 해소되었고
R2는 다중 패밀리 null로 "결과가 일반적"임을 보였다. 남은 핵심 거절 사유는 **R1(합성 벤치마크)과 R6(인간
검증 없음)**이며, 이는 사람·데이터가 필요하다(P0-2, P0-3). 독점 패밀리 부재(P0-1b)는 심사자가 지적할
가능성이 높지만 비용만으로 해결된다. 지금 제출한다면 커버레터 Version A(업데이트됨)를 쓰되, P0-2·P0-3
없이 Article로 내는 위험을 감수하는 것이고, 보수적으로는 Version B(presubmission enquiry)가 안전하다.
