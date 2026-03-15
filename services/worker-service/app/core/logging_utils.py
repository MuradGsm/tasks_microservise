from typing import Any

def build_event_log_context(event: dict[str, Any]) -> dict[str, Any]:
    context: dict[str, Any] = {}

    for key in ("event_type", "issue_id", "project_id", "actor_id", "comment_id"):
        value = event.get(key)
        if value is not None:
            context[key] = value
    
    return context