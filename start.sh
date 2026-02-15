#!/bin/bash
# Quick Start Script for Revenue Agent System
# This script starts the revenue agent system with minimal setup

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💰 Revenue Agent System - Quick Start"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -q -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi
echo ""

# Determine mode (dev or prod)
MODE=${1:-dev}

if [ "$MODE" = "prod" ] || [ "$MODE" = "production" ]; then
    echo "🚀 Starting in PRODUCTION mode with gunicorn..."
    echo "📍 Server will be available at: http://localhost:5000"
    echo ""
    echo "API Endpoints:"
    echo "  • Dashboard:  http://localhost:5000/"
    echo "  • Health:     http://localhost:5000/health"
    echo "  • Revenue:    http://localhost:5000/api/revenue"
    echo ""
    gunicorn app:app --bind 0.0.0.0:5000 --workers 2 --timeout 120
else
    echo "🔧 Starting in DEVELOPMENT mode..."
    echo "📍 Server will be available at: http://localhost:5000"
    echo ""
    echo "API Endpoints:"
    echo "  • Dashboard:  http://localhost:5000/"
    echo "  • Health:     http://localhost:5000/health"
    echo "  • Revenue:    http://localhost:5000/api/revenue"
    echo ""
    python app.py
fi
