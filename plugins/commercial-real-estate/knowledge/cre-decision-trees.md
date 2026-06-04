# CRE decision trees

Which analysis for which question — traverse top-to-bottom before picking a method.

## Decision Tree: Should we buy this deal?

1) Re-underwrite to in-place NOI (§3 #1). 2) Separate going-in cap from levered IRR (§3 #2). 3) Price the spread (§3 #3). 4) Stress the debt and refi (§3 #6). 5) Only then weigh the pro-forma upside.

## Decision Tree: This asset missed NOI

1) Is it a rent (occupancy/NER), opex, or recovery variance (§3 #7)? 2) Is the miss structural or a timing lag? 3) Map to a leasing, expense, or recovery fix.

## Decision Tree: Sell or hold through the refi?

1) What rate/cap does the refinance clear at (§3 #6)? 2) What's the clearing sale price today? 3) Compare hold equity-at-risk to a sale now.

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Underwrite to in-place NOI** → use when: Build a CRE base case on contractual in-place income before any pro-forma step-up — separating real income from assumed growth so the return rests on something sourced. ([`../skills/underwrite-to-in-place-noi/SKILL.md`](../skills/underwrite-to-in-place-noi/SKILL.md))
- **Price the cap-rate-vs-Treasury spread** → use when: Frame a cap rate as a risk premium over the 10-yr Treasury, not an absolute level, so a 'compression' is read correctly. ([`../skills/price-the-cap-rate-spread/SKILL.md`](../skills/price-the-cap-rate-spread/SKILL.md))
- **Decompose net effective rent** → use when: Convert a face rent to net effective by netting TI, free rent, and leasing commissions, so comps and underwriting use the rent the landlord actually earns. ([`../skills/decompose-net-effective-rent/SKILL.md`](../skills/decompose-net-effective-rent/SKILL.md))
- **Stress the debt and refinance wall** → use when: Size the debt, schedule DSCR through the hold, and surface the refinance year and the rate at which the deal breaks. ([`../skills/stress-the-debt-and-refi/SKILL.md`](../skills/stress-the-debt-and-refi/SKILL.md))
- **Build a NOI-growth asset plan** → use when: Sequence lease rollovers, recovery improvements, and capex against a quarterly NOI target so a held asset tracks (or beats) its acquisition underwriting. ([`../skills/build-the-asset-plan/SKILL.md`](../skills/build-the-asset-plan/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`cre-engagement-lead`](../agents/cre-engagement-lead.md)
- **The underwriting model** → [`acquisitions-underwriter`](../agents/acquisitions-underwriter.md)
- **The owned asset** → [`asset-property-manager`](../agents/asset-property-manager.md)
- **The outside view** → [`cre-market-analyst`](../agents/cre-market-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. Underwrite to in-place NOI, not pro-forma — if this is in question, apply §3 #1 before any method.
2. Cap rate and discount rate are not interchangeable — if this is in question, apply §3 #2 before any method.
3. Always separate the spread — if this is in question, apply §3 #3 before any method.
4. Vacancy is bifurcated — never quote it without the tier — if this is in question, apply §3 #4 before any method.
5. Net effective rent is the real number, not face rent — if this is in question, apply §3 #5 before any method.
6. Debt is the swing factor, not the cap rate — if this is in question, apply §3 #6 before any method.
7. Operating expenses are an underwriting input, not a plug — if this is in question, apply §3 #7 before any method.
8. Cite the source and date for every market number — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
