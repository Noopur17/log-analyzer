import tempfile
import unittest
from pathlib import Path

from analyzer.log_parser import LogParser
from analyzer.metrics import filter_entries, summarize_logs


class MetricsTests(unittest.TestCase):
    def test_filter_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "app.log"
            log_file.write_text(
                "[2026-03-08 12:00:00] INFO: Start\n"
                "[2026-03-08 12:01:00] ERROR: Timeout\n"
                "[2026-03-08 12:02:00] ERROR: Timeout\n"
                "[2026-03-08 12:03:00] WARNING: Retry\n",
                encoding="utf-8",
            )

            parsed = LogParser([str(log_file)]).parse()
            filtered = filter_entries(parsed.entries, levels=["error"], contains="time")
            summary = summarize_logs(filtered, parsed, top_messages=1)

        self.assertEqual(summary["matching_entries"], 2)
        self.assertEqual(summary["counts_by_level"], {"ERROR": 2})
        self.assertEqual(summary["top_messages"], [{"message": "Timeout", "count": 2}])
        self.assertEqual(summary["first_timestamp"], "2026-03-08 12:01:00")
        self.assertEqual(summary["last_timestamp"], "2026-03-08 12:02:00")


if __name__ == "__main__":
    unittest.main()
