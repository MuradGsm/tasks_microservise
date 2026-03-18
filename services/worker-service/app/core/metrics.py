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

notifications_sent_total = Counter(
    "sjira_worker_notifications_sent_total",
    "Total number of notifications sent successfully",
    ["event_type"],
)

event_processing_duration_seconds = Histogram(
    "sjira_worker_event_processing_duration_seconds",
    "Time spent processing a worker event",
    ["event_type"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)