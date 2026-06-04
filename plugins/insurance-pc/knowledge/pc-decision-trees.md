# P&C decision trees

Which analysis for which symptom — traverse top-to-bottom before picking a method.

## Decision Tree: Combined ratio deteriorated

1) Split loss vs expense (§3 #1). 2) Strip cat (§3 #4). 3) Separate frequency vs severity (§3 #3). 4) Check reserve development (§3 #5).

## Decision Tree: Is the rate adequate?

1) Build the indicated rate (§3 #2). 2) Compare to filed. 3) Stress for loss trend (§3 #3).

## Decision Tree: Which lines to grow/shrink

1) Decompose NCR by line (§3 #6). 2) Strip cat per line (§3 #4). 3) Map mix decisions to the result.

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Decompose the combined ratio** → use when: Split the combined ratio into loss and expense, then attritional and catastrophe, so a deteriorating result is diagnosed correctly. ([`../skills/decompose-the-combined-ratio/SKILL.md`](../skills/decompose-the-combined-ratio/SKILL.md))
- **Price to rate adequacy** → use when: Price risk to expected loss plus expense plus profit load against loss trend, not to the competitor, so growth doesn't grow a loss. ([`../skills/price-to-rate-adequacy/SKILL.md`](../skills/price-to-rate-adequacy/SKILL.md))
- **Separate frequency from severity** → use when: Decompose a loss-ratio move into frequency and severity, since they have opposite responses, before prescribing. ([`../skills/separate-frequency-and-severity/SKILL.md`](../skills/separate-frequency-and-severity/SKILL.md))
- **Review claims leakage** → use when: Read indemnity leakage, LAE, and cycle time as managed metrics, not minimized payout, to find the controllable gap. ([`../skills/review-claims-leakage/SKILL.md`](../skills/review-claims-leakage/SKILL.md))
- **Read the portfolio result** → use when: Read the underwriting result by line of business, attritional-vs-cat and net-of-reinsurance, so the mix story is visible. ([`../skills/read-the-portfolio-result/SKILL.md`](../skills/read-the-portfolio-result/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`underwriting-lead`](../agents/underwriting-lead.md)
- **Risk selection and pricing** → [`pc-underwriter`](../agents/pc-underwriter.md)
- **Claims operations** → [`claims-specialist`](../agents/claims-specialist.md)
- **The numbers** → [`actuarial-pricing-analyst`](../agents/actuarial-pricing-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. The combined ratio is loss plus expense — read both — if this is in question, apply §3 #1 before any method.
2. Underwrite to the loss ratio, not the competitor's rate — if this is in question, apply §3 #2 before any method.
3. Separate frequency from severity — if this is in question, apply §3 #3 before any method.
4. Isolate the catastrophe load — if this is in question, apply §3 #4 before any method.
5. Reserve adequacy is the truth-teller — if this is in question, apply §3 #5 before any method.
6. Line-of-business mix drives the portfolio result — if this is in question, apply §3 #6 before any method.
7. Claims is a leakage-and-cycle-time problem, not just payout — if this is in question, apply §3 #7 before any method.
8. Cite the source and date for every benchmark — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
