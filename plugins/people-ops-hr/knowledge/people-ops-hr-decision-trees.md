# People Ops / HR — Decision Trees

_Decision trees + a dated reference map. Practice and tooling rows are `[verify-at-build]` — re-check against the current vendor/framework, and **never** treat any row as employment-law advice. Last reviewed: 2026-06-08._

Traverse before designing a hiring loop, setting a comp band, authoring a policy, running a lifecycle event, or diagnosing a funnel. **5 trees below:** is-this-hire-structured-and-fair, is-this-comp-decision-defensible, is-this-lifecycle-step-owned-and-offboarding-complete, is-this-policy-plain-language-and-not-a-legal-opinion, and what-is-the-funnel-telling-me. **Cardinal rule for every tree: where a branch reaches employment law (FLSA classification, EEO, leave entitlement, equal-pay, pay-transparency, termination), the output is "flag for counsel" — this knowledge bank does not give legal advice.**

## Decision Tree: Is this hire structured enough to be fair and predictive?

Structure — a defined rubric assessed the same way for every candidate — predicts performance and reduces bias better than freeform interviews.

```mermaid
graph TD
  A[Open role to fill] --> B{Is the role's LEVEL defined on the ladder?}
  B -- No --> C[Level it first - the band and competencies flow from the level; route leveling to total-rewards-analyst]
  B -- Yes --> D{Does each competency have ONE assessor + an anchored scorecard?}
  D -- No --> E[Redesign the loop - map one competency to one assessor; anchor 1-4 rating levels per competency]
  D -- Yes --> F{Does the debrief force EVIDENCE before a hire/no-hire verdict?}
  F -- No --> G[Add a structured debrief rubric - opinions without evidence amplify bias]
  F -- Yes --> H{Does any stage touch EEO / ban-the-box / pay-transparency?}
  H -- Yes --> I[Flag those points for counsel, then proceed - do NOT opine on the posting/candidate]
  H -- No --> J[Run the structured loop - instrument the funnel as you go]
```

_One competency, one assessor, one anchored scorecard, evidence-forced debrief. Applicant volume is a vanity count; conversion and time-in-stage are the diagnostic._

## Decision Tree: Is this compensation decision defensible (band + equity)?

Structure before generosity: a leveling framework, a band that maps to the level, and a pay-equity review that controls for legitimate factors.

```mermaid
graph TD
  A[Comp decision: offer, raise, or band] --> B{Is there a leveling / job-architecture ladder?}
  B -- No --> C[Build the ladder first - levels x families; a band with no level under it has no logic]
  B -- Yes --> D{Does the band have a midpoint, spread, and market-strategy posture?}
  D -- No --> E[Set range mechanics - midpoint = market posture, spread = growth runway, compa-ratio for position]
  D -- Yes --> F{Has a pay-equity review controlled for level/tenure/location/performance?}
  F -- No --> G[Run the controlled review - surface the UNEXPLAINED residual, not a raw average gap]
  F -- Yes --> H{Unexplained gap or equal-pay/transparency exposure?}
  H -- Yes --> I[Remediation framing + flag the legal certification for counsel - do NOT self-certify compliant]
  H -- No --> J[Apply the decision from the band; record the compa-ratio and rationale]
```

_No band without a level under it. A pay-equity check that doesn't control for legitimate factors proves nothing. Legal certification is counsel's, not yours._

## Decision Tree: Is this lifecycle step owned, repeatable, and offboarding-complete?

The value of People Ops is consistency — the same good onboarding and the same complete offboarding, every time, owned by someone. Offboarding is the half everyone forgets.

```mermaid
graph TD
  A[Lifecycle event: a hire or a departure] --> B{Is there a NAMED owner + a written checklist for it?}
  B -- No --> C[Stop improvising - assign an owner and write the repeatable list; same good start/exit every time]
  B -- Yes --> D{Is the HRIS status change the FIRST step that triggers the rest?}
  D -- No --> E[Make the HRIS update the trigger - it is the source of truth or it is nothing; downstream reports drift otherwise]
  D -- Yes --> F{Departure? Are access revoke + final pay + equipment + knowledge transfer all on the list?}
  F -- No --> G[Add the missing steps - a missed access step is a SECURITY risk; route the data/access posture to security-reviewer]
  F -- Yes --> H{Does final pay / separation terms / timing touch employment law?}
  H -- Yes --> I[Flag final-pay timing + separation terms for counsel, then run the rest - do NOT opine]
  H -- No --> J[Run the owned checklist; confirm the HRIS reflects the change before closing]
```

_A missed access step is a security risk; a missed final-pay step is a compliance and trust risk. Offboarding is half the lifecycle — give it an owned checklist, triggered off the HRIS._

## Decision Tree: Is this policy plain-language, consistent, and not a legal opinion?

A policy nobody understands is a liability; a policy that contradicts another is worse than none; a policy that gives a legal opinion is the cardinal risk.

```mermaid
graph TD
  A[Drafting a handbook / policy] --> B{Does it follow statement -> scope -> rule -> process -> edge cases?}
  B -- No --> C[Restructure to the house format - plain language first, then mechanics, consistent across the handbook]
  B -- Yes --> D{Does it contradict any existing policy?}
  D -- Yes --> E[Reconcile first - a contradicting policy is worse than none; one canonical answer]
  D -- No --> F{Does it state an entitlement, eligibility, or classification (leave, exempt status, EEO)?}
  F -- Yes --> G[Flag the determination for counsel - describe the PROCESS, never opine on the legal entitlement]
  F -- No --> H{Is it jurisdiction-specific (accrual caps, final-pay timing, posting)?}
  H -- Yes --> I[Note the jurisdiction dependency and route the mechanics to counsel; keep the company-process part]
  H -- No --> J[Publish in plain language; assign an owner to keep it current]
```

_Statement → scope → rule → process → edge cases, consistent across the handbook. The moment a policy reaches an entitlement or classification, the output is "have counsel review this," not an answer._

## Decision Tree: What is the hiring funnel actually telling me (conversion, not volume)?

Applicant volume is a vanity count. Conversion between stages and time-in-stage are the diagnostics — pair every throughput number with a quality signal.

```mermaid
graph TD
  A[Hiring is slow / inconsistent / not converting] --> B{Is the funnel INSTRUMENTED - conversion + time-in-stage per stage?}
  B -- No --> C[Instrument it first - applicant count alone is vanity; you cannot fix what you cannot see]
  B -- Yes --> D{Where is the biggest conversion DROP or the longest time-in-stage?}
  D -- Top of funnel --> E[Sourcing / posting problem - widen or retarget sourcing; check the JD and channels, not the rubric]
  D -- Screen to onsite --> F[Screen calibration problem - tighten the screen rubric; one competency, one assessor]
  D -- Onsite to offer --> G[Debrief / decision problem - is the debrief evidence-forced? unstructured vibes leak here]
  D -- Offer to accept --> H{Is it comp, experience, or speed?}
  H -- Comp --> I[Route comp competitiveness to total-rewards-analyst - band/posture, not a one-off]
  H -- Experience/speed --> J[Candidate experience is the brand AND a conversion lever - fix latency + communication]
  E --> K{Does any stage touch EEO / ban-the-box / pay-transparency?}
  F --> K
  G --> K
  I --> K
  J --> K
  K -- Yes --> L[Flag those points for counsel, then proceed]
  K -- No --> M[Apply the fix at the diagnosed stage; re-measure conversion next cycle]
```

_Conversion + time-in-stage diagnose where candidates are lost; volume is vanity. A fast, fair, communicative process is both employer brand and an offer-accept conversion lever._

---

## Reference map (2026, `[verify-at-build]` — not legal advice)

| Area | Common practice / tooling | Notes |
|---|---|---|
| HRIS / core HR | BambooHR, Rippling, Gusto, HiBob, Workday (up-market) | The system of record for status/level/comp/dates — prefer one canonical source over spreadsheets `[verify-at-build]` |
| Applicant tracking (ATS) | Greenhouse, Ashby, Lever, Workable | Structured-hiring and funnel-metric support varies — verify scorecard/kit features `[verify-at-build]` |
| Structured hiring | Competency-anchored scorecards, interviewer-to-competency mapping, structured debrief | Research favors structured over unstructured interviews for validity + fairness `[verify-at-build]` |
| Comp / market data | Radford, Mercer, Payscale, Pave, Carta (equity) | Quote the market posture (lead/match/lag, which percentile/market), not a bare number `[verify-at-build]` |
| Leveling / job architecture | Levels x job families, competency definitions per level | The ladder under the band and the hiring rubric `[verify-at-build]` |
| Pay equity | Controlled regression / cohort analysis (level, tenure, location, performance) | Surface the *unexplained* residual; legal certification → counsel `[verify-at-build]` |
| Performance / review cycles | Merit matrix (performance x position-in-range), calibration, promotion tied to the ladder | Split merit vs. promotion vs. equity budgets; calibrate before communicating `[verify-at-build]` |
| Handbook / policy | Plain-language statement -> scope -> rule -> process -> edge cases; consistent across the handbook | Entitlement/accrual mechanics are jurisdiction-specific → flag for counsel `[verify-at-build]` |
| Employment-compliance basics | FLSA exempt/non-exempt, at-will, EEO, ADA/leave, pay-transparency, ban-the-box | **Flag for qualified counsel — this plugin does not give legal advice** `[verify-at-build]` |

_Framework references: structured-interview validity research; Team-of-one to mid-market People Ops practice. Every compensation, hiring, and policy item that touches employment law is **flagged for counsel** — re-verify any tool, market source, or practice before quoting it, and never present a row here as a legal determination._
