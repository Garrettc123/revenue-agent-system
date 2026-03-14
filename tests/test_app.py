"""
Tests for the Revenue Agent System Flask application
"""
import pytest
import json
from datetime import datetime
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for the health check endpoint"""
    
    def test_health_endpoint_returns_200(self, client):
        """Test that health endpoint returns 200 status"""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_health_endpoint_returns_json(self, client):
        """Test that health endpoint returns JSON"""
        response = client.get('/health')
        assert response.content_type == 'application/json'
    
    def test_health_endpoint_has_correct_structure(self, client):
        """Test that health endpoint returns expected data structure"""
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'status' in data
        assert 'service' in data
        assert data['status'] == 'healthy'
        assert data['service'] == 'revenue-agent'


class TestRevenueAPI:
    """Tests for the revenue API endpoint"""
    
    def test_revenue_api_returns_200(self, client):
        """Test that revenue API returns 200 status"""
        response = client.get('/api/revenue')
        assert response.status_code == 200
    
    def test_revenue_api_returns_json(self, client):
        """Test that revenue API returns JSON"""
        response = client.get('/api/revenue')
        assert response.content_type == 'application/json'
    
    def test_revenue_api_has_required_fields(self, client):
        """Test that revenue API returns all required fields"""
        response = client.get('/api/revenue')
        data = json.loads(response.data)
        
        # Check all required fields are present
        required_fields = ['mrr', 'customers', 'arr', 'timestamp']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_revenue_api_mrr_is_number(self, client):
        """Test that MRR is a number"""
        response = client.get('/api/revenue')
        data = json.loads(response.data)
        assert isinstance(data['mrr'], (int, float))
        assert data['mrr'] > 0
    
    def test_revenue_api_customers_is_number(self, client):
        """Test that customers count is a number"""
        response = client.get('/api/revenue')
        data = json.loads(response.data)
        assert isinstance(data['customers'], int)
        assert data['customers'] > 0
    
    def test_revenue_api_arr_is_number(self, client):
        """Test that ARR is a number"""
        response = client.get('/api/revenue')
        data = json.loads(response.data)
        assert isinstance(data['arr'], (int, float))
        assert data['arr'] > 0
    
    def test_revenue_api_arr_calculation(self, client):
        """Test that ARR is 12 times MRR"""
        response = client.get('/api/revenue')
        data = json.loads(response.data)
        assert data['arr'] == data['mrr'] * 12
    
    def test_revenue_api_timestamp_format(self, client):
        """Test that timestamp is in ISO format"""
        response = client.get('/api/revenue')
        data = json.loads(response.data)
        
        # Should be able to parse the timestamp
        try:
            datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("Timestamp is not in valid ISO format")


class TestDashboard:
    """Tests for the dashboard endpoint"""
    
    def test_dashboard_returns_200(self, client):
        """Test that dashboard returns 200 status"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_dashboard_returns_html(self, client):
        """Test that dashboard returns HTML"""
        response = client.get('/')
        assert 'text/html' in response.content_type
    
    def test_dashboard_contains_title(self, client):
        """Test that dashboard HTML contains title"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'Revenue Agent Dashboard' in html
    
    def test_dashboard_contains_revenue_elements(self, client):
        """Test that dashboard contains revenue display elements"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'Monthly Recurring Revenue' in html
        assert 'Active Customers' in html
        assert 'System Status' in html
    
    def test_dashboard_has_javascript(self, client):
        """Test that dashboard includes JavaScript for updates"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert '<script>' in html
        assert '/api/revenue' in html


class TestAppConfiguration:
    """Tests for application configuration"""
    
    def test_app_is_flask_app(self):
        """Test that app is a Flask application"""
        from flask import Flask
        assert isinstance(app, Flask)
    
    def test_app_has_routes(self):
        """Test that app has registered routes"""
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/' in routes
        assert '/health' in routes
        assert '/api/revenue' in routes


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_404_on_invalid_route(self, client):
        """Test that invalid routes return 404"""
        response = client.get('/invalid-route-that-does-not-exist')
        assert response.status_code == 404
    
    def test_405_on_wrong_method(self, client):
        """Test that wrong HTTP methods return 405"""
        response = client.post('/health')
        assert response.status_code == 405


class TestIntegration:
    """Integration tests"""
    
    def test_dashboard_can_fetch_revenue_data(self, client):
        """Test that dashboard can successfully fetch from revenue API"""
        # First get the dashboard
        dashboard_response = client.get('/')
        assert dashboard_response.status_code == 200
        
        # Then verify the API it calls is working
        api_response = client.get('/api/revenue')
        assert api_response.status_code == 200
        data = json.loads(api_response.data)
        assert 'mrr' in data
    
    def test_multiple_api_calls_are_consistent(self, client):
        """Test that multiple API calls return consistent data types"""
        for _ in range(3):
            response = client.get('/api/revenue')
            data = json.loads(response.data)
            assert isinstance(data['mrr'], (int, float))
            assert isinstance(data['customers'], int)
            assert isinstance(data['arr'], (int, float))
