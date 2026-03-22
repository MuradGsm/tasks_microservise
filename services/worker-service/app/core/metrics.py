from prometheus_client import Counter, Histogram

events_consumed_total = Counter(
    "sjira_worker_events_consumed_total",
    "Total number of events consumed from Redis queue",
    ["event_type"],
)

events_failed_total = Counter(
    "sjira_worker_events_failed_total",
    "Total number of failed event processing attempts",
    ["event_type"],
)

events_validation_failed_total = Counter(
    "sjira_worker_events_validation_failed_total",
    "Total number of events that failed schema validation",
    ["event_type"],
)

events_unknown_total = Counter(
    "sjira_worker_events_unknown_total",
    "Total number of events with unknown event type",
    ["event_type"],
)

notifications_sent_total = Counter(
    "sjira_worker_notifications_sent_total",
    "Total number of notifications sent successfully",
    ["event_type"],
)

notification_delivery_attempts_total = Counter(
    "sjira_worker_notification_delivery_attempts_total",
    "Total number of notification delivery attempts",
    ["event_type"],
)

notification_delivery_failures_total = Counter(
    "sjira_worker_notification_delivery_failures_total",
    "Total number of failed notification delivery attempts",
    ["event_type"],
)

downstream_http_requests_total = Counter(
    "sjira_worker_downstream_http_requests_total",
    "Total number of downstream HTTP requests",
    ["target_service", "method", "status"],
)

downstream_http_request_duration_seconds = Histogram(
    "sjira_worker_downstream_http_request_duration_seconds",
    "Duration of downstream HTTP requests",
    ["target_service", "method"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)

event_processing_duration_seconds = Histogram(
    "sjira_worker_event_processing_duration_seconds",
    "Time spent processing a worker event",
    ["event_type"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)