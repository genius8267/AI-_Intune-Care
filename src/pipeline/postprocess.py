"""
Post-processing Module
PII scrubbing, tone adjustment, safety validation
"""
import asyncio
import re
from typing import Optional

class PostProcessor:
    def __init__(self, mode: str = "mock"):
        self.mode = mode
        self.target_latency = 30  # ms
        
        # PII patterns to remove
        self.pii_patterns = [
            (r'\d{3}-\d{4}-\d{4}', '[전화번호]'),  # Phone numbers
            (r'\d{6}-\d{7}', '[주민번호]'),        # Korean ID numbers
            (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[이메일]'),  # Email
            (r'\d{5,}', '[번호]'),                 # Long numbers
        ]
    
    async def process(self, text: str) -> str:
        """
        Clean and validate response text
        """
        # Simulate processing time
        if self.mode == "mock":
            await asyncio.sleep(self.target_latency / 1000)
        
        # Remove PII
        cleaned = self._scrub_pii(text)
        
        # Ensure appropriate tone
        cleaned = self._adjust_tone(cleaned)
        
        # Validate length
        if len(cleaned) > 500:
            cleaned = cleaned[:497] + "..."
        
        return cleaned
    
    def _scrub_pii(self, text: str) -> str:
        """Remove personally identifiable information"""
        result = text
        for pattern, replacement in self.pii_patterns:
            result = re.sub(pattern, replacement, result)
        return result
    
    def _adjust_tone(self, text: str) -> str:
        """Ensure therapeutic, supportive tone"""
        # Remove any harsh language
        harsh_words = {
            '절대': '가능하면',
            '반드시': '되도록',
            '틀렸': '다르게 생각해볼 수 있',
            '안돼': '어려울 수 있어'
        }
        
        result = text
        for harsh, gentle in harsh_words.items():
            result = result.replace(harsh, gentle)
        
        # Ensure polite endings
        if not result.endswith(('요', '까요?', '네요', '어요')):
            if result.endswith('.'):
                result = result[:-1] + '요.'
        
        return result