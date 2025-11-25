"""
Error Handler Utility

Provides user-friendly error messages with actionable solutions
and documentation links for common issues.
"""

from enum import Enum
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """Standardized error codes for ASURA"""
    
    # Scanner Errors (1xx)
    SCAN_TIMEOUT = "SCAN_TIMEOUT_101"
    SCANNER_NOT_FOUND = "SCANNER_NOT_FOUND_102"
    SCANNER_FAILED = "SCANNER_FAILED_103"
    SCAN_PATH_INVALID = "SCAN_PATH_INVALID_104"
    NO_FILES_FOUND = "NO_FILES_FOUND_105"
    
    # Path Validation Errors (2xx)
    INVALID_PATH = "INVALID_PATH_201"
    PATH_NOT_FOUND = "PATH_NOT_FOUND_202"
    SYSTEM_DIR_BLOCKED = "SYSTEM_DIR_BLOCKED_203"
    PATH_OUTSIDE_WHITELIST = "PATH_OUTSIDE_WHITELIST_204"
    
    # Database Errors (3xx)
    DB_CONNECTION_FAILED = "DB_CONNECTION_FAILED_301"
    DB_QUERY_FAILED = "DB_QUERY_FAILED_302"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND_303"
    
    # API Errors (4xx)
    INVALID_REQUEST = "INVALID_REQUEST_401"
    MISSING_PARAMETER = "MISSING_PARAMETER_402"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED_403"
    
    # LLM/AI Errors (5xx)
    AI_API_KEY_MISSING = "AI_API_KEY_MISSING_501"
    AI_REQUEST_FAILED = "AI_REQUEST_FAILED_502"
    AI_MODEL_UNAVAILABLE = "AI_MODEL_UNAVAILABLE_503"
    
    # System Errors (6xx)
    DISK_SPACE_LOW = "DISK_SPACE_LOW_601"
    MEMORY_ERROR = "MEMORY_ERROR_602"
    PERMISSION_DENIED = "PERMISSION_DENIED_603"


class ErrorHandler:
    """
    Central error handling with user-friendly messages and solutions.
    """
    
    # Error code to user-friendly message mapping
    ERROR_MESSAGES: Dict[ErrorCode, Dict[str, Any]] = {
        ErrorCode.SCAN_TIMEOUT: {
            "title": "Scan Timed Out",
            "message": "The security scan took too long to complete and was stopped.",
            "solution": [
                "Try scanning fewer files or a smaller directory",
                "Increase timeout in settings or environment variables",
                "Check if your project has very large files (>1MB) that should be excluded"
            ],
            "docs_link": "docs/QUICK_START.md#troubleshooting",
            "severity": "warning"
        },
        
        ErrorCode.SCANNER_NOT_FOUND: {
            "title": "Security Scanner Not Installed",
            "message": "One or more required security scanning tools are not installed on your system.",
            "solution": [
                "Install missing tools: pip install bandit safety semgrep",
                "Check installation: Run the scanner command manually to verify",
                "Restart the application after installation"
            ],
            "docs_link": "docs/QUICK_START.md#prerequisites",
            "severity": "error"
        },
        
        ErrorCode.SCANNER_FAILED: {
            "title": "Scanner Execution Failed",
            "message": "A security scanner encountered an error while analyzing your code.",
            "solution": [
                "Check the scanner logs in logs/scans/ directory",
                "Verify your code doesn't have syntax errors",
                "Try running the scanner manually to see detailed error output",
                "Some scanners may fail on certain file types - this is normal"
            ],
            "docs_link": "docs/QUICK_START.md#troubleshooting",
            "severity": "warning"
        },
        
        ErrorCode.INVALID_PATH: {
            "title": "Invalid Project Path",
            "message": "The project path you provided is not valid or contains unsupported characters.",
            "solution": [
                "Use an absolute path (e.g., C:\\Users\\YourName\\project)",
                "Avoid spaces in the path if possible",
                "Avoid special characters like <, >, |, etc.",
                "Make sure the directory exists and is accessible"
            ],
            "docs_link": "docs/QUICK_START.md#creating-a-project",
            "severity": "error"
        },
        
        ErrorCode.PATH_NOT_FOUND: {
            "title": "Project Path Not Found",
            "message": "The specified project directory does not exist or is not accessible.",
            "solution": [
                "Verify the path exists on your system",
                "Check that you have permission to access the directory",
                "Make sure the drive/mount point is available",
                "Use an absolute path instead of a relative path"
            ],
            "docs_link": "docs/QUICK_START.md#creating-a-project",
            "severity": "error"
        },
        
        ErrorCode.SYSTEM_DIR_BLOCKED: {
            "title": "System Directory Blocked",
            "message": "Scanning system directories is not allowed for security reasons.",
            "solution": [
                "Choose a user project directory instead",
                "Avoid scanning: C:\\Windows, C:\\Program Files, /etc, /usr, /var",
                "Create a separate directory for your project code"
            ],
            "docs_link": "docs/SECURITY.md",
            "severity": "error"
        },
        
        ErrorCode.NO_FILES_FOUND: {
            "title": "No Scannable Files Found",
            "message": "No source code files were found in the specified directory.",
            "solution": [
                "Verify the directory contains Python, JavaScript, or other code files",
                "Check if files are in subdirectories (scanning is recursive)",
                "Supported extensions: .py, .js, .jsx, .ts, .tsx, .java, .go, etc.",
                "Large files (>1MB) are automatically excluded"
            ],
            "docs_link": "docs/QUICK_START.md#supported-languages",
            "severity": "warning"
        },
        
        ErrorCode.DB_CONNECTION_FAILED: {
            "title": "Database Connection Failed",
            "message": "Could not connect to the ASURA database.",
            "solution": [
                "Restart the backend server",
                "Check if asura.db file is corrupted",
                "Verify you have write permissions in the backend directory",
                "Delete asura.db to recreate (will lose history)"
            ],
            "docs_link": "docs/QUICK_START.md#troubleshooting",
            "severity": "error"
        },
        
        ErrorCode.RECORD_NOT_FOUND: {
            "title": "Record Not Found",
            "message": "The requested project or scan does not exist in the database.",
            "solution": [
                "Verify the project/scan ID is correct",
                "Check if the record was deleted",
                "Refresh the page to get the latest data"
            ],
            "docs_link": None,
            "severity": "error"
        },
        
        ErrorCode.RATE_LIMIT_EXCEEDED: {
            "title": "Too Many Requests",
            "message": "You have exceeded the rate limit for API requests.",
            "solution": [
                "Wait a minute before making more requests",
                "Current limit: 60 requests per minute",
                "Consider batching multiple operations together"
            ],
            "docs_link": None,
            "severity": "warning"
        },
        
        ErrorCode.AI_API_KEY_MISSING: {
            "title": "AI API Key Not Configured",
            "message": "OpenRouter API key is not set. AI features will not work.",
            "solution": [
                "Get a free API key from https://openrouter.ai",
                "Add OPENROUTER_API_KEY=your_key to backend/.env file",
                "Restart the backend server",
                "Note: AI features are optional, core scanning still works"
            ],
            "docs_link": "docs/GET_API_KEY.md",
            "severity": "info"
        },
        
        ErrorCode.AI_REQUEST_FAILED: {
            "title": "AI Analysis Failed",
            "message": "The AI service encountered an error while analyzing vulnerabilities.",
            "solution": [
                "Check your internet connection",
                "Verify your API key is still valid",
                "The service may be temporarily unavailable - try again later",
                "Check OpenRouter status at https://openrouter.ai/status"
            ],
            "docs_link": "docs/GET_API_KEY.md",
            "severity": "warning"
        },
        
        ErrorCode.DISK_SPACE_LOW: {
            "title": "Low Disk Space",
            "message": "Your system is running low on available disk space.",
            "solution": [
                "Free up disk space by deleting unnecessary files",
                "Clean up old scan logs in logs/scans/ directory",
                "Move large files to another drive",
                "At least 1GB free space is recommended"
            ],
            "docs_link": None,
            "severity": "warning"
        },
        
        ErrorCode.PERMISSION_DENIED: {
            "title": "Permission Denied",
            "message": "You don't have permission to access this file or directory.",
            "solution": [
                "Run the application with appropriate permissions",
                "Check file/directory ownership and permissions",
                "On Windows: Run as Administrator if needed",
                "On Linux/Mac: Check chmod permissions"
            ],
            "docs_link": None,
            "severity": "error"
        }
    }
    
    @classmethod
    def get_error_response(
        cls, 
        error_code: ErrorCode, 
        details: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a user-friendly error response.
        
        Args:
            error_code: The error code enum
            details: Additional technical details (optional)
            context: Additional context data (optional)
            
        Returns:
            Dict with error information formatted for API response
        """
        error_info = cls.ERROR_MESSAGES.get(error_code, {
            "title": "Unknown Error",
            "message": "An unexpected error occurred.",
            "solution": ["Please contact support or check logs"],
            "docs_link": None,
            "severity": "error"
        })
        
        response = {
            "error": True,
            "error_code": error_code.value,
            "title": error_info["title"],
            "message": error_info["message"],
            "severity": error_info["severity"],
            "solutions": error_info["solution"]
        }
        
        if error_info.get("docs_link"):
            response["learn_more"] = error_info["docs_link"]
        
        if details:
            response["technical_details"] = details
        
        if context:
            response["context"] = context
        
        # Log the error
        logger.error(f"[{error_code.value}] {error_info['title']}: {details or 'No details'}")
        
        return response
    
    @classmethod
    def format_exception(cls, exception: Exception, error_code: Optional[ErrorCode] = None) -> Dict[str, Any]:
        """
        Format a Python exception into a user-friendly error response.
        
        Args:
            exception: The exception object
            error_code: Optional error code (will try to infer if not provided)
            
        Returns:
            Formatted error response
        """
        # Try to infer error code from exception type
        if error_code is None:
            exception_name = type(exception).__name__
            
            if "NotFound" in exception_name or "DoesNotExist" in exception_name:
                error_code = ErrorCode.RECORD_NOT_FOUND
            elif "Permission" in exception_name or "Forbidden" in exception_name:
                error_code = ErrorCode.PERMISSION_DENIED
            elif "Database" in exception_name or "SQL" in exception_name:
                error_code = ErrorCode.DB_QUERY_FAILED
            elif "Timeout" in exception_name:
                error_code = ErrorCode.SCAN_TIMEOUT
            else:
                # Generic error for unknown exceptions
                return {
                    "error": True,
                    "error_code": "UNKNOWN_ERROR",
                    "title": "An Error Occurred",
                    "message": str(exception),
                    "severity": "error",
                    "solutions": ["Check the logs for more information", "Contact support if the issue persists"]
                }
        
        return cls.get_error_response(
            error_code,
            details=str(exception),
            context={"exception_type": type(exception).__name__}
        )
    
    @classmethod
    def log_and_raise(cls, error_code: ErrorCode, details: Optional[str] = None):
        """
        Log an error and raise an exception with user-friendly message.
        
        Args:
            error_code: The error code
            details: Additional details
            
        Raises:
            Exception with formatted error message
        """
        error_response = cls.get_error_response(error_code, details)
        raise Exception(error_response["message"])
