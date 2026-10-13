"""Guards for C1-12-02: no approval claimed, nothing sent (unit tests)."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(rel):
    return (HERE.parent / rel).read_text(encoding="utf-8").lower()


class DemoGuardTests(unittest.TestCase):
    def test_no_approval_claimed(self):
        for rel in ("notes/demo-checklist.md", "reports/proposal.md"):
            text = read(rel)
            self.assertNotIn("одобрено", text)
            self.assertNotIn("valve согласилась", text)

    def test_send_not_authorized(self):
        text = read("notes/demo-checklist.md")
        self.assertIn("только по", text)
        self.assertIn("явному поручению", text)


if __name__ == "__main__":
    unittest.main()
