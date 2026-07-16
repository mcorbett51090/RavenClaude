# Claude subreddit scan — research, panel decision & build plan (2026-07-16)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), 3 denied-as-covered. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.200.0): **Plan Mode is a tool-enforced read-only gate — enter it, don't just ask the agent to "think first."**

> This is the **sixteenth** run of this recurring scan. Prior runs (most recent first):
>
> - [2026-07-15](../2026-07-15-claude-subreddit-scan/README.md) — **drop-a-tier-for-grunt-work-subagents** (approved; the model-tier axis of the spawn decision).
> - [2026-07-14](../2026-07-14-claude-subreddit-scan/README.md) — **treat-repo-committed-`.claude`-config-as-untrusted-input** (approved; the _inbound_ trust-boundary sibling).
> - [2026-07-09](../2026-07-09-claude-subreddit-scan/README.md) — **scope-a-skill-to-one-workflow / the-description-is-the-trigger** (approved).
> - [2026-07-03](../2026-07-03-claude-subreddit-scan/README.md) — **compact-proactively / persist-state-before-compaction** (approved).
> - [2026-07-02](../2026-07-02-claude-subreddit-scan/README.md) — **the OS-enforced Bash sandbox** (approved) + deferred proactive-compaction.
> - [2026-06-24](../2026-06-24-claude-subreddit-scan/README.md) — **keep-SKILL.md-bodies-lean / progressive disclosure** (approved).
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — **MCP tool-context budget** (approved → the count→cost rule).
> - earlier: 2026-06-09 · 06-10 · 06-11 · 06-13 · 06-15 · 06-19 · 06-20 · 06-21.
>
> Today's net-new finding (H1) is the **explore-then-execute** gate — the entry-side sibling to the exit-side [`definition-of-done-gate`](../../../plugins/ravenclaude-core/best-practices/definition-of-done-gate-makes-done-mean-done.md). The repo owns "prefer a deterministic gate over a prose rule" as a meta-principle and pairs "enter plan mode" with the Keep/Update/Deny flow in the root `CLAUDE.md` "Plan-mode default", but **no consumer-facing best-practice states the discipline** — the same knowledge-names-it / no-rule-teaches-it gap the 07-15 model-tiering rule and the 07-14 untrusted-config rule were each approved to close.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent dev communities about using Claude Code effectively.

**Route note (honest — same hard block as the 07-02 / 07-03 / 07-09 / 07-14 / 07-15 runs):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (Reddit's official OAuth2 Data API), which `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`. Both env vars were **unset this session** (verified: both UNSET), and the direct Reddit routes stayed hard-blocked:

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session |
| `WebSearch` with `allowed_domains:["reddit.com"]` | ❌ `400 — reddit.com is not accessible to our user agent` (Anthropic-crawler UA block — unchanged from prior runs) |
| `WebFetch https://www.reddit.com/...json` (top listings) | ❌ "Claude Code is unable to fetch from www.reddit.com" (same UA block) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — surfaces practitioner write-ups + Reddit-discussion **aggregations** via search snippets |

**Provenance of the findings below:** practitioner write-ups + Reddit-discussion aggregations read via unrestricted web-search snippets, cross-checked against **this repo's own surface** (the 34-rule core best-practice set + the `knowledge/concepts/` bank + the 15 prior scans) and, for the approved item, the primary [Claude Code best-practices doc](https://code.claude.com/docs/en/best-practices) and this repo's root `CLAUDE.md` "Plan-mode default". This is the documented fallback — **not** direct subreddit reads (unreachable this session). **Standing next-scan action (carried again):** set `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` in the routine's environment and run `reddit-scan.py` first — with the web route to Reddit UA-blocked, the OAuth2 API is the only path to real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `Claude Code tips subagents hooks r/ClaudeAI 2026`
- `reddit r/ClaudeAI Claude Code best practices workflow July 2026`
- `r/ClaudeAI Claude Code best practices discussion insights subagents context`
- `Claude Code biggest lessons mistakes July 2026 subagents skills plan mode context`
- `Claude Code plan mode before coding best practice why it matters 2026`

**Sources mined (via search snippets):** SmartScope (Claude Code advanced best-practices — hooks/subagents/context), MarkTechPost (Claude Code 2026 features), Totalum (skills vs hooks vs subagents vs MCP), the Anthropic [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) doc, iwoszapar ("8 rules I learned the hard way"), Claude Directory / Blink / codewithmukesh / anyonebuilds (Plan Mode guides), Tembo / hidekazu-konishi (subagents & orchestration).

---

## 2. Findings (4 — all checked against the 34-rule core set + the 15 prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Use Plan Mode before you let the agent edit — and it is a _tool-enforced read-only state_, not an advisory "think first."** Recurring consensus in the practitioner/Reddit aggregations: letting Claude jump straight to coding produces the "almost right" failure (solves the wrong problem, writes the wrong file, misses a dependency). The load-bearing distinction the sources make: Plan Mode is a **hard constraint enforced by the tool** (edits blocked until you approve a plan), *"unlike simply asking Claude to 'think first' — which is advisory and easily overridden."* Enter it for multi-file / schema / security-sensitive / unfamiliar changes; skip it for trivial one-file edits. | **Genuine gap at the best-practice tier.** Grep of `best-practices/` for `plan.?mode` → **zero** hits; there is no Learn concept card for it either. The principle IS present as **maintainer/setup guidance** — the root [`CLAUDE.md`](../../../CLAUDE.md) § "Plan-mode default" ("enter plan mode first and present a Keep/Update/Deny structure") and the [`init-agent-ready`](../../../plugins/ravenclaude-core/commands/init-agent-ready.md) template seed the same line into a consumer's `CLAUDE.md` — but **no consumer-facing best-practice states the discipline** (that Plan Mode is a hard gate, when to enter it, why it beats an advisory prompt). Same knowledge-names-it / no-rule-teaches-it gap the 07-15 + 07-14 rules were approved under. **Additive.** |
| **H2** | **Configure a `fallbackModel` / model-fallback chain for resilience (June-2026 feature) — if the primary model is overloaded/unavailable, the chain continues.** | **Denied — covered (engine + knowledge + referenced in a rule).** Owned by [`knowledge/model-fallback.md`](../../../plugins/ravenclaude-core/knowledge/model-fallback.md) + the `_model-fallback.sh` hook + Gates 120/121, and explicitly cited in the 07-15 [`drop-a-tier`](../../../plugins/ravenclaude-core/best-practices/drop-a-tier-for-grunt-work-subagents-strong-model-supervises.md) rule's "See also" as the complementary _model-unavailable_ ladder (distinct from cost-tiering). Deny (house-rule #4). |
| **H3** | **Subagent isolation is not free context savings — if a subagent returns a wall of text, you paid for the isolation and still flooded the parent.** | **Denied — covered.** Owned by [`subagent-isolates-clutter-skill-keeps-the-work-in-thread`](../../../plugins/ravenclaude-core/best-practices/subagent-isolates-clutter-skill-keeps-the-work-in-thread.md) + the [Structured Output Protocol](../../../plugins/ravenclaude-core/CLAUDE.md) (return the conclusion, not the transcript) + [`focused-task-delegation-beats-full-context-dumps`](../../../plugins/ravenclaude-core/best-practices/focused-task-delegation-beats-full-context-dumps.md). Deny. |
| **H4** | **The unbounded "go investigate" — asking the agent to explore with no scope floods context by reading hundreds of files; scope it narrowly or hand it to a subagent.** | **Denied — covered.** Owned by [`delegate-reads-fan-out-keep-branch-writes-in-main`](../../../plugins/ravenclaude-core/best-practices/delegate-reads-fan-out-keep-branch-writes-in-main.md) + [`focused-task-delegation-beats-full-context-dumps`](../../../plugins/ravenclaude-core/best-practices/focused-task-delegation-beats-full-context-dumps.md) + [`compact-proactively-and-persist-state-before-compaction`](../../../plugins/ravenclaude-core/best-practices/compact-proactively-and-persist-state-before-compaction.md). Deny. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to every prior scan: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no _action_ on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably.

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook. _[For a lesson that IS in the root/maintainer `CLAUDE.md` but NOT in any consumer-facing best-practice, "additive" is satisfied at the best-practice tier — the 07-02 sandbox / 07-14 untrusted-config / 07-15 model-tiering precedent: maintainer guidance naming a lesson does not mean a consumer-facing rule teaches the action.]_
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** zero `best-practices/` hits + no concept card; the discipline lives only as a maintainer/setup line in the root/template `CLAUDE.md`, and the best-practices are the consumer-facing surface — the established knowledge-names-it / no-rule-teaches-it gap. **In-scope, NOT generic advice:** the non-generic edge is the **tool-enforced-gate vs. advisory-prompt** distinction — a Claude-Code-specific mechanic that maps directly onto this repo's own [`prefer-a-deterministic-gate-over-a-prose-rule`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md) principle and the Keep/Update/Deny `design_checkins` flow; pitched at the mechanic (not at "plan before you code," which would be generic). **Load-bearing:** the cost of omission is the observable "almost right" redo — an edit lands, then a second run undoes it. **Low-blast:** additive markdown. | Keep it distinct from the DoD gate (exit-side) by framing as the **entry-side** explore-then-execute gate. Frame explicitly as a **correctness** gate, not a permission/safety boundary (it doesn't relax `deny`/`ask`/`allow` or the sandbox). Mark the activation mechanic **`verify-at-use`** (keybinding/flag/tool name evolve; the durable fact is the read-only-until-approved _shape_). Note that auto-approving every plan unread collapses it back to the advisory prompt it replaces. |
| **H2** | ❌ Deny | Fails #1 — covered by the model-fallback knowledge file + hooks + gates, and already cross-referenced from the 07-15 rule as the complementary unavailable-model ladder. | None. |
| **H3** | ❌ Deny | Fails #1 — covered by the subagent-isolation + Structured-Output + focused-delegation rules. | None. |
| **H4** | ❌ Deny | Fails #1 — covered by the delegate-reads + focused-delegation + proactive-compaction rules. | None. |

**Net:** 1 approved (H1), 3 denied (all covered). One solid, well-grounded, correctness-bearing addition — the missing _entry-side_ explore-then-execute gate — beats padding a mature 34-rule set. Consistent with house-rule #4 and every prior scan's one-tight-rule discipline.

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "Plan Mode is a tool-enforced read-only gate — enter it, don't just ask the agent to 'think first'." Sections: Why (tool-enforced-gate vs advisory-prompt; the "almost right" cost; knowledge-names-it/no-rule-teaches-it) / How (when to enter: 3+ files, schema/migration/manifest, security-sensitive, unfamiliar; how it composes with design_checkins + DoD + route-before-spawning) / Edge cases (skip trivial edits; correctness-not-permission gate; approval isn't a rubber stamp; verify-at-use mechanic) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/plan-mode-is-a-tool-enforced-gate-not-an-advisory-think-first.md` | Mirrors the one-rule-per-file format of the existing rules. |
| 2 | Index update: → **35 rules**; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.199.0 → **0.200.0**, mirrored across all three surfaces. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json` via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. |
| 4 | CHANGELOG top entry for 0.200.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-07-16-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook — so no count-string sync is needed. Markdown + manifest diff only; ran `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- Practitioner aggregations (read via unrestricted web-search snippets; several Reddit-sourced): SmartScope (Claude Code advanced best-practices — hooks/subagents/context), MarkTechPost (Claude Code 2026 features), Totalum (skills vs hooks vs subagents vs MCP), iwoszapar ("8 rules I learned the hard way"), Tembo / hidekazu-konishi (subagents & orchestration), and the Plan-Mode guides (Claude Directory, Blink, codewithmukesh, anyonebuilds).
- Primary: [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) (the tool-enforced-read-only-state framing; verify-at-use anchor for the activation mechanic).
- Cross-checked against this repo: root [`CLAUDE.md`](../../../CLAUDE.md) § "Plan-mode default", [`best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md), [`best-practices/definition-of-done-gate-makes-done-mean-done.md`](../../../plugins/ravenclaude-core/best-practices/definition-of-done-gate-makes-done-mean-done.md), and (for the denied items) [`knowledge/model-fallback.md`](../../../plugins/ravenclaude-core/knowledge/model-fallback.md) + the subagent-isolation / focused-delegation rules.
- Prior runs: [`2026-07-15`](../2026-07-15-claude-subreddit-scan/README.md) · [`2026-07-14`](../2026-07-14-claude-subreddit-scan/README.md) · [`2026-07-09`](../2026-07-09-claude-subreddit-scan/README.md) · [`2026-07-03`](../2026-07-03-claude-subreddit-scan/README.md) · [`2026-07-02`](../2026-07-02-claude-subreddit-scan/README.md)
