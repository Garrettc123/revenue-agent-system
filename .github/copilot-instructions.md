# Revenue Agent System - Copilot Instructions

## Project Overview

The Revenue Agent System is a comprehensive multi-stream revenue management platform that integrates various monetization strategies into a unified system. The project handles:

- **Subscription Management**: Stripe-based SaaS subscriptions with tiered pricing
- **Affiliate/Referral Programs**: Commission tracking and automated payouts
- **Content Monetization**: Creator revenue streams and content licensing
- **Services Marketplace**: B2B service offerings and API billing
- **Revenue Analytics**: Real-time dashboard with metrics tracking

## Technology Stack

### Backend
- **Python 3.11+** with Flask 3.x for web application
- **gunicorn** for production WSGI server (2 workers, 120s timeout)
- **PostgreSQL** for relational data storage
- **MongoDB** for document storage
- **Redis** for caching and session management

### Frontend/API
- **Node.js** with Express.js for API routes and integrations
- **JavaScript** (ES6+) for revenue modules
- **HTML templates** embedded in Flask via `render_template_string`

### Payment & Integration
- **Stripe** for payment processing and subscriptions
- **Webhooks** for real-time event handling

### Deployment & Infrastructure
- **Docker** and **docker-compose** for containerization
- **Render.com** or **Railway** for production hosting
- **Prometheus** and **Grafana** for monitoring

## Coding Standards & Conventions

### Python (Flask Application)

#### General Guidelines
- Use **Python 3.11+** features and type hints where appropriate
- Follow **PEP 8** style guidelines for Python code
- Keep functions focused and single-purpose
- Use environment variables for configuration (via `os.environ.get()`)

#### Flask Patterns
- Use `jsonify()` for JSON responses
- Include error handling for all API endpoints
- Use ISO 8601 format for timestamps (`datetime.utcnow().isoformat()`)
- Always specify host as `0.0.0.0` for Docker compatibility

#### Example Pattern
```python
@app.route('/api/endpoint')
def api_endpoint():
    return jsonify({
        "key": "value",
        "timestamp": datetime.utcnow().isoformat()
    })
```

### JavaScript (Node.js/Express)

#### General Guidelines
- Use **ES6+** features (const/let, arrow functions, async/await)
- Use **const** for immutable values, **let** for mutable ones
- Include JSDoc-style comments for modules and complex functions
- Use meaningful variable names (camelCase)

#### Module Structure
- Start each file with a descriptive block comment
- Use Express Router for modular route handling
- Export routers using `module.exports`
- Group related endpoints logically

#### Example Pattern
```javascript
/**
 * Module Name - Description
 * Purpose and functionality
 */

const express = require('express');
const router = express.Router();

// Route definitions
router.get('/endpoint', (req, res) => {
  res.json({ status: 'success' });
});

module.exports = router;
```

### Environment Variables

Always use environment variables for:
- API keys and secrets (Stripe, OpenAI, etc.)
- Database connection strings
- Webhook URLs
- Port configuration
- Feature flags

Reference them securely:
```python
# Python
stripe_key = os.environ.get('STRIPE_SECRET_KEY')

# JavaScript
const stripeKey = process.env.STRIPE_SECRET_KEY;
```

## Project Structure

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
├── DEPLOYMENT.md               # Complete deployment guide
└── SECURITY.md                 # Security policy
```

## Build, Test & Deployment

### Local Development

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run Flask application
python app.py

# Application runs on http://localhost:5000
```

### Docker Development

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f revenue-app

# Rebuild after code changes
docker-compose up -d --build revenue-app
```

### Testing

```bash
# Run tests (if test suite exists)
pytest

# Run in Docker
docker-compose exec revenue-app python -m pytest
```

### Production Deployment

The application is configured for deployment on:
- **Render.com**: Uses `render.yaml` and `Procfile`
- **Railway**: Automatic deployment via CLI
- **Docker**: Production-ready multi-stage Dockerfile

Production server: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

## Security Guidelines

### Critical Security Practices

1. **Never commit secrets**: Use environment variables for all sensitive data
2. **Input validation**: Validate and sanitize all user inputs
3. **Webhook verification**: Always verify Stripe webhook signatures
4. **HTTPS only**: Use TLS/SSL in production
5. **Rate limiting**: Implement rate limiting for API endpoints
6. **SQL injection prevention**: Use parameterized queries
7. **CORS configuration**: Restrict CORS to known origins

### Secret Management

- Store secrets in environment variables or secret managers
- Use `.env` files for local development (never commit)
- Rotate API keys and secrets regularly
- Enable GitHub secret scanning

### Stripe Security

```javascript
// Always verify webhook signatures
const signature = req.headers['stripe-signature'];
const event = stripe.webhooks.constructEvent(
  req.body, 
  signature, 
  process.env.STRIPE_WEBHOOK_SECRET
);
```

## Common Tasks & Patterns

### Adding a New API Endpoint (Flask)

```python
@app.route('/api/new-endpoint')
def new_endpoint():
    try:
        # Implementation
        result = process_request()
        return jsonify({
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Adding Revenue Module (JavaScript)

```javascript
/**
 * New Revenue Module - Description
 */

const express = require('express');
const router = express.Router();

// Configuration
const MODULE_CONFIG = {
  // settings
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

### Database Connections

```python
# PostgreSQL connection
DATABASE_URL = os.environ.get('DATABASE_URL')

# MongoDB connection
MONGODB_URI = os.environ.get('MONGODB_URI')
```

## Error Handling

### Python/Flask
- Use try/except blocks for error-prone operations
- Return appropriate HTTP status codes
- Include error messages in JSON responses

### JavaScript/Express
- Use async/await with try/catch
- Use Express error handling middleware
- Log errors appropriately

## Monitoring & Observability

### Health Checks
- Flask app exposes `/health` endpoint
- Docker health check configured in Dockerfile
- Returns JSON with status and service name

### Metrics
- Prometheus metrics endpoint at `/metrics` (when configured)
- Grafana dashboards for visualization
- Monitor MRR, ARR, customer count, API usage

## Dependencies Management

### Python
- Add new dependencies to `requirements.txt`
- Pin versions for production stability
- Use virtual environments for development

### Node.js
- Dependencies managed in individual modules
- Use npm for package management
- Lock versions for critical packages

## Documentation

### Code Comments
- Use docstrings for Python functions
- Use JSDoc-style comments for JavaScript
- Document complex business logic
- Explain "why" not just "what"

### API Documentation
- Document all endpoints with:
  - Method (GET, POST, etc.)
  - Parameters and request body
  - Response format
  - Error codes

## Contributing Guidelines

When making changes:
1. Follow existing code patterns and conventions
2. Test locally with Docker before committing
3. Update documentation if adding features
4. Ensure security best practices are followed
5. Verify environment variables are documented
6. Test payment flows with Stripe test mode

## Revenue Stream Guidelines

### Stripe Integration
- Use test mode keys for development (`sk_test_...`)
- Always handle webhook failures gracefully
- Implement idempotency for payment operations
- Store customer IDs and subscription IDs securely

### Affiliate System
- Track referral sources accurately
- Implement commission calculations server-side
- Provide clear payout schedules
- Validate affiliate links before creating

### Content Monetization
- Respect content licensing terms
- Implement usage tracking
- Handle creator payouts reliably
- Support multiple payment methods

## Performance Considerations

- Use Redis for caching frequently accessed data
- Implement connection pooling for databases
- Optimize database queries
- Use async operations where appropriate
- Monitor response times and optimize slow endpoints

## Troubleshooting Common Issues

### Port Conflicts
- Default Flask port: 5000
- Production port: from `$PORT` environment variable
- Check `docker-compose.yml` for service ports

### Database Connection
- Verify `DATABASE_URL` environment variable
- Check database service is running in Docker
- Ensure network connectivity between services

### Stripe Webhooks
- Use ngrok or localtunnel for local testing
- Verify webhook secret is correct
- Check webhook signature validation

## Additional Resources

- **Deployment Guide**: See `DEPLOYMENT.md` for complete deployment instructions
- **Security Policy**: See `SECURITY.md` for security guidelines
- **Docker Compose**: See `docker-compose.yml` for service configuration
- **Stripe API**: https://stripe.com/docs/api
- **Flask Documentation**: https://flask.palletsprojects.com/

## Questions or Issues?

- Review existing code patterns in the repository
- Check `DEPLOYMENT.md` for infrastructure setup
- Refer to official documentation for frameworks used
- Test changes thoroughly in Docker environment before deployment
