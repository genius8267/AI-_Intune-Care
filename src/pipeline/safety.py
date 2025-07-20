"""
3-Layer Safety System
Real-time crisis detection and intervention
"""
import asyncio
import re
from typing import Dict, List

class SafetyGuard:
    def __init__(self, mode: str = "mock"):
        self.mode = mode
        self.target_latency = 50  # ms
        
        # Korean crisis keywords (with variations)
        self.crisis_keywords = {
            'immediate': ['자살', '죽고싶', '죽고 싶', '죽을래', '죽을 래', '목매', '투신', 
                         '죽어', '죽을', '죽고', '죽는', '죽이고'],
            'high': ['우울', '힘들어', '힘들 어', '포기', '무의미', '절망', '끝내', '사라지'],
            'medium': ['외로워', '외로 워', '슬퍼', '슬 퍼', '불안', '걱정', '스트레스']
        }
        
        # Regex patterns for more flexible matching
        self.crisis_patterns = {
            'immediate': [
                r'죽\s*고\s*싶',     # 죽고싶, 죽고 싶, 죽 고 싶
                r'죽\s*을\s*래',     # 죽을래, 죽을 래
                r'자\s*살',          # 자살, 자 살
                r'목\s*[을를]\s*매',  # 목을 매, 목 을 매
                r'뛰\s*어\s*내\s*리'  # 뛰어내리, 뛰어 내리
            ],
            'high': [
                r'우\s*울',          # 우울, 우 울
                r'힘\s*들',          # 힘들어, 힘 들어
                r'포\s*기',          # 포기, 포 기
                r'절\s*망',          # 절망, 절 망
            ]
        }
        
        self.emergency_response = """당신의 마음이 많이 힘드신 것 같아요. 
지금 이 순간, 당신은 혼자가 아닙니다. 
잠시만 기다려 주세요. 곧 전문 상담사님이 연결될 거예요.
그동안 제가 옆에 있을게요. 함께 깊은 숨을 쉬어볼까요?"""
    
    async def check(self, text: str) -> Dict:
        """
        3-layer safety check
        Returns risk assessment and intervention plan
        """
        # Layer 1: Keyword detection (5ms)
        layer1_start = asyncio.create_task(self._layer1_keywords(text))
        
        # Layer 2: Context analysis (20ms)
        layer2_start = asyncio.create_task(self._layer2_context(text))
        
        # Layer 3: Pattern analysis (25ms)
        layer3_start = asyncio.create_task(self._layer3_patterns(text))
        
        # Wait for all layers
        layer1_risk = await layer1_start
        layer2_risk = await layer2_start
        layer3_risk = await layer3_start
        
        # Combine assessments
        max_risk = max(layer1_risk, layer2_risk, layer3_risk)
        
        # Determine risk level
        if max_risk > 0.8:
            risk_level = "critical"
            intervention = "immediate_escalation"
        elif max_risk > 0.6:
            risk_level = "high"
            intervention = "enhanced_monitoring"
        elif max_risk > 0.4:
            risk_level = "medium"
            intervention = "gentle_support"
        else:
            risk_level = "low"
            intervention = None
        
        # Simulate total processing time
        if self.mode == "mock":
            await asyncio.sleep(max(0, (self.target_latency / 1000) - 0.025))
        
        return {
            'risk_level': risk_level,
            'risk_score': max_risk,
            'intervention': intervention,
            'layers': {
                'keyword': layer1_risk,
                'context': layer2_risk,
                'pattern': layer3_risk
            },
            'emergency_response': self.emergency_response if risk_level == "critical" else None
        }
    
    async def _layer1_keywords(self, text: str) -> float:
        """Layer 1: Real-time keyword detection"""
        await asyncio.sleep(0.005)  # 5ms
        
        risk_score = 0.0
        
        # Check exact keywords
        for level, keywords in self.crisis_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    if level == 'immediate':
                        risk_score = max(risk_score, 0.9)
                    elif level == 'high':
                        risk_score = max(risk_score, 0.7)
                    elif level == 'medium':
                        risk_score = max(risk_score, 0.5)
        
        # Check regex patterns for flexible spacing
        for level, patterns in self.crisis_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    if level == 'immediate':
                        risk_score = max(risk_score, 0.95)
                    elif level == 'high':
                        risk_score = max(risk_score, 0.75)
        
        return risk_score
    
    async def _layer2_context(self, text: str) -> float:
        """Layer 2: Contextual analysis"""
        await asyncio.sleep(0.02)  # 20ms
        
        # Check for isolation indicators
        isolation_words = ['혼자', '아무도', '관심없', '버림받']
        isolation_score = sum(1 for word in isolation_words if word in text) * 0.2
        
        # Check for hopelessness
        hopeless_words = ['의미없', '포기', '끝', '못하겠']
        hopeless_score = sum(1 for word in hopeless_words if word in text) * 0.25
        
        return min(isolation_score + hopeless_score, 1.0)
    
    async def _layer3_patterns(self, text: str) -> float:
        """Layer 3: Pattern analysis"""
        await asyncio.sleep(0.025)  # 25ms
        
        # Analyze sentence patterns
        risk_patterns = [
            r'더\s*이상.*못|안|없',  # "더 이상 ~ 못/안/없"
            r'죽.*싶|싶.*죽',        # Death wish patterns
            r'끝.*내|내.*끝'         # Ending patterns
        ]
        
        pattern_score = 0.0
        for pattern in risk_patterns:
            if re.search(pattern, text):
                pattern_score += 0.3
        
        return min(pattern_score, 1.0)