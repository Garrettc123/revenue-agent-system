"""Production WSGI entrypoint that attaches funnel + autonomous revenue control APIs."""
from flask import jsonify, request

from app import app as application, conductor, fetch_stripe_revenue
from .routes import funnel_bp
from autonomous_runtime import get_runtime

application.register_blueprint(funnel_bp)

# One runtime object per worker. The ledger provides durable observability and
# idempotent event keys; AUTONOMOUS_RUNTIME_ENABLED can disable the loop for tests.
runtime = get_runtime(conductor=conductor, revenue_reader=fetch_stripe_revenue)

@application.get('/api/agents/status')
def agents_status():
    return jsonify(runtime.status())

@application.post('/api/agents/start')
def agents_start():
    return jsonify(runtime.start())

@application.post('/api/agents/stop')
def agents_stop():
    return jsonify(runtime.stop())

@application.post('/api/agents/force-cycle')
def agents_force_cycle():
    return jsonify(runtime.force_cycle())

@application.get('/api/agents/events')
def agents_events():
    limit = request.args.get('limit', 50, type=int)
    events = runtime.ledger.recent(limit)
    return jsonify({'events': events, 'count': len(events)})

@application.get('/api/agents/health')
def agents_health():
    status = runtime.status()
    return jsonify({'status': 'healthy' if status['running'] else 'stopped', 'runtime': status})

if __import__('os').getenv('AUTONOMOUS_RUNTIME_ENABLED', '1').lower() not in {'0', 'false', 'no'}:
    runtime.start()

app = application
