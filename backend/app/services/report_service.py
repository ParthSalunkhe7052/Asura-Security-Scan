from typing import Dict, Any, List
from app.schemas.sarif import (
    SarifReport, SarifRun, SarifTool, SarifToolDriver, 
    SarifResult, SarifMessage, SarifLocation, 
    SarifPhysicalLocation, SarifArtifactLocation, SarifRegion
)

def convert_to_sarif(scan_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert internal Asura scan results to SARIF 2.1.0 format.
    
    Args:
        scan_results: Dictionary containing 'vulnerabilities' list from SecurityScanner.run_all()
        
    Returns:
        Dictionary representation of the SARIF report
    """
    results: List[SarifResult] = []
    
    # Map Asura severity to SARIF level
    severity_map = {
        "CRITICAL": "error",
        "HIGH": "error",
        "MEDIUM": "warning",
        "LOW": "note",
        "INFO": "note"
    }
    
    for vuln in scan_results.get("vulnerabilities", []):
        # Determine SARIF level
        asura_severity = vuln.get("severity", "LOW").upper()
        sarif_level = severity_map.get(asura_severity, "note")
        
        # Create location object
        file_path = vuln.get("file_path", "")
        # Ensure relative path doesn't start with / or \
        if file_path.startswith("/") or file_path.startswith("\\"):
            file_path = file_path[1:]
            
        line_number = vuln.get("line_number")
        region = None
        if line_number:
            try:
                line = int(line_number)
                region = SarifRegion(startLine=line)
            except (ValueError, TypeError):
                pass
                
        location = SarifLocation(
            physicalLocation=SarifPhysicalLocation(
                artifactLocation=SarifArtifactLocation(uri=file_path),
                region=region
            )
        )
        
        # Create result object
        result = SarifResult(
            ruleId=f"{vuln.get('tool', 'asura')}/{vuln.get('vulnerability_type', 'unknown')}",
            level=sarif_level,
            message=SarifMessage(text=vuln.get("description", "No description provided")),
            locations=[location],
            properties={
                "tool": vuln.get("tool"),
                "confidence": vuln.get("confidence"),
                "cwe_id": vuln.get("cwe_id"),
                "code_snippet": vuln.get("code_snippet")
            }
        )
        results.append(result)
        
    # Create the full report
    report = SarifReport(
        runs=[
            SarifRun(
                tool=SarifTool(
                    driver=SarifToolDriver(
                        name="Asura",
                        version="0.3.0"
                    )
                ),
                results=results
            )
        ]
    )
    
    return report.model_dump(by_alias=True, exclude_none=True)
