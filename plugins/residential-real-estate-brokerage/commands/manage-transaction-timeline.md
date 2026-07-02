---
description: "Reconstruct an executed contract's contract-to-close calendar from the effective date, date every contingency deadline, and flag at-risk items with the next action per party (periods verify-at-use against the contract)."
argument-hint: "[effective date + contract type + known contingencies/dates]"
---

You are running `/residential-real-estate-brokerage:manage-transaction-timeline`. Use `listing-and-transaction-coordinator` + the `transaction-timeline-management` skill.

> Advisory, not legal advice. Contingency **periods are contract- and jurisdiction-specific** — every date is `[verify-at-use]` against the executed contract. No client PII — work in roles (buyer side / seller side / lender / title), never a personal record.

## Steps
1. Anchor to the **effective date** and capture the contract type and any known contingency periods.
2. Reconstruct the full milestone calendar — earnest money, inspection + response, appraisal, financing, title, walkthrough, closing/funding — dating each from the effective date. Confirm periods `[verify-at-use]`.
3. Track each item to satisfied / waived-in-writing / notice-sent, and **flag at-risk items** (upstream work late) with the next action per party. Use the offer & counter tree in `knowledge/residential-brokerage-decision-trees.md` when a contingency response is itself a negotiation.
4. Emit using `templates/transaction-timeline-checklist.md` + the Structured Output block.
