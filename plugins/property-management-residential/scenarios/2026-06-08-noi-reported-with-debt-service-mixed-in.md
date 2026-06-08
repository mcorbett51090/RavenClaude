---
scenario_id: 2026-06-08-noi-reported-with-debt-service-mixed-in
contributed_at: 2026-06-08
plugin: property-management-residential
product: generic
product_version: "unknown"
scope: likely-general
tags: [noi, owner-statement, debt-service, capex, reporting]
confidence: high
reviewed: false
---

## Problem

An owner statement reported "NOI" with the mortgage payment and a roof replacement netted into the same line. The number came out negative for a property that was operationally healthy, the owner panicked, and two weeks were lost reconciling a figure that was never NOI in the first place. Two different questions — operating performance and levered cash flow — had been collapsed into one mislabeled line, so neither was answerable from the statement.

## Constraints context

- The property manager's spreadsheet had one "net" column that subtracted every cash outflow, including debt service and capex.
- The owner used that number to judge operating performance, the lender used it for a different purpose, and they disagreed — because it answered neither question cleanly.
- "NOI" and "cash flow" were used interchangeably in conversation, which masked the mislabel.

## Attempts

- Tried: explaining the negative number verbally each month. Failed — a recurring verbal caveat on a mislabeled line is not a fix; the next statement re-created the confusion.
- Tried: adding the mortgage as a footnote while leaving it in the net line. Failed — it was still netted in, so the headline number was still wrong.
- Tried: reporting NOI as operating income minus operating expenses ONLY, with debt service, capex, and depreciation moved to clearly-labeled below-the-line items, and a separate levered-cash-flow figure beneath them. This worked — both questions became answerable from the same statement.

## Resolution

NOI went back to operating-only (income minus operating expenses, excluding debt service, capex, and depreciation by construction). The mortgage, the roof (capex), and depreciation sat below the NOI line, and a distinct levered-cash-flow line answered the cash question separately. The trust-account reconciliation, GL posting, and tax treatment were routed to `finance` as the books of record — the owner statement reported operations, not the books.

## Lesson

NOI is operating-only and is NOT cash flow. Never net debt service, capex, or depreciation into NOI; report them below the line and answer the levered-cash-flow question separately. The owner statement reports operations; the books of record (trust account, GL, tax) belong to `finance`. Mislabeling cash flow as NOI turns a healthy property into a false alarm.
