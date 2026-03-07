from pydantic import BaseModel, field_validator

class ProjectMemberCreate(BaseModel):
    user_id: int
    role: str = "MEMBER"

    @field_validator('role')
    @classmethod
    def validate_role(cls, v:str) -> str:
        v = v.strip().upper()
        if v != "MEMBER":
            raise ValueError('role must be MEMBER')
        return v


class ProjectMemberOut(BaseModel):
    id: int
    project_id: int
    user_id: int
    role: str
     