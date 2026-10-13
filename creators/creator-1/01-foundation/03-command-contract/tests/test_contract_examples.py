"""C1-01-03 proposal examples: allowed vs rejected orders (unit tests).

Proposal source: notes/contract-review.md. This is the creator-1 proposal side;
the shared version is agreed with creator 2 later. No native calls here.
"""
import unittest

ALLOWED_TYPES = {
    "DOTA_UNIT_ORDER_MOVE_TO_POSITION",
    "DOTA_UNIT_ORDER_ATTACK_TARGET",
}


def validate(order, seen_ids):
    """Return (ok, reason). Pure shape/duplicate check, no engine."""
    if not isinstance(order, dict):
        return False, "not-a-dict"
    for field in ("orderId", "orderType", "actorEntity", "revision"):
        if field not in order:
            return False, f"missing-{field}"
    if order["orderId"] in seen_ids:
        return False, "duplicate-order"
    if order["orderType"] not in ALLOWED_TYPES:
        return False, "bad-type"
    if not isinstance(order["actorEntity"], int) or order["actorEntity"] < 0:
        return False, "bad-actor"
    if not isinstance(order["revision"], int) or order["revision"] < 0:
        return False, "bad-revision"
    if order["orderType"] == "DOTA_UNIT_ORDER_MOVE_TO_POSITION":
        pos = order.get("position")
        if (not isinstance(pos, (list, tuple)) or len(pos) != 2
                or not all(isinstance(v, (int, float)) for v in pos)):
            return False, "bad-position"
    if order["orderType"] == "DOTA_UNIT_ORDER_ATTACK_TARGET":
        tgt = order.get("targetEntity")
        if not isinstance(tgt, int) or tgt < 0:
            return False, "bad-target"
    return True, "ok"


class ContractExampleTests(unittest.TestCase):
    def test_allowed_move(self):
        ok, reason = validate({
            "orderId": "m1", "orderType": "DOTA_UNIT_ORDER_MOVE_TO_POSITION",
            "actorEntity": 500, "position": [-128, -64], "revision": 3,
        }, set())
        self.assertTrue(ok, reason)

    def test_allowed_attack(self):
        ok, reason = validate({
            "orderId": "a1", "orderType": "DOTA_UNIT_ORDER_ATTACK_TARGET",
            "actorEntity": 500, "targetEntity": 511, "revision": 3,
        }, set())
        self.assertTrue(ok, reason)

    def test_reject_unknown_type(self):
        ok, reason = validate({
            "orderId": "x1", "orderType": "DOTA_UNIT_ORDER_CAST_POSITION",
            "actorEntity": 500, "revision": 3,
        }, set())
        self.assertFalse(ok)
        self.assertEqual(reason, "bad-type")

    def test_reject_duplicate(self):
        order = {
            "orderId": "m1", "orderType": "DOTA_UNIT_ORDER_MOVE_TO_POSITION",
            "actorEntity": 500, "position": [0, 0], "revision": 1,
        }
        ok, _ = validate(order, set())
        self.assertTrue(ok)
        ok2, reason2 = validate(order, {"m1"})
        self.assertFalse(ok2)
        self.assertEqual(reason2, "duplicate-order")

    def test_reject_foreign_or_stale_shape(self):
        ok, reason = validate({
            "orderId": "s1", "orderType": "DOTA_UNIT_ORDER_MOVE_TO_POSITION",
            "actorEntity": -5, "position": [0, 0], "revision": 1,
        }, set())
        self.assertFalse(ok)
        self.assertEqual(reason, "bad-actor")
        ok, reason = validate({
            "orderId": "s2", "orderType": "DOTA_UNIT_ORDER_ATTACK_TARGET",
            "actorEntity": 500, "targetEntity": 511, "revision": -1,
        }, set())
        self.assertFalse(ok)
        self.assertEqual(reason, "bad-revision")

    def test_reject_missing_target_or_position(self):
        ok, reason = validate({
            "orderId": "s3", "orderType": "DOTA_UNIT_ORDER_ATTACK_TARGET",
            "actorEntity": 500, "revision": 1,
        }, set())
        self.assertFalse(ok)
        self.assertEqual(reason, "bad-target")
        ok, reason = validate({
            "orderId": "s4", "orderType": "DOTA_UNIT_ORDER_MOVE_TO_POSITION",
            "actorEntity": 500, "revision": 1,
        }, set())
        self.assertFalse(ok)
        self.assertEqual(reason, "bad-position")


if __name__ == "__main__":
    unittest.main()
