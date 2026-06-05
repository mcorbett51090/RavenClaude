# Annotate Volatile Content With a Last-Verified Date

**Status:** Pattern
**Domain:** Technical Writing — Content maintenance
**Applies to:** `technical-writing-docs`

---

## Why this exists

Some documentation content is stable for years (a conceptual explanation of how OAuth works); other content can be wrong within weeks (pricing, rate limits, SDK compatibility matrices, third-party integration steps). Treating all content with the same review cadence means stable content gets reviewed unnecessarily and volatile content quietly goes stale. Annotating volatile content with a last-verified date and a staleness trigger creates an explicit signal: a reader seeing a two-year-old pricing table knows to verify before citing it; a content audit can mechanically find the oldest last-verified dates and prioritize them.

## How to apply

**How to identify volatile content:**

| Volatile (annotate) | Stable (normal review cycle) |
|---|---|
| Third-party pricing or limits | First-principles concepts and explanations |
| SDK / library version compatibility matrices | Architectural diagrams (unless the architecture changes) |
| OAuth provider specifics (token lifetime, scopes) | Step-by-step procedures for your own system |
| Cloud service quotas and region availability | Glossary definitions |
| CLI output (may change with tool versions) | Core API contract (when spec-driven) |

**Annotation format:**

```markdown
<!-- Last verified: 2026-06-05. Re-verify before quoting: rate limits subject to change. -->
| Tier    | Requests/min |
|---------|-------------|
| Free    | 60          |
| Pro     | 600         |
```

Or as a visible callout:

```markdown
> **Note:** Rate limits as of 2026-06-05. Check the [pricing page](https://example.com/pricing)
> for current values before building against these limits.
```

**Staleness tracking in CI:**

```python
# scripts/check-stale-content.py — find annotations older than N days
import re, datetime, subprocess, sys

threshold_days = 180
pattern = re.compile(r'Last verified: (\d{4}-\d{2}-\d{2})')
# ... scan docs/, flag annotations older than threshold_days
```

**Do:**
- Add the staleness-check script to the CI suite (warn-only, not blocking) so the content team gets a report.
- Include a "staleness trigger" comment: what event (a vendor release, a pricing announcement) should prompt re-verification.
- Re-verify the annotation date on every review that touches the volatile section, not just when the number changes.

**Don't:**
- Use a last-verified date as a substitute for actually keeping the content current — it is a signal, not an excuse.
- Annotate stable first-principles content — over-annotation trains readers to ignore the signal.
- Leave a section annotated as verified in 2022 on a docs site maintained in 2026 — that is a broken signal.

## Edge cases / when the rule does NOT apply

- **Generated reference docs**: if the reference is spec-driven and regenerated on every build, the generation timestamp is the implicit "last verified" date; no manual annotation needed.
- **Docs sites that explicitly version by product release**: the version number and release date are the staleness anchor — no per-section annotation needed if the version is clearly surfaced.

## See also

- [`../agents/docs-architect.md`](../agents/docs-architect.md) — sets the overall content review policy
- [`./stale-docs-are-worse-than-none.md`](./stale-docs-are-worse-than-none.md) — the parent rule this annotation practice operationalizes

## Provenance

Codifies house opinion #5 ("Stale docs are worse than no docs — date volatile content") from `CLAUDE.md` §2. Annotation pattern informed by the ravenclaude-core claim-grounding discipline and Diátaxis freshness guidance. _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
