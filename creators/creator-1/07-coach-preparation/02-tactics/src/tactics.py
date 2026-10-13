"""C1-07-02 pre-match plan: limited tactical set with observable influence.

The plan never invents engine effects: it only biases the personal policy
choice among already-allowed targets, and every bias is declared in advance
so preparation has a describable observable influence. Intent is not effect.
"""
TACTICS = ("push", "farm", "split", "regroup")

BIAS = {
    "push": {"kind": "attack", "note": "prefer first visible target"},
    "farm": {"kind": "hold", "note": "prefer last visible target"},
    "split": {"kind": "attack", "note": "prefer last visible target"},
    "regroup": {"kind": "move", "note": "rally at [0, 0]"},
}


def make_plan(tactic, version="tactics-v1"):
    """Return plan dict or None for an unknown tactic."""
    if tactic not in TACTICS:
        return None
    return {"tactic": tactic, "bias": BIAS[tactic], "version": version}


def apply_plan(choice_fn, context, profile, plan):
    """Run choice_fn under a plan; returns (choice, trail).

    The trail records plan tactic + version so the influence is observable
    and comparable across plans on the same scene.
    """
    if plan is None or plan.get("tactic") not in TACTICS:
        return None, "bad-plan"
    choice, explanation = choice_fn(context, profile, plan["bias"])
    trail = {"plan": plan["tactic"], "version": plan["version"],
             "bias": plan["bias"]["kind"], "explanation": explanation}
    return choice, trail
