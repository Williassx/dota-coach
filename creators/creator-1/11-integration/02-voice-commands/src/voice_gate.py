"""C1-11-02 voice gate: structured commands only, same arbiter path.

Only a fully structured, allowed command passes; ambiguity never invents
an order. Voice proposals use the arbiter's source "coach" with origin
"voice" as metadata, not authentication. This nonmutating preliminary gate
does not execute or authorize an order. The common arbiter owns seen-ID and
accepted-revision commits and final admission. Real speech recognition and
server/native integration remain open (C2-06-02/03).
"""
ALLOWED_ACTIONS = ("attack", "retreat", "farm", "gather")
PAYLOAD_FIELDS = ("action", "target", "orderId", "revision")
COMMAND_FIELDS = PAYLOAD_FIELDS + ("source", "origin")
MAX_IDENTIFIER_LENGTH = 64
MAX_REVISION = 9007199254740991


def _exact_dict(value, fields):
    return (type(value) is dict and len(value) == len(fields) and
            all(type(key) is str for key in value) and set(value) == set(fields))


def _identifier(value):
    return (type(value) is str and 0 < len(value) <= MAX_IDENTIFIER_LENGTH and
            value == value.strip() and
            all(ord(character) >= 32 and ord(character) != 127 for character in value))


def _field_reason(payload):
    if type(payload["action"]) is not str or payload["action"] not in ALLOWED_ACTIONS:
        return "action-not-allowed"
    if not _identifier(payload["orderId"]):
        return "invalid-order-id"
    if not _identifier(payload["target"]):
        return "invalid-target"
    revision = payload["revision"]
    # Exact int rejects bool, fractional/infinite/NaN floats without unsafe coercion.
    if type(revision) is not int or not 0 <= revision <= MAX_REVISION:
        return "invalid-revision"
    return "ok"


def parse_structured(payload):
    """Return (command | None, reason). Pure, no audio, no ASR."""
    if type(payload) is not dict:
        return None, "not-a-dict"
    for field in PAYLOAD_FIELDS:
        if field not in payload:
            return None, "ambiguous"
    if not _exact_dict(payload, PAYLOAD_FIELDS):
        return None, "unexpected-fields"
    reason = _field_reason(payload)
    if reason != "ok":
        return None, reason
    return {"orderId": payload["orderId"], "source": "coach", "origin": "voice",
            "revision": payload["revision"], "action": payload["action"],
            "target": payload["target"]}, "ok"


def admit(command, seen_ids, manual_mode):
    """Preliminary check only; never add IDs or commit revisions.

    The caller supplies the common arbiter's external seen_ids set. A valid
    structured voice proposal is not proof of server permission or execution.
    """
    if (not _exact_dict(command, COMMAND_FIELDS) or
            type(command["source"]) is not str or command["source"] != "coach" or
            type(command["origin"]) is not str or command["origin"] != "voice" or
            _field_reason(command) != "ok"):
        return None, "invalid-command"
    if type(seen_ids) is not set:
        return None, "invalid-seen-ids"
    if type(manual_mode) is not bool:
        return None, "invalid-manual-mode"
    if command["orderId"] in seen_ids:
        return None, "duplicate"
    if manual_mode:
        return None, "manual-holds-action"
    return command, "ok"
