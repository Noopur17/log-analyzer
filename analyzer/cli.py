from __future__ import annotations

import argparse
import sys
from datetime import datetime

from analyzer.log_parser import LogParser, TIMESTAMP_FORMAT
from analyzer.metrics import filter_entries, summarize_logs
from analyzer.reporter import generate_report

HELP_TIMESTAMP_FORMAT = TIMESTAMP_FORMAT.replace("%", "%%")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze structured application logs.")
    parser.add_argument(
        "--log",
        nargs="+",
        required=True,
        help="One or more log files or directories containing .log files.",
    )
    parser.add_argument(
        "--output",
        help="Optional report output path. Required for csv output.",
    )
    parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Report format.",
    )
    parser.add_argument(
        "--level",
        action="append",
        help="Filter to one or more log levels. Can be passed multiple times.",
    )
    parser.add_argument(
        "--since",
        help=f"Only include entries on or after this timestamp ({HELP_TIMESTAMP_FORMAT}).",
    )
    parser.add_argument(
        "--until",
        help=f"Only include entries on or before this timestamp ({HELP_TIMESTAMP_FORMAT}).",
    )
    parser.add_argument(
        "--contains",
        help="Only include entries whose message contains this text.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively scan directories passed to --log.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of top repeated messages to include.",
    )
    return parser


def parse_cli_timestamp(raw_value: str | None, label: str) -> datetime | None:
    if raw_value is None:
        return None
    try:
        return datetime.strptime(raw_value, TIMESTAMP_FORMAT)
    except ValueError as exc:
        raise ValueError(f"invalid {label} timestamp '{raw_value}', expected {TIMESTAMP_FORMAT}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        since = parse_cli_timestamp(args.since, "since")
        until = parse_cli_timestamp(args.until, "until")
        if since and until and since > until:
            raise ValueError("--since must be earlier than or equal to --until")

        parse_result = LogParser(args.log, recursive=args.recursive).parse()
        matching_entries = filter_entries(
            parse_result.entries,
            levels=args.level,
            since=since,
            until=until,
            contains=args.contains,
        )
        summary = summarize_logs(matching_entries, parse_result, top_messages=args.top)
        report = generate_report(summary, output_format=args.format, output_file=args.output)

        if args.output:
            print(f"Report saved to {args.output}")
        else:
            print(report)
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
