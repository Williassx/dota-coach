"""Guards for C1-12-01: no claimed permission (unit tests)."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def register():
    return (HERE.parent / "notes" / "rights-register.md").read_text(
        encoding="utf-8")


class RightsRegisterTests(unittest.TestCase):
    def test_no_permission_claimed(self):
        text = register().lower()
        self.assertNotIn("разрешено", text)
        self.assertNotIn("лицензия получена", text)
        self.assertIn("открытый вопрос", text)

    def test_sources_read_and_linked(self):
        text = register()
        self.assertIn("docs/legal/plan.md", text)
        self.assertIn("initial-review.md", text)

    def test_inaccessible_marked_not_read(self):
        text = register().lower()
        self.assertIn("не прочитаны", text)
        self.assertIn("не отказ правообладателя", text)


if __name__ == "__main__":
    unittest.main()
