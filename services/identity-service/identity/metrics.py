from prometheus_client import Counter

identity_login_success_total = Counter(
    "sjira_identity_login_success_total",
    "Total number of successful login requests in identity-service"
)


identity_login_failed_total = Counter(
    "sjira_identity_login_failed_total",
    "Total number of failed login requests in identity-service"
)

identity_token_refresh_total = Counter(
    "sjira_identity_token_refresh_total",
    "Total number of successful token refresh requests in identity-service",
)

identity_token_refresh_failed_total = Counter(
    "sjira_identity_token_refresh_failed_total",
    "Total number of failed token refresh requests in identity-service",
)