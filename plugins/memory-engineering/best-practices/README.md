# Memory Engineering best-practice docs

Named, citable rules for the `memory-engineering` plugin's 3 specialist agents. Each file is one rule — read, applied, and cited whole. Each is **1:1 with a house opinion** in [`../CLAUDE.md`](../CLAUDE.md) §3, and each is grounded in this plugin's [knowledge bank](../knowledge/memory-engineering-paradigms.md).

---

## Index

_8 rules, one per house opinion (§3). The order is the order a design hits them._

| Doc | Status | Use when |
|---|---|---|
| [`memory-cost-lives-on-the-write-path-amortize-before-you-adopt.md`](./memory-cost-lives-on-the-write-path-amortize-before-you-adopt.md) | Absolute rule | Anyone proposes adding, expanding or keeping a durable memory store. |
| [`prove-the-no-memory-baseline-loses-before-you-build-memory.md`](./prove-the-no-memory-baseline-loses-before-you-build-memory.md) | Absolute rule | The first time "we should add memory" is said out loud. |
| [`nothing-forgets-by-default-retention-is-the-operators-job.md`](./nothing-forgets-by-default-retention-is-the-operators-job.md) | Absolute rule | Before a store takes its first write, or when growth is deferred. |
| [`name-the-surface-who-holds-the-bytes-and-who-executes-the-write.md`](./name-the-surface-who-holds-the-bytes-and-who-executes-the-write.md) | Pattern | A design has reached "we'll use memory" without naming where the bytes land. |
| [`a-memory-store-is-untrusted-input-to-every-future-session-asi06.md`](./a-memory-store-is-untrusted-input-to-every-future-session-asi06.md) | Absolute rule | Any diff that writes to, reads from or deletes from a durable store. |
| [`memory-is-context-not-enforcement-to-block-use-a-hook.md`](./memory-is-context-not-enforcement-to-block-use-a-hook.md) | Absolute rule | A design or threat model answers "what stops this?" with a document. |
| [`deleting-the-row-is-not-erasure-embeddings-and-versions-retain-it.md`](./deleting-the-row-is-not-erasure-embeddings-and-versions-retain-it.md) | Absolute rule | Any store that could hold personal data; any deletion request. |
| [`every-published-memory-ranking-is-self-reported-build-your-own.md`](./every-published-memory-ranking-is-self-reported-build-your-own.md) | Pattern | Anyone offers a vendor benchmark or a leaderboard as evidence. |

## How these are meant to be used

- **Cite the file, not a paraphrase.** Each rule is written to be quoted whole into a deliverable.
- **Two rules will often apply at once.** Route the sequencing to [`memory-architect-lead`](../agents/memory-architect-lead.md) — overlapping signals usually mean two drivers at once, and the order changes the answer.
- **Volatile facts stay out of these files.** Caps, header strings and cache multipliers live, dated, in [`../knowledge/memory-surfaces-2026.md`](../knowledge/memory-surfaces-2026.md) `[verify-at-use]`. A rule that restated one would go stale silently.
- **Two of the eight have mechanical backup.** The plugin's advisory [hook](../hooks/flag-memory-engineering-antipatterns.sh) flags an unsourced benchmark figure and a cost claim with no named baseline. It is advisory by design and it does not cover the other six — a hook is not a substitute for reading the rule.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — the team constitution (house opinions §3, anti-patterns §4, output contract §7).
- [`../knowledge/`](../knowledge/memory-engineering-decision-trees.md) — the decision trees that route to these rules.
- [`../scenarios/README.md`](../scenarios/README.md) — three engagements where each of these was learned the expensive way.
