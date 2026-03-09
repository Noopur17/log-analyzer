FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Set PYTHONPATH so imports work
ENV PYTHONPATH=/app

# ENTRYPOINT to allow passing arguments at runtime
ENTRYPOINT ["python3", "-m", "analyzer.cli"]