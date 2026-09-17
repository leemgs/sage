# 인간 IAA 주석 안내 (How to annotate) — 이대로만 하시면 됩니다

이 폴더로 **인간 inter-annotator agreement(IAA)** 를 측정합니다. 목표: 서로 독립적인
**사람 3명**이 같은 70개 문항의 "상황 상태"를 각자 판단해 채우면, 그 일치도(Fleiss κ)를
계산해 벤치마크 gold 라벨이 사람 판단과 일치하는지 검증합니다.

---

## 0) 당신(연구자)이 직접 해야 할 일 — 5단계

1. **주석자 3명 섭외** (동료/학생 등, 서로 상의하지 않고 독립 작업).
2. 각자에게 파일 1개씩 배부:
   - 주석자 1 → `annotator_1.csv`
   - 주석자 2 → `annotator_2.csv`
   - 주석자 3 → `annotator_3.csv`
   (세 파일은 문항 순서가 서로 섞여 있습니다. 정상입니다.)
3. 각 주석자는 **빈 칸 9개 열만 채웁니다** (아래 §2 코드북 참고). 나머지 열은 **절대 수정 금지**.
4. 채운 CSV 3개를 **파일명 그대로** 저에게 주세요 (예: `annotator_1.csv` 등).
5. 그러면 제가 `code/annotation_cli.py score --provenance human_annotations` 로
   **Fleiss κ + 불일치표(adjudication)** 를 계산하고 논문 Methods/Results에 반영합니다.

> 📎 **정답 예시 파일**: `EXAMPLE_annotator_filled.csv` — 7개 문항을 올바르게 채운 예시입니다.
> 각 주석자에게 "이렇게 채우면 된다"고 보여주세요. (이건 예시일 뿐, 실제 채점엔 안 들어갑니다.)

---

## 1) 절대 규칙
- **`blind_id, item_id, question, evidence` 4개 열은 그대로 둡니다** (내용/순서 변경 금지).
- 주석자끼리 **답을 상의하지 않습니다** (독립성이 핵심).
- 모든 문항의 9개 열을 **빠짐없이** 채웁니다 (빈 칸이 있으면 채점이 거부됩니다).
- 아래 코드북의 **정해진 값만** 사용합니다 (오타·대소문자 주의).

---

## 2) 코드북 — 채워야 하는 9개 열과 허용값

각 문항의 `question`(질문)과 `evidence`(claim들의 JSON)를 읽고 판단합니다.

| 열 | 뜻 (질문에 답할 때 이 문항의 상태는?) | 허용값 |
|----|------|--------|
| **action** | 답할 수 있는가, 아니면 정보가 부족/확인필요인가 | `ANSWER` / `CLARIFY` / `ABSTAIN` |
| **answer** | action이 ANSWER면 **실제 정답**(예: `Juno`, `yes`, `no`, 날짜). ANSWER가 아니면 그 토큰(`CLARIFY` 또는 `ABSTAIN`)을 그대로 | 자유 텍스트 또는 `CLARIFY`/`ABSTAIN` |
| **temporal_state** | 정답이 **질의 시점(time)에 따라 달라지는가** | `relevant`(시점에 따라 바뀜) / `stable`(시점 무관) |
| **modality** | 근거가 **확정된 사실인가, 제안/검토 단계인가** | `confirmed`(확정) / `proposed`(제안·미결정) |
| **scope** | 답이 **전체에 적용되는가, 일부/조건부인가** | `global`(전체) / `limited`(일부·조건부) |
| **source_status** | 출처들이 **일치하는가, 충돌하는가** | `reliable`(일관/신뢰) / `conflict`(출처 충돌) |
| **observer_state** | 질문 속 관찰자가 **필요한 정보를 다 아는가** | `shared`(공유된 지식) / `partial`(관찰자가 일부만 앎) |
| **world** | 질문이 **현실 세계인가, 가정(반사실) 시나리오인가** | `actual`(현실) / `counterfactual`(가정) |
| **notes** | (선택) 자유 메모. 채점에 안 들어감 | 자유 텍스트 (비워도 됨) |

> 판단이 애매하면 본인이 가장 타당하다고 보는 값을 고르세요 — **불일치 자체가 측정 대상**이므로
> "정답을 맞히는" 게 아니라 **독립적 판단**이 중요합니다.

---

## 3) 채우는 예시 (실제 문항 기준)

`EXAMPLE_annotator_filled.csv`의 행을 그대로 옮기면:

| item_id | action | answer | temporal_state | modality | scope | source_status | observer_state | world |
|---------|--------|--------|----------------|----------|-------|----------------|----------------|-------|
| temporal-0165 (현재 디렉터?) | ANSWER | Juno | relevant | confirmed | global | reliable | shared | actual |
| counterfactual-0486 (가정 시나리오) | ANSWER | yes | stable | confirmed | global | reliable | shared | **counterfactual** |
| hidden_premise-0153 (지금 등록 가능?) | **CLARIFY** | CLARIFY | stable | confirmed | **limited** | reliable | shared | actual |
| source_conflict-0462 (디렉터 누구?) | ANSWER | Faye | stable | confirmed | global | **conflict** | shared | actual |
| observer-0575 (Luca가 믿는가?) | ANSWER | yes | stable | confirmed | global | reliable | **partial** | actual |

---

## 4) 다 채운 뒤
- 채운 `annotator_1.csv`, `annotator_2.csv`, `annotator_3.csv` **3개 파일을 저에게 전달**하세요.
- 제가 자동으로:
  1. `annotation_cli.py score --provenance human_annotations` → 슬롯별 **Fleiss κ, 만장일치율**
  2. `annotation_cli.py adjudicate` → **불일치 문항표**
  3. 결과를 논문(Methods "Human evaluation" + Results/Evidence ladder)과 `RESPONSE_TO_REVIEWERS.md`의 M-B 항목에 반영.

이게 끝나면 리뷰어의 최대 요구사항(인간 검증)이 "준비됨"에서 "실측 완료"로 바뀝니다.
