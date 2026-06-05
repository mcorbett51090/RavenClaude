---
name: example-testing-setup
description: "Setup guide for testing code examples in documentation CI — covers doctest, snippet extraction, execution sandboxing, and the failure-handling policy to ensure every published example actually runs."
---

# Example Testing Setup

## When to Use This

Your docs contain code examples that may silently rot as the API evolves. Use this skill to wire example testing into CI so every example is verified on every PR and release.

## Strategy Selection

| Doc toolchain | Example type | Recommended approach |
|---|---|---|
| Any | Shell/CLI commands | Extract + run in CI with `script -q -c "..."` or bash |
| Python project | Python snippets | doctest or pytest with extracted snippets |
| Node/JS project | JS/TS snippets | Jest or Vitest with imported snippet files |
| OpenAPI spec | Request/response examples | Dredd or Schemathesis against a running service |
| Any | Multi-language | mdbook's `{{#include}}` or Docusaurus `@theme/CodeBlock` with test runner |

**Core principle:** examples live in source files that are imported into docs, never pasted inline. The test runs the source file; the doc renders it.

## Pattern 1 — Include-from-File

Instead of inline fenced code blocks, maintain runnable source files:

```
docs/
  examples/
    quickstart.py       ← the actual runnable file
    auth-example.py
  quickstart.md         ← imports from examples/
```

In Docusaurus MDX:
```mdx
import CodeBlock from '@theme/CodeBlock';
import QuickstartSource from '!!raw-loader!./examples/quickstart.py';

<CodeBlock language="python">{QuickstartSource}</CodeBlock>
```

The test CI step simply runs all files under `docs/examples/`:

```yaml
- name: Test documentation examples
  run: |
    for f in docs/examples/*.py; do
      echo "Testing $f"
      python "$f" || exit 1
    done
```

## Pattern 2 — Doctest (Python)

Embed testable examples directly in docstrings and markdown using `doctest`:

```python
def calculate_discount(price: float, pct: float) -> float:
    """
    >>> calculate_discount(100.0, 10)
    90.0
    >>> calculate_discount(50.0, 0)
    50.0
    """
    return price * (1 - pct / 100)
```

CI step:
```yaml
- name: Run doctests
  run: python -m doctest -v docs/**/*.md
```

Limit doctest to **self-contained expressions**. Long setup sequences belong in Pattern 1.

## Pattern 3 — OpenAPI Request/Response Validation

For API reference docs, validate that request/response examples in the OpenAPI spec actually match the live service:

```yaml
# Using Schemathesis
- name: Test API examples
  run: |
    schemathesis run docs/openapi.yaml \
      --base-url http://localhost:8080 \
      --checks all \
      --contrib-openapi-formats-uuid \
      --hypothesis-max-examples 50
```

Or with Dredd for exact example matching:
```yaml
- name: Dredd API tests
  run: dredd docs/openapi.yaml http://localhost:8080
```

## CI Integration

```yaml
# .github/workflows/docs.yml (relevant excerpt)
jobs:
  test-examples:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Start service
        run: docker compose up -d && sleep 5
      - name: Test examples
        run: make test-docs-examples
      - name: Link check
        run: npx --yes @umbrellio/check-links docs/
```

## Failure Handling Policy

When an example fails in CI:

1. **The PR is blocked** — a failing example is a bug in the docs, not a documentation style issue.
2. **The fix must come before the merge** — no exceptions for "we'll fix the docs later."
3. **If an example is intentionally broken** (illustrating an error condition), mark it explicitly:
   ```python
   # This example deliberately raises an error:
   # >>> connect_without_auth()
   # AuthenticationError: No credentials provided
   ```
   Wrap it in an expect-failure harness or exclude it from the test runner with a comment.

## Pitfalls

- Inline copy-pasted examples that drift from the actual API — fix by using Pattern 1 (include from file).
- Testing examples only against a mock/stub service — if the mock is out of date, examples can pass and still be wrong for real users. Run against a real service in at least one CI stage.
- Letting the example test job be advisory (allowed to fail) — the moment it's advisory, nobody fixes it and it becomes noise within weeks.
- Long-running setup in examples — each example should set up and tear down its own state; shared state between examples makes failures hard to diagnose.

## See Also

- [`../../agents/docs-site-engineer.md`](../../agents/docs-site-engineer.md) — CI build/deploy, link-checking, and example testing wiring
- [`../../agents/api-reference-writer.md`](../../agents/api-reference-writer.md) — runnable examples in API reference
