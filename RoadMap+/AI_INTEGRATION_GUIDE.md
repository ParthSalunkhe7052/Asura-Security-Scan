# 🤖 ASURA AI INTEGRATION GUIDE

## Overview
This guide covers all FREE AI model options for Asura's vulnerability analysis features.

---

## 🎯 AI Features in Asura

### 1. Vulnerability Explanation
**Input:** Vulnerability details (type, severity, code snippet)  
**Output:** Beginner-friendly explanation with real-world attack scenario

**Example:**
```
Input: SQL Injection in login.py:42
Output: "This code is vulnerable because user input is directly inserted 
into SQL queries. An attacker could type `' OR '1'='1` as the password 
to bypass authentication and access any account."
```

### 2. Secure Code Suggestion
**Input:** Vulnerable code snippet + context  
**Output:** Fixed version with inline comments explaining the changes

**Example:**
```python
# ❌ VULNERABLE
query = f"SELECT * FROM users WHERE username='{username}'"

# ✅ FIXED
query = "SELECT * FROM users WHERE username=?"
cursor.execute(query, (username,))  # Parameterized query prevents injection
```

### 3. Test Case Generation (Optional)
**Input:** Vulnerability details  
**Output:** Pytest test case to catch the vulnerability

---

## 🆓 FREE AI MODEL OPTIONS

### Option 1: Google Gemini Flash (RECOMMENDED)

#### Why Gemini Flash?
- ✅ **Generous free tier:** 15 requests/minute, 1500/day
- ✅ **Fast:** ~1-2 second response time
- ✅ **Good at code:** Trained on programming content
- ✅ **Easy API:** Simple REST interface
- ✅ **No credit card required**

#### Setup Steps

**1. Get API Key (Free)**
```
1. Visit https://aistudio.google.com/
2. Click "Get API Key"
3. Sign in with Google account
4. Copy your API key
```

**2. Install SDK**
```bash
pip install google-generativeai
```

**3. Code Implementation**
```python
# backend/app/services/ai_gemini.py
import google.generativeai as genai
import os

class GeminiAIService:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def explain_vulnerability(self, vulnerability: dict) -> str:
        prompt = f"""
        Explain this security vulnerability in simple terms:
        
        Type: {vulnerability['type']}
        Severity: {vulnerability['severity']}
        File: {vulnerability['file']}
        Line: {vulnerability['line']}
        Code:
        {vulnerability['code_snippet']}
        
        Provide:
        1. What this vulnerability means
        2. How an attacker could exploit it
        3. Real-world example of damage
        Keep it under 200 words, beginner-friendly.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def suggest_fix(self, vulnerability: dict) -> str:
        prompt = f"""
        Provide a secure code fix for this vulnerability:
        
        Type: {vulnerability['type']}
        Vulnerable Code:
        {vulnerability['code_snippet']}
        
        Return:
        1. Fixed code with inline comments
        2. Brief explanation of why it's secure now
        Format as Python code block.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
```

**4. Environment Variable**
```bash
# backend/.env
GEMINI_API_KEY=your_api_key_here
```

**5. Rate Limiting (Important!)**
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=15):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

# Usage
@rate_limit(calls_per_minute=14)  # Stay under 15/min limit
def call_gemini_api():
    # ...
```

#### Costs (As of Oct 2025)
- **Free tier:** 1500 requests/day
- **If you exceed:** $0.00015 per request (still very cheap)

---

### Option 2: Groq (Alternative)

#### Why Groq?
- ✅ **Blazing fast:** 500+ tokens/second
- ✅ **Free tier:** Very generous
- ✅ **Multiple models:** Llama 3.1, Mixtral
- ❌ Smaller context window than Gemini

#### Setup

**1. Get API Key**
```
1. Visit https://console.groq.com/
2. Sign up (free)
3. Create API key
```

**2. Install SDK**
```bash
pip install groq
```

**3. Code Implementation**
```python
# backend/app/services/ai_groq.py
from groq import Groq
import os

class GroqAIService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-70b-versatile"
    
    def explain_vulnerability(self, vulnerability: dict) -> str:
        prompt = # ... same as Gemini
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a security expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
```

---

### Option 3: Ollama (100% Offline)

#### Why Ollama?
- ✅ **Completely free:** No API limits
- ✅ **100% offline:** No internet needed
- ✅ **Privacy:** Data never leaves your machine
- ❌ Slower than API options
- ❌ Requires ~4GB disk space for model

#### Setup

**1. Install Ollama**
```bash
# Windows
winget install Ollama.Ollama

# Or download from https://ollama.com/download
```

**2. Pull Model**
```bash
ollama pull llama3.2:3b
# Or for better quality (but slower):
ollama pull codellama:13b
```

**3. Code Implementation**
```python
# backend/app/services/ai_ollama.py
import requests
import os

class OllamaAIService:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = "llama3.2:3b"
    
    def explain_vulnerability(self, vulnerability: dict) -> str:
        prompt = # ... same as Gemini
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        return response.json()["response"]
```

**4. Check if Ollama is Running**
```python
def is_ollama_available() -> bool:
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except:
        return False
```

---

## 🔄 MULTI-MODEL FALLBACK STRATEGY

Implement automatic fallback for reliability:

```python
# backend/app/services/ai_service.py
from app.services.ai_gemini import GeminiAIService
from app.services.ai_groq import GroqAIService
from app.services.ai_ollama import OllamaAIService
import os

class AIService:
    def __init__(self):
        self.providers = []
        
        # Try Gemini first (fastest + best quality)
        if os.getenv("GEMINI_API_KEY"):
            self.providers.append(("Gemini", GeminiAIService()))
        
        # Fallback to Groq
        if os.getenv("GROQ_API_KEY"):
            self.providers.append(("Groq", GroqAIService()))
        
        # Last resort: Ollama (local)
        if self._is_ollama_available():
            self.providers.append(("Ollama", OllamaAIService()))
    
    def explain_vulnerability(self, vulnerability: dict) -> dict:
        for provider_name, provider in self.providers:
            try:
                result = provider.explain_vulnerability(vulnerability)
                return {
                    "explanation": result,
                    "provider": provider_name,
                    "success": True
                }
            except Exception as e:
                print(f"❌ {provider_name} failed: {e}")
                continue
        
        return {
            "explanation": "AI analysis unavailable. Please check your API keys.",
            "provider": None,
            "success": False
        }
```

---

## 💾 CACHING AI RESPONSES

Save money and improve speed by caching:

```python
# backend/app/services/ai_cache.py
import hashlib
import json
from sqlalchemy.orm import Session
from app.models.models import AICache

class AICacheService:
    @staticmethod
    def get_cache_key(vulnerability: dict) -> str:
        # Create unique hash from vulnerability details
        content = f"{vulnerability['type']}:{vulnerability['file']}:{vulnerability['line']}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    @staticmethod
    def get_cached_response(db: Session, cache_key: str) -> str | None:
        cached = db.query(AICache).filter(AICache.key == cache_key).first()
        return cached.response if cached else None
    
    @staticmethod
    def save_response(db: Session, cache_key: str, response: str):
        cache = AICache(key=cache_key, response=response)
        db.add(cache)
        db.commit()
```

**Usage:**
```python
def explain_with_cache(db: Session, vulnerability: dict) -> str:
    cache_key = AICacheService.get_cache_key(vulnerability)
    
    # Try cache first
    cached = AICacheService.get_cached_response(db, cache_key)
    if cached:
        print("✅ Cache hit!")
        return cached
    
    # Call AI if not cached
    response = ai_service.explain_vulnerability(vulnerability)
    AICacheService.save_response(db, cache_key, response)
    
    return response
```

---

## 🎨 UI INTEGRATION

### Frontend Component

```jsx
// frontend/src/components/VulnerabilityCard.jsx
import { Sparkles, Copy } from 'lucide-react'
import { useState } from 'react'

function VulnerabilityCard({ vulnerability }) {
  const [aiExplanation, setAiExplanation] = useState(null)
  const [loading, setLoading] = useState(false)

  const explainWithAI = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/ai/explain/${vulnerability.id}`)
      const data = await response.json()
      setAiExplanation(data)
    } catch (error) {
      console.error('AI failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="border rounded-lg p-4 mb-4">
      <div className="flex justify-between items-start">
        <div>
          <span className={`badge severity-${vulnerability.severity.toLowerCase()}`}>
            {vulnerability.severity}
          </span>
          <h3 className="font-bold mt-2">{vulnerability.type}</h3>
          <p className="text-sm text-gray-600">
            {vulnerability.file}:{vulnerability.line}
          </p>
        </div>
        
        <button 
          onClick={explainWithAI}
          disabled={loading}
          className="btn-primary flex items-center gap-2"
        >
          <Sparkles size={16} />
          {loading ? 'Analyzing...' : 'Explain with AI'}
        </button>
      </div>

      {aiExplanation && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs text-blue-600">
              ✨ Powered by {aiExplanation.provider}
            </span>
            <button className="text-gray-500 hover:text-gray-700">
              <Copy size={14} />
            </button>
          </div>
          <p className="text-sm">{aiExplanation.explanation}</p>
        </div>
      )}
    </div>
  )
}
```

---

## 📊 API ENDPOINT

```python
# backend/app/api/ai.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/ai", tags=["ai"])
ai_service = AIService()

@router.get("/explain/{vulnerability_id}")
async def explain_vulnerability(vulnerability_id: int, db: Session = Depends(get_db)):
    # Get vulnerability from DB
    vuln = db.query(Vulnerability).filter(Vulnerability.id == vulnerability_id).first()
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    
    # Check cache
    cache_key = AICacheService.get_cache_key(vuln.__dict__)
    cached = AICacheService.get_cached_response(db, cache_key)
    if cached:
        return {"explanation": cached, "provider": "Cache", "success": True}
    
    # Get AI explanation
    result = ai_service.explain_vulnerability(vuln.__dict__)
    
    # Save to cache
    if result["success"]:
        AICacheService.save_response(db, cache_key, result["explanation"])
    
    return result
```

---

## 🧪 TESTING AI INTEGRATION

### Mock AI for Tests

```python
# tests/test_ai_service.py
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_ai_service():
    service = Mock()
    service.explain_vulnerability.return_value = {
        "explanation": "This is a test explanation",
        "provider": "Mock",
        "success": True
    }
    return service

def test_ai_explanation_endpoint(client, mock_ai_service):
    with patch('app.api.ai.ai_service', mock_ai_service):
        response = client.get("/api/ai/explain/1")
        assert response.status_code == 200
        assert "explanation" in response.json()
```

---

## 🔐 SECURITY BEST PRACTICES

### 1. Never Hardcode API Keys
```python
# ❌ BAD
GEMINI_API_KEY = "AIzaSyC..."

# ✅ GOOD
import os
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
```

### 2. Don't Send Sensitive Data to AI
```python
# ❌ BAD - sending database passwords
vulnerability['code'] = "DB_PASSWORD = 'secret123'"

# ✅ GOOD - redact sensitive data
def redact_secrets(code: str) -> str:
    # Replace tokens, passwords, keys with [REDACTED]
    code = re.sub(r'(password|token|key)\s*=\s*[\'"].+[\'"]', 
                  r'\1 = "[REDACTED]"', code, flags=re.IGNORECASE)
    return code
```

### 3. Rate Limit User Requests
```python
# Prevent abuse of AI endpoints
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/explain/{vuln_id}")
@limiter.limit("10/minute")  # Max 10 AI requests per minute
async def explain_vulnerability(...):
    ...
```

---

## 📈 MONITORING AI USAGE

Track costs and performance:

```python
# backend/app/models/models.py
class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"
    
    id = Column(Integer, primary_key=True)
    provider = Column(String)  # "Gemini", "Groq", etc.
    feature = Column(String)  # "explain", "suggest_fix"
    tokens_used = Column(Integer, nullable=True)
    response_time_ms = Column(Integer)
    success = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)
```

**Dashboard Stats:**
```python
@router.get("/ai/stats")
async def get_ai_stats(db: Session = Depends(get_db)):
    total_requests = db.query(AIUsageLog).count()
    by_provider = db.query(
        AIUsageLog.provider, 
        func.count(AIUsageLog.id)
    ).group_by(AIUsageLog.provider).all()
    
    return {
        "total_requests": total_requests,
        "requests_by_provider": dict(by_provider),
        "cache_hit_rate": calculate_cache_hit_rate(db)
    }
```

---

## 🎯 RECOMMENDED PROMPTS

### For Vulnerability Explanation
```python
EXPLAIN_PROMPT = """
You are a cybersecurity expert explaining vulnerabilities to junior developers.

Vulnerability Details:
- Type: {vuln_type}
- Severity: {severity}
- File: {file}:{line}
- Code:
{code_snippet}

Provide:
1. **What it means:** Plain English explanation (2-3 sentences)
2. **Attack scenario:** How a hacker would exploit this (1 example)
3. **Impact:** What damage could occur (be specific)

Keep response under 150 words. Use simple language, no jargon.
"""
```

### For Secure Fix Suggestion
```python
FIX_PROMPT = """
You are a security engineer fixing vulnerable code.

Vulnerable Code:
{code_snippet}

Vulnerability Type: {vuln_type}
Language: {language}

Provide:
1. Fixed code (with inline comments explaining changes)
2. Why this fix prevents the vulnerability (2 sentences)

Return only the code block and explanation. Be concise.
"""
```

---

## 🚀 DEPLOYMENT NOTES

### Environment Variables Checklist
```bash
# Required for AI features
GEMINI_API_KEY=xxx        # Get from Google AI Studio
GROQ_API_KEY=xxx          # Get from Groq Console
OLLAMA_BASE_URL=http://localhost:11434  # Local Ollama

# Optional
AI_CACHE_ENABLED=true
AI_DEFAULT_PROVIDER=gemini
```

### Startup Check
```python
@app.on_event("startup")
async def check_ai_providers():
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  No Gemini API key found. AI features will be limited.")
    else:
        print("✅ Gemini AI configured")
```

---

## 📝 SUMMARY

**For v1.0 (Recommended):**
- Use **Gemini Flash** as primary (free, fast, good)
- Add **Ollama** as offline fallback
- Implement caching to reduce API calls
- Keep prompts simple and focused

**Future Enhancements:**
- Add GPT-4 support for paid users
- Fine-tune local models on security data
- Generate automated fix PRs

---

**Questions? Check the main ROADMAP.md or open a GitHub issue!**
