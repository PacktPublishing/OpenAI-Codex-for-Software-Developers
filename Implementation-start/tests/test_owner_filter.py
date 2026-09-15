from app.services import list_tasks


def test_list_tasks_can_filter_by_owner(app):
    with app.app_context():
        tasks = list_tasks(owner="Avery")

    assert [task.title for task in tasks] == ["Urgent todo"]


def test_owner_filter_composes_with_status_and_priority(app):
    with app.app_context():
        tasks = list_tasks(owner="Sam", status="blocked", priority="medium")

    assert [task.title for task in tasks] == ["Blocked medium"]
