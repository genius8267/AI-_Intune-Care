#!/bin/bash
# Intune-Care Voice AI Therapist - Quick Demo Script
# No setup required - runs in mock mode by default

set -e

echo "🎙️ Intune-Care Real-Time Voice AI Therapist Demo"
echo "================================================"
echo ""

# Check if running from correct directory
if [ ! -f "src/main.py" ]; then
    echo "❌ Error: Please run this script from the repository root directory"
    echo "   cd AI-_Intune-Care && ./demo/run_demo.sh"
    exit 1
fi

# Use provided text or default
INPUT_TEXT="${1:-안녕하세요, 오늘 기분이 좀 우울해요}"

echo "📝 Input: \"$INPUT_TEXT\""
echo ""
echo "🔄 Processing..."
echo ""

# Run the demo in mock mode (no API keys needed)
python3 src/main.py --mode mock --text "$INPUT_TEXT"

echo ""
echo "✅ Demo complete!"
echo ""
echo "💡 To run with real APIs:"
echo "   1. Copy .env.example to .env"
echo "   2. Add your API keys"
echo "   3. Run: python3 src/main.py --mode live --text \"$INPUT_TEXT\""
echo ""
echo "📺 See demo/demo_video.mp4 for full system demonstration"