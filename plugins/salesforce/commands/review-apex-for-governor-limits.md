---
description: Audit Apex (a class, trigger, or the current diff) for governor-limit defects — SOQL/DML in loops, non-selective queries, missing bulkification, recursion, and CRUD/FLS gaps — and propose concrete fixes ranked by severity.
argument-hint: "[class/trigger name or path; omit for the current diff]"
---

# Review Apex for governor limits

You are running `/salesforce:review-apex-for-governor-limits`. Audit the Apex the user named (`$ARGUMENTS`) — or the current working diff if none — for the governor-limit and security defects this plugin's `salesforce-reviewer` and `apex-engineer` care about most. Report findings ranked by severity with the fix for each.

## When to use this

Before deploying Apex, or when an org hits "Too many SOQL queries: 101" / "Apex CPU time limit exceeded" / row-lock errors. Also good as a pre-PR self-review.

## Steps

1. **Read the target** (`$ARGUMENTS` if given; else the diff).
2. Scan for the defect classes, each citing the backing best-practice:
   - **SOQL/DML in a loop** (`apex-soql-in-loops-is-a-defect`, `bulkify-every-soql-and-dml`) — the #1 cause of limit blowups. P0.
   - **Non-selective SOQL** — filters not on indexed fields, no `LIMIT`, full-table scans (`apex-query-selectively-with-indexes`, `data-selective-soql-on-indexed-fields`). P1.
   - **Missing recursion control** on trigger handlers (`apex-recursion-control-on-handlers`). P1.
   - **Per-record lookups** that should be Map-based O(1) (`apex-collections-and-maps-for-o1-lookups`). P1.
   - **CRUD/FLS not enforced**, missing `with sharing` (`enforce-sharing-and-crud-fls`). P0 (security).
   - **Dynamic SOQL without bind variables** — injection risk (`apex-bind-variables-in-dynamic-soql`). P0 (security).
   - **Large result sets** that should be Batch Apex (`data-batch-apex-for-large-result-sets`). P2.
   - **Tests** using `SeeAllData` or no bulk (200-record) assertion (`apex-test-data-with-testfactory-not-seealldata`). P1.
3. For each finding: file:line, the defect, the one-line fix, and the best-practice it violates.
4. Offer to apply the mechanical fixes (loop-hoisting a query into a pre-loop Map, adding `LIMIT`, wrapping in CRUD checks) on request.

## Guardrails

- Don't rewrite working logic for style; flag only genuine limit/security defects.
- A P0 (security or guaranteed limit blowup) blocks; a P2 is advisory.
- If the code is actually fine, say so plainly — don't manufacture findings.
