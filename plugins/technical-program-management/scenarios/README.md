# technical-program-management scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) program-
> delivery situations. Consulted by the agents as a **secondary** source — always
> behind the mandatory unverified-scenario preamble (see
> [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md)).

This directory holds **scenarios** — program war stories of "the program faced
situation X, here were the constraints, we tried A/B/C, and D was the move that
worked." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — never overriding the cited
  knowledge bank or best-practices, and never surfaced without the preamble

These are **delivery narratives**, not code fixes: a program that stayed "green"
until a hidden dependency slipped it a month, a launch that skipped go/no-go
criteria, a status nobody acted on because it led with activity. The "Resolution"
is a TPM move plus the outcome it produced. Scenarios carry **no client PII or real
company names**.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: technical-program-management
product: <charter | dependencies | status | launch>
product_version: "n/a" # non-code vertical — no product version
scope: engagement-specific | domain-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---
```

Below the frontmatter: **Situation → Constraints → What we tried → Resolution →
Lesson**, in prose.
