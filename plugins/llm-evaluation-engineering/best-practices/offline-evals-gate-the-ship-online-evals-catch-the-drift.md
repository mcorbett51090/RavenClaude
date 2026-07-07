# Offline evals gate the ship; online evals catch the drift

**Rule.** Run both. A frozen offline golden set decides ship/no-ship before release; online production
signals (implicit: edit distance, escalation, retry, downstream conversion; explicit: thumbs, ratings)
catch what offline can't see.

**Why.** Offline is controlled and repeatable but frozen — it can't see distribution shift, new user
behavior, or a prompt that's technically fine but annoying. Online is real but noisy and lagging. Each
covers the other's blind spot.

**Anti-pattern it kills.** Shipping on a green offline suite and never watching production — so a
month of quiet quality drift goes unnoticed until churn shows up.

**In practice.** The offline gate is a number decided before the run; the online layer is a dashboard of
a few production signals with an alert threshold.
