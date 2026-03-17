from prometheus_client import Counter

http_requests_custom_total = Counter(
    "sjira_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

auth_failures_total = Counter(
    "sjira_auth_failures_total",
    "Total authentication failures",
    ["reason", "path"]
)

upstream_requests_total = Counter(
    "sjira_upstream_requests_total",
    "Total upstream requests",
    ["service", 'status']
)