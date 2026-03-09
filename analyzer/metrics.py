from __future__ import annotations

from collections import Counter
from datetime import datetime

from analyzer.log_parser import LogEntry, ParseResult


def filter_entries(
    entries: list[LogEntry],
    levels: list[str] | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    contains: str | None = None,
) -> list[LogEntry]:
    normalized_levels = {level.upper() for level in levels or []}
    contains_value = contains.lower() if contains else None

    filtered: list[LogEntry] = []
    for entry in entries:
        if normalized_levels and entry.level not in normalized_levels:
            continue
        if since and entry.timestamp < since:
            continue
        if until and entry.timestamp > until:
            continue
        if contains_value and contains_value not in entry.message.lower():
            continue
        filtered.append(entry)
    return filtered


def summarize_logs(
    entries: list[LogEntry],
    parse_result: ParseResult,
    top_messages: int = 5,
) -> dict:
    counts_by_level = dict(sorted(Counter(entry.level for entry in entries).items()))
    message_counts = Counter(entry.message for entry in entries)
    ranked_messages = [
        {"message": message, "count": count}
        for message, count in message_counts.most_common(top_messages)
    ]

    timestamps = [entry.timestamp for entry in entries]
    first_timestamp = min(timestamps).strftime("%Y-%m-%d %H:%M:%S") if timestamps else None
    last_timestamp = max(timestamps).strftime("%Y-%m-%d %H:%M:%S") if timestamps else None

    return {
        "files_scanned": parse_result.files_scanned,
        "total_lines": parse_result.total_lines,
        "parsed_lines": parse_result.parsed_lines,
        "skipped_lines": parse_result.skipped_lines,
        "matching_entries": len(entries),
        "counts_by_level": counts_by_level,
        "first_timestamp": first_timestamp,
        "last_timestamp": last_timestamp,
        "top_messages": ranked_messages,
        "levels_present": sorted(counts_by_level.keys()),
    }
