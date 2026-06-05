# Lock VFX scope and deliverables before principal photography ends

**Status:** Absolute rule
**Domain:** Film & video production / VFX / post-production
**Applies to:** `film-video-production`

---

## Why this exists

Visual effects work that is scoped and bid after principal photography ends always costs more than VFX scoped before the shoot. The reason is structural: once the footage exists, the VFX supervisor is optimizing around imperfect plates, practical choices already made, and the inevitable "can we fix this in post?" requests that accumulate during production. A VFX scope that is locked before the shoot allows the supervisor to influence practical choices on set — lens selection, green-screen vs. on-location, practical vs. digital elements — that determine the VFX cost. Post-lock scope changes also create a cascade risk in the post dependency chain: VFX-heavy sequences cannot be conformed or color graded until the VFX are delivered, and late-locked VFX are the single most common cause of a slipped delivery date.

## How to apply

Produce a VFX brief before the production design phase is complete:

```
VFX brief — [Project] — [Date] — Version ____

Total estimated VFX shots:       ____
Complexity breakdown:
  Simple (wire removal, cleanup): ____ shots — est. $____ each
  Moderate (environment ext.):    ____ shots — est. $____ each
  Complex (creature / simulation): ____ shots — est. $____ each
  Hero (title sequence / key FX): ____ shots — est. $____ each

Scenes requiring VFX supervision on set:
  Scene # | Date | Requirement
  _______ | ____ | ___________

On-set capture requirements (markers, LiDAR, HDRI, witness cameras):
  ____

VFX house (if selected):          ____
Bid received:                     Y/N — dated: ____
VFX delivery date to post:        ____
Post critical-path dependency:    Conform / Color can begin after: ____
```

Lock this scope before the shoot begins. Any scope change after principal photography wraps requires a revised bid and a critical-path impact assessment.

**Do:**
- Include the VFX supervisor in the production design phase, not just in post — on-set decisions made without VFX input are the primary source of post-production cost overruns.
- Build VFX delivery as a hard gate in the post schedule, with a published date that the color and sound teams can plan around.
- Budget VFX per-shot bids, not as a lump "VFX contingency" line — lump-sum VFX estimates are almost always understated.

**Don't:**
- Defer VFX scope until the offline edit is cut — by then, the most expensive "can we fix this in post?" decisions have already been made on set.
- Allow the director to add VFX requests during the offline edit without a formal scope change and bid update; undocumented VFX additions are the fastest way to break a post budget.
- Forget to include on-set VFX supervisor day rates in the below-the-line budget; VFX supervision is a production cost, not a post cost.

## Edge cases / when the rule does NOT apply

- Minimally edited documentary projects without planned VFX are exempt; however, if on-location environments reveal an unexpected VFX opportunity (e.g., drone footage that needs sky replacement), scope it and bid it before cutting it in.
- Commercial spots with VFX as the primary creative medium typically scope VFX before any other production element; the rule still applies, but the sequence of work is different.

## See also

- [`../agents/post-production-supervisor.md`](../agents/post-production-supervisor.md) — owns the VFX schedule gate and the post dependency chain.
- [`../agents/line-producer.md`](../agents/line-producer.md) — budgets VFX from the brief as a distinct cost account.
- [`./post-is-a-dependency-chain-sequence-it-dont-parallelize-blin.md`](./post-is-a-dependency-chain-sequence-it-dont-parallelize-blin.md) — VFX delivery is the critical gate in the dependency chain this rule protects.

## Provenance

Derived from VFX production management practice and post-production scheduling methodology. `[unverified — training knowledge]` — validate VFX per-shot cost estimates with a current bid from a qualified VFX house.

---

_Last reviewed: 2026-06-05 by `claude`_
