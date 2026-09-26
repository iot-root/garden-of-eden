# GEMINI.md

Garden of Eden is a Python 3.9+ Raspberry Pi garden controller.

## Read first

@context_documentation/project-context.md

Read these when the task touches them:

- `CONTRIBUTORS.md` - Conventional Commit format (required for all commits).
- `context_documentation/README.md` - documentation bank conventions.
- `context_documentation/pi-operations.md` - connecting to the Pi, running repo scripts there.
- `context_documentation/known-issues.md` - confirmed limitations and operational risks.

Read nearby implementation and tests before editing. Keep changes focused and
follow existing patterns.

## Repository conventions

- This is a Python 3.9+ Raspberry Pi garden controller.
- Application code lives in `app/`; Pi-only operational scripts live in `bin/`.
- Prefer existing helpers, configuration, routes, and test patterns over new abstractions.
- Keep hardware-specific behavior testable through the existing simulator and hardware stubs where practical.
- Pins, I2C addresses, thresholds, and paths belong in `config.py` (read from `.env`), never hardcoded in a driver.
- Drivers: `app/sensors/<name>/<name>.py`. Routes: `app/sensors/<name>/routes.py`, a Flask Blueprint with every route wrapped in `check_sensor_guard`.
- Use `logging.getLogger(__name__)`, never `print`.
- Never commit `.env` files, credentials, API keys, private keys, personal usernames, private IP addresses, or other machine-specific values. Keep personal Pi values in local environment variables (`GARDEN_PI_USER`, `GARDEN_PI_HOST`) or `GEMINI.local.md`.
- Use ASCII for new files unless the content clearly requires another character set.
- Avoid unrelated refactors, formatting churn, and changes to user-owned worktree modifications.

## Validation

Use the project development environment when available:

```bash
.venv-dev/bin/python -m pytest
.venv-dev/bin/ruff check .
.venv-dev/bin/black --check .
```

For a focused change, run the narrowest relevant test or check first. Always run `git diff --check` before finishing. Note: `python -m unittest` must use `-t . -s tests` so `tests/__init__.py` installs the hardware stubs before `app/` imports.

## Commit messages

Use the Conventional Commit format defined in `CONTRIBUTORS.md`:

```text
<type>(<optional scope>): <brief description>
```

Use lowercase types such as `feat`, `fix`, `docs`, `test`, `refactor`, `style`, or `chore`. Keep the subject concise and add a body only when more context is useful. Do not create commits unless explicitly requested.
