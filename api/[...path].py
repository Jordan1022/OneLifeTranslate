#!/usr/bin/env python3
"""
Vercel-compatible API entry point for OneLife Translation Stream
Simplified version without audio dependencies for serverless deployment
"""
import os
import sys
import json
import time
import hashlib
import hmac
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

# Set up environment for serverless deployment
os.environ.setdefault('USE_MOCK', 'true')

# Authentication models
class TokenValidationRequest(BaseModel):
    token: str

class AuthConfig:
    def __init__(self):
        self.auth_secret = os.getenv('AUTH_SECRET', 'onelife-church-spanish-2024')
        self.valid_tokens = self._generate_valid_tokens()
    
    def _generate_valid_tokens(self):
        base_tokens = [
            'onelife-spanish-access',
            'church-translation-2024',
        ]
        
        # Add time-based tokens
        import datetime
        current_week = datetime.datetime.now().isocalendar()[1]
        weekly_token = f"week-{current_week}-2024"
        base_tokens.append(weekly_token)
        
        # Hash tokens for security
        hashed_tokens = []
        for token in base_tokens:
            hashed = hmac.new(
                self.auth_secret.encode(),
                token.encode(),
                hashlib.sha256
            ).hexdigest()[:16]
            hashed_tokens.append(hashed)
        
        return hashed_tokens + base_tokens

# Global auth config
auth_config = AuthConfig()
security = HTTPBearer(auto_error=False)

def verify_token(token: str) -> bool:
    """Verify if a token is valid"""
    if not token or token not in auth_config.valid_tokens:
        return False
    return True

def get_current_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """Extract and validate token from Authorization header"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not verify_token(credentials.credentials):
        raise HTTPException(status_code=403, detail="Invalid authentication token")
    
    return credentials.credentials

def verify_query_token(request: Request) -> bool:
    """Verify token from query parameters"""
    token = request.query_params.get('token')
    return verify_token(token) if token else False

# Mock pipeline for serverless environment
class MockPipeline:
    def __init__(self):
        self.is_running = False
        self.captions = []
        self.stream_start_time = None
        self.connected_clients = 0
    
    async def start_pipeline(self):
        self.is_running = True
        self.stream_start_time = time.time()
        
        # Add some mock captions
        self.captions = [
            {"timestamp": 0, "text": "Bienvenidos a OneLife Church", "language": "es"},
            {"timestamp": 5, "text": "Servicio de traducción en vivo", "language": "es"}
        ]
    
    async def stop_pipeline(self):
        self.is_running = False

# Create FastAPI app
app = FastAPI(
    title="OneLife Translation Stream",
    description="Real-time English to Spanish translation for church services",
    version="0.3.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance
pipeline = MockPipeline()

@app.get("/")
async def root():
    """API Root"""
    return {"message": "OneLife Translation API", "version": "0.3.0", "mode": "serverless-mock"}

@app.post("/validate-token")
async def validate_token(request: TokenValidationRequest):
    """Validate an authentication token"""
    if verify_token(request.token):
        return {"valid": True, "message": "Token is valid"}
    else:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.get("/auth/tokens")
async def get_valid_tokens():
    """Get current valid tokens (for development only)"""
    return {
        "tokens": auth_config.valid_tokens[:3],  # Only show first 3 for security
        "note": "Mock tokens for serverless deployment"
    }

@app.post("/start")
async def start_stream(token: str = Depends(get_current_token)):
    """Start the translation stream"""
    await pipeline.start_pipeline()
    return {"status": "started", "stream_url": "/stream/playlist.m3u8", "mode": "mock"}

@app.post("/stop")
async def stop_stream(token: str = Depends(get_current_token)):
    """Stop the translation stream"""
    await pipeline.stop_pipeline()
    return {"status": "stopped"}

@app.get("/stream/{filename}")
async def serve_stream_file(filename: str):
    """Serve HLS stream files (mock response)"""
    if filename.endswith('.m3u8'):
        # Return a basic HLS playlist
        content = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
segment-0.ts
#EXT-X-ENDLIST"""
        return {"content": content, "type": "application/vnd.apple.mpegurl"}
    else:
        raise HTTPException(status_code=404, detail="Stream file not found")

@app.get("/captions")
async def get_captions_stream(request: Request):
    """SSE endpoint for live captions"""
    if not verify_query_token(request):
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    
    async def caption_generator():
        # Mock caption stream
        mock_captions = [
            {"timestamp": 0, "text": "Bienvenidos a OneLife Church", "language": "es"},
            {"timestamp": 5, "text": "Servicio de traducción en vivo", "language": "es"},
            {"timestamp": 10, "text": "Este es un modo de demostración", "language": "es"}
        ]
        
        import asyncio
        for caption in mock_captions:
            yield json.dumps(caption)
            await asyncio.sleep(5)  # Wait 5 seconds between captions
    
    return EventSourceResponse(caption_generator())

@app.get("/status")
async def get_status(token: str = Depends(get_current_token)):
    """Get pipeline status"""
    return {
        "status": "running" if pipeline.is_running else "stopped",
        "captions_count": len(pipeline.captions),
        "connected_clients": pipeline.connected_clients,
        "stream_start_time": pipeline.stream_start_time,
        "mode": "serverless-mock"
    }

# Vercel serverless handler
app_handler = app 