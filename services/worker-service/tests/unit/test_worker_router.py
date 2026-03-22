import pytest

from app.worker.router import route_event


@pytest.mark.asyncio
async def test_unknown_event_does_not_crash():
    event = {
        "event_type": "something_weird",
        "issue_id": 1,
        "actor_id": 10,
        "project_id": 1,
    }

    await route_event(event)

@pytest.mark.asyncio
async def test_invalid_issue_created_payload_does_not_crash():
    event = {
        "event_type": "issue_created",
        "actor_id": 10,
        "project_id": 1,
    }

    await route_event(event)