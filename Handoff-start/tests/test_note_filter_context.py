import re
from urllib.parse import parse_qs, urlparse

from app.models import Task


def _location_query(response):
    return parse_qs(urlparse(response.headers["Location"]).query, keep_blank_values=True)


def _task_id(app):
    with app.app_context():
        return Task.query.filter_by(title="Urgent todo").one().id


def test_filtered_board_renders_note_form_with_active_filters(app, client):
    task_id = _task_id(app)

    response = client.get("/?status=todo&priority=urgent&owner=Avery")
    html = response.get_data(as_text=True)
    note_form = re.search(
        rf'<form method="post" action="/tasks/{task_id}/notes">(.*?)</form>',
        html,
        re.DOTALL,
    )

    assert response.status_code == 200
    assert note_form is not None
    assert 'name="return_status" value="todo"' in note_form.group(1)
    assert 'name="return_priority" value="urgent"' in note_form.group(1)
    assert 'name="return_owner" value="Avery"' in note_form.group(1)


def test_note_form_preserves_active_filters(app, client):
    client.application.config["SECRET_KEY"] = "test"
    task_id = _task_id(app)

    response = client.post(
        f"/tasks/{task_id}/notes",
        data={
            "note": "Reviewed",
            "return_status": "todo",
            "return_priority": "urgent",
            "return_owner": "Avery",
        },
    )

    assert response.status_code == 302
    assert _location_query(response) == {
        "owner": ["Avery"],
        "priority": ["urgent"],
        "status": ["todo"],
    }


def test_rejected_note_also_preserves_active_filters(app, client):
    client.application.config["SECRET_KEY"] = "test"

    response = client.post(
        f"/tasks/{_task_id(app)}/notes",
        data={"note": " ", "return_owner": "Avery"},
    )

    assert response.status_code == 302
    assert _location_query(response) == {"owner": ["Avery"]}


def test_note_redirect_ignores_unapproved_return_fields(app, client):
    client.application.config["SECRET_KEY"] = "test"

    response = client.post(
        f"/tasks/{_task_id(app)}/notes",
        data={
            "note": "Reviewed",
            "return_owner": "Avery",
            "return_to": "https://example.com",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/")
    assert _location_query(response) == {"owner": ["Avery"]}
