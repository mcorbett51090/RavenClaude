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
| [`knowledge/cost-and-caching-decision-trees.md`](knowledge/cost-and-caching-decision-trees.md) | **Mermaid** — (1) cache-hit-rate-collapse debug tree ("caching configured but bill not dropping"); (2) the cost-lever ladder ("bill too high — which lever, in what order"). Complements the existing decision-tree file. Owned by `prompt-and-context-engineer` + `claude-app-ops-engineer` |
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

## 8a. Scenarios bank (enabled — build-out 2026-06-05)

Now live. [`scenarios/`](scenarios/) holds dated, scope-tagged, **unverified** Claude-app build narratives (the marketplace dual-bank pattern; see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)). Surface a matching scenario only as a *secondary* source, behind the mandatory unverified-scenario preamble ("Based on N unverified scenarios from YYYY-MM tagged [scope] — verify in your environment"), never overriding the cited knowledge bank (§8). Any dated platform fact inside a scenario (model id, price, GA status, window size) carries `[verify-at-use]` and defers to the capability map. The most-likely-to-benefit specialists — `prompt-and-context-engineer`, `claude-app-ops-engineer`, `eval-engineer`, `mcp-and-server-tools-engineer` — should check the bank when a situation matches.

| File | Scope | Tags |
|---|---|---|
| [`prompt-cache-hit-rate-collapse`](scenarios/2026-06-05-prompt-cache-hit-rate-collapse.md) | likely-general | prompt-caching, cache-hit-rate, cost-blowout, prefix-invalidation |
| [`tool-use-runaway-loop`](scenarios/2026-06-05-tool-use-runaway-loop.md) | likely-general | tool-use, agentic-loop, runaway, idempotency, stop-reason |
| [`rag-retrieval-miss-under-200k`](scenarios/2026-06-05-rag-retrieval-miss-under-200k.md) | likely-general | rag, retrieval, long-context, reranking, eval-the-retriever |
| [`streaming-timeout-on-long-output`](scenarios/2026-06-05-streaming-timeout-on-long-output.md) | likely-general | streaming, timeout, max-tokens, backoff, 429 |
| [`eval-regression-shipped-silently`](scenarios/2026-06-05-eval-regression-shipped-silently.md) | likely-general | evals, regression, golden-set, llm-judge, model-migration |

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

## 11. Technical-runtime tier — SDK prerequisite, recommended-not-bundled MCP, LSP, and the cost estimator

This is a **code/AI** domain, so the plugin carries a runtime tier. Each item below is dispositioned against [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) and the marketplace value-add menu; the summary table is §12.

### 11.1 The SDK prerequisite

The agents recommend and emit code against the **Anthropic SDK** (`pip install anthropic` / `npm i @anthropic-ai/sdk`) and the **Claude Agent SDK** (`pip install claude-agent-sdk` / `npm i @anthropic-ai/claude-agent-sdk`), run by the developer with their own `ANTHROPIC_API_KEY` (or Bedrock/Vertex/Foundry creds). See [`knowledge/agent-sdk-and-managed-agents.md`](knowledge/agent-sdk-and-managed-agents.md). Default model `claude-opus-4-8`; adaptive thinking; pin the id; always set `max_tokens` (§3 #11). Model ids/prices/GA status live in the dated capability map, not baked into personas.

### 11.2 Recommended (not bundled) MCP servers — verified, no invented servers

This plugin **bundles no MCP server**, on purpose. Per [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**. Real research (2026-06-05) confirms nothing in the Claude/AI domain clears that bar:

| Candidate | Disposition | Why `[verify-at-use]` |
|---|---|---|
| **An Anthropic-hosted "Claude docs" MCP server** | **Does not exist (do not invent).** | The Claude API *Remote MCP servers* page states the listed servers are third-party, *"not owned, operated, or endorsed by Anthropic."* No first-party zero-auth docs MCP is published. Community ones (e.g. an `anthropic-docs-mcp` on directories) are unverified third-party — not bundleable, not recommended without a `security-reviewer` pass. |
| **`fetch` reference server** ([modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers), MIT, first-party, no-auth, read-only) | **Recommend-not-bundle.** | It's the closest fit (no auth, read-only web→markdown) but it fetches **arbitrary URLs** — a broad capability, not a narrow Claude-docs server — so it's a consumer **`claude mcp add`** choice gated through `security-reviewer` (untrusted-content / SSRF surface), not a default bundle. Package/runner is version-volatile (historically the Python `uvx mcp-server-fetch`; a web check 2026-06-05 reported an `npx @modelcontextprotocol/server-fetch` form) — confirm the exact package + runner before quoting. |
| **Postgres / DB / filesystem / git reference servers** | **Recommend-not-bundle** (same as backend-engineering). | Per-consumer path *and/or* write-capable *and/or* secret-handling (a DB connection string is a secret → reference, never literal). The Anthropic `@modelcontextprotocol/server-postgres` reference is **archived/deprecated** — do not recommend it. |

**Why none are bundled (load-bearing):** the doctrine's decision table routes "per-consumer config OR write-capable OR secret-handling OR arbitrary-fetch breadth" to **recommend, don't bundle**. If a genuinely zero-config, read-only, narrowly-scoped Claude-docs MCP appears, revisit with Step 4 of the doctrine. **No invented packages or model/version claims** appear here; every status is dated and re-verifiable.

> Verified 2026-06-05 against the [Claude API Remote-MCP-servers page](https://platform.claude.com/docs/en/agents-and-tools/remote-mcp-servers) (third-party disclaimer) and the [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) repo (reference-server set incl. `fetch`; the archived set incl. postgres). Package names, runner (`uvx`/`npx`), and archival status are volatile — re-confirm at use.

### 11.3 LSP code intelligence — bundled config, binary installed separately

This is a code domain, so the plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) giving agents real code intelligence over the example languages they emit (Python / TypeScript-JS — the two Anthropic-SDK languages most used in this plugin's snippets):

| Language | Server | `command` | Install (consumer, separate) |
|---|---|---|---|
| Python | Pyright | `pyright-langserver --stdio` | `pip install pyright` **or** `npm install -g pyright` |
| TypeScript/JS | typescript-language-server | `typescript-language-server --stdio` | `npm install -g typescript-language-server typescript` |

**The plugin ships the *config*, not the *binary*.** A missing server shows `Executable not found in $PATH` in the `/plugin` Errors tab and that one language degrades — everything else keeps working (loud-but-non-fatal). Go/Rust are omitted (this plugin's snippets are Python/TS); add them if a consumer's Claude integration is in another language. Package names + the `--stdio` invocation verified against the Claude Code plugins reference LSP table (2026-06-05); LSP support landed in Claude Code 2.0.74 `[verify-at-use]`.

### 11.4 Runnable script — the cost / context-budget estimator

[`scripts/claude_cost_estimator.py`](scripts/claude_cost_estimator.py) (stdlib-only, ruff-clean) removes arithmetic error from three recurring decisions, mirroring the §12 cost/caching trees: `cache` (prompt-cache break-even + cost over N requests), `budget` (does prefix + history + per-turn growth fit the context window, and for how many turns), `batch` (interactive vs Batch-API cost). It is a **calculator, not a data source** — the user supplies every token count and price; the dated default multipliers/discount are `[verify-at-use]` snapshots, not authoritative. Owned by `claude-app-ops-engineer` (FinOps) + `prompt-and-context-engineer` (caching/context-budget).

---

## 12. Value-add completeness (build-out 2026-06-05)

Disposition of every value-add menu item (built vs. recorded N-A with reason), mirroring the merged `backend-engineering`/`veterinary-practice` pattern. Pre-existing surfaces (6 agents, 7 skills, 5 commands, 13-doc knowledge bank, 30 best-practices, 6 templates, 1 advisory hook) came from PR #315 and earlier; this build-out adds the net-new gap.

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 5 scenarios (prompt-cache hit-rate collapse, tool-use runaway loop, RAG retrieval miss under 200K, streaming/timeout on long output, eval regression shipped silently) + `README.md` index on the marketplace 9-field schema. Replaces the §8a TODO; the four most-relevant agents check the bank via the scenario-retrieval skill. |
| 2 | **Decision-tree (Mermaid) knowledge** | **BUILT** — `knowledge/cost-and-caching-decision-trees.md`: (1) cache-hit-rate-collapse debug tree, (2) the cost-lever ladder. Chosen because the existing tree file already covers model-selection, retrieval-strategy (RAG-vs-long-context), capability-home, eval-gate, orchestration-shape (agent-vs-workflow), async-delivery, injection, and document-format — these two cost/caching diagnostics were the genuine gaps (not duplicates). |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §11.2. Real web research (2026-06-05): no first-party Anthropic Claude-docs MCP exists (the Remote-MCP page disclaims the listed servers as third-party); the MIT `fetch` reference server is the closest but fetches arbitrary URLs (breadth → `security-reviewer`-gated `claude mcp add`, not a bundle); DB/filesystem/git are per-tenant/write/secret. No invented servers. |
| 4 | **LSP server** | **BUILT** — `.lsp.json` (Pyright + typescript-language-server), wired via `plugin.json` `lspServers`. Useful for a code domain; the two Anthropic-SDK languages this plugin's snippets use. Binaries install separately (§11.3). |
| 5 | **Runnable script** | **BUILT** — `scripts/claude_cost_estimator.py` (`cache` / `budget` / `batch`), stdlib-only, ruff-clean, calculator-not-data-source. Real value: it's the arithmetic behind the cost-lever + cache-hit-rate trees. |
| 6 | **bin/ · monitors · output-styles · settings defaults · themes** | **N-A** — no groundable, broadly-valuable instance. The advisory hook (`check-claude-app-anti-patterns.sh`) + the skills already cover the in-loop surface; a `bin/` linter would duplicate the hook; the plugin is config-light by design and its deliverables are advisory snippets, not styled output. |
| 7 | **skills / hooks / commands / templates** | **Coverage sufficient** — 7 skills, 5 commands, 6 templates, 1 advisory hook already cover caching, routing, tool-schema design, eval golden-set building, context-budget planning, MCP authoring, and Agent-SDK hook design. No gap this round; the scenarios + 2 trees + script extend reach without a new agent (team-growth-as-knowledge house rule). |
| 8 | **CHANGELOG.md** | **BUILT** — top entry added for this build-out. No `NOTICE.md` (nothing third-party is bundled; the script is original stdlib-only, all sources cited inline). |

---

## 13. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Structured Output Protocol (upstream): [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- The prompt-engineer seam: [`../ravenclaude-core/agents/prompt-engineer.md`](../ravenclaude-core/agents/prompt-engineer.md)
- Build provenance: [`../../docs/claude-app-engineering-plugin-analysis.md`](../../docs/claude-app-engineering-plugin-analysis.md)
