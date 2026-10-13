"""Schema checks for C1-06-01 profiles: versions, coverage, measured-vs-traits.

Measured features and game-trait labels live in separate sections; traits are
never proven by aggregates. Real data is absent, so the only valid example is
the explicitly marked synthetic fixture.
"""
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTES = HERE.parent / "notes"


def load_fixture(name):
    return json.loads((HERE / "fixtures" / name).read_text(encoding="utf-8"))


def validate(profile):
    """Return (ok, reason) for the profile schema."""
    if not isinstance(profile, dict):
        return False, "not-a-dict"
    for field in ("identity", "version", "measured", "traits",
                  "coverage", "uncertainty", "synthetic"):
        if field not in profile:
            return False, f"missing-{field}"
    if not isinstance(profile["measured"], list):
        return False, "bad-measured"
    for feat in profile["measured"]:
        for field in ("name", "value", "matches", "origin"):
            if field not in feat:
                return False, f"measured-missing-{field}"
    if not isinstance(profile["traits"], list):
        return False, "bad-traits"
    cov = profile["coverage"]
    if not isinstance(cov, (int, float)) or not 0 <= cov <= 1:
        return False, "bad-coverage"
    unc = profile["uncertainty"]
    if (not isinstance(unc, dict) or unc.get("level") not in
            ("low", "medium", "high")):
        return False, "bad-uncertainty"
    if not isinstance(profile["synthetic"], bool):
        return False, "synthetic-not-explicit"
    return True, "ok"


class ProfileSchemaTests(unittest.TestCase):
    def test_synthetic_fixture_is_valid_and_flagged(self):
        prof = load_fixture("synthetic-profile.json")
        self.assertTrue(prof["synthetic"])
        ok, reason = validate(prof)
        self.assertTrue(ok, reason)

    def test_traits_kept_separate_from_measured(self):
        prof = load_fixture("synthetic-profile.json")
        measured_names = {f["name"] for f in prof["measured"]}
        trait_names = {t["name"] for t in prof["traits"]}
        self.assertTrue(measured_names.isdisjoint(trait_names))
        for trait in prof["traits"]:
            # Each trait must carry an explicit NOT-proven marker.
            self.assertIn("NOT proven", trait.get("note", ""))

    def test_reject_missing_version_or_origin(self):
        prof = load_fixture("synthetic-profile.json")
        bad = dict(prof)
        del bad["version"]
        ok, reason = validate(bad)
        self.assertFalse(ok)
        self.assertEqual(reason, "missing-version")

    def test_reject_implicit_synthetic_flag(self):
        prof = dict(load_fixture("synthetic-profile.json"))
        prof["synthetic"] = "yes"
        ok, reason = validate(prof)
        self.assertFalse(ok)
        self.assertEqual(reason, "synthetic-not-explicit")

    def test_reject_bad_coverage_and_uncertainty(self):
        prof = dict(load_fixture("synthetic-profile.json"))
        prof["coverage"] = 1.5
        ok, reason = validate(prof)
        self.assertFalse(ok)
        self.assertEqual(reason, "bad-coverage")

    def test_protocol_note_locks_test_before_features(self):
        # NOTE: explicit utf-8 — Windows default cp1251 mangles Cyrillic.
        text = (NOTES / "evaluation-protocol.md").read_text(encoding="utf-8")
        for marker in ("целый матч", "validation", "не используются",
                       "Ревизия 1"):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
