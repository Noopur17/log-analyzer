import argparse
from analyzer.log_parser import LogParser
from analyzer.metrics import summarize_logs
from analyzer.reporter import generate_report

def main():
    parser = argparse.ArgumentParser(description="Log Analyzer")
    parser.add_argument('--log', type=str, required=True, help='Path to log file')
    parser.add_argument('--output', type=str, default='report.json', help='Output report file')
    args = parser.parse_args()

    parser_obj = LogParser(args.log)
    entries = parser_obj.parse()
    summary = summarize_logs(entries)
    generate_report(summary, args.output)

if __name__ == "__main__":
    main()