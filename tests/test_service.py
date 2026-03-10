import unittest

from analyzer.service import analyze_text


class ServiceTests(unittest.TestCase):
    def test_analyze_text_uses_python_pipeline(self) -> None:
        result = analyze_text(
            "[2026-03-08 12:00:00] INFO: Start\n"
            "[2026-03-08 12:01:00] ERROR: Timeout\n"
            "bad line\n",
            levels=["ERROR"],
        )

        self.assertEqual(result["summary"]["parsed_lines"], 2)
        self.assertEqual(result["summary"]["skipped_lines"], 1)
        self.assertEqual(result["summary"]["matching_entries"], 1)
        self.assertEqual(result["entries"][0]["level"], "ERROR")


if __name__ == "__main__":
    unittest.main()
