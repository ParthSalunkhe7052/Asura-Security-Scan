# Changelog

All notable changes to ASURA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Mutation testing integration (Mutmut)
- JavaScript/TypeScript support
- PDF report generation
- Scheduled scans
- CI/CD pipeline integration

## [0.3.0] - 2025-11-03

### Added
- **AI Integration**: OpenRouter API integration with automatic model fallback
  - Primary model: `meta-llama/llama-3.2-3b-instruct:free`
  - Fallback to 3 alternative models if rate-limited
  - Vulnerability explanations and fix suggestions
- **Scan Comparison**: Compare two scans side-by-side
- **Enhanced Dashboard**: Modern UI with gradient cards and improved navigation
- **Rate Limiting**: 60 requests per minute per IP to prevent abuse
- **Request Size Limiting**: 10MB maximum request size
- **Comprehensive Logging**: All scanner outputs logged to `backend/logs/`

### Changed
- Updated API version to 0.3.0
- Improved error handling across all scanners
- Enhanced metrics computation with better timeout handling
- Modernized UI with Tailwind CSS gradients and hover effects

### Fixed
- **Scanner Integration**: Fixed all three security scanners (Bandit, Safety, Semgrep)
  - Added missing `pbr>=5.11.0` dependency for Bandit
  - Updated Safety parser for v2.3.5 JSON format
  - Fixed Semgrep to use direct executable instead of Python module
- **Encoding Issues**: Added UTF-8 encoding environment variables for all scanners
- **Metrics Timeout**: Added 120s timeout for Radon complexity analysis
- **Coverage Analysis**: Improved test directory detection and error handling

## [0.2.0] - 2025-10-25

### Added
- **Code Metrics**: Radon complexity analysis and pytest coverage tracking
- **Health Score**: Combined security and coverage score with A-F grading
- **Report Export**: JSON and HTML report generation
- **Metrics Dashboard**: Dedicated page for code quality metrics
- **Scan History**: View and track all scans over time
- **Progress Tracking**: Real-time scan progress updates

### Changed
- Restructured API endpoints for better organization
- Improved database schema with scan status tracking
- Enhanced UI with separate cards for each feature

### Fixed
- Path validation to prevent special characters causing errors
- Auto-selection of projects in dashboard
- Scanner error handling and partial completion status

## [0.1.0] - 2025-10-20

### Added
- **Initial Release** 🎉
- **Security Scanning**: Integrated Bandit, Safety, and Semgrep
- **Project Management**: Create and manage multiple projects
- **FastAPI Backend**: RESTful API with SQLAlchemy ORM
- **React Frontend**: Modern UI with React 18 and Vite
- **SQLite Database**: Lightweight local database
- **Vulnerability Tracking**: Store and display security findings
- **CORS Support**: Frontend-backend communication
- **API Documentation**: Auto-generated Swagger docs at `/docs`

### Security Scanners
- **Bandit**: Python security linter for common vulnerabilities
- **Safety**: Dependency vulnerability scanner using CVE database
- **Semgrep**: Multi-language static analyzer with custom rules

### UI Features
- Dashboard with project overview
- Projects page for managing projects
- Security results page with vulnerability details
- Scan history with timeline view
- Dark mode support
- Responsive design

---

## Version History

- **v0.3.0** (2025-11-03): AI Integration & Scanner Fixes
- **v0.2.0** (2025-10-25): Code Metrics & Health Scoring
- **v0.1.0** (2025-10-20): Initial Release

---

## Legend

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute to ASURA.

## Support

For issues and questions, please visit our [GitHub Issues](https://github.com/ParthSalunkhe7052/Asura-Security-Scan/issues) page.
