"""Regression tests for the Sprint 2 Product Factory runner."""

from __future__ import annotations

import json
import unittest
from io import StringIO
from unittest.mock import patch

from apps.cli.main import main as cli_main
from apps.factory.runner import build_launch_pack
from scripts.validate_launch_pack import REQUIRED_SECTIONS


class ProductFactoryRunnerTests(unittest.TestCase):
    def test_runner_builds_complete_launch_pack(self) -> None:
        pack = build_launch_pack("Launch a kids activity kit on Instagram")
        self.assertEqual(pack["reportType"], "LAUNCH_PACK")
        self.assertTrue(pack["phase1Manual"])
        self.assertEqual(sorted(pack["sections"].keys()), sorted(REQUIRED_SECTIONS))
        self.assertGreaterEqual(len(pack["risks"]), 1)
        self.assertGreaterEqual(len(pack["nextActions"]), 1)

    def test_runner_rejects_empty_requirement(self) -> None:
        with self.assertRaises(ValueError):
            build_launch_pack("   ")

    def test_cli_run_command_prints_launch_pack_json(self) -> None:
        output = StringIO()
        with patch("sys.stdout", output):
            exit_code = cli_main(["run", "Launch a Tamil typography product"])
        self.assertEqual(exit_code, 0)
        pack = json.loads(output.getvalue())
        self.assertEqual(pack["reportType"], "LAUNCH_PACK")
        self.assertIn("marketing", pack["sections"])


if __name__ == "__main__":
    unittest.main()
