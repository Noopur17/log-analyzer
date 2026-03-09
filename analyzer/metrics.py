from collections import Counter

def summarize_logs(entries):
    levels = [e['level'] for e in entries]
    summary = Counter(levels)
    return summary