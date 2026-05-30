# Fire the save play while the relationship can still be saved — diagnose root cause first

**Status:** Primary diagnostic

**Domain:** Churn risk / Recovery

**Applies to:** `edtech-partner-success`

---

## Why this exists

The window in which a churn risk is recoverable closes long before the renewal date. A save play fired at T-30 reads as a panic move; the same play fired the week the leading signal turned has runway. But early *firing* is only half the rule — the other half is that the most expensive recovery mistake is treating the symptom, not the cause. The plugin's named wrong-first-picks (renewal-on-rostering, discount-as-recovery, recovery-on-stage-1) all share one defect: a play was selected from the score's color instead of the root cause. The recovery-play house opinion is that the first step is *listening*, not intervention, and the diagnostic runs before the remedy.

## How to apply

When a leading signal turns or a red-flag fires, run the 4-hypothesis diagnostic before selecting any remedy, and route through the play-selection tree so a higher-priority cause isn't skipped.

```
Save-play sequence (on leading-signal turn OR red-flag fire):
  0. Suppress check — calendar dead zone / testing window? If yes → NO PLAY, re-eval at window end.
  1. Rostering/SSO check — error rate elevated last 14 days? If yes → IMPLEMENTATION play, not commercial.
  2. Sponsor check — named champion changed or silent 30+ days? If yes → sponsor re-engagement FIRST.
  3. 4-hypothesis diagnostic (parallel, listen before pitching):
       A product-fit   B implementation health   C sponsorship   D external pressure
  4. Select remedy matched to the confirmed hypothesis; set 30/60/90 measurable signal targets.
  5. Escalation ladder if targets miss: PSM → success leadership → exec sponsor → counsel → churn-prep.
```

- Set time-bound, measurable recovery targets ("active-teacher % back above X within 30 days"), not "partner is healthier" (a §4 anti-pattern).
- Recovery cadence upgrades to twice-weekly during active risk; other partners stay monthly.
- Withdraw any in-flight advocacy ask — a bottom-quartile partner is off-limits for references.

**Do:**
- Open with a low-pressure listening touchpoint, not "we noticed your usage dropped" (accusatory) or "checking in" (boilerplate).
- Confirm the named decision-maker is alive in the role before running anything renewal-adjacent (superintendent turnover hit 23% in 2024-25).

**Don't:**
- Reach for a discount as the recovery move — discount-as-recovery buys one renewal and churns the next because the real problem was never addressed.
- Run a generic recovery play on a stage-1 partner whose modest adoption is normal for the early arc; that reads as "you're already a failure."

## Edge cases / when the rule does NOT apply

- **Unrecoverable cases** — when the diagnostic confirms the partner has decided to leave (budget eliminated, competitor already selected), shift to graceful-exit + reference-protection, not a save play. Fighting a lost renewal burns goodwill and the reference.
- **Calendar false-positive** — a leading-signal turn inside a dead zone is suppressed, not saved; re-evaluate at the window's end before firing anything.
- **Score-drift suspicion** — if the signal that turned is itself drifting (yellow partners renewing, green ones churning), audit the score with `learning-analytics-analyst` before treating the partner as at-risk.

## See also

- [`./health-design-leading-not-lagging-signals.md`](./health-design-leading-not-lagging-signals.md) — leading signals are what create the save window
- [`../knowledge/partner-success-decision-trees.md`](../knowledge/partner-success-decision-trees.md) — the account-health → intervention and renewal-risk-triage trees
- [`../knowledge/partner-health-decline-which-play.md`](../knowledge/partner-health-decline-which-play.md) — the play-selection router this rule traverses
- [`../skills/recovery-play-design/SKILL.md`](../skills/recovery-play-design/SKILL.md) — the 4-hypothesis diagnostic and escalation ladder

## Provenance

Distilled from `skills/recovery-play-design/SKILL.md` (4-hypothesis diagnostic, escalation ladder, listen-first), `knowledge/partner-health-decline-which-play.md` (named wrong-first-picks, higher-branch-wins ordering), `agents/success-playbook-designer.md` (listen-before-intervene opinion), and house opinion §3 #10 (don't sell). Authored 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
