from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


LOG_PATTERN = re.compile(r"\[(?P<timestamp>.*?)\]\s+(?P<level>\w+):\s+(?P<message>.*)")
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


@dataclass(frozen=True)
class LogEntry:
    timestamp: datetime
    level: str
    message: str
    source: str
    line_number: int


@dataclass(frozen=True)
class ParseResult:
    entries: list[LogEntry]
    files_scanned: int
    total_lines: int
    parsed_lines: int
    skipped_lines: int


def parse_timestamp(raw_value: str) -> datetime:
    return datetime.strptime(raw_value, TIMESTAMP_FORMAT)


def parse_log_line(raw_line: str, source: Path | str, line_number: int) -> LogEntry | None:
    match = LOG_PATTERN.match(raw_line)
    if not match:
        return None

    try:
        timestamp = parse_timestamp(match.group("timestamp"))
    except ValueError:
        return None

    return LogEntry(
        timestamp=timestamp,
        level=match.group("level").upper(),
        message=match.group("message"),
        source=str(source),
        line_number=line_number,
    )


def resolve_log_paths(paths: list[str], recursive: bool = False) -> list[Path]:
    resolved_paths: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            raise FileNotFoundError(f"log path does not exist: {raw_path}")
        if path.is_file():
            resolved_paths.append(path)
            continue

        iterator = path.rglob("*.log") if recursive else path.glob("*.log")
        directory_files = sorted(child for child in iterator if child.is_file())
        if not directory_files:
            raise FileNotFoundError(f"no .log files found in directory: {raw_path}")
        resolved_paths.extend(directory_files)

    deduped = sorted({path.resolve() for path in resolved_paths})
    return deduped


class LogParser:
    def __init__(self, paths: list[str], recursive: bool = False):
        self.paths = paths
        self.recursive = recursive

    def parse(self) -> ParseResult:
        entries: list[LogEntry] = []
        total_lines = 0
        skipped_lines = 0
        file_paths = resolve_log_paths(self.paths, recursive=self.recursive)

        for path in file_paths:
            with path.open("r", encoding="utf-8") as log_file:
                for line_number, raw_line in enumerate(log_file, start=1):
                    total_lines += 1
                    entry = parse_log_line(raw_line.rstrip("\n"), path, line_number)
                    if entry is None:
                        skipped_lines += 1
                        continue
                    entries.append(entry)

        return ParseResult(
            entries=entries,
            files_scanned=len(file_paths),
            total_lines=total_lines,
            parsed_lines=len(entries),
            skipped_lines=skipped_lines,
        )
