import subprocess
import json
import os
import sys
from typing import List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
import argparse
import fnmatch


def validate_scanner_path(path: str) -> tuple:
    """
    Validate project path for security scanning.
    Returns: (is_valid, error_message)
    """
    if not Path(path).exists():
        return False, f"Project path does not exist: {path}"
    
    # Reject paths with special characters that cause issues with CLI tools on Windows
    if sys.platform == 'win32' and ('+' in path or ' ' in path):
        return False, (
            f"Path contains special characters (+, spaces) that cause issues with security scanners on Windows.\n"
            f"Path: {path}\n\n"
            f"Solution: Please rename your project folder to remove spaces and special characters.\n"
            f"Example: 'Clash Emote Detector+' → 'ClashEmoteDetector'\n\n"
            f"Then update the project path in ASURA Projects page."
        )
    
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
            ] + [str(f) for f in python_files]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 min should be enough for filtered files
                check=False,  # Don't raise on non-zero exit
                encoding='utf-8',
                errors='replace'  # Replace encoding errors
            )
            
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
            error_msg = "Bandit scan timed out (300s)"
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
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
                encoding='utf-8',
                errors='replace',  # Replace encoding errors
                env=env
            )
            
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
            error_msg = "Safety scan timed out (120s)"
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
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 min should be enough for filtered files
                check=False,
                encoding='utf-8',
                errors='replace',  # Replace encoding errors
                env=env
            )
            
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
            error_msg = "Semgrep scan timed out (120s) even after filtering"
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
        
        # Run Bandit
        self.progress_messages.append("🔴 Step 1/3: Running Bandit scanner...")
        if progress_callback:
            progress_callback('\n'.join(self.progress_messages))
        
        bandit_results, bandit_status = self.run_bandit()
        if progress_callback:
            progress_callback('\n'.join(self.progress_messages))
        
        # Run Safety
        self.progress_messages.append("")
        self.progress_messages.append("🟡 Step 2/3: Running Safety scanner...")
        if progress_callback:
            progress_callback('\n'.join(self.progress_messages))
        
        safety_results, safety_status = self.run_safety()
        if progress_callback:
            progress_callback('\n'.join(self.progress_messages))
        
        # Run Semgrep
        self.progress_messages.append("")
        self.progress_messages.append("🔵 Step 3/3: Running Semgrep scanner...")
        if progress_callback:
            progress_callback('\n'.join(self.progress_messages))
        
        semgrep_results, semgrep_status = self.run_semgrep()
        if progress_callback:
            progress_callback('\n'.join(self.progress_messages))
        
        all_vulnerabilities = bandit_results + safety_results + semgrep_results
        
        # Track tool statuses
        tool_statuses = {
            "bandit": bandit_status,
            "safety": safety_status,
            "semgrep": semgrep_status
        }
        
        # Determine overall scan status
        failed_tools = [tool for tool, status in tool_statuses.items() if status != "success" and "skipping" not in status.lower()]
        if len(failed_tools) == 3:
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
        
        # Final progress update
        if progress_callback:
            progress_callback('\n'.join(self.progress_messages))
        
        return {
            "vulnerabilities": all_vulnerabilities,
            "total_issues": len(all_vulnerabilities),
            "severity_counts": severity_counts,
            "tools_used": ["bandit", "safety", "semgrep"],
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
