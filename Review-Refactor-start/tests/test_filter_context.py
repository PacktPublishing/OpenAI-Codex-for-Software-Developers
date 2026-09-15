import re
from urllib.parse import parse_qs, urlparse

from app.models import Task


def _location_query(response):
    return parse_qs(urlparse(response.headers["Location"]).query, keep_blank_values=True)


def _task_id(app):
    with app.app_context():
        return Task.query.filter_by(title="Urgent todo").one().id


def _rendered_filter_fields(html):
    fields = {}
    for name in ("return_status", "return_priority", "return_owner"):
        match = re.search(rf'<input type="hidden" name="{name}" value="([^"]*)">', html)
        assert match is not None, f"Missing rendered {name} field"
        fields[name] = match.group(1)
    return fields


def test_filtered_board_status_form_preserves_active_filters(app, client):
    client.application.config["SECRET_KEY"] = "test"
    task_id = _task_id(app)
    board = client.get("/?status=todo&priority=urgent&owner=Avery")
    html = board.get_data(as_text=True)

    assert board.status_code == 200
    assert f'action="/tasks/{task_id}/status"' in html
    form_data = _rendered_filter_fields(html)
    form_data["status"] = "doing"

    response = client.post(
        f"/tasks/{task_id}/status",
        data=form_data,
    )

    assert response.status_code == 302
    assert _location_query(response) == {
        "owner": ["Avery"],
        "priority": ["urgent"],
        "status": ["todo"],
    }


def test_rejected_status_update_also_preserves_active_filters(app, client):
    client.application.config["SECRET_KEY"] = "test"

    response = client.post(
        f"/tasks/{_task_id(app)}/status",
        data={"status": "mystery", "return_owner": "Avery"},
    )

    assert response.status_code == 302
    assert _location_query(response) == {"owner": ["Avery"]}


def test_status_redirect_ignores_unapproved_return_fields(app, client):
    client.application.config["SECRET_KEY"] = "test"

    response = client.post(
        f"/tasks/{_task_id(app)}/status",
        data={"status": "doing", "return_owner": "Avery", "return_next": "https://example.com"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/")
    assert _location_query(response) == {"owner": ["Avery"]}


def test_status_redirect_drops_blank_and_whitespace_filter_values(app, client):
    client.application.config["SECRET_KEY"] = "test"

    response = client.post(
        f"/tasks/{_task_id(app)}/status",
        data={
            "status": "doing",
            "return_status": " ",
            "return_priority": "",
            "return_owner": "\t",
        },
    )

    assert response.status_code == 302
    assert _location_query(response) == {}
