#!/usr/bin/env python3
"""
Vercel-compatible entry point for OneLife Translation Stream
"""
import os
import sys
from pathlib import Path

# Add project directories to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import the FastAPI app from streamer.api
from streamer.api import app

# Set up environment for production
os.environ.setdefault('USE_MOCK', 'false')

# This is what Vercel will use as the ASGI application
handler = app 