from prometheus_client import Counter, Gauge, Histogram

notifications_push_total = Counter(
    "sjira_notifications_push_total",
    "Total number of internal push notification requests received",
    ["type"],
)

notifications_push_failed_total = Counter(
    "sjira_notifications_push_failed_total",
    "Total number of internal push notification requests failed",
    ["type"],
)

websocket_active_connections = Gauge(
    "sjira_notifications_websocket_active_connections",
    "Current number of active WebSocket connections",
)

websocket_messages_sent_total = Counter(
    "sjira_notifications_websocket_messages_sent_total",
    "Total number of WebSocket messages sent successfully",
    ["type"],
)

notification_delivery_duration_seconds = Histogram(
    "sjira_notifications_delivery_duration_seconds",
    "Time spent processing internal notification push requests",
    ["type"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)