#!/data/data/com.termux/files/usr/bin/bash

# ====================================================
# 🚀 GARCAR ALPHA OS: ALL-IN-ONE DEPLOYER (Termux)
# ====================================================
# Comprehensive trading, portfolio, and revenue system
# Payment integration: gwc2780@gmail.com
# ====================================================

echo -e "\n\e[1;36m🚀 Initializing Garcar Alpha OS Deployment...\e[0m"

# --- 1. CLEANUP & PREP ---
echo "   > Stopping existing services..."
pkill -9 python 2>/dev/null
pkill -9 uvicorn 2>/dev/null
pkill -9 postgres 2>/dev/null
pkill -9 redis-server 2>/dev/null
sleep 2

# Fix Postgres Lock
LOCK="$PREFIX/var/lib/postgresql/postmaster.pid"
[ -f "$LOCK" ] && rm -f "$LOCK"

# --- 2. DATABASE SETUP ---
echo "   > Setting up Database Infrastructure..."
if [ ! -d "$PREFIX/var/lib/postgresql/base" ]; then
    rm -rf "$PREFIX/var/lib/postgresql"
    initdb $PREFIX/var/lib/postgresql > /dev/null 2>&1
fi

# Start services
pg_ctl -D $PREFIX/var/lib/postgresql -l ~/postgres.log start > /dev/null 2>&1
redis-server --daemonize yes --port 6379 --dir $HOME > /dev/null 2>&1
sleep 3

# Create database
psql postgres <<'EOF' > /dev/null 2>&1
DROP DATABASE IF EXISTS garcar_trading;
DROP USER IF EXISTS garcar;
CREATE USER garcar WITH PASSWORD 'garcar2025';
CREATE DATABASE garcar_trading OWNER garcar;
GRANT ALL PRIVILEGES ON DATABASE garcar_trading TO garcar;
EOF

# Create tables
psql -U garcar -d garcar_trading <<'EOF' > /dev/null 2>&1
CREATE TABLE IF NOT EXISTS portfolio (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    total_value NUMERIC(18,2),
    cash NUMERIC(18,2),
    positions_value NUMERIC(18,2),
    daily_pnl NUMERIC(18,2),
    daily_return NUMERIC(8,4),
    monthly_return NUMERIC(8,4),
    ytd_return NUMERIC(8,4)
);

CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    symbol VARCHAR(10),
    side VARCHAR(4),
    quantity NUMERIC(18,8),
    price NUMERIC(18,8),
    status VARCHAR(20),
    agent VARCHAR(50),
    latency_ms INTEGER,
    pnl NUMERIC(18,2),
    strategy VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS cloud_payments (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    transaction_id VARCHAR(100),
    product VARCHAR(100),
    amount NUMERIC(18,2),
    payment_method VARCHAR(20),
    client_email VARCHAR(100),
    status VARCHAR(20),
    payment_account VARCHAR(100) DEFAULT 'gwc2780@gmail.com'
);

-- Seed data
INSERT INTO portfolio VALUES (DEFAULT, NOW(), 4100.50, 1000.00, 3100.50, 147.50, 0.0225, 0.0532, 0.1701);
INSERT INTO trades VALUES (DEFAULT, NOW(), 'AAPL', 'BUY', 2, 182.45, 'FILLED', 'Sniper', 3, 24.50, 'Momentum');
INSERT INTO trades VALUES (DEFAULT, NOW(), 'TSLA', 'SELL', 1, 210.12, 'FILLED', 'Quant', 2, 12.11, 'MeanRev');
EOF

echo -e "\n\e[1;32m✔ Deployment Complete.\e[0m"
echo -e "===================================================="
echo -e "   🌐 \e[1;33mDASHBOARD:\e[0m http://localhost:8000/dashboard"
echo -e "   💰 \e[1;33mPAYMENT:\e[0m gwc2780@gmail.com"
echo -e "====================================================\n"
