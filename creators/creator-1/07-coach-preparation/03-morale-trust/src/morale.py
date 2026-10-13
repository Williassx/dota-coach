"""C1-07-03 morale: game parameters only, never claims about the human.

Support adjusts agreed numeric game parameters (focus, steadiness) within
declared bounds; resistance caps how far orders may push a player. Every
output carries its assumption labels, so a game assumption is never
presented as a confirmed fact about the person.
"""
FOCUS_BOUNDS = (0.0, 1.0)
STEADINESS_BOUNDS = (0.0, 1.0)
MAX_PUSH = 0.3


def clamp(value, bounds):
    lo, hi = bounds
    return max(lo, min(hi, value))


def apply_support(params, support, resistance):
    """Return (new_params, labels). Pure, no engine, no personal data."""
    if not isinstance(params, dict) or support not in ("praise", "calm",
                                                       "rally"):
        return None, "bad-input"
    if not isinstance(resistance, (int, float)) or not 0 <= resistance <= 1:
        return None, "bad-resistance"
    push = MAX_PUSH * (1 - resistance)
    deltas = {"praise": (push, 0.0), "calm": (0.0, push),
              "rally": (push / 2, push / 2)}[support]
    new_params = {
        "focus": clamp(params.get("focus", 0.5) + deltas[0], FOCUS_BOUNDS),
        "steadiness": clamp(params.get("steadiness", 0.5) + deltas[1],
                            STEADINESS_BOUNDS),
    }
    labels = {"assumption": "game-only",
              "about_person": False,
              "support": support,
              "resistance": resistance}
    return new_params, labels
