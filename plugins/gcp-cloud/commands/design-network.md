---
description: "Design private-by-default GCP networking: Shared VPC, default-deny firewall by tag/SA, private service access, Cloud NAT."
argument-hint: "[connectivity + what must stay private]"
---

You are running `/gcp-cloud:design-network`. Use `gcp-network-engineer` + the `gcp-private-networking` skill.

## Steps
1. Lay out Shared VPC (host + service projects).
2. Default-deny firewall + tag/SA-targeted allows.
3. Private Google Access + Private Service Connect + Cloud NAT.
4. Route exposure verdicts to security-engineering.
5. Emit (from `templates/shared-vpc-design.md`) + Structured Output block.
