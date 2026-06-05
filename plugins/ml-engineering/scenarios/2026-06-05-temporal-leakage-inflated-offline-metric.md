---
scenario_id: 2026-06-05-temporal-leakage-inflated-offline-metric
contributed_at: 2026-06-05
plugin: ml-engineering
product: python
product_version: "unknown"
scope: likely-general
tags: [leakage, temporal-split, validation, offline-online-gap, label-window, target-leakage]
confidence: high
reviewed: false
---

## Problem

A churn model reported a spectacular offline AUC of 0.97 and the team was ready to ship it as a win. In production it landed around 0.71 — still useful, but the offline number was a fantasy. Nothing had drifted (it was launch); the offline metric had simply been measured wrong. Two leaks compounded: (1) the train/test split was a **random shuffle of rows that were time-ordered**, so the model trained on the future and tested on the past for the same customers; and (2) one feature, `support_tickets_30d`, was computed over a window that **straddled the label date** — it counted tickets in the 30 days *around* the churn event, including the angry tickets a customer files *while* churning, which at serving time don't exist yet. Both are leakage: the model was scored on information it would never have in production.

## Constraints context

- Time-ordered data (customer activity over months) but the pipeline used a stock `train_test_split(shuffle=True)` — the default — so rows from the same customer at different times landed on both sides of the split.
- Features were built by a single batch job that joined against the *whole* event table with no point-in-time cutoff, so any window function could see across the label boundary.
- The label (churned in month N) and a feature window (activity in month N) overlapped because the windows were defined by calendar month, not anchored to a per-row prediction timestamp.
- The offline metric was the only gate; there was no held-out-by-time backtest and no parity check against what serving could actually compute.

## Attempts

- Tried: more regularization / a simpler model to "stop the overfitting." No real change to the gap — the problem wasn't model variance, it was that the *labels and features were contaminated*. A simpler model leaks just as happily.
- Tried: k-fold cross-validation. Made the offline number look *more* trustworthy (tight CV folds!) while being just as leaked — shuffled CV on temporal data leaks across every fold. A confident wrong number is worse than an obviously shaky one.
- Tried (the fix): a **time-based split** (train on the past, validate on a strictly later window, never shuffle across time) plus **point-in-time-correct feature windows** anchored to each row's prediction cutoff (every feature computed using only data available *before* the label date), plus a one-time **audit of every feature for label-window overlap**. The retrained model's offline AUC dropped to ~0.72 — and then *matched* production. The "drop" wasn't a regression; it was the honest number finally appearing.

## Resolution

**An offline metric inflated by leakage is a production disappointment with a delay; validate honestly — no future information, time-aware splits, point-in-time features.** The durable rules:

1. **Pick the split that matches the data's structure.** Temporal data → time-based split (train past, validate future), never a random shuffle and never shuffled k-fold. Entity-correlated rows (many per customer) → grouped split so a customer is entirely in one fold. The default `shuffle=True` is the single most common temporal-leakage bug.
2. **Anchor every feature to a point-in-time cutoff.** A training row's features must be computed using only data that existed *before* that row's label/prediction time — never over the whole table, never a window that straddles the label date. This is the same point-in-time-correct discipline a feature store enforces; without it you both leak the future *and* compute values serving can never reproduce.
3. **Audit features for target/label leakage explicitly.** Any feature whose value is influenced by the outcome (tickets filed *while* churning, a field populated *by* the event) is a leak. A feature that's "too predictive" on its own is the tell — interrogate it before celebrating it.
4. **Use the test set once, after the splits are honest.** A leaked metric is not a small error you can shave off; it's a different number entirely. Re-establish the honest baseline first, then compare candidates against it — and route "is this candidate really better?" to `applied-statistics`.

The trap is that the leaked number is *higher*, so it looks like success — leakage never makes your offline metric look *worse*. The day-one online shortfall is the bill coming due. A model that's worse than offline from launch is skew or leakage, not drift.

**Action for the next engineer:** when an offline metric looks too good (AUC ≫ what the problem should allow) or when online underperforms offline *immediately*, suspect leakage before anything else. Check the split (shuffled on time-ordered data?) and check every feature's window against the label timestamp. The fix lowers the offline number — that's the honest baseline arriving, not a regression.

Cross-reference: complements [`../best-practices/validate-without-leakage.md`](../best-practices/validate-without-leakage.md) and [`../best-practices/eliminate-training-serving-skew.md`](../best-practices/eliminate-training-serving-skew.md); traverse the "which validation split" tree in [`../knowledge/ml-engineering-decision-trees.md`](../knowledge/ml-engineering-decision-trees.md). Shares the launch-day-shortfall diagnosis with [`2026-06-05-training-serving-skew-feature-source.md`](2026-06-05-training-serving-skew-feature-source.md) (skew is the serving-path twin of this training-path leak). Whether a candidate's lift over the honest baseline is real → `applied-statistics`.
