# Enforce Pod Security Admission restricted profile in production namespaces

**Status:** Pattern
**Domain:** Kubernetes / pod security
**Applies to:** `cloud-native-kubernetes`

---

## Why this exists

Without Pod Security Admission (PSA), any pod in a namespace can declare `privileged: true`, `hostNetwork: true`, or `runAsUser: 0` — giving workloads host-level access that bypasses container isolation. PSA enforces security profiles at the namespace level: `baseline` prevents the most obvious privilege escalations; `restricted` enforces the full hardened set (non-root, no privileged escalation, read-only root filesystem recommended, seccomp profile required). Pod Security Policies (the predecessor) were removed in Kubernetes 1.25 — PSA is the supported replacement.

## How to apply

```yaml
# Label namespaces to enforce the restricted or baseline profile
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    # enforce: hard-deny pods that violate the profile
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    # warn: allow but warn in kubectl output
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/warn-version: latest
    # audit: log violations to the audit log
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/audit-version: latest
```

For workloads running under `restricted`, set the required security context:
```yaml
containers:
  - name: app
    image: myregistry.example.com/app:1.4.7
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      runAsUser: 65534   # nobody
      capabilities:
        drop:
          - ALL
    volumeMounts:
      - name: tmp
        mountPath: /tmp   # writable scratch space
volumes:
  - name: tmp
    emptyDir: {}   # tmp is writable; root FS is read-only
```

**Profile selection guidance:**

| Namespace type | Recommended profile |
|---|---|
| Production workloads | `restricted` |
| Staging workloads | `restricted` |
| System namespaces (kube-system) | `privileged` (system components need host access) |
| Dev/lab namespaces | `baseline` (some dev tooling needs relaxed rules) |
| Monitoring (Prometheus node exporter) | `privileged` or node-exporter-specific exception |

**Do:**
- Start with `warn` + `audit` mode in staging to identify non-compliant workloads before switching to `enforce`.
- Fix workloads to comply with `restricted` rather than downgrading the namespace profile.
- Drop all Linux capabilities and add back only what is genuinely required (`NET_BIND_SERVICE` for port 80/443 in the container).

**Don't:**
- Label `kube-system` as `restricted` — system components like `kube-proxy` and CSI drivers need host access.
- Use `privileged` mode for application workloads — it grants full host access and is essentially a container escape.
- Assume `baseline` is "secure" for prod — it only blocks the worst violations; `restricted` is the security target.

## Edge cases / when the rule does NOT apply

- **DaemonSets for observability agents** (node exporter, log forwarder): they legitimately need host filesystem access; run them in a dedicated namespace with a `privileged` or custom `baseline` exception, not in the app namespace.
- **Legacy workloads** that cannot be modified to comply immediately: use `warn` mode and set a remediation deadline; don't accept `privileged` permanently.

## See also

- [`../agents/k8s-platform-operator.md`](../agents/k8s-platform-operator.md) — owns admission control and namespace security.
- [`./admission-control-over-manual-review.md`](./admission-control-over-manual-review.md) — PSA is an admission controller; OPA Gatekeeper/Kyverno provide additional policy coverage.
- [`./least-privilege-in-cluster.md`](./least-privilege-in-cluster.md) — PSA is the pod-security leg of least privilege.

## Provenance

Codifies the `k8s-platform-operator` remit in `CLAUDE.md` §1: "admission control (policy)" and the capability map entry for "Pod Security Admission (GA — replaced PSP)." Standard Kubernetes hardening from the CIS Kubernetes Benchmark v1.9 and the Kubernetes security documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
