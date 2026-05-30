# Apex Decision Trees

**Dated:** 2026-05-30 · **Status:** current; governor-limit numbers and selectivity thresholds tagged `[verify-at-build]`

Canonical decision trees for the Apex domain — async-channel selection, security enforcement, trigger-logic placement, SOQL selectivity, and bulk-safety. Each tree is meant to be **traversed top-to-bottom before selecting a method**, not pattern-matched on keywords. The first branch where the condition resolves cleanly is the leaf to apply. Format follows [`../../../docs/best-practices/decision-trees-in-knowledge-files.md`](../../../docs/best-practices/decision-trees-in-knowledge-files.md).

---

## Decision Tree: Async Apex — which channel (Future / Queueable / Batch / Scheduled / Platform Event)

**When this applies:** You have work that must leave the synchronous transaction — a callout from a trigger context, a roll-up over more rows than a synchronous query can hold, a job that must chain, or a recurring task. Observable triggers: `System.LimitException` from synchronous volume, "callout not allowed from trigger," a need to run on a schedule, or an `@future` that won't compile because you passed an sObject.

**Last verified:** 2026-05-30 against [`apex-async-patterns.md`](apex-async-patterns.md) and the Spring '26 limits cheat sheet `[verify-at-build]`.

```mermaid
flowchart TD
    START[Work must leave the sync transaction] --> Q1{Processing > ~50k rows / needs QueryLocator streaming?}
    Q1 -->|YES| BATCH[Batch Apex — Database.Batchable]
    Q1 -->|NO| Q2{Must run on a recurring schedule / cron?}
    Q2 -->|YES| SCHED[Schedulable — enqueues the real work]
    Q2 -->|NO| Q3{Need to chain jobs or pass sObject / complex state?}
    Q3 -->|YES| QUEUE[Queueable — implements Queueable]
    Q3 -->|NO| Q4{Decoupled pub/sub — notify other systems / async event consumers?}
    Q4 -->|YES| PE[Platform Event — publish + subscribe]
    Q4 -->|NO| Q5{Simple fire-and-forget callout, primitive params only?}
    Q5 -->|YES| FUTURE[Future — @future, callout=true]
    Q5 -->|NO| QUEUE
```

**Rationale per leaf:**
- *Batch Apex* — only channel that streams via `QueryLocator` and chunks (scope ≤ 2,000), so it survives row counts a single 50k-row SOQL can't hold; **requires:** nothing beyond standard Apex, but jobs compete for the org's concurrent-batch/flex-queue capacity.
- *Schedulable* — owns cron timing only; it should enqueue a Batch/Queueable rather than do heavy work itself.
- *Queueable* — the modern default for chaining and `sObject`/complex state; supersedes `@future` for nearly every new case.
- *Platform Event* — decouples producer from consumer (pub/sub) so neither blocks the other; the right tool when "other systems / async subscribers must hear about this," not when you just need more limits.
- *Future* — legacy fire-and-forget; primitive params only, no chaining, no return — reach for it only for a simple callout, and prefer Queueable even there.

**Tradeoffs summary table:**

| Channel | Best for | Chaining | State it carries | Watch-out `[verify-at-build]` |
|---|---|---|---|---|
| Batch | LDV / millions of rows | `finish()` can enqueue next | start/execute/finish state | concurrent-batch + flex-queue caps |
| Queueable | chaining, complex state | enqueue from within (depth-limited) | sObjects, full objects | chain depth limited from sync context |
| Future | simple fire-and-forget callout | none | primitive params only | no sObject params; superseded by Queueable |
| Schedulable | cron timing | kicks off Batch/Queueable | minimal | scheduled-job count limit |
| Platform Event | decoupled pub/sub | n/a (event-driven) | event payload fields | delivery semantics; publish-after-commit option |

---

## Decision Tree: Apex Security — where to enforce CRUD/FLS (with sharing / WITH SECURITY_ENFORCED / stripInaccessible / USER_MODE)

**When this applies:** You are writing Apex that reads or writes records on behalf of a user (a controller, a service called from LWC/Aura/VF, a user-invoked action). Observable triggers: a PMD/CRUD-FLS reviewer finding, an `@AuraEnabled` method exposing data, or a `without sharing` keyword with no justification. The *verdict* escalates to `ravenclaude-core/security-reviewer`; this tree picks the *mechanism*.

**Last verified:** 2026-05-30 against [`sharing-and-security-model.md`](sharing-and-security-model.md) and the `salesforce-reviewer` rubric items 6–7.

```mermaid
flowchart TD
    START[Apex touching records] --> Q1{Runs on behalf of a user, or a system/integration job?}
    Q1 -->|System job, documented| SYS[without sharing + comment — scope narrowly]
    Q1 -->|User context| SHARE[with sharing class — record-level access]
    SHARE --> Q2{Reading or writing?}
    Q2 -->|Reading via SOQL| Q3{Need a hard fail or graceful strip on inaccessible fields?}
    Q3 -->|Hard fail is correct| SE[WITH SECURITY_ENFORCED in the SOQL]
    Q3 -->|Strip & continue| SI_READ[Security.stripInaccessible AccessType.READABLE]
    Q2 -->|Writing via DML| SI_WRITE[Security.stripInaccessible AccessType.CREATABLE/UPDATABLE before DML]
    SHARE --> Q4{Whole method should run in user mode end-to-end?}
    Q4 -->|YES| UM[AccessLevel.USER_MODE on the DML/query]
```

**Rationale per leaf:**
- *with sharing* — the default; enforces **record-level** OWD/sharing for the running user. **requires:** nothing; it is the baseline posture.
- *WITH SECURITY_ENFORCED* — enforces **field- and object-level** read access *in the query*; **throws** if the user lacks access to any selected field — use when a missing field is an error, not a silent omission.
- *Security.stripInaccessible (READABLE)* — removes inaccessible fields from results **without throwing**, so partial reads degrade gracefully — use when you'd rather return what the user can see.
- *Security.stripInaccessible (CREATABLE/UPDATABLE)* — strips fields the user can't write **before** the DML, preventing an FLS bypass on insert/update.
- *AccessLevel.USER_MODE* — runs the query/DML in user mode (FLS + sharing) as one switch; the modern end-to-end enforcement when you want uniform user-mode behavior.
- *without sharing* — only for a **documented** system operation that must see all records; scoped narrowly, never the default.

**Tradeoffs summary table:**

| Mechanism | Enforces | On inaccessible field | Use when |
|---|---|---|---|
| `with sharing` | record-level (OWD/sharing) | n/a (records, not fields) | always, by default, in user context |
| `WITH SECURITY_ENFORCED` | field + object read | **throws** `QueryException` | a missing field must be a hard error |
| `stripInaccessible` (READABLE) | field read | silently strips | partial read should degrade gracefully |
| `stripInaccessible` (CREATABLE/UPDATABLE) | field write | strips before DML | prevent FLS bypass on insert/update |
| `AccessLevel.USER_MODE` | FLS + sharing, query+DML | throws on violation | uniform user-mode for the whole operation |

---

## Decision Tree: Trigger Logic — where does this belong (before/after, handler, async, Flow)?

**When this applies:** You have logic to attach to a DML event and must decide the trigger context and placement. Observable triggers: a new automation requirement on an object, a field that must be defaulted/validated, a roll-up, or a callout that needs to happen on save.

**Last verified:** 2026-05-30 against [`trigger-handler-framework.md`](trigger-handler-framework.md) and house opinions #2–#4, #11–#12.

```mermaid
flowchart TD
    START[Logic on a DML event] --> Q1{Same-record field set/validate, no related-record query?}
    Q1 -->|YES| FLOW[Before-save Flow or before-trigger handler — no extra DML]
    Q1 -->|NO| Q2{Needs the record Id / related records / cross-object update?}
    Q2 -->|YES| AFTER[after-context handler method]
    Q2 -->|NO, modify the saving record| BEFORE[before-context handler method]
    AFTER --> Q3{Operation needs a callout or exceeds sync limits?}
    BEFORE --> Q3
    Q3 -->|YES| ASYNC[Enqueue Queueable / @future from the handler]
    Q3 -->|NO| Q4{Handler issues DML on its own object?}
    Q4 -->|YES| GUARD[Add static recursion guard — mandatory]
    Q4 -->|NO| DONE[Logic-less trigger + bulk-safe handler — compliant]
    GUARD --> DONE
    ASYNC --> DONE
```

**Rationale per leaf:**
- *Before-save Flow / before-trigger* — same-record field changes need **no extra DML** (the platform saves `Trigger.new` as part of the original save); cheapest, and Flow is preferred for trivial cases (house opinion #11).
- *after-context handler* — the record Id and related records only exist **after** insert; cross-object work and roll-ups belong here.
- *before-context handler* — modify the saving record in place; no DML needed to persist the change.
- *Enqueue async* — callouts can't fire synchronously from a trigger, and over-limit work must move off the transaction.
- *Static recursion guard* — any handler that DMLs its own object will re-fire itself; the guard is **mandatory** (house opinion #4).
- *Logic-less trigger* — the trigger body never holds logic; one trigger per object dispatches to the handler.

**Tradeoffs summary table:**

| Placement | Extra DML? | Has record Id? | Use when |
|---|---|---|---|
| Before-save Flow | no | yes (on update) | trivial same-record field set, declarative ceiling not reached |
| before-trigger handler | no | no (on insert) | modify saving record, complex same-record logic |
| after-trigger handler | yes (cross-object) | yes | roll-ups, related-record updates, anything needing the Id |
| Async from handler | deferred | yes | callouts, over-limit volume |

---

## Decision Tree: SOQL Selectivity — will this query stay index-backed at volume?

**When this applies:** You are authoring or fixing a SOQL query that will run against an object expected to grow large (orders, cases, line items, logs). Observable triggers: `System.QueryException: Non-selective query against large object type`, a slow query in production, or a Query Plan showing cost ≥ 1.0.

**Last verified:** 2026-05-30 against [`large-data-volume-design.md`](large-data-volume-design.md); selectivity thresholds are platform values `[verify-at-build]`.

```mermaid
flowchart TD
    START[Query on a high-volume object] --> Q1{Filters on an indexed field? Id/Name/audit/lookup/extId/unique/custom-index}
    Q1 -->|NO| ADDIDX[Add a custom index or refilter on an indexed field]
    Q1 -->|YES| Q2{"Filter uses leading % wildcard or negative operator (!=, NOT, NOT IN)?"}
    Q2 -->|YES| REWRITE[Rewrite as a positive, bounded predicate]
    Q2 -->|NO| Q3{Predicate selective enough to clear the optimizer threshold?}
    Q3 -->|NO| BOUND[Add a bounded date/status window to narrow the set]
    Q3 -->|YES| Q4{Result set still very large?}
    Q4 -->|YES| BATCH[Stream with Batch Apex QueryLocator, not one SOQL]
    Q4 -->|NO| Q5{Frequent reporting query on the same fields?}
    Q5 -->|YES| SKINNY[Consider a skinny table — request via Support]
    Q5 -->|NO| GOOD[Selective, index-backed — good]
    ADDIDX --> GOOD
    REWRITE --> GOOD
    BOUND --> GOOD
    BATCH --> GOOD
    SKINNY --> GOOD
```

**Rationale per leaf:**
- *Add/standardize an index* — the optimizer can only choose an index that exists; a non-indexed filter forces a full scan that fails at volume. **requires:** custom index requested via Support, or the field flagged external-ID/unique.
- *Rewrite positive & bounded* — leading `%` wildcards and negative operators are non-selective by construction; a positive set + date window restores index use.
- *Add a bounded window* — even an indexed field is non-selective if the predicate matches too large a fraction of rows; bound it.
- *Batch QueryLocator* — streams large sets in chunks instead of holding 50k rows in one query's heap.
- *Skinny table* — a Salesforce-managed copy avoids base-table joins for hot reporting queries.

**Tradeoffs summary table:**

| Lever | Cost | Effect | Use when |
|---|---|---|---|
| Indexed/selective filter | design effort | optimizer picks the index | always — the primary lever |
| Custom index | Support request / config | makes a new field selectable | a needed filter field isn't indexed |
| Bounded date/status window | narrows results | clears the selectivity threshold | indexed but matches too many rows |
| Batch QueryLocator | async complexity | streams instead of loading | result set exceeds a single SOQL |
| Skinny table | Support request, sync overhead | removes joins | frequent reporting on fixed fields |

---

## Decision Tree: Bulk Safety — is this Apex safe for a 200-record load?

**When this applies:** You are reviewing or writing any Apex that runs in a trigger, a Batch `execute`, or any path a data load can reach. Observable triggers: `Too many SOQL queries: 101`, `Too many DML statements: 151`, `Apex CPU time limit exceeded`, or a test that only inserts one record.

**Last verified:** 2026-05-30 against [`governor-limits-and-bulkification.md`](governor-limits-and-bulkification.md); limit numbers `[verify-at-build]`.

```mermaid
flowchart TD
    START[Apex touching records] --> Q1{SOQL or DML inside a for/while loop — directly or via a called method?}
    Q1 -->|YES| HOIST[NOT bulk-safe — hoist the query/DML out of the loop]
    Q1 -->|NO| Q2{Correlating two collections with a nested loop?}
    Q2 -->|YES| MAP["Replace with a Map keyed on the join field — O(1) lookup"]
    Q2 -->|NO| Q3{Queries collect IDs into a Set/Map first, query once?}
    Q3 -->|NO| HOIST
    Q3 -->|YES| Q4{DML issued once on a collection, not per record?}
    Q4 -->|NO| HOIST
    Q4 -->|YES| Q5{Proven by a 200-record test asserting outcomes?}
    Q5 -->|NO| TEST[Add a 200-record bulk test before shipping]
    Q5 -->|YES| SAFE[Bulk-safe — verify against current limits]
    HOIST --> MAP
    MAP --> Q3
    TEST --> SAFE
```

**Rationale per leaf:**
- *Hoist out of the loop* — a SOQL/DML in a loop multiplies one operation by batch size and trips the 100-SOQL / 150-DML ceiling; this is the dominant Salesforce failure mode.
- *Replace with a Map* — a nested correlation loop is O(n×m) and trips CPU time at scale; a map keyed on the join field is O(1) per lookup.
- *Collect IDs / query once* — one query bound with `WHERE Id IN :ids` replaces N per-record queries.
- *One DML on a collection* — accumulate into a `List` and `insert`/`update` once.
- *200-record test* — coverage isn't a test; a 200-record assertion is what proves the path survives a load.

**Tradeoffs summary table:**

| Symptom | Limit hit `[verify-at-build]` | Root cause | Fix |
|---|---|---|---|
| Too many SOQL queries: 101 | 100 sync / 200 async | query in a loop | hoist + bind `IN :ids` |
| Too many DML statements: 151 | 150 | DML per record | accumulate list, one DML |
| Apex CPU time exceeded | 10,000 ms sync / 60,000 async | nested correlation loop | `Map` keyed lookup |
| Passes test, fails in prod | n/a | single-record test only | 200-record bulk test |

---

## Sources

- [`apex-async-patterns.md`](apex-async-patterns.md) — async channel comparison and limits
- [`governor-limits-and-bulkification.md`](governor-limits-and-bulkification.md) — limits table, bulk pattern
- [`trigger-handler-framework.md`](trigger-handler-framework.md) — one-trigger / handler / recursion
- [`large-data-volume-design.md`](large-data-volume-design.md) — selectivity, indexes, skinny tables
- [`sharing-and-security-model.md`](sharing-and-security-model.md) — OWD / sharing / FLS layering
- Format reference: [`../../../docs/best-practices/decision-trees-in-knowledge-files.md`](../../../docs/best-practices/decision-trees-in-knowledge-files.md)
