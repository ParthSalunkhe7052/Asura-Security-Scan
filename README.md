# 🔥 ASURA - AI SecureLab

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-61dafb.svg)](https://reactjs.org/)
[![Version](https://img.shields.io/badge/version-0.3.0-green.svg)](docs/CHANGELOG.md)

## The Hook (For HR/Managers)

**What is it?**
A privacy-first, local security and code quality scanner that combines open-source tools with AI analysis to secure your code.

**The Problem**
Developers waste time manually configuring multiple security tools and worrying about data privacy when using cloud-based scanners.

**The Solution**
Asura automates security auditing by running industry-standard scanners (Bandit, Semgrep, Safety) locally and using AI to explain vulnerabilities and generate fixes, saving hours of debugging time while keeping code 100% private.

**Example**
"Instead of 'Running a Python script with Bandit and Semgrep,' say 'An automated security analyst that finds vulnerabilities and writes the fix for you.'"

## The Tech (For Developers/CTOs)

**Tech Stack**
- **Frontend:** React 18, Vite, TailwindCSS, Recharts
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, SQLite
- **Scanners:** Bandit, Safety, Semgrep, Radon

**Architecture**
The React frontend provides a responsive dashboard that communicates with the FastAPI backend via REST endpoints. The backend orchestrates local CLI tools (scanners) to analyze the codebase, parses their output, and stores structured results in a local SQLite database. AI analysis is integrated to process these results and generate natural language explanations and fixes.

**Installation**
You can run Asura locally in minutes.

**One-Click Setup (Windows)**
```bash
git clone https://github.com/ParthSalunkhe7052/Asura-Security-Scan.git
cd Asura-Security-Scan
setup.bat
start.bat
```

**Manual Setup**
1. **Backend**:
   ```bash
   cd backend
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Access the app at `http://localhost:5173`.

---

## ✨ Key Features

### 🔒 Comprehensive Security Scanning
- **Bandit**: Python security linter for common vulnerabilities.
- **Safety**: Checks dependencies against known CVEs.
- **Semgrep**: Multi-language static analysis with 1000+ rules.
- **Real-time Progress**: Watch scans execute live.

### 🤖 AI-Powered Analysis (New!)
- **Smart Explanations**: AI explains vulnerabilities in plain English.
- **Auto-Fix Suggestions**: Get secure code alternatives instantly.
- **AI Auto Fix Prompt**: Generate prompts for AI IDEs (Cursor, Windsurf) to fix issues automatically.
- **Offline Capable**: Core scanning works perfectly without AI.

### 📊 Code Quality & Metrics
- **Health Scoring**: A-F grading based on security and coverage.
- **Complexity Analysis**: Radon-powered cyclomatic complexity checks.
- **Test Coverage**: Integrated Pytest coverage reporting.

### 🔐 Privacy First
- **Local Execution**: All scans run on your machine.
- **No Telemetry**: Your code never leaves your computer.
- **Optional Cloud**: AI features are opt-in; everything else is local.

---

## 📸 Screenshots

### Dashboard
Get a complete overview of your project health, security scores, and vulnerability distribution.
![Dashboard](screenshots/dashboard.png)

### Project Management
Manage multiple projects easily from a clean, intuitive interface.
![Projects Tab](screenshots/projects_tab.png)

### Scan History
View and compare past scans to track improvements over time.
![Scans Tab](screenshots/scans_tab.png)

### Detailed Scan Report
Drill down into specific vulnerabilities with code snippets and severity levels.
![Scan Report](screenshots/scan_report.png)

### AI Summary & Fixes
Understand issues quickly with AI-generated summaries and fix suggestions.
![AI Summary](screenshots/ai_summary.png)

---

## 📁 Project Structure

```
asura/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Scanners & AI logic
│   │   └── models/       # Database models
│   ├── tests/            # Pytest suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # UI Components
│   │   └── pages/        # Application Pages
│   └── package.json
├── screenshots/          # Project screenshots
├── docs/                 # Documentation
└── README.md             # This file
```

---

## 🗺️ Roadmap

- [ ] **Mutation Testing**: Integrate Mutmut for Python.
- [ ] **CI/CD Integration**: GitHub Actions support.
- [ ] **Report Export**: PDF and improved HTML reports.
- [ ] **More Languages**: Support for Go, Rust, and Java.

---

## 🤝 Contributing

Contributions are welcome! Please check out [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ by Parth Salunkhe**
