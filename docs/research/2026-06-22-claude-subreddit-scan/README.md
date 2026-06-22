# Claude subreddit scan — research, panel decision & build plan (2026-06-22)

**Author:** `claude` (automated scheduled routine)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 5 findings surfaced → **1 approved**, 4 deferred/denied as already-covered or out-of-scope. The approved item shipped as a documented interaction in `ravenclaude-core/knowledge/subagent-isolation-and-tooling.md` (v0.158.0).

> This is the **fourth** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions three-tier posture (approved), skills-vs-subagents-vs-MCP, headless-CI cost guardrails, thinking budgets.
>
> Today's findings are deliberately disjoint from all three prior sets.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode and adjacent communities about using Claude Code effectively.

**Route note (honest — same as the 2026-06-11 run):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py), which pulls real subreddit listings via Reddit's official OAuth2 Data API. It `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars were unset this session** (verified — `${REDDIT_CLIENT_ID:-NO}` / `${REDDIT_CLIENT_SECRET:-NO}` both returned `NO`). So this run fell back to **unrestricted web search**, the documented fallback. The structural block (crawler-UA 403 on `reddit.com`) is solved by the script; the operational gap is still just the missing credentials.

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ the sanctioned route — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session |
| `WebSearch allowed_domains:[reddit.com]` | **400 — "domains not accessible to our user agent"** (Anthropic crawler-UA block) |
| `WebFetch` of aggregator articles (aitooldiscovery, smartscope, ofox, support.claude.com) | **403 Forbidden** (bot blocks) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion snippets + practitioner write-ups |

**Provenance of the findings below:** Reddit-discussion aggregations + practitioner write-ups via unrestricted web search, **cross-checked against primary Anthropic docs** for the one approved item. **Not** direct subreddit reads. **Next scan: set the two Reddit creds and run `reddit-scan.py` first** to close the provenance gap.

**Queries run (fallback route):**

- `ClaudeAI subreddit Claude Code best tips 2026 subagents hooks workflow`
- `Claude Code power user techniques reddit discussion 2026 CLAUDE.md context`
- `Claude Code reddit r/ClaudeAI CLAUDE.md tips context window compaction subagent gotchas 2026`
- `Claude Code skills plugins reddit community sharing 2026 marketplace useful agents`
- `Claude Code common mistakes pitfalls reddit r/ClaudeAI 2026 token cost context management`
- `CLAUDE_CODE_SUBAGENT_MODEL environment variable Claude Code default subagent model official docs`

**Primary source cross-checked for the approved item:** [Anthropic — Create custom subagents § "Choose a model"](https://code.claude.com/docs/en/sub-agents) (fetched + saved this session; the four-step resolution order quoted verbatim below).

---

## 2. Findings (5) and the grounded "already covered?" check

| # | Finding (community lesson) | Already in repo? (grounded check) | Decision |
| --- | --- | --- | --- |
| **F1** | **`CLAUDE_CODE_SUBAGENT_MODEL` is a session-global default-model lever for subagents, and it sits ABOVE the per-agent `model:` frontmatter.** Set it once → every un-pinned subagent runs on the cheaper backbone (main-on-Opus / subagents-on-Sonnet, the most-discussed multi-agent cost pattern). Default with nothing set is `inherit` (subagent = main model). | **Genuine gap.** [`knowledge/subagent-isolation-and-tooling.md`](../../../plugins/ravenclaude-core/knowledge/subagent-isolation-and-tooling.md) documents the per-agent `model:` **frontmatter** field but **not** the global env var, and **not** the four-step resolution order — so the load-bearing fact that the env var *overrides* the roster's `model:` pins is undocumented. `grep -r CLAUDE_CODE_SUBAGENT_MODEL` over the repo returned nothing this session. | ✅ **APPROVE** |
| **F2** | Subagents don't inherit parent skills → preload via the `skills:` frontmatter field. | **Already covered** — `subagent-isolation-and-tooling.md` field-set table: "`skills` — **Preload** named skills into the agent at dispatch." | ❌ deny (covered) |
| **F3** | The "March 2026 prompt-caching incident" caused 10–20× token inflation. | **Reject — unverifiable + out of core scope.** Single-aggregator claim, no primary source located; not actionable as a durable rule. Prompt caching is the `claude-app-engineering` plugin's domain, which already ships a `prompt-caching-playbook.md` + `cache-the-static-prefix.md`. | ❌ deny |
| **F4** | `claude-hud` plugin = live token/cost overlay. | **Reject — superseded + needs review.** Token visibility is already served by the Mímir session tab + `docs/token-budget-playbook.md`; recommending a third-party plugin would need a `security-reviewer` pass for marginal gain. | ❌ deny |
| **F5** | "Checkpoint before autonomous work; rollback instead of fix-forward — a fresh start beats wrestling a degraded session." | **Already covered.** The 2026-06-10 scan approved checkpoints/`/rewind`; context hygiene is covered extensively in the CLAUDE.md "Context & Session Hygiene" section and the failure-modes doc. | ❌ deny (covered) |

---

## 3. Panel / decision process

This routine ran unattended (no human watching), so the decision was made against the documented **approval criteria** rather than convening the live `claude -p` tribunal seats (which need a toggled-on category + interactive context). The criteria each finding was judged against:

1. **Verifiable against a primary source** (accuracy discipline — AGENTS.md "Accuracy discipline"). F1 alone is grounded in the official doc, fetched and quoted this session. F3 failed here.
2. **Genuinely absent from the repo** (grounded check, not memory). F2/F5 failed — already shipped. F1 passed (`grep` returned nothing).
3. **Domain-neutral + fits core** (house rule #1). F3/F4 are domain-plugin or external-tool territory.
4. **Durable, not a moving target.** F1 is a stable, documented resolution order; F3/F4 are incident/tool references that age fast.

**Concern noted on the approved item (F1):** the community aggregation claimed the env var "doesn't override built-in agents' hard-coded models." The official four-step order does not carve that out, so the addition states the four-step order as fact (grounded) and flags the built-in-agent nuance explicitly as `[unverified — community aggregation]` with a "verify at use" marker — rather than asserting or dropping it.

---

## 4. Build plan (approved item F1)

| What | Where | Dependency |
| --- | --- | --- |
| Document the `CLAUDE_CODE_SUBAGENT_MODEL` env var, the official four-step model-resolution order, the two practitioner cost levers, and **the gotcha that the env var overrides the roster's per-agent `model:` pins** | New `###` subsection in [`plugins/ravenclaude-core/knowledge/subagent-isolation-and-tooling.md`](../../../plugins/ravenclaude-core/knowledge/subagent-isolation-and-tooling.md), placed right after the "Implication for core's roster" paragraph it qualifies | none — single-file knowledge edit |
| Version bump (knowledge ships to consumers → user-visible) | `plugins/ravenclaude-core/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` mirror: `0.157.0 → 0.158.0` | CI fails on version drift between the two |
| CHANGELOG top entry | `plugins/ravenclaude-core/CHANGELOG.md` | none |

**Not touched:** no hook, script, agent, skill, gate, dashboard, or `.repo-layout.json` change. Additive prose only. **Migration:** none — nothing in a consumer's installed plugin behaves differently on `/plugin marketplace update`; the env var is a consumer-environment lever, now documented.

---

## 5. Sources

- [Anthropic — Create custom subagents](https://code.claude.com/docs/en/sub-agents) (primary — the four-step model resolution order; fetched + saved this session)
- Practitioner aggregations read via unrestricted web-search snippets (direct fetch 403'd): aitooldiscovery "Claude Code Reddit", morphllm "Claude Code Reddit", techtaek "context discipline 2026", buildtolaunch "Token Optimization", smartscope / ofox "hooks-subagents-skills 2026 guide".
