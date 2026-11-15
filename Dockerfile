# Website Monitor: the API (python api.py), the scheduler
# (python scheduler.py), the command line (websites-monitor) and the MCP
# server (websites-monitor mcp) run from this image.
FROM python:3.11-slim@sha256:07d4824036af339fa1b6ef769cc99d9c10a141769538b52b3b597c84f7a7b535

LABEL org.opencontainers.image.title="Website Monitor" \
      org.opencontainers.image.description="Security, performance and SEO checks for websites, with a web UI and a REST API" \
      org.opencontainers.image.source="https://github.com/fabriziosalmi/websites-monitor" \
      org.opencontainers.image.licenses="MIT"

WORKDIR /app

# curl for the health check; dnsutils and whois for the DNS and WHOIS checks.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    dnsutils \
    whois \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/logs /app/reports \
    && printf '#!/bin/sh\nexec python -m websites_monitor "$@"\n' > /usr/local/bin/websites-monitor \
    && chmod 0755 /usr/local/bin/websites-monitor

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "api.py"]
