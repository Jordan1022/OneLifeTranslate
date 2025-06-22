#!/usr/bin/env python3
"""
OneLife Translation Stream Demo
Demonstrates the translation pipeline with sample content
"""
import asyncio
import logging
import time
import os
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample church service content for demonstration
DEMO_ENGLISH_PHRASES = [
    "Welcome to OneLife Church! We're so glad you're here with us today.",
    "Let's begin our worship service by standing and singing together.",
    "Today we're going to talk about God's amazing grace and love for us.",
    "The Holy Spirit is moving in our hearts and lives.",
    "We invite you to join us for communion, the Lord's Supper.",
    "Your tithes and offerings support our ministry and mission.",
    "Let's pray together for our community and those in need.",
    "The Scripture reading today comes from the Gospel of John.",
    "We believe in salvation through faith in Jesus Christ.",
    "May God's blessing be upon you as you leave here today."
]

DEMO_SPANISH_TRANSLATIONS = [
    "¡Bienvenidos a la iglesia OneLife! Estamos muy contentos de que estén aquí con nosotros hoy.",
    "Comencemos nuestro servicio de adoración poniéndonos de pie y cantando juntos.",
    "Hoy vamos a hablar sobre la gracia y el amor increíbles de Dios por nosotros.",
    "El Espíritu Santo se está moviendo en nuestros corazones y vidas.",
    "Los invitamos a acompañarnos en la comunión, la Cena del Señor.",
    "Sus diezmos y ofrendas apoyan nuestro ministerio y misión.",
    "Oremos juntos por nuestra comunidad y por aquellos en necesidad.",
    "La lectura de las Escrituras de hoy viene del Evangelio de Juan.",
    "Creemos en la salvación a través de la fe en Jesucristo.",
    "Que la bendición de Dios sea sobre ustedes al salir de aquí hoy."
]

class TranslationDemo:
    def __init__(self):
        self.is_running = False
        self.phrase_index = 0
        
    def print_header(self):
        print("🎤 OneLife Translation Stream - DEMO MODE")
        print("=" * 60)
        print("This demo simulates the real-time translation pipeline:")
        print("1. English speech input → Spanish audio output")
        print("2. Live captions synchronized with audio")
        print("3. Church-specific terminology using custom glossary")
        print("=" * 60)
        print()
    
    def simulate_audio_capture(self):
        """Simulate audio capture from Dante device"""
        print("🎙️  [AUDIO CAPTURE] Dante Virtual Soundcard connected")
        print("   └─ Sample rate: 48kHz, Channels: 1 (mono)")
        print("   └─ Audio chunks: 1024 samples (~21ms)")
        time.sleep(0.5)
    
    def simulate_speech_recognition(self, text):
        """Simulate Whisper API speech-to-text"""
        print(f"🎧 [WHISPER API] Processing audio... ", end="", flush=True)
        time.sleep(1.0)  # Simulate API latency
        print("✓")
        print(f"   └─ Transcribed: \"{text}\"")
        return text
    
    def apply_glossary(self, text):
        """Apply church-specific glossary terms"""
        glossary_replacements = {
            "Holy Spirit": "Espíritu Santo",
            "Lord's Supper": "Cena del Señor", 
            "tithes and offerings": "diezmos y ofrendas",
            "communion": "comunión",
            "salvation": "salvación",
            "Scripture": "Escrituras"
        }
        
        applied_terms = []
        for en_term, es_term in glossary_replacements.items():
            if en_term.lower() in text.lower():
                applied_terms.append(f"{en_term} → {es_term}")
        
        if applied_terms:
            print("📖 [GLOSSARY] Applied church terms:")
            for term in applied_terms:
                print(f"   └─ {term}")
        
        return text
    
    def simulate_translation(self, english_text):
        """Simulate GPT-4o Mini translation"""
        print(f"🔄 [GPT-4o MINI] Translating... ", end="", flush=True)
        time.sleep(0.8)  # Simulate API latency
        print("✓")
        
        # Get corresponding Spanish translation
        spanish_text = DEMO_SPANISH_TRANSLATIONS[self.phrase_index]
        print(f"   └─ Translated: \"{spanish_text}\"")
        return spanish_text
    
    def simulate_text_to_speech(self, spanish_text):
        """Simulate ElevenLabs TTS"""
        print(f"🗣️  [ELEVENLABS TTS] Generating speech... ", end="", flush=True)
        time.sleep(1.2)  # Simulate TTS processing
        print("✓")
        print(f"   └─ Voice: Lucía (LATAM Spanish)")
        print(f"   └─ Audio chunks: Streaming 44.1kHz")
        return b"mock_audio_data"
    
    def simulate_hls_streaming(self, audio_data):
        """Simulate HLS packaging and streaming"""
        print(f"📺 [HLS PACKAGER] Creating segments... ", end="", flush=True)
        time.sleep(0.3)  # Simulate ffmpeg processing
        print("✓")
        print(f"   └─ Segment: 2-second duration")
        print(f"   └─ Format: AAC audio, 128kbps")
        print(f"   └─ Playlist: Updated with new segment")
        return "segment_001.m4s"
    
    def simulate_caption_sync(self, spanish_text, timestamp):
        """Simulate caption synchronization"""
        print(f"💬 [LIVE CAPTIONS] Synchronized display")
        print(f"   └─ Timestamp: {timestamp:.1f}s")
        print(f"   └─ Caption: \"{spanish_text}\"")
        print(f"   └─ Delivery: Server-Sent Events (SSE)")
    
    async def run_translation_pipeline(self, english_phrase):
        """Run complete translation pipeline for one phrase"""
        print(f"\n🔄 Processing phrase {self.phrase_index + 1}/{len(DEMO_ENGLISH_PHRASES)}")
        print("─" * 50)
        
        start_time = time.time()
        
        # Step 1: Audio capture
        self.simulate_audio_capture()
        
        # Step 2: Speech recognition
        english_text = self.simulate_speech_recognition(english_phrase)
        
        # Step 3: Apply glossary
        english_text = self.apply_glossary(english_text)
        
        # Step 4: Translation
        spanish_text = self.simulate_translation(english_text)
        
        # Step 5: Text-to-speech
        audio_data = self.simulate_text_to_speech(spanish_text)
        
        # Step 6: HLS streaming
        segment_file = self.simulate_hls_streaming(audio_data)
        
        # Step 7: Caption synchronization
        self.simulate_caption_sync(spanish_text, time.time() - start_time)
        
        total_time = time.time() - start_time
        print(f"\n⏱️  Total latency: {total_time:.2f}s (Target: <3s)")
        
        self.phrase_index += 1
        return spanish_text
    
    async def run_demo(self):
        """Run the complete demo"""
        self.print_header()
        
        print("Starting demo in 3 seconds...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            await asyncio.sleep(1)
        
        print("\n🚀 Demo starting now!\n")
        
        # Process each demo phrase
        for phrase in DEMO_ENGLISH_PHRASES:
            await self.run_translation_pipeline(phrase)
            
            # Wait between phrases
            print("\n⏸️  Waiting for next phrase...")
            await asyncio.sleep(2)
        
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("\nThis demo showed the complete translation pipeline:")
        print("• Audio capture from Dante Virtual Soundcard")
        print("• Real-time speech recognition with Whisper")
        print("• Context-aware translation with GPT-4o Mini")
        print("• Natural speech synthesis with ElevenLabs")
        print("• HLS streaming with synchronized captions")
        print("\n🎯 Ready for live church services!")
        print("   Run 'python main.py' to start the real system")

async def main():
    """Main demo function"""
    demo = TranslationDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())