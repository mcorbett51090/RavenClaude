# Fix the product before writing around it

**Stance:** when the getting-started path is painful, the first move is a
product-feedback ticket — not a longer tutorial.

## Why

DevRel's highest-leverage output is the friction it **removes**, not the words it
adds to paper over friction. A tutorial that walks developers around a confusing
default, a bad error message, or a missing convenience is technical debt with a
smile: every new developer still hits the flaw, the doc rots as the product
changes, and the underlying problem never gets prioritized because no one filed it
with evidence. Content is the stopgap; the fix is the goal.

## In practice

- Traverse the fix-or-document tree in
  [`../knowledge/devrel-engagement-decision-trees.md`](../knowledge/devrel-engagement-decision-trees.md):
  is the step painful because the **product** is confusing/broken, or because it's
  merely undiscoverable?
- Product-pain → file a
  [`product-feedback-brief`](../templates/product-feedback-brief.md) with frequency
  + severity evidence; add a **clearly-marked** workaround only as a stopgap.
- Sound-but-undiscoverable → now it's a legitimate content task.
- Bring recurring community pain to product as evidence, not anecdotes — that's how
  DevRel earns its seat.

## Smell

A growing library of "workaround" docs and a product backlog with no DevRel-filed
DX bugs in it. The docs are hiding the signal product needs.
