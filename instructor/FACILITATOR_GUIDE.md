# Facilitator Guide

This guide is for course delivery and repository maintenance. Students should follow the root `README.md`.

## Before class

1. Run `python scripts/verify_workshop.py` with Python 3.12.
2. Confirm CI is green on Windows and Ubuntu.
3. Recheck the official Codex CLI/IDE links and `codex login status` command.
4. Complete setup from a fresh clone on the classroom network.
5. Keep one untouched clone available for recovery demonstrations.

After committing the complete candidate and creating the `workshop-start` tag, run the release gate:

```powershell
python scripts/verify_workshop.py --release
```

This additionally requires a clean worktree and confirms that every critical student asset is tracked.

## Checkpoint matrix

| Stage | Expected start | Required recovery decision |
| --- | --- | --- |
| Foundations | 5 green | reset after Lab 1 only if learner wants to repeat |
| Repository Orientation | 5 green; map absent | application/test edits are out of scope |
| Planning/Tests | 5 green; map present | preserve Lab 3 plan for Lab 4 |
| Implementation | 5 legacy green; 2 owner failures | failures must be missing `owner`, not test construction |
| Debugging/Extension | 11 green | preserve Lab 6 correction for Lab 7 |
| Review/Refactor | 16 green | preserve Lab 8 correction for Lab 9 |
| Handoff | 20 green | only two new handoff documents are allowed |

## Coaching standard

- Ask for the observed behavior and evidence before suggesting code.
- Accept implementation variation when the behavior contract, scope, and verification are equivalent.
- Stop learners at planning-only and intentional-red checkpoints.
- Never solve a lab by opening a later stage. Use the checkpoint matrix and agent scenario matrix instead.
- Treat the unsafe redirect in Lab 8 as the required highest-risk finding.
- Use stage-scoped status and diff because the course has one root Git repository.

## Developer-agent forward test

`.agents/evals/cases.json` contains ten clean-room cases. After changing `AGENTS.md` or a skill, copy the named stage to a disposable checkout, start a fresh Codex chat, invoke the named skill with the case prompt, and score only the listed `must`/`must_not` observations. Do not show the expected observations to the agent. Record failures as instruction or skill defects, fix the smallest shared cause, and rerun the affected case plus the stage-isolation case.

## Recovery

Preview before reset:

```powershell
.\scripts\reset-stage.ps1 -Stage <exact-stage-name>
```

Confirm only after the learner agrees to discard all work in that stage. Paired labs lose both labs' work when their shared stage is reset.

## Acceptable variation

Names, assertion style, helper shape, and template markup may differ. Require the same observable behavior, explicit constraints, expected test state, and stage-scoped diff. Do not accept skipped tests, broader schemas/dependencies, request-controlled redirect destinations, or unsupported handoff claims.
