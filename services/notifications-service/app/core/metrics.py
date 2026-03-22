from prometheus_client import Counter, Gauge, Histogram

notifications_push_total = Counter(
    "notifications_push_total",
    "Total number of internal push notification requests",
    ["type"],
)

notifications_push_failed_total = Counter(
    "notifications_push_failed_total",
    "Total number of failed internal push notification requests",
    ["type"],
)

notification_delivery_duration_seconds = Histogram(
    "notification_delivery_duration_seconds",
    "Duration of notification processing and delivery",
    ["type"],
)

websocket_active_connections = Gauge(
    "websocket_active_connections",
    "Current number of active websocket connections",
)

websocket_messages_sent_total = Counter(
    "websocket_messages_sent_total",
    "Total number of websocket messages sent",
    ["type"],
)

notifications_created_total = Counter(
    "notifications_created_total",
    "Total number of notifications created",
    ["type"],
)

notifications_deduplicated_total = Counter(
    "notifications_deduplicated_total",
    "Total number of notifications deduplicated",
    ["type"],
)

notifications_marked_read_total = Counter(
    "notifications_marked_read_total",
    "Total number of notifications marked as read",
)

notifications_mark_all_read_total = Counter(
    "notifications_mark_all_read_total",
    "Total number of notifications marked as read via mark all",
)

websocket_delivery_failed_total = Counter(
    "websocket_delivery_failed_total",
    "Total number of failed websocket deliveries",
    ["type"],
)

websocket_delivery_skipped_total = Counter(
    "websocket_delivery_skipped_total",
    "Total number of skipped websocket deliveries due to no active connections",
    ["type"],
)