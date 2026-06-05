# Date and source every eligibility criterion, benefit rule, and compliance figure

**Status:** Absolute rule
**Domain:** Accuracy / grounding
**Applies to:** `hospice-referral-sales`

---

## Why this exists

LCDs are issued per Medicare Administrative Contractor and revised over time; benefit-period rules, per-diem rates, and nominal-value limits change; safe-harbor details are exact. A liaison who quotes a threshold or a rule from memory in front of a clinician or in a deliverable risks being wrong in a way that costs credibility (with a sophisticated source) or creates exposure (with a compliance figure). Every criterion, rule, and figure carries its source and date — or is marked example-until-confirmed.

## How to apply

**Do:**
- Cite the LCD / CMS rule / safe-harbor regulation and the date for any threshold or rule.
- Mark any unsourced number `[example — confirm against the current rule]`.
- Refresh the knowledge references when a rule, LCD, or regulation changes.
- Route a current-rule question to `ravenclaude-core` deep-researcher for live verification.

**Don't:**
- State an LCD threshold, per-diem, benefit-period detail, or compliance limit as a live fact without a source.
- Carry a remembered figure into a deliverable as if confirmed.
- Assume last year's rule still holds.

## Edge cases / when the rule does NOT apply

Stable structural facts (there are four levels of care; the benefit requires a six-month prognosis) are durable and need no per-use citation — the rule targets *volatile thresholds and figures* (specific LCD numbers, per-diem rates, nominal-value limits).

## See also
- [`../knowledge/hospice-eligibility-lcd-reference.md`](../knowledge/hospice-eligibility-lcd-reference.md)
- [`../knowledge/hospice-sales-compliance-reference.md`](../knowledge/hospice-sales-compliance-reference.md)

## Provenance

Codifies CLAUDE.md §3 #8 and the marketplace Claim-Grounding discipline.

---

_Last reviewed: 2026-06-05 by `claude`_
