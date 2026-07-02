# Build the group block before you sell it

**Status:** Pattern
**Domain:** Group operations
**Applies to:** `travel-agency-tour-operations`

> Advisory operations rule. Block terms — deposit, cutoff, attrition, tour-conductor comps — are supplier-contract-specific and `[verify-at-use]`. No traveler PII.

---

## Why this exists

A group is a **contracted liability**, not twelve independent bookings. When you hold a room or seat block, you commit to deposits, a **cutoff date** (when unsold inventory releases), and **attrition** (a percentage you owe even if it goes unsold). Selling against a block you haven't contracted — or over-blocking on optimism — either leaves you unable to deliver the promised rate/inventory or stuck paying attrition on rooms nobody bought. Contracting first turns the group from a gamble into a managed instrument.

## How to apply

- Contract the block **first**: negotiate the rate, deposit, cutoff date, attrition %, and any tour-conductor/comp benefit (`[verify-at-use]`) — traverse the group-vs-FIT tree in [`../knowledge/travel-agency-decision-trees.md`](../knowledge/travel-agency-decision-trees.md).
- **Size the block to real demand.** If you can't confidently fill it, take a smaller block or route travelers as FIT to cap attrition exposure.
- Manage **pickup vs the block** to the cutoff; release unsold inventory before the penalty date.
- Track group deposits and name lists on the supplier's payment cadence.

**Do:** contract before selling; size to demand; manage pickup to cutoff.
**Don't:** promise group rates on an uncontracted block; over-block and eat attrition.

## Edge cases / when the rule does NOT apply

Small parties wanting custom pacing with no shared-block economics are simply FIT — don't force a block where flexibility beats leverage. The rule applies once block economics are actually in play.

## See also

- [`../skills/group-vs-fit-trip-operations/SKILL.md`](../skills/group-vs-fit-trip-operations/SKILL.md)
- Knowledge: [`../knowledge/travel-agency-reference-2026.md`](../knowledge/travel-agency-reference-2026.md)

## Provenance

Codifies `itinerary-and-booking-specialist` house opinion and the group-vs-FIT decision tree. Block terms: [`../knowledge/travel-agency-reference-2026.md`](../knowledge/travel-agency-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
