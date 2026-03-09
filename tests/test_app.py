"""
Smoke tests for the Revenue Agent System Flask app.
Tests that all key endpoints return expected responses.
"""
import json
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Health check returns healthy status."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'revenue-agent'


def test_dashboard_loads(client):
    """Dashboard HTML page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Revenue Agent' in response.data


def test_revenue_api(client):
    """Revenue API returns expected fields."""
    response = client.get('/api/revenue')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'mrr' in data
    assert 'customers' in data
    assert 'arr' in data
    assert 'timestamp' in data
    assert isinstance(data['mrr'], (int, float))
    assert isinstance(data['customers'], int)


def test_trigger_payout_success(client):
    """Trigger payout succeeds when amount meets tier minimum."""
    response = client.post(
        '/api/trigger-payout',
        json={'affiliate_id': 'test_001', 'tier': 'silver', 'amount': 150}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['amount'] == 150
    assert data['tier'] == 'silver'


def test_trigger_payout_below_minimum(client):
    """Trigger payout returns 400 when amount is below tier minimum."""
    response = client.post(
        '/api/trigger-payout',
        json={'affiliate_id': 'test_001', 'tier': 'gold', 'amount': 50}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'pending'


def test_checkout_success_page(client):
    """Checkout success page renders with session ID."""
    response = client.get('/checkout/success?session_id=cs_test_123')
    assert response.status_code == 200
    assert b'cs_test_123' in response.data


def test_checkout_cancel_page(client):
    """Checkout cancel page renders."""
    response = client.get('/checkout/cancel')
    assert response.status_code == 200
    assert b'Cancelled' in response.data


def test_conductor_dashboard(client):
    """Master conductor dashboard returns operational status."""
    response = client.get('/api/conductor/dashboard')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'operational'
    assert 'summary' in data
    assert 'revenueStreams' in data


def test_conductor_health(client):
    """Conductor health check returns status."""
    response = client.get('/api/conductor/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data


def test_conductor_financial_summary(client):
    """Conductor financial summary returns revenue data."""
    response = client.get('/api/conductor/financial-summary')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'revenue' in data
    assert 'expenses' in data
    assert 'projections' in data
    assert 'gross' in data['revenue']
    assert 'margin' in data['revenue']


def test_conductor_forecast(client):
    """Conductor forecast returns projection data."""
    response = client.get('/api/conductor/forecast')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'forecast12Months' in data
    assert 'totalProjected' in data
    assert 'growthRate' in data
    assert isinstance(data['forecast12Months'], list)
    assert len(data['forecast12Months']) > 0
