---
scenario_id: 2026-06-08-rfi-answer-built-before-it-was-priced
contributed_at: 2026-06-08
plugin: construction-field-management
product: generic
product_version: "unknown"
scope: likely-general
tags: [rfi, change-order, unpriced-work, claim, ball-in-court]
confidence: high
reviewed: false
---

## Problem

A field RFI on a slab-edge detail came back from the architect with an answer that quietly added a continuous edge angle and extra embeds across the whole perimeter — clearly more material and labor than the contract documents showed. The superintendent, not wanting to hold up the pour, treated the RFI answer as direction and built it. Three months later the GC submitted a change order for the added work; the owner rejected it, arguing the GC had performed the work without a priced, authorized change and so had waived the claim.

## Constraints context

- Aggressive schedule; the foundation was on the critical path and the crew was standing by.
- The contract required written authorization (a signed CO or a construction change directive) before extra work.
- The RFI log captured the question and the answer but never flagged the answer as scope-bearing, and ball-in-court was never moved to the cost side.

## Attempts

- Tried: submitting the change order after the fact with the RFI answer as backup. Failed — an RFI is a clarification, not an authorization to perform added work; the owner held that performing first waived it.
- Tried: arguing the answer was a design change the GC was directed to follow. Partially helped but weak without a written directive — it came down to a dispute, not a clean CO.
- Tried (on the next event): a rule that any RFI answer is screened for scope/cost/time impact at log-close; if it's scope-bearing, ball-in-court moves to the cost lead, a PCO is priced and time-impacted, and a CO or written directive is obtained *before* the work proceeds. This worked.

## Resolution

Wiring the RFI close-out to a "is this scope-bearing?" gate stopped clarifications from silently becoming unpriced changes. When the next RFI answer added scope, it routed to the cost lead as a PCO, got priced and time-impacted, and was executed as a CO before the crew built it — the cost was recovered cleanly instead of fought over. The schedule pressure was handled with a written change directive (authorizing the work at a not-to-exceed while price was finalized), not by building on a verbal.

## Lesson

Nothing scope-bearing gets built unpriced. An RFI answer that adds scope, cost, or time is a change — screen for it at log-close, move ball-in-court to the cost lead, and get a signed CO or a written directive before the work proceeds. Building first on a verbal is how a recoverable cost becomes a waived claim.
