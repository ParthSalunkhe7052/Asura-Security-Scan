from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SarifArtifactLocation(BaseModel):
    uri: str

class SarifRegion(BaseModel):
    startLine: Optional[int] = None
    startColumn: Optional[int] = None

class SarifPhysicalLocation(BaseModel):
    artifactLocation: SarifArtifactLocation
    region: Optional[SarifRegion] = None

class SarifLocation(BaseModel):
    physicalLocation: SarifPhysicalLocation

class SarifMessage(BaseModel):
    text: str

class SarifResult(BaseModel):
    ruleId: str
    level: str  # "error", "warning", "note"
    message: SarifMessage
    locations: List[SarifLocation]
    properties: Optional[Dict[str, Any]] = None

class SarifToolDriver(BaseModel):
    name: str = "Asura"
    version: str = "0.3.0"
    informationUri: str = "https://github.com/ParthSalunkhe7052/Asura-Security-Scan"

class SarifTool(BaseModel):
    driver: SarifToolDriver

class SarifRun(BaseModel):
    tool: SarifTool
    results: List[SarifResult]

class SarifReport(BaseModel):
    version: str = "2.1.0"
    schema_: str = Field("https://json.schemastore.org/sarif-2.1.0.json", alias="$schema")
    runs: List[SarifRun]
