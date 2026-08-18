---
scenario_id: 2026-08-17-the-upload-endpoint-stored-nothing
contributed_at: 2026-08-17
plugin: forms-engineering
product: form-hardening
product_version: "n/a"
scope: likely-general
tags: [attachments, storage-binding, silent-failure, observability, delivery-defect]
confidence: medium
reviewed: false
---

## Problem

An intake form accepted attachments. The endpoint was fully coded: origin check, session check, ownership check, declared-type allow-list, size ceiling. It passed review and every gate it had. **Every valid attachment then died at the storage seam** — the object-storage binding the handler wrote to was never actually bound in the deployed environment, so the write threw, the error was swallowed, and the submission was recorded as accepted with no file attached.

## Context

- The handler had been written against a binding name that existed in the configuration file as a **comment describing** the intended binding, not as a live block.
- A tracker item had been flipped to done on the strength of a grep that matched that comment.
- Attachments were optional on the form, so most submissions never exercised the path. The ones that did produced a "thank you" page.
- The only place the failure was visible was an unread error stream.

## Attempts

- Tried: re-reading the handler. Outcome: nothing wrong with it. The authority chain was correct and in the right order. This is why it survived review — the defect was not in the code that was reviewed.
- Tried: grepping the configuration for the binding name. Outcome: **a match** — inside a comment. This is the trap: a grep is satisfied by the thing being *described*, and the same grep is what had closed the tracker item.
- Tried: re-running the grep with the match required to be inside an actual binding block rather than anywhere in the file. Outcome: zero. The binding did not exist.
- Tried (the move that worked): treating "submission accepted" and "attachment stored" as two separate observable outcomes, counting both, and alerting on the gap. Outcome: the gap was immediately visible, and would have been visible from day one.

## Resolution

The class here is a **delivery defect** — a submission the server accepted that never reached the process behind it — and it is invisible by construction, because the user-facing path succeeds. Neither the code review nor the type-and-size validation could have caught it; both were correct.

Two durable lessons. First: **a configuration grep must require the match to be inside the block it claims**, never merely present in the file — a comment describing a binding is not a binding. Second: **an accepted submission is not a delivered submission**, and instrumenting only the first makes the second unfalsifiable.

**Action for the next person hitting this pattern:** count acceptance and delivery separately and alert on the divergence — the defect taxonomy is in [`../knowledge/form-telemetry-and-spc.md`](../knowledge/form-telemetry-and-spc.md) §4. Attachment handling rules themselves are owned upstream at [`../../ravenclaude-core/rules/security.md`](../../ravenclaude-core/rules/security.md) §File handling, and the binding verdict on any change to this path is [`../../ravenclaude-core/agents/security-reviewer.md`](../../ravenclaude-core/agents/security-reviewer.md)'s.

**Sources for facts cited:** the comment-matched-instead-of-the-binding failure is a recorded defect shape in this marketplace's own operational notes (2026-08-17); the substrate instance it was observed on is described, with its re-verification command, in this plugin's substrate knowledge file (`knowledge/ravenpower-form-substrate.md` — referenced, deliberately not linked, so the substrate layer stays deletable). Figures are illustrative `[ESTIMATE]`.
