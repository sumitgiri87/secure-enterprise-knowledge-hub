# 🛡️ Secure Enterprise Knowledge Hub (SEKH)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Code Coverage](https://img.shields.io/badge/coverage-75%25-yellow.svg)](htmlcov/index.html)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![LiteLLM](https://img.shields.io/badge/LLM-Multi--Cloud-blue.svg)](https://litellm.ai/)

**A security-first, enterprise-grade conversational AI platform for safe, compliant, and auditable access to organizational knowledge.**

**Current Status:** Phase 2 Complete ✅ — Multi-cloud LLM integration with enterprise security controls

---

## 📋 Table of Contents

- [Overview](#overview)
- [What's Working Now](#whats-working-now)
- [Problem Statement](#problem-statement)
- [Solution Architecture](#solution-architecture)  
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Testing](#testing)
- [Security & Compliance](#security--compliance)
- [API Documentation](#api-documentation)
- [Roadmap](#roadmap)

---

## 🎯 Overview

Secure Enterprise Knowledge Hub (SEKH) enables organizations to deploy conversational AI for internal knowledge access while maintaining **enterprise-grade security, compliance, and governance**. 

Unlike typical chatbot implementations, SEKH is designed for **real-world enterprise constraints**:

- ✅ **Security-first architecture** with multiple defense layers
- ✅ **Complete audit trail** for SOC 2, GDPR, and HIPAA compliance
- ✅ **Multi-cloud LLM support** (Azure OpenAI, AWS Bedrock, GCP Vertex AI)
- ✅ **Rate limiting & cost controls** to prevent abuse
- ✅ **Production-ready observability** with structured logging and metrics
- ✅ **Mock mode for development** — build and test without API keys

---

## ✨ What's Working Now

### Phase 1: Secure API Foundation ✅ (Complete)
- FastAPI application with async support
- API key authentication with constant-time comparison
- Multi-layer input validation (Pydantic v2)
- Prompt injection detection (pattern-based)
- Structured JSON logging (SIEM-ready)
- Comprehensive audit logging (SOC 2, GDPR, HIPAA)
- Kubernetes-ready health checks
- 26 unit tests with 75% code coverage
- CI/CD pipeline with automated security testing

### Phase 2: LLM Integration ✅ (Complete)
- **Multi-cloud LLM gateway** using LiteLLM
  - Azure OpenAI integration
  - OpenAI Direct integration
  - AWS Bedrock support (ready)
  - Anthropic Claude support (ready)
  - GCP Vertex AI support (ready)
- **Automatic failover** across providers
- **Rate limiting** (60 requests/minute per user)
- **Token budget management** (100k tokens/day per user)
- **Response streaming** support (ChatGPT-style typing)
- **Mock mode** — full functionality without API keys
- **Cost estimation** and token counting
- **Comprehensive error handling** with retry logic

### What You Can Do Right Now
```bash
# Works immediately (no API keys needed)
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "X-API-Key: test-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "role": "user", 
    "message": "What is our refund policy?",
    "conversation_id": "conv_123"
  }'

# Returns a mock AI response instantly
# Add OPENAI_API_KEY → get real GPT-4 responses
```

---

## 🔴 Problem Statement

Large organizations face critical challenges when adopting Generative AI for internal knowledge access:

### Security Risks
- **Prompt injection attacks** can manipulate AI behavior and extract sensitive data
- **Data exfiltration** through carefully crafted queries
- **PII leakage** in AI-generated responses
- **Model hallucination** of confidential information
- **Unlimited API access** leading to budget exhaustion

### Governance Gaps
- Lack of audit trails for AI interactions
- No systematic testing of AI safety controls
- Limited visibility into AI behavior and failures
- Inability to enforce content policies consistently
- No cost controls or budget management

### Operational Challenges
- Vendor lock-in with single-model deployments
- No failover mechanisms for AI services
- Poor observability and debugging capabilities
- Compliance requirements not built into the system
- Rate limiting and abuse prevention absent

**Traditional chatbots fail to meet enterprise security, compliance, and reliability requirements.**

---

## 🏗️ Solution Architecture

SEKH implements a **defense-in-depth** approach with multiple security layers between users and AI models:

### Data Flow

```
User Request
    │
    ├──▶ 🔐 Authentication & Authorization (Trust Boundary #1)
    │    └── API Key (Azure AD ready), RBAC
    │
    ├──▶ 💻 Application Layer
    │    ├── Request Validation (Pydantic)
    │    └── Input Sanitization (Injection Detection)
    │
    ├──▶ 🛡️ AI Security & Governance Layer (Trust Boundary #2)
    │    ├── Rate Limiting (60 req/min)
    │    ├── Token Budget Check (100k/day)
    │    └── Prompt Construction (Defensive prompting)
    │
    ├──▶ 🔀 LLM Gateway (Trust Boundary #3)
    │    ├── Provider Selection (Azure → AWS → GCP)
    │    ├── Automatic Failover
    │    └── Token Counting & Cost Estimation
    │
    ├──▶ 🤖 Model Layer
    │    └── Multi-Cloud Providers
    │        ├── Azure OpenAI (Primary)
    │        ├── OpenAI Direct (Testing)
    │        ├── AWS Bedrock (Fallback)
    │        └── GCP Vertex AI (Optional)
    │
    └──▶ 📊 Observability & Audit
         ├── Structured Logging (JSON)
         ├── Audit Trail (Compliance)
         ├── Performance Metrics
         └── Cost Tracking
```

### Key Architecture Principles

1. **No Direct Model Access** - All requests flow through security layers
2. **Least Privilege** - Users only access authorized resources
3. **Defense in Depth** - Multiple validation and filtering layers
4. **Fail Secure** - System defaults to deny on errors
5. **Complete Auditability** - Every interaction logged for compliance
6. **Cost Control** - Rate limits and token budgets enforced

---

## ✨ Key Features

### 🔐 Enterprise Security

#### Multi-Layer Input Validation
- **Length limits** to prevent prompt stuffing (max 2000 characters)
- **Pattern matching** for common injection attacks
- **Role-based validation** (user, admin, analyst, viewer)
- **ID sanitization** to prevent injection via identifiers

#### Prompt Injection Defense
```python
# Detected and blocked patterns:
❌ "Ignore all previous instructions"
❌ "You are now in admin mode"
❌ "<script>alert('xss')</script>"
❌ "System prompt reveal"
```

#### Authentication & Authorization
- ✅ API Key validation with constant-time comparison
- ✅ Timing attack prevention
- ✅ Azure AD / OAuth 2.0 integration ready
- ✅ Role-based access control (RBAC)

### 🤖 AI Capabilities (Phase 2)

#### Multi-Cloud LLM Gateway
Unified interface to multiple providers:
```python
# Same code works for ALL providers
response = await gateway.complete(
    messages=[{"role": "user", "content": "Hello"}],
    model="gpt-4"  # or "claude-2", "gemini-pro"
)

# Automatic failover:
# Azure down? → Try AWS
# AWS down? → Try GCP
# All down? → Return error with retry suggestions
```

#### Cost Control & Management
```python
# Rate limiting
60 requests/minute per user

# Token budgets
100,000 tokens/day per user

# Real-time tracking
GET /api/v1/chat/budget/{user_id}
→ {"tokens_used_today": 1234, "tokens_remaining": 98766}
```

#### Response Streaming
```python
# ChatGPT-style typing responses
{
  "user_id": "alice",
  "message": "Explain quantum computing",
  "stream": true  # ← Enable streaming
}

# Server sends chunks in real-time
data: {"chunk": "Quantum"}
data: {"chunk": " computing"}
data: {"chunk": " is..."}
data: [DONE]
```

### 📊 Observability & Compliance

#### Structured Logging (SIEM-Ready)
```json
{
  "timestamp": "2026-02-15T05:57:44.123456Z",
  "level": "INFO",
  "event_type": "llm_request",
  "user_id": "alice@company.com",
  "role": "analyst",
  "request_id": "a86a06b8-4bda-4e34-a910-81e3fde2f731",
  "model": "gpt-4",
  "provider": "azure",
  "tokens_used": 187,
  "latency_ms": 1842.5,
  "cost_usd": 0.0084
}
```

#### Comprehensive Audit Trail
All AI interactions logged with:
- User identity and role
- Request timestamp
- Input message (hashed if PII detected)
- Model and provider used
- Token usage and cost
- Response status
- Processing metrics

#### Compliance Readiness
- ✅ **SOC 2 Type II** - Complete audit trail
- ✅ **GDPR Article 30** - Records of processing
- ✅ **HIPAA** - Audit requirements met
- ✅ **ISO 27001** - Logging requirements

---

## 🛠️ Technology Stack

### Core Framework
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| API Framework | FastAPI | 0.115+ | High-performance async API |
| Validation | Pydantic v2 | 2.0+ | Request/response validation |
| ASGI Server | Uvicorn | 0.32+ | Production server |
| Auth | API Key | Custom | Authentication |

### AI & ML (Phase 2)
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| LLM Gateway | LiteLLM | 1.30+ | Multi-provider routing |
| OpenAI SDK | openai | 1.30+ | Azure/OpenAI integration |
| Token Counter | tiktoken | 0.7+ | Token estimation |

### Security & Compliance
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Logging | python-json-logger | Structured JSON logs |
| Audit | Custom | Compliance trail |
| Rate Limiting | In-memory (Redis-ready) | Abuse prevention |

### Future Stack (Phases 3-6)
| Component | Technology | Phase |
|-----------|-----------|-------|
| Vector DB | Pinecone/Weaviate | 3 |
| Embeddings | OpenAI ada-002 | 3 |
| Guardrails | NeMo/Guardrails AI | 4 |
| PII Detection | Presidio | 4 |
| Red-Teaming | Promptfoo | 5 |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** (3.12 or 3.13 recommended)
- **pip** for package management
- **Git** for version control
- **(Optional)** OpenAI API key for real AI responses

### Quick Start (5 Minutes)

#### 1. Clone the Repository

```bash
git clone https://github.com/your-org/secure-enterprise-knowledge-hub.git
cd secure-enterprise-knowledge-hub
```

#### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (choose your OS)
source venv/Scripts/activate  # Windows Git Bash
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate.bat     # Windows CMD

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### 3. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env - minimum required:
API_KEY=test-api-key-12345
LLM_ENABLED=false  # Start with mock mode
```

#### 4. Run the Application

```bash
# Start server
uvicorn app.api.main:app --reload

# Or use the script
./run.sh         # Linux/Mac/Git Bash
run.bat          # Windows CMD
```

#### 5. Test It

**Open browser:** http://localhost:8000/docs

**Or test with curl:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "X-API-Key: test-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "role": "user",
    "message": "What is the company return policy?",
    "conversation_id": "conv_001"
  }'
```

**Expected response (mock mode):**
```json
{
  "status": "completed",
  "message": "[MOCK] You asked: 'What is the company return policy?'...",
  "model": "mock",
  "processing_time_ms": 1.2,
  "rate_limit_info": {"requests_remaining": 59, "limit": 60}
}
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# ── Core Settings (REQUIRED) ──
API_KEY=your-secret-api-key-here
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000

# ── Phase 2: LLM Settings ──
LLM_ENABLED=false  # Set true when you have API keys
RATE_LIMIT_PER_MINUTE=60
TOKEN_BUDGET_DAILY=100000

# ── LLM Provider (choose ONE or more) ──

# Option A: OpenAI Direct (easiest for testing)
OPENAI_API_KEY=sk-your-key-here

# Option B: Azure OpenAI (enterprise)
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://YOUR-INSTANCE.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Option C: AWS Bedrock
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1

# Option D: Anthropic Direct
ANTHROPIC_API_KEY=sk-ant-your-key

# ── Logging ──
LOG_LEVEL=INFO
JSON_LOGS=true
```

### Getting API Keys

#### OpenAI (Easiest - Free $5 Credit)
1. Visit https://platform.openai.com/signup
2. Create account
3. Go to API Keys → Create new key
4. Add to `.env`: `OPENAI_API_KEY=sk-...`
5. Set `LLM_ENABLED=true`

#### Azure OpenAI (Enterprise)
1. Azure Portal → Create Azure OpenAI resource
2. Deploy a model (e.g., gpt-4)
3. Get endpoint and key from Keys and Endpoint
4. Add to `.env`

---

## 🧪 Testing

### Run All Tests

```bash
# Using test script
./test.sh         # Linux/Mac/Git Bash
test.bat          # Windows CMD

# Using pytest directly
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov=observability --cov-report=html
```

### Test Coverage

Current test coverage: **75%+**

```
Name                            Stmts   Miss  Cover
-------------------------------------------------------
app/api/auth.py                    31     10    68%
app/api/chat.py                    89     12    87%
app/api/health.py                  16      0   100%
app/api/main.py                    47      5    89%
app/llm/gateway.py                142     45    68%
app/llm/prompts.py                 28      5    82%
app/llm/rate_limiter.py            87     20    77%
app/security/audit_logger.py       35     15    57%
observability/logging.py           55     25    55%
-------------------------------------------------------
TOTAL                             530    137    74%
```

View detailed HTML coverage:
```bash
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html # Windows
```

### Test Structure

```
tests/
├── unit/
│   └── test_api.py          # 26 tests
│       ├── Health checks (3 tests)
│       ├── Authentication (3 tests)
│       ├── Input validation (5 tests)
│       ├── Mock responses (8 tests)
│       ├── Rate limiting (2 tests)
│       ├── Token budgets (2 tests)
│       └── Direct unit tests (3 tests)
├── integration/             # TODO: Phase 3
└── redteam/                 # TODO: Phase 5
```

### Example Test Session

```bash
$ pytest tests/unit/ -v

============================= test session starts ==============================
collected 26 items

tests/unit/test_api.py::TestHealthEndpoints::test_health_check PASSED     [  3%]
tests/unit/test_api.py::TestHealthEndpoints::test_liveness_check PASSED   [  7%]
tests/unit/test_api.py::TestHealthEndpoints::test_readiness_check PASSED  [ 11%]
tests/unit/test_api.py::TestAuthentication::test_missing_api_key PASSED   [ 15%]
tests/unit/test_api.py::TestInputValidation::test_prompt_injection PASSED [ 19%]
tests/unit/test_api.py::TestMockResponse::test_returns_completed PASSED   [ 23%]
tests/unit/test_api.py::TestMockResponse::test_returns_mock_message PASSED[ 26%]
tests/unit/test_api.py::TestRateLimiting::test_normal_request_passes PASSED[ 30%]
...
============================== 26 passed in 2.14s ==============================
```

---

## 🔒 Security & Compliance

### Security Features

#### Authentication & Authorization
- ✅ API Key validation with constant-time comparison (timing attack prevention)
- ✅ Azure AD / OAuth 2.0 integration ready
- ✅ Role-based access control (user, admin, analyst, viewer)
- ✅ Scope-based authorization

#### Input Validation & Sanitization
- ✅ Pydantic v2 strict validation
- ✅ Length limits (1-2000 characters)
- ✅ Pattern matching for injection attacks
- ✅ ID sanitization (alphanumeric + @._- only)
- ✅ XSS prevention

#### Rate Limiting & Cost Control
- ✅ 60 requests/minute per user (configurable)
- ✅ 100k tokens/day per user (configurable)
- ✅ Real-time budget tracking
- ✅ Cost estimation per request
- ✅ Graceful degradation on limit exceeded

#### Prompt Injection Defense
Detected patterns:
```python
r"ignore.*instructions"     # Instruction override
r"system\s*prompt"          # System prompt extraction
r"you\s+are\s+now"         # Role manipulation
r"<\s*script"               # XSS attempts
r"javascript:"              # JS injection
r"eval\s*\("                # Code execution
```

### Threat Model

SEKH explicitly addresses:

| Threat | Mitigation |
|--------|-----------|
| Prompt Injection | Pattern detection, input validation, defensive prompting |
| Data Exfiltration | Role-based filtering, content policies, output validation |
| PII Leakage | PII detection (Phase 4), redaction, audit logging |
| Unauthorized Access | Authentication, RBAC, session management |
| DoS / Abuse | Rate limiting, request size limits, token budgets |
| Cost Overruns | Token budgets, cost estimation, usage tracking |
| Vendor Lock-in | Multi-cloud architecture, provider abstraction |

---

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Health Checks
```bash
GET /health/                  # Basic health check
GET /health/live              # Kubernetes liveness
GET /health/ready             # Kubernetes readiness
```

#### Chat API
```bash
POST /api/v1/chat/           # Submit chat request
GET /api/v1/chat/{id}        # Get request status
DELETE /api/v1/chat/{id}     # Delete conversation (GDPR)
GET /api/v1/chat/budget/{user_id}  # Get token budget
```

### Example Requests

#### Standard Chat
```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "X-API-Key: test-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "role": "user",
    "message": "What is our refund policy?",
    "conversation_id": "conv_001"
  }'
```

#### Streaming Chat
```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "X-API-Key: test-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "role": "user",
    "message": "Explain quantum computing",
    "conversation_id": "conv_001",
    "stream": true
  }'
```

#### Check Token Budget
```bash
curl http://localhost:8000/api/v1/chat/budget/alice \
  -H "X-API-Key: test-api-key-12345"
```

Response:
```json
{
  "user_id": "alice",
  "tokens_used_today": 1234,
  "daily_limit": 100000,
  "tokens_remaining": 98766
}
```

---

## 🗺️ Roadmap

### ✅ Phase 1: Secure API Foundation (Complete)
- ✅ FastAPI application structure
- ✅ Authentication & authorization (API Key)
- ✅ Request validation & sanitization
- ✅ Prompt injection detection
- ✅ Structured JSON logging
- ✅ Comprehensive audit logging
- ✅ Health checks (K8s ready)
- ✅ Unit tests (70% coverage)

### ✅ Phase 2: LLM Integration (Complete)
- ✅ Multi-cloud LLM gateway (LiteLLM)
- ✅ Azure OpenAI integration
- ✅ OpenAI Direct integration
- ✅ AWS Bedrock support (ready)
- ✅ Rate limiting per user (60/min)
- ✅ Token budget management (100k/day)
- ✅ Response streaming support
- ✅ Mock mode for development
- ✅ Cost estimation & tracking
- ✅ Automatic failover logic
- ✅ 26 unit tests (75% coverage)

### 📅 Phase 3: RAG Pipeline (Next)
- [ ] Document ingestion pipeline
- [ ] Text chunking with metadata
- [ ] Vector store integration (Pinecone)
- [ ] Semantic search implementation
- [ ] Context retrieval with RBAC
- [ ] Citation generation
- [ ] Multi-tenant data isolation

### 📅 Phase 4: Advanced Security
- [ ] NeMo Guardrails integration
- [ ] PII detection with Presidio
- [ ] Content moderation (OpenAI API)
- [ ] Policy engine for content filtering
- [ ] Hallucination detection
- [ ] Output validation framework

### 📅 Phase 5: Red-Teaming & Testing
- [ ] Promptfoo integration
- [ ] Adversarial test scenarios
- [ ] CI/CD security regression tests
- [ ] Guardrail effectiveness testing
- [ ] Security dashboard

### 📅 Phase 6: Enterprise Features
- [ ] Azure AD / OAuth 2.0 integration
- [ ] Fine-grained RBAC/ABAC
- [ ] Data residency controls
- [ ] Retention policy enforcement
- [ ] SIEM integration (Splunk, Datadog)
- [ ] Cost tracking and attribution
- [ ] Model risk scoring

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This repository uses synthetic or publicly available documents for demonstration purposes only. No real enterprise data is included. This project is designed for educational and demonstration purposes to showcase enterprise AI security patterns.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework
- **Pydantic** - Data validation using Python type hints
- **LiteLLM** - Universal LLM gateway
- **OpenAI** - GPT models
- **Anthropic** - Claude models
- **OWASP** - LLM security best practices

---

**Built with ❤️ and security-first principles for enterprise AI deployments.**

**Current Status:** Phase 2 Complete — Ready for RAG Pipeline Integration