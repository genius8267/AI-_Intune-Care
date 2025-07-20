#!/usr/bin/env python3
"""
Latency benchmark test for Intune-Care voice pipeline
"""
import asyncio
import time
import json
import statistics
from datetime import datetime
import aiohttp
import numpy as np

# Test configuration
API_URL = "http://localhost:8080/api/v1/voice"
WS_URL = "ws://localhost:8080/ws"
TEST_SAMPLES = [
    "안녕하세요, 오늘 기분이 어떠세요?",
    "요즘 너무 힘들고 우울해요",
    "직장 스트레스로 잠을 못 자고 있어요",
    "가족과의 관계가 어려워요",
    "미래가 불안해요"
]
ITERATIONS = 100

async def measure_single_request(session, audio_data):
    """Measure latency for a single voice request"""
    start_time = time.perf_counter()
    
    try:
        async with session.post(API_URL, data=audio_data) as response:
            result = await response.json()
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            return {
                "latency_ms": latency_ms,
                "success": True,
                "response": result
            }
    except Exception as e:
        return {
            "latency_ms": None,
            "success": False,
            "error": str(e)
        }

async def run_benchmark():
    """Run the complete benchmark suite"""
    results = []
    
    async with aiohttp.ClientSession() as session:
        for i in range(ITERATIONS):
            # Cycle through test samples
            sample = TEST_SAMPLES[i % len(TEST_SAMPLES)]
            
            # Simulate audio data (in real test, would be actual audio)
            audio_data = sample.encode('utf-8')
            
            result = await measure_single_request(session, audio_data)
            results.append(result)
            
            # Small delay between requests
            await asyncio.sleep(0.1)
            
            if (i + 1) % 10 == 0:
                print(f"Progress: {i + 1}/{ITERATIONS} requests completed")
    
    return results

def analyze_results(results):
    """Analyze benchmark results"""
    successful_results = [r for r in results if r["success"]]
    latencies = [r["latency_ms"] for r in successful_results]
    
    if not latencies:
        return {"error": "No successful requests"}
    
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "total_requests": len(results),
        "successful_requests": len(successful_results),
        "failed_requests": len(results) - len(successful_results),
        "success_rate": len(successful_results) / len(results) * 100,
        "latency_stats": {
            "min": min(latencies),
            "max": max(latencies),
            "mean": statistics.mean(latencies),
            "median": statistics.median(latencies),
            "stdev": statistics.stdev(latencies) if len(latencies) > 1 else 0,
            "p50": np.percentile(latencies, 50),
            "p75": np.percentile(latencies, 75),
            "p90": np.percentile(latencies, 90),
            "p95": np.percentile(latencies, 95),
            "p99": np.percentile(latencies, 99)
        }
    }
    
    # Check if we meet the target
    analysis["meets_target"] = analysis["latency_stats"]["p95"] < 700
    
    return analysis

def generate_report(analysis):
    """Generate a markdown report"""
    report = f"""# Latency Benchmark Report

Generated: {analysis['timestamp']}

## Summary
- Total Requests: {analysis['total_requests']}
- Success Rate: {analysis['success_rate']:.1f}%
- **P95 Latency: {analysis['latency_stats']['p95']:.0f}ms**
- Target Met: {'✅ Yes' if analysis['meets_target'] else '❌ No'}

## Latency Distribution
| Percentile | Latency (ms) | Target | Status |
|------------|--------------|--------|--------|
| P50 | {analysis['latency_stats']['p50']:.0f} | <500 | {'✅' if analysis['latency_stats']['p50'] < 500 else '❌'} |
| P75 | {analysis['latency_stats']['p75']:.0f} | <600 | {'✅' if analysis['latency_stats']['p75'] < 600 else '❌'} |
| P90 | {analysis['latency_stats']['p90']:.0f} | <700 | {'✅' if analysis['latency_stats']['p90'] < 700 else '❌'} |
| P95 | {analysis['latency_stats']['p95']:.0f} | <700 | {'✅' if analysis['latency_stats']['p95'] < 700 else '❌'} |
| P99 | {analysis['latency_stats']['p99']:.0f} | <900 | {'✅' if analysis['latency_stats']['p99'] < 900 else '❌'} |

## Statistics
- Min: {analysis['latency_stats']['min']:.0f}ms
- Max: {analysis['latency_stats']['max']:.0f}ms
- Mean: {analysis['latency_stats']['mean']:.0f}ms
- Median: {analysis['latency_stats']['median']:.0f}ms
- StdDev: {analysis['latency_stats']['stdev']:.0f}ms
"""
    return report

async def main():
    """Main benchmark execution"""
    print("🚀 Starting Intune-Care Latency Benchmark")
    print(f"Running {ITERATIONS} requests...")
    
    # Run benchmark
    results = await run_benchmark()
    
    # Analyze results
    analysis = analyze_results(results)
    
    # Save results
    with open('results/latest.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Generate report
    report = generate_report(analysis)
    with open('results/report.md', 'w') as f:
        f.write(report)
    
    # Print summary
    print("\n📊 Benchmark Complete!")
    print(f"P95 Latency: {analysis['latency_stats']['p95']:.0f}ms")
    print(f"Target Met: {'✅ Yes' if analysis['meets_target'] else '❌ No'}")
    
    # Exit with appropriate code
    exit(0 if analysis['meets_target'] else 1)

if __name__ == "__main__":
    asyncio.run(main())