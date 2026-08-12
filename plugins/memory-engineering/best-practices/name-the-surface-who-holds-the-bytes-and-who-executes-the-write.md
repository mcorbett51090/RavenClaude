# Name the surface before you design: who holds the bytes, and who executes the write.

**Status:** Pattern. **Constitution:** §3 #4, §4.

## Use when

Any design conversation that has reached "we'll use memory" without naming *where* the bytes land.

## The rule

**"Memory" is not a surface.** Before any further design, name the specific storage surface and answer two questions about it in writing: **who holds the bytes**, and **who executes the write**. Two surfaces with the same-looking API can have opposite trust and data-residency models; collapsing them misstates the part that matters.

The two questions are not a formality. *Who holds the bytes* sets data residency, contract scope, and who can be compelled to produce them. *Who executes the write* sets who owns path traversal, size caps, redaction and expiry — because whoever executes the write owns the safeguards the platform documents but does not enforce for you.

## Why it matters

One vendor's memory surfaces differ on exactly these axes: on one, storage is **client-side** and the vendor-looking path is a prefix your own handler maps onto storage you own; on another, the **vendor** holds the bytes, mounts are set at session creation, and access is enforced at the filesystem level. A design that says "memory" and means the first while the security review assumes the second has a hole nobody can see in the diagram.

The same conflation hides the *status* question. A surface behind a dated beta header is a dated fact, and a beta→GA transition invalidates a design note independently of its age.

## How to apply

Fill this row for every surface in the design, once, and put it in the [memory design record](../templates/memory-design-record.md):

| Question | Why it decides the design |
|---|---|
| Who holds the bytes? | Data residency, contract scope, who can be compelled to produce them |
| Who executes the write? | Who owns path traversal, size caps, redaction, expiry |
| GA or beta, and the exact header string **today**? | A beta header is a dated fact — write the date beside it |
| What are the hard caps, and what happens *at* the cap? | Silent truncation and hard failure need different designs |
| Is there an audit trail, and can a historical value be redacted? | This is the entire erasure story |
| Does anything consolidate or forget on its own? | Usually the answer is no — see rule §3 #3 |

- Never quote a header string, a cap or a multiplier from memory. They are the fastest-moving content in this plugin: read them from [memory surfaces](../knowledge/memory-surfaces-2026.md), dated, `[verify-at-use]`.
- The questions are vendor-neutral even though the worked example is not. Porting the design to another stack means re-answering the same six rows, not finding the equivalent product name.

## The anti-pattern this prevents

The §4 failure mode: **"we'll use memory" with no named surface, no byte-holder, and no named write executor** — the design that survives review because everyone in the room silently supplied a different answer.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) §3 #4 — the house opinion this rule encodes.
- [`../knowledge/memory-surfaces-2026.md`](../knowledge/memory-surfaces-2026.md) — the five surfaces, their dated strings, limits and sharp edges.
- [`../knowledge/memory-engineering-decision-trees.md`](../knowledge/memory-engineering-decision-trees.md) — Tree 2 routes a write to its surface.
- [`../agents/memory-architect-lead.md`](../agents/memory-architect-lead.md) — the agent that names the surface.
