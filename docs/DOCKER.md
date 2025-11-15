# 🐳 Docker Deployment Guide

This guide explains how to run the Website Monitor using Docker and Docker Compose for easy deployment and scaling.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose V2
- Git (to clone the repository)

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/fabriziosalmi/websites-monitor.git
cd websites-monitor

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment
Edit `.env` file with your settings:
```bash
# Google PageSpeed API Key (optional but recommended)
PAGESPEED_API_KEY=your_api_key_here

# Monitoring interval (3600 = 1 hour)
MONITOR_INTERVAL=3600

# Database password for production
DB_PASSWORD=your_secure_password
```

### 3. Configure Websites
Edit `config.yaml` to specify websites to monitor:
```yaml
websites:
  - example.com
  - your-website.com
```

### 4. Start Services
```bash
# Basic setup (API + Scheduler)
docker-compose up -d

# Production setup (with Nginx, Redis, PostgreSQL)
docker-compose --profile production up -d
```

## 📊 Service Architecture

### Core Services
- **website-monitor-api**: FastAPI REST API server
- **website-monitor-scheduler**: Periodic monitoring service

### Production Services (optional)
- **nginx**: Reverse proxy with SSL termination
- **redis**: Caching and task queue
- **postgres**: Results storage database

## 🔧 Configuration Options

### Basic Setup
```bash
# Start only API service
docker-compose up website-monitor-api

# Start API + Scheduler
docker-compose up website-monitor-api website-monitor-scheduler

# View logs
docker-compose logs -f website-monitor-api
```

### Production Setup
```bash
# Full production stack
docker-compose --profile production up -d

# Scale API service
docker-compose up --scale website-monitor-api=3

# Update services
docker-compose pull && docker-compose up -d
```

### Custom Configurations

#### Custom Monitoring Interval
```bash
# Check every 30 minutes
MONITOR_INTERVAL=1800 docker-compose up -d

# Check every 6 hours  
MONITOR_INTERVAL=21600 docker-compose up -d
```

#### Custom API Port
```bash
# Run on port 9000
sed -i 's/8000:8000/9000:8000/' docker-compose.yml
docker-compose up -d
```

## 📁 Volume Mounts

The following directories are mounted for persistence:

```yaml
volumes:
  - ./config.yaml:/app/config.yaml:ro        # Configuration (read-only)
  - ./reports:/app/reports                   # Generated reports
  - ./logs:/app/logs                         # Application logs
  - ./README.md:/app/README.md               # Updated README
```

## 🌐 Access Points

After starting the services:

- **🏠 API Homepage**: http://localhost:8000/
- **📚 Interactive Docs (Swagger)**: http://localhost:8000/api/docs
- **📖 API Reference (ReDoc)**: http://localhost:8000/api/redoc
- **📊 Health Check**: http://localhost:8000/health

With Nginx (production):
- **🌍 Main Site**: http://localhost/
- **🔒 HTTPS**: https://localhost/ (after SSL setup)

## 🔍 Monitoring & Debugging

### Service Status
```bash
# Check all services
docker-compose ps

# Check specific service
docker-compose ps website-monitor-api

# View service logs
docker-compose logs -f website-monitor-api
docker-compose logs -f website-monitor-scheduler
```

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# Container health
docker inspect website-monitor-api | grep -A 5 Health
```

### Resource Usage
```bash
# Monitor resource usage
docker stats

# Monitor specific container
docker stats website-monitor-api
```

## 🗄️ Database Integration (Production)

When using the production profile, PostgreSQL stores monitoring results:

```bash
# Connect to database
docker-compose exec postgres psql -U monitor_user -d website_monitor

# View recent results
docker-compose exec postgres psql -U monitor_user -d website_monitor -c "
  SELECT website, check_name, result, timestamp 
  FROM monitoring_results 
  ORDER BY timestamp DESC 
  LIMIT 10;
"
```

## 🚀 Deployment Scenarios

### Development
```bash
# Quick start for development
docker-compose up website-monitor-api
```

### Production (Single Server)
```bash
# Full production stack
docker-compose --profile production up -d

# With custom domain
docker-compose --profile production up -d
# Then configure your domain DNS to point to the server
```

### Production (Load Balanced)
```bash
# Scale API service
docker-compose --profile production up -d --scale website-monitor-api=3

# Use external load balancer pointing to nginx
```

## 🔒 SSL Configuration

### Self-Signed Certificate (Development)
```bash
# Create SSL directory
mkdir -p docker/ssl

# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout docker/ssl/key.pem -out docker/ssl/cert.pem -days 365 -nodes -subj "/CN=localhost"

# Enable HTTPS in nginx.conf (uncomment HTTPS section)
```

### Let's Encrypt (Production)
```bash
# Using certbot
docker run --rm -v $(pwd)/docker/ssl:/etc/letsencrypt/live/yourdomain.com certbot/certbot certonly --standalone -d yourdomain.com

# Update nginx.conf with proper certificate paths
```

## 🔧 Customization

### Custom Checks
Add new check files to `checks/` directory and rebuild:
```bash
# Add new check file
echo "def check_custom(): return '🟢'" > checks/check_custom.py

# Rebuild container
docker-compose build website-monitor-api
docker-compose up -d
```

### Custom API Configuration
Create custom API configuration:
```python
# Create custom_api.py
from api import app
# Add custom routes

# Update docker-compose.yml
command: ["python", "custom_api.py"]
```

## 📊 Monitoring Integration

### Prometheus Metrics
```bash
# Add metrics endpoint to API
# Mount prometheus config
volumes:
  - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

# Add prometheus service
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
```

### Grafana Dashboard
```bash
# Add Grafana service
services:
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 🧹 Maintenance

### Update Services
```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose up -d

# Clean old images
docker image prune
```

### Backup Data
```bash
# Backup database
docker-compose exec postgres pg_dump -U monitor_user website_monitor > backup.sql

# Backup reports
tar -czf reports_backup.tar.gz reports/
```

### Log Rotation
```bash
# Configure log rotation
docker run --log-driver=json-file --log-opt max-size=10m --log-opt max-file=3 ...
```

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Check what's using port 8000
lsof -i :8000

# Use different port
sed -i 's/8000:8000/8001:8000/' docker-compose.yml
```

**Permission issues:**
```bash
# Fix volume permissions
sudo chown -R $USER:$USER reports logs
```

**Memory issues:**
```bash
# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory

# Monitor container memory
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

**Network issues:**
```bash
# Check network connectivity
docker-compose exec website-monitor-api ping google.com

# Check DNS resolution
docker-compose exec website-monitor-api nslookup example.com
```

### Performance Tuning

**API Performance:**
```bash
# Increase workers
command: ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Enable async processing
environment:
  - ASYNC_WORKERS=4
```

**Database Performance:**
```bash
# Tune PostgreSQL
environment:
  - POSTGRES_SHARED_BUFFERS=256MB
  - POSTGRES_MAX_CONNECTIONS=100
```

## 📞 Support

For Docker-related issues:
- Check logs: `docker-compose logs -f [service-name]`
- Verify configuration: `docker-compose config`
- Restart services: `docker-compose restart [service-name]`

For application issues:
- API docs: http://localhost:8000/api/docs
- Health check: http://localhost:8000/health
- GitHub issues: https://github.com/fabriziosalmi/websites-monitor/issues

---

Made with ❤️ by [Fabrizio Salmi](https://github.com/fabriziosalmi) • [![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/fabriziosalmi/websites-monitor)
