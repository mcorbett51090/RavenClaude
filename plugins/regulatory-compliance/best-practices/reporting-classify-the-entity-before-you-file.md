# Classify the entity before you file — the classification decides the return

**Status:** Absolute rule — filing the wrong return, or the right return on a wrong entity classification, is a reportable error; the classification is the upstream decision, not a field on the form.

**Domain:** Regulatory reporting

**Applies to:** `regulatory-compliance`

---

## Why this exists

The `filing-*` rules cover filing *hygiene* (variance explanation, fix-the-source, maker-checker, source-trace) — but they all assume you already know **which return applies**, and that depends on **how the entity is classified**. For information-reporting regimes (FATCA / CRS) the entity's classification — Reporting Financial Institution vs Non-Financial Entity, active vs passive NFE — determines which return family is even owed and what must be reported. Get the classification wrong and every downstream filing is wrong no matter how clean the data. This rule puts the classification *before* the filing, where it belongs.

## How to apply

**Classify the entity first, then select the return:**

1. **Determine the entity's status under each applicable regime** before mapping any data:
   - FATCA/CRS: is it a **Financial Institution** (depository, custodial, investment entity, specified insurance) or a **Non-Financial Entity**? If NFE, **active or passive**? Passive NFEs require look-through to controlling persons.
   - Supervisory/prudential returns: which **return family** the entity's licence/class triggers.
2. **Document the classification basis** — the test applied and the evidence — because it's the assumption every filing inherits and the first thing an examiner challenges.
3. **Then** select the return and apply the `filing-*` hygiene rules (source-trace, maker-checker, variance).
4. **Re-test on a triggering change** — a new business line, a licence change, or crossing a threshold can reclassify the entity and change what's owed.

**Do:** classify under each regime before touching the data; document the test + evidence; look through passive NFEs to controlling persons; re-test on a triggering event.

**Don't:** start from "the return we filed last year" and assume the classification still holds; treat classification as a checkbox on the form; file a supervisory return without confirming the entity's class triggers it.

## Edge cases / when the rule does NOT apply

A single-regime entity with a long-stable, documented classification and no triggering changes may proceed straight to the filing rules — the classification step is fast when nothing changed (but still confirm "nothing changed"). Specific FATCA/CRS category definitions, thresholds, and the supervisory return-family mappings are **jurisdiction- and version-specific** — `[verify-at-build]`; never hard-code a threshold or category from memory.

## See also

- [`./filing-source-trace-every-load-bearing-cell.md`](./filing-source-trace-every-load-bearing-cell.md) — the hygiene rules that apply *after* the return is selected
- [`./filing-maker-checker-is-two-people.md`](./filing-maker-checker-is-two-people.md) · [`./filing-explain-the-variance-before-you-submit.md`](./filing-explain-the-variance-before-you-submit.md)
- [`./scope-the-jurisdiction-before-you-map.md`](./scope-the-jurisdiction-before-you-map.md) — the parallel "scope before you map" discipline
- [`../agents/regulatory-reporting-analyst.md`](../agents/regulatory-reporting-analyst.md) — owns reporting classification
- FATCA/CRS guidance + the entity's supervisory framework — authoritative (`[verify-at-build]` thresholds/categories)

## Provenance

Surfaced by the two-panel + tiebreak coverage campaign (2026-06-01): the `regulatory-reporting-analyst` had four filing-hygiene rules but none covered the upstream entity-classification that decides *which* return applies. Grounded in FATCA/CRS classification frameworks. Categories/thresholds are `[verify-at-build]`. (The matching which-return *tree* is deferred to the campaign's tree batch.)

---

_Last reviewed: 2026-06-01 by `claude`_
