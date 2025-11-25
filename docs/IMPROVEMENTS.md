# Improvement Proposals for Asura

## A. Project Summary
*   **Core Function**: A local-first security orchestration tool that wraps Bandit (Python SAST), Safety (Python SCA), and Semgrep (Polyglot SAST) into a unified dashboard.
*   **Key Features**: Real-time scanning, AI-powered vulnerability explanations (OpenRouter), and code quality metrics (Radon/Coverage).
*   **Attack Surface**: Scans Python and JavaScript/TypeScript codebases.
*   **Reporting**: JSON and HTML exports; interactive React dashboard.
*   **Current CI**: GitHub Actions run internal tests and linters but do **not** use Asura to scan the codebase or block pull requests based on security findings.

## B. Capability Comparison

| Feature | Asura (Current) | SonarQube | Snyk | Semgrep (OSS/CLI) |
| :--- | :--- | :--- | :--- | :--- |
| **Deployment** | Local / Desktop | Server / Cloud | Cloud / CLI | CLI / Cloud |
| **Scan Coverage** | Python, JS/TS (SAST + SCA) | 30+ Languages | Broad SCA + SAST | 30+ Languages |
| **CI Integration** | None (Manual only) | Quality Gates | PR Checks | PR Comments |
| **Reporting** | Custom JSON/HTML | Dashboard / PDF | Dashboard / SBOM | SARIF / JSON |
| **Secrets Detection**| Pre-commit only | Plugin required | Native | Native |
| **IDE Integration** | None | Extensive | Extensive | Extensive |
| **Deduplication** | Basic (Scan History) | Advanced State | Advanced State | Rule-based |

## C. Prioritized Improvements

1.  **SARIF Report Export**
    *   **Why**: Enables integration with GitHub Security tab, GitLab Security Dashboard, and VS Code extensions.
    *   **Complexity**: Low
    *   **Effort**: 4–8 hours
    *   **Resource Impact**: Low
    *   **Steps**:
        1.  Create a Pydantic model for the SARIF 2.1.0 schema in `backend/app/schemas/sarif.py`.
        2.  Implement a converter function in `backend/app/services/report_service.py` that maps internal `Vulnerability` objects to SARIF `runs` and `results`.
        3.  Add a `--format sarif` option to the export logic.
        4.  Verify by uploading a generated file to a GitHub repository's "Code Scanning" alerts.
    *   **Acceptance Criteria**: Running `asura export --format sarif` generates a valid JSON file that passes the SARIF validator and can be uploaded to GitHub.
    *   **Follow-up**: Add support for GitLab's Code Quality JSON format.

2.  **Headless CLI Mode**
    *   **Why**: Allows running scans in CI/CD pipelines without starting the web server or UI.
    *   **Complexity**: Low
    *   **Effort**: 6–10 hours
    *   **Resource Impact**: Low
    *   **Steps**:
        1.  Create `backend/app/cli.py` using `argparse` or `typer`.
        2.  Import `SecurityScanner` from `app.core.scanner`.
        3.  Implement a `scan` command that accepts a path and exit code thresholds (e.g., `--fail-on HIGH`).
        4.  Expose via `python -m app.cli` entry point.
    *   **Acceptance Criteria**: Running `python -m app.cli scan .` prints results to stdout and returns exit code 0 (pass) or 1 (fail) based on findings.
    *   **Follow-up**: Add a progress bar using `tqdm` for the CLI.

3.  **GitHub Actions Security Gate**
    *   **Why**: Automatically blocks pull requests that introduce new high-severity vulnerabilities.
    *   **Complexity**: Low
    *   **Effort**: 2–4 hours
    *   **Resource Impact**: Low (Runs on ephemeral runners)
    *   **Steps**:
        1.  Create `.github/workflows/security-scan.yml`.
        2.  Use the new CLI mode (Improvement #2) to scan the repo on `pull_request`.
        3.  Configure it to fail the build if `CRITICAL` or `HIGH` issues are found.
        4.  Upload the SARIF artifact (Improvement #1) using `github/codeql-action/upload-sarif`.
    *   **Acceptance Criteria**: A PR with a known vulnerability (e.g., hardcoded password) fails the GitHub Action check.
    *   **Follow-up**: Add a job summary step to display results directly in the GitHub Actions UI summary.

4.  **Runtime Secrets Scanning**
    *   **Why**: `detect-secrets` is currently only in pre-commit; missing it in the dashboard leaves a gap for checked-in secrets.
    *   **Complexity**: Medium
    *   **Effort**: 8–12 hours
    *   **Resource Impact**: Low
    *   **Steps**:
        1.  Add `detect-secrets` wrapper to `backend/app/core/scanner.py` (similar to Bandit/Safety wrappers).
        2.  Parse the baseline or raw output into the standard `Vulnerability` format.
        3.  Map results to a new "SECRETS" category in the dashboard.
    *   **Acceptance Criteria**: A file containing `AWS_ACCESS_KEY_ID = "AKIA..."` is flagged in the dashboard as a "High" severity issue.
    *   **Follow-up**: Allow users to mark false positives in the UI (stored in local DB).

5.  **Frontend Dependency Scanning (SCA)**
    *   **Why**: Currently `Safety` only checks Python `requirements.txt`; `package.json` is ignored.
    *   **Complexity**: Medium
    *   **Effort**: 6–10 hours
    *   **Resource Impact**: Low
    *   **Steps**:
        1.  Add a check for `package.json` in `scanner.py`.
        2.  Implement a wrapper for `npm audit --json` (or `yarn audit`).
        3.  Parse the nested JSON output and map to Asura's severity levels.
    *   **Acceptance Criteria**: A project with a vulnerable `package.json` (e.g., old lodash) shows vulnerabilities in the Asura dashboard.
    *   **Follow-up**: Add support for `yarn.lock` or `pnpm-lock.yaml`.

6.  **Dockerized Runner**
    *   **Why**: Eliminates "works on my machine" issues and simplifies CI setup (no need to install Python/Node manually).
    *   **Complexity**: Medium
    *   **Effort**: 4–6 hours
    *   **Resource Impact**: Medium (Image storage)
    *   **Steps**:
        1.  Create a `Dockerfile` that installs Python, Node, and all scanner dependencies.
        2.  Set the entrypoint to the new CLI tool.
        3.  Publish to GHCR or Docker Hub.
    *   **Acceptance Criteria**: `docker run -v $(pwd):/app asura/scanner` runs the scan and outputs results without any local installation.
    *   **Follow-up**: Publish a "slim" tag with fewer dependencies for faster downloads.

7.  **Ignore File Support (.asuraignore)**
    *   **Why**: Users need to suppress false positives or ignore specific test directories persistently.
    *   **Complexity**: Low
    *   **Effort**: 2–4 hours
    *   **Resource Impact**: Low
    *   **Steps**:
        1.  Update `get_scannable_files` in `scanner.py` to look for `.asuraignore`.
        2.  Implement `gitignore`-style pattern matching (using `pathspec` library).
        3.  Filter file lists before passing them to scanners.
    *   **Acceptance Criteria**: Files listed in `.asuraignore` are not present in the scan results or logs.
    *   **Follow-up**: Add a UI editor for the `.asuraignore` file.

8.  **Status Badge Generation**
    *   **Why**: Provides immediate visual feedback on project security health in the README.
    *   **Complexity**: Low
    *   **Effort**: 2–4 hours
    *   **Resource Impact**: Low
    *   **Steps**:
        1.  Use a library like `anybadge` or generate simple SVG strings.
        2.  Create a badge based on the "Health Score" (A-F).
        3.  Save `security-badge.svg` to the project root after a scan.
    *   **Acceptance Criteria**: A `security-badge.svg` file is created in the root directory after a scan completes.
    *   **Follow-up**: Add a "Security Score" badge (e.g., "95/100") in addition to the grade.

## D. What NOT to Do

1.  **Build a Multi-User SaaS Platform**: Do not add user authentication, role-based access control (RBAC), or centralized database servers (PostgreSQL). This defeats the "local-first" privacy value proposition and drastically increases engineering/maintenance cost.
2.  **Write Custom Static Analysis Engines**: Do not attempt to write custom regex-based scanners for languages. It is brittle and high-maintenance. Rely on extending Semgrep rules instead.
3.  **Real-time IDE Plugin (from scratch)**: Building a VS Code extension that communicates with the local Python backend is complex and error-prone (port conflicts, process management). Stick to CLI/CI integration first.

## E. Implementation Example: SARIF Export & CLI

**Implementation Checklist**
- [ ] **Schema**: Define `SarifReport` Pydantic models in `backend/app/schemas/sarif.py`.
- [ ] **Converter**: Implement `convert_to_sarif()` in `backend/app/services/report_service.py`.
- [ ] **CLI**: Create `backend/app/cli.py` with `scan` command and exit codes.
- [ ] **Entry Point**: Expose `python -m app.cli` in `backend/__main__.py` or similar.
- [ ] **CI**: Add `.github/workflows/security.yml` to run the CLI on PRs.

### 1. SARIF Schema (backend/app/schemas/sarif.py)
```python
from typing import List, Optional
from pydantic import BaseModel

class SarifResult(BaseModel):
    ruleId: str
    level: str  # "error", "warning", "note"
    message: dict
    locations: List[dict]

class SarifRun(BaseModel):
    tool: dict
    results: List[SarifResult]

class SarifReport(BaseModel):
    version: str = "2.1.0"
    $schema: str = "https://json.schemastore.org/sarif-2.1.0.json"
    runs: List[SarifRun]
```

### 2. CLI Entry Point (backend/app/cli.py)
```python
import argparse
import sys
import json
from pathlib import Path
from app.core.scanner import SecurityScanner
from app.services.report_service import convert_to_sarif

def main():
    parser = argparse.ArgumentParser(description="Asura Security Scanner CLI")
    parser.add_argument("path", help="Path to project to scan")
    parser.add_argument("--format", choices=["json", "sarif", "text"], default="text")
    parser.add_argument("--fail-on", choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"], help="Exit with error if severity found")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    print(f"🚀 Starting scan on {args.path}...")
    scanner = SecurityScanner(args.path)
    results = scanner.run_all()
    
    # Handle Output
    if args.format == "sarif":
        output_data = convert_to_sarif(results)
        output_str = json.dumps(output_data, indent=2)
    else:
        output_str = json.dumps(results, indent=2)

    if args.output:
        Path(args.output).write_text(output_str, encoding="utf-8")
        print(f"📄 Report saved to {args.output}")
    elif args.format != "text":
        print(output_str)

    # Handle Exit Code
    severity_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    threshold = severity_map.get(args.fail_on, 5)
    
    max_severity = 0
    for vuln in results["vulnerabilities"]:
        s = severity_map.get(vuln["severity"], 0)
        if s > max_severity:
            max_severity = s
            
    if args.fail_on and max_severity >= threshold:
        print(f"❌ Failed: Found issues of severity {args.fail_on} or higher.")
        sys.exit(1)
        
    print("✅ Scan passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### 3. GitHub Action Workflow (.github/workflows/security.yml)
```yaml
name: Security Scan
on: [pull_request]

jobs:
  asura-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install Asura
        run: |
          pip install -r backend/requirements.txt
          
      - name: Run Scan
        run: |
          # Run scan, fail on HIGH, output SARIF
          python -m backend.app.cli . --format sarif --output results.sarif --fail-on HIGH
        env:
          PYTHONPATH: backend
          
      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: results.sarif
```
