---
name: scenario-retrieval
description: Consult the unverified scenarios bank (`plugins/<plugin>/scenarios/*.md`) before answering plugin-domain questions. Glob + tag-filter + recency-weight, surface top 2-3 with mandatory unverified-scenario preamble ("Based on N unverified scenarios from YYYY-MM tagged [scope] — verify in your environment"). Secondary source — never replaces canonical knowledge files.
---

# Skill: scenario-retrieval

> **Invoked by:** any agent that may benefit from a war-story narrative before answering. Currently wired into `ravenclaude-core/architect`, `ravenclaude-core/security-reviewer`, and the `power-platform/*` agents via inline priors.
>
> **When to invoke:** before answering any question where domain-specific scenarios *might* exist (e.g., "I'm hitting a 403 on Dataverse table creation as SPN", "Canvas LMS connector is missing in Airbyte", "Power BI Embedded RLS isn't filtering"). Scenarios are unverified field notes; treat them as a **secondary** source, not a substitute for canonical knowledge files or best-practices.
>
> **Output:** matching scenarios surfaced to the user with the **mandatory unverified-scenario preamble** baked into the response.

## The dual-bank model

The RavenClaude marketplace has two banks of operational guidance:

| Bank | Where | What | Trust |
|---|---|---|---|
| **Canonical / knowledge** | `plugins/<plugin>/knowledge/<topic>.md` + `docs/best-practices/<rule>.md` | Curated, maintainer-reviewed reference material. Long-form. | High — agents should follow without disclaimer |
| **Scenarios** | `plugins/<plugin>/scenarios/<YYYY-MM-DD>-<slug>.md` | Dated war-story narratives from real engagements. Schema-validated but not reviewed. | Low to medium — agents surface with mandatory preamble |

This skill governs how agents consult the **second** bank.

## The retrieval pattern (glob-and-filter)

When invoked, the agent should:

1. **Glob** the scenarios directory for the relevant plugin:
   ```
   plugins/<plugin>/scenarios/*.md
   ```
2. **Read** the YAML frontmatter of each match (cheap — 9 fields).
3. **Filter** by `tags`, `product`, `product_version`, and `scope` to find scenarios that match the current engagement's context.
4. **Rank** by recency (newer first) and `confidence` (high before medium before low). De-prioritize `scope: tenant-specific` scenarios unless the current engagement matches that specific tenant context.
5. **Surface** at most the top 2-3 matches to the user — more is noise.

For v0.1.0, the pattern is **plain file-system glob + frontmatter parsing**. No vector index. No semantic similarity. Tag-based filtering is the load-bearing mechanism.

## The mandatory unverified-scenario preamble

When an agent **cites a scenario** in its response to the user, it MUST prefix the citation with a one-line preamble. This is non-negotiable.

**Preamble template:**

> *"Based on [N] unverified scenario[s] from [YYYY-MM] tagged [scope] — verify in your environment before applying."*

**Examples:**

> *"Based on 1 unverified scenario from 2026-05 tagged tenant-specific — verify in your environment before applying."*

> *"Based on 2 unverified scenarios (2026-04, 2026-05) tagged likely-general — verify in your environment before applying."*

**Why it's mandatory:**

Scenarios are not reviewed. A single contributor's mis-diagnosis can become a marketplace-wide assumption if agents silently treat scenarios as canonical. The preamble:

1. **Signals to the user** that the advice is from a single-source field note, not a verified pattern.
2. **Forces the agent's own attention** on the scope flag — the agent can't skip past `scope: tenant-specific` if it has to type those words.
3. **Creates an audit trail** in the transcript — a maintainer reviewing the conversation later can immediately see which advice came from canonical vs scenarios.

## When NOT to surface scenarios

- The user's question has a clear canonical answer in `plugins/<plugin>/knowledge/` or `docs/best-practices/`. Use the canonical source; mention the scenario only as supplementary if the scope matches.
- The matching scenarios have `scope: tenant-specific` and the current engagement clearly doesn't share that tenant context (different vertical, different product version, different permissions configuration). De-prioritize or skip.
- `confidence: low` AND zero corroborating scenarios. A single low-confidence note from 6 months ago should not drive a recommendation.
- The user is in a regulated context (FERPA / HIPAA / PCI / GDPR) and the scenario hasn't been scrubbed for that compliance regime. Surface only with explicit "this scenario predates [regulation] compliance review."

## Anti-patterns this skill flags

- Citing a scenario **without** the unverified-preamble — the worst failure mode; gives the user canonical-sounding advice from a single field note.
- Citing a `scope: tenant-specific` scenario as if it were `likely-general`.
- Surfacing more than 2-3 matches — noise; the user won't read.
- Treating absence of a scenario as evidence of absence — the bank is sparse by design; an agent that says "there's no scenario for this so it must be a non-issue" is wrong.
- Auto-promoting an unverified scenario into the user's answer text without attribution.
- Modifying the scenario file on the fly (e.g., to "fix" a typo) — scenarios are append-only narratives; edits should go through `/wrap` again or manual marketplace edit.

## How an agent uses this skill (worked example)

User asks: *"Why is my service principal getting 403 on Dataverse table creation even though I gave it System Customizer?"*

Agent (Power Platform specialist) consults this skill, runs:

```
ls plugins/power-platform/scenarios/*.md
```

Finds `2026-05-21-spn-flow-create-403.md` with tags `[spn, dataverse, application-user, 403, permissions]`. Matches the user's question on `spn`, `dataverse`, `403`, `permissions`.

Reads frontmatter: `scope: likely-general`, `confidence: medium`, `reviewed: false`.

Surfaces the scenario:

> *Based on 1 unverified scenario from 2026-05 tagged likely-general — verify in your environment before applying.*
>
> A previous engagement saw the same 403 pattern. The fix that worked: the SPN needs to be added as an **Application User** in the *target environment*, in addition to having the security role. The security role alone is insufficient. Check `Power Platform Admin Center → <environment> → Application users → New app user → select your SPN`.
>
> If that doesn't resolve it, the canonical reference is `plugins/power-platform/knowledge/programmatic-flow-creation.md` which covers the full auth-surface debugging path.

Note how the response:
- Leads with the preamble.
- States the scope/confidence in plain language.
- Provides the resolution **and** points to the canonical knowledge file as the more authoritative source.

## Inline-prior pattern for agents

Agents that should consult this skill carry a one-paragraph inline prior in their file:

> **Scenario retrieval (priors).** Before answering a [plugin-domain]-shaped question, glob `plugins/[plugin]/scenarios/*.md` and read the frontmatter of any file whose `tags` or `product` match the user's context. Surface up to 2-3 matches with the **mandatory unverified-scenario preamble** ("Based on N unverified scenarios from YYYY-MM tagged [scope] — verify in your environment"). Treat scenarios as **secondary** to canonical knowledge files; never replace a `plugins/[plugin]/knowledge/` answer with a scenario, and never elide the preamble. Full pattern: [`../skills/scenario-retrieval.md`](../skills/scenario-retrieval.md).

## v0.1.0 scope notes

- **Plugin coverage:** scenarios bank is enabled in `power-platform` only as of v0.1.0. Other plugins have `TODO` markers in their CLAUDE.md to enable the bank when they accumulate scenarios.
- **Retrieval mechanism:** glob + frontmatter parsing. No vector index, no embedding pipeline.
- **Auto-promotion:** disabled in v0.1.0. When ≥2 independent scenarios corroborate the same finding (different `contributed_at` quarters), an agent will eventually propose promotion to `docs/best-practices/`. v0.2.0 work.
- **Conflict detection:** disabled in v0.1.0. If two scenarios disagree, a future `conflicts_with:` field handles it. v0.2.0 work.
- **Recency decay:** not automated. The `contributed_at` field is consulted at retrieval time, but no CI sweep deprecates stale scenarios yet.

## Refresh triggers

- Claude Code adds a native vector-index primitive that's worth migrating to
- ≥10 scenarios across the marketplace and the glob pattern starts breaking
- A real-engagement scenario surfaces an edge case the schema doesn't capture
- The mandatory-preamble pattern produces noise complaints (tune the trigger conditions for surfacing)
- The first auto-promotion fires and we need conflict handling
