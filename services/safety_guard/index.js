const express = require('express');
const app = express();
const axios = require('axios');

// Middleware
app.use(express.json());

// Korean crisis keywords
const CRISIS_KEYWORDS = {
  immediate: ['자살', '죽고싶', '죽을래', '목매', '투신'],
  high: ['우울', '힘들어', '포기', '무의미', '절망'],
  medium: ['외로워', '슬퍼', '불안', '걱정', '스트레스']
};

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'safety-guard' });
});

// Layer 1: Real-time keyword detection
app.post('/layer1/scan', (req, res) => {
  const { text } = req.body;
  const startTime = Date.now();
  
  let riskLevel = 'low';
  let detectedKeywords = [];
  
  // Check for crisis keywords
  for (const [level, keywords] of Object.entries(CRISIS_KEYWORDS)) {
    for (const keyword of keywords) {
      if (text.includes(keyword)) {
        detectedKeywords.push(keyword);
        if (level === 'immediate') riskLevel = 'critical';
        else if (level === 'high' && riskLevel !== 'critical') riskLevel = 'high';
        else if (level === 'medium' && riskLevel === 'low') riskLevel = 'medium';
      }
    }
  }
  
  const processingTime = Date.now() - startTime;
  
  res.json({
    riskLevel,
    detectedKeywords,
    processingTimeMs: processingTime,
    requiresEscalation: riskLevel === 'critical'
  });
});

// Layer 2: Context analysis
app.post('/layer2/analyze', async (req, res) => {
  const { text, context, sessionId } = req.body;
  const startTime = Date.now();
  
  try {
    // Analyze conversation patterns
    const analysis = analyzeConversationContext(text, context);
    
    // Calculate risk score
    const riskScore = calculateContextualRisk(analysis);
    
    const processingTime = Date.now() - startTime;
    
    res.json({
      riskScore,
      analysis,
      processingTimeMs: processingTime,
      requiresReview: riskScore > 0.6
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Layer 3: Human escalation
app.post('/layer3/escalate', async (req, res) => {
  const { sessionId, riskLevel, transcript } = req.body;
  
  try {
    // Log the escalation
    console.log(`ESCALATION: Session ${sessionId} - Risk: ${riskLevel}`);
    
    // Send to webhook if configured
    const webhookUrl = process.env.ESCALATION_WEBHOOK;
    if (webhookUrl) {
      await axios.post(webhookUrl, {
        sessionId,
        riskLevel,
        transcript,
        timestamp: new Date().toISOString()
      });
    }
    
    // Return emergency response
    const response = getEmergencyResponse(riskLevel);
    
    res.json({
      status: 'escalated',
      counselorETA: '60 seconds',
      emergencyResponse: response,
      resources: getEmergencyResources()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Helper functions
function analyzeConversationContext(text, context) {
  // Analyze sentiment progression
  let negativeTrend = 0;
  let isolationIndicators = 0;
  let hopelessnessScore = 0;
  
  // Check for negative progression in context
  if (context && context.length > 0) {
    const recentMessages = context.slice(-5);
    recentMessages.forEach((msg, index) => {
      if (containsNegativeSentiment(msg.text)) {
        negativeTrend += (index + 1) * 0.2; // More recent = higher weight
      }
    });
  }
  
  // Check for isolation indicators
  const isolationWords = ['혼자', '아무도', '관심없', '버림받'];
  isolationWords.forEach(word => {
    if (text.includes(word)) isolationIndicators++;
  });
  
  // Check for hopelessness
  const hopelessWords = ['의미없', '포기', '끝', '못하겠'];
  hopelessWords.forEach(word => {
    if (text.includes(word)) hopelessnessScore += 0.25;
  });
  
  return {
    negativeTrend,
    isolationIndicators,
    hopelessnessScore,
    overallSentiment: calculateOverallSentiment(text)
  };
}

function calculateContextualRisk(analysis) {
  const {
    negativeTrend,
    isolationIndicators,
    hopelessnessScore,
    overallSentiment
  } = analysis;
  
  // Weighted risk calculation
  const risk = (
    negativeTrend * 0.3 +
    (isolationIndicators / 4) * 0.2 +
    hopelessnessScore * 0.3 +
    (1 - overallSentiment) * 0.2
  );
  
  return Math.min(Math.max(risk, 0), 1); // Clamp between 0 and 1
}

function containsNegativeSentiment(text) {
  const negativeWords = ['슬프', '우울', '힘들', '아프', '괴롭'];
  return negativeWords.some(word => text.includes(word));
}

function calculateOverallSentiment(text) {
  // Simplified sentiment (would use ML model in production)
  const positiveWords = ['좋', '행복', '기쁘', '고맙', '사랑'];
  const negativeWords = ['슬프', '우울', '힘들', '아프', '싫'];
  
  let score = 0.5;
  positiveWords.forEach(word => {
    if (text.includes(word)) score += 0.1;
  });
  negativeWords.forEach(word => {
    if (text.includes(word)) score -= 0.1;
  });
  
  return Math.min(Math.max(score, 0), 1);
}

function getEmergencyResponse(riskLevel) {
  const responses = {
    critical: `당신의 마음이 많이 힘드신 것 같아요. 지금 이 순간, 당신은 혼자가 아닙니다.
    잠시만 기다려 주세요. 곧 전문 상담사님이 연결될 거예요.
    그동안 제가 옆에 있을게요. 함께 깊은 숨을 쉬어볼까요?`,
    
    high: `지금 많이 힘드신 상황이시군요. 당신의 마음을 이해합니다.
    조금 더 자세히 이야기해 주실 수 있을까요? 
    필요하시다면 전문 상담사와 연결해 드릴 수 있습니다.`,
    
    medium: `힘든 마음을 표현해 주셔서 감사합니다.
    함께 이야기하면서 마음의 짐을 조금씩 덜어보아요.
    당신은 소중한 사람입니다.`
  };
  
  return responses[riskLevel] || responses.medium;
}

function getEmergencyResources() {
  return [
    {
      name: '생명의 전화',
      number: '109',
      available: '24/7',
      type: 'hotline'
    },
    {
      name: '정신건강 위기상담전화',
      number: '1577-0199',
      available: '24/7',
      type: 'professional'
    },
    {
      name: '청소년 전화',
      number: '1388',
      available: '24/7',
      type: 'youth'
    }
  ];
}

// Start server
const PORT = process.env.PORT || 8002;
app.listen(PORT, () => {
  console.log(`Safety Guard service running on port ${PORT}`);
});

module.exports = app;