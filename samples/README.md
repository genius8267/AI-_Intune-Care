# Audio Samples for Testing

This directory contains Korean language audio samples for testing the voice pipeline.

## Sample Files

- `korean_greeting.wav` - "안녕하세요, 오늘 기분이 어떠세요?"
- `emotional_distress.wav` - "요즘 너무 힘들고 우울해요"
- `work_stress.wav` - "직장 스트레스로 잠을 못 자고 있어요"
- `family_issues.wav` - "가족과의 관계가 어려워요"
- `future_anxiety.wav` - "미래가 불안해요"

## Format Specifications

- Format: WAV
- Sample Rate: 16kHz
- Bit Depth: 16-bit
- Channels: Mono
- Duration: 3-5 seconds each

## Usage

```bash
# Test single file
curl -X POST http://localhost:8080/api/v1/voice \
  -H "Content-Type: audio/wav" \
  --data-binary @samples/korean_greeting.wav

# Test WebSocket streaming
wscat -c ws://localhost:8080/ws < samples/emotional_distress.wav
```

## Recording New Samples

To record new test samples:

```bash
# macOS
sox -d -r 16000 -c 1 -b 16 samples/new_sample.wav

# Linux
arecord -f S16_LE -r 16000 -c 1 samples/new_sample.wav

# Using FFmpeg
ffmpeg -f avfoundation -i ":0" -ar 16000 -ac 1 samples/new_sample.wav
```

## Privacy Note

These samples are for testing purposes only. Do not include real therapy sessions or personally identifiable information.