import subprocess
import json
import os
import sys
from typing import List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
import argparse
import fnmatch
from app.utils.path_validator import PathValidator
from app.utils.path_validator import PathValidator
from app.utils.dependency_checker import DependencyChecker
from app.utils.badge_generator import generate_badge
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed


def validate_scanner_path(path: str) -> tuple:
    """
    Validate project path for security scanning.
    Returns: (is_valid, error_message)
    
    This function now uses PathValidator for enhanced security.
    """
    allowed_roots = PathValidator.get_allowed_roots_from_env()
    is_valid, error_msg, resolved_path = PathValidator.sanitize_and_validate(path, allowed_roots)
    
    if not is_valid:
        return False, error_msg
    
    return True, ""


def get_scannable_files(project_path: Path, max_files: int = 1000) -> Dict[str, List[Path]]:
    """
    Intelligently filter files for security scanning.
    Returns dict with 'python', 'javascript', 'other' file lists.
    
    Strategy:
    - Skip node_modules, venv, build dirs
    - Skip minified and bundled files
    - Skip files > 1MB (likely generated)
    - Prioritize source directories
    - Limit total files to prevent timeouts
    """
    skip_dirs = {
        'node_modules', 'venv', '.venv', 'env', 'ENV',
        'build', 'dist', '.git', '__pycache__', '.pytest_cache',
        'site-packages', '.tox', '.eggs', 'vendor', 'packages',
        'bower_components', '.next', '.nuxt', 'coverage',
        'tmp', 'temp', 'cache', '.cache', 'logs', 'log'
    }
    
    skip_patterns = {
        '*.min.js', '*.min.css', '*.bundle.js', '*.chunk.js',
        '*.map', '*.lock', '*.sum', '*.log', '*.pyc', '*.pyo',
        '*.svg', '*.png', '*.jpg', '*.jpeg', '*.gif',
        '*.woff', '*.woff2', '*.ttf', '*.eot', '*.ico'
    }

    # Load .asuraignore patterns
    ignore_file = project_path / ".asuraignore"
    if ignore_file.exists():
        try:
            with open(ignore_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        skip_patterns.add(line)
                        # Also add directory exclusion if it looks like a dir
                        if line.endswith('/'):
                            skip_dirs.add(line.rstrip('/'))
            print(f"📋 Loaded ignore patterns from .asuraignore")
        except Exception as e:
            print(f"⚠️  Error reading .asuraignore: {e}")
    
    scannable_extensions = {
        '.py', '.js', '.jsx', '.ts', '.tsx', '.vue',
        '.java', '.cpp', '.c', '.h', '.hpp',
        '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt'
    }
    
    python_files = []
    javascript_files = []
    other_files = []
    
    def should_skip_file(file_path: Path) -> bool:
        """Check if file should be skipped"""
        try:
            # Skip large files (> 1MB)
            if file_path.stat().st_size > 1_000_000:
                return True
        except:
            return True
        
        # Check skip patterns
        name = file_path.name
        for pattern in skip_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
        
        # Only scan known source extensions
        return file_path.suffix not in scannable_extensions
    
    print(f"🔍 Scanning for source files in: {project_path.name}")
    
    try:
        for root, dirs, files in os.walk(project_path):
            # Skip directories
            dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
            
            for file in files:
                file_path = Path(root) / file
                
                if should_skip_file(file_path):
                    continue
                
                # Categorize by language
                if file_path.suffix == '.py':
                    python_files.append(file_path)
                elif file_path.suffix in {'.js', '.jsx', '.ts', '.tsx', '.vue'}:
                    javascript_files.append(file_path)
                else:
                    other_files.append(file_path)
                
                # Stop if we have too many files
                total = len(python_files) + len(javascript_files) + len(other_files)
                if total >= max_files:
                    break
            
            if len(python_files) + len(javascript_files) + len(other_files) >= max_files:
                break
    
    except Exception as e:
        print(f"⚠️  Error scanning files: {e}")
    
    print(f"📁 Found scannable files:")
    print(f"   ├─ Python: {len(python_files)}")
    print(f"   ├─ JavaScript/TypeScript: {len(javascript_files)}")
    print(f"   └─ Other: {len(other_files)}")
    
    return {
        'python': python_files[:500],  # Limit each category
        'javascript': javascript_files[:500],
        'other': other_files[:500]
    }


class SecurityScanner:
    """Unified security scanner interface with robust error handling and logging"""
    
    def __init__(self, project_path: str, scan_id: str = None):
        self.project_path = Path(project_path)
        
        # Validate path strictly
        is_valid, error_msg = validate_scanner_path(str(self.project_path))
        if not is_valid:
            raise ValueError(error_msg)
        
        self.scan_id = scan_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logs_dir = Path("logs/scans")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Progress tracking for live updates
        self.progress_messages = []
        
        # Get filtered list of files to scan (prevents timeout on large projects)
        self.scannable_files = get_scannable_files(self.project_path, max_files=1000)
        
        # Load timeout configuration from environment variables
        self.bandit_timeout = int(os.environ.get('BANDIT_TIMEOUT', '120'))
        self.safety_timeout = int(os.environ.get('SAFETY_TIMEOUT', '60'))
        self.semgrep_timeout = int(os.environ.get('SEMGREP_TIMEOUT', '180'))
        self.detect_secrets_timeout = int(os.environ.get('DETECT_SECRETS_TIMEOUT', '60'))
        self.npm_timeout = int(os.environ.get('NPM_TIMEOUT', '120'))
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, OSError)),
        reraise=True
    )
    def _run_subprocess_with_retry(self, cmd, timeout, env=None, **kwargs):
        """
        Run subprocess with automatic retry on transient failures.
        Retries up to 3 times with exponential backoff (2s, 4s, 8s).
        
        SECURITY: This method is safe because:
        - All commands passed to it are constructed with controlled inputs
        - Uses sys.executable (system Python interpreter)
        - Uses validated, filtered file paths from get_scannable_files()
        - Uses hardcoded scanner tool names (bandit, safety, semgrep)
        - No user-controllable input reaches subprocess
        - Never uses shell=True
        """
        try:
            result = subprocess.run(  # nosec B603
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                encoding='utf-8',
                errors='replace',
                env=env or os.environ.copy(),
                **kwargs
            )
            return result
        except (ConnectionError, OSError) as e:
            # Log retry attempt
            logging.warning(f"Subprocess call failed, will retry: {e}")
            raise
    
    def run_bandit(self) -> Tuple[List[Dict[str, Any]], str]:
        """Run Bandit security scanner for Python code
        Returns: (vulnerabilities, status_message)
        """
        tool_name = "bandit"
        try:
            # Get only Python files from filtered list
            python_files = self.scannable_files.get('python', [])
            
            if not python_files:
                msg = "No Python files found to scan with Bandit"
                print(f"ℹ️  {msg}")
                return [], msg
            
            msg = f"🔍 Running Bandit on {len(python_files)} Python files"
            print(msg)
            self.progress_messages.append(msg)
            
            # Run bandit on specific files (not recursive directory scan)
            cmd = [
                sys.executable, "-m", "bandit",
                "-f", "json"
            ]
            
            # Check if .bandit configuration file exists in project root
            # This suppresses false positives like B101 (assert in tests)
            bandit_config = self.project_path / ".bandit"
            if bandit_config.exists():
                cmd.extend(["-c", str(bandit_config)])
                print(f"📋 Using Bandit configuration: {bandit_config.name}")
                self.progress_messages.append(f"Using Bandit config to suppress false positives")
            
            # Add files to scan
            cmd.extend([str(f) for f in python_files])
            
            result = self._run_subprocess_with_retry(cmd, timeout=self.bandit_timeout)
            
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            # Save raw outputs for debugging
            self._save_output(tool_name, stdout, stderr, result.returncode)
            
            if not stdout:
                error_msg = f"Bandit returned empty output. Return code: {result.returncode}"
                if stderr:
                    error_msg += f"\nStderr: {stderr[:500]}"
                print(f"❌ {error_msg}")
                return [], error_msg
            
            # Handle very large outputs (>5MB) - likely from scanning large codebases
            if len(stdout) > 5_000_000:
                error_msg = f"Bandit output too large ({len(stdout):,} bytes). Consider scanning smaller directories."
                print(f"⚠️  {error_msg}")
                self._save_raw_output(tool_name, "too_large", f"Output size: {len(stdout)} bytes\nTruncated for safety.")
                return [], error_msg
            
            try:
                data = json.loads(stdout)
            except json.JSONDecodeError as e:
                error_msg = f"Bandit JSON parse error: {e}. Stdout length: {len(stdout):,} bytes"
                print(f"❌ {error_msg}")
                # Try to truncate and show a helpful message
                preview = stdout[:1000] + "..." if len(stdout) > 1000 else stdout
                self._save_raw_output(tool_name, "unparseable", f"Parse Error: {e}\n\nOutput Preview:\n{preview}")
                return [], error_msg
            
            vulnerabilities = []
            for item in data.get("results", []):
                vulnerabilities.append({
                    "tool": "bandit",
                    "severity": self._map_bandit_severity(item.get("issue_severity")),
                    "file_path": item.get("filename", ""),
                    "line_number": item.get("line_number"),
                    "vulnerability_type": item.get("test_id", "UNKNOWN"),
                    "description": item.get("issue_text", ""),
                    "code_snippet": item.get("code", ""),
                    "cwe_id": item.get("issue_cwe", {}).get("id") if isinstance(item.get("issue_cwe"), dict) else None,
                    "confidence": item.get("issue_confidence", "")
                })
            
            msg = f"✅ Bandit: {len(vulnerabilities)} issues found"
            print(msg)
            self.progress_messages.append(msg)
            return vulnerabilities, "success"
            
        except subprocess.TimeoutExpired:
            error_msg = f"Bandit scan timed out ({self.bandit_timeout}s)"
            print(f"⚠️  {error_msg}")
            return [], error_msg
        except FileNotFoundError:
            error_msg = "Bandit not installed. Run: pip install bandit"
            print(f"❌ {error_msg}")
            return [], error_msg
        except Exception as e:
            error_msg = f"Bandit scan failed: {type(e).__name__}: {e}"
            print(f"❌ {error_msg}")
            return [], error_msg
    
    def run_safety(self) -> Tuple[List[Dict[str, Any]], str]:
        """Run Safety scanner for dependency vulnerabilities
        Returns: (vulnerabilities, status_message)
        """
        tool_name = "safety"
        try:
            # Look for requirements.txt
            req_file = self.project_path / "requirements.txt"
            if not req_file.exists():
                msg = "No requirements.txt found, skipping Safety scan"
                print(f"ℹ️  {msg}")
                return [], msg
            
            # Validate requirements.txt is readable with UTF-8
            try:
                with open(req_file, 'r', encoding='utf-8', errors='strict') as f:
                    f.read()
            except UnicodeDecodeError as e:
                error_msg = f"requirements.txt has invalid UTF-8 encoding: {e}"
                print(f"⚠️  {error_msg}")
                # Try to read with error handling and create a clean temp file
                try:
                    with open(req_file, 'r', encoding='utf-8', errors='replace') as f:
                        clean_content = f.read()
                    # Create a temporary clean file
                    import tempfile
                    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
                    temp_file.write(clean_content)
                    temp_file.close()
                    req_file = Path(temp_file.name)
                    print(f"ℹ️  Created cleaned requirements file at: {req_file}")
                except Exception as clean_err:
                    error_msg = f"Could not clean requirements.txt: {clean_err}"
                    print(f"❌ {error_msg}")
                    return [], error_msg
            
            cmd = [sys.executable, "-m", "safety", "check", "--file", str(req_file), "--json"]
            msg = f"🔍 Running: {' '.join(cmd)}"
            print(msg)
            self.progress_messages.append(msg)
            
            # Set UTF-8 encoding environment variables to help Safety
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            result = self._run_subprocess_with_retry(cmd, timeout=self.safety_timeout, env=env)
            
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            self._save_output(tool_name, stdout, stderr, result.returncode)
            
            if not stdout:
                # Safety returns exit code 0 when no vulnerabilities found
                if result.returncode == 0:
                    msg = "✅ Safety: 0 vulnerabilities found"
                    print(msg)
                    self.progress_messages.append(msg)
                    return [], "success"
                else:
                    error_msg = f"Safety returned empty output with code {result.returncode}"
                    if stderr:
                        error_msg += f"\nStderr: {stderr[:500]}"
                    print(f"❌ {error_msg}")
                    return [], error_msg
            
            try:
                data = json.loads(stdout)
            except json.JSONDecodeError as e:
                error_msg = f"Safety JSON parse error: {e}"
                print(f"❌ {error_msg}")
                self._save_raw_output(tool_name, "unparseable", stdout)
                return [], error_msg
            
            vulnerabilities = []
            
            # Safety 2.3.5+ uses a new JSON format with separate vulnerabilities array
            if isinstance(data, dict) and "vulnerabilities" in data:
                # New format: {vulnerabilities: [{vulnerability_id, package_name, CVE, advisory, ...}]}
                for vuln in data.get("vulnerabilities", []):
                    package_name = vuln.get("package_name", "unknown")
                    vuln_id = vuln.get("vulnerability_id", "unknown")
                    cve = vuln.get("CVE", "")
                    advisory = vuln.get("advisory", "No description available")
                    analyzed_version = vuln.get("analyzed_version", "unknown")
                    more_info = vuln.get("more_info_url", "")
                    
                    # Truncate long advisories
                    if len(advisory) > 300:
                        advisory = advisory[:297] + "..."
                    
                    vulnerabilities.append({
                        "tool": "safety",
                        "severity": "HIGH",  # Safety reports all as high severity
                        "file_path": "requirements.txt",
                        "line_number": None,
                        "vulnerability_type": f"{cve}_{vuln_id}" if cve else f"SAFETY_{vuln_id}",
                        "description": f"{package_name} {analyzed_version}: {advisory}",
                        "code_snippet": f"{package_name}=={analyzed_version}",
                        "cwe_id": None,
                        "confidence": "HIGH"
                    })
            elif isinstance(data, list):
                # Old format: list of vulnerability objects
                for item in data:
                    vulnerabilities.append({
                        "tool": "safety",
                        "severity": self._map_safety_severity(item),
                        "file_path": "requirements.txt",
                        "line_number": None,
                        "vulnerability_type": f"VULNERABLE_DEPENDENCY_{item.get('package', 'UNKNOWN')}",
                        "description": f"{item.get('package', 'Unknown package')} {item.get('installed_version', '')} - {item.get('vulnerability', 'No description')}",
                        "code_snippet": f"{item.get('package', '')}=={item.get('installed_version', '')}",
                        "cwe_id": None,
                        "confidence": "HIGH"
                    })
            
            msg = f"✅ Safety: {len(vulnerabilities)} vulnerabilities found"
            print(msg)
            self.progress_messages.append(msg)
            return vulnerabilities, "success"
            
        except subprocess.TimeoutExpired:
            error_msg = f"Safety scan timed out ({self.safety_timeout}s)"
            print(f"⚠️  {error_msg}")
            return [], error_msg
        except FileNotFoundError:
            error_msg = "Safety not installed. Run: pip install safety"
            print(f"❌ {error_msg}")
            return [], error_msg
        except Exception as e:
            error_msg = f"Safety scan failed: {type(e).__name__}: {e}"
            print(f"❌ {error_msg}")
            return [], error_msg
    
    def run_semgrep(self) -> Tuple[List[Dict[str, Any]], str]:
        """Run Semgrep static analyzer
        Returns: (vulnerabilities, status_message)
        """
        tool_name = "semgrep"
        try:
            # Get all scannable files (semgrep supports multiple languages)
            all_files = []
            for file_list in self.scannable_files.values():
                all_files.extend(file_list)
            
            if not all_files:
                msg = "No source files found to scan with Semgrep"
                print(f"ℹ️  {msg}")
                return [], msg
            
            msg = f"🔍 Running Semgrep on {len(all_files)} files"
            print(msg)
            self.progress_messages.append(msg)
            
            # Semgrep 1.38.0+ deprecates python -m usage, use direct executable
            import shutil
            venv_scripts = Path(sys.executable).parent
            
            # Try venv semgrep.exe first (Windows), then system PATH
            semgrep_exe = venv_scripts / "semgrep.exe"
            semgrep_unix = venv_scripts / "semgrep"
            
            if semgrep_exe.exists():
                # Windows: use semgrep.exe directly
                cmd = [str(semgrep_exe), "--config=auto", "--json"]
            elif semgrep_unix.exists() and semgrep_unix.is_file():
                # Unix: use semgrep script
                cmd = [str(semgrep_unix), "--config=auto", "--json"]
            elif shutil.which("semgrep"):
                # System-wide semgrep
                cmd = ["semgrep", "--config=auto", "--json"]
            else:
                # Fallback to python -m (will show deprecation warning)
                cmd = [sys.executable, "-m", "semgrep", "--config=auto", "--json"]
            
            # Add specific files to scan (not directory)
            cmd.extend([str(f) for f in all_files])
            
            # Set UTF-8 encoding environment variables to help Semgrep
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            result = self._run_subprocess_with_retry(cmd, timeout=self.semgrep_timeout, env=env)
            
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            self._save_output(tool_name, stdout, stderr, result.returncode)
            
            if not stdout:
                error_msg = f"Semgrep returned empty output. Return code: {result.returncode}"
                if stderr:
                    error_msg += f"\nStderr: {stderr[:500]}"
                print(f"❌ {error_msg}")
                return [], error_msg
            
            try:
                data = json.loads(stdout)
            except json.JSONDecodeError as e:
                error_msg = f"Semgrep JSON parse error: {e}"
                print(f"❌ {error_msg}")
                self._save_raw_output(tool_name, "unparseable", stdout)
                return [], error_msg
            
            vulnerabilities = []
            for item in data.get("results", []):
                vulnerabilities.append({
                    "tool": "semgrep",
                    "severity": self._map_semgrep_severity(item.get("extra", {}).get("severity", "INFO")),
                    "file_path": item.get("path", ""),
                    "line_number": item.get("start", {}).get("line"),
                    "vulnerability_type": item.get("check_id", "UNKNOWN"),
                    "description": item.get("extra", {}).get("message", ""),
                    "code_snippet": item.get("extra", {}).get("lines", ""),
                    "cwe_id": None,
                    "confidence": "MEDIUM"
                })
            
            msg = f"✅ Semgrep: {len(vulnerabilities)} issues found"
            print(msg)
            self.progress_messages.append(msg)
            return vulnerabilities, "success"
            
        except subprocess.TimeoutExpired:
            error_msg = f"Semgrep scan timed out ({self.semgrep_timeout}s) even after filtering"
            print(f"⚠️  {error_msg}")
            return [], error_msg
        except FileNotFoundError:
            error_msg = "Semgrep not installed. Run: pip install semgrep"
            print(f"❌ {error_msg}")
            return [], error_msg
        except Exception as e:
            error_msg = f"Semgrep scan failed: {type(e).__name__}: {e}"
            print(f"❌ {error_msg}")
            return [], error_msg

    def run_detect_secrets(self) -> Tuple[List[Dict[str, Any]], str]:
        """Run detect-secrets to find hardcoded secrets
        Returns: (vulnerabilities, status_message)
        """
        tool_name = "detect-secrets"
        try:
            # We scan the whole project
            cmd = [sys.executable, "-m", "detect_secrets", "scan", str(self.project_path), "--all-files"]
            
            msg = f"🔍 Running detect-secrets on project"
            print(msg)
            self.progress_messages.append(msg)
            
            result = self._run_subprocess_with_retry(cmd, timeout=self.detect_secrets_timeout)
            
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            self._save_output(tool_name, stdout, stderr, result.returncode)
            
            if not stdout:
                # detect-secrets might return empty JSON if no secrets?
                # Actually it returns a JSON with "results": {}
                # If completely empty, it's an error
                error_msg = f"detect-secrets returned empty output. Return code: {result.returncode}"
                if stderr:
                    error_msg += f"\nStderr: {stderr[:500]}"
                print(f"❌ {error_msg}")
                return [], error_msg
                
            try:
                data = json.loads(stdout)
            except json.JSONDecodeError as e:
                error_msg = f"detect-secrets JSON parse error: {e}"
                print(f"❌ {error_msg}")
                self._save_raw_output(tool_name, "unparseable", stdout)
                return [], error_msg
                
            vulnerabilities = []
            results = data.get("results", {})
            
            for file_path, secrets in results.items():
                for secret in secrets:
                    vulnerabilities.append({
                        "tool": "detect-secrets",
                        "severity": "HIGH", # Secrets are always high/critical
                        "file_path": file_path,
                        "line_number": secret.get("line_number"),
                        "vulnerability_type": secret.get("type", "Secret"),
                        "description": f"Potential {secret.get('type', 'secret')} found. Hash: {secret.get('hashed_secret', '')[:8]}...",
                        "code_snippet": "REDACTED", # Don't show the secret
                        "cwe_id": "CWE-798", # Use of Hard-coded Credentials
                        "confidence": "HIGH"
                    })
            
            msg = f"✅ detect-secrets: {len(vulnerabilities)} secrets found"
            print(msg)
            self.progress_messages.append(msg)
            return vulnerabilities, "success"
            
        except subprocess.TimeoutExpired:
            error_msg = f"detect-secrets scan timed out ({self.detect_secrets_timeout}s)"
            print(f"⚠️  {error_msg}")
            return [], error_msg
        except FileNotFoundError:
            error_msg = "detect-secrets not installed. Run: pip install detect-secrets"
            print(f"❌ {error_msg}")
            return [], error_msg
        except Exception as e:
            error_msg = f"detect-secrets scan failed: {type(e).__name__}: {e}"
            print(f"❌ {error_msg}")
            return [], error_msg

    def run_npm_audit(self) -> Tuple[List[Dict[str, Any]], str]:
        """Run npm audit for JavaScript/TypeScript dependency vulnerabilities
        Returns: (vulnerabilities, status_message)
        """
        tool_name = "npm-audit"
        try:
            # Look for package.json
            package_json = self.project_path / "package.json"
            if not package_json.exists():
                # Try finding it in subdirectories (e.g. frontend/)
                found = list(self.project_path.glob("**/package.json"))
                # Filter out node_modules
                found = [p for p in found if "node_modules" not in p.parts]
                
                if not found:
                    msg = "No package.json found, skipping npm audit"
                    print(f"ℹ️  {msg}")
                    return [], msg
                package_json = found[0]
                
            project_dir = package_json.parent
            msg = f"🔍 Running npm audit in {project_dir.name}"
            print(msg)
            self.progress_messages.append(msg)
            
            # Run npm audit --json
            # We need shell=True on Windows for npm sometimes, but let's try without first or use shutil.which
            npm_cmd = "npm"
            if os.name == 'nt':
                npm_cmd = "npm.cmd"
                
            cmd = [npm_cmd, "audit", "--json"]
            
            result = self._run_subprocess_with_retry(cmd, timeout=self.npm_timeout, cwd=str(project_dir))
            
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            self._save_output(tool_name, stdout, stderr, result.returncode)
            
            if not stdout:
                error_msg = f"npm audit returned empty output. Return code: {result.returncode}"
                if stderr:
                    error_msg += f"\nStderr: {stderr[:500]}"
                print(f"❌ {error_msg}")
                return [], error_msg
                
            try:
                data = json.loads(stdout)
            except json.JSONDecodeError as e:
                error_msg = f"npm audit JSON parse error: {e}"
                print(f"❌ {error_msg}")
                self._save_raw_output(tool_name, "unparseable", stdout)
                return [], error_msg
                
            vulnerabilities = []
            
            # npm audit json structure:
            # { "advisories": { ... }, "metadata": { ... } } (v6)
            # { "vulnerabilities": { ... }, "metadata": { ... } } (v7+)
            
            vuln_dict = data.get("vulnerabilities", {})
            if not vuln_dict and "advisories" in data:
                vuln_dict = data.get("advisories", {})
                
            # Flatten the recursive structure if needed, or just take top-level
            # v7+ structure is complex. Let's try to extract basic info.
            
            def extract_vulns(v_data):
                extracted = []
                if isinstance(v_data, dict):
                    for name, info in v_data.items():
                        if isinstance(info, dict):
                            severity = info.get("severity", "low").upper()
                            if severity == "MODERATE": severity = "MEDIUM"
                            
                            # v7+ has 'via' which lists sources
                            via = info.get("via", [])
                            description = "Vulnerable dependency"
                            if isinstance(via, list) and via and isinstance(via[0], dict):
                                description = via[0].get("title", description)
                            elif isinstance(via, list) and via and isinstance(via[0], str):
                                description = f"Depends on vulnerable {via[0]}"
                                
                            extracted.append({
                                "tool": "npm-audit",
                                "severity": severity,
                                "file_path": "package.json",
                                "line_number": None,
                                "vulnerability_type": "VULNERABLE_DEPENDENCY",
                                "description": f"{name}: {description}",
                                "code_snippet": f"{name} (version check)",
                                "cwe_id": None,
                                "confidence": "HIGH"
                            })
                return extracted

            vulnerabilities = extract_vulns(vuln_dict)
            
            msg = f"✅ npm-audit: {len(vulnerabilities)} issues found"
            print(msg)
            self.progress_messages.append(msg)
            return vulnerabilities, "success"
            
        except subprocess.TimeoutExpired:
            error_msg = f"npm audit timed out ({self.npm_timeout}s)"
            print(f"⚠️  {error_msg}")
            return [], error_msg
        except FileNotFoundError:
            error_msg = "npm not found. Install Node.js"
            print(f"❌ {error_msg}")
            return [], error_msg
        except Exception as e:
            error_msg = f"npm audit failed: {type(e).__name__}: {e}"
            print(f"❌ {error_msg}")
            return [], error_msg
    
    def run_all(self, progress_callback=None) -> Dict[str, Any]:
        """Run all security scanners with detailed status tracking"""
        msg1 = f"🔍 Starting security scan on: {self.project_path.name}"
        msg2 = f"📝 Scan ID: {self.scan_id}"
        msg3 = f"📂 Logs: {self.logs_dir}"
        msg4 = ""
        print(msg1)
        print(msg2)
        print(msg3)
        self.progress_messages.extend([msg1, msg2, msg3, msg4])
        
        # Initial progress update
        if progress_callback:
            progress_callback('\n'.join(self.progress_messages))
        
        # Run scanners in parallel using ThreadPoolExecutor
        self.progress_messages.append("🚀 Running all scanners in parallel for faster results...")
        if progress_callback:
            progress_callback('\n'.join(self.progress_messages))
        
        # Check scanner availability and filter out unavailable ones
        available_scanners = {}
        unavailable_scanners = {}
        
        all_scanners = {
            "bandit": self.run_bandit,
            "safety": self.run_safety,
            "semgrep": self.run_semgrep,
            "detect-secrets": self.run_detect_secrets,
            "npm-audit": self.run_npm_audit
        }
        
        for scanner_name, scanner_func in all_scanners.items():
            if DependencyChecker.is_scanner_available(scanner_name):
                available_scanners[scanner_name] = scanner_func
            else:
                unavailable_scanners[scanner_name] = "not installed"
                msg = f"⚠️  {scanner_name.capitalize()} not available - skipping"
                print(msg)
                self.progress_messages.append(msg)
        
        # If no scanners available, return early with error
        if not available_scanners:
            error_msg = "❌ No security scanners available. Please install at least one: pip install bandit safety semgrep detect-secrets"
            print(error_msg)
            self.progress_messages.append(error_msg)
            if progress_callback:
                progress_callback('\n'.join(self.progress_messages))
            
            return {
                "vulnerabilities": [],
                "total_issues": 0,
                "severity_counts": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
                "tools_used": [],
                "overall_status": "failed",
                "tool_statuses": unavailable_scanners,
                "failed_tools": list(unavailable_scanners.keys()),
                "logs_path": str(self.logs_dir)
            }
        
        # Update progress with available scanners
        if unavailable_scanners:
            msg = f"ℹ️  Running {len(available_scanners)}/{len(all_scanners)} available scanners: {', '.join(available_scanners.keys())}"
            print(msg)
            self.progress_messages.append(msg)
            if progress_callback:
                progress_callback('\n'.join(self.progress_messages))
        
        # Execute available scanners concurrently
        tool_statuses = {}
        all_results = {}
        
        # Initialize statuses for unavailable scanners
        for scanner_name, reason in unavailable_scanners.items():
            tool_statuses[scanner_name] = f"skipped: {reason}"
            all_results[scanner_name] = []
        
        max_workers = min(3, len(available_scanners))  # Adjust workers based on available scanners
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit only available scanner jobs
            future_to_scanner = {
                executor.submit(scanner_func): scanner_name 
                for scanner_name, scanner_func in available_scanners.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_scanner):
                scanner_name = future_to_scanner[future]
                try:
                    results, status = future.result()
                    all_results[scanner_name] = results
                    tool_statuses[scanner_name] = status
                    
                    # Update progress as each scanner completes
                    icon = {"bandit": "🔴", "safety": "🟡", "semgrep": "🔵", "detect-secrets": "🔑", "npm-audit": "📦"}.get(scanner_name, "⚪")
                    self.progress_messages.append(f"{icon} {scanner_name.capitalize()} completed: {len(results)} issues found")
                    if progress_callback:
                        progress_callback('\n'.join(self.progress_messages))
                        
                except Exception as e:
                    # Handle scanner failures gracefully
                    logging.error(f"{scanner_name} scanner failed: {e}")
                    all_results[scanner_name] = []
                    tool_statuses[scanner_name] = f"failed: {str(e)}"
                    self.progress_messages.append(f"❌ {scanner_name.capitalize()} failed: {str(e)[:100]}")
                    if progress_callback:
                        progress_callback('\n'.join(self.progress_messages))
        
        # Combine all results
        all_vulnerabilities = []
        for scanner_name in ["bandit", "safety", "semgrep", "detect-secrets", "npm-audit"]:
            all_vulnerabilities.extend(all_results.get(scanner_name, []))
        
        # Determine overall scan status
        failed_tools = [tool for tool, status in tool_statuses.items() if status != "success" and "skipping" not in status.lower()]
        if len(failed_tools) == 5:
            overall_status = "failed"
        elif failed_tools:
            overall_status = "partial_complete"
        else:
            overall_status = "complete"
        
        # Calculate statistics
        severity_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }
        
        for vuln in all_vulnerabilities:
            severity = vuln.get("severity", "LOW")
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Add summary to progress messages
        summary_msgs = [
            "",
            "="*50,
            "📊 Scan Summary:",
            f"   Overall Status: {overall_status.upper()}",
            f"   Total Issues: {len(all_vulnerabilities)}",
            f"   🔴 Critical: {severity_counts['CRITICAL']}",
            f"   🟠 High: {severity_counts['HIGH']}",
            f"   🟡 Medium: {severity_counts['MEDIUM']}",
            f"   🔵 Low: {severity_counts['LOW']}",
        ]
        if failed_tools:
            summary_msgs.append(f"   ⚠️  Failed Tools: {', '.join(failed_tools)}")
        summary_msgs.append("="*50)
        
        for msg in summary_msgs:
            print(msg)
        self.progress_messages.extend(summary_msgs)
        
        # Calculate Health Score & Grade for Badge
        # Simple logic: Start at 100, deduct points
        # CRITICAL: -20, HIGH: -10, MEDIUM: -5, LOW: -1
        score = 100
        score -= (severity_counts["CRITICAL"] * 20)
        score -= (severity_counts["HIGH"] * 10)
        score -= (severity_counts["MEDIUM"] * 5)
        score -= (severity_counts["LOW"] * 1)
        score = max(0, score)
        
        if score >= 90: grade = "A"
        elif score >= 80: grade = "B"
        elif score >= 70: grade = "C"
        elif score >= 60: grade = "D"
        elif score >= 50: grade = "E"
        else: grade = "F"
        
        # Generate Badge
        badge_path = self.project_path / "security-badge.svg"
        if generate_badge(score, grade, badge_path):
            msg = f"🛡️  Security Badge generated: {badge_path.name}"
            print(msg)
            self.progress_messages.append(msg)

        # Final progress update
        if progress_callback:
            progress_callback('\n'.join(self.progress_messages))
        
        return {
            "vulnerabilities": all_vulnerabilities,
            "total_issues": len(all_vulnerabilities),
            "severity_counts": severity_counts,
            "tools_used": ["bandit", "safety", "semgrep", "detect-secrets", "npm-audit"],
            "overall_status": overall_status,
            "tool_statuses": tool_statuses,
            "failed_tools": failed_tools,
            "logs_path": str(self.logs_dir)
        }
    
    @staticmethod
    def _map_bandit_severity(severity: str) -> str:
        """Map Bandit severity to our enum"""
        mapping = {
            "HIGH": "HIGH",
            "MEDIUM": "MEDIUM",
            "LOW": "LOW"
        }
        return mapping.get(severity, "MEDIUM")
    
    @staticmethod
    def _map_safety_severity(item: Dict) -> str:
        """Map Safety severity (all HIGH for vulnerabilities)"""
        return "HIGH"
    
    @staticmethod
    def _map_semgrep_severity(severity: str) -> str:
        """Map Semgrep severity to our enum"""
        mapping = {
            "ERROR": "HIGH",
            "WARNING": "MEDIUM",
            "INFO": "LOW"
        }
        return mapping.get(severity.upper(), "MEDIUM")
    
    def _save_output(self, tool_name: str, stdout: str, stderr: str, returncode: int):
        """Save tool output to log files for debugging"""
        try:
            log_base = self.logs_dir / f"{self.scan_id}_{tool_name}"
            
            with open(f"{log_base}_stdout.txt", "w", encoding="utf-8") as f:
                f.write(f"Return Code: {returncode}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n")
                f.write(stdout if stdout else "(empty)")
            
            with open(f"{log_base}_stderr.txt", "w", encoding="utf-8") as f:
                f.write(f"Return Code: {returncode}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n")
                f.write(stderr if stderr else "(empty)")
        except Exception as e:
            print(f"⚠️  Failed to save logs: {e}")
    
    def _save_raw_output(self, tool_name: str, suffix: str, content: str):
        """Save unparseable output for debugging"""
        try:
            log_file = self.logs_dir / f"{self.scan_id}_{tool_name}_{suffix}.txt"
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n")
                f.write(content)
            print(f"📝 Raw output saved to: {log_file}")
        except Exception as e:
            print(f"⚠️  Failed to save raw output: {e}")


def run_self_test():
    """Run self-test scan on asura-test-vulns project"""
    print("="*80)
    print(" ASURA SCANNER SELF-TEST")
    print("="*80)
    print()
    
    # Determine test project path
    test_path = Path(r"C:\Users\parth\OneDrive\Desktop\asura-test-vulns")
    if not test_path.exists():
        test_path = Path.home() / "Desktop" / "asura-test-vulns"
    
    if not test_path.exists():
        print(f"❌ FAILED: Test project not found at {test_path}")
        print(f"   Please ensure asura-test-vulns exists")
        return False
    
    print(f"📁 Test Project: {test_path}")
    print()
    
    # Create scanner with special selftest scan_id
    scanner = SecurityScanner(str(test_path), scan_id="selftest")
    
    # Create selftest logs directory
    selftest_logs = Path("logs/selftest")
    selftest_logs.mkdir(parents=True, exist_ok=True)
    scanner.logs_dir = selftest_logs
    
    all_passed = True
    results_summary = []
    
    # Test Bandit
    print("[TEST 1/3] Bandit")
    print("-" * 40)
    bandit_vulns, bandit_status = scanner.run_bandit()
    if bandit_status == "success" and len(bandit_vulns) > 0:
        # Check for expected vulnerabilities
        vuln_types = [v["vulnerability_type"] for v in bandit_vulns]
        has_pickle = any("pickle" in str(v).lower() for v in vuln_types)
        has_shell = any("B602" in v or "B607" in v for v in vuln_types)  # shell=True issues
        
        print(f"✅ [SELF-TEST] bandit: OK - {len(bandit_vulns)} issues found")
        if has_pickle:
            print(f"   ✓ Found pickle vulnerability")
        if has_shell:
            print(f"   ✓ Found shell=True vulnerability")
        results_summary.append(f"bandit: OK, {len(bandit_vulns)} issues")
    else:
        print(f"❌ [SELF-TEST] bandit: FAILED - {bandit_status}")
        print(f"   Expected vulnerabilities but found {len(bandit_vulns)}")
        all_passed = False
        results_summary.append(f"bandit: FAILED ({bandit_status})")
    print()
    
    # Test Semgrep
    print("[TEST 2/3] Semgrep")
    print("-" * 40)
    semgrep_vulns, semgrep_status = scanner.run_semgrep()
    if semgrep_status == "success":
        if len(semgrep_vulns) > 0:
            print(f"✅ [SELF-TEST] semgrep: OK - {len(semgrep_vulns)} issues found")
            results_summary.append(f"semgrep: OK, {len(semgrep_vulns)} issues")
        else:
            print(f"⚠️  [SELF-TEST] semgrep: OK but 0 issues (may need better rules)")
            results_summary.append(f"semgrep: OK, 0 issues")
    else:
        print(f"❌ [SELF-TEST] semgrep: FAILED - {semgrep_status}")
        all_passed = False
        results_summary.append(f"semgrep: FAILED ({semgrep_status})")
    print()
    
    # Test Safety
    print("[TEST 3/3] Safety")
    print("-" * 40)
    safety_vulns, safety_status = scanner.run_safety()
    if safety_status == "success" or "skipping" in safety_status.lower():
        if len(safety_vulns) > 0:
            print(f"✅ [SELF-TEST] safety: OK - {len(safety_vulns)} vulnerabilities found")
            results_summary.append(f"safety: OK, {len(safety_vulns)} vulnerabilities")
        else:
            print(f"✅ [SELF-TEST] safety: OK - 0 vulnerabilities (clean dependencies)")
            results_summary.append(f"safety: OK, 0 vulnerabilities")
    else:
        print(f"❌ [SELF-TEST] safety: FAILED - {safety_status}")
        all_passed = False
        results_summary.append(f"safety: FAILED ({safety_status})")
    print()
    
    # Summary
    print("="*80)
    print(" SELF-TEST SUMMARY")
    print("="*80)
    for result in results_summary:
        print(f"  {result}")
    print()
    print(f"📂 Logs saved to: {selftest_logs}")
    print()
    
    if all_passed:
        print("✅ ALL TESTS PASSED")
        return True
    else:
        print("❌ SOME TESTS FAILED - Check logs for details")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Asura Security Scanner")
    parser.add_argument("--self-test", action="store_true", help="Run self-test on asura-test-vulns")
    parser.add_argument("--path", type=str, help="Path to scan")
    
    args = parser.parse_args()
    
    if args.self_test:
        success = run_self_test()
        sys.exit(0 if success else 1)
    elif args.path:
        scanner = SecurityScanner(args.path)
        results = scanner.run_all()
        print(json.dumps(results, indent=2))
    else:
        parser.print_help()
