# Choose sidecar vs ambient mode deliberately when installing a service mesh

**Status:** Primary diagnostic
**Domain:** Kubernetes / service mesh
**Applies to:** `cloud-native-kubernetes`

---

## Why this exists

Service mesh adoption often stalls because the sidecar model (Envoy injected into every pod) visibly increases CPU and memory overhead — sometimes 50–200m CPU and 50–100Mi per pod. Teams either abandon the mesh or run it at inconsistent injection. Ambient mode (Istio 1.22+, GA for L4 in 2024) moves the data plane out of pod sidecars into a per-node ztunnel and a per-namespace waypoint proxy — radically reducing per-pod overhead for L4 mTLS, while adding a waypoint proxy only for pods needing L7 features. The decision to use sidecar or ambient depends on whether you need L7 per-pod policies, your Kubernetes and Istio version, and whether the added complexity of ambient is justified.

## How to apply

**Decision shortcut:**

| Requirement | Mode |
|---|---|
| mTLS for all east-west + no per-pod CPU overhead | Ambient (ztunnel only) |
| L7 per-request retry/timeout/traffic-split | Ambient with waypoint proxy |
| Fine-grained per-pod L7 policies, precise header routing | Sidecar |
| Istio version < 1.22 or ambient not GA in your CNI/cloud | Sidecar |
| Simplest possible install, most mature | Sidecar |

**Sidecar (traditional):**
```yaml
# Enable sidecar injection on a namespace
kubectl label namespace production istio-injection=enabled
```

**Ambient mode:**
```bash
# Install Istio with ambient profile (requires compatible CNI + k8s 1.28+)
istioctl install --set profile=ambient

# Label namespace for ambient (no sidecar injection)
kubectl label namespace production istio.io/dataplane-mode=ambient

# Add a waypoint proxy for L7 features in the namespace
istioctl waypoint apply --namespace production --enroll-namespace
```

**Do:**
- Evaluate ambient mode for new mesh deployments on Kubernetes 1.28+ with a compatible CNI (eBPF-based: Cilium, or Istio CNI).
- Use `istioctl analyze` to validate your mesh configuration before rolling to production.
- Start with L4 ambient (ztunnel only) for mTLS; add waypoint proxies only for namespaces that need L7 policies.
- Measure per-pod CPU/memory with sidecars before committing to a mode for a large cluster.

**Don't:**
- Enable sidecar injection on `kube-system` or `istio-system` namespaces.
- Run ambient and sidecar modes in the same namespace — the behavior is undefined.
- Treat ambient as "simpler" for operations if your team has zero ambient ops experience — it has its own failure modes.

## Edge cases / when the rule does NOT apply

- **Non-Istio meshes** (Linkerd, Consul Connect): Linkerd uses micro-proxies rather than Envoy sidecars and has a different overhead profile; Consul Connect has its own architecture. Evaluate the mesh choice before the sidecar/ambient question.
- **Clusters too small for mesh overhead** (< 5 nodes, < 20 pods): the mesh justify itself only when mTLS and traffic management are genuinely needed; small clusters may be better served by NetworkPolicy + application-level auth.

## See also

- [`../agents/service-mesh-networking-engineer.md`](../agents/service-mesh-networking-engineer.md) — owns mesh selection, configuration, and mTLS design.
- [`./mesh-must-earn-its-complexity.md`](./mesh-must-earn-its-complexity.md) — the prerequisite rule: confirm the mesh is justified before choosing a mode.

## Provenance

Codifies the `service-mesh-networking-engineer` remit from `CLAUDE.md` §1: "service-mesh (mTLS, traffic-splitting for canary, retries/timeouts/circuit-breaking)" and the capability map note: "Istio/Linkerd — mTLS, traffic-split; weigh sidecar cost (ambient mode emerging)." Ambient mode reached L4 GA in Istio 1.22 (2024); verify L7 GA status before production adoption.

---

_Last reviewed: 2026-06-05 by `claude`_
