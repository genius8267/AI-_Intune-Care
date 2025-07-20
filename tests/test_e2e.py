"""
End-to-end tests for Intune-Care Voice AI Therapist
"""
import pytest
import subprocess
import json
import time

class TestE2E:
    """End-to-end integration tests"""
    
    def test_demo_script_runs(self):
        """Test that demo script executes without errors"""
        result = subprocess.run(
            ["bash", "demo/run_demo.sh"],
            input="안녕하세요",
            text=True,
            capture_output=True
        )
        assert result.returncode == 0
        assert "response" in result.stdout
    
    def test_korean_input_processing(self):
        """Test Korean language input"""
        test_cases = [
            "스트레스를 받고 있어요",
            "우울한 기분이 들어요",
            "불안해서 잠을 못 자요"
        ]
        
        for text in test_cases:
            result = subprocess.run(
                ["python3", "src/main.py", "--mode", "mock", "--text", text, "--json"],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0
            
            # Parse JSON output
            output = json.loads(result.stdout)
            assert output['success'] is True
            assert output['total_latency_ms'] < 700
            assert 'response' in output
    
    def test_crisis_detection(self):
        """Test crisis keyword detection and response"""
        crisis_text = "죽고 싶다는 생각이 들어요"
        
        result = subprocess.run(
            ["python3", "src/main.py", "--mode", "mock", "--text", crisis_text, "--json"],
            capture_output=True,
            text=True
        )
        
        output = json.loads(result.stdout)
        assert output['safety']['risk_level'] == 'immediate'
        assert output['safety']['alert_human'] is True
        assert '혼자가 아닙니다' in output['response']
    
    def test_latency_requirements(self):
        """Test that all responses meet <700ms requirement"""
        # Run 10 requests and check latency
        latencies = []
        
        for i in range(10):
            start = time.time()
            result = subprocess.run(
                ["python3", "src/main.py", "--mode", "mock", "--text", "테스트", "--json"],
                capture_output=True,
                text=True
            )
            end = time.time()
            
            output = json.loads(result.stdout)
            latencies.append(output['total_latency_ms'])
        
        # Check all latencies are under 700ms
        assert all(l < 700 for l in latencies)
        
        # Check P95 latency
        latencies.sort()
        p95_index = int(len(latencies) * 0.95)
        assert latencies[p95_index] < 700
    
    def test_cultural_emotion_detection(self):
        """Test Korean cultural emotion markers"""
        test_cases = {
            "마음속에 깊은 한이 있어요": "한",
            "정이 많은 사람이에요": "정",
            "눈치를 너무 많이 봐요": "눈치"
        }
        
        for text, expected_marker in test_cases.items():
            result = subprocess.run(
                ["python3", "src/main.py", "--mode", "mock", "--text", text, "--json"],
                capture_output=True,
                text=True
            )
            
            output = json.loads(result.stdout)
            assert expected_marker in output.get('cultural_markers', [])
    
    @pytest.mark.skip(reason="Requires Docker setup")
    def test_docker_deployment(self):
        """Test Docker Compose deployment"""
        # This would test the full Docker setup
        # Skipped in basic tests but important for CI/CD
        pass