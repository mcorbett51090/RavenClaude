---
name: submittals-rfis-change-orders
description: "Manage the GC's submittal register (identify required submittals, set lead-time-driven due dates, track review status), draft and track RFIs (structured question format, response tracking, overdue escalation), and document change orders (CO pricing coordination, package assembly, CO log maintenance). The three processes are connected: RFIs clarify design, submittals confirm procurement, and COs pay for scope changes."
---

# Submittals, RFIs, and Change Orders

**Purpose:** keep the project's document flow moving so field work is never blocked by an
unanswered question, an un-approved submittal, or an undocumented change.

---

## Part 1 — Submittal Register

### Setup (Day 1–2 of project)

1. Read every specification section. Pull required submittals from Part 1 (General) of each
   section — the "Submittals" paragraph.
2. Build the register: spec section | submittal type (shop drawing / product data / sample /
   test report) | responsible sub | target submission date | required approval date | need-on-site.
3. Set the required approval date by working backward from need-on-site:
   `need-on-site − delivery/fabrication lead time − review period (per contract, typically 14–21
   days for shop drawings) − GC review (5 days) = submit by date`.
4. Sequence submittals by procurement lead time — long-lead MEP equipment (12–20 weeks) first,
   commodity materials (2–4 weeks) last.

### Tracking (weekly)

- Update status after every transmittal and every returned action.
- Flag: submitted but approaching review deadline (no response coming?), Revise-and-Resubmit
  (how long will the correction take?), approved but sub hasn't ordered yet.
- Integrate with the CPM: if a submittal's approval will be late, the schedule engineer needs
  to know now.

### Submittal actions (typical)

| Action | Meaning | Next step |
|---|---|---|
| Approved (A) | Fabricate / procure as submitted | Issue to sub; file |
| Approved as Noted (AN) | Minor comments; acceptable | Route comments to sub; order can proceed |
| Revise and Resubmit (RR) | Significant comments; do not proceed | Sub corrects; resubmit; reset clock |
| Rejected (R) | Does not comply with contract | Sub provides alternative; resubmit |

---

## Part 2 — RFIs

### When to write an RFI

- Drawing conflicts (architectural vs. structural, civil vs. MEP)
- Missing dimensions or details
- Specification ambiguities
- Field conditions that differ from the drawings
- Owner-directed verbal changes that need written clarification

### RFI structure

```
RFI #[###]
Date: [date]
Project: [name and number]
Subject: [one-line description]
Spec/Drawing Reference: [sheet number and detail or spec section]
Description: [what the drawing/spec says; what the field condition is; why the two conflict]
Question: [specific, single question — one question per RFI]
Schedule/Cost Impact if Unanswered: [state it; e.g., "Tile installation blocked; 5-day delay"]
Response Required By: [date — typically 7–10 business days per contract]
Submitted by: [name, company]
```

**One question per RFI.** Multi-question RFIs get partial answers and are harder to track.

### RFI tracking

- Log every RFI: number, date submitted, date due, date answered, response action.
- Flag overdue RFIs weekly. Send a formal written follow-up after the response deadline passes.
- Link RFIs to their schedule impact: if the answer will change a design, the schedule engineer
  may need to update the activity.
- If the RFI answer changes scope, a change order is the next step.

---

## Part 3 — Change Orders

### Change-order trigger sources

| Source | Who identifies it |
|---|---|
| Owner-directed scope change | Owner issues direction |
| RFI response that changes scope | Coordinator identifies; notify PM |
| Differing site condition | Superintendent; notify PM immediately |
| Design error / omission | Submittal review or RFI exposes it |
| Regulatory / code interpretation | Inspector or building department |

### Change-order documentation discipline

**No verbal change orders.** An oral direction from the owner, architect, or their rep is
not a change order. Issue a Request for Change (RFC) or Proposed Change Order (PCO) in writing
before the work starts. If the owner says "just do it and we'll sort the paperwork later," the
GC does the work at its own risk — and often doesn't get paid.

### CO pricing

Work with `estimating-and-takeoff-analyst` to price:
- Direct labor: hours × loaded rate (document the rate source and date)
- Material: quote or unit-price book (document source and date)
- Equipment: rental or owned
- Subcontractor cost + markup per contract terms
- GC overhead and profit per contract terms (typically specified as a %)
- Bond (if applicable on CO amounts)
- Time impact: schedule days affected (separate from direct cost)

### CO package to owner

1. Cover letter: CO number, description, contract value before/after, time impact.
2. Cost breakdown: labor, material, equipment, sub, OH&P.
3. Supporting documentation: RFI response, architect's SI, owner's letter, field photos.
4. Schedule impact: CPM fragnet or narrative (days added/subtracted, no impact on critical path).
5. Time-extension request if applicable.

### CO log

Track: CO number | description | date submitted | amount | time (days) | status (pending /
approved / rejected / in dispute) | SOV line where it will be billed once approved.

---

## Anti-patterns

- A submittal log without need-on-site dates (you can't tell what's urgent).
- An RFI with multiple questions (partial answers guaranteed).
- Verbal or email-only change directions without a written CO.
- A CO log not updated after each pay app cycle.
- Submittals transmitted all at once in the first week, overwhelming the reviewer.

## Output

Three living documents: the submittal register, the RFI log, and the change-order log. Reference
template: [`../../templates/schedule-of-values.md`](../../templates/schedule-of-values.md) for
CO integration into billing.
