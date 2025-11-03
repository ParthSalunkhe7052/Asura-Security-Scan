"""
Integration tests for security scanner tools
Tests that Bandit, Semgrep, and Safety run correctly and return parseable JSON
"""
import sys
import subprocess
import json
import pytest
from pathlib import Path


TEST_PROJECT_PATH = Path(r"C:\Users\parth\OneDrive\Desktop\asura-test-vulns")


def test_bandit_execution():
    """Test that Bandit runs and returns valid JSON"""
    if not TEST_PROJECT_PATH.exists():
        pytest.skip(f"Test project not found at {TEST_PROJECT_PATH}")
    
    cmd = [sys.executable, "-m", "bandit", "-r", str(TEST_PROJECT_PATH), "-f", "json"]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        check=False
    )
    
    # Bandit should return output
    assert result.stdout, f"Bandit returned empty stdout. Return code: {result.returncode}"
    
    # Should be valid JSON
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"Bandit output is not valid JSON: {e}\nStdout: {result.stdout[:500]}")
    
    # Should have results key
    assert "results" in data, "Bandit JSON missing 'results' key"
    
    # Should find at least one issue in asura-test-vulns
    assert len(data["results"]) > 0, "Expected to find vulnerabilities in test project"
    
    print(f"✅ Bandit test passed: {len(data['results'])} issues found")


def test_semgrep_execution():
    """Test that Semgrep runs and returns valid JSON"""
    if not TEST_PROJECT_PATH.exists():
        pytest.skip(f"Test project not found at {TEST_PROJECT_PATH}")
    
    cmd = [sys.executable, "-m", "semgrep", "--config=auto", "--json", str(TEST_PROJECT_PATH)]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        check=False
    )
    
    # Semgrep should return output
    assert result.stdout, f"Semgrep returned empty stdout. Return code: {result.returncode}\nStderr: {result.stderr[:500]}"
    
    # Should be valid JSON
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"Semgrep output is not valid JSON: {e}\nStdout: {result.stdout[:500]}")
    
    # Should have results key
    assert "results" in data, "Semgrep JSON missing 'results' key"
    
    print(f"✅ Semgrep test passed: {len(data['results'])} issues found")


def test_safety_execution():
    """Test that Safety runs and returns valid JSON"""
    if not TEST_PROJECT_PATH.exists():
        pytest.skip(f"Test project not found at {TEST_PROJECT_PATH}")
    
    req_file = TEST_PROJECT_PATH / "requirements.txt"
    if not req_file.exists():
        pytest.skip(f"No requirements.txt found in {TEST_PROJECT_PATH}")
    
    cmd = [sys.executable, "-m", "safety", "check", "--file", str(req_file), "--json"]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        check=False
    )
    
    # Safety might return empty for clean dependencies (exit code 0)
    # or JSON list for vulnerabilities
    if result.returncode == 0 and not result.stdout:
        print("✅ Safety test passed: 0 vulnerabilities (clean dependencies)")
        return
    
    # If there's output, it should be valid JSON
    if result.stdout:
        try:
            data = json.loads(result.stdout)
            assert isinstance(data, list), "Safety should return a JSON list"
            print(f"✅ Safety test passed: {len(data)} vulnerabilities found")
        except json.JSONDecodeError as e:
            pytest.fail(f"Safety output is not valid JSON: {e}\nStdout: {result.stdout[:500]}")


def test_scanner_class_integration():
    """Test the SecurityScanner class end-to-end"""
    if not TEST_PROJECT_PATH.exists():
        pytest.skip(f"Test project not found at {TEST_PROJECT_PATH}")
    
    # Import after ensuring path exists
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from app.core.scanner import SecurityScanner
    
    scanner = SecurityScanner(str(TEST_PROJECT_PATH), scan_id="test_integration")
    
    # Test Bandit
    bandit_vulns, bandit_status = scanner.run_bandit()
    assert bandit_status == "success", f"Bandit failed: {bandit_status}"
    assert len(bandit_vulns) > 0, "Expected to find vulnerabilities with Bandit"
    
    # Test Semgrep
    semgrep_vulns, semgrep_status = scanner.run_semgrep()
    assert semgrep_status == "success", f"Semgrep failed: {semgrep_status}"
    
    # Test Safety
    safety_vulns, safety_status = scanner.run_safety()
    # Safety can skip if no requirements.txt
    assert safety_status == "success" or "skipping" in safety_status.lower(), f"Safety failed: {safety_status}"
    
    # Test run_all
    results = scanner.run_all()
    assert "vulnerabilities" in results
    assert "overall_status" in results
    assert results["overall_status"] in ["complete", "partial_complete", "failed"]
    
    print(f"✅ Scanner class integration test passed")
    print(f"   Total issues: {results['total_issues']}")
    print(f"   Status: {results['overall_status']}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
