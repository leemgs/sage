# Kaggle에서 인간 IAA 실행하기 — 복사/붙여넣기 STEP BY STEP

이 문서 하나만 따라 하면 됩니다. **사람 주석자 3명**이 70문항을 채우고,
Kaggle에서 노트북을 돌려 **Fleiss κ + 불일치표**를 뽑아 저에게 주시면
논문의 리뷰어 요구사항 **M-B(인간 검증)** 가 "실측 완료"로 바뀝니다.

노트북은 두 가지가 있습니다. **A안(권장)** 을 먼저 시도하고, 인터넷을 못 켜면 **B안** 을 쓰세요.

| | A안 · Handoff (권장) | B안 · Self-contained (인터넷 불가 시) |
|---|---|---|
| 파일 | `SituationCatch_HumanIAA_Handoff_Kaggle.ipynb` | `human_iaa_kaggle.ipynb` |
| 인터넷 | **필요** (Settings→Internet→On) | 불필요 |
| 하는 일 | 저장소 자동 clone + 실제 CLI 실행 + 파이프라인 자가검증 | 채점 로직 내장, clone 없음 |
| 준비물 | 채운 CSV 3개만 업로드 | 노트북 + 채운 CSV 3개 업로드 |

---

## STEP 1 — 주석자 3명에게 나눠줄 파일 받기 (연구자 = 당신)

저장소 `paper/annotation_packets/` 에서 아래 5개를 내려받습니다
(GitHub 웹에서 파일 열고 **Download raw** 또는 저장소를 clone).

- `annotator_1.csv`, `annotator_2.csv`, `annotator_3.csv`  ← **주석자에게 1개씩 배부**
- `HOW_TO_ANNOTATE.md`  ← 코드북(채우는 규칙)
- `EXAMPLE_WALKTHROUGH.md`  ← 7개 카테고리 작성 사례(해설 포함)

> 원링크(복사용):
> - https://github.com/leemgs/sage/blob/main/paper/annotation_packets/annotator_1.csv
> - https://github.com/leemgs/sage/blob/main/paper/annotation_packets/annotator_2.csv
> - https://github.com/leemgs/sage/blob/main/paper/annotation_packets/annotator_3.csv

---

## STEP 2 — 주석자 3명이 각자 CSV 채우기 (서로 상의 금지)

각 CSV의 **9개 열**만 채웁니다 (`notes`는 선택). 나머지 4개 열
(`blind_id, item_id, question, evidence`)은 **절대 수정 금지**.

| 열 | 허용값 |
|----|--------|
| action | `ANSWER` / `CLARIFY` / `ABSTAIN` |
| answer | 실제 정답(예: `Juno`, `yes`, `no`) 또는 `CLARIFY`/`ABSTAIN` |
| temporal_state | `relevant` / `stable` |
| modality | `confirmed` / `proposed` |
| scope | `global` / `limited` |
| source_status | `reliable` / `conflict` |
| observer_state | `shared` / `partial` |
| world | `actual` / `counterfactual` |
| notes | (선택) 자유 메모 |

- Excel/Google Sheets로 열어 채운 뒤 **CSV(UTF-8)로 다시 저장**, 파일명은 그대로.
- 채우는 법이 헷갈리면 `EXAMPLE_WALKTHROUGH.md`의 7개 사례를 그대로 참고.
- 규칙: 3명 독립 작성 · 빈 칸 없이 전부 채움 · 코드북 값만 사용(오타/대소문자 주의).

---

## STEP 3-A — Kaggle 실행 (A안 · 권장, 인터넷 ON)

1. https://www.kaggle.com 로그인 → 우측 상단 **Create → New Notebook**
2. 상단 **File → Import Notebook → GitHub** 탭에 아래 URL 붙여넣기(복사용):
   ```
   https://github.com/leemgs/sage/blob/main/paper/annotation_packets/SituationCatch_HumanIAA_Handoff_Kaggle.ipynb
   ```
   (GitHub 탭이 없으면 **Link** 탭에 위 URL, 또는 파일을 내려받아 **File → Import Notebook → Upload**)
3. 우측 패널 **Settings → Internet → On** (저장소 clone에 필요; 계정 전화인증 필요할 수 있음)
4. **Run All** — STEP 0~3까지 초록불(합성 κ 출력)이면 환경 정상.
   - 이때 STEP 3은 *합성 페르소나* 검증이라 논문에 안 들어갑니다(자동 표시됨).
5. 채운 CSV 3개 업로드: 우측 **+ Add Input → Upload → Upload a Dataset** 에
   `annotator_1.csv`, `annotator_2.csv`, `annotator_3.csv` 올리고 **Create**.
6. 다시 **Run All**. STEP 4가 `provenance = human_annotations` 로 **실측 κ** 를 출력하고
   STEP 5가 불일치표, STEP 6이 `human_iaa_results.zip` 을 만듭니다.
7. 우측 **Output** 패널에서 `human_iaa_results.zip` 다운로드.

> A안은 채점 코드를 저장소에서 그대로 clone해 쓰므로, `/kaggle/input` 에 올린 CSV만
> 자동으로 가져옵니다. 합성 데이터(`SIMULATION_MANIFEST.json` 있는 폴더)는
> 자동으로 제외되어, 합성이 사람 데이터로 잘못 채점되는 일이 없습니다.

---

## STEP 3-B — Kaggle 실행 (B안 · 인터넷 불가 시)

인터넷을 못 켜는 계정이면 이 방법을 쓰세요. clone 없이 노트북 안에 채점 로직이 들어 있습니다.

1. `human_iaa_kaggle.ipynb` 를 저장소에서 내려받기(복사용):
   ```
   https://github.com/leemgs/sage/blob/main/paper/annotation_packets/human_iaa_kaggle.ipynb
   ```
2. Kaggle **Create → New Notebook → File → Import Notebook → Upload** 로 위 파일 업로드.
3. **+ Add Input → Upload** 로 채운 `annotator_1/2/3.csv` 업로드(인터넷 OFF 그대로 OK).
4. **Run All** → `/kaggle/working` 에 `agreement.json`, `adjudication.csv`,
   `human_iaa_results.zip` 생성 → **Output** 패널에서 다운로드.

---

## STEP 4 — 결과를 저에게 전달

`human_iaa_results.zip` (또는 그 안의 `agreement.json` + `adjudication.csv`)을 주세요.
제가 자동으로:
1. 논문 **Methods "Human evaluation"** 에 3인 IAA 설계와 측정된 Fleiss κ 삽입,
2. **Results / Evidence ladder** 에 실측 일치도 반영,
3. `RESPONSE_TO_REVIEWERS.md` 의 **M-B** 를 "준비됨" → "실측 완료"로 갱신,
4. PDF 재빌드 후 `main` 에 push.

---

## 자주 나는 오류 (fail-closed 메시지)

코드는 무결성을 위해 **문제가 있으면 채점을 거부**합니다. 메시지대로 고치고 다시 Run All 하세요.

| 메시지 | 원인 · 해결 |
|--------|-------------|
| `Need at least three completed annotator files.` | CSV가 3개 미만. 3개 모두 업로드. |
| `Missing <slot> in ...: <item_id>` | 그 파일의 해당 문항 열이 비어 있음. 채우기. |
| `Mismatched item set in ...` | 4개 고정 열을 건드려 item_id가 달라짐. 원본 packet에서 다시 시작. |
| `Duplicate item_id in ...` | 행을 복사하다 중복. 중복 행 제거. |
| `Refusing to infer human provenance...` | (수동 실행 시) `--provenance human_annotations` 누락. 노트북은 자동 처리하므로 Run All만. |

---

## 참고 — 이건 제가 못 하는 부분 (사람만 가능)

- **주석자 3명의 독립 판단** 은 사람만 할 수 있습니다(그게 IAA의 정의). 저는 파이프라인·
  노트북·검증까지만 준비했고, 실제 라벨은 STEP 2에서 사람이 넣어야 합니다.
- **Zenodo DOI** 는 당신의 계정 연동이 필요합니다(Kaggle과 무관, 별도 안내 참고).
