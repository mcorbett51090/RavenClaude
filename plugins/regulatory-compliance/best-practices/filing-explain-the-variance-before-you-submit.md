# Explain every material variance vs prior period before you submit

**Status:** Absolute rule
**Domain:** Regulatory reporting — pre-submission review
**Applies to:** `regulatory-compliance`

---

## Why this exists

The regulator reads this period's return next to last period's — and so should the firm, before it submits. A material movement at the line level that the firm cannot explain is the single most common opening question in a return review, because an unexplained variance is either a real business change the firm should be able to articulate or an error the firm hasn't caught. Submitting first and explaining later inverts the order: the explanation should be in hand *before* the file goes in, line by line, so the firm controls the narrative instead of reacting to the examiner's. An unexplained material variance is a plugin-wide flagged anti-pattern; it is also frequently the first symptom of a bad source cell that the fix-the-source discipline should have caught.

## How to apply

Run a line-level diff against the prior period and attach an explanation to every material movement before sign-off:

```
Schedule + line     the cell that moved
Prior / current     both values + the variance (absolute + %)
Material?            against the regime's materiality definition  [verify-at-build — materiality is regulator-specific]
Explanation         the business/methodology reason (new book, FX, assumption change, one-off)
Cross-check         does the variance reconcile to a known driver, or does it signal a source error?
```

A variance you cannot explain is not "noise to flag later" — it is a stop-and-investigate before submission, because the explanation you can't write is often a source cell you got wrong.

**Do:**
- Diff this period against prior at the line level and explain every material movement before sign-off.
- State which regime's materiality definition sets the "material" bar (house opinion #7, #12).
- Treat an unexplainable variance as a source-error candidate and route it to the fix-the-source path, not an in-return plug.

**Don't:**
- Submit with material variances unexplained and plan to answer if asked — the explanation belongs in the workpaper now.
- Apply one materiality definition across regimes — BMA "material" ≠ NAIC "material" ≠ Solvency II "material."
- Confuse "explained" with "explained away" — the explanation must reconcile to a real driver.

## Edge cases / when the rule does NOT apply

- **First-ever filing** for a new entity has no prior period to diff — variance review is replaced by a reasonableness review against the business plan / opening balances.
- **Restructured returns** (a schema change that re-maps lines) need a bridge from old line to new line before a variance is even meaningful — explain the re-mapping first.
- **Legal-opinion gate** — if a variance stems from a disputed accounting or legal position, the position routes to counsel/technical accounting; the variance documentation continues.

## See also

- [`./filing-source-trace-every-load-bearing-cell.md`](./filing-source-trace-every-load-bearing-cell.md) — the lineage that lets you explain a variance.
- [`./filing-fix-the-source-not-the-return.md`](./filing-fix-the-source-not-the-return.md) — where an unexplained variance routes when it's a source error.
- [`../agents/regulatory-reporting-analyst.md`](../agents/regulatory-reporting-analyst.md) — "Diff vs prior period explained. Material changes vs prior period are explained at the line level before submission."

## Provenance

Codifies the `regulatory-reporting-analyst` opinions "Diff vs prior period explained" and "Materiality is regulator-specific," and the anti-pattern "filing with material variances from prior period that aren't explained" ([`../agents/regulatory-reporting-analyst.md`](../agents/regulatory-reporting-analyst.md)), plus house opinions #7 (materiality in writing) and #12 (jurisdiction matters) in [`../CLAUDE.md`](../CLAUDE.md) §3.

---

_Last reviewed: 2026-05-30 by `claude`_
