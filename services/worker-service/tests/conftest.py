import pytest

@pytest.fixture
def issue_created_event():
    return {
        "event_type": "issue_created",
        "issue_id": 101,
        "project_id": 1,
        "actor_id": 10
    }


@pytest.fixture
def comment_added_event():
    return {
        "event_type": "comment_added",
        "issue_id": 101,
        "comment_id": 501,
        "project_id": 1,
        "actor_id": 10
    }


@pytest.fixture
def issue_status_changed_event():
    return {
        "event_type": "issue_status_changed",
        "issue_id": 101,
        "project_id": 1,
        "actor_id": 10,
        "old_status": "OPEN",
        "new_status": "IN_PROGRESS",
    }