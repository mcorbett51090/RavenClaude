# Claude subreddit scan — research, panel decision & build plan (2026-06-25)

**Author:** `claude` (automated scheduled routine)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), 1 denied-as-duplicate, 2 deferred-as-covered. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.183.0).

> This is the **seventh** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions three-tier `deny`/`ask`/`allow` (approved), skills-vs-subagents-vs-MCP, headless-CI cost guardrails, thinking budgets.
> - [2026-06-13](../2026-06-13-claude-subreddit-scan/README.md) — git-worktrees for parallel Claude instances (approved) + a correction to the `subagent-isolation` premise.
> - [2026-06-15](../2026-06-15-claude-subreddit-scan/README.md) — scope-the-reviewer-to-correctness (approved), interview→SPEC, `claude -p` fan-out, `/clear`+`/btw` hygiene.
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — `CLAUDE_CODE_SUBAGENT_MODEL` resolution order (approved) + the MCP tool-context budget; CLAUDE.md memory hygiene (deferred).
> - [2026-06-24](../2026-06-24-claude-subreddit-scan/README.md) — SKILL.md progressive-disclosure body budget (approved); procedural-instructions-belong-in-skill (folded), model-tiering (denied dup), config-as-execution-vector (deferred).
>
> Today's net-new finding (G1) is disjoint from all six prior sets. It is the **umbrella** the repo's `definition-of-done-gate` / `expensive-test-front-loading` / `visual-feedback-loop` / `scope-the-reviewer` leaves all instantiate — the general "give the agent a readable verification signal" principle that no prior rule states.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode and adjacent communities about using Claude Code effectively.

**Route note (honest — unchanged from the prior three scans):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py), which pulls real subreddit listings via Reddit's official OAuth2 Data API. It `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars were unset this session** (verified — `${REDDIT_CLIENT_ID:-NO}` / `${REDDIT_CLIENT_SECRET:-NO}` both returned `NO`). So this run fell back to **unrestricted web search**, the documented fallback.

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ the sanctioned route — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session (re-verified) |
| `WebFetch https://www.reddit.com/...` + redlib/old.reddit mirrors | ❌ "unable to fetch from www.reddit.com" / `403` (Anthropic crawler-UA block — the structural block `reddit-scan.py` exists to route around) |
| `WebSearch allowed_domains:[reddit.com]` | ❌ **400 — "domains not accessible to our user agent"** (crawler-UA block) |
| `WebFetch` of aggregator articles (morphllm, aitooldiscovery) | ❌ `403 Forbidden` (bot blocks) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion aggregations + practitioner write-ups |
| `WebFetch` of the **primary Anthropic doc** (`code.claude.com/docs/en/best-practices`) | ✅ works — fetched + quoted this session for the approved item |

**Provenance of the findings below:** Reddit-discussion aggregations + practitioner write-ups via unrestricted web search, **cross-checked against the primary Anthropic best-practices doc** for the approved item (fetched and quoted this session). **Not** direct subreddit reads. **Standing next-scan action (carried for the fourth run): set the two Reddit creds and run `reddit-scan.py` first** to close the provenance gap.

**Queries run (fallback route — unrestricted web search):**

- `r/ClaudeAI Claude Code best practices tips 2026`
- `reddit ClaudeAI Claude Code most upvoted tips workflow June 2026`
- `Claude Code reddit subagent model Sonnet Opus CLAUDE_CODE_SUBAGENT_MODEL cost workflow`
- `Claude Code reddit /compact /memory context rot short sessions checkpoint commit`
- `Claude Code give verifiable check tests build screenshot self-correct iterate 2-3x quality Boris Cherny`
- `Claude Code subagent one-shot stateless cannot ask followup over-specify prompt return summary reddit`

**Primary source cross-checked for the approved item:** [Anthropic — Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) § "Give Claude a way to verify its work" (fetched + quoted this session; the four enforcement levels — in-prompt / `/goal` condition / Stop hook / second-opinion subagent — are reproduced verbatim in the analysis below).

---

## 2. Findings (4) and the grounded "already covered?" check

| # | Finding (community lesson) | Already in repo? (grounded check) | Decision |
| --- | --- | --- | --- |
| **G1** | **Give the agent a check it can read (tests / build exit code / linter / fixture-diff / screenshot) and it iterates to green on its own — "the feedback loop matters more than the prompt, by a wide margin."** The official doc leads with this and lists four enforcement levels (in-prompt → `/goal` condition → Stop hook → second-opinion subagent); Claude Code's creator estimates a 2–3× quality lift. | **Genuine gap — the *umbrella* is missing.** The repo ships every *leaf*: the **Stop-hook** instance ([`definition-of-done-gate-makes-done-mean-done.md`](../../../plugins/ravenclaude-core/best-practices/definition-of-done-gate-makes-done-mean-done.md)), the **cost** variant ([`expensive-test-front-loading.md`](../../../plugins/ravenclaude-core/best-practices/expensive-test-front-loading.md)), the **visual** instance ([`knowledge/visual-feedback-loop.md`](../../../plugins/ravenclaude-core/knowledge/visual-feedback-loop.md)), the **second-opinion** instance ([`scope-the-reviewer-to-correctness-or-it-manufactures-work.md`](../../../plugins/ravenclaude-core/best-practices/scope-the-reviewer-to-correctness-or-it-manufactures-work.md)) — but **no rule names the general principle** that *every* task should carry a readable verification signal and the agent should iterate to green before handing back. `grep` over `best-practices/` for the umbrella turned up only the four leaves. The doc's four enforcement levels map 1:1 onto them, which is exactly why the umbrella belongs as the See-also hub that ties them together. | ✅ **APPROVE** |
| **G2** | **`CLAUDE_CODE_SUBAGENT_MODEL` + planner-on-Opus/workers-on-cheaper model routing for cost** — subagent-heavy sessions can be ~85% of the token bill; audit the env var (`echo $CLAUDE_CODE_SUBAGENT_MODEL`), route the planner to Opus and workers to Sonnet/Haiku. | **Covered — duplicate.** The env var + four-step resolution order shipped in the [2026-06-22 scan](../2026-06-22-claude-subreddit-scan/README.md) → `knowledge/subagent-isolation-and-tooling.md`; model-tiering was a 06-09 finding; the marketplace ships a whole `ai-coding-model-guidance` plugin + the `model-selection` Learn concept. The 85%-of-bill figure is a volatile platform anecdote, not a durable rule. | ❌ deny (covered) |
| **G3** | **Proactive `/compact` at ~60% context (not at the 95% auto-trigger) with explicit preservation instructions; durable files survive, live context doesn't; `git log` is a free context source.** | **Covered.** Context-compaction was a 06-10 finding; the `/compact` 60%-rule + targeted directives were a [2026-06-20](../2026-06-20-claude-subreddit-scan/README.md) finding; `mcp-tool-context-is-a-budget` + `claude-md-imports-organize-they-dont-shrink-context` + the CLAUDE.md "Context & Session Hygiene" section + the checkpoints rule cover the durable-vs-live boundary. | ⏸️ defer (covered) |
| **G4** | **Subagents are one-shot/stateless per invocation and return only a summary — restate any rule that must reach the subagent in the delegation prompt ("ignore vendor/"), and design the handoff because the parent never sees the subagent's full context.** | **Covered.** [`focused-task-delegation-beats-full-context-dumps.md`](../../../plugins/ravenclaude-core/best-practices/focused-task-delegation-beats-full-context-dumps.md) (restate constraints, give the focused slice) + [`structured-output-protocol-for-all-agent-handoffs.md`](../../../plugins/ravenclaude-core/best-practices/structured-output-protocol-for-all-agent-handoffs.md) (the summary-back envelope) + `knowledge/subagent-isolation-and-tooling.md` already hold this. | ⏸️ defer (covered) |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — same rationale as every prior scan: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no *action* on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably.

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **G1** | ✅ **Approve** | Passes all four. **Additive:** the four enforcement leaves exist; the *umbrella principle* does not (grep-verified) — and the leaves are stronger *with* a named hub that tells an agent to always carry a verification signal and points to the right leaf. **In-scope:** verification discipline is core's home turf, and it's the one rule the official guide leads with — the least "generic" framing possible. **Load-bearing:** the trust-then-verify gap (plausible work handed back unverified) has a concrete, measurable cost; the doc's creator puts it at 2–3×. **Low-blast:** additive markdown. | Keep the community-attributed 2–3× figure marked `[verify-at-use]` and ground the principle itself in the primary doc (done). Frame it as the *umbrella*, cross-linked to all four leaves + the epistemic protocols, so it complements rather than duplicates them. Don't let it drift into restating the DoD-gate's *mechanism* — it owns the *principle*, the gate owns the *enforcement*. |
| **G2** | ❌ Deny | Fails #1 — duplicate. The env var + resolution order shipped 06-22; model-tiering shipped 06-09; the `ai-coding-model-guidance` plugin owns the depth. The 85%-of-bill figure is a volatile anecdote, not a durable rule. | None — cleanly covered. |
| **G3** | ⏸️ Defer | Fails #1 — covered across the 06-10 + 06-20 scans and four standing context-budget rules. The `git log`-as-context angle is mildly fresh but thin and already implied by the checkpoints/commit-discipline rules. | If a future scan finds a crisp, under-covered "read git history instead of re-deriving" angle that the existing rules genuinely miss, revisit standalone. |
| **G4** | ⏸️ Defer | Fails #1 — `focused-task-delegation` + `structured-output-protocol` + the subagent-isolation knowledge already hold the restate-constraints-in-the-prompt and summary-back-handoff lessons. | None — shipping it would near-duplicate two existing rules. Per the one-tight-rule-per-scan discipline, ship only the clearly net-new G1. |

---

## 4. Build plan (approved item G1)

| What | Where | Dependency |
| --- | --- | --- |
| New best-practice naming the umbrella verification-loop principle (construct a readable pass/fail signal; iterate to green; show evidence; pick the cheapest enforcement level), cross-linked to all four existing leaves + the epistemic protocols | New [`plugins/ravenclaude-core/best-practices/give-the-agent-a-verification-signal-it-can-read.md`](../../../plugins/ravenclaude-core/best-practices/give-the-agent-a-verification-signal-it-can-read.md) | none — single additive markdown file (matches `plugins/*/best-practices/**` allow-list glob, so no `.repo-layout.json` change) |
| Index row + count bump (24 → 25 rules) | [`plugins/ravenclaude-core/best-practices/README.md`](../../../plugins/ravenclaude-core/best-practices/README.md) | none |
| Version bump (best-practices ship to consumers → user-visible) | `plugins/ravenclaude-core/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` mirror: `0.182.0 → 0.183.0` | CI fails on version drift between the two |
| CHANGELOG top entry | `plugins/ravenclaude-core/CHANGELOG.md` | none |

**Not touched:** no hook, script, agent, skill, gate, dashboard, knowledge file, or `.repo-layout.json` change. Additive prose + an index row + version/CHANGELOG bookkeeping only. **Migration:** none — nothing in a consumer's installed plugin behaves differently on `/plugin marketplace update`; a new best-practice is inert until an agent reads it.

---

## 5. Sources

- [Anthropic — Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) (primary — § "Give Claude a way to verify its work" + the four enforcement levels; fetched + quoted this session)
- Practitioner aggregations read via unrestricted web-search snippets (direct fetch 403'd): morphllm "Claude Code Reddit", aitooldiscovery "Claude AI Reddit", builder.io "50 Claude Code Tips", smartscope "advanced best practices 2026", the-ai-corner "Claude best practices 2026", youcanbuildthings "subagents burn tokens", okhlopkov "/compact explained", vibecoder.me "verification beats prompting" (the most-cited Boris-Cherny workflow lesson).
