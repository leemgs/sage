"""Schema-driven situation sensing, update, and response policy."""
from __future__ import annotations
import copy
import re
from typing import Any


def predict_claim(text: str) -> dict[str, Any]:
    """Infer the benchmark state slots from natural-language claim text.

    This deliberately transparent sensor is a reproducible baseline. It does
    not inspect gold state slots.
    """
    t = text.lower()
    out: dict[str, Any] = {"text": text}
    day = re.search(r"\bday\s+(\d+)\b", t)
    out["time"] = int(day.group(1)) if day else 0
    if "appointed" in t or " as " in t and "confirms" in t:
        out["event"] = "appoint"
    elif "resigned" in t:
        out["event"] = "resign"
    elif "cancel" in t:
        out["event"] = "cancel"
    elif "invitation" in t:
        out["event"] = "invite"
    elif "no decision" in t:
        out["event"] = "not_decided"
    elif "considering closing" in t:
        out["event"] = "close"
    elif "restructuring" in t:
        out["event"] = "restructure"
    elif "offline" in t:
        out["event"] = "offline"
    elif "online" in t:
        out["event"] = "online"
    elif "registration" in t:
        out["event"] = "eligibility"
    else:
        out["event"] = "unknown"
    out["status"] = (
        "rumor" if "anonymous" in t else
        "proposed" if "considering" in t else
        "assumed" if "hypothetical" in t else "confirmed"
    )
    out["source"] = (
        "anonymous" if "anonymous" in t else
        "official" if any(x in t for x in ("official", "board", "notice")) else
        "scenario" if "hypothetical" in t else "reported"
    )
    out["scope"] = (
        "counterfactual" if "hypothetical" in t else
        "reality" if "in reality" in t else
        "local" if "only" in t else "global"
    )
    actor = re.match(r"([A-Z][A-Za-z-]+)", text)
    out["actor"] = actor.group(1) if actor else ""
    return out


def predict_state(item: dict[str, Any]) -> dict[str, Any]:
    predicted = copy.deepcopy(item)
    predicted["claims"] = [predict_claim(c["text"]) for c in item["claims"]]
    predicted["state_source"] = "predicted_from_text"
    return predicted


def corrupt_state(item: dict[str, Any]) -> dict[str, Any]:
    x = predict_state(item)
    for c in x["claims"]:
        c["scope"] = "global"
        c["status"] = "confirmed"
        c["source"] = "reported"
    x["state_source"] = "deliberately_corrupted"
    return x


def _answer(value: str, confidence: float = .95) -> dict[str, Any]:
    return {"action": "ANSWER", "answer": value, "confidence": confidence}


def decide(item: dict[str, Any]) -> dict[str, Any]:
    """Apply auditable category semantics to a supplied or predicted state."""
    cat, claims = item["category"], item["claims"]
    if cat == "hidden_premise":
        return {"action": "CLARIFY", "answer": "CLARIFY", "confidence": .93}
    if cat == "temporal":
        holder = None
        for c in sorted(claims, key=lambda z: z.get("time", 0)):
            if c.get("time", 0) <= item["query_time"]:
                if c.get("event") == "appoint":
                    holder = c.get("actor")
                elif c.get("event") == "resign" and c.get("actor") == holder:
                    holder = None
        return _answer(holder or "unknown", .94 if holder else .5)
    if cat == "source_conflict":
        rank = lambda c: (c.get("source") == "official",
                          c.get("status") == "confirmed", c.get("time", 0))
        return _answer(max(claims, key=rank).get("actor", "unknown"))
    if cat == "modality":
        closed = any(c.get("event") == "close" and
                     c.get("status") == "confirmed" for c in claims)
        return _answer("yes" if closed else "no")
    if cat == "scope":
        universal = any(c.get("scope") == "global" for c in claims)
        return _answer("yes" if universal else "no")
    if cat == "observer":
        person = re.search(r"Does (\w+)", item["question"]).group(1)
        invited = any(c.get("event") == "invite" and
                      c.get("actor") == person for c in claims)
        knows = any(c.get("event") == "cancel" and
                    person in c.get("observed_by", []) for c in claims)
        return _answer("no" if knows else ("yes" if invited else "unknown"))
    if cat == "counterfactual":
        cf = [c for c in claims if c.get("scope") == "counterfactual"]
        return _answer("yes" if cf and cf[-1].get("event") == "online" else "no")
    return {"action": "ABSTAIN", "answer": "ABSTAIN", "confidence": .4}


def is_correct(item: dict[str, Any], prediction: dict[str, Any]) -> bool:
    if prediction["action"] != item["gold_action"]:
        return False
    return prediction["action"] != "ANSWER" or (
        str(prediction["answer"]).casefold() == str(item["gold_answer"]).casefold()
    )
