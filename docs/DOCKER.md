# Running with Docker

`docker-compose.yml` runs two containers from the image built by the `Dockerfile` (Python 3.11, base image pinned by digest).

| Service | Command | What it does |
|---|---|---|
| `website-monitor-api` | `python api.py` | REST API and web UI on port 8000 inside the container. |
| `website-monitor-scheduler` | `python scheduler.py` | Runs `main.py` every `MONITOR_INTERVAL` seconds (default 3600) and writes `reports/report.md`. A run that takes more than 30 minutes is stopped. |

Both run with `mem_limit: 256m` and `no-new-privileges`, and restart unless stopped.

## Start

```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
curl -s http://127.0.0.1:8000/health
```

The web UI is at http://127.0.0.1:8000/ and the API reference at http://127.0.0.1:8000/api/docs.

## Address and port

The API is published on `${WM_BIND_ADDRESS}:${WM_PORT}`, by default `127.0.0.1:8000`, so only the machine itself can reach it. To publish it on a network interface, set both in `.env`:

```bash
WM_BIND_ADDRESS=192.0.2.10    # an address of this host, or 0.0.0.0 for all
WM_PORT=18000
```

The API has no authentication and its checks send requests to any host they are given, including hosts inside your network. Publish it only on a trusted network or behind an authenticating reverse proxy. See [SECURITY.md](../SECURITY.md).

## Keys

Set in `.env`; all optional. A check that needs a missing key returns no verdict and names the key.

| Variable | Check |
|---|---|
| `PAGESPEED_API_KEY` | `pagespeed_performances`, and the Lighthouse score of `accessibility` |
| `GITHUB_TOKEN` | `data_leakage` |
| `WAVE_API_KEY` | `accessibility`, when Lighthouse gives no score |

## Files

| Host path | Container path | Used by |
|---|---|---|
| `config.yaml` | `/app/config.yaml` (read only) | Both: the sites the scheduler checks. |
| `docs/` | `/app/docs` (read only) | API: the web UI. Edits show up without rebuilding the image. |
| `reports/` | `/app/reports` | Scheduler: `report.md`. |
| `logs/` | `/app/logs` | Scheduler: `scheduler.log`. |

The domain blacklist (107 MB) is downloaded when the API starts and cached in the container's `/tmp/websites-monitor/`. Once the copy is more than an hour old, the next check that reads it starts a download in the background and keeps using the old copy until the new one is complete. A new container downloads it again.

## Update

```bash
git pull
docker compose up -d --build
```

## Logs and status

```bash
docker compose logs -f website-monitor-api
docker compose logs -f website-monitor-scheduler
docker inspect -f '{{.State.Health.Status}}' website-monitor-api
```

The API container has a health check on `GET /health`. The scheduler has none: if its process stops, the container stops and Docker restarts it.

## Command line and MCP server

The image has the `websites-monitor` command (the same as `python -m websites_monitor`):

```bash
docker exec website-monitor-api websites-monitor scan example.com --checks ssl_cert,hsts
docker exec website-monitor-api websites-monitor report example.com --format markdown
```

An MCP client can run the MCP server inside the container over stdio with `docker exec -i website-monitor-api websites-monitor mcp`; see the MCP section of the README for the client configuration.

## Prebuilt image

Each push to `main` publishes `ghcr.io/fabriziosalmi/websites-monitor:latest` for linux/amd64 and linux/arm64. To use it instead of building, replace `build: .` with `image: ghcr.io/fabriziosalmi/websites-monitor:latest` in both services. The image already contains the web UI, so the `./docs` mount is then optional.

To run the API alone:

```bash
docker run -d --name website-monitor -p 127.0.0.1:8000:8000 --memory 256m \
  ghcr.io/fabriziosalmi/websites-monitor:latest
```
