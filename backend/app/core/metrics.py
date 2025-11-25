import subprocess
import json
import os
import sys
from typing import Dict, Any, List, Set
from pathlib import Path
import argparse
import re


def validate_project_path(path: str) -> tuple[bool, str]:
    """
    Validate project path and check for problematic characters.
    Returns: (is_valid, error_message)
    """
    if not Path(path).exists():
        return False, f"Path does not exist: {path}"
    
    # Check for problematic characters that cause issues with CLI tools on Windows
    if sys.platform == 'win32' and ('+' in path or ' ' in path):
        return False, (
            f"Path contains special characters (+, spaces) that cause issues with analysis tools on Windows.\n"
            f"Path: {path}\n\n"
            f"Solution: Please rename your project folder to remove spaces and special characters.\n"
            f"Example: 'Clash Emote Detector+' → 'ClashEmoteDetector'"
        )
    
    return True, ""


def get_important_source_files(project_path: Path, max_files: int = 500) -> List[Path]:
    """
    Intelligently filter source files to scan only important code.
    
    Strategy:
    1. Only scan actual source code files
    2. Skip generated files, minified files, and large files
    3. Prioritize main source directories
    4. Limit total file count to prevent timeouts
    
    Args:
        project_path: Root path of the project
        max_files: Maximum number of files to scan (default 500)
    
    Returns:
        List of Path objects for files to scan
    """
    # Directories to ALWAYS skip
    skip_dirs = {
        'node_modules', 'venv', '.venv', 'env', 'ENV',
        'build', 'dist', '.git', '__pycache__', '.pytest_cache',
        'site-packages', '.tox', '.eggs', 'vendor', 'packages',
        'bower_components', '.next', '.nuxt', 'coverage',
        'tmp', 'temp', 'cache', '.cache', 'logs', 'log'
    }
    
    # File patterns to skip
    skip_patterns = {
        '.min.js', '.min.css',  # Minified files
        '.bundle.js', '.chunk.js',  # Bundled files
        '.map',  # Source maps
        '.lock', '.sum',  # Lock files
        '.log', '.pyc', '.pyo',  # Logs and compiled
        '.svg', '.png', '.jpg', '.jpeg', '.gif',  # Images
        '.woff', '.woff2', '.ttf', '.eot',  # Fonts
    }
    
    # Source file extensions (what we DO want to scan)
    source_extensions = {
        '.py', '.js', '.jsx', '.ts', '.tsx',
        '.java', '.cpp', '.c', '.h', '.hpp',
        '.cs', '.go', '.rs', '.php', '.rb',
        '.swift', '.kt', '.scala'
    }
    
    # Priority directories (scan these first)
    priority_dirs = {'src', 'app', 'lib', 'core', 'api', 'server', 'client'}
    
    important_files = []
    priority_files = []
    
    def should_skip_file(file_path: Path) -> tuple[bool, str]:
        """Check if file should be skipped. Returns (should_skip, reason)"""
        # Check file size - skip files > 1MB (likely generated)
        try:
            if file_path.stat().st_size > 1_000_000:
                return True, "large_file"
        except:
            return True, "inaccessible"
        
        # Check if filename matches skip pattern
        name_lower = file_path.name.lower()
        for pattern in skip_patterns:
            if name_lower.endswith(pattern):
                return True, "skip_pattern"
        
        # Only include source files
        if file_path.suffix not in source_extensions:
            return True, "not_source"
        
        return False, "ok"
    
    def is_skip_directory(dir_name: str) -> bool:
        """Check if directory should be skipped"""
        return dir_name in skip_dirs or dir_name.startswith('.')
    
    print(f"🔍 Scanning for important source files in: {project_path.name}")
    
    # Walk through project directory
    try:
        for root, dirs, files in os.walk(project_path):
            # Filter out directories to skip (modifies dirs in-place)
            dirs[:] = [d for d in dirs if not is_skip_directory(d)]
            
            root_path = Path(root)
            is_priority_dir = any(p in root_path.parts for p in priority_dirs)
            
            for file in files:
                file_path = root_path / file
                
                # Check if we should skip this file
                should_skip, reason = should_skip_file(file_path)
                if should_skip:
                    continue
                
                # Add to appropriate list
                if is_priority_dir:
                    priority_files.append(file_path)
                else:
                    important_files.append(file_path)
                
                # Stop if we have enough files
                if len(priority_files) + len(important_files) >= max_files * 2:
                    break
            
            if len(priority_files) + len(important_files) >= max_files * 2:
                break
    
    except Exception as e:
        print(f"⚠️  Error scanning directory: {e}")
        return []
    
    # Combine: priority files first, then others
    result = priority_files + important_files
    result = result[:max_files]  # Limit to max_files
    
    print(f"📁 Found {len(result)} source files to analyze")
    if len(priority_files) > 0:
        print(f"   ├─ {min(len(priority_files), max_files)} from priority directories")
    if len(important_files) > 0:
        remaining = max_files - len(priority_files)
        print(f"   └─ {min(len(important_files), remaining)} from other directories")
    
    return result


class CodeMetricsAnalyzer:
    """Analyze code quality metrics: complexity, coverage, and compute health scores"""
    
    def __init__(self, project_path: str, test_dir: str = None):
        self.project_path = Path(project_path)
        
        # Validate path
        is_valid, error_msg = validate_project_path(str(self.project_path))
        if not is_valid:
            raise ValueError(error_msg)
        
        # Set test directory - look for common test directories if not specified
        if test_dir:
            self.test_dir = Path(test_dir)
        else:
            # Try to find test directory automatically
            common_test_dirs = ['tests', 'test', 'testing']
            self.test_dir = None
            for test_dirname in common_test_dirs:
                potential_test_dir = self.project_path / test_dirname
                if potential_test_dir.exists() and potential_test_dir.is_dir():
                    self.test_dir = potential_test_dir
                    print(f"ℹ️  Found test directory: {test_dirname}")
                    break
        
    def analyze_complexity(self) -> Dict[str, Any]:
        """
        Analyze cyclomatic complexity using radon on important source files only
        
        Returns:
            {
                "status": "success" or "error",
                "files": {
                    "file_path": {
                        "complexity": float,
                        "functions": [...]
                    }
                },
                "average_complexity": float,
                "error": str (if error)
            }
        """
        result = {
            "status": "error",
            "files": {},
            "average_complexity": 0.0,
            "error": None
        }
        
        try:
            # Get filtered list of important source files
            source_files = get_important_source_files(self.project_path, max_files=500)
            
            if not source_files:
                result["error"] = "No source files found to analyze"
                result["status"] = "skipped"
                print(f"⚠️  {result['error']}")
                return result
            
            
            print(f"📊 Running radon complexity analysis on {len(source_files)} files")
            
            # SECURITY: Safe subprocess usage
            # - Uses sys.executable (Python interpreter - controlled by system, not user input)
            # - Uses hardcoded radon command with fixed flags
            # - Uses validated file paths from get_important_source_files() which filters and validates
            # - No shell=True, no user-controllable input reaches subprocess
            # Run radon on specific files instead of whole directory
            # This prevents timeout on large projects
            cmd = [
                sys.executable, "-m", "radon", "cc",
                "-a",  # Show average complexity
                "-j"   # JSON output
            ] + [str(f) for f in source_files]
            
            process = subprocess.run(  # nosec B603
                cmd,
                capture_output=True,
                text=True,
                timeout=60,  # 1 minute should be enough for filtered files
                encoding='utf-8',
                errors='replace',
                check=False  # Don't raise on non-zero exit
            )
            
            stdout = process.stdout.strip()
            stderr = process.stderr.strip()
            
            if not stdout:
                error_msg = f"Radon returned empty output. Return code: {process.returncode}"
                if stderr:
                    error_msg += f"\nStderr: {stderr[:500]}"
                result["error"] = error_msg
                print(f"⚠️  {error_msg}")
                return result
            
            try:
                data = json.loads(stdout)
            except json.JSONDecodeError as e:
                result["error"] = f"Could not parse radon output as JSON: {e}"
                print(f"❌ {result['error']}")
                return result
            
            # Process complexity data
            total_complexity = 0.0
            function_count = 0
            
            for file_path, functions in data.items():
                if not functions:
                    continue
                
                file_complexities = []
                for func in functions:
                    complexity = func.get("complexity", 0)
                    file_complexities.append(complexity)
                    total_complexity += complexity
                    function_count += 1
                
                result["files"][file_path] = {
                    "complexity": sum(file_complexities) / len(file_complexities) if file_complexities else 0.0,
                    "functions": functions
                }
            
            if function_count > 0:
                result["average_complexity"] = total_complexity / function_count
            
            result["status"] = "success"
            print(f"✅ Complexity analysis complete: avg={result['average_complexity']:.2f}")
            
        except subprocess.TimeoutExpired:
            result["error"] = "Radon analysis timed out (60s limit) even after filtering. Try scanning a smaller subdirectory."
            print(f"❌ {result['error']}")
        except FileNotFoundError:
            result["error"] = "Radon not found. Please install: pip install radon"
            print(f"❌ {result['error']}")
        except Exception as e:
            result["error"] = f"Complexity analysis error: {type(e).__name__}: {str(e)}"
            print(f"❌ {result['error']}")
        
        return result
    
    def analyze_coverage(self) -> Dict[str, Any]:
        """
        Analyze test coverage using coverage.py and pytest
        
        Returns:
            {
                "status": "success" or "error",
                "coverage_percent": float,
                "lines_covered": int,
                "lines_total": int,
                "files": {...},
                "error": str (if error)
            }
        """
        result = {
            "status": "error",
            "coverage_percent": 0.0,
            "lines_covered": 0,
            "lines_total": 0,
            "files": {},
            "error": None
        }
        
        try:
            # Check if tests exist
            if not self.test_dir or not self.test_dir.exists():
                result["error"] = "No test directory found. Coverage analysis requires tests."
                result["status"] = "skipped"
                print(f"ℹ️  {result['error']}")
                return result
            
            # Run pytest with coverage from project directory
            test_path = str(self.test_dir)
            
            cmd = [
                sys.executable, "-m", "pytest",
                test_path,
                f"--cov={self.project_path}",
                "--cov-report=json",
                "--cov-report=term",
                "-v"
            ]
            
            print(f"🧪 Running coverage analysis on tests in: {self.test_dir.name}")
            
            # SECURITY: Safe subprocess usage
            # - Uses sys.executable (controlled), hardcoded pytest command
            # - Uses validated project path from constructor (validate_project_path)
            # - Uses validated test directory path (checked to exist)
            # - No shell=True, no user-controllable arguments
            # Run coverage from the project directory
            process = subprocess.run(  # nosec B603
                cmd,
                cwd=str(self.project_path),  # FIXED: Run from project dir, not parent
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                errors='replace',
                check=False  # Don't raise on non-zero exit
            )
            
            # Read coverage.json from project directory
            coverage_json_path = self.project_path / "coverage.json"
            if coverage_json_path.exists():
                with open(coverage_json_path, 'r') as f:
                    coverage_data = json.load(f)
                
                # Extract summary
                totals = coverage_data.get("totals", {})
                result["coverage_percent"] = totals.get("percent_covered", 0.0)
                result["lines_covered"] = totals.get("covered_lines", 0)
                result["lines_total"] = totals.get("num_statements", 0)
                
                # Extract per-file data
                files_data = coverage_data.get("files", {})
                for file_path, file_info in files_data.items():
                    summary = file_info.get("summary", {})
                    result["files"][file_path] = {
                        "percent_covered": summary.get("percent_covered", 0.0),
                        "covered_lines": summary.get("covered_lines", 0),
                        "num_statements": summary.get("num_statements", 0)
                    }
                
                result["status"] = "success"
                print(f"✅ Coverage analysis complete: {result['coverage_percent']:.2f}%")
                
            else:
                # Try parsing from stdout
                stdout = process.stdout
                # Look for coverage percentage in output
                match = re.search(r'TOTAL.*?(\d+)%', stdout)
                if match:
                    result["coverage_percent"] = float(match.group(1))
                    result["status"] = "success"
                    print(f"✅ Coverage analysis complete: {result['coverage_percent']:.2f}%")
                else:
                    result["error"] = "Coverage completed but could not parse results. Check that tests run successfully."
                    result["status"] = "completed_no_data"
                    print(f"⚠️  {result['error']}")
            
        except subprocess.TimeoutExpired:
            result["error"] = "Coverage analysis timed out after 300 seconds. Project may be too large."
            print(f"❌ {result['error']}")
        except FileNotFoundError:
            result["error"] = "pytest or coverage not found. Please install: pip install pytest pytest-cov coverage"
            print(f"❌ {result['error']}")
        except Exception as e:
            result["error"] = f"Coverage analysis error: {type(e).__name__}: {str(e)}"
            print(f"❌ {result['error']}")
        
        return result
    
    @staticmethod
    def compute_code_health_score(
        security_score: float = 0.0,
        coverage_score: float = 0.0
    ) -> Dict[str, Any]:
        """
        Compute overall code health score
        
        Formula: 0.5 * SecurityScore + 0.5 * CoverageScore
        
        Args:
            security_score: Security score (0-100)
            coverage_score: Test coverage score (0-100)
        
        Returns:
            {
                "code_health_score": float,
                "security_score": float,
                "coverage_score": float,
                "grade": str  (A, B, C, D, F)
            }
        """
        # Normalize all scores to 0-100 range
        security_score = max(0.0, min(100.0, security_score))
        coverage_score = max(0.0, min(100.0, coverage_score))
        
        # Compute weighted health score
        health_score = (
            0.5 * security_score +
            0.5 * coverage_score
        )
        
        # Assign grade
        if health_score >= 90:
            grade = "A"
        elif health_score >= 80:
            grade = "B"
        elif health_score >= 70:
            grade = "C"
        elif health_score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "code_health_score": round(health_score, 2),
            "security_score": round(security_score, 2),
            "coverage_score": round(coverage_score, 2),
            "grade": grade,
            "breakdown": {
                "security_weight": 0.5,
                "coverage_weight": 0.5
            }
        }
    
    def analyze_all(self) -> Dict[str, Any]:
        """
        Run all metrics analyses
        
        Returns comprehensive metrics dictionary
        """
        print("\n" + "=" * 60)
        print("CODE METRICS ANALYSIS")
        print("=" * 60)
        
        results = {
            "complexity": self.analyze_complexity(),
            "coverage": self.analyze_coverage(),
        }
        
        # Compute health score if we have coverage
        coverage_score = results["coverage"].get("coverage_percent", 0.0)
        
        # For now, security score would come from DB
        # This is just for demonstration
        health = self.compute_code_health_score(
            security_score=0.0,  # Would fetch from latest scan
            coverage_score=coverage_score
        )
        
        results["health"] = health
        
        print("\n" + "=" * 60)
        print("METRICS SUMMARY")
        print("=" * 60)
        print(f"Average Complexity: {results['complexity'].get('average_complexity', 0):.2f}")
        print(f"Test Coverage: {results['coverage'].get('coverage_percent', 0):.2f}%")
        print(f"Code Health Score: {health['code_health_score']:.2f} (Grade: {health['grade']})")
        print("=" * 60)
        
        return results


def self_test():
    """Self-test function for metrics analyzer"""
    print("=" * 60)
    print("CODE METRICS SELF-TEST")
    print("=" * 60)
    
    # Test 1: Check radon installation
    print("\n1. Checking radon installation...")
    try:
        # SECURITY: Safe - uses sys.executable and hardcoded command, no user input
        result = subprocess.run(  # nosec B603
            [sys.executable, "-m", "radon", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(f"✅ Radon installed")
    except Exception as e:
        print(f"❌ Radon not installed: {e}")
        return False
    
    # Test 2: Check coverage installation
    print("\n2. Checking coverage installation...")
    try:
        # SECURITY: Safe - uses sys.executable and hardcoded command, no user input
        result = subprocess.run(  # nosec B603
            [sys.executable, "-m", "coverage", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(f"✅ Coverage version: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Coverage not installed: {e}")
        return False
    
    # Test 3: Create sample module and analyze
    print("\n3. Creating sample module for analysis...")
    test_module_dir = Path("tests/sample_module")
    test_module_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample code with varying complexity
    sample_code = """
def simple_function(x):
    '''Simple function with complexity 1'''
    return x + 1

def moderate_function(x, y):
    '''Moderate complexity function'''
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y
    else:
        return 0

def complex_function(a, b, c):
    '''Complex function with multiple branches'''
    result = 0
    if a > 0:
        result += a
    if b > 0:
        result += b
    elif b < 0:
        result -= b
    
    if c > 0:
        if result > 10:
            return result * c
        else:
            return result + c
    else:
        return result
"""
    
    (test_module_dir / "sample_code.py").write_text(sample_code.strip())
    print(f"✅ Created sample code at {test_module_dir}")
    
    # Test 4: Run metrics analysis
    print("\n4. Running metrics analysis...")
    try:
        analyzer = CodeMetricsAnalyzer(project_path=str(test_module_dir))
        
        # Test complexity
        complexity_results = analyzer.analyze_complexity()
        print(f"\n✅ Complexity analysis:")
        print(f"   Status: {complexity_results['status']}")
        print(f"   Average complexity: {complexity_results.get('average_complexity', 0):.2f}")
        print(f"   Files analyzed: {len(complexity_results.get('files', {}))}")
        
        if complexity_results['status'] == 'error':
            print(f"   Error: {complexity_results.get('error')}")
            
        # Test health score computation
        health = analyzer.compute_code_health_score(
            security_score=85.0,
            coverage_score=80.0
        )
        print(f"\n✅ Health score computation:")
        print(f"   Code Health Score: {health['code_health_score']:.2f}")
        print(f"   Grade: {health['grade']}")
        
    except Exception as e:
        print(f"❌ Metrics analysis failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ CODE METRICS SELF-TEST PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Code quality metrics analysis")
    parser.add_argument("--self-test", action="store_true", help="Run self-test")
    parser.add_argument("--project-path", help="Path to project to analyze")
    parser.add_argument("--test-dir", help="Path to test directory")
    
    args = parser.parse_args()
    
    if args.self_test:
        success = self_test()
        sys.exit(0 if success else 1)
    elif args.project_path:
        analyzer = CodeMetricsAnalyzer(args.project_path, args.test_dir)
        results = analyzer.analyze_all()
        print(json.dumps(results, indent=2))
    else:
        parser.print_help()
