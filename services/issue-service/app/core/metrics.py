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
    "Total number of comments created is issue service",
    ["from_status", "to_status"],
)

project_service_requests_total = Counter(
    "sjira_issue_project_service_requests_total",
    "Total number of requests from issue-service to project-service",
    ["operation", "status"],
)

project_service_request_failures_total = Counter(
    "sjira_issue_project_service_request_failures_total",
    "Total number of failed requests from issue-service to project-service",
    ["operation"],
)

issues_created_total = Counter(
    "sjira_issues_created_total",
    "Total number of issues created in issue-service",
)

issues_updated_total = Counter(
    "sjira_issues_updated_total",
    "Total number of issues updated in issue-service",
)

issues_deleted_total = Counter(
    "sjira_issues_deleted_total",
    "Total number of issues soft deleted in issue-service",
)