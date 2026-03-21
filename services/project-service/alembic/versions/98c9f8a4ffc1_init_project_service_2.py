from alembic import op
import sqlalchemy as sa


revision = "NEW_REVISION_ID"
down_revision = "98c9f8a4ffc1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_foreign_key(
        "fk_projectmember_project_id_project",
        "projectmember",
        "project",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_projectmember_project_id_project",
        "projectmember",
        type_="foreignkey",
    )