from prometheus_client import Counter

projects_created_total = Counter(
    "sjira_projects_created_total",
    "Total number of projects created in project-service"
)

projects_updated_total = Counter(
    "sjira_projects_updated_total",
    "Total number of projects updated in project-service"
)

projects_members_added_total = Counter(
    "sjira_projects_added_total",
    "Total number of projects membres added in project-service"
)