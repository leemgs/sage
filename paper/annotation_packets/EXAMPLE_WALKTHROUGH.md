# 작성 사례집 (해설 포함) — 주석 중 옆에 두고 참고하세요

각 사례는 **질문 → 근거(claim) → 채운 값 → 왜 그렇게 채웠는지**를 보여줍니다.
7개 카테고리 각각에서 **핵심이 되는 열(굵게)** 이 무엇인지에 주목하세요. 나머지 열은
대개 기본값(temporal_state=stable, modality=confirmed, scope=global, source_status=reliable,
observer_state=shared, world=actual)이고, **그 문항의 성격을 결정하는 한 열만 달라집니다.**

> 판단이 애매하면 본인 판단으로 고르세요. "정답 맞히기"가 아니라 **독립적 판단**이 목적입니다.

---

## 사례 1 — temporal (시점에 따라 답이 바뀜)
**질문(t=11):** Who is the current director at time 11?
**근거:** (t6) Bora 임명 · (t8) Bora 사임 · (t9) Juno 임명 — 모두 official·confirmed
**채운 값:** action=`ANSWER`, answer=`Juno`, **temporal_state=`relevant`**, modality=confirmed, scope=global, source_status=reliable, observer_state=shared, world=actual
**해설:** 디렉터가 시간에 따라 바뀌므로 t11 기준 최신 유효값은 Juno. 답이 **질의 시점에 좌우**되므로 temporal_state=`relevant`.

## 사례 2 — counterfactual (현실 vs 가정)
**질문(t=12):** In the hypothetical scenario, can users access service Alpha?
**근거:** (t10) 현실: Alpha offline (scope=reality) · (t11) 가정 시나리오: Alpha online (scope=counterfactual, status=assumed)
**채운 값:** action=`ANSWER`, answer=`yes`, temporal_state=stable, modality=confirmed, scope=global, source_status=reliable, observer_state=shared, **world=`counterfactual`**
**해설:** 질문이 "가정 시나리오"를 물으므로 가정 세계의 사실(online)을 따름 → yes. 질문이 **가정 세계**를 대상으로 하므로 world=`counterfactual`.

## 사례 3 — hidden_premise (답에 필요한 정보가 빠짐)
**질문(t=12):** Can I register now?
**근거:** (t9) Registration open **for Delta residents** until day 14 (scope=Delta)
**채운 값:** **action=`CLARIFY`**, answer=`CLARIFY`, temporal_state=stable, modality=confirmed, **scope=`limited`**, source_status=reliable, observer_state=shared, world=actual
**해설:** 등록은 "Delta 주민"에게만 열림(scope=`limited`). 질문자가 Delta 주민인지 **정보가 없어 답할 수 없음** → action=`CLARIFY`.

## 사례 4 — source_conflict (출처가 서로 충돌)
**질문(t=10):** Who is the director?
**근거:** (t8) 익명 글: Juno (status=rumor) · (t9) 공식 공지: Faye (status=confirmed)
**채운 값:** action=`ANSWER`, answer=`Faye`, temporal_state=stable, modality=confirmed, scope=global, **source_status=`conflict`**, observer_state=shared, world=actual
**해설:** 두 출처가 다른 사람을 지목 → source_status=`conflict`. 신뢰 가능한 공식 출처를 채택 → Faye.

## 사례 5 — modality (확정 vs 제안·미결정)
**질문(t=6):** Has Beta been closed?
**근거:** (t4) 이사회가 폐쇄 **검토 중** (status=proposed) · (t5) **아직 결정 없음** (confirmed)
**채운 값:** action=`ANSWER`, answer=`no`, temporal_state=stable, **modality=`proposed`**, scope=global, source_status=reliable, observer_state=shared, world=actual
**해설:** 폐쇄는 제안·검토 단계일 뿐 결정되지 않음 → modality=`proposed`, 따라서 "폐쇄됐는가?"엔 no.

## 사례 6 — observer (관찰자가 아는 것 vs 실제)
**질문(t=8):** Does Luca believe the meeting will occur?
**근거:** (t5) Luca는 회의 초대를 받음 · (t7) 회의 취소됨 — **단 Luca는 취소 통보를 못 받음** (observed_by=Ivan,Dina)
**채운 값:** action=`ANSWER`, answer=`yes`, temporal_state=stable, modality=confirmed, scope=global, source_status=reliable, **observer_state=`partial`**, world=actual
**해설:** 실제로는 취소됐지만 **Luca의 지식 상태**에는 취소가 없음 → Luca는 회의가 열린다고 믿음(yes). 관찰자가 일부만 앎 → observer_state=`partial`.

## 사례 7 — scope (전체 vs 일부·조건부)
**질문(t=11):** Does the restructuring apply to every unit?
**근거:** (t10) 구조조정은 **Alpha 유닛에만** 적용 (scope=Alpha)
**채운 값:** action=`ANSWER`, answer=`no`, temporal_state=stable, modality=confirmed, **scope=`limited`**, source_status=reliable, observer_state=shared, world=actual
**해설:** Alpha에만 적용되므로 "모든 유닛에 적용되는가?"엔 no. 적용 범위가 일부 → scope=`limited`.

---

## 빠른 요약 — 카테고리별 "이 열만 특별히 보라"
| 카테고리 | 특별히 결정적인 열 | 전형적 값 |
|----------|-------------------|-----------|
| temporal | temporal_state | `relevant` |
| counterfactual | world | `counterfactual` |
| hidden_premise | action (+ scope) | `CLARIFY` (+ `limited`) |
| source_conflict | source_status | `conflict` |
| modality | modality | `proposed` |
| observer | observer_state | `partial` |
| scope | scope | `limited` |

나머지 열은 기본값(stable / confirmed / global / reliable / shared / actual)에서 시작해,
근거를 읽고 달라지는 경우에만 바꾸면 됩니다. 허용값 전체 목록은 `HOW_TO_ANNOTATE.md`의 코드북을 보세요.
