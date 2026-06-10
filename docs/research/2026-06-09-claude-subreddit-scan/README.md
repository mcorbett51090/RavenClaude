# Claude subreddit scan — research, panel decision & build plan (2026-06-09)

**Author:** `claude` (automated overnight scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 5 findings surfaced → **1 approved**, 4 rejected as already-covered or out-of-scope. The approved item shipped as one new consumer-facing best-practice in `ravenclaude-core`.

---

## 1. What was searched (and the route reality)

**Goal:** recent high-quality posts/discussion on r/Claude, r/ClaudeAI, and adjacent communities about using Claude Code effectively.

**Route note (honest):** `reddit.com` is **blocked for the search/fetch user agent** in this environment — both `WebSearch allowed_domains:[reddit.com]` and `WebFetch` of `reddit.com/...json` returned hard blocks ("domains not accessible to our user agent" / "unable to fetch from www.reddit.com"). Per the repo's Capability-Grounding discipline, that is evidence about **one route**, not the goal. The working route was **unrestricted web search**, which surfaces Reddit-sourced content via search snippets and third-party aggregations of Reddit threads. Findings below are therefore drawn from Reddit-discussion _aggregations_ cross-checked against primary Anthropic docs — not from direct subreddit reads. This is flagged so a future session doesn't over-trust the provenance.

**Queries run (working route):**

- `Claude Code best practices subagents hooks CLAUDE.md tips 2026 reddit discussion`
- `Claude Code multi-agent orchestration parallel subagents reddit pattern Opus Sonnet`
- `Claude Code plan mode TDD test driven development workflow reddit best practice`

**Sources mined:**

- [morphllm.com — "Claude Code Reddit: What Developers Actually Say (2026)"](https://www.morphllm.com/claude-code-reddit) (aggregation of r/ClaudeAI discussion; 403 on direct fetch, read via search snippet)
- [builder.io — "50 Claude Code Tips and Best Practices"](https://www.builder.io/blog/claude-code-tips-best-practices) (403 on direct fetch, read via search snippet)
- [Anthropic — Claude Code best practices](https://code.claude.com/docs/en/best-practices) (primary, for cross-check)
- [Anthropic — Create custom subagents](https://code.claude.com/docs/en/sub-agents) (primary, for cross-check)

---

## 2. Findings (5)

| # | Finding (community lesson) | Already in repo? |
| --- | --- | --- |
| F1 | **Hooks are deterministic; `CLAUDE.md` is advisory.** For anything that must happen every time (format/lint/test/layout), use a hook or CI gate, not a prose rule — and **prune `CLAUDE.md`** (keep it lean / nested), because an over-long file gets half-ignored. | **Authoring side only.** `AGENTS.md` house-rule #4 + hook-and-CI layout enforcement live this internally, but there is **no consumer-facing named rule** stating it. |
| F2 | **Model tiering** — run the orchestrator on Opus, fan focused sub-tasks to Sonnet/Haiku to cut cost without losing quality. | **Yes — thoroughly.** `ai-coding-model-guidance` ships `right-size-not-top-of-range.md`, `narrate-the-tier-selection-not-just-the-sku.md`, `cross-tool-model-lineup-2026.md`, `right_size_cost.py`; core has `dynamic-workflows.md`. |
| F3 | **Subagent context isolation** — spawn a sub-agent for exploration so it doesn't flood the main context window. | **Yes.** `best-practices/focused-task-delegation-beats-full-context-dumps.md`, `knowledge/subagent-isolation-and-tooling.md`, the `Explore` agent. |
| F4 | **Plan-mode-first + explicit-failing-test TDD** — "write a FAILING test first, do NOT write implementation yet," because Claude defaults to implementation-first. | **Partially / out-of-scope.** Plan-mode default is in `CLAUDE.md`; `definition-of-done` + `spec-reread-ritual` cover the verification side. The red-green TDD prompt itself is generic coding advice the core best-practices set explicitly excludes. |
| F5 | **Context hygiene / `/clear` between unrelated tasks** — context "rot" as the window fills; start fresh between unrelated tasks. | **Mostly.** Delegation/isolation rules cover the multi-agent angle; a standalone consumer rule on single-session `/clear` hygiene is borderline-generic. |

---

## 3. Panel decision

**Mechanism:** This is a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation. Rationale: the comfort-posture `decision_review` knob is **off by default**, the tribunal's live seats cost a `claude -p` round per seat, and none of these findings is a yes/no _action_ on an irreversible/high-blast operation — they're additive-content proposals where the binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (If Matt wants the live tribunal applied retroactively, `decision-review` over this doc's decisions is the surface.)

**Approval criteria** (a finding is approved only if all hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook.
2. **In-scope** — domain-neutral and constitution-grounded (the core best-practices README forbids "generic coding advice").
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **F1** | ✅ **Approve** | Passes all four. The repo proves the lesson true on its authoring side but ships **no consumer-facing rule** — a genuine gap for the `/init-agent-ready` audience. Constitution-grounded (house-rule #4, issue #23478 hook+CI pattern), high cost when missed (silently-skipped must-haves under load). | None material. Kept tight to avoid drift with `hook-authoring.md` (cross-linked, not duplicated). |
| **F2** | ❌ Deny | Fails #1 — duplicate. Already covered with more depth (a whole plugin + a cost script) than a new rule would add. | Adding it would dilute, not extend. |
| **F3** | ❌ Deny | Fails #1 — duplicate of `focused-task-delegation-…` + `subagent-isolation-…`. | — |
| **F4** | ❌ Deny | Fails #2 — red-green TDD is generic coding advice the core set explicitly excludes; the plan-mode/verification slice is already present. | If desired, belongs in a _domain_ plugin (e.g. `qa-test-automation`), not core. |
| **F5** | ⏸️ Defer | Borderline #2 (generic) and partially #1 (covered for multi-agent). Not worth a thin standalone rule today. | Revisit only if a concrete single-session context-rot failure is observed. |

**Net:** 1 approved, 3 denied, 1 deferred. One solid, well-grounded addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 ("don't restate what's already enforced/covered").

---

## 4. Build plan (approved: F1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "Prefer a deterministic gate over a prose rule — and prune the prose it replaces." | `plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md` | Follows the one-rule-per-file format (Why / How / Edge cases / See also / Provenance). |
| 2 | Index update: 15 → 16 rules; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.138.0 → **0.139.0**, mirrored. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` | CI fails on version drift between the two. |
| 4 | CHANGELOG top entry for 0.139.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-06-09-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. Markdown-only diff, but run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [morphllm.com — Claude Code Reddit: What Developers Actually Say (2026)](https://www.morphllm.com/claude-code-reddit)
- [builder.io — 50 Claude Code Tips and Best Practices](https://www.builder.io/blog/claude-code-tips-best-practices)
- [Anthropic — Claude Code best practices](https://code.claude.com/docs/en/best-practices)
- [Anthropic — Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code issue #23478 — path-scoped rule files load on Read, not Write](https://github.com/anthropics/claude-code/issues/23478)
