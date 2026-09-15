import os
from pathlib import Path

from flask import Flask

from .models import db
from .routes import bp


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "workshop-development-only"),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{Path(app.instance_path) / 'triage.sqlite'}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if config:
        app.config.update(config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    app.register_blueprint(bp)

    @app.cli.command("init-db")
    def init_db_command() -> None:
        from .seed import init_db

        init_db(app)
        print("Initialized the task triage database.")

    return app

