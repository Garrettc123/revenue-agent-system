# 🚀 Deployment Guide

## Quick Start Options

### 1. Local Docker Deployment (Fastest)

```bash
# Clone repository
git clone https://github.com/Garrettc123/revenue-agent-system.git
cd revenue-agent-system

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Services will be available at:**
- Main API: http://localhost:8000
- MLOps API: http://localhost:8090
- Grafana Dashboard: http://localhost:3000 (admin/admin2025)
- Prometheus: http://localhost:9090

---

### 2. Cloud Deployment (Render.com - Free Tier)

**One-Click Deploy:**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Garrettc123/revenue-agent-system)

**Manual Deploy:**

1. Create account at [render.com](https://render.com)
2. Connect GitHub repository
3. Deploy using `render.yaml` configuration
4. Services auto-deploy on git push

**Your APIs will be live at:**
- `https://revenue-agent-api.onrender.com`
- `https://mlops-api.onrender.com`

---

### 3. GitHub Actions CI/CD

**Auto-deployment on every push:**

1. Add secrets to GitHub repository:
   - Settings → Secrets → Actions
   - Add `RENDER_API_KEY`
   - Add `RENDER_SERVICE_ID`

2. Push to main branch:
```bash
git add .
git commit -m "Deploy update"
git push origin main
```

3. Watch deployment: Actions tab in GitHub

---

### 4. Manual Python Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run main API
python backend/main.py

# Run MLOps API (separate terminal)
python mlops-system/prometheus-ultraops.py

# Run trading bot (separate terminal)
python trading-systems/predictive-trading-bot.py
```

---

## System Requirements

### Minimum:
- 2 CPU cores
- 4GB RAM
- 10GB disk space
- Python 3.11+

### Recommended:
- 4 CPU cores
- 8GB RAM
- 20GB SSD
- Docker & Docker Compose

---

## Environment Variables

```bash
# Required
PAYMENT_ACCOUNT=gwc2780@gmail.com
API_TOKEN=prometheus-production-token-2025

# Database
POSTGRES_HOST=localhost
POSTGRES_DB=revenue_agent
POSTGRES_USER=agent
POSTGRES_PASSWORD=secure_password_2025

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Trading
TICKERS=AAPL,TSLA,MSFT,NVDA,GOOGL,AMZN
```

---

## Health Checks

```bash
# Main API
curl http://localhost:8000/health

# MLOps API
curl http://localhost:8090/health

# Test prediction
curl -X POST http://localhost:8090/predict \
  -H "Authorization: Bearer prometheus-production-token-2025" \
  -H "Content-Type: application/json" \
  -d '{
    "lag_1": 105.5,
    "rolling_mean_7": 104.2,
    "volatility_7": 0.015
  }'
```

---

## Monitoring

**Grafana Dashboard:**
1. Open http://localhost:3000
2. Login: admin / admin2025
3. View "Revenue Agent System" dashboard

**Prometheus Metrics:**
1. Open http://localhost:9090
2. Query: `up` to check service status
3. Query: `rate(http_requests_total[5m])` for request rate

---

## Troubleshooting

### Docker Issues:
```bash
# Stop all services
docker-compose down

# Remove volumes (fresh start)
docker-compose down -v

# Rebuild containers
docker-compose build --no-cache

# Start with logs
docker-compose up
```

### Python Issues:
```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.11+
```

### Port Conflicts:
```bash
# Check what's using ports
lsof -i :8000
lsof -i :8090
lsof -i :3000

# Kill processes
kill -9 <PID>
```

---

## Scaling

### Horizontal Scaling:
```bash
# Scale trading bot instances
docker-compose up -d --scale trading-bot=3

# Scale MLOps API instances
docker-compose up -d --scale mlops-api=5
```

### Kubernetes Deployment:
```bash
# Coming soon: K8s manifests
kubectl apply -f k8s/
```

---

## Support

- **GitHub Issues:** https://github.com/Garrettc123/revenue-agent-system/issues
- **Payment Account:** gwc2780@gmail.com
- **Documentation:** See README.md

---

**🎉 Your system is now PRODUCTION READY!**
