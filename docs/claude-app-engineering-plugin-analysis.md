# claude-app-engineering — next-most-useful-addition analysis + buildout plan

**Date:** 2026-05-28
**Author:** Autonomous repo-analysis pass, round 2 (Claude Opus 4.7, overnight loop)
**Status:** Decision + research synthesis + buildout plan. §6 carries the expert review + gap analysis + score; §7 is the plan as revised by that review. Execution-sequenced build steps are inline in §5/§7.
**Grounding:** Claude-platform claims grounded in official docs (platform.claude.com, code.claude.com/agent-sdk, modelcontextprotocol.io) retrieved 2026-05-28. Source URLs inline.

---

## 0. TL;DR

Round 1 of this loop shipped `microsoft-fabric`. The next most valuable addition is a new **`claude-app-engineering`** plugin — a specialist team for building **applications on the Claude API + Claude Agent SDK + MCP**. Rationale: Raven Power's positioning explicitly names *"Agentic AI with Anthropic Claude"* as a service line ([`plugin-roadmap-analysis.md`](plugin-roadmap-analysis.md) §2.1); the marketplace **itself** is the proof-of-craft (it *is* a Claude Agent SDK plugin set); no opinionated "build production Claude apps" team exists in the Claude Code ecosystem (Anthropic ships examples, not an opinionated team); and the platform is a fast-moving, high-leverage body of knowledge (prompt caching, the Agent SDK, MCP, Managed Agents, evals) that a from-memory answer would get stale on within a month. The harness already ships a `claude-api` skill, validating demand.

---

## 1. Where round 1 left the gap map

After `microsoft-fabric`, the round-1 candidate table ([`microsoft-fabric-plugin-analysis.md`](microsoft-fabric-plugin-analysis.md) §2) re-scores like this:

| Candidate | Matt-edge | Active fit | Differentiation | Surface | Readiness | Grounding-now | Verdict |
|---|---|---|---|---|---|---|---|
| **`claude-app-engineering`** | 5 | 5 | **5** | 4 | 4 | 5 | **BUILD — winner** |
| `azure-cloud` (Bicep/IaC/Entra) | 3 | 4 | 2 | 5 | 3 | 5 | Defer — heavy overlap with core backend/security/architect + Fabric admin |
| `salesforce` | 2 | 2 | 2 | 5 | 3 | 3 | Defer — still competes with the PP/Microsoft brand |
| Deepen `web-design` knowledge | 3 | 4 | 3 | 3 | 5 | 4 | Bonus/maintenance, not a headline new domain |
| Backfill scenario frontmatter (older plugins) | — | — | — | — | 5 | — | Maintenance task, queue separately |

`claude-app-engineering` is the only remaining candidate scoring ≥4 on Matt-edge, active fit, differentiation, and grounding-now simultaneously. It is **the** domain where Matt has demonstrable craft (this repo), where the market is hot, and where no opinionated competitor plugin exists.

---

## 2. The architecture decision: new plugin vs. extend `ravenclaude-core`

The one contestable call (and the first thing §6's review stress-tests). **Decision: new plugin.**

- **Domain-distinct?** Yes. `ravenclaude-core` is the *domain-neutral team pattern* a consumer installs to get a Team Lead + specialists. `claude-app-engineering` is a *domain specialist team for a specific engineering discipline* — building software whose runtime is the Claude API/SDK. Putting Claude-API-specific caching/eval/MCP content into core would violate the "core stays domain-neutral" house rule.
- **≥3 agents?** Six (see §4).
- **The overlap risk is `ravenclaude-core/prompt-engineer`.** Clean seam: *"improve this prompt" → `core/prompt-engineer`* (a domain-neutral artifact-crafting role); *"design the prompt + caching + context strategy for a production Claude app" → `claude-app-engineering`* (API-specific engineering: cache breakpoints, 1M-context management, structured outputs, thinking config, cost). Same relationship `web-design` has to `core/frontend-coder`.
- **The house rule "domain plugins must not fork core's review roles"** is honored: this plugin ships **no** security-reviewer or architect clone. AI-app security (prompt injection, tool sandboxing, secret handling) and cross-domain architecture **escalate to `core/security-reviewer` and `core/architect`** — the plugin supplies AI-app-specific *knowledge*, core supplies the *review*.

---

## 3. Deep dive — the Claude app-engineering surface (research synthesis)

All claims grounded in official docs, retrieved 2026-05-28.

### 3.1 The four build surfaces (the core "how do I build this?" decision)
Per the [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview):

| Surface | You own | Best for |
|---|---|---|
| **Messages API** (Client SDK) | the whole tool loop | single requests, custom orchestration, full control |
| **Claude Agent SDK** (Python/TS) | config; Claude owns the agent loop + built-in tools | agents that read/run/edit on *your* infra; CI/CD; custom apps |
| **Managed Agents** (hosted REST) | events in / results out; Anthropic owns sandbox + session | production agents without operating sandbox/session infra; long-running/async |
| **Workbench / Console** | nothing (UI) | prototyping, prompt iteration |

Common path: prototype in Agent SDK locally → Managed Agents for production. (Note: from **2026-06-15**, Agent SDK + `claude -p` usage on subscription plans draws from a separate Agent SDK credit.)

### 3.2 Models (2026-05) — right-size, don't default to Opus
Opus 4.7 (hardest reasoning), Opus 4.6, **Sonnet 4.6** (balanced; **1M context**; **adaptive thinking** — `thinking:{type:"adaptive"}`, `budget_tokens` deprecated on 4.6), **Haiku 4.5** (cheap/fast). Opus 4.7 + Sonnet 4.6 both carry **1M-token context**. ([release notes](https://platform.claude.com/docs/en/release-notes/overview))

### 3.3 Prompt caching — the #1 cost + latency lever
([prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)) `cache_control` breakpoints (automatic top-level OR up to 4 explicit); **5-min** (1.25× write) vs **1-hour** (2× write) TTL; **cache read = 0.1× input**. Invalidation hierarchy **tools → system → messages** (a tool-def change busts everything). Minimum cacheable tokens are model-specific (Opus/Haiku 4.x = 4,096; Sonnet 4.6 = 1,024). Place the breakpoint on the **last stable block**; pre-warm to kill first-request latency; caches are **workspace-isolated** (Feb 2026). Thinking blocks are cached alongside content and preserved by default on Opus 4.5+/Sonnet 4.6+.

### 3.4 Tool use & structured output
Tool definitions (name + description + JSON schema — the description *is* the prompt), `tool_choice`, parallel tool use, the tool loop (`stop_reason: tool_use` → execute → `tool_result`). Structured/JSON output via tools rather than prose parsing.

### 3.5 MCP — reusable capability layer
([modelcontextprotocol.io](https://modelcontextprotocol.io)) Servers expose **tools / resources / prompts** (+ sampling, roots, elicitation) over **stdio / SSE / Streamable HTTP**; OAuth-style auth for remote servers. The Agent SDK connects MCP servers via `mcp_servers` config. Build an MCP server when a capability is **reused across apps/agents**; an in-process tool when it's app-specific.

### 3.6 Agent SDK internals
([overview](https://code.claude.com/docs/en/agent-sdk/overview)) Built-in tools (Read/Write/Edit/Bash/Glob/Grep/WebSearch/WebFetch/Monitor/AskUserQuestion); **hooks** (PreToolUse/PostToolUse/Stop/SessionStart/SessionEnd/UserPromptSubmit…) as callbacks; **subagents** (`AgentDefinition`, invoked via the `Agent` tool, `parent_tool_use_id` tracking); **permissions** (allowed_tools, permission_mode); **sessions** (resume + fork); filesystem config (`.claude/skills/*/SKILL.md`, `.claude/commands`, `CLAUDE.md`, plugins). **RavenClaude itself is a worked example** of skills + agents + hooks + plugins.

### 3.7 Extended/adaptive thinking & context management
Adaptive thinking on Sonnet 4.6 (replaces `budget_tokens`); extended thinking requires `temperature` unset/1; **1M context** + context editing/compaction; the **memory tool** (public beta, `managed-agents-2026-04-01` header for Managed Agents).

### 3.8 Batch, evals, reliability
**Batch API** — 50% discount, async 24h; `output-300k-2026-03-24` beta header raises batch `max_tokens` to 300k on Opus 4.7/4.6 + Sonnet 4.6 ([batch](https://platform.claude.com/docs/en/build-with-claude/batch-processing)). **Evals** — golden datasets, LLM-as-judge, regression suites; measure a delta before shipping a prompt/model change. **Reliability** — 429/overloaded handling with exponential backoff + jitter; streaming; observability (token usage, cache hit rate, latency).

### 3.9 Security (escalates to core/security-reviewer)
Prompt injection from tool results / retrieved docs / user input; never let untrusted content escalate tool access; secrets in env/secret-manager (never literals; `sk-ant-…` in source is a leak); redact PII from logs; sandbox tool execution. Computer use is GA (March 2026) and carries its own sandboxing requirements.

---

## 4. Plugin scope (the buildout)

A domain-specialist team in the `power-platform`/`microsoft-fabric` mold. Requires `ravenclaude-core@>=0.7.0`.

### 4.1 Roster — 6 agents

| Agent | Owns | Spawn when |
|---|---|---|
| **`claude-solution-architect`** | the build-surface decision (Messages API / Agent SDK / Managed Agents / Workbench), model right-sizing, deployment target (own infra / Bedrock / Vertex / Foundry), overall app architecture | "how should I build this Claude app?"; "Agent SDK or Managed Agents?"; "which model?" |
| **`prompt-and-context-engineer`** | prompt design, **prompt-caching strategy**, 1M-context management, structured outputs, adaptive/extended thinking, citations | "design the prompt + caching strategy"; "my cache hit rate is low"; "structure this output" |
| **`tool-and-mcp-engineer`** | tool-use design, **MCP server authoring** (transports/capabilities/auth), tool_choice, parallel tools, MCP-vs-tool decision | "build an MCP server"; "design these tools"; "expose this system to Claude" |
| **`agent-sdk-engineer`** | building with the Agent SDK (subagents, hooks, skills, sessions, permissions, plan mode) + Managed Agents | "build an agent with the SDK"; "add a hook/subagent/skill"; "move to Managed Agents" |
| **`eval-engineer`** | eval design, golden datasets, LLM-as-judge, regression suites, pre-ship deltas | "set up evals"; "did this prompt change regress?"; "measure quality" |
| **`claude-app-ops-engineer`** | token-cost **FinOps** (cache hit rate, batch, model routing), rate-limit/retry/backoff, streaming, observability | "my Claude bill is too high"; "handle 429s"; "add observability" |

*(No security-reviewer/architect clone — AI-app security + cross-domain architecture escalate to core per §2.)*

### 4.2 Knowledge bank — 8 docs (dated, cited)
1. `claude-build-surface-decision-tree.md` — Mermaid: Messages API / Agent SDK / Managed Agents / Workbench + deployment target.
2. `model-selection-and-2026-capability-map.md` — model lineup + dated GA/beta capability map (the freshness anchor).
3. `prompt-caching-playbook.md` — breakpoints, TTL, pricing, minimums, invalidation, pre-warming, hit-rate measurement.
4. `tool-use-and-structured-output.md` — tool contracts, tool_choice, parallel tools, the loop, structured output.
5. `mcp-server-authoring.md` — architecture, transports, capabilities, auth, security; MCP-vs-tool decision.
6. `agent-sdk-and-managed-agents.md` — SDK internals + Managed Agents + Client-SDK comparison + the June-2026 credit note.
7. `evals-and-quality.md` — eval design, golden sets, LLM-as-judge, regression discipline.
8. `claude-app-finops-reliability-and-security.md` — cost model, batch, routing, backoff, observability + the prompt-injection/secrets section that escalates to core/security-reviewer.

### 4.3 Templates — 6
`claude-app-architecture-spec.md`, `prompt-and-caching-design.md`, `mcp-server-spec.md`, `eval-plan.md`, `claude-app-cost-model.md`, `agent-sdk-app-runbook.md`.

### 4.4 Hook (advisory; `CLAUDE_APP_STRICT=1` to block)
`check-claude-app-anti-patterns.sh` on `.py`/`.ts`/`.js`/`.json`/`.md`:
1. Hardcoded `sk-ant-…` API key literal → secret leak (security).
2. `budget_tokens` near a `sonnet-4-6` model id → deprecated; use adaptive thinking.
3. Retired model id (`claude-2`, `claude-instant`, `claude-1`) → bump to a current 4.x model.
4. `temperature` set to a non-1 value alongside `thinking` enabled → extended thinking needs temperature 1/unset.

### 4.5 House opinions — 14 (see §7 for the final list; highlights)
Cache the static prefix · pick the build surface from the tree · right-size the model · evals before vibes · structured output via tools · tools are a contract · untrusted content is untrusted (escalate to core/security-reviewer) · secrets never in code · 429s get backoff · batch the async work · thinking config is model-specific · pin the model + watch the date · don't fork core's review roles · MCP for reuse, tools for one-offs.

### 4.6 Seams
- **`ravenclaude-core/prompt-engineer`** — "improve this prompt" → core; "design the app's prompt+caching+context strategy" → here.
- **`ravenclaude-core/security-reviewer`** — prompt injection, auth, secrets, tool sandboxing → core (mandatory).
- **`ravenclaude-core/architect`** — cross-domain architecture adjudication.
- **`ravenclaude-core/backend-coder` / `frontend-coder`** — the non-Claude app code → core; the Claude integration layer → here.
- **`web-design`** — the app's marketing site / UI shell → web-design.
- **`data-platform` / `microsoft-fabric`** — the app's data backend → those plugins.

---

## 5. Risks & open questions (pre-review)
- **R1 — prompt-engineer overlap.** The seam must be crisp or core/prompt-engineer and this plugin's prompt-and-context-engineer collide. *(Review: stress-test the wording.)*
- **R2 — "too meta."** The plugin is for building the same kind of thing the marketplace is. Is that clarifying (worked example) or confusing? *(Review.)*
- **R3 — Currency rot.** The platform ships monthly; the dated capability map + retrieval-dated citations + Researcher sweep are the mitigation.
- **R4 — Roster size.** 6 agents — is any foldable (e.g., ops into architect)? *(Review.)*
- **R5 — No bundled MCP.** v0.1.0 documents `pip install claude-agent-sdk` / `npm i @anthropic-ai/claude-agent-sdk` + the Anthropic SDK as prerequisites; bundles nothing.

---

## 6. Expert review + gap analysis + score

Two independent reviewers were convened against §0-§5: a **Claude-platform / Agent-SDK domain engineer** and the **RavenClaude marketplace-conventions architect**. Both returned **Approve-with-changes**; the new-plugin decision was endorsed without dissent.

### 6.1 Scores (1-5)

| Dimension | Score | Reviewer |
|---|---|---|
| New-plugin justification | 5 | conventions |
| Surface coverage | 3 | domain |
| Technical accuracy (as drafted in §3) | 3 | domain |
| Roster design | 4 | domain |
| Knowledge-bank design | 4 | domain |
| House-opinions / hook quality | 3 | domain |
| Seam cleanliness (prompt-engineer / security / architect) | 3 | conventions |
| Convention compliance | 4 | conventions |
| Scope realism for v0.1.0 | 4 | both |

**Composite ~3.7/5 — Approve-with-changes.** The two 3s (surface coverage, seam cleanliness) drive the must-fix list; both are fixable in the knowledge bank + CLAUDE.md wording, not the architecture.

### 6.2 Must-fix (folded into §7)

1. **[domain] No owner for Anthropic-hosted server tools.** Computer use, code execution, web search/fetch, the Files API, and the memory tool as an *implemented* feature are mentioned in prose but unowned. → give `mcp-and-server-tools-engineer` (renamed from `tool-and-mcp-engineer`) explicit ownership of hosted server tools; add a **9th knowledge doc** `server-side-tools-and-files.md`. No 7th agent.
2. **[domain] Move in-app tool-use *design* to `prompt-and-context-engineer`.** Tool schemas / `tool_choice` / parallel tools / the Messages-API tool loop / structured output are the same "contract-design" muscle as prompts; the MCP agent should be the **MCP-server + hosted-server-tools** specialist. Keeps the roster at 6.
3. **[domain] Operationalize cache-invalidation churn** in `prompt-caching-playbook.md` + a house opinion: *stable content above the breakpoint, volatile below; never mutate tool defs per request* (the #1 real-world hit-rate killer).
4. **[conventions] Make the prompt-engineer seam binding CLAUDE.md text; `eval-engineer` is a third collision.** `core/prompt-engineer` critiques prompts *and* tracks Claude-platform updates via the `claude-api` skill — overlapping both `prompt-and-context-engineer` and `eval-engineer`. → put the exact §10 seam wording (below) in the plugin's CLAUDE.md + a reciprocal one-line prior on `core/prompt-engineer.md`.
5. **[conventions] Pin `ravenclaude-core@>=0.7.0`** (the minimum actually needed — Structured Output + CGP + spawn-team; the Thing/posture are consumer features that don't raise the floor). Do **not** bump to 0.48.0.
6. **[domain] Revise the hook to higher-value, lower-false-positive checks** (see §7.4). Demote model-version-coupled checks (budget_tokens, temperature+thinking) — they rot; move them to knowledge instead.

### 6.3 Should-fix / corrections (folded into §7 + the knowledge bank)

- **[conventions] Justify `claude-solution-architect` against the "could core/architect + a skill match it?" test** (the test that folded `data-platform-architect` into a `stack-selection` skill). → §7 argues it carries operational craft core/architect lacks: deployment-target-specific caching/model-ID/quota constraints (Bedrock/Vertex/Foundry), the build-surface migration path (prototype→Agent SDK→Managed Agents), and token cost-shape modeling. Mirrors how `microsoft-fabric/fabric-architect` was justified in round 1.
- **[domain] Evals doc** must cover judge-prompt drift / position bias (pairwise + randomized order) and eval cost (judge on **Haiku via Batch**, 50%).
- **[domain] FinOps** gets the concrete routing lever (cheap triage → escalate-on-uncertainty; metric = **cost-per-resolved-task + cache hit rate**, not raw tokens) and a deployment-target section.
- **[conventions] CHANGELOG + three-way version sync** — ship `CHANGELOG.md` at `[0.1.0]`; sync `plugin.json` `version` + catalog per-plugin `version` + bump catalog `metadata.version` (0.27.0 → 0.28.0). Scenario frontmatter mandatory on all 6 agents, `audience: [dev]` (don't invent a new taxonomy value).
- **[domain] §3 accuracy** — the §3.3 minimum-cacheable-tokens figures (Opus/Haiku 4.x = 4,096; Sonnet 4.6 = 1,024) come from the **live docs retrieved 2026-05-28** (more current than a Jan-2026 memory, which would say 1,024/2,048). Ship them **dated + cited** in the capability map so the monthly Researcher sweep refreshes one file; the same applies to the 1-hour-TTL multiplier, the 300k-output batch header, adaptive thinking, the June-2026 Agent SDK credit, and computer-use GA. R2 "too meta" confirmed a non-issue — state the worked-example framing in CLAUDE.md.

---

## 7. Revised plan (per §6)

**Build it, with these locked-in changes.**

### 7.1 Roster — 6 agents (re-allocated per §6.2)
1. **`claude-solution-architect`** — build-surface + model + deployment-target decision, app architecture. *(Justified: deployment-target-specific constraints + build-surface migration path + cost-shape modeling — operational craft core/architect + a skill lacks.)*
2. **`prompt-and-context-engineer`** — prompts, **prompt-caching strategy**, 1M-context management, adaptive/extended thinking, citations, **+ tool-use design (schemas / tool_choice / parallel tools / the Messages-API tool loop) + structured output** (moved here).
3. **`mcp-and-server-tools-engineer`** — **MCP server authoring** (transports / capabilities / auth) **+ Anthropic-hosted server tools** (computer use, code execution, web search/fetch, Files API, memory-tool runtime); MCP-vs-tool decision.
4. **`agent-sdk-engineer`** — Agent SDK (subagents/hooks/skills/sessions/permissions/plan-mode) + Managed Agents.
5. **`eval-engineer`** — eval design, golden sets, LLM-as-judge (position-bias + Haiku-on-Batch cost), regression deltas.
6. **`claude-app-ops-engineer`** — token-cost FinOps (routing ladder, cache hit rate, cost-per-resolved-task), 429/backoff, streaming, observability.

### 7.2 Knowledge bank — 9 docs (dated + cited)
The eight from §4.2 **plus** `server-side-tools-and-files.md` (computer use, code execution, web search/fetch, Files API, memory tool). Accuracy corrections from §6.3 baked into `prompt-caching-playbook.md`, `model-selection-and-2026-capability-map.md`, `evals-and-quality.md`, and `claude-app-finops-reliability-and-security.md`.

### 7.3 House opinions — 14 (final list in CLAUDE.md §3)
Cache static-prefix-above-the-breakpoint / volatile-below (no per-request tool-def churn) · pick the build surface from the tree · routing ladder + cost-per-resolved-task · evals before vibes (Haiku judge on Batch, randomized order) · structured output via tools · tools are a contract · untrusted content is untrusted (→ core/security-reviewer) · secrets never in code / never log full prompts · 429s get backoff+jitter · batch the async · `max_tokens` mandatory + pin the model + thinking-config-is-dated · MCP for reuse, tools for one-offs · don't fork core's review roles · cite the capability with a retrieval date.

### 7.4 Hook — `check-claude-app-anti-patterns.sh` (advisory; `CLAUDE_APP_STRICT=1` to block)
On `.py`/`.ts`/`.js`: (1) hardcoded `sk-ant-…` literal → secret leak; (2) a `messages.create`/`.messages.stream` call in a file with **no `max_tokens` anywhere** → silent-truncation risk; (3) retired model id (`claude-2`, `claude-instant`, `claude-1`) → bump to a current 4.x; (4) full-message logging (`print(messages`, `console.log(messages`, `logger.*(messages`) → secret/PII leak. (budget_tokens / temperature+thinking moved to knowledge, not the hook — too model-version-coupled.)

### 7.5 Seams — binding CLAUDE.md §10 wording
- **`core/prompt-engineer`:** *prompt-as-artifact* (authoring/critiquing agent + skill files, reusable prompt patterns, tracking Anthropic's prompting guidance) → core; the *application's* prompt + caching + context + thinking + token-economics engineering → here. **Litmus:** *a better-written prompt or a reusable agent/skill definition → core/prompt-engineer; the caching strategy, context budget, thinking config, or token economics of a running Claude app → here.* Eval of an *agent-file* prompt stays core (`agent-quality-rubric`); eval of an *app* prompt/model change is `eval-engineer`. Add a reciprocal one-line prior to `core/prompt-engineer.md`.
- **`core/security-reviewer` (mandatory):** all AI-app security (prompt injection, tool sandboxing, secrets, PII-in-logs, computer-use sandboxing) → core; this plugin supplies AI-app security *knowledge*, core supplies the *verdict*. No security-reviewer clone.
- **`core/architect`:** cross-domain/whole-system architecture → core; `claude-solution-architect` owns the Claude-runtime build-surface/model/deployment decision only. No architect clone.
- **`core/backend-coder`/`frontend-coder`** → non-Claude app code; **`web-design`** → UI shell; **`data-platform`/`microsoft-fabric`** → data backend.

### 7.6 Build mechanics
`requires: ravenclaude-core@>=0.7.0`; three-way version sync (plugin.json + catalog entry + catalog `metadata.version` 0.27.0→0.28.0); `CHANGELOG.md` at `[0.1.0]`; scenario frontmatter (`audience:[dev]`) on all 6 agents; advisory hook; standard subdirs already allow-listed; regenerate `repo-guide.html`; update `architecture.md` + root `README.md`; reciprocal prior on `core/prompt-engineer.md`. No NOTICE/MCP (documents the SDK `pip`/`npm` prerequisite).

---

## 8. Sources
Claude platform docs retrieved 2026-05-28: [API overview](https://platform.claude.com/docs/en/api/overview), [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing), [release notes](https://platform.claude.com/docs/en/release-notes/overview), [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview), [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview), [Model Context Protocol](https://modelcontextprotocol.io), and the [claude-api skill](https://github.com/anthropics/skills/blob/main/skills/claude-api/SKILL.md).
