---
scenario_id: 2026-06-05-agentforce-nondeterministic-action-misfire
contributed_at: 2026-06-05
plugin: salesforce
product: agentforce
product_version: "unknown"
scope: likely-general
tags: [agentforce, determinism, atlas, trust-layer, topic-scope, invocable-action, guardrails]
confidence: medium
reviewed: false
---

## Problem

A team shipped an Agentforce service agent meant to answer order-status questions and, as a convenience, gave it an "update shipping address" action and a broadly-worded topic ("help the customer with their order"). In testing it was delightful. In production the Atlas reasoning engine — being **non-deterministic** — occasionally chose the update-address action when a customer merely *mentioned* a new address while asking about status, silently mutating records the customer never asked to change. Worse, the same fixed-path task ("email the order confirmation PDF") sometimes ran and sometimes didn't, because it had been modeled as an agent action rather than a deterministic automation. The business expected a fixed process to be reliable and got a probabilistic one.

## Constraints context

- The topic instructions were broad ("help with the order"), so Atlas had wide latitude to pick actions — the agent's action surface was effectively unbounded relative to its intent.
- The convenience write action (`update shipping address`) was not idempotent and had no confirmation step, so a mis-selected invocation committed immediately.
- Part of the workload was genuinely fixed-path (send the same confirmation email every time) and never needed reasoning — it was non-determinism applied where determinism belonged (house opinion #14).
- `[verify-at-build]` all Agentforce specifics — Atlas behavior, Trust Layer features, topic/action authoring in the Agentforce builder — are fast-moving; confirm against current Salesforce docs before relying on any named behavior.

## Attempts

- Tried: lowering the model "temperature" / asking for more deterministic output. This is the wrong lever — an LLM-planned agent is non-deterministic by construction; you don't tune it into a Flow. Rejected.
- Tried: adding a long natural-language instruction telling the agent "only update the address if the customer explicitly asks." Helped in testing, regressed in the wild — prose guardrails are probabilistic, not enforcement; the model still mis-selected under novel phrasings.
- Tried (the fix, two parts): **(1) pull the fixed-path work out of the agent entirely** — the confirmation email became a deterministic Flow, not an agent action, so it runs identically every time. **(2) Re-scope the topic tightly and harden the remaining write action** — narrow topic instructions, the address-change action gated behind an explicit confirmation step and made idempotent, and the whole agent gated by the Einstein Trust Layer (grounding, masking, prompt defense, audit trail).

## Resolution

**Agentforce is non-deterministic — never put it where a deterministic automation belongs, scope topics tightly to bounded actions, and gate every agent with the Trust Layer.** The reliable design:

1. **Determinism check first.** If the path is fixed and the outcome must be identical every time, build a Flow or Apex — *not* an agent. Reserve the agent for genuine reasoning over varied, unstructured input where that reasoning adds real value.
2. **Bound the topic to explicit, deterministic actions.** Atlas plans by selecting from the topic's actions; a tightly-scoped topic with a small set of deterministic actions (standard actions, Flows, `@InvocableMethod` Apex) keeps the reasoning — and the side effects — bounded. A broad topic with a powerful write action is an invitation to mis-selection.
3. **Make every write action idempotent and confirmed.** A non-deterministic planner *will* occasionally select the wrong action; the action's own guardrails (confirmation, idempotency, narrow scope) are the enforcement, not the prose instruction.
4. **Gate with the Einstein Trust Layer, always.** Grounding, PII masking, prompt defense, toxicity detection, zero-retention, audit trail — no agent ships without it.
5. **Test and evaluate before *and* after ship.** Because behavior is probabilistic, a one-time manual test isn't a guarantee; evaluate the agent against a scenario set and keep watching in production.

The trap: the agent demos beautifully because the happy path is common, so the mis-selection and the silently-skipped fixed-path action only surface at production volume and variety — exactly when they're most expensive.

**Action for the next builder:** before modeling anything as an agent action, ask "does this need reasoning, or is it a fixed path?" — push fixed paths to Flow/Apex. For the genuinely-agentic remainder, scope topics tightly, make write actions idempotent + confirmed, and confirm the Trust Layer is on. Treat prose guardrails as hints, never as enforcement.

Cross-reference: canonical guidance in [`../knowledge/agentforce-determinism-and-trust.md`](../knowledge/agentforce-determinism-and-trust.md) and the **Automation — Agentforce vs Flow/Apex** decision tree in [`../knowledge/platform-alm-agentforce-decision-trees.md`](../knowledge/platform-alm-agentforce-decision-trees.md); rules [`../best-practices/agentforce-earns-its-non-determinism.md`](../best-practices/agentforce-earns-its-non-determinism.md), [`../best-practices/agentforce-scope-topics-tightly-with-explicit-instructions.md`](../best-practices/agentforce-scope-topics-tightly-with-explicit-instructions.md), [`../best-practices/agentforce-action-grounding-and-guardrails.md`](../best-practices/agentforce-action-grounding-and-guardrails.md), and [`../best-practices/agentforce-test-and-evaluate-before-and-after-ship.md`](../best-practices/agentforce-test-and-evaluate-before-and-after-ship.md). House opinion #14.
