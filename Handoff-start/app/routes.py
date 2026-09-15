from __future__ import annotations

from collections.abc import Mapping

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .services import (
    VALID_PRIORITIES,
    VALID_STATUSES,
    add_note,
    dashboard_counts,
    list_owners,
    list_tasks,
    update_status,
)

bp = Blueprint("tasks", __name__)


def _active_filters(form: Mapping[str, str]) -> dict[str, str]:
    filters = {}
    for name in ("status", "priority", "owner"):
        value = form.get(f"return_{name}", "").strip()
        if value:
            filters[name] = value
    return filters


def _redirect_to_active_filters():
    return redirect(url_for("tasks.index", **_active_filters(request.form)))


@bp.get("/")
def index():
    status = request.args.get("status") or None
    priority = request.args.get("priority") or None
    owner = request.args.get("owner") or None
    tasks = list_tasks(status=status, priority=priority, owner=owner)
    return render_template(
        "index.html",
        counts=dashboard_counts(),
        owners=list_owners(),
        priorities=VALID_PRIORITIES,
        selected_owner=owner,
        selected_priority=priority,
        selected_status=status,
        statuses=VALID_STATUSES,
        tasks=tasks,
    )


@bp.post("/tasks/<int:task_id>/status")
def change_status(task_id: int):
    status = request.form.get("status", "")
    try:
        update_status(task_id, status)
        flash("Status updated.", "success")
    except ValueError as exc:
        flash(str(exc), "error")
    return _redirect_to_active_filters()


@bp.post("/tasks/<int:task_id>/notes")
def create_note(task_id: int):
    note = request.form.get("note", "")
    try:
        add_note(task_id, note)
        flash("Note added.", "success")
    except ValueError as exc:
        flash(str(exc), "error")
    return _redirect_to_active_filters()

