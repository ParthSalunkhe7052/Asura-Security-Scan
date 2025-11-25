import argparse
import sys
import json
import os
from pathlib import Path
from typing import Dict, Any

# Add the parent directory to sys.path to allow imports from app
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.scanner import SecurityScanner
from app.services.report_service import convert_to_sarif

def main():
    parser = argparse.ArgumentParser(description="Asura Security Scanner CLI")
    parser.add_argument("path", help="Path to project to scan")
    parser.add_argument("--format", choices=["json", "sarif", "text"], default="text", help="Output format")
    parser.add_argument("--fail-on", choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"], help="Exit with error if severity found")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    target_path = Path(args.path).resolve()
    if not target_path.exists():
        print(f"❌ Error: Path '{target_path}' does not exist.")
        sys.exit(1)
        
    print(f"🚀 Starting Asura scan on: {target_path}")
    
    try:
        scanner = SecurityScanner(str(target_path))
        
        if args.verbose:
            print(f"ℹ️  Found {sum(len(files) for files in scanner.scannable_files.values())} scannable files.")
            
        results = scanner.run_all()
        
    except Exception as e:
        print(f"❌ Error during scan: {e}")
        sys.exit(1)
    
    # Handle Output Format
    output_str = ""
    if args.format == "sarif":
        output_data = convert_to_sarif(results)
        output_str = json.dumps(output_data, indent=2)
    elif args.format == "json":
        # Convert datetime objects to string for JSON serialization if needed
        # But run_all returns dicts with mostly primitives, let's hope it's json serializable
        output_str = json.dumps(results, indent=2, default=str)
    else:
        # Text format
        output_str = format_text_report(results)

    # Write Output
    if args.output:
        try:
            Path(args.output).write_text(output_str, encoding="utf-8")
            print(f"📄 Report saved to {args.output}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
    elif args.format != "text":
        # Print JSON/SARIF to stdout if no output file specified
        print(output_str)
    else:
        # Print text report to stdout
        print(output_str)

    # Handle Exit Code
    if args.fail_on:
        severity_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        threshold = severity_map.get(args.fail_on, 5)
        
        max_severity = 0
        for vuln in results.get("vulnerabilities", []):
            s = severity_map.get(vuln.get("severity", "LOW"), 0)
            if s > max_severity:
                max_severity = s
                
        if max_severity >= threshold:
            print(f"\n❌ Failed: Found issues of severity {args.fail_on} or higher.")
            sys.exit(1)
            
    print("\n✅ Scan passed.")
    sys.exit(0)

def format_text_report(results: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 50)
    lines.append("ASURA SECURITY SCAN REPORT")
    lines.append("=" * 50)
    
    vulns = results.get("vulnerabilities", [])
    lines.append(f"Total Issues: {len(vulns)}")
    
    severity_counts = results.get("severity_counts", {})
    lines.append(f"Critical: {severity_counts.get('CRITICAL', 0)}")
    lines.append(f"High:     {severity_counts.get('HIGH', 0)}")
    lines.append(f"Medium:   {severity_counts.get('MEDIUM', 0)}")
    lines.append(f"Low:      {severity_counts.get('LOW', 0)}")
    lines.append("-" * 50)
    
    if not vulns:
        lines.append("No vulnerabilities found! 🎉")
    else:
        for i, vuln in enumerate(vulns, 1):
            severity = vuln.get("severity", "UNKNOWN")
            lines.append(f"[{i}] {severity} - {vuln.get('vulnerability_type', 'Issue')}")
            lines.append(f"    File: {vuln.get('file_path')}:{vuln.get('line_number', '?')}")
            lines.append(f"    Tool: {vuln.get('tool')}")
            lines.append(f"    Desc: {vuln.get('description')}")
            lines.append("")
            
    return "\n".join(lines)

if __name__ == "__main__":
    main()
