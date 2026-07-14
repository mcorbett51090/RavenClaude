# Claude subreddit scan — research, panel decision & build plan (2026-07-07)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), 3 denied-as-covered/generic. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.187.0) — the **deterministic-enforcement sibling** to the compaction-discipline rule the 2026-07-03 scan shipped.

> This is the **thirteenth** run of this recurring scan. Prior runs (approved rule in **bold**):
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — **hooks-deterministic-vs-advisory**, model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — **checkpoints/`/rewind`**, the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — **permissions three-tier `deny`/`ask`/`allow`**.
> - [2026-06-13](../2026-06-13-claude-subreddit-scan/README.md) — **git-worktrees for parallel Claude instances** + a correction to the `subagent-isolation` premise.
> - [2026-06-15](../2026-06-15-claude-subreddit-scan/README.md) · [2026-06-19](../2026-06-19-claude-subreddit-scan/README.md) · [2026-06-20](../2026-06-20-claude-subreddit-scan/README.md) · [2026-06-21](../2026-06-21-claude-subreddit-scan/README.md).
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — **MCP tool-context budget** (the count→cost rule).
> - [2026-06-24](../2026-06-24-claude-subreddit-scan/README.md) — **keep-SKILL.md-bodies-lean / progressive disclosure**.
> - [2026-07-02](../2026-07-02-claude-subreddit-scan/README.md) — **the OS-enforced Bash sandbox** + deferred proactive-compaction.
> - [2026-07-03](../2026-07-03-claude-subreddit-scan/README.md) — **compact-proactively-and-persist-state-before-compaction** (the behavioral rule this scan's finding mechanizes).
>
> Today's net-new finding (H1) is the **deterministic-enforcement sibling** the 07-03 rule left implicit. It is disjoint from every prior approved rule: 07-03 owns the *behavioral* discipline ("remember to persist before compaction"); H1 owns the *mechanism that enforces it without the model remembering* — the `PreCompact` hook — a gap that sits precisely on the seam between the 07-03 rule and the existing `prefer-a-deterministic-gate-over-a-prose-rule`.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest — Reddit was hard-blocked on every route tried, as on the 2026-07-02/03 scans):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (Reddit's official OAuth2 Data API), which `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars were unset this session** (re-verified — `os.environ` returned unset for both). Every direct Reddit route was blocked:

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session (re-verified) |
| `WebSearch` with `allowed_domains:["reddit.com"]` | ❌ `400 — reddit.com is not accessible to our user agent` (Anthropic crawler block) |
| `WebFetch https://www.reddit.com/...json` / `old.reddit.com` | ❌ `unable to fetch` (crawler-UA block) |
| `WebFetch` a redlib mirror (`redlib.catsarch.com`) | ❌ `403 Forbidden` |
| `WebSearch site:reddit.com …` | ❌ no links returned |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — surfaces practitioner write-ups + Reddit-discussion **aggregations** + primary Anthropic docs (Reddit itself never loaded) |

**Provenance of the findings below:** drawn from practitioner write-ups + Reddit-discussion aggregations via unrestricted web search, cross-checked against **primary Anthropic docs** and **this repo's own surface** — **not** from direct subreddit reads (unreachable this session). This is the documented fallback. **Standing next-scan action (carried again, now the highest-priority setup debt): set `REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET` in the routine's environment and run `reddit-scan.py` first** — with the web-search route to Reddit UA-blocked, the OAuth2 API is the only remaining path to real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `r/ClaudeAI Claude Code best practices subagents hooks tips 2026`
- `Claude Code subagents do not inherit skills preload context isolation gotcha 2026`
- `Claude Code 2.0 context management compaction plan mode community lessons 2026`
- `Claude Code PreCompact PostCompact hook persist state before compaction`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide) (**primary** — the `PreCompact` / `PostCompact` events + `manual`/`auto` trigger, and the `InstructionsLoaded` `compact` reason; confirmed this session 2026-07-07)
- [Anthropic — Best practices](https://code.claude.com/docs/en/best-practices) · [Sub-agents](https://code.claude.com/docs/en/sub-agents) (primary)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): SmartScope "Claude Code Advanced Best Practices [2026]", ofox.ai / DEV "Hooks, Subagents & Skills complete guide", Fastio / Tembo / Totalum "subagents practical guide", BSWEN / ClaudeLog / MindStudio (compaction & context management).

---

## 2. Findings (4 — assessed against the repo's own surface)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **The `PreCompact` hook is the deterministic enforcer of "persist before compaction."** Claude Code fires a `PreCompact` hook *before* every context compaction (trigger `manual` = user ran `/compact`, `auto` = the harness hit the threshold), with a `PostCompact` bookend and an `InstructionsLoaded` `compact` reason. A command hook on `PreCompact` flushes the plan / open decisions / rejected approaches to disk **deterministically** — closing the seam between two existing rules: 07-03's behavioral "persist before compaction" and `prefer-a-deterministic-gate-over-a-prose-rule`'s "mechanize load-bearing rules into hooks." | **NO — net-new.** `docs/best-practices/hook-authoring.md` lists `PreCompact` only as a passing "other event," never as a load-bearing pattern; the 07-03 compaction rule is explicitly *behavioral* (depends on the model/user remembering). Grounded against the primary hooks doc this session (`PreCompact`/`PostCompact` + `manual`/`auto` confirmed). |
| H2 | **Subagents don't inherit parent skills; the `skills:` frontmatter preloads them into the isolated context.** Three-layer context (system prompt → preloaded skills → task); parent history never leaks in. | **Covered.** `knowledge/subagent-isolation-and-tooling.md` documents the isolation model + the subagent frontmatter field set (incl. `skills`), and `best-practices/focused-task-delegation-beats-full-context-dumps.md` owns the "don't dump full context" axis. |
| H3 | **Compact at ~60% / at task boundaries, not the 95% cliff; `/compact` loses intermediate reasoning so persist first.** | **Covered — this is the 07-03 rule itself** (`compact-proactively-and-persist-state-before-compaction.md`), shipped in v0.185.0. H1 is its deterministic sibling, not a restatement. |
| H4 | **`SessionEnd` hook for a durable run-summary / audit trail.** | **Covered / N-A.** The repo already ships a `Stop`-hook family (`dod-gate`, `remind-tests`, `stream-session-close`), the JSONL event substrate, and the notify channel for end-of-run egress; a `SessionEnd` audit rule would duplicate the substrate. No net-new lesson. |

---

## 3. Panel decision (documented decision process)

Per the repo's real-time decision-review discipline, each candidate was scored against the four standing criteria the prior scans use (the `decision-review` tribunal engine needs `claude -p` for live seat verdicts, which isn't wired in this routine's environment, so this is the documented-decision-process path the task allows):

1. **Net-new** — not already stated by an existing rule/knowledge file (house-rule #4: "don't restate what's already enforced/covered").
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Net-new:** no rule states the `PreCompact` *mechanism*; the hook-authoring doc mentions the event only in passing, and 07-03 is explicitly behavioral. It sits exactly on the seam between two existing rules and is named by neither — the strongest kind of additive finding. **In-scope:** hooks + context-management are both core's home turf, and this is marketplace-specific (the repo *ships hooks* and just added the compaction rule). **Load-bearing:** an advisory "remember to persist" is the weakest possible guard for auto-compaction — which fires late and unattended; the deterministic hook flushes state whether or not anyone noticed, and losing a plan/decision to a compaction it could have survived is a real, recurring cost. **Low-blast:** additive markdown. | Keep it tight and cross-linked to the two rules it bridges so it reads as their missing hinge, not a fourth context near-duplicate. Mark the event payload (`PreCompact`/`PostCompact`, `manual`/`auto`) **verify-at-use** — the hook event set evolves; it was confirmed against the primary hooks doc this session but should be re-checked against the settings schema before a consumer wires it. |
| H2 | ❌ Deny | Fails #1 — covered. Subagent skill-inheritance + the three-layer context model are owned by `knowledge/subagent-isolation-and-tooling.md` + the focused-delegation rule. | None — cleanly covered. |
| H3 | ❌ Deny | Fails #1 — it **is** the 07-03 rule (v0.185.0). H1 is its deterministic sibling, deliberately distinct. | None. |
| H4 | ❌ Deny | Fails #1 (+ partially #3) — the `Stop`-hook family + JSONL substrate + notify channel already own end-of-run audit; a `SessionEnd` rule would duplicate the substrate with no net-new lesson. | None — if a future scan finds a `SessionEnd`-specific lesson the substrate can't express, revisit. |

**Net:** 1 approved (H1), 3 denied (H2/H3/H4 covered). One tightly-scoped addition that completes an existing pair — consistent with house-rule #4 and every prior scan's one-tight-rule discipline. Padding a mature repo (28 rules, ~48 concept cards, the full hook set) with near-duplicates would be the anti-pattern.

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "The `PreCompact` hook is the deterministic enforcer of persist-before-compaction." Sections: Why (the two rules it bridges + the advisory-guard gap) / How to apply (register a `PreCompact` command hook; branch on `trigger`; keep it idempotent + fail-open; `PostCompact` verifies) / Edge cases (short sessions; insurance-not-replacement; not a compaction veto; verify-at-use; non-Claude hosts) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/precompact-hook-is-the-deterministic-enforcer-of-persist-before-compaction.md` | Follows the one-rule-per-file format of the existing rules. |
| 2 | Index update: → **28 rules**; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.186.1 → **0.187.0**, mirrored across all three. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json` via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. |
| 4 | CHANGELOG top entry for 0.187.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-07-07-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook/agent — so no count-string sync + no frontmatter gate. Markdown + manifest diff only; run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide) (**primary** — `PreCompact`/`PostCompact` events, `manual`/`auto` trigger, `InstructionsLoaded` `compact` reason; confirmed 2026-07-07) · [Best practices](https://code.claude.com/docs/en/best-practices) · [Sub-agents](https://code.claude.com/docs/en/sub-agents)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): SmartScope, ofox.ai / DEV (hooks-subagents-skills), Fastio / Tembo / Totalum (subagents), BSWEN / ClaudeLog / MindStudio (compaction & context management).
- Cross-checked against this repo: [`best-practices/compact-proactively-and-persist-state-before-compaction.md`](../../../plugins/ravenclaude-core/best-practices/compact-proactively-and-persist-state-before-compaction.md) (the behavioral sibling H1 mechanizes), [`best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md) (the principle H1 applies), [`docs/best-practices/hook-authoring.md`](../../best-practices/hook-authoring.md) (lists `PreCompact` only in passing), [`knowledge/subagent-isolation-and-tooling.md`](../../../plugins/ravenclaude-core/knowledge/subagent-isolation-and-tooling.md) (H2 coverage).
- Prior runs: [`2026-07-02`](../2026-07-02-claude-subreddit-scan/README.md) · [`2026-07-03`](../2026-07-03-claude-subreddit-scan/README.md) (the scan whose compaction rule this finding completes).
- **Route-reality note:** direct Reddit access was fully blocked this session (OAuth2 creds unset; `reddit.com` UA-blocked on both WebSearch and WebFetch; redlib mirror 403; `site:reddit.com` returned nothing). Findings are from indexed aggregations + primary docs, not direct subreddit reads — see §1.
