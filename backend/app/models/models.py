from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class SeverityEnum(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ScanStatusEnum(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    path = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    scans = relationship("Scan", back_populates="project", cascade="all, delete-orphan")

class Scan(Base):
    __tablename__ = "scans"
    __table_args__ = (
        Index('idx_scan_project_id', 'project_id'),
        Index('idx_scan_status', 'status'),
        Index('idx_scan_started_at', 'started_at'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    scan_type = Column(String, nullable=False)  # "security"
    scan_name = Column(String, nullable=True)  # "ProjectName - Scan #N"
    status = Column(Enum(ScanStatusEnum), default=ScanStatusEnum.PENDING)
    progress_log = Column(Text, nullable=True)  # Real-time progress messages
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    total_issues = Column(Integer, default=0)
    health_score = Column(Float, nullable=True)
    
    # AI Analysis fields
    ai_suggestions = Column(Text, nullable=True)  # Cached AI response
    ai_model = Column(String, nullable=True)  # Model used (e.g., "llama-3.2")
    ai_generated_at = Column(DateTime, nullable=True)  # When AI analysis was done
    
    project = relationship("Project", back_populates="scans")
    vulnerabilities = relationship("Vulnerability", back_populates="scan", cascade="all, delete-orphan")

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    __table_args__ = (
        Index('idx_vulnerability_scan_id', 'scan_id'),
        Index('idx_vulnerability_severity', 'severity'),
        Index('idx_vulnerability_tool', 'tool'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    tool = Column(String, nullable=False)  # "bandit", "safety", "semgrep"
    severity = Column(Enum(SeverityEnum), nullable=False)
    file_path = Column(String, nullable=False)
    line_number = Column(Integer, nullable=True)
    vulnerability_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    code_snippet = Column(Text, nullable=True)
    cwe_id = Column(String, nullable=True)
    confidence = Column(String, nullable=True)
    
    scan = relationship("Scan", back_populates="vulnerabilities")

class CodeMetrics(Base):
    __tablename__ = "code_metrics"
    __table_args__ = (
        Index('idx_code_metrics_project_id', 'project_id'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Coverage metrics
    coverage_percent = Column(Float, default=0.0)
    lines_covered = Column(Integer, default=0)
    lines_total = Column(Integer, default=0)
    
    # Complexity metrics (JSON-stored per-file data)
    complexity_data = Column(Text, nullable=True)  # JSON string
    average_complexity = Column(Float, default=0.0)
    
    # Health scores
    security_score = Column(Float, default=0.0)
    coverage_score = Column(Float, default=0.0)
    code_health_score = Column(Float, default=0.0)
    
    project = relationship("Project", backref="code_metrics")

class Config(Base):
    __tablename__ = "configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index('idx_notification_created_at', 'created_at'),
        Index('idx_notification_is_read', 'is_read'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # "scan_started", "scan_completed", "scan_failed"
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    is_read = Column(Integer, default=0)  # 0 = unread, 1 = read (using integer for SQLite compatibility)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    scan = relationship("Scan", backref="notifications")
    project = relationship("Project", backref="notifications")
