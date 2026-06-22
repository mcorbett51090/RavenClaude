# Weekly Tier-A news sweep — Microsoft stack (2026-06-19)

A weekly news-cadence sweep ([`docs/research-routine-two-cadence.md`](../research-routine-two-cadence.md)) scoped to the Microsoft-stack Tier-A cluster, run one week after the 2026-06-11 broad sweep (whose three clearest open corrections + advisor tool have since shipped via #413 / #420). All facts re-verified **this session against the primary source — Microsoft Learn's official "What's new" pages — via the Microsoft-Learn MCP** (a first-party route; preferred over the 403-prone direct fetch).

**Triage key:** **C** = corrects/fills a now-stale gap · **A** = net-new capability the bank lacks. Each finding carries its primary citation + an ISO retrieval date; volatile preview→GA items carry `[verify-at-use]`.

## Process (per the task's panel protocol)

1. **Panel 1 (usefulness)** — independent 3-seat panel: all six findings **USEFUL**; F5 ranked P0 (action-forcing), F1–F4/F6 P1 additions; scoping notes on F4 (headline `agentUser`) and F6 (scope to m365-copilot + cross-ref, don't duplicate into Fabric).
2. **Panel 2 (detailed build-plan review)** — a *different* 3-seat panel did its own research and **disagreed** on F1/F2/F6, flagging them as preview, not GA.
3. **Tiebreak (Panel 3)** — the disagreement was resolved by fetching the **live primary pages** and ruling on the verbatim evidence:
   - **F1 Fabric Graph → GA.** The live `/fabric/graph/overview` page carries **no preview banner** (GA pricing, GA region list, ISO/IEC 39075 GQL) and the what's-new "Generally available features" table lists "Fabric Graph (Generally Available)" June 2026. Only the *graph-as-AI-data-source* sub-feature is preview. Panel 2's "preview" rested on the stale Oct-2025 archive entry.
   - **F2 Eventstream Kafka/Service Bus → GA-announced, page-still-preview.** The what's-new RTI table says "Generally Available," but the source page title is still "Add Apache Kafka source … **(preview)**." Primaries conflict → write the conservative caveated form + `[verify-at-use]`.
   - **F6 Fabric Data Agents in M365 Copilot → GA-announced, page-still-preview.** The what's-new GA table says GA, but the dedicated consume page carries "**Important: This feature is in preview**." Primaries conflict → caveated + `[verify-at-use]`.

## Findings (all built in this PR)

### microsoft-fabric — `knowledge/fabric-2026-capability-map.md`
- **A — Fabric Graph GA (June 2026).** Graph workload (model/visualize/analyze relationships over OneLake, GQL/NL2GQL, CU-billed, no separate SKU; min 100 GB storage). Was preview since Oct 2025. Graph-as-AI-data-source in Fabric Data Agent remains preview. Source: [Graph overview](https://learn.microsoft.com/fabric/graph/overview) + [Fabric what's-new](https://learn.microsoft.com/fabric/fundamentals/whats-new).
- **A — Eventstream Apache Kafka + Azure Service Bus connectors (GA-announced, page-still-preview).** What's-new RTI table = GA June 2026 (hardened reliability, SASL_SSL/SASL_PLAINTEXT/Entra, production throughput); source page title still "(preview)". `[verify-at-use]`. Source: [Add Apache Kafka source](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-source-apache-kafka).

### microsoft-graph — `knowledge/identity-auth-decision-trees.md` + `knowledge/workloads-notifications-decision-trees.md`
- **A — Programmatic FIDO2 passkey registration GA (June 2026).** `fido2AuthenticationMethod: creationOptions` → POST `publicKeyCredential`; lets an app register passkeys on a user's behalf. Source: [Graph what's-new](https://learn.microsoft.com/graph/whats-new-overview).
- **A — `agentUser` + `verifiedIdProfile` GA in v1.0 (May 2026).** `agentUser` = an Entra user subtype for AI agents as digital workers (`idtyp=user` tokens, 1:1 to a parent agent identity, **no password auth, no privileged admin roles, guest-like permissions**). `[verify-at-use]` — brand-new, surface still moving. Source: [Graph what's-new](https://learn.microsoft.com/graph/whats-new-overview) + [agentUser resource](https://learn.microsoft.com/graph/api/resources/agentuser).
- **A — `ownerlessGroupPolicy` GA in v1.0 (May 2026).** Actionable-email policy prompting active members of an ownerless M365 group to accept ownership. Source: [Graph what's-new](https://learn.microsoft.com/graph/whats-new-overview).

### azure-cloud — `knowledge/azure-2026-capability-map.md`
- **C (P0, action-forcing) — AKS Azure Linux 2.0 retirement.** AKS support/security updates ended **2025-11-30**; node images **removed 2026-03-31** (after which affected node pools can't scale). Migrate to osSku **AzureLinux3** (default for `--os-sku AzureLinux` on K8s **1.32–1.36**; also selectable on 1.28+). Source: [AKS Azure Linux support cycle](https://learn.microsoft.com/azure/azure-linux/aks-support-cycle) + [Upgrade OS version in AKS](https://learn.microsoft.com/azure/aks/upgrade-os-version).

### microsoft-365-copilot — `knowledge/grounding-source-decision-2026.md`
- **A — Fabric Data Agents in M365 Copilot (GA-announced, page-still-preview).** Business users discover/chat governed Fabric data sources inside M365 Copilot (publish to Agent Store; Entra-enforced RLS/CLS respected). What's-new GA table vs. a "This feature is in preview" page banner → caveated + `[verify-at-use]`. Cross-references microsoft-fabric (not duplicated). Source: [Consume Fabric data agent in M365 Copilot](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-365-copilot).

## Honest nulls / not chased this sweep
- The remaining 06-11 queue items (tableau 2026.2, Snowflake Iceberg v3, analytics-engineering re-checks) are non-Microsoft and were 403-prone to direct fetch; deferred to a sweep with a verifiable primary route rather than written on search snippets.
- Other June-2026 Fabric GA rows (Migration Assistant direct connection, AI Functions gpt-5-mini default, Real-Time Dashboards Live Refresh) are real but did not change a *documented* decision in the bank this week — logged, not padded into edits.
