# Safe refactor notes

## Contract preserved

- Both status and note mutations return to the internal task index.
- Only nonblank status, priority, and owner values survive the redirect.
- Successful and rejected mutations follow the same redirect rule.
- Existing task ordering, messages, and persistence behavior remain unchanged.

## Before and after

Before, redirect filtering was coupled to Flask request state and hidden-field markup was duplicated. After, one pure helper builds the allowlisted filter dictionary and one template macro renders the shared fields.

Evidence: 20 behavioral tests pass, including the rendered note-form path. Ruff is clean, and the final diff is limited to the route, template, focused tests, and these review artifacts.
