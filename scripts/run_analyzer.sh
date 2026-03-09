#!/bin/bash
# Usage: ./scripts/run_analyzer.sh logs/sample.log
python3 -m analyzer.cli --log "$@"
