import unittest

from analyzer.webapp import analyze_payload


class WebAppTests(unittest.TestCase):
    def test_analyze_payload_returns_summary_and_entries(self) -> None:
        result = analyze_payload(
            {
                "text": "[2026-03-08 12:00:00] ERROR: Timeout\n",
                "levels": ["ERROR"],
            }
        )

        self.assertEqual(result["summary"]["matching_entries"], 1)
        self.assertEqual(result["entries"][0]["message"], "Timeout")

    def test_analyze_payload_rejects_empty_text(self) -> None:
        with self.assertRaises(ValueError):
            analyze_payload({"text": "   "})


if __name__ == "__main__":
    unittest.main()
