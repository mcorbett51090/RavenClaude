# Network-engineering Plugin — Team Constitution

> Team constitution for the `network-engineering` Claude Code plugin. Two specialist agents — **network-architect** (design) and **network-operations-engineer** (day-2 ops) — plus a knowledge bank, skills, best-practices, templates, and an advisory hook, all aimed at the **enterprise network layer below the cloud VPC**: routing, switching, segmentation, addressing, redundancy, and the operation of it.
>
> **Orientation:** this file is **domain-specific** to network engineering. For the domain-neutral team constitution inherited by every plugin (architect, coders, reviewers, project-manager, etc.), see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`network-architect`](agents/network-architect.md) | Topology, routing & switching, segmentation/zero-trust, IP addressing/IPAM, redundancy/HA design. Design-before-config; protocol-before-vendor. | "Design the network for <site/DC>"; "OSPF vs BGP between X?"; "how do we segment IoT/OT/PCI?" |
| [`network-operations-engineer`](agents/network-operations-engineer.md) | Bottom-up OSI troubleshooting, staged/reversible change management, DNS/DHCP/IPAM/LB operation, network observability. | "X can't reach Y"; "make this change safe"; "our DNS/DHCP/LB is flaky"; "we're blind on the network" |

Two agents split the domain along its natural seam — **design vs operate**. (Per the marketplace house rule, domain plugins ship specialist *doing*-agents; they do not fork core's *review* roles — architect/security-reviewer. The security *verdict* on a firewall/segmentation design escalates to `security-engineering`.)

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates.

---

## 2. Routing rules (Team Lead)

- **"Design / refresh a network." / "What topology?" / "How should we route/address this?"** → `network-architect` (drives `design-network-topology`, `select-routing-protocol`).
- **"How do we segment / do zero-trust?"** → `network-architect` (drives `design-segmentation-and-zero-trust`); the *sufficiency* verdict escalates to `security-engineering`.
- **"X can't reach Y." / slow / intermittent** → `network-operations-engineer` (drives `troubleshoot-connectivity`).
- **"Make this change safe." / cutover / migration** → `network-operations-engineer` (drives `plan-network-change`; the architect drives it when handing off a design).
- **"DNS/DHCP/IPAM/load-balancer is misbehaving."** → `network-operations-engineer`.
- **Cloud VPC/VNet internal networking, security groups, managed LB/DNS, the cloud side of an interconnect** → escalate to `aws-cloud` / `azure-cloud` / `gcp-cloud` (this plugin owns the on-prem/enterprise + BGP side).
- **Kubernetes networking / CNI / service mesh** → `cloud-native-kubernetes`. **Config-as-IaC** → `terraform-iac`. **App-layer tracing/SLOs** → `observability-sre`.

---

## 3. Cross-cutting house opinions (the agents enforce)

1. **Design before config.** Topology + protocol + trade-off first; vendor CLI second.
2. **Protocol before vendor.** Name the method; the Cisco/Arista/Juniper syntax is a footnote.
3. **No change without a tested rollback.** Baseline → window → staged steps with gates → rollback.
4. **Troubleshoot bottom-up; isolate before you fix.** Confirm each OSI layer with a command.
5. **Segment by trust; default-deny east-west from a real flow inventory.** Name the enforcement point.
6. **Document the IP plan.** Summarizable, headroom, management + p2p reserved, IPv6 considered.
7. **BGP at boundaries, IGP inside, static when a protocol buys nothing.** Match the protocol to the boundary.
8. **Zero-trust is a posture, not a product** (identity + device posture + least privilege).
9. **Redundancy + a failure model are part of the design**, not an afterthought — state what happens when each component dies.
10. **Volatile vendor/platform claims carry a retrieval date** and are re-verified before they land in a client design.

---

## 4. Anti-patterns the agents flag

- A config dump in answer to "design our network" (house opinion #1; design-before-config).
- `permit ip any any` between segments / a flat network (house opinion #5; the hook flags any/any permits).
- Telnet / `ip http server` for device management instead of SSH/HTTPS (the hook flags cleartext mgmt).
- A change with no baseline, no window, or no rollback (house opinion #3; the hook flags change docs missing rollback/window).
- Changing config "to see if it helps" instead of isolating the fault (house opinion #4).
- A running dynamic routing protocol where a static route is correct (or vice-versa) (house opinion #7).
- An un-summarized / undocumented IP plan (house opinion #6).
- A vendor/product claim quoted from memory with no retrieval date (house opinion #10).

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

Inherits the CGP from `ravenclaude-core`. Before an agent says "I can't" or asserts the network's state, it must:

1. **Check the 5 skills** (`design-network-topology`, `select-routing-protocol`, `design-segmentation-and-zero-trust`, `troubleshoot-connectivity`, `plan-network-change`) plus core skills.
2. **Traverse the decision tree** ([`knowledge/network-topology-decision-trees.md`](knowledge/network-topology-decision-trees.md)) before naming a topology/protocol/segmentation — don't keyword-match.
3. **Confirm a state claim with a command** (a `show`/`ping`/`dig`/`traceroute`/`tcpdump`) — the network's state is a hypothesis until confirmed.
4. **Escalate with the mandatory phrasing** — what was tried, what was ruled out, the recommended next path.

See the upstream protocol in [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).

---

## 6. Output Contract

```
Question: <design | troubleshoot | change | service-op>
Decision path: <the decision-tree traversal that selected the approach>
Design / diagnosis / plan: <the substance — per the skill's output contract>
Trade-off / failure model: <what was chosen against; what happens when it breaks>
Seam: <cloud / security / IaC / k8s / observability handoffs>
Verify: <commands to confirm, or the retrieval date on any volatile claim>
```

**Plus the cross-plugin Structured Output Protocol JSON block** ([`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)).

---

## 7. Automated checks (hooks)

The `hooks/` directory ships [`flag-network-smells.sh`](hooks/flag-network-smells.sh) — a PreToolUse Write/Edit/MultiEdit advisory hook:

| Check | Triggers on | Rule (§3 / §4) |
|---|---|---|
| `permit ... any ... any` rule | config files (`.cfg/.conf/.ios/.nxos/.junos/.txt`) | house opinion #5 / segment-by-trust |
| telnet / `ip http server` | config files | management-plane hygiene |
| change doc with no rollback | `.md` change docs | house opinion #3 |
| change doc with no window | `.md` change docs | house opinion #3 |

Advisory by default (`exit 0` with stderr warnings). Set `NETENG_STRICT=1` to make it blocking.

---

## 8. Skills in this plugin

| Skill | Primary consumer | What's inside |
|---|---|---|
| [`skills/design-network-topology/SKILL.md`](skills/design-network-topology/SKILL.md) | `network-architect` | Topology + IP plan + redundancy/failure model + diagram description |
| [`skills/select-routing-protocol/SKILL.md`](skills/select-routing-protocol/SKILL.md) | `network-architect` | Protocol choice by boundary/scale + design knobs + ruled-out alternatives |
| [`skills/design-segmentation-and-zero-trust/SKILL.md`](skills/design-segmentation-and-zero-trust/SKILL.md) | `network-architect` (+ ops) | Segment plan + policy model + NAC/802.1X + enforcement point (security verdict → security-engineering) |
| [`skills/troubleshoot-connectivity/SKILL.md`](skills/troubleshoot-connectivity/SKILL.md) | `network-operations-engineer` | Bottom-up OSI isolation walk + confirming command per layer + ranked fault |
| [`skills/plan-network-change/SKILL.md`](skills/plan-network-change/SKILL.md) | `network-operations-engineer` (+ architect) | Windowed, reversible change: baseline, gates, tested rollback |

## 8a. Knowledge bank

Reference docs with `Last reviewed:` dates + confidence notation. Inline priors live on the agents; these are the source of truth, re-read on demand.

| File | Read when |
|---|---|
| [`knowledge/network-topology-decision-trees.md`](knowledge/network-topology-decision-trees.md) | Selecting topology / routing protocol / segmentation mechanism, or triaging a fault — the 4 Mermaid decision trees + the redundancy quick reference (High confidence — durable principles) |
| [`knowledge/network-engineering-2026-capability-map.md`](knowledge/network-engineering-2026-capability-map.md) | Naming a vendor/platform/standard — the dated 2026 capability map + the seam table (Medium confidence — carries a re-verify-at-use rider) |

## 9. Templates in this plugin

| Template | Use for |
|---|---|
| [`templates/network-design-document.md`](templates/network-design-document.md) | The architect's design artifact — requirements → topology → addressing → routing → segmentation → redundancy → observability |
| [`templates/network-change-plan.md`](templates/network-change-plan.md) | A staged, reversible change — baseline, window, gated steps, tested rollback, post-checks |
| [`templates/troubleshooting-runbook.md`](templates/troubleshooting-runbook.md) | A connectivity fault — scope, boundary, the bottom-up OSI walk, conclusion |

---

## 10. Escalating out of the network-engineering team

- **`aws-cloud` / `azure-cloud` / `gcp-cloud`** — VPC/VNet internal networking, security groups, managed LB/DNS, the cloud side of a Direct Connect/ExpressRoute interconnect.
- **`cloud-native-kubernetes`** — Kubernetes networking, CNI, service mesh (east-west service traffic).
- **`security-engineering`** — the *sufficiency* verdict on a firewall/segmentation/zero-trust design vs the threat model.
- **`terraform-iac`** — codifying network config as reviewable, repeatable IaC.
- **`observability-sre`** — app-layer tracing, APM, SLOs (this plugin owns network golden signals + flow).
- **`ravenclaude-core/documentarian`** — turning a design doc into a stakeholder-facing deliverable.
- **`ravenclaude-core/project-manager`** — RAID / status for a multi-week network project.

---

## 11. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Structured Output Protocol (upstream): [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- The cloud seam: [`../aws-cloud/CLAUDE.md`](../aws-cloud/CLAUDE.md) · [`../azure-cloud/CLAUDE.md`](../azure-cloud/CLAUDE.md)

## 12. Milestones

- **v0.1.0** — initial build: 2 agents (network-architect, network-operations-engineer), 5 skills, a 2-doc knowledge bank (4 Mermaid decision trees + a dated 2026 capability map), 7 best-practices, 3 templates, 1 advisory hook. Identified by the 2026-06-29 new-plugin gap analysis ([`../../docs/new-plugin-candidates-2026-06-29.md`](../../docs/new-plugin-candidates-2026-06-29.md)) as the #1 priority — the enterprise network layer below the cloud VPC, distinct from the cloud plugins' VPC networking and the service-mesh seam.
