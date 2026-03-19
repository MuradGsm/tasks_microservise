from prometheus_client import Counter


issue_events_published_total = Counter(
    "sjira_issue_events_published_total",
    "Total number of issue-service events successfully published to Redis",
    ["event_type"],
)

issue_events_publish_failed_total = Counter(
    "sjira_issue_events_publish_failed_total",
    "Total number of issue-service events failed to publish to Redis",
    ["event_type"],
)

comments_created_total = Counter(
    "sjira_comments_created_total",
    "Total number of comments created is issue service"
)

status_changed_total = Counter(
    "sjira_status_changed_total",
    "Total number of issue status trasitions is issue-service",
    ["from_status", "to_status"],
)