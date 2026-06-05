---
scenario_id: 2026-06-05-rollout-stuck-pdb-deadlock
contributed_at: 2026-06-05
plugin: cloud-native-kubernetes
product: kubernetes
product_version: "unknown"
scope: likely-general
tags: [rollout, pdb, maxunavailable, deadlock, drain, surge]
confidence: high
reviewed: false
---

## Problem

A Deployment rollout hung forever. `kubectl rollout status deploy/<name>` sat at `Waiting for deployment "..." rollout to finish: 2 out of 3 new replicas have been updated...` and never advanced. Separately, a routine node drain for a cluster upgrade (`kubectl drain <node>`) blocked with `Cannot evict pod as it would violate the pod's disruption budget`. Both were the same root cause wearing two costumes: a **PodDisruptionBudget that mathematically could not be satisfied** during a voluntary disruption.

## Constraints context

- A 3-replica Deployment with a `PodDisruptionBudget` of `minAvailable: 3` (someone set it equal to the replica count "to be safe").
- The Deployment's `strategy` was `RollingUpdate` with `maxUnavailable: 1`, `maxSurge: 0` (a memory-tight node pool, so surge was disabled to avoid scheduling a 4th pod).
- With `minAvailable: 3` and only 3 replicas, the PDB allows **zero** voluntary disruptions — so the rolling update (which needs to take one pod down to replace it) and the node drain (which needs to evict a pod) both deadlock against the same budget.
- A second contributor: one replica was wedged in `Pending` (no node had room) so even the *involuntary* count was already at the edge.

## Attempts

- Tried: `kubectl rollout restart` — no effect; restart issues the same rolling update that's already stuck on the PDB.
- Tried: `kubectl drain --force` — `--force` only overrides unmanaged (bare) pods; it does **not** override a PDB. The drain still blocked. (`--disable-eviction` *would* bypass the PDB by deleting pods directly — but that defeats the safety the PDB exists for and risks an availability dip; it is a break-glass move, not the fix.)
- Tried: reading `kubectl get pdb` — `ALLOWED DISRUPTIONS: 0` was the whole diagnosis in one column. `minAvailable: 3` on a 3-replica set means the budget can never release a pod. [verify-at-use — `kubectl get pdb` `ALLOWED DISRUPTIONS` column semantics; confirm against the PDB docs for your cluster version.]
- Tried (the fix that worked): set the PDB to `minAvailable: 2` (or equivalently `maxUnavailable: 1`) so the budget permits exactly one pod down at a time, AND bumped the Deployment to 4 replicas so steady-state still keeps 3 up during a single disruption. `ALLOWED DISRUPTIONS` went to 1; the rollout completed and the drain proceeded one pod at a time.

## Resolution

**A PDB whose `minAvailable` equals (or exceeds) the replica count permits zero voluntary disruptions — it deadlocks every rollout, drain, and node upgrade.** The PDB is a *budget for voluntary disruption*, not a floor you pin to "all of them." The order:

1. **`kubectl get pdb`** — read the `ALLOWED DISRUPTIONS` column. `0` means nothing can be voluntarily evicted; that is the deadlock, full stop.
2. **Reconcile the math:** `minAvailable` must be **strictly less** than the replica count (or use `maxUnavailable`, which is relative and survives replica-count changes). A common safe choice: `maxUnavailable: 1` on a 3+ replica Deployment.
3. **Give the rollout room to move:** either `maxSurge: 1` (schedule the new pod before killing an old one — needs node headroom) or accept `maxUnavailable: 1` with a PDB that allows it. Surge-0 + minAvailable-equals-replicas is the classic double-bind.
4. **Clear any `Pending` replica first** — a workload that can't schedule its current replicas will never satisfy a budget during disruption; that's a capacity problem feeding the PDB problem.

The trap is that `minAvailable: 3` *looks* like the safest possible setting ("never drop below 3!") but on a 3-replica set it is the **least** safe operationally — it makes the workload un-upgradable and blocks node maintenance, so the next forced node reboot takes it down anyway with no graceful path.

**Action for the next engineer:** before declaring a rollout "broken," run `kubectl get pdb` and read `ALLOWED DISRUPTIONS`. If it's `0`, the PDB is the deadlock — set `minAvailable` strictly below the replica count (or switch to `maxUnavailable`), and ensure surge or unavailable budget gives the rolling update somewhere to step.

Cross-reference: this is the field-note complement to [`../best-practices/pdb-with-every-rollout.md`](../best-practices/pdb-with-every-rollout.md). The upgrade-blocking-vs-optional tree in [`../knowledge/cloud-native-kubernetes-decision-trees.md`](../knowledge/cloud-native-kubernetes-decision-trees.md) covers when a drain-blocking PDB turns a routine upgrade into a blocking one; the node-pressure/eviction mechanics belong to `k8s-platform-operator`.
