---
description: "Assess platform maturity (ad-hoc -> paved-road -> self-service -> product), name the cognitive load to remove next, and produce the 2-3 highest-leverage moves to the next rung."
argument-hint: "[context, e.g. '8 teams, one paved-road template, infra by ticket, no portal']"
---

You are running `/platform-engineering-idp:assess-platform-maturity`. Use the `platform-product-lead`
discipline and the `platform-as-product` skill.

## Steps

1. Place the org honestly on the maturity ladder (ad-hoc / paved-road / self-service / product) using
   the table in `knowledge/platform-engineering-decision-trees.md`.
2. Name the single highest `frequency × pain × #teams` developer journey still unaddressed.
3. Decide build-vs-buy / what-to-own-first via the relevant decision trees.
4. Output the 2-3 highest-leverage moves to the next rung, each tied to the cognitive load it removes
   and an adoption (not feature-count) goal.
5. Fill `templates/platform-maturity-scorecard.md`, then emit the Structured Output block with
   handoffs (idp-portal-engineer / golden-path-engineer / devex-metrics-engineer).
