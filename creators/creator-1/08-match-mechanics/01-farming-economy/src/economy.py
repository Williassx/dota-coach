"""C1-08-01 farming economy: allowed actions, standard rules, no guarantees.

A click never guarantees a last-hit or deny — the client resolves the
outcome; this layer only issues allowed attempts and changes the purchase
plan. Every refusal carries an understandable reason (gold shortage,
invalid purchase, wrong target side).
"""
ALLOWED_ACTIONS = ("attack_creep", "deny_creep", "change_plan")

SHOP_ITEMS = {"tango": 90, "salve": 110, "branches": 50, "boots": 250}


def attempt(action, target_side, gold, plan=None, item=None):
    """Return (ok, detail, reason). Pure rules, no engine."""
    if action not in ALLOWED_ACTIONS:
        return False, None, "action-not-allowed"
    if action == "change_plan":
        if not isinstance(plan, list):
            return False, None, "bad-plan"
        return True, {"plan": plan}, "plan-changed"
    if target_side == "ally" and action != "deny_creep":
        return False, None, "ally-only-deny"
    if target_side == "enemy" and action != "attack_creep":
        return False, None, "enemy-only-attack"
    if target_side not in ("ally", "enemy"):
        return False, None, "bad-target"
    if item is not None:
        if item not in SHOP_ITEMS:
            return False, None, "invalid-purchase"
        if gold < SHOP_ITEMS[item]:
            return False, None, "gold-shortage"
        return True, {"attempt": action, "item": item,
                      "guaranteed": False}, "attempt-issued"
    return True, {"attempt": action, "guaranteed": False}, "attempt-issued"
