import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from analyzer.cli import main


class CliTests(unittest.TestCase):
    def test_cli_prints_table_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "app.log"
            log_file.write_text(
                "[2026-03-08 12:00:00] INFO: Started\n"
                "[2026-03-08 12:01:00] ERROR: Timeout\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(["--log", str(log_file)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Files scanned: 1", output)
        self.assertIn("ERROR", output)

    def test_cli_returns_error_for_bad_timestamp(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = main(
                ["--log", "logs/sample.log", "--since", "2026/03/08 12:00:00"]
            )

        self.assertEqual(exit_code, 1)
        self.assertIn("invalid since timestamp", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
