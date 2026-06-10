<!-- RAVENCLAUDE-STAGING-METADATA
type: lesson
topic: power-platform
proposed-by: consumer engagement — a regulatory-compliance risk-scoring PBIP model (Copilot CLI session)
proposed-on: 2026-06-09
target-file: plugins/power-platform/knowledge/pbip-duplicated-constants-dax-and-mquery.md
status: pending
-->

## 2026-06-09 — A business constant duplicated across a DAX measure AND an M-query column must change as a pair

**Context:** In a regulatory-compliance scoring PBIP model, domain weights (illustrative example values: Client Money 40, Directorship 35, Nominee 25) drive both model-level domain scores and question-level contribution scores.

**What we tried first:** Updated the weights only in the DAX layer — the `_Measures.tmdl` constants (e.g. `measure 'Client Money Domain Weight' = 40`, …) and the hardcoded multipliers inside `Applicable Ceiling`, each `Domain Score` measure, and `Question Scope Score Contribution`.

**Why it failed:** The same weights are ALSO encoded a second time in `Questions.tmdl` as a Power Query (M) computed column — `Domain_Weight` (`if [Category_Number] = 5 then 35 ... else 40`). That column feeds `Question Weighted Score` and every question-level contribution measure. Updating only the DAX side leaves the M-query column on the OLD weights — and nothing errors: the model loads cleanly and the question-level numbers are silently wrong. This is the same failure family as the existing silent-zero / silent-blank scoring lessons, but the duplication spans the **DAX layer and the M (load) layer**, so a measures-only search never reveals the second copy.

**What works:** Treat the constant as living in TWO independent source-of-truth locations and change both together: (1) the DAX constants + multipliers in `_Measures.tmdl`, and (2) the `Domain_Weight` M-query column in `Questions.tmdl`. After any weight change, verify the **question-level** score measures (not just the domain-level ones) against an expected value — that's the surface that exposes the drift.

**How to apply:**
- Before changing any scoring/business constant in a PBIP model, grep BOTH the TMDL measures AND the M-query (`*.tmdl` partition / Power Query) columns for the value — a constant computed in Power Query won't appear in a measures-only search.
- Add a verification step that asserts a known question-level score after a weight change; a silently stale duplicate shows up there, not at the domain level.

**Trace:** Consumer PBIP scoring engagement (generalized; client/project identifiers removed). The specific weights/category numbers are illustrative. Companion to the power-platform knowledge files `pbir-m-query-pitfalls.md` (load-stage silent data loss) and `pbir-dax-pitfalls.md` / `dax-category-name-mismatch-zero-scores.md` (silent-zero scoring). The general rule — a duplicated constant across the DAX and M layers drifts silently — applies to any PBIP model, not just scoring.
