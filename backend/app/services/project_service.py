from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Project, Scan
from app.schemas.project import ProjectCreate, ProjectUpdate
from typing import Optional, List
from fastapi import HTTPException
from app.utils.path_validator import PathValidator

class ProjectService:
    @staticmethod
    def create_project(db: Session, project: ProjectCreate) -> Project:
        """Create a new project"""
        # Check if project with same name already exists
        existing = db.query(Project).filter(Project.name == project.name).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Project '{project.name}' already exists")
        
        # Validate and sanitize project path
        allowed_roots = PathValidator.get_allowed_roots_from_env()
        is_valid, error_msg, resolved_path = PathValidator.sanitize_and_validate(
            project.path, 
            allowed_roots
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Use the resolved canonical path
        db_project = Project(
            name=project.name,
            path=str(resolved_path),
            description=project.description
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all projects with pagination"""
        return db.query(Project).offset(skip).limit(limit).all()

    @staticmethod
    def get_projects_with_stats(db: Session, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all projects with statistics"""
        projects = db.query(Project).offset(skip).limit(limit).all()
        results = []
        for project in projects:
            # Get statistics
            total_scans = db.query(func.count(Scan.id)).filter(Scan.project_id == project.id).scalar()
            
            last_scan = db.query(Scan).filter(Scan.project_id == project.id)\
                .order_by(Scan.started_at.desc()).first()
            
            results.append({
                **project.__dict__,
                "total_scans": total_scans,
                "last_scan_date": last_scan.started_at if last_scan else None,
                "latest_health_score": last_scan.health_score if last_scan else None
            })
        return results
    
    @staticmethod
    def get_project(db: Session, project_id: int) -> Optional[Project]:
        """Get a single project by ID"""
        return db.query(Project).filter(Project.id == project_id).first()
    
    @staticmethod
    def get_project_with_stats(db: Session, project_id: int) -> dict:
        """Get project with statistics"""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        
        # Get statistics
        total_scans = db.query(func.count(Scan.id)).filter(Scan.project_id == project_id).scalar()
        
        last_scan = db.query(Scan).filter(Scan.project_id == project_id)\
            .order_by(Scan.started_at.desc()).first()
        
        return {
            **project.__dict__,
            "total_scans": total_scans,
            "last_scan_date": last_scan.started_at if last_scan else None,
            "latest_health_score": last_scan.health_score if last_scan else None
        }
    
    @staticmethod
    def update_project(db: Session, project_id: int, project_update: ProjectUpdate) -> Optional[Project]:
        """Update a project"""
        db_project = db.query(Project).filter(Project.id == project_id).first()
        if not db_project:
            return None
        
        update_data = project_update.model_dump(exclude_unset=True)
        
        # If path is being updated, validate it
        if 'path' in update_data:
            allowed_roots = PathValidator.get_allowed_roots_from_env()
            is_valid, error_msg, resolved_path = PathValidator.sanitize_and_validate(
                update_data['path'],
                allowed_roots
            )
            
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
            
            update_data['path'] = str(resolved_path)
        
        for key, value in update_data.items():
            setattr(db_project, key, value)
        
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def delete_project(db: Session, project_id: int) -> bool:
        """Delete a project"""
        db_project = db.query(Project).filter(Project.id == project_id).first()
        if not db_project:
            return False
        
        db.delete(db_project)
        db.commit()
        return True
