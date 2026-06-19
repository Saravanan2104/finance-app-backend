from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.notification import Notification


def create_notification(
    db: Session,
    user_id: int,
    message: str
):

    notification = Notification(
        user_id=user_id,
        message=message
    )

    db.add(notification)
    db.commit()

    return notification


def get_notifications(
    db: Session,
    current_user
):

    return db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).all()


def mark_notification_read(
    db: Session,
    notification_id: int,
    current_user
):

    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.is_read = True

    db.commit()

    return {
        "message": "Notification marked as read"
    }