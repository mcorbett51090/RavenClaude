---
name: cluster-upgrade-and-capacity
description: "Playbook for planning and executing a safe Kubernetes control-plane and node-pool upgrade, covering version-skew rules, pre-flight checks, node drain sequencing, and capacity planning for node pools. Prevents the most common upgrade-day outages."
---

# Cluster Upgrade and Capacity Planning

## 1. Version Skew Rules (non-negotiable)

| Component pair | Max skew |
|---|---|
| kube-apiserver ↔ kubelet | kubelet may be at most **2 minor versions behind** apiserver |
| kube-apiserver ↔ kube-controller-manager / kube-scheduler | Must be **same minor version** |
| kubectl ↔ kube-apiserver | kubectl may be ±1 minor version |
| Helm chart API versions | Must target APIs present in the **target** cluster version |

**Upgrade order:** control plane first, then node pools one at a time.

## 2. Pre-Upgrade Checklist

Run these before touching anything:

- [ ] `kubectl get nodes` — all nodes `Ready`; no `NotReady` or `Unknown`
- [ ] Check deprecated API usage: `kubectl api-resources --verbs=list` + run [pluto](https://github.com/FairwindsOps/pluto) or `kubectl deprecations` against manifests
- [ ] Audit admission webhooks — `ValidatingWebhookConfiguration` and `MutatingWebhookConfiguration`: set `failurePolicy: Fail` webhooks will block upgrades if their endpoint is down
- [ ] Verify PodDisruptionBudgets allow at least 1 disruption on every workload (`kubectl get pdb -A`)
- [ ] Snapshot etcd (managed clusters: confirm automated backup is current)
- [ ] Review add-on compatibility matrix: CNI, CSI drivers, metrics-server, CoreDNS — all must support the target version
- [ ] Read the upstream changelog for removed/deprecated APIs in the target minor version

## 3. Upgrade Sequence

```
1. Upgrade control plane (managed: click/Terraform; self-managed: kubeadm upgrade apply)
2. Cordon + drain node 1 of pool A  →  confirm pod reschedule  →  upgrade node  →  uncordon
3. Repeat for remaining nodes in pool A (rolling — respect PDBs)
4. Upgrade node pool B (if separate), same rolling procedure
5. Upgrade add-ons to versions compatible with the new control plane
6. Run smoke tests against the cluster API and critical workloads
```

**Drain flags:**
```bash
kubectl drain <node> \
  --ignore-daemonsets \    # DaemonSet pods are managed separately
  --delete-emptydir-data \ # Evict pods using emptyDir (data is lost — intentional)
  --timeout=300s
```

## 4. Capacity Planning

### Node Pool Sizing Formula

```
Required nodes = ceil( sum(all-pod-requests) / (node-allocatable × target-utilization) )
```

- `node-allocatable` = node capacity minus OS/kubelet/system reserved (check `kubectl describe node`)
- `target-utilization` = 0.70 for CPU, 0.80 for memory (headroom for burst and rolling upgrades)
- Add 1–2 surge nodes for the rolling upgrade itself (pods need somewhere to land during drain)

### HPA Sizing Inputs

| Input | Where to get it |
|---|---|
| Observed p99 CPU/mem per replica | Prometheus / CloudWatch Container Insights |
| Traffic multiplier at peak | Load test or prod traffic pattern |
| Pod startup time | `kubectl describe pod` → container start latency |

Set `minReplicas` ≥ 2 (single replica = planned outage during upgrade).

### Cluster Autoscaler vs Karpenter

| Factor | Cluster Autoscaler | Karpenter |
|---|---|---|
| Node provisioning granularity | Node group / ASG | Any instance type that fits |
| Speed | 1–3 min (ASG warm) | 30–90 s (direct EC2 API) |
| Bin-packing | Limited | Aggressive consolidation |
| Multi-cloud | Yes | AWS-native (Azure/GCP in progress) |

Use Karpenter on EKS when bin-packing efficiency and speed matter; use CA otherwise.

## 5. Post-Upgrade Validation

```bash
kubectl get nodes                          # all Ready, correct version
kubectl get pods -A | grep -v Running      # no CrashLoopBackOff / Pending
kubectl top nodes                          # resource usage sane
kubectl get events -A --sort-by=.lastTimestamp | tail -50
```

Smoke-test critical services and verify SLO dashboards show no degradation for 15 minutes before declaring success.

## Pitfalls

- Skipping the deprecated-API scan — `v1beta1` removed in 1.25 / 1.26 breaks apply on upgrade day.
- `failurePolicy: Fail` webhooks whose backend pod is on the node being drained — the drain blocks and the upgrade hangs.
- Single-replica stateful workloads with `maxUnavailable: 1` PDBs — drain waits forever for a pod that can't move.
- Upgrading node pools before the control plane — violates skew rules and can corrupt cluster state.
- Forgetting to upgrade the CNI/CSI add-ons — they often break silently on a new API server.
- No capacity surge during rolling upgrade — pods evicted during drain find no nodes with capacity and stay `Pending`.
