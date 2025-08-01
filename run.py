#!/usr/bin/env python
"""
Run script for the Finance SMS Logger Flask Application.
"""

import os
import sys
import dotenv
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

dotenv.load_dotenv(project_dir / ".env")

# Check if virtual environment is activated
if not hasattr(sys, "real_prefix") and not (
    hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
):
    print("WARNING: Virtual environment not activated!")
    print("Please activate it with: .\\venv\\Scripts\\activate.ps1")
    print()

# Import and run the Flask app
try:
    from app import app, AppConfig

    print("Finance SMS Logger Flask Application")
    print("=" * 50)
    print(f"Debug mode: {AppConfig.DEBUG}")
    print(f"API Prefix: {AppConfig.API_PREFIX}")
    print(f"Log Level: {AppConfig.LOG_LEVEL}")
    print("=" * 50)
    print("Starting server...")
    print("=" * 50)

    # Create necessary directories
    os.makedirs(AppConfig.LOGS_DIR, exist_ok=True)
    app.run(
        port=AppConfig.PORT,
        debug=AppConfig.DEBUG,
        threaded=True,
    )

except ImportError as e:
    print(f"Import error: {e}")
    print(
        "Please ensure all dependencies are installed: pip install -r requirements.txt"
    )
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)
