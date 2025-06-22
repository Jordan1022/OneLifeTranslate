"""
ElevenLabs streaming TTS worker for Spanish audio generation
"""
import os
import asyncio
import queue
import logging
from typing import Optional, Callable, AsyncGenerator
import io

logger = logging.getLogger(__name__)

class ElevenLabsWorker:
    def __init__(self, api_key: Optional[str] = None, voice_name: str = "Lucía"):
        self.api_key = api_key or os.getenv("ELEVEN_API_KEY")
        if not self.api_key:
            raise ValueError("ElevenLabs API key is required")
        
        self.voice_name = voice_name
        self.voice_id = None
        self.is_running = False
        self.initialize_voice()
    
    def initialize_voice(self):
        """Initialize ElevenLabs voice"""
        try:
            from elevenlabs import voices, generate, stream, set_api_key
            set_api_key(self.api_key)
            
            # Find voice ID for Lucía or similar LATAM voice
            available_voices = voices()
            for voice in available_voices:
                if "lucia" in voice.name.lower() or "latam" in voice.name.lower():
                    self.voice_id = voice.voice_id
                    logger.info(f"Using voice: {voice.name}")
                    break
            
            if not self.voice_id:
                # Use first available voice as fallback
                self.voice_id = available_voices[0].voice_id
                logger.warning(f"Lucía voice not found, using: {available_voices[0].name}")
                
        except ImportError:
            logger.error("ElevenLabs library not installed")
            self.voice_id = "mock_voice"
        except Exception as e:
            logger.error(f"Error initializing ElevenLabs: {e}")
            self.voice_id = "mock_voice"
    
    async def text_to_speech_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """Stream TTS audio for Spanish text"""
        try:
            from elevenlabs import generate, stream
            
            # Generate streaming audio
            audio_stream = generate(
                text=text,
                voice=self.voice_id,
                model="eleven_multilingual_v2",
                stream=True
            )
            
            # Yield audio chunks
            for chunk in audio_stream:
                if chunk:
                    yield chunk
                    
        except ImportError:
            # Mock audio data for testing
            logger.warning("ElevenLabs not available, using mock audio")
            yield b'\x00' * 1024  # Silent audio chunk
        except Exception as e:
            logger.error(f"TTS streaming error: {e}")
            yield b'\x00' * 1024  # Silent audio chunk
    
    async def process_loop(self, 
                          spanish_queue: queue.Queue, 
                          audio_callback: Callable[[bytes], None]):
        """Main processing loop for continuous TTS"""
        self.is_running = True
        logger.info("ElevenLabs TTS worker started")
        
        while self.is_running:
            try:
                # Get Spanish text from queue
                spanish_text = spanish_queue.get(timeout=0.1)
                
                if spanish_text and spanish_text.strip():
                    logger.info(f"Generating TTS for: {spanish_text[:50]}...")
                    
                    # Stream TTS audio
                    async for audio_chunk in self.text_to_speech_stream(spanish_text):
                        if audio_chunk:
                            audio_callback(audio_chunk)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in TTS processing loop: {e}")
                await asyncio.sleep(0.1)
    
    def stop(self):
        """Stop the worker"""
        self.is_running = False
        logger.info("TTS worker stopped")

# Mock implementation for testing
class MockTTSWorker:
    def __init__(self):
        self.is_running = False
    
    async def text_to_speech_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """Mock TTS streaming"""
        # Generate silent audio chunks
        chunk_size = 1024
        duration_chunks = 10  # ~0.2 seconds at 48kHz
        
        for _ in range(duration_chunks):
            yield b'\x00' * chunk_size
            await asyncio.sleep(0.02)  # 20ms per chunk
    
    async def process_loop(self, 
                          spanish_queue: queue.Queue, 
                          audio_callback: Callable[[bytes], None]):
        """Mock processing loop"""
        self.is_running = True
        logger.info("Mock TTS worker started")
        
        while self.is_running:
            try:
                spanish_text = spanish_queue.get(timeout=1.0)
                if spanish_text:
                    logger.info(f"Mock TTS for: {spanish_text[:50]}...")
                    async for audio_chunk in self.text_to_speech_stream(spanish_text):
                        if audio_chunk:
                            audio_callback(audio_chunk)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in mock TTS: {e}")
                await asyncio.sleep(0.1)
    
    def stop(self):
        self.is_running = False
        logger.info("Mock TTS worker stopped")

class AudioBuffer:
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.buffer = io.BytesIO()
        self.lock = asyncio.Lock()
    
    async def add_chunk(self, chunk: bytes):
        """Add audio chunk to buffer"""
        async with self.lock:
            self.buffer.write(chunk)
    
    async def get_wav_segment(self, duration_seconds: float = 2.0) -> Optional[bytes]:
        """Get WAV segment from buffer"""
        bytes_needed = int(self.sample_rate * duration_seconds * 2)  # 16-bit
        
        async with self.lock:
            self.buffer.seek(0)
            data = self.buffer.read(bytes_needed)
            
            if len(data) < bytes_needed:
                return None
            
            # Remove read data from buffer
            remaining = self.buffer.read()
            self.buffer = io.BytesIO(remaining)
        
        # Create WAV file
        import wave
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(data)
        
        return wav_buffer.getvalue()