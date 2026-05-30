# Test an agent with an evaluation set, not a demo — and keep measuring it after it ships

**Status:** Pattern — strong default; shipping a non-deterministic agent on a single happy-path demo is negligence.

**Domain:** Agentforce / agent design

**Applies to:** `salesforce`

---

## Why this exists

A non-deterministic system cannot be verified the way deterministic code is: there is no single "expected output" to assert against, and a demo that works once proves nothing — the same utterance may plan differently next time. The way you build confidence in an agent is an **evaluation set**: a curated battery of representative utterances, paraphrases, edge cases, and adversarial inputs, each with a defined success criterion (did it pick the right topic? call the right action? ground the answer? refuse the unsafe request?). You run the set, measure the pass rate, and treat a regression as a release blocker — the same role Apex test coverage plays for code, adapted for variance. And because the model, the data it grounds in, and user phrasing all drift, evaluation is **not a one-time gate**: production conversations must be sampled and scored continuously, or quality erodes invisibly between releases. Salesforce ships tooling for exactly this (testing/eval in the Agentforce builder and the Testing Center) — the rule is to *use* it, with a real set, not to ship on vibes.

## How to apply

Build a versioned evaluation set covering the agent's real surface, gate releases on its pass rate, and sample production traffic to catch drift.

```
EVALUATION SET (version-controlled alongside the agent):
  Happy path ......... canonical utterances for each topic -> expect: right topic + right action + grounded answer
  Paraphrase ......... same intent, varied wording ........ expect: same routing (tests robustness, not luck)
  Edge / ambiguous ... underspecified or multi-intent ..... expect: clarifying question, not a wrong guess
  Out-of-scope ....... requests outside the topic set ..... expect: graceful decline / handoff, not improvisation
  Adversarial ........ prompt injection, PII fishing, toxic  expect: Trust Layer blocks; no leak, no compliance

PRE-SHIP GATE:
  run set -> measure pass rate per category -> regression vs baseline BLOCKS the release

POST-SHIP (continuous):
  sample real conversations -> score against the same criteria -> drift below threshold => investigate / re-tune
```

```bash
# Run the agent's evaluation/test definitions through the CLI as a release gate (names verify-at-build)
sf agent test run --target-org uat --test-name BillingAgent_Eval --wait 30
# A failed/regressed run fails the pipeline, exactly like a failed Apex test
```

**Do:**
- Curate an evaluation set that covers paraphrases, edge cases, out-of-scope, and adversarial inputs — not just the demo path.
- Define a clear success criterion per case (correct topic, correct action, grounded, safe refusal) and track the pass rate over time.
- Gate releases on the eval pass rate, and **sample production conversations** to catch post-ship drift.

**Don't:**
- Sign off an agent on a single happy-path walkthrough — one success is not a pass rate.
- Test only that it answers; test that it answers *correctly*, *grounded*, and *refuses the unsafe request*.
- Treat the pre-ship eval as the end — without ongoing sampling, quality decays silently between releases.

## Edge cases / when the rule does NOT apply

A throwaway internal **prototype** explicitly not exposed to real users can run on a lighter set — but the moment it touches real data or real users, the full discipline applies. The exact tooling (Testing Center, `sf agent test`, eval-spec format) and the metrics it surfaces are **fast-moving** — verify command names, eval-set schema, and scoring options `[verify-at-build]` rather than copying them as gospel. Adversarial coverage overlaps with security review: prompt-injection and data-exposure *verdicts* escalate to `ravenclaude-core/security-reviewer`; this rule owns the *test discipline*, not the security ruling.

## See also

- [`agentforce-action-grounding-and-guardrails.md`](./agentforce-action-grounding-and-guardrails.md) — the grounding and guards the eval set verifies
- [`agentforce-earns-its-non-determinism.md`](./agentforce-earns-its-non-determinism.md) — why a non-deterministic system needs a different verification model
- [`apex-test-data-with-testfactory-not-seealldata.md`](./apex-test-data-with-testfactory-not-seealldata.md) — the deterministic-test analogue for the agent's Apex actions
- [`../knowledge/agentforce-determinism-and-trust.md`](../knowledge/agentforce-determinism-and-trust.md) — Trust Layer behaviors the adversarial cases probe
- [`../agents/agentforce-architect.md`](../agents/agentforce-architect.md) — the agent that owns the eval design

## Provenance

Extends house opinion #14's "non-determinism is a cost" into a verification discipline, codifying the `agentforce-architect`'s Trust-Layer and watch-outs posture. Grounded in [`../knowledge/agentforce-determinism-and-trust.md`](../knowledge/agentforce-determinism-and-trust.md) and Salesforce's Agentforce Testing Center / agent-evaluation guidance. Tooling, command names, and eval schema are fast-moving — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
