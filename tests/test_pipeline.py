"""
Unit tests for voice pipeline components
"""
import pytest
import asyncio
from src.pipeline import asr, safety, llm, tts
from src.config.settings import load_settings

class TestPipeline:
    """Test voice pipeline components"""
    
    @pytest.fixture
    def settings(self):
        """Load test settings"""
        return load_settings()
    
    @pytest.mark.asyncio
    async def test_asr_latency(self, settings):
        """Test ASR stays within latency budget"""
        result = await asr.process_audio(b"mock audio data", mode="mock")
        assert result['latency_ms'] <= settings['latency_budget']['asr']
        assert result['text'] is not None
    
    @pytest.mark.asyncio
    async def test_safety_crisis_detection(self):
        """Test safety layer detects crisis keywords"""
        crisis_text = "죽고 싶어요"
        result = await safety.check_safety(crisis_text)
        assert result['risk_level'] == 'immediate'
        assert result['intervention'] == 'crisis'
        assert result['alert_human'] is True
    
    @pytest.mark.asyncio
    async def test_safety_normal_flow(self):
        """Test safety layer passes normal text"""
        normal_text = "오늘 날씨가 좋네요"
        result = await safety.check_safety(normal_text)
        assert result['risk_level'] == 'low'
        assert result['intervention'] == 'none'
        assert result['alert_human'] is False
    
    @pytest.mark.asyncio
    async def test_llm_korean_emotion(self):
        """Test LLM detects Korean cultural emotions"""
        han_text = "마음속 깊은 한이 있어요"
        result = await llm.process_text(han_text, mode="mock")
        assert '한' in result['cultural_markers']
        assert result['latency_ms'] <= 280
    
    @pytest.mark.asyncio
    async def test_end_to_end_latency(self):
        """Test full pipeline stays under 700ms"""
        start = asyncio.get_event_loop().time()
        
        # Simulate full pipeline
        asr_result = await asr.process_audio(b"audio", mode="mock")
        safety_result = await safety.check_safety(asr_result['text'])
        llm_result = await llm.process_text(asr_result['text'], mode="mock")
        tts_result = await tts.synthesize_speech(llm_result['response'], mode="mock")
        
        total_latency = (asyncio.get_event_loop().time() - start) * 1000
        
        # Check individual components
        assert asr_result['latency_ms'] <= 90
        assert safety_result['latency_ms'] <= 50
        assert llm_result['latency_ms'] <= 280
        assert tts_result['latency_ms'] <= 180
        
        # Check total
        component_sum = (asr_result['latency_ms'] + safety_result['latency_ms'] + 
                        llm_result['latency_ms'] + tts_result['latency_ms'])
        assert component_sum < 700
        
    def test_settings_loading(self, settings):
        """Test configuration loading"""
        assert settings['mode'] in ['mock', 'live']
        assert settings['latency_budget']['total_target'] == 700
        assert 'safety' in settings
        assert 'models' in settings