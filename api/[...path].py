#!/usr/bin/env python3
"""
Vercel API entry point for OneLife Translation Stream
"""
import os
import sys
from pathlib import Path

# Add api directory to path
api_root = Path(__file__).parent
sys.path.append(str(api_root))

# Set up environment for production
os.environ.setdefault('USE_MOCK', 'true')  # Use mock mode for Vercel deployment

# Import the FastAPI app from streamer.api
from streamer.api import app

# Export the FastAPI app for Vercel
# Vercel will use this as the ASGI application
def handler(request, context):
    """Vercel serverless function handler"""
    return app

# This is what Vercel will use as the ASGI application
# Both 'app' and 'handler' are available for different Vercel configurations 