from pydantic import BaseModel, Field, field_validator
import re

KEY_RE = re.compile(r"^[A-Z0-9_]{2,10}$")

class ProjectCreate(BaseModel):
    key: str = Field(..., min_length=2, max_length=20)
    name: str = Field(..., min_length=2, max_length=20)

    @field_validator("key")
    @classmethod
    def normalize_and_validate_key(cls, v: str) -> str:
        v = v.strip().upper()
        if not KEY_RE.match(v):
            raise ValueError(r"^[A-Z0-9_]{2,10}$")
        return v
    
    @field_validator('name')
    @classmethod
    def normalize_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be empty")
        return v
    

class ProjectOut(BaseModel):
    id: int
    key: str
    name: str
    owner_id: int


class ProjectUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=20)

    @field_validator('name')
    @classmethod
    def normalize_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be empty")
        return v