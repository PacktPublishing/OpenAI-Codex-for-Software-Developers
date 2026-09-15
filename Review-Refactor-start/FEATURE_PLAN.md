# Owner Filter — Tested Feature Plan

## User story and outcome

As a team lead, I want to filter the task board by owner so I can focus on one teammate's workload.

Outcome: selecting an existing owner narrows the visible task cards while preserving the board's established filtering, sorting, empty-state, and global-count behavior.

## Behavior rules

- **B-01 — Exact owner:** `owner=Avery` shows only tasks whose stored owner is exactly `Avery`.
- **B-02 — All owners:** a missing or blank owner filter preserves the current all-owner behavior.
- **B-03 — Composition:** owner, status, and priority filters intersect when supplied together.
- **B-04 — Unknown owner:** an unmatched owner returns HTTP 200 and the existing no-results state.
- **B-05 — Choices:** the owner control lists distinct stored owners in ascending display order and retains the selected value.
- **B-06 — Stable surroundings:** dashboard counts remain global and existing status/priority behavior does not change.

## Assumptions and questions

Confirmed facts:

- `Task.owner` is already a required string (`app/models.py:11-19`).
- `list_tasks` already composes optional status and priority predicates (`app/services.py:9-20`).
- the toolbar uses GET selects with an empty “All” option (`app/templates/index.html:4-32`).

Chosen assumptions:

- matching is exact and case-sensitive because it follows stored values and a dropdown avoids free-text normalization.
- `Unassigned` is a valid owner choice when present in persisted tasks.
- counts remain global because `dashboard_counts()` currently ignores filters (`app/routes.py:22-29`, `app/services.py:52-56`).

Open product question for a later story: should status/note POST redirects preserve active filters? Current redirects return to the unfiltered index (`app/routes.py:33-52`).

## Scope boundaries

In scope:

- optional owner filtering in the existing GET board route;
- a distinct-owner service query;
- one owner dropdown matching current filter patterns;
- focused service and route tests.

Out of scope:

- schema changes, owner normalization, autocomplete, or a new owner entity;
- new endpoints or client-side filtering;
- filtered dashboard counts;
- preserving filters after status/note mutations;
- unrelated refactoring or styling redesign.

## Architecture decision

Choose the existing route → service → SQLAlchemy → template path.

- Extend `list_tasks(status=None, priority=None, owner=None)` and add an owner predicate beside the existing filters (`app/services.py:9-20`).
- Add `list_owners()` in the service layer to return sorted distinct stored owners; this keeps database access out of the route and template.
- Read `owner` in `routes.index` and pass `owners` plus `selected_owner` to the template (`app/routes.py:17-30`).
- Add a GET select beside the current status and priority controls (`app/templates/index.html:4-32`).

Rejected alternative: introduce an `Owner` model and foreign key. It adds migration and lifecycle complexity without a story requirement because owner is already persisted as a string.

## Data flow

1. Browser submits `GET /?owner=Avery` from the existing toolbar form (`app/templates/index.html:4-32`).
2. `routes.index` reads the optional value and passes it with status and priority (`app/routes.py:17-30`).
3. `services.list_tasks` adds `filter_by(owner=owner)` when the value is present, then preserves current sorting (`app/services.py:9-20`).
4. SQLAlchemy returns matching `Task` records whose owner field is defined in `app/models.py:11-19`.
5. The route supplies tasks, choices, and selected state to `index.html`, which renders cards or its existing empty state (`app/templates/index.html:35-84`).

## Change impact

| File / symbol | Responsibility in this story | Adjacent proof |
| --- | --- | --- |
| `app/services.py` · `list_tasks`, new `list_owners` | filtering rule and owner-choice query | service patterns in `tests/test_tasks.py:13-28` |
| `app/routes.py` · `index` | query input and template context | home-page test in `tests/test_tasks.py:5-10` |
| `app/templates/index.html` · toolbar | owner selection and retained state | existing status/priority selects, lines 4-32 |
| `tests/test_owner_filter.py` | focused red behavior contract | fixtures already provide Avery and Sam, `tests/conftest.py:7-30` |
| `tests/test_tasks.py` | request-level and regression coverage | current five tests, lines 5-46 |

## Test design

| Behavior | Test | Expected observation |
| --- | --- | --- |
| B-01 | `test_list_tasks_can_filter_by_owner` | only Avery's task is returned |
| B-02 | `test_blank_owner_preserves_all_tasks` | blank owner returns both fixture tasks in current sort order |
| B-03 | `test_owner_filter_composes_with_status_and_priority` | matching owner/status/priority yields Sam's task; a conflicting status yields none |
| B-04 | `test_unknown_owner_uses_empty_state` | response is 200 and contains existing no-results copy |
| B-05 | `test_owner_choices_are_distinct_sorted_and_selected` | choices are Avery/Sam once each and Avery remains selected |
| B-06 | `test_owner_filter_does_not_change_global_counts` | filtered page still shows global todo and blocked counts |
| B-06 | existing `test_list_tasks_can_filter_by_status` and `test_dashboard_counts_statuses` | prior behavior remains green |

Red-test checkpoint: draft B-01 and B-03 first. Before implementation they fail because `list_tasks` does not accept `owner`; the existing five-test suite remains green.

## Edge cases

- missing or empty query value;
- unknown but well-formed owner;
- owner combined with matching and conflicting status/priority;
- duplicate tasks for one owner and existing sort stability;
- default `Unassigned` value when present;
- selected-state rendering and Clear behavior;
- existing global counts and status/priority regression.

## Prototype decision

No prototype is needed. The story follows an existing GET-filter pattern and the in-memory fixtures already exercise two distinct owners. If owner normalization or autocomplete becomes required, prototype that decision separately before expanding this slice.

## Implementation checklist

1. Add and run focused B-01 and B-03 tests; confirm the expected red failure is the missing `owner` parameter.
2. Extend `list_tasks` with the smallest owner predicate; rerun focused tests.
3. Add `list_owners()` and focused distinct/sorted coverage for B-05.
4. Pass owner input, choices, and selected state through `routes.index`.
5. Add the owner select by following the existing toolbar pattern.
6. Add request-level coverage for B-02, B-04, B-05, and global-count behavior B-06.
7. Run the focused file, the full suite, Ruff, and diff checking.
8. Review every changed line against scope; report assumptions, deferred filter persistence, and verification evidence.
