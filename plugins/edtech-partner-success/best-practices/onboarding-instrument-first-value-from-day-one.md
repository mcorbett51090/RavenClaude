# Instrument first-value from day one of onboarding, not at the first QBR

**Status:** Pattern

**Domain:** Onboarding / Adoption

**Applies to:** `edtech-partner-success`

---

## Why this exists

Time-to-first-value (TTFV) is the single most-predictive early renewal signal in EdTech, and it is the one most often measured too late to act on. Teams that wait until the first QBR to ask "are they getting value?" discover a stalled implementation 90 days after it stalled — past the K-12 settling window (Phase 2, weeks 4-8) where adoption patterns set and usually persist. The fix is to decide what "first value" means for *this* partner before go-live, instrument the signal on day one, and watch it weekly through the 90-day arc. A success plan whose only success criterion is "they'll be happier" (a §4 anti-pattern) cannot do this; a plan with a named, dated, measurable first-value milestone can.

## How to apply

Define first-value at contract close, instrument it before go-live, and track it on the weekly pulse — not the QBR.

```
First-value definition (fill in BEFORE go-live, store in the success plan):
  Partner: <name>     Segment: <k12 | higher-ed | corp-ld>
  "First value" for THIS partner = <specific observable, e.g. "10 teachers each run
        the reporting workflow on real class data twice">
  NOT "logged in" — logins are not adoption (house opinion: adoption depth > usage breadth)
  Target date: <within the 90-day arc; for K-12, before the Phase 2 settling window closes>
  Instrumented by: <named owner> on: <date signal goes live>
  Leading proxy (if telemetry not shareable): <e.g. train-the-trainer completion %>
```

- Tie the milestone to a partner-stated goal captured verbatim by the `partner-profile-curator`, not an internal KPI.
- Make the first-value signal visible on the Tuesday-morning dashboard (`learning-analytics-analyst`), drillable to the 2-3 components.
- When telemetry isn't shareable, use a structured proxy (train-the-trainer completion, a sampled manual count) rather than waiting for data that may never come.

**Do:**
- Pick 2-3 deep workflows at 80%+ depth as the first-value target, not 10 workflows at 20% (adoption-sequencing stage-1 rule).
- Run the calendar-dead-zone overlay: a go-live landing in late August or the first two weeks of school will under-instrument; check the arc before committing the date.

**Don't:**
- Treat "rostering synced" or "accounts provisioned" as first value — that's setup, not value.
- Push feature breadth in stage 1 to make the dashboard look fuller; depth predicts renewal, breadth doesn't.

## Edge cases / when the rule does NOT apply

- **Pure re-implementation of an existing partner** (renewal-driven re-platform) — they already know what value looks like; instrument continuity, not first-value.
- **Corporate L&D with a compliance-training use case** — "value" may be a completion-rate floor mandated externally, not a depth metric; define against the mandate.
- **Pilot-before-scale partners** (Mississippi-style) — first-value is measured at the pilot cohort scale first, then re-baselined at full rollout; don't read pilot numbers as district numbers.

## See also

- [`./health-design-leading-not-lagging-signals.md`](./health-design-leading-not-lagging-signals.md) — first-value is the canonical leading signal
- [`../skills/implementation-90-day-arc/SKILL.md`](../skills/implementation-90-day-arc/SKILL.md) — the arc this milestone lives inside
- [`../knowledge/k12-adoption-arc-fall-spring-summer.md`](../knowledge/k12-adoption-arc-fall-spring-summer.md) — Phase 2 settling window is the most-predictive period
- [`../agents/edtech-partner-success-manager.md`](../agents/edtech-partner-success-manager.md) — owns the 30/60/90 plan and the first-value definition

## Provenance

Distilled from `knowledge/k12-adoption-arc-fall-spring-summer.md` (Phase 2 most-predictive), `skills/implementation-90-day-arc/SKILL.md`, `skills/adoption-sequencing-k12/SKILL.md` (stage-1 depth-over-breadth), and `psm-metrics-glossary.md` (TTV/TTFV entry). Reinforces house opinions "adoption depth > usage breadth" and "a success plan with no measurable success criteria" anti-pattern. Authored 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
