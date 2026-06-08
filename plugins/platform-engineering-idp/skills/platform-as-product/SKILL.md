---
name: platform-as-product
description: "Run the platform as a product: decide whether to start a platform team, scope the thinnest viable platform, pick the Team-Topologies model, run developer user-research, build an adoption strategy, and assess platform maturity (ad-hoc -> paved-road -> self-service -> product)."
---

# Platform as a Product

**Purpose:** treat the internal platform as a product with developers as customers, so it earns
adoption instead of mandating it.

## The operating loop

1. **Find the pain.** Talk to stream-aligned teams; find the recurring, high-frequency friction (the
   developer journey, not a feature wish-list).
2. **Scope the thinnest viable platform.** Pave the single highest `frequency × pain × #teams`
   journey first. One paved road that one team loves beats a portal nobody opens.
3. **Pick the team model (Team Topologies).** Platform group (owns paved roads as products), enabling
   team (teaches/uplifts), stream-aligned (the customers). The platform team reduces *others'*
   cognitive load — that's the whole charter.
4. **Build vs buy.** Buy/adopt before building (managed portal); build (Backstage) before
   frameworking; below ~3 teams, a template beats a team. Traverse the buy-vs-build tree.
5. **Earn adoption.** Be the easy path; dogfood; land one happy team and let pull spread it. Never
   mandate — a mandate hides the product failure.
6. **Measure outcomes.** Adoption, time-to-prod, reported friction — not features shipped. Hand off to
   `devex-measurement`.

## Maturity ladder

`Ad-hoc -> Paved road -> Self-service -> Platform-as-product` — see the maturity table in
[`../../knowledge/platform-engineering-decision-trees.md`](../../knowledge/platform-engineering-decision-trees.md).
Assess honestly; pick the 2-3 moves to the next rung.

## Anti-patterns

- Mandating adoption instead of earning it.
- A grand portal before one golden path is worth paving.
- KPIs measured in platform features instead of developer outcomes.
- Modeling the whole org's catalog before anyone has a question it answers.

## Output

A go/no-go + thinnest-viable scope + team topology + build-vs-buy, OR a maturity assessment with the
next-rung moves. Use [`../../templates/platform-maturity-scorecard.md`](../../templates/platform-maturity-scorecard.md).
