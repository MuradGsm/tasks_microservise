from prometheus_client import Counter

projects_created_total = Counter(
    "sjira_projects_created_total",
    "Total number of projects created in project-service",
)

projects_updated_total = Counter(
    "sjira_projects_updated_total",
    "Total number of projects updated in project-service",
)

projects_deleted_total = Counter(
    "sjira_projects_deleted_total",
    "Total number of projects deleted in project-service",
)

project_members_added_total = Counter(
    "sjira_project_members_added_total",
    "Total number of project members added in project-service",
)

project_members_removed_total = Counter(
    "sjira_project_members_removed_total",
    "Total number of project members removed in project-service",
)

project_access_checks_total = Counter(
    "sjira_project_access_checks_total",
    "Total number of project access checks in project-service",
)