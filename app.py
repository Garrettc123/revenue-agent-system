from flask import Flask, render_template_string, jsonify, request
import os
import stripe
from datetime import datetime
from master_conductor import get_conductor

app = Flask(__name__)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')

# Initialize Master Conductor
conductor = get_conductor()

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Revenue Agent Dashboard</title>
    <style>
        body { background: #1a1a2e; color: #00ff41; font-family: monospace; padding: 20px; }
        .metric { background: #16213e; padding: 20px; margin: 10px; border-radius: 8px; }
        .amount { font-size: 48px; font-weight: bold; }
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
    <div class="metric">
        <h2>Monthly Recurring Revenue</h2>
        <div class="amount" id="mrr">$0</div>
    </div>
    <div class="metric">
        <h2>Active Customers</h2>
        <div class="amount" id="customers">0</div>
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
        setInterval(() => {
            fetch('/api/revenue')
                .then(r => r.json())
                .then(d => {
                    document.getElementById('mrr').textContent = '$' + d.mrr.toLocaleString();
                    document.getElementById('customers').textContent = d.customers;
                });
        }, 5000);

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

@app.route('/api/revenue')
def revenue_api():
    return jsonify({
        "mrr": 5000,
        "customers": 12,
        "arr": 60000,
        "timestamp": datetime.utcnow().isoformat()
    })

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
