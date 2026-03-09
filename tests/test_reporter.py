import csv
import json
import tempfile
import unittest
from pathlib import Path

from analyzer.reporter import generate_report


SUMMARY = {
    "files_scanned": 1,
    "total_lines": 4,
    "parsed_lines": 4,
    "skipped_lines": 0,
    "matching_entries": 2,
    "counts_by_level": {"ERROR": 2},
    "first_timestamp": "2026-03-08 12:01:00",
    "last_timestamp": "2026-03-08 12:02:00",
    "top_messages": [{"message": "Timeout", "count": 2}],
    "levels_present": ["ERROR"],
}


class ReporterTests(unittest.TestCase):
    def test_table_rendering(self) -> None:
        rendered = generate_report(SUMMARY, output_format="table")
        self.assertIn("Counts by level", rendered)
        self.assertIn("ERROR", rendered)

    def test_json_report_written(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "report.json"
            generate_report(SUMMARY, output_format="json", output_file=str(output_file))
            written = json.loads(output_file.read_text(encoding="utf-8"))

        self.assertEqual(written["matching_entries"], 2)

    def test_csv_report_written(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "report.csv"
            generate_report(SUMMARY, output_format="csv", output_file=str(output_file))
            with output_file.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))

        self.assertTrue(any(row["section"] == "levels" and row["name"] == "ERROR" for row in rows))


if __name__ == "__main__":
    unittest.main()
