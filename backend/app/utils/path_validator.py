"""Path validation and sanitization utilities for security"""
import os
import sys
from pathlib import Path
from typing import Tuple


class PathValidator:
    """Validates and sanitizes file paths to prevent directory traversal and injection attacks"""
    
    @staticmethod
    def sanitize_and_validate(path: str, allowed_roots: list = None) -> Tuple[bool, str, Path]:
        """
        Sanitize and validate a file path for security scanning.
        
        Args:
            path: The path to validate
            allowed_roots: Optional list of allowed root directories. If None, uses system defaults.
            
        Returns:
            Tuple of (is_valid, error_message, resolved_path)
        """
        try:
            # Convert to Path object and resolve to absolute canonical path
            # This handles .., ~, symlinks, etc.
            path_obj = Path(path).resolve()
            
            # Check if path exists
            if not path_obj.exists():
                return False, f"Path does not exist: {path}", None
            
            # Check if it's a directory
            if not path_obj.is_dir():
                return False, f"Path must be a directory: {path}", None
            
            # Prevent scanning system directories
            dangerous_dirs = PathValidator._get_dangerous_directories()
            path_str = str(path_obj).lower()
            
            for danger_dir in dangerous_dirs:
                if path_str.startswith(danger_dir.lower()) or path_str == danger_dir.lower():
                    return False, (
                        f"Cannot scan system directory: {path_obj}\n"
                        f"Scanning system directories is prohibited for security reasons."
                    ), None
            
            # Check for hidden directories (starting with .)
            if path_obj.name.startswith('.') and path_obj.name not in ['.', '..']:
                return False, (
                    f"Cannot scan hidden directory: {path_obj.name}\n"
                    f"Hidden directories typically contain sensitive configuration."
                ), None
            
            # Validate against allowed roots if provided
            if allowed_roots:
                is_allowed = False
                resolved_roots = [Path(root).resolve() for root in allowed_roots]
                
                for allowed_root in resolved_roots:
                    try:
                        # Check if path is within allowed root
                        path_obj.relative_to(allowed_root)
                        is_allowed = True
                        break
                    except ValueError:
                        continue
                
                if not is_allowed:
                    return False, (
                        f"Path is outside allowed directories: {path_obj}\n"
                        f"Allowed roots: {', '.join(str(r) for r in resolved_roots)}"
                    ), None
            
            # Check for problematic characters on Windows
            if sys.platform == 'win32':
                # Some CLI tools have issues with certain characters
                problematic_chars = PathValidator._check_problematic_windows_chars(str(path_obj))
                if problematic_chars:
                    return False, (
                        f"Path contains characters that cause issues with security scanners on Windows: {problematic_chars}\n"
                        f"Path: {path_obj}\n\n"
                        f"Solution: Please rename your project folder to remove these characters.\n"
                        f"Example: 'My Project+' → 'MyProject'\n\n"
                        f"Then update the project path in ASURA."
                    ), None
            
            # All checks passed
            return True, "", path_obj
            
        except Exception as e:
            return False, f"Path validation error: {str(e)}", None
    
    @staticmethod
    def _get_dangerous_directories() -> list:
        """Get list of system directories that should never be scanned"""
        dangerous = []
        
        if sys.platform == 'win32':
            # Windows system directories - only actual system dirs, not entire drive
            dangerous.extend([
                'C:\\Windows',
                'C:\\Program Files',
                'C:\\Program Files (x86)',
                'C:\\ProgramData',
                'C:\\System Volume Information',
                os.environ.get('SYSTEMROOT', 'C:\\Windows'),
            ])
        else:
            # Unix-like system directories
            dangerous.extend([
                '/bin', '/sbin', '/usr/bin', '/usr/sbin',
                '/etc', '/sys', '/proc', '/dev',
                '/boot', '/root', '/lib', '/lib64'
            ])
        
        return dangerous
    
    @staticmethod
    def _check_problematic_windows_chars(path: str) -> str:
        """Check for characters that cause issues with CLI tools on Windows"""
        problematic = []
        
        # Characters that commonly cause issues with subprocess calls
        # Spaces are generally handled by quoting, so we allow them now
        # if ' ' in path:
        #     problematic.append('spaces')
        if '+' in path:
            problematic.append('+')
        if '&' in path:
            problematic.append('&')
        if '(' in path or ')' in path:
            problematic.append('parentheses')
        
        return ', '.join(problematic) if problematic else ""
    
    @staticmethod
    def get_allowed_roots_from_env() -> list:
        """Get allowed scan roots from environment variable"""
        env_var = os.environ.get('ALLOWED_SCAN_ROOTS', '')
        if not env_var:
            return None
        
        # Split by semicolon on Windows, colon on Unix
        separator = ';' if sys.platform == 'win32' else ':'
        roots = [root.strip() for root in env_var.split(separator) if root.strip()]
        
        return roots if roots else None
