# Compress time-to-first-value through the train-the-trainer cascade, not direct teacher training

**Status:** Pattern

**Domain:** Onboarding / Time-to-first-value

**Applies to:** `edtech-partner-success`

---

## Why this exists

Time-to-first-value (TTFV) is the most-predictive early renewal signal, and the single biggest lever on it in K-12 is *how* the partner gets trained. Direct vendor-to-teacher training does not scale: a vendor cannot reach every teacher in a district, the calendar won't allow it, and the value clock keeps running while teachers wait for a session that never reaches them. Train-the-trainer is the only model that works at K-12 scale — equip 2-3 partner-side champions deeply, and they run the subsequent waves on the district's own PD schedule. The failure mode (named in the implementation failure modes) is *training cascade collapse*: the vendor trained the champions but the champions never ran the downstream waves, so first-value never lands and the partner stalls past the settling window where adoption patterns set. Compressing TTFV means designing the cascade — and instrumenting whether the waves actually fire — not just delivering a kickoff session.

## How to apply

Design the cascade with named champions, scheduled waves aligned to the district's PD calendar, and a completion signal that proves the waves happened.

```
Train-the-trainer cascade (the TTFV lever):
  1. Identify 2-3 partner-side champions (NOT one — cascade collapses on one departure).
  2. Two-session champion arc: Session 1 product DEPTH, Session 2 facilitation CRAFT.
  3. Schedule downstream waves onto the district's REAL PD windows (in-service days,
     half-day PD, after-school PD) — align to state PD-hour frameworks where they earn credit
     (CA 150/5yr · NY 100/5yr CTLE · FL 120 inservice pts · TX 150 CPE · IL 120 PEL). `[verify-at-build]`
  4. PD modality decision: live-in-person / live-virtual / hybrid / async-with-followup —
     async without a follow-up touchpoint is where cascades quietly die.
  5. INSTRUMENT cascade completion as a leading first-value proxy:
     train-the-trainer completion % + PD-hour progress — visible on the Tuesday dashboard.
  6. Teacher-union overlay in unionized states — PD that consumes contracted time has rules. `[verify-at-build]`
```

**Do:**
- Use train-the-trainer completion as the first-value *proxy* when usage telemetry isn't shareable — a structured proxy beats waiting for data that may never come.
- Watch the settling window (weeks 4-8): if the cascade hasn't fired by then, the adoption pattern is setting without it.

**Don't:**
- Try to scale by training teachers directly — it doesn't reach the room, and the value clock runs out.
- Declare onboarding "done" at champion training; done is when the downstream waves have run and first-value is instrumented.

## Edge cases / when the rule does NOT apply

- **Very small partner** (single school, handful of teachers) — direct training can scale here; the cascade overhead isn't justified.
- **Corporate L&D self-serve** — a mature L&D org may run its own enablement; the vendor supplies the curriculum, not the cascade.
- **Calendar-dead-zone go-live** — a cascade scheduled into late August or the first two weeks of school under-fires; check the arc before committing the dates (the highest-leverage pre-flight check).

## See also

- [`./onboarding-instrument-first-value-from-day-one.md`](./onboarding-instrument-first-value-from-day-one.md) — first-value definition + instrumentation the cascade feeds
- [`./onboarding-sequence-depth-before-breadth-in-stage-one.md`](./onboarding-sequence-depth-before-breadth-in-stage-one.md) — the depth the cascade drives toward
- [`../skills/partner-training-program-design/SKILL.md`](../skills/partner-training-program-design/SKILL.md) — train-the-trainer is the only model that scales; PD modality rule
- [`../knowledge/k12-pd-norms-and-constraints.md`](../knowledge/k12-pd-norms-and-constraints.md) — state PD-hour requirements, district PD windows, union overlay
- [`../knowledge/district-implementation-failure-modes.md`](../knowledge/district-implementation-failure-modes.md) — training-cascade-collapse failure mode
- [`../agents/edtech-partner-success-manager.md`](../agents/edtech-partner-success-manager.md) — owns the implementation arc

## Provenance

Distilled from `skills/partner-training-program-design/SKILL.md` (train-the-trainer-only-model, PD modality rule, union overlay), `knowledge/district-implementation-failure-modes.md` (training-cascade-collapse), `knowledge/k12-pd-norms-and-constraints.md` (state PD-hour frameworks, district PD windows), and `skills/implementation-90-day-arc/SKILL.md` (calendar-dead-zone go-live check). State PD-hour + union specifics marked `[verify-at-build]`. Authored 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
