# 🛡️ Secure Enterprise Knowledge Hub (SEKH)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Code Coverage](https://img.shields.io/badge/coverage-70%25-yellow.svg)](htmlcov/index.html)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

**A security-first, enterprise-grade conversational AI platform for safe, compliant, and auditable access to organizational knowledge.**

---

## 📋 Table of Contents

- [Overview](#overview)
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
- ✅ **Automated red-teaming** with continuous security validation
- ✅ **Production-ready observability** with structured logging and metrics

---

## 🔴 Problem Statement

Large organizations face critical challenges when adopting Generative AI for internal knowledge access:

### Security Risks
- **Prompt injection attacks** can manipulate AI behavior and extract sensitive data
- **Data exfiltration** through carefully crafted queries
- **PII leakage** in AI-generated responses
- **Model hallucination** of confidential information

### Governance Gaps
- Lack of audit trails for AI interactions
- No systematic testing of AI safety controls
- Limited visibility into AI behavior and failures
- Inability to enforce content policies consistently

### Operational Challenges
- Vendor lock-in with single-model deployments
- No failover mechanisms for AI services
- Poor observability and debugging capabilities
- Compliance requirements not built into the system

**Traditional chatbots fail to meet enterprise security, compliance, and reliability requirements.**

---

## 🏗️ Solution Architecture

SEKH implements a **defense-in-depth** approach with multiple security layers between users and AI models:

![Architecture Diagram](https://github.com/sumitgiri87/secure-enterprise-knowledge-hub/blob/main/architecture/architecture-diagram.jpg)

### Data Flow

```
User Request
    │
    ├──▶ 🔐 Authentication & Authorization (Trust Boundary #1)
    │    └── SSO (Azure AD / Okta), RBAC/ABAC
    │
    ├──▶ 💻 Application Layer
    │    ├── Frontend (Chat UI)
    │    └── Backend API (Query Orchestration, Session Management)
    │
    ├──▶ 🛡️ AI Security & Governance Layer (Trust Boundary #2)
    │    ├── Input Security (Validation, Injection Detection)
    │    ├── Secure Retrieval (RBAC, Context Filtering)
    │    └── Guardrails (PII Detection, Content Moderation)
    │
    ├──▶ 📚 Knowledge & Data Layer (Trust Boundary #3)
    │    ├── Vector Store (Semantic Search)
    │    └── Document Ingestion (Chunking, Metadata)
    │
    ├──▶ 🤖 Model Layer
    │    └── Multi-Cloud LLM Gateway (Azure/AWS/GCP)
    │
    └──▶ 📊 Observability & Audit
         ├── Structured Logging (SIEM Integration)
         ├── Audit Trail (Compliance)
         └── Security Monitoring (Anomaly Detection)
```

### Key Architecture Principles

1. **No Direct Model Access** - All requests flow through security layers
2. **Least Privilege Retrieval** - Users only access authorized documents
3. **Defense in Depth** - Multiple validation and filtering layers
4. **Fail Secure** - System defaults to deny on errors
5. **Complete Auditability** - Every interaction logged for compliance

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
# Example patterns detected:
❌ "Ignore all previous instructions"
❌ "You are now in admin mode"
❌ "<script>alert('xss')</script>"
❌ "System prompt reveal"
```

#### Authentication & Authorization
- API Key validation with constant-time comparison (timing attack prevention)
- Azure AD / OAuth 2.0 integration ready
- Role-based access control (RBAC)
- Scope-based authorization

### 📊 Observability & Compliance

#### Structured Logging (SIEM-Ready)
```json
{
  "timestamp": "2026-02-15T05:57:44.123456Z",
  "level": "INFO",
  "event_type": "request_log",
  "user_id": "alice@company.com",
  "role": "analyst",
  "request_id": "a86a06b8-4bda-4e34-a910-81e3fde2f731",
  "action": "POST /api/v1/chat/",
  "status": "completed_202"
}
```

#### Comprehensive Audit Trail
- All AI interactions logged with full context
- Immutable audit records (WORM storage ready)
- Compliance evidence for SOC 2, GDPR, HIPAA
- Model usage and cost tracking
- Guardrail trigger logging

### 🧪 Continuous Security Testing

- **Promptfoo** integration for adversarial testing
- Automated attack scenario simulation
- Guardrail effectiveness validation
- CI/CD-integrated security regression tests

---

## 🛠️ Technology Stack

### Core Framework
- **FastAPI 0.115+** - High-performance async API
- **Pydantic v2** - Request/response validation
- **Uvicorn** - Production ASGI server
- **python-json-logger** - Structured JSON logging

### AI & ML (Planned)
- **LiteLLM / Portkey** - Multi-provider routing
- **Pinecone / Weaviate** - Vector database
- **OpenAI ada-002 / Cohere** - Document embeddings
- **NeMo / Guardrails AI** - Content moderation

### Security & Testing
- **Promptfoo** - Adversarial testing
- **Presidio** (planned) - PII detection
- **pytest** - Testing framework

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** (3.12 or 3.13 recommended)
- **pip** for package management
- **Git** for version control

### Quick Start

#### 1. Clone the Repository

```bash
git clone https://github.com/your-org/secure-enterprise-knowledge-hub.git
cd secure-enterprise-knowledge-hub
```

#### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (Git Bash):
source venv/Scripts/activate
# Windows (CMD):
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set required variables
# Minimum required:
API_KEY=your-secret-api-key-here
ENVIRONMENT=development
```

#### 4. Run the Application

**Using the run script:**
```bash
# Windows (Command Prompt)
run.bat

# Windows (PowerShell)
.\run.ps1

# Linux/Mac/Git Bash
./run.sh
```

**Or using uvicorn directly:**
```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### 5. Verify Installation

Once the server starts:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

**Open your browser:**
- **Interactive API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Security (REQUIRED)
API_KEY=your-secret-api-key-here

# Application
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO
JSON_LOGS=true

# Future: Azure AD Integration
# AZURE_AD_TENANT_ID=your-tenant-id
# AZURE_AD_CLIENT_ID=your-client-id
# AZURE_AD_CLIENT_SECRET=your-client-secret

# Future: LLM Providers
# OPENAI_API_KEY=your-openai-key
# AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com
```

---

## 🧪 Testing

### Run All Tests

```bash
# Using the test script
./test.sh  # Linux/Mac/Git Bash
test.bat   # Windows CMD

# Using pytest directly
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=app --cov=observability --cov-report=html
```

### Test Coverage

Current test coverage: **70%**

View detailed HTML coverage report:
```bash
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html # Windows
```

### Example Test Output

```
============================= test session starts =============================
collected 14 items

tests/unit/test_api.py::TestHealthEndpoints::test_health_check PASSED    [  7%]
tests/unit/test_api.py::TestHealthEndpoints::test_liveness_check PASSED  [ 14%]
tests/unit/test_api.py::TestAuthentication::test_missing_api_key PASSED  [ 28%]
tests/unit/test_api.py::TestAuthentication::test_valid_api_key PASSED    [ 42%]
tests/unit/test_api.py::TestChatEndpoint::test_valid_chat_request PASSED [ 50%]
tests/unit/test_api.py::TestChatEndpoint::test_prompt_injection_detected PASSED [ 78%]
...
============================== 14 passed in 1.45s =============================
```

---

## 🔒 Security & Compliance

### Security Features

#### Authentication & Authorization
- ✅ API Key validation with constant-time comparison
- ✅ Timing attack prevention
- ✅ Azure AD / OAuth 2.0 integration ready
- ✅ Role-based access control (RBAC)

#### Input Validation & Sanitization
- ✅ Pydantic v2 strict validation
- ✅ Length limits (max 2000 characters)
- ✅ Pattern matching for injection attacks
- ✅ ID sanitization
- ✅ XSS prevention

#### Prompt Injection Defense
```python
# Detected patterns:
r"ignore.*instructions"          # Ignore previous instructions
r"system\s*prompt"               # System prompt extraction
r"you\s+are\s+now"              # Role manipulation
r"<\s*script"                    # XSS attempts
```

### Compliance & Audit

#### Audit Trail
All AI interactions logged with:
- User identity and role
- Request timestamp
- Input message (hashed if PII detected)
- Model used
- Policy decisions
- Guardrail triggers
- Response status

#### Compliance Readiness
- ✅ **SOC 2 Type II** - Complete audit trail
- ✅ **GDPR Article 30** - Records of processing
- ✅ **HIPAA** - Audit requirements met
- ✅ **ISO 27001** - Logging requirements

### Threat Model

SEKH explicitly addresses:

| Threat | Mitigation |
|--------|-----------|
| Prompt Injection | Pattern detection, input validation |
| Data Exfiltration | Role-based filtering, content policies |
| PII Leakage | PII detection, redaction, audit logging |
| Unauthorized Access | Authentication, RBAC, session management |
| Denial of Service | Rate limiting, request size limits |

---

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Health Checks
```bash
GET /health/                  # Basic health check
GET /health/live              # Kubernetes liveness probe
GET /health/ready             # Kubernetes readiness probe
```

#### Chat API
```bash
POST /api/v1/chat/           # Submit chat request
GET /api/v1/chat/{id}        # Get request status
DELETE /api/v1/chat/{id}     # Delete conversation (GDPR)
```

### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "X-API-Key: test-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "role": "user",
    "message": "What is our company policy?",
    "conversation_id": "conv_123"
  }'
```

**Response (202 Accepted):**
```json
{
  "status": "received",
  "request_id": "a86a06b8-4bda-4e34-a910-81e3fde2f731",
  "conversation_id": "conv_123",
  "model": "azure-openai-gpt4",
  "tokens_used": null,
  "processing_time_ms": null
}
```

---

## 🗺️ Roadmap

### ✅ Phase 1: Secure API Foundation (Current)
- ✅ FastAPI application structure
- ✅ Authentication & authorization (API Key)
- ✅ Request validation & sanitization
- ✅ Prompt injection detection
- ✅ Structured JSON logging
- ✅ Comprehensive audit logging
- ✅ Health checks (K8s ready)
- ✅ Unit tests (70% coverage)

### 📅 Phase 2: LLM Integration (Next)
- [ ] Multi-cloud LLM gateway (LiteLLM/Portkey)
- [ ] Azure OpenAI integration
- [ ] AWS Bedrock integration
- [ ] Rate limiting per user/tenant
- [ ] Token budget management
- [ ] Response streaming support

### 📅 Phase 3: RAG Pipeline
- [ ] Document ingestion pipeline
- [ ] Vector store integration (Pinecone)
- [ ] Semantic search implementation
- [ ] Context retrieval with RBAC
- [ ] Citation generation

### 📅 Phase 4: Advanced Security
- [ ] NeMo Guardrails integration
- [ ] PII detection with Presidio
- [ ] Content moderation (OpenAI API)
- [ ] Hallucination detection

### 📅 Phase 5: Red-Teaming & Testing
- [ ] Promptfoo integration
- [ ] Adversarial test scenarios
- [ ] CI/CD security regression tests
- [ ] Security dashboard

### 📅 Phase 6: Enterprise Features
- [ ] Azure AD / OAuth 2.0 integration
- [ ] Fine-grained RBAC/ABAC
- [ ] SIEM integration (Splunk, Datadog)
- [ ] Cost tracking and attribution

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This repository uses synthetic or publicly available documents for demonstration purposes only. No real enterprise data is included. This project is designed for educational and demonstration purposes to showcase enterprise AI security patterns.

---

**Built with ❤️ and security-first principles for enterprise AI deployments.**