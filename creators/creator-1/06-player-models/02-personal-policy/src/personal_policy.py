"""C1-06-02 personal choice policy (TEST profiles only, no real people).

The policy consumes an observation-shaped projection and a TEST profile,
and emits an arbiter-shaped command. Differences from the baseline are
explainable by input features by construction: the same context with the
same profile always yields the same choice, and the choice record names
the deciding feature. Hero rules and vision are never bypassed — the
policy only selects among already-allowed targets.
"""
BASELINE_ID = "synthetic-baseline"


def choose(context, profile):
    """Return (choice, explanation). Pure function, no engine, no network."""
    if not isinstance(context, dict) or not isinstance(profile, dict):
        return None, "bad-input"
    visible = context.get("visible", [])
    if not visible:
        return {"kind": "wait", "profile": profile.get("identity")}, \
            "no-visible-target"
    measured = {f["name"]: f["value"]
                for f in profile.get("measured", [])}
    aggression = measured.get("aggression", 0.5)
    if aggression >= 0.5:
        target = visible[0]
        return {"kind": "attack", "target": target.get("id"),
                "profile": profile.get("identity")}, \
            f"aggression={aggression}>=0.5"
    target = visible[-1]
    return {"kind": "hold", "target": target.get("id"),
            "profile": profile.get("identity")}, \
        f"aggression={aggression}<0.5"


def to_arbiter_command(choice, order_id, revision):
    """Wrap a policy choice into the arbiter command shape (C1-03-03)."""
    if choice is None:
        return None
    return {"orderId": order_id, "source": "ai", "revision": revision,
            "choice": choice}
