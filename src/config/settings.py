"""
Configuration settings loader
"""
import os
import yaml
from pathlib import Path

def load_settings():
    """Load settings from YAML file"""
    config_path = Path(__file__).parent / "settings.yaml"
    
    # Default settings
    settings = {
        'mode': 'mock',
        'latency_budget': {
            'asr': 90,
            'safety': 50,
            'llm': 280,
            'postprocess': 30,
            'tts': 180,
            'total_target': 700
        },
        'models': {
            'asr': 'deepgram-korean',
            'llm': 'gpt-4o',
            'tts': 'elevenlabs-korean'
        },
        'safety': {
            'escalation_threshold': 0.8,
            'monitoring_threshold': 0.6
        }
    }
    
    # Load from file if exists
    if config_path.exists():
        with open(config_path) as f:
            file_settings = yaml.safe_load(f)
            settings.update(file_settings)
    
    # Override with environment variables
    if os.getenv('INTUNE_MODE'):
        settings['mode'] = os.getenv('INTUNE_MODE')
    
    return settings