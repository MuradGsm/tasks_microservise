from pydantic import BaseModel

class NotificationPayload(BaseModel):
    type: str
    title: str
    message: str
    entity_type: str
    entity_id: int
    project_id: int