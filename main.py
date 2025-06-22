#!/usr/bin/env python3
"""
OneLife Translation Stream - Main Application
Real-time English to Spanish translation for church services
"""
import os
import sys
import logging
import asyncio
from pathlib import Path

# Add project directories to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from streamer.api import app
import uvicorn

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('translation_stream.log')
        ]
    )

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    # Check Python packages
    required_packages = [
        'fastapi', 'uvicorn', 'openai', 'elevenlabs', 
        'numpy', 'asyncio', 'websockets'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_deps.append(package)
    
    # Check for ffmpeg
    import shutil
    if not shutil.which('ffmpeg'):
        print("Warning: ffmpeg not found. HLS streaming may not work properly.")
        print("Install ffmpeg: https://ffmpeg.org/download.html")
    
    if missing_deps:
        print(f"Missing Python packages: {', '.join(missing_deps)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Check environment variables"""
    env_vars = {
        'OPENAI_API_KEY': 'OpenAI API key for Whisper and GPT-4o',
        'ELEVEN_API_KEY': 'ElevenLabs API key for TTS (optional in mock mode)'
    }
    
    missing_vars = []
    for var, description in env_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var}: {description}")
    
    if missing_vars:
        print("Missing environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nCreate a .env file or set these environment variables.")
        print("For testing, you can run in mock mode (USE_MOCK=true)")
        return False
    
    return True

def main():
    """Main application entry point"""
    print("🎤 OneLife Translation Stream v0.3")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment (optional in mock mode)
    use_mock = os.getenv('USE_MOCK', 'false').lower() == 'true'
    if not use_mock and not check_environment():
        print("\nRunning in mock mode for testing...")
        os.environ['USE_MOCK'] = 'true'
    
    # Create required directories
    directories = ['stream', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # Server configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    
    print(f"\n🚀 Starting server at http://{host}:{port}")
    print(f"📺 Frontend will be available at http://localhost:{port}")
    print(f"🔄 Mock mode: {'enabled' if use_mock else 'disabled'}")
    
    if use_mock:
        print("⚠️  Using mock services for development/testing")
        print("   Set real API keys and USE_MOCK=false for production")
    
    print("\n📋 Features:")
    print("  • Real-time audio capture (Dante Virtual Soundcard)")
    print("  • Speech-to-text (OpenAI Whisper)")
    print("  • Translation (GPT-4o Mini)")
    print("  • Text-to-speech (ElevenLabs)")
    print("  • HLS streaming with live captions")
    
    print("\n🎯 Usage:")
    print("  1. Open the web interface")
    print("  2. Click 'Start Stream' to begin translation")
    print("  3. Audio will be captured, translated, and streamed")
    print("  4. View live Spanish captions in the sidebar")
    
    # Start the server
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()