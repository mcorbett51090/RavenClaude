---
scenario_id: 2026-06-05-ingress-503-dns-and-readiness
contributed_at: 2026-06-05
plugin: cloud-native-kubernetes
product: ingress-nginx
product_version: "unknown"
scope: likely-general
tags: [ingress, 503, dns, readiness-probe, endpoints, service-selector]
confidence: medium
reviewed: false
---

## Problem

A freshly-deployed service returned **HTTP 503 Service Temporarily Unavailable** through its Ingress, intermittently at first and then constantly. The pods were `Running`. `curl` from inside the cluster to the pod IP worked. The instinct was "the Ingress controller is broken" — but the controller was fine; it had **no healthy endpoints to route to**, and the reason changed over the incident.

## Constraints context

- An `ingress-nginx` controller fronting a Deployment behind a `ClusterIP` Service.
- The pods passed their `livenessProbe` but had **no `readinessProbe`** — so a pod that was `Running` but not yet serving was still being added to the Service's endpoints (early traffic) and, after a config change, a pod that had *stopped* serving stayed in rotation.
- A second, separate cause that surfaced later: a label typo. The Service `selector: app: web-api` did not match the pods' actual label `app: web` (a rename mid-PR). The Service had **zero endpoints** — `kubectl get endpoints <svc>` showed `<none>`.
- DNS was a red herring the team chased first: `nslookup` of the in-cluster Service name resolved fine; the problem was never name resolution, it was that the resolved Service had no backing pods.

## Attempts

- Tried: restarting the ingress controller. No effect — a 503 from `ingress-nginx` with no upstreams is "no healthy endpoint," not a controller fault.
- Tried: chasing DNS (`nslookup`, CoreDNS logs). DNS resolved correctly; this burned an hour. The Service *name* worked; the Service had no *endpoints*.
- Tried: reading `kubectl get endpoints <service>` and `kubectl describe svc <service>`. `ENDPOINTS: <none>` was the diagnosis — the Service selector matched no pods. [verify-at-use — `kubectl get endpoints` semantics; on newer clusters prefer `kubectl get endpointslices`.]
- Tried (the fixes that worked): (a) fixed the Service `selector` to match the pods' real labels — endpoints populated immediately and the constant 503 cleared; (b) added a `readinessProbe` hitting the app's `/healthz` so only serving pods receive traffic — this killed the *intermittent* 503s during deploys (the early-traffic and draining-pod windows).

## Resolution

**A 503 through an Ingress almost always means "no healthy endpoint," not "the Ingress is broken" — walk the chain Ingress → Service → endpoints → pod, and the empty link is your bug.** The order:

1. **`kubectl get endpoints <service>` (or `endpointslices`)** — if it's `<none>` or empty, the Service selector doesn't match any *ready* pod. That's the 503. Don't touch the Ingress controller yet.
2. **Empty because of a selector mismatch?** Compare `kubectl describe svc` `Selector:` against the pods' actual labels (`kubectl get pods --show-labels`). A rename or typo is the classic cause.
3. **Empty because pods aren't ready?** A pod with no `readinessProbe` is added to endpoints the instant it's `Running` (serves too early) and never removed when it stops serving. Add a readiness probe so endpoints track *serving*, not *running*.
4. **Only then suspect DNS or the controller** — and verify DNS by resolving the name, not by assuming. A name that resolves to a service with no endpoints is the trap that sends teams down the DNS rabbit hole.

The trap is that "503" reads like an edge/controller problem, so teams restart the Ingress controller and chase DNS — neither of which can manufacture an endpoint. The missing endpoint is upstream of all of it.

**Action for the next engineer:** on any Ingress 503, the first command is `kubectl get endpoints <service>`, not an Ingress-controller log dive. Empty endpoints → fix the selector or add a readiness probe. Populated endpoints but still 503 → *then* it's worth looking at the controller, TLS, or the upstream timeout.

Cross-reference: complements [`../best-practices/probes-are-mandatory.md`](../best-practices/probes-are-mandatory.md). The expose/route decision tree in [`../knowledge/cloud-native-kubernetes-decision-trees.md`](../knowledge/cloud-native-kubernetes-decision-trees.md) covers the Ingress/Gateway-API choice; the networking-and-ingress sizing tree in [`../knowledge/networking-and-ingress-decision-trees.md`](../knowledge/networking-and-ingress-decision-trees.md) covers controller selection. Mesh-level routing belongs to `service-mesh-networking-engineer`.
