"""
FastAPI backend for real-time translation streaming
"""
import asyncio
import queue
import logging
import json
import time
import os
import hashlib
import hmac
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sse_starlette.sse import EventSourceResponse
import uvicorn
from pydantic import BaseModel

# Import our workers
import sys
sys.path.append('..')

from ingest.audio_capture import DanteAudioCapture, MockAudioCapture
from ingest.pcm_queue import AudioQueue
from stt.whisper_api_worker import WhisperWorker, MockWhisperWorker
from translate.gpt4o_worker import GPT4oTranslationWorker, MockTranslationWorker
from tts.eleven_stream import ElevenLabsWorker, MockTTSWorker, AudioBuffer
from streamer.hls_packager import HLSPackager, MockHLSPackager

logger = logging.getLogger(__name__)

# Authentication models
class TokenValidationRequest(BaseModel):
    token: str

class AuthConfig:
    def __init__(self):
        # Get auth secret from environment variable
        self.auth_secret = os.getenv('AUTH_SECRET', 'onelife-church-spanish-2024')
        
        # Generate valid tokens (you can customize this logic)
        self.valid_tokens = self._generate_valid_tokens()
    
    def _generate_valid_tokens(self):
        """Generate valid access tokens"""
        # You can customize this to generate multiple tokens
        # For now, we'll create a single shared token and a few dated tokens
        base_tokens = [
            'onelife-spanish-access',  # Main token
            'church-translation-2024',  # Alternative token
        ]
        
        # Add time-based tokens (weekly rotation)
        import datetime
        current_week = datetime.datetime.now().isocalendar()[1]
        weekly_token = f"week-{current_week}-2024"
        base_tokens.append(weekly_token)
        
        # Hash tokens for security
        hashed_tokens = []
        for token in base_tokens:
            # Create HMAC hash
            hashed = hmac.new(
                self.auth_secret.encode(),
                token.encode(),
                hashlib.sha256
            ).hexdigest()[:16]  # Take first 16 chars for shorter URL
            hashed_tokens.append(hashed)
        
        return hashed_tokens + base_tokens  # Accept both hashed and plain for flexibility

# Global auth config
auth_config = AuthConfig()
security = HTTPBearer(auto_error=False)

def verify_token(token: str) -> bool:
    """Verify if a token is valid"""
    if not token:
        return False
    
    # Check against valid tokens
    if token in auth_config.valid_tokens:
        return True
    
    # Check if it's a hashed version of a valid token
    for valid_token in ['onelife-spanish-access', 'church-translation-2024']:
        hashed = hmac.new(
            auth_config.auth_secret.encode(),
            valid_token.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        if token == hashed:
            return True
    
    return False

def get_current_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """Extract and validate token from Authorization header"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not verify_token(credentials.credentials):
        raise HTTPException(status_code=403, detail="Invalid authentication token")
    
    return credentials.credentials

def verify_query_token(request: Request) -> bool:
    """Verify token from query parameters (for SSE endpoints)"""
    token = request.query_params.get('token')
    return verify_token(token) if token else False

class TranslationPipeline:
    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock
        self.is_running = False
        
        # Initialize queues
        self.audio_queue = AudioQueue()
        self.english_queue = queue.Queue()
        self.spanish_queue = queue.Queue()
        self.tts_audio_queue = queue.Queue()
        
        # Initialize workers
        if use_mock:
            self.audio_capture = MockAudioCapture()
            self.whisper_worker = MockWhisperWorker()
            self.translation_worker = MockTranslationWorker()
            self.tts_worker = MockTTSWorker()
            self.hls_packager = MockHLSPackager()
        else:
            self.audio_capture = DanteAudioCapture()
            self.whisper_worker = WhisperWorker()
            self.translation_worker = GPT4oTranslationWorker()
            self.tts_worker = ElevenLabsWorker()
            self.hls_packager = HLSPackager()
        
        self.audio_buffer = AudioBuffer()
        
        # Caption storage with timing
        self.captions = []
        self.caption_clients = set()
        
        # Stream start time for synchronization
        self.stream_start_time = None
    
    async def start_pipeline(self):
        """Start the translation pipeline"""
        if self.is_running:
            return
        
        self.is_running = True
        self.stream_start_time = time.time()
        
        logger.info("Starting translation pipeline...")
        
        # Start all workers
        asyncio.create_task(self.audio_capture.start_capture(self.on_audio_chunk))
        asyncio.create_task(self.whisper_worker.process_loop(self.audio_queue.queue, self.on_english_text))
        asyncio.create_task(self.translation_worker.process_loop(self.english_queue, self.on_spanish_text))
        asyncio.create_task(self.tts_worker.process_loop(self.spanish_queue, self.on_tts_audio))
        asyncio.create_task(self.hls_processing_loop())
    
    async def stop_pipeline(self):
        """Stop the translation pipeline"""
        self.is_running = False
        
        self.audio_capture.stop_capture()
        self.whisper_worker.stop()
        self.translation_worker.stop()
        self.tts_worker.stop()
        
        await self.hls_packager.finalize_stream()
        
        logger.info("Translation pipeline stopped")
    
    def on_audio_chunk(self, audio_data):
        """Handle incoming audio chunk"""
        # Convert numpy array to bytes if needed
        if hasattr(audio_data, 'tobytes'):
            audio_bytes = audio_data.tobytes()
        else:
            audio_bytes = audio_data
        
        self.audio_queue.put_audio_chunk(audio_bytes)
    
    def on_english_text(self, text: str):
        """Handle English transcription"""
        logger.info(f"English: {text}")
        self.english_queue.put(text)
    
    def on_spanish_text(self, text: str):
        """Handle Spanish translation"""
        logger.info(f"Spanish: {text}")
        
        # Add to caption with timing
        current_time = time.time() - self.stream_start_time if self.stream_start_time else 0
        caption = {
            "timestamp": current_time,
            "text": text,
            "language": "es"
        }
        self.captions.append(caption)
        
        # Send to connected caption clients
        asyncio.create_task(self.broadcast_caption(caption))
        
        self.spanish_queue.put(text)
    
    def on_tts_audio(self, audio_data: bytes):
        """Handle TTS audio output"""
        asyncio.create_task(self.audio_buffer.add_chunk(audio_data))
    
    async def hls_processing_loop(self):
        """Process TTS audio into HLS segments"""
        while self.is_running:
            try:
                # Get audio segment from buffer
                wav_data = await self.audio_buffer.get_wav_segment(2.0)
                
                if wav_data:
                    # Create HLS segment
                    segment_path = await self.hls_packager.create_segment_from_audio(wav_data)
                    if segment_path:
                        logger.debug(f"Created HLS segment: {segment_path}")
                    
                    # Cleanup old segments
                    self.hls_packager.cleanup_old_segments()
                else:
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error in HLS processing: {e}")
                await asyncio.sleep(0.1)
    
    async def broadcast_caption(self, caption: Dict[str, Any]):
        """Broadcast caption to all connected clients"""
        if not self.caption_clients:
            return
        
        message = json.dumps(caption)
        
        # Remove disconnected clients
        disconnected = set()
        
        for client in self.caption_clients:
            try:
                await client.put({"type": "sse", "data": message})
            except:
                disconnected.add(client)
        
        self.caption_clients -= disconnected

# Global pipeline instance
pipeline: Optional[TranslationPipeline] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global pipeline
    
    # Startup
    use_mock = True  # Set to False for production with real APIs
    pipeline = TranslationPipeline(use_mock=use_mock)
    
    yield
    
    # Shutdown
    if pipeline:
        await pipeline.stop_pipeline()

# Create FastAPI app
app = FastAPI(
    title="OneLife Translation Stream",
    description="Real-time English to Spanish translation for church services",
    version="0.3.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

@app.get("/")
async def root():
    """Serve the frontend"""
    return FileResponse("frontend/dist/index.html")

@app.post("/validate-token")
async def validate_token(request: TokenValidationRequest):
    """Validate an authentication token"""
    if verify_token(request.token):
        return {"valid": True, "message": "Token is valid"}
    else:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.get("/auth/tokens")
async def get_valid_tokens():
    """Get current valid tokens (for admin use only - remove in production or protect)"""
    # WARNING: This endpoint should be removed or protected in production
    return {
        "tokens": auth_config.valid_tokens,
        "note": "Remove this endpoint in production"
    }

@app.post("/start")
async def start_stream(token: str = Depends(get_current_token)):
    """Start the translation stream"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
    
    await pipeline.start_pipeline()
    return {"status": "started", "stream_url": "/stream/playlist.m3u8"}

@app.post("/stop")
async def stop_stream(token: str = Depends(get_current_token)):
    """Stop the translation stream"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
    
    await pipeline.stop_pipeline()
    return {"status": "stopped"}

@app.get("/stream/{filename}")
async def serve_stream_file(filename: str):
    """Serve HLS stream files"""
    stream_dir = Path("stream")
    file_path = stream_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Stream file not found")
    
    # Set appropriate content type
    if filename.endswith('.m3u8'):
        media_type = "application/vnd.apple.mpegurl"
    elif filename.endswith('.m4s') or filename.endswith('.ts'):
        media_type = "video/mp2t"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(file_path, media_type=media_type)

@app.get("/captions")
async def get_captions_stream(request: Request):
    """SSE endpoint for live captions"""
    # Verify token from query parameter
    if not verify_query_token(request):
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    
    async def caption_generator():
        if not pipeline:
            return
        
        # Create a queue for this client
        client_queue = asyncio.Queue()
        pipeline.caption_clients.add(client_queue)
        
        try:
            while True:
                # Wait for caption data
                event = await client_queue.get()
                if event["type"] == "sse":
                    yield event["data"]
        except asyncio.CancelledError:
            pass
        finally:
            pipeline.caption_clients.discard(client_queue)
    
    return EventSourceResponse(caption_generator())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message.get("type") == "start":
                if pipeline:
                    await pipeline.start_pipeline()
                    await websocket.send_text(json.dumps({
                        "type": "started",
                        "stream_url": "/stream/playlist.m3u8"
                    }))
            elif message.get("type") == "stop":
                if pipeline:
                    await pipeline.stop_pipeline()
                    await websocket.send_text(json.dumps({"type": "stopped"}))
                    
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")

@app.get("/status")
async def get_status(token: str = Depends(get_current_token)):
    """Get pipeline status"""
    if not pipeline:
        return {"status": "not_initialized"}
    
    return {
        "status": "running" if pipeline.is_running else "stopped",
        "captions_count": len(pipeline.captions),
        "connected_clients": len(pipeline.caption_clients),
        "stream_start_time": pipeline.stream_start_time
    }

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )