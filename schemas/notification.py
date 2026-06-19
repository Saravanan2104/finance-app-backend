from datetime import date

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: int
    user_id: int

    message: str

    is_read: bool

    created_at: date

    model_config = ConfigDict(
        from_attributes=True
    )