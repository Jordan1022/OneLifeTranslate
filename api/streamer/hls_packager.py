"""
HLS packager for streaming Spanish audio using ffmpeg
"""
import os
import asyncio
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional, List
import time

logger = logging.getLogger(__name__)

class HLSPackager:
    def __init__(self, output_dir: str = "stream", segment_duration: int = 2):
        self.output_dir = Path(output_dir)
        self.segment_duration = segment_duration
        self.playlist_file = self.output_dir / "playlist.m3u8"
        self.segment_counter = 0
        self.is_running = False
        self.ffmpeg_process = None
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize empty playlist
        self.init_playlist()
    
    def init_playlist(self):
        """Initialize HLS playlist file"""
        playlist_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:{self.segment_duration}
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-PLAYLIST-TYPE:EVENT
"""
        with open(self.playlist_file, 'w') as f:
            f.write(playlist_content)
    
    def add_segment(self, segment_path: str, duration: float):
        """Add a new segment to the HLS playlist"""
        try:
            # Read current playlist
            with open(self.playlist_file, 'r') as f:
                lines = f.readlines()
            
            # Find insertion point (before #EXT-X-ENDLIST if present)
            insert_index = len(lines)
            if lines and lines[-1].strip() == "#EXT-X-ENDLIST":
                insert_index = -1
            
            # Add new segment
            segment_name = Path(segment_path).name
            new_lines = [
                f"#EXTINF:{duration:.3f},\n",
                f"{segment_name}\n"
            ]
            
            # Insert new segment
            if insert_index == -1:
                lines = lines[:-1] + new_lines + [lines[-1]]
            else:
                lines.extend(new_lines)
            
            # Write updated playlist
            with open(self.playlist_file, 'w') as f:
                f.writelines(lines)
            
            logger.info(f"Added segment {segment_name} to playlist")
            
        except Exception as e:
            logger.error(f"Error adding segment to playlist: {e}")
    
    async def create_segment_from_audio(self, audio_data: bytes) -> Optional[str]:
        """Create HLS segment from audio data using ffmpeg"""
        try:
            segment_filename = f"segment_{self.segment_counter:06d}.m4s"
            segment_path = self.output_dir / segment_filename
            self.segment_counter += 1
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_wav.write(audio_data)
                temp_wav_path = temp_wav.name
            
            try:
                # Convert to HLS segment using ffmpeg
                ffmpeg_cmd = [
                    'ffmpeg', '-y', '-i', temp_wav_path,
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    '-ar', '48000',
                    '-ac', '1',
                    '-f', 'segment',
                    '-segment_format', 'mpegts',
                    '-segment_time', str(self.segment_duration),
                    '-segment_list_flags', '+live',
                    str(segment_path)
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *ffmpeg_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    # Calculate segment duration
                    duration = self.segment_duration
                    
                    # Add to playlist
                    self.add_segment(str(segment_path), duration)
                    
                    return str(segment_path)
                else:
                    logger.error(f"FFmpeg error: {stderr.decode()}")
                    return None
                    
            finally:
                # Clean up temporary file
                os.unlink(temp_wav_path)
                
        except Exception as e:
            logger.error(f"Error creating HLS segment: {e}")
            return None
    
    async def finalize_stream(self):
        """Finalize the HLS stream"""
        try:
            # Add end marker to playlist
            with open(self.playlist_file, 'a') as f:
                f.write("#EXT-X-ENDLIST\n")
            
            logger.info("HLS stream finalized")
            
        except Exception as e:
            logger.error(f"Error finalizing stream: {e}")
    
    def cleanup_old_segments(self, keep_count: int = 10):
        """Clean up old segment files"""
        try:
            segments = sorted(self.output_dir.glob("segment_*.m4s"))
            
            if len(segments) > keep_count:
                old_segments = segments[:-keep_count]
                for segment in old_segments:
                    segment.unlink()
                    logger.debug(f"Removed old segment: {segment.name}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up segments: {e}")

# Mock implementation for testing
class MockHLSPackager:
    def __init__(self, output_dir: str = "stream", segment_duration: int = 2):
        self.output_dir = Path(output_dir)
        self.segment_duration = segment_duration
        self.segment_counter = 0
        self.output_dir.mkdir(exist_ok=True)
        
        # Create a simple mock playlist
        playlist_path = self.output_dir / "playlist.m3u8"
        with open(playlist_path, 'w') as f:
            f.write("""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:2
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-PLAYLIST-TYPE:EVENT
""")
    
    async def create_segment_from_audio(self, audio_data: bytes) -> Optional[str]:
        """Mock segment creation"""
        segment_filename = f"mock_segment_{self.segment_counter:06d}.m4s"
        segment_path = self.output_dir / segment_filename
        self.segment_counter += 1
        
        # Create empty segment file
        with open(segment_path, 'wb') as f:
            f.write(b'\x00' * 1024)  # Mock segment data
        
        # Update mock playlist
        playlist_path = self.output_dir / "playlist.m3u8"
        with open(playlist_path, 'a') as f:
            f.write(f"#EXTINF:{self.segment_duration}.000,\n")
            f.write(f"{segment_filename}\n")
        
        logger.info(f"Created mock segment: {segment_filename}")
        return str(segment_path)
    
    async def finalize_stream(self):
        """Mock stream finalization"""
        playlist_path = self.output_dir / "playlist.m3u8"
        with open(playlist_path, 'a') as f:
            f.write("#EXT-X-ENDLIST\n")
        logger.info("Mock HLS stream finalized")
    
    def cleanup_old_segments(self, keep_count: int = 10):
        """Mock cleanup"""
        logger.debug("Mock segment cleanup")