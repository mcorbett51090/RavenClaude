# Contributing to <project>

> Template for `CONTRIBUTING.md`. The CONTRIBUTING file is *operations* — it converts a drive-by into a contributor. Keep it concrete and short. Replace every `<placeholder>`.

Thanks for your interest in contributing to **<project>**! This guide covers how to propose changes.

## Ways to contribute
- **Report a bug** — open an issue using the bug template; include version, environment, and a minimal reproduction.
- **Request a feature** — open a discussion/issue describing the problem first, not just the solution.
- **Submit a fix** — see "Pull requests" below. Look for [`good-first-issue`](<good-first-issue-url>) to start.
- **Improve docs** — docs PRs are first-class and very welcome.

## Before you start
- Read the Code of Conduct (`CODE_OF_CONDUCT.md`).
- For anything non-trivial, **open an issue first** so we can agree on the approach before you invest time.

## Development setup
```bash
<clone + install + test commands>
```

## Pull requests
1. Fork and create a branch: `<type>/<short-slug>` (e.g. `fix/connection-pool-race`).
2. Make focused changes with tests; keep the PR scoped to one thing.
3. Update the `[Unreleased]` section of the project `CHANGELOG.md`.
4. Ensure CI is green (lint, tests, format).
5. **Sign off your commits** (`git commit -s`) — this project uses the [DCO](https://developercertificate.org/). *(Or: this project requires a CLA — see <cla-url>.)*

## Commit messages
<We use Conventional Commits (feat:/fix:/docs:/…) — releases are automated from them.>
*(Or: keep messages clear and imperative; no strict convention required.)*

## Review & merge
- A maintainer responds within <SLA, e.g. 3 business days>.
- Address review comments by pushing follow-up commits (we squash on merge).
- Out-of-scope PRs may be declined with a reason — thank you regardless.

## Getting help
Ask in <discussions/Discord/Matrix link>. For **security issues**, do NOT open a public issue — see the project `SECURITY.md`.
