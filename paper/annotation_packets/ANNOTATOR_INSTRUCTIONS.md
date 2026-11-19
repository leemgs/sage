# 주석자 지침 / Annotator instructions

## 한국어

이 연구에 참여해 주셔서 감사합니다. 이 작업은 펀딩이 없는 공개 연구를 돕는 자원 참여입니다.

### 하실 일
- 짧은 영어 질문 70개를 읽고, 각 질문에 딸린 근거 문장(1–3개)을 보고 9개 칸을 채웁니다.
- 정답을 맞히는 시험이 아닙니다. **서로 독립적으로 판단했을 때 얼마나 일치하는지**를 재는 것이 목적입니다.
  애매하면 가장 타당하다고 생각하는 값을 고르세요.
- 예상 시간: 지침과 예시 읽기 30분, 이후 문항당 1–2분 → 총 2–3시간.

### 규칙
- 다른 주석자와 **상의하지 마세요**. 논문 원고나 코드(정답이 들어 있음)를 미리 보지 마세요.
- 회색 칸 5개(`blind_id`, `item_id`, `question`, `query_time`, `evidence`)는 고치지 마세요.
- `query_time`은 질문을 받은 시점입니다. 근거의 `(t3)`, `(t8)` 같은 시점과 같은 눈금이며,
  "지금"·"현재"는 이 시점을 뜻합니다.
- 노란 칸 9개를 모든 문항에 빠짐없이 채우세요(`notes`는 선택). 엑셀 파일에서는 드롭다운으로 고릅니다.

### 각 칸의 뜻
| 칸 | 스스로에게 할 질문 | 고를 수 있는 값 |
|---|---|---|
| `action` | 근거만으로 답할 수 있는가, 꼭 필요한 정보가 빠졌는가? | `ANSWER`(답함), `CLARIFY`(빠진 정보를 되물음), `ABSTAIN`(답할 수 없음) |
| `answer` | `ANSWER`이면 답 자체(예: `Juno`, `yes`, `no`). 아니면 `CLARIFY`나 `ABSTAIN`을 그대로 | 자유 텍스트 |
| `temporal_state` | 답이 질문 시점에 따라 달라지는가? | `relevant`, `stable` |
| `modality` | 결정적인 근거가 확정된 사실인가, 제안·검토 중인가? | `confirmed`, `proposed` |
| `scope` | 결정적인 근거가 모두에게 적용되는가, 일부에게만인가? | `global`, `limited` |
| `source_status` | 출처들이 일치하는가, 충돌하는가? | `reliable`, `conflict` |
| `observer_state` | 질문 속 인물이 관련 정보를 모두 아는가? | `shared`, `partial` |
| `world` | 현실 세계에 대한 질문인가, 가정한 상황인가? | `actual`, `counterfactual` |
| `notes` | 메모(선택, 채점 안 함) | 자유 텍스트 |

예시 7개는 엑셀의 "Examples (not rated)" 시트와 `EXAMPLE_WALKTHROUGH.md`(해설 포함)에 있습니다.
이 예시는 여러분이 채울 70문항에 들어 있지 않습니다. 같은 범주라도 답은 문항마다 다르니
매 문항의 근거를 읽고 판단하세요.

### 다 채운 뒤
파일 이름을 바꾸지 말고 저장해서(`annotator_N.xlsx`, CSV로 작업했다면 `annotator_N.csv`)
연구자에게 보내 주세요. 수집하는 것은 이 표뿐이며 개인정보는 수집하지 않습니다.

---

## English

### What you will do
- Read 70 short English questions, each with one to three evidence statements, and fill in
  nine columns of a spreadsheet, choosing each value from a fixed list.
- The goal is not to find "the right answer" but to measure **how much independent people
  agree**. If an item is unclear, choose the value you find most reasonable.
- Expected time: about 30 minutes to read this guide and the seven worked examples, then
  1–2 minutes per item, **2–3 hours in total**.

### Who can take part
- Anyone who reads English comfortably; no special background is needed. Authors of the
  study and people who wrote its code cannot take part.
- Work **alone**: do not discuss items with the other annotators, and do not look at the
  manuscript or the code beforehand (they contain the reference answers).

### Steps
1. Open your workbook (`annotator_N.xlsx`) in Excel, LibreOffice or Google Sheets
   (a CSV copy, `annotator_N.csv`, is included if you prefer it). In the workbook the
   rating columns have drop-down lists and the fixed columns are locked. **Do not change** the columns `blind_id`, `item_id`, `question`, `query_time`, `evidence`.
   `query_time` is when the question is asked, on the same scale as the evidence times;
   "now" and "current" refer to it.
2. For every row, fill the columns below. `notes` is optional.
3. Save the workbook under the same file name (or, if you used the CSV, save it as CSV) and
   send it back to the researcher.

### Codebook

| Column | Question to ask yourself | Allowed values |
|---|---|---|
| `action` | Can the question be answered from the evidence, or is essential information missing or unreliable? | `ANSWER`, `CLARIFY` (ask the user for missing information), `ABSTAIN` (cannot answer) |
| `answer` | If `action` is `ANSWER`: the answer itself (e.g. `Juno`, `yes`, `no`). Otherwise repeat `CLARIFY` or `ABSTAIN`. | free text |
| `temporal_state` | Does the answer depend on the time the question is asked? | `relevant`, `stable` |
| `modality` | Is the decisive evidence a settled fact, or only proposed / under consideration? | `confirmed`, `proposed` |
| `scope` | Does the decisive evidence apply to everyone, or only to some people, places or units? | `global`, `limited` |
| `source_status` | Do the sources agree, or do they conflict? | `reliable`, `conflict` |
| `observer_state` | Does the person the question asks about know everything relevant? | `shared`, `partial` |
| `world` | Is the question about the real world or a hypothetical scenario? | `actual`, `counterfactual` |
| `notes` | Optional comments; not scored. | free text |

### Worked examples (not among your 70 items)

| Question (query time) | Evidence | Filled values |
|---|---|---|
| Who is the current chair at time 3? | t2 Juno appointed; t6 Juno resigned; t7 Faye appointed | `ANSWER`, `Juno`, **`relevant`**, confirmed, global, reliable, shared, actual — at time 3 Juno was still chair; the latest statement is not the answer. |
| In the hypothetical scenario, can users access service Beta? | t5 in reality Beta is online; t6 in the hypothetical scenario Beta goes offline | `ANSWER`, `no`, stable, confirmed, global, reliable, shared, **`counterfactual`** |
| Can I register now? (t12) | t9 registration is open for Beta residents until day 14 | **`CLARIFY`**, `CLARIFY`, stable, confirmed, **`limited`**, reliable, shared, actual — we do not know whether the asker lives in Beta. |
| Who is the coordinator? (t19) | t17 official notice: Hana; t18 anonymous post: Cato | `ANSWER`, `Hana`, stable, confirmed, global, **`conflict`**, shared, actual — the newer claim is only a rumour. |
| Has Alpha been closed? (t6) | t4 no decision has been made; t5 the board is considering closing Alpha | `ANSWER`, `no`, stable, **`proposed`**, global, reliable, shared, actual |
| Does Dina believe the meeting will occur? (t18) | t15 Dina received the invitation; t17 the meeting was cancelled, but Dina did not receive the cancellation | `ANSWER`, `yes`, stable, confirmed, global, reliable, **`partial`**, actual |
| Does the restructuring apply to every unit? (t18) | t17 a restructuring applies to every unit | `ANSWER`, `yes`, stable, confirmed, **`global`**, reliable, shared, actual |

Within one category the answer differs from item to item (for example, a question that
states where the asker lives can be answered), so read every item's evidence.

Thank you for contributing to open, unfunded research.
