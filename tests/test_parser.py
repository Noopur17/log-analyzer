import tempfile
import unittest
from pathlib import Path

from analyzer.log_parser import LogParser, resolve_log_paths


class ParserTests(unittest.TestCase):
    def test_parse_counts_valid_and_skipped_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "app.log"
            log_file.write_text(
                "[2026-03-08 12:00:00] info: Started\n"
                "invalid line\n"
                "[2026-03-08 12:01:00] ERROR: Failed\n",
                encoding="utf-8",
            )

            result = LogParser([str(log_file)]).parse()

        self.assertEqual(result.files_scanned, 1)
        self.assertEqual(result.total_lines, 3)
        self.assertEqual(result.parsed_lines, 2)
        self.assertEqual(result.skipped_lines, 1)
        self.assertEqual([entry.level for entry in result.entries], ["INFO", "ERROR"])

    def test_resolve_directory_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "one.log").write_text("", encoding="utf-8")
            nested = root / "nested"
            nested.mkdir()
            (nested / "two.log").write_text("", encoding="utf-8")

            direct_paths = resolve_log_paths([str(root)])
            recursive_paths = resolve_log_paths([str(root)], recursive=True)

        self.assertEqual(len(direct_paths), 1)
        self.assertEqual(len(recursive_paths), 2)


if __name__ == "__main__":
    unittest.main()
