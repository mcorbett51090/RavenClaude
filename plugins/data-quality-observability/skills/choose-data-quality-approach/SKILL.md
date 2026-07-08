---
name: choose-data-quality-approach
description: Pick the right data-quality approach and tooling for a described stack by traversing the data-quality tooling decision tree (already-on-dbt? → check shape, known-rule vs unknown-over-time → build vs buy → where checks run → tool), then return the recommended contracts/tests/monitors mix, the tool (dbt tests / dbt-expectations / Great Expectations / Soda / Elementary / a managed platform / warehouse-native), where each check runs, the block-vs-warn policy, the SLAs, and the conditions that would flip the choice. Reach for this when the user asks "dbt tests vs Great Expectations vs Soda vs Monte Carlo?", "contracts vs tests vs monitors?", "where should checks run?", or "build vs buy observability?". Used by `data-quality-architect` (primary).
---

# Skill: choose-data-quality-approach

> **Invoked by:** `data-quality-architect` (primary). Also consulted by `data-quality-engineer` when a build reveals the chosen tool can't express a required check.
>
> **When to invoke:** "dbt tests vs Great Expectations vs Soda vs a managed platform?"; "contracts vs tests vs monitors?"; "where should the checks run?"; "build vs buy for observability?"; any "how should we assure this data's quality?" question.
>
> **Output:** the recommended contracts/tests/monitors mix + the tool + where each check runs + the block-vs-warn policy + the SLAs + the 1-2 flip conditions that would change the answer.

## Procedure

1. **Restate the situation in the tree's terms.** Capture: the **stack** (warehouse, on-dbt-or-not, orchestrator), the **pain** (silent bad data / stakeholder-found errors / no coverage / audit pressure), the **team size & budget**, and the **datasets in scope** with their consumers.
2. **Separate what you're asserting.** For each concern, classify it: a **known rule** (not-null, unique, referential, accepted-values) → a **test**; the **unknown over time** (freshness slipping, volume anomaly, schema drift, distribution shift) → a **monitor**; a **producer-boundary guarantee** (schema + semantics a consumer relies on) → a **contract**. Most programs need all three — name the mix, don't force one tool to be everything.
3. **Sequence by ROI.** Freshness + volume monitors first (cheap, catch most real incidents), producer contracts on the highest-value sources next, column-level tests where they earn their keep. Flag any "200 tests, zero monitors" starting point as inverted.
4. **Traverse the decision tree** in [`../../knowledge/data-quality-tooling-decision-tree.md`](../../knowledge/data-quality-tooling-decision-tree.md) against those inputs:
   - already-on-dbt + the check is a schema/row-level rule → **dbt tests** (+ **dbt-expectations** for distribution/value-range assertions),
   - Python-centric pipeline, rich expectation library + data docs wanted → **Great Expectations**,
   - warehouse-native, YAML-first checks + a monitoring UI, dbt-or-not → **Soda Core / Soda Cloud**,
   - already-on-dbt + want anomaly monitors + a UI with low lift → **Elementary**,
   - large estate, want automated coverage + ML anomaly detection + lineage, budget exists → a **managed platform** (Monte Carlo / Bigeye / Metaplane),
   - a quick gate with no new tool → **warehouse-native checks** (a `SELECT` assertion / constraint).
5. **Place each check** deliberately: **in-transform** (dbt test beside the model), **post-load gate** (a GE/Soda checkpoint that blocks promotion), or **independent monitor** (a platform / scheduled scan watching production).
6. **Set block-vs-warn per check:** circuit-break only where downstream harm > pipeline-stall cost; otherwise warn.
7. **Define the SLAs/SLIs** (freshness / completeness / validity, each with an owner) and **state the flip conditions** — the 1-2 facts that, if different, change the answer (e.g., "if they leave dbt, dbt-tests-first no longer holds").

## Worked example

> User: "We're on Snowflake + dbt, a 4-person team, and twice this quarter a stakeholder found a stale dashboard before we did. No monitoring today. dbt tests, Great Expectations, or Monte Carlo?"

- The pain is **the unknown over time** (staleness nobody was watching), not a broken row-rule — so **monitors first**, tests second.
- Already-on-dbt + small team + want low-lift anomaly monitors → **Elementary** for freshness/volume/anomaly monitors on top of the existing dbt project, plus **dbt tests** (and dbt-expectations) for the known rules on the key marts. Hold **Monte Carlo** as the buy option *if* the estate and budget grow — don't lead with it before the ROI basics exist.
- **Where checks run:** dbt tests in-transform; Elementary monitors as independent scheduled monitors on production.
- **Block-vs-warn:** the revenue mart's freshness monitor **blocks** the downstream refresh; a low-stakes staging distribution check **warns**.
- **SLA:** "revenue mart ≤ 2h behind source, owner = analytics on-call."
- **Flip condition:** if the team leaves dbt or the estate grows past what two people can watch, revisit for a managed platform (Monte Carlo / Bigeye / Metaplane).

## Guardrails

- Never name a tool before traversing the tree — approach before brand.
- Never sequence 200 column tests ahead of freshness + volume monitors (highest-ROI first).
- A contract that blocks nothing is aspirational — say so and put it at the producer boundary, enforced.
- Block-vs-warn is a per-check decision, not a global default; weigh harm against stall cost.
- Governance questions (who may access, PII, retention) are **not** DQ — route to `data-governance-privacy`.
- Volatile claims (platform features, pricing, connector coverage) carry a **retrieval date** and are re-verified before a client commitment. See [`../../knowledge/data-observability-patterns-2026.md`](../../knowledge/data-observability-patterns-2026.md).
