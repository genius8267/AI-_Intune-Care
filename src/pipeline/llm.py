"""
LLM (Large Language Model) Processing
GPT-4o integration for therapeutic responses
"""
import asyncio
import os
import random
from typing import Dict, Tuple

class LLMProcessor:
    def __init__(self, mode: str = "mock"):
        self.mode = mode
        self.target_latency = 280  # ms
        
        if mode == "live":
            self.api_key = os.getenv("OPENAI_API_KEY")
            # Would initialize OpenAI client here
        
        # Mock responses for different emotional states
        self.mock_responses = {
            'sadness': [
                "지금 많이 힘드신 것 같네요. 우울한 기분이 드실 때는 그 감정을 인정하는 것부터 시작하는 게 중요해요. 오늘 어떤 일이 있으셨는지 편하게 이야기해 주실 수 있을까요?",
                "마음이 무거우신가 봐요. 이런 감정을 느끼는 것은 자연스러운 일이에요. 함께 천천히 이야기해보면서 마음의 짐을 조금씩 덜어보면 어떨까요?"
            ],
            'anxiety': [
                "불안한 마음이 크신 것 같아요. 지금 이 순간, 깊게 숨을 들이쉬고 천천히 내쉬어 보세요. 무엇이 가장 걱정되시는지 말씀해 주실 수 있나요?",
                "걱정이 많으신가 봐요. 불안은 우리를 보호하려는 마음의 신호예요. 구체적으로 어떤 부분이 가장 신경 쓰이시는지 함께 살펴볼까요?"
            ],
            'stress': [
                "스트레스가 많이 쌓이셨군요. 일상에서 작은 휴식을 찾는 것도 중요해요. 최근에 가장 부담스러웠던 일은 무엇인가요?",
                "많이 지치셨나 봐요. 스트레스를 받을 때는 잠시 멈추고 자신을 돌아보는 시간이 필요해요. 오늘 하루는 어떠셨나요?"
            ],
            'neutral': [
                "안녕하세요! 오늘은 어떤 하루를 보내고 계신가요? 편하게 이야기 나누어요.",
                "만나서 반가워요. 오늘 기분은 어떠신가요? 무엇이든 편하게 말씀해 주세요."
            ]
        }
    
    async def generate(self, text: str, safety_result: Dict) -> Tuple[str, Dict]:
        """
        Generate therapeutic response and emotion analysis
        """
        # Detect emotion
        emotion = await self._analyze_emotion(text)
        
        if self.mode == "mock":
            # Simulate processing time
            await asyncio.sleep(self.target_latency / 1000)
            
            # Select appropriate response based on emotion
            emotion_type = emotion['primary']
            responses = self.mock_responses.get(emotion_type, self.mock_responses['neutral'])
            response = random.choice(responses)
            
        else:  # live mode
            # Real OpenAI API call would go here
            await asyncio.sleep(self.target_latency / 1000)
            response = "Live mode response would come from GPT-4o"
        
        return response, emotion
    
    async def _analyze_emotion(self, text: str) -> Dict:
        """Analyze emotional content"""
        # Korean emotion keywords
        emotion_keywords = {
            'sadness': ['우울', '슬프', '힘들', '외로', '눈물'],
            'anxiety': ['불안', '걱정', '두렵', '무서', '긴장'],
            'stress': ['스트레스', '압박', '부담', '지치', '피곤'],
            'anger': ['화나', '짜증', '분노', '억울', '미워'],
            'joy': ['기쁘', '행복', '좋', '즐거', '신나']
        }
        
        # Detect primary emotion
        detected_emotion = 'neutral'
        max_score = 0
        
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > max_score:
                max_score = score
                detected_emotion = emotion
        
        # Korean cultural emotions
        cultural_emotions = {
            '한': 0.0,
            '정': 0.0, 
            '눈치': 0.0
        }
        
        # Check for 한 (han)
        if any(word in text for word in ['그리움', '서러움', '아쉬움', '후회']):
            cultural_emotions['한'] = 0.7
        
        # Check for 정 (jeong)
        if any(word in text for word in ['고마워', '보고싶', '사랑', '우리']):
            cultural_emotions['정'] = 0.7
            
        # Check for 눈치 (nunchi)
        if any(word in text for word in ['미안', '부담', '실례', '죄송']):
            cultural_emotions['눈치'] = 0.6
        
        return {
            'primary': detected_emotion,
            'confidence': min(max_score * 0.3 + 0.5, 1.0),
            'cultural': cultural_emotions
        }