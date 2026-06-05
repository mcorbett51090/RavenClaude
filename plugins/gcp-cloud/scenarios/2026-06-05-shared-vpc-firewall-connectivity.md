---
scenario_id: 2026-06-05-shared-vpc-firewall-connectivity
contributed_at: 2026-06-05
plugin: gcp-cloud
product: vpc
product_version: "unknown"
scope: likely-general
tags: [shared-vpc, firewall, default-deny, service-project, connectivity]
confidence: medium
reviewed: false
---

## Problem

A team migrating onto a **Shared VPC** could not get a new Cloud Run service (in a *service* project) to reach a Cloud SQL instance and an internal HTTP backend (both attached to the *host* project's shared subnets). Connections hung and then timed out. The team's first instinct was "the Shared VPC isn't wired up" and they nearly tore the whole topology down and rebuilt it. The actual problem was two layers down: (1) the subnet existed but the service project's principal had no `compute.networkUser` on it, and (2) the host VPC had **no explicit allow rule** for the internal traffic — and a VPC's *implied* rules are allow-egress / **deny-ingress**, so east-west traffic was silently dropped.

## Constraints context

- Segment: a platform team running the central **host project** for ~8 service projects; app teams owned their own service projects but not the network.
- The network was deliberately centralized (that's the point of Shared VPC) — app teams *couldn't* add their own firewall rules, which is correct but meant every connectivity request routed through the platform team and looked like "the network is broken" from the app side.
- They had been debugging at the wrong layer — checking the Serverless VPC connector and the Cloud SQL config repeatedly — because the failure (a timeout, not a `403`) gave no signal about *which* control was dropping the packets.

## Attempts

- Tried: re-create the Serverless VPC Access connector and re-check the Cloud SQL private-IP config. Outcome: no change — the connector was fine; the traffic was being dropped before it mattered.
- Tried: confirm the **subnet-level IAM**. The service project's serverless identity (and the connector's) needed `roles/compute.networkUser` on the *specific shared subnet* (granted at the subnet, not blanket at the host project). Outcome: fixed the "can't even attach to the subnet" half.
- Tried: read the host VPC firewall rules **as a default-deny model** rather than assuming "no rule = allowed." Outcome: found there was no ingress allow rule for the internal CIDR / source tag at all — the implied deny-ingress was doing exactly what it's designed to. Added a **scoped** allow-ingress rule (specific source range + target service-account, specific port), not a broad `0.0.0.0/0`.
- Tried (the durable move): re-expressed the firewall rules using **service-account-based** source/target instead of IP ranges where possible, so the rule says "this workload may reach that workload" rather than "this CIDR may reach that CIDR" — identities survive a re-IP, ranges don't.

## Resolution

The fix was two scoped grants at two layers, **not** a topology rebuild: (1) `roles/compute.networkUser` on the shared subnet for the service project's serverless/connector identity (the attach permission), and (2) a **least-scope allow-ingress firewall rule** on the host VPC for the specific source→target→port (the traffic permission), expressed with service accounts rather than broad CIDRs. The mental model that unlocked it: a Shared VPC connectivity failure is almost always *IAM-on-the-subnet* **or** *the implied deny-ingress*, not the topology — and a hung timeout (vs. a `403`) is the tell that you're looking at a **firewall** drop, not an API-permission denial.

**Action for the next engineer hitting this pattern:** when a service-project workload can't reach a host-project resource, check the two layers in order before touching topology — (a) does the calling identity have `compute.networkUser` on the *specific subnet*, and (b) is there an explicit **allow-ingress** rule for that source→target→port on the host VPC (remember the implied rule set is deny-ingress)? Prefer **service-account / tag-based** firewall rules over CIDRs so the rule expresses identity, and keep rules least-scope (named ports, named sources) rather than broad ranges. Network changes on a Shared VPC are the platform team's lane — route the rule + its blast-radius note there, and any cross-boundary security question to `security-engineering` / `ravenclaude-core/security-reviewer`.

Cross-reference: complements [`../knowledge/gcp-cloud-decision-trees.md`](../knowledge/gcp-cloud-decision-trees.md) `## Decision Tree: How to connect projects/networks?` and `## Decision Tree: GCP network isolation` (the firewall-rules leaf), and the best-practices [`shared-vpc-for-multi-project-networking`](../best-practices/shared-vpc-for-multi-project-networking.md), [`private-by-default-gcp`](../best-practices/private-by-default-gcp.md), and [`use-the-resource-hierarchy`](../best-practices/use-the-resource-hierarchy.md).
</content>
</invoke>
