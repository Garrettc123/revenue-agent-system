# Revenue Agent System 💰

A full-stack SaaS revenue agent system with multi-stream monetization capabilities. This system integrates subscription billing, affiliate programs, content monetization, and services marketplace into a unified dashboard.

## 🚀 Features

### Core Revenue Streams
- **Stripe Integration**: SaaS subscriptions with tiered pricing ($29-$499/month)
- **Affiliate System**: Multi-tier partner program with recurring commissions
- **Content Monetization**: Digital products, courses, and ad revenue
- **Services Marketplace**: Custom integrations and consulting services
- **Master Dashboard**: Real-time revenue analytics and forecasting

### Technical Stack
- **Backend**: Python Flask + Gunicorn
- **APIs**: RESTful endpoints with JSON responses
- **Deployment**: Render, Heroku-compatible (Procfile included)
- **Dependencies**: Stripe, LangChain, FastAPI, SQLAlchemy

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Node.js 14+ (for build scripts)
- Git

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Garrettc123/revenue-agent-system.git
cd revenue-agent-system
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

Or use the npm script:
```bash
npm run install:python
```

### 3. Set Environment Variables
Create a `.env` file in the root directory:
```bash
# Optional - defaults provided
PORT=5000

# For production Stripe integration (optional)
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_STARTER_PRICE_ID=price_xxx
STRIPE_PROFESSIONAL_PRICE_ID=price_xxx
STRIPE_ENTERPRISE_PRICE_ID=price_xxx
```

## 🏃 Running the Application

### Development Mode
```bash
npm run dev
# or
python app.py
```

The dashboard will be available at `http://localhost:5000`

### Production Mode
```bash
npm start
# or
gunicorn app:app --bind 0.0.0.0:5000 --workers 2 --timeout 120
```

## 🧪 Testing

Run the test suite:
```bash
npm test
# or
pytest tests/ -v
```

Run with coverage:
```bash
npm run test:python
```

## 📊 API Endpoints

### Health Check
```
GET /health
```
Returns server health status.

### Revenue API
```
GET /api/revenue
```
Returns current revenue metrics:
- Monthly Recurring Revenue (MRR)
- Active customers
- Annual Recurring Revenue (ARR)
- Timestamp

### Dashboard
```
GET /
```
Web dashboard with live revenue metrics (auto-refreshes every 5 seconds).

## 🚀 Deployment

### Render
This project is configured for Render deployment via `render.yaml`:
1. Connect your GitHub repository to Render
2. Render will automatically detect the configuration
3. Set environment variables in Render dashboard
4. Deploy!

### Heroku
Using the included `Procfile`:
```bash
heroku create your-app-name
git push heroku main
```

### Manual Deployment
1. Ensure all dependencies are installed
2. Set environment variables
3. Run with gunicorn: `gunicorn app:app --bind 0.0.0.0:$PORT`

## 📁 Project Structure

```
revenue-agent-system/
├── app.py                      # Main Flask application
├── stripe-integration.js       # Stripe subscription logic
├── affiliate-system.js         # Affiliate program management
├── content-monetization.js     # Content revenue tracking
├── services-marketplace.js     # Services and consulting
├── revenue-dashboard.js        # Master dashboard aggregation
├── requirements.txt            # Python dependencies
├── package.json               # Build scripts and metadata
├── Procfile                   # Heroku deployment config
├── render.yaml                # Render deployment config
├── .gitignore                 # Git ignore patterns
└── tests/                     # Test suite
    └── test_app.py            # Application tests
```

## 🔐 Security Notes

- Never commit `.env` files with real API keys
- Use environment variables for all sensitive configuration
- The current implementation uses mock data for demonstration
- Implement proper authentication before production use

## 🛠️ Build Commands

```bash
# Install dependencies
npm run install:python

# Run tests
npm test

# Start development server
npm run dev

# Start production server
npm start

# Full build (install + test)
npm run build

# Check deployment configuration
npm run deploy:check

# Health check (requires running server)
npm run health-check
```

## 📈 Revenue Metrics

The system currently displays:
- **MRR (Monthly Recurring Revenue)**: $5,000
- **Active Customers**: 12
- **ARR (Annual Recurring Revenue)**: $60,000

These are demo values. In production, connect to your payment processor and database.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - See LICENSE file for details

## 📧 Support

For support, please open an issue in the GitHub repository.

---

**Built with ❤️ for revenue optimization**
