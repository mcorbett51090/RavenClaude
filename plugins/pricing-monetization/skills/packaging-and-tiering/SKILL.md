---
name: packaging-and-tiering
description: "Design good-better-best packaging where each tier is fenced by a self-selection dimension (scale, use case, support, security) rather than a longer feature list, and separate core from add-ons. Reach for this when turning a feature set into tiers, when customers all pick the cheapest plan, or when tiers differ only by feature count. Pairs with value-metric-design."
---

# Skill: Packaging & Tiering

Packaging turns a value metric and a feature set into the plans a customer chooses
between. Done right, customers **self-select** into the tier that fits them. Done
wrong (tiers separated only by a longer feature list), customers learn to wait for
the cheap plan to grow the feature.

## Step 0 — One opinion up front
**Fencing is the whole game.** A tier boundary must be a dimension the customer
self-selects on — scale, use case, support level, or security/compliance — not just
"more features." If you can't name the fence, the tier isn't a tier.

## Step 1 — Pick the fencing dimension(s)
Choose 1–2 dimensions customers naturally differ on:
- **Scale** — seats, volume, usage allowance (the most common fence)
- **Use case** — starter vs professional vs enterprise workflows
- **Support / SLA** — response times, dedicated CSM
- **Security / compliance / admin** — SSO, audit logs, data residency (a classic
  enterprise fence)

## Step 2 — Build good-better-best
- **Three tiers, occasionally four.** More than four paralyzes the buyer and dilutes
  fencing. If you "need" five, two aren't fenced.
- **Design the middle to win.** The middle tier is usually the intended default;
  fence so most of the target segment lands there. The top anchors; the bottom
  captures price-sensitive buyers.
- **Place each feature deliberately** — a feature in the bottom tier should be one
  you're happy giving the price-sensitive segment; a fence feature (SSO, advanced
  security) belongs at the tier that gates the upgrade.

## Step 3 — Separate add-ons from tiers
Features only *some* customers value belong as **add-ons**, not as a reason to spawn
a fourth tier. Add-ons let you monetize the long tail without complicating the core
ladder.

## Step 4 — Anchor and decoy deliberately
A visible enterprise/"contact us" tier reframes the middle as reasonable — but only
with a *real* fence behind it (custom security, volume, SLA). "Contact us" to hide a
number you haven't decided is a tell, not a strategy.

## Step 5 — Pressure-test
- Does each tier boundary have a nameable fence? (If not, fix it.)
- Would a customer who *should* be in the top tier be tempted to under-buy the
  middle? (Tighten the fence.)
- Does the bottom tier cannibalize the middle? (Move a key feature up.)

## Output
A tier table (tier × fence × included value-metric allowance × key features), the
add-on list, and the self-selection logic — i.e. *why* each target customer lands in
the tier you intend. Hand WTP validation of the tier prices to
`willingness-to-pay-research`.
