---
name: aws-account-strategy
description: "Design a multi-account AWS landing zone: separate accounts by blast radius (prod/non-prod/security/shared-services) under Organizations, SCP guardrails as ceilings, region/AZ resilience, and the Control-Tower-or-not decision."
---

# AWS Account Strategy

## Multi-account by blast radius
Separate **prod / non-prod / security / shared-services** accounts under **Organizations**. One account = one blast radius + an unattributable bill.

## Guardrails
**SCPs** set the org-wide ceiling (even an admin can't exceed them). **Control Tower** if you want the landing zone + guardrails managed.

## Resilience
Multi-**AZ** by default (cheap HA); multi-**region** only when RTO/RPO/latency justifies it. State the RTO/RPO.

## Build
The topology is the design; `terraform-iac` builds it.
