# 🧰 ASURA TOOLS COMPARISON & SELECTION GUIDE

## Overview
This document compares all tools considered for Asura and justifies the final selections.

---

## 🔒 STATIC SECURITY SCANNERS

### Python Security

| Tool | Pros | Cons | Selected? |
|------|------|------|-----------|
| **Bandit** | Fast, Python-specific, good documentation | Python only | ✅ YES |
| **Semgrep** | Multi-language, custom rules, fast | Requires rule tuning | ✅ YES |
| **Pylint** | Comprehensive linting | Too many false positives for security | ❌ NO |
| **Pyre** | Type checking security | Slow, complex setup | ❌ NO |

### Dependency Scanning

| Tool | Pros | Cons | Selected? |
|------|------|------|-----------|
| **Safety** | Fast, free, good CVE database | Python only | ✅ YES |
| **pip-audit** | Official PyPA tool | Newer, less mature | ⚠️ MAYBE v2 |
| **Snyk** | Excellent, multi-language | Requires account, rate limits | ❌ NO |
| **OWASP Dependency-Check** | Multi-language, comprehensive | Slow (downloads large DB) | ❌ NO |

### Multi-Language Static Analysis

| Tool | Pros | Cons | Selected? |
|------|------|------|-----------|
| **Semgrep** | Fast, custom rules, 30+ languages | Requires rule knowledge | ✅ YES |
| **SonarQube** | Enterprise-grade, great UI | Heavy, requires server | ❌ NO |
| **CodeQL** | GitHub-native, powerful | Complex setup, slow | ❌ NO |
| **Checkmarx** | Enterprise tool | Paid, overkill | ❌ NO |

**Decision:** Bandit + Safety + Semgrep = Lightweight, fast, covers 80% of needs.

---

## 🧬 MUTATION TESTING TOOLS

### Python

| Tool | Pros | Cons | Selected? |
|------|------|------|-----------|
| **Mutmut** | Fast, simple API, good docs | Python only | ✅ YES |
| **Cosmic Ray** | More mutation operators | Slower, heavier | ❌ NO |
| **MutPy** | Academic project | Unmaintained since 2020 | ❌ NO |

### JavaScript/TypeScript (Future)

| Tool | Pros | Cons | Selected? |
|------|------|------|-----------|
| **Stryker** | Best JS mutation tester | Slow on large projects | ⚠️ v2.0 |
| **Mutode** | Lightweight | Limited operators | ❌ NO |

**Decision:** Mutmut for v1 (Python), Stryker for v2 (JS).

---

## 🤖 AI MODELS & APIs

### Free Options

| Model | Provider | Free Tier | Pros | Cons | Selected? |
|-------|----------|-----------|------|------|-----------|
| **Gemini 1.5 Flash** | Google | 15 req/min, 1500/day | Fast, free API key, good code understanding | Requires internet | ✅ PRIMARY |
| **Groq (Llama 3)** | Groq | Very fast, generous limits | Fastest inference | Smaller context window | ✅ ALTERNATIVE |
| **Mistral 7B** | HuggingFace | Free tier | Open source, decent | Rate limited | ⚠️ FALLBACK |
| **CodeLlama 34B** | Together AI | Free tier | Code-specialized | API limits | ⚠️ FALLBACK |
| **Llama 3.2:3b** | Ollama (Local) | Unlimited | 100% offline, no API | Slower, requires install | ✅ OFFLINE OPTION |
| **GPT-4o** | OpenAI | Paid only | Best quality | $$$, not free | ❌ NO |
| **Claude Sonnet 4** | Anthropic | Paid only | Excellent reasoning | $$$, not free | ❌ NO |

**Decision:**
- **Primary:** Google Gemini Flash (best free option)
- **Fast Alternative:** Groq
- **Offline Fallback:** Ollama (llama3.2:3b)

### API Key Setup
```python
# .env file
GEMINI_API_KEY=your_key_here  # Free from https://aistudio.google.com/
GROQ_API_KEY=your_key_here    # Free from https://groq.com/
OLLAMA_BASE_URL=http://localhost:11434  # Local
```

---

## 📊 CODE METRICS TOOLS

| Tool | Purpose | Pros | Cons | Selected? |
|------|---------|------|------|-----------|
| **Radon** | Complexity (McCabe) | Fast, multiple metrics | Python only | ✅ YES |
| **Coverage.py** | Test coverage | Standard tool, accurate | N/A | ✅ YES |
| **Lizard** | Complexity (multi-language) | 20+ languages | Less Python-specific | ⚠️ v2.0 |
| **Flake8** | Style + basic errors | Fast linting | Not security-focused | ⚠️ OPTIONAL |

---

## 🗄️ DATABASE OPTIONS

| Database | Pros | Cons | Selected? |
|----------|------|------|-----------|
| **SQLite** | Zero setup, file-based, fast reads | Single-writer limit | ✅ YES |
| **PostgreSQL** | Robust, multi-user | Requires server | ❌ NO |
| **MongoDB** | Flexible schema | Overkill, needs server | ❌ NO |
| **JSON Files** | Simple | No indexing, slow queries | ❌ NO |

**Decision:** SQLite for v1 (single-user), PostgreSQL optional for team features in v2.

---

## 🎨 FRONTEND FRAMEWORKS

| Framework | Pros | Cons | Selected? |
|-----------|------|------|-----------|
| **React + Vite** | Fast HMR, huge ecosystem | Requires learning hooks | ✅ YES |
| **Vue 3** | Easier learning curve | Smaller ecosystem | ❌ NO |
| **Svelte** | Less boilerplate | Smaller community | ❌ NO |
| **Vanilla JS** | No dependencies | Too much manual work | ❌ NO |

**UI Component Libraries:**

| Library | Pros | Cons | Selected? |
|---------|------|------|-----------|
| **shadcn/ui** | Copy-paste, customizable | Requires setup | ✅ YES |
| **Radix UI** | Accessible, unstyled | More manual styling | ⚠️ (Used by shadcn) |
| **Material-UI** | Complete system | Heavy bundle | ❌ NO |
| **Ant Design** | Enterprise-ready | Too opinionated | ❌ NO |

---

## 📈 CHARTING LIBRARIES

| Library | Pros | Cons | Selected? |
|---------|------|------|-----------|
| **Recharts** | React-native, simple API | Less customization | ✅ YES |
| **Chart.js** | Popular, feature-rich | Requires wrapper for React | ⚠️ ALTERNATIVE |
| **D3.js** | Maximum flexibility | Steep learning curve | ❌ NO |
| **ApexCharts** | Beautiful defaults | Larger bundle | ❌ NO |

---

## 📄 REPORT GENERATION

| Tool | Format | Pros | Cons | Selected? |
|------|--------|------|------|-----------|
| **ReportLab** | PDF | Pure Python, flexible | Complex API | ✅ YES |
| **WeasyPrint** | PDF | HTML → PDF (easier) | External dependencies | ⚠️ ALTERNATIVE |
| **Jinja2** | HTML | Template-based, clean | Requires CSS | ✅ YES (HTML) |
| **PDFKit** | PDF | Simple wkhtmltopdf wrapper | Requires binary | ❌ NO |

---

## 🚀 DEPLOYMENT OPTIONS (Future)

| Platform | Pros | Cons | Selected? |
|----------|------|------|-----------|
| **Local Install** | Full control, private | Each user installs | ✅ v1.0 |
| **Render** | Free tier, easy deploy | Cold starts | ⚠️ v2.0 (optional) |
| **Railway** | Good DX, free tier | Limited free hours | ⚠️ v2.0 (optional) |
| **Vercel** | Great for frontend | Not ideal for Python | ❌ NO |
| **Docker** | Consistent environment | Adds complexity | ❌ NO (per spec) |

---

## 🧪 TESTING FRAMEWORKS

| Tool | Purpose | Pros | Cons | Selected? |
|------|---------|------|------|-----------|
| **pytest** | Unit testing | Python standard, plugins | N/A | ✅ YES |
| **pytest-asyncio** | Async tests | Essential for FastAPI | N/A | ✅ YES |
| **pytest-cov** | Coverage reporting | Integrates with pytest | N/A | ✅ YES |
| **unittest** | Built-in testing | No install needed | Less features | ❌ NO |
| **Playwright** | E2E testing | Modern, reliable | Heavy for our use case | ⚠️ v2.0 |

---

## 🔧 BUILD & DEV TOOLS

### Python

| Tool | Purpose | Selected? |
|------|---------|-----------|
| **Black** | Code formatting | ✅ YES |
| **Flake8** | Linting | ✅ YES |
| **MyPy** | Type checking | ⚠️ OPTIONAL |
| **isort** | Import sorting | ✅ YES |

### JavaScript

| Tool | Purpose | Selected? |
|------|---------|-----------|
| **ESLint** | Linting | ✅ YES |
| **Prettier** | Formatting | ✅ YES |
| **TypeScript** | Type safety | ⚠️ v2.0 |

---

## 🌐 LANGUAGE SUPPORT ROADMAP

### v1.0 (Launch)
- ✅ **Python** - Full support (Bandit, Safety, Mutmut)
- ⚠️ **JavaScript/TypeScript** - Basic (Semgrep only)

### v1.5 (Q1 2026)
- **JavaScript/TypeScript** - Full (ESLint, npm audit, Stryker)
- **React/Vue** - Framework-specific rules

### v2.0 (Q2 2026)
- **Go** - Semgrep + gosec
- **Rust** - Semgrep + Clippy
- **Java** - Semgrep + SpotBugs

### Future Considerations
- **PHP** - Semgrep + Psalm
- **C/C++** - Semgrep + Clang-Tidy
- **Solidity** - Smart contract scanning

---

## 💡 WHY NOT [POPULAR TOOL]?

### Why not SonarQube?
- Requires dedicated server
- Complex setup for local use
- Overkill for solo developers

### Why not Snyk?
- Requires account + login
- Rate limits on free tier
- Not 100% local

### Why not Docker?
- User requirement: no Docker
- Adds installation complexity
- Asura works fine without it

### Why not paid AI models (GPT-4, Claude)?
- User requirement: free tools only
- Gemini Flash is sufficient
- Ollama provides offline alternative

---

## 🎯 SELECTION CRITERIA

When evaluating tools, we prioritized:

1. **Zero Cost** - Must be free for commercial use
2. **Local-First** - Works offline (except AI, which is optional)
3. **Easy Install** - `pip install` or `npm install` only
4. **Good Docs** - Active community, tutorials
5. **Performance** - Scans should be fast (<5 min for 10k LOC)
6. **Accuracy** - Low false positive rate

---

## 📚 REFERENCE LINKS

### Official Documentation
- Bandit: https://bandit.readthedocs.io/
- Safety: https://pyup.io/safety/
- Semgrep: https://semgrep.dev/docs/
- Mutmut: https://mutmut.readthedocs.io/
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/

### AI Providers
- Gemini: https://ai.google.dev/
- Groq: https://groq.com/
- Ollama: https://ollama.ai/

### Comparison Resources
- SAST Tools: https://owasp.org/www-community/Source_Code_Analysis_Tools
- Mutation Testing: https://github.com/theofidry/awesome-mutation-testing

---

**Last Updated:** October 19, 2025  
**Maintainer:** Asura Team
