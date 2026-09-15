from app.models import Task, db
from app.services import list_owners


def test_owner_choices_exclude_whitespace_only_values(app):
    with app.app_context():
        db.session.add(
            Task(
                title="Owner data edge case",
                description="Reproduces a whitespace-only choice",
                owner="   ",
            )
        )
        db.session.commit()

        owners = list_owners()

    assert owners == ["Avery", "Sam"]
