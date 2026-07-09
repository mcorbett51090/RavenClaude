# TODO — FIPA Dispatch Analysis: other filing-extract flows not being triggered

> **Status:** OPEN — captured 2026-06-25 as a durable to-do (not yet investigated).
> **Why this file exists:** preserving the full investigation brief so it survives across
> sessions and can't be overwritten/lost. See [[feedback_no_overwrite_redo_work]] (memory).

## Context
Filing extraction pipeline: Contoso Insight Power Platform app
Flow: `FilingIntake-Process-Action-MultiSubmission` (FIPA)
FIPA ID (DEV): `332049b0-ca53-f111-bec7-7ced8d663e7c`
Draft: `src/flows-draft/ContosoReporting/FilingIntake-Process-Action-MultiSubmission.json`
DEV env: `https://contosodev.crm3.dynamics.com`

## Symptom
Only BS (Balance Sheet) and IS (Income Statement) extractor flows are being triggered.
AR (Auditor's Report), CF (Cash Flow), LIQ (Liquidity Analysis), AML, ARF, ARI extractors
are not being triggered even when the classifier identifies those filing types.

## Known issues already fixed
- IS extractor was stuck on `Call_IS_Extractor_Existing` step (live portal has step that
  was removed from draft; fix: portal delete of that step — NOT YET DONE, still outstanding)
- Both BS and IS extractors had `Sort_ByLen` null-guard bug — FIXED 2026-06-25
- FIPA draft shows all branches but live portal version may differ

## Key questions for investigation

### Q1: Does the live FIPA actually have branches for all filing types?
The draft (`FilingIntake-Process-Action-MultiSubmission.json`) should show all branches.
Check: does the live portal FIPA (fetch via Dataverse `workflows({id})?$select=clientdata`)
have action branches for AR, CF, LIQ, AML, ARF, ARI or only BS and IS?

Command to fetch live FIPA:
```
GET https://contosodev.crm3.dynamics.com/api/data/v9.2/workflows(332049b0-ca53-f111-bec7-7ced8d663e7c)?$select=clientdata,name
```

### Q2: Is the classifier correctly identifying multi-filing submissions?
The classifier flow (`FilingTypeClassifier-Trigger`) reads the document and sets
`contoso_filingtype` and `contoso_ismultisubmission`. If it's not identifying AR/CF/LIQ sections,
FIPA won't dispatch those extractors.

Check: `contoso_filingintakes` records — what is `contoso_filingtype` and `contoso_classifiedsections`
on a recent run that was expected to have multiple filing types?

### Q3: MULTI_SUB_SECTIONS entity sets
The UI queries these entity sets for section records:
- BS:  `contoso_balancesheets` (filter: `contoso_filingintakeid`)
- IS:  `contoso_incomestatements` (filter: `contoso_filingintakeid`)
- CF:  `contoso_cashflows` (filter: `contoso_filingintakeid`)
- LIQ: `contoso_liquidityanalysises` (filter: `contoso_filingintakeid`)
- AR:  `contoso_auditorsreports` (filter: `contoso_filingintakeid`)

Are records being created in CF/LIQ/AR entity sets for any intake?

### Q4: AR outstanding schema issue
AR extractor has a known open issue (AR-7 from architecture-tracker.md):
`contoso_auditorsreport` is missing the `contoso_filingintakeid` lookup column.
Without this FK, FIPA cannot create or link AR records, and the AR extractor
cannot be filtered by intake. This may be blocking AR entirely.

### Q5: Connection reference
All extractor flows bind to `contoso_sharedcommondataserviceforapps_spn`.
If CF/LIQ/AR extractor flows are OFF (disabled) in DEV, FIPA will fail silently
when trying to call them as child flows.

Check flow states:
```
GET contosodev.crm3.dynamics.com/api/data/v9.2/workflows?$filter=category eq 5 and statecode eq 0
    &$select=name,statecode,statuscode
```

## Flow IDs (DEV)
- FIPA:          332049b0-ca53-f111-bec7-7ced8d663e7c
- BS extractor:  e12231ff-dc65-f111-ab0c-7ced8da7387a
- IS extractor:  5d6ab7fe-dc65-f111-ab0c-7ced8da73e16
- AR extractor:  dd406aed-b34f-f111-bec7-6045bd5c8504
- CF extractor:  1c6a53a9-1170-f111-ab0f-7ced8ddfba57  ← was noted as OFF in checkpoint
- LIQ extractor: a56f1c38-4670-f111-ab0f-7ced8ddfba57

## Recommended investigation steps (in priority order)
1. Fetch live FIPA clientdata → map all action branches → confirm AR/CF/LIQ branches exist
2. Check statecode of CF/LIQ/AR extractor flows — if OFF, activate them
3. Check a recent failed/processed intake → what does `contoso_classifiedsections` contain?
4. Confirm AR-7 (contoso_filingintakeid FK on contoso_auditorsreport) status
5. Check if FIPA live version still has `Call_IS_Extractor_Existing` in IS FALSE-branch

## Draft file location
`src/flows-draft/ContosoReporting/FilingIntake-Process-Action-MultiSubmission.json`
