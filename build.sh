#!/bin/bash
# Full End-to-End Build Script for Revenue Agent System
# This script performs a complete build and validation

set -e  # Exit on any error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Revenue Agent System - Full Build"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Install dependencies
echo "📦 Installing Python dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Step 2: Run tests
echo "🧪 Running test suite..."
python -m pytest tests/ -v
echo "✅ All tests passed"
echo ""

# Step 3: Validate app imports
echo "🔍 Validating Flask app..."
python -c "import app; print('✅ Flask app imports successfully')"
echo ""

# Step 4: Check deployment configuration
echo "🔧 Checking deployment configuration..."
gunicorn app:app --check-config
echo "✅ Gunicorn configuration valid"
echo ""

# Step 5: Test endpoints (if server not running)
echo "🌐 Testing application endpoints..."
if ! curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "Starting test server..."
    gunicorn app:app --bind 0.0.0.0:5000 --daemon --pid build_test.pid
    sleep 3
    
    # Test health
    if curl -s -f http://localhost:5000/health > /dev/null; then
        echo "✅ Health endpoint working"
    else
        echo "❌ Health endpoint failed"
        kill $(cat build_test.pid) 2>/dev/null || true
        exit 1
    fi
    
    # Test revenue API
    if curl -s -f http://localhost:5000/api/revenue > /dev/null; then
        echo "✅ Revenue API working"
    else
        echo "❌ Revenue API failed"
        kill $(cat build_test.pid) 2>/dev/null || true
        exit 1
    fi
    
    # Test dashboard
    if curl -s -f http://localhost:5000/ > /dev/null; then
        echo "✅ Dashboard working"
    else
        echo "❌ Dashboard failed"
        kill $(cat build_test.pid) 2>/dev/null || true
        exit 1
    fi
    
    # Cleanup
    kill $(cat build_test.pid) 2>/dev/null || true
    rm -f build_test.pid
else
    echo "✅ Server already running, skipping endpoint tests"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ BUILD SUCCESSFUL! ✨"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💰 Revenue Agent System is ready for deployment!"
echo ""
echo "Commands:"
echo "  Development: npm run dev  or  python app.py"
echo "  Production:  npm start    or  gunicorn app:app"
echo "  Tests:       npm test     or  python -m pytest tests/"
echo ""
