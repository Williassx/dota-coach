"""C1-09-03 result bundle: unambiguous result, restorable review slice.

End-of-match events must come from the confirmed set; the bundle stores
commands, versions and the necessary events for review. The stored review
is a limited slice — it is never called a full Dota replay. Restoring a
supported review from a bundle is pure; a new live match stays open.
"""
CONFIRMED_ENDINGS = ("radiant-win", "dire-win", "abandoned")
BUNDLE_VERSION = "c1-result-v1"


def seal_result(ending, commands, versions, events):
    """Return bundle dict or (None, reason). Pure, no engine."""
    if ending not in CONFIRMED_ENDINGS:
        return None, "unconfirmed-ending"
    if not isinstance(commands, list) or not isinstance(versions, dict):
        return None, "bad-commands-or-versions"
    if not isinstance(events, list):
        return None, "bad-events"
    return {"ending": ending, "commands": commands, "versions": versions,
            "events": events, "bundle": BUNDLE_VERSION,
            "full_replay": False}, "ok"


def restore_review(bundle):
    """Restore the supported review slice, or (None, reason)."""
    if not isinstance(bundle, dict):
        return None, "not-a-bundle"
    if bundle.get("bundle") != BUNDLE_VERSION:
        return None, "unsupported-bundle"
    if bundle.get("full_replay") is not False:
        return None, "must-stay-limited"
    return {"ending": bundle["ending"], "events": bundle["events"]}, "ok"
