from pydantic import BaseModel


class IssueInternalOut(BaseModel):
    id: int
    project_id: int
    reporter_id: int
    assignee_id: int | None