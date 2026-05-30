# Pick Azure compute from the decision tree, not from habit

**Status:** Pattern — strong default; deviate only with a written reason tied to a tree leaf.

**Domain:** Compute / Architecture

**Applies to:** `azure-cloud`

---

## Why this exists

The recurring "where should this run?" question has a habitual wrong answer — reach for AKS (or for whatever the team ran last) regardless of fit — and AKS carries the most operational burden of any Azure compute option (≥6 nodes for prod, node/upgrade management, network-policy design). Azure ships five distinct compute surfaces with different scale-to-zero behavior and ops cost: Static Web Apps, Azure Functions, Container Apps, App Service, and AKS. The two levers that actually decide are **scale-to-zero need** (event-driven/spiky workloads waste money on always-on plans) and **ops burden you can absorb** (PaaS simplicity vs Kubernetes control). House opinion #7 is "pick compute from the tree" — traverse [`../knowledge/azure-compute-decision-tree.md`](../knowledge/azure-compute-decision-tree.md) before naming a service, and reserve AKS for when you genuinely need the Kubernetes API, a service mesh, GPU node pools, or multi-workload isolation.

## How to apply

Walk the tree top-to-bottom; the first branch that resolves cleanly is the answer. Compose per-service — Functions for the event-driven pieces, Container Apps or AKS for the core service — rather than forcing one host on everything.

```
Static SPA + light serverless API?        -> Static Web Apps (git-deployed, global)
Event-driven, sporadic/spiky, scale-to-0?  -> Azure Functions (Flex Consumption)
Need the Kubernetes API / mesh / GPU pools? -> AKS
Containerized + serverless scale / Dapr?    -> Container Apps  (house default for containers)
Otherwise a straightforward HTTP web app?   -> App Service (PaaS, deployment slots)
```

**Do:**
- Traverse the tree before recommending; cite the leaf you landed on and *why* (the observable condition that resolved).
- Default containers to **Container Apps** (serverless scale, Dapr, traffic-split) unless a Kubernetes-specific need pushes you to AKS.
- Make prod **zone-redundant** where the SKU supports it (house opinion #8); for Functions, remember Flex Consumption AZ needs ≥2 always-ready instances.
- Compose surfaces in one system — event-driven glue on Functions, core service on Container Apps/AKS.

**Don't:**
- Default to AKS because it's familiar; it's the most ops, picked only at the Kubernetes-API leaf.
- Put an event-driven, spiky workload on an always-on App Service plan and pay for idle.
- Assume Functions Consumption migrates in place to other plans — it doesn't (no deployment slots, one app per plan).

## Edge cases / when the rule does NOT apply

- **An existing AKS estate** with platform investment already amortized may absorb a new workload more cheaply than standing up a new surface — the tree informs greenfield; brownfield weighs the sunk platform.
- **Hard isolation / compliance** mandates (dedicated nodes, custom CNI, node-level controls) can land you on AKS even when Container Apps would otherwise fit — that's the multi-workload-isolation leaf firing legitimately.
- **The data tier** (Azure SQL / Cosmos / PostgreSQL Flexible Server) is a separate `azure-architect` call, not part of the compute tree.
- Hosting **a Claude app** on Azure (Container Apps / Functions / Foundry) is provisioned here, but the agent logic is `claude-app-engineering` — honor the seam (house opinion #15).

## See also

- [`../knowledge/azure-compute-decision-tree.md`](../knowledge/azure-compute-decision-tree.md) — the canonical compute tree + the non-Fabric data tier
- [`../knowledge/azure-ai-foundry.md`](../knowledge/azure-ai-foundry.md) — the AI hosting surface when the workload is a model/agent
- [`../agents/app-platform-engineer.md`](../agents/app-platform-engineer.md) — owns the compute decision and the Claude-app Azure host
- [`../agents/azure-architect.md`](../agents/azure-architect.md) — owns the cross-service call and the data tier

## Provenance

Codifies house opinion #7 ("pick compute from the tree") and #8 (zone-redundant prod) from [`../CLAUDE.md`](../CLAUDE.md) §3, and the compute anti-pattern in §4 ("defaulting to AKS when Container Apps/App Service fits"). Grounded in the compute decision tree knowledge file, itself sourced from Microsoft's compute-decision and container-service guides (retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
