"""C1-09-02 opponent: limited policies through shared rules, no hidden reads.

The opponent uses the same observation shape and the same arbiter command
shape as our side (shared controller path). Allowed observations only:
entries flagged hidden/future are refused before choice, so the opponent
cannot read hidden information by construction.
"""
OPPONENT_POLICIES = ("defensive", "greedy")


def opponent_choice(policy, visible_targets):
    """Return target id or None. Pure, no engine, no hidden input."""
    if policy not in OPPONENT_POLICIES:
        return None, "unknown-policy"
    if not isinstance(visible_targets, list):
        return None, "bad-targets"
    for t in visible_targets:
        if not isinstance(t, dict) or t.get("visible") is not True:
            return None, "not-allowed-observation"
        if t.get("hidden") is True or t.get("future") is True:
            return None, "hidden-read-refused"
    if not visible_targets:
        return None, "no-target"
    if policy == "defensive":
        return visible_targets[-1]["id"], "ok"
    return visible_targets[0]["id"], "ok"


def to_arbiter_command(target_id, order_id, revision):
    if target_id is None:
        return None
    return {"orderId": order_id, "source": "ai", "revision": revision,
            "target": target_id, "side": "opponent"}
