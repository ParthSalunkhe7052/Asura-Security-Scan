from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.models import SeverityEnum, ScanStatusEnum

class VulnerabilityResponse(BaseModel):
    id: int
    tool: str
    severity: SeverityEnum
    file_path: str
    line_number: Optional[int]
    vulnerability_type: str
    description: str
    code_snippet: Optional[str]
    cwe_id: Optional[str]
    confidence: Optional[str]
    
    class Config:
        from_attributes = True

class ScanCreate(BaseModel):
    project_id: int
    scan_type: str = Field(..., pattern="^(security|mutation)$")

class ScanResponse(BaseModel):
    id: int
    project_id: int
    scan_type: str
    scan_name: Optional[str] = None
    status: ScanStatusEnum
    progress_log: Optional[str] = None  # Real-time progress updates for terminal display
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    total_issues: int
    health_score: Optional[float]
    
    # AI Analysis fields
    ai_suggestions: Optional[str] = None
    ai_model: Optional[str] = None
    ai_generated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ScanDetailResponse(ScanResponse):
    vulnerabilities: List[VulnerabilityResponse] = []
