from datetime import datetime
from typing import Any

from pydantic import BaseModel


class NotificationPayload(BaseModel):
    type: str
    title: str
    message: str
    entity_type: str | None = None
    entity_id: int | None = None
    project_id: int | None = None


class NotificationPushRequest(BaseModel):
    user_id: int
    payload: NotificationPayload


class NotificationCreate(BaseModel):
    user_id: int
    type: str
    title: str
    message: str
    entity_type: str | None = None
    entity_id: int | None = None
    project_id: int | None = None


class NotificationRead(BaseModel):
    id: int
    user_id: int
    type: str
    title: str
    message: str
    entity_type: str | None
    entity_id: int | None
    project_id: int | None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    items: list[NotificationRead]
    total: int
    limit: int
    offset: int


class UnreadCountResponse(BaseModel):
    unread_count: int