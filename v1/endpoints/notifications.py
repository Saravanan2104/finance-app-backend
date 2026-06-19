from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db
from core.auth import get_current_user

from schemas.notification import (
    NotificationResponse
)

from services.notification_service import (
    get_notifications,
    mark_notification_read
)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get(
    "/",
    response_model=list[NotificationResponse]
)
def notifications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_notifications(
        db,
        current_user
    )


@router.put(
    "/{notification_id}/read"
)
def read_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return mark_notification_read(
        db,
        notification_id,
        current_user
    )