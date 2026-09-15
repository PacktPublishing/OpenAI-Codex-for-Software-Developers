# Team Task Triage Board — Repository Map

## Purpose and runtime

This is a small Flask task board backed by SQLite. The application factory configures persistence, initializes SQLAlchemy, registers the task routes, and exposes database initialization (`app/__init__.py:9-30`, `create_app`). The workshop uses Python 3.12.x and declares Flask plus Flask-SQLAlchemy (`pyproject.toml:1-9`). Verification uses pytest and Ruff (`pyproject.toml:11-19`).

## Responsibility map

| Path | Responsibility | Evidence |
| --- | --- | --- |
| `app/__init__.py` | application composition and database configuration | `create_app`, lines 9-30 |
| `app/routes.py` | HTTP inputs, response rendering, redirects, and user messages | `index`, `change_status`, `create_note`, lines 17-52 |
| `app/services.py` | task queries, validation, mutations, sorting, and counts | `list_tasks`, `add_note`, `update_status`, `dashboard_counts`, lines 5-56 |
| `app/models.py` | persisted `Task` shape | `Task`, lines 11-28 |
| `app/templates/` | filters, task display, and update forms | `index.html`, lines 4-84; `base.html`, lines 10-34 |
| `app/seed.py` and `data/` | destructive database reset and sample records | `init_db`, lines 16-21; `seed_tasks.json`, lines 1-34 |
| `tests/` | isolated fixtures and behavioral checks | `conftest.py`, lines 7-36; `test_tasks.py`, lines 5-46 |

## Representative flow

`GET /?status=blocked` enters `routes.index` (`app/routes.py:17-30`), which passes the query value to `list_tasks` (`app/services.py:9-20`). The service filters and sorts `Task` records from SQLAlchemy, while `dashboard_counts` calculates summary values (`app/services.py:52-56`). The route renders both into `index.html` (`app/templates/index.html:4-84`), which extends the page shell and count navigation in `base.html` (`app/templates/base.html:10-34`).

## Likely change points

| Change type | Primary files | Adjacent evidence and tests | Expected blast radius |
| --- | --- | --- | --- |
| Add or change a filter | `routes.py`, `services.py`, `index.html` | `test_list_tasks_can_filter_by_status`, `tests/test_tasks.py:13-17` | request input, query behavior, control state |
| Add a task field | `models.py`, template, seed data | fixtures in `tests/conftest.py:12-30` | schema, display, fixtures, initialization |
| Add a task action | `routes.py`, `services.py`, form template | status and note patterns in `tests/test_tasks.py:20-37` | validation, persistence, feedback |
| Change status vocabulary | `services.py:5`, template loops | invalid-status test, `tests/test_tasks.py:20-28` | filtering, updates, counts, presentation |

## Risk map

| Evidence-backed risk | Why it matters | Next check |
| --- | --- | --- |
| the manifest requires Python 3.12.x (`pyproject.toml:5`) | a locally passing suite on another interpreter does not prove support-policy conformance | run verification on Python 3.12 before release |
| `init_db` calls `drop_all` before recreating tables (`app/seed.py:16-21`) | running it against the wrong database destroys data | confirm environment and database URI before initialization |
| query filters accept arbitrary strings (`app/routes.py:19-21`, `app/services.py:12-16`) | unknown filters silently return an empty board | decide whether invalid values should be rejected or normalized |
| status updates validate vocabulary, but persisted priority values have no equivalent boundary (`app/services.py:5-6,42-48`) | unexpected values sort last and may escape UI assumptions | identify every task-creation path before adding validation |
| POST forms show no CSRF token (`app/templates/index.html:58-78`) | browser-originated mutations lack an evident request-forgery control | confirm deployment and security requirements before release |
| the `app` test fixture seeds two in-memory tasks rather than loading JSON seed data (`tests/conftest.py:7-36`) | seed loading and full sample behavior are not covered together | add a seed-specific check when that workflow changes |

## Open questions

- Is this workshop-only software, or is deployment expected? That changes the priority of CSRF and production configuration.
- Should invalid filter values produce an error, normalize to “all,” or return no results?
- Is `init-db` intentionally destructive in every environment?
- Which user story will drive the next change? Likely files depend on the requested behavior.

## Verification commands

```powershell
python -m pytest
python -m ruff check .
git status --short
```
