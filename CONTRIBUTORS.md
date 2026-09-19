# Contributors

Thank you to all the contributors who have helped improve this project! Please follow the guidelines below for issues, pull requests and commit messages.

## Issues

Every change starts with an issue. Use the issue templates: a bug report needs the steps to reproduce it, the hardware (Gardyn model and Pi) and the version you're running. Code-quality issues don't need a repro, but should say what's wrong and where.

Keep to one problem per issue so a PR can close it cleanly.

## Pull Requests

The **PR rules** check enforces these on every pull request:

- **One issue per PR.** The description links the issue it resolves with `Closes #<issue>` (or `Refs #<issue>` for partial work). The link must point to an issue, not another PR.
- **Small enough to review.** At most 400 changed lines across 20 files, not counting `tests/`, `docs/` and Markdown. Split bigger work into several PRs. A maintainer can waive the limit with the `large-pr-approved` label.
- **Title is a Conventional Commit**, 72 characters or fewer (see below). PRs are squash-merged, so the title becomes the commit that release-please uses for the changelog and version.
- **Branch is named after the change**: `<type>/<short-description>` in lowercase kebab-case, e.g. `fix/pump-speed-when-off`. Don't open PRs from `main` or name branches after a version; release-please decides versions.

CI also runs lint (ruff, black), the unit tests on Python 3.9 and 3.11, a shell-script check, and a check that no secret files (`.env`, keys, credentials) are tracked.

### Changes that build on each other

Open them as separate PRs and stack them: base each branch on the previous one with `git rebase`, and write `Depends on #<pr>` in the description so they're reviewed in order. If one PR in the chain is rejected, rebase the later ones onto the last accepted PR.

Don't bundle several open PRs into one to avoid conflicts. Smaller PRs are easier to review, and a reviewer can accept some without the rest.

### Testing

Run the tests off-Pi before opening a PR:

```bash
python -m unittest discover -t . -s tests -p 'test_*.py'
ruff check . && black --check .
```

If the change touches hardware behaviour (GPIO, I2C, pump, light, sensors), say in the PR whether and how you tested it on a unit.

## Commit Message Guidelines

Your commit messages should follow the conventional commit format:

```
<type>(<optional scope>)<place-!-for-breaking-changes>: <description>

[optional body]

[optional footer]
```

### Type

The `<type>` should be one of the following:

- `feat`: A new feature.
- `fix`: A bug fix.
- `docs`: Documentation updates.
- `style`: Changes that do not affect code (e.g., formatting, white-space, etc.).
- `refactor`: Code changes that neither fix a bug nor add a feature.
- `perf`: A change that improves performance.
- `test`: Adding or modifying tests.
- `build`: Changes to packaging or dependencies (requirements, Dockerfile).
- `ci`: Changes to CI workflows.
- `chore`: Other maintenance that doesn't change the code's behaviour.
- `revert`: Reverts a previous commit.

### Scope (optional)

The `<scope>` should indicate the scope of the commit (e.g., component, module, etc.). It is optional if the commit applies globally.

### Description

The `<description>` should provide a brief summary of the change.

### Breaking Changes

For breaking changes include an '!' after the scope and elaborate a bit in the body.

```
feat!: some breaking change description

<body description>

BREAKING CHANGE: <what-broke-description>
```

### Body (optional)

The `<body>` should provide more detailed information about the change. It can span multiple lines.

### Footer (optional)

The `<footer>` should contain any additional information related to the commit, such as references to issues or breaking changes.

```
Refs: #100,#101,etc

or 

BREAKING CHANGE: breaks some interface
```

## Examples

### Good Examples

- ✅ `feat: Add user authentication`
- ✅ `fix(auth): Resolve issue with login logic`
- ✅ `fix(scope/another-scope/some-scope): commit subject with multiple scopes`
- ✅ `docs: Update README with new examples`
- ✅ `style: Format code according to style guide`
- ✅ `refactor: Simplify data processing method`
- ✅ `test: Add unit tests for API endpoints`
- ✅ `chore: Upgrade dependencies to latest versions`

### Bad Examples

- ❌ `added new feature`
- ❌ `Fixed the login bug`
- ❌ `Documentation updates`
- ❌ `Fix formatting`
- ❌ `Changed some code`
- ❌ `Added tests`
- ❌ `Updated dependencies`

Remember to follow these guidelines when making contributions. Consistent and clear commit messages help maintain a healthy and easily understandable codebase.

Thank you again for your contributions! 🙌

## Community and Volunteering

Please have a look at the [Volunteer](https://github.com/iot-root/garden-of-eden/wiki/Volunteer) page for instructions on where to start and more.
