"""C1-07-01 roster validation: supported combos, weak-coverage warnings (tests).

Proposal-level compatibility matrix over explicitly synthetic TEST profiles;
no hidden assignment of unsupported profiles. A confirmed roster is a pure
local decision here — passing it to the interface (creator 2) stays open.
"""
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent

ROLES = {1, 2, 3, 4, 5}
WEAK_COVERAGE = 0.5

# Proposal matrix: TEST profile id -> {supported heroes, roles}.
COMPAT = {
    "TEST-player-001": {"heroes": {"npc_dota_hero_crystal_maiden",
                                   "npc_dota_hero_lion"},
                        "roles": {4, 5}},
    "TEST-player-002": {"heroes": {"npc_dota_hero_juggernaut",
                                   "npc_dota_hero_sven"},
                        "roles": {1}},
    "TEST-player-003": {"heroes": {"npc_dota_hero_lina",
                                   "npc_dota_hero_storm_spirit"},
                        "roles": {2}},
    "TEST-player-004": {"heroes": {"npc_dota_hero_axe",
                                   "npc_dota_hero_centaur"},
                        "roles": {3}},
    "TEST-player-005": {"heroes": {"npc_dota_hero_lion",
                                   "npc_dota_hero_shadow_shaman"},
                        "roles": {4, 5}},
}


def load_fixture(name):
    return json.loads((HERE / "fixtures" / name).read_text(encoding="utf-8"))


def validate_roster(assignments, profiles):
    """Return (confirmed, warnings, reason). Pure local check, no engine."""
    warnings = []
    if not isinstance(assignments, list) or len(assignments) != 5:
        return False, warnings, "need-five"
    ids = [a.get("projectId") for a in assignments]
    if any(not isinstance(i, str) or not i for i in ids):
        return False, warnings, "bad-id"
    if len(set(ids)) != 5:
        return False, warnings, "duplicate-player"
    heroes = [a.get("hero") for a in assignments]
    if any(not isinstance(h, str) or not h for h in heroes):
        return False, warnings, "bad-hero"
    if len(set(heroes)) != 5:
        return False, warnings, "duplicate-hero"
    roles = [a.get("role") for a in assignments]
    if set(roles) != ROLES:
        return False, warnings, "roles-must-be-1-to-5"
    for a in assignments:
        pid = a["projectId"]
        if pid not in profiles:
            return False, warnings, "unsupported-profile"
        compat = COMPAT.get(pid)
        if compat is None:
            return False, warnings, "unsupported-profile"
        if a["hero"] not in compat["heroes"]:
            return False, warnings, "hero-not-supported"
        if a["role"] not in compat["roles"]:
            return False, warnings, "role-not-supported"
        cov = profiles[pid].get("coverage", 0)
        if cov < WEAK_COVERAGE:
            warnings.append(f"weak-coverage:{pid}={cov}")
    return True, warnings, "ok"


class RosterValidatorTests(unittest.TestCase):
    def test_valid_fixture_confirms_with_weak_warning(self):
        doc = load_fixture("synthetic-roster.json")
        ok, warnings, reason = validate_roster(doc["assignments"],
                                              doc["profiles"])
        self.assertTrue(ok, reason)
        self.assertTrue(any(w.startswith("weak-coverage:TEST-player-002")
                            for w in warnings))

    def test_reject_unknown_profile_openly(self):
        doc = load_fixture("synthetic-roster.json")
        bad = json.loads(json.dumps(doc))
        bad["assignments"][0]["projectId"] = "stranger-007"
        ok, _, reason = validate_roster(bad["assignments"], bad["profiles"])
        self.assertFalse(ok)
        self.assertEqual(reason, "unsupported-profile")

    def test_reject_unsupported_hero(self):
        doc = load_fixture("synthetic-roster.json")
        bad = json.loads(json.dumps(doc))
        bad["assignments"][0]["hero"] = "npc_dota_hero_invoker"
        ok, _, reason = validate_roster(bad["assignments"], bad["profiles"])
        self.assertFalse(ok)
        self.assertEqual(reason, "hero-not-supported")

    def test_reject_duplicate_player_and_role_gap(self):
        doc = load_fixture("synthetic-roster.json")
        bad = json.loads(json.dumps(doc))
        bad["assignments"][1]["projectId"] = \
            bad["assignments"][0]["projectId"]
        ok, _, reason = validate_roster(bad["assignments"], bad["profiles"])
        self.assertFalse(ok)
        self.assertEqual(reason, "duplicate-player")
        bad2 = json.loads(json.dumps(doc))
        bad2["assignments"][4]["role"] = 1
        ok, _, reason = validate_roster(bad2["assignments"],
                                        bad2["profiles"])
        self.assertFalse(ok)
        self.assertEqual(reason, "roles-must-be-1-to-5")

    def test_reject_short_roster(self):
        doc = load_fixture("synthetic-roster.json")
        ok, _, reason = validate_roster(doc["assignments"][:4],
                                        doc["profiles"])
        self.assertFalse(ok)
        self.assertEqual(reason, "need-five")


if __name__ == "__main__":
    unittest.main()
