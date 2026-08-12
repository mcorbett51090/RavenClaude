# Deleting the row is not erasure.

**Status:** Absolute rule. **Constitution:** §3 #7, §4.

## Use when

Designing any store that could hold personal data — and the moment a deletion request, a retention schedule, or a "we can just delete it" arrives.

## The rule

**Removing a memory's row does not necessarily erase what it carried.** Embeddings, immutable version history and derived summaries retain the content, and a redaction path may refuse to touch the current head. **State what remains *before* the first write**, not when the request arrives.

Five residues, each a place an erasure request quietly fails:

| Residue | Why it survives | What to do about it |
|---|---|---|
| **Embeddings / vector rows** | Deleting the source text does not delete the derived vector, and vectors are invertible in practice | Delete or re-index the vector in the same transaction as the row |
| **Immutable version history** | The audit trail is the point — versions survive deletion of the memory | Use the platform's redaction operation; verify it actually applied |
| **Derived summaries** | A compaction, a consolidation output or a "learned context" carries the fact forward under a new id | Enumerate every derived artifact at design time; there is no automatic cascade |
| **Cached prefixes** | An evictable cache is not a store of record, but the bytes exist until eviction | Do not model it as durable; do not model it as erased either |
| **Backups and exports** | Outside the store's own API entirely | Answer this in the retention policy, not in the code |

## Why it matters

Text embeddings are invertible to a startling degree — published work recovers the exact text of most short inputs from their embeddings, including personal information from clinical notes. Regulators have separately reasoned that mathematical objects derived from personal data are not automatically anonymous. Together those make **"delete the row, keep the vector"** an indefensible erasure story.

**That step is this plugin's reasoned engineering inference, not settled law.** No regulator guidance addressed specifically at embeddings in an agent memory index was located. Teach it as an inference; route the determination to the qualified authority.

## How to apply

- **Write the erasure story into the [memory design record](../templates/memory-design-record.md) before the first write**, enumerating all five residues for your actual stack.
- Know the sharp edge: **a version that is the current head cannot be redacted.** Write a new version, or delete the memory, *first* — then redact. An implementation that redacts the live value fails silently on exactly the data the request was about and returns success-shaped output.
- **Verify erasure by reading back, never by checking a return code.**
- Sequence rollback and erasure deliberately: with no restore endpoint, rollback is retrieve-then-rewrite, so a rollback performed *after* an erasure can reintroduce the erased content.
- Keep the boundary: whether the store holds personal data, what lawful basis applies, whether a request is in scope, and what a retention schedule must say are determinations for [`data-governance-privacy`](../../data-governance-privacy/) and counsel. This team's job is to make the system able to carry the determination out.

## The anti-pattern this prevents

The §4 failure mode: **an erasure story that stops at the row and never names the embedding, the version history, or the derived summary** — which reads as complete right up to the first request that has to be answered under oath.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) §3 #7 — the house opinion this rule encodes.
- [`../knowledge/memory-security-and-privacy.md`](../knowledge/memory-security-and-privacy.md) — the sourced evidence, the regulator's position, the stated gap, and the residue table in full.
- [`../knowledge/memory-engineering-decision-trees.md`](../knowledge/memory-engineering-decision-trees.md) — Tree 3 separates wrong, stale and poisoned from un-erased.
- [`../agents/memory-retention-and-erasure-engineer.md`](../agents/memory-retention-and-erasure-engineer.md) — the agent that owns erasure residue.
