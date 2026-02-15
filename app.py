from flask import Flask, render_template_string, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# Revenue configuration constants
MRR = 5000
CUSTOMERS = 12
ARR = 60000

# Wealth calculation constants
LIQUID_FUNDS_MONTHS = 3  # Months of MRR kept as liquid funds
EMERGENCY_RESERVE_MONTHS = 6  # Recommended emergency reserve in months
IMMEDIATELY_ACCESSIBLE_MONTHS = 2  # Immediately accessible emergency funds in months
CURRENT_RESERVE_MONTHS = 4  # Current emergency fund balance in months

# Health score calculation
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
        "mrr": MRR,
        "customers": CUSTOMERS,
        "arr": ARR,
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/masterwealth')
def masterwealth_api():
    """Calculate total wealth across all revenue streams"""
    # Calculate wealth components
    liquid_funds = MRR * LIQUID_FUNDS_MONTHS
    emergency_reserve = MRR * EMERGENCY_RESERVE_MONTHS
    total_wealth = ARR + liquid_funds + emergency_reserve
    
    # Revenue projections (monthly intervals)
    projection_30d = MRR * 1  # 1 month
    projection_60d = MRR * 2  # 2 months
    projection_90d = MRR * 3  # 3 months
    
    return jsonify({
        "total_wealth": total_wealth,
        "liquid_funds": liquid_funds,
        "emergency_reserve": emergency_reserve,
        "arr": ARR,
        "mrr": MRR,
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
    # Calculate emergency fund metrics
    immediately_accessible = MRR * IMMEDIATELY_ACCESSIBLE_MONTHS
    emergency_reserve = MRR * EMERGENCY_RESERVE_MONTHS
    current_reserve = MRR * CURRENT_RESERVE_MONTHS
    
    # Calculate health score (0-100 based on current vs recommended reserve)
    health_score = min(HEALTH_SCORE_MAX, int((current_reserve / emergency_reserve) * HEALTH_SCORE_MAX))
    
    # Determine status based on health score thresholds
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
