# Pick the build surface from the tree — a classification call isn't an agent

**Status:** Absolute rule — defaulting to the Agent SDK for a single-shot call, or to Managed Agents when you already operate infra, is the named anti-pattern (#2).

**Domain:** Architecture / build surface

**Applies to:** `claude-app-engineering`

---

## Why this exists

There are four ways to build a Claude-backed feature — Workbench, Messages API (Client SDK), Claude Agent SDK, Managed Agents — and they are not interchangeable defaults; each trades control for managed convenience differently. The recurring mistake is surface-by-habit: reaching for the **Agent SDK** because "we're building an agent" when the task is a single classification call that a Messages request handles with less code and full control; or reaching for **Managed Agents** for the hosted convenience when you already run the infra a Managed Agent would duplicate. House opinion #2: **pick the surface by traversing the decision tree on observable inputs** — are you still prototyping a prompt; does Claude need to autonomously read/run/edit files + use tools *in a loop*; and if so, should the agent + sandbox run in *your* process or be Anthropic-hosted. A classification call isn't an agent; don't give it an agent loop.

## How to apply

Traverse the build-surface tree on the observables before writing code — don't keyword-match "agent." Design the migration path so promoting later isn't a rewrite.

```text
prototyping a prompt? ─────────────► Workbench / Console (no code)
   else, loop of autonomous
   read/run/edit + tools? ──no──────► Messages API / Client SDK (you own the loop)
                          └─yes──► run agent + sandbox in MY infra? ──yes──► Claude Agent SDK
                                                                     └─no───► Managed Agents (hosted)
```

```python
# A single classification/extraction call is NOT an agent — Messages API, full control:
resp = client.messages.create(model="claude-haiku-4-5", max_tokens=512,
                              tools=CLASSIFY, tool_choice={"type":"tool","name":"classify"},
                              messages=[{"role":"user","content":doc}])
# Genuinely agentic (autonomous multi-step read/run/edit + tools) on YOUR files/infra:
async for msg in query(prompt=task, options=ClaudeAgentOptions(allowed_tools=["Read","Edit","Bash"])):
    handle(msg)                       # Agent SDK runs the loop in your process
```

**Do:**
- **Traverse the build-surface tree** ([`../knowledge/claude-build-surface-decision-tree.md`](../knowledge/claude-build-surface-decision-tree.md)) on the observables before choosing — don't pattern-match on the word "agent."
- Use the **Messages API** for single requests / custom orchestration / a classification or extraction call — own the loop, full control.
- Reach for the **Agent SDK** only when Claude genuinely needs an autonomous read/run/edit + tool loop on **your** infra/files; **Managed Agents** when you don't want to operate the sandbox/session infra (long-running/async).
- Design the **migration path** (Workbench → Agent SDK local → Managed Agents prod) so the move isn't a rewrite — keep tool logic portable, prompts/skills in files.

**Don't:**
- Default to the **Agent SDK** for a single-shot call — the named anti-pattern (#2); a classification call isn't an agent.
- Reach for **Managed Agents** when you already operate the infra they'd duplicate (#2).
- Add an agent loop you don't need — start with the simplest surface that works ([`../knowledge/agent-orchestration-patterns.md`](../knowledge/agent-orchestration-patterns.md)).

## Edge cases / when the rule does NOT apply

- **The deployment-target call** (Claude API vs Bedrock / Vertex / Foundry) is a *separate, downstream* decision driven by residency/quota/procurement/caching — not this surface tree ([`../knowledge/claude-app-finops-reliability-and-security.md`](../knowledge/claude-app-finops-reliability-and-security.md)).
- **Model right-sizing** (Opus/Sonnet/Haiku) is orthogonal — pick the surface first, then the model via the routing ladder ([`right-size-with-a-routing-ladder.md`](./right-size-with-a-routing-ladder.md)).
- **Billing (dated):** from 2026-06-15, Agent SDK + `claude -p` on subscription plans draw a separate Agent SDK credit — verify before scoping cost ([verify-at-build]).
- The agent *loop's* guardrails (max turns, stop conditions) are a separate rule once you've chosen an agentic surface ([`agent-guardrail-the-loop.md`](./agent-guardrail-the-loop.md)).

## See also

- [`../knowledge/claude-build-surface-decision-tree.md`](../knowledge/claude-build-surface-decision-tree.md) — the canonical surface tree + migration path
- [`../knowledge/agent-sdk-and-managed-agents.md`](../knowledge/agent-sdk-and-managed-agents.md) — Client SDK vs Agent SDK vs Managed Agents in depth
- [`./agent-guardrail-the-loop.md`](./agent-guardrail-the-loop.md) — guardrails once you've chosen an agentic surface
- [`../agents/claude-solution-architect.md`](../agents/claude-solution-architect.md) — owns the build-surface decision

## Provenance

Codifies house opinion #2 from [`../CLAUDE.md`](../CLAUDE.md) §3 ("pick the build surface from the tree") and the §4 anti-pattern ("defaulting to the Agent SDK for a single-shot call, or to Managed Agents when you already operate infra"). Grounded in [`../knowledge/claude-build-surface-decision-tree.md`](../knowledge/claude-build-surface-decision-tree.md) (code.claude.com/agent-sdk + platform.claude.com/managed-agents, retrieved 2026-05-28). The 2026-06-15 billing note is dated — verify.

---

_Last reviewed: 2026-05-30 by `claude`_
