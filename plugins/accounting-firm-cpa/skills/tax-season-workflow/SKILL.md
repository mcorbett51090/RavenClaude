---
description: "Design and operate the end-to-end US tax-season workflow for a CPA firm: return intake through e-file acceptance, extension strategy, review-tier routing, client document-chase program, and e-file rejection triage."
---

# Tax Season Workflow

**Purpose:** run a CPA firm's tax season as a repeatable, deadline-safe operation — from client
document receipt to IRS acceptance — with appropriate review tiers, a proactive extension
strategy, and a document-chase program that prevents the last-minute crunch.

---

## Entry point

Spawn when asked to design, audit, or improve a firm's tax-season workflow. Primary agent:
`tax-workflow-strategist`. Supporting: `firm-practice-lead` (capacity), `firm-advisory-lead`
(scope conversations with clients).

---

## Phase 1: Season setup (8–12 weeks before first deadline)

1. **Return inventory.** Catalogue the return mix: count by type (1040, 1120, 1065, 1041, 990),
   complexity tier (simple / standard / complex), and assigned staff level.
2. **Deadline calendar.** Map all filing and extension deadlines for the current tax year.
   Note: deadlines shift when they fall on weekends/holidays — always verify the IRS and
   state agency calendar for the current year `[verify-at-use]`.
3. **Capacity check.** For each return type × complexity tier, estimate average charge hours.
   Multiply by return count → total demand hours. Compare to available staff hours by level.
   Flag gaps; design levers (overtime, outsourcing, extensions, workflow efficiency).
4. **Review-tier assignment matrix.** Define which staff level prepares and reviews each
   complexity tier. Use the decision tree in
   [`../../knowledge/cpa-firm-decision-trees.md`](../../knowledge/cpa-firm-decision-trees.md).
5. **Software and workflow tool check.** Confirm tax software licenses and capacity
   (UltraTax, Lacerte, CCH Axcess `[verify-at-use]`), workflow tracking tool (Karbon, Canopy
   `[verify-at-use]`), and client portal for document receipt.

---

## Phase 2: Client outreach and document chase

1. **Organizer send.** Send tax organizers / document-request checklists 6–8 weeks before the
   return deadline. Personalize for entity type (W-2 earner vs. Schedule E vs. pass-through K-1).
2. **Document receipt tracking.** Log receipt date per client in the workflow tool. Flag clients
   with no response after two weeks.
3. **Reminder cadence:**
   - First reminder: 3 weeks before original deadline
   - Second reminder: 2 weeks before, with extension warning
   - Extension trigger: if no complete document package by 1 week before deadline, file extension
     and notify client
   - Final notice: at extended deadline for clients on extension
4. **Completeness check at intake.** Before assigning to a preparer, verify the document package
   is complete: prior-year return, W-2s / 1099s, K-1s (if applicable), bank statements
   (if Schedule C/E), depreciation schedules, and any new items flagged from prior year.
   Return incomplete packages to the client with a specific missing-item list.

---

## Phase 3: Preparation and review

1. **Preparer assignment.** Assign each return to a preparer based on return complexity and
   preparer competence. Do not batch all complex returns to the same preparer.
2. **Preparation SLA.** Define turnaround time by complexity tier (e.g., simple 1040 = 2 business
   days; complex 1065 = 5 business days from complete document package).
3. **First review.** Reviewer verifies: all income items present, deductions supported, prior-year
   comparison for unusual items, mathematical accuracy, and no open questions.
4. **Second review (complex tier only).** For returns with planning opportunities, unusual
   positions, or high complexity — manager or partner review before partner sign-off.
5. **Partner sign-off.** Partner reviews and approves the return before it leaves the firm.
   Verify e-file authorization (Form 8879 / equivalent) is signed by the client.

---

## Phase 4: Extension strategy

1. **Extension decision criteria:** file an automatic extension (Form 4868 for 1040,
   Form 7004 for 1120/1065) when:
   - Key documents (K-1s, amended 1099s) have not arrived
   - The return requires complex research or planning that cannot be done by the deadline
   - Capacity constraints prevent completing the return with adequate review time
2. **Balance-due obligation.** An extension of *time to file* is NOT an extension of *time to
   pay*. Estimate the balance due and advise the client to pay by the original deadline to
   avoid failure-to-pay penalties. Document the estimate.
3. **Client communication.** Notify clients of extensions with: the reason, the new deadline,
   any estimated payment required, and what the client must do (provide remaining documents
   by a specific date).
4. **Extended return calendar.** Track all extended returns with their new deadlines. Build
   a second-season capacity plan for the September/October extended-return crunch.

---

## Phase 5: E-file and acceptance tracking

1. **E-file submission.** Submit returns via the tax software. Confirm submission confirmation
   number is logged in the workflow tool.
2. **Acknowledgment tracking.** IRS acknowledgments typically arrive within 24–48 hours. Do
   not mark a return "filed" until the acceptance acknowledgment is received.
3. **Rejection triage:**
   - Identity mismatch (name/SSN/DOB): verify client data vs. SSA records; correct and re-file
   - Prior-year AGI mismatch: obtain correct prior-year AGI; use $0 if prior year was a reject
     or paper-filed
   - Duplicate SSN: another return was already filed for this SSN; investigate identity theft risk
   - EIN mismatch (business returns): verify EIN vs. IRS EIN confirmation letter
   - If rejection cannot be resolved electronically: paper-file with extension-penalty-avoidance
     documentation
4. **Archive.** Upon acceptance: archive the signed return, all workpapers, e-file authorization
   forms, and the acceptance acknowledgment. Retention per firm policy (typically 7 years minimum).

---

## Anti-patterns

- A single queue for all return types — complex and simple mixed together.
- Extension filings with no estimated balance-due payment.
- E-file submission without tracking acknowledgments to accepted status.
- Completeness checks skipped at intake to "get returns moving."
- Review assignment based on staff availability rather than return complexity.

---

## Output

A phased tax-season operating plan with: return inventory, deadline calendar, capacity analysis,
review-tier matrix, document-chase calendar, extension strategy, and e-file tracking protocol.
Use [`../../templates/`](../../templates/) for engagement letter and PBC list templates.
