from pydantic import BaseModel, Field
from datetime import datetime


class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


class CommentOut(BaseModel):
    id: int
    issue_id: int
    author_id: int
    text: str
    created_at: datetime