from pydantic import BaseModel
from datetime import datetime


class HistoryOut(BaseModel):
    id: int
    issue_id: int
    actor_id: int
    field: str
    old_value: str | None
    new_value: str | None
    created_at: datetime
    