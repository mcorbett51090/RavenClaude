# Memory Design Record — &lt;system&gt; — &lt;date&gt;

> The one durable artifact this team produces. Written **before the first write**, because four of its seven rows are unanswerable afterwards. Synthesized by [`memory-architect-lead`](../agents/memory-architect-lead.md).

## 0. Should this exist at all? (§3 #2 — the gate)

| Baseline | Measured on our data? | Accuracy | Cost per correct answer | Did it lose? |
|---|---|---|---|---|
| No memory (full history or none) |  |  |  |  |
| Lexical retrieval (deterministic top-*k*) |  |  |  |  |

**Both must lose before anything below is worth filling in.** If either wins, stop here and record that.

## 1. Paradigm (§3 #2)

| Field | Value |
|---|---|
| Paradigm | I raw context / II flat retrieval / III.a structure-augmented / III.b consolidating store / IV agentic |
| Construction · storage · retrieval · mutability | &lt;the four axes, one line each&gt; |
| Why not the cheaper paradigm above it | &lt;the answer that makes this record honest&gt; |

## 2. Surface (§3 #4)

| Question | Answer |
|---|---|
| Which surface | |
| **Who holds the bytes** | |
| **Who executes the write** | |
| GA or beta, exact header string, **and the date you read it** | `[verify-at-use]` — [memory surfaces](../knowledge/memory-surfaces-2026.md) |
| Hard caps, and what happens **at** the cap | |

## 3. What earns a write

| Field | Value |
|---|---|
| Trigger for a write | |
| Who or what executes it (code path / model-driven) | |
| Consolidation timing — write-path, offline batch, or never | |
| The bill that timing chooses | |

## 4. Retention (§3 #3)

| Field | Value |
|---|---|
| TTL / decay | |
| Size or item cap | |
| Behaviour at the cap (hard failure vs silent truncation) | |
| **Retention owner (role)** | |
| Growth projection at 30 / 90 / 365 days | see [cost sheet](memory-cost-sheet.md) |

## 5. Erasure — what remains after a delete (§3 #7)

| Residue | Present here? | Who deletes it | How erasure is **verified** |
|---|---|---|---|
| Embeddings / vector rows | | | read-back, never a return code |
| Immutable version history | | | redact — **not** the current head |
| Derived summaries / consolidations | | | |
| Cached prefixes | | | |
| Backups and exports | | | answered in the retention policy |

Legal basis, scope and schedule are **not** decided here — route to [`data-governance-privacy`](../../data-governance-privacy/) and counsel (§2).

## 6. Poisoning exposure (§3 #5)

Summary only — the full sheet is the [memory threat model](memory-threat-model.md).

| Field | Value |
|---|---|
| Write paths reachable from untrusted input | |
| Read-only inventory | |
| Audit trail queryable before an incident? | |
| Rollback rehearsed? | |

## 7. Economics (§3 #1, #8)

| Field | Value |
|---|---|
| **Named baseline** | full-context-prefill / lexical-retrieval / stateless |
| Break-even query volume (`n*`) | see [cost sheet](memory-cost-sheet.md) |
| Cost per correct answer, this system vs baseline | see [eval sheet](memory-eval-sheet.md) |
| Cache-invalidation bill | |

## 8. Assumptions, data gaps, and next actions

| Item | Owner | Date | Expected movement |
|---|---|---|---|
| | | | |

**Sources:** &lt;URL — retrieval date&gt; for every external number (§4 cite-or-mark rule).
