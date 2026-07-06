# Claude subreddit scan — research, panel decision & build plan (2026-07-03)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), 3 denied-as-covered/generic. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.185.0). It is the candidate the 2026-07-02 scan explicitly deferred as "the strongest next candidate."

> This is the **twelfth** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions three-tier `deny`/`ask`/`allow` (approved).
> - [2026-06-13](../2026-06-13-claude-subreddit-scan/README.md) — git-worktrees for parallel Claude instances (approved) + a correction to the `subagent-isolation` premise.
> - [2026-06-15](../2026-06-15-claude-subreddit-scan/README.md) · [2026-06-19](../2026-06-19-claude-subreddit-scan/README.md) · [2026-06-20](../2026-06-20-claude-subreddit-scan/README.md) · [2026-06-21](../2026-06-21-claude-subreddit-scan/README.md).
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — **MCP tool-context budget** (approved → the count→cost rule).
> - [2026-06-24](../2026-06-24-claude-subreddit-scan/README.md) — **keep-SKILL.md-bodies-lean / progressive disclosure** (approved).
> - [2026-07-02](../2026-07-02-claude-subreddit-scan/README.md) — **the OS-enforced Bash sandbox** (approved) + deferred **proactive-compaction** as the strongest next candidate.
>
> Today's net-new finding (H1) is that **deferred candidate**, now promoted. It is disjoint from all prior approved rules: the 06-10/06-22 context items own context *cost* + *checkpoints*; H1 owns the *compaction discipline itself* (when to compact, and what to persist before it discards intermediate reasoning) — a gap the context-window concept card describes but no rule states.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest — the block is worse this session than prior runs):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (Reddit's official OAuth2 Data API), which `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars were unset this session** (verified — `os.environ` returned `False` for both). Unlike prior runs where the unrestricted `WebSearch` fallback still reached Reddit-discussion aggregations, this session Reddit was **hard-blocked on every route tried:**

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session (re-verified) |
| `WebSearch` with `allowed_domains:["reddit.com"]` | ❌ `400 — reddit.com is not accessible to our user agent` (Anthropic crawler block) |
| `WebFetch https://www.reddit.com/...json` / `old.reddit.com` / a redlib mirror | ❌ `unable to fetch` / `403` (crawler-UA block + mirror block) |
| `WebFetch https://www.google.com/search?q=...` | ❌ `403 Forbidden` |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — surfaces practitioner write-ups + Reddit-discussion **aggregations** + primary Anthropic docs (Reddit itself never loaded) |

**Provenance of the findings below:** drawn from practitioner write-ups + Reddit-discussion aggregations via unrestricted web search, cross-checked against **primary Anthropic docs** and **this repo's own surface** — **not** from direct subreddit reads (which were unreachable this session). This is the documented fallback, degraded further than usual. **Standing next-scan action (carried again, now higher-priority): set `REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET` in the routine's environment and run `reddit-scan.py` first** — with the web-search route to Reddit also now UA-blocked, the OAuth2 API is the only remaining path to real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `Claude Code /compact microcompact auto-compact persist context before compaction best practices docs`
- `Claude Code Agent Teams Channels Ultrareview feature 2026 community`
- `Claude Code plugin marketplace subagent best practices community insights 2026`
- `Claude Code output styles vs CLAUDE.md when to use 2026 community tips`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Best practices](https://code.claude.com/docs/en/best-practices) (primary — "Give Claude a way to verify its work"; context/`/compact` guidance) and this repo's own [`knowledge/concepts/context-window.md`](../../../plugins/ravenclaude-core/knowledge/concepts/context-window.md) (the concept card that describes compaction but states no discipline for it).
- Practitioner aggregations (read via search snippets; several Reddit-sourced): ClaudeLog (auto-compact FAQ), MindStudio (`/compact` context-rot guide), Decode Claude / oldeucryptoboi (compaction deep-dives), Ken Huang (context management at scale), builder.io (50 tips). The "run `/compact` at ~60% not 95% / at task boundaries" and "append preservation instructions" practices recur across these.
- [Anthropic — Agent Teams](https://code.claude.com/docs/en/agent-teams), [Sub-agents](https://code.claude.com/docs/en/sub-agents), [Orchestrate subagents at scale with dynamic workflows](https://code.claude.com/docs/en/workflows), [Output styles](https://code.claude.com/docs/en/output-styles) (primary — for the H2/H3/H4 already-covered checks).

---

## 2. Findings (4 — all checked against the 26-rule core set + the 11 prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Compact proactively (at task boundaries, ~before quality degrades), and persist load-bearing state to disk *before* compaction.** Auto-compact fires late (~80% of the window); by then context rot has started, so the summary that defines the rest of the session is written while the model reasons at its worst. Running `/compact` at a task boundary compacts while clean. And a compact recap is a *summary* — intermediate reasoning, rejected approaches, and plans that live only in the conversation are discarded, so anything load-bearing must be written to a file/commit/test (or anchored with `/compact <preservation instructions>`) first. | **Genuine gap (consumer-facing) — the 07-02 deferred candidate.** [`knowledge/concepts/context-window.md`](../../../plugins/ravenclaude-core/knowledge/concepts/context-window.md) *describes* compaction (it happens; work becomes a summary; durable facts belong in CLAUDE.md/files) but states **no discipline**. `mcp-tool-context-...` mentions "compacts early" re: token *cost*; `claude-md-imports-...` mentions "`/compact` survival" (which CLAUDE.md re-injects) — a **different axis**. `checkpoints-...` owns `/rewind` vs commits. Grep of `best-practices/` for the actionable compaction discipline (proactive-not-reactive; persist-before-compact) → **zero rule hits.** |
| **H2** | **Output styles replace the system prompt (role/tone/format); CLAUDE.md adds project facts on top — don't put durable project rules in an output style, and hooks (deterministic) beat CLAUDE.md (advisory, ~80%) for must-happen-every-time.** | **Denied — generic + partially covered.** The hooks-deterministic-vs-CLAUDE.md-advisory half is already the 06-09-scan finding + owned by `prefer-a-deterministic-gate-over-a-prose-rule.md`. The output-style-vs-CLAUDE.md surface choice is genuinely not a rule, but it's **generic Claude-Code tool-usage advice**, not a marketplace-authoring lesson grounded in this repo's constitution — the core best-practices README explicitly forbids "generic coding advice." Deny. |
| **H3** | **Agent Teams — a lead session coordinates specialist subagents (own context/prompt/tools); the main agent owns planning + integration; write dynamic workflows to orchestrate fleets at low coordination cost.** | **Covered — duplicate.** `route-before-spawning.md`, `delegate-reads-fan-out-...`, `focused-task-delegation-...`, and `structured-output-protocol-for-all-agent-handoffs.md` own the orchestrator-worker discipline; `knowledge/dynamic-workflows.md` owns the fleet-orchestration story (incl. the `## Choosing an orchestration shape` aid). Deny. |
| **H4** | **`/ultrareview` — a cloud fleet of agents hunts bugs before you merge a critical PR; run a review pass as a gate, not an afterthought.** | **Covered — duplicate + product-feature.** The just-landed (v0.184.4) `give-the-agent-a-verification-signal-it-can-read.md` umbrella + `scope-the-reviewer-to-correctness-or-it-manufactures-work.md` + the `/code-review` and `verify` skills own the pre-merge review discipline. `/ultrareview` is an Anthropic *product feature*, not a marketplace-authoring lesson. Deny. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to the prior scans: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no *action* on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably.

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** the compaction *discipline* (proactive-not-reactive; persist-before-compact) is stated by no rule — the context-window concept card only describes *that* compaction happens; the two adjacent context rules own *cost* and *`/compact` re-injection*, a different axis. It was also the panel's own **deferred next candidate** from 07-02. **In-scope:** context management is core's home turf (three existing rules already live there); this is the missing sibling. **Load-bearing:** losing a plan/decision/rejected-approach to a compaction it could have survived is a real, recurring, observable cost — the post-compact agent re-explores a dead end. **Low-blast:** additive markdown. | Keep it tight and cross-linked to the three existing context rules (`context-window.md`, `mcp-tool-context-...`, `checkpoints-...`) so the axes stay distinct and it doesn't read as a fourth near-duplicate. Mark the specific thresholds (auto-compact ~80%, "compact at ~60% / at task boundaries") **verify-at-use** — Claude Code's compaction behavior evolves and the ~60% figure is practitioner guidance, not a doc-stated constant. |
| **H2** | ❌ Deny | Fails #2 (generic) + partially #1. The hooks-vs-CLAUDE.md half is already covered; the output-style-vs-CLAUDE.md surface choice is generic Claude-Code usage advice, not a constitution-grounded marketplace-authoring lesson. | None — if a future scan finds a marketplace-specific angle (e.g. a plugin authoring an output style), revisit. |
| **H3** | ❌ Deny | Fails #1 — duplicate. Orchestrator-worker + dynamic-workflow orchestration are owned by four best-practices + `knowledge/dynamic-workflows.md`. | None — cleanly covered. |
| **H4** | ❌ Deny | Fails #1 — duplicate — and it's a product feature, not an authoring lesson. Pre-merge review discipline is owned by the verification-signal umbrella + the reviewer-scope rule + the `/code-review`/`verify` skills. | None. |

**Net:** 1 approved (H1), 3 denied (H2 generic, H3/H4 covered). One solid, well-grounded addition — and specifically the one the prior panel teed up — beats padding a mature repo with near-duplicates or generic tips. Consistent with house-rule #4 ("don't restate what's already enforced/covered") and every prior scan's one-tight-rule discipline.

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "Compact proactively, and persist load-bearing state before compaction." Sections: Why (half one — proactive-not-reactive; half two — compaction discards, so persist first) / How to apply (compact at task boundaries; anchor the summary with `/compact` preservation instructions or a CLAUDE.md note; persist to disk before the window fills) / Edge cases (short sessions; `/compact` vs `/clear`; microcompact; in-session vs durable memory; non-Claude hosts) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/compact-proactively-and-persist-state-before-compaction.md` | Follows the one-rule-per-file format of the existing rules. |
| 2 | Index update: → **27 rules**; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.184.4 → **0.185.0**, mirrored across all three. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json` via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. |
| 4 | CHANGELOG top entry for 0.185.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-07-03-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook — so no count-string sync is needed. Markdown + manifest diff only; run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Best practices](https://code.claude.com/docs/en/best-practices) (context/`/compact` + verify-your-work guidance) · [Agent Teams](https://code.claude.com/docs/en/agent-teams) · [Sub-agents](https://code.claude.com/docs/en/sub-agents) · [Orchestrate subagents at scale with dynamic workflows](https://code.claude.com/docs/en/workflows) · [Output styles](https://code.claude.com/docs/en/output-styles)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): ClaudeLog (auto-compact FAQ), MindStudio (`/compact` context-rot), Decode Claude / oldeucryptoboi (compaction deep-dives), Ken Huang (context management at scale), builder.io (50 tips).
- Cross-checked against this repo: [`knowledge/concepts/context-window.md`](../../../plugins/ravenclaude-core/knowledge/concepts/context-window.md) (describes compaction, states no discipline), `best-practices/mcp-tool-context-is-a-budget-enable-only-what-you-need.md` (context *cost* sibling), `best-practices/checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md` (durable-state sibling), `best-practices/claude-md-imports-organize-they-dont-shrink-context.md` (`/compact` re-injection axis).
- Prior runs: [`2026-06-22`](../2026-06-22-claude-subreddit-scan/README.md) · [`2026-06-24`](../2026-06-24-claude-subreddit-scan/README.md) · [`2026-07-02`](../2026-07-02-claude-subreddit-scan/README.md) (the scan that deferred this finding as the strongest next candidate).
- **Route-reality note:** direct Reddit access was fully blocked this session (OAuth2 creds unset; `reddit.com` UA-blocked on both WebSearch and WebFetch; mirrors + Google 403). Findings are from indexed aggregations + primary docs, not direct subreddit reads — see §1.
