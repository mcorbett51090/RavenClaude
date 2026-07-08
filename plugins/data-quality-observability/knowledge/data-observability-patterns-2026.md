# Knowledge — Data-observability patterns (2026)

> **Last reviewed:** 2026-07-08 · **Confidence:** High on the durable concepts (the 5 pillars, test-vs-monitor, circuit-breaker/quarantine, SLAs/SLIs, incident severity); **Medium on the dated tooling map — platform features and pricing are volatile and carry retrieval dates below.**
> The reference the `data-quality-engineer` reads when building and operating checks: the pillars, the test-vs-monitor line, containment patterns, anomaly-detection approaches, DQ SLAs/SLIs, incident severity, and a 2026 tooling snapshot.

The team's discipline: **assert the known with tests, watch the unknown with monitors, give every check an owner + severity, anchor every monitor to a baseline + tolerance, and root-cause an incident to the CHANGE.**

---

## The 5 pillars of data observability

| Pillar | Watches | Typical failure it catches |
|---|---|---|
| **Freshness** | How recent the data is vs its expected cadence | A pipeline silently stopped; a stakeholder sees stale numbers |
| **Volume** | Row count / bytes per load vs a baseline | A partial load, a dropped partition, a doubled backfill |
| **Schema** | Columns, types, nullability at the boundary | A silent upstream column rename/drop — the #1 root cause |
| **Distribution** | The shape of the values (mean, ranges, category share, null rate) | A logic bug or source change that keeps volume/schema intact but corrupts values |
| **Lineage** | Upstream→downstream dependencies | Blast radius: which dashboards/models go stale when this breaks |

Freshness + volume are the **highest-ROI** pair — cheap to run, they catch most real incidents. Schema + distribution catch the subtler corruptions. Lineage is what turns an alert into a *scoped* incident.

---

## Test vs monitor — the core distinction

- A **test** asserts a **known rule at a point in time**: not-null, unique, referential integrity, accepted-values, a value in a fixed range. It answers "does this violate a rule we already know?" It runs when the data is built/loaded and passes or fails deterministically.
- A **monitor** watches for the **unknown over time**: freshness slipping, volume drifting, schema changing, a distribution shifting. It answers "is something *different* from normal?" It needs a **baseline** (what normal looks like) and a **tolerance** (how far off is too far).

You need both. Tests alone are blind to the anomalies nobody wrote a rule for; monitors alone can't enforce the hard rules a contract guarantees. **A test is your known-knowns; a monitor is your known-unknowns.**

---

## Containment patterns: circuit-breaker & quarantine

When a check fails, the response is a design choice, not a reflex:

- **Circuit-breaker (block).** The check **fails the pipeline** so bad data never reaches downstream. Use it where **downstream harm > pipeline-stall cost** — e.g. a broken PK on the revenue mart. A write-audit-publish (WAP) pattern is the clean implementation: write to a staging location, *audit* with the checks, and only *publish* (swap/promote) if they pass.
- **Quarantine.** Route the bad rows/partition to a side location, let the good data flow, and flag the quarantined slice for correction. Use it when partial data is better than none and the bad subset is separable.
- **Warn.** Log/alert but let the run proceed. Use it for informative-but-not-harmful signals where a stall would cost more than the anomaly.

The rule: **block-vs-warn (vs quarantine) is decided per check by weighing downstream harm against stall cost** — never a global default.

---

## Anomaly-detection approaches: threshold vs statistical/ML

| Approach | Use when | Trade-off |
|---|---|---|
| **Threshold / rule** | The acceptable band is known and **stable** (e.g. "null rate < 1%") | Simple, explainable; brittle if the metric legitimately moves — false alarms |
| **Statistical (rolling baseline, z-score/σ, IQR)** | The metric drifts but is roughly stationary | Adapts to level; needs enough history; can miss seasonality |
| **ML / seasonality-aware** | The metric has weekly/daily seasonality or trend (e.g. weekend order dips) | Fewer false alarms on moving metrics; opaquer, needs a platform or a model to maintain |

Every anomaly monitor needs a **baseline + a tolerance** — a hard-coded magic number (`count > 1000`) is a false-alarm factory. Choose the detector to match how the metric actually behaves: static band for stable, seasonality-aware for moving.

---

## Data-quality SLAs & SLIs

Treat data quality like a service:

- **SLIs** (what you measure): **freshness** (lag behind event/source time), **completeness** (row count / null rate vs baseline), **validity** (% rows passing the contract's rules), and **uptime** of the checks themselves.
- **SLAs** (the promise): e.g. "the revenue mart is ≤ 2h behind source, 99% of business days" — each with a **named owner** and an **escalation path**. An SLA with no owner is a slogan.
- **SLOs/error budgets:** allow a bounded number of misses before it's a program problem, so a single blip doesn't page at 3am but a pattern does.

---

## Incident severity

| Severity | Trigger | Response |
|---|---|---|
| **Sev-1** | A trusted, business-facing number is wrong or stale (revenue, exec dashboard, regulatory report) | Page now; contain (circuit-break/quarantine); comms to consumers; run the runbook to correction |
| **Sev-2** | A non-critical dataset wrong/stale, or a critical one at risk | Same-day triage + fix; monitor for escalation |
| **Sev-3** | A warn-level anomaly, a low-stakes dataset, or a caught-at-gate issue | Ticket + fix in normal flow; add a prevent step |

Severity drives the response and who gets paged — it's set when the monitor is authored, not improvised during the fire.

---

## Root-causing a bad-data incident — to the CHANGE

Every bad-data incident traces to a **change**, not just a symptom. The four usual suspects:

1. **Schema change** — an upstream column renamed/dropped/retyped (the most common; a schema-drift monitor catches it at the seam).
2. **Upstream source change** — the source system's own data changed (new category, a backfill, a definition shift).
3. **Transform-logic change** — a dbt/SQL change altered the numbers (git-blame the model between the last-good and first-bad run).
4. **Late-arriving / out-of-order data** — the data wasn't wrong, it was *incomplete* when the run fired (a freshness/volume signal, fixed by a re-run once complete).

"Re-run it and see" is not root-causing. Name which change, then the fix follows: revert/patch the logic, adapt to the schema, wait+backfill for late data.

---

## 2026 tooling map (dated — volatile, re-verify before quoting)

- **In-project (dbt world):** dbt tests (not-null/unique/relationships/accepted-values, `severity: warn|error`), **dbt-expectations** (GE-style assertions in dbt), **Elementary** (dbt-native anomaly monitors + UI). _(Retrieved 2026-07-08.)_
- **Framework:** **Great Expectations** (expectation suites, checkpoints, data docs) for Python pipelines; **Soda Core / Soda Cloud** (SodaCL YAML checks + monitoring UI), warehouse-native. _(Retrieved 2026-07-08.)_
- **Managed observability platforms:** **Monte Carlo**, **Bigeye**, **Metaplane** — automated freshness/volume/schema/anomaly coverage + column-level lineage, ML anomaly detection, incident workflows. Feature depth, pricing, and connector coverage **vary and change** — treat as a 2026-07 snapshot and re-verify with `ravenclaude-core/deep-researcher` before a client commitment. _(Retrieved 2026-07-08.)_
- **Warehouse-native:** constraints + `SELECT`-assertion checks (Snowflake/BigQuery/Databricks) for a quick gate with no new tool.

---

## Provenance

- Durable concepts (5 pillars, test-vs-monitor, WAP/circuit-breaker/quarantine, SLIs/SLAs, incident severity, root-cause-to-change) are consensus practice across the observability literature, reviewed 2026-07-08 — **High confidence**.
- The tooling map is a **2026-07 snapshot**; platform features/pricing/connectors are volatile and carry the retrieval dates above — re-verify before pinning in a deliverable.
