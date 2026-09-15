from app.models import Task, db
from app.services import list_owners, list_tasks


def test_list_tasks_can_filter_by_owner(app):
    with app.app_context():
        tasks = list_tasks(owner="Avery")

    assert [task.title for task in tasks] == ["Urgent todo"]


def test_owner_filter_composes_with_status_and_priority(app):
    with app.app_context():
        tasks = list_tasks(owner="Sam", status="blocked", priority="medium")

    assert [task.title for task in tasks] == ["Blocked medium"]


def test_blank_owner_preserves_all_tasks(app):
    with app.app_context():
        tasks = list_tasks(owner="")

    assert [task.title for task in tasks] == ["Urgent todo", "Blocked medium"]


def test_unknown_owner_uses_empty_state(client):
    response = client.get("/?owner=Nobody")

    assert response.status_code == 200
    assert b"No tasks match the current filters." in response.data


def test_owner_choices_are_distinct_sorted_and_selected(app, client):
    with app.app_context():
        db.session.add_all(
            [
                Task(title="Another Avery task", description="Duplicate choice", owner="Avery"),
                Task(title="Another Sam task", description="Duplicate choice", owner="Sam"),
                Task(title="Blank owner task", description="Excluded choice", owner=""),
            ]
        )
        db.session.commit()
        owners = list_owners()

    response = client.get("/?owner=Avery")
    html = response.get_data(as_text=True)

    assert owners == ["Avery", "Sam"]
    assert html.count('<option value="Avery"') == 1
    assert html.count('<option value="Sam"') == 1
    assert 'value="Avery" selected' in html


def test_owner_filter_does_not_change_global_counts(client):
    response = client.get("/?owner=Avery")

    assert b"todo: 1" in response.data
    assert b"blocked: 1" in response.data
