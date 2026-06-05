---
scenario_id: 2026-06-05-drift-detection-and-retrain-trigger
contributed_at: 2026-06-05
plugin: ml-engineering
product: evidently
product_version: "unknown"
scope: likely-general
tags: [drift, psi, concept-drift, retrain-trigger, monitoring, alert-fatigue]
confidence: medium
reviewed: false
---

## Problem

A demand-forecasting model degraded slowly over a quarter — error (MAPE) crept up from ~8% to ~14% — and nobody noticed until a planner complained that the forecasts "felt off." There *was* a monitoring dashboard, and it *was* showing drift the whole time: it fired a Population Stability Index (PSI) alert on three input features almost daily. But the alerts had no threshold tied to an action, so the team had muted them weeks earlier as noise. The model had no defined retraining trigger — "we retrain when it looks bad" — so the decay ran unchecked until a human happened to look. Two coupled failures: (1) input-drift alerts with no actionable threshold, fired so often they were tuned out (alert fatigue), and (2) no link from any drift signal to a retrain decision.

## Constraints context

- Ground-truth labels (actual demand) arrived on a **2–4 week lag**, so performance decay couldn't be measured in real time — input/prediction drift were the only *early* signals available.
- Several input features were genuinely seasonal (they drift every year on schedule); a naive PSI alarm fired on that expected seasonal movement, which is most of why it became noise.
- Retraining wasn't free — a full retrain + backtest + review was roughly a day of pipeline + analyst time, so "retrain on every drift blip" was not viable either.
- No statistical gate on "is this MAPE rise real or sampling noise?" — the team eyeballed it.

## Attempts

- Tried: lowering the PSI alert threshold to catch decay earlier. Made it *worse* — more alerts, more fatigue, faster muting. Sensitivity without an action mapping is just noise.
- Tried: a fixed monthly scheduled retrain. Helped the slow decay but was wasteful (retrained when stable) and still too slow for a sharp regime change mid-month.
- Tried (the fix): a **two-tier trigger with an action mapped to each tier, plus a hold-out performance gate once labels land**. (a) Input drift (PSI/KS on the non-seasonal features, with seasonal features either deseasonalized or excluded) → *investigate*, not auto-retrain. (b) Once the lagged labels arrive, compute performance decay against the hold-out baseline and route the "is the drop real?" question to a statistical test before acting. (c) Performance drop past the agreed threshold *and* confirmed real → retrain. (d) A scheduled cadence retrain as a floor under all of it. After this, drift alerts mapped to a decision instead of a dashboard nobody read.

## Resolution

**A drift metric with no threshold-to-action mapping is theater; define the retraining trigger — and what each signal *does* — before launch, not after the decay.** The durable shape:

1. **Separate the early signal from the ground truth.** Input/prediction drift is the *leading* indicator you have before labels arrive; performance decay (once labels land) is the *truth*. Monitor both, but don't treat a drift alarm as a retrain command — it's an "investigate" command. The diagnosis (data drift vs concept drift) selects the fix and is not interchangeable.
2. **Map each tier to an action up front.** Mild input drift → log/investigate. Severe input drift with no labels yet → escalate label collection / shadow a candidate. Confirmed performance drop → retrain. Scheduled cadence → floor. An alert that maps to nothing gets muted; an alert that maps to an action gets acted on.
3. **Deseasonalize (or exclude) features that drift on a known schedule** before alarming on them, or every season produces a false "drift" alarm — the single biggest source of the fatigue here.
4. **Gate the retrain decision on a real signal, not eyeballing.** Whether a MAPE/AUC change is a real regression or sampling noise is the statistician's call — route it to `applied-statistics`; MLOps makes the comparison fair and reproducible, they judge significance. Retraining on noise burns the budget and can make things worse.

The trap is that *having a drift dashboard feels like monitoring.* It isn't, until each signal has a threshold and each threshold has an owner and an action. A muted alert is worse than no alert — it's a false sense of coverage.

**Action for the next engineer:** before launch, write down the retraining trigger explicitly — schedule, drift threshold, and performance-drop threshold — and for each, the action it fires and who owns it. If an alert doesn't map to an action, don't ship the alert. When a performance drop appears, confirm it's real with `applied-statistics` before you spend a retrain on it.

Cross-reference: complements [`../best-practices/monitor-drift-and-define-the-trigger.md`](../best-practices/monitor-drift-and-define-the-trigger.md) and [`../best-practices/route-significance-to-the-statistician.md`](../best-practices/route-significance-to-the-statistician.md); traverse the "data drift or concept drift", "when to retrain", and "which drift metric" trees in [`../knowledge/ml-engineering-decision-trees.md`](../knowledge/ml-engineering-decision-trees.md). Whether a measured drop is statistically real → `applied-statistics`.
