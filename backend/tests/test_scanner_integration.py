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
