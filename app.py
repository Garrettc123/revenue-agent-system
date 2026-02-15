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
        .wealth-section { border: 2px solid #ffd700; }
        .emergency-section { border: 2px solid #ff6b6b; }
        .status-excellent { color: #00ff41; }
        .status-good { color: #90ee90; }
        .status-adequate { color: #ffa500; }
        .status-low { color: #ff6b6b; }
        .sub-metric { font-size: 18px; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>💰 Revenue Agent System - LIVE</h1>
    
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
        <h2>System Status</h2>
        <div class="amount">● ONLINE</div>
    </div>
    <script>
        function updateDashboard() {
            // Update revenue metrics
            fetch('/api/revenue')
                .then(r => r.json())
                .then(d => {
                    document.getElementById('mrr').textContent = '$' + d.mrr.toLocaleString();
                    document.getElementById('customers').textContent = d.customers;
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
        
        // Initial update
        updateDashboard();
        
        // Update every 5 seconds
        setInterval(updateDashboard, 5000);
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

@app.route('/api/masterwealth')
def masterwealth_api():
    """Calculate total wealth across all revenue streams"""
    mrr = 5000
    customers = 12
    arr = 60000
    
    # Calculate wealth components
    liquid_funds = mrr * 3  # 3 months of MRR as liquid funds
    emergency_reserve = mrr * 6  # 6 months emergency fund
    total_wealth = arr + liquid_funds + emergency_reserve
    
    # Revenue projections
    projection_30d = mrr * 1
    projection_60d = mrr * 2
    projection_90d = mrr * 3
    
    return jsonify({
        "total_wealth": total_wealth,
        "liquid_funds": liquid_funds,
        "emergency_reserve": emergency_reserve,
        "arr": arr,
        "mrr": mrr,
        "projections": {
            "30_days": projection_30d,
            "60_days": projection_60d,
            "90_days": projection_90d
        },
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/emergency-funds')
def emergency_funds_api():
    """Get emergency fund status and availability"""
    mrr = 5000
    
    # Calculate emergency fund metrics
    immediately_accessible = mrr * 2  # 2 months worth immediately accessible
    emergency_reserve = mrr * 6  # 6 months recommended reserve
    current_reserve = mrr * 4  # Current emergency fund balance
    
    # Calculate health score (0-100)
    health_score = min(100, int((current_reserve / emergency_reserve) * 100))
    
    # Determine status
    if health_score >= 80:
        status = "excellent"
    elif health_score >= 60:
        status = "good"
    elif health_score >= 40:
        status = "adequate"
    else:
        status = "low"
    
    return jsonify({
        "immediately_accessible": immediately_accessible,
        "current_reserve": current_reserve,
        "recommended_reserve": emergency_reserve,
        "health_score": health_score,
        "status": status,
        "days_of_coverage": int((current_reserve / mrr) * 30),
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "revenue-agent"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
