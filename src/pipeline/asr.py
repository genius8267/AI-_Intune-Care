"""
ASR (Automatic Speech Recognition) Module
Deepgram integration with mock mode for demos
"""
import asyncio
import time
import os
from typing import Optional

class ASRProcessor:
    def __init__(self, mode: str = "mock"):
        self.mode = mode
        self.target_latency = 90  # ms
        
        if mode == "live":
            self.api_key = os.getenv("DEEPGRAM_API_KEY")
            if self.api_key:
                # Would initialize Deepgram client here
                pass
    
    async def process(self, audio_or_text: str) -> str:
        """
        Process audio to text (or pass through text in mock mode)
        """
        if self.mode == "mock":
            # Simulate processing time
            await asyncio.sleep(self.target_latency / 1000)
            # In mock mode, just return the input text
            return audio_or_text
        
        else:  # live mode
            # Real Deepgram API call would go here
            # For now, simulate with realistic latency
            await asyncio.sleep(self.target_latency / 1000)
            
            # This would be replaced with actual Deepgram transcription
            return audio_or_text
    
    def validate_korean(self, text: str) -> bool:
        """Check if text contains Korean characters"""
        return any('\uac00' <= char <= '\ud7af' for char in text)