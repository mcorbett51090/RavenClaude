# Memory Engineering scenarios bank

Dated, scope-tagged, **unverified** engagement narratives for the `memory-engineering` plugin (the marketplace scenarios pattern; see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md)).

## The unverified-scenario contract

A scenario is a **secondary** source. It carries a pattern, never an authority.

1. **Surface a scenario only behind the mandatory unverified-scenario preamble** — state that it is an unverified narrative from this bank, dated, and that it has not been reviewed.
2. **It never overrides the cited [knowledge bank](../knowledge/memory-engineering-paradigms.md) or a qualified authority** (§2). Where a scenario and a dated knowledge file disagree, the knowledge file wins and the scenario is wrong.
3. **No user data, no stored memory content, no PII** — in these files or in anything derived from them (§4). Every narrative here is deliberately de-identified to the pattern.
4. **Volatile facts are not carried in a scenario.** Caps, header strings, retention windows and cache multipliers are `[verify-at-use]` against [`../knowledge/memory-surfaces-2026.md`](../knowledge/memory-surfaces-2026.md), which is dated and swept.
5. **Every figure is `[unverified — training knowledge]`** unless it is re-derived on the client's own data (§3 #8) — which is the entire point of house opinion #8.

## Index

| Scenario | Scope | Pattern |
|---|---|---|
| [`2026-08-06-poisoned-memory-survived-the-fix.md`](./2026-08-06-poisoned-memory-survived-the-fix.md) | likely-general | The prompt was patched and the behaviour returned — persistence, not injection, is the defining property (§3 #5) |
| [`2026-08-06-memory-never-amortized.md`](./2026-08-06-memory-never-amortized.md) | likely-general | An LLM-mediated build never broke even; the lexical baseline won on both axes (§3 #1, #2) |
| [`2026-08-06-deleted-the-row-not-the-person.md`](./2026-08-06-deleted-the-row-not-the-person.md) | likely-general | An erasure request missed the embedding, the immutable version history and a derived summary (§3 #7) |

## See also

- [`../best-practices/README.md`](../best-practices/README.md) — the eight rules these three engagements each learned the expensive way.
- [`../knowledge/memory-engineering-decision-trees.md`](../knowledge/memory-engineering-decision-trees.md) — the trees these scenarios traverse.
- [`../CLAUDE.md`](../CLAUDE.md) — the team constitution (§2 boundaries, §3 house opinions, §4 anti-patterns).
