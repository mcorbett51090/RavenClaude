# A PBC Item Is Complete Only When Evidence Is Attached

**Status:** Absolute rule
**Domain:** Audit preparation
**Applies to:** `finance`

---

## Why this exists

The single most common cause of an extended audit timeline is a Provided-by-Client (PBC) item marked "complete" in the tracker that the auditor opens and finds contains an assertion rather than evidence — a description of the control instead of a sample of it working, a policy reference instead of a signed reconciliation, a "see controller" note instead of the actual document. Every iteration adds days to the timeline and signals a disorganized finance function. The PBC tracker is not a to-do list; it is an evidence-delivery mechanism. An item is not complete until the auditor can close it without a follow-up request.

## How to apply

Apply a two-criterion completion gate to every PBC item before marking it "Complete" in the tracker.

```
PBC Completion Gate — Both criteria must pass
──────────────────────────────────────────────
Criterion 1 — EVIDENCE ATTACHED:
  The file contains the actual document(s) the auditor needs,
  not a pointer, description, or cross-reference to another folder.
  For a control: the sample population + selected items + evidence of operation.
  For a balance: the signed reconciliation + source ledger tie + GL extract.
  For a policy: the approved policy document + last-approval sign-off date.

Criterion 2 — SELF-REVIEW COMPLETE:
  Someone other than the person who gathered the evidence reviewed it and:
  □ Confirmed the document covers the period requested.
  □ Confirmed the document shows what it is supposed to show.
  □ Confirmed the document is legible and complete (no cut-off pages, missing rows).
  □ Signed the review in the tracker (reviewer name + date).

Only then: update tracker status to "Complete" and deliver.
```

**Do:**
- Use a consistent folder structure: one subfolder per PBC item, named with the tracker item number.
- Deliver in the format the auditor requested — if they asked for Excel, don't send PDF.
- Include a brief transmittal note on complex items: "This is the AR reconciliation for Dec 31, 20XX, tied to GL account 1200."
- Track outstanding PBC items by age (days open) and escalate items older than 5 business days.

**Don't:**
- Mark an item "In Progress" as "Complete" to improve the tracker percentage — auditors track their own open requests independently and the discrepancy is immediately visible.
- Send a folder of 40 unlabeled files for a single PBC item — organize before delivering.
- Deliver a password-protected file without providing the password in a separate secure message.

## Edge cases / when the rule does NOT apply

- **Oral walkthroughs** — the auditor may accept a live demonstration as evidence for a specific control; document that the walkthrough occurred (date, attendees, control demonstrated) in the tracker note.
- **Items where the evidence has a legitimate legal hold or privilege restriction** — flag these proactively in the tracker with a note to your legal counsel and audit committee before the fieldwork window opens, not when the request arrives.

## See also

- [`../agents/audit-prep-specialist.md`](../agents/audit-prep-specialist.md) — owns the PBC tracker and the audit-prep process.
- [`./audit-controls-need-an-owner-frequency-and-evidence.md`](./audit-controls-need-an-owner-frequency-and-evidence.md) — the upstream rule; a control must have evidence of operation before that evidence can satisfy a PBC request.

## Provenance

Codifies the audit-prep-specialist's PBC-list discipline from the finance plugin's CLAUDE.md §1 and the `soc-control-walkthrough` skill. The two-criterion completion gate reflects standard public-accounting fieldwork practice and the finance plugin's house opinion #6 (audit trail in every workpaper).

---

_Last reviewed: 2026-06-05 by `claude`_
