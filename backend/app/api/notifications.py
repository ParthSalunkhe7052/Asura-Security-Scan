from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.models import Notification, Scan, Project

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
async def get_notifications(
    limit: int = 50,
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all notifications, ordered by most recent first
    
    Args:
        limit: Maximum number of notifications to return
        unread_only: If True, only return unread notifications
    
    Returns:
        List of notifications
    """
    query = db.query(Notification).order_by(Notification.created_at.desc())
    
    if unread_only:
        query = query.filter(Notification.is_read == 0)
    
    notifications = query.limit(limit).all()
    
    return {
        "notifications": [
            {
                "id": n.id,
                "type": n.type,
                "title": n.title,
                "message": n.message,
                "scan_id": n.scan_id,
                "project_id": n.project_id,
                "is_read": n.is_read == 1,
                "created_at": n.created_at.isoformat() if n.created_at else None
            }
            for n in notifications
        ],
        "unread_count": db.query(Notification).filter(Notification.is_read == 0).count()
    }


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = 1
    db.commit()
    
    return {"message": "Notification marked as read"}


@router.post("/mark-all-read")
async def mark_all_read(db: Session = Depends(get_db)):
    """Mark all notifications as read"""
    db.query(Notification).update({"is_read": 1})
    db.commit()
    
    return {"message": "All notifications marked as read"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification deleted"}


def create_notification(
    db: Session,
    type: str,
    title: str,
    message: str,
    scan_id: Optional[int] = None,
    project_id: Optional[int] = None
) -> Notification:
    """
    Helper function to create a notification
    
    Args:
        db: Database session
        type: Notification type (scan_started, scan_completed, scan_failed)
        title: Notification title
        message: Notification message
        scan_id: Optional scan ID
        project_id: Optional project ID
    
    Returns:
        Created notification
    """
    notification = Notification(
        type=type,
        title=title,
        message=message,
        scan_id=scan_id,
        project_id=project_id,
        is_read=0
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
