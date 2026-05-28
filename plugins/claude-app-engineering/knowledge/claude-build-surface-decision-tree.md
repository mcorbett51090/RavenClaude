# Decision tree: which Claude build surface?

**Last reviewed:** 2026-05-28 · **Confidence:** high (platform.claude.com + code.claude.com/agent-sdk, retrieved 2026-05-28).
**Owner:** `claude-solution-architect` (traverse before recommending a surface).

```mermaid
flowchart TD
    A[Build a Claude-backed feature] --> P{Just prototyping / iterating on a prompt?}
    P -->|Yes| WB[Workbench / Console<br/>no code, fast prompt iteration]
    P -->|No| L{Does Claude need to autonomously<br/>read/run/edit files + use tools<br/>in a loop?}
    L -->|No — single request or<br/>you want to own the loop| MA[Messages API / Client SDK<br/>you implement the tool loop]
    L -->|Yes| H{Where should the agent + sandbox run?}
    H -->|In MY process / infra,<br/>on my files & services| SDK[Claude Agent SDK<br/>Python or TypeScript]
    H -->|Anthropic-hosted, per-session<br/>sandbox, async/long-running,<br/>no infra to operate| MGA[Managed Agents<br/>hosted REST API]
```

## The four surfaces

| Surface | You own | Claude owns | Best for |
|---|---|---|---|
| **Workbench / Console** | nothing (UI) | — | prototyping, prompt iteration |
| **Messages API** (Client SDK) | the whole tool loop, orchestration | model inference | single requests, custom orchestration, full control |
| **Claude Agent SDK** (Python/TS) | config, custom tools, infra | the agent loop + built-in tools + context mgmt | agents on *your* infra/files; CI/CD; custom apps |
| **Managed Agents** (hosted REST) | events in / results out | the loop **and** the sandbox + session log | production agents w/o operating sandbox/session infra; long-running/async |

Source: [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview), [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview).

## The migration path (the recurring real decision)
**Prototype in Workbench → build in the Agent SDK locally → move to Managed Agents for production** when you don't want to operate the sandbox/session infrastructure. This is the canonical path; design so the move doesn't require a rewrite (keep tool logic portable, keep prompts/skills in files).

## Client SDK vs Agent SDK in one line
- **Client SDK:** `response = client.messages.create(...)`; **you** loop on `stop_reason == "tool_use"`, execute the tool, send `tool_result`, repeat.
- **Agent SDK:** `async for message in query(prompt=..., options=...)`; Claude runs the loop, executes built-in tools, manages context.

## Deployment target also shapes the architecture
The same surfaces run against the Claude API directly **or** via **Amazon Bedrock** (`CLAUDE_CODE_USE_BEDROCK=1`), **Claude Platform on AWS**, **Google Vertex AI** (`CLAUDE_CODE_USE_VERTEX=1`), or **Microsoft Foundry** (`CLAUDE_CODE_USE_FOUNDRY=1`). Each has distinct model-ID schemes, region/quota constraints, and prompt-caching support — pick the target with the data-residency + procurement + caching story the engagement needs (see [`claude-app-finops-reliability-and-security.md`](claude-app-finops-reliability-and-security.md)).

> **Billing note (dated):** from **2026-06-15**, Agent SDK + `claude -p` usage on subscription plans draws from a separate Agent SDK credit. Verify before quoting an engagement. ([source](https://code.claude.com/docs/en/agent-sdk/overview))

> House-opinion link: **#2 pick the build surface from the tree** (don't default to the Agent SDK for a single-shot classification, or to Managed Agents when you already operate infra).
