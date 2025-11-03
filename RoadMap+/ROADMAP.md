# 🔥 ASURA - AI SecureLab
## Comprehensive Development Roadmap

---

## 📋 PROJECT OVERVIEW

**Asura** is an all-in-one local security & mutation testing tool designed for solo developers and small teams (2-5 people). It provides:

- **Static Security Scanning** using open-source tools
- **Code Mutation Testing** for unit test strength validation
- **AI-Powered Analysis** for vulnerability explanations and fix suggestions
- **Interactive Web Dashboard** for seamless user experience
- **100% Local & Offline** - No cloud dependencies, maximum privacy

**Target Users:** Solo developers, freelancers, small dev teams  
**Deployment:** Local-first, runs on Windows/Linux/macOS  
**License:** Open Source (MIT/Apache 2.0)

---

## 🎯 CORE PRINCIPLES

1. **Privacy First** - All data stays local, no telemetry
2. **Zero Docker** - Simple installation, no containers
3. **Lightweight** - Fast scans, minimal resource usage
4. **Extensible** - Custom rules support via Semgrep YAML
5. **Educational** - Clear explanations, not just findings

---

## 🛠️ TECH STACK

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** SQLite with SQLAlchemy ORM
- **Task Queue:** Celery + Redis (for async scans)
- **Testing:** pytest, pytest-cov, pytest-asyncio

### Frontend
- **Framework:** React 18 + Vite
- **Styling:** TailwindCSS + shadcn/ui components
- **Charts:** Recharts or Chart.js
- **Icons:** Lucide React
- **State Management:** Zustand or React Context
- **HTTP Client:** Axios or Tanstack Query

### Security Tools (Integrated)
- **Bandit** - Python security linter
- **Safety** - Dependency vulnerability scanner
- **Semgrep** - Multi-language static analyzer
- **Mutmut** - Python mutation testing
- **Radon** - Code complexity metrics
- **Coverage.py** - Test coverage analysis

### AI Integration (Phase 3)
- **Primary:** Google Gemini Flash (Free 15 req/min)
- **Alternatives:** Groq (free, fast), HuggingFace Inference API
- **Fallback:** Ollama (local, no API needed)

---

## 📅 DEVELOPMENT PHASES

---

## **PHASE 1: FOUNDATION (WEEKS 1-2)**

### Week 1: Project Setup & Architecture

#### Backend Setup
- [x] Initialize FastAPI project structure
  ```
  /backend
    /app
      /api         # API routes
      /core        # Core business logic
      /models      # SQLAlchemy models
      /schemas     # Pydantic schemas
      /services    # Service layer
      /utils       # Helper functions
    /tests         # Test suite
    main.py        # Entry point
    requirements.txt
  ```
- [x] Setup SQLAlchemy + Alembic migrations
- [x] Create database models:
  - `Project` - Scanned projects
  - `Scan` - Scan history with timestamps
  - `Vulnerability` - Security findings
  - `MutationTest` - Mutation test results
  - `Config` - User preferences

#### Frontend Setup
- [x] Initialize React + Vite project
  ```
  /frontend
    /src
      /components  # Reusable UI components
      /pages       # Page components
      /hooks       # Custom React hooks
      /lib         # Utilities
      /api         # API client
    /public
  ```
- [x] Setup TailwindCSS + shadcn/ui
- [x] Create basic layout (Header, Sidebar, Main)
- [x] Install dependencies: axios, recharts, lucide-react

#### API Endpoints (Placeholders)
- `POST /api/projects` - Register new project
- `POST /api/scan/security` - Run security scan
- `POST /api/scan/mutation` - Run mutation tests
- `GET /api/scans/{project_id}` - Get scan history
- `GET /api/reports/{scan_id}` - Get detailed report

#### Deliverables
✅ Running FastAPI server on `http://localhost:8000`  
✅ Running React dev server on `http://localhost:5173`  
✅ Database schema created  
✅ Basic API docs at `/docs`

---

### Week 2: Core Scanner Integration

#### Tool Integration Module
Create `/backend/app/core/scanner.py`:

```python
class SecurityScanner:
    def run_bandit(self, project_path: str) -> dict
    def run_safety(self, project_path: str) -> dict
    def run_semgrep(self, project_path: str) -> dict
    def run_all(self, project_path: str) -> dict
```

#### Tasks
- [x] Install scanner tools: `pip install bandit safety semgrep`
- [x] Implement wrapper functions for each tool
- [x] Parse JSON/XML outputs into unified schema:
  ```json
  {
    "tool": "bandit",
    "severity": "HIGH|MEDIUM|LOW",
    "file_path": "path/to/file.py",
    "line_number": 42,
    "vulnerability_type": "SQL_INJECTION",
    "description": "...",
    "code_snippet": "...",
    "cwe_id": "CWE-89"
  }
  ```
- [x] Store results in SQLite via SQLAlchemy
- [x] Create test project with intentional vulnerabilities
- [x] Unit tests for each scanner integration

#### Custom Rules Support
- [x] Create `/backend/rules/custom/` directory
- [x] Allow users to drop Semgrep YAML rules
- [x] Load custom rules during scan: `semgrep --config /backend/rules/`

#### Deliverables
✅ Working security scan endpoint  
✅ Test coverage > 80%  
✅ Sample vulnerable project scanned successfully

---

## **PHASE 2: MUTATION TESTING & UI (WEEKS 3-4)**

### Week 3: Mutation Testing Integration

#### Mutmut Integration
- [x] Install mutmut: `pip install mutmut`
- [x] Create `/backend/app/core/mutation_tester.py`
- [x] Implement mutation test runner:
  ```python
  class MutationTester:
      def run_mutmut(self, project_path: str, test_dir: str) -> dict
      def parse_results(self) -> dict
  ```
- [x] Parse mutmut output:
  - Total mutants
  - Killed mutants (tests caught the mutation)
  - Survived mutants (tests didn't catch it - weak tests!)
  - Mutation score percentage
- [x] Store results in database

#### Code Quality Metrics
- [x] Integrate Radon for cyclomatic complexity
- [x] Integrate Coverage.py for test coverage
- [x] Create combined "Code Health Score" (0-100):
  ```
  Score = (0.4 * SecurityScore) + (0.3 * MutationScore) + (0.3 * CoverageScore)
  ```

#### API Endpoints
- `POST /api/mutation/run` - Start mutation test
- `GET /api/mutation/status/{job_id}` - Check progress (async)
- `GET /api/metrics/{project_id}` - Get code quality metrics

#### Deliverables
✅ Mutation testing works on sample projects  
✅ Async task queue for long-running scans  
✅ Code health score algorithm implemented

---

### Week 4: Dashboard UI Development

#### Pages to Build
1. **Dashboard Home** (`/`)
   - Project selector dropdown
   - Quick actions: "Run Security Scan", "Run Mutation Test"
   - Latest scan summary cards
   - Code health score gauge

2. **Security Results** (`/security`)
   - Vulnerability list (filterable by severity)
   - File tree view with issue counts
   - Code snippet viewer with syntax highlighting
   - "View Fix Suggestion" button (Phase 3)

3. **Mutation Testing** (`/mutation`)
   - Mutation score chart
   - Survived mutants table
   - "Where are my tests weak?" insights

4. **History** (`/history`)
   - Timeline of all scans
   - Trend charts (security score over time)
   - Compare two scans side-by-side

5. **Settings** (`/settings`)
   - Project path configuration
   - Scanner tool toggles (enable/disable bandit, safety, etc.)
   - Custom Semgrep rules upload
   - Theme toggle (light/dark)

#### UI Components
- Severity badge (HIGH=red, MEDIUM=orange, LOW=yellow)
- Code viewer with line highlighting
- Progress indicators for running scans
- Toast notifications (success/error)
- Export buttons (PDF, JSON, HTML)

#### Deliverables
✅ Fully functional dashboard  
✅ Responsive design (desktop + tablet)  
✅ Real-time scan progress updates via WebSocket

---

## **PHASE 3: AI INTEGRATION (WEEK 5)**

### AI Analysis Layer

#### Free AI Model Options
**Recommended: Google Gemini Flash**
- Free tier: 15 requests/minute, 1500 requests/day
- API Key: Free from Google AI Studio
- Model: `gemini-1.5-flash`

**Alternative 1: Groq**
- Free tier: Fast inference, generous limits
- Models: Llama 3, Mixtral
- Best for speed

**Alternative 2: HuggingFace Inference API**
- Free tier available
- Models: CodeLlama, Mistral
- Rate limited but sufficient

**Fallback: Ollama (Local)**
- 100% offline
- Models: llama3.2:3b, codellama:7b
- No API limits, but slower

#### Implementation
Create `/backend/app/services/ai_service.py`:

```python
class AIAnalyzer:
    def explain_vulnerability(self, vuln: dict) -> str
    def suggest_fix(self, vuln: dict, code_context: str) -> str
    def generate_test_case(self, vuln: dict) -> str
```

#### Features
1. **Vulnerability Explanation**
   - Takes vulnerability details → sends to AI
   - Returns beginner-friendly explanation
   - Includes real-world attack scenario

2. **Secure Code Suggestion**
   - Analyzes vulnerable code snippet
   - Generates fixed version with comments
   - Explains why the fix works

3. **Test Case Generation** (Optional)
   - Creates pytest test to catch the vulnerability
   - Helps improve mutation score

#### Caching Strategy
- Hash vulnerability fingerprint (file + line + type)
- Cache AI responses in SQLite (`AICache` table)
- Saves API calls for repeated scans

#### UI Integration
- "✨ Explain with AI" button on each vulnerability
- Modal popup with AI explanation + fix
- Copy-to-clipboard for suggested code

#### Deliverables
✅ AI service with Gemini Flash integration  
✅ Response caching system  
✅ UI buttons for AI features  
✅ Fallback to Ollama if API fails

---

## **PHASE 4: REPORTING & POLISH (WEEK 6)**

### Report Generation

#### Report Formats

**1. PDF Report** (using ReportLab or WeasyPrint)
```
📄 ASURA Security Report
   Generated: 2025-01-15 14:30
   Project: my-awesome-app

   🛡️ Executive Summary
   - Total Issues: 23 (5 HIGH, 12 MEDIUM, 6 LOW)
   - Code Health Score: 78/100
   - Mutation Score: 85%

   🔍 Detailed Findings
   [Vulnerability details with code snippets]

   📊 Recommendations
   [AI-generated summary]
```

**2. JSON Export**
```json
{
  "scan_id": "abc123",
  "timestamp": "2025-01-15T14:30:00Z",
  "project": "my-awesome-app",
  "vulnerabilities": [...],
  "mutation_results": {...},
  "metrics": {...}
}
```

**3. HTML Report**
- Standalone HTML file with embedded CSS
- Interactive charts (Chart.js embedded)
- Shareable with non-technical stakeholders

#### API Endpoints
- `GET /api/reports/export/{scan_id}?format=pdf|json|html`
- `GET /api/reports/compare/{scan_id_1}/{scan_id_2}`

### Trend Analysis

#### Charts to Implement
1. **Security Score Over Time** (Line chart)
2. **Vulnerability Count by Severity** (Bar chart)
3. **Mutation Score Trend** (Line chart)
4. **Most Vulnerable Files** (Horizontal bar)

#### Implementation
- Use Recharts on frontend
- Backend endpoint: `GET /api/trends/{project_id}?days=30`

### Final Polish

#### Code Quality
- [x] Run `black` and `flake8` on Python code
- [x] Run `eslint` and `prettier` on React code
- [x] Achieve >85% test coverage

#### Documentation
- [x] **README.md** - Installation, usage, features
- [x] **CONTRIBUTING.md** - How to contribute
- [x] **ARCHITECTURE.md** - System design docs
- [x] **API_DOCS.md** - Endpoint documentation
- [x] **CHANGELOG.md** - Version history

#### Performance Optimization
- [x] Add database indexes on frequently queried fields
- [x] Implement pagination for large result sets
- [x] Lazy load code snippets in UI

#### Error Handling
- [x] Graceful fallbacks if scanner tool missing
- [x] User-friendly error messages
- [x] Retry logic for AI API calls

#### Deliverables
✅ PDF/JSON/HTML export working  
✅ Trend charts functional  
✅ Documentation complete  
✅ Ready for GitHub release

---

## 📦 ADDITIONAL TOOLS & LIBRARIES

### Python Backend
```txt
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0

# Security Scanners
bandit==1.7.5
safety==2.3.5
semgrep==1.45.0

# Mutation Testing
mutmut==2.4.3
coverage==7.3.2

# Code Analysis
radon==6.0.1
pyflakes==3.1.0

# Utilities
python-dotenv==1.0.0
python-multipart==0.0.6
httpx==0.25.1

# AI Integration (Phase 3)
google-generativeai==0.3.1  # Gemini
groq==0.4.0                 # Groq (alternative)

# Reporting
reportlab==4.0.7            # PDF generation
jinja2==3.1.2               # HTML templates

# Async Tasks
celery==5.3.4
redis==5.0.1

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "zustand": "^4.4.7",
    "@tanstack/react-query": "^5.12.2",
    "recharts": "^2.10.3",
    "lucide-react": "^0.294.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-tabs": "^1.0.4",
    "sonner": "^1.2.0",
    "tailwindcss": "^3.3.5",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.1.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "eslint": "^8.54.0",
    "prettier": "^3.1.0"
  }
}
```

---

## 🚀 FEATURE CHECKLIST

### Core Features (v1.0)
- [ ] Static security scanning (Bandit, Safety, Semgrep)
- [ ] Mutation testing (Mutmut)
- [ ] Code complexity metrics (Radon)
- [ ] Test coverage analysis (Coverage.py)
- [ ] Custom Semgrep rules support
- [ ] SQLite database for scan history
- [ ] Interactive web dashboard
- [ ] Code health score calculation
- [ ] Vulnerability details with code snippets
- [ ] Export reports (PDF, JSON, HTML)
- [ ] Trend analysis charts
- [ ] Dark/Light theme

### AI Features (v1.1)
- [ ] Vulnerability explanation (AI-powered)
- [ ] Secure code fix suggestions
- [ ] Test case generation
- [ ] Response caching
- [ ] Multi-model support (Gemini, Groq, Ollama)

### Future Enhancements (v2.0+)
- [ ] JavaScript/TypeScript mutation testing (Stryker)
- [ ] Deep React/Vue component analysis
- [ ] Git integration (scan only changed files)
- [ ] Scheduled scans (cron-like)
- [ ] File watcher for continuous monitoring
- [ ] CI/CD pipeline integration (GitHub Actions)
- [ ] VS Code extension
- [ ] Multi-project comparison
- [ ] Team collaboration (optional cloud sync)
- [ ] API security testing (basic endpoint probing)
- [ ] SARIF format export (GitHub Advanced Security)
- [ ] Dependency graph visualization
- [ ] Auto-fix PR generation (experimental)
- [ ] Blockchain smart contract scanning (Solidity)

---

## 🎓 LEARNING RESOURCES

### For Contributors
- **FastAPI:** https://fastapi.tiangolo.com/tutorial/
- **Semgrep Rules:** https://semgrep.dev/docs/writing-rules/overview/
- **Mutation Testing Concepts:** https://en.wikipedia.org/wiki/Mutation_testing
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **CWE Database:** https://cwe.mitre.org/

### Tools Documentation
- Bandit: https://bandit.readthedocs.io/
- Safety: https://pyup.io/safety/
- Semgrep: https://semgrep.dev/docs/
- Mutmut: https://mutmut.readthedocs.io/

---

## 🧪 TESTING STRATEGY

### Unit Tests
- All scanner wrapper functions
- Database models and queries
- API endpoint logic
- AI service with mocked responses

### Integration Tests
- End-to-end scan workflow
- Database persistence
- File upload and processing

### Test Projects
Create sample vulnerable projects:
1. **Python Flask App** with SQL injection, XSS
2. **Django App** with CSRF issues
3. **FastAPI App** with authentication flaws

---

## 📊 SUCCESS METRICS

### v1.0 Goals
- Scan a medium project (10k LOC) in <2 minutes
- Detect at least 90% of OWASP Top 10 issues
- Mutation score accuracy >95%
- UI loads in <1 second
- Zero crashes during 100 consecutive scans

### Community Goals (6 months)
- 500+ GitHub stars
- 20+ contributors
- 10+ custom Semgrep rules shared
- Featured on Reddit r/Python or HackerNews

---

## 🤝 CONTRIBUTION GUIDELINES

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/awesome-feature`)
3. Write tests for new features
4. Ensure all tests pass (`pytest`)
5. Format code (`black backend/`, `prettier --write frontend/`)
6. Submit a pull request

### Areas We Need Help
- Adding support for more languages (Go, Rust, Java)
- Writing Semgrep rules for framework-specific issues
- UI/UX improvements
- Documentation and tutorials

---

## 🛡️ SECURITY & ETHICS

### Safe Usage
- **Only scan code you own or have permission to scan**
- Tool does NOT exploit vulnerabilities - only identifies them
- No network traffic generated during scans (except optional AI API)
- All data stored locally, no telemetry

### Responsible Disclosure
If you find a security issue in Asura itself:
1. Do NOT open a public GitHub issue
2. Email: security@asura-project.com (create this)
3. We'll respond within 48 hours

---

## 📞 SUPPORT & COMMUNITY

- **GitHub Discussions:** For questions and ideas
- **Discord Server:** Real-time chat (setup later)
- **Documentation:** Full wiki on GitHub
- **YouTube:** Tutorial videos (future)

---

## 📅 RELEASE SCHEDULE

- **v0.1 (Alpha):** Week 2 - Core scanning works
- **v0.5 (Beta):** Week 4 - UI functional
- **v1.0 (Stable):** Week 6 - Production ready
- **v1.1 (AI):** Week 8 - AI features added
- **v2.0:** Q2 2025 - Advanced features

---

## 🎯 FINAL THOUGHTS

Asura aims to democratize security testing by making it:
- **Accessible** - No expensive licenses or cloud accounts
- **Educational** - Learn while you scan
- **Practical** - Actionable results, not just noise
- **Private** - Your code never leaves your machine

**Let's make security testing boring (in a good way)!** 🔥

---

**Last Updated:** October 19, 2025  
**Version:** 1.0  
**Maintainers:** Parth & Contributors
