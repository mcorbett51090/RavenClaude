# partnerships-alliances

The **indirect-revenue engine** for a partnerships, alliances, or channel leader — a
team of 3 specialist agents that designs the partner program, structures joint
go-to-market, sizes partner-sourced pipeline honestly, and runs the incentive and QBR
cadence to a P&L.

> Part of the [RavenClaude](https://github.com/mcorbett51090/RavenClaude) marketplace.
> Inherits the domain-neutral protocols in [`ravenclaude-core`](../ravenclaude-core/).
> Requires `ravenclaude-core@>=0.7.0`.

## Who it's for

A head of partnerships / alliances / channel who owns a **partner-sourced or
partner-influenced revenue number** and needs a working program — not a "what is a
partnership" tutorial. If you own direct-sales forecast and comp, that's
[`sales-revops`](../sales-revops/); technical pre-sales is
[`sales-engineering`](../sales-engineering/); developer/community ecosystem is
[`developer-relations`](../developer-relations/).

## The team

| Agent | Owns |
|---|---|
| [`partnerships-lead`](agents/partnerships-lead.md) | Scoping the partner motion, ecosystem strategy, routing, and the partner plan. |
| [`channel-program-manager`](agents/channel-program-manager.md) | Partner tiering, onboarding & enablement, MDF/incentives, deal registration, QBR cadence. |
| [`alliance-gtm-strategist`](agents/alliance-gtm-strategist.md) | Co-sell/rep-to-rep plays, joint value proposition, ISV/tech alliances, marketplace, partner-sourced pipeline. |

## What it believes (house opinions)

1. Partner-**sourced** ≠ partner-**influenced** — attribute honestly.
2. A partner tier is a set of **obligations**, not a logo wall.
3. Co-sell dies without a **named rep-to-rep** motion.
4. The **joint value proposition** is the product, not the logos.
5. MDF is an **investment with a return**, not a rebate.
6. **Enablement precedes expectation.**
7. **Concentration is a risk** — manage the partner portfolio.
8. **Cite the source and date** for every incentive, margin, and market figure.

See [`CLAUDE.md`](CLAUDE.md) §3 for the full text.

## Skills / commands

| Skill | Command |
|---|---|
| [`build-a-partner-tiering-model`](skills/build-a-partner-tiering-model/SKILL.md) | `/partnerships-alliances:build-a-partner-tiering-model` |
| [`size-partner-sourced-pipeline`](skills/size-partner-sourced-pipeline/SKILL.md) | `/partnerships-alliances:size-partner-sourced-pipeline` |
| [`structure-a-co-sell-motion`](skills/structure-a-co-sell-motion/SKILL.md) | `/partnerships-alliances:structure-a-co-sell-motion` |
| [`design-an-mdf-program`](skills/design-an-mdf-program/SKILL.md) | `/partnerships-alliances:design-an-mdf-program` |

## Knowledge bank

- [`knowledge/partnerships-kpi-glossary.md`](knowledge/partnerships-kpi-glossary.md)
- [`knowledge/partnership-economics.md`](knowledge/partnership-economics.md)
- [`knowledge/partnerships-decision-trees.md`](knowledge/partnerships-decision-trees.md) (Mermaid decision trees)

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install partnerships-alliances@ravenclaude
```

## Scope & disclaimer

Operations and GTM decision-support, **not** legal, tax, or antitrust advice. Partner-margin
norms, MDF rates, marketplace fees, and incentive/channel-conflict/antitrust rules are
volatile and jurisdictional — every such figure carries a retrieval date + `[verify-at-use]`,
and legal terms route to counsel. No partner PII.
