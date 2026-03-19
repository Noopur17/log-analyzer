FROM python:3.11-slim

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["log-analyzer-web"]

ARG CACHE_BUST=1
RUN echo "Build time: $CACHE_BUST"