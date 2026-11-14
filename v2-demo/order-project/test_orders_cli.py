"""Process-level and in-process tests for orders_cli.py.

Source-only test module: no subprocesses are executed on import.
Tests are run independently by the instructor.
"""

import copy
import io
import json
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from order_service import ORDERS

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


class OrdersCliProcessTests(unittest.TestCase):
    """End-to-end CLI behavior verified via subprocess."""

    def run_cli(self, *args, timeout=10):
        return subprocess.run(
            [sys.executable, "orders_cli.py", *args],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR,
            timeout=timeout,
        )

    def test_ben_shipped_complete_json(self):
        result = self.run_cli("--user", "2", "--status", "shipped")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout), [{"id": 11, "item": "mouse"}])

    def test_ana_no_status_filter_complete_json(self):
        result = self.run_cli("--user", "1")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            json.loads(result.stdout),
            [{"id": 10, "item": "keyboard"}, {"id": 12, "item": "monitor"}],
        )

    def test_ben_pending_empty_list(self):
        result = self.run_cli("--user", "2", "--status", "pending")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout), [])

    def test_unknown_user_service_error_stream(self):
        result = self.run_cli("--user", "99", "--status", "lost")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "error: unknown user\n")

    def test_invalid_status_service_error_stream(self):
        result = self.run_cli("--user", "2", "--status", "lost")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "error: unknown status\n")

    def test_validation_order_user_before_status(self):
        result = self.run_cli("--user", "99", "--status", "lost")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, "error: unknown user\n")

    def test_help_exits_zero_and_shows_options(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("--user", result.stdout)
        self.assertIn("--status", result.stdout)

    def test_missing_required_user_returns_two(self):
        result = self.run_cli("--status", "shipped")
        self.assertEqual(result.returncode, 2)

    def test_non_integer_user_returns_two(self):
        result = self.run_cli("--user", "not-an-int")
        self.assertEqual(result.returncode, 2)

    def test_unknown_option_with_valid_user_returns_two(self):
        # unknown options must be rejected, not silently ignored
        result = self.run_cli("--user", "1", "--bogus")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertNotEqual(result.stderr, "")


class OrdersCliUnitTests(unittest.TestCase):
    """In-process tests proving delegation and import safety."""

    def _fresh_cli_module(self):
        sys.modules.pop("orders_cli", None)
        import orders_cli
        return orders_cli

    def test_import_makes_zero_service_calls_and_parses_no_argv(self):
        import argparse
        with patch("order_service.orders_for") as service_mock, \
             patch("argparse.ArgumentParser.parse_args") as parse_mock:
            orders_cli = self._fresh_cli_module()
        self.assertEqual(service_mock.call_count, 0)
        self.assertEqual(parse_mock.call_count, 0)
        self.assertIs(orders_cli.orders_for, service_mock)

    def test_help_makes_zero_service_calls(self):
        orders_cli = self._fresh_cli_module()
        with patch.object(orders_cli, "orders_for") as service_mock:
            with self.assertRaises(SystemExit) as raised:
                orders_cli.main(["--help"])
        self.assertEqual(raised.exception.code, 0)
        self.assertEqual(service_mock.call_count, 0)

    def test_main_delegates_actual_user_and_status(self):
        orders_cli = self._fresh_cli_module()
        distinctive = [{"id": 999, "item": "distinctive"}]
        with patch.object(orders_cli, "orders_for", return_value=distinctive) as service_mock:
            out = io.StringIO()
            err = io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = orders_cli.main(["--user", "5", "--status", "shipped"])
        self.assertEqual(code, 0)
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(json.loads(out.getvalue()), distinctive)
        service_mock.assert_called_once_with(5, "shipped")


class ImportSafetyTests(unittest.TestCase):
    """Importing orders_cli must have no side effects."""

    def test_import_produces_no_output(self):
        sys.modules.pop("orders_cli", None)
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            import orders_cli  # noqa: F401
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), "")

    def test_import_does_not_mutate_orders(self):
        snapshot = copy.deepcopy(ORDERS)
        sys.modules.pop("orders_cli", None)
        import orders_cli  # noqa: F401
        self.assertEqual(ORDERS, snapshot)


if __name__ == "__main__":
    unittest.main()