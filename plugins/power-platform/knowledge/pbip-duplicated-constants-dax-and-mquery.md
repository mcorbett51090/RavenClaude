# A business constant duplicated across a DAX measure AND an M-query column must change as a pair

> **Last reviewed:** 2026-09-11. Source: consumer engagement with a regulatory-compliance risk-scoring PBIP model, 2026-06-09 (Copilot CLI session; client/project identifiers removed). The domain names and weight values below are illustrative — re-derive the analogous constants for your own model rather than treating these as fixed.
>
> **When to read this file.** You're about to change a scoring weight, threshold, or any other business constant in a PBIP model, and you're tempted to search only the DAX measures (`_Measures.tmdl`) for it. Read this first — the same constant can be duplicated a second time as a Power Query (M) computed column, and a measures-only search will never surface that copy.

---

## The failure

In a scoring model, domain weights (illustrative values: Client Money 40, Directorship 35, Nominee 25) drove both model-level domain scores and question-level contribution scores. An engineer updated the weights in the DAX layer only — the `_Measures.tmdl` constants (e.g. `measure 'Client Money Domain Weight' = 40`) and the hardcoded multipliers inside `Applicable Ceiling`, each `Domain Score` measure, and `Question Scope Score Contribution`.

The same weights were **also** encoded a second time in `Questions.tmdl`, as a Power Query (M) computed column — `Domain_Weight` (`if [Category_Number] = 5 then 35 ... else 40`). That column fed `Question Weighted Score` and every question-level contribution measure. Updating only the DAX side left the M-query column on the old weights — and nothing errored. The model loaded cleanly. The question-level numbers were silently wrong while the domain-level numbers were correct, which made the bug harder to notice: a spot-check at the domain level looked fine.

This is the same failure family as the silent-zero / silent-blank scoring lessons in [`dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md) — a change that looks complete produces a model that loads and renders normally but computes the wrong number with no surfaced error. What makes this variant distinct: the duplication spans **two different layers** (the DAX measure layer and the M/Power-Query load layer), so a search strategy that only covers one of them will miss the other copy entirely. A reviewer checking `_Measures.tmdl` has no reason to expect the same constant is also live inside a `Questions.tmdl` computed column.

## What works

Treat the constant as living in **two independent source-of-truth locations**, and change both together:

1. The DAX constants and multipliers in `_Measures.tmdl`.
2. The `Domain_Weight` (or equivalently-named) M-query computed column in the relevant dimension table's `.tmdl` (here, `Questions.tmdl`).

After any weight change, verify the **question-level** score measures specifically, not just the domain-level ones — the question level is the surface that exposes the drift, because that's the layer still reading the stale M-query column.

## How to apply

- Before changing any scoring or business constant in a PBIP model, grep **both** the TMDL measures **and** the M-query (Power Query) partitions/columns for the value. A constant computed in Power Query will not appear in a measures-only search, and vice versa.
- Add a verification step that asserts a known question-level score after a weight change. A silently stale duplicate shows up there first, not at the domain level — don't treat a correct domain-level spot-check as proof the change is complete.
- For any newly-authored model, prefer a **single shared source of truth** for a constant used in both layers over duplicating it: a small reference table (one row per domain/category, one weight column) that both the DAX measures and the M-query column look up via `RELATED()` / `LOOKUPVALUE()`, rather than hardcoding the same value twice in two different languages. A shared reference table removes the *duplicate-copy* shape of this bug at the source, though verification after any change is still worth doing.
- When the constant also has a scale convention (fractional 0–1 vs. absolute 0–100), check that convention is consistent across both layers too — a scale mismatch introduced in only one of the two copies is the same silent-drift shape as a value mismatch, see [`dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md#fix-c--score-scale-gotcha--100-if-category_weight-is-fractional) (FIX C) for the scale-specific variant of this same "both sides must move together" rule.

## Edge cases / scope of this rule

- A model authored with a shared dimension/reference table, consumed by reference (`RELATED()`/`LOOKUPVALUE()`) from both the DAX and M layers, has only one copy of the constant to change — the structural fix recommended above addresses this case by construction.
- A constant that only ever appears in one layer (DAX-only, or M-query-only) has no second copy to drift out of sync — the risk this lesson describes is specific to a constant duplicated across both layers.

## See also

- [`pbir-m-query-pitfalls.md`](pbir-m-query-pitfalls.md) — other silent-data-loss shapes at the M/load stage; this lesson is a silent-*drift* shape rather than data loss, but lives at the same layer.
- [`pbir-dax-pitfalls.md`](pbir-dax-pitfalls.md) — other silent-blank/silent-zero DAX measure-design pitfalls.
- [`dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md) — the companion silent-zero-score lesson (hardcoded string filters, not duplicated constants) and the score-scale gotcha this lesson's scale note points back to.

## Provenance

Consumer PBIP scoring engagement, 2026-06-09: domain weights changed in the DAX layer only; the same weights were separately encoded in a Power Query computed column that went unnoticed and stayed stale, producing correct domain-level scores and silently wrong question-level scores. Generalized; client/project identifiers removed, weights and category numbers are illustrative. Revised 2026-09-11 during promotion from staging to add the shared-reference-table structural recommendation and the explicit cross-link to the score-scale variant of the same rule.

---

_Last reviewed: 2026-09-11 by consumer-project session_
