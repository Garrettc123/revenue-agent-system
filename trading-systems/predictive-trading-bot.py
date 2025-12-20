#!/usr/bin/env python3
"""
Predictive Algorithmic Trading Signal System
Machine learning-powered trading bot with technical indicators
"""

import yfinance as yf
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictiveTradingBot:
    def __init__(self, ticker='AAPL', start_date='2020-01-01', end_date='2025-12-20'):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.model = None
        self.data = None

    def get_data_and_features(self):
        """
        Fetches historical stock data and engineers features for the predictive model.
        The features are designed to capture trends, momentum, and volatility.
        """
        try:
            logger.info(f"Fetching data for {self.ticker}...")
            data = yf.download(self.ticker, start=self.start_date, end=self.end_date)
            
            if data.empty:
                logger.error("No data found for the given ticker and date range.")
                return None, None
            
            # Target: 1 if price went up, 0 otherwise
            data['target'] = (data['Close'].shift(-1) > data['Close']).astype(int)
            data['Signal'] = 0
            
            # Feature Engineering
            # 1. Moving Averages (for Trend)
            data['SMA_5'] = data['Close'].rolling(window=5).mean()
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            
            # 2. Relative Strength Index (RSI - for Momentum)
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            RS = gain / loss
            data['RSI_14'] = 100 - (100 / (1 + RS))
            
            # 3. MACD (for Momentum and Trend)
            exp1 = data['Close'].ewm(span=12, adjust=False).mean()
            exp2 = data['Close'].ewm(span=26, adjust=False).mean()
            data['MACD'] = exp1 - exp2
            data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
            
            # 4. Volatility (using Bollinger Bands)
            data['Upper_BB'] = data['SMA_20'] + 2 * data['Close'].rolling(window=20).std()
            data['Lower_BB'] = data['SMA_20'] - 2 * data['Close'].rolling(window=20).std()
            
            # Drop NaN values
            data.dropna(inplace=True)
            
            # Define features (X) and target (y)
            features = ['Close', 'SMA_5', 'SMA_20', 'RSI_14', 'MACD', 'MACD_Signal', 'Upper_BB', 'Lower_BB']
            X = data[features]
            y = data['target']
            
            self.data = data
            return X, y
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return None, None

    def generate_signals(self, X, y):
        """
        Trains a RandomForestClassifier and generates buy/sell signals.
        """
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Train model
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            logger.info(f"Model Accuracy: {accuracy:.2f}")
            
            # Generate signals
            full_predictions = self.model.predict(X)
            signals = np.where(full_predictions == 1, 'BUY', 'SELL')
            
            return signals
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            return None

    def run(self):
        """
        Execute complete trading signal generation
        """
        logger.info(f"🤖 Predictive Trading Bot initialized for {self.ticker}")
        
        X, y = self.get_data_and_features()
        
        if X is not None:
            signals = self.generate_signals(X, y)
            
            if signals is not None:
                self.data['Signal'] = signals
                
                last_signal_date = self.data.index[-1].strftime('%Y-%m-%d')
                last_signal = self.data['Signal'].iloc[-1]
                
                logger.info(f"\n📊 Latest Signal for {self.ticker} on {last_signal_date}: {last_signal}")
                logger.info(f"\n📈 Last 10 Days:")
                print(self.data[['Close', 'Signal']].tail(10))
                
                return self.data
        
        return None


if __name__ == "__main__":
    # Run for multiple tickers
    tickers = ['AAPL', 'TSLA', 'MSFT', 'NVDA']
    
    for ticker in tickers:
        bot = PredictiveTradingBot(ticker=ticker)
        bot.run()
        print("\n" + "="*80 + "\n")
