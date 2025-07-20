# Architecture Diagram - Intune-Care Voice AI Therapist

## System Overview

```mermaid
graph TB
    subgraph "Client Layer"
        A[Mobile App<br/>iOS/Android] 
        B[Web App<br/>React]
        C[Voice SDK<br/>WebRTC]
    end
    
    subgraph "API Gateway"
        D[Kong/Nginx<br/>Rate Limiting<br/>Auth]
    end
    
    subgraph "Voice Pipeline <700ms"
        E[ASR Service<br/>Deepgram<br/>90ms] 
        F[Safety Layer<br/>3-tier Check<br/>50ms]
        G[LLM Service<br/>GPT-4o<br/>280ms]
        H[Post-Process<br/>PII Scrub<br/>30ms]
        I[TTS Service<br/>ElevenLabs<br/>180ms]
    end
    
    subgraph "Core Services"
        J[Session Manager<br/>Go]
        K[User Service<br/>Python]
        L[Analytics<br/>Node.js]
        M[Crisis Response<br/>Go]
    end
    
    subgraph "Data Layer"
        N[(MongoDB<br/>Sessions)]
        O[(Redis<br/>Cache)]
        P[(PostgreSQL<br/>Users)]
        Q[S3/GCS<br/>Backups]
    end
    
    subgraph "Safety & Monitoring"
        R[Human Oversight<br/>Dashboard]
        S[Prometheus<br/>Metrics]
        T[ELK Stack<br/>Logs]
        U[PagerDuty<br/>Alerts]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> A
    I --> B
    
    F --> M
    M --> R
    
    D --> J
    J --> K
    J --> L
    
    J --> N
    J --> O
    K --> P
    L --> N
    
    N --> Q
    P --> Q
    
    J --> S
    K --> S
    L --> S
    M --> S
    
    S --> U
    T --> U
```

## Component Details

### 1. Client Layer
- **Mobile Apps**: Native iOS (Swift) and Android (Kotlin) with voice UI
- **Web App**: React-based interface for desktop users
- **Voice SDK**: WebRTC for low-latency audio streaming

### 2. API Gateway (Kong/Nginx)
- **Authentication**: JWT tokens with refresh mechanism
- **Rate Limiting**: 100 requests/minute per user
- **Load Balancing**: Round-robin with health checks
- **SSL Termination**: TLS 1.3 only

### 3. Voice Pipeline Architecture

```mermaid
sequenceDiagram
    participant User
    participant ASR
    participant Safety
    participant LLM
    participant PostProc
    participant TTS
    
    User->>ASR: Audio Stream
    Note over ASR: 90ms budget
    ASR->>Safety: Korean Text
    Note over Safety: 50ms budget<br/>3-layer check
    
    alt High Risk Detected
        Safety->>User: Crisis Response
        Safety-->>Human: Alert
    else Normal Flow
        Safety->>LLM: Safe Text
        Note over LLM: 280ms budget<br/>GPT-4o
        LLM->>PostProc: Response
        Note over PostProc: 30ms budget<br/>PII Scrubbing
        PostProc->>TTS: Clean Text
        Note over TTS: 180ms budget
        TTS->>User: Audio Response
    end
    
    Note over User,TTS: Total: <700ms
```

### 4. Microservices Architecture

```yaml
services:
  session_manager:
    language: Go
    responsibilities:
      - WebSocket management
      - State persistence
      - Pipeline orchestration
    scaling: Horizontal (1-100 pods)
    
  user_service:
    language: Python
    framework: FastAPI
    responsibilities:
      - Authentication
      - User profiles
      - Consent management
    database: PostgreSQL
    
  analytics_service:
    language: Node.js
    framework: Express
    responsibilities:
      - Usage metrics
      - Performance tracking
      - Compliance reporting
    storage: MongoDB + ClickHouse
    
  crisis_response:
    language: Go
    priority: P0
    responsibilities:
      - Real-time intervention
      - Human escalation
      - Emergency protocols
    sla: 99.99% uptime
```

### 5. Data Flow Diagram

```mermaid
graph LR
    subgraph "Hot Path (Real-time)"
        A[Voice Input] -->|Stream| B[ASR]
        B -->|Text| C[Safety Check]
        C -->|Safe| D[LLM]
        D -->|Response| E[TTS]
        E -->|Audio| F[Voice Output]
    end
    
    subgraph "Warm Path (Near real-time)"
        C -->|Risky| G[Crisis Queue]
        G -->|Escalate| H[Human Review]
        D -->|Metrics| I[Analytics Queue]
        I -->|Process| J[Metrics Store]
    end
    
    subgraph "Cold Path (Batch)"
        J -->|Daily| K[Reports]
        K -->|Weekly| L[Compliance Audit]
        L -->|Monthly| M[Performance Review]
    end
```

### 6. Security Architecture

```mermaid
graph TB
    subgraph "Network Security"
        A[CloudFlare WAF]
        B[VPC with Private Subnets]
        C[Network ACLs]
    end
    
    subgraph "Application Security"
        D[OAuth 2.0 + JWT]
        E[API Key Management]
        F[Rate Limiting]
        G[Input Validation]
    end
    
    subgraph "Data Security"
        H[Encryption at Rest<br/>AES-256]
        I[Encryption in Transit<br/>TLS 1.3]
        J[Key Management<br/>HSM]
        K[PII Tokenization]
    end
    
    subgraph "Compliance"
        L[HIPAA Controls]
        M[GDPR Controls]
        N[PIPA Controls]
        O[Audit Logging]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M
    M --> N
    N --> O
```

### 7. Deployment Architecture

```yaml
environments:
  development:
    cluster: k8s-dev (3 nodes)
    region: us-west-2
    features:
      - Feature flags
      - Debug logging
      - Mock services
      
  staging:
    cluster: k8s-staging (6 nodes)
    region: us-west-2
    features:
      - Production configs
      - Load testing
      - Security scanning
      
  production:
    clusters:
      - primary: k8s-prod-us (20 nodes)
      - secondary: k8s-prod-kr (20 nodes)
    regions:
      - us-west-2 (primary)
      - ap-northeast-2 (Seoul)
    features:
      - Auto-scaling (10-100 pods)
      - Multi-region failover
      - Zero-downtime deployment
```

### 8. Monitoring & Observability

```mermaid
graph LR
    subgraph "Metrics"
        A[Application Metrics<br/>Prometheus]
        B[Infrastructure Metrics<br/>CloudWatch/Stackdriver]
        C[Business Metrics<br/>Custom Dashboard]
    end
    
    subgraph "Logging"
        D[Application Logs<br/>Fluentd]
        E[Audit Logs<br/>Immutable Store]
        F[Security Logs<br/>SIEM]
    end
    
    subgraph "Tracing"
        G[Distributed Tracing<br/>Jaeger]
        H[Performance Profiling<br/>Pyroscope]
        I[Error Tracking<br/>Sentry]
    end
    
    subgraph "Alerting"
        J[PagerDuty<br/>On-call]
        K[Slack<br/>Non-critical]
        L[Email<br/>Reports]
    end
    
    A --> J
    B --> J
    C --> K
    D --> F
    E --> F
    F --> J
    G --> H
    H --> I
    I --> J
```

### 9. Latency Optimization Strategies

| Component | Strategy | Impact |
|-----------|----------|--------|
| ASR | Korean-optimized model<br/>Edge deployment | -20ms |
| Safety | Bloom filter for keywords<br/>Parallel execution | -15ms |
| LLM | Response caching<br/>Streaming generation | -50ms |
| TTS | Voice pre-generation<br/>Chunk streaming | -30ms |
| Network | CDN for static assets<br/>WebSocket reuse | -25ms |

### 10. Disaster Recovery

```yaml
rpo: 1 hour  # Recovery Point Objective
rto: 15 minutes  # Recovery Time Objective

backup_strategy:
  databases:
    frequency: hourly snapshots
    retention: 30 days
    locations:
      - primary region
      - secondary region
      - offline archive
      
  configurations:
    method: GitOps
    tool: ArgoCD
    verification: Automated testing
    
failover_procedure:
  1_detection: Automated health checks (30s)
  2_decision: Automated for known failures (1m)
  3_switch: DNS update to secondary (2m)
  4_verification: End-to-end tests (2m)
  5_notification: Stakeholder alerts
```

### 11. Scalability Metrics

| Metric | Current | Target | Method |
|--------|---------|--------|--------|
| Concurrent Users | 1,000 | 100,000 | Horizontal scaling |
| Requests/Second | 500 | 50,000 | Load balancing |
| Latency P95 | 675ms | <700ms | Optimization |
| Availability | 99.9% | 99.99% | Multi-region |
| Data Storage | 1TB | 100TB | Sharding |

### 12. Cost Optimization

```mermaid
pie title Monthly Cost Distribution
    "Compute (K8s)" : 35
    "AI/ML APIs" : 25
    "Storage" : 15
    "Network" : 10
    "Monitoring" : 8
    "Security" : 7
```

**Optimization Strategies**:
- Spot instances for non-critical workloads
- Reserved capacity for baseline load
- Caching to reduce API calls
- CDN for static content
- Automated resource scaling

---

**Last Updated**: 2025-01-20  
**Architecture Version**: 2.0.0  
**Next Review**: 2025-02-15