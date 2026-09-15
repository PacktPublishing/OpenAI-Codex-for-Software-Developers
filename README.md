# Build AI Agents with OpenAI Codex

## Team Task Triage Board workshop

This one-day workshop uses Codex as an Agile TDD developer agent. You will inspect, plan, test, implement, debug, review, refactor, and hand off changes to a deliberately small Flask task board backed by SQLite.

The application is not an AI agent. It is the shared engineering problem that lets you practice building a reliable agent workflow with `AGENTS.md`, reusable skills, behavioral evidence, and reviewable diffs.

## Quick start

### Before class

Forward [STUDENT_SETUP.md](STUDENT_SETUP.md) to attendees before class. It contains the
minimum software, account, access, and readiness checklist.

At minimum, install these prerequisites:

- Python 3.12.x
- Git
- either [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) or the [Codex IDE extension](https://learn.chatgpt.com/docs/codex/ide)

CLI users can verify authentication with:

```text
codex --version
codex login status
```

IDE users should complete **Sign in with ChatGPT** before class.

### Set up the repository

Clone the repository with the URL supplied by your instructor, then run one bootstrap command from the repository root.
Bootstrap creates the shared `.venv`, installs the pinned course environment from `requirements.txt`, and verifies every starting checkpoint.

Windows PowerShell:

```powershell
.\scripts\bootstrap.ps1
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
sh scripts/bootstrap.sh
source .venv/bin/activate
```

Success ends with:

```text
Workshop verification passed (full).
Agents: checkpoint_auditor / security_reviewer
Checkpoints: 5 / 5 / 5 / (5 pass + 2 expected fail) / 11 / 16 / 20
Setup complete.
```

If setup fails, stop and fix the reported prerequisite or checkpoint mismatch before beginning a lab. Before making lab changes, rerun the canonical starting-checkpoint audit with `scripts/preflight.ps1 -Full` or `sh scripts/preflight.sh --full`. After work begins, use the active lab's focused and full-stage commands instead; root preflight intentionally expects untouched starting folders.

### Start Lab 1

Open the **repository root** as the Codex/IDE workspace. Keep it open for the whole course; each lab names the only stage folder Codex may inspect.

In your activated terminal:

```powershell
Set-Location Foundations-start
python -m flask --app app init-db
python -m flask --app app run --debug
```

On macOS/Linux, use `cd Foundations-start`. Open the local URL printed by Flask, confirm that the task board loads, then stop the server with `Ctrl+C`.

> The app has a workshop-only fallback secret so local exercises work after a new terminal opens. It is not suitable for deployment.

## Course map

All stages live in one root Git repository. Changes accumulate across lab folders, so run tests and diffs from the active stage. Never copy a later-stage solution into an earlier lab.

| Lab | Active stage | Keep changes for next lab? | Starting evidence | Suggested time |
| ---: | --- | --- | --- | ---: |
| 1 | `Foundations-start` | No | 5 pass | 25 min |
| 2 | `Repository-Orientation-start` | No | 5 pass; map absent | 30 min |
| 3-4 | `Planning-Tests-start` | Yes | 5 pass; map present | 50 min |
| 5 | `Implementation-start` | No | 5 pass + 2 intentional failures | 45 min |
| 6-7 | `Debugging-Extension-start` | Yes | 11 pass | 60 min |
| 8-9 | `Review-Refactor-start` | Yes | 16 pass | 75 min |
| 10 | `Handoff-start` | No | 20 pass and evidence present | 30 min |

The starting folders are independent checkpoints. “Keep changes” means continue in that same folder for the paired lab only.

### Current-lab checklist

At the start of every lab:

1. Find the lab row above and `cd` to its exact active stage.
2. Run the lab's baseline commands and compare the expected green/red state.
3. Keep Codex at the repository root, but name the active stage and forbid other stages in the prompt.
4. When the lab requests a specialist, name the project agent and wait for its report before continuing.
5. During review, run `git status --short -- .` and `git diff -- .` from the active stage so earlier labs stay out of view.
6. Stop at the checkpoint before switching or continuing folders.

## How to work with Codex

For every lab:

1. Keep the IDE/Codex workspace at the repository root so `AGENTS.md` and `.agents/skills` are available.
2. Name the active stage in the prompt and forbid inspection of other `*-start` folders.
3. Use the requested skill; it supplies the repeatable workflow while the lab prompt controls scope.
4. Review proposed commands and every changed line.
5. Do not let Codex commit during a lab.

The strongest task prompts provide:

- **Goal:** the outcome to create.
- **Context:** the active stage, source evidence, and current checkpoint.
- **Constraints:** allowed paths, frozen behavior, non-goals, and stop conditions.
- **Done when:** observable behavior and commands that prove completion.

### Evidence ladder

Run from the active stage after a code change. Replace the focused path with the one named by the lab.

```powershell
python -m pytest -q tests/test_relevant_behavior.py
python -m pytest -q
python -m ruff check .
git diff --check -- .
git status --short -- .
git diff -- .
```

Focused checks answer whether the intended behavior changed. The full suite detects collateral damage. Ruff and the diff checks detect quality and scope problems. A claim that checks passed is not evidence until you see the command result.

When Codex creates a new file, make it visible to Git diff without staging its content:

```powershell
git add -N -- path/to/new-file
git diff -- path/to/new-file
```

### Project agents

The root `AGENTS.md` defines the primary **Workshop Developer Agent**. Two project-scoped
specialists in `.codex/agents/` demonstrate independent agent-assisted review:

| Agent | Job | May edit? | Disposition |
| --- | --- | :---: | --- |
| `checkpoint_auditor` | execute the documented checkpoint checks and compare exact expected evidence | No | `READY`, `EXPECTED_RED`, or `BLOCKED` |
| `security_reviewer` | trace request-controlled data to sensitive destinations and rank concrete findings | No | accept, correct, reject, or defer per finding |

The specialists do not replace the reusable skills. Each specialist follows the relevant
skill in an isolated thread, returns evidence or findings, and stops. The primary agent
retains responsibility for decisions, changes, and final verification.

Codex loads project agents when a repository session starts. After cloning, pulling an
update that adds `.codex/agents/`, or changing an agent definition, start a new Codex chat
from the repository root. The lab prompts explicitly request delegation; do not ask the
specialists to edit and do not run them concurrently with production changes.

The three demonstrations occur at deliberately different boundaries:

1. Lab 5: `checkpoint_auditor` recognizes the exact intentional-red starting state.
2. Lab 8: `security_reviewer` finds a green-but-unsafe redirect without correcting it.
3. Lab 10: `checkpoint_auditor` independently checks the final handoff scope and evidence.

## Lab 1 — Establish a bounded development workflow

**Active stage:** `Foundations-start`
**Skill:** use the root Agile TDD contract; no task skill is required.
**Baseline:** 5 tests pass and Ruff is clean.
**Outcome:** add `in_review` as a valid task status with focused proof.

From `Foundations-start`, submit:

```text
Active stage: Foundations-start. Do not inspect another *-start folder.

Goal: Add "in_review" as a valid task status.

Context: Inspect the active Flask app and existing tests first. Identify the source of truth for valid statuses and the behavior that rejects unknown statuses.

Constraints: Make the smallest change. Do not alter the schema, add a route, redesign the UI, change dependencies, or change unrelated behavior.

Process: Explain the intended files and checks before editing. Add focused coverage, run the focused test, then run the full suite and Ruff. Summarize the stage-scoped diff and assumptions.

Done when: "in_review" is accepted, unknown status is still rejected, all tests pass, Ruff passes, and every changed line supports this goal.
```

Verify from `Foundations-start`:

```powershell
python -m pytest -q
python -m ruff check .
git diff --check -- .
git status --short -- .
git diff -- .
```

Accept variation in test names or assertion style when behavior and scope are equivalent. If the result is broad, ask Codex to retain only the minimal service behavior and focused proof.

**Checkpoint:** stop work in this folder and move to `Repository-Orientation-start`.

## Lab 2 — Map an unfamiliar repository

**Active stage:** `Repository-Orientation-start`
**Skill:** `$orient-repository-with-codex`
**Baseline:** 5 tests pass; Ruff is clean; `REPOSITORY_MAP.md` is absent.
**Outcome:** create an evidence-backed map without changing application or tests.

Submit:

```text
Use $orient-repository-with-codex.
Active stage: Repository-Orientation-start. Do not inspect another *-start folder.

Goal: Build a concise map of the active stage before implementation.

Inspect first: Read the root AGENTS.md and README.md, then the active stage. Identify runtime, verification, entry points, domain logic, persistence, interfaces, and tests.

Boundaries: Do not modify application, configuration, or tests; install dependencies; or run destructive commands. Draft in chat first. When invited, write only Repository-Orientation-start/REPOSITORY_MAP.md. Label facts, inferences, and open questions.

Evidence: Cite a path plus symbol or line for every architectural claim. Trace one representative request or data flow end to end.

Output: purpose/runtime, responsibility table, one flow, likely change points with adjacent tests, evidence-backed risks, open questions, and verification commands. Keep it under 900 words.
```

Challenge one cited claim by opening its source. If evidence is weak, ask Codex to separate proof from inference and revise the row. Then say: `Write only Repository-Orientation-start/REPOSITORY_MAP.md.`

Verify from `Repository-Orientation-start`:

```powershell
git add -N -- REPOSITORY_MAP.md
git diff --check -- .
git diff -- REPOSITORY_MAP.md
python -m pytest -q
python -m ruff check .
```

**Checkpoint:** application and tests are unchanged; the map is evidence-backed. Move to `Planning-Tests-start`.

## Lab 3 — Turn a story into a tested plan

**Active stage:** `Planning-Tests-start`
**Skill:** `$turn-story-into-tested-plan`
**Baseline:** 5 tests pass; `REPOSITORY_MAP.md` exists; `FEATURE_PLAN.md` is absent.
**Outcome:** plan owner filtering without creating tests or implementation.

Submit:

```text
Use $turn-story-into-tested-plan.
Active stage: Planning-Tests-start. Do not inspect another *-start folder.

Goal: Turn this story into an implementation-ready plan:
“As a team lead, I want to filter the task board by owner so I can focus on one teammate's workload.”

Context: Use the active stage's REPOSITORY_MAP.md, relevant source, and current tests. Cite path plus symbol or line for architecture and impact claims.

Decide: Define observable behavior; separate facts, assumptions, constraints, and questions; choose the smallest architecture; trace data flow; name files and methods; identify edge cases and non-goals.

Use behavior IDs: B-01 exact owner; B-02 missing/blank owner means all; B-03 composition with status/priority; B-04 unknown owner uses existing no-results state; B-05 distinct sorted choices retain selection; B-06 global counts and existing filters remain stable. Map each to a named future test and expected observation.

Boundaries: Do not modify application, configuration, or tests. Draft first. When invited, write only Planning-Tests-start/FEATURE_PLAN.md.

Done when: every behavior maps to proof, repository claims cite evidence, the checklist is bounded, existing checks pass, and tests/test_owner_filter.py does not exist.
```

Review exact matching, composition, the All option, choices, blank values, ordering, and global counts. Resolve ambiguity as a decision, assumption, or open question. Then authorize only `FEATURE_PLAN.md`.

Verify from `Planning-Tests-start`:

```powershell
git add -N -- FEATURE_PLAN.md
Test-Path .\tests\test_owner_filter.py  # expect False
python -m pytest -q
python -m ruff check .
git diff --check -- .
git diff -- FEATURE_PLAN.md
```

On POSIX, replace `Test-Path` with `test ! -e tests/test_owner_filter.py`.

**Checkpoint:** keep this folder and treat the approved plan as frozen for Lab 4.

## Lab 4 — Design intentional-red tests

**Active stage:** continue in `Planning-Tests-start`
**Skill:** `$design-intentional-red-tests`
**Input:** the approved `FEATURE_PLAN.md`; application remains unchanged.
**Outcome:** create exactly two tests whose failures identify the missing owner boundary.

Submit:

```text
Use $design-intentional-red-tests.
Active stage: Planning-Tests-start. Treat FEATURE_PLAN.md as frozen and do not inspect another stage.

Select B-01 and B-03. Create exactly these tests in tests/test_owner_filter.py:
- test_list_tasks_can_filter_by_owner
- test_owner_filter_composes_with_status_and_priority

Constraints: Change only tests/test_owner_filter.py. Do not revise the plan, application, configuration, fixtures, or dependencies. Do not skip, xfail, weaken, or mock away behavior.

Before writing: state the behavior ID, fixture evidence, action, and expected observation for each test.

Done when: legacy tests remain green; exactly two new tests fail only because list_tasks lacks owner; Ruff passes; no implementation changed; and you stop at red.
```

Verify from `Planning-Tests-start`:

```powershell
git add -N -- tests/test_owner_filter.py
python -m pytest -q tests/test_tasks.py
python -m pytest -q tests/test_owner_filter.py
python -m ruff check .
git diff --check -- .
git diff -- .
```

An import, fixture, syntax, or unrelated failure is not intentional red. Correct test construction only.

**Checkpoint:** stop with two explained failures. Do not implement in this folder.

## Lab 5 — Implement a focused feature slice

**Active stage:** `Implementation-start`
**Skill:** `$implement-focused-slice`
**Baseline:** 5 legacy tests pass; 2 owner tests fail because `list_tasks` lacks `owner`; the approved map and plan exist.
**Outcome:** implement owner filtering one behavior at a time.

First verify from `Implementation-start`:

```powershell
python -m pytest -q tests/test_tasks.py
python -m pytest -q tests/test_owner_filter.py
```

Continue only when the second command shows the two expected `owner` argument failures. Then submit:

```text
Active stage: Implementation-start. Lab 5. Do not inspect another *-start folder.

Delegate the starting-checkpoint audit to the project checkpoint_auditor agent. Have it use
$verify-workshop-checkpoint, execute the documented Lab 5 baseline, return READY,
EXPECTED_RED, or BLOCKED with exact evidence, and make no edits. Wait for the specialist
before continuing and summarize its disposition.
```

Continue only when the specialist returns `EXPECTED_RED` for five passing legacy tests and
the two documented owner-argument failures. This independent report supplements rather than
replaces the baseline commands you already ran. Then submit:

```text
Use $implement-focused-slice.
Active stage: Implementation-start. Do not inspect another *-start folder.

Use FEATURE_PLAN.md and the two intentional-red owner tests to implement the smallest complete owner-filter slice.

Constraints:
- edit only app/services.py, app/routes.py, app/templates/index.html, and tests/test_owner_filter.py;
- preserve exact case-sensitive matching, task ordering, global counts, and existing behavior;
- exclude blank stored owners from choices because blank means All;
- do not change schema, dependencies, mutation redirects, or styling;
- do not weaken, delete, skip, or xfail tests.

Process: Confirm the red cause. Make only the service change needed for the first green tests and show that diff. Then complete B-02 through B-06 one behavior at a time. Run focused, full, Ruff, and stage-scoped diff checks.

Done when: 11 tests pass, Ruff passes, exactly the four allowed files changed, B-01 through B-06 have evidence, and deferrals are explicit.
```

Verify from `Implementation-start`:

```powershell
python -m pytest -q tests/test_owner_filter.py
python -m pytest -q
python -m ruff check .
git diff --check -- .
git status --short -- .
git diff --stat -- .
git diff -- .
```

**Checkpoint:** move to `Debugging-Extension-start`; do not copy this implementation.

## Lab 6 — Debug from evidence

**Active stage:** `Debugging-Extension-start`
**Skill:** `$debug-from-evidence`
**Baseline:** 11 tests pass and Ruff is clean.
**Outcome:** reproduce and correct a whitespace-owner defect through a falsifiable hypothesis.

First ask Codex to create the controlled failure:

```text
Active stage: Debugging-Extension-start. Do not inspect another stage.
Create only tests/test_debug_owner_choices.py with test_owner_choices_exclude_whitespace_only_values. Insert a Task whose owner is three spaces, commit it to the test database, call list_owners(), and assert owners are exactly ["Avery", "Sam"]. Use existing fixtures/imports. Do not change production code.
```

Run:

```powershell
git add -N -- tests/test_debug_owner_choices.py
python -m pytest -q tests/test_debug_owner_choices.py
```

Expect one failure showing the whitespace-only choice. Then submit:

```text
Use $debug-from-evidence.
Active stage: Debugging-Extension-start. Diagnose the captured owner-choice failure before editing.

Inspect the assertion, fixture data, owner-choice query, and adjacent owner tests.

Constraints: edit only app/services.py and tests/test_debug_owner_choices.py; preserve matching, ordering, duplicate suppression, counts, and empty-string behavior; do not change model, schema, seed, dependencies, or UI; do not weaken the expectation.

Process: reproduce; report observed vs expected; trace to the nearest query boundary; state one falsifiable hypothesis and disproof; run the smallest experiment with a prediction; apply the minimum correction only when supported; verify focused, adjacent, full, Ruff, and diff.

Return symptom, evidence, root cause, correction, proof, and uncertainty. Do not create another repository file.
```

Verify from `Debugging-Extension-start`:

```powershell
python -m pytest -q tests/test_debug_owner_choices.py
python -m pytest -q tests/test_owner_filter.py
python -m pytest -q
python -m ruff check .
git diff --check -- .
git diff -- .
```

**Checkpoint:** keep the corrected service and regression; continue here for Lab 7.

## Lab 7 — Extend behavior with guardrails

**Active stage:** continue in `Debugging-Extension-start`
**Skills:** `$design-intentional-red-tests`, then `$implement-focused-slice`
**Input:** Lab 6 is green and frozen.
**Outcome:** preserve approved filters after status updates without accepting a caller-controlled destination.

Ask for tests first:

```text
Use $design-intentional-red-tests.
Active stage: Debugging-Extension-start. Lab 6 is frozen.

Create only tests/test_filter_context.py with four behavioral tests proving: the rendered status form carries status/priority/owner through GET to POST to redirect; rejected updates preserve them; arbitrary return fields/external URLs are ignored and redirect stays internal; blank values are dropped.

Use only status, priority, and owner as approved keys. Do not edit application or existing tests. Run the new file and explain every pass/failure, then stop at the characterized red state.
```

After reviewing those failures, submit:

```text
Use $implement-focused-slice.
Active stage: Debugging-Extension-start. The four filter-context tests are approved.

Goal: Preserve nonblank status, priority, and owner after successful and rejected status updates.

Constraints: edit only app/routes.py, app/templates/index.html, tests/test_filter_context.py, and an adjacent test only if the full suite proves irrelevant markup coupling; always redirect to the internal board; never accept a destination URL; preserve Lab 6, query semantics, models, counts, styling, dependencies, and note behavior.

Done when: four redirect tests pass, blanks/arbitrary return fields are ignored, full suite and Ruff pass, and note-filter persistence remains deferred.
```

Verify from `Debugging-Extension-start`:

```powershell
git add -N -- tests/test_filter_context.py
python -m pytest -q tests/test_debug_owner_choices.py tests/test_filter_context.py
python -m pytest -q tests/test_owner_filter.py
python -m pytest -q
python -m ruff check .
git diff --check -- .
git diff -- .
```

**Checkpoint:** move to `Review-Refactor-start`; note submission remains intentionally deferred.

## Lab 8 — Review and correct generated code

**Active stage:** `Review-Refactor-start`
**Skill:** `$review-generated-code`
**Baseline:** 16 tests pass and Ruff is clean.
**Outcome:** identify and correct a green-but-unsafe redirect.

> This candidate is deliberately unsafe. Use it only in this workshop stage.

Create the candidate:

```text
Active stage: Review-Refactor-start. Prepare a review candidate only; do not add tests. In create_note, read a trimmed return_to from form data and redirect to it when nonblank, otherwise to task index. Add a hidden return_to containing request.full_path. Change only app/routes.py and app/templates/index.html. Show the diff.
```

Run the existing checks. They may remain green; that is the lesson.

```powershell
python -m pytest -q
python -m ruff check .
git diff -- .
```

Now run the independent security-review demonstration:

```text
Active stage: Review-Refactor-start. Lab 8. Do not inspect another *-start folder.

Delegate review of the complete note-context diff to the project security_reviewer agent.
Have it use $review-generated-code, trace every request-controlled value to its final
destination, rank findings, specify the smallest regression proof, and make no edits. Wait
for the specialist and return its report before proposing a correction.
```

Do not continue unless the specialist ranks the caller-controlled redirect destination as
the highest-risk finding and stops without editing. Now submit:

```text
Use $review-generated-code.
Active stage: Review-Refactor-start. Review the complete note-context diff before editing.

Goal: Preserve active task filters after note submission.

Use the security_reviewer report as independent input, then inspect the complete diff
yourself. Review correctness, security, maintainability, readability, scope, and test
adequacy. Trace every request-derived value to its destination. Preserve status-update
behavior; add no dependency or navigation redesign; separate evidence from preference.

Return ranked findings, an accept/correct/reject/defer disposition for each meaningful change, the smallest regression test for confirmed defects, and a bounded correction plan. Do not edit until findings are ranked.

After approval, implement only the correction and tests. Create REVIEW_NOTES.md. Keep the destination fixed to the internal task index and preserve only nonblank status, priority, and owner. Do not add a pure helper, template macro, or REFACTOR_NOTES.md.
```

Do not approve correction until the request-controlled destination is the highest-risk finding.

Verify from `Review-Refactor-start`:

```powershell
git add -N -- tests/test_note_filter_context.py REVIEW_NOTES.md
python -m pytest -q tests/test_note_filter_context.py tests/test_filter_context.py
python -m pytest -q
python -m ruff check .
git diff --check -- .
git diff -- .
```

**Checkpoint:** expect approximately 20 green tests. Keep this folder for Lab 9.

## Lab 9 — Refactor safely

**Active stage:** continue in `Review-Refactor-start`
**Skill:** `$refactor-with-guardrails`
**Input:** corrected Lab 8 behavior and approximately 20 green tests.
**Outcome:** improve structure in two reversible steps without behavior change.

Submit:

```text
Use $refactor-with-guardrails.
Active stage: Review-Refactor-start. Lab 8 behavior, tests, and dispositions are frozen.

Problem: filter extraction is coupled to request state and hidden-field markup repeats across mutation forms.

Preserve the internal task-index destination; status/priority/owner allowlist; blank removal; success/error redirects; task ordering; messages; and persistence.

Constraints: change only app/routes.py, app/templates/index.html, focused tests, REVIEW_NOTES.md only for clarification, and new REFACTOR_NOTES.md. Introduce no feature or dependency. Keep tests behavioral.

Process: first introduce one pure filter-dictionary helper and verify focused/full. Only then introduce one template macro and verify again. Record before/after responsibilities and evidence in REFACTOR_NOTES.md.

Done when: helper is independent of request globals, macro removes repeated markup, approximately 20 tests remain green, Ruff passes, and notes claim no feature change.
```

After each transformation, run from `Review-Refactor-start`:

```powershell
git add -N -- REFACTOR_NOTES.md
python -m pytest -q tests/test_note_filter_context.py tests/test_filter_context.py
python -m pytest -q
python -m ruff check .
git diff --check -- .
git diff -- .
```

**Checkpoint:** accept only if behavior stayed fixed and responsibilities are easier to explain.

## Lab 10 — Prepare the developer handoff

**Active stage:** `Handoff-start`
**Skill:** `$prepare-developer-handoff`
**Baseline:** 20 tests pass; map, plan, review notes, and refactor notes exist.
**Outcome:** create a reviewer-ready handoff and capstone evidence without changing code.

First run from `Handoff-start`:

```powershell
python -m pytest -q
python -m ruff check .
git status --short -- .
```

Then submit:

```text
Use $prepare-developer-handoff.
Active stage: Handoff-start. Do not inspect another stage.

Create only TEAM_HANDOFF.md and CAPSTONE_EVIDENCE.md.

TEAM_HANDOFF.md must state the reviewer decision, outcome/scope, observable behavior, executed verification, decisions/tradeoffs, risks/limitations, deferrals, and review steps.

CAPSTONE_EVIDENCE.md must trace inspect → clarify → plan → test → implement → debug → review → refactor → verify → handoff to durable repository evidence.

Do not modify application, tests, dependencies, or existing evidence. Support material claims with an executed command result, file, test, or revision. Separate completed, deferred, and not assessed. Exclude secrets, personal data, machine paths, and unexecuted-check claims.

Done when: another engineer can decide whether to accept the work and reproduce its verification; only the two requested documents changed.
```

Verify from `Handoff-start`:

```powershell
git add -N -- TEAM_HANDOFF.md CAPSTONE_EVIDENCE.md
python -m pytest -q
python -m ruff check .
git diff --check -- .
git status --short -- .
git diff -- TEAM_HANDOFF.md CAPSTONE_EVIDENCE.md
```

Run the final independent audit:

```text
Active stage: Handoff-start. Lab 10 completion audit. Do not inspect another *-start folder.

Delegate the completion audit to the project checkpoint_auditor agent. Have it use
$verify-workshop-checkpoint, verify the Lab 10 tests, Ruff, allowed two-document scope, diff
quality, and reproducible evidence, and make no edits. Wait for a READY or BLOCKED
disposition and summarize the exact executed evidence.
```

Accept the handoff only when the specialist returns `READY` and its evidence agrees with the
commands you ran. Review as the recipient: What decision is requested? What behavior changed?
What evidence is reproducible? What is deferred or unassessed? What should be inspected first?

**Checkpoint:** you completed inspect → decide → prove → review → hand off.

## Recovery

Your work is recoverable because bootstrap tags the course baseline as `workshop-start`. Reset restores that tag even if a learner accidentally creates a later commit.

Preview a stage reset from the repository root:

```powershell
.\scripts\reset-stage.ps1 -Stage Foundations-start
```

The preview exits successfully and makes no changes. Confirmation discards tracked/untracked source changes plus known ignored workshop state in that stage: the local SQLite `instance/`, Python/test/Ruff caches, bytecode, and `.env`. To reset only the named stage:

```powershell
.\scripts\reset-stage.ps1 -Stage Foundations-start -ConfirmReset
```

On POSIX, use `sh scripts/reset-stage.sh Foundations-start` to preview and append `--yes` to confirm. Never reset a paired stage between its two labs unless you intend to restart both.

## Troubleshooting

### The checkpoint differs before I start

Stop. Run the active stage's documented baseline, then run the root preflight. Confirm the correct stage and expected intentional failures. Reset only that stage if you have no work to preserve.

### Codex proposes different but valid code

Compare observable behavior, boundaries, and evidence—not line-for-line output. Ask Codex to explain the tradeoff before deciding.

### Codex cannot find a project agent

Confirm that `.codex/agents/checkpoint_auditor.toml` and
`.codex/agents/security_reviewer.toml` exist, update the Codex client, and start a new chat
with the repository root as the workspace. CLI users can run `codex features list` and
confirm that `multi_agent` is enabled. Do not substitute an editing agent for either
specialist. The deterministic lab commands remain the source of truth, but the named
multi-agent demonstration is incomplete until the project agent loads.

### A focused test fails unexpectedly

Say:

```text
Do not edit yet. Separate the observed failure from inference, identify the nearest responsible boundary, and propose one falsifiable hypothesis plus the smallest experiment.
```

### The diff includes unrelated files

Do not delete work you do not understand. Scope status and diff to the active stage. Ask Codex to revert only named edits it made during the current lab, or reset the stage only when you have decided to discard all of its work.

### Focused checks pass but the full suite fails

Treat the full failure as evidence. Do not weaken it. Decide whether production broke an existing contract or an adjacent test is coupled to an irrelevant detail.

### I closed my terminal

Reactivate the one shared environment from the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
```

On POSIX: `source .venv/bin/activate`.

### PowerShell says running scripts is disabled

Allow local scripts only for the current terminal session, then rerun bootstrap or activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Bootstrap says `.venv` is stale

The environment belongs only to this workshop checkout and can be recreated. Remove the root `.venv` directory—not a stage folder—then rerun bootstrap. Do not remove source files or use a broad clean command.

## Final self-assessment

You are ready to reuse this workflow when you can answer yes to each statement:

- I state goal, context, constraints, and done evidence before editing.
- I distinguish repository fact, inference, hypothesis, decision, and assumption.
- I stop at planning-only and intentional-red checkpoints.
- I work one behavior through red, green, and safe refactor.
- I run focused-to-broad verification and inspect a scoped diff.
- I debug from observations and falsifiable hypotheses.
- I trace untrusted input across a trust boundary.
- I use an independent specialist for checkpoint evidence or security review without delegating edits.
- I separate behavior correction from structure-only refactoring.
- I hand another engineer reproducible evidence instead of unsupported claims.
