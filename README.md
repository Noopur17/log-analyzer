# Log Analyzer

`log-analyzer` is a small Python CLI for parsing structured application logs, filtering them, and generating reports in table, JSON, or CSV format.

## Features

- Parse log lines in the format `[YYYY-MM-DD HH:MM:SS] LEVEL: message`
- Read one file, many files, or directories of `.log` files
- Filter by level, time range, or message text
- Print a terminal summary or write JSON/CSV reports
- Track skipped malformed lines so bad input is visible
- Includes a browser UI for pasted logs and file uploads backed by the Python analyzer

## Quick Start

### Run from source

```bash
python3 -m analyzer.cli --log logs/sample.log
```

### Run the browser UI

```bash
./scripts/run_ui.sh
```

Then open [http://localhost:8000](http://localhost:8000).

### Install as a CLI

```bash
python3 -m pip install .
log-analyzer --log logs/sample.log --format json --output report.json
```

### Run with Docker

Build the image:

```bash
docker build -t log-analyzer:latest -f dockerfile .
```

Run the web UI container:

```bash
docker run --rm -p 8000:8000 log-analyzer:latest
```

Then open [http://localhost:8000](http://localhost:8000).

Run the CLI inside the image:

```bash
docker run --rm -v "$PWD/logs:/app/logs" log-analyzer:latest log-analyzer --log /app/logs/sample.log
```

### GitHub Actions Docker publish

This repo now includes a GitHub Actions workflow at `.github/workflows/docker-publish.yml`.

It does two things:

- runs the Python test suite on every push and pull request
- builds and pushes Docker images to `noopur17/log-analyzer` on pushes to `main` and tags like `v0.1.0`

Set these GitHub repository secrets before using it:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

Recommended tag flow:

```bash
git tag v0.1.0
git push origin main --tags
```

## Usage

```bash
python3 -m analyzer.cli --log logs/sample.log
python3 -m analyzer.cli --log logs/sample.log --level ERROR
python3 -m analyzer.cli --log logs/sample.log --since "2026-03-08 12:01:00" --format json
python3 -m analyzer.cli --log logs --recursive --contains timeout --format csv --output report.csv
```

## Validation

Run the automated tests:

```bash
python3 -m unittest discover -s tests -v
```

Manual validation:

```bash
python3 -m analyzer.cli --log logs/sample.log
python3 -m analyzer.cli --log logs/sample.log --format json --output report.json
cat report.json
```

Validate the UI locally:

```bash
./scripts/run_ui.sh
```

Open [http://localhost:8000](http://localhost:8000), click `Load sample`, then verify the summary shows:

- `Files: 1`
- `Lines: 5`
- `Parsed: 4`
- `Skipped: 1`
- `Matches: 4`

The UI sends pasted or uploaded log text to the local Python backend at `/api/analyze`, so the UI and CLI use the same parsing and filtering logic.

## Example Output

```text
Files scanned: 1
Total lines: 5
Parsed lines: 4
Skipped lines: 1
Matching entries: 4
Time range: 2026-03-08 12:00:00 to 2026-03-08 12:03:00

Counts by level
ERROR    2
INFO     1
WARNING  1

Top messages
2        Database timeout
1        Application started
1        Disk usage high
```
