# Go/no-go needs written, pre-agreed criteria

**Stance:** launch criteria are measurable, owner-assigned, and agreed *before* the
readiness review. Criteria invented in the room are bias, not a bar.

## Why

A go/no-go decided on the day, from the gut, is indistinguishable from a guess —
and it's the kind that produces a retro titled "how did we miss this?" When the
bar is written and agreed in advance, the review becomes a check against a
contract instead of a negotiation under deadline pressure (where "we're so close"
always wins).

## In practice

- Define each criterion as a **measurable** condition with a **named owner** who
  confirms it (e.g. "p99 latency < 300ms under 2× expected load — owned by SRE").
- Agree the full set with the sponsor *before* the review.
- In the review, mark each GO / NO-GO / **waived**. A waiver is recorded with its
  **risk acceptance** and who accepted it — never silently dropped.
- End with an explicit decision and the name of who made it.

Use the [`launch-readiness-checklist`](../templates/launch-readiness-checklist.md)
template and the go/no-go tree in
[`../knowledge/tpm-engagement-decision-trees.md`](../knowledge/tpm-engagement-decision-trees.md).

## Smell

"We'll watch it closely" as a launch gate — that's a hope, not a threshold. A gate
is a metric and a number.
