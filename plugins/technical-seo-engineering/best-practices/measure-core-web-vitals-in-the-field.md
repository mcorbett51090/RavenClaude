# Measure Core Web Vitals in the field, at the 75th percentile

**Status:** Absolute rule
**Domain:** Page experience as a ranking input
**Applies to:** `technical-seo-engineering`

---

## Why this exists

Core Web Vitals affect ranking through **field data** — real users, measured over a ~28-day window (CrUX), assessed at the **75th percentile**. A Lighthouse / PageSpeed lab score is a **diagnostic**: it runs once, on one simulated device and network, and is invaluable for *reproducing and debugging* a problem — but it is **not** the ranking input. A page can score 95 in the lab and still fail the field assessment because real users are on slower devices and networks. Optimizing to the lab score while ignoring the field report is optimizing the wrong number.

A second perishable fact: the **metric set itself changed** — **INP replaced FID** in 2024. Quoting FID (or its threshold) dates the analysis and gives a wrong answer.

## How to apply

**Do:**
- Judge CWV against the **Search Console Core Web Vitals report / CrUX** field data at the **75th percentile**.
- Use Lighthouse/PageSpeed to *reproduce and diagnose*, then confirm the fix landed in the **field** report (allow for the ~28-day trailing window).
- Diagnose **LCP / INP / CLS** as the three current metrics.

**Don't:**
- Declare CWV "fixed" from a green lab score alone.
- Quote **FID** — it's been replaced by INP.
- Quote a threshold value without re-verifying it (they have changed).

## Edge cases / when the rule does NOT apply

- **A brand-new page / low-traffic URL** may have no field data yet — fall back to lab as a *provisional* signal, and say so explicitly; the field data is what will ultimately count.

## See also

- [`../knowledge/technical-seo-engineering-reference-2026.md`](../knowledge/technical-seo-engineering-reference-2026.md) — the dated thresholds and the FID→INP change (re-verify).
- [`../skills/optimize-core-web-vitals/SKILL.md`](../skills/optimize-core-web-vitals/SKILL.md).

## Provenance

Codifies the `core-web-vitals-engineer` house opinion "a perfect Lighthouse score with failing field data is a failing page." Grounded in web.dev Core Web Vitals documentation and Google Search Central page-experience guidance, retrieved 2026-06-25 — re-verify the thresholds and metric set before quoting.

---

_Last reviewed: 2026-06-25 by `claude`_
