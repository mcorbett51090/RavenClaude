# DTC margin beats wholesale but doesn't scale like it

**Status:** Pattern
**Domain:** Channel strategy
**Applies to:** `craft-beverage-operations`

> Operations rule. No PII. Channel-margin benchmarks are `[verify-at-use]`.

---

## Why this exists

The channel-mix decision is the margin decision, and most producers under-manage it. DTC (tasting room, club, e-commerce) keeps the full retail margin; wholesale gives it away — the distributor **and** the retailer each take a cut — but moves volume DTC can't. The trade is real: DTC margin vs wholesale scale. You optimize it by allocating production on net margin per channel against the demand each can absorb.

## How to apply

- Compute **net** margin per channel on the true COGS per unit — wholesale after distributor and retailer take, not gross price.
- Grow DTC demand (conversion, club) before defaulting to wholesale for volume.
- Use wholesale for reach/volume once DTC demand is tapped — with eyes open to franchise-law lock-in.
- Allocate production on net margin × absorbable demand.

**Do:** allocate on net margin and absorbable demand; grow DTC demand first.
**Don't:** default to wholesale for growth without reading the margin given away; compare channels on gross price.

## Edge cases / when the rule does NOT apply

A brand-awareness or market-entry play may accept low wholesale margin to build presence — a deliberate choice, made knowing the margin trade.

## See also

- [`../skills/three-tier-and-self-distribution-economics/SKILL.md`](../skills/three-tier-and-self-distribution-economics/SKILL.md)
- [`the-club-is-the-recurring-revenue-engine.md`](./the-club-is-the-recurring-revenue-engine.md)

## Provenance

Codifies the `craft-beverage-operations-lead` and `tasting-room-and-club-manager` house opinions and the channel-mix decision tree. Benchmarks: [`../knowledge/craft-beverage-reference-2026.md`](../knowledge/craft-beverage-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-04 by `claude`_
