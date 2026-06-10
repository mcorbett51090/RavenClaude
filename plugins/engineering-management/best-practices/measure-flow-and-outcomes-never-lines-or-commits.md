# Measure flow and outcomes, never lines or commits.

**Status:** Absolute rule. **Constitution:** §3 #3, §4.

## Use when
Any use of metrics to read a team or a person. Read, applied, and cited whole.

## The rule
DORA (deploy frequency, lead time, change-fail rate, MTTR) and throughput are team health signals to improve the system — the moment they become individual stack-rank inputs they get gamed and the signal dies (Goodhart). Never rank a person by a velocity metric.

## Why it matters
This is house opinion §3 #3, distilled into a citable rule. Managers act on these deliverables and they concern real people and real systems, so a framing error here is not academic — it sends real decisions, careers, and codebases the wrong way. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a method — it sets the framing, not the conclusion.
- Metrics read the system, never the individual; DORA bands are cited with a report year + date (§3 #3 #8).
- A claim about a person is a hypothesis to test, never a verdict; management deliverables about a person are drafts for a human to own (§1, §2).
- Cite a source + date for any external benchmark, or mark it `[unverified — training knowledge]` (§3 #8).
- When this rule and another both apply, route to [`delivery-and-execution-manager`](../agents/delivery-and-execution-manager.md) to sequence them — overlapping signals usually mean two drivers at once.
- Keep sensitive personnel PII (health, protected-class, comp) out of the deliverable; route HR/legal/comp determinations to the qualified authority (§2).
- Close with a recommendation that has an owner, a date, and an expected change.

## The anti-pattern this prevents
The §4 failure mode: acting as if "measure flow and outcomes, never lines or commits." weren't true — one of the most common ways a management decision quietly goes wrong for the person or team it affects. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §3 #3 — the house opinion this rule encodes.
- [`../knowledge/engineering-management-decision-trees.md`](../knowledge/engineering-management-decision-trees.md) — the decision trees that route to it.
