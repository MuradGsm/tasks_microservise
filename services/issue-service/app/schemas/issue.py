from pydantic import BaseModel, Field
from typing import Optional

class IssueCreate(BaseModel):
    title: str =Field(..., min_length=3, max_length=255)
    description: str|None =None
    type: str = "TASK"


class IssueOut(BaseModel):
    id: int
    project_id: int
    number: int
    key: str
    title: str
    status: str
    type: str
    reporter_id: int 


class IssueUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    assignee_id: Optional[int] = None