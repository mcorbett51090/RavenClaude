---
name: change-order-and-pay-application
description: "Run the money: build a schedule of values tied to cost codes, assemble an AIA G702/G703 pay application with stored materials and retainage handled correctly, track a change from proposed (PCO/COR) to executed (CO) so nothing is built unpriced, and keep budget-vs-actual honest with a real cost-to-complete."
---

# Change Order & Pay Application

## Schedule of values (SOV)
Break the contract sum into billable line items tied to the cost codes. Reasonable front-loading is normal; abusive front-loading gets the draw rejected — name the trade honestly. The SOV is the structure the G703 continuation sheet tracks against month over month, so define stored-materials and retainage handling up front.

## Pay application (G702/G703)
The G702 is the application/certificate summary; the G703 continuation sheet carries the line items: scheduled value, work completed prior + this period, stored materials, total completed-and-stored, retainage held per the contract, prior payments, and current payment due. Reconcile it and assemble the back-up so the architect can certify without a fight. Verify retainage % and stored-materials rules against the **specific contract**.

## Change management (PCO → CO)
A change starts as a PCO/COR, gets priced *and* time-impacted, and is executed as a CO before the work proceeds. Route the time impact to `project-management`; cost and time are two columns of one change. Log every change with status and ball-in-court so a proposed change never quietly fails to execute. No work gets built unpriced.

## Budget-vs-actual
Committed vs. actual vs. forecast by cost code, with a real cost-to-complete and a projected final cost. Unbilled commitments (signed subs/POs) are real money — leave them out and the report lies.

## Output
An SOV tied to cost codes, a clean G702/G703 pay app, a change tracked PCO→CO, or a reconciled cost report. Route the field event behind a change to `project-engineer`, the time-impact to `project-management`, trade pricing to `skilled-trades-contracting`.
