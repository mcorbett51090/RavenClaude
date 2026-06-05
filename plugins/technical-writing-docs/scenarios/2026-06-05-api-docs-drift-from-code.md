---
scenario_id: 2026-06-05-api-docs-drift-from-code
contributed_at: 2026-06-05
plugin: technical-writing-docs
product: openapi
product_version: "unknown"
scope: likely-general
tags: [api-docs, drift, openapi, spec-driven, ci-gate, examples]
confidence: high
reviewed: false
---

## Problem

A REST API's reference docs were hand-maintained in Markdown tables alongside a separate, hand-edited OpenAPI file — and both had drifted from the running service. Three params had been renamed in code, one endpoint had gained a required `Idempotency-Key` header, and two error codes (`409`, `422`) the service now returned were undocumented. Support tickets traced back to developers copy-pasting request bodies straight from the docs that the API rejected. The docs *looked* authoritative, which made the drift worse than a gap: readers trusted a wrong answer.

## Constraints context

- The "source of truth" was ambiguous: code annotations, a hand-edited `openapi.yaml`, and the Markdown reference tables could each claim it, and all three disagreed.
- No CI gate tied any of the three together, so drift was invisible until a reader hit it.
- The team's instinct was to "do a docs audit" — a one-time manual reconciliation that would drift again the next sprint. The `stale-docs-are-worse-than-none` and `spec-driven-reference-not-hand-maintained` best-practices say the opposite: stop hand-maintaining the copy.

## Attempts

- Tried: a manual reconciliation pass (read the code, fix the Markdown tables). Closed the current gap but fixed nothing structural — three weeks later a new param drifted. A point-fix on a process problem.
- Tried: generating the OpenAPI spec **from** the code (framework-native: FastAPI/`drf-spectacular`/`springdoc`-style annotations → spec), making the spec a build artifact, not a hand-edited file. This removed one of the three competing sources.
- Tried (the move that worked): made the **spec the single source** and rendered reference **from** it (Redocly/`redoc`-style), then added a CI gate that (a) regenerates the spec from code and fails on an uncommitted diff, and (b) runs the documented request examples against a contract/mock so a renamed field fails the build. Traversed `knowledge/technical-writing-docs-decision-trees.md` "How do I keep examples from going stale?" → the "generated from a spec → regenerate on spec change" leaf.

## Resolution

The fix was **structural, not editorial**: collapse three competing sources to one (the spec, generated from code), render reference from it, and gate both the spec-freshness and the examples in CI. Drift now fails the build instead of reaching a reader. The auth section was pulled to the front and linked from every reference page (`api-auth-docs-before-feature-docs`), since the most common first-call failure was an undocumented header.

**Action for the next writer hitting this pattern:** do not start with a docs audit. Find the *number* of sources of truth first — if it is more than one, the audit will drift again. Collapse to one spec-driven source, render reference from it, and add the two CI gates (spec-freshness + examples-run) before fixing any individual page. The canonical guidance is [`../knowledge/technical-writing-docs-decision-trees.md`](../knowledge/technical-writing-docs-decision-trees.md) and the [`spec-driven-reference-not-hand-maintained`](../best-practices/spec-driven-reference-not-hand-maintained.md) + [`examples-must-run`](../best-practices/examples-must-run.md) best-practices. Route anything touching auth/secrets in the examples to `ravenclaude-core/security-reviewer`.

**Sources (retrieved 2026-06-05):**
- Diátaxis — reference vs. how-to distinction: https://diataxis.fr/reference/
- OpenAPI Specification (the spec-as-source-of-truth contract): https://spec.openapis.org/

These are stable framework/standards sources; the specific codegen tool names (FastAPI / drf-spectacular / springdoc / Redocly) are version- and stack-dependent — `[verify-at-use]` against the consumer's actual stack and tool versions before any deliverable.
