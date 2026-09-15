import pytest

from app import create_app
from app.models import Task, db


@pytest.fixture()
def app():
    test_app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "TESTING": True})
    with test_app.app_context():
        db.create_all()
        db.session.add_all(
            [
                Task(
                    title="Urgent todo",
                    description="Needs attention",
                    owner="Avery",
                    status="todo",
                    priority="urgent",
                ),
                Task(
                    title="Blocked medium",
                    description="Needs help",
                    owner="Sam",
                    status="blocked",
                    priority="medium",
                ),
            ]
        )
        db.session.commit()
    yield test_app


@pytest.fixture()
def client(app):
    return app.test_client()

