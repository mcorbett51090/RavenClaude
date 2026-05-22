---
name: dlp-policy-design
description: Design tenant Data Loss Prevention policies for Power Platform — business / non-business / blocked classification, environment-scoped vs tenant-wide policies, exemption process, common-connector pitfalls (HTTP, SharePoint, Dataverse, custom connectors), and the "every flow gets re-evaluated on policy change" implication. Used by `power-platform-admin` (primary).
---

# DLP Policy Design Skill

**Purpose:** Equip `power-platform-admin` to design tenant Data Loss Prevention (DLP) policies that actually hold the line in a real organization without creating a flood of "my flow stopped working" tickets. This is one of the two or three governance decisions that meaningfully shapes how Power Platform feels in the tenant — get it right early.

## When to Use

- **Greenfield tenant DLP** — no policies in place, or the only policy is the default tenant one and you need a real framework.
- **Expanding the DLP framework to a new environment** — new Production env, new dev env, new BU env that needs different rules.
- **Remediating an active DLP incident** — a policy change broke flows in production, or a flow snuck through that should have been blocked.
- **Reviewing third-party connector additions** — a maker requests a custom connector or a premium connector that is not yet classified.

## Core Principles

1. **Default-deny philosophy.** Anything not explicitly classified Business is Non-Business or Blocked. Makers must justify Business classification; the burden is on the request, not on the policy.
2. **Three buckets only.** Business, Non-Business, Blocked. Resist the urge to invent more — connectors cannot live in two business buckets; data cannot cross between Business and Non-Business in the same app/flow.
3. **Env-scoped policies override tenant-wide.** A more specific policy beats the broader one. Use this for production lockdown without crippling shared developer envs.
4. **Custom connectors are first-class objects.** Each one is its own object in the policy. Classify deliberately. A custom connector is exactly as risky as the API it wraps — usually riskier, because makers built it.
5. **Policy changes re-evaluate every flow and app in scope.** A change can suspend flows that were previously running. Plan the comms before you flip the switch — silent breakage erodes trust in governance fast.
6. **Document the exemption process before the first exemption is requested.** Without a process, exemptions become "whoever asks loudest in Teams." With a process, the conversation is about evidence and approvers, not relationships.

## Playbook

### 1. The 3-bucket classification model

| Bucket | What lives here | Examples |
|---|---|---|
| **Business** | Connectors that touch corporate data the org has classified as official-record-of-truth | Dataverse, SharePoint (sanctioned tenants only), Outlook 365, Teams, M365 Groups, approved LOB custom connectors |
| **Non-Business** | Connectors useful for personal productivity but not for moving corporate data | Twitter, RSS, Bing Maps, Weather, Notifications, MSN Weather, personal OneDrive |
| **Blocked** | Connectors that must never appear in any app/flow in scope | High-risk: HTTP with Azure AD off-tenant, generic HTTP (depending on policy), SQL with arbitrary connection strings, anything wrapping unsanctioned external services |

**The rule that hurts**: a flow or app cannot use a Business connector and a Non-Business connector together. They are isolated. This is intentional — it stops data from leaking across the boundary — but it means the line you draw is the line your makers will run into every day. Draw it carefully.

### 2. HTTP, SharePoint, Dataverse, and Custom Connectors — the danger classes

- **HTTP / HTTP with Azure AD / HTTP Webhook** — generic HTTP is the highest-blast-radius connector in the platform. It can call anything reachable. Treat as Blocked at tenant scope; allow per-env only where there is a specific business case and active monitoring.
- **Send an HTTP request to Dataverse** vs **Dataverse** connectors — different objects in DLP. If you allow Dataverse for everyone but Blocked the HTTP-request-to-Dataverse, you've successfully shut down the most common Dataverse-bulk-ops pattern. Decide deliberately.
- **SharePoint** — usually Business, but understand that "SharePoint" in DLP is the connector, not a specific tenant or site. A flow with SharePoint as Business can read from *any* SharePoint tenant the maker can authenticate to — including personal accounts and external tenants. Pair with conditional-access policies in Entra to actually restrict the underlying API surface.
- **Custom connectors** — each is its own object in the DLP policy. By default, custom connectors are classified per the tenant default (usually Non-Business). Triaging custom connector requests is most of the ongoing DLP work in a mature tenant.

### 3. Policy evaluation order

Power Platform evaluates DLP policies in this order:
1. **Environment-scoped policy** matching the app/flow's home env, if one exists.
2. **Tenant-wide policy excluding specific envs**, if the env is in scope.
3. **Tenant-wide policy** as the catchall.

The most specific policy wins. Use this to your advantage:
- Tenant-wide policy = strict (Blocked for HTTP, custom connectors default Non-Business).
- Environment-scoped policies for sanctioned dev envs and specific BU prod envs override with looser rules where there's justification.
- Never the other way around — a loose tenant policy with strict per-env overrides is harder to reason about and easier to leave a hole in.

### 4. Exemption process

Document this before you publish the first policy:

1. **Maker submits a request** — form or ticket, must include: connector(s) needed, business case, data classification of what moves through, alternative approaches considered.
2. **Triage by CoE / Admin** — confirm the connector is what they actually need (often it's not — they want SharePoint when really they want Dataverse).
3. **Architecture review** — if the request is for a high-blast-radius connector (HTTP, custom connector to external service), a Solution Architect signs off.
4. **Decision** — approved (with env-scope, expiry date, monitoring requirement), denied with alternative, or escalated.
5. **Implementation** — the env-scoped policy is updated. Comms to the maker. Audit log entry.
6. **Quarterly review** — every exemption is reviewed quarterly; expired ones revert.

Without the expiry + review step, exemptions accumulate forever and the policy is fiction.

### 5. The comms plan for any policy change

Every policy change must come with:
- **Pre-change audit** — run a CoE-kit-flavored "DLP impact report" to enumerate every flow/app that will be affected by the change. (`Get-AdminPowerAppEnvironment`, `Get-AdminFlow`, then cross-reference against new policy.)
- **Notification** — owners of affected flows/apps are notified directly, ideally 7-14 days in advance, with the specific connector(s) that will become disallowed and a suggested alternative.
- **Grace period** — staggered rollout if the impact list is large. Pilot env first, then tenant.
- **Rollback plan** — exactly how to revert the policy if production starts smoking. Document the policy GUID, the previous classification of every changed connector, the time-to-revert estimate. Revert is fast (minutes); recovery of affected flows is slow (re-publish, often re-share).

### 6. CoE Kit dependency

The Center of Excellence Starter Kit's analytics surface DLP impact — which envs/flows/apps are touched by which policy. If the tenant doesn't have CoE Kit installed, the first answer to almost any DLP question is "install CoE Kit." Without it, DLP design becomes guesswork at scale, and exemptions are tracked in spreadsheets that go stale.

## Anti-Patterns to Flag

- A tenant policy that classifies everything as Business (defeats the point of DLP)
- HTTP allowed everywhere "just for now"
- Custom connectors auto-classified Business by tenant default
- Policy changes published without an impact audit
- Exemptions tracked in chat history with no expiry
- Per-env policies more permissive than the env-scoped tenant exclusion (creates confusion about which wins)
- Using DLP to enforce data residency or sensitivity classification — those need Purview/Information Protection labels, not DLP
- Blocking SharePoint at tenant level "to be safe" — broke every legitimate flow in the org

## Escalation

- **DLP change broke production flows mid-day** → revert immediately, then root-cause. Do not "wait and see" — every minute is more ticket volume.
- **Custom connector classification disagreement with a BU** → architecture review via Team Lead, not a hallway conversation.
- **Sensitivity labels / Purview / data residency requirements** → these are not DLP problems. Escalate to `ravenclaude-core` `security-reviewer` and `architect` — DLP is one layer; you also need labels, conditional access, and possibly geo-region policies.
- **CoE Kit not installed in the tenant** → escalate to Team Lead for project work, not for ad-hoc remediation. DLP design without CoE Kit visibility is operating blind.

When in doubt, lock it down and exempt rather than open it up and chase leaks. Reverting an over-strict DLP policy is fast. Recovering from data exfiltration is not.
