# Name your Direct Lake mode — on-OneLake or on-SQL

**Status:** Absolute rule — "Direct Lake" without the mode is an unfinished sentence, and the omission changes the fallback behavior you design for.

**Domain:** Direct Lake / semantic models

**Applies to:** `microsoft-fabric`

---

## Why this exists

There are **two** Direct Lake variants and they behave oppositely on fallback. Saying "Direct Lake" without "on OneLake" or "on SQL" leaves the single most consequential design fact undecided: whether the model **falls back to DirectQuery** under pressure or **errors** instead. This is the plugin's documented #1 mistake. Get it wrong and you either design gold tables to "stay under guardrails" for an engine that never falls back, or you assume a graceful DirectQuery fallback that on-OneLake simply does not provide — and your report errors (or returns empty) in front of the client.

## How to apply

State the mode before you design anything, then design **to that mode's failure shape**.

| | Direct Lake on OneLake (modern default) | Direct Lake on SQL (older path) |
|---|---|---|
| Reads via | OneLake APIs | the SQL analytics endpoint |
| DirectQuery fallback | **No** — unframed/unprocessed table → **errors** | **Yes** — exceeds SKU guardrails or hits an unsupported feature → falls back |
| Security misconfig | OneLake RLS/CLS → **empty results**, not an error | SQL-endpoint OLS/RLS **forces** the fallback |
| Composite models | Supported (mix Direct Lake + Import/DQ) | — |
| Gateway | Not supported | — |

```text
On OneLake → every gold table must be FRAMED and OneLake-security roles correct
             (an unprocessed table errors; a bad role yields EMPTY, not an error).
On SQL     → keep gold UNDER the SKU guardrails and avoid features that force DirectQuery;
             SQL-endpoint OLS/RLS forces fallback (or fails if fallback is disabled).
```

**Do:**
- Write the mode explicitly in every model spec, design note, and diagnosis.
- On-OneLake: design so every gold table is framed; treat *empty* results as a likely OneLake-security misconfig, not a data bug.
- On-SQL: design gold to stay under guardrails; expect SQL OLS/RLS to force the DirectQuery path.

**Don't:**
- Assume on-OneLake "falls back to DirectQuery" — it doesn't; it errors.
- Diagnose a fallback without first naming the mode — the root cause taxonomy is mode-specific.

## Edge cases / when the rule does NOT apply

- **Import or DirectQuery** storage mode is a different decision entirely — the mode-naming rule is only about which Direct Lake variant you chose once Direct Lake is the answer.
- **A pure prototype** on a single small table may never approach a guardrail — but you still name the mode, because the fallback behavior is what you'll hand to the next engineer.

## See also

- [`../knowledge/direct-lake-and-semantic-models.md`](../knowledge/direct-lake-and-semantic-models.md) — the two modes, framing, fallback, and the gold-shaping requirements
- [`shape-gold-for-direct-lake.md`](./shape-gold-for-direct-lake.md) — the gold-table optimization that keeps on-OneLake framed and on-SQL under guardrails
- [`../agents/fabric-semantic-model-engineer.md`](../agents/fabric-semantic-model-engineer.md) — owns the Direct Lake model + mode choice + fallback diagnosis

## Provenance

Codifies house opinion #8 ("Know your Direct Lake mode") from [`../CLAUDE.md`](../CLAUDE.md) §3 and the "two Direct Lake modes — get this right (it's the #1 mistake)" section of [`../knowledge/direct-lake-and-semantic-models.md`](../knowledge/direct-lake-and-semantic-models.md) (Microsoft Learn, retrieved 2026-05-28). The anti-pattern hook flags "Direct Lake" written with no mode nearby.

---

_Last reviewed: 2026-05-30 by `claude`_
