# Small-firm practice decision trees

Which analysis for which symptom — traverse top-to-bottom before picking a method.

## Decision Tree: Busy but broke

1) Read realization and the billed-vs-collected gap (§3 #1). 2) Locate write-down/write-off/A/R leakage. 3) Check intake and scope (§3 #2, #4). 4) Check utilization (§3 #5).

## Decision Tree: Should I take this matter?

1) Conflict check (§3 #2). 2) Fit/viability. 3) Scope and fee structure (§3 #4). Route the call to the attorney.

## Decision Tree: An ethics/trust question

Stop. Route to the responsible attorney and the applicable rules of professional conduct (§3 #6) — this plugin does not resolve ethics questions.

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Read realization** → use when: Read realization and the billed-vs-collected gap, locating write-downs, write-offs, and A/R, so the practice's real economics are visible. ([`../skills/read-realization/SKILL.md`](../skills/read-realization/SKILL.md))
- **Run conflict-checked intake** → use when: Run intake as risk management — conflict check and fit/viability screen before the engagement — to prevent the matters that destroy realization. ([`../skills/run-conflict-checked-intake/SKILL.md`](../skills/run-conflict-checked-intake/SKILL.md))
- **Support drafting as work product** → use when: Draft and review documents from clause libraries with issue flags, as attorney-reviewed work product, never legal advice. ([`../skills/support-drafting/SKILL.md`](../skills/support-drafting/SKILL.md))
- **Scope the matter and fee** → use when: Scope a matter and choose the fee structure deliberately, since an open-ended hourly with no budget breeds write-offs. ([`../skills/scope-the-matter/SKILL.md`](../skills/scope-the-matter/SKILL.md))
- **Build a practice scorecard** → use when: Build a realization-led practice scorecard with utilization, collected revenue, and A/R, each defined and baselined. ([`../skills/build-practice-scorecard/SKILL.md`](../skills/build-practice-scorecard/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`legal-engagement-lead`](../agents/legal-engagement-lead.md)
- **Litigation matters** → [`litigation-specialist`](../agents/litigation-specialist.md)
- **Transactional drafting** → [`contracts-drafting-specialist`](../agents/contracts-drafting-specialist.md)
- **The numbers** → [`legal-operations-analyst`](../agents/legal-operations-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. Realization, not billed hours, is the practice's truth — if this is in question, apply §3 #1 before any method.
2. Intake is risk management — conflict and fit before the engagement — if this is in question, apply §3 #2 before any method.
3. Work product is attorney decision-support, never legal advice — if this is in question, apply §3 #3 before any method.
4. Scope the matter and the fee structure deliberately — if this is in question, apply §3 #4 before any method.
5. Utilization and the non-billable load are a capacity story — if this is in question, apply §3 #5 before any method.
6. Trust accounting and ethics rules are non-negotiable guardrails — if this is in question, apply §3 #6 before any method.
7. Collections and A/R are part of the matter, not after it — if this is in question, apply §3 #7 before any method.
8. Date and source any rate, benchmark, or law reference — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
