"""
OpenAI Whisper API worker for speech-to-text
"""
import os
import asyncio
import queue
import logging
from typing import Optional, Callable
import openai
from openai import OpenAI

logger = logging.getLogger(__name__)

class WhisperWorker:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.is_running = False
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
    
    async def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio data using Whisper API"""
        try:
            # Create a temporary file-like object
            import io
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"  # Required for OpenAI API
            
            # Call Whisper API
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language="en"  # Assuming English input
            )
            
            return response.strip() if response else None
            
        except Exception as e:
            logger.error(f"Whisper API error: {e}")
            return None
    
    async def process_loop(self, 
                          audio_queue: queue.Queue, 
                          text_callback: Callable[[str], None]):
        """Main processing loop for continuous transcription"""
        self.is_running = True
        logger.info("Whisper worker started")
        
        while self.is_running:
            try:
                # Get audio data from queue
                audio_data = audio_queue.get(timeout=0.1)
                
                if audio_data:
                    # Transcribe audio
                    text = await self.transcribe_audio(audio_data)
                    
                    if text and text.strip():
                        logger.info(f"Transcribed: {text[:100]}...")
                        text_callback(text.strip())
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in Whisper processing loop: {e}")
                await asyncio.sleep(0.1)
    
    def stop(self):
        """Stop the worker"""
        self.is_running = False
        logger.info("Whisper worker stopped")

# Mock implementation for testing
class MockWhisperWorker:
    def __init__(self):
        self.is_running = False
    
    async def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Mock transcription for testing"""
        await asyncio.sleep(0.1)  # Simulate API delay
        return "This is a mock transcription for testing purposes."
    
    async def process_loop(self, 
                          audio_queue: queue.Queue, 
                          text_callback: Callable[[str], None]):
        """Mock processing loop"""
        self.is_running = True
        logger.info("Mock Whisper worker started")
        
        while self.is_running:
            try:
                audio_data = audio_queue.get(timeout=1.0)
                if audio_data:
                    text = await self.transcribe_audio(audio_data)
                    if text:
                        text_callback(text)
            except queue.Empty:
                # Generate periodic mock transcriptions
                text_callback("Mock English text for translation testing.")
            except Exception as e:
                logger.error(f"Error in mock processing: {e}")
                await asyncio.sleep(0.1)
    
    def stop(self):
        self.is_running = False
        logger.info("Mock Whisper worker stopped")