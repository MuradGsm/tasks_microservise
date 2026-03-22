import pytest

from app.worker.router import route_event


@pytest.mark.asyncio
async def test_issue_created_event_routes_to_notification(
    monkeypatch,
    issue_created_event,
):
    sent_notifications = []

    async def fake_get_issue(issue_id: int):
        return {
            "id": issue_id,
            "reporter_id": 20,
            "assignee_id": 30,
        }

    async def fake_push_notification(user_id: int, payload: dict):
        sent_notifications.append(
            {
                "user_id": user_id,
                "payload": payload,
            }
        )

    monkeypatch.setattr(
        "app.notifications.recipients.get_issue",
        fake_get_issue,
    )
    monkeypatch.setattr(
        "app.notifications.delivery.push_notification",
        fake_push_notification,
    )

    await route_event(issue_created_event)

    assert len(sent_notifications) == 1
    assert sent_notifications[0]["user_id"] == 30


@pytest.mark.asyncio
async def test_comment_added_event_routes_to_notification(
    monkeypatch,
    comment_added_event,
):
    sent_notifications = []

    async def fake_get_issue(issue_id: int):
        return {
            "id": issue_id,
            "reporter_id": 20,
            "assignee_id": 30,
        }

    async def fake_push_notification(user_id: int, payload: dict):
        sent_notifications.append(
            {
                "user_id": user_id,
                "payload": payload,
            }
        )

    monkeypatch.setattr(
        "app.notifications.recipients.get_issue",
        fake_get_issue,
    )
    monkeypatch.setattr(
        "app.notifications.delivery.push_notification",
        fake_push_notification,
    )

    await route_event(comment_added_event)

    sent_user_ids = sorted(item["user_id"] for item in sent_notifications)
    assert sent_user_ids == [20, 30]


@pytest.mark.asyncio
async def test_notification_retry_succeeds_on_second_attempt(
    monkeypatch,
    issue_created_event,
):
    sent_notifications = []
    attempts = {"count": 0}

    async def fake_get_issue(issue_id: int):
        return {
            "id": issue_id,
            "reporter_id": 20,
            "assignee_id": 30,
        }

    async def fake_push_notification(user_id: int, payload: dict):
        attempts["count"] += 1

        if attempts["count"] == 1:
            raise RuntimeError("temporary notifications error")

        sent_notifications.append(
            {
                "user_id": user_id,
                "payload": payload,
            }
        )

    async def fake_sleep(_: float):
        return None

    monkeypatch.setattr(
        "app.notifications.recipients.get_issue",
        fake_get_issue,
    )
    monkeypatch.setattr(
        "app.notifications.delivery.push_notification",
        fake_push_notification,
    )
    monkeypatch.setattr(
        "app.notifications.delivery.asyncio.sleep",
        fake_sleep,
    )

    await route_event(issue_created_event)

    assert attempts["count"] == 2
    assert len(sent_notifications) == 1
    assert sent_notifications[0]["user_id"] == 30