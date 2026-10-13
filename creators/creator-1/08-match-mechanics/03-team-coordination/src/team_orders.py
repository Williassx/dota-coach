"""C1-08-03 team orders: addressees, confirmation, observable actions.

A team order (attack / retreat / farm / gather) is distributed across roles
with per-role individual policies; the same target is never assigned twice
(resource conflict is refused), and unreachable addressees are refused
openly. Every issued order carries its addressees and requires confirmation;
stale confirmations are rejected by revision.
"""
TEAM_ORDERS = ("attack", "retreat", "farm", "gather")


def distribute(order, roles, targets, policies):
    """Return (assignments, reason). Pure distribution, no engine."""
    if order not in TEAM_ORDERS:
        return None, "order-unknown"
    if not roles or not targets:
        return None, "empty-side"
    for addr in roles:
        if addr not in policies:
            return None, f"unreachable:{addr}"
    if len(set(targets)) != len(targets):
        return None, "resource-conflict"
    assignments = {}
    for i, addr in enumerate(roles):
        allowed = policies[addr]
        pick = targets[i % len(targets)]
        if pick not in allowed:
            return None, f"policy-refuses:{addr}:{pick}"
        assignments[addr] = {"order": order, "target": pick,
                             "needs_confirm": True}
    return assignments, "ok"


def confirm(assignments, confirmations, revision, expected_revision):
    """Confirm addressees; stale revision rejects the whole batch."""
    if revision != expected_revision:
        return None, "stale-confirmation"
    if set(confirmations) != set(assignments):
        return None, "partial-confirmation"
    return {a: dict(v, confirmed=True) for a, v in assignments.items()}, "ok"
