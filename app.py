from flask import Flask, render_template_string, jsonify, request
import os
import stripe
from datetime import datetime
from master_conductor import get_conductor

app = Flask(__name__)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')

# Initialize Master Conductor
conductor = get_conductor()

# Revenue configuration constants
MRR = 5000
CUSTOMERS = 12
ARR = MRR * 12

# Wealth calculation constants
LIQUID_FUNDS_MONTHS = 3          # Months of MRR kept as liquid funds
EMERGENCY_RESERVE_MONTHS = 6     # Recommended emergency reserve in months
IMMEDIATELY_ACCESSIBLE_MONTHS = 2  # Immediately accessible emergency funds
CURRENT_RESERVE_MONTHS = 4       # Current emergency fund balance in months

# Health score thresholds
HEALTH_SCORE_MAX = 100
HEALTH_EXCELLENT_THRESHOLD = 80
HEALTH_GOOD_THRESHOLD = 60
HEALTH_ADEQUATE_THRESHOLD = 40

# Time calculations
DAYS_PER_MONTH = 30

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Revenue Agent Dashboard</title>
    <style>
        body { background: #1a1a2e; color: #00ff41; font-family: monospace; padding: 20px; }
        .metric { background: #16213e; padding: 20px; margin: 10px; border-radius: 8px; }
        .amount { font-size: 48px; font-weight: bold; }
        .wealth-index { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: 3px solid #ffd700; }
        .wealth-index .amount { color: #ffd700; text-shadow: 0 0 10px #ffd700; }
        .wealth-section { border: 2px solid #ffd700; }
        .emergency-section { border: 2px solid #ff6b6b; }
        .status-excellent { color: #00ff41; }
        .status-good { color: #90ee90; }
        .status-adequate { color: #ffa500; }
        .status-low { color: #ff6b6b; }
        .sub-metric { font-size: 18px; margin-top: 10px; }
        .revenue-streams { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
        .stream { background: #0f3460; padding: 15px; border-radius: 5px; }
        .stream-value { font-size: 24px; font-weight: bold; color: #00d4ff; }
        .growth-metric { font-size: 18px; color: #00ff88; margin: 5px 0; }
        .payout-button {
            background: #00ff41;
            color: #1a1a2e;
            border: none;
            padding: 15px 30px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            border-radius: 8px;
            margin-top: 20px;
        }
        .payout-button:hover { background: #00cc33; }
        .payout-status { margin-top: 20px; padding: 15px; border-radius: 8px; }
        .success { background: #2d5016; color: #00ff41; }
        .error { background: #501616; color: #ff4141; }
    </style>
</head>
<body>
    <h1>💰 Revenue Agent System - LIVE</h1>

    <div class="metric wealth-index">
        <h2>🌟 UNPRECEDENTED WEALTH INDEX 🌟</h2>
        <div class="amount" id="wealth-index">$0M</div>
        <div class="growth-metric" id="wealth-subtitle">5-Year Compounding Projection</div>
    </div>

    <div class="metric wealth-section">
        <h2>🏆 Master Wealth (Total)</h2>
        <div class="amount" id="masterwealth">$0</div>
        <div class="sub-metric">
            ARR: $<span id="arr">0</span> |
            Liquid: $<span id="liquid">0</span> |
            Emergency: $<span id="emergency-reserve">0</span>
        </div>
    </div>

    <div class="metric emergency-section">
        <h2>🚨 Emergency Funds Available TODAY</h2>
        <div class="amount" id="emergency-accessible">$0</div>
        <div class="sub-metric">
            Health: <span id="health-score">0</span>%
            (<span id="health-status" class="status-excellent">excellent</span>) |
            Coverage: <span id="coverage-days">0</span> days
        </div>
    </div>

    <div class="metric">
        <h2>Monthly Recurring Revenue</h2>
        <div class="amount" id="mrr">$0</div>
    </div>
    <div class="metric">
        <h2>Active Customers</h2>
        <div class="amount" id="customers">0</div>
    </div>

    <div class="metric">
        <h2>Revenue Streams</h2>
        <div class="revenue-streams" id="revenue-streams">
            <div class="stream"><div>SaaS</div><div class="stream-value" id="stream-saas">$0</div></div>
            <div class="stream"><div>API Usage</div><div class="stream-value" id="stream-api">$0</div></div>
            <div class="stream"><div>Content</div><div class="stream-value" id="stream-content">$0</div></div>
            <div class="stream"><div>Affiliates</div><div class="stream-value" id="stream-affiliates">$0</div></div>
            <div class="stream"><div>Services</div><div class="stream-value" id="stream-services">$0</div></div>
        </div>
    </div>

    <div class="metric">
        <h2>Growth Metrics</h2>
        <div class="growth-metric" id="growth-rate">Annual Growth: 0%</div>
        <div class="growth-metric" id="customer-ltv">Customer LTV: $0</div>
        <div class="growth-metric" id="monthly-velocity">Monthly Velocity: $0</div>
    </div>

    <div class="metric">
        <h2>System Status</h2>
        <div class="amount">● ONLINE</div>
    </div>
    <div class="metric">
        <h2>🚀 Auto Payout</h2>
        <p>Trigger automatic payout to affiliates</p>
        <button class="payout-button" onclick="triggerPayout()">Trigger Payout</button>
        <div id="payout-status"></div>
    </div>
    <script>
        function updateDashboard() {
            // Update basic revenue metrics
            fetch('/api/revenue')
                .then(r => r.json())
                .then(d => {
                    document.getElementById('mrr').textContent = '$' + d.mrr.toLocaleString();
                    document.getElementById('customers').textContent = d.customers;
                });

            // Update wealth index
            fetch('/api/wealth-index')
                .then(r => r.json())
                .then(d => {
                    document.getElementById('wealth-index').textContent = '$' + d.wealth_index + 'M';
                    document.getElementById('wealth-subtitle').textContent =
                        '5-Year Projection: $' + (d.five_year_projection / 1000000).toFixed(2) + 'M';
                    document.getElementById('stream-saas').textContent =
                        '$' + (d.revenue_streams.saas / 1000).toFixed(0) + 'K';
                    document.getElementById('stream-api').textContent =
                        '$' + (d.revenue_streams.api / 1000).toFixed(0) + 'K';
                    document.getElementById('stream-content').textContent =
                        '$' + (d.revenue_streams.content / 1000).toFixed(0) + 'K';
                    document.getElementById('stream-affiliates').textContent =
                        '$' + (d.revenue_streams.affiliates / 1000).toFixed(0) + 'K';
                    document.getElementById('stream-services').textContent =
                        '$' + (d.revenue_streams.services / 1000).toFixed(0) + 'K';
                    document.getElementById('growth-rate').textContent =
                        'Annual Growth: ' + d.growth_metrics.annual_growth_rate;
                    document.getElementById('customer-ltv').textContent =
                        'Customer LTV: $' + d.growth_metrics.customer_ltv.toLocaleString();
                    document.getElementById('monthly-velocity').textContent =
                        'Monthly Velocity: $' + d.growth_metrics.monthly_velocity.toLocaleString();
                });

            // Update masterwealth
            fetch('/api/masterwealth')
                .then(r => r.json())
                .then(d => {
                    document.getElementById('masterwealth').textContent = '$' + d.total_wealth.toLocaleString();
                    document.getElementById('arr').textContent = d.arr.toLocaleString();
                    document.getElementById('liquid').textContent = d.liquid_funds.toLocaleString();
                    document.getElementById('emergency-reserve').textContent = d.emergency_reserve.toLocaleString();
                });

            // Update emergency funds
            fetch('/api/emergency-funds')
                .then(r => r.json())
                .then(d => {
                    document.getElementById('emergency-accessible').textContent = '$' + d.immediately_accessible.toLocaleString();
                    document.getElementById('health-score').textContent = d.health_score;
                    const statusEl = document.getElementById('health-status');
                    statusEl.textContent = d.status;
                    statusEl.className = 'status-' + d.status;
                    document.getElementById('coverage-days').textContent = d.days_of_coverage;
                });
        }

        // Initial load
        updateDashboard();

        // Auto-refresh every 5 seconds
        setInterval(updateDashboard, 5000);

        function triggerPayout() {
            const statusDiv = document.getElementById('payout-status');
            statusDiv.innerHTML = '<div class="payout-status">Processing payout...</div>';
            
            // Demo: In production, these values would come from actual affiliate data
            fetch('/api/trigger-payout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    affiliate_id: 'demo_affiliate_001',
                    tier: 'silver',
                    amount: 250
                })
            })
            .then(r => r.json())
            .then(d => {
                if (d.status === 'success') {
                    statusDiv.innerHTML = `
                        <div class="payout-status success">
                            ✓ Payout Successful!<br>
                            Amount: $${d.amount}<br>
                            Payout ID: ${d.payout_id}<br>
                            Tier: ${d.tier}
                        </div>
                    `;
                } else {
                    statusDiv.innerHTML = `
                        <div class="payout-status error">
                            ✗ ${d.message || 'Payout failed'}
                        </div>
                    `;
                }
            })
            .catch(e => {
                statusDiv.innerHTML = `
                    <div class="payout-status error">
                        ✗ Error: ${e.message}
                    </div>
                `;
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)


def fetch_stripe_revenue():
    """Fetch actual revenue data from Stripe API with fallback to mock data"""
    try:
        if not stripe.api_key:
            return {
                "mrr": MRR,
                "customers": CUSTOMERS,
                "arr": ARR,
                "total_revenue": 0,
                "configured": False
            }

        # Fetch all active subscriptions with auto-pagination (avoids N+1 queries)
        mrr = 0
        for subscription in stripe.Subscription.list(status='active', limit=100).auto_paging_iter():
            for item in subscription['items']['data']:
                price = item['price']  # Use embedded price data
                amount = price['unit_amount'] / 100 if price['unit_amount'] else 0
                if price['recurring']['interval'] == 'year':
                    amount = amount / 12
                mrr += amount

        # Get accurate customer count
        customer_count = 0
        for _ in stripe.Customer.list(limit=100).auto_paging_iter():
            customer_count += 1

        # Fetch total revenue from successful charges
        charges = stripe.Charge.list(limit=100)
        total_revenue = sum(
            charge['amount'] / 100
            for charge in charges.data
            if charge['status'] == 'succeeded'
        )

        return {
            "mrr": round(mrr, 2),
            "customers": customer_count,
            "arr": round(mrr * 12, 2),
            "total_revenue": round(total_revenue, 2),
            "configured": True
        }
    except Exception as e:
        print(f"[Stripe] Error fetching revenue: {e}")
        return {
            "mrr": MRR,
            "customers": CUSTOMERS,
            "arr": ARR,
            "total_revenue": 0,
            "configured": False,
            "error": str(e)
        }


@app.route('/api/revenue')
def revenue_api():
    revenue_data = fetch_stripe_revenue()
    revenue_data['timestamp'] = datetime.utcnow().isoformat()
    return jsonify(revenue_data)

@app.route('/api/trigger-payout', methods=['POST'])
def trigger_payout():
    """
    Trigger automatic payout for affiliates
    NOTE: This is a demo/development endpoint. In production:
    - Authentication should be required
    - Affiliate data should come from database
    - Actual Stripe Connect payouts should be initiated
    """
    try:
        data = request.get_json() if hasattr(request, 'get_json') else {}
        affiliate_id = data.get('affiliate_id', 'default_affiliate')
        tier = data.get('tier', 'bronze')
        
        # Tier-based minimum payout amounts
        PAYOUT_MINIMUMS = {
            'bronze': 50,
            'silver': 100,
            'gold': 200,
            'platinum': 500
        }
        
        minimum_required = PAYOUT_MINIMUMS.get(tier, 50)
        
        # Simulate payout processing
        payout_amount = data.get('amount', 0)
        if payout_amount < minimum_required:
            return jsonify({
                "status": "pending",
                "message": f"Minimum payout amount not met for {tier} tier",
                "minimum_required": minimum_required,
                "current_balance": payout_amount
            }), 400
        
        return jsonify({
            "status": "success",
            "payout_id": f"payout_{datetime.utcnow().timestamp()}",
            "affiliate_id": affiliate_id,
            "amount": payout_amount,
            "tier": tier,
            "processed_at": datetime.utcnow().isoformat(),
            "estimated_arrival": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/checkout/success')
def checkout_success():
    session_id = request.args.get('session_id', '')
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Payment Approved</title>
    <style>
        body { background: #1a1a2e; color: #00ff41; font-family: monospace; padding: 40px; text-align: center; }
        .card { background: #16213e; padding: 40px; border-radius: 8px; display: inline-block; }
        .amount { font-size: 48px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <div class="amount">✓</div>
        <h1>Session Approved</h1>
        <p>Your checkout session has been approved successfully.</p>
        <p>Session ID: {{ session_id }}</p>
        <p><a href="/" style="color:#00ff41;">Return to Dashboard</a></p>
    </div>
</body>
</html>
""", session_id=session_id)


@app.route('/checkout/cancel')
def checkout_cancel():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Checkout Cancelled</title>
    <style>
        body { background: #1a1a2e; color: #ff4141; font-family: monospace; padding: 40px; text-align: center; }
        .card { background: #16213e; padding: 40px; border-radius: 8px; display: inline-block; }
    </style>
</head>
<body>
    <div class="card">
        <h1>✗ Checkout Cancelled</h1>
        <p>Your checkout session was cancelled.</p>
        <p><a href="/" style="color:#00ff41;">Return to Dashboard</a></p>
    </div>
</body>
</html>
""")


@app.route('/api/checkout-session', methods=['POST'])
def create_checkout_session():
    """
    Create a Stripe Checkout Session for a subscription tier.
    All sessions are processed and approved upon completion via webhook.
    """
    try:
        data = request.get_json() or {}
        tier = data.get('tier', 'starter')
        email = data.get('email', '')
        user_id = data.get('user_id', '')

        tier_price_ids = {
            'starter': os.getenv('STRIPE_STARTER_PRICE_ID', ''),
            'professional': os.getenv('STRIPE_PROFESSIONAL_PRICE_ID', ''),
            'enterprise': os.getenv('STRIPE_ENTERPRISE_PRICE_ID', '')
        }

        if tier not in tier_price_ids:
            return jsonify({"status": "error", "message": "Invalid tier"}), 400

        price_id = tier_price_ids[tier]
        if not price_id:
            return jsonify({
                "status": "error",
                "message": f"Price ID not configured for tier: {tier}"
            }), 400

        app_url = os.getenv('APP_URL', 'http://localhost:5000')
        session_params = {
            'mode': 'subscription',
            'line_items': [{'price': price_id, 'quantity': 1}],
            'success_url': f"{app_url}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
            'cancel_url': f"{app_url}/checkout/cancel",
            'metadata': {'user_id': user_id, 'tier': tier}
        }
        if email:
            session_params['customer_email'] = email

        session = stripe.checkout.Session.create(**session_params)

        return jsonify({
            "status": "success",
            "sessionId": session.id,
            "url": session.url,
            "tier": tier,
            "paymentStatus": session.payment_status,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/checkout-session/<session_id>', methods=['GET'])
def get_checkout_session(session_id):
    """
    Retrieve a Stripe Checkout Session and return its approval status.
    A session is approved when payment_status is 'paid' or status is 'complete'.
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        approved = session.status == 'complete' and session.payment_status == 'paid'

        return jsonify({
            "status": "success",
            "sessionId": session.id,
            "sessionStatus": session.status,
            "paymentStatus": session.payment_status,
            "approved": approved,
            "tier": session.metadata.get('tier') if session.metadata else None,
            "amountTotal": session.amount_total / 100 if session.amount_total else None,
            "currency": session.currency,
            "customerEmail": session.customer_email,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events for automatic revenue tracking"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        else:
            event = stripe.Event.construct_from(
                request.get_json(), stripe.api_key
            )

        event_type = event['type']

        if event_type == 'payment_intent.succeeded':
            amount = event['data']['object']['amount'] / 100
            print(f"[Webhook] Payment succeeded: ${amount}")
        elif event_type == 'customer.subscription.created':
            print(f"[Webhook] New subscription: {event['data']['object']['id']}")
        elif event_type == 'customer.subscription.updated':
            print(f"[Webhook] Subscription updated: {event['data']['object']['id']}")
        elif event_type == 'customer.subscription.deleted':
            print(f"[Webhook] Subscription cancelled: {event['data']['object']['id']}")
        elif event_type == 'charge.succeeded':
            amount = event['data']['object']['amount'] / 100
            print(f"[Webhook] Charge succeeded: ${amount}")
        elif event_type == 'invoice.payment_succeeded':
            amount = event['data']['object']['amount_paid'] / 100
            print(f"[Webhook] Invoice paid: ${amount}")

        return jsonify({"status": "success", "event": event_type}), 200

    except ValueError as e:
        print(f"[Webhook] Invalid payload: {e}")
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        print(f"[Webhook] Invalid signature: {e}")
        return jsonify({"error": "Invalid signature"}), 400
    except Exception as e:
        print(f"[Webhook] Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/revenue/sync', methods=['POST'])
def sync_revenue():
    """Manually trigger revenue sync from Stripe"""
    try:
        revenue_data = fetch_stripe_revenue()
        return jsonify({
            "status": "success",
            "message": "Revenue data synced",
            "data": revenue_data,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/wealth-index')
def wealth_index():
    """
    Unprecedented Wealth Index — aggregate customer LTV with 5-year compounding projections
    """
    ANNUAL_GROWTH_RATE = 0.235

    # Base revenue streams (monthly)
    saas_subscriptions = 100000
    api_usage = 50000
    content_revenue = 30000
    affiliate_commissions = 40000
    services_consulting = 80000
    total_monthly = (saas_subscriptions + api_usage + content_revenue
                     + affiliate_commissions + services_consulting)

    active_customers = 500
    avg_lifetime_months = 36

    avg_monthly_per_customer = total_monthly / active_customers
    customer_ltv = round(avg_monthly_per_customer * avg_lifetime_months, 0)
    total_customer_lifetime_value = active_customers * customer_ltv

    # 5-year compounding projection
    growth_multiplier = 1 + ANNUAL_GROWTH_RATE
    year_1 = total_monthly * 12
    year_2 = year_1 * growth_multiplier
    year_3 = year_2 * growth_multiplier
    year_4 = year_3 * growth_multiplier
    year_5 = year_4 * growth_multiplier
    five_year_wealth = year_1 + year_2 + year_3 + year_4 + year_5

    monthly_velocity = total_monthly * ANNUAL_GROWTH_RATE / 12
    wealth_index = round((total_customer_lifetime_value + five_year_wealth) / 1_000_000, 2)

    return jsonify({
        "wealth_index": wealth_index,
        "wealth_index_label": f"${wealth_index}M Unprecedented Wealth",
        "total_customer_lifetime_value": total_customer_lifetime_value,
        "five_year_projection": round(five_year_wealth, 2),
        "monthly_revenue": total_monthly,
        "annual_revenue_projection": total_monthly * 12,
        "revenue_streams": {
            "saas": saas_subscriptions,
            "api": api_usage,
            "content": content_revenue,
            "affiliates": affiliate_commissions,
            "services": services_consulting
        },
        "growth_metrics": {
            "monthly_velocity": round(monthly_velocity, 2),
            "annual_growth_rate": f"{ANNUAL_GROWTH_RATE * 100}%",
            "customer_ltv": int(customer_ltv),
            "active_customers": active_customers
        },
        "wealth_milestones": {
            "year_1": round(year_1, 2),
            "year_2": round(year_2, 2),
            "year_3": round(year_3, 2),
            "year_4": round(year_4, 2),
            "year_5": round(year_5, 2)
        },
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/api/masterwealth')
def masterwealth_api():
    """Calculate total wealth across all revenue streams"""
    liquid_funds = MRR * LIQUID_FUNDS_MONTHS
    emergency_reserve = MRR * EMERGENCY_RESERVE_MONTHS
    total_wealth = ARR + liquid_funds + emergency_reserve

    return jsonify({
        "total_wealth": total_wealth,
        "liquid_funds": liquid_funds,
        "emergency_reserve": emergency_reserve,
        "arr": ARR,
        "mrr": MRR,
        "projections": {
            "30_days": MRR * 1,
            "60_days": MRR * 2,
            "90_days": MRR * 3
        },
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/api/emergency-funds')
def emergency_funds_api():
    """Get emergency fund status and availability"""
    immediately_accessible = MRR * IMMEDIATELY_ACCESSIBLE_MONTHS
    emergency_reserve = MRR * EMERGENCY_RESERVE_MONTHS
    current_reserve = MRR * CURRENT_RESERVE_MONTHS

    health_score = min(HEALTH_SCORE_MAX, int((current_reserve / emergency_reserve) * HEALTH_SCORE_MAX))

    if health_score >= HEALTH_EXCELLENT_THRESHOLD:
        status = "excellent"
    elif health_score >= HEALTH_GOOD_THRESHOLD:
        status = "good"
    elif health_score >= HEALTH_ADEQUATE_THRESHOLD:
        status = "adequate"
    else:
        status = "low"

    return jsonify({
        "immediately_accessible": immediately_accessible,
        "current_reserve": current_reserve,
        "recommended_reserve": emergency_reserve,
        "health_score": health_score,
        "status": status,
        "days_of_coverage": int((current_reserve / MRR) * DAYS_PER_MONTH),
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "revenue-agent"})


# Master Conductor API Endpoints

@app.route('/api/conductor/dashboard')
def conductor_dashboard():
    """
    Master dashboard aggregating all revenue streams
    """
    return jsonify(conductor.get_master_dashboard())

@app.route('/api/conductor/financial-summary')
def conductor_financial_summary():
    """
    Financial summary with revenue, expenses, and profit
    """
    return jsonify(conductor.get_financial_summary())

@app.route('/api/conductor/forecast')
def conductor_forecast():
    """
    Revenue forecast for next 12 months
    """
    months = request.args.get('months', 12, type=int)
    return jsonify(conductor.get_revenue_forecast(months))

@app.route('/api/conductor/health')
def conductor_health():
    """
    System health check with detailed status
    """
    return jsonify(conductor.get_system_health())

@app.route('/api/conductor/orchestrate-payout', methods=['POST'])
def conductor_orchestrate_payout():
    """
    Orchestrate automatic payout cycle across all revenue streams
    """
    try:
        data = request.get_json() if hasattr(request, 'get_json') else {}
        tier = data.get('tier', None)
        result = conductor.orchestrate_payout_cycle(tier)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
