# Design slot-filling with explicit confirmation before any irreversible action

**Status:** Absolute rule
**Domain:** Copilot Studio bot design
**Applies to:** `power-platform`

---

## Why this exists

Copilot Studio's slot-filling (entity extraction + clarification questions) gathers variables for an action without additional turns when the NLU is confident. This speed is a benefit for read operations and a liability for writes: a high-confidence extraction that fires `CancelOrder(orderId=12345)` without user confirmation is an accidental-destruction incident waiting for the first ambiguous utterance. The Trust Layer is a Copilot/AI Builder concern; confirmation is a conversation-design concern — and conversation design owns the blast radius of a misheard value.

## How to apply

For every topic that calls an action with side effects (create, update, delete, send, approve):

```yaml
# Slot-fill the parameters first
- entity: orderId
  required: true
  prompt: "Which order number would you like to cancel?"

# Explicit confirmation node BEFORE the action
- message: "You want to cancel order {orderId}. Is that correct?"
- condition: userResponse = "yes"
  then:
    - action: CancelOrder(orderId)
    - message: "Order {orderId} has been cancelled."
  else:
    - message: "Okay, the cancellation has been stopped."
```

Checklist:
- [ ] Every `Power Automate` or `HTTP` action call that mutates data has a confirmation node upstream.
- [ ] The confirmation message echoes the filled values back verbatim — the user must see what will be acted on.
- [ ] Negative confirmation ("No", "Stop", "Cancel") always routes to a graceful out, not a loop.
- [ ] High-blast-radius actions (financial transactions, bulk operations, account deletions) add a second confirmation with a typed-value challenge (e.g., "type CONFIRM to proceed").

**Do:**
- Use adaptive cards for confirmations on complex multi-value actions — prose confirmations are hard to scan.
- Store the confirmation result in a topic variable so the conversation log shows what the user agreed to.
- Test the "No" path explicitly — it is the path most often skipped in happy-path demos.

**Don't:**
- Configure slot-filling to run the action automatically on first intent — the NLU confidence score is not a substitute for user confirmation.
- Reuse a generic "Are you sure?" message across all topics — the confirmation must be specific enough that the user can validate the extracted values.
- Skip confirmation for "small" actions like updating a single field — the user's definition of "small" and the system's are different.

## Edge cases / when the rule does NOT apply

Read-only actions (search, lookup, list) do not need a confirmation node. A conversational action whose only output is a message (no external side effect) also does not need confirmation.

## See also

- [`../agents/copilot-studio-engineer.md`](../agents/copilot-studio-engineer.md) — owns Copilot Studio bot design and the slot-filling pattern
- [`./copilot-escalation-and-guardrails.md`](./copilot-escalation-and-guardrails.md) — the complementary guardrails for out-of-scope requests

## Provenance

Codifies `copilot-studio-engineer`'s opinion from the `copilot-studio-bot-design` skill (CLAUDE.md §8) on slot-filling and confirmation; standard responsible-AI bot design practice.

---

_Last reviewed: 2026-06-05 by `claude`_
