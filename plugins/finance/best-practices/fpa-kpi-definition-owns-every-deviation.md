# Pin the KPI definition before reporting it, and own every deviation from the canonical form

**Status:** Absolute rule
**Domain:** FP&A / KPI governance
**Applies to:** `finance`

---

## Why this exists

The most common cause of "our ARR numbers don't match" is not bad data — it is two teams using slightly different definitions of the same metric. One team includes month-to-month contracts; the other excludes them. One team nets off discounts; the other does not. A KPI without a locked, written definition is an invitation for drift, and once two reports disagree the cost is not just a restatement — it is a credibility loss with the board or the lender reading both. The KPI definition IS the metric; without it you have a label on noise.

## How to apply

Every KPI that appears in a board pack, investor update, or management report must have a written definition with these six properties (drawn from the `kpi-definition` skill):

1. **Name** — the exact label used everywhere, with no synonyms.
2. **Formula** — explicit numerator / denominator / inclusion and exclusion rules.
3. **Frequency and reporting period** — monthly average? end-of-period snapshot?
4. **Canonical source** — which system, GL account, or dataset is authoritative.
5. **Owner** — who is responsible for computing and defending it.
6. **Version history** — when the definition changed and why (so prior periods are comparable).

When a deliverable must deviate from the canonical definition (e.g., pro forma ARR excluding a divested line), state the deviation explicitly in the deliverable:

> "ARR here is computed on the canonical definition in the KPI dictionary, *excluding* the divested Widgets business (effect: −$2.1M vs reported ARR). See KPI dictionary v3.1 for the standard definition."

**Do:**
- Store KPI definitions in a single, version-controlled dictionary (often a tab in the FP&A model or a shared doc with a version date).
- Force a definition review when the business model changes (new revenue type, acquisition, divestitures).
- Flag in every report when a metric shown is non-standard, and quantify the gap.

**Don't:**
- Allow the same metric name to carry different definitions in different reports without disclosure.
- Treat a definition change as backward-compatible — restate or disclose the break in the series.
- Let an analyst "fix" a metric for a specific output without logging the deviation.

## Edge cases / when the rule does NOT apply

Ad-hoc, one-time analysis for internal discussion (not a report shipped to stakeholders) can use working definitions as long as the document header says "draft / internal only — definitions not canonical."

## See also

- [`../agents/fpa-analyst.md`](../agents/fpa-analyst.md) — owns the KPI dictionary and variance-commentary discipline.
- [`../agents/board-pack-composer.md`](../agents/board-pack-composer.md) — must apply the canonical definitions when assembling the pack.
- [`./reconcile-before-you-narrate.md`](./reconcile-before-you-narrate.md) — the upstream gate: an unreconciled KPI never goes into commentary.

## Provenance

Codifies house opinion #8 ("one source of truth per metric") and the `kpi-definition` skill's six-property framework from CLAUDE.md §8. The SaaS canonical definitions (ARR/NRR/LTV-CAC) are grounded in the `kpi-definition` skill's canonical-SaaS-definitions section.

---

_Last reviewed: 2026-06-05 by `claude`_
