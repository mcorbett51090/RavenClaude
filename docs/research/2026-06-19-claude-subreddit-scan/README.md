# Claude subreddit scan — research, panel decision & build plan (2026-06-19)

**Author:** `claude` (automated scan / scheduled routine)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 fresh findings surfaced (none overlapping the 2026-06-09 / -10 / -11 scans) → **1 approved**, 1 deferred-as-covered, 2 denied/deferred. The approved item shipped as one new consumer-facing best-practice in `ravenclaude-core` (v0.158.0).

> This is the **fourth** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions `deny`/`ask`/`allow` (approved), skills-vs-subagents-vs-MCP, CI token caps, thinking-budget keywords.
>
> Today's findings are deliberately disjoint from all three sets.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest — same as the prior three scans):** the repo ships the sanctioned front door [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (Reddit's official OAuth2 Data API). It was attempted first this session and `_die`d as designed — `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` are **both unset this session** (verified: `${REDDIT_CLIENT_ID:+set}` → unset; running the script with real `--subreddits` args returned `ERROR: REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set`). So the *structural* block is solved; the *operational* gap is still the missing credentials in this environment.

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session (re-verified) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion snippets + practitioner write-ups |
| `WebFetch code.claude.com/docs/en/memory` (primary-source grounding) | ✅ works — used to verify the approved finding verbatim |

**Provenance of the findings below:** drawn from Reddit-discussion aggregations + 2026 practitioner write-ups via unrestricted web search, **cross-checked against primary Anthropic docs** (the approved finding is grounded verbatim against [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)). This is the documented fallback, **not** the preferred route. **Next scan: set the two Reddit creds and run `reddit-scan.py` first** so findings come from real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `Claude Code best practices reddit r/ClaudeAI 2026 CLAUDE.md output styles subagents lessons learned`
- `Claude Code git worktrees parallel agents workflow 2026 multiple sessions isolation tip`
- `Claude Code CLAUDE.md import nested memory hierarchy @import file best practice 2026`
- `Claude Code output styles custom slash commands hooks SessionStart PreCompact 2026 new features`
- `Claude Code spec-driven development plan file write spec first then implement 2026 workflow lesson`
- `Claude Code reddit 2026 common mistake too much in CLAUDE.md rules ignored instruction adherence context bloat`

---

## 2. Findings

| # | Finding (community signal) | Repo-coverage check |
| --- | --- | --- |
| **I1** | **`@import` in CLAUDE.md is an *organization* tool, not a *context-budget* tool.** Splitting a big `CLAUDE.md` into `@path` imports makes the file look smaller but loads every imported byte into context **at launch** — identical token cost + adherence penalty. The lever that actually shrinks baseline context is **conditional loading**: path-scoped `.claude/rules/` (load only when a matching file is touched) and skills (load only on invocation). Community pain point: "context windows stuffed with noise," CLAUDE.md bloat reducing rule adherence. | **Genuine gap.** `knowledge/concepts/context-window.md` teaches the desk/filing-cabinet model and `docs/token-budget-playbook.md` covers prompt-caching, but **no rule or concept** states the import-doesn't-reduce-context point or names `.claude/rules/`/skills as the real budget levers. And the repo *lives* the worked example — its own root `CLAUDE.md` (81 lines) opens with `@AGENTS.md` (188 lines), both loaded at launch. |
| **I2** | **Git worktrees / `isolation: worktree` for parallel agents** — give each session its own working dir on a shared `.git` so 3–5 agents write simultaneously without collisions; `EnterWorktree` / subagent `isolation: worktree` frontmatter. | **Covered + explicitly bounded.** The repo ships `skills/new-worktree`, `skills/cleanup-worktrees`, `skills/spawn-team`, the **Sleipnir** worktree-traversal convention, and the `delegate-reads-fan-out-keep-branch-writes-in-main` best-practice — which *explicitly* documents that background sub-agents are auto-denied git writes (worktree-isolated **or** not), so the marketplace's orchestrator-worker model is designed *around* the parallel-writer pattern rather than adopting it. |
| **I3** | **Built-in output styles were deprecated → migrate to the SessionStart hook** (Claude Code v1.0.48-era churn; a migrator tool exists). | **No repo content to correct + Claude-Code-CLI churn.** The repo ships a SessionStart hook (`capability-orientation.sh`) but no output-style asset, so there is nothing currently-false to fix. The finding is a moving-target CLI fact, not an additive durable lesson. |
| **I4** | **Spec-driven development** — write a `/specs` markdown spec first, generate a numbered-task plan, implement task-by-task with review between; "the spec, not the code, is the primary artifact," version-controlled + diffable in PRs. | **Covered in principle.** The plan-mode default (root `CLAUDE.md`), the repo's heavy plan/research-doc discipline (`docs/plans/**`, FORGE), and the `definition-of-done-gate` already encode "durable plan artifact before code + verify against it." The `/spec`-command specifics are generic-platform churn. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to the three prior scans: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no *action* on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (If Matt wants the live tribunal applied retroactively, `decision-review` over this doc's decisions is the surface.)

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (in core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **I1** | ✅ **Approve** | Passes all four. **Additive:** no rule/concept names the import-vs-context-reduction trap or the path-scoped-rules/skills levers — `context-window.md` is the adjacent-but-distinct desk model. **In-scope:** context-budget discipline *is* RavenClaude's domain (the token-budget playbook, the ~15K agent-description cap, the per-agent ≤300-char gate), and the repo's own `CLAUDE.md` → `@AGENTS.md` import is the canonical worked example — the least-generic topic possible for this repo. **Load-bearing:** a consumer who splits a 1,000-line `CLAUDE.md` into imports believing they saved context is actively fooled — the cost (tokens + degraded adherence) is real and the correct lever (conditional loading) is non-obvious. **Low-blast:** additive markdown. Primary-source-grounded verbatim against the Anthropic memory doc. | Kept tight; cross-linked to `prefer-a-deterministic-gate-over-a-prose-rule` (the pruning complement), `focused-task-delegation` (the sub-agent-side budget rule), and `permissions-are-deny-ask-allow` (the sibling "treat config like code" posture rule). The `/compact`-survival axis and the HTML-comment-strip exception are scoped into edge-cases so they don't blur the core point. |
| **I2** | ⏸️ Defer (already covered) | Fails #1. Worktree machinery (`new-worktree`/`cleanup-worktrees`/`spawn-team`/Sleipnir) and the parallel-writer boundary (`delegate-reads-fan-out-keep-branch-writes-in-main`) already exist; the marketplace deliberately *doesn't* adopt free parallel-writer worktrees because background sub-agents are auto-denied git writes. A new rule would duplicate and partly contradict the shipped posture. | Nothing to add. If Claude Code ever lifts the background-subagent git-write auto-deny, revisit whether the keep-writes-in-main rule needs a worktree carve-out. |
| **I3** | ❌ Deny | Fails #1 and #3 for the repo. There is no output-style asset in the repo to correct (nothing currently-false), and the migration is a version-pinned CLI fact in active churn — canonizing it would age badly. | If the repo ever ships an output-style or a knowledge file asserts one exists, add a one-line currency note then — not a best-practice now. |
| **I4** | ❌ Deny | Fails #1 — duplicate in principle. Plan-mode-default + the repo's plan/research-doc discipline + the `definition-of-done-gate` already encode "durable plan artifact before code, verified against it." The net-new delta is the `/spec` command + `/specs` folder convention, which is generic-platform-101 and CLI-churny. | If a consumer-authoring guide is ever built (an `/init-agent-ready` companion), a "spec-first" subsection could fold in there, grounded in the repo's own FORGE/plan discipline — not as a standalone core rule. |

**Net:** 1 approved, 1 deferred, 2 denied. One solid, well-grounded addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 ("don't restate what's already enforced/covered") and the three prior scans' discipline (each landed exactly one tight rule).

---

## 4. Build plan (approved: I1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "CLAUDE.md `@imports` organize — they don't shrink context; path-scoped rules and skills do." Sections: Why / How (always-loaded-vs-conditionally-loaded table + the repo's own `@AGENTS.md` import as the worked example) / Edge cases (dedup-payoff, HTML-comment strip, `/compact` axis, non-Claude hosts) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/claude-md-imports-organize-they-dont-shrink-context.md` | Follows the one-rule-per-file format of the existing 18 rules. |
| 2 | Index update: 18 → 19 rules; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.157.0 → **0.158.0**, mirrored. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` | CI fails on version drift between the two. |
| 4 | CHANGELOG top entry for 0.158.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-06-19-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. Markdown-only diff, but run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — How Claude remembers your project (memory)](https://code.claude.com/docs/en/memory) — verbatim: `@path` imports "help organization but do not reduce context, since imported files load at launch"; path-scoped `.claude/rules/` "only load into context when Claude works with matching files, reducing noise and saving context space"; skills "only load when you invoke them or when Claude determines they're relevant"; managed/HTML-comment + `/compact` survival behavior. (Primary grounding for the approved finding.)
- Practitioner aggregations (read via search snippets): MarkTechPost (Claude Code Guide 2026), DEV Community (nested CLAUDE.md loading), Medium/Serenities AI (CLAUDE.md complete guide), MindStudio / Developers Digest / RockB (worktrees parallel-agents 2026), GitHawkAI (output-style → SessionStart migrator), DataCamp / Augment Code (spec-driven development), morphllm "Claude Code Reddit: What Developers Actually Say (2026)".
- Prior runs: [`2026-06-09`](../2026-06-09-claude-subreddit-scan/README.md) · [`2026-06-10`](../2026-06-10-claude-subreddit-scan/README.md) · [`2026-06-11`](../2026-06-11-claude-subreddit-scan/README.md)
