from pydantic import BaseModel


class TransitionRequest(BaseModel):
    to_status: str

class TransitionResponse(BaseModel):
    issue_id: int
    from_status: str
    to_status: str