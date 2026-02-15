#!/bin/bash
# Revenue Agent System - Deployment Script
# Usage: ./deploy.sh [local|production]

set -e

DEPLOYMENT_TYPE="${1:-local}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Revenue Agent System Deployment"
echo "===================================="
echo ""

# Check dependencies
check_dependencies() {
    echo "📋 Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    echo "✅ All dependencies found"
    echo ""
}

# Create .env file if it doesn't exist
setup_env() {
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        echo "📝 Creating .env file from template..."
        if [ -f "$SCRIPT_DIR/.env.example" ]; then
            cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
            echo "✅ .env file created. Please update it with your actual values."
            echo "⚠️  Edit .env file before continuing with production deployment!"
            
            if [ "$DEPLOYMENT_TYPE" = "production" ]; then
                echo ""
                read -p "Press enter to continue after updating .env file..."
            fi
        else
            echo "❌ .env.example not found!"
            exit 1
        fi
    else
        echo "✅ .env file already exists"
    fi
    echo ""
}

# Deploy locally
deploy_local() {
    echo "🏠 Deploying locally..."
    echo ""
    
    # Determine docker compose command
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        DOCKER_COMPOSE="docker compose"
    fi
    
    # Build and start services
    echo "🔨 Building Docker images..."
    $DOCKER_COMPOSE build
    
    echo ""
    echo "🚀 Starting services..."
    $DOCKER_COMPOSE up -d
    
    echo ""
    echo "⏳ Waiting for services to be healthy..."
    sleep 10
    
    # Check health
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "✅ Application is healthy!"
    else
        echo "⚠️  Application may not be fully started yet. Check logs with: $DOCKER_COMPOSE logs -f"
    fi
    
    echo ""
    echo "📊 Service Status:"
    $DOCKER_COMPOSE ps
    
    echo ""
    echo "🎉 Deployment complete!"
    echo ""
    echo "📍 Access points:"
    echo "   • Revenue Dashboard: http://localhost:8000"
    echo "   • Health Check:      http://localhost:8000/health"
    echo "   • Grafana:           http://localhost:3000 (admin/admin123)"
    echo "   • Prometheus:        http://localhost:9090"
    echo ""
    echo "📝 Useful commands:"
    echo "   • View logs:         $DOCKER_COMPOSE logs -f"
    echo "   • Stop services:     $DOCKER_COMPOSE down"
    echo "   • Restart:           $DOCKER_COMPOSE restart"
    echo ""
}

# Deploy to production (Railway/Render)
deploy_production() {
    echo "☁️  Production Deployment"
    echo ""
    echo "⚠️  This will deploy to production environment."
    echo ""
    
    read -p "Are you sure you want to continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Deployment cancelled."
        exit 0
    fi
    
    # Check if Railway CLI is available
    if command -v railway &> /dev/null; then
        echo "🚂 Deploying with Railway..."
        railway up
    # Check if Render CLI is available
    elif command -v render &> /dev/null; then
        echo "☁️  Deploying with Render..."
        render deploy
    else
        echo "⚠️  No production deployment tool found (Railway or Render CLI)"
        echo ""
        echo "Options:"
        echo "1. Install Railway CLI: npm i -g @railway/cli"
        echo "2. Push to GitHub and use Render's GitHub integration"
        echo "3. Use Docker deployment: docker-compose -f docker-compose.yml up -d"
        echo ""
        exit 1
    fi
    
    echo ""
    echo "✅ Production deployment initiated!"
    echo "Check your platform dashboard for deployment status."
}

# Main deployment flow
main() {
    cd "$SCRIPT_DIR"
    
    check_dependencies
    setup_env
    
    case "$DEPLOYMENT_TYPE" in
        local)
            deploy_local
            ;;
        production|prod)
            deploy_production
            ;;
        *)
            echo "❌ Invalid deployment type: $DEPLOYMENT_TYPE"
            echo "Usage: $0 [local|production]"
            exit 1
            ;;
    esac
}

main
