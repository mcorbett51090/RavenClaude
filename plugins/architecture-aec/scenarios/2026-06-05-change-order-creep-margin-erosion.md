---
scenario_id: 2026-06-05-change-order-creep-margin-erosion
contributed_at: 2026-06-05
plugin: architecture-aec
product: scope-management
product_version: "n/a"
scope: likely-general
tags: [change-order, scope-creep, additional-services, margin, asa]
confidence: medium
reviewed: false
---

## Problem

A small architecture firm finished a project on-time and well-liked by the client but **made almost no money on it**. The principal couldn't explain the gap: the fee was fair, the team wasn't slow, yet the margin evaporated. The instinct was "we under-bid," and the next proposal was about to be padded across the board — a move that risked losing competitive work without fixing the actual leak.

## Context

- Segment: commercial interiors / fit-out, independent firm, fixed-fee basic-services contract with a thin additional-services clause nobody invoked.
- Constraint: the client made a steady stream of "just one more option" and "can you also look at…" requests across SD and DD. Each felt too small to issue an Additional Services Authorization (ASA) for — so the team absorbed them. Individually trivial; cumulatively, a second unpaid project.
- No issue log tying scope changes to fee. The owner-initiated changes, unforeseen-condition responses, and extra design options were invisible until the P&L showed the hole.

## Attempts

- Tried: reconstructed the change history and sized it against the contract. The absorbed/unbilled scope work was a large share of the planned profit — when modeled, the **effective margin had collapsed from the planned ~18% [ESTIMATE] toward break-even** because the unbilled work is effort delivered for *no fee* and erodes profit dollar-for-dollar. Outcome: proved the leak was unbilled scope, **not** an under-priced base fee.
- Tried: classified each absorbed request through the additional-services tree — owner-initiated change / unforeseen condition / extra option (all ASA-eligible) vs. genuine in-scope refinement. The large majority were ASA-eligible and had simply never been authorized. Outcome: showed the fix was a *process* (authorize before working), not a *price* (pad the fee).
- Tried (the move that worked): adopted "authorize additional services **before** the work, not after" (§3 #2) — a one-paragraph ASA or a brief scope memo at the moment a request crossed the in-scope line, plus a single RFI/change-order/scope log so the burn was visible weekly instead of at billing. Re-ran the next proposal's base fee at its *correct* (unpadded) level, with the additional-services mechanism actually used.

## Resolution

The margin killer was **scope creep absorbed silently**, not a low fee. Padding the base fee would have made the firm less competitive while leaving the real leak — unauthorized scope — wide open. Instituting before-the-work authorization and a visible change log recovered the margin on the next engagement without raising the headline fee.

**Action for the next consultant hitting this pattern:** when a fairly-priced project loses money, **measure the absorbed/unbilled scope before touching the base fee.** Change orders typically run ~5-10% of value as a normal band and 8-14% on average, with distressed jobs to ~25% [verify-at-use] — quantify where this project sits and how much of that work was unbilled. The fix is almost always *authorize additional services before the work* (§3 #2) plus one issue log (§3 #3), not a flat fee increase. The [`../scripts/aec_calc.py`](../scripts/aec_calc.py) `change-order` mode computes the CO % and the margin erosion from absorbed work; see also the [`../skills/control-scope-creep/SKILL.md`](../skills/control-scope-creep/SKILL.md) playbook and the "Additional Services" tree in [`../knowledge/aec-decision-trees.md`](../knowledge/aec-decision-trees.md).

**Sources (retrieved 2026-06-05):**
- Construct Two Group — *The Ultimate Guide to Construction Change Orders (2025)* (change-order % bands): https://constructtwo.com/uncategorized/construction-change-orders-guide-2025/
- AIA Contracts — *The Truth About Change Orders*: https://learn.aiacontracts.com/wp-content/uploads/2023/07/The-Truth-About-Change-Orders.pdf

Change-order percentage bands are industry rules-of-thumb, not hard rules — treat as `[verify-at-use]` and validate against the project's actual contract and scope record (§3 #8).
