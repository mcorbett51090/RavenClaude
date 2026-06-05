---
scenario_id: 2026-06-05-unit-economics-contribution-margin-teardown
contributed_at: 2026-06-05
plugin: finance
product: fpa
product_version: "n/a"
scope: segment-specific
tags: [saas, unit-economics, cac, ltv, contribution-margin, rule-of-40]
confidence: medium
---

## Problem

A SaaS company was raising and the pitch leaned on a headline "3:1 LTV:CAC" and a Rule-of-40 score that cleared 40%. A diligence-style read found the LTV:CAC was computed on **revenue** (not gross-margin) LTV, the CAC excluded a chunk of sales comp and all marketing tooling, and the Rule-of-40 used an EBITDA margin that added back items a buyer wouldn't. The "good" unit economics were a definitional artifact. The risk: defending a number in diligence that falls apart under one question, or — worse — steering spend off a ratio that's measuring the wrong thing.

## Context

- Segment: B2B SaaS, ~$10–50M ARR band (growth stage), subscription + usage, one currency.
- Constraint: every metric in scope (LTV, CAC, NRR, payback, Rule of 40, burn multiple, magic number) is **definition-sensitive** — small framing choices swing each by tens of percent, and "one source of truth per metric" (§3 #8) was not being enforced. Sales and finance were quoting different CAC.
- Pressure was to keep the flattering numbers for the raise rather than restate to a defensible basis.

## Attempts

- Tried: restated **LTV on gross margin, not revenue** (LTV = ARPA × gross-margin% ÷ churn), and built CAC **fully loaded** (all sales + marketing comp, tooling, and allocated overhead) — the two most common inflators. Outcome: the 3:1 compressed materially; still positive, but a different story.
- Tried: separated **CAC payback** (months of gross profit to recover CAC) from the LTV:CAC ratio and read it against stage benchmarks rather than an absolute. Outcome: payback sat above the growth-stage target band, flagging an efficiency issue the ratio alone had hidden.
- Tried: recomputed **Rule of 40, NRR, burn multiple, and the magic number** on consistent, buyer-defensible definitions, each with a written definition and one owner. Outcome: NRR was the genuinely strong metric and became the lead of the narrative; the Rule-of-40 score landed lower but honest, and the burn multiple exposed the real capital-efficiency question.

## Resolution

The deliverable was a unit-economics pack where every metric carried its definition, its data lineage, and one owner — gross-margin LTV, fully-loaded CAC, payback in months, NRR, Rule of 40, burn multiple, magic number — restated to a basis that survives diligence. The honest pack was *more* fundable than the flattering one because NRR (the compounding metric) was real and the team could defend every number under questioning. The flattering version would have cost credibility on the first hard question.

**Action for the next analyst hitting this pattern:** **define the metric before you compute it, and use one definition per metric (§3 #8).** LTV is gross-margin-based, not revenue; CAC is fully loaded; read CAC payback in months *separately* from the LTV:CAC ratio; recompute Rule of 40 / NRR / burn multiple / magic number on buyer-defensible bases and read each against *stage* benchmarks, not an absolute. A flattering-but-fragile number loses more in diligence than an honest one. Canonical reference: [`../knowledge/fpa-decision-support-and-unit-economics.md`](../knowledge/fpa-decision-support-and-unit-economics.md) and the [`kpi-definition`](../skills/kpi-definition/SKILL.md) skill. The [`../scripts/finance_calc.py`](../scripts/finance_calc.py) `unit-economics` mode computes gross-margin LTV, payback, and the LTV:CAC ratio with the definitions stated.

**Sources (retrieved 2026-06-05):**
- Benchmarkit — 2025 SaaS performance metrics (NRR, CAC payback, magic number medians): https://www.benchmarkit.ai/2025benchmarks
- Data-Mania — B2B SaaS revenue-efficiency benchmarks (magic number, Rule of 40, NRR by stage): https://www.data-mania.com/blog/b2b-saas-revenue-efficiency-benchmarks-2026-magic-number-rule-of-40-nrr-by-stage/

Stage benchmarks (NRR ~104–106% top-performer median, 120%+ at $50M+ ARR; CAC payback ~12–18 months growth-stage, worsened toward ~20 months median; Rule of 40 cleared by ~11–30% of companies; burn multiple > 3x past $10M ARR is an efficiency problem) are **dated and volatile** — `[verify-at-use]` against the current period and the company's stage before relying on them (§3 #1, §3 #8).
