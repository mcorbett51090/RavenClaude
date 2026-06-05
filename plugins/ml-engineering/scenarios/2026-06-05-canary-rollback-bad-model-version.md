---
scenario_id: 2026-06-05-canary-rollback-bad-model-version
contributed_at: 2026-06-05
plugin: ml-engineering
product: kserve
product_version: "unknown"
scope: likely-general
tags: [canary, rollback, registry, shadow, serving-version, offline-online-mismatch]
confidence: medium
reviewed: false
---

## Problem

A recommender team promoted a new model version straight to 100% of traffic because it beat the incumbent on every offline metric. Within an hour, click-through rate dropped ~6% and a downstream service started timing out — the new model's feature-fetch was slower and occasionally returned a payload the ranking service couldn't parse. Rolling back took 40 minutes of scramble because the "previous model" was a file someone had copied to a server weeks ago, not a versioned artifact in the registry, and nobody was certain which exact version had been live. The model that won offline lost online, and the team had built no safe way to find that out cheaply or to undo it fast.

## Constraints context

- A live, user-facing metric (CTR) existed and could be measured within hours — so a canary was feasible and a full-traffic cutover was needless risk.
- The new version was **not** a pure model swap: it changed a feature dependency and the output payload shape — i.e. a partially-breaking change, exactly the case shadow mode exists for.
- Deployments were "copy the artifact to the box," not "promote a registry version + point serving at it," so there was no clean, fast way to roll back to a known-good version.
- The offline win was real *as an offline number* — but it didn't account for serving latency, the payload-contract break, or the online objective (CTR) diverging from the offline objective (ranking loss).

## Attempts

- Tried: full cutover gated only on the offline metric. This *was* the failure — offline lift is necessary, not sufficient; it can't see serving latency, contract breaks, or an online/offline objective mismatch.
- Tried: rolling back by re-copying the old artifact. Slow and error-prone (40 min, uncertain which version) precisely because the old version wasn't an addressable registry entry.
- Tried (the fix): make the **registry the deploy source of truth**, then **shadow the breaking change, then canary the rest**. Shadow mode ran the new version on live traffic with its predictions logged but not served — which immediately exposed both the payload-contract break and the latency regression with *zero* user impact. After fixing those, a canary (1% → 10% → 100%, gated on live CTR with a statistical check) caught that even the corrected version was a slight CTR *regression*, so it was never promoted. Rollback became "repoint serving at the previous registry version" — seconds, not 40 minutes.

## Resolution

**Deploy a registered version from the registry, never a copied file — and roll out with shadow then canary so a bad version is caught small and undone fast.** The durable shape:

1. **The registry is the source of truth for what's deployed.** Serving points at a registry version (or alias like `@champion`), so "what's live?" and "roll back to the last good one" are both one addressable operation, not archaeology. A copied file is an un-versioned, un-auditable liability.
2. **Match the rollout to the risk.** A breaking/contract-changing version → shadow first (zero user impact; validates output shape, distribution, and latency on real traffic). A same-schema change with a live metric and a known baseline → canary (1%→10%→100%, gated on the live metric). A low-risk incremental retrain → direct deploy with monitoring. Don't full-cutover a partially-breaking change on an offline number alone.
3. **Offline better ≠ online better.** The offline metric can't see serving latency, a payload-contract break, or an online objective (CTR/revenue) that diverges from the offline one (loss/AUC). The canary's live-metric gate is what surfaces that gap *before* all users feel it — and here it correctly *blocked* a version that won offline but lost online.
4. **Make rollback a first-class, rehearsed operation.** If undoing a deploy is a 40-minute scramble, the rollout isn't safe regardless of how good the canary is. Registry-versioned serving makes rollback fast; rehearse it so it's muscle memory under incident pressure.

The trap is treating the offline leaderboard as the promotion decision. It's the *entry ticket* to a rollout, not the rollout's verdict — the verdict is the live signal under canary, and the safety net is a registry rollback that takes seconds.

**Action for the next engineer:** never promote a model to full traffic on offline metrics alone. Deploy from the registry, shadow anything that changes the output contract or a dependency, canary anything with a live metric, and confirm the rollback path is one operation before you start. Route "is the canary's lift/regression real?" to `applied-statistics` — a 6% CTR move on an hour of traffic still needs a significance check.

Cross-reference: complements [`../best-practices/roll-out-with-shadow-then-canary.md`](../best-practices/roll-out-with-shadow-then-canary.md), [`../best-practices/shadow-mode-before-live-traffic.md`](../best-practices/shadow-mode-before-live-traffic.md), and [`../best-practices/registry-is-the-source-of-truth.md`](../best-practices/registry-is-the-source-of-truth.md); traverse the "model rollout — shadow, canary, or full deploy?" tree in [`../knowledge/ml-engineering-decision-trees.md`](../knowledge/ml-engineering-decision-trees.md). Whether a canary's measured CTR delta is real, not noise → `applied-statistics`.
