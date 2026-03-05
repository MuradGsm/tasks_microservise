from fastapi import HTTPException

OPEN = "OPEN"
IN_PROGRESS = "IN_PROGRESS"
BLOCKED = "BLOCKED"
DONE = "DONE"

ALLOWED_STATUSES = {OPEN, IN_PROGRESS, BLOCKED, DONE}

WORKFLOW = {
    OPEN: {IN_PROGRESS, BLOCKED},
    IN_PROGRESS: {DONE, BLOCKED, OPEN},
    BLOCKED: {IN_PROGRESS, OPEN},
    DONE: {IN_PROGRESS}
}

def validate_status(value: str) -> str:
    v = value.strip().upper()
    if v not in ALLOWED_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid status")
    return v

def asserts_transition_allowed(from_status: str, to_status: str) -> None:
    allowed = WORKFLOW.get(from_status, set())
    if to_status not in allowed:
        raise HTTPException(status_code=409, detail=f"Transition not allowed: {from_status} -> {to_status}")