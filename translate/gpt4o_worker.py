"""
GPT-4o Mini worker for English to Spanish translation
"""
import os
import asyncio
import queue
import logging
import csv
from typing import Optional, Dict, Callable
from openai import OpenAI

logger = logging.getLogger(__name__)

class GlossaryManager:
    def __init__(self, glossary_path: str = "glossary.csv"):
        self.glossary_path = glossary_path
        self.glossary = {}
        self.load_glossary()
    
    def load_glossary(self):
        """Load glossary from CSV file"""
        try:
            with open(self.glossary_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.glossary[row['en'].lower()] = row['es']
            logger.info(f"Loaded {len(self.glossary)} glossary entries")
        except FileNotFoundError:
            logger.warning(f"Glossary file {self.glossary_path} not found")
        except Exception as e:
            logger.error(f"Error loading glossary: {e}")
    
    def apply_glossary(self, text: str) -> str:
        """Apply glossary replacements to text"""
        if not self.glossary:
            return text
        
        # Simple word replacement (could be enhanced with NLP)
        for en_term, es_term in self.glossary.items():
            text = text.replace(en_term, f"[GLOSSARY:{en_term}→{es_term}]")
        
        return text
    
    def get_glossary_context(self) -> str:
        """Get glossary as context for translation prompt"""
        if not self.glossary:
            return ""
        
        glossary_items = [f"'{en}' → '{es}'" for en, es in self.glossary.items()]
        return f"Glossary: {', '.join(glossary_items)}"

class GPT4oTranslationWorker:
    def __init__(self, api_key: Optional[str] = None, glossary_path: str = "glossary.csv"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.glossary_manager = GlossaryManager(glossary_path)
        self.is_running = False
        
        # System prompt for translation
        self.system_prompt = """You are a fast, literal English→Spanish translator for church services. 
        Maintain the tone and emotion of the original speech. Use Latin American Spanish.
        If provided with glossary terms in brackets [GLOSSARY:term→translation], use the specified translation.
        Return only the Spanish translation without any additional text or explanations."""
    
    async def translate_text(self, english_text: str) -> Optional[str]:
        """Translate English text to Spanish using GPT-4o Mini"""
        try:
            # Apply glossary preprocessing
            preprocessed_text = self.glossary_manager.apply_glossary(english_text)
            
            # Add glossary context if available
            glossary_context = self.glossary_manager.get_glossary_context()
            user_prompt = f"{glossary_context}\n\nTranslate: {preprocessed_text}" if glossary_context else preprocessed_text
            
            # Call GPT-4o Mini
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                max_tokens=500,
                response_format={"type": "text"}
            )
            
            spanish_text = response.choices[0].message.content.strip()
            
            # Clean up glossary markers
            import re
            spanish_text = re.sub(r'\[GLOSSARY:[^\]]+\]', '', spanish_text)
            
            return spanish_text
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return None
    
    async def process_loop(self, 
                          english_queue: queue.Queue, 
                          spanish_callback: Callable[[str], None]):
        """Main processing loop for continuous translation"""
        self.is_running = True
        logger.info("GPT-4o translation worker started")
        
        while self.is_running:
            try:
                # Get English text from queue
                english_text = english_queue.get(timeout=0.1)
                
                if english_text and english_text.strip():
                    # Translate text
                    spanish_text = await self.translate_text(english_text)
                    
                    if spanish_text:
                        logger.info(f"Translated: {english_text[:50]}... → {spanish_text[:50]}...")
                        spanish_callback(spanish_text)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in translation processing loop: {e}")
                await asyncio.sleep(0.1)
    
    def stop(self):
        """Stop the worker"""
        self.is_running = False
        logger.info("Translation worker stopped")

# Mock implementation for testing
class MockTranslationWorker:
    def __init__(self):
        self.is_running = False
        self.mock_translations = [
            "Esta es una traducción de prueba.",
            "Bienvenidos a la iglesia OneLife.",
            "Oremos juntos en este momento.",
            "La palabra de Dios es poderosa.",
            "Que Dios los bendiga a todos."
        ]
        self.translation_index = 0
    
    async def translate_text(self, english_text: str) -> Optional[str]:
        """Mock translation for testing"""
        await asyncio.sleep(0.1)  # Simulate API delay
        translation = self.mock_translations[self.translation_index % len(self.mock_translations)]
        self.translation_index += 1
        return translation
    
    async def process_loop(self, 
                          english_queue: queue.Queue, 
                          spanish_callback: Callable[[str], None]):
        """Mock processing loop"""
        self.is_running = True
        logger.info("Mock translation worker started")
        
        while self.is_running:
            try:
                english_text = english_queue.get(timeout=1.0)
                if english_text:
                    spanish_text = await self.translate_text(english_text)
                    if spanish_text:
                        spanish_callback(spanish_text)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in mock translation: {e}")
                await asyncio.sleep(0.1)
    
    def stop(self):
        self.is_running = False
        logger.info("Mock translation worker stopped")