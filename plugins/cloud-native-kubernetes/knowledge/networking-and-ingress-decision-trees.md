# Networking & Ingress — Decision Trees

_Topic-specific complement to [`cloud-native-kubernetes-decision-trees.md`](cloud-native-kubernetes-decision-trees.md). That file answers the **architecture** questions — "do we need a mesh?" and "north-south vs east-west routing." This file answers the **implementation** questions one layer down: which ingress mechanism to pick once you've decided you need north-south routing, and how to debug an Ingress that returns errors._

**Last verified:** 2026-06-05 against the Kubernetes Gateway API status (GA) and Ingress documentation. Gateway-API GA status and controller feature support are `[verify-at-use]` — re-check the controller's conformance level before committing.

Traverse before installing an ingress controller or writing an Ingress/Gateway resource.

## Decision Tree: Which north-south routing mechanism?

You've decided clients need to reach a service from outside (the architecture tree sent you here). Now pick the mechanism. **Gateway API is the successor to Ingress for new routing**; reach for plain Service types only when the need is trivial.

```mermaid
flowchart TD
    START[Clients need to reach a service from outside] --> L4{Is it L7/HTTP, or raw L4 TCP/UDP?}
    L4 -->|Raw L4 TCP/UDP<br/>databases, game servers, custom protocol| LB[Service type LoadBalancer<br/>cloud LB per service]
    L4 -->|L7 HTTP/HTTPS| NEW{New routing, or extending existing Ingress?}
    NEW -->|New| GW{Need expressive routing —<br/>header/weight splits, multi-team,<br/>cross-namespace, role separation?}
    GW -->|Yes| GATEWAY[Gateway API<br/>GatewayClass + Gateway + HTTPRoute]
    GW -->|No, single team, simple host/path| SIMPLE{Just one or two host/path rules?}
    SIMPLE -->|Yes| INGRESS[Ingress resource<br/>existing controller, simplest]
    SIMPLE -->|No, growing| GATEWAY
    NEW -->|Extending existing Ingress estate| INGRESS
    GATEWAY --> CTRL[Pick a Gateway-API-conformant controller<br/>see the controller-selection tree below]
    INGRESS --> CTRL
```

**Rationale per leaf:**

- _Service type LoadBalancer_ — for non-HTTP L4 traffic (TCP/UDP), or a single service that just needs an external IP. One cloud load balancer per service; simple but doesn't scale to many services (cost + IP sprawl).
- _Ingress resource_ — the established L7 mechanism: host/path rules against a shared controller. Fine for a small, single-team estate; its extension points are annotation-driven and controller-specific (a portability tax).
- _Gateway API_ — the role-oriented successor: `GatewayClass` (infra), `Gateway` (cluster-op owned listener), `HTTPRoute` (app-team owned routing). Native header/weight-based splits, cross-namespace routing, and clean multi-team separation without annotation soup. **The default for new north-south routing.**

**Tradeoffs summary:**

| Mechanism | Layer | Multi-team / expressive | Use when |
|---|---|---|---|
| Service LoadBalancer | L4 | No | Raw TCP/UDP, or one external service |
| Ingress | L7 | Limited (annotations) | Small single-team HTTP estate |
| Gateway API | L7 | Yes (role-separated) | New routing, multi-team, weight/header splits |

## Decision Tree: Picking the ingress / Gateway controller

The mechanism (above) is the *API*; the controller is the *implementation*. Match it to what you already run and what you need.

```mermaid
flowchart TD
    START[Choosing a controller] --> MESH{Already running a service mesh<br/>Istio / Linkerd?}
    MESH -->|Yes, Istio| ISTIOGW[Use the mesh's Gateway<br/>one data plane for north-south + east-west]
    MESH -->|No| MANAGED{On a managed cloud cluster<br/>and want the cloud LB integrated?}
    MANAGED -->|Yes| CLOUDGW[Cloud provider Gateway/Ingress controller<br/>AKS/EKS/GKE native — owned by the cloud plugin]
    MANAGED -->|No, cloud-agnostic| FEAT{Need advanced L7 features<br/>WAF, auth, rate-limit at the edge?}
    FEAT -->|Yes| FEATURE[A feature-rich controller<br/>an API-gateway-class controller<br/>verify Gateway-API conformance at use]
    FEAT -->|No, standard HTTP| STANDARD[A conformant Gateway-API<br/>reference impl or a supported controller]
```

> **Do not pick community `ingress-nginx` for a new cluster.** The Kubernetes project **retired** the community `ingress-nginx` controller: best-effort maintenance ended **March 2026**, after which there are **no releases, bug fixes, or security patches** and the repos go read-only (per the [Nov 11 2025 retirement notice](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/) and the [Jan 29 2026 Steering/Security-Response statement](https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/)). Existing deployments keep functioning, but standing up `ingress-nginx` on a **new** cluster now signs up for un-patched CVEs. Migrate to the **Gateway API** (the recommended successor) or a supported/commercial ingress controller. `[verified 2026-07-08 — kubernetes.io]`

**Rationale:**

- _Mesh Gateway_ — if you already run Istio/Linkerd, route north-south through the mesh's gateway so you operate one data plane, not two. (Don't *add* a mesh just to get an ingress — see the architecture file's mesh-justification tree.)
- _Cloud-native controller_ — on a managed cluster, the cloud's own Gateway/Ingress controller integrates the cloud load balancer + IAM cleanly; that selection is the **cloud plugin's** lane (`azure-cloud` / `aws-cloud` / `gcp-cloud`), this team consumes it.
- _Feature-rich / standard controller_ — cloud-agnostic clusters pick a controller by feature need; **verify the controller's Gateway-API conformance level** before committing if you're on the Gateway API. `[verify-at-use]` **Note the community `ingress-nginx` retirement (March 2026, no further security patches — see the callout above): prefer a Gateway-API implementation or a maintained/commercial controller for new builds.**

## Decision Tree: Debugging an Ingress that returns an error

A controller-level error code points at *where* in the chain the request died. Walk it from the closest layer outward.

```mermaid
flowchart TD
    START[Ingress returns an error] --> CODE{Which status?}
    CODE -->|503 Service Unavailable| EP{kubectl get endpoints svc — empty?}
    EP -->|Empty / none| SEL[No ready endpoints:<br/>fix Service selector OR add a readinessProbe<br/>this is the usual 503 cause]
    EP -->|Populated| UPSTREAM[Upstream timeout / app erroring:<br/>check pod logs + the controller timeout annotations]
    CODE -->|404 Not Found| RULE[Host/path rule miss:<br/>check Ingress host + path + pathType,<br/>and ingressClassName matches the controller]
    CODE -->|502 Bad Gateway| PROTO[Upstream protocol/port mismatch:<br/>Service targetPort wrong, or app speaks https/h2c<br/>and the controller expects http]
    CODE -->|TLS / cert error| TLS[Secret missing/expired, wrong namespace,<br/>or SNI host mismatch — check the tls secretName]
```

**The load-bearing rule:** a **503 through an Ingress is almost always "no healthy endpoint," not a broken controller.** First command is `kubectl get endpoints <service>` (or `endpointslices`) — empty endpoints mean a Service selector mismatch or pods that never went `Ready`. Don't restart the controller or chase DNS until you've confirmed the Service actually has backing pods. `[verify-at-use — endpoints vs endpointslices command on your cluster version.]`

## See also

- [`cloud-native-kubernetes-decision-trees.md`](cloud-native-kubernetes-decision-trees.md) — the **architecture** trees (mesh-justification, north-south-vs-east-west, secrets source) this file complements.
- [`../best-practices/gateway-api-for-new-ingress.md`](../best-practices/gateway-api-for-new-ingress.md) and [`../best-practices/probes-are-mandatory.md`](../best-practices/probes-are-mandatory.md) — the rule form.
- [`../scenarios/2026-06-05-ingress-503-dns-and-readiness.md`](../scenarios/2026-06-05-ingress-503-dns-and-readiness.md) — the field note where the 503 debug tree was the fix.
- The mesh data plane, mTLS, and east-west traffic-splitting belong to `service-mesh-networking-engineer`; managed-cloud LB/controller selection to the cloud plugins.
