# Retrieval quality caps generation quality — fix retrieval first.

**Status:** Absolute rule. **Constitution:** §3 #1, §4.

## Use when
Any ai / rag engineering deliverable where this question is in play — read, applied, and cited whole.

## The rule
An LLM can only ground on what it's given; if the right passage isn't retrieved, no prompt or bigger model recovers it. When answers are wrong, measure recall@k before touching the prompt or swapping the model.

## Why it matters
This is house opinion §3 #1, distilled into a citable rule. Practitioners act on these deliverables, so a framing error here is not academic — it sends real operating decisions the wrong way. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a method — it sets the framing, not the conclusion.
- Make every number in the deliverable carry a definition, a window, and a baseline (§3 #1).
- Cite a source + date for any external benchmark, or mark it `[unverified — training knowledge]` (§3 #8).
- When this rule and another both apply, route to [`rag-architect-lead`](../agents/rag-architect-lead.md) to sequence them — overlapping signals usually mean two drivers at once.
- Keep user data / prompt PII out of the deliverable; route professional/legal determinations to the qualified authority (§2).
- Close with a recommendation that has an owner, a date, and an expected metric movement.

## The anti-pattern this prevents
The §4 failure mode: acting as if "retrieval quality caps generation quality — fix retrieval first." weren't true — the most common way an analysis quietly misleads the practitioner who acts on it. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §3 #1 — the house opinion this rule encodes.
- [`../knowledge/ai-rag-engineering-decision-trees.md`](../knowledge/ai-rag-engineering-decision-trees.md) — the decision trees that route to it.
