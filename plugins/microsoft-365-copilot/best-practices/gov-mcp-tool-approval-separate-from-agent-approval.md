# Approve MCP tools independently of the agent — they are governed separately in the Agent Registry

**Status:** Absolute rule
**Domain:** Copilot governance / Agent Registry
**Applies to:** `microsoft-365-copilot`

---

## Why this exists

When an agent exposes MCP (Model Context Protocol) tools, the tenant admin must approve two independent things: the **agent** itself (via the M365 admin center Agent Registry → Agents tab) and each **MCP tool** the agent uses (Agent Registry → Tools tab). An admin who approves the agent assumes the MCP tools are implicitly approved — they are not. An agent with an approved app package but unapproved MCP tools will silently fail to invoke those tools at runtime, producing unhelpful responses that look like model failures. The tools approval step is a separate admin-center action that is easy to miss in the go-live checklist.

## How to apply

Go-live checklist for any agent that uses MCP tools:

- [ ] **Agent approved**: M365 admin center → Copilot → Agent Registry → Agents tab → agent shows "Active".
- [ ] **Each MCP tool approved**: M365 admin center → Copilot → Agent Registry → Tools tab → all tools used by this agent show "Active".
- [ ] **Tenant MCP consent**: if the MCP server is external, confirm the tenant-level MCP consent was granted via the separate consent flow (not just the app package consent).
- [ ] **Test tool invocation**: in the Agents Toolkit Playground, verify each tool is invocable and returns the expected response.

Diagnosis when tools fail silently:
```
1. Open M365 admin center → Agent Registry → Tools.
2. Check status of each tool the agent uses.
3. If status is "Pending" or "Not approved" → approve it.
4. If status is "Active" → check the MCP server's network connectivity and the tenant MCP consent grant.
```

**Do:**
- Include both agent approval and tool approval steps in every deployment runbook.
- Test tool invocability from the agent immediately after tool approval — the approval propagation can take minutes `[verify-at-build]`.
- When an MCP tool is updated (new version, new endpoints), verify whether re-approval is required — tool updates may reset the approval status.

**Don't:**
- Assume agent approval implies tool approval — they are independent registry entries.
- List only the agent package in the change-management record; list all MCP tools separately with their approval status.
- Use the agent in production before confirming every tool it calls has been individually approved.

## Edge cases / when the rule does NOT apply

Agents that use no MCP tools (pure declarative agents with only SharePoint knowledge or synced connectors) do not have a tools-approval step. This rule applies only to agents that declare MCP tool use in the manifest.

## See also

- [`../agents/copilot-admin-governance.md`](../agents/copilot-admin-governance.md) — owns Agent Registry lifecycle and the approval workflow
- [`./gov-route-agents-and-mcp-tools-through-the-agent-registry.md`](./gov-route-agents-and-mcp-tools-through-the-agent-registry.md) — the broader Agent Registry lifecycle rule this extends

## Provenance

Codifies CLAUDE.md house opinion #13 ("org-catalog publish is admin-gated; MCP tools need separate tenant consent") from `copilot-admin-governance-2026.md`; Microsoft Learn Agent Registry documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
