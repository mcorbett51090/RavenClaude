---
name: gcp-private-networking
description: "Design private-by-default GCP networking: Shared VPC for multi-project, default-deny firewall targeted by tag/service-account, Private Google Access + Private Service Connect, and Cloud NAT for controlled egress."
---

# GCP Private Networking

## Shared VPC
Centralize the network in a **host project**; service projects attach. Cleaner than per-project VPC + peering.

## Firewall
**Default-deny**, then allow by **network tag / service account** (not broad CIDRs). Never open admin ports to the internet.

## Private
**Private Google Access** (no external IP), **Private Service Connect** (private service access), **Cloud NAT** (controlled egress).

Plan CIDRs to avoid overlap. Route exposure verdicts to `security-engineering`.
