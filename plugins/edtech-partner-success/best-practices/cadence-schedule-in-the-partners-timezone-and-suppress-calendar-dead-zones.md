# Schedule in the partner's time zone and suppress signals during calendar dead zones

**Status:** Pattern

**Domain:** Operating cadence / Segment-aware timing

**Applies to:** `edtech-partner-success`

---

## Why this exists

Touchpoint cadence is segment-aware (house opinion §3 #6), and two timing mistakes generate most cross-book noise. The first is scheduling in the PSM's time zone: a Friday 5 PM PT message to an East-Coast partner lands at their 8 PM and isn't read until Monday morning — ~64 hours later by the PSM clock — so a "no response in 48 hours" decay rule fires a false alarm. The second is reading silence during a known dead zone as disengagement: K-12 districts are unreachable for roughly 40% of the calendar year (late August, the first two weeks of school, Thanksgiving week, winter and spring break, state testing windows, end-of-year wrap-up), and a red-flag play firing at Day 5 of winter break is noise, not signal. The same calendar-blindness wrong-first-pick recurs: PSM sees a December usage drop, fires a recovery play, partner replies "we were on break," score recovers in mid-January on its own, and the PSM has spent credibility.

## How to apply

Surface partner-local time first on every touchpoint, and gate every "no response in N" signal behind the segment dead-zone calendar.

```
Cadence discipline:
  TIME ZONE — schedule in the PARTNER's local TZ; partner-local time is the primary
              surface, PSM-local is parenthetical. Default meeting window:
              10 AM - 2 PM partner-local (mid-day calls land best).
              Subtract weekend + evening hours in partner-local TZ before calling a
              signal "stale".
  DEAD-ZONE SUPPRESSION — suppress no-response decay + proactive asks during:
              late Aug · first 2 weeks of school · Thanksgiving week · winter break ·
              spring break · state testing windows · end-of-year wrap-up.
              When a pulse request lands mid-dead-zone, the response must say so:
              "partner is in [dead zone] — no-response signal unreliable; re-eval at [date]."
  PER-PARTNER CADENCE (default, in the profile):
              weekly async pulse / monthly sync / quarterly QBR / annual review.
              top-quartile health → may compress to bi-monthly.
              active recovery     → upgrades to twice-weekly.
  QUARTERLY — Q3 (Feb-Apr) is the K-12 renewal-build window; shift to weekly renewal prep.
              Friday PM + Monday AM are reactive-only; don't draw conclusions from Friday silence.
```

**Do:**
- Store the default cadence + TZ + dead-zone status in the durable profile (via `partner-profile-curator`) and read it before scheduling.
- Apply the dead-zone overlay to health-score decay so a seasonal dip doesn't trigger a false yellow.

**Don't:**
- Let a play with a "trigger if no response in N hours" condition fire without the dead-zone + weekend overlay.
- Push a QBR or expansion ask into late August, a testing window, or a break — move it.

## Edge cases / when the rule does NOT apply

- **Genuine emergency / support escalation** — reactive support runs even in dead zones; the suppression is for *proactive* PSM-driven signals, not partner-initiated incidents.
- **Higher-ed / corporate L&D** — the dead zones differ (finals weeks; fiscal-year-end + December close); use the segment's own calendar, not the K-12 one.
- **Time-zone-homogeneous single-state book** — the TZ rule is a no-op, but the dead-zone suppression still applies.

## See also

- [`./renewal-start-the-k12-clock-at-180-days-not-90.md`](./renewal-start-the-k12-clock-at-180-days-not-90.md) — the renewal clock rides on this calendar
- [`./risk-early-warning-fire-the-save-play-while-it-still-saves.md`](./risk-early-warning-fire-the-save-play-while-it-still-saves.md) — the suppress-check is step 0 of the save play
- [`../knowledge/k12-psm-operating-cadence.md`](../knowledge/k12-psm-operating-cadence.md) — TZ discipline, dead-zone table, signals-by-rhythm, per-partner cadence
- [`../knowledge/k12-adoption-arc-fall-spring-summer.md`](../knowledge/k12-adoption-arc-fall-spring-summer.md) — Phase 4 (Thanksgiving-Jan 2) dead zone
- [`../agents/edtech-partner-success-manager.md`](../agents/edtech-partner-success-manager.md) — owns touchpoint scheduling; `success-playbook-designer` owns trigger suppression

## Provenance

Distilled from `knowledge/k12-psm-operating-cadence.md` (TZ discipline, dead-zone table, signals-by-rhythm, per-partner cadence, Q3 renewal-build), `knowledge/partner-health-decline-which-play.md` (calendar-blindness wrong-first-pick / SUPPRESS branch), and house opinion §3 #6. Authored 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
