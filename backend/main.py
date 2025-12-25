#!/usr/bin/env python3
"""
Revenue Agent System - Main Entry Point
Starts the FastAPI application server
"""

import uvicorn
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    # Import the app from the api module
    from api.main import app
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
