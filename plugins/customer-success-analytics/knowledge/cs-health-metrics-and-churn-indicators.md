# CS Health Metrics & Churn Indicators (domain-neutral)

> **Last reviewed:** 2026-06-03
> **Read when:** selecting which signals compose an account-health view; deciding which signals are churn-*leading* vs *lagging*; setting up the transparent weighted tier + the per-Red explainability contract; arguing against a black-box ML score in phase 1.
> **Scope:** domain-neutral. These are universal customer-success mechanics — they hold for B2B SaaS, services, and platform businesses alike. Segment-specific overlays (budget cycles, academic calendars, rostering) belong in a vertical plugin, not here.

This file is the source of truth behind the `cs-analytics-architect` and `churn-signal-analyst` agents and the `health-tier-design` skill. It is consistent with the unified-CS-analytics build plan's §3.4 (the ~12 health signals that make the tier).

---

## 1. The core framing: leading vs lagging

A churn indicator is only useful if it moves **while there is still time to act**.

- **Leading indicator** — moves *before* the account has decided to leave. It predicts. (Usage trending down; health score falling; champion gone silent.) These belong in the **risk tier**.
- **Lagging indicator** — moves *after* the decision is effectively made. It confirms. (A renewal opp marked Closed-Lost; a cancellation request; a contract non-renewed.) These belong on the dashboard as **context**, never as a tier *input* — by the time they move, the prediction window has closed.

> **Rule:** before adding any signal to the tier, classify it leading or lagging. If it lags, it is context, not a predictor. Calling a lagging signal a "churn predictor" is the most common modeling error in CS analytics.

---

## 2. Why slope beats absolute level

The single most important measurement choice: **measure the trend, not the level.**

- An account using a product *a lot* but with a **30/60/90-day downward slope** is at more risk than a low-but-flat account. The slope is the leading signal; the level is a snapshot that lags.
- Same for the health score: the **7/30-day delta** leads; the absolute number on any given day lags.
- Practically: materialize the trend columns (`usage_trend_30d`, `health_score_trend_7d/_30d`) in the data model so the tier reads the slope directly. Never make the dashboard recompute trend at render time, and never tier on the absolute value when the slope is available.

---

## 3. The ~10-12 CS-health signals (★ = churn-leading)

The signals that compose a domain-neutral account-health view. The starred ones are leading indicators eligible for the risk tier; the unstarred ones are context or slower-moving inputs.

1. **★ Usage-trend slope (30/60/90-day)** — the strongest single predictor. *Slope, not absolute level.* A sustained decline leads churn by a wide margin.
2. **★ Health-score trend (7/30-day delta)** — direction beats the absolute value of the CS platform's native score. A falling score leads; a steady score (even a mediocre one) is far less alarming.
3. **★ Renewal proximity × engagement** — renewal within ~90 days *combined with* low touch / declining usage = high risk. **Proximity alone is not risk** — every account eventually hits 90 days out. The product of proximity and (lack of) engagement is the signal.
4. **★ Support volume + P1/P2 rate** — a spike in support load, especially high-severity tickets, in the ~90 days before renewal is a strong leading signal. The **P1/P2 *rate* matters more than raw volume** — a busy power user files lots of low-sev tickets; that is not risk.
5. **★ Champion / sponsor silence (absence)** — a named champion who has gone quiet, or a sponsor who skipped the last two reviews, is a leading indicator. **Absence is a signal** — a *dead* relationship often predicts churn better than any present-signal spike.
6. **★ Escalation-keyword density / dead-channel detection** (from derived collaboration signals) — rising escalation language, or the *absence* of expected activity in a shared customer channel, leads. (Derived signals only — never raw message bodies.)
7. **NPS + recency** — a detractor *not followed up* is a risk; but stale NPS is noise. Recency matters — weight the most recent response, decay the old ones.
8. **CSM touch cadence** — days since the last meaningful CSM interaction vs. the tier's expectation; an overdue QBR or onboarding milestone. Slower-moving; supports the tier rather than driving it alone.
9. **Median first-response time (support)** — slow support erodes trust and shows up at renewal. A relationship-quality input.
10. **Feature adoption / breadth** — narrow adoption (one feature, one team) is fragile; broad adoption is sticky. Slower-moving context.
11. **Days to renewal (CRM)** — pure context; it *gates the urgency* of everything above but is not itself risk.
12. **Renewal-opportunity stage (CRM)** — context; a renewal opp stuck early, or marked Closed-Lost 90 days out, is a flag. (The Closed-Lost case is *lagging* — show it, don't tier on it.)

---

## 4. The transparent weighted tier

The output of the signals is a **Green / Yellow / Red** churn-risk tier. In phase 1 it is **rule-based, transparent, and tunable** — not a learned model.

A tier rule is a readable boolean expression over the leading signals, for example:

```
Red    := health_score_trend_30d = down
          AND days_to_renewal < 90
          AND (support_p1_p2_rate_30d > t_support OR escalation_signal_7d > t_escalation)
Yellow := health_score_trend_30d = down  (any one leading signal tripped, renewal not imminent)
Green  := otherwise
```

Design principles for the tier:

- **Weighting is rarely equal.** Different signals predict with different strength; tune the weights / threshold cut-points to the team's actual past churn (see §6). Equal-weighting is a placeholder, not a design.
- **Fewer, sharper signals beat more, fuzzier ones.** A 5-signal tier you can explain beats a 12-signal tier you can't. Drop signals that correlate but don't *lead* — correlation is not prediction; it's noise dressed as signal.
- **Renewal proximity is a gate, not a term.** It multiplies the urgency of the engagement signals; it never stands alone as a risk term.
- **Independent red-flag triggers run alongside the tier, not inside it.** A composite reacts too slowly to a champion departure or an explicit "we're evaluating alternatives." Fast triggers fire the recovery motion the same day, regardless of the tier's color.

---

## 5. The explainability requirement (every Red shows why)

A tier that says "Red" with no reason is useless to the leader and unconvincing to the account.

**Every Red (and Yellow) carries its driving signals** — the 2-3 that tripped, each with:

- the **signal name** (e.g. "support P1/P2 rate")
- its **value** (e.g. "4 P1/P2 tickets in 30 days")
- the **threshold** it crossed (e.g. "threshold: 2")
- the **window** measured (e.g. "trailing 30 days")

This is the explainability contract. It ships *with* the tier, not as an afterthought, and it is the single biggest driver of CS-team adoption: a leader trusts a tier they can read and repeat to the account.

---

## 6. Tuning against actual past churn

A threshold you can't back-test is a guess wearing a number.

- **When historical outcomes exist:** back-test the tier against the last renewal cycle. Did the Red list match the accounts that actually churned? Did any Green account churn (a *signal gap* — the most valuable finding; it names the missing signal)? Did a signal correlate but not predict (drop it)?
- **When they don't:** start from a **documented default** threshold, mark it **provisional**, and schedule the retune for after the first renewal cycle. A provisional default is honest; a guessed-but-unmarked threshold is not.
- **Refresh discipline:** re-audit each cycle. A score that's never been refreshed against outcomes is suspect by default.

---

## 7. Why no black-box ML in phase 1

The phase-1 tier is **rule-based and explainable on purpose**, even though a logistic-regression churn model is technically straightforward.

- **Trust and adoption are the whole game in phase 1.** A CS team acts on a tier they can explain to themselves and to the account. A model nobody can read produces "why is this Red?" arguments that torpedo credibility before the platform earns any.
- **Anchor on the CS platform's native score; add signals additively.** If the team already trusts the CSP's (Planhat's, or any CSP's) native health score, that is the anchor — pulled as-is, not silently recomputed. Extra signals surface *alongside* it as visible sub-indicators. Replacing a black box with another black box on day one is the fastest way to lose the room.
- **Defer the composite until evidence demands it.** Build the weighted composite only when the additive sub-signals *demonstrably diverge* from the native tier — and even then, prefer a transparent weighting over a learned one until volume genuinely justifies ML.
- **ML is a later option, never the phase-1 default.** A lightweight churn model can come once the rule tier has been tuned against at least one real renewal cycle and the account volume justifies the loss of explainability.

---

## 8. Anti-patterns

- A lagging signal (Closed-Lost opp, cancellation) used as a tier *input* and called a "predictor"
- Renewal proximity treated as risk on its own (every account at 90 days flagged Red regardless of engagement)
- Absolute usage / absolute health score used where the slope / delta is the real predictor
- A Red with no named drivers (no explainability contract)
- Signals kept because they correlate, not because they lead
- A composite expected to catch a champion departure (too slow — needs an independent fast trigger)
- A black-box ML score shipped before the transparent rule tier was tuned against a real cycle
- A threshold set by intuition with no back-test and no "provisional" marker
- A refresh that never asks "did any green account churn?"

---

## References

- Skill: [`../skills/health-tier-design/SKILL.md`](../skills/health-tier-design/SKILL.md)
- Companion knowledge: [`renewal-and-account-lifecycle.md`](renewal-and-account-lifecycle.md)
- Template: [`../templates/cs-health-data-model.md`](../templates/cs-health-data-model.md)
- Agents: [`../agents/churn-signal-analyst.md`](../agents/churn-signal-analyst.md), [`../agents/cs-analytics-architect.md`](../agents/cs-analytics-architect.md)
