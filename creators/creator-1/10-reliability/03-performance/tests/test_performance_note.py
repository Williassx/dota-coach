"""Guards for C1-10-03: no fabricated measurements (unit tests)."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPORT = HERE.parent / "reports" / "performance.md"


def report():
    return REPORT.read_text(encoding="utf-8")


class PerformanceNoteTests(unittest.TestCase):
    def test_no_measurements_claimed(self):
        text = report()
        self.assertIn("Измерений нет", text)

    def test_cloud_estimate_not_passed_off(self):
        text = report().lower()
        self.assertIn("не является", text)
        self.assertNotIn("ms", text)
        self.assertNotIn("fps", text)


if __name__ == "__main__":
    unittest.main()
