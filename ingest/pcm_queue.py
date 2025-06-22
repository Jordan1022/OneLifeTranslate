"""
PCM audio queue and buffer management
"""
import asyncio
import queue
import threading
import io
import wave
import struct
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class PCMBuffer:
    def __init__(self, sample_rate: int = 48000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.buffer = []
        self.lock = threading.Lock()
    
    def add_chunk(self, chunk: bytes):
        """Add audio chunk to buffer"""
        with self.lock:
            self.buffer.extend(chunk)
    
    def get_wav_bytes(self, duration_seconds: float = 1.0) -> Optional[bytes]:
        """Get WAV-formatted bytes for the specified duration"""
        samples_needed = int(self.sample_rate * duration_seconds * self.channels)
        bytes_needed = samples_needed * 2  # 16-bit samples
        
        with self.lock:
            if len(self.buffer) < bytes_needed:
                return None
            
            # Extract needed bytes
            chunk_data = bytes(self.buffer[:bytes_needed])
            self.buffer = self.buffer[bytes_needed:]
        
        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(chunk_data)
        
        return wav_buffer.getvalue()
    
    def clear(self):
        """Clear the buffer"""
        with self.lock:
            self.buffer.clear()

class AudioQueue:
    def __init__(self, max_size: int = 100):
        self.queue = queue.Queue(maxsize=max_size)
        self.pcm_buffer = PCMBuffer()
    
    def put_audio_chunk(self, chunk: bytes):
        """Add audio chunk to processing queue"""
        try:
            self.queue.put_nowait(chunk)
            self.pcm_buffer.add_chunk(chunk)
        except queue.Full:
            logger.warning("Audio queue full, dropping chunk")
    
    async def get_wav_for_stt(self, duration: float = 2.0) -> Optional[bytes]:
        """Get WAV data suitable for STT processing"""
        return self.pcm_buffer.get_wav_bytes(duration)
    
    def get_chunk_nowait(self) -> Optional[bytes]:
        """Get audio chunk without blocking"""
        try:
            return self.queue.get_nowait()
        except queue.Empty:
            return None