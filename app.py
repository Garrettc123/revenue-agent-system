from flask import Flask, render_template_string, jsonify
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
    <script>
        setInterval(() => {
            fetch('/api/revenue')
                .then(r => r.json())
                .then(d => {
                    document.getElementById('mrr').textContent = '$' + d.mrr.toLocaleString();
                    document.getElementById('customers').textContent = d.customers;
                });
        }, 5000);
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

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "revenue-agent"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
