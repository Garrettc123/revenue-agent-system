# 🚀 Revenue Agent System - Quick Deploy

## Instant Deployment (One Command)

```bash
./deploy.sh local
```

That's it! Your revenue system is now running.

## Access Your Dashboard

- **Revenue Dashboard**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Grafana Monitoring**: http://localhost:3000 (admin/admin123)
- **Prometheus Metrics**: http://localhost:9090

## What Just Happened?

The deployment script automatically:
1. ✅ Checked Docker is installed
2. ✅ Created .env configuration file
3. ✅ Built all Docker containers
4. ✅ Started all services (App, PostgreSQL, Redis, MongoDB, Prometheus, Grafana)
5. ✅ Verified the system is healthy

## Next Steps

### 1. Configure Payment Integration
Edit `.env` and add your Stripe keys:
```bash
STRIPE_SECRET_KEY=sk_live_your_actual_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_actual_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

Then restart:
```bash
docker-compose restart revenue-app
```

### 2. Production Deployment

**Option A: Railway (Recommended)**
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

**Option B: Render**
```bash
# Push to GitHub, then connect repository in Render dashboard
# Render will auto-deploy using render.yaml configuration
```

**Option C: Docker on Any Server**
```bash
# On your production server
git clone https://github.com/Garrettc123/revenue-agent-system.git
cd revenue-agent-system
cp .env.example .env
# Edit .env with production values
./deploy.sh production
```

### 3. Enable Auto-Deployment

GitHub Actions will automatically deploy when you push to main/master branch.

**Configure deployment secrets:**
1. Go to GitHub repository → Settings → Secrets
2. Add secrets:
   - `RENDER_DEPLOY_HOOK` - Get from Render dashboard
   - `RAILWAY_TOKEN` - Get from Railway dashboard

## View Logs

```bash
# All services
docker-compose logs -f

# Just the app
docker-compose logs -f revenue-app
```

## Stop Services

```bash
docker-compose down
```

## Complete Documentation

See [DEPLOYMENT.md](./DEPLOYMENT.md) for comprehensive deployment guide.

---

**Status**: ✅ Production Ready | **Last Updated**: February 2026
