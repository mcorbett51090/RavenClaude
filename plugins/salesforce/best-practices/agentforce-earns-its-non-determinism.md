# Make Agentforce earn its non-determinism — deterministic work stays deterministic

**Status:** Absolute rule — never put an agent where a deterministic automation belongs, and never ship one ungated by the Trust Layer.

**Domain:** Agentforce / agent design

**Applies to:** `salesforce`

---

## Why this exists

Agentforce is driven by the Atlas reasoning engine and is **non-deterministic** — the same input can yield a different plan. That variance is a *cost*, not a feature. Spending it on fixed-path work (where the outcome must be identical every time) buys you unpredictability, consumption credits, and an audit headache in exchange for nothing a Flow couldn't do reliably. And an agent that reaches org data without the Einstein Trust Layer leaks PII, has no prompt defense, and no audit trail. This is house opinion #14.

## How to apply

Run the requirement through the determinism gate before designing anything, then keep the agent's *actions* deterministic even though its *planning* is not.

```
Is the path fixed and must the outcome be identical every time?
  YES -> deterministic: Flow or Apex, NOT an agent
  NO  -> does reasoning over varied input add real value?
           NO  -> deterministic (Flow/Apex)
           YES -> can the work be bounded topics + deterministic actions?
                    NO  -> rescope (too open-ended for a safe agent)
                    YES -> Agentforce agent
                             + gate with the Einstein Trust Layer
                             + compose deterministic actions (Flow / @InvocableMethod Apex)
```

**Do:**
- Scope each **topic** tightly — a bounded job with clear instructions and a fixed action set; Atlas plans only within the actions you give it.
- Make every action **deterministic, idempotent, and limit-safe** (standard actions, Flow actions, invocable Apex).
- Route every agent through the Trust Layer: grounding, PII masking, prompt defense, toxicity filtering, audit.

**Don't:**
- Use an agent when you can't articulate what reasoning *buys* you — "the best agent is often a Flow".
- Let the reasoning engine improvise side effects; keep side effects in deterministic actions.
- Ship without Trust Layer grounding and masking.

## Edge cases / when the rule does NOT apply

The rule is about *placement*, not a ban — genuine reasoning over varied, unstructured input (triage, summarization, open-ended Q&A over grounded data) is exactly where an agent earns its keep. Invocable Apex actions still run inside normal Apex governor limits, so a bulk-heavy action is `apex-engineer`'s problem regardless of the agent wrapping it. All Agentforce specifics (determinism-level naming, request/consumption numbers) are fast-moving — verify `[verify-at-build]`.

## See also

- [`../knowledge/agentforce-determinism-and-trust.md`](../knowledge/agentforce-determinism-and-trust.md) — determinism levels, Atlas, the Trust Layer
- [`flow-vs-apex-one-entry-point.md`](./flow-vs-apex-one-entry-point.md) — the deterministic alternatives an agent should defer to
- [`bulkify-every-soql-and-dml.md`](./bulkify-every-soql-and-dml.md) — invocable-action Apex is still bulk-bound
- [`../agents/agentforce-architect.md`](../agents/agentforce-architect.md) — the agent that owns this call

## Provenance

Codifies house opinion #14 from [`../CLAUDE.md`](../CLAUDE.md) and the `agentforce-architect` discipline, grounded in [`../knowledge/agentforce-determinism-and-trust.md`](../knowledge/agentforce-determinism-and-trust.md) (sourced from Salesforce's Atlas reasoning-engine, levels-of-determinism, and Einstein Trust Layer docs).

---

_Last reviewed: 2026-05-30 by `claude`_
