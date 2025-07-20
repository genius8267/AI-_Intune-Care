"""
Inference Service - Real-time AI processing for voice therapy
"""
import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import openai
from typing import Optional, AsyncGenerator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Intune-Care Inference Service")

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class TranscriptRequest(BaseModel):
    text: str
    session_id: str
    emotion: Optional[dict] = None
    context: Optional[list] = []

class InferenceResponse(BaseModel):
    response: str
    emotion: dict
    safety_score: float
    processing_time_ms: int

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": os.getenv("MODEL_NAME", "gpt-4o"),
        "service": "inference"
    }

@app.post("/process")
async def process_transcript(request: TranscriptRequest):
    """Process transcript and generate response"""
    import time
    start_time = time.time()
    
    try:
        # Generate therapeutic response
        response = await generate_response(
            request.text,
            request.context,
            request.emotion
        )
        
        # Analyze emotion
        emotion = analyze_emotion(request.text)
        
        # Calculate safety score
        safety_score = calculate_safety_score(request.text, response)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return InferenceResponse(
            response=response,
            emotion=emotion,
            safety_score=safety_score,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stream")
async def stream_response(request: TranscriptRequest):
    """Stream response for real-time interaction"""
    async def generate():
        async for chunk in stream_therapeutic_response(
            request.text,
            request.context,
            request.emotion
        ):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

async def generate_response(text: str, context: list, emotion: dict) -> str:
    """Generate therapeutic response using GPT-4o"""
    
    system_prompt = """You are a compassionate AI therapist specializing in CBT. 
    You understand Korean culture deeply, including concepts like 한(han), 정(jeong), and 눈치(nunchi).
    Respond with empathy, validation, and gentle guidance.
    Keep responses concise (2-3 sentences) for natural conversation flow."""
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add context from previous conversation
    for ctx in context[-5:]:  # Last 5 exchanges
        messages.append({"role": "user", "content": ctx["user"]})
        messages.append({"role": "assistant", "content": ctx["assistant"]})
    
    # Add current message
    messages.append({"role": "user", "content": text})
    
    response = await openai.ChatCompletion.acreate(
        model=os.getenv("MODEL_NAME", "gpt-4o"),
        messages=messages,
        max_tokens=int(os.getenv("MAX_TOKENS", "500")),
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
    )
    
    return response.choices[0].message.content

async def stream_therapeutic_response(
    text: str, 
    context: list, 
    emotion: dict
) -> AsyncGenerator[str, None]:
    """Stream therapeutic response for low latency"""
    
    system_prompt = """You are a compassionate AI therapist. 
    Respond with empathy and understanding.
    Keep responses natural and conversational."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]
    
    stream = await openai.ChatCompletion.acreate(
        model=os.getenv("MODEL_NAME", "gpt-4o"),
        messages=messages,
        stream=True,
        max_tokens=int(os.getenv("MAX_TOKENS", "500")),
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.get("content"):
            yield chunk.choices[0].delta.content

def analyze_emotion(text: str) -> dict:
    """Analyze emotional content of the text"""
    # Placeholder - would use Korean emotion model
    keywords = {
        "슬퍼": "sadness",
        "우울": "depression", 
        "기뻐": "joy",
        "화나": "anger",
        "불안": "anxiety",
        "외로워": "loneliness"
    }
    
    detected = "neutral"
    confidence = 0.5
    
    for korean, emotion in keywords.items():
        if korean in text:
            detected = emotion
            confidence = 0.8
            break
    
    # Check for Korean cultural emotions
    cultural_emotions = {
        "한": 0.0,
        "정": 0.0,
        "눈치": 0.0
    }
    
    if "그리움" in text or "서러움" in text:
        cultural_emotions["한"] = 0.7
    if "고마워" in text or "정들었" in text:
        cultural_emotions["정"] = 0.7
    if "미안" in text or "부담" in text:
        cultural_emotions["눈치"] = 0.6
    
    return {
        "primary": detected,
        "confidence": confidence,
        "cultural": cultural_emotions
    }

def calculate_safety_score(user_text: str, ai_response: str) -> float:
    """Calculate safety score for the interaction"""
    # Placeholder - would use safety model
    crisis_keywords = ["자살", "죽고싶", "죽을래", "자해"]
    
    for keyword in crisis_keywords:
        if keyword in user_text:
            return 0.2  # High risk
    
    return 0.95  # Safe

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)