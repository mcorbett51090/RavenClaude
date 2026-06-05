# Set Case Reserves on Case Facts, Not on Payment History

**Status:** Absolute rule
**Domain:** Claims / reserving
**Applies to:** `insurance-pc`

---

## Why this exists

A case reserve set by extrapolating from prior payments rather than from the specific facts of the open claim produces two failure modes: it understates exposure on a claim with unusual severity characteristics (because the reserve is anchored to prior-payment patterns that don't apply here), and it overstates exposure on a claim that is more routine than historical precedent suggests. Both errors distort the IBNR calculation that sits on top of the case reserves and mislead the actuarial team about the adequacy of the overall reserve position. Fact-based reserving is not slower — it is more accurate, and accuracy is what the combined ratio measures.

## How to apply

Set each case reserve against the specific known and estimated facts of the claim, not against a formula derived from prior paid.

```
Case Reserve Setting — Fact Basis Checklist
──────────────────────────────────────────────────────
□ COVERAGE VERIFICATION
  Policy limits, retentions, endorsements, and exclusions confirmed
  Coverage in force on the date of loss confirmed

□ INJURY / DAMAGE FACTS
  Bodily injury: medical treatment to date, prognosis, disability extent,
                 permanency assessment (or pending — flag as uncertain)
  Property: replacement cost or ACV established from inspection or estimate
  Business interruption: period of restoration, daily income loss estimate

□ LIABILITY FACTS
  Liability established / contested / indeterminate — state the basis
  Comparative negligence estimate (where applicable)
  Third-party involvement

□ RESERVE COMPONENTS
  Indemnity: central estimate + high end (document both; carry the central)
  Loss adjustment expense (LAE): allocated (legal, experts) + unallocated
  Litigation exposure flag: escalate to supervisor if litigation is filed or threatened

□ RESERVE RATIONALE (one paragraph)
  "Reserve of $X,XXX is based on [facts listed]. The primary uncertainty is [Y].
   The reserve will be reviewed at [next evaluation point]."

□ REVIEWER
  Reserves above $X require supervisor or claims manager review before posting.
```

**Do:**
- Revise the case reserve every time material new information is received — a reserve that sits unchanged for 12+ months on a litigated matter is a flag.
- Set the indemnity reserve at the expected ultimate outcome, not at the current paid amount or a formula-derived percentage of paid.
- Document the rationale at the time of setting; "no change" entries in the reserve log are acceptable only when accompanied by a note confirming the facts were reviewed and no new information changed the estimate.

**Don't:**
- Set a reserve at a round number without a calculation that supports it.
- Use "payment pattern" (e.g., "similar claims settle for X% of limits") as the primary reserve basis without also confirming that the specific claim facts align with the pattern's underlying data.
- Allow reserves to be set below the known damage amount as a way to manage the incurred-loss ratio artificially.

## Edge cases / when the rule does NOT apply

- **IBNR reserves** (incurred but not reported, set at the portfolio level) — these are actuarial reserves, not case reserves; they are set by the actuarial team on triangle development, not on individual case facts.
- **High-frequency, low-severity lines** (e.g., auto glass) where formula-based reserves are standard industry practice and are periodically reconciled to actuals — document the formula and its basis; the principle of fact-based adequacy still applies at the aggregate level.

## See also

- [`../agents/claims-specialist.md`](../agents/claims-specialist.md) — owns case reserve setting, claims triage, and cycle-time management.
- [`./reserve-adequacy-is-the-truth-teller.md`](./reserve-adequacy-is-the-truth-teller.md) — the house opinion that frames why reserve accuracy is the foundational discipline; individual case reserves aggregate into the portfolio reserve position this rule governs.

## Provenance

Codifies the claims-specialist's reserving discipline from the insurance-pc plugin's CLAUDE.md §3 #5 (reserve adequacy is the truth-teller) and §3 #7 (claims is a leakage-and-cycle-time problem). The fact-basis checklist reflects standard best-practices claims reserving guidance from ISO, NAIC, and carrier claims management frameworks.

---

_Last reviewed: 2026-06-05 by `claude`_
