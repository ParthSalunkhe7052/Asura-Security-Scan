# 🔥 ASURA - AI SecureLab

> An all-in-one local security testing and code quality tool for developers

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-61dafb.svg)](https://reactjs.org/)
[![Version](https://img.shields.io/badge/version-0.3.0-green.svg)](CHANGELOG.md)
![GitHub Stars](https://img.shields.io/github/stars/ParthSalunkhe7052/Asura-Security-Scan?style=social)
![GitHub Issues](https://img.shields.io/github/issues/ParthSalunkhe7052/Asura-Security-Scan)
![GitHub Forks](https://img.shields.io/github/forks/ParthSalunkhe7052/Asura-Security-Scan?style=social)

ASURA is a privacy-first security testing tool that helps solo developers and small teams identify vulnerabilities in their code using open-source scanners and AI-powered analysis. All data stays local - no cloud dependencies required.

## ✨ Features

### 🔒 Security Scanning
- **Bandit** - Python security linter for common vulnerabilities
- **Safety** - Dependency vulnerability scanner using CVE database  
- **Semgrep** - Multi-language static analyzer with 1000+ rules
- **Real-time Progress** - Watch scans as they run

### 🤖 AI-Powered Analysis
- **Vulnerability Explanations** - AI explains security issues in plain English
- **Fix Suggestions** - Get AI-generated secure code alternatives
- **OpenRouter Integration** - Free tier with automatic model fallback
- **Offline Ready** - Works without AI if needed

### 📊 Code Quality Metrics
- **Complexity Analysis** - Radon-powered cyclomatic complexity
- **Test Coverage** - Pytest coverage integration
- **Health Scoring** - A-F grades based on security + coverage
- **Trend Tracking** - Monitor improvements over time

### 📈 Reporting & History
- **Export Reports** - JSON and HTML formats
- **Scan Comparison** - Compare two scans side-by-side
- **Historical Tracking** - View all past scans
- **Detailed Findings** - Code snippets with line numbers

### 🎯 Modern Dashboard
- **Beautiful React UI** - Modern design with TailwindCSS
- **Real-time Updates** - Live scan progress
- **Dark Mode** - Easy on the eyes
- **Responsive** - Works on desktop and tablets

### 🔐 Privacy & Security
- **100% Local** - All scans run on your machine
- **No Telemetry** - Your code never leaves your computer
- **No Cloud Required** - Optional AI features only
- **Open Source** - Full transparency, MIT licensed

## 📸 Screenshots

### Dashboard
Get a complete overview of your project health with security scores, coverage metrics, and vulnerability distribution.

![Dashboard](screenshots/Screenshot%20(52).png)

### Security Scan Results
View detailed scan results with severity levels, health scores, and filtering options.

![Scan Results](screenshots/Screenshot%20(53).png)

### AI-Powered Analysis
Get intelligent vulnerability explanations and fix suggestions powered by AI.

![AI Analysis](screenshots/Screenshot%20(54).png)

### Detailed Vulnerability List
Browse through all detected vulnerabilities with code references and security tool tags.

![Vulnerability List](screenshots/Screenshot%20(55).png)

### Project Management
Manage multiple projects with ease from a clean, intuitive interface.

![Projects](screenshots/Screenshot%20(56).png)

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Git (for cloning)

### One-Click Setup (Windows)

```bash
# Clone the repository
git clone https://github.com/ParthSalunkhe7052/Asura-Security-Scan.git
cd Asura-Security-Scan

# Run setup script
setup.bat

# Start ASURA
start.bat
```

The setup script will:
1. Create Python virtual environment
2. Install backend dependencies
3. Install frontend dependencies

### Manual Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```

The API will be running at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be running at `http://localhost:5173`

### Optional: AI Features Setup

To enable AI-powered vulnerability explanations:

1. Get a free OpenRouter API key at [https://openrouter.ai](https://openrouter.ai)
2. Create `.env` file in backend directory:
   ```bash
   OPENROUTER_API_KEY=your_key_here
   ```
3. Restart the backend server

**Note:** AI features are optional. All core security scanning works without AI.

## 📖 Usage

### 1. Create a Project

1. Navigate to the **Projects** page
2. Click **New Project**  
3. Enter project details:
   - **Name**: Your project name
   - **Path**: Absolute path to your codebase (no spaces or special characters)
   - **Description**: Optional description
4. Click **Create Project**

### 2. Run a Security Scan

1. Go to the **Dashboard**
2. Select your project from the dropdown
3. Click **Start Security Scan**
4. Watch real-time progress as scanners run
5. View results automatically when complete

### 3. Analyze Results

- **Dashboard**: High-level overview with health scores
- **Security Results**: Detailed findings with severity levels
- **Code Metrics**: Complexity and coverage analysis  
- **History**: Compare scans over time

### 4. Use AI Features (Optional)

On the Security Results page:
1. Click **Explain with AI** on any vulnerability
2. Get beginner-friendly explanation
3. View secure code fix suggestions
4. Copy fixes directly to your code

### 5. Export Reports

1. Navigate to scan results
2. Click **Export** button
3. Choose format (JSON or HTML)
4. Share with team or save for records

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Lightweight database
- **Bandit** - Python security scanner
- **Safety** - Dependency vulnerability scanner
- **Semgrep** - Multi-language static analyzer

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Lucide React** - Icons
- **Axios** - HTTP client
- **React Router** - Navigation

## 📊 Version 0.3.0 - Current Status

### ✅ Completed Features

**Core Security Scanning**
- [x] Bandit integration for Python security
- [x] Safety integration for dependency vulnerabilities  
- [x] Semgrep integration for multi-language analysis
- [x] Real-time scan progress tracking
- [x] Comprehensive error handling and logging

**AI Integration** (NEW in v0.3.0)
- [x] OpenRouter API integration
- [x] Automatic model fallback (4 models)
- [x] Vulnerability explanations in plain English
- [x] Secure code fix suggestions
- [x] Works offline without AI

**Code Quality Metrics**
- [x] Radon complexity analysis  
- [x] Pytest coverage integration
- [x] Health score calculation (A-F grades)
- [x] Per-file metrics breakdown

**Reporting & History**
- [x] JSON export
- [x] HTML export with embedded CSS
- [x] Scan comparison tool
- [x] Historical trend tracking

**User Interface**
- [x] Modern React dashboard
- [x] Real-time progress updates
- [x] Dark mode support
- [x] Responsive design
- [x] Gradient card designs

### 🚧 Roadmap (Future Versions)

**v0.4.0 - Mutation Testing**
- [ ] Mutmut integration for Python
- [ ] Test suite quality scoring
- [ ] Mutation coverage reports

**v0.5.0 - Enhanced Features**
- [ ] PDF report generation
- [ ] Scheduled scans
- [ ] Email notifications
- [ ] Multi-user support

**v1.0.0 - Production Ready**
- [ ] JavaScript/TypeScript mutation testing (Stryker)
- [ ] CI/CD integration (GitHub Actions, GitLab CI)
- [ ] VS Code extension
- [ ] Performance optimizations

## 🔐 Security Scanners

### Bandit
Scans Python code for common security issues:
- SQL injection
- Hard-coded passwords
- Use of exec/eval
- Weak cryptography
- And more...

### Safety
Checks Python dependencies against a database of known vulnerabilities:
- CVE database lookup
- Package version checks
- Security advisories

### Semgrep
Multi-language static analyzer with custom rules:
- Python, JavaScript, TypeScript, Go, and more
- OWASP Top 10 coverage
- Custom rule support

## 📊 Code Quality Metrics

### Radon - Complexity Analysis
- Measures cyclomatic complexity
- Identifies complex functions
- Recommends refactoring targets
- Per-file and per-function metrics

### Coverage.py - Test Coverage
- Line coverage percentage
- Shows untested code
- Integration with pytest
- Detailed per-file reports

### Health Score
Combined quality metric:
- **Formula**: `(Security Score + Coverage Score) / 2`
- **Security Score**: Based on vulnerability severity and count
- **Coverage Score**: Test coverage percentage  
- **Grades**: A (90+), B (80+), C (70+), D (60+), F (<60)
- **Trend Tracking**: See improvements over time

## 📁 Project Structure

```
asura/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes (projects, scans, metrics, reports)
│   │   ├── core/         # Core logic (scanner, metrics, llm_adapter, database)
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic (scan_service, project_service)
│   ├── tests/            # Backend tests
│   ├── logs/             # Scan logs (auto-generated)
│   ├── requirements.txt  # Python dependencies
│   └── .env.example      # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable React components
│   │   ├── pages/        # Page components (Dashboard, Projects, etc.)
│   │   ├── contexts/     # React contexts
│   │   └── lib/          # Utilities (API client, utils)
│   └── package.json      # Node dependencies
├── screenshots/          # UI screenshots
├── setup.bat             # Windows setup script
├── start.bat             # Windows start script  
├── LICENSE               # MIT License
├── CONTRIBUTING.md       # Contribution guidelines
└── CHANGELOG.md          # Version history
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Contribution Guide

1. **Fork & Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/asura.git
   ```

2. **Create Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Write tests
   - Follow code style
   - Update documentation

4. **Submit PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Areas We Need Help
- 📝 Writing Semgrep rules for new frameworks
- 🌍 Adding support for more languages (Go, Rust, Java)
- 🎨 UI/UX improvements
- 📚 Documentation and tutorials
- 🧪 Test coverage improvements

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**TL;DR**: Free to use, modify, and distribute. No warranty provided.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework
- [Bandit](https://bandit.readthedocs.io/) - Security linter
- [Safety](https://pyup.io/safety/) - Dependency checker
- [Semgrep](https://semgrep.dev/) - Static analyzer
- [React](https://react.dev/) - UI library
- [TailwindCSS](https://tailwindcss.com/) - CSS framework

## 📞 Support

- **Documentation**: See [QUICK_START.md](QUICK_START.md) and [GET_API_KEY.md](GET_API_KEY.md)
- **Bug Reports**: [Open an issue](https://github.com/ParthSalunkhe7052/Asura-Security-Scan/issues)
- **Feature Requests**: [Start a discussion](https://github.com/ParthSalunkhe7052/Asura-Security-Scan/discussions)
- **Security Issues**: Email parth.ajit7052@gmail.com (do NOT open public issues)

## 🗺️ Roadmap

See [CHANGELOG.md](CHANGELOG.md) for version history and upcoming features.

## 📊 Project Stats

- **Version**: 0.3.0
- **Language**: Python (Backend), JavaScript (Frontend)
- **License**: MIT
- **Status**: Active Development
- **First Release**: October 2025

## 🎯 Project Goals

ASURA aims to make security testing:
- **Accessible** - Free and open source, no expensive licenses
- **Educational** - Learn security concepts while scanning  
- **Practical** - Actionable results, not just noise
- **Private** - Your code never leaves your machine

---

**Built with ❤️ by Parth and Contributors**

*Making security testing accessible, educational, and private for developers everywhere.*

---

### ⭐ Star Us!

If you find ASURA useful, please consider giving us a star on GitHub. It helps others discover the project!
