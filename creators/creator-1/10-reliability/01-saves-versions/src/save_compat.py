"""C1-10-01 saves: versioned data, compatible loads, safe refusals.

Compatible data restores; anything else (corrupt, ancient, foreign) is
refused without touching current state — the loader never mutates its
input and returns fresh structures only.
"""
CURRENT_VERSION = 1
MIN_SUPPORTED_VERSION = 1


def save_state(payload):
    """Wrap payload into a versioned save."""
    return {"save_version": CURRENT_VERSION, "payload": payload}


def load_state(blob, current=None):
    """Return (restored | None, reason). Never mutates current."""
    if not isinstance(blob, dict):
        return None, "corrupt"
    version = blob.get("save_version")
    if not isinstance(version, int):
        return None, "corrupt"
    if version > CURRENT_VERSION:
        return None, "newer-than-code"
    if version < MIN_SUPPORTED_VERSION:
        return None, "too-old"
    if "payload" not in blob:
        return None, "corrupt"
    return {"payload": blob["payload"],
            "loaded_version": version}, "ok"
