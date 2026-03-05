from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Text, UniqueConstraint, Index, Boolean

from app.config.database import Base, int_pk


class IssueCounter(Base):
    project_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    next_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class Issue(Base):
    __table_args__ = (
        UniqueConstraint("project_id", "number", name="uq_issue_project_number"),
        Index("ix_issue_project_id", "project_id"),
        Index("ix_issue_reporter_id", "reporter_id"),
    )

    id: Mapped[int] = int_pk()
    project_id: Mapped[int] = mapped_column(Integer, nullable=False)

    number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1,2,3 внутри проекта

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    type: Mapped[str] = mapped_column(String(32), nullable=False, default="TASK")

    reporter_id: Mapped[int] = mapped_column(Integer, nullable=False)
    assignee_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class IssueComment(Base):
    __table_args__ = (
        Index("ix_issue_comment_issue_id", "issue_id"),
        Index("ix_issue_comment_author_id", "author_id")
    )
    id: Mapped[int] = int_pk()
    issue_id: Mapped[int] = mapped_column(Integer, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)