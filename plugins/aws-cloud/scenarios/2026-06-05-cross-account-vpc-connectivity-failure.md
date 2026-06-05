---
scenario_id: 2026-06-05-cross-account-vpc-connectivity-failure
contributed_at: 2026-06-05
plugin: aws-cloud
product: vpc
product_version: "n/a"
scope: likely-general
tags: [vpc, transit-gateway, routing, security-group, connectivity]
confidence: medium
reviewed: false
---

## Problem

After attaching two VPCs in different accounts to a Transit Gateway, a service in VPC-A still could not reach a service in VPC-B — connections hung and timed out rather than being refused. The team's first instinct was "the Transit Gateway attachment is broken" and they were about to tear it down and rebuild it. The attachment was fine; the failure was the layered routing-and-filtering chain that has to *all* be correct end-to-end for cross-VPC traffic to flow.

## Context

- Estate: a hub-and-spoke topology — one Transit Gateway in a shared-services account, spoke VPCs in separate workload accounts (the multi-account-by-blast-radius posture, CLAUDE.md §2).
- Constraint: a hang/timeout (not a "connection refused") almost always means traffic left but nothing came back — a routing or stateful-filter asymmetry — versus a refused connection, which means traffic arrived and was rejected at the host. Reading that signal narrows the search before touching anything.
- Multiple independent layers each have to allow the path: the TGW route table, *both* VPCs' subnet route tables, the security groups on both ends, and the NACLs. Any one missing entry produces the same symptom.

## Attempts

- Tried: rebuilding the Transit Gateway attachment. Outcome: no change — the attachment was never the problem. Tearing down working infrastructure on a hunch.
- Tried (the systematic walk that worked): traced the path layer by layer in the order packets traverse it, instead of guessing. (1) **TGW route table** — confirmed routes for both VPC CIDRs and that both attachments were associated/propagated. (2) **Subnet route tables** — VPC-A's route table had a route to VPC-B's CIDR via the TGW, but VPC-B's route table was **missing the return route** to VPC-A — so the SYN arrived and the reply had nowhere to go (the hang). (3) **Security groups** — VPC-B's SG allowed the app port only from VPC-B's own CIDR, not from VPC-A's. (4) **NACLs** — confirmed the ephemeral-port return range was allowed (NACLs are stateless, unlike SGs). Outcome: the missing return route + the SG source CIDR were the two faults.
- Tried (the confirmation): used **VPC Reachability Analyzer** to validate the path source-to-destination after each fix, so "it should work now" became "the analyzer confirms the path is open." Outcome: a verifiable green path instead of a retry-and-hope.

## Resolution

The failure was a **routing-and-filtering asymmetry**, not a broken TGW: VPC-B lacked a return route to VPC-A, and VPC-B's security group didn't allow VPC-A's CIDR on the app port. The fix was the missing return route + the SG source rule, confirmed with Reachability Analyzer. Cross-account/cross-VPC reachability requires *every* layer — TGW route table, both subnet route tables, both security groups, and the NACLs — to agree; one missing entry yields a silent hang.

**Action for the next engineer hitting this pattern:** **read the symptom first** — hang/timeout points at routing or a stateful-filter asymmetry (traffic left, nothing returned); "connection refused" points at the host/SG. Then walk the layers in packet order: TGW route table → both subnet route tables (check the **return** route, the most common miss) → both security groups (the destination SG must allow the *source* CIDR) → NACLs (stateless — allow the ephemeral return range). Confirm with **VPC Reachability Analyzer** rather than retrying the connection. Don't rebuild the attachment until the layered walk has ruled it out. `[verify-at-use]` Reachability Analyzer's current cross-account support against AWS docs.

**Sources (retrieved 2026-06-05):**
- AWS — Transit Gateway routing and attachments: https://docs.aws.amazon.com/vpc/latest/tgw/how-transit-gateways-work.html
- AWS — VPC Reachability Analyzer: https://docs.aws.amazon.com/vpc/latest/reachability/what-is-reachability-analyzer.html
- AWS — security groups vs network ACLs (stateful vs stateless): https://docs.aws.amazon.com/vpc/latest/userguide/infrastructure-security.html

AWS networking feature support evolves — `[verify-at-use]` cross-account Reachability Analyzer support and any TGW routing limits before relying on them.
