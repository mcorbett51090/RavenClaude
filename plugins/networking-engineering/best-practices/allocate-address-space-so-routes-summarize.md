# Allocate address space so routes summarize

**Status:** Strong default
**Domain:** Design / IP addressing
**Applies to:** `networking-engineering`

---

## Why this exists

Route summarization is only possible if the addresses underneath a boundary are
*contiguous*. Allocate address space randomly or first-come-first-served and you can
never aggregate — every site leaks dozens of specific routes network-wide, routing
tables bloat, and a single flapping link ripples convergence everywhere. The failure is
silent at build time and expensive to fix later: retrofitting summarization means
renumbering live segments. Hierarchy is a decision you make once, up front, or pay for
forever.

## How to apply

**Do:**
- Allocate top-down: region → site → building/pod → segment, each level a contiguous block that summarizes to one prefix at the boundary above.
- Reserve growth headroom **at the parent level** before handing out leaf subnets.
- Size subnets from real host counts × a growth factor, rounded to a power-of-two prefix — not to tidy round numbers.
- Summarize explicitly at every area/AS/site boundary the allocation allows.

**Don't:**
- Hand out subnets non-contiguously "to save space" — it permanently defeats aggregation.
- Assign a /24 to everything reflexively; size to need with headroom.
- Leave summarization unconfigured when the addressing supports it.

## Edge cases / when the rule does NOT apply

- **Legacy/inherited address space** you can't renumber yet — document the un-summarizable islands and summarize what you can; plan renumbering as debt.
- **Deliberately de-aggregated prefixes for BGP traffic engineering / multi-homing** — a conscious policy exception, not sloppiness. Mark it as such.

## See also
- [`../knowledge/subnetting-and-segmentation-decision-tree.md`](../knowledge/subnetting-and-segmentation-decision-tree.md)
- [`../skills/design-ip-addressing-and-segmentation/SKILL.md`](../skills/design-ip-addressing-and-segmentation/SKILL.md)

## Provenance
Codifies the `network-architect` house opinion "summarization is a design decision, not an afterthought" and hierarchical-addressing best practice. Last reviewed 2026-07-01.

---

_Last reviewed: 2026-07-01 by `claude`_
