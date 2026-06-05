# Show Prior-Year Development Separately From Current-Year Loss Ratio

**Status:** Absolute rule
**Domain:** Portfolio analytics / reserving
**Applies to:** `insurance-pc`

---

## Why this exists

Mixing current-year (accident-year) losses with prior-year development in a single incurred loss ratio obscures the quality of current-year underwriting. Adverse development on prior years — the emergence of losses above reserves on closed accident years — flows through the current calendar year's income statement, making a sound current-year book look worse than it is, and favorable development on prior years can paper over a deteriorating current-year book. An underwriting team that doesn't separate the two cannot know whether its current-year combined ratio reflects the effectiveness of its present pricing and risk selection or the inherited quality of prior underwriting. This distinction matters for management decisions, for reserve reviews, and for setting go-forward rate levels.

## How to apply

Report the calendar-year loss ratio with a prior-year development split in every management and board report.

```
Loss Ratio Presentation — With Prior-Year Development Split
──────────────────────────────────────────────────────────────
                            Current period (calendar year)
                            Total    | Current AY | Prior AY development
────────────────────────────────────────────────────────────
Incurred losses ($M)        $XXX.X   | $XXX.X     | +/– $XX.X  (favorable)/(adverse)
Earned premium ($M)         $XXX.X   |             |
────────────────────────────────────────────────────────────
Incurred loss ratio         XX.X%    | XX.X%      | +/– X.X pts

Commentary required:
  "Prior-year development of $X.X M ([favorable/adverse]) reflects
   [reserve strengthening on / release from] AY 20XX–20XX.
   Current accident-year loss ratio of XX.X% compares to a target
   of XX.X% and a prior-year AY loss ratio of XX.X% at equivalent
   development point."
```

**Do:**
- Track accident-year loss ratios to the same development point for a consistent YOY comparison (e.g., "AY 2025 at 12 months vs. AY 2024 at 12 months").
- Report the prior-year development by accident year when material — a blanket "prior years" line hides which accident years are sources of reserve uncertainty.
- For specialty or casualty lines with long development tails, show prior-year development as a multi-year exhibit, not a single line.

**Don't:**
- Report only the calendar-year combined ratio for an underwriting management discussion — it blends current-year performance with historical reserve actions.
- Present a calendar-year combined ratio that includes favorable prior-year development as evidence of "improving underwriting" — the two should be explicitly distinguished.
- Ignore prior-year development that appears consistently adverse across multiple years; it is a signal that the reserve selection process has a systematic bias.

## Edge cases / when the rule does NOT apply

- **Short-tail lines** (property, auto physical damage) with minimal prior-year development — the development amount may not be material enough to warrant a separate line; disclose the immateriality and the threshold.
- **External financial reporting** governed by GAAP/STAT conventions — the statutory and GAAP statements follow their own formats; this rule governs the management-reporting layer above the statutory statements, not the statements themselves.

## See also

- [`../agents/actuarial-pricing-analyst.md`](../agents/actuarial-pricing-analyst.md) — owns the accident-year vs. calendar-year loss analysis.
- [`./reserve-adequacy-is-the-truth-teller.md`](./reserve-adequacy-is-the-truth-teller.md) — prior-year development is the empirical test of whether prior reserves were adequate; consistent adverse development is the failure signal.

## Provenance

Codifies the actuarial-pricing-analyst's prior-year development reporting discipline from the insurance-pc plugin's CLAUDE.md §3 #5 (reserve adequacy is the truth-teller) and §3 #3 (separate frequency from severity). The accident-year vs. calendar-year split is standard P&C carrier management reporting practice (NAIC, CAS, and carrier internal reporting conventions).

---

_Last reviewed: 2026-06-05 by `claude`_
