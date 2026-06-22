# Claude subreddit scan — research, panel decision & build plan (2026-06-22)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), **1 already-shipped** by the intervening 2026-06-13 scan, 2 denied-as-covered. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.161.0).

> **Branch-currency note (added at merge):** this scan was drafted against a branch point that predated the **2026-06-13** scan; on rebase, `main` had moved to v0.160.0 and **already shipped the git-worktrees rule** this doc had listed as finding H3. The disposition below is corrected to reflect that — H3 is **already-shipped, not denied** — and the version/date were rebased (0.158.0 → **0.161.0**, 06-14 → **06-22**). The approved H1 (MCP tool-context budget) was re-checked against the new `main` and remains genuinely net-new.

> This is the **fifth** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions three-tier `deny`/`ask`/`allow` (approved), skills-vs-subagents-vs-MCP, headless-CI cost guardrails, thinking budgets.
> - [2026-06-13](../2026-06-13-claude-subreddit-scan/README.md) — **git-worktrees for parallel Claude instances (approved → v0.160.0)** + a correction to the `subagent-isolation` premise. This is the scan that overtook this doc's H3.
>
> Today's net-new finding (H1) is disjoint from all four sets.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest):** the sanctioned front door for this scan is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py), which pulls real subreddit listings via Reddit's official OAuth2 Data API. It `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars were unset this session** (verified — `os.environ` check returned `False` for both). The one-time credential setup still hasn't landed in this environment, so — exactly as in the 2026-06-11 run — this scan fell back to unrestricted web search. The *structural* block (crawler-UA 403 on `reddit.com`) is solved by the script; the *operational* gap is just the missing credentials.

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session |
| `WebSearch allowed_domains:[reddit.com]` | **400 — "domains not accessible to our user agent"** (Anthropic crawler-UA block) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion aggregations + practitioner write-ups |

**Provenance of the findings below:** drawn from Reddit-discussion aggregations + practitioner write-ups via unrestricted web search, cross-checked against primary Anthropic docs and **this repo's own architecture** — **not** from direct subreddit reads. This is the documented fallback, **not** the preferred route. **Next scan: set the two Reddit creds and run `reddit-scan.py` first** so findings come from real subreddit listings (closing the provenance gap for good).

**Queries run (fallback route — unrestricted web search):**

- `Claude Code CLAUDE.md memory file discipline what to put pitfalls bloat reddit discussion 2026`
- `Claude Code MCP server too many tools context bloat token budget disable reddit 2026`
- `Claude Code git worktrees parallel agents multiple instances workflow 2026`
- `Claude Code spec-driven development plan first verify evidence Claude claims success reddit 2026`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Manage context / costs](https://code.claude.com/docs/en/costs) and [Context windows](https://docs.claude.com/en/docs/build-with-claude/context-windows) (primary)
- [Anthropic — How Claude remembers your project (memory)](https://code.claude.com/docs/en/memory) (primary)
- [Anthropic — Run parallel sessions with worktrees](https://code.claude.com/docs/en/worktrees) (primary)
- [`anthropics/claude-code#11364` — Lazy-load MCP tool definitions to reduce context usage](https://github.com/anthropics/claude-code/issues/11364) (the upstream signal behind Tool Search)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): Scott Spence "Optimising MCP server context usage in Claude Code"; Joe Njenga "Claude Code cut MCP context bloat 46.9% with Tool Search"; techtaek "Claude Code context discipline 2026"; Augment Code "Claude Code for spec-driven development".

---

## 2. Findings (4 — all fresh vs. the 2026-06-09 / -10 / -11 scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Every enabled MCP server's tool schemas are preloaded into the context window before you type anything** — names + descriptions + full JSON schemas. A widely-shared measurement: **7 MCP servers ≈ 67K tokens, ~33.7% of a 200K budget, consumed before any work.** The levers: enable only the servers you need, prefer **tool-search / lazy-loading** (load schemas on demand) over preloading, disable unused servers, and **measure** the budget (`/context`). | **Genuine gap (consumer-facing).** `knowledge/concepts/context-window.md` says the window *includes* "tool schemas" generically and that the SessionStart banner is a recurring tax — but never teaches the **MCP-server-count → token-cost** mechanic or the operational levers. `AGENTS.md` covers the **agent-_description_ ~15K budget** (a different surface, and it's marketplace-_authoring_ guidance). And **this session is the worked example**: its MCP tools (github, Google-Drive, …) are deferred + lazy-loaded via `ToolSearch`, not preloaded — the fix, lived. |
| **H2** | **CLAUDE.md / memory hygiene: separate stable human-written instructions from discovered auto-memory; keep it short (~under 200 lines); every memory note must help the next session act faster or be pruned.** Stale/contradictory memory is actively dangerous; a note that only records "X once happened" belongs in a retrospective, not active memory. | **Partially covered + restates the docs.** The repo's `CLAUDE.md` "Memory references" section + the Sága-log retrospective-vs-active-memory distinction already embody the principle; the generic "keep CLAUDE.md short / prune stale notes" half largely restates the Anthropic [memory doc](https://code.claude.com/docs/en/memory) — generic-platform-101, which the core set excludes. |
| **H3** | **Run multiple Claude Code agents in parallel via git worktrees** — each agent its own branch + directory + ports, no working-tree contention; "Agent Teams" (Opus 4.6, Feb 2026) formalizes a team-lead spawning self-coordinating teammates. | **Already shipped on `main` (2026-06-13 scan).** The intervening scan approved this exact finding as a net-new peer-process rule, [`isolate-parallel-claude-instances-in-git-worktrees.md`](../../../plugins/ravenclaude-core/best-practices/isolate-parallel-claude-instances-in-git-worktrees.md) (v0.160.0), **and corrected the `subagent-isolation` premise** this doc's draft had leaned on (the "git-write is auto-denied to subagents / `isolation:"worktree"` strips `Read`" claims were falsified there). So H3 is not a candidate here — it's done, and done better than "denied as covered" would have been. |
| **H4** | **Spec-driven: checkable success criteria beat interpretable ones** — "`npm test` passes" / "`curl` returns 200" produce more reliable outcomes than "well-structured" / "good performance"; have the agent show evidence rather than assert success. | **Covered — duplicate.** `definition-of-done-gate-makes-done-mean-done.md` (a gate makes *done* mean done), `check-runtime-state.md` (read the substrate, don't assume), and `three-epistemic-protocols.md` (evidence, not assertion) already teach exactly this. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to the prior scans: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no _action_ on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (If Matt wants the live tribunal applied retroactively, `decision-review` over this doc's decisions is the surface.)

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** no consumer-facing rule names the MCP-server-count → context-cost mechanic; `context-window.md` is the generic explainer and the `AGENTS.md` 15K budget is the *agent-description* authoring analog on a different surface. **In-scope:** context/budget governance is core's domain, and **the repo's own deferred-MCP-via-`ToolSearch` architecture is the canonical worked example** — the least-generic possible framing for this repo (same shape as the 06-11 `permissions` approval, whose worked example was the repo's own deny list). **Load-bearing:** ~⅓ of the context budget silently consumed before any work is a real, measurable cost with a real fix. **Low-blast:** additive markdown. | Keep it tight and cross-linked to `context-window.md` (the parent concept), `focused-task-delegation-beats-full-context-dumps.md` (the same desk-not-filing-cabinet discipline applied to delegation), and the `AGENTS.md` agent-description budget (the sibling budget on the authoring side). Frame the moving specifics (Tool Search rollout, `/context`) as dated/verify-at-use so the rule doesn't rot. |
| **H2** | ⏸️ Defer | Borderline #1 and #2. The load-bearing nugget (separate stable instructions from discovered memory; prune history-only notes) is real, but the repo's `CLAUDE.md` Memory-references section + Sága-log already embody it, and the "keep it short" half restates the Anthropic memory doc — generic-platform-101. | If an `/init-agent-ready` companion on "structuring your own CLAUDE.md" is ever built, fold the stable-vs-discovered + prune-history-only discipline in there grounded in RavenClaude's memory model — not as a standalone core rule. |
| **H3** | ✅ Already shipped (no action) | The **2026-06-13 scan** already approved this as the net-new peer-process rule `isolate-parallel-claude-instances-in-git-worktrees.md` (v0.160.0) and corrected the `subagent-isolation` premise. This doc's original draft verdict ("deny — duplicate, covered by subagent-isolation") was **wrong twice over**: the finding was genuinely net-new (a peer-process posture the sub-agent rule explicitly defers), and the premise it cited had since been falsified. Recording the correction rather than hiding it. | Nothing to add — `main` carries the rule. The lesson logged: a "deny as covered" is only as good as the coverage claim; re-check it against current `main`, not the branch point. |
| **H4** | ❌ Deny | Fails #1 — duplicate. `definition-of-done-gate-makes-done-mean-done.md` + `check-runtime-state.md` + `three-epistemic-protocols.md` already teach checkable-criteria / evidence-not-assertion. | None — cleanly covered. |

**Net:** 1 approved (H1), 1 already-shipped (H3, by the 06-13 scan), 1 deferred (H2), 1 denied (H4). One solid, well-grounded addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 ("don't restate what's already enforced/covered") and the prior scans' discipline (each landed exactly one tight rule).

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "MCP tool context is a budget — enable only what you need." Sections: Why / How (count→cost mechanic, the enable-only / lazy-load / measure levers, the repo's own deferred-MCP-via-`ToolSearch` as the worked example) / Edge cases / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/mcp-tool-context-is-a-budget-enable-only-what-you-need.md` | Follows the one-rule-per-file format of the existing rules. |
| 2 | Index update: → **20 rules** (19 on `main` after the 06-13 worktree rule, +1 here); add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.160.0 → **0.161.0**, mirrored. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json`) | CI fails on version drift between the two. |
| 4 | CHANGELOG top entry for 0.161.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-06-22-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. Markdown-only diff, but run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Manage context / costs](https://code.claude.com/docs/en/costs) · [Context windows](https://docs.claude.com/en/docs/build-with-claude/context-windows)
- [Anthropic — How Claude remembers your project (memory)](https://code.claude.com/docs/en/memory)
- [Anthropic — Run parallel sessions with worktrees](https://code.claude.com/docs/en/worktrees)
- [`anthropics/claude-code#11364` — Lazy-load MCP tool definitions to reduce context usage](https://github.com/anthropics/claude-code/issues/11364)
- Practitioner aggregations (read via search snippets): Scott Spence (optimising MCP server context usage), Joe Njenga (Tool Search MCP context reduction), techtaek (context discipline 2026), Augment Code (spec-driven development capabilities & limits)
- Prior runs: [`2026-06-09`](../2026-06-09-claude-subreddit-scan/README.md) · [`2026-06-10`](../2026-06-10-claude-subreddit-scan/README.md) · [`2026-06-11`](../2026-06-11-claude-subreddit-scan/README.md)
