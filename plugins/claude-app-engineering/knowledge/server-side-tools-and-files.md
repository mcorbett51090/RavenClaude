# Anthropic-hosted server tools & the Files API

**Last reviewed:** 2026-05-28 · **Confidence:** medium-high — several of these are beta/recent; dated, verify before quoting. ([API overview](https://platform.claude.com/docs/en/api/overview), retrieved 2026-05-28.)
**Owner:** `mcp-and-server-tools-engineer`.

These are tools and APIs Anthropic runs (distinct from MCP servers you author and from the Agent SDK's local built-in tools). They're requested via the Messages API and often gated by a beta header.

## Computer use
Claude controls a computer via screenshots + mouse/keyboard tool calls. **GA on claude.ai (March 2026)**; via the API, **you still run the actions in a sandboxed VM** (X11/Xvfb display, lightweight desktop, pre-installed apps). High blast radius — sandbox hard, never point it at a machine with credentials/state, and route the sandboxing design to `ravenclaude-core/security-reviewer`. Use only when DOM/API automation can't do the job.

## Code execution tool
Claude runs code in an Anthropic-hosted sandbox and uses the result. Good for data analysis, math, and verifying generated code. Verify GA/beta + the sandbox's network/package posture before relying on it for sensitive data.

## Web search / web fetch (server tools)
Anthropic-hosted retrieval Claude can call directly (distinct from the Agent SDK's local `WebSearch`/`WebFetch` built-ins). Treat fetched content as **untrusted** (injection) — see [`tool-use-and-structured-output.md`](tool-use-and-structured-output.md).

## Files API
Upload files once and reference them by ID across requests (and from the code execution tool), instead of re-sending bytes every call. Cuts token cost + latency for repeated large documents. Verify retention, size limits, and per-workspace scope before designing around it.

## Memory tool
A tool that lets Claude persist and recall information across turns/sessions via a storage backend you (or Managed Agents) provide. **Public beta**; on Managed Agents it's gated by the `managed-agents-2026-04-01` header. Pair it with a redaction pass (don't persist secrets/PII) and an eviction policy. Distinct from prompt caching (which reuses a prefix, not stored memories) and from the Agent SDK's `CLAUDE.md`/session memory.

## Caching server-tool calls
Server-tool `tool_use`/`tool_result` blocks are cacheable content, but toggling a server tool (e.g., web search on/off) invalidates system + messages caches — keep the tool set stable across cached turns ([`prompt-caching-playbook.md`](prompt-caching-playbook.md)).

> **All of these carry dated GA/beta status — confirm against [`model-selection-and-2026-capability-map.md`](model-selection-and-2026-capability-map.md) (and re-verify on the Researcher sweep) before promising one to a client.**
