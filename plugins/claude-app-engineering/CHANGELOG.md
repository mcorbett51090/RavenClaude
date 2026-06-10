# Changelog — claude-app-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.7.2] — 2026-06-10

Freshness-anchor refresh — **Claude Fable 5** (`claude-fable-5`), Anthropic's first public **Mythos-class** model, went **GA 2026-06-09** (the day of the prior 0.7.1 review — a same-day miss caught on the next sweep). Sources: [Claude Fable 5 and Claude Mythos 5](https://www.anthropic.com/news/claude-fable-5-mythos-5), [Fable 5 on AWS](https://aws.amazon.com/blogs/aws/anthropic-claude-fable-5-on-aws-mythos-class-capabilities-with-built-in-safeguards-now-available/), [Fable 5 in Microsoft Foundry](https://azure.microsoft.com/en-us/blog/claude-fable-5-is-now-available-in-microsoft-foundry-powering-the-next-era-of-autonomous-agents/) (GA 2026-06-09; retrieved 2026-06-10). Anthropic's news page 403s automated fetch — facts cross-referenced across secondaries (CNBC, TechCrunch, AWS/Azure blogs, dev guides), the repo's accepted "primary 403 → cross-reference" pattern.

### Changed

- **`knowledge/model-selection-and-2026-capability-map.md`** (the anchor) — added **Fable 5** as the top lineup row: GA 2026-06-09, 1M context / 128K max output, **$10/$50 per Mtok (exactly 2× Opus 4.8)**, 90% prompt-cache discount, safety-fallback to Opus 4.8 on cyber/bio/chem (~<5% of sessions) framed as a behavioral discontinuity, AWS Bedrock + Microsoft Foundry availability. Soft/single-source benchmark claims (SOTA-on-nearly-all, >10%-over-Opus, SWE-bench ~80.3%) carry `[verify-at-use — single-source]` markers. **Fable 5 is the capability flagship but NOT the recommended default** — Opus 4.8 stays the cost-sane Opus-tier default (2× cost + the safety-fallback); the right-size ladder reserves Fable 5 for the genuinely hard long-horizon autonomous tail. Re-cast the Opus 4.8 row from "current flagship" to "recommended default + Fable-5 safety-fallback target". Added a capability-status row for Fable 5/Mythos 5 GA. Named **Mythos 5** (safeguards-lifted sibling) for completeness only — explicitly not a default. Re-dated `Last reviewed` 2026-06-09 → 2026-06-10.
- Version **0.7.1 → 0.7.2** bumped in `.claude-plugin/plugin.json` **and** the `marketplace.json` catalog entry in lockstep (CI fails on drift).

## [0.7.1] — 2026-06-09

Freshness-anchor refresh — **Claude Opus 4.8** (`claude-opus-4-8`) is now the current flagship, superseding Opus 4.7. Sources: [Introducing Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8) + [What's new in Opus 4.8](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-8) (GA 2026-05-28; retrieved 2026-06-09).

### Changed

- **`knowledge/model-selection-and-2026-capability-map.md`** (the anchor) — added Opus 4.8 as the flagship row (GA 2026-05-28, 1M context, $5/$25 per Mtok in/out, fast mode $10/$50, per-response reasoning-effort control, fixes 4.7's comment-verbosity + tool-call-skipping); relabelled Opus 4.7 "prior flagship"; added the 1M-context row's 4.8 entry, a **Dynamic Workflows (research preview)** row, and a **reasoning-effort control** row; re-dated `Last reviewed` 2026-05-28 → 2026-06-09 with the Opus 4.8 sources.
- Corrected every reference that asserted **Opus 4.7 as the _current_ flagship/frontier** to **Opus 4.8** (Panel-3 ruling: fix flagship-asserting refs, leave incidental "1M-context list"/dated-example mentions): `knowledge/claude-app-decision-trees.md` (top leaf + rationale + tradeoff row), `best-practices/right-size-with-a-routing-ladder.md` (prose + the `claude-opus-4-8` code pin), `best-practices/pin-the-model-id.md` (`"frontier"` config id), `templates/claude-app-architecture-spec.md` (routing-ladder example), `agents/claude-solution-architect.md` (description), `hooks/check-claude-app-anti-patterns.sh` (retired-model warning text), and the plugin/marketplace descriptions.



Value-add build-out — closing the net-new gap against the full value-add menu (the repeatable plugin-enrichment recipe, mirroring `backend-engineering` 0.3.0 and `veterinary-practice` 0.2.0). Every menu item is dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)".

> Recommended version: **0.7.0** (minor — net-new user-visible surfaces, no breaking change). Bump `.claude-plugin/plugin.json` **and** the `marketplace.json` catalog entry in lockstep (CI fails on drift); this CHANGELOG entry is pre-staged for that bump.

### Added

- **scenarios/ bank (5 field notes) + README.** `prompt-cache-hit-rate-collapse` (zero `cache_read_input_tokens` = a silent prefix invalidator, not "caching broken"), `tool-use-runaway-loop` (a deterministic iteration cap + idempotent effects, not a prompt, are the termination guarantee), `rag-retrieval-miss-under-200k` (eval the retriever separately; under ~200K prefer long-context over a pipeline), `streaming-timeout-on-long-output` (stream long/high-`max_tokens` work; back off `429`s with jitter), `eval-regression-shipped-silently` (golden set + CI gate; split model migrations into their own eval event). Marketplace 9-field schema; retires the §8a TODO and wires the four most-relevant agents to the bank.
- **Decision-tree knowledge.** `knowledge/cost-and-caching-decision-trees.md` — two Mermaid trees: (1) cache-hit-rate-collapse debug tree, (2) the cost-lever ladder (caching → routing → batch → right-size, in order). Fills the cost/caching-diagnostic gaps the existing tree file left.
- **LSP code-intelligence config.** `.lsp.json` (referenced from `plugin.json` `lspServers`) configuring Pyright (Python) + typescript-language-server (TS/JS) — the two Anthropic-SDK languages this plugin's snippets use. Ships the config, not the binary (loud-but-non-fatal if missing).
- **Runnable script.** `scripts/claude_cost_estimator.py` — stdlib-only, ruff-clean: `cache` (prompt-cache break-even), `budget` (context-window budget across multi-turn growth), `batch` (interactive vs Batch-API cost). A calculator, not a data source; dated default multipliers are `[verify-at-use]`.
- **CLAUDE.md** §8a (scenarios bank live), §8 knowledge-table row for the new trees, §11 (runtime tier — SDK prerequisite + recommend-not-bundle MCP + LSP + the cost estimator), and the §12 value-add completeness disposition table.

### Decisions (recorded, not built)

- **No bundled MCP server.** Real web research (2026-06-05): no first-party Anthropic Claude-docs MCP exists (the Claude API Remote-MCP page disclaims the listed servers as third-party, *"not owned, operated, or endorsed by Anthropic"*); the MIT `fetch` reference server is the closest zero-auth/read-only fit but fetches **arbitrary URLs** (breadth → a `security-reviewer`-gated `claude mcp add`, not a bundle); DB/filesystem/git are per-tenant/write/secret-handling and the Anthropic postgres reference is archived. Documented the recommend-not-bundle disposition. **No invented servers/packages/versions.**
- **No `bin/`, monitors, output-styles, settings defaults, or themes** — none cleared the "groundable + broadly valuable, doesn't duplicate the advisory hook or a neighbouring plugin" bar.
- **Skills/commands/templates coverage held sufficient** — 7 skills, 5 commands, 6 templates, 1 advisory hook already cover the surface; the scenarios + 2 trees + script extend reach without a new agent (team-growth-as-knowledge house rule).

### Verify-at-use

- The `fetch` MCP package name + runner (`uvx` vs `npx`), the MCP reference-server set + the postgres-reference archival, and the absence of a first-party Claude-docs MCP — all dated 2026-06-05, re-confirm against the vendor.
- LSP support landed in Claude Code 2.0.74; re-confirm the version + the `pyright`/`typescript-language-server` install paths.
- The cost estimator's default cache write/read multipliers (~1.25×/2× write, ~0.1× read) + the ~50% Batch discount are dated snapshots in the script, not authoritative — confirm against current Anthropic pricing.

## [0.2.0] — 2026-05-28

Knowledge-bank expansion (9 → 13 docs) — a wide-net gap scan surfaced four missing surfaces, each researched and fleshed out:

- `retrieval-and-rag-2026.md` — the RAG-vs-long-context-vs-Files decision (skip RAG under ~200K tokens + caching), Anthropic **Contextual Retrieval** (contextual embeddings + contextual BM25 + RRF + reranking; 49%/67% fewer failed retrievals), Voyage embeddings, chunking, agentic RAG.
- `prompt-engineering-techniques.md` — the quality craft (the leverage ladder: clear+direct → multishot → CoT/thinking → XML → role/system → prefill → chaining), output control, hallucination reduction, the prompt→eval loop. Distinct from the caching (cost) doc and core/prompt-engineer (artifacts).
- `agent-orchestration-patterns.md` — workflows vs agents + the five Anthropic patterns (prompt chaining / routing / parallelization / orchestrator-workers / evaluator-optimizer), Agent Skills as the shared standard, start-simple discipline. RavenClaude is the worked orchestrator-worker example.
- `context-engineering-2026.md` — curating the right tokens in a 1M window: caching layout, retrieve-vs-hold, ordering, context editing/compaction, the memory tool, sub-agent context isolation.

Wired into CLAUDE.md §8. Grounded in Anthropic docs + "Building effective agents" + Contextual Retrieval (retrieved 2026-05-28), dated freshness anchors.

## [0.1.0] — 2026-05-28

Initial release. A Claude app-engineering specialist team built from a researched, expert-reviewed plan (see [`docs/claude-app-engineering-plugin-analysis.md`](../../docs/claude-app-engineering-plugin-analysis.md)).

- **6 agents:** `claude-solution-architect`, `prompt-and-context-engineer`, `mcp-and-server-tools-engineer`, `agent-sdk-engineer`, `eval-engineer`, `claude-app-ops-engineer`.
- **9-doc knowledge bank** (citation-grounded, retrieval-dated 2026-05-28): build-surface decision tree, model-selection + dated 2026 capability map, prompt-caching playbook, tool-use + structured output, MCP server authoring, server-side tools + Files API, Agent SDK + Managed Agents, evals + quality, and FinOps + reliability + security.
- **6 templates:** architecture spec, prompt-and-caching design, MCP server spec, eval plan, cost model, Agent SDK runbook.
- **1 advisory hook** (`check-claude-app-anti-patterns.sh`, `CLAUDE_APP_STRICT=1` to block): hardcoded `sk-ant-` key, `messages.create` with no `max_tokens`, retired model id, full-message logging.
- **14 house opinions.** Seams: prompt-as-artifact → `ravenclaude-core/prompt-engineer`; AI-app security → `ravenclaude-core/security-reviewer`; whole-system architecture → `ravenclaude-core/architect` (a reciprocal prior was added to `core/prompt-engineer.md`).
- Requires `ravenclaude-core@>=0.7.0`. No bundled MCP — documents the Anthropic SDK / Claude Agent SDK prerequisite.

### Built per the round-2 expert review
- Promoted in-app tool-use design into `prompt-and-context-engineer`; made `mcp-and-server-tools-engineer` the MCP + hosted-server-tools owner; added the `server-side-tools-and-files.md` doc; operationalized cache-invalidation churn; made the prompt-engineer seam binding CLAUDE.md text.

### Deferred to a later version
- A `skills/` directory (procedures promoted from `/wrap` feedback) and a `scenarios/` bank (first real engagement scenario).
- Evaluate bundling a Claude/Anthropic MCP server if a stable community one emerges.
