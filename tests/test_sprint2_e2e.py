"""Unit wrapper around the Sprint 2 e2e acceptance test."""

from __future__ import annotations

import tempfile
import unittest

from scripts.sprint2_e2e import REQUIRED_REPORT_KEYS, run_e2e


class Sprint2E2ETests(unittest.TestCase):
    def test_acceptance_idea_returns_required_research_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_e2e(directory)
        self.assertTrue(result["ok"], result["issues"])
        report = result["report"]
        for key in REQUIRED_REPORT_KEYS:
            self.assertIn(key, report)
        self.assertEqual(report["reportType"], "RESEARCH_REPORT")


if __name__ == "__main__":
    unittest.main()
