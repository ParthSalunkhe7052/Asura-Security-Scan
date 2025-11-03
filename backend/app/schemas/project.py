from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    path: str = Field(..., min_length=1, description="Project directory path")
    description: Optional[str] = Field(None, max_length=500, description="Project description")

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    path: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=500)

class ProjectResponse(BaseModel):
    id: int
    name: str
    path: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProjectWithStats(ProjectResponse):
    total_scans: int = 0
    last_scan_date: Optional[datetime] = None
    latest_health_score: Optional[float] = None
