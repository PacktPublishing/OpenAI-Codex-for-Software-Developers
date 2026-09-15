from __future__ import annotations

from sqlalchemy import func

from .models import Task, db

VALID_STATUSES = ("todo", "doing", "blocked", "done")
VALID_PRIORITIES = ("low", "medium", "high", "urgent")


def list_tasks(
    status: str | None = None,
    priority: str | None = None,
    owner: str | None = None,
) -> list[Task]:
    query = Task.query

    if status:
        query = query.filter_by(status=status)

    if priority:
        query = query.filter_by(priority=priority)

    if owner:
        query = query.filter_by(owner=owner)

    priority_rank = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    tasks = query.all()
    return sorted(tasks, key=lambda task: (priority_rank.get(task.priority, 99), task.created_at))


def list_owners() -> list[str]:
    statement = (
        db.select(Task.owner)
        .where(func.trim(Task.owner) != "")
        .distinct()
        .order_by(Task.owner)
    )
    return list(db.session.execute(statement).scalars())


def get_task(task_id: int) -> Task:
    return db.get_or_404(Task, task_id)


def add_note(task_id: int, note: str) -> Task:
    task = get_task(task_id)
    clean_note = note.strip()
    if not clean_note:
        raise ValueError("Note cannot be blank.")

    if task.notes:
        task.notes = f"{task.notes}\n{clean_note}"
    else:
        task.notes = clean_note

    db.session.commit()
    return task


def update_status(task_id: int, status: str) -> Task:
    if status not in VALID_STATUSES:
        raise ValueError(f"Unsupported status: {status}")

    task = get_task(task_id)
    task.status = status
    db.session.commit()
    return task


def dashboard_counts() -> dict[str, int]:
    counts = {status: 0 for status in VALID_STATUSES}
    for task in Task.query.all():
        counts[task.status] = counts.get(task.status, 0) + 1
    return counts
