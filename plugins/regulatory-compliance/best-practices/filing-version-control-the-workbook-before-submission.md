# Version-Control the Filing Workbook Before Submission

**Status:** Absolute rule
**Domain:** Regulatory filing / reporting
**Applies to:** `regulatory-compliance`

---

## Why this exists

A regulatory return submitted to a regulator cannot be unsent. If a post-submission error is found in the source workbook, the firm must determine what was actually submitted — which requires knowing the exact state of the file at the time of submission. Firms that overwrite the pre-submission workbook lose the ability to compare what was submitted to what the corrected file shows, which is precisely what the regulator needs for a restatement discussion. Version control on a filing workbook is a compliance-audit discipline, not an IT convention.

## How to apply

Apply a version stamp and save-as discipline to the filing workbook at three mandatory checkpoints.

```
Filing Workbook Version-Control Checkpoints
──────────────────────────────────────────────────────
CHECKPOINT 1 — After maker completes draft (pre-checker review)
  Filename: <ReturnName>_<Period>_DRAFT_<YYYYMMDD>_<MakerInitials>.xlsx
  Action: Save a read-only copy before handing to checker.
  Tab: Add a "Version" tab with: maker name, date, data sources cited (per
       filing-source-trace-every-load-bearing-cell.md).

CHECKPOINT 2 — After checker review and sign-off (pre-submission)
  Filename: <ReturnName>_<Period>_FINAL_<YYYYMMDD>.xlsx
  Action: Lock inputs; save a new copy; do NOT overwrite the DRAFT copy.
  Tab: Add checker name, date, and "approved for submission" to the Version tab.

CHECKPOINT 3 — Immediately after submission
  Filename: <ReturnName>_<Period>_SUBMITTED_<YYYYMMDD>.xlsx
  Action: Add the submission confirmation number / regulator receipt to the Version tab.
  Retain: Store the SUBMITTED version separately from the working files.
          Rename it with "_SUBMITTED" suffix and archive it.

Post-submission retention:
  Keep the DRAFT, FINAL, and SUBMITTED versions for the full retention period.
  The SUBMITTED version is the legal record; don't delete it when a new period opens.
```

**Do:**
- Run the version-control discipline even for returns submitted through a portal — save a copy of the populated workbook before uploading; the portal may not provide a downloadable copy of what was submitted.
- For portal submissions, capture a screenshot of the submission-confirmation page and attach it to the SUBMITTED version record.
- For XML or XBRL submissions, keep the generated file alongside the source workbook.

**Don't:**
- Overwrite the pre-submission file with post-period corrections — create a new version with a clear "POST-SUBMISSION AMENDMENT" label.
- Rely on email trails as the sole version record; email is not archived to the same retention standards as the filing workbooks.
- Treat the FINAL copy as the permanent record; the SUBMITTED version (after confirmation) is the record because it reflects exactly what was transmitted.

## Edge cases / when the rule does NOT apply

- **Systems-generated electronic filings** (e.g., a core-banking system that constructs and submits the return programmatically) — the system's audit log substitutes for the file versioning; verify that the audit log captures the version and the submission timestamp.
- **Immaterial corrections discovered before the regulator opens the return** — still create a SUBMITTED_CORRECTED version; the discipline is the same.

## See also

- [`../agents/regulatory-reporting-analyst.md`](../agents/regulatory-reporting-analyst.md) — owns filing preparation and version discipline.
- [`./filing-maker-checker-is-two-people.md`](./filing-maker-checker-is-two-people.md) — the maker-checker control assumes the DRAFT and FINAL are distinct files; this rule makes that operationally concrete.

## Provenance

Codifies the regulatory-reporting-analyst's filing version-control discipline, extending CLAUDE.md §3 #6 ("default to written") and the `supervisory-return-prep` skill's pre-submission checklist. The three-checkpoint structure reflects standard filing governance practice across BMA, CIMA, and SEC regulatory submission contexts.

---

_Last reviewed: 2026-06-05 by `claude`_
