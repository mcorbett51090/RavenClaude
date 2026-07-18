# corporate-development-ma

A **buy-side deal team** for a corp-dev, strategy, or finance lead — 3 specialist agents
that frame the deal thesis before the model, triangulate a valuation, run diligence to
confirm or kill the thesis, and price the integration that captures the value.

> Part of the [RavenClaude](https://github.com/mcorbett51090/RavenClaude) marketplace.
> Inherits the domain-neutral protocols in [`ravenclaude-core`](../ravenclaude-core/).
> Requires `ravenclaude-core@>=0.7.0`.

## Who it's for

A corp-dev lead, strategy/finance executive, or founder-operator running an acquisition
who owns **a deal and a return** — not a "what is M&A" tutorial. If you're raising capital
as an issuer, that's [`startup-fundraising`](../startup-fundraising/); ongoing FP&A is
[`finance`](../finance/); cash/debt/hedging is [`treasury-management`](../treasury-management/).

## The team

| Agent | Owns |
|---|---|
| [`corpdev-lead`](agents/corpdev-lead.md) | The thesis, sourcing/screening, valuation framing, deal structure, IC memo synthesis. |
| [`ma-diligence-lead`](agents/ma-diligence-lead.md) | The confirm-or-kill diligence plan, quality-of-earnings reading, red-flag escalation. |
| [`integration-pmi-strategist`](agents/integration-pmi-strategist.md) | Owner/date synergy planning, the operating model, the 100-day plan, retention, integration-risk pricing. |

## What it believes (house opinions)

1. The **thesis precedes the model**.
2. Value = standalone + **synergies − integration cost − control premium**.
3. **Synergies are a plan** with an owner and a date, not a line item.
4. **Triangulate** valuation — one method is an opinion.
5. **Diligence confirms or kills** the thesis; it is not a checklist.
6. **Integration risk is priced pre-signing** or paid post-close.
7. **Culture and key-person retention** are diligence items, not soft stuff.
8. **Cite the source and date** for every comp, multiple, and market figure.

See [`CLAUDE.md`](CLAUDE.md) §3 for the full text.

## Skills / commands

| Skill | Command |
|---|---|
| [`frame-a-deal-thesis`](skills/frame-a-deal-thesis/SKILL.md) | `/corporate-development-ma:frame-a-deal-thesis` |
| [`triangulate-a-valuation`](skills/triangulate-a-valuation/SKILL.md) | `/corporate-development-ma:triangulate-a-valuation` |
| [`run-a-diligence-plan`](skills/run-a-diligence-plan/SKILL.md) | `/corporate-development-ma:run-a-diligence-plan` |
| [`plan-post-merger-integration`](skills/plan-post-merger-integration/SKILL.md) | `/corporate-development-ma:plan-post-merger-integration` |

## Knowledge bank

- [`knowledge/ma-kpi-glossary.md`](knowledge/ma-kpi-glossary.md)
- [`knowledge/ma-valuation-and-deal-economics.md`](knowledge/ma-valuation-and-deal-economics.md)
- [`knowledge/ma-decision-trees.md`](knowledge/ma-decision-trees.md) (Mermaid decision trees)

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install corporate-development-ma@ravenclaude
```

## Scope & disclaimer

Strategic and financial decision-support — **not** legal, tax, or accounting advice, and
**not** a fairness opinion or a formal valuation. Multiples, transaction comps, and
regulatory thresholds are volatile and jurisdictional — every such figure carries a
retrieval date + `[verify-at-use]`. No material non-public information the user isn't
authorized to hold. Legal → counsel; audited numbers → accountants; a fairness opinion → a banker.
