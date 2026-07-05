# Claude subreddit scan — research, panel decision & build plan (2026-07-05)

**Author:** `claude` (automated scheduled routine)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), 3 denied-as-covered. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.185.0).

> This is the **12th** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions three-tier `deny`/`ask`/`allow` (approved), skills-vs-subagents-vs-MCP, headless-CI cost guardrails, thinking budgets.
> - [2026-06-13](../2026-06-13-claude-subreddit-scan/README.md) — git-worktrees for parallel Claude instances (approved) + a correction to the `subagent-isolation` premise.
> - [2026-06-15](../2026-06-15-claude-subreddit-scan/README.md) — scope-the-reviewer-to-correctness (approved), interview→SPEC, `claude -p` fan-out, `/clear`+`/btw` hygiene.
> - [2026-06-19](../2026-06-19-claude-subreddit-scan/README.md) · [2026-06-20](../2026-06-20-claude-subreddit-scan/README.md) · [2026-06-21](../2026-06-21-claude-subreddit-scan/README.md).
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — `CLAUDE_CODE_SUBAGENT_MODEL` resolution order + the MCP tool-context budget (approved).
> - [2026-06-24](../2026-06-24-claude-subreddit-scan/README.md) — SKILL.md progressive-disclosure body budget (approved).
> - [2026-07-02](../2026-07-02-claude-subreddit-scan/README.md) — the Bash-sandbox rule (approved → v0.183.0) + [the verification-loop umbrella](../2026-07-02-claude-subreddit-scan-verification-loop/README.md) (approved → v0.184.4). **H2 of the 07-02 scan — proactive context compaction — was explicitly deferred as "the strongest next candidate."**
>
> **This run's net-new finding (H1) is that deferred 07-02 H2, now picked up.** It is disjoint from every shipped rule: the repo's context-budget rules (`mcp-tool-context-is-a-budget`, `claude-md-imports-organize-they-dont-shrink-context`) govern context *cost*; no rule states the *compaction discipline itself* (proactive-not-reactive; persist-before-compact because reasoning is discarded).

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode and adjacent communities about using Claude Code effectively.

**Route note (honest — unchanged from every prior scan).** The sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py), which pulls real subreddit listings via Reddit's official OAuth2 Data API. It `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars were unset this session** (verified — `os.environ` check returned `UNSET` for both). This session also re-confirmed that **every direct Reddit route is blocked** for the Anthropic crawler here, trying five distinct paths before falling back:

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset (re-verified this session) |
| `WebSearch allowed_domains:[reddit.com]` | ❌ 400 — "domains not accessible to our user agent" |
| `WebFetch www.reddit.com/....json` (top/week, top/month, subreddit `.json`) | ❌ "unable to fetch from www.reddit.com" |
| `WebFetch old.reddit.com/....json` | ❌ "unable to fetch from old.reddit.com" |
| `WebFetch` redlib / safereddit mirrors | ❌ 403 Forbidden |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion aggregations + practitioner write-ups + primary Anthropic docs |

**Provenance of the findings below:** drawn from Reddit-discussion aggregations + practitioner context-management write-ups via unrestricted web search, cross-checked against **primary Anthropic docs** and **this repo's own surface** — **not** from direct subreddit reads. This is the documented fallback, **not** the preferred route. **Standing next-scan action (carried again, now the ~10th time): set the two Reddit creds and run `reddit-scan.py` first** so findings come from real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `r/ClaudeAI Claude Code hooks subagents workflow tips 2026`
- `reddit ClaudeAI Claude Code plugins skills best practices recent`
- `Claude Code compact context proactively before degrades persist state to file microcompact 2026`
- `Claude Code subagent does not inherit skills CLAUDE.md context must preload reddit lesson`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Manage costs effectively](https://code.claude.com/docs/en/costs) (primary — auto-compaction summarizes near the limit; `/compact <instructions>`; the `# Compact instructions` CLAUDE.md block; `/clear`, subagent-delegation, CLAUDE.md→skills, plan-mode to keep the window small), fetched this session.
- This repo's own [`plugins/ravenclaude-core/knowledge/concepts/context-window.md`](../../../plugins/ravenclaude-core/knowledge/concepts/context-window.md) (the mechanism: a finite window that fills and then compacts to a summary → durable facts belong in files).
- Practitioner aggregations (read via search snippets; several Reddit-sourced): MindStudio ("/compact command to prevent context rot", "context compounding"), CryptoFlex ("smart compact — preserve context before compaction"), SitePoint (long-running-session context management), Steve Kinney ("Compacting Claude Code sessions"), knightli / claudefa.st (usage limits + context-recovery hooks). The **proactive-at-~60%** heuristic and the **persist-before-compact** framing are the community consensus these aggregate.
- Also surfaced but denied-as-covered: ofox.ai / SmartScope "hooks/subagents/skills complete guide" and artificialcorner "33 Claude Code skills" (subagent-skill-inheritance, skill/hook/subagent selection, plan-interview).

---

## 2. Findings (4 — all checked against the 26-rule core set + the 11 prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Compact context proactively — before quality degrades (a widely-cited heuristic is ~60% utilization), not at the auto-trigger limit — and persist load-bearing state to a file *before* compaction, because `/compact` discards intermediate reasoning** (rejected approaches, distilled tool output, un-written-down decisions). Auto-compaction fires when the window is already near-full, so the model has been reasoning in a degraded window *and* the summary is written under that same pressure. Tell `/compact` what to keep (inline or a `# Compact instructions` CLAUDE.md block). | **Genuine gap (consumer-facing) — and pre-vetted.** The 2026-07-02 scan flagged this exact finding (its H2) as "**the strongest next candidate**" and deferred it only under the one-rule-per-scan discipline. Re-verified still-uncovered this session: `grep` of `best-practices/` for `compact`/`compaction` hits only `mcp-tool-context-is-a-budget` + `claude-md-imports` (context *cost*, not compaction discipline); `git log` since 07-02 shows no compaction rule shipped. `knowledge/concepts/context-window.md` states the *mechanism* ("after compaction the older work is a summary → durable facts belong in files") but **no best-practice teaches the discipline** (proactive-not-reactive; persist-before-compact). |
| **H2** | **A subagent starts with a clean context — it does NOT inherit the parent's skills/CLAUDE.md reasoning; preload the conventions it must follow into its definition or its spawn prompt**, and scope each subagent's tools tightly (a research agent gets read-only + web; a writer gets Edit + Bash, no network). | **Covered.** [`knowledge/subagent-isolation-and-tooling.md:61`](../../../plugins/ravenclaude-core/knowledge/subagent-isolation-and-tooling.md) documents the `skills` frontmatter field as the **preload** mechanism and the exact per-agent writable declarative surface; [`knowledge/dynamic-workflows.md:78,103`](../../../plugins/ravenclaude-core/knowledge/dynamic-workflows.md) states "permissions are inherited at spawn" + the clean-context model; the consumer-facing [`focused-task-delegation-beats-full-context-dumps.md`](../../../plugins/ravenclaude-core/best-practices/focused-task-delegation-beats-full-context-dumps.md) + [`structured-output-protocol-for-all-agent-handoffs.md`](../../../plugins/ravenclaude-core/best-practices/structured-output-protocol-for-all-agent-handoffs.md) own the task-scoped-brief discipline. Deny — duplicate. |
| **H3** | **Pick the right primitive: "a Skill teaches the *how*, a Hook enforces the *rule*, a Subagent isolates the *work*."** Start with skills (cheapest), add hooks for deterministic enforcement, reach for subagents when parallelism/context-isolation matters. | **Covered.** [`knowledge/orchestration-decision-trees.md`](../../../plugins/ravenclaude-core/knowledge/orchestration-decision-trees.md) carries the skill-vs-agent tree; [`knowledge/dynamic-workflows.md`](../../../plugins/ravenclaude-core/knowledge/dynamic-workflows.md) § "Choosing an orchestration shape" owns the subagent/skill/agent-team/workflow selection with a tradeoffs table; [`prefer-a-deterministic-gate-over-a-prose-rule.md`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md) owns "hook enforces the rule." The crisp three-way aphorism is nice packaging but the *content* is fully shipped; a 06-11-scan finding ("skills-vs-subagents-vs-MCP") already covered the same ground. Deny — duplicate. |
| **H4** | **Interview-before-code: have Claude ask thorough clarifying questions (a popular skill asks 16–50 depending on complexity) and work through decision branches before writing any code**, because most mistakes come from Claude guessing intent. | **Covered.** The 2026-06-15 scan's approved thread already covered **interview→SPEC**; the plugin ships the **plan-mode default** (root `CLAUDE.md` "Plan-mode default" — Keep/Update/Deny before writing on non-trivial changes) and [`skills/spec-reread-ritual`](../../../plugins/ravenclaude-core/skills/spec-reread-ritual/SKILL.md) / [`skills/two-panel-plan-review`](../../../plugins/ravenclaude-core/skills/two-panel-plan-review/SKILL.md). Deny — duplicate. |

---

## 3. Panel decision (the tribunal / decision process)

The recurring scan routes each finding's yes/no "does this earn a repo change?" through the same rule-derivable criteria the decision-review tribunal applies. `.ravenclaude/comfort-posture.yaml` `decision_review` is **off by default** in this environment (verified — no live `claude -p` seat panel convened), so per the documented fallback the process is applied **as a documented rubric** here, not a live seat vote. The rubric (unchanged across scans):

**Approval criteria (all four must hold):**
1. **Net-new** — not already stated by a shipped best-practice, knowledge file, or CLAUDE.md milestone (grounded `grep`/read check, cited).
2. **Consumer-facing** — teaches a consumer of `ravenclaude-core` something actionable, not marketplace-internal trivia.
3. **Grounded** — anchorable to a primary Anthropic doc (or this repo's own verified surface), not just a community claim.
4. **One-tight-rule discipline** — at most one net-new best-practice per scan (avoids rule-sprawl; the strongest single candidate ships, the rest defer).

| # | Verdict | Reasoning | Concerns / caveats |
| --- | --- | --- | --- |
| **H1** | ✅ **APPROVE → ship as a best-practice** | Passes all four. **Net-new** (grep + git-log verified uncovered; the 07-02 scan pre-classified it net-new and deferred it only for rule-discipline). **Consumer-facing** (every long session hits it). **Grounded** (Anthropic Manage-costs doc + this repo's context-window concept card, both read this session). **One-tight-rule** (it *is* the single strongest candidate — the other three are duplicates). | The **~60% utilization** figure is a community heuristic, **not** an Anthropic-published threshold — written into the rule explicitly as a rule of thumb + an edge-case warning against wiring a hard 60% trigger. Provenance is a fallback web-search read, not a direct subreddit read (stated in the rule's Provenance block). |
| **H2** | ❌ **DENY — covered** | Fails criterion 1. The clean-context/preload lesson is documented in two knowledge files (the `skills` preload field + "inherited at spawn"), and the consumer-facing discipline is owned by `focused-task-delegation` + `structured-output-protocol`. | Not a defect that it's "only" in knowledge — subagent authoring is where consumers meet it, and it's covered there. |
| **H3** | ❌ **DENY — covered** | Fails criterion 1. The skill/hook/subagent selection content is fully shipped across `orchestration-decision-trees.md`, `dynamic-workflows.md` § "Choosing an orchestration shape", and `prefer-a-deterministic-gate`. | The aphorism is good packaging; if it ever earns a place it's a one-line addition to the existing tree's intro, not a new rule. |
| **H4** | ❌ **DENY — covered** | Fails criterion 1. Interview→SPEC was an approved 06-15 thread; plan-mode default + `spec-reread-ritual` + `two-panel-plan-review` own it. | — |

**Net:** 1 approved (H1), 3 denied-as-covered. Consistent with the scan's steady-state: the core rule-set is mature, so most community "tips" now land as *already-covered*, and the marginal net-new item is increasingly a **deferred prior-scan candidate** being picked up (here, 07-02's H2).

---

## 4. Build plan (for the approved item, H1)

**What ships (all additive; no load-bearing file touched):**

1. **New best-practice rule** — [`plugins/ravenclaude-core/best-practices/compact-context-proactively-and-persist-state-before-it-is-discarded.md`](../../../plugins/ravenclaude-core/best-practices/compact-context-proactively-and-persist-state-before-it-is-discarded.md). Status **Pattern**. Sections: Why-this-exists (the double-degradation of late auto-compaction) · How-to-apply (compact on your schedule; tell `/compact` what to keep; **persist load-bearing state to a file first**; keep the desk clear with `/clear`/subagent-delegation) · Edge-cases (short sessions exempt; ~60% is a heuristic not a gate; `/compact` ≠ `/clear` ≠ `/rewind`; non-Claude-Code hosts) · See-also (5 sibling rules) · Provenance (Anthropic Manage-costs + context-window concept card + the community heuristic, honestly attributed to the fallback route) · Last-reviewed stamp.
2. **README index** — [`best-practices/README.md`](../../../plugins/ravenclaude-core/best-practices/README.md): `_26 rules._` → `_27 rules._`, one new index row.
3. **Version bump** — `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json`: `0.184.4` → **`0.185.0`** (minor: a new consumer-visible best-practice). CI fails on version drift between the two mirrors, so both move together.
4. **CHANGELOG** — top entry `0.185.0 — 2026-07-05` (the plugin ships a `CHANGELOG.md`; convention = keep the top entry current on every bump).
5. **This research doc** — `docs/research/2026-07-05-claude-subreddit-scan/README.md`.

**Where it fits in the repo structure.** A best-practice rule is a consumer-facing markdown file the `ravenclaude-core` agents surface + cite whole; it sits alongside the other 26 under `plugins/ravenclaude-core/best-practices/`. No new directory, so **no `.repo-layout.json` glob change** is needed (`plugins/*/best-practices/*.md` is already allowed). It cross-links to the existing `context-window` concept card and four sibling context/recovery rules; it does not modify any of them.

**Dependencies / ordering.** None blocking — additive markdown + two version-string edits. The pre-push checklist (per `AGENTS.md` § Testing): JSON validity on both manifests, `prettier --write .` (the new `.md` is excluded from prettier but the run keeps the tree clean), and the layout allow-list check (no new path). `docs/` changes commit straight to `main` per the docs-only rule, but they ride **in** this PR because the same PR carries the plugin change they document (cleaner provenance than a split).

**Migration:** none — additive consumer-facing markdown; nothing in a consumer's installed plugin changes on `/plugin marketplace update` beyond one new best-practice appearing in the index.

---

## 5. Honest limitations of this scan

- **Not a direct subreddit read.** Every direct Reddit route is blocked for the crawler here and the sanctioned `reddit-scan.py` creds are unset, so findings come from community-aggregation + practitioner write-ups via web search, cross-checked against primary docs. The approved rule's own Provenance block says this. **The durable fix remains: set `REDDIT_CLIENT_ID`/`SECRET` and run `reddit-scan.py`.**
- **The ~60% heuristic is community consensus, not an Anthropic threshold** — carried into the rule as a rule of thumb with an explicit "don't wire a hard trigger" edge-case.
- **Single-rule discipline** — three real-but-covered findings (H2–H4) were denied to hold the one-tight-rule line; none is lost (each is already owned by a shipped surface, cited above).
