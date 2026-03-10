from __future__ import annotations

from datetime import datetime

from analyzer.log_parser import ParseResult, parse_log_line
from analyzer.metrics import filter_entries, summarize_logs


def parse_filter_timestamp(raw_value: str | None, label: str) -> datetime | None:
    if raw_value is None:
        return None

    from analyzer.log_parser import TIMESTAMP_FORMAT

    try:
        return datetime.strptime(raw_value, TIMESTAMP_FORMAT)
    except ValueError as exc:
        raise ValueError(
            f"invalid {label} timestamp '{raw_value}', expected {TIMESTAMP_FORMAT}"
        ) from exc


def parse_text_entries(text: str, source: str = "inline") -> ParseResult:
    entries = []
    total_lines = 0
    skipped_lines = 0

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip():
            continue
        total_lines += 1
        entry = parse_log_line(raw_line, source, line_number)
        if entry is None:
            skipped_lines += 1
            continue
        entries.append(entry)

    return ParseResult(
        entries=entries,
        files_scanned=1,
        total_lines=total_lines,
        parsed_lines=len(entries),
        skipped_lines=skipped_lines,
    )


def serialize_entry(entry) -> dict:
    return {
        "timestamp": entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "level": entry.level,
        "message": entry.message,
        "source": entry.source,
        "line_number": entry.line_number,
    }


def analyze_entries(
    parse_result: ParseResult,
    levels: list[str] | None = None,
    since: str | None = None,
    until: str | None = None,
    contains: str | None = None,
    top_messages: int = 5,
) -> dict:
    since_dt = parse_filter_timestamp(since, "since")
    until_dt = parse_filter_timestamp(until, "until")
    if since_dt and until_dt and since_dt > until_dt:
        raise ValueError("--since must be earlier than or equal to --until")

    matching_entries = filter_entries(
        parse_result.entries,
        levels=levels,
        since=since_dt,
        until=until_dt,
        contains=contains,
    )
    return {
        "summary": summarize_logs(matching_entries, parse_result, top_messages=top_messages),
        "entries": [serialize_entry(entry) for entry in matching_entries],
    }


def analyze_text(
    text: str,
    levels: list[str] | None = None,
    since: str | None = None,
    until: str | None = None,
    contains: str | None = None,
    top_messages: int = 5,
) -> dict:
    parse_result = parse_text_entries(text)
    return analyze_entries(
        parse_result,
        levels=levels,
        since=since,
        until=until,
        contains=contains,
        top_messages=top_messages,
    )
