"""Guards for C1-11-03: the split must stay honest (unit tests)."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def report():
    return (HERE.parent / "reports" / "acceptance.md").read_text(
        encoding="utf-8")


class AcceptanceSplitTests(unittest.TestCase):
    def test_three_way_split_present(self):
        text = report()
        for section in ("## Готовы", "## Неработающие", "## Непроверенные"):
            self.assertIn(section, text)

    def test_no_live_chain_claimed(self):
        text = report()
        self.assertIn("не выполнялась", text)
        # Only the negated criterion quote may contain the phrase.
        self.assertNotIn("цепочка выполнена.", text.lower())
        self.assertNotIn("цепочка пройдена", text.lower())

    def test_blockers_listed(self):
        text = report().lower()
        for blocker in ("dota", "производительности", "обоими владельцами"):
            self.assertIn(blocker, text)


if __name__ == "__main__":
    unittest.main()
