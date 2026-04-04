# Revenue Agent System - Complete Deployment Guide

## 🚀 Quick Start (5 Minutes to Running System)

### Prerequisites
- Docker & Docker Compose installed
- Git installed
- GitHub account with repository access

### Step 1: Clone Repository
```bash
git clone https://github.com/Garrettc123/revenue-agent-system.git
cd revenue-agent-system
```

### Step 2: Create Environment File
Create `.env` file in the root directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://revenue_user:changeme123@postgres:5432/revenue_db
POSTGRES_PASSWORD=changeme123
MONGODB_PASSWORD=changeme123
MONGODB_URI=mongodb://admin:changeme123@mongodb:27017

# Payment Integration
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Monitoring
GRAFANA_PASSWORD=admin123

# APIs & Webhooks
OPENAI_API_KEY=sk-your_openai_key
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Step 3: Create docker-compose.yml
```yaml
version: '3.8'

services:
  revenue-app:
    build: .
    container_name: revenue-agent
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - MONGODB_URI=${MONGODB_URI}
      - SLACK_WEBHOOK=${SLACK_WEBHOOK}
    depends_on:
      - postgres
      - redis
      - mongodb
    restart: unless-stopped
    networks:
      - revenue-network

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=revenue_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=revenue_db
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - revenue-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - revenue-network

  mongodb:
    image: mongo:7
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=${MONGODB_PASSWORD}
    ports:
      - "27017:27017"
    volumes:
      - mongodb-data:/data/db
    restart: unless-stopped
    networks:
      - revenue-network

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - prometheus-data:/prometheus
    restart: unless-stopped
    networks:
      - revenue-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
    restart: unless-stopped
    networks:
      - revenue-network

volumes:
  postgres-data:
  redis-data:
  mongodb-data:
  prometheus-data:
  grafana-data:

networks:
  revenue-network:
    driver: bridge
```

### Step 4: Deploy
```bash
docker-compose up -d
```

### Step 5: Verify Deployment
```bash
# Check all services are running
docker-compose ps

# Check application health
curl http://localhost:8000/health

# View logs
docker-compose logs -f revenue-app
```

## 📊 Access Your Systems

| Service | URL | Credentials |
|---------|-----|-------------|
| Revenue App | http://localhost:8000 | - |
| Grafana Dashboard | http://localhost:3000 | admin / admin123 |
| Prometheus | http://localhost:9090 | - |
| PostgreSQL | localhost:5432 | revenue_user / changeme123 |
| MongoDB | localhost:27017 | admin / changeme123 |
| Redis | localhost:6379 | - |

## 🔄 Production Deployment Options

### Option 1: Railway (Recommended)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Deploy
railway up
```

### Option 2: AWS EKS
1. Create EKS cluster
2. Configure kubectl
3. Apply Kubernetes manifests (see k8s/ directory)
4. Deploy using GitHub Actions workflow

### Option 3: Vercel (Frontend) + Railway (Backend)
- Use existing Vercel integration
- Deploy backend to Railway
- Configure environment variables in both platforms

## 🛠️ Development Workflow

### Local Development
```bash
# Start services
docker-compose up -d

# Make code changes
# ...

# Rebuild and restart
docker-compose up -d --build revenue-app

# View logs
docker-compose logs -f revenue-app
```

### Running Tests
```bash
# Inside container
docker-compose exec revenue-app python -m pytest

# Or locally
pip install -r requirements.txt
pytest
```

## 💰 Revenue Stream Activation

### 1. Configure Stripe for Auto-Revenue Retrieval
The system automatically fetches real-time revenue data from Stripe.

1. Get API keys from https://dashboard.stripe.com/apikeys
2. Add to `.env` file:
   ```bash
   STRIPE_SECRET_KEY=sk_test_your_key_here
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
   ```
3. Set up webhooks at: `https://your-domain.com/webhooks/stripe`
4. Select these webhook events:
   - `payment_intent.succeeded`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `charge.succeeded`
   - `invoice.payment_succeeded`
5. Copy the webhook signing secret and add to `.env`

### 2. Test Auto-Revenue Endpoints

```bash
# Check revenue data (auto-fetches from Stripe)
curl http://localhost:5000/api/revenue

# Manually trigger revenue sync
curl -X POST http://localhost:5000/api/revenue/sync

# Test webhook endpoint
curl -X POST http://localhost:5000/webhooks/stripe \
  -H "Content-Type: application/json" \
  -d '{"type": "payment_intent.succeeded", "data": {"object": {"amount": 5000}}}'
```

### 3. Access Live Dashboard
- Dashboard: http://localhost:5000
- Auto-refreshes every 5 seconds with real Stripe data
- Shows MRR, customer count, and system status

### 4. Monitor Revenue
- Grafana: http://localhost:3000
- Check dashboard: "Revenue Metrics"
- Slack notifications configured via webhook
- Real-time webhook events logged in application logs

## 📈 Monitoring & Observability

### Grafana Dashboards
1. Login to http://localhost:3000
2. Navigate to Dashboards
3. Import pre-configured dashboards:
   - Revenue Metrics
   - System Health
   - API Performance

### Prometheus Metrics
- Application metrics: http://localhost:8000/metrics
- Prometheus UI: http://localhost:9090

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f revenue-app

# Last 100 lines
docker-compose logs --tail=100 revenue-app
```

## 🔒 Security Checklist

- [ ] Change all default passwords in `.env`
- [ ] Use strong PostgreSQL password
- [ ] Enable HTTPS/TLS in production
- [ ] Rotate API keys regularly
- [ ] Enable GitHub secret scanning
- [ ] Configure firewall rules
- [ ] Set up automated backups
- [ ] Enable 2FA on all accounts

## 🚨 Troubleshooting

### Application Won't Start
```bash
# Check logs
docker-compose logs revenue-app

# Rebuild image
docker-compose build --no-cache revenue-app
docker-compose up -d
```

### Database Connection Issues
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Connect to database
docker-compose exec postgres psql -U revenue_user -d revenue_db
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

## 📞 Support & Resources

- **GitHub Issues**: https://github.com/Garrettc123/revenue-agent-system/issues
- **Deployment Script**: `../master-deployment-auto-deploy-revenue/scripts/autodeploy-revenue-systems.sh`
- **Status Page**: Check GitHub Actions for deployment status

## ⚡ Next Steps

1. ✅ Deploy locally (completed above)
2. 🔄 Set up production deployment (Railway/AWS)
3. 💳 Configure payment webhooks
4. 📊 Customize Grafana dashboards
5. 🤖 Enable GitHub Actions auto-deployment
6. 💰 Start generating revenue!

---

**Last Updated**: February 15, 2026
**Status**: Production Ready 🚀
