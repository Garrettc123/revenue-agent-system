# GitHub Copilot Instructions for Revenue Agent System

## Repository Overview

This is a **Revenue Agent System** - a comprehensive revenue tracking and monitoring platform that manages multiple revenue streams including:

- SaaS subscriptions via Stripe
- Affiliate commissions and payouts
- Content monetization
- Services marketplace
- API usage billing

The system provides a real-time dashboard for monitoring revenue metrics, customer data, and financial health indicators.

## Technology Stack

### Backend
- **Python 3.11** with Flask 3.1.2
- **Gunicorn** for production WSGI server
- **Stripe API** for payment processing
- PostgreSQL and MongoDB for data storage (configured in docker-compose)

### Frontend/APIs
- **Express.js** routers for modular API endpoints
- **Node.js** for JavaScript-based services
- Vanilla JavaScript for dashboard UI (no framework)

### Infrastructure
- **Docker** for containerization
- **Docker Compose** for local development
- Render/Heroku for production deployment (via Procfile)

### Dependencies
Key Python packages:
- Flask 3.1.2
- stripe 14.1.0
- gunicorn 25.0.1
- requests 2.32.5
- See `requirements.txt` for complete list

## Project Structure

```
revenue-agent-system/
├── app.py                      # Main Flask application entry point
├── requirements.txt            # Python dependencies
├── Procfile                    # Production deployment config (gunicorn)
├── Dockerfile                  # Container build instructions
├── docker-compose.yml          # Multi-service orchestration
│
├── revenue-dashboard.js        # Master dashboard Express router
├── stripe-integration.js       # Stripe payment integration
├── affiliate-system.js         # Affiliate tracking & payouts
├── content-monetization.js     # Content revenue tracking
├── services-marketplace.js     # Service sales tracking
│
├── DEPLOYMENT.md               # Comprehensive deployment guide
├── SECURITY.md                 # Security policies
└── render.yaml                 # Render.com deployment config
```

## Build, Test, and Run Commands

### Local Development

```bash
# Python Flask app (development)
python app.py

# Production-like local run
gunicorn app:app --bind 0.0.0.0:8000 --workers 2 --timeout 120

# Docker build and run
docker build -t revenue-agent .
docker run -p 8000:8000 revenue-agent

# Docker Compose (full stack)
docker-compose up --build
```

### Testing

⚠️ **Note**: This repository currently has no automated tests. When adding tests:
- Use `pytest` for Python tests
- Follow the pattern: `tests/test_*.py` for test files
- Run with: `pytest` or `pytest -v` for verbose output

### Deployment

```bash
# Render.com (uses render.yaml)
git push origin main

# Manual production deployment
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

## Code Style and Conventions

### Python (Flask)

1. **Import Organization**
   ```python
   from flask import Flask, render_template_string, jsonify
   import os
   from datetime import datetime
   ```

2. **API Endpoints**
   - Use `@app.route()` decorator
   - Return JSON with `jsonify()`
   - Use ISO 8601 timestamps: `datetime.utcnow().isoformat()`
   
   ```python
   @app.route('/api/revenue')
   def get_revenue():
       return jsonify({
           'status': 'success',
           'timestamp': datetime.utcnow().isoformat(),
           'data': {...}
       })
   ```

3. **Configuration**
   - Use environment variables via `os.getenv()`
   - Define constants at top of file in UPPER_CASE
   - Provide sensible defaults for development

4. **Error Handling**
   - Provide graceful fallbacks with mock data when external services fail
   - Log errors appropriately
   - Return proper HTTP status codes

### JavaScript (Express Routers)

1. **File Structure**
   ```javascript
   /**
    * Module Name - Brief Description
    * Detailed purpose of this module
    */
   
   const express = require('express');
   const router = express.Router();
   
   // Route handlers
   router.get('/endpoint', (req, res) => {
       // Implementation
   });
   
   module.exports = router;
   ```

2. **Naming Conventions**
   - Use camelCase for variables and functions
   - Use descriptive names: `monthlyRecurring`, `totalRevenue`
   - Router files use kebab-case: `stripe-integration.js`

3. **Response Format**
   ```javascript
   res.json({
       status: 'operational',
       timestamp: new Date().toISOString(),
       data: {...}
   });
   ```

4. **Comments**
   - Use JSDoc-style block comments for module headers
   - Add inline comments for complex business logic
   - Explain revenue calculation formulas

### HTML/CSS (Inline Templates)

- Embedded HTML uses inline `<style>` tags
- Dark theme by default: background `#1a1a2e`, text `#00ff41`
- Monospace font for dashboard aesthetics
- Use emoji in headers: 💰, 📊, 🎯, etc.

## Security Best Practices

### Critical Security Rules

1. **Never commit secrets or API keys** to the repository
   - Use environment variables for all sensitive data
   - Never hardcode: `STRIPE_SECRET_KEY`, `DATABASE_URL`, etc.

2. **Stripe Webhook Verification**
   ```python
   # ALWAYS verify webhook signatures
   stripe.Webhook.construct_event(
       payload, sig_header, webhook_secret
   )
   ```

3. **Input Validation**
   - Validate all user inputs
   - Sanitize data before database operations
   - Use parameterized queries for SQL

4. **HTTPS Only**
   - Production must use HTTPS
   - Webhook endpoints require HTTPS

5. **Environment Variables**
   - Store in `.env` file (never commit)
   - Load via `os.getenv()` in Python
   - Reference in `docker-compose.yml` as `${VAR_NAME}`

### Secrets to Never Commit

- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `DATABASE_URL` / `POSTGRES_PASSWORD`
- `MONGODB_URI` / `MONGODB_PASSWORD`
- `OPENAI_API_KEY`
- `SLACK_WEBHOOK`
- Any API keys or credentials

## Stripe Integration Patterns

### Fetching Resources
```python
# ALWAYS use auto_paging_iter() to avoid pagination limits
for subscription in stripe.Subscription.list(
    limit=100
).auto_paging_iter():
    # Process subscription
```

### Embedded Data Access
```python
# Use embedded price data to avoid N+1 queries
price = subscription_item['price']
amount = price['unit_amount']
# Instead of: stripe.Price.retrieve(price_id)
```

### Webhook Handling
```python
@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    # MUST verify signature first
    event = stripe.Webhook.construct_event(
        payload, sig_header, webhook_secret
    )
    
    # Then process event
    if event['type'] == 'payment_intent.succeeded':
        # Handle payment
```

## Revenue Calculation Patterns

### Constants and Configuration
```python
# Define revenue constants at top of file
MRR = 25000  # Monthly Recurring Revenue
ARR = MRR * 12  # Annual Recurring Revenue
CUSTOMERS = 150
```

### Wealth Calculations
```python
# Customer LTV formula
customer_ltv = (monthly_revenue / customers) * 36

# Emergency funds health score
score = (current_reserve / recommended_reserve) * 100
# Status thresholds: excellent ≥80%, good ≥60%, adequate ≥40%, low <40%
```

## Docker Configuration

### Dockerfile Best Practices
- Base image: `python:3.11-slim`
- Create non-root user: `app`
- Install system deps: `gcc`, `postgresql-client`
- Use multi-stage builds for optimization
- Health check with `curl`

### Docker Compose
- Define services: app, postgres, mongodb
- Use environment variables from `.env`
- Volume mounts for persistence
- Network isolation between services

## API Endpoint Patterns

### Standard Response Format
```python
{
    "status": "success" | "error",
    "timestamp": "2024-02-16T18:00:00.000Z",
    "data": {...},
    "message": "Optional message"
}
```

### Key Endpoints
- `/` - Dashboard HTML
- `/api/revenue` - Current revenue metrics
- `/api/masterwealth` - Total wealth calculation (ARR + liquid + emergency funds)
- `/api/wealth-index` - Comprehensive wealth index with projections
- `/api/emergency-funds` - Emergency fund health score

## Boundaries and Restrictions

### DO NOT Modify Without Explicit Permission

1. **Production configuration files** (unless fixing a security issue)
   - `Procfile`
   - `render.yaml`
   - `docker-compose.yml` (production values)

2. **Security-critical code**
   - Webhook signature verification
   - Authentication/authorization logic
   - Stripe API integration (unless fixing bugs)

3. **Existing working endpoints** (unless fixing bugs or security issues)
   - Don't break existing API contracts
   - Maintain backward compatibility

4. **External dependencies** (unless necessary)
   - Don't add new packages without good reason
   - Don't update major versions without testing

### Safe to Modify

1. **Documentation files**
   - README.md
   - DEPLOYMENT.md
   - SECURITY.md
   - This instructions file

2. **UI/UX improvements**
   - Dashboard styling
   - Visual indicators
   - Error messages

3. **New features** (with tests)
   - New API endpoints
   - Additional revenue streams
   - Enhanced calculations

## Working with This Repository

### Adding New Features

1. **Understand existing patterns** - Review similar code first
2. **Follow conventions** - Match the established style
3. **Test locally** - Use Docker Compose for full stack testing
4. **Update documentation** - Keep DEPLOYMENT.md current
5. **Security first** - Follow security best practices
6. **Mock data acceptable** - For development, mock data is fine

### Debugging Tips

1. **Check logs**
   ```bash
   docker-compose logs -f revenue-app
   ```

2. **Test endpoints**
   ```bash
   curl http://localhost:8000/api/revenue
   ```

3. **Validate environment**
   ```bash
   docker-compose config
   ```

### Common Tasks

**Add a new API endpoint:**
1. Define route in `app.py` or appropriate `.js` router
2. Follow existing response format
3. Update documentation
4. Test locally

**Update revenue calculations:**
1. Locate constants at top of `app.py`
2. Modify calculation logic
3. Verify all dependent endpoints
4. Test with mock data

**Deploy changes:**
1. Commit to main branch
2. Push to GitHub
3. Render/Heroku auto-deploys
4. Verify in production

## Additional Context

### Development Philosophy
- **Graceful degradation** - System works with mock data if external services unavailable
- **Real-time updates** - Dashboard refreshes every 5 seconds
- **Multi-stream revenue** - Track all revenue sources in one place
- **Financial health monitoring** - Beyond revenue, track LTV, emergency funds, wealth index

### Monitoring and Observability
- Health checks via curl in Docker
- ISO 8601 timestamps on all responses
- Status indicators on dashboard
- Real-time metric updates via polling

## Getting Help

### Resources
- **Deployment Guide**: See `DEPLOYMENT.md` for full setup instructions
- **Security Policy**: See `SECURITY.md` for security guidelines
- **Stripe Docs**: https://stripe.com/docs/api
- **Flask Docs**: https://flask.palletsprojects.com/

### When Stuck
1. Check existing code for patterns
2. Review documentation files
3. Test with Docker Compose locally
4. Verify environment variables are set correctly
5. Check Stripe dashboard for payment issues

---

**Remember**: This is a revenue-critical system. Always prioritize security, data integrity, and backward compatibility when making changes.
