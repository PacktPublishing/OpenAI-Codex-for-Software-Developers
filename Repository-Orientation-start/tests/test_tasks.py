from app.models import Task
from app.services import add_note, dashboard_counts, list_tasks, update_status


def test_home_page_lists_seeded_tasks(client):
    response = client.get("/")

    assert response.status_code == 200
    assert client.application.secret_key
    assert b"Urgent todo" in response.data
    assert b"Blocked medium" in response.data


def test_list_tasks_can_filter_by_status(app):
    with app.app_context():
        tasks = list_tasks(status="blocked")

    assert [task.title for task in tasks] == ["Blocked medium"]


def test_update_status_rejects_unknown_status(app):
    with app.app_context():
        task = Task.query.filter_by(title="Urgent todo").one()
        try:
            update_status(task.id, "mystery")
        except ValueError as exc:
            assert "Unsupported status" in str(exc)
        else:
            raise AssertionError("Expected unsupported status to raise ValueError")


def test_add_note_appends_text(app):
    with app.app_context():
        task = Task.query.filter_by(title="Urgent todo").one()
        add_note(task.id, "First note")
        add_note(task.id, "Second note")

        assert task.notes == "First note\nSecond note"


def test_dashboard_counts_statuses(app):
    with app.app_context():
        counts = dashboard_counts()

    assert counts["todo"] == 1
    assert counts["blocked"] == 1
    assert counts["done"] == 0
