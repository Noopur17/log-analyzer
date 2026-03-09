FROM python:3.11-slim

WORKDIR /app

# Install the project so the packaged CLI is available
COPY pyproject.toml README.md ./
COPY analyzer ./analyzer
RUN pip install --no-cache-dir .

COPY . .

ENTRYPOINT ["log-analyzer"]
