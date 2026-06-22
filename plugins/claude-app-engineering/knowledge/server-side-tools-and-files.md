# Anthropic-hosted server tools & the Files API

**Last reviewed:** 2026-06-12 (advisor tool added — verified against the [advisor-tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool); rest of bank 2026-05-28) · **Confidence:** medium-high — several of these are beta/recent; dated, verify before quoting. ([API overview](https://platform.claude.com/docs/en/api/overview), retrieved 2026-05-28.)
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

## Advisor tool
Pairs a **faster, cheaper executor model** (the top-level `model`) with a **higher-intelligence advisor model** (the `model` inside the tool def) that the executor consults *mid-generation* for a plan/course-correction — all inside a single `/v1/messages` request, no client round-trips. **Beta** — header `advisor-tool-2026-03-01`; tool `type: "advisor_20260301"`, `name: "advisor"`. The executor decides *when* to call; the server forwards the **full transcript** to the advisor automatically (`server_tool_use.input` is always empty), runs a separate server-side inference, returns an `advisor_tool_result`, and the executor continues, informed.

**This is a routing-ladder play (§3 #3), not just a tool** — long-horizon agentic work (coding, computer use, multi-step research) where most turns are mechanical but the *plan* is decisive, so you get near advisor-solo quality while the bulk of tokens generate at executor rates. Per the [advisor-tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool): Sonnet-executor + Opus-advisor for a quality lift at similar/lower total cost vs Opus-solo; Haiku-executor + Opus-advisor for a step up over Haiku alone. Weak fit for single-turn Q&A (nothing to plan). **The advisor must be ≥ as capable as the executor** — an invalid pair returns `400 invalid_request_error`; the dated valid executor→advisor matrix lives in [`model-selection-and-2026-capability-map.md`](model-selection-and-2026-capability-map.md), not here (one file refreshes — §3 #14).

**Cost + control levers (FinOps — shared with `claude-app-ops-engineer`):**
- Advisor tokens bill **separately at the advisor's rate**, reported in `usage.iterations[]` (`type: "advisor_message"`), **not** rolled into top-level `usage`; top-level `max_tokens` bounds the **executor only**.
- `max_tokens` **on the tool def** (min 1024) caps advisor output per call — Anthropic's recommended start is **2048** (~7× shorter advisor output, ~0% truncation in their test; 1024 truncates ~10%).
- `max_uses` caps advisor calls **per request** (over-cap → an `advisor_tool_result_error` with `error_code: "max_uses_exceeded"`, executor continues). **No built-in conversation-level cap — count client-side**; to stop, remove the tool **and** strip every `advisor_tool_result` block from history, else `400`.
- `caching: {"type":"ephemeral","ttl":"5m"|"1h"}` on the tool def caches the advisor's own transcript — Anthropic says it breaks even at **~3 advisor calls**; keep it off for short tasks.

**Reliability:** every advisor failure — `max_uses_exceeded`, `too_many_requests`, `overloaded`, `prompt_too_long`, `execution_time_exceeded`, `unavailable` — returns **inside** the result block, so the request does **not** fail; the executor proceeds without that advice. The advisor sub-inference **does not stream** (the executor stream pauses); a dangling call ends the turn with `stop_reason: "pause_turn"` — re-send to let it finish.

**Platform availability:** **Claude API + Claude Platform on AWS only** — **not** AWS Bedrock, Vertex AI, or Microsoft Foundry. Flag this in any build-surface recommendation; confirm the dated GA/beta status against [`model-selection-and-2026-capability-map.md`](model-selection-and-2026-capability-map.md) before promising it to a client.

## Caching server-tool calls
Server-tool `tool_use`/`tool_result` blocks are cacheable content, but toggling a server tool (e.g., web search on/off) invalidates system + messages caches — keep the tool set stable across cached turns ([`prompt-caching-playbook.md`](prompt-caching-playbook.md)).

> **All of these carry dated GA/beta status — confirm against [`model-selection-and-2026-capability-map.md`](model-selection-and-2026-capability-map.md) (and re-verify on the Researcher sweep) before promising one to a client.**
