# 💰 Revenue Agent System

> A comprehensive multi-stream revenue management platform that unifies subscription billing, affiliate programs, content monetization, and B2B services into a single, powerful system.

[![Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)](https://github.com/Garrettc123/revenue-agent-system)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🚀 Features

### Revenue Streams
- **💳 Subscription Management** - Stripe-powered SaaS billing with tiered pricing (Starter, Professional, Enterprise)
- **🤝 Affiliate & Referral Programs** - Commission tracking with automated payouts and partner tiers
- **📝 Content Monetization** - Creator revenue streams with usage tracking and licensing
- **🏢 Services Marketplace** - B2B service offerings with API-based billing
- **📊 Revenue Analytics** - Real-time dashboard with MRR, ARR, and customer metrics

### Technical Capabilities
- **Real-time Webhooks** - Instant event processing for payments and subscriptions
- **Multi-database Architecture** - PostgreSQL for transactions, MongoDB for documents, Redis for caching
- **Production-Ready** - Docker containerization with health checks and monitoring
- **Secure by Default** - Environment-based secrets, webhook verification, input validation
- **Scalable Infrastructure** - Gunicorn WSGI server with multiple workers

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [Security](#-security)
- [License](#-license)

## ⚡ Quick Start

Get the Revenue Agent System running in 5 minutes:

```bash
# Clone the repository
git clone https://github.com/Garrettc123/revenue-agent-system.git
cd revenue-agent-system

# Start with Docker Compose
docker-compose up -d

# Check application health
curl http://localhost:8000/health
```

Access the dashboard at **http://localhost:8000** 🎉

## 💻 Installation

### Prerequisites

- **Docker & Docker Compose** (recommended) OR
- **Python 3.11+** for local development
- **PostgreSQL 16+**, **MongoDB 7+**, **Redis 7+** (if running without Docker)

### Option 1: Docker (Recommended)

```bash
# Create environment file
cat > .env << EOF
DATABASE_URL=postgresql://revenue_user:changeme123@postgres:5432/revenue_db
MONGODB_URI=mongodb://admin:changeme123@mongodb:27017
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
EOF

# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f revenue-app
```

### Option 2: Local Development

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export STRIPE_SECRET_KEY=sk_test_your_key_here
export DATABASE_URL=postgresql://localhost/revenue_db

# Run the application
python app.py
```

The application will start on **http://localhost:5000**

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐
│  Flask App      │  ← Main web application (Python 3.11+)
│  (app.py)       │
└────────┬────────┘
         │
         ├─── Revenue Modules (Node.js/Express)
         │    ├── stripe-integration.js      (Subscriptions)
         │    ├── affiliate-system.js        (Referrals)
         │    ├── content-monetization.js    (Creators)
         │    └── services-marketplace.js    (B2B Services)
         │
         ├─── Data Layer
         │    ├── PostgreSQL    (Relational data)
         │    ├── MongoDB       (Document storage)
         │    └── Redis         (Caching/Sessions)
         │
         └─── External Services
              ├── Stripe        (Payments)
              ├── Prometheus    (Metrics)
              └── Grafana       (Dashboards)
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Flask 3.x (Python 3.11+) | Web application framework |
| **Web Server** | Gunicorn | Production WSGI server (2 workers, 120s timeout) |
| **Revenue Modules** | Node.js + Express.js | Modular revenue stream handlers |
| **Databases** | PostgreSQL 16, MongoDB 7, Redis 7 | Multi-database architecture |
| **Payments** | Stripe API | Payment processing and subscriptions |
| **Containers** | Docker + Docker Compose | Containerization and orchestration |
| **Monitoring** | Prometheus + Grafana | Metrics collection and visualization |
| **Deployment** | Render.com / Railway | Cloud hosting platforms |

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/revenue_db
MONGODB_URI=mongodb://user:password@host:27017
POSTGRES_PASSWORD=your_secure_password
MONGODB_PASSWORD=your_secure_password

# Stripe Configuration (Get from https://dashboard.stripe.com/apikeys)
STRIPE_SECRET_KEY=sk_test_or_live_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_or_live_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Stripe Price IDs (Create in Stripe Dashboard)
STRIPE_STARTER_PRICE_ID=price_starter_id
STRIPE_PROFESSIONAL_PRICE_ID=price_professional_id
STRIPE_ENTERPRISE_PRICE_ID=price_enterprise_id

# Application Configuration
PORT=8000
FLASK_ENV=production

# Monitoring
GRAFANA_PASSWORD=admin_password

# Optional: External Integrations
OPENAI_API_KEY=sk-your_openai_key
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK
```

### Stripe Setup

1. **Create a Stripe account** at https://stripe.com
2. **Get API keys** from Dashboard → Developers → API keys
3. **Create Products & Prices**:
   - Starter: $29/month
   - Professional: $99/month
   - Enterprise: $499/month
4. **Set up webhooks** at `https://your-domain.com/webhooks/stripe`
5. **Add webhook secret** to your `.env` file

## 🎯 Usage

### Access the Dashboard

Open your browser to:
- **Local**: http://localhost:8000
- **Docker**: http://localhost:8000
- **Production**: https://your-domain.com

The dashboard displays:
- 💰 Monthly Recurring Revenue (MRR)
- 👥 Active Customers
- 📈 Annual Recurring Revenue (ARR)
- ⚡ System Status

### API Endpoints

#### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "revenue-agent"
}
```

#### Revenue Metrics
```bash
GET /api/revenue
```

Response:
```json
{
  "mrr": 5000,
  "customers": 12,
  "arr": 60000,
  "timestamp": "2026-02-15T20:00:00.000000"
}
```

## 📚 API Documentation

### Subscription Tiers

| Tier | Price | Features |
|------|-------|----------|
| **Starter** | $29/mo | GitHub webhooks, Basic Linear sync, Notion automation, 100 AI analyses/month |
| **Professional** | $99/mo | All Starter + Advanced CI/CD, Full Linear integration, 1,000 AI analyses/month |
| **Enterprise** | $499/mo | All Professional + Unlimited analyses, Custom integrations, Dedicated support |

### Affiliate Commission Structure

| Product Tier | Recurring Commission | First Payment |
|--------------|---------------------|---------------|
| Starter | 30% | 15% |
| Professional | 25% | 20% |
| Enterprise | 20% | 25% |
| API Usage | 15% | - |

### Partner Tiers

| Tier | Min Monthly Revenue | Bonus | Benefits |
|------|-------------------|-------|----------|
| **Bronze** | $0 | 0% | Basic referral link, Monthly payouts |
| **Silver** | $5,000 | +5% | White-label page, Bi-weekly payouts |
| **Gold** | $25,000 | +10% | Custom integration, Weekly payouts |

## 🛠️ Development

### Project Structure

```
revenue-agent-system/
├── app.py                      # Main Flask application
├── stripe-integration.js       # Stripe subscription handling
├── affiliate-system.js         # Affiliate/referral program
├── content-monetization.js     # Content creator revenue
├── services-marketplace.js     # B2B services marketplace
├── revenue-dashboard.js        # Master dashboard router
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Multi-service orchestration
├── Procfile                    # Production deployment config
├── render.yaml                 # Render.com deployment
├── .github/
│   └── copilot-instructions.md # GitHub Copilot configuration
├── DEPLOYMENT.md               # Complete deployment guide
├── SECURITY.md                 # Security policy
└── README.md                   # This file
```

### Local Development Workflow

1. **Make code changes** to Python or JavaScript files
2. **Rebuild the container**:
   ```bash
   docker-compose up -d --build revenue-app
   ```
3. **View logs**:
   ```bash
   docker-compose logs -f revenue-app
   ```
4. **Test changes** in your browser or with curl

### Adding a New Revenue Module

Follow the established pattern:

```javascript
/**
 * Revenue System - Your Module Name
 * Brief description of functionality
 */

const express = require('express');
const router = express.Router();

// Configuration
const MODULE_CONFIG = {
  // Your settings
};

// Routes
router.post('/endpoint', async (req, res) => {
  try {
    // Implementation
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
```

### Coding Conventions

- **Python**: Follow PEP 8, use `jsonify()` for responses, ISO 8601 timestamps
- **JavaScript**: ES6+, JSDoc comments, Express Router pattern, `module.exports`
- **Security**: Never commit secrets, use environment variables, verify webhooks
- **Docker**: Host must be `0.0.0.0` for container compatibility

See `.github/copilot-instructions.md` for detailed coding standards.

## 🚢 Deployment

### Production Deployment Options

#### Option 1: Render.com (Recommended)

```bash
# Configure render.yaml (already included)
# Push to GitHub
git push origin main

# Deploy via Render Dashboard
# - Connect GitHub repository
# - Render will auto-detect render.yaml
# - Set environment variables in dashboard
```

#### Option 2: Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway up
```

#### Option 3: Docker on VPS

```bash
# On your server
git clone https://github.com/Garrettc123/revenue-agent-system.git
cd revenue-agent-system
cp .env.example .env
# Edit .env with your production values
docker-compose up -d
```

### Monitoring & Observability

Access monitoring dashboards:

- **Grafana**: http://localhost:3000 (admin / your_password)
- **Prometheus**: http://localhost:9090
- **Application Metrics**: http://localhost:8000/metrics

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python -m pytest

# Run with Docker
docker-compose exec revenue-app python -m pytest

# Run specific test file
python -m pytest tests/test_app.py

# Run with coverage
python -m pytest --cov=. --cov-report=html
```

### Manual Testing

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

Test revenue API:
```bash
curl http://localhost:8000/api/revenue
```

Test with Stripe test mode:
- Use test API keys (`sk_test_...`)
- Use test card: 4242 4242 4242 4242
- View test events in Stripe Dashboard

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Follow coding conventions** (see `.github/copilot-instructions.md`)
4. **Test locally with Docker** before committing
5. **Commit your changes**: `git commit -m "Add your feature"`
6. **Push to the branch**: `git push origin feature/your-feature`
7. **Open a Pull Request**

### Development Guidelines

- Follow existing code patterns and conventions
- Test locally with Docker before committing
- Update documentation if adding features
- Ensure security best practices are followed
- Verify environment variables are documented
- Test payment flows with Stripe test mode

## 🔒 Security

### Security Best Practices

- ✅ **Secrets**: Never commit secrets or API keys
- ✅ **Environment Variables**: Use `.env` for all sensitive data
- ✅ **Webhook Verification**: Always verify Stripe webhook signatures
- ✅ **HTTPS**: Use TLS/SSL in production
- ✅ **Input Validation**: Validate and sanitize all user inputs
- ✅ **Dependencies**: Regularly update dependencies

### Reporting Security Issues

Please report security vulnerabilities via GitHub Security Advisories or by contacting the maintainers directly. See [SECURITY.md](SECURITY.md) for details.

### Security Features

- Environment-based secret management
- Stripe webhook signature verification
- Docker security best practices (non-root user)
- Health check endpoints for monitoring
- Input validation on all endpoints

## 📖 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide with step-by-step instructions
- **[SECURITY.md](SECURITY.md)** - Security policy and vulnerability reporting
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - Coding standards and GitHub Copilot configuration

## 🔗 Resources

- **Stripe API Documentation**: https://stripe.com/docs/api
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Docker Documentation**: https://docs.docker.com/
- **Express.js Guide**: https://expressjs.com/

## 📊 Project Status

- ✅ **Production Ready** - Fully functional and tested
- ✅ **Docker Support** - Complete containerization
- ✅ **Multi-Stream Revenue** - All revenue modules implemented
- ✅ **Monitoring** - Prometheus & Grafana integration
- ✅ **Documentation** - Comprehensive guides and instructions

## 🎯 Roadmap

Future enhancements planned:
- [ ] GraphQL API for revenue data
- [ ] Advanced analytics dashboard
- [ ] Multi-currency support
- [ ] Automated tax calculations
- [ ] Mobile app integration
- [ ] Advanced fraud detection

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/Garrettc123/revenue-agent-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Garrettc123/revenue-agent-system/discussions)
- **Documentation**: See `/docs` directory

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- Flask & Python community
- Stripe API
- Express.js
- Docker
- Open source contributors

---

**Made with ❤️ by the Revenue Agent System Team**

*Last Updated: February 15, 2026*
