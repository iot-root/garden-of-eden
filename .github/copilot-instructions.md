# Copilot Instructions

## Read first

Before making changes, read the relevant context from:

- `CONTRIBUTORS.md` for Conventional Commit rules.
- `ai-doc-bank/README.md` for the documentation bank conventions.
- `ai-doc-bank/project-context.md` for architecture, paths, and validation commands.
- `ai-doc-bank/pi-operations.md` for Raspberry Pi operational guidance.

Read nearby implementation and tests before editing. Keep changes focused on the requested behavior and follow existing patterns.

## Repository conventions

- This is a Python 3.9+ Raspberry Pi garden controller.
- Application code lives under `app/`; operational scripts live under `bin/` and are intended to run on the Pi.
- Prefer existing helpers, configuration, routes, and test patterns over new abstractions.
- Keep hardware-specific behavior testable through the existing simulator and hardware stubs where practical.
- Do not commit `.env` files, credentials, API keys, private keys, personal usernames, private IP addresses, or other machine-specific values.
- Keep Pi connection values in local environment variables such as `GARDEN_PI_USER` and `GARDEN_PI_HOST`.
- Use ASCII for new files unless the content clearly requires another character set.
- Avoid unrelated refactors, formatting churn, and changes to user-owned worktree modifications.

## Validation

Use the project development environment when available:

```bash
.venv-dev/bin/python -m pytest
.venv-dev/bin/ruff check .
.venv-dev/bin/black --check .
```

For a focused change, run the narrowest relevant test or check first. Always run `git diff --check` before finishing.

## Documentation

Update the relevant documentation when behavior or operational procedures change. Put durable project knowledge in `ai-doc-bank/` and link new documents from `ai-doc-bank/README.md`. Keep personal machine configuration out of committed documentation.

## Commit messages

Use the Conventional Commit format defined in `CONTRIBUTORS.md`:

```text
<type>(<optional scope>): <brief description>
```

Use lowercase types such as `feat`, `fix`, `docs`, `test`, `refactor`, `style`, or `chore`. Keep the subject concise and add a body only when more context is useful. Do not create commits unless explicitly requested.
