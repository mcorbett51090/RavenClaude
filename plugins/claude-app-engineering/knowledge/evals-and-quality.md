# Evals & quality

**Last reviewed:** 2026-05-28 · **Confidence:** high (established LLM-eval practice + Anthropic guidance, retrieved 2026-05-28).
**Owner:** `eval-engineer`.

## The discipline (house opinion #4 — evals before vibes)
**No prompt or model change ships without an eval delta on a golden set.** "It looks better" is not a result. Build the eval *before* the change so you can measure the before/after.

## The eval stack
1. **Golden dataset** — a curated, version-controlled set of representative inputs + expected outputs (or expected properties). Start small (20-50 cases), grow from production failures. Include the hard/edge/adversarial cases, not just the happy path.
2. **Graders**, cheapest-reliable-first:
   - **Programmatic** — exact match, regex, JSON-schema validity, contains/not-contains, numeric tolerance. Use whenever the answer is checkable in code (it's free + deterministic).
   - **LLM-as-judge** — for open-ended quality (helpfulness, faithfulness, tone). Use when programmatic can't capture it.
   - **Human** — the ground-truth spot-check that calibrates the judge; sample, don't grade everything.
3. **Metrics** — accuracy / pass-rate on the golden set, plus task-level business metrics (cost-per-resolved-task, latency). Report a **delta vs the prior version**, with the failing cases enumerated.

## LLM-as-judge — the two things that make it fail
1. **Position / verbosity bias.** Judges favor the first option and longer answers. Mitigate: **pairwise** comparison with **randomized order** (run A-vs-B and B-vs-A; average), and score on a rubric, not a vibe. Keep the judge prompt **version-controlled** — judge-prompt drift silently moves your baseline.
2. **Cost.** A judge call per eval case per run adds up. **Default the judge to Haiku** and run eval batches through the **Batch API (50% off)** ([`claude-app-finops-reliability-and-security.md`](claude-app-finops-reliability-and-security.md)). Reserve a stronger judge model only for the cases Haiku is unsure on.

## Regression discipline
- Run the eval in CI on every prompt/model/tool-def change; fail the build on a regression beyond a set threshold.
- Pin the eval **model + judge model + judge prompt** so a baseline shift is intentional, not accidental.
- When the platform ships a new model, re-baseline deliberately (the capability map's job — [`model-selection-and-2026-capability-map.md`](model-selection-and-2026-capability-map.md)).

## Seam
Evaluating an **application's** prompt/model change is this agent. Evaluating a **RavenClaude agent-file's** prompt quality is `ravenclaude-core/prompt-engineer` via the `agent-quality-rubric` skill (see [`../CLAUDE.md`](../CLAUDE.md) §10).
