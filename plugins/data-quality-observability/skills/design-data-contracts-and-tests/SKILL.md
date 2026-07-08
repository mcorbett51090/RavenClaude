---
name: design-data-contracts-and-tests
description: From a dataset and its consumers, derive the producer-boundary data contract (schema, semantics, freshness and volume expectations, ownership) and the concrete validation test suite (not-null, unique, accepted-values, referential integrity, distribution/value-range), each test carrying a severity. Reach for this when the user asks "write the data contract for this table", "what tests should this dataset have?", or "define the guarantees this producer owes its consumers". Used by `data-quality-architect` and `data-quality-engineer`.
---

# Skill: design-data-contracts-and-tests

> **Invoked by:** `data-quality-engineer` (primary, to author) and `data-quality-architect` (to shape the contract before the tool is fixed).
>
> **When to invoke:** "Write the data contract for <dataset>"; "what tests should <table> have?"; "what does this producer owe its consumers?"; any move from a dataset to its enforceable guarantees.
>
> **Output:** the producer-boundary contract (schema, semantics, freshness/volume expectations, ownership) + the concrete test suite (not-null / unique / accepted-values / referential / distribution), each test with a severity, captured in the check spec.

## Procedure

1. **Name the dataset, its grain, and its consumers.** One row = what? Which dashboards, models, exports, or downstream teams depend on it? The consumers define what the contract must guarantee — a contract with no named consumer is guessing.
2. **Draft the schema half of the contract.** Columns, types, nullability, primary key / grain, and any enum domains. This is the structural guarantee the producer owes.
3. **Draft the semantic half.** What each column *means*, units, valid ranges, referential relationships, and the freshness + volume expectations ("landed by 05:00 UTC", "row count within ±15% of trailing-7-day mean"). Assign an **owner** — the contract is a producer-boundary promise, so someone must own keeping it.
4. **Derive the test suite from the contract** (don't invent tests unmoored from a guarantee):
   - **not-null** on required columns,
   - **unique** (and grain/primary-key uniqueness),
   - **accepted-values** for enum/domain columns,
   - **referential integrity** for foreign keys (every child has a parent),
   - **distribution / value-range** for the semantic ranges (min/max, non-negative, value-in-range, category-share), using dbt-expectations / GE / Soda as the tool allows.
5. **Assign a severity per test.** Error/block where a failure would corrupt a downstream number; warn where it's informative but not harmful. This feeds the block-vs-warn wiring later.
6. **Place each test:** in-transform (dbt test beside the model) for model-owned rules; post-load gate (GE/Soda checkpoint) where the contract must block promotion of a raw/landed dataset.
7. **Capture it** in [`../../templates/data-quality-check-spec.md`](../../templates/data-quality-check-spec.md) so the contract, tests, severities, placement, owner, and SLA live in one reviewable page.

## Worked example

> User: "Write the contract + tests for `fct_orders`, consumed by the revenue dashboard and the finance export."

- **Grain:** one row per order (`order_id` unique). **Consumers:** revenue dashboard, finance export → the contract must guarantee a trustworthy revenue total.
- **Schema:** `order_id` (string, PK, not null), `customer_id` (string, not null, FK → `dim_customers`), `order_status` (enum: placed/shipped/cancelled/refunded), `order_total` (numeric, ≥ 0), `ordered_at` (timestamp, not null).
- **Semantics/freshness/volume:** `order_total` in the currency's minor units, non-negative; freshness "≤ 2h behind source `ordered_at`"; volume "daily order count within ±20% of trailing-7-day mean". **Owner:** analytics on-call.
- **Tests:** not-null(`order_id`,`customer_id`,`order_total`,`ordered_at`); unique(`order_id`); accepted-values(`order_status`); relationships(`customer_id` → `dim_customers.customer_id`); expression `order_total >= 0` (dbt-expectations `expect_column_values_to_be_between`, min 0). **Severities:** the PK-uniqueness and FK tests **block** (a broken join corrupts the revenue total); the volume check **warns**.
- **Placement:** all in-transform as dbt tests on `fct_orders`, with the freshness/volume expectations promoted to monitors (hand to `set-up-data-observability-monitors`).

## Guardrails

- Every test traces to a contract guarantee; a test with no consumer-facing reason is noise.
- The contract lives at the **producer boundary** and is **enforced** (blocks a merge/promotion) — not parked in a wiki.
- Severity is deliberate per test; not everything blocks. Block where a failure corrupts a downstream number.
- Freshness + volume are **monitors**, not point-in-time tests — cross-reference [`set-up-data-observability-monitors`](../set-up-data-observability-monitors/SKILL.md) rather than faking them as static tests.
- Distribution/range tests need a stated range or baseline, never a magic number pulled from thin air.
- See the patterns reference for the test-vs-monitor line: [`../../knowledge/data-observability-patterns-2026.md`](../../knowledge/data-observability-patterns-2026.md).
