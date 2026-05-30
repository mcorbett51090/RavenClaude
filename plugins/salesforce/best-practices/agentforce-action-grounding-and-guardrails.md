# Ground every agent action in real data and guard every side effect — the model plans, deterministic actions execute

**Status:** Absolute rule — an ungrounded answer or an unconfirmed irreversible action is a defect, not a UX choice.

**Domain:** Agentforce / agent design

**Applies to:** `salesforce`

---

## Why this exists

An Agentforce agent that answers from the model's parametric knowledge instead of from grounded Salesforce data will confidently invent — wrong order totals, made-up policy, a customer who doesn't exist. The Atlas reasoning engine is only as trustworthy as the data its actions retrieve, so **grounding** (dynamic grounding in Salesforce records, retrieval from a knowledge source) is what turns a plausible-sounding agent into a correct one. The second failure mode is on the write side: the model *plans* non-deterministically, so if a planning step can directly trigger an irreversible side effect — issue a refund, delete a record, send an email — variance in the plan becomes variance in the real world. The discipline that makes agents safe is the same one that makes them useful: the model reasons, but **deterministic, idempotent, guard-railed actions** are what actually touch data, and high-stakes actions require confirmation or human approval before they fire. This is the operational layer beneath house opinion #14.

## How to apply

Give the agent grounded read actions and deterministic write actions; put a confirmation or approval gate in front of anything irreversible; let the Trust Layer mask and audit the whole exchange.

```
GROUND every answer:
  - Read actions pull from Salesforce records / a knowledge source — never "the model knows"
  - If the grounding source returns nothing, the agent says so; it does not fabricate

GUARD every side effect (invocable Apex / Flow action):
  - Idempotent: same inputs => same result, safe to retry (Atlas may re-plan)
  - Typed, validated inputs; reject out-of-range before any DML
  - Low-stakes / reversible ...... agent may execute directly
  - High-stakes / irreversible ... REQUIRE explicit user confirmation or a human-approval step
                                   (refund, delete, external payment, mass update)

GATE the exchange with the Einstein Trust Layer:
  - PII masking before the prompt reaches the model
  - Prompt-injection defense, toxicity filtering, zero retention, full audit trail
```

```apex
@InvocableMethod(label='Issue Refund' description='Refund a charge — requires confirmed amount')
public static List<Result> issueRefund(List<Request> reqs) {
    // GUARD: validate before any side effect — the model's plan is not trusted input
    for (Request r : reqs) {
        if (r.amount == null || r.amount <= 0 || r.amount > r.chargeTotal) {
            throw new RefundException('Refund amount out of bounds'); // reject, don't guess
        }
    }
    // IDEMPOTENT: keyed on the charge so an Atlas re-plan can't double-refund
    // ... bulk-safe DML, delegated to apex-engineer for limit-safety ...
}
```

**Do:**
- Ground every customer-facing answer in retrieved Salesforce/knowledge data; have the agent admit "I don't have that" rather than invent.
- Make write actions idempotent and input-validated so a re-planned cycle can't double-act or act on garbage.
- Put a confirmation/approval gate in front of every irreversible or high-value action.

**Don't:**
- Let the model answer from parametric knowledge where a grounded fact is available.
- Expose a raw destructive operation as a one-shot agent action with no confirmation.
- Trust the model's plan as validated input — validate inside the deterministic action.

## Edge cases / when the rule does NOT apply

A **purely informational** agent over fully public, non-sensitive content has lighter grounding/guard needs — but it still runs through the Trust Layer, because prompt-injection and toxicity defense are not optional. Some low-stakes, fully-reversible actions (drafting a note, suggesting next-best-action without committing) legitimately skip the confirmation gate — "reversible and low-value" is the test, and when in doubt, gate. All Agentforce specifics — action types, grounding source options, Trust Layer feature names — are fast-moving; verify `[verify-at-build]`.

## See also

- [`agentforce-earns-its-non-determinism.md`](./agentforce-earns-its-non-determinism.md) — the determinism placement decision this operationalizes
- [`agentforce-test-and-evaluate-before-and-after-ship.md`](./agentforce-test-and-evaluate-before-and-after-ship.md) — proving the grounding and guards actually hold
- [`bulkify-every-soql-and-dml.md`](./bulkify-every-soql-and-dml.md) — invocable-action Apex is still bulk- and limit-bound
- [`enforce-sharing-and-crud-fls.md`](./enforce-sharing-and-crud-fls.md) — the agent's read actions still run under the user's CRUD/FLS
- [`../knowledge/agentforce-determinism-and-trust.md`](../knowledge/agentforce-determinism-and-trust.md) — Atlas, grounding, and the Trust Layer
- [`../agents/agentforce-architect.md`](../agents/agentforce-architect.md) — the agent that owns this design

## Provenance

Codifies house opinion #14 and the `agentforce-architect`'s "untrusted by default / tight topics, deterministic actions" discipline. Grounded in [`../knowledge/agentforce-determinism-and-trust.md`](../knowledge/agentforce-determinism-and-trust.md), sourced from Salesforce's Atlas reasoning-engine, dynamic-grounding, and Einstein Trust Layer documentation. All Agentforce specifics are `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
