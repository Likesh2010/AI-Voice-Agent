from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ...repositories.repos import notification_repo
from ...models import User, Notification
from ... import schemas
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/notifications", tags=["In-App Notifications"])


@router.get("", response_model=List[schemas.NotificationOut])
def get_user_notifications(
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve in-app alerts and execution update notifications for the authenticated user."""
    if unread_only:
        return notification_repo.get_unread_by_user(db, user_id=current_user.id)
    return notification_repo.get_by_user(db, user_id=current_user.id)


@router.put("/read-all")
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all unread notifications for the client as read."""
    notification_repo.mark_all_as_read(db, user_id=current_user.id)
    return {"status": "success", "detail": "All notifications marked as read"}


@router.put("/{id}/read", response_model=schemas.NotificationOut)
def mark_notification_as_read(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle a single notification read property to true by ID."""
    notif = notification_repo.get(db, id)
    if not notif or notif.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notif.read = True
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
