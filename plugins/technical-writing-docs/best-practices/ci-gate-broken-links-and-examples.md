# Gate the Docs Build on Broken Links and Failing Examples

**Status:** Absolute rule
**Domain:** Technical Writing — Docs-as-code / CI
**Applies to:** `technical-writing-docs`

---

## Why this exists

A broken link in documentation destroys the reader's path at precisely the moment they need to follow it. A code example that returns an error when copied and run destroys trust faster than missing documentation — the reader followed the official guide and it didn't work. Both failures are mechanically detectable and mechanically preventable. Checking them manually on every release is not a process; gating the build on them is.

## How to apply

**Two gates, both required:**

**Gate 1 — Broken link check:**

```yaml
# Example: lychee link checker in GitHub Actions
- name: Check links
  uses: lycheeverse/lychee-action@v1
  with:
    args: --verbose --no-progress 'docs/**/*.md' 'docs/**/*.html'
    fail: true
```

Or using the docs framework's built-in checker:
```bash
# Docusaurus
npx docusaurus build   # --broken-links=throw is the default in v3

# MkDocs
mkdocs build --strict   # treats warnings (broken links) as errors
```

**Gate 2 — Code example execution:**

```yaml
# Example: run extracted snippets as integration tests
- name: Run doc examples
  run: |
    python scripts/extract-and-test-examples.py docs/
    # Each code block tagged ```python test is extracted and run
```

Strategies by language/framework:

| Language | Approach |
|---|---|
| Python | `doctest` module; or extract + `pytest` |
| JavaScript/TypeScript | Extract snippets; run with `node` or `jest --testPathPattern=docs` |
| Shell | `shellcheck` for linting; `bats` for execution |
| OpenAPI examples | `redocly lint --extends recommended` checks example conformance against the schema |

**Do:**
- Run both checks on every PR that touches `docs/`, not just on release branches.
- Distinguish *internal* broken links (fixable) from *external* links (which can break at any time); check external links on a schedule (weekly), not on every PR.
- Label code blocks that should be tested (`test`) vs display-only (`no-test`) so the extraction script doesn't try to run pseudo-code.

**Don't:**
- Ignore link-check failures with a global allowlist — investigate each one.
- Skip the gate for "just docs" PRs — docs PRs are where broken links are introduced.
- Treat a link to an anchor (`#section-name`) as automatically valid — anchor links break when headings are renamed.

## Edge cases / when the rule does NOT apply

- **Docs sites with a lot of external links to third-party content**: check external links weekly in a scheduled job, not on every PR, to avoid rate-limiting and transient failures blocking unrelated work.
- **Display-only pseudocode or partial snippets**: mark explicitly as non-executable; the gate skips them. Do not let the labeling become a workaround to avoid fixing real broken examples.

## See also

- [`../agents/docs-site-engineer.md`](../agents/docs-site-engineer.md) — owns the docs build and CI integration
- [`./examples-must-run.md`](./examples-must-run.md) — the principle this gate enforces mechanically

## Provenance

Codifies house opinion #3 ("Examples must run") and house opinion #2 ("Docs-as-code") applied at the CI layer. Link-checking tools: Lychee, Hyperlink (Zola), Docusaurus built-in, lycheeverse/lychee-action. _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
