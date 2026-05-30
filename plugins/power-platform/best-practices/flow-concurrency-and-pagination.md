# Set Apply-to-each concurrency deliberately, turn on pagination, and prefer batch over per-row loops

**Status:** Pattern — strong default. A loop running at the silent default of 20, with pagination off, over a source that returns more than its default page, is three latent bugs in one action.

**Domain:** Power Automate

**Applies to:** `power-platform`

---

## Why this exists

Three defaults bite at scale and all three are invisible in the designer until the run is slow or wrong:

1. **`Apply to each` concurrency defaults to OFF (sequential).** When you do turn it on, it defaults to a **degree of parallelism of 20** — rarely the right number, and never the one you should accept without a reason. A sequential loop over 2,000 rows is 2,000 serial round-trips.
2. **Pagination defaults to OFF.** A *List rows* / *Get items* action returns only its **default page** (commonly the connector's page size) unless you enable pagination and raise the threshold. Your loop then silently processes the first page and ignores the rest — a *correctness* bug that looks like missing data, not an error.
3. **A loop is the wrong tool for bulk writes.** Per-row `Apply to each` over a Dataverse table is N round-trips; the Dataverse connector's batch / `$batch` Web API does it in one.

(Concurrency-default-20 and the sequential-by-default behavior verified this session against Microsoft Learn Logic Apps *for-each* concurrency reference — Power Automate shares the runtime; pagination thresholds are connector-specific, treat exact numbers as `[verify per connector]`.)

## How to apply

**Concurrency** — set it explicitly in the loop's **Settings → Concurrency Control**: toggle ON, set the **Degree of Parallelism**. Typical: 50 (the practical ceiling) for independent, idempotent iterations; **1 (or OFF)** when iterations must run in order or share mutable state.

```
# Apply to each — Settings:
Concurrency Control: On
Degree of Parallelism: 50   # independent rows; document why
```

**Pagination** — on the *List rows* / *Get items* action's **Settings → Pagination**: toggle ON and set the **Threshold** to the maximum rows you actually need.

```
# List rows — Settings:
Pagination: On
Threshold: 5000
```

**Prefer batch over per-row loops** — for bulk Dataverse writes, call the Web API `$batch` endpoint (via the *Perform an unbound action* / HTTP-with-Dataverse path) instead of looping:

```http
POST /api/data/v9.2/$batch
# one round-trip carrying N changesets, instead of N Apply-to-each iterations
```

**Do:**
- Set concurrency to **1** whenever the loop body writes to a shared variable — parallel iterations race on `Set variable` and you get nondeterministic results.
- Turn pagination ON the moment a list source *could* exceed its default page, even if today's data fits — the bug appears later, in prod, as "some records were skipped."
- Cap the parallelism you actually need; 50 against a throttled backend just front-loads 429s. Pair high parallelism with a real retry policy (see `flow-error-handling-and-retry-policy.md`).

**Don't:**
- Leave `Apply to each` at the default 20 "because it worked" — state the number and the reason.
- Parallelize a loop whose iterations depend on each other's output or order.
- Loop-and-`Patch` thousands of Dataverse rows when one `$batch` call does it — that's the canonical "Apply to each over thousands of items" anti-pattern.

## Edge cases / when the rule does NOT apply

- **Order-dependent processing** (each row's result feeds the next) — keep concurrency at 1; parallelism is a correctness bug here, not a speedup.
- **Variables inside the loop** — `Set variable` / `Increment variable` are not concurrency-safe; either run sequential or refactor to `Compose` per-iteration outputs and aggregate after.
- **A genuinely small, fixed list** (≤ a handful of items) — pagination and high parallelism add nothing; leave them off.
- **Connector-specific page sizes vary** — the pagination *threshold* you set is an upper bound; the connector still pages internally at its own size.

## See also

- [`./flow-error-handling-and-retry-policy.md`](./flow-error-handling-and-retry-policy.md) — pair high parallelism with retry/throttle handling
- [`./flow-child-flows-and-reuse.md`](./flow-child-flows-and-reuse.md) — why calling a child flow per-row in a big loop multiplies run count
- [`../skills/power-automate/SKILL.md`](../skills/power-automate/SKILL.md) — §4 Performance & Scale (parallelism, batching, throttling)
- [`../knowledge/flow-decision-trees.md`](../knowledge/flow-decision-trees.md) — `## Decision Tree: Reuse — child flow vs inline vs other surface`
- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) — "Increase Apply to each parallelism explicitly — default 20 is rarely the right answer."

## Provenance

Codifies the `flow-engineer` agent's parallelism opinion ("default 20 is rarely right; set it, typically 50, document why") and named anti-pattern ("Apply to each over thousands of items running sequentially"), plus the `power-automate` skill §4. Concurrency-default and sequential-by-default verified this session against Logic Apps for-each reference; pagination thresholds and Dataverse `$batch` mechanics are connector-version-specific — `[verify per connector before quoting exact numbers]`.

---

_Last reviewed: 2026-05-30 by `claude`_
