<!--
Title: a Conventional Commit, 72 characters max, e.g. `fix(pump): stop speed/set starting the pump when off`
Branch: <type>/<short-description>, e.g. `fix/pump-speed-when-off` (not `main`, not a version)
One issue per PR. Rules are checked automatically; see CONTRIBUTORS.md.
-->

Closes #

<!-- If this builds on another open PR, say so and it will be reviewed after that one: -->
<!-- Depends on # -->

## What changed and why

## How it was tested

- [ ] Unit tests pass: `python -m unittest discover -t . -s tests -p 'test_*.py'`
- [ ] `ruff check . && black --check .`
- [ ] Tested on hardware (model / Pi): <!-- or explain why not needed -->

## Checklist

- [ ] This PR does one thing and resolves the linked issue
- [ ] New behaviour has tests
- [ ] Docs and `.env-dist` are updated if config, endpoints, topics or setup changed
- [ ] Breaking changes are marked with `!` in the title and explained in the description
