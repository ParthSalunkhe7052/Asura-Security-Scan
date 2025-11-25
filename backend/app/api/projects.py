from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectWithStats
from app.services.project_service import ProjectService
from app.utils.error_handler import ErrorHandler, ErrorCode
from typing import List

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project"""
    try:
        return ProjectService.create_project(db, project)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ProjectWithStats])
async def list_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all projects with statistics"""
    return ProjectService.get_projects_with_stats(db, skip, limit)

@router.get("/{project_id}", response_model=ProjectWithStats)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project with statistics"""
    project = ProjectService.get_project_with_stats(db, project_id)
    if not project:
        error = ErrorHandler.get_error_response(
            ErrorCode.RECORD_NOT_FOUND,
            details=f"Project with ID {project_id} not found",
            context={"project_id": project_id}
        )
        return JSONResponse(status_code=404, content=error)
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int, 
    project_update: ProjectUpdate, 
    db: Session = Depends(get_db)
):
    """Update a project"""
    project = ProjectService.update_project(db, project_id, project_update)
    if not project:
        error = ErrorHandler.get_error_response(
            ErrorCode.RECORD_NOT_FOUND,
            details=f"Project with ID {project_id} not found",
            context={"project_id": project_id}
        )
        return JSONResponse(status_code=404, content=error)
    return project

@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project"""
    success = ProjectService.delete_project(db, project_id)
    if not success:
        error = ErrorHandler.get_error_response(
            ErrorCode.RECORD_NOT_FOUND,
            details=f"Project with ID {project_id} not found",
            context={"project_id": project_id}
        )
        return JSONResponse(status_code=404, content=error)
    return None
