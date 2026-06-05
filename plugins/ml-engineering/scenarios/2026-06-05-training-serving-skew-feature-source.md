---
scenario_id: 2026-06-05-training-serving-skew-feature-source
contributed_at: 2026-06-05
plugin: ml-engineering
product: feast
product_version: "unknown"
scope: likely-general
tags: [training-serving-skew, feature-store, online-offline, point-in-time, parity, leakage]
confidence: high
reviewed: false
---

## Problem

A fraud-scoring model evaluated beautifully offline — AUC 0.94 on the held-out test set — then scored noticeably worse in production from day one (catch rate roughly a third lower than the offline estimate predicted), with no drift to blame because it was *launch* day. The model wasn't decaying; it had never actually been as good as the offline number said. The culprit was a **feature that was computed one way in training and a different way at serving time**: `txn_count_7d` (count of the account's transactions in the trailing 7 days). In training it was computed by a batch SQL job over the full history; at serving it was read from a Redis counter that a streaming job maintained. The two disagreed — the batch job counted with a clean 7-day window aligned to the label timestamp, the online counter had a rolling reset bug and a different timezone boundary — so the model saw a *different distribution* of that feature in production than the one it learned on.

## Constraints context

- Two separate code paths produced the "same" feature: an offline batch transform (training) and an online transform (serving). Classic two-pipeline setup, no shared definition.
- The offline path could see the future relative to a serving request (it computed over the whole table), so even the *training* feature was subtly leaked — the window wasn't anchored to a point-in-time-correct cutoff per row.
- No parity test compared the offline-materialized feature value against the online-served value for the same entity at the same timestamp.
- The team's first instinct was "the model decayed / the data drifted" — but it was wrong from minute one, which rules out drift.

## Attempts

- Tried: retraining on more recent data. No change — retraining a model on the *offline* feature can't fix a feature that's computed differently at *serving*. The skew is in the serving path, not the model's age.
- Tried: adding the production feature distribution to a monitoring dashboard. Useful — it *showed* the offline-vs-online histogram mismatch for `txn_count_7d` — but it diagnosed, it didn't fix.
- Tried (the fix): moved the feature to a **feature store with a single shared definition**, so the offline (training) materialization and the online (serving) retrieval come from the *same* transformation, and used a **point-in-time-correct join** for the training set so each row's feature is computed as-of that row's label timestamp (no future leakage). Then added a parity check. After re-training on the now-consistent feature, the production catch rate matched the offline estimate.

## Resolution

**Training-serving skew is the silent killer, and the fix is a single source of truth for each feature — not a second model.** Two independent code paths computing "the same" feature will diverge; the only durable fix is one definition that both training and serving consume.

1. **One definition, two reads.** A feature store (Feast / a managed one) lets you define `txn_count_7d` once and serve it offline (batch materialization for training) and online (low-latency lookup for serving) from the same logic. That structurally eliminates the two-pipeline drift.
2. **Point-in-time-correct training joins.** The training feature for a row must be computed as-of that row's event/label time — never over the whole table — or you both leak the future *and* compute a value serving can never reproduce. This is the leakage half of skew; it inflates the offline metric the same way skew deflates the online one.
3. **Add a parity test as a gate.** For a sample of entities, assert `offline_feature(entity, t) == online_feature(entity, t)` within tolerance. A skew bug fails this test before launch instead of after. Make it a promotion gate, not a dashboard you read after the incident.
4. **Rule out skew before you blame drift.** A model that's worse than offline *from launch* is skew or leakage, not drift — drift takes time. The decision tree is: bad on day one → skew/leakage; degrades over weeks → drift. Don't retrain to fix a serving-path bug.

The trap is that the offline metric *looks* authoritative, so an online shortfall reads as "the world changed." On launch day the world hasn't changed yet — the only thing that differs between offline and online is the feature pipeline.

**Action for the next engineer:** when a model underperforms its offline metric *immediately*, do not retrain and do not assume drift. Pull the same entity through both the training feature path and the serving feature path at the same timestamp and diff the values. A mismatch there is your bug; a feature store with a point-in-time-correct join is the structural fix.

Cross-reference: complements [`../best-practices/eliminate-training-serving-skew.md`](../best-practices/eliminate-training-serving-skew.md), [`../best-practices/feature-store-is-the-consistency-contract.md`](../best-practices/feature-store-is-the-consistency-contract.md), and [`../best-practices/validate-without-leakage.md`](../best-practices/validate-without-leakage.md); see the validation-split tree in [`../knowledge/ml-engineering-decision-trees.md`](../knowledge/ml-engineering-decision-trees.md). Whether a remaining offline-online gap is statistically real → `applied-statistics`.
