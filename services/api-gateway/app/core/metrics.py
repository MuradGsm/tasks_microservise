from prometheus_client import Counter, Histogram

http_requests_custom_total = Counter(
    "sjira_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

auth_failures_total = Counter(
    "sjira_auth_failures_total",
    "Total authentication failures",
    ["reason", "path"],
)

upstream_requests_total = Counter(
    "sjira_upstream_requests_total",
    "Total upstream requests",
    ["service", "status"],
)

auth_request_duration_seconds = Histogram(
    "sjira_auth_request_duration_seconds",
    "Latency of token validation requests to identity-service",
    ["outcome"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)

upstream_request_duration_seconds = Histogram(
    "sjira_upstream_request_duration_seconds",
    "Latency of upstream proxy requests",
    ["service", "outcome"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)