# 주석자 모집 안내 / Annotator recruitment guide

이 문서는 연구자(저자)가 주석자 3명을 모집할 때 그대로 보내거나 참고할 수 있는 안내문입니다.
아래 영어 본문은 한국어를 읽지 않는 주석자에게 보낼 수 있습니다.
This page can be sent as is to prospective annotators; the English part is self-contained.

---

## 한국어

### 무엇을 하나요?
- 짧은 영어 질문 70개와 각 질문에 딸린 근거 문장(1–3개)을 읽고, 표의 9개 칸을 채웁니다.
  각 칸은 정해진 값 중 하나를 고릅니다(예: `ANSWER` / `CLARIFY` / `ABSTAIN`).
- 목적은 "정답 맞히기"가 아니라, **사람들이 각자 판단했을 때 얼마나 일치하는지**를 재는 것입니다.
- 예상 소요 시간: 처음 30분은 안내서와 예시 7개를 읽고, 이후 문항당 1–2분 → **총 2–3시간** 정도.

### 누가 할 수 있나요?
- 영어 문장을 읽고 이해할 수 있는 사람(전공 무관). 이 연구의 저자·코드 작성자는 제외합니다.
- 세 사람은 **서로 상의하지 않고** 각자 작업해야 합니다. 논문 원고나 코드(정답이 들어 있음)를
  미리 보지 않아야 합니다.

### 보상과 동의
- 이 연구는 펀딩이 없는 공개 연구입니다. 보상 여부와 방식은 연구자가 정하며, 사전에 알려야 합니다.
- 주석자의 이름은 원하는 경우에만 논문 감사의 글에 넣습니다. 수집하는 것은 채운 표뿐이며,
  주석자에 대한 개인정보는 수집하지 않습니다.
- 소속 기관에 따라 이런 주석 작업도 연구윤리(IRB) 확인이 필요할 수 있으니, 시작 전에 확인하세요.

### 진행 순서
1. 각자에게 자기 번호의 패키지를 보냅니다(`annotator_N_package.zip`: 엑셀 파일, 같은 내용의
   CSV, 주석자 지침 `ANNOTATOR_INSTRUCTIONS.md`, 예시). 패키지는
   `python code/annotation_workbooks.py make`로 만든 엑셀에 지침과 예시를 더한 것입니다.
   세 사람이 같은 70문항을 받지만 순서가 섞여 있습니다.
2. 함께 보낼 안내서: `HOW_TO_ANNOTATE.md`(코드북), `EXAMPLE_WALKTHROUGH.md`와
   `EXAMPLE_annotator_filled.csv`(예시 7개 — 주석할 70문항에는 들어 있지 않음).
   영어 사용자에게는 이 문서의 영어 본문을 함께 보냅니다.
3. 주석자는 Excel이나 Google Sheets에서 9개 칸만 채우고 **CSV로 저장**해 돌려줍니다
   (Excel의 "CSV UTF-8"도 괜찮습니다). 대소문자나 앞뒤 공백은 자동으로 맞춰지지만,
   코드북에 없는 값이 있으면 채점이 멈추고 어느 칸인지 알려 줍니다.
4. 엑셀로 돌려받으면 `python code/annotation_workbooks.py to-csv --xlsx annotator_N.xlsx
   --out filled/annotator_N.csv`로 CSV로 바꿉니다(고정 열은 원본 패킷에서 복원).
   채운 파일 3개를 Claude에게 주면 Fleiss κ와 불일치표를 계산해 논문에 반영합니다.
   직접 계산하려면 `KAGGLE_STEP_BY_STEP.md`를 따르세요.

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
1. Open your file (`annotator_1.csv`, `annotator_2.csv` or `annotator_3.csv`) in Excel or
   Google Sheets. **Do not change** the columns `blind_id`, `item_id`, `question`, `query_time`, `evidence`.
   `query_time` is when the question is asked, on the same scale as the evidence times;
   "now" and "current" refer to it.
2. For every row, fill the columns below. `notes` is optional.
3. Save as CSV with the same file name (Excel's "CSV UTF-8" is fine) and send it back.

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
