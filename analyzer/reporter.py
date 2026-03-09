from __future__ import annotations

import csv
import json
from pathlib import Path


def render_table(summary: dict) -> str:
    lines = [
        f"Files scanned: {summary['files_scanned']}",
        f"Total lines: {summary['total_lines']}",
        f"Parsed lines: {summary['parsed_lines']}",
        f"Skipped lines: {summary['skipped_lines']}",
        f"Matching entries: {summary['matching_entries']}",
    ]

    if summary["first_timestamp"] and summary["last_timestamp"]:
        lines.append(
            f"Time range: {summary['first_timestamp']} to {summary['last_timestamp']}"
        )

    lines.append("")
    lines.append("Counts by level")
    if summary["counts_by_level"]:
        for level, count in summary["counts_by_level"].items():
            lines.append(f"{level:<8} {count}")
    else:
        lines.append("No matching log entries")

    if summary["top_messages"]:
        lines.append("")
        lines.append("Top messages")
        for item in summary["top_messages"]:
            lines.append(f"{item['count']:<8} {item['message']}")

    return "\n".join(lines)


def write_json_report(summary: dict, output_file: str) -> None:
    with open(output_file, "w", encoding="utf-8") as report_file:
        json.dump(summary, report_file, indent=4)


def write_csv_report(summary: dict, output_file: str) -> None:
    with open(output_file, "w", encoding="utf-8", newline="") as report_file:
        writer = csv.DictWriter(
            report_file,
            fieldnames=["section", "name", "value", "count", "message"],
        )
        writer.writeheader()
        for name in [
            "files_scanned",
            "total_lines",
            "parsed_lines",
            "skipped_lines",
            "matching_entries",
            "first_timestamp",
            "last_timestamp",
        ]:
            writer.writerow({"section": "summary", "name": name, "value": summary[name]})
        for level, count in summary["counts_by_level"].items():
            writer.writerow(
                {"section": "levels", "name": level, "count": count}
            )
        for item in summary["top_messages"]:
            writer.writerow(
                {
                    "section": "messages",
                    "count": item["count"],
                    "message": item["message"],
                }
            )


def generate_report(summary: dict, output_format: str = "table", output_file: str | None = None) -> str:
    if output_format == "json":
        rendered = json.dumps(summary, indent=4)
        if output_file:
            write_json_report(summary, output_file)
        return rendered

    if output_format == "csv":
        if not output_file:
            raise ValueError("csv output requires --output")
        write_csv_report(summary, output_file)
        return str(Path(output_file))

    rendered = render_table(summary)
    if output_file:
        Path(output_file).write_text(rendered + "\n", encoding="utf-8")
    return rendered
