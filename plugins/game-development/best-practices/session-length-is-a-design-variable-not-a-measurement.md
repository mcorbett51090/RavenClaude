# Session length is a design variable, not a measurement

**Status:** Pattern
**Domain:** Game design and retention
**Applies to:** `game-development`

---

## Why this exists

Most game teams measure average session length as a health metric after launch without having designed for a target session length before launch. This inverts the relationship. Session length — how long a player intends to play per sitting — is a design constraint that drives almost every downstream decision: the duration of the core loop, the length of a tutorial segment, the pacing of content reveals, the length of a match or level, and the frequency of natural save points. A mobile game targeting commute-length sessions (8–12 minutes) has fundamentally different loop design requirements than a console game targeting couch-evening sessions (45–90 minutes). Measuring first without designing invites the worst failure mode: a session length that doesn't match the target player context, discovered post-launch.

## How to apply

Define the target session length at the start of core-loop design. Use it as a constraint to size every loop, level, and content beat.

```
Session-length design framework:

  Step 1: Define the target context.
    — Mobile commute: 5–12 minutes
    — Mobile casual: 10–20 minutes
    — PC/console lunch break: 20–45 minutes
    — PC/console evening session: 45–90+ minutes

  Step 2: Map target session length to loop cadence.
    — One core loop iteration should fit in ~25–35% of target session length
      so a player completes 3–4 loops per session (the "just one more" trigger)
    — Example: 15-min session → core loop ~4–5 minutes per iteration

  Step 3: Design the exit-point density.
    — Natural, guilt-free exit points (end of level, save point, round end) appear
      at the target session length AND at 50% of the target (early exit option)

  Step 4: Validate in the vertical slice.
    — Playtest timer: what is the actual session length distribution in the slice?
    — If median is > 30% above target: loop is too long or exit points are too sparse.
    — If median is > 30% below target: loop is too short or players are losing interest.
```

**Do:**
- State the target session length in the design document as a constraint, not a goal.
- Build the tutorial to fit within one target session (or less, for mobile).
- Add an early-exit option at 50% of the target session so casual players don't feel trapped.

**Don't:**
- Design level length by "what feels right" without timing playtests against a target.
- Treat average session length as a pure measurement; it is a designed outcome first.
- Launch without at least one playtest that explicitly measures session distribution.

## Edge cases / when the rule does NOT apply

Idle and incremental games have session lengths measured in seconds (the check-in loop) alongside background session "presence"; the design constraint is the check-in frequency, not a continuous-session length. Competitive e-sports titles with match-based structures have session lengths that are match multiples — design for match length, not arbitrary session targets.

## See also

- [`../agents/game-designer.md`](../agents/game-designer.md) — owns core-loop and progression design where session-length targets must be embedded.
- [`./the-core-loop-is-the-product-design-it-before-the-features.md`](./the-core-loop-is-the-product-design-it-before-the-features.md) — the parent rule that session length constrains.

## Provenance

Codifies a standard game-design practice; the measurement-first inversion is the most common pattern in teams that skipped explicit session-length targeting at design time and discovered the mismatch in post-launch analytics.

---

_Last reviewed: 2026-06-05 by `claude`_
