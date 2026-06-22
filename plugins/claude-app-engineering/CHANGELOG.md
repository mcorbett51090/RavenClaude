# Changelog — claude-app-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.9.2] — 2026-06-21

Research-sweep follow-on to the 2026-06-13 Fable 5 / Mythos 5 suspension (#426): closes the one consequence #426 left open in `knowledge/model-selection-and-2026-capability-map.md` — the **advisor-tool pairing**. The rule "Fable 5 → Fable 5 advisor; Mythos 5 → Mythos 5 advisor" is **unsatisfiable** while those models are suspended, so the advisor-tool row now directs an Opus 4.8 executor + Opus 4.8 advisor until access is restored. Re-dated 2026-06-21. Surfaced by Panel 2's detailed review of the sweep (the contradiction #426 didn't catch). No migration — knowledge-file content only.

## [0.9.1] — 2026-06-13

Research-sweep **correction** (Tier-A weekly news sweep) — **Fable 5 & Mythos 5 were suspended worldwide on 2026-06-12** under a US export-control directive; Anthropic disabled both for all customers across the Claude API, AWS Bedrock, GitHub Copilot, and Microsoft Foundry (disputing the rationale and stating it is working to restore access). Independently verified this session against the primary source [Anthropic statement](https://www.anthropic.com/news/fable-mythos-access) (corroborated by [Bloomberg](https://www.bloomberg.com/news/articles/2026-06-13/anthropic-says-us-limits-foreign-access-to-fable-5-mythos-5) + [CNBC](https://www.cnbc.com/2026/06/12/anthropic-disables-access-to-fable-5-and-mythos-5-to-comply-with-government-directive.html)). Routed through three expert panels (usefulness → USEFUL/unanimous; detailed review → APPROVE-WITH-FIX; the framing fixes — *current-status/disputed not deprecation*, named secondaries, `[verify-at-use]` markers — are applied).

### Fixed

- **`knowledge/model-selection-and-2026-capability-map.md`** — the file's central routing recommendation ("route the hard long-horizon autonomous tail to Fable 5") now points at a **currently-uncallable** model. Added a suspension banner; annotated the Fable 5 lineup row, the Mythos 5 note, the routing-ladder sentence, and the capability-status row to mark **SUSPENDED 2026-06-12** and re-route to **Opus 4.8** until restored. Framed as a fluid/disputed *current-status* fact (re-verify before quoting), **not** a deprecation. Opus 4.8 / Sonnet 4.6 / Haiku 4.5 unaffected.
- Version **0.9.0 → 0.9.1** in `.claude-plugin/plugin.json` **and** `marketplace.json` (lockstep).

## [0.9.0] — 2026-06-12

Research-sweep addition — documents Anthropic's new server-side **advisor tool** (beta `advisor-tool-2026-03-01`), a genuine zero-coverage gap in the knowledge bank. Verified 2026-06-12 against the primary [Advisor tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool) (corroborated by the [advisor-strategy blog](https://claude.com/blog/the-advisor-strategy) + SDK code samples). Routed through two expert panels (usefulness → USEFUL/high; detailed review → APPROVE-WITH-CHANGES/high; the required error-enumeration and version-lockstep changes are applied below); panels concurred so no tiebreak was needed. Provenance: [`docs/research/2026-06-12-advisor-tool-finding.md`](../../docs/research/2026-06-12-advisor-tool-finding.md).

### Added

- **`knowledge/server-side-tools-and-files.md`** — new **Advisor tool** section: a faster/cheaper **executor** model consults a higher-intelligence **advisor** model mid-generation inside one `/v1/messages` request (no client round-trips; server forwards the full transcript). Framed as a **routing-ladder/FinOps play** (house opinion #3): Sonnet-exec+Opus-advisor for a quality lift at similar/lower cost vs Opus-solo; Haiku-exec+Opus-advisor for a step up. Documents the cost/control levers (`max_tokens` min 1024, recommended 2048; `max_uses` per-request; `caching` break-even ~3 calls; advisor billed separately in `usage.iterations[]`), the full six-code error model (failures return *inside* the result block — the request does not fail), `stop_reason: "pause_turn"` on a dangling call, and the **Claude API + Claude Platform on AWS only** restriction (NOT Bedrock/Vertex/Foundry).
- **`knowledge/model-selection-and-2026-capability-map.md`** — added an **Advisor tool** capability-status row carrying the dated `[verify-at-use 2026-06-12]` pairing matrix (advisor must be ≥ executor) + platform restriction, per house opinion #14 (volatile model-pair facts live in the one dated freshness anchor, not duplicated in the knowledge doc).

### Changed

- Version **0.8.0 → 0.9.0** (minor — net-new capability) bumped in `.claude-plugin/plugin.json` **and** the `marketplace.json` catalog entry in lockstep (CI fails on drift); the catalog server-tools list now names the advisor tool.

## [0.8.0] — 2026-06-11

Research-sweep refresh — two net-new, primary-source-verified Claude-platform facts added to the knowledge bank, plus the Foundry Fable 5 caveat sharpened. Verified 2026-06-11 against [Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback), the [Classifier fallback and billing for Claude Fable 5 cookbook](https://platform.claude.com/cookbook/fable-5-fallback-billing-guide), [Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview) + [What's new in Claude Managed Agents](https://claude.com/blog/whats-new-in-claude-managed-agents), and the `learn.microsoft.com` Foundry model table (via the Microsoft-Learn MCP).

### Added

- **`knowledge/model-selection-and-2026-capability-map.md`** — expanded the Fable 5 row's **safety-fallback note into FinOps + reliability mechanics**: a refusal is an **HTTP 200 with `stop_reason: "refusal"`**; **no charge when the refusal precedes any output** (token counts informational, no rate-limit hit), but a **mid-stream refusal bills input + already-streamed output**. Documented Anthropic's **server-side classifier fallback** (up to 3 fallback models, run in-chain on the same request; at launch the only permitted target is Opus 4.8; fallback credit refunds the prompt-cache switch cost; per-agent — only the refused agent moves). Complements the existing "design around the discontinuity" note.
- **`knowledge/agent-sdk-and-managed-agents.md`** — added **Managed Agents scheduled/cron deployments + vault env-var credentials** (public beta, announced 2026-06-09): a cron schedule starts a fresh session per fire with no scheduler to host (nightly sync / weekly scan / daily digest); vaults now inject env-var secrets into the sandbox for authenticated CLIs/SDKs.

### Changed

- **`knowledge/model-selection-and-2026-capability-map.md`** — **sharpened** the Foundry Fable 5 caveat in both the lineup row and the capability-status row (prior "lists only the gated `claude-mythos-preview`" was imprecise — Opus/Sonnet/Haiku previews are listed too); restated as "Learn table lists Opus/Sonnet/Haiku previews + gated `claude-mythos-preview` but does **not** list `claude-fable-5`," **re-verified 2026-06-11** via Microsoft-Learn. Re-dated `Last reviewed` 2026-06-10 → 2026-06-11 and added the new sources to the header.
- Version **0.7.3 → 0.8.0** (minor — net-new knowledge) bumped in `.claude-plugin/plugin.json` **and** the `marketplace.json` catalog entry in lockstep (CI fails on drift).

## [0.7.3] — 2026-06-10

Freshness-anchor follow-up — codified the **403 route ladder** so a bot-blocked primary source becomes a re-route, not a miss (the lesson from the Fable 5 sweep, where `anthropic.com` + the GitHub changelog 403'd automated `WebFetch`).

### Changed

- **`knowledge/model-selection-and-2026-capability-map.md`** "How to keep this current" — on a `WebFetch` 403, route through [`webfetch-hardening`](../ravenclaude-core/skills/webfetch-hardening/SKILL.md) § "the 403 / refusal route ladder": `WebSearch` (reads the blocked content) → domain MCP (Microsoft-Learn / GitHub) → a non-blocked host → secondaries last; noted Wayback + UA/header spoofing are unavailable in this harness.
- **Softened the Fable 5 Microsoft Foundry claim** (both the lineup row and the capability-status row): Foundry is **announced** via the Azure blog, but the authoritative Foundry Learn model table still lists only the gated `claude-mythos-preview` as of 2026-06-10 — re-verify. (Surfaced by reading the Foundry docs via the Microsoft-Learn MCP, the route ladder in action.)
- Version **0.7.2 → 0.7.3** bumped in `.claude-plugin/plugin.json` **and** the `marketplace.json` catalog entry in lockstep.

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
