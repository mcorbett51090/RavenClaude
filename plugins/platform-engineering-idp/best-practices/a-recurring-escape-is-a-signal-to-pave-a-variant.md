# A recurring escape is a signal to pave a new variant

**Status:** Pattern
**Domain:** Golden-path maintenance
**Applies to:** `platform-engineering-idp`

---

## Why this exists

The escape hatch is what keeps a golden path from becoming a cage — but if many teams keep taking the
*same* escape, that's not the long tail, it's an unmet common need. Ignoring it leaves a growing
shadow platform; treating it as a violation alienates the teams. The healthy response is to listen:
fold the recurring escape into a new supported variant of the path.

## How to apply

- Instrument escapes — track when and why teams step off the road.
- When an escape recurs across teams, evaluate it as a candidate new paved variant.
- Pave the variant (with its own defaults + escape hatch), shrinking the unsupported surface.

**Do:**

- Treat off-road usage data as roadmap input.
- Pave a second/third supported shape when demand is real.
- Keep each variant as ergonomic as the original path.

**Don't:**

- Punish or forbid escapes (drives them underground).
- Pave a variant for a one-off (that's correctly long tail).
- Let the supported set ossify while real usage drifts off-road.

## Edge cases / when the rule does NOT apply

A genuinely rare or one-team escape should stay an escape — paving it would gold-plate. The trigger is
*recurrence across teams*, not any deviation.

## See also

- [`./pave-the-80-keep-an-escape-hatch.md`](./pave-the-80-keep-an-escape-hatch.md)
- [`../knowledge/platform-engineering-decision-trees.md`](../knowledge/platform-engineering-decision-trees.md)

## Provenance

Codifies the golden-path evolution practice (Spotify/Netflix paved-road retrospectives) that supported
paths expand by observing real developer behavior, not by decree.

---

_Last reviewed: 2026-06-08 by `claude`._
