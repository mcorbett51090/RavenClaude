# Claude subreddit scan — research, panel decision & build plan (2026-06-29)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), 2 denied-as-covered, 1 deferred. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.182.0 → **0.183.0**).

> This is the **seventh+** run of this recurring scan. Prior runs (most recent first):
>
> - [2026-06-24](../2026-06-24-claude-subreddit-scan/README.md) — **keep SKILL.md bodies lean / progressive disclosure (approved → v0.172.0)**; facts-vs-procedures-belong-in-a-skill (deferred-and-folded), model-tiering (denied dup), config-as-execution-vector (deferred).
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — **MCP tool-context budget (approved → v0.161.0, the count→cost rule)**; CLAUDE.md memory hygiene (deferred), git-worktrees (already-shipped), spec-driven checkable-criteria (denied dup).
> - [2026-06-13](../2026-06-13-claude-subreddit-scan/README.md) — git-worktrees for parallel Claude instances (approved → v0.160.0) + a correction to the `subagent-isolation` premise.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions three-tier `deny`/`ask`/`allow` (approved), skills-vs-subagents-vs-MCP, headless-CI cost guardrails, thinking budgets.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
>
> Today's net-new finding (H1) is disjoint from all prior sets. It is the **fourth instruction-method authoring rule** in the ladder the scans have been building out: hooks-vs-prose (06-09), the MCP-budget (06-22), the SKILL.md-body budget (06-24), and now the **output-style / system-prompt** tier — the highest-leverage and most silently-dangerous of the methods.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest — unchanged from the prior scans):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py), which pulls real subreddit listings via Reddit's official OAuth2 Data API. It `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars were unset this session** (verified this session — `os.environ` check returned `False` for both). So — exactly as in the prior runs — this scan fell back to unrestricted web search.

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session (re-verified) |
| `WebFetch https://www.reddit.com/...` | ❌ Anthropic crawler-UA block (the structural block `reddit-scan.py` exists to route around) |
| `WebSearch allowed_domains:[reddit.com]` / `site:reddit.com` | ❌ no usable links (crawler-UA block) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion aggregations + practitioner write-ups + primary Anthropic docs |

**Provenance of the findings below:** drawn from Reddit-discussion aggregations + practitioner write-ups via unrestricted web search, cross-checked against **primary Anthropic docs** and **this repo's own surface** — **not** from direct subreddit reads. This is the documented fallback, **not** the preferred route. **Standing next-scan action (carried again): set the two Reddit creds and run `reddit-scan.py` first** so findings come from real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `Claude Code best practices reddit June 2026 subagents hooks output styles tips that actually work`
- `r/ClaudeAI Claude Code 2.0 plan mode context management lessons learned 2026`
- `Claude Code CLAUDE.md mistakes anti-patterns reddit discussion 2026 what not to do`
- `Claude Code output styles replace system prompt keep-coding-instructions frontmatter risk 2026`
- `Claude Code subagents do not inherit skills preload frontmatter context window 2026`
- `Claude Code 2.0 reddit checkpointing rewind native subagents what changed power users 2026`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Output styles](https://code.claude.com/docs/en/output-styles) and [Modifying system prompts](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts) (primary — the `keep-coding-instructions` flag + the Proactive/Explanatory/Learning built-ins)
- [Anthropic — Steering Claude Code: skills, hooks, rules, subagents and more](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more) (primary — the 7-instruction-method framing; "use a hook to enforce a rule with code")
- [Anthropic — Create custom subagents](https://code.claude.com/docs/en/sub-agents) (primary — the `skills` frontmatter preload field; subagents inherit nothing from the parent conversation)
- [Anthropic — Checkpointing](https://code.claude.com/docs/en/checkpointing) and [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) (primary)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): SmartScope (advanced best practices), ofox.ai (hooks/subagents/skills guide), explainx.ai ("all 7 instruction methods"), HeyClaude (output styles without losing coding instructions), and the upstream issue [`anthropics/claude-code#32910`](https://github.com/anthropics/claude-code/issues/32910) (subagent skill discovery).

---

## 2. Findings (4 — all checked against the prior scans + the 24-rule core set)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **A custom Claude Code output style silently REPLACES the built-in software-engineering system prompt unless you set `keep-coding-instructions: true`.** An output style is the *system-prompt tier* of steering — the highest instruction-following weight of any method, because it sits in the system prompt rather than appended to it. By default a custom style *overwrites* the `claude_code` preset (scope-narrowly, omit unrequested comments, take security seriously, **run the tests before declaring done**), so authoring a coding-adjacent style without the flag quietly turns Claude Code into a general assistant — looser diffs, skipped verification — with **no error**. The fix is a one-line frontmatter flag; the cost of missing it is invisible until it bites. | **Genuine gap (consumer-facing).** Grep of `plugins/ravenclaude-core/` + `docs/` for `output.?styl` / `keep-coding-instructions` returns **no authoring rule** — every hit is a capability-matrix **"N-A — this plugin ships no output style"** row (the core CLAUDE.md value-add table line 1060; the same N-A in microsoft-365-copilot / azure-cloud / mobile-engineering), and `keep-coding-instructions` appears **nowhere** in the repo. The repo has authoring rules for the *other* instruction-method tiers — hooks (`prefer-a-deterministic-gate-over-a-prose-rule.md`), the MCP budget, the SKILL.md body budget (06-24), `CLAUDE.md` imports — but **nothing on the output-style / system-prompt tier**, the one with the highest leverage and the silent-failure mode. |
| **H2** | **Subagents inherit nothing from the parent conversation, and don't auto-load the parent's skills — preload via the `skills:` frontmatter field (full content injected at startup); newer Claude Code (v2.1.133+) also lets them *discover* project/user/plugin skills via the Skill tool.** | **Covered.** [`knowledge/subagent-isolation-and-tooling.md`](../../../plugins/ravenclaude-core/knowledge/subagent-isolation-and-tooling.md) already documents the `skills` preload field (line 61: "**Preload** named skills into the agent at dispatch") and the writable declarative surface; the 06-13 scan + the CLAUDE.md "Delegating branch-mutating work" section cover the isolation premise. The v2.1.133+ discovery nuance (and the `#32910` "docs say don't inherit but filesystem discovery works anyway" wrinkle) is a *refinement* to that knowledge file, not a net-new best-practice. Deny-as-covered (note for a future knowledge-freshness sweep). |
| **H3** | **After two failed plan-corrections the context is contaminated — `/clear` and rewrite a precise initial prompt rather than grinding; surgically compact the failed-attempt detail after a debugging win.** | **Substantially covered + a prior deferral.** [`checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md`](../../../plugins/ravenclaude-core/best-practices/checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md) covers `/rewind` vs commits and touches `/clear`; the 06-22 scan **deferred** the CLAUDE.md-memory/context-compaction finding. The "fresh session beats a long corrected one" lesson is real but overlaps both — fold into a future context-hygiene rule if it recurs, don't ship a near-duplicate now. Defer. |
| **H4** | **Plan mode is tool-level enforced (read/search/think only, no edits) — front-load the hard thinking before context is polluted by implementation detail; break work into research → plan → implement phases.** | **Covered — duplicate.** plan-mode-TDD was a 06-09-scan finding; the core ships `route-before-spawning` + the orchestration decision trees + the Focused-Task-Execution discipline in CLAUDE.md, and `prefer-a-deterministic-gate` covers the enforce-with-code half. Deny. |

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
| **H1** | ✅ **Approve** | Passes all four. **Additive:** grep-verified — no output-style authoring rule exists; the only repo hits are "we ship no output style" N-A rows, and `keep-coding-instructions` is absent everywhere. **In-scope:** instruction-method authoring is core's home turf — this completes the ladder the prior scans built (hooks-vs-prose, MCP budget, SKILL.md body, CLAUDE.md imports) with its missing top tier. **Load-bearing:** the failure is *silent* (no error; the agent quietly drops scope/verify/security instincts on every session under that style) and the fix is one frontmatter line — the highest-value shape of a best-practice. **Low-blast:** additive markdown. | Keep it tight and cross-linked to the other instruction-method rules (`prefer-a-deterministic-gate`, the SKILL.md-body rule, `claude-md-imports`). Frame the flag name + built-in-style list as verify-at-use platform facts and the *mechanic* (a custom style replaces the system prompt) as the durable part, so the rule doesn't rot. Be explicit that the omit case (replacing the role entirely) is legitimate — the rule is "keep them *while still coding*," not "always keep them." |
| **H2** | ❌ Deny | Fails #1 — covered. The `skills` preload field + the isolation premise already live in `subagent-isolation-and-tooling.md` and the CLAUDE.md delegation section. The v2.1.133+ discovery nuance is a knowledge-file *refresh*, not a standalone rule. | Worth queuing for the next knowledge-file-staleness sweep: add the v2.1.133+ "subagents also discover the full skill catalog via the Skill tool" line + the `#32910` wrinkle to the knowledge file. |
| **H3** | ⏸️ Defer | Borderline #1. The fresh-session/`/clear`-and-rewrite + surgical-compaction lesson is real and crisp, but overlaps the checkpoints rule and the 06-22 deferred context-compaction finding. Shipping standalone would near-duplicate. | If a future scan finds the context-hygiene angle recurring AND under-covered, ship a single "a fresh session with a precise prompt beats a long contaminated one" rule grounded in the CLAUDE.md Context & Session Hygiene section + the checkpoints rule. |
| **H4** | ❌ Deny | Fails #1 — duplicate. plan-mode-TDD (06-09) + the orchestration decision trees + Focused-Task-Execution already cover it. | None — cleanly covered. |

**Net:** 1 approved (H1), 2 denied (H2/H4), 1 deferred (H3). One solid, well-grounded addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 ("don't restate what's already enforced/covered") and the prior scans' discipline (each landed exactly one tight rule).

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "Output styles replace the system prompt — keep the coding instructions when you're still coding." Sections: Why (the system-prompt tier → the silent-replacement trap → the software-engineering preset that gets dropped) / How (the re-voice-vs-replace decision, `keep-coding-instructions: true`, built-ins first, where the file lives + team scope, do/don't) / Edge cases / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/output-styles-replace-the-system-prompt-keep-coding-instructions-when-still-coding.md` | Follows the one-rule-per-file format of the existing rules. |
| 2 | Index update: → **25 rules**; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.182.0 → **0.183.0**, mirrored across all three. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json` via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. |
| 4 | CHANGELOG top entry for 0.183.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-06-29-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook — so no count-string sync is needed (verified this session). Markdown + manifest diff only; run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Output styles](https://code.claude.com/docs/en/output-styles) · [Modifying system prompts](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts)
- [Anthropic — Steering Claude Code: skills, hooks, rules, subagents and more](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)
- [Anthropic — Create custom subagents](https://code.claude.com/docs/en/sub-agents) · [Checkpointing](https://code.claude.com/docs/en/checkpointing) · [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): SmartScope, ofox.ai, explainx.ai ("all 7 instruction methods"), HeyClaude (output styles without losing coding instructions); upstream issue [`anthropics/claude-code#32910`](https://github.com/anthropics/claude-code/issues/32910).
- Prior runs: [`2026-06-09`](../2026-06-09-claude-subreddit-scan/README.md) · [`2026-06-10`](../2026-06-10-claude-subreddit-scan/README.md) · [`2026-06-11`](../2026-06-11-claude-subreddit-scan/README.md) · [`2026-06-13`](../2026-06-13-claude-subreddit-scan/README.md) · [`2026-06-22`](../2026-06-22-claude-subreddit-scan/README.md) · [`2026-06-24`](../2026-06-24-claude-subreddit-scan/README.md)
