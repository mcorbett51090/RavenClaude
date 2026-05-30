# Give every health-score component a half-life, then audit the score against outcomes quarterly

**Status:** Absolute rule

**Domain:** Learning analytics / Health-score design

**Applies to:** `edtech-partner-success`

---

## Why this exists

A health score with no decay accumulates history forever: a deep-engagement burst from nine months ago keeps a now-disengaged partner green, and a single bad month drags a recovered partner red long after the cause cleared. House opinion §3 #3 is non-negotiable — every component has a half-life; the score reflects *current state*, not historical accumulation. The companion failure is never validating the score: most health scores stop predicting renewal outcomes within a few quarters of launch (signal staleness, mis-tuned weights, vanity pollution), and a score nobody audits drifts silently until yellow partners are renewing and green ones are churning. Decay keeps the score current; the quarterly correlation audit keeps it *honest*. Without both, the PSM is acting on a number that feels precise and predicts nothing.

## How to apply

Assign each component a decay half-life at design time, and re-validate the whole score against real renewal outcomes every quarter.

```
Decay + audit discipline:
  DESIGN TIME — every component gets a half-life:
    login frequency        → fast decay (last ~30 days dominate)
    deep-feature adoption  → slow decay (once adopted, stays adopted a while)
    sentiment (NPS/CSAT)    → medium; re-ask, don't carry a stale survey forever
    → a component with NO defined decay is a §4 anti-pattern — reject it.
  QUARTERLY AUDIT — correlate final score x renewal outcome:
    corr < ~0.5  → the score is broken. Recalibrate, do NOT reassure.
    recalibration order: signal change → component change → weight retune → threshold rebase
    prove it: hold-out cohort scored AS OF 90 days pre-renewal, then parallel-run v1+v2
              one quarter before cutover. Never patch in place unverified.
  ACID TEST: can the PSM answer "what would I do to be green?" concretely?
             If they hand-wave, the score has drifted past usefulness.
```

**Do:**
- Run two scores — a fast-decay "current state" + a slow-decay "trajectory" — rather than forcing one number to be both.
- Overlay the calendar dead zones on decay so a December dip or a testing-window silence doesn't decay a partner into a false yellow.

**Don't:**
- Tune your gut to match the score when they disagree — if the score stopped predicting, the score is the suspect; audit it.
- Cut over a recalibrated score without the hold-out-cohort + parallel-run proof that it rank-orders risk better than the old one.

## Edge cases / when the rule does NOT apply

- **Brand-new instrumentation** with no renewal history — you can't yet correlate; start with adoption-depth-trend as the prior and run the first audit at the first renewal cohort.
- **Cohorts < 10 partners** — correlation on a sub-10 cohort is noise; validate at segment level until the book grows.
- **Outcome-only buyers** — surface the lagging outcome metric *for them*, but the PSM's actionable score still needs leading components + decay.

## Edge cases note

A red-flag trigger (sudden 30% drop, champion departure, 3 weeks silence) runs *alongside* the decaying composite, not inside it — triggers fire fast; the composite is the trailing confirmation. Don't bury reactivity inside a decaying average.

## See also

- [`./health-design-leading-not-lagging-signals.md`](./health-design-leading-not-lagging-signals.md) — the sibling rule on leading-vs-lagging signal selection
- [`../knowledge/partner-health-score-drift.md`](../knowledge/partner-health-score-drift.md) — the 7 drift causes, diagnosis tree, retune-vs-rebuild, hold-out discipline
- [`../skills/partner-health-scoring/SKILL.md`](../skills/partner-health-scoring/SKILL.md) — half-life / decay design
- [`../agents/learning-analytics-analyst.md`](../agents/learning-analytics-analyst.md) — owns decay design and the quarterly audit

## Provenance

Distilled from `agents/learning-analytics-analyst.md` ("decay matters more than weighting", quarterly correlation audit, hold-out + parallel-run), `knowledge/partner-health-score-drift.md` (drift typology, recalibration playbook), and house opinions §3 #3 + §4 (no-decay component anti-pattern). Authored 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
