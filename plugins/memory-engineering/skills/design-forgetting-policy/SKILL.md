---
name: design-forgetting-policy
description: "Design retention and erasure before the first write — TTL, caps, decay, consolidation timing, dedup, contradiction handling, and what a delete actually leaves behind. Reach for this on any durable store."
---

# Skill: Design the forgetting policy

**Decision 3 of the six-decision spine — *what makes it forget, and what does erasure actually require?*** Two halves, and the second is the one that gets skipped: **bounding growth** and **removing meaning**. A store can be perfectly bounded and still be unable to honour a deletion request.

**The finding this whole skill rests on:** across the evaluated systems in the published benchmark, **none pruned or forgot by default** — footprint grew monotonically under default behaviour, and bounding it required an independent forgetting policy. Retention is the operator's job, not the library's (§3 #3).

Do this **before the store takes its first write.** Retrofitting a retention policy onto a live store is a migration; writing one first is a paragraph.

---

## Part A — Bounding the store

### Step 1 — State the default out loud

Write the sentence into the [memory design record](../../templates/memory-design-record.md): *"Nothing in this store forgets unless we make it."* An unbounded store is a decision nobody made. If you cannot name the mechanism that removes an entry, there isn't one.

### Step 2 — Choose the bound, and project it

Three bounds, and they compose:

| Bound | What it does | What it does **not** do |
|---|---|---|
| **TTL** | Holds the store at a flat steady state once it fills | Nothing about relevance — an old fact may still be the only true one |
| **Size / item cap** | Puts a ceiling on footprint | Nothing about *which* item goes; you still owe an eviction rule |
| **Decay / relevance scoring** | Demotes rather than deletes | It is not erasure — the bytes are still there |

Project it before you commit to it, with [the calculator](../../scripts/memory_engineering_calc.py):

```
memory_engineering_calc.py store-growth --writes-per-day 40 --avg-size-kb 2.5 \
  --ttl-days 90 --max-items 2000
```

Observed output includes `Steady state : 3,600 items / 9,000 KB (TTL holds it flat)` and `--max-items cap : reached on day 50 (2,000 items)`. Drop the TTL and cap flags and the same command prints the fixed *nothing forgets by default* NOTE instead — that NOTE is the finding, not a warning.

### Step 3 — Check the surface's own cap, and what happens at it

Your bound is not the only one. A surface may impose a hard cap **below** yours, and the failure mode differs: some caps make new writes **fail**, others **silently drop** the overflow at load time. Current published caps, dated: [memory surfaces (2026)](../../knowledge/memory-surfaces-2026.md). Design for whichever failure you actually get.

> **Bytes are the tame axis.** Measured footprint varied about ninefold across systems at 1M tokens, while construction **token cost** diverged far more sharply — super-linearly for agentic paradigms, because each ingestion reads the growing store before writing. Project the growth *slope*, not the day-one footprint ([economics](../../knowledge/memory-engineering-economics.md)).

### Step 4 — Decide where consolidation runs, and what it bills

Three positions, three bills. Pick one deliberately; the default is "nowhere," which is how duplicates accumulate.

| Position | What it costs | What it costs you later |
|---|---|---|
| **On the write path** | An inference call on every write — a latency **and** cost tax on every turn | Nothing accumulates, but every turn pays |
| **Offline / batch** | A separate job, billed at standard token rates, scaling with input volume | **Staleness** between runs |
| **At read time** | Nothing stored; resolution cost on every read | Repeated work, and no durable resolution to audit |

An offline consolidation job typically produces a **new** output store and leaves the input untouched — which is a safety property, and also means nothing is fixed until you cut over. Confirm the actual semantics for your surface before designing around them.

### Step 5 — Write the dedup rule

Name the identity key. "Same fact" is not a definition. Decide: exact-match on a normalized key, embedding similarity above a threshold, or a model judgement — and record which, because each has a different false-merge rate and the third is not reproducible.

### Step 6 — Contradiction handling — detect, then **stop**

Two entries disagree. This is the most common durable-memory defect after unbounded growth, and it has one hard rule:

> **Never auto-merge a contradiction. Surface it for a human decision.**

An automatic merge picks a winner using a heuristic nobody agreed to (usually "newest wins"), destroys the losing entry, and leaves no record that a choice was made. When the choice was wrong, there is nothing left to audit. Recency is a *signal*, not a resolution rule: a superseded fact and a temporarily-wrong correction look identical by timestamp.

The design that works:

1. **Detect** on write, or in the consolidation pass — do not wait for a bad answer.
2. **Keep both**, flagged, with provenance on each — who wrote it, when, from which session.
3. **Surface** the pair to a named human owner with a deadline.
4. **Record the resolution** as a new entry with a pointer to what it superseded — never as a silent overwrite.
5. **Add the case to the golden set** ([build-memory-eval](../build-memory-eval/SKILL.md)). An unresolved contradiction that produced a wrong answer is an eval item, permanently.

If your volume genuinely cannot support a human in the loop, the honest design is to **refuse to answer** from a contradicted entry and escalate, not to guess and look confident.

### Step 7 — Staleness is not contradiction

Stamp every entry with a write timestamp and, where the platform offers one, its own modification marker. Then be precise about the distinction, because the two look identical in a transcript and have nothing else in common:

- **Contradiction** — two entries, both present, incompatible. → Step 6.
- **Staleness** — one entry, once true, now aged out. → A retention defect. TTL, decay, or a re-verification trigger.
- **Never true, and untrusted input could reach the write path** → not a retention problem at all. That is **poisoning**; go to [memory-poisoning-review](../memory-poisoning-review/SKILL.md) and to the store, not to the prompt.

**Age is not correctness.** A freshness marker tells you when something was written, never whether it is still true.

---

## Part B — Erasure: what a delete actually leaves behind

### Step 8 — Enumerate the residue *before* the first write

**Deleting the row is not erasure** (§3 #7). Every item below is a place a deletion request quietly fails, and there is no automatic cascade between them.

| Residue | Why it survives | What the design must say |
|---|---|---|
| **Embeddings / vector rows** | Deleting the source text does not delete the derived vector — and embeddings are invertible to a startling degree | Delete or re-index the vector in the same transaction as the row |
| **Immutable version history** | The audit trail is the point; versions outlive the memory they belong to and carry their own retention window | Use the platform's redaction operation, then **verify it applied** |
| **Derived summaries** | A compaction output, a consolidation result, or a "learned context" carries the fact forward under a new id | Enumerate every derived artifact at design time |
| **Cached prefixes** | An evictable cache is not a store of record, but the bytes exist until eviction | Do not model it as durable; do not model it as erased either |
| **Backups and exports** | Outside the store's own API entirely | Answer this in the retention policy, not in the code |

The evidence for the embeddings row — the inversion result and the regulator's reasoning about derived mathematical objects — is in [memory security and privacy](../../knowledge/memory-security-and-privacy.md), together with an explicit statement of where the reasoning is **this plugin's inference rather than settled law**. Carry that hedge forward; do not launder it.

### Step 9 — The sharp edge that breaks naive erasure

**A version that is the current head may not be redactable.** On a versioned store, you may have to write a new version, or delete the memory, **first** — and only then redact. An implementation that calls redaction on the live value can fail on exactly the data the request was about **and return success-shaped output.**

Two consequences, both non-negotiable:

- **Verify erasure by reading it back. Never by checking a return code.**
- **Sequence matters.** A rollback performed *after* an erasure can reintroduce the erased content, because rollback is retrieve-then-rewrite. Write the ordering into the runbook.

### Step 10 — Rehearse the erasure, on a real store, before you promise it

Pick a real entry in a non-production store. Delete it. Then go looking: the row, the vector, every derived summary, the version history, the export. Write down what you found still there. **That list is the erasure story** — not the code path you intended.

If the platform offers no redaction path at all, erasure is **unimplementable on that surface**. Escalate before anyone promises it to a customer.

### Step 11 — Hand off the determination you are not qualified to make

This is an engineering skill. **Whether the store holds personal data, what lawful basis applies, whether a given request is in scope, and what a retention schedule must say are determinations for the qualified authority** — route them to [`data-governance-privacy`](../../../data-governance-privacy/) and to counsel. This skill's job is to make sure that when the determination arrives, the system can actually carry it out.

## Output

A retention and erasure policy with: the bound and its projection, the consolidation position and its bill, the dedup key, the contradiction procedure with a named human owner, and the enumerated residue list with a rehearsed deletion behind it. Traverse Tree 3 in [the decision trees](../../knowledge/memory-engineering-decision-trees.md).
