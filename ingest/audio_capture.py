"""
Audio capture from Dante Virtual Soundcard using PortAudio
"""
import asyncio
import queue
import threading
import numpy as np
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)

class DanteAudioCapture:
    def __init__(self, 
                 sample_rate: int = 48000,
                 channels: int = 1,
                 chunk_size: int = 1024,
                 device_name: Optional[str] = None):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.device_name = device_name
        self.audio_queue = queue.Queue()
        self.is_running = False
        self.stream = None
        
        # Try to import pyaudio (fallback to portaudio)
        try:
            import pyaudio
            self.pa = pyaudio.PyAudio()
            self.use_pyaudio = True
        except ImportError:
            logger.warning("PyAudio not found, using basic audio capture")
            self.use_pyaudio = False
    
    def find_dante_device(self) -> Optional[int]:
        """Find Dante Virtual Soundcard device"""
        if not self.use_pyaudio:
            return None
            
        for i in range(self.pa.get_device_count()):
            device_info = self.pa.get_device_info_by_index(i)
            if "dante" in device_info['name'].lower() or "dvs" in device_info['name'].lower():
                logger.info(f"Found Dante device: {device_info['name']}")
                return i
        
        logger.warning("No Dante device found, using default input")
        return None
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Audio callback for real-time processing"""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Convert bytes to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        
        # Put audio data in queue for processing
        try:
            self.audio_queue.put_nowait(audio_data)
        except queue.Full:
            logger.warning("Audio queue full, dropping frame")
        
        return (None, 0)  # Continue recording
    
    async def start_capture(self, callback: Callable[[np.ndarray], None]):
        """Start audio capture with callback"""
        if not self.use_pyaudio:
            logger.error("PyAudio not available, cannot start capture")
            return
        
        device_index = self.find_dante_device()
        
        self.stream = self.pa.open(
            format=self.pa.get_format_from_width(2),  # 16-bit
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=self.chunk_size,
            stream_callback=self.audio_callback
        )
        
        self.is_running = True
        self.stream.start_stream()
        logger.info("Audio capture started")
        
        # Process audio data in background
        while self.is_running:
            try:
                audio_data = self.audio_queue.get(timeout=0.1)
                callback(audio_data)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing audio: {e}")
    
    def stop_capture(self):
        """Stop audio capture"""
        self.is_running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.use_pyaudio:
            self.pa.terminate()
        logger.info("Audio capture stopped")

# Mock implementation for testing when Dante is not available
class MockAudioCapture:
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.is_running = False
    
    async def start_capture(self, callback: Callable[[np.ndarray], None]):
        """Mock audio capture for testing"""
        self.is_running = True
        logger.info("Mock audio capture started")
        
        while self.is_running:
            # Generate silent audio for testing
            mock_audio = np.zeros(1024, dtype=np.int16)
            callback(mock_audio)
            await asyncio.sleep(0.02)  # ~50ms chunks
    
    def stop_capture(self):
        self.is_running = False
        logger.info("Mock audio capture stopped")