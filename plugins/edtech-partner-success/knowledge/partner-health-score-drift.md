# Partner health score drift — when the score stops predicting outcomes

> **Last reviewed:** 2026-05-21. Source: research-distilled from customer-success scoring practice (Gainsight / ChurnZero patterns), the [`partner-health-scoring`](../skills/partner-health-scoring/SKILL.md) skill, and the team's house opinions on decay and signal citation. Refresh when: (a) the team's product mix changes materially (new module, deprecated feature), (b) a segment-shift event (district consolidation, higher-ed sector contraction) changes who the partners *are*, or (c) renewal-prediction accuracy drops below ~70% on the most recent quarter.

A partner health score earns its keep by **predicting outcomes** — renewal, expansion, advocacy, churn. When the score stops doing that, the dashboard becomes decoration and the PSM stops trusting it. This document captures the drift symptoms, the diagnostic tree, and the recalibration playbook.

---

## The drift symptom

The PSM and the analyst feel drift before they prove it. The early signals:

- **"Yellow" partners renew at full ARR; "green" partners churn.** The most common symptom. The score's *rank order* of risk has decayed.
- **Every partner is green.** The thresholds were set last year; everyone has grown into them. The score is bragging, not predicting.
- **Every partner is yellow.** The opposite — thresholds set in a friendlier product era; current usage patterns don't clear the old bar.
- **A specific cohort is mis-scored.** New-product partners look red because the product's deepest features take longer to adopt; veteran partners look green because their old workflows still register.
- **The PSM can't explain the score to the partner.** When the partner asks "what would I have to do to be green?", the PSM stumbles. The score has become noise.

If two of those signals are present, the score has drifted. Stop arguing about whether it has; start diagnosing.

---

## The root causes (in order of frequency)

### 1. Signal staleness — the product changed, the signals didn't

Most common cause. A signal was set when feature X was the primary engagement surface. The product launched feature Y, deprecated X, and the score still weights X. Partners on Y look red; partners stuck on X look green. **The score is now measuring loyalty to a deprecated feature.**

- **How to spot:** Compare the top 2-3 signals' definitions against the current product release notes. Any feature whose name no longer matches the in-app navigation is a red flag.
- **Fix:** Quarterly signal review tied to the product release calendar. New feature ships → its corresponding signal goes through *propose → instrument → measure → integrate* before it joins the composite.

### 2. Decay too slow — old engagement keeps stale partners green

Per house opinion #3 in [`../CLAUDE.md`](../CLAUDE.md): "A signal from 6 months ago is not a signal today." Drift here is silent. A partner that *was* highly adopted six months ago has stopped using the product weekly, but the score's half-life is too long to react. The PSM sees green; the partner is actually disengaged and considering alternatives.

- **How to spot:** Sample 5 green partners and pull their last-30-day engagement directly. If the score says green and the 30-day engagement is bottom-quartile, decay is too slow.
- **Fix:** Halve the half-life on the fastest-moving signals (login frequency, in-app actions). Keep slower decay only on signals that *should* be slow (deep-feature adoption, contract milestones).

### 3. Mis-tuned weights — segment shifted, weights didn't

The book of partners isn't the same shape it was a year ago. A new tier launched, a vertical was added, a segment consolidated. The composite weights were tuned to the old mix.

- **How to spot:** Re-run the same composite on the partner cohort as of 12 months ago vs today. If the *distribution* of scores has shifted materially (mean moved, variance compressed or expanded), the weights are off.
- **Fix:** Re-fit the weights against a held-out cohort whose renewal outcome you know. This is regression-flavored work; the `learning-analytics-analyst` owns it.

### 4. Champion change not captured

The most predictive single signal in many books is **does the partner still have a healthy champion in role**. When the champion leaves, signal silence often follows in 30-60 days, then a renewal conversation that goes sideways. If the score doesn't carry a "champion alive" component, the PSM is flying without instrumentation on the most predictive variable.

- **How to spot:** Audit the last 5 churn cases. How many had a champion departure in the 90 days before the churn signal showed up?
- **Fix:** Add a "relationship health" component to the composite — last touchpoint with named champion, role tenure of named champion, named successor identified. The `partner-profile-curator` is the data source.

### 5. Cohort comparison baselines drifted

If the score includes a cohort-relative component ("you're in the bottom quartile of your segment"), the cohort definition matters. Cohorts that were homogeneous a year ago aren't anymore.

- **How to spot:** Audit the cohort assignment for 10 partners. Are partners in the same cohort actually comparable today?
- **Fix:** Re-segment. The cohort definition is owned by the analyst, refreshed quarterly.

### 6. Vanity metrics polluting the composite

A metric was added because it was easy to instrument, not because it predicts anything. Total sessions, total logins, total page views. The signal moves; the partner outcome doesn't.

- **How to spot:** Correlate each component individually with renewal outcomes over the last 4 quarters. Any component with near-zero correlation is a candidate for removal.
- **Fix:** Remove the component. The analyst's instinct is "more signal = better score"; the discipline is the opposite.

### 7. Threshold drift — green/yellow/red bars not updated

The bands were set when scores ran lower (or higher). Now everyone clusters in one band. The composite is fine; the bucketing is broken.

- **How to spot:** Distribution histogram of current scores. If 90% land in one band, the bands are wrong.
- **Fix:** Re-anchor bands to outcome data, not to "feels right." Bottom-quartile of historical renewers anchors red; top-quartile anchors green.

---

## Diagnosis tree

When drift is suspected, run in this order:

1. **Verify the symptom.** Pull the last 4 quarters of (final score) × (renewal outcome). What's the correlation? Below ~0.5, the score is genuinely broken.
2. **Distribution check.** Histogram of current scores. Bimodal? Clustered? Flat?
3. **Cohort check.** Same distribution, broken down by segment / tier / vertical. Where's the drift concentrated?
4. **Component-level correlation.** Each component vs outcome, individually. Which components carry weight, which are noise?
5. **Decay check.** For each component, plot the value at t-0, t-30, t-90, t-180. Is the decay rate reasonable for what the signal represents?
6. **Champion check.** Of the last N churn cases, what fraction had a champion-change signal that wasn't in the score?
7. **Threshold check.** Distribution of scores vs the green/yellow/red bands. Are the bands isolating ~20%/60%/20% (or whatever the original design called for)?

The first one that comes back "broken" is the root cause; the others are often downstream.

---

## Recalibration playbook

### Step 1 — Decide retune vs rebuild

- **Retune** (a few weeks of work) when: drift is localized to 1-2 components, decay needs adjustment, weights are off, thresholds need re-anchoring. The skeleton holds.
- **Rebuild** (a quarter of work) when: 3+ components are stale, the product has changed materially, the segment mix has shifted enough that the old composite doesn't apply. Don't patch — author a v2 score and run it alongside v1 for one quarter before cutover.

### Step 2 — Hold-out cohort

Whatever you do, **prove it on a hold-out**. Take a cohort whose renewal outcome you already know (last quarter's renewers and churners). Score them with the new composite *as of 90 days before their renewal date*. Does the new score rank-order risk better than the old? If not, the new score isn't better; it's different.

### Step 3 — Run both scores in parallel for one quarter

The PSM continues operating from the v1 score. The analyst runs v2 silently. Each renewal cycle, capture: did v1 predict it? did v2? what did each miss? After a quarter, compare. **Cut over only when v2 is meaningfully better across multiple renewal outcomes — not after one good prediction.**

### Step 4 — Document the cut-over

Every component change goes into the partner-health-scoring skill doc with a date. A PSM joining the team 18 months from now should be able to read why the score is what it is.

### Step 5 — Quarterly check-in becomes part of the cadence

Score drift is the default state. Quarterly review against outcome data is the only thing that prevents it. Calendar it.

---

## Anti-patterns the analyst flags

- A score that hasn't been audited against actual renewal outcomes in >2 quarters
- A "health score is broken" complaint addressed by adjusting thresholds instead of investigating which components have drifted
- Adding a new component without removing a stale one ("composite bloat" — every component dilutes the others)
- A v2 score deployed without a hold-out test
- A weight change tuned to make the PSM's gut-feel ranking match the score, instead of the other way around (overfitting to existing bias)
- A decay rate set "to be safe" (slower than needed) without modeling what slow decay does to recently-disengaged partners
- A composite with no champion-health component
- Threshold bands set to make "more partners green" because leadership wanted a friendlier dashboard

---

## When the partner asks "what would I have to do to be green?"

This question is the acid test of a working score. If the PSM can answer it concretely — "lift weekly active-teacher count from 60% to 75% over the next quarter, get [named feature] adoption above 40%, and confirm [champion's named successor] is in the conversation by end of next month" — the score works. If the PSM hand-waves, the score has drifted past usefulness.

The score serves the conversation; the conversation doesn't serve the score.

---

## Refresh triggers for this document

Re-read and update when:

- Renewal-prediction correlation drops below ~0.6 on the most recent two quarters.
- The product launches a feature large enough to require its own signal.
- A segment-shift event (M&A, district consolidation, regulatory change) materially changes the partner mix.
- A new methodology (e.g., gradient-boosted churn model, NPS-driven composite, value-realization framework) is adopted by the analytics team.
- The team observes a renewal outcome whose surprise *would have been predicted* by a component currently outside the composite.
