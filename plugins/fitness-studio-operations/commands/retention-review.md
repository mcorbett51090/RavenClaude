---
name: retention-review
description: "Run a retention review: compute the real churn rate (with freeze treatment), read cohort retention, build a signal-ranked at-risk list with interventions, and decide keep-vs-acquire and the win-back play."
argument-hint: "[member roster with join/cancel/freeze dates + visit history]"
---

You are running `/fitness-studio-operations:retention-review`. Use `member-retention-analyst` + the `analyze-retention-and-churn` skill.

## Steps
1. Compute monthly logo churn (cancels / start-of-period actives) with the freeze treatment defined and documented; report the 6-12 month trend.
2. Plot retention by join cohort and membership type; read the first-90-day cliff.
3. Traverse the retention-intervention tree in `knowledge/fitness-studio-operations-decision-trees.md`.
4. Build a signal-ranked at-risk list (frequency drop, failed payment, no future booking, pack ending) with an intervention per tier.
5. Run keep-vs-acquire arithmetic (cost of save vs P(save) × saved LTV vs CAC) and a segmented win-back play.
6. Emit using `templates/retention-dashboard.md` + the Structured Output block; feed avg lifetime months back to fitness-studio-operations-lead.
