"""Guards for C1-12-03: no release claimed (unit tests)."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(rel):
    return (HERE.parent / rel).read_text(encoding="utf-8").lower()


class ReleaseGuardTests(unittest.TestCase):
    def test_no_release_claimed(self):
        for rel in ("notes/release-checklist.md", "reports/release.md"):
            text = read(rel)
            self.assertNotIn("выпущено", text)
            self.assertNotIn("релиз состоялся", text)

    def test_blockers_recorded(self):
        text = read("notes/release-checklist.md")
        self.assertIn("не выбран", text)
        self.assertIn("не разрешён", text)


if __name__ == "__main__":
    unittest.main()
