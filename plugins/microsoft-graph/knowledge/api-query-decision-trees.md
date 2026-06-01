# Microsoft Graph — API & query decision trees

**Last reviewed:** 2026-05-30 · **Confidence:** medium-high (first-party Microsoft Learn). Volatile facts (throttling limits, beta-vs-v1.0 availability, header names) carry inline markers + per-tree `Last verified` dates; re-verify on the Researcher sweep before quoting.

> Canonical decision trees for the `graph-api-engineer` surface. Traverse the relevant tree top-to-bottom against the user's observable situation **before** choosing a method (per the pre-action-traversal prior in [`../CLAUDE.md`](../CLAUDE.md) §5). Default to the smaller-blast-radius leaf; escalate only when it demonstrably fails.
>
> Volatile facts (throttling limits, beta-vs-v1.0 endpoint availability, header names) are marked inline and re-verified before quoting. See [`api-honor-throttling-and-retry-after.md`](../best-practices/api-honor-throttling-and-retry-after.md), [`api-page-to-exhaustion.md`](../best-practices/api-page-to-exhaustion.md), [`api-delta-for-what-changed.md`](../best-practices/api-delta-for-what-changed.md).

---

## Decision Tree: Graph API — "what changed?" (poll vs delta vs change-notification)

**When this applies:** You need to react to changes in a Graph resource (new mail, updated user, new Teams message) and are deciding how to detect them — not a one-time read.

**Last verified:** 2026-05-30 against Microsoft Graph v1.0 change-tracking docs (delta query + subscriptions). `[verify-at-build]` — supported resources for delta and for rich notifications change over time.

```mermaid
flowchart TD
    START[Need to detect changes in a resource] --> Q1{Need near-real-time push, within seconds?}
    Q1 -->|YES| Q2{Resource supports change notifications?}
    Q1 -->|NO, periodic sync is fine| Q3{Resource supports delta query?}
    Q2 -->|YES| SUB[Change-notification subscription]
    Q2 -->|NO| Q3
    Q3 -->|YES| DELTA[Delta query with stored deltaLink]
    Q3 -->|NO| POLL[Polling with $filter on lastModifiedDateTime + stored watermark]
```

**Rationale per leaf:**
- _Change-notification subscription_ — push within seconds; lowest latency and lowest call volume, but stateful (validation + renewal + lifecycle handling required). See the notifications tree + `notify-subscriptions-need-renewal-and-lifecycle-handling.md`.
- _Delta query_ — periodic "what changed since last sync" without re-pulling the whole collection; persist the `deltaLink` and resume from it.
- _Polling with watermark_ — only when neither is supported; filter server-side on a change timestamp and store the high-water mark. Most expensive; last resort.

**Tradeoffs summary:**

| Method | Latency | Call volume | State to manage | Use when |
|---|---|---|---|---|
| Subscription | seconds | lowest | subscription id + renewal + (cert for rich) | near-real-time, resource supports it |
| Delta query | minutes (your cadence) | low | `deltaLink` per resource | periodic sync, resource supports delta |
| Poll + watermark | your cadence | high | timestamp watermark | neither delta nor notifications available |

---

## Decision Tree: Graph API — request efficiency (single vs page-loop vs $batch)

**When this applies:** You are issuing one or more Graph reads/writes and deciding how to structure the calls to minimize round-trips and avoid throttling.

**Last verified:** 2026-05-30 against Graph `$batch` (max 20 requests/batch `[verify-at-build]`) and paging docs.

```mermaid
flowchart TD
    START[About to call Graph] --> Q1{One resource, one operation?}
    Q1 -->|YES| Q2{Returns a collection?}
    Q1 -->|NO, several independent ops| BATCH[Combine with $batch, max ~20 per batch]
    Q2 -->|NO, single item| ONE[Single GET with $select]
    Q2 -->|YES| PAGE[GET with $select/$filter then follow @odata.nextLink to exhaustion]
```

**Rationale per leaf:**
- _Single GET with `$select`_ — never fetch a full entity when you need three fields.
- _Page to exhaustion_ — a collection response is one page; follow `@odata.nextLink` until absent. A first-page result is not "all results."
- _`$batch`_ — fold up to ~20 independent requests into one round-trip; respect per-request dependencies via `dependsOn`. Cuts latency and throttling pressure.

**Tradeoffs summary:**

| Method | Round-trips | Best for | Watch out |
|---|---|---|---|
| Single GET + `$select` | 1 | one item, few fields | over-fetch if `$select` omitted |
| Page loop | N pages | full collections | client-side filtering instead of `$filter` |
| `$batch` | 1 | many independent ops | 20-request cap; inner 429s still possible |

---

## Decision Tree: Graph API — throttled (HTTP 429) response

**When this applies:** A Graph call returned **429 Too Many Requests** (or you are designing for it). Observable: `429` status + a `Retry-After` header.

**Last verified:** 2026-05-30 against Graph throttling guidance (`Retry-After` is authoritative; limits are per-workload and per-app/per-tenant). `[verify-at-build]` — specific limits vary by service.

```mermaid
flowchart TD
    START[Got 429 Too Many Requests] --> Q1{Retry-After header present?}
    Q1 -->|YES| WAIT[Wait exactly Retry-After, then retry once]
    Q1 -->|NO| BACKOFF[Exponential backoff with jitter]
    WAIT --> Q2{Still 429 after retries?}
    BACKOFF --> Q2
    Q2 -->|YES| Q3{Are you making many small calls?}
    Q2 -->|NO| DONE[Succeeded]
    Q3 -->|YES| REDUCE[Reduce call volume: $batch, $select, delta instead of re-reads]
    Q3 -->|NO, single heavy call| SPREAD[Spread load over time / shard by resource]
```

**Rationale per leaf:**
- _Honor `Retry-After`_ — it is a contract; waiting exactly that long and retrying once is the sanctioned path.
- _Backoff + jitter_ — when no header, exponential backoff with jitter avoids synchronized retry storms.
- _Reduce volume_ — persistent throttling is a design smell: batch, select fewer fields, switch re-reads to delta.
- _Spread / shard_ — a single hot resource needs load spreading, not just retries.

**Tradeoffs summary:**

| Response | When | Effect |
|---|---|---|
| Honor `Retry-After` | header present | correct, polite, usually sufficient |
| Backoff + jitter | no header | avoids retry storms |
| Reduce volume (`$batch`/`$select`/delta) | repeated 429s | fixes the cause |
| Spread / shard | one hot path | smooths the spike |

---

## Decision Tree: Graph API — advanced query (default vs ConsistencyLevel=eventual)

**When this applies:** You need `$count`, `$search`, `$orderby` with `$filter`, or `$filter` on a directory property that the default query engine rejects (often a `400` telling you to use advanced query).

**Last verified:** 2026-05-30 against Graph advanced-query guidance for directory objects. `[verify-at-build]`.

```mermaid
flowchart TD
    START[Building a directory-object query] --> Q1{Need $count, $search, or filter the default engine rejects?}
    Q1 -->|NO| DEFAULT[Default query, no special header]
    Q1 -->|YES| ADV[Add header ConsistencyLevel eventual AND include $count=true]
    ADV --> Q2{Results need strong ordering guarantees?}
    Q2 -->|YES| NOTE[Accept eventual consistency caveat or re-query]
    Q2 -->|NO| OK[Use advanced query]
```

**Rationale per leaf:**
- _Default query_ — for simple equality filters and reads; no header needed.
- _Advanced query_ — `ConsistencyLevel: eventual` **plus** `$count=true` unlocks `$search`, `$count`, and not-supported-by-default `$filter`/`$orderby` on directory objects.
- _Eventual-consistency caveat_ — advanced queries are eventually consistent; don't assume read-your-write immediacy.

**Tradeoffs summary:**

| Mode | Header | Capability | Caveat |
|---|---|---|---|
| Default | none | equality filter, basic reads | limited operators |
| Advanced | `ConsistencyLevel: eventual` + `$count=true` | `$search`/`$count`/rich `$filter`/`$orderby` | eventual consistency |

---

## See also

- [`../../../docs/best-practices/decision-trees-in-knowledge-files.md`](../../../docs/best-practices/decision-trees-in-knowledge-files.md) — the format these trees follow
- [`identity-auth-decision-trees.md`](./identity-auth-decision-trees.md) · [`workloads-notifications-decision-trees.md`](./workloads-notifications-decision-trees.md)
- [`../agents/graph-api-engineer.md`](../agents/graph-api-engineer.md) — the agent that traverses these
