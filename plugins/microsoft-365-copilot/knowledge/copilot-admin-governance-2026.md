# Copilot admin & governance — Agent Registry, approval, publish, licensing (2026)

**Last reviewed:** 2026-05-30
**Confidence:** High on the Agent Registry + approval-role model (first-party). `[verify-at-build]` on Agent 365 + PAYG metering specifics.
**Read when:** governing the agent lifecycle, planning publish, or sizing licensing/PAYG.

---

## Agents are apps

An agent (declarative or custom-engine) ships as an **M365 app package** — manifest + icons + (optional) plugin/connector files. RAI validation runs on sideload/publish. Grounding: [agents are apps](https://learn.microsoft.com/microsoft-365/copilot/extensibility/agents-are-apps), [publish](https://learn.microsoft.com/microsoft-365/copilot/extensibility/publish).

## The publish path (admin-gated)

```
sideload (dev)  →  org catalog (AI-Admin / Global-Admin approves)  →  AppSource (optional)
```

House opinion #13: **org-catalog publish is admin-gated.** You don't ship to users without the gate.

## The Agent Registry + approval roles

The **M365 admin center Agent Registry** is the governance surface — agents are reviewed and approved by the **AI Administrator / Global Administrator**. **MCP tools need separate tenant consent** (an agent's MCP grounding is governed independently of the agent). Grounding: [M365 agents admin guide](https://learn.microsoft.com/microsoft-365/copilot/agent-essentials/m365-agents-admin-guide).

## Licensing + PAYG

- **Copilot seats** for users.
- **Connector item quotas** per tenant (a large source can exhaust them).
- **Pay-as-you-go (PAYG)** metering for some agent consumption — now GA in a concrete form: **Copilot Cowork went GA 2026-06-16 with usage-based "Copilot Credits" billing** (also covers the Work IQ API) — [Cowork what's-new](https://learn.microsoft.com/microsoft-365/copilot/cowork/whats-new) + [Partner Center June 2026](https://learn.microsoft.com/partner-center/announcements/2026-june), verified 2026-07-01. So PAYG metering is a live billing surface, not hypothetical; which agents/actions meter which credits is still expanding `[verify-at-build]`. (Credits pack sizing — e.g. 25,000/pack — see `best-practices/gov-attach-a-payg-billing-policy-with-a-budget-cap.md`.)

House opinion #8: **no org-data grounding without a license story** — every recommendation carries the **`Licensing impact:`** line.

## The data layer routes to security/Purview

This doc covers *lifecycle + licensing*. The **data-protection** layer — Purview DLP-for-Copilot, sensitivity labels, oversharing remediation, RSS/RCD — lives in [`copilot-security-purview-2026.md`](copilot-security-purview-2026.md), and **residency** in [`data-residency-and-compliance-2026.md`](data-residency-and-compliance-2026.md). The security *verdict* is `ravenclaude-core/security-reviewer`'s.

## Agent 365 (track, don't over-invest)

**Agent 365 / Agent 365 SDK** — Entra agent identity + governed MCP — is emerging `[verify-at-build]`. Track it; a v0.2.0 `agent-365-engineer` is deferred until GA.

## Refresh triggers
- Approval-role names or Agent Registry surface change.
- PAYG metering reached GA (Copilot Cowork + Copilot Credits, 2026-06-16 — recorded above); re-check which agents/actions meter credits as coverage expands.
- Agent 365 reaches GA.
