"""C1-05-03 replay gate: observed actions in, inferred intent kept separate.

Replays are UNAVAILABLE (decision recorded in notes/replay-coverage.md):
no parser is invented here. This gate defines the normalization rule that
will apply once a compatible parser is fixed: drop future/hidden entries,
split observed action from inferred intent, stamp source + gate version.
"""
GATE_VERSION = "c1-replay-gate-v1"


def normalize_event(event):
    """Return (kept_dict | None, reason). Pure rule, no engine, no network."""
    if not isinstance(event, dict):
        return None, "not-a-dict"
    if event.get("future") is True or event.get("hidden") is True:
        return None, "future-or-hidden"
    if "action" not in event or "match_id" not in event:
        return None, "missing-action-or-match"
    kept = {
        "match_id": event["match_id"],
        "seq": event.get("seq"),
        "observed_action": event["action"],
        "inferred_intent": event.get("intent"),
        "intent_is_guess": True,
        "source": event.get("source", "unknown"),
        "gate": GATE_VERSION,
    }
    return kept, "ok"
