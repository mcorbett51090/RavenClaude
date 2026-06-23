# Sequence onboarding for depth before breadth — 2-3 workflows at 80%, not 10 at 20%

**Status:** Pattern

**Domain:** Onboarding / Adoption sequencing

**Applies to:** `edtech-partner-success`

---

## Why this exists

A newly-implemented partner has finite teacher attention in the opening weeks, and how that attention is spent in the settling window (K-12 Phase 2, weeks 4-8) sets the adoption pattern that usually persists for the year. The most common onboarding failure is breadth-chasing: the PSM pushes ten features so the dashboard looks full, teachers touch each one once, and nothing reaches the depth that predicts renewal. Depth-of-feature adoption is a leading renewal signal; usage breadth is a vanity metric that can rise while the partner is failing. The plugin's house opinion is explicit — five active users using three deep features beats fifty users opening the app once — and the stage-1 rule is **do NOT push feature breadth in stage 1.**

## How to apply

Pick 2-3 high-value workflows, drive them to real depth on real class data, and defer the rest until the first wave is habitual.

```
Stage-1 onboarding sequence (newly-implemented partner):
  1. Pick 2-3 workflows tied to the partner's STATED goal (verbatim, from the profile),
     not the feature list the product team is proudest of.
  2. Target depth: each chosen workflow run on real class data, repeatedly, by the
     trained champions — "80%+ depth on 2-3" beats "20% on 10".
  3. Defer breadth: every other feature is a stage-2/3 expansion, not a stage-1 task.
  4. Instrument depth-of-adoption TREND (rising/falling) as the first-value signal,
     not a cumulative login count.
  5. Re-baseline at the settling window (weeks 4-8): is the pattern set? If thin,
     diagnose root cause (worksheet) BEFORE adding more surface.
```

**Do:**
- Tie each chosen workflow to a partner-stated goal captured verbatim by the `partner-profile-curator`.
- Run the train-the-trainer model — direct vendor-to-teacher training does not scale in K-12; equip 2-3 champions to run the waves.
- Read stage-1 health through the adoption-arc overlay: modest numbers are normal early, not a recovery trigger.

**Don't:**
- Light up ten surfaces to make the Tuesday dashboard look busy — breadth-without-depth reads as adoption and isn't.
- Run a generic recovery play on a stage-1 partner whose modest metrics are normal for the arc (that reads as "you're already a failure").

## Edge cases / when the rule does NOT apply

- **Re-implementation of an existing partner** — they already know the deep workflows; sequence for continuity, not first-depth.
- **Compliance-training corporate L&D** — "value" may be an externally-mandated completion floor across the full surface; breadth IS the goal there, by mandate.
- **Multi-school district pilot** — depth is measured at the pilot-cohort scale first, then re-baselined at full rollout; don't read pilot depth as district depth.

## See also

- [`./onboarding-instrument-first-value-from-day-one.md`](./onboarding-instrument-first-value-from-day-one.md) — depth is what first-value measures
- [`./health-design-leading-not-lagging-signals.md`](./health-design-leading-not-lagging-signals.md) — depth-of-adoption trend is the canonical leading signal
- [`../skills/adoption-sequencing-k12/SKILL.md`](../skills/adoption-sequencing-k12/SKILL.md) — the stage 1-4 sequencing rules
- [`../knowledge/k12-adoption-arc-fall-spring-summer.md`](../knowledge/k12-adoption-arc-fall-spring-summer.md) — Phase 2 settling window is the most-predictive period
- [`../agents/edtech-partner-success-manager.md`](../agents/edtech-partner-success-manager.md) — owns the onboarding sequence

## Provenance

Distilled from `skills/adoption-sequencing-k12/SKILL.md` (stage-1 depth-over-breadth, "DO NOT push feature breadth in stage 1"), `knowledge/k12-adoption-arc-fall-spring-summer.md` (Phase 2 most-predictive), and house opinions §3 #10 (don't sell) + the "adoption depth > usage breadth" agent opinion. Authored 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
