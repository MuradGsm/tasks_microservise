from typing import Any
from pydantic import BaseModel


class NotificationPushRequest(BaseModel):
    user_id: int
    payload: dict[str, Any]
    