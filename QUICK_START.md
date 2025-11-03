# ASURA Quick Start Guide

## 🚀 Getting Started

### Method 1: One-Click Setup (Windows)

```bash
# Run setup (first time only)
setup.bat

# Start ASURA
start.bat
```

The `start.bat` script will open two windows:
- **Backend**: `http://localhost:8000` 
- **Frontend**: `http://localhost:5173`

### Method 2: Manual Start

#### 1. Start the Backend
```bash
cd backend
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
uvicorn app.main:app --reload
```
Backend runs on: `http://localhost:8000`

#### 2. Start the Frontend
```bash
cd frontend
npm run dev
```
Frontend runs on: `http://localhost:5173`

---

## 📁 Setting Up Your First Project

### Step 1: Ensure Valid Project Path

**✅ GOOD:**
```
C:\Projects\MyWebApp
C:\Code\SecurityTest
/home/user/apps/backend
```

**❌ BAD (will be rejected):**
```
C:\My Projects\Web App      (spaces)
C:\Code\App+Features         (plus sign)  
C:\Projects\Test Site v2.0   (both)
```

**Fix bad paths:**
```bash
# Rename your folder to remove special characters
rename "C:\My Projects\Web App" WebApp
```

### Step 2: Create Project in ASURA

1. Navigate to **Projects** page
2. Click **"Add Project"**
3. Fill in:
   - **Name:** Your project name (can have spaces here)
   - **Path:** MUST be path without spaces/special chars
   - **Description:** Optional
4. Click **"Create Project"**

### Step 3: Select Project on Dashboard

1. Go to **Dashboard**
2. Use dropdown: **"-- Select a project to view stats --"**
3. Choose your project
4. Stats and actions will appear

---

## 🔒 Running Security Scans

### Quick Security Scan
1. Select project on Dashboard
2. Click **"Start Scan"** in Security Scan card
3. Wait for scan to complete (see progress)
4. View results automatically

### What Gets Scanned
- **Bandit:** Python code vulnerabilities
- **Semgrep:** Multi-language security patterns
- **Safety:** Dependency vulnerabilities (if `requirements.txt` exists)

### Scan Results
- View by severity: CRITICAL, HIGH, MEDIUM, LOW
- See file paths and line numbers
- Get code snippets
- Export reports (PDF/JSON)

---

## 📊 Viewing Metrics

### Code Metrics Include:
1. **Complexity Analysis** (via Radon)
   - Cyclomatic complexity
   - Average complexity per function
   - File-by-file breakdown

2. **Test Coverage** (via pytest-cov)
   - Overall coverage %
   - Lines covered vs total
   - Per-file coverage
   - **Requires:** `tests` directory in your project

3. **Code Health Score**
   - Combines security + coverage
   - Graded A-F
   - Trend over time

### Viewing Metrics
1. Select project on Dashboard
2. Click **"View Metrics"** button
3. Or navigate to `/metrics/{projectId}`

### If Metrics Fail

**Complexity Analysis Timeout:**
- Your project is too large (>10,000 files)
- Solution: Exclude large directories or scan smaller modules

**Coverage Analysis Skipped:**
- No `tests` directory found
- Solution: Create a `tests` or `test` folder with pytest tests

---

## 🧪 Test Directory Structure

For coverage analysis to work, structure your project like this:

```
MyProject/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
├── tests/              ← ASURA auto-detects this
│   ├── __init__.py
│   ├── test_main.py
│   └── test_utils.py
├── requirements.txt
└── README.md
```

**Supported test directory names:**
- `tests`
- `test`
- `testing`

---

## 📈 Understanding Scan Status

### Scan Statuses
- **PENDING:** Scan created, waiting to start
- **RUNNING:** Scan in progress
- **COMPLETED:** Scan finished successfully
- **FAILED:** All scanners failed

### Partial Completion
If some scanners fail but others succeed:
- Status: **COMPLETED**
- Check logs: `backend/logs/scans/`
- Review which tools failed

---

## 🐛 Troubleshooting

### "Path contains special characters"
```
Error: Path contains special characters (+, spaces)...

Solution: Rename your project folder
Example: 'My App+' → 'MyApp'
Example: 'C:\My Projects\App' → 'C:\MyProjects\App'

Valid path: Letters, numbers, underscores, hyphens, forward/back slashes only
```

### "Radon analysis timed out"
```
Error: Radon analysis timed out (120s limit)

Solutions:
1. Scan a smaller subdirectory
2. Exclude large folders (node_modules, venv)
3. Your project may be too large
```

### "No test directory found"
```
Error: No test directory found. Coverage analysis requires tests.

Solution: Create a 'tests' folder with pytest tests
```

### "Coverage completed but could not parse results"
```
Error: Coverage completed but could not parse results

Solutions:
1. Check that pytest is installed
2. Verify tests run successfully: pytest tests/
3. Check coverage.json is created in project directory
```

### Dashboard shows no project selected
```
Issue: Stats not loading

Solution: Select a project from the dropdown first
No auto-selection - you must choose explicitly
```

### "AI features not working"
```
Issue: "Explain with AI" button disabled or not responding

Solutions:
1. Check if OPENROUTER_API_KEY is set in backend/.env
2. Verify API key is valid (starts with sk-or-v1-)
3. Check backend logs for API errors
4. Try restarting the backend
5. Check if OpenRouter is rate-limiting (wait a few minutes)
```

### "Scanner failed" or "Partial completion"
```
Issue: Some scanners succeeded but others failed

Solutions:
1. Check backend/logs/scans/ for detailed error logs
2. Verify all dependencies installed: pip install -r requirements.txt
3. For Semgrep: Ensure semgrep.exe is in venv\Scripts\
4. For Safety: Check requirements.txt exists in project
5. For Bandit: Verify Python files exist in project
```

---

## 🔧 Advanced Usage

### Self-Test Scanners
```bash
cd backend
python -m app.core.scanner --self-test
```
Tests all three scanners on known vulnerable code.

### Self-Test Metrics
```bash
cd backend  
python -m app.core.metrics --self-test
```
Tests complexity and health score computation.

### View Logs
```bash
# Scan logs
cd backend/logs/scans
dir  # Windows
ls   # Linux/Mac

# Each scan creates files:
# {scan_id}_bandit_stdout.txt
# {scan_id}_semgrep_stdout.txt
# {scan_id}_safety_stdout.txt
```

---

## 🤖 Optional: AI Features Setup

### Why Enable AI?
- Get beginner-friendly vulnerability explanations
- Receive secure code fix suggestions
- Learn security concepts as you scan

### Setup Steps

1. **Get Free OpenRouter API Key**
   - Visit [https://openrouter.ai](https://openrouter.ai)
   - Sign up (free, no credit card required)
   - Go to "Keys" section
   - Create a new API key
   - Copy the key (starts with `sk-or-v1-...`)

2. **Configure ASURA**
   ```bash
   cd backend
   # Create .env file (if it doesn't exist)
   copy .env.example .env
   ```

3. **Add API Key**
   Open `backend/.env` and add:
   ```bash
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   ```

4. **Restart Backend**
   ```bash
   # Stop the backend (Ctrl+C)
   # Start it again
   uvicorn app.main:app --reload
   ```

5. **Test AI Features**
   - Run a security scan
   - Go to results page
   - Click "Explain with AI" button
   - You should see AI-generated explanations!

### AI Models Used (Automatic Fallback)

1. **Primary**: `meta-llama/llama-3.2-3b-instruct:free` (fastest)
2. **Backup 1**: `qwen/qwen-2-7b-instruct:free`
3. **Backup 2**: `google/gemini-2.0-flash-exp:free`
4. **Backup 3**: `deepseek/deepseek-r1:free`

If one model is rate-limited, ASURA automatically tries the next one!

### Without AI

ASURA works perfectly without AI:
- All security scanning works
- All code metrics work
- Reports and exports work
- Only "Explain with AI" button will be disabled

---

## 📚 API Endpoints

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project details

### Scans
- `POST /api/scans` - Start new scan
- `GET /api/scans/{id}` - Get scan details
- `GET /api/scans/project/{id}` - Get project scans
- `GET /api/scans/{id}/vulnerabilities` - Get scan vulnerabilities

### Metrics
- `GET /api/metrics/{project_id}` - Get project metrics
- `GET /api/metrics/{project_id}/complexity` - Get complexity details
- `GET /api/metrics/{project_id}/history` - Get metrics history
- `POST /api/metrics/{project_id}/compute` - Trigger metrics computation

---

## ⚡ Performance Tips

1. **Exclude unnecessary directories:**
   - Scanners auto-exclude: `venv`, `node_modules`, `__pycache__`, `.git`
   - For custom exclusions, edit scanner config

2. **Scan incrementally:**
   - Scan specific modules instead of entire monorepo
   - Create separate projects for each module

3. **Run scans during off-hours:**
   - Large scans can take 5-10 minutes
   - Schedule or run in background

4. **Monitor resource usage:**
   - Radon/Semgrep are CPU-intensive
   - Don't run multiple scans simultaneously

---

## 🎯 Best Practices

### Project Setup
✅ Use clean paths without special characters  
✅ Include a `tests` directory for coverage  
✅ Keep `requirements.txt` updated for Safety scans  
✅ Add a README describing project structure  

### Regular Scanning
✅ Scan after major changes  
✅ Review CRITICAL/HIGH issues immediately  
✅ Track metrics trends over time  
✅ Export reports for audits  

### Dashboard Usage
✅ Select project before taking actions  
✅ Use auto-refresh for running scans  
✅ Check severity breakdown regularly  
✅ Monitor code health score  

---

## 📞 Getting Help

### Error Logs
Check backend console for detailed errors:
```bash
cd backend
python -m app.main  # See all output here
```

### Scan Logs
```bash
cd backend/logs/scans
# View detailed scanner output
```

### Documentation
- `RESTRUCTURING_SUMMARY.md` - Full technical details
- `README.md` - Project overview
- `FINAL_FEATURE_STATUS.md` - Feature status

---

## ✨ Features Available (v0.3.0)

### Core Features
✅ **Security Scanning** (Bandit, Semgrep, Safety)  
✅ **Code Metrics** (Radon complexity, pytest coverage)  
✅ **Health Score** (A-F grading system)  
✅ **Dashboard** with real-time updates  
✅ **Scan History** with trend analysis  
✅ **Scan Comparison** (side-by-side)  
✅ **Vulnerability Details** with code snippets  
✅ **Report Export** (JSON, HTML)  

### AI Features (Optional)
✅ **AI Explanations** (OpenRouter API with fallback)  
✅ **Fix Suggestions** (secure code alternatives)  
✅ **Auto-Fallback** (4 free models)  
✅ **Works Offline** (AI is optional)

### UI Features
✅ **Modern Dashboard** (TailwindCSS, gradient cards)  
✅ **Dark Mode** support  
✅ **Responsive Design** (desktop + tablet)  
✅ **Real-time Progress** tracking  

---

## 🚦 Quick Checklist

Before scanning a new project:

- [ ] Project path has no spaces or special characters
- [ ] Project is added in ASURA Projects page
- [ ] Project selected in Dashboard dropdown
- [ ] For coverage: `tests` directory exists
- [ ] For Safety: `requirements.txt` exists
- [ ] Backend is running
- [ ] Frontend is running

Ready to scan! 🚀

---

**Happy Scanning!** 🛡️
