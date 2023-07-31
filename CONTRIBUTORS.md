# CONTRIBUTORS

Thank you to all the contributors who have helped improve this project!

## Commit Message Guidelines

Please follow the below guidelines for your commit messages:

## Format

Your commit messages should follow the Conventional Commit format:

```
<type>(<optional scope>)<place-!-if-breakingchange>: <description>

[optional body]

[optional footer]
```

## Type

The `<type>` should be one of the following:

- `feat`: A new feature.
- `fix`: A bug fix.
- `docs`: Documentation updates.
- `style`: Changes that do not affect code (e.g., formatting, white-space, etc.).
- `refactor`: Code changes that neither fix a bug nor add a feature.
- `test`: Adding or modifying tests.
- `chore`: Changes to the build process, tooling, etc.

### Scope (optional)

The `<scope>` should indicate the scope of the commit (e.g., component, module, etc.). It is optional if the commit applies globally.


### Breaking Changes !

For breaking changes include a '!' after the <type>(<scope>)!: some breaking change.

```
feat!: some breaking change

<body description>

BREAKING CHANGE: <what-broke-description>
```

### Description

The `<description>` should provide a brief summary of the change.

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

## Volunteer

Very nice!! :)

Please have a look at the [Volunteer](https://github.com/iot-root/gardyn-of-eden/wiki/Volunteer)
page for instructions on where to start and more.