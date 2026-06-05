# Issue Log — Every RFI Response and Every O/C in One Place

**Status:** Pattern
**Domain:** Architecture/AEC
**Applies to:** `architecture-aec`

---

## Why this exists

RFI responses scattered across email threads and change-order directives filed in separate folders are the document management pattern that produces claims. An architect who cannot quickly produce "RFI #47 — issued date, response date, response content, change-order status" during a dispute is disadvantaged. The issue log is not a bureaucratic overhead; it is the project's single version of truth for field coordination, and it makes the CA record auditable at contract closeout.

## How to apply

Maintain a single issue log for every project from the first CA kick-off through substantial completion:

```
Project Issue Log
──────────────────
Project:  ________________

| # | Type | Date Issued | Issued By | Subject | Date Responded | Response Summary | O/C? | O/C # | Status |
|---|------|-------------|-----------|---------|----------------|-----------------|------|-------|--------|
| 1 | RFI  |             |           |         |                |                 |      |       | Open / Closed |
| 2 | PR   |             |           |         |                |                 |      |       |        |
| 3 | ASI  |             |           |         |                |                 |      |       |        |

Types: RFI (Request for Information), PR (Proposal Request), ASI (Architect's Supplemental Instruction), PCO (Potential Change Order), O/C (Owner's Change)
```

**Do:**
- Enter every RFI within 24 hours of receipt; close it within 24 hours of response.
- Link RFI responses to any resulting change-order paperwork — the chain RFI → PCO → O/C is the cost audit trail.
- Review the issue-log weekly with the contractor during CA; log-velocity is a leading indicator of document coordination quality.

**Don't:**
- Let any RFI age past seven days without a response or a documented request for extension — unanswered RFIs are a contractor's schedule-impact claim in the making.
- File RFI responses separately from the log; the log is the index, and the responses are the records behind it.
- Close an RFI as "answered" when the answer was "see drawing revision" without logging the revision number and date.

## Edge cases / when the rule does NOT apply

Design-phase clarifications (during SD/DD) are tracked on the project issue log as design decisions, not RFIs, but the same logging discipline applies. The RFI format is specifically a construction administration instrument.

## See also

- [`../agents/construction-documents-specialist.md`](../agents/construction-documents-specialist.md) — owns RFI/change-order management and the issue log.
- [`./rfis-and-change-orders-are-a-coordination-signal-not-just-pa.md`](./rfis-and-change-orders-are-a-coordination-signal-not-just-pa.md) — the governing rule on reading RFI patterns as a coordination quality signal.

## Provenance

Codifies CLAUDE.md §3 #3 (RFIs and change orders are a coordination signal, not just paperwork) with a specific issue-log instrument. Issue-log discipline during CA is a standard AIA and NCARB construction administration practice requirement [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
