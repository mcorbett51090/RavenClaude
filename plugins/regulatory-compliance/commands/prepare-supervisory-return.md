---
description: Prepare a regulatory return that survives an exam — scope the regime first, source-trace every load-bearing cell to a reproducible lineage, explain every material variance vs prior period before submission, fix bad data at the source not in the return, and run a genuine two-person maker-checker chain.
argument-hint: "[the return + regime, e.g. 'BMA EBS return for a Bermuda reinsurer' or 'FATCA filing']"
---

# Prepare a supervisory return

You are running `/regulatory-compliance:prepare-supervisory-return`. Prepare (or pre-submission review) the regulatory return the user described (`$ARGUMENTS`), following this plugin's `regulatory-reporting-analyst` discipline. A return value you cannot reproduce will not survive an exam.

## When to use this

Period-end filing prep or a pre-submission review for a supervisory return (FATCA, CRS, BMA EBS, Solvency II, RBC, statutory). Not for fixing the upstream accounting itself (route source-data quality issues to the `finance` controller) and not for whether a restatement triggers a legal disclosure obligation (counsel).

## Steps

1. **Scope the jurisdiction and regime first** (`scope-the-jurisdiction-before-you-map`): name the regulator + regime so each threshold word and materiality definition is applied in-scope; route BMA/Bermuda matters to `bermuda-insurance-specialist`. BMA "material" is not NAIC "material" is not Solvency II "material."
2. **Source-trace every load-bearing cell** (`filing-source-trace-every-load-bearing-cell`): capture full lineage — source system + account + period, extract timestamp + query, every transform (FX, mapping, statutory-vs-GAAP adjustment), and the destination cell with workbook version — so a second person could re-derive the value. Re-verify any rolled-forward number against the current source; last period's reconciliation does not re-verify this period.
3. **Explain every material variance vs prior period before you submit** (`filing-explain-the-variance-before-you-submit`): diff line-by-line against prior, attach a business/methodology reason to every material movement, and treat an unexplainable variance as a source-error candidate — not "noise to flag later."
4. **Fix the source, not the return** (`filing-fix-the-source-not-the-return`): when lineage reveals bad data, correct the system of record and let it flow through, or disclose the limitation and raise it to the controller — never an undisclosed in-return plug. A discovered prior-period error is a formal amendment/restatement, not a silent re-upload.
5. **Run a genuine two-person maker-checker** (`filing-maker-checker-is-two-people`): preparer and reviewer are different named people, both signing in writing, with the checker independently re-walking the lineage and the variance explanations — plus a pre-submission walkthrough by someone outside the prep team for material returns.

## Guardrails

- One person signing both maker and checker lines is no control — document a compensating control if segregation is genuinely constrained, never waive it silently.
- Legitimate documented adjustments (statutory-vs-GAAP, admitted-vs-non-admitted, eliminations) belong in the transform step with their basis recorded — they are methodology, not hidden plugs.
- Cite the regulator's primary source (section + subsection + paragraph), not a summary; route any customer PII handling through `ravenclaude-core/security-reviewer`.
