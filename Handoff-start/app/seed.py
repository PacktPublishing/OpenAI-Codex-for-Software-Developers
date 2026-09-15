from __future__ import annotations

import json
from pathlib import Path

from flask import Flask

from .models import Task, db


def load_seed_tasks() -> list[dict[str, str]]:
    seed_path = Path(__file__).resolve().parent.parent / "data" / "seed_tasks.json"
    return json.loads(seed_path.read_text(encoding="utf-8"))


def init_db(app: Flask) -> None:
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add_all(Task(**task) for task in load_seed_tasks())
        db.session.commit()

