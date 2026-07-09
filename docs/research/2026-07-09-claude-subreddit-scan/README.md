# Claude subreddit scan — research, panel decision & build plan (2026-07-09)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), 3 denied-as-covered/generic. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.188.0): **scope a skill to one workflow — the description is what triggers it.**

> This is the **thirteenth** run of this recurring scan. Prior runs (most recent first):
>
> - [2026-07-03](../2026-07-03-claude-subreddit-scan/README.md) — **compact-proactively / persist-state-before-compaction** (approved → the 07-02 deferred candidate, promoted).
> - [2026-07-02](../2026-07-02-claude-subreddit-scan/README.md) — **the OS-enforced Bash sandbox** (approved) + deferred proactive-compaction.
> - [2026-06-24](../2026-06-24-claude-subreddit-scan/README.md) — **keep-SKILL.md-bodies-lean / progressive disclosure** (approved).
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — **MCP tool-context budget** (approved → the count→cost rule).
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) · [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) · [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) · [2026-06-13](../2026-06-13-claude-subreddit-scan/README.md) · [2026-06-15](../2026-06-15-claude-subreddit-scan/README.md) · [2026-06-19](../2026-06-19-claude-subreddit-scan/README.md) · [2026-06-20](../2026-06-20-claude-subreddit-scan/README.md) · [2026-06-21](../2026-06-21-claude-subreddit-scan/README.md).
>
> Today's net-new finding (H1) is the **scope/trigger sibling** of the 06-24 approved rule. That rule (`keep-skill-bodies-lean`) owns the skill **body token-budget** axis; H1 owns a distinct axis it explicitly does not cover — how tightly to **scope** a skill and how to write its **description as the trigger**, since a skill that does too much misfires or never fires regardless of how lean its body is.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using and authoring for Claude Code effectively.

**Route note (honest — same hard block as the 07-02/07-03 runs):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (Reddit's official OAuth2 Data API), which `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` — **both env vars were unset this session** (re-verified: `os.environ.get(...)` returned `False` for both). Reddit remained hard-blocked on the direct routes:

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session (re-verified) |
| `WebSearch` with `allowed_domains:["reddit.com"]` / `WebFetch` a Reddit URL | ❌ Anthropic-crawler UA block (unchanged from prior runs) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — surfaces practitioner write-ups + Reddit-discussion **aggregations** + primary Anthropic docs (Reddit itself never loaded) |

**Provenance of the findings below:** practitioner write-ups + Reddit-discussion aggregations via unrestricted web search, cross-checked against **primary Anthropic docs** (the Agent Skills overview + the Claude Code skills doc) and **this repo's own surface** (the 28-rule core best-practice set + the 12 prior scans) — **not** direct subreddit reads (unreachable this session). This is the documented fallback. **Standing next-scan action (carried again):** set `REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET` in the routine's environment and run `reddit-scan.py` first — with the web route to Reddit UA-blocked, the OAuth2 API is the only path to real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `Claude Code skills subagents CLAUDE.md common mistakes lessons learned July 2026`
- `Claude Code skill description not triggering "does too much" split one workflow reliable invocation`
- `Anthropic agent skills description "when to use" model decides load naming reliable trigger 2026`
- `Claude Code plugin marketplace authoring best practices context budget 2026 community`

**Sources mined (cross-checked against primary docs):**

- **Anthropic primary** — [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) and [Extend Claude with skills](https://code.claude.com/docs/en/skills): "Claude uses the `name` and `description` … when deciding whether to trigger the skill"; the metadata is preloaded, the body is not; the **verb-ing + noun** naming convention; the skill-listing character cap.
- **Practitioner aggregations (several Reddit-sourced, read via search snippets):** SmartScope (advanced best practices), duet.so (skills complete guide), agentkit.best ("Subagents: Common Mistakes"), mager.co (skills vs workflows), codemeetai / buildtolaunch ("Claude Skills not working — fixes"). The "a skill that does too much won't trigger reliably / if you use *and* in the description more than once, split it / the description decides whether it fires at all" lesson recurs across these.
- Cross-checked against this repo: [`best-practices/keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md`](../../../plugins/ravenclaude-core/best-practices/keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md) (owns body token-budget), [`best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md) (determinism axis), [`best-practices/claude-md-imports-organize-they-dont-shrink-context.md`](../../../plugins/ravenclaude-core/best-practices/claude-md-imports-organize-they-dont-shrink-context.md) (always-loaded-vs-conditionally-loaded axis), and the `AGENTS.md` ≤300-char agent-description routing budget.

---

## 2. Findings (4 — all checked against the 27-rule core set + the 12 prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Scope a skill to one workflow; the `description` is the trigger surface.** Claude preloads only each skill's `name`+`description` and matches the current task against them to decide whether the skill fires — the body loads only after. So a skill that does too much fails both ways: it won't fire when it should (a compound/abstract description can't be cleanly matched to a concrete request) and it fires at the wrong moment (it triggers on a request that wanted only one of its jobs). Fix: one skill = one workflow (if the description needs "and" more than once, split it); write the description as `Use when [context]. [What it does]. [disambiguator]`; name it verb-ing+noun. | **Genuine gap (consumer-facing).** [`keep-skill-bodies-lean`](../../../plugins/ravenclaude-core/best-practices/keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md) owns the **body token-budget** axis; it mentions the description only as "make it earn its always-on cost — say what it does AND when," and states **no scope/trigger discipline**. Grep of `best-practices/` for `single responsibility` / `one workflow` / `does too much` / `too broad` → **zero hits**. `domain-plugins-extend-via-skills` owns skill-vs-agent extension, not skill scope. **Additive.** |
| **H2** | **Choose the steering surface by load-cadence × determinism** — durable facts → `CLAUDE.md`; procedures → skills; must-happen-every-time → hooks; isolated/parallel work → subagents. (The "all 7 instruction methods" framing.) | **Denied — covered by two existing rules whose union this is.** The **determinism** half is [`prefer-a-deterministic-gate-over-a-prose-rule.md`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md) (its table maps must-happen+objective → hook/CI/deny, judgment → prose). The **load-cadence** half is [`claude-md-imports-organize-they-dont-shrink-context.md`](../../../plugins/ravenclaude-core/best-practices/claude-md-imports-organize-they-dont-shrink-context.md) ("the decision is always-loaded vs conditionally-loaded"; names path-scoped rules + skills as the on-demand surfaces). A consolidated matrix rule would be a near-duplicate of the two. Deny. |
| **H3** | **CLAUDE.md is always-on context (facts); skills are on-demand context (procedures) — move a 30-line procedure out of CLAUDE.md into a skill.** | **Denied — duplicate.** This is exactly the thesis of [`claude-md-imports-organize-they-dont-shrink-context.md`](../../../plugins/ravenclaude-core/best-practices/claude-md-imports-organize-they-dont-shrink-context.md) ("a multi-step procedure that lives in CLAUDE.md is paying rent every conversation; as a skill it pays only when used"). Deny. |
| **H4** | **Context thresholds — keep newcomer sessions under ~40%, wrap by ~60%.** | **Denied — covered + volatile.** Owned by [`compact-proactively-and-persist-state-before-compaction.md`](../../../plugins/ravenclaude-core/best-practices/compact-proactively-and-persist-state-before-compaction.md) (compact at task boundaries, `/context` as the instrument) and [`mcp-tool-context-is-a-budget-...`](../../../plugins/ravenclaude-core/best-practices/mcp-tool-context-is-a-budget-enable-only-what-you-need.md). The exact %s are practitioner rules-of-thumb, already `verify-at-use` in those rules. Deny. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to every prior scan: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no *action* on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (The repo rule — CLAUDE.md "Decision review" — routes yes/no *decisions* through the tribunal; a content-additivity judgment is not one.)

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** the skill scope/trigger discipline is stated by no rule — `keep-skill-bodies-lean` is the token-budget sibling one axis over, and its own text is the proof (it treats the description as a cost line, not a trigger to scope). **In-scope:** this is *skill-authoring craft* — exactly what a plugin marketplace shipping ~670 SKILL.md files does at scale — grounded in the constitution's own ≤300-char agent-description routing discipline (the same mechanic one tier up), not generic tool-usage advice. **Load-bearing:** a skill that misfires (fires on the wrong task, or never fires) is a real, recurring cost every consumer of the plugin pays. **Low-blast:** additive markdown. | Keep it tight and cross-linked to `keep-skill-bodies-lean` so the two axes (scope/trigger vs body-token-budget) stay distinct and it doesn't read as a near-duplicate. Mark the platform specifics (the description-listing char cap, metadata-budget) `verify-at-use` — Claude Code's skill-loading mechanics evolve. |
| **H2** | ❌ Deny | Fails #1 — the two axes it unifies are each already owned (determinism → `prefer-a-deterministic-gate`; load-cadence → `claude-md-imports`). A consolidation would restate their union. | None — if a future scan finds a genuinely new lever the two rules don't cover, revisit. |
| **H3** | ❌ Deny | Fails #1 — duplicate of `claude-md-imports` (procedures belong in on-demand skills, not always-on CLAUDE.md). | None — cleanly covered. |
| **H4** | ❌ Deny | Fails #1 (covered by the two context rules) and the exact %s are volatile practitioner guidance already flagged `verify-at-use`. | None. |

**Net:** 1 approved (H1), 3 denied (H2/H3 covered, H4 covered+volatile). One solid, well-grounded addition — the missing scope/trigger sibling to the 06-24 body-budget rule — beats padding a mature 27-rule set with near-duplicates or generic tips. Consistent with house-rule #4 ("don't restate what's already enforced/covered") and every prior scan's one-tight-rule discipline.

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "Scope a skill to one workflow — the description is what triggers it." Sections: Why (description = trigger surface; both failure modes; scope/trigger vs body-budget axis; the agent-routing analog) / How to apply (one-workflow split test; the `Use when …` description shape; verb-ing+noun naming; test the trigger) / Edge cases (multi-step≠multi-workflow; chaining; surface-selection is elsewhere; non-Claude hosts) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md` | Follows the one-rule-per-file format of the existing rules. |
| 2 | Index update: → **28 rules**; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.187.4 → **0.188.0**, mirrored across all three. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json` via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. |
| 4 | CHANGELOG top entry for 0.188.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-07-09-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook — so no count-string sync is needed. Markdown + manifest diff only; run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- **Anthropic primary** — [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) · [Extend Claude with skills](https://code.claude.com/docs/en/skills) · [Best practices](https://code.claude.com/docs/en/best-practices) · [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills).
- Practitioner aggregations (read via search snippets; several Reddit-sourced): [SmartScope — advanced best practices](https://smartscope.blog/en/generative-ai/claude/claude-code-best-practices-advanced-2026/), [duet.so — skills complete guide](https://duet.so/guides/claude-code-skills-complete-guide), [agentkit.best — subagents common mistakes](https://agentkit.best/blog/vc-04-subagents-from-basic-to-deep-dive-i-misunderstood), [mager.co — skills vs workflows](https://www.mager.co/blog/2026-06-13-claude-skills-vs-workflows/), [codemeetai — how to create a Claude Code skill](https://codemeetai.substack.com/p/how-to-create-a-claude-code-skill), [buildtolaunch — Claude skills not working](https://buildtolaunch.substack.com/p/claude-skills-not-working-fix).
- Cross-checked against this repo: [`keep-skill-bodies-lean-...`](../../../plugins/ravenclaude-core/best-practices/keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md) (body token-budget sibling), [`prefer-a-deterministic-gate-...`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md) + [`claude-md-imports-...`](../../../plugins/ravenclaude-core/best-practices/claude-md-imports-organize-they-dont-shrink-context.md) (the H2 axes), [`compact-proactively-...`](../../../plugins/ravenclaude-core/best-practices/compact-proactively-and-persist-state-before-compaction.md) + [`mcp-tool-context-...`](../../../plugins/ravenclaude-core/best-practices/mcp-tool-context-is-a-budget-enable-only-what-you-need.md) (the H4 axis), `AGENTS.md` (the ≤300-char agent-description routing budget).
- Prior runs: [`2026-06-24`](../2026-06-24-claude-subreddit-scan/README.md) (the body-budget sibling) · [`2026-07-02`](../2026-07-02-claude-subreddit-scan/README.md) · [`2026-07-03`](../2026-07-03-claude-subreddit-scan/README.md).
- **Route-reality note:** direct Reddit access was blocked this session (OAuth2 creds unset; `reddit.com` UA-blocked on WebSearch/WebFetch). Findings are from indexed aggregations + primary docs, not direct subreddit reads — see §1.
