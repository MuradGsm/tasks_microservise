from app.models.issue_models import IssueHistory
from sqlalchemy.ext.asyncio import AsyncSession

MAX_VALUE_LEN = 2000

def _to_str(v) -> str | None:
    if v is None:
        return None
    s = str(v)
    if len(s) > MAX_VALUE_LEN:
        s = s[:MAX_VALUE_LEN]+ "..."
    return s

def add_history(
    *,
    issue_id: int,
    actor_id: int,
    field: str,
    old_value,
    new_value,
    session: AsyncSession,  
    ) -> None:
    session.add(
        IssueHistory(
            issue_id=issue_id,
            actor_id=actor_id,
            field=field,
            old_value=_to_str(old_value),
            new_value=_to_str(new_value),
        )
    )