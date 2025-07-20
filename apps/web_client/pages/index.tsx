import React, { useState, useEffect, useRef } from 'react';
import styled from '@emotion/styled';

const Container = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 40px;
  max-width: 600px;
  width: 100%;
  text-align: center;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
`;

const Title = styled.h1`
  font-size: 2.5rem;
  margin-bottom: 20px;
  font-weight: 700;
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  margin-bottom: 40px;
  opacity: 0.9;
`;

const MicButton = styled.button<{ isRecording: boolean }>`
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: none;
  background: ${props => props.isRecording ? '#ff4757' : '#48dbfb'};
  color: white;
  font-size: 3rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  
  &:hover {
    transform: scale(1.05);
  }
  
  &:active {
    transform: scale(0.95);
  }
`;

const Status = styled.div`
  margin-top: 30px;
  font-size: 1.1rem;
  opacity: 0.8;
`;

const Response = styled.div`
  margin-top: 30px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  text-align: left;
  max-height: 200px;
  overflow-y: auto;
`;

const LatencyBadge = styled.div`
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.3);
  padding: 10px 20px;
  border-radius: 25px;
  font-size: 0.9rem;
`;

export default function Home() {
  const [isRecording, setIsRecording] = useState(false);
  const [status, setStatus] = useState('안녕하세요! 마이크 버튼을 눌러 대화를 시작해주세요.');
  const [response, setResponse] = useState('');
  const [latency, setLatency] = useState<number | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Initialize WebSocket connection
    const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8080/ws');
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setResponse(data.response);
      setLatency(data.latency);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatus('연결 오류가 발생했습니다.');
    };
    
    wsRef.current = ws;
    
    return () => {
      ws.close();
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
          // Send audio data through WebSocket
          wsRef.current.send(event.data);
        }
      };
      
      mediaRecorder.start(100); // Send data every 100ms
      mediaRecorderRef.current = mediaRecorder;
      
      setIsRecording(true);
      setStatus('듣고 있습니다... 편하게 말씀해주세요.');
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setStatus('마이크 접근 권한이 필요합니다.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      mediaRecorderRef.current = null;
    }
    
    setIsRecording(false);
    setStatus('응답을 생성하고 있습니다...');
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <Container>
      <LatencyBadge>
        {latency ? `응답 시간: ${latency}ms` : '대기 중...'}
      </LatencyBadge>
      
      <Card>
        <Title>🎙️ Intune-Care</Title>
        <Subtitle>AI와 함께하는 마음 건강 상담</Subtitle>
        
        <MicButton 
          isRecording={isRecording}
          onClick={toggleRecording}
        >
          {isRecording ? '⏸️' : '🎤'}
        </MicButton>
        
        <Status>{status}</Status>
        
        {response && (
          <Response>
            <strong>AI 상담사:</strong> {response}
          </Response>
        )}
      </Card>
    </Container>
  );
}