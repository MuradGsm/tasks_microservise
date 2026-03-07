from app.config.database import Base, int_pk
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, UniqueConstraint, Index


class Project(Base):
    id: Mapped[int] = int_pk
    key: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, nullable=False)

class ProjectMember(Base):
    __table_args__=(
        UniqueConstraint("project_id", "user_id", name="uq_project_member_project_user"),
        Index('ix_project_member_project_id', "project_id")
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)