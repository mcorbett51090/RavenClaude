---
scenario_id: 2026-06-05-cluster-cost-right-sizing
contributed_at: 2026-06-05
plugin: cloud-native-kubernetes
product: kubernetes
product_version: "unknown"
scope: likely-general
tags: [cost, right-sizing, requests, bin-packing, vpa, utilization]
confidence: medium
reviewed: false
---

## Problem

A cluster's cloud bill kept climbing while the team "wasn't deploying anything new." The node count had crept from 6 to 11 over a quarter. The dashboards showed **node CPU at ~25% and memory at ~40%** average utilization — the nodes were mostly idle, yet the cluster autoscaler kept adding nodes and refused to remove them. The instinct was "we need cheaper/bigger nodes"; the actual problem was that **resource *requests* were 3-4x the real usage**, so the scheduler thought every node was full when it was nearly empty.

## Constraints context

- ~80 workloads, most copied from a template that set `requests.cpu: "1"` and `requests.memory: "2Gi"` regardless of the app — a default nobody revisited.
- Real usage (from `kubectl top pods` and the metrics pipeline) was typically `~150m` CPU and `~400Mi` memory per pod — the requests were a 5-7x over-reservation.
- The **scheduler bin-packs on requests, not usage.** With every pod reserving 1 full core, a handful of pods "filled" a node on paper; the autoscaler added nodes to place pending pods, then could never scale down because each node's *requested* total stayed above the scale-down threshold even though actual usage was tiny.
- A few workloads were the opposite problem — under-requested and getting CPU-throttled — so a blanket "halve all requests" would have hurt them.

## Attempts

- Tried: switching to a larger node SKU "for better density." This made it worse — bigger nodes cost more and the over-requesting still left them ~25% utilized; the bill rose.
- Tried: lowering the cluster-autoscaler scale-down utilization threshold. It helped marginally but didn't touch the root cause — the requests, not the threshold, were lying to the scheduler.
- Tried (the diagnosis): ran VPA in **recommendation mode** (`updateMode: "Off"`) across the namespaces to get per-workload `target` requests from observed usage, and compared `sum(requests)` vs `sum(usage)` cluster-wide. The requested:used ratio was ~4:1 — quantifying the waste. [verify-at-use — VPA recommendation/`updateMode: Off` behavior; confirm against the VPA docs for your install.]
- Tried (the fix that worked): right-sized `requests` per workload toward the VPA `target` (request ≈ p50-p90 observed, not a flat template default), kept memory `request == limit` for predictable QoS, and added a `LimitRange` per namespace so new workloads couldn't re-introduce the 1-core default. Bin-packing tightened, the autoscaler drained and removed 4 nodes, and the bill dropped ~30% with no latency regression.

## Resolution

**A cluster that's expensive but shows low node utilization is almost always over-*requesting*, not under-provisioned — the scheduler reserves on requests, so inflated requests buy nodes you don't use.** The order:

1. **Compare requested vs used cluster-wide** — `sum(requests)` (what the scheduler reserves) against `sum(actual usage)` (`kubectl top`, the metrics pipeline). A high requested:used ratio (say >2:1) is the waste signal; low *node* utilization with high *requested* allocation is the fingerprint.
2. **Right-size requests per workload from observed usage** — VPA in recommendation mode gives per-workload targets. Request ≈ steady-state usage; don't copy a template default across unlike workloads.
3. **Don't blanket-cut** — under-requested, CPU-throttled workloads need requests *raised*; right-sizing is per-workload, both directions.
4. **Pin the gains with a `LimitRange`** per namespace so the next copy-paste deploy can't re-introduce the oversized default, and revisit quarterly.

The trap is that low utilization reads as "wrong node size," sending teams to resize or re-platform the node pool — which never recovers the waste, because the waste lives in the *requests*, not the nodes. Right-size the requests and the existing nodes empty out on their own.

**Action for the next engineer:** before resizing the node pool or tuning the autoscaler, pull requested-vs-used. If requests dwarf usage, that's the bill — right-size requests from VPA recommendations, fence it with a LimitRange, and let the autoscaler reclaim the nodes.

Cross-reference: complements [`../best-practices/resource-requests-and-limits-are-mandatory.md`](../best-practices/resource-requests-and-limits-are-mandatory.md) and [`../best-practices/quotas-and-limitranges-per-namespace.md`](../best-practices/quotas-and-limitranges-per-namespace.md). The workload-resource-sizing tree in [`../knowledge/workload-resource-and-autoscaling-decision-trees.md`](../knowledge/workload-resource-and-autoscaling-decision-trees.md) walks the request/limit/QoS choice; the metrics pipeline that surfaces real usage belongs to `observability-sre`, and managed-node-pool cost/SKU choices to the cloud plugins.
