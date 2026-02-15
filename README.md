# 💰 Revenue Agent System

An automated revenue tracking and management system with real-time Stripe integration.

## 🚀 Features

### Automatic Revenue Retrieval
The system automatically fetches real-time revenue data from your Stripe account:

- **Monthly Recurring Revenue (MRR)**: Calculated from all active subscriptions
- **Annual Recurring Revenue (ARR)**: Projected yearly revenue
- **Customer Count**: Total number of active customers
- **Total Revenue**: Sum of all successful charges

### Real-time Webhook Integration
Automatically captures and processes Stripe events:

- Payment success notifications
- Subscription lifecycle events (created, updated, cancelled)
- Invoice and charge events
- Secure webhook signature verification

### Live Dashboard
Real-time revenue dashboard that automatically refreshes every 5 seconds with the latest data.

## 📋 Quick Start

### Prerequisites
- Python 3.8+
- Stripe account with API keys

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export STRIPE_SECRET_KEY="sk_test_your_key_here"
export STRIPE_WEBHOOK_SECRET="whsec_your_webhook_secret"
export PORT=5000

# Run the application
python app.py
```

### Using Docker

```bash
# Build the image
docker build -t revenue-agent .

# Run with environment variables
docker run -p 5000:5000 \
  -e STRIPE_SECRET_KEY="sk_test_your_key" \
  -e STRIPE_WEBHOOK_SECRET="whsec_your_secret" \
  revenue-agent
```

## 🔌 API Endpoints

### GET `/api/revenue`
Fetch current revenue data from Stripe.

**Response:**
```json
{
  "mrr": 15000.00,
  "arr": 180000.00,
  "customers": 42,
  "total_revenue": 50000.00,
  "configured": true,
  "timestamp": "2026-02-15T20:00:00.000000"
}
```

### POST `/api/revenue/sync`
Manually trigger a revenue data sync from Stripe.

**Response:**
```json
{
  "status": "success",
  "message": "Revenue data synced",
  "data": { ... },
  "timestamp": "2026-02-15T20:00:00.000000"
}
```

### POST `/webhooks/stripe`
Stripe webhook endpoint for automatic event processing.

**Supported Events:**
- `payment_intent.succeeded`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `charge.succeeded`
- `invoice.payment_succeeded`

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "revenue-agent"
}
```

## 🔐 Security

### Webhook Signature Verification
All incoming webhooks are verified using Stripe's signature verification to ensure authenticity. Set the `STRIPE_WEBHOOK_SECRET` environment variable to enable this feature.

### Environment Variables
Never commit your Stripe API keys. Always use environment variables:

```bash
# Required for production
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Optional
PORT=5000
```

### Graceful Fallback
If Stripe is not configured or API calls fail, the system gracefully falls back to mock data, ensuring the dashboard remains operational.

## 🛠️ Configuration

### Setting Up Stripe Webhooks

1. Go to [Stripe Dashboard → Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Enter your webhook URL: `https://your-domain.com/webhooks/stripe`
4. Select events to listen to (or select "all events")
5. Copy the webhook signing secret
6. Set the `STRIPE_WEBHOOK_SECRET` environment variable

## 📊 Dashboard

Access the live dashboard at `http://localhost:5000/`

The dashboard displays:
- Real-time MRR updates
- Active customer count
- System status
- Auto-refreshes every 5 seconds

## 🧪 Testing

### Test Without Stripe Configuration
The system works without Stripe credentials by returning mock data:

```bash
# Run without Stripe keys
python app.py
```

### Test Webhook Endpoint

```bash
curl -X POST http://localhost:5000/webhooks/stripe \
  -H "Content-Type: application/json" \
  -d '{"type": "payment_intent.succeeded", "data": {"object": {"amount": 5000}}}'
```

## 🔄 How It Works

1. **Automatic Data Fetching**: When `/api/revenue` is called, the system queries Stripe's API to fetch:
   - All active subscriptions (with automatic pagination)
   - Customer count (with accurate pagination)
   - Recent charges for total revenue calculation

2. **MRR Calculation**: 
   - Fetches all active subscriptions
   - Uses embedded price data (no N+1 queries)
   - Normalizes yearly subscriptions to monthly amounts
   - Sums all monthly amounts

3. **Webhook Processing**: 
   - Receives events from Stripe in real-time
   - Verifies webhook signatures for security
   - Logs all revenue-related events
   - Can be extended to trigger custom actions

## 📈 Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 🔒 Security Policy

See [SECURITY.md](SECURITY.md) for our security policy and reporting vulnerabilities.

## 📝 License

This project is part of the Tree of Life revenue system.

## 🤝 Contributing

Contributions are welcome! Please ensure all security best practices are followed.

---

**Built with ❤️ for automated revenue tracking**
