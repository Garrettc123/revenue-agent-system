from flask import Flask, render_template_string, jsonify, request
import os
from datetime import datetime

app = Flask(__name__)

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
            
            fetch('/api/trigger-payout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    affiliate_id: 'user_001',
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
    """Trigger automatic payout for affiliates"""
    try:
        data = request.get_json() if hasattr(request, 'get_json') else {}
        affiliate_id = data.get('affiliate_id', 'default_affiliate')
        tier = data.get('tier', 'bronze')
        
        # Simulate payout processing
        payout_amount = data.get('amount', 0)
        if payout_amount < 50:
            return jsonify({
                "status": "pending",
                "message": "Minimum payout amount not met",
                "minimum_required": 50,
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

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "revenue-agent"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
