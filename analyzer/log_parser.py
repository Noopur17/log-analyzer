import re
from datetime import datetime

class LogParser:
    def __init__(self, log_file):
        self.log_file = log_file
        self.entries = []

    def parse(self):
        with open(self.log_file, 'r') as f:
            for line in f:
                match = re.match(r'\[(.*?)\] (\w+): (.*)', line)
                if match:
                    timestamp, level, message = match.groups()
                    self.entries.append({
                        "timestamp": datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"),
                        "level": level,
                        "message": message
                    })
        return self.entries