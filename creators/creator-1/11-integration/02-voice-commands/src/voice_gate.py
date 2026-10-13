"""C1-11-02 voice gate: structured commands only, same arbiter path.

Only a fully structured, allowed command passes — ambiguity never invents
an order (it asks for clarification). Voice goes through the same arbiter
shape as buttons and text (source "voice"), so repeats and MANUAL rules
apply unchanged. Real speech recognition stays open (C2-06-02/03).
"""
ALLOWED_ACTIONS = ("attack", "retreat", "farm", "gather")


def parse_structured(payload):
    """Return (command | None, reason). Pure, no audio, no ASR."""
    if not isinstance(payload, dict):
        return None, "not-a-dict"
    for field in ("action", "target", "orderId", "revision"):
        if field not in payload:
            return None, "ambiguous"
    if payload["action"] not in ALLOWED_ACTIONS:
        return None, "action-not-allowed"
    return {"orderId": payload["orderId"], "source": "voice",
            "revision": payload["revision"], "action": payload["action"],
            "target": payload["target"]}, "ok"


def admit(command, seen_ids, manual_mode):
    """Arbiter-side admission: repeat and MANUAL rules. Pure."""
    if command["orderId"] in seen_ids:
        return None, "duplicate"
    if command["action"] in ("attack",) and manual_mode:
        return None, "manual-holds-action"
    return command, "ok"
