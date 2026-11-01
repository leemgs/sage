# 작성 사례집 (해설 포함) — 주석 중 옆에 두고 참고하세요

각 사례는 **질문 → 근거(claim) → 채운 값 → 왜 그렇게 채웠는지**를 보여줍니다.
7개 사례는 실제 패킷 문항이며 `EXAMPLE_annotator_filled.csv`에 같은 값으로 들어 있습니다.
7개 카테고리 각각에서 **핵심이 되는 열(굵게)** 이 무엇인지에 주목하세요. 나머지 열은
대개 기본값(temporal_state=stable, modality=confirmed, scope=global, source_status=reliable,
observer_state=shared, world=actual)이고, **그 문항의 성격을 결정하는 한 열만 달라집니다.**

> **중요 — 같은 카테고리라도 정답은 문항마다 다릅니다.** 이 벤치마크(v0.2)는 카테고리마다
> 정답이 yes/no(또는 질문/답변)로 고르게 섞여 있고, **가장 최근 주장이 정답이 아닌 경우가 절반**입니다.
> "보통 이렇더라"로 채우지 말고, 매 문항의 근거를 읽고 판단하세요.

> 판단이 애매하면 본인 판단으로 고르세요. "정답 맞히기"가 아니라 **독립적 판단**이 목적입니다.

---

## 사례 1 — temporal (질의 시점이 결정함) · `temporal-0079`
**질문(t=5):** Who is the current manager at time 5?
**근거:** (t3) Hana 임명 · (t8) Hana 사임 · (t9) Bora 임명 — 모두 official·confirmed
**채운 값:** action=`ANSWER`, answer=`Hana`, **temporal_state=`relevant`**, modality=confirmed, scope=global, source_status=reliable, observer_state=shared, world=actual
**해설:** 질의 시점 t=5는 사임(t8)과 Bora 임명(t9)보다 **이전**입니다. 그 시점의 담당자는 Hana.
가장 최근 주장(Bora)을 고르면 틀립니다. 답이 질의 시점에 좌우되므로 temporal_state=`relevant`.

## 사례 2 — counterfactual (현실 vs 가정) · `counterfactual-0233`
**질문(t=18):** In the hypothetical scenario, can users access service Alpha?
**근거:** (t16) 현실: Alpha online (scope=reality) · (t17) 가정 시나리오: Alpha **offline** (scope=counterfactual, status=assumed)
**채운 값:** action=`ANSWER`, answer=`no`, temporal_state=stable, modality=confirmed, scope=global, source_status=reliable, observer_state=shared, **world=`counterfactual`**
**해설:** 질문은 가정 세계를 묻습니다. 가정에서는 offline → no. 현실(online)과 섞지 마세요.

## 사례 3 — hidden_premise (답에 필요한 정보가 빠짐) · `hidden_premise-0008`
**질문(t=13):** Can I register now?
**근거:** (t10) Registration is open **for Beta residents** until day 15 (scope=Beta)
**채운 값:** **action=`CLARIFY`**, answer=`CLARIFY`, temporal_state=stable, modality=confirmed, **scope=`limited`**, source_status=reliable, observer_state=shared, world=actual
**해설:** 등록은 Beta 주민에게만 열림(scope=`limited`). 질문자가 Beta 주민인지 **정보가 없어** 답할 수 없음 → `CLARIFY`.

## 사례 4 — source_conflict (출처가 서로 충돌) · `source_conflict-0371`
**질문(t=12):** Who is the lead?
**근거:** (t10) 공식 공지: Bora (status=confirmed) · (t11) 익명 글: Luca (status=rumor)
**채운 값:** action=`ANSWER`, answer=`Bora`, temporal_state=stable, modality=confirmed, scope=global, **source_status=`conflict`**, observer_state=shared, world=actual
**해설:** 두 출처가 다른 사람을 지목 → `conflict`. **더 최근인 것은 익명 소문**이지만, 신뢰할 수 있는 공식 공지를 채택 → Bora.

## 사례 5 — modality (확정 vs 제안·미결정) · `modality-0478`
**질문(t=5):** Has Alpha been closed?
**근거:** (t3) 아직 결정 없음 (confirmed) · (t4) 이사회가 폐쇄 **검토 중** (status=proposed)
**채운 값:** action=`ANSWER`, answer=`no`, temporal_state=stable, **modality=`proposed`**, scope=global, source_status=reliable, observer_state=shared, world=actual
**해설:** 가장 최근 주장이 "폐쇄 검토 중"이지만 **제안일 뿐 결정이 아님** → modality=`proposed`, 폐쇄되지 않음(no).

## 사례 6 — observer (관찰자가 아는 것 vs 실제) · `observer-0420`
**질문(t=19):** Does Dina believe the meeting will occur?
**근거:** (t16) Dina는 회의 초대를 받음 · (t18) 회의 취소됨 — **단 Dina는 취소 통보를 못 받음** (observed_by=Hana, Cato)
**채운 값:** action=`ANSWER`, answer=`yes`, temporal_state=stable, modality=confirmed, scope=global, source_status=reliable, **observer_state=`partial`**, world=actual
**해설:** 실제로는 취소됐지만 Dina의 지식에는 취소가 없음 → Dina는 회의가 열린다고 믿음(yes).

## 사례 7 — scope (전체 vs 일부·조건부) · `scope-0121`
**질문(t=20):** Does the restructuring apply to every unit?
**근거:** (t19) A restructuring applies **to every unit** (scope=global)
**채운 값:** action=`ANSWER`, answer=`yes`, temporal_state=stable, modality=confirmed, **scope=`global`**, source_status=reliable, observer_state=shared, world=actual
**해설:** 모든 유닛에 적용 → yes, scope=`global`. ("**only** the Alpha unit"이면 no, scope=`limited`.)

---

## 같은 카테고리의 반대 경우 — 패킷에서 만나게 됩니다

| 카테고리 | 이런 문항이면 | 채우는 법 |
|----------|--------------|-----------|
| hidden_premise | 질문에 "**I live in Beta.** Can I register now?"처럼 전제가 주어짐 | 근거의 지역과 같으면 `ANSWER`/`yes`, 다르면 `ANSWER`/`no` (scope는 `limited`) |
| modality | "The board **voted to close** Alpha." (confirmed)가 있음 | answer=`yes`, modality=`confirmed` |
| observer | "…and **Dina received** the cancellation." | answer=`no` (Dina는 취소를 앎), observer_state=`shared` |
| counterfactual | 가정 시나리오에서 online, 현실은 offline | answer=`yes`, world=`counterfactual` |
| temporal | 질의 시점이 모든 사건 **이후** | 가장 나중에 임명된 사람 |
| source_conflict | 공식 공지가 더 최근 | 역시 공식 공지의 인물 |

## 빠른 요약 — 카테고리별 "이 열만 특별히 보라"
| 카테고리 | 특별히 결정적인 열 | 값은 문항마다 다름 |
|----------|-------------------|-------------------|
| temporal | temporal_state | 보통 `relevant` (답은 질의 시점 기준) |
| counterfactual | world | `counterfactual` (답은 가정 세계 기준) |
| hidden_premise | action (+ scope) | 전제 없으면 `CLARIFY`, 있으면 `ANSWER` |
| source_conflict | source_status | `conflict` (답은 신뢰 출처 기준) |
| modality | modality | 제안뿐이면 `proposed`, 결정됐으면 `confirmed` |
| observer | observer_state | 통보 못 받았으면 `partial`, 받았으면 `shared` |
| scope | scope | 일부면 `limited`, 전체면 `global` |

나머지 열은 기본값(stable / confirmed / global / reliable / shared / actual)에서 시작해,
근거를 읽고 달라지는 경우에만 바꾸면 됩니다. 허용값 전체 목록은 `HOW_TO_ANNOTATE.md`의 코드북을 보세요.
