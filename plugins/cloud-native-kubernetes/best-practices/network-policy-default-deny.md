# Apply a default-deny NetworkPolicy before adding allow rules

**Status:** Absolute rule
**Domain:** Kubernetes / networking / security
**Applies to:** `cloud-native-kubernetes`

---

## Why this exists

Without any NetworkPolicy, every pod in a cluster can reach every other pod — namespace boundaries are administrative, not network boundaries. A compromised pod can scan and connect to any other service. A default-deny NetworkPolicy closes all ingress and egress for pods in a namespace, and subsequent allow policies then open exactly the traffic needed. The house opinion #3 is explicit: "least privilege in the cluster — default-deny NetworkPolicies." The order matters: apply default-deny first, then add allow rules, not the reverse.

## How to apply

```yaml
# 1. Apply default-deny FIRST in each namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}   # matches all pods in the namespace
  policyTypes:
    - Ingress
    - Egress
---
# 2. Allow specific ingress from the ingress controller
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-controller
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8080
---
# 3. Allow egress to the database namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-db-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: database
      ports:
        - protocol: TCP
          port: 5432
---
# 4. Allow DNS egress (required for name resolution)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

**Do:**
- Apply default-deny in every production and staging namespace — not just namespaces with sensitive workloads.
- Always add a DNS allow rule alongside default-deny — without it, DNS resolution fails and pods cannot reach any service by name.
- Use `namespaceSelector` + `podSelector` together for precise allow rules.
- Test NetworkPolicies in a dev namespace before applying to production.

**Don't:**
- Add default-deny to `kube-system` — the control plane components need unrestricted communication.
- Apply NetworkPolicies without a CNI that enforces them (Flannel without Calico, for example, does not enforce NetworkPolicy).
- Use NetworkPolicies as the only east-west control for hostile tenants — see `namespaces-are-the-tenancy-boundary` for the limits.

## Edge cases / when the rule does NOT apply

- **Clusters without a NetworkPolicy-enforcing CNI** (e.g., basic Flannel): NetworkPolicies exist in the API server but are not enforced — they give false security. Install Calico, Cilium, or a CNI that enforces them first.
- **Development namespaces** with rapidly changing service topology: default-deny in dev is noisy; apply it at least to staging and prod.

## See also

- [`../agents/k8s-platform-operator.md`](../agents/k8s-platform-operator.md) — owns NetworkPolicy design and namespace security.
- [`./namespaces-are-the-tenancy-boundary.md`](./namespaces-are-the-tenancy-boundary.md) — NetworkPolicies are the network complement to RBAC namespace isolation.
- [`./least-privilege-in-cluster.md`](./least-privilege-in-cluster.md) — NetworkPolicy is the network leg of least privilege; RBAC is the API leg.

## Provenance

Codifies the `k8s-platform-operator` house opinion #3 from `CLAUDE.md` §2: "least privilege in the cluster — default-deny NetworkPolicies." Standard Kubernetes security hardening from the CIS Kubernetes Benchmark and the NIST SP 800-190 container security guide.

---

_Last reviewed: 2026-06-05 by `claude`_
