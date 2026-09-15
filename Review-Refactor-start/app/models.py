from __future__ import annotations

from datetime import UTC, datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False, default="")
    owner: Mapped[str] = mapped_column(nullable=False, default="Unassigned")
    status: Mapped[str] = mapped_column(nullable=False, default="todo")
    priority: Mapped[str] = mapped_column(nullable=False, default="medium")
    notes: Mapped[str] = mapped_column(nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(UTC))

    def to_summary(self) -> dict[str, str | int]:
        return {
            "id": self.id,
            "title": self.title,
            "owner": self.owner,
            "status": self.status,
            "priority": self.priority,
        }
