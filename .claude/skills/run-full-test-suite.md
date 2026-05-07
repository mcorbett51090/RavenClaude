---
name: run-full-test-suite
description: Run the project's full quality gate — format check, lint, typecheck, unit tests, integration tests — in order, fail fast, summarize. Use before reporting any non-trivial change as complete.
---

# Skill: run-full-test-suite

Run the gates in §4 of CLAUDE.md, in order. Stop at the first failure and report what failed and where.

## Default invocation order
The exact commands depend on the project. Detect them once and cache the answer in this file's `## Project commands` section below; subsequent runs use the cache.

```
1. format check     # e.g. prettier --check ., ruff format --check, gofmt -l
2. lint             # e.g. eslint ., ruff check, golangci-lint run
3. typecheck        # e.g. tsc --noEmit, mypy, pyright
4. unit tests       # e.g. vitest run, pytest -q, go test ./...
5. integration tests # if a separate command exists
6. build            # only if the project ships a compiled artifact
```

## Detection rules
- `package.json` → look for `scripts.format`, `scripts.lint`, `scripts.typecheck`, `scripts.test`. Prefer these over guessing.
- `pyproject.toml` → check `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest]`.
- `Makefile` → if `make test`, `make lint`, `make check` exist, prefer them.
- `go.mod` → standard `go vet ./... && go test ./...`.

## Behavior contract
- **Fail fast.** Don't run unit tests if lint failed.
- **Don't auto-fix without permission.** Detection of a fixable lint issue → report it; let the human decide.
- **Report exit codes.** Always include the failing command and its exit code in the output.
- **Time each stage.** If a stage takes > 60s, surface the duration so the team can spot regressions.

## Output format
```
[1/5] format    ✅  (1.2s)
[2/5] lint      ✅  (3.4s)
[3/5] typecheck ❌  (8.1s)
                exit 2
                src/auth/session.ts:42 — Type 'string | undefined' is not assignable to type 'string'

Stopped at typecheck. Earlier stages passed.
```

## Project commands (filled in on first run)
<!-- Edit this block once with the project's actual commands -->
```
format:        <command>
lint:          <command>
typecheck:     <command>
unit:          <command>
integration:   <command>
build:         <command>
```
