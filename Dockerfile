# Website Monitor: the API (python api.py) and the scheduler
# (python scheduler.py) run from this image.
FROM python:3.15-slim@sha256:8c13a3f37a6a5b71498228e902c4b9f51c1f7900d49fabf71f9a650c6120e0d0

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
RUN mkdir -p /app/logs /app/reports

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "api.py"]
