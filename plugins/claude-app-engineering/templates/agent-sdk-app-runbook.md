# Agent SDK app runbook — <AGENT>

> Owned by `agent-sdk-engineer`. See `knowledge/agent-sdk-and-managed-agents.md`. RavenClaude's own `plugins/*/` is the worked example.

## Loop warranted?
- <yes — multi-step, tool-using; no — single call → Messages API (prompt-and-context-engineer)>

## Build (Agent SDK)
- **Language:** <Python | TypeScript>
- **allowed_tools:** <least-privilege set>
- **permission_mode:** <default | acceptEdits | …>; deny destructive by default
- **Subagents:** <AgentDefinition(s), add `Agent` to allowed_tools>
- **Hooks:** <PreToolUse/PostToolUse/Stop/… + what they enforce>
- **Skills / commands:** <.claude/skills/*/SKILL.md>
- **MCP servers:** <mcp_servers entries → mcp-and-server-tools-engineer>
- **Sessions:** <capture id; resume; fork strategy>

## Permissions & sandbox (→ core/security-reviewer)
- [ ] Least privilege; destructive denied; hooks enforce
- [ ] Secrets via env/secret-manager; not in source/logs
- [ ] Tool/computer-use sandboxing reviewed

## Production
- **Stay SDK or move to Managed Agents?** <why>
- **If Managed Agents:** sandbox/session-log implications; memory beta header (dated); custom-tool return pattern
- **Billing note (dated):** Agent SDK credit change 2026-06-15 — verify cost scope

## Quality
- **Evals:** → `eval-engineer` (golden set + CI gate)
