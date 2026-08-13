# Claude subreddit scan — research, panel decision & build plan (2026-07-15)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), 3 denied-as-covered/volatile. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.192.0): **drop a tier for grunt-work subagents — the strong model supervises, cheap models execute.**

> This is the **fifteenth** run of this recurring scan. Prior runs (most recent first):
>
> - [2026-07-14](../2026-07-14-claude-subreddit-scan/README.md) — **treat-repo-committed-`.claude`-config-as-untrusted-input** (approved; the _inbound_ trust-boundary sibling).
> - [2026-07-09](../2026-07-09-claude-subreddit-scan/README.md) — **scope-a-skill-to-one-workflow / the-description-is-the-trigger** (approved).
> - [2026-07-03](../2026-07-03-claude-subreddit-scan/README.md) — **compact-proactively / persist-state-before-compaction** (approved).
> - [2026-07-02](../2026-07-02-claude-subreddit-scan/README.md) — **the OS-enforced Bash sandbox** (approved) + deferred proactive-compaction.
> - [2026-06-24](../2026-06-24-claude-subreddit-scan/README.md) — **keep-SKILL.md-bodies-lean / progressive disclosure** (approved).
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — **MCP tool-context budget** (approved → the count→cost rule).
> - earlier: 2026-06-09 · 06-10 · 06-11 · 06-13 · 06-15 · 06-19 · 06-20 · 06-21.
>
> Today's net-new finding (H1) is the **cost axis** of the spawn decision. The repo already owns _what_ to fan out ([`delegate-reads-fan-out`](../../../plugins/ravenclaude-core/best-practices/delegate-reads-fan-out-keep-branch-writes-in-main.md)) and _how to brief_ it ([`focused-task-delegation`](../../../plugins/ravenclaude-core/best-practices/focused-task-delegation-beats-full-context-dumps.md)); neither owns _which model_ each worker runs. The principle is stated at the knowledge tier ([`knowledge/concepts/model-selection.md`](../../../plugins/ravenclaude-core/knowledge/concepts/model-selection.md)) but no consumer-facing best-practice makes it the dispatch-time discipline — the same knowledge-names-it / no-rule-teaches-it gap the 07-14 untrusted-config rule and the 07-02 sandbox rule were each approved to close.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent dev communities about using Claude Code effectively.

**Route note (honest — same hard block as the 07-02 / 07-03 / 07-09 / 07-14 runs):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (Reddit's official OAuth2 Data API), which `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`. Both env vars were **unset this session** (verified: both UNSET), and the direct Reddit routes stayed hard-blocked:

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session |
| `WebSearch` with `allowed_domains:["reddit.com"]` | ❌ `400 — reddit.com is not accessible to our user agent` (Anthropic-crawler UA block — unchanged from prior runs) |
| `WebFetch` of practitioner-aggregation pages (morphllm, techsy) | ❌ `403 Forbidden` (same UA block as Reddit) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — surfaces practitioner write-ups + Reddit-discussion **aggregations** via search snippets |

**Provenance of the findings below:** practitioner write-ups + Reddit-discussion aggregations read via unrestricted web-search snippets, cross-checked against **this repo's own surface** (the 33-rule core best-practice set + the `knowledge/concepts/` bank + the 14 prior scans) and, for the approved item, **this-session tool schemas** (the Agent tool `model` field; the workflow harness `opts.model` / `opts.effort`, which "inherit the main-loop model" when omitted). This is the documented fallback — **not** direct subreddit reads (unreachable this session). **Standing next-scan action (carried again):** set `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` in the routine's environment and run `reddit-scan.py` first — with the web route to Reddit UA-blocked, the OAuth2 API is the only path to real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `r/ClaudeAI Claude Code tips workflow best practices 2026`
- `reddit Claude Code hooks subagents advanced techniques June July 2026`
- `Claude Code community biggest complaints CLAUDE.md ignored context rot skills 2026`
- `Claude Code plugin skills progressive disclosure token cost best practices 2026`
- `Claude Code extended thinking ultrathink /effort July 2026 when to use reddit tips`

**Sources mined (via search snippets):** SmartScope (Claude Code advanced best-practices — hooks/subagents/context), the Anthropic/Claude blog "Steering Claude Code: CLAUDE.md, skills, hooks, subagents", MarkTechPost (Claude Code 2026 features), morphllm "Claude Code Reddit: what developers actually say", techsy/MindStudio (context-rot / `/compact`), kentgigger + decodeclaude (`/effort`, ultrathink deprecation), the Skill-authoring best-practices doc (progressive disclosure).

---

## 2. Findings (4 — all checked against the 33-rule core set + the 14 prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Assign cheaper/faster models to the subagents doing grunt work; reserve the capable model for the actual reasoning (and keep the strong model supervising).** Recurring consensus in the practitioner/Reddit aggregations: a fan-out of search/fetch/scan/summarize workers doesn't need a frontier model — and a spawned agent _inherits the parent's tier by default_, so an unset `model:` silently runs the whole fan-out at orchestrator cost. Right-size the tier at dispatch. | **Genuine gap at the best-practice tier.** The principle is _stated_ in [`knowledge/concepts/model-selection.md`](../../../plugins/ravenclaude-core/knowledge/concepts/model-selection.md) ("strong model supervises, cheap models execute … subagents are the natural place to drop a tier"), but that is a **Learn-tab teaching card, not a consumer-facing rule.** Grep of `best-practices/` for `model` / `haiku` / `sonnet` / `opus` → **zero** hits; the spawn-adjacent rules ([`delegate-reads-fan-out`](../../../plugins/ravenclaude-core/best-practices/delegate-reads-fan-out-keep-branch-writes-in-main.md), [`focused-task-delegation`](../../../plugins/ravenclaude-core/best-practices/focused-task-delegation-beats-full-context-dumps.md), [`route-before-spawning`](../../../plugins/ravenclaude-core/best-practices/route-before-spawning.md)) own _what_/_how-to-brief_/_which-specialist_, none owns _which model_. Same knowledge-names-it / no-rule-teaches-it gap the 07-14 + 07-02 rules were approved under. **Additive.** |
| **H2** | **`/effort` is the new session-level reasoning-effort dial (low…max); ultrathink keyword-triggers are deprecated (max thinking by default as of Jan 2026).** | **Denied — volatile; the durable half is subsumed.** A genuinely new mechanic, but the sources conflict (one says `/effort max/high/low` is the official knob, another says ultrathink is deprecated with max-by-default) — exactly the volatility bar that denied 07-14's H2 (nested-`.claude` precedence). The durable "match reasoning effort to task difficulty" lesson is folded into the approved H1 rule (the `opts.effort` low-for-mechanical / high-for-hardest guidance). Deny the standalone; revisit `/effort` when the UI stabilizes. |
| **H3** | **Context rot / "CLAUDE.md gets ignored when too long" — compact proactively; keep the memory file lean.** | **Denied — covered.** Owned by [`compact-proactively-and-persist-state-before-compaction`](../../../plugins/ravenclaude-core/best-practices/compact-proactively-and-persist-state-before-compaction.md) + [`precompact-hook-is-the-deterministic-enforcer`](../../../plugins/ravenclaude-core/best-practices/precompact-hook-is-the-deterministic-enforcer-of-persist-before-compaction.md) (07-03) and [`claude-md-imports-organize-they-dont-shrink-context`](../../../plugins/ravenclaude-core/best-practices/claude-md-imports-organize-they-dont-shrink-context.md). Deny (house-rule #4: don't restate what's covered). |
| **H4** | **Progressive disclosure for skills — metadata loads at startup, the SKILL.md body only when relevant; keep bodies lean.** | **Denied — covered.** Owned by [`keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail`](../../../plugins/ravenclaude-core/best-practices/keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md) (06-24) + [`scope-a-skill-to-one-workflow`](../../../plugins/ravenclaude-core/best-practices/scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md) (07-09) + [`a-skills-body-is-the-gotchas`](../../../plugins/ravenclaude-core/best-practices/a-skills-body-is-the-gotchas-the-model-doesnt-know-not-the-happy-path.md). Deny. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to every prior scan: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no _action_ on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably.

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook. _[For a lesson that IS in a knowledge/concept file but NOT in any consumer-facing best-practice, "additive" is satisfied at the best-practice tier — the 07-02 sandbox / 07-14 untrusted-config precedent: knowledge naming a lesson does not mean a rule teaches the action.]_
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** zero `best-practices/` hits for model tiering; the discipline lives only as a Learn-tab concept, and the best-practices are the consumer-facing surface agents cite at dispatch — the established knowledge-names-it / no-rule-teaches-it gap. **In-scope:** multi-agent orchestration cost is core's home turf (it ships the Team Lead + the workflow harness + a parallelism knob), and the model knob is a Claude-Code/harness-specific mechanic, not generic coding advice. **Load-bearing:** the cost of omission is observable and silent — an unset `model:` runs an N-worker fan-out at frontier tier; the two-sided edge (under-tiering forces a redo) is a real second failure. **Low-blast:** additive markdown. | Keep it distinct from the model-selection _concept_ by pitching at the **dispatch decision** (name the silent default-inheritance trap + the two-sided floor + the review-panel diversity carve-out — none fully in the concept), not by re-teaching the three tiers. Mark model **ids/tiers `verify-at-use`** (the line-up evolves; the durable fact is the shape + inherit-unless-set). Frame as a **cost** knob, explicitly _not_ a correctness/safety gate. |
| **H2** | ❌ Deny | Fails on volatility (conflicting Jan-2026 deprecation + evolving `/effort` UI — the 07-14 H2 bar). The durable "effort-to-difficulty" half is folded into H1's `opts.effort` guidance, so nothing is lost. | Revisit `/effort` as a standalone rule once the mechanic stabilizes across a couple of releases. |
| **H3** | ❌ Deny | Fails #1 — covered by the proactive-compaction pair + the imports rule. | None. |
| **H4** | ❌ Deny | Fails #1 — covered by the three skill-authoring rules. | None. |

**Net:** 1 approved (H1), 3 denied (H2 volatile, H3+H4 covered). One solid, well-grounded, cost-bearing addition — the missing _model-tier_ axis of the spawn decision — beats padding a mature 33-rule set. Consistent with house-rule #4 and every prior scan's one-tight-rule discipline.

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "Drop a tier for grunt-work subagents — the strong model supervises, cheap models execute." Sections: Why (default-inherit trap; the three tiers; knowledge-names-it/no-rule-teaches-it) / How (set `model` on the Agent-tool spawn; `opts.model`+`opts.effort` on `agent()`; the tell) / two-sided failure (under-tiering forces a redo) / Edge cases (review-panel diversity carve-out; single-agent; verify-at-use ids; cost-not-safety) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/drop-a-tier-for-grunt-work-subagents-strong-model-supervises.md` | Mirrors the one-rule-per-file format of the existing rules. |
| 2 | Index update: → **34 rules**; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.191.1 → **0.192.0**, mirrored across all three surfaces. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json` via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. |
| 4 | CHANGELOG top entry for 0.192.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-07-15-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook — so no count-string sync is needed. Markdown + manifest diff only; ran `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- Practitioner aggregations (read via unrestricted web-search snippets; several Reddit-sourced): SmartScope (Claude Code advanced best-practices — hooks/subagents/context), the Anthropic/Claude blog "Steering Claude Code: CLAUDE.md, skills, hooks, subagents", MarkTechPost (Claude Code 2026 features), morphllm ("Claude Code Reddit: what developers actually say"), techsy/MindStudio (context-rot / `/compact`), kentgigger + decodeclaude (`/effort` / ultrathink deprecation), the Skill-authoring best-practices doc (progressive disclosure).
- Cross-checked against this repo: [`knowledge/concepts/model-selection.md`](../../../plugins/ravenclaude-core/knowledge/concepts/model-selection.md), [`knowledge/model-fallback.md`](../../../plugins/ravenclaude-core/knowledge/model-fallback.md), and the spawn-adjacent best-practices ([`delegate-reads-fan-out`](../../../plugins/ravenclaude-core/best-practices/delegate-reads-fan-out-keep-branch-writes-in-main.md), [`focused-task-delegation`](../../../plugins/ravenclaude-core/best-practices/focused-task-delegation-beats-full-context-dumps.md), [`route-before-spawning`](../../../plugins/ravenclaude-core/best-practices/route-before-spawning.md)).
- Model tiers/ids verify-at-use: [Claude models overview](https://docs.claude.com/en/docs/about-claude/models) · [Choosing a model — Claude Code](https://code.claude.com/docs/en/model-config).
- Prior runs: [`2026-07-14`](../2026-07-14-claude-subreddit-scan/README.md) · [`2026-07-09`](../2026-07-09-claude-subreddit-scan/README.md) · [`2026-07-03`](../2026-07-03-claude-subreddit-scan/README.md) · [`2026-07-02`](../2026-07-02-claude-subreddit-scan/README.md) · [`2026-06-24`](../2026-06-24-claude-subreddit-scan/README.md)
