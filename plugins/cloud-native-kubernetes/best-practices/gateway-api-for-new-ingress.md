# Use Gateway API for new ingress — not the Ingress resource

**Status:** Pattern
**Domain:** Kubernetes / networking
**Applies to:** `cloud-native-kubernetes`

---

## Why this exists

The Kubernetes `Ingress` resource is minimal and forces routing features (header matching, traffic weighting, TLS routing) into non-standard annotations that differ per controller. Gateway API is the official successor: it is role-oriented (GatewayClass, Gateway, HTTPRoute owned by different personas), expressive (header-based routing, traffic weighting, URL rewrites are first-class), and portable across controllers (Istio, Cilium, NGINX, AWS Load Balancer Controller, etc.). For new deployments, Gateway API reduces annotation sprawl and is the standard the ecosystem is converging on. The capability map entry confirms: "Gateway API — GA (replacing Ingress for new)."

## How to apply

```yaml
# Gateway — provisioned by the infrastructure/platform team
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: prod-gateway
  namespace: gateway-system
spec:
  gatewayClassName: nginx   # or cilium, istio, aws, etc.
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      tls:
        mode: Terminate
        certificateRefs:
          - kind: Secret
            name: prod-tls-cert
      allowedRoutes:
        namespaces:
          from: Selector
          selector:
            matchLabels:
              gateway-access: "true"
---
# HTTPRoute — owned by the application team
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: app-route
  namespace: production
spec:
  parentRefs:
    - name: prod-gateway
      namespace: gateway-system
  hostnames:
    - "app.example.com"
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api
      backendRefs:
        - name: api-service
          port: 8080
          weight: 100
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: frontend-service
          port: 3000
```

**Traffic splitting for canary:**
```yaml
# Split traffic 90/10 between stable and canary
backendRefs:
  - name: api-service-stable
    port: 8080
    weight: 90
  - name: api-service-canary
    port: 8080
    weight: 10
```

**Do:**
- Separate the `Gateway` resource (platform team) from `HTTPRoute` resources (app team) — the role separation is a core Gateway API feature.
- Use `allowedRoutes.namespaces` to control which namespaces can attach routes to the gateway.
- Migrate existing `Ingress` resources to `HTTPRoute` when the controller supports Gateway API.

**Don't:**
- Create new workloads with `Ingress` unless your controller doesn't yet support Gateway API.
- Put the Gateway in the application namespace — it is infrastructure, owned by the platform team.
- Mix `Ingress` and `HTTPRoute` on the same controller — some controllers support both, but the behavior can be surprising.

## Edge cases / when the rule does NOT apply

- **Controllers that do not yet support Gateway API**: check your specific ingress controller's Gateway API support matrix before committing to it.
- **Simple single-path, single-service ingress** with no routing logic in an existing Ingress-only cluster: a plain `Ingress` is acceptable; do not add Gateway API overhead for a single static route.

## See also

- [`../agents/service-mesh-networking-engineer.md`](../agents/service-mesh-networking-engineer.md) — owns Gateway API and ingress design.
- [`./mesh-must-earn-its-complexity.md`](./mesh-must-earn-its-complexity.md) — Gateway API is the ingress/north-south tool; a mesh is the east-west tool.

## Provenance

Codifies the `service-mesh-networking-engineer` remit from `CLAUDE.md` §1 and the capability map entry: "Gateway API — GA (replacing Ingress for new) — role-oriented, expressive routing." Gateway API v1 reached GA in Kubernetes 1.28 (2023).

---

_Last reviewed: 2026-06-05 by `claude`_
