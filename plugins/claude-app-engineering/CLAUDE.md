# Claude App-Engineering Plugin — Team Constitution

> Team constitution for the `claude-app-engineering` Claude Code plugin. Six specialist agents for building **production applications on the Claude API, the Claude Agent SDK, and MCP** — plus a citation-grounded knowledge bank, templates, and an advisory hook.
>
> Built for developers shipping Claude-backed products: the build-surface decision, prompt caching, tool use, MCP servers, Agent SDK / Managed Agents, evals, and LLM FinOps — grounded in first-party docs, not a memory of a platform that ships monthly.
>
> **The marketplace is the worked example.** RavenClaude itself *is* a Claude Agent SDK plugin set (skills + agents + hooks + plugins). When designing a consumer's Claude app, point at `plugins/*/` as a reference implementation — that's clarifying, not meta-confusion.
>
> **Orientation:** this file is **domain-specific** to building Claude apps. For the domain-neutral team (architect, coders, reviewers, prompt-engineer, etc.) inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`claude-solution-architect`](agents/claude-solution-architect.md) | the **build-surface** decision (Messages API / Agent SDK / Managed Agents / Workbench), model right-sizing, deployment target, app architecture + migration path | "how should I build this Claude app?"; "Agent SDK or Managed Agents?"; "which model + deployment?" |
| [`prompt-and-context-engineer`](agents/prompt-and-context-engineer.md) | prompts, **prompt-caching strategy**, 1M-context, adaptive/extended thinking, citations, **in-app tool-use design + the Messages-API loop + structured output** | "design the prompt + caching strategy"; "low cache hit rate"; "structure this output"; "design these tools" |
| [`mcp-and-server-tools-engineer`](agents/mcp-and-server-tools-engineer.md) | **MCP server authoring** + **Anthropic-hosted server tools** (computer use, code execution, web search/fetch, Files API, memory) | "build an MCP server"; "expose this system to Claude"; "set up computer use / code execution / Files API" |
| [`agent-sdk-engineer`](agents/agent-sdk-engineer.md) | the **Claude Agent SDK** (subagents/hooks/skills/sessions/permissions/plan-mode) + **Managed Agents** | "build an agent with the SDK"; "add a hook/subagent/skill"; "move to Managed Agents" |
| [`eval-engineer`](agents/eval-engineer.md) | **evals** — golden sets, programmatic + LLM-as-judge grading, regression deltas | "set up evals"; "did this prompt change regress?"; "my judge is unreliable" |
| [`claude-app-ops-engineer`](agents/claude-app-ops-engineer.md) | **FinOps** (cache hit rate, routing ladder, Batch, cost-per-resolved-task), reliability (429/backoff), observability | "my bill is too high"; "handle 429s"; "add observability" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. This is a domain **doing**-team in the `power-platform`/`microsoft-fabric` mold. Per the marketplace house rule it ships **no** security-reviewer or architect clone — AI-app security and cross-domain architecture escalate to core (§10).

---

## 2. Routing rules (Team Lead)

- **"How should I build this on Claude?" / surface / model / deployment** → `claude-solution-architect`.
- **Prompts / caching / context / thinking / structured output / in-app tool design** → `prompt-and-context-engineer`.
- **MCP server / hosted server tools (computer use, code execution, Files API, memory)** → `mcp-and-server-tools-engineer`.
- **Agent SDK build / hooks / subagents / sessions / Managed Agents** → `agent-sdk-engineer`.
- **Evals / "did this regress?" / LLM-judge** → `eval-engineer`.
- **Cost / 429s / reliability / observability** → `claude-app-ops-engineer`.
- **Improve a prompt or agent/skill file as an artifact** → `ravenclaude-core/prompt-engineer` (the seam, §10).
- **Any auth / secret / PII / injection / sandboxing** → `ravenclaude-core/security-reviewer` (mandatory).
- **Whole-system architecture across non-Claude services** → `ravenclaude-core/architect`.

---

## 3. Cross-cutting house opinions (every agent enforces; the hook flags the grep-able ones)

1. **Cache the static prefix.** Stable content above the breakpoint, volatile below; **never mutate tool defs per request** (the #1 cache-hit-rate killer).
2. **Pick the build surface from the tree.** Messages API / Agent SDK / Managed Agents / Workbench — a classification call isn't an agent.
3. **Right-size with a routing ladder.** Cheap triage (Haiku) → escalate-on-uncertainty to Sonnet/Opus; the metric is **cost-per-resolved-task + cache hit rate**, not raw tokens.
4. **Evals before vibes.** No prompt/model/tool change ships without a delta on a golden set; judge on Haiku via Batch, randomize order against position bias.
5. **Structured output via tools, not regex.**
6. **Tools are a contract.** Name + description + JSON schema; the description is the prompt.
7. **Untrusted content is untrusted.** Tool results, retrieved docs, fetched web content, user input can carry injection; never let them escalate tool access; escalate the design to `core/security-reviewer`.
8. **Secrets never in code; never log full prompts.** Keys in env/secret-manager; redact PII from logs and the memory tool.
9. **429 / overloaded get exponential backoff + jitter** (capped retries, idempotency for effects).
10. **Batch the async.** 50% off (+300k-output beta) — don't pay interactive rates for offline work.
11. **`max_tokens` is mandatory; pin the model; thinking config is dated.** Adaptive thinking on Sonnet 4.6 (`budget_tokens` deprecated there) — keep version-specific params in the capability map, not baked into code/personas.
12. **MCP for reuse, in-process tools for one-offs.**
13. **Don't fork core's review roles.** AI-app security → `core/security-reviewer`; cross-domain architecture → `core/architect`.
14. **Cite the capability with a retrieval date.** The platform ships monthly; every numeric/GA claim lives in the dated capability map so one file refreshes, not six.

---

## 4. Anti-patterns every agent flags

- A breakpoint above per-request content, or regenerating/reordering tool defs each call (busts the cache — #1).
- Defaulting to the Agent SDK for a single-shot call, or to Managed Agents when you already operate infra (#2).
- Defaulting to Opus for everything; optimizing raw tokens instead of cost-per-resolved-task (#3).
- Shipping a prompt/model change on "looks better" with no eval delta (#4).
- Parsing JSON out of prose instead of a forced tool call (#5).
- A thin tool description and hoping the system prompt fixes it (#6).
- Letting a tool result / retrieved doc escalate tool access or auto-approve a destructive action (#7).
- `sk-ant-…` literal in source; `print(messages)` / logging full prompts (#8 — the hook flags both).
- Retrying a 429 immediately with no backoff/jitter (#9).
- Running evals/backfills/bulk jobs at interactive rates instead of Batch (#10).
- A `messages.create` call with no `max_tokens` (#11 — the hook flags it); a retired model id (`claude-2`/`claude-instant`/`claude-1`).
- Standing up an MCP server for one app's one function (#12).
- Building a security-reviewer/architect clone instead of escalating to core (#13).
- Quoting a capability's GA/preview status with no retrieval date (#14).

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

Inherits the CGP from `ravenclaude-core`. Before any agent says "I can't" or declares a design, it must:

1. **Consult the knowledge bank** (§8) — the decision tree + dated capability map + playbooks are the source of truth.
2. **Traverse the relevant decision tree** (build-surface, MCP-vs-tool) before recommending — don't keyword-match.
3. **Try the next-easiest defensible path** before declaring blocked (Messages API → Agent SDK → Managed Agents; in-process tool → MCP; programmatic grader → LLM judge).
4. **Escalate with the mandatory phrasing** — what was tried, what was ruled out, the recommended next path.

See the upstream protocol in [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).

---

## 6. Output Contract

Each agent ends with its role-specific contract (see the agent file) **plus the cross-plugin Structured Output Protocol JSON block** ([`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)). Agents are **advisory and interactive**: the consumer's app + API keys live outside the repo, so they recommend and emit runnable snippets (Python/TS, `fab`-style CLI, MCP configs, eval harnesses) the developer runs — they don't call the API against the consumer's account.

---

## 7. Automated checks (hooks)

The `hooks/` directory ships [`check-claude-app-anti-patterns.sh`](hooks/check-claude-app-anti-patterns.sh) — a PreToolUse Write/Edit/MultiEdit hook on `.py`/`.ts`/`.js`/`.tsx`/`.jsx` files:

| Check | Triggers on | Rule (§3 / §4) |
|---|---|---|
| Hardcoded `sk-ant-…` API key literal | source files | #8 — secrets never in code |
| `messages.create`/`.messages.stream` in a file with **no `max_tokens`** anywhere | source files | #11 — silent-truncation / overspend risk |
| Retired model id (`claude-2`, `claude-instant`, `claude-1`) | source files | #11 — pin a current 4.x model |
| Full-message logging (`print(messages`, `console.log(messages`, `logger.*(messages`) | source files | #8 — never log full prompts (secret/PII leak) |

Advisory by default (`exit 0` with stderr warnings). Set `CLAUDE_APP_STRICT=1` to make it blocking. Model-version-coupled checks (adaptive-thinking params, temperature+thinking) deliberately live in the knowledge bank, not the hook — they'd rot monthly.

---

## 8. Knowledge bank

Reference docs with `Last reviewed:` dates + confidence + source URLs. Inline priors live on the agents; the files in `knowledge/` are the source of truth, re-read on demand. **All numeric/GA claims are dated** and concentrated in the capability map so the Researcher sweep refreshes one file, not six.

| File | Read when |
|---|---|
| [`knowledge/claude-build-surface-decision-tree.md`](knowledge/claude-build-surface-decision-tree.md) | Choosing how to build — Messages API / Agent SDK / Managed Agents / Workbench + deployment target |
| [`knowledge/model-selection-and-2026-capability-map.md`](knowledge/model-selection-and-2026-capability-map.md) | "Which model?" / "is this GA or beta?" — the dated lineup + capability map (the freshness anchor) |
| [`knowledge/prompt-caching-playbook.md`](knowledge/prompt-caching-playbook.md) | Designing/debugging caching — breakpoints, TTL, pricing, minimums, invalidation churn, pre-warming, hit-rate |
| [`knowledge/tool-use-and-structured-output.md`](knowledge/tool-use-and-structured-output.md) | Designing tools / the Messages-API loop / structured output |
| [`knowledge/mcp-server-authoring.md`](knowledge/mcp-server-authoring.md) | Building an MCP server / MCP-vs-tool decision |
| [`knowledge/server-side-tools-and-files.md`](knowledge/server-side-tools-and-files.md) | Computer use / code execution / web search-fetch / Files API / memory tool |
| [`knowledge/agent-sdk-and-managed-agents.md`](knowledge/agent-sdk-and-managed-agents.md) | Building with the Agent SDK or Managed Agents |
| [`knowledge/evals-and-quality.md`](knowledge/evals-and-quality.md) | Setting up evals / making an LLM-judge trustworthy + cheap |
| [`knowledge/claude-app-finops-reliability-and-security.md`](knowledge/claude-app-finops-reliability-and-security.md) | Cost / reliability / observability + the AI-app security section (escalates to core) |
| [`knowledge/retrieval-and-rag-2026.md`](knowledge/retrieval-and-rag-2026.md) | Answering over a corpus — the RAG-vs-long-context-vs-Files decision (skip RAG under ~200K tokens), Anthropic **Contextual Retrieval** (contextual embeddings + BM25 + RRF + reranking), Voyage embeddings, chunking, agentic RAG. Owned by `prompt-and-context-engineer` + `mcp-and-server-tools-engineer` |
| [`knowledge/prompt-engineering-techniques.md`](knowledge/prompt-engineering-techniques.md) | Making a running app's prompt produce the right output — the leverage ladder (clear+direct → multishot → CoT/thinking → XML structure → role/system → prefill → chaining), output control, hallucination reduction, the prompt→eval loop. Owned by `prompt-and-context-engineer` |
| [`knowledge/agent-orchestration-patterns.md`](knowledge/agent-orchestration-patterns.md) | Workflows vs agents + the 5 Anthropic patterns (prompt chaining / routing / parallelization / orchestrator-workers / evaluator-optimizer), Agent Skills as the shared standard, start-simple discipline. RavenClaude is the orchestrator-worker example. Owned by `agent-sdk-engineer` + `claude-solution-architect` |
| [`knowledge/context-engineering-2026.md`](knowledge/context-engineering-2026.md) | Curating the right tokens in a 1M window — caching layout, retrieve-vs-hold, ordering, context editing/compaction, the memory tool, sub-agent context isolation, thinking-block cost. Owned by `prompt-and-context-engineer` |

---

## 8a. Scenarios bank — TODO (planned)

Not yet enabled. Per the marketplace pattern, enable when the first real engagement scenario surfaces via `/wrap`: create `plugins/claude-app-engineering/scenarios/` with a `README.md` (copy from `plugins/power-platform/scenarios/README.md`), add the scenario-retrieval inline-prior block to the relevant agents, and remove this block.

---

## 9. Templates in this plugin

| Template | Use for |
|---|---|
| [`templates/claude-app-architecture-spec.md`](templates/claude-app-architecture-spec.md) | Surface + model + deployment + tools/MCP + caching + eval/ops plan |
| [`templates/prompt-and-caching-design.md`](templates/prompt-and-caching-design.md) | Prompt layout, breakpoint placement, TTL, context budget, hit-rate target |
| [`templates/mcp-server-spec.md`](templates/mcp-server-spec.md) | MCP server: capabilities, transport, auth, schemas, security hand-off |
| [`templates/eval-plan.md`](templates/eval-plan.md) | Golden set + graders + metric + CI + judge-bias controls |
| [`templates/claude-app-cost-model.md`](templates/claude-app-cost-model.md) | Token/cost model: caching, routing ladder, batch, cost-per-resolved-task |
| [`templates/agent-sdk-app-runbook.md`](templates/agent-sdk-app-runbook.md) | Agent SDK build → Managed Agents promotion runbook |

---

## 10. Escalating out of the claude-app-engineering team — the seams

**`ravenclaude-core/prompt-engineer`** — owns the *prompt-as-artifact* meta-layer: authoring/critiquing/refactoring agent files, skill files, and reusable prompt patterns across the marketplace, and tracking Anthropic's published prompting guidance. **This plugin owns the *application's* prompt + context + caching engineering**: cache-breakpoint placement, TTL choice, 1M-context management, structured-output-via-tools, thinking config, and the cost/latency of those choices in a running app. **Litmus test:** *if the deliverable is a better-written prompt or a reusable agent/skill definition → `core/prompt-engineer`; if it's the caching strategy, context budget, thinking config, or token economics of a production Claude app → here (`prompt-and-context-engineer`).* Eval of an *agent-file* prompt's quality stays `core/prompt-engineer` via the `agent-quality-rubric` skill; eval of an *app* prompt/model change is `eval-engineer` here.

**`ravenclaude-core/security-reviewer` (mandatory)** — every AI-app security concern (prompt injection from tool results / retrieved docs / user input, tool-execution + computer-use sandboxing, secret handling, PII redaction in logs/memory) escalates to core. This plugin supplies AI-app-specific *knowledge* (the security section of [`knowledge/claude-app-finops-reliability-and-security.md`](knowledge/claude-app-finops-reliability-and-security.md)); core supplies the *review verdict*. This plugin ships **no** security-reviewer.

**`ravenclaude-core/architect`** — cross-domain / whole-system architecture spanning non-Claude services. `claude-solution-architect` owns the *Claude-runtime* build-surface/model/deployment decision only. This plugin ships **no** architect clone.

**`ravenclaude-core/backend-coder` / `frontend-coder`** — the non-Claude application code (the API server, the web app); the Claude integration layer is here.

**`web-design`** — the app's marketing site / UI shell. **`data-platform` / `microsoft-fabric`** — the app's data backend (SMB-embedded vs enterprise-Microsoft).

**`azure-cloud/app-platform-engineer`** (when installed) — provisions the **Azure host** the Claude app deploys to (Container Apps / Functions / Foundry), its scaling, networking, and the IaC. **Litmus test:** *prompt / caching / tool / eval code → here; "where on Azure does this run and how is it provisioned" → `azure-cloud/app-platform-engineer`.* `claude-solution-architect` names the deployment target; azure-cloud provisions + scales it. (Reciprocal of [`../azure-cloud/CLAUDE.md`](../azure-cloud/CLAUDE.md) §10.)

---

## 11. The SDK prerequisite (no bundled MCP at v0.1.0)

No bundled MCP server. The agents recommend and emit code against the **Anthropic SDK** (`pip install anthropic` / `npm i @anthropic-ai/sdk`) and the **Claude Agent SDK** (`pip install claude-agent-sdk` / `npm i @anthropic-ai/claude-agent-sdk`), run by the developer with their own `ANTHROPIC_API_KEY` (or Bedrock/Vertex/Foundry creds). See [`knowledge/agent-sdk-and-managed-agents.md`](knowledge/agent-sdk-and-managed-agents.md). If a stable community Claude/Anthropic MCP emerges, evaluate bundling it later.

---

## 12. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Structured Output Protocol (upstream): [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- The prompt-engineer seam: [`../ravenclaude-core/agents/prompt-engineer.md`](../ravenclaude-core/agents/prompt-engineer.md)
- Build provenance: [`../../docs/claude-app-engineering-plugin-analysis.md`](../../docs/claude-app-engineering-plugin-analysis.md)
