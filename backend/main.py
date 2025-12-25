#!/usr/bin/env python3
"""
Revenue Agent System - Main Entry Point
Starts the FastAPI application server
"""

import uvicorn
import sys
from pathlib import Path

# Add src directory to Python path for module imports
src_path = Path(__file__).parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from api.main import app

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
