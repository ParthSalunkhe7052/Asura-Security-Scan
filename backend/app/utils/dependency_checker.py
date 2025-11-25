"""
Dependency Checker Utility

Detects available security scanner tools at application startup
and provides graceful degradation when tools are missing.
"""

import shutil
import subprocess
import os
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class DependencyChecker:
    """Check availability of external security scanner tools"""
    
    SCANNERS = {
        "bandit": {
            "command": "bandit",
            "version_flag": "--version",
            "install_hint": "pip install bandit",
            "description": "Python security linter"
        },
        "safety": {
            "command": "safety",
            "version_flag": "--version",
            "install_hint": "pip install safety",
            "description": "Python dependency security checker"
        },
        "semgrep": {
            "command": "semgrep",
            "version_flag": "--version",
            "install_hint": "pip install semgrep",
            "description": "Multi-language security scanner"
        },
        "radon": {
            "command": "radon",
            "version_flag": "--version",
            "install_hint": "pip install radon",
            "description": "Code complexity analyzer"
        },
        "pytest": {
            "command": "pytest",
            "version_flag": "--version",
            "install_hint": "pip install pytest pytest-cov",
            "description": "Testing framework for coverage metrics"
        },
        "detect-secrets": {
            "command": "detect-secrets",
            "version_flag": "--version",
            "install_hint": "pip install detect-secrets",
            "description": "Secrets detection tool"
        },
        "npm-audit": {
            "command": "npm.cmd" if os.name == "nt" else "npm",
            "version_flag": "--version",
            "install_hint": "Install Node.js and npm",
            "description": "Node.js package manager (for SCA)"
        }
    }
    
    @classmethod
    def check_tool(cls, tool_name: str) -> Tuple[bool, str]:
        """
        Check if a specific tool is available.
        
        Args:
            tool_name: Name of the tool to check (e.g., "bandit", "safety")
            
        Returns:
            Tuple of (is_available, version_or_error)
        """
        if tool_name not in cls.SCANNERS:
            return False, f"Unknown tool: {tool_name}"
        
        tool_info = cls.SCANNERS[tool_name]
        command = tool_info["command"]
        
        # First check if command exists in PATH
        if not shutil.which(command):
            return False, f"Not installed. Install with: {tool_info['install_hint']}"
        
        # Try to get version
        try:
            # SECURITY: Safe subprocess usage
            # - Uses hardcoded tool names from SCANNERS dict (bandit, safety, semgrep, etc.)
            # - Uses hardcoded version flags (--version)
            # - No user-controllable input  
            # - Never uses shell=True
            result = subprocess.run(  # nosec B603
                [command, tool_info["version_flag"]],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Extract version from output (usually first line)
                version_line = result.stdout.strip().split('\n')[0] if result.stdout else "installed"
                return True, version_line
            else:
                return False, f"Command failed: {result.stderr.strip()}"
                
        except subprocess.TimeoutExpired:
            return False, "Version check timed out"
        except Exception as e:
            return False, f"Error checking version: {str(e)}"
    
    @classmethod
    def check_all_dependencies(cls) -> Dict[str, Dict[str, any]]:
        """
        Check all scanner dependencies in parallel for faster startup.
        
        Returns:
            Dict with tool statuses
        """
        results = {}
        import concurrent.futures

        # Helper to check one tool and return result
        def check_one(name, info):
            is_available, version_or_error = cls.check_tool(name)
            return name, {
                "available": is_available,
                "description": info["description"],
                "install_hint": info["install_hint"],
                "version" if is_available else "error": version_or_error
            }

        # Run checks in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_tool = {
                executor.submit(check_one, name, info): name 
                for name, info in cls.SCANNERS.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_tool):
                tool_name, result = future.result()
                results[tool_name] = result
                
                # Log immediately
                if result["available"]:
                    logger.info(f"✓ {tool_name}: {result['version']}")
                else:
                    # Don't log stack traces for known missing tools to keep logs clean
                    logger.warning(f"✗ {tool_name}: {result['error']}")
        
        return results
    
    @classmethod
    def get_available_scanners(cls) -> List[str]:
        """
        Get list of available scanner tools.
        
        Returns:
            List of scanner names (e.g., ["bandit", "safety"])
        """
        results = cls.check_all_dependencies()
        return [tool for tool, info in results.items() if info["available"]]
    
    @classmethod
    def get_missing_scanners(cls) -> Dict[str, str]:
        """
        Get dict of missing scanner tools with installation instructions.
        
        Returns:
            Dict: {tool_name: install_hint}
        """
        results = cls.check_all_dependencies()
        return {
            tool: info["install_hint"] 
            for tool, info in results.items() 
            if not info["available"]
        }
    
    @classmethod
    def print_status_summary(cls) -> None:
        """Print a formatted summary of all tool statuses"""
        print("\n" + "=" * 60)
        print("🔍 Scanner Dependency Check")
        print("=" * 60)
        
        results = cls.check_all_dependencies()
        
        available_count = sum(1 for info in results.values() if info["available"])
        total_count = len(results)
        
        for tool_name, info in results.items():
            status = "✓" if info["available"] else "✗"
            description = info["description"]
            
            if info["available"]:
                version = info.get("version", "installed")
                print(f"{status} {tool_name:12} - {description:35} [{version}]")
            else:
                error = info.get("error", "Not available")
                print(f"{status} {tool_name:12} - {description:35} [{error}]")
        
        print("=" * 60)
        print(f"Status: {available_count}/{total_count} tools available")
        
        # Show installation hints for missing tools
        missing = cls.get_missing_scanners()
        if missing:
            print("\n⚠️  Missing Tools - Installation Instructions:")
            for tool, hint in missing.items():
                print(f"   {tool}: {hint}")
        
        print("=" * 60 + "\n")
    
    @classmethod
    def is_scanner_available(cls, scanner_name: str) -> bool:
        """
        Quick check if a specific scanner is available.
        
        Args:
            scanner_name: Name of scanner (e.g., "bandit", "safety", "semgrep")
            
        Returns:
            Boolean indicating availability
        """
        is_available, _ = cls.check_tool(scanner_name)
        return is_available
