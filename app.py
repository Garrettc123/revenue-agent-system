"""Revenue Agent System application."""
import os
import queue
import threading
from datetime import datetime
from typing import Any
from flask import Flask, Response, jsonify, render_template_string, request, stream_with_context
try:
    import stripe
except ImportError:
    stripe = None
try:
    from cache_utils import cached, invalidate_revenue_cache, TTL_STRIPE_REVENUE
except ImportError:
    def cached(*_args, **_kwargs): return lambda fn: fn
    def invalidate_revenue_cache(): pass
    TTL_STRIPE_REVENUE = 0
try:
    from master_conductor import get_conductor
except ImportError:
    get_conductor = None
try:
    from funnel_control.routes import funnel_bp
except ImportError:
    funnel_bp = None

app = Flask(__name__)
MRR = int(os.getenv("MRR", 5000)); CUSTOMERS = int(os.getenv("CUSTOMERS", 12)); ARR = int(os.getenv("ARR", MRR * 12))
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
if stripe is not None: stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
conductor = get_conductor() if get_conductor else None
_sse_subscribers: list[queue.Queue] = []; _sse_lock = threading.Lock()

def _notify_sse(event: str, data: dict[str, Any]):
    import json
    payload = f"event: {event}\ndata: {json.dumps(data)}\n\n"
    with _sse_lock:
        for q in list(_sse_subscribers):
            try: q.put_nowait(payload)
            except queue.Full: _sse_subscribers.remove(q)

DASHBOARD_HTML = """<!doctype html><html><head><title>Revenue Agent Dashboard</title></head><body><h1>Revenue Agent Dashboard</h1><h2>Monthly Recurring Revenue</h2><div id='mrr'>$0</div><h2>Active Customers</h2><div id='customers'>0</div><h2>System Status</h2><div>ONLINE</div><script>async function updateDashboard(){const r=await fetch('/api/revenue');const d=await r.json();document.getElementById('mrr').textContent='$'+Number(d.mrr).toLocaleString();document.getElementById('customers').textContent=d.customers;}updateDashboard();</script></body></html>"""

@app.route('/')
def dashboard(): return render_template_string(DASHBOARD_HTML)

@cached('stripe_revenue', ttl=TTL_STRIPE_REVENUE)
def fetch_stripe_revenue():
    if stripe is None or not stripe.api_key:
        return {'mrr': MRR, 'customers': CUSTOMERS, 'arr': ARR, 'total_revenue': 0, 'configured': False}
    try:
        mrr = 0.0
        for sub in stripe.Subscription.list(status='active', limit=100).auto_paging_iter():
            for item in sub['items']['data']:
                price = item['price']; amount = (price.get('unit_amount') or 0) / 100
                if price.get('recurring', {}).get('interval') == 'year': amount /= 12
                mrr += amount * item.get('quantity', 1)
        customers = sum(1 for _ in stripe.Customer.list(limit=100).auto_paging_iter())
        charges = stripe.Charge.list(limit=100)
        total = sum(c['amount'] / 100 for c in charges.data if c.get('status') == 'succeeded')
        return {'mrr': round(mrr, 2), 'customers': customers, 'arr': round(mrr * 12, 2), 'total_revenue': round(total, 2), 'configured': True}
    except Exception as exc:
        return {'mrr': MRR, 'customers': CUSTOMERS, 'arr': ARR, 'total_revenue': 0, 'configured': False, 'error': str(exc)}

@app.route('/api/revenue')
def revenue_api():
    data = fetch_stripe_revenue(); data['timestamp'] = datetime.utcnow().isoformat(); return jsonify(data)

@app.route('/health')
def health(): return jsonify({'status': 'healthy', 'service': 'revenue-agent'})

@app.route('/api/revenue/sync', methods=['POST'])
def sync_revenue():
    invalidate_revenue_cache(); return jsonify({'status': 'success', 'data': fetch_stripe_revenue(), 'timestamp': datetime.utcnow().isoformat()})

@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    if stripe is None: return jsonify({'error': 'Stripe unavailable'}), 503
    try:
        if STRIPE_WEBHOOK_SECRET: event = stripe.Webhook.construct_event(request.data, request.headers.get('Stripe-Signature'), STRIPE_WEBHOOK_SECRET)
        else: event = stripe.Event.construct_from(request.get_json(silent=True) or {}, stripe.api_key)
        event_type = event['type']; invalidate_revenue_cache(); _notify_sse('revenue_update', {'event': event_type})
        return jsonify({'status': 'success', 'event': event_type})
    except Exception as exc: return jsonify({'error': str(exc)}), 400

@app.route('/api/conductor/dashboard')
def conductor_dashboard(): return jsonify(conductor.get_master_dashboard() if conductor else {'status':'unavailable'})
@app.route('/api/conductor/financial-summary')
def conductor_financial_summary(): return jsonify(conductor.get_financial_summary() if conductor else {'status':'unavailable'})
@app.route('/api/conductor/forecast')
def conductor_forecast(): return jsonify(conductor.get_revenue_forecast(request.args.get('months', 12, type=int)) if conductor else {'status':'unavailable'})
@app.route('/api/conductor/health')
def conductor_health(): return jsonify(conductor.get_system_health() if conductor else {'status':'unavailable'})

@app.route('/api/events/stream')
def events_stream():
    def generate():
        q = queue.Queue(maxsize=50)
        with _sse_lock: _sse_subscribers.append(q)
        try:
            yield 'event: heartbeat\ndata: {}\n\n'
            while True:
                try: yield q.get(timeout=25)
                except queue.Empty: yield ': keep-alive\n\n'
        except GeneratorExit: pass
        finally:
            with _sse_lock:
                if q in _sse_subscribers: _sse_subscribers.remove(q)
    return Response(stream_with_context(generate()), mimetype='text/event-stream', headers={'Cache-Control':'no-cache','X-Accel-Buffering':'no'})

if funnel_bp is not None: app.register_blueprint(funnel_bp)
if __name__ == '__main__': app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
