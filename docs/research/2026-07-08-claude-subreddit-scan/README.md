# Claude subreddit scan — research, panel decision & build plan (2026-07-08)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), 3 denied (2 covered, 1 generic). The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.187.0).

> This is the **thirteenth** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions three-tier `deny`/`ask`/`allow` (approved).
> - [2026-06-13](../2026-06-13-claude-subreddit-scan/README.md) — git-worktrees for parallel Claude instances (approved) + a correction to the `subagent-isolation` premise.
> - [2026-06-15](../2026-06-15-claude-subreddit-scan/README.md) · [2026-06-19](../2026-06-19-claude-subreddit-scan/README.md) · [2026-06-20](../2026-06-20-claude-subreddit-scan/README.md) · [2026-06-21](../2026-06-21-claude-subreddit-scan/README.md).
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — **MCP tool-context budget** (approved → the count→cost rule).
> - [2026-06-24](../2026-06-24-claude-subreddit-scan/README.md) — **keep-SKILL.md-bodies-lean / progressive disclosure** (approved).
> - [2026-07-02](../2026-07-02-claude-subreddit-scan/README.md) — **the OS-enforced Bash sandbox** (approved) + deferred **proactive-compaction**.
> - [2026-07-03](../2026-07-03-claude-subreddit-scan/README.md) — **compact-proactively / persist-state-before-compaction** (approved, the 07-02 deferred candidate).
>
> Today's net-new finding (H1) is the **skill-vs-subagent isolate-vs-steer decision** — disjoint from every prior approved rule: the delegation/routing rules (06-09, 06-13) own the *parallelism / which-specialist* axes; H1 owns the prior question of *skill-or-subagent for a single capability*, decided by where the intermediate results should live. A gap the constitution's prose implies but no rule states.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively — and, specifically for this marketplace, **plugin/skill/subagent authoring** lessons.

**Route note (honest — unchanged from the last three runs).** The sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (Reddit's official OAuth2 Data API), which `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars were unset this session** (re-verified — `os.environ` returned `False` for both). Direct Reddit reads stayed blocked; the documented fallback (unrestricted `WebSearch` + primary-doc cross-check) was used.

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset (re-verified `False`/`False`) |
| `WebSearch allowed_domains:["reddit.com"]` | ⚠️ returns indexed titles/URLs but no Reddit body (Anthropic crawler UA-block on the page itself) |
| `WebFetch https://claude.com/blog/...` (the primary steering blog) | ❌ `HTTP 403 Forbidden` — recovered the content via `WebSearch allowed_domains:["claude.com"]` snippets instead |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — practitioner write-ups + Reddit-discussion aggregations + primary Anthropic docs/blog snippets |

**Provenance of the findings below:** practitioner write-ups + Reddit-discussion aggregations via unrestricted web search, **cross-checked against the Anthropic primary "Steering Claude Code" blog and this repo's own surface** — not from direct subreddit reads (unreachable this session). **Standing next-scan action (carried again):** set `REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET` in the routine's environment and run `reddit-scan.py` first.

**Queries run (fallback route — unrestricted web search):**

- `Claude Code plugin marketplace best practices community lessons July 2026 CLAUDE.md skills subagents`
- `Claude Code output styles vs subagents vs skills when to use each 2026 tips`
- `Claude Code common mistakes context management CLAUDE.md bloat 2026 reddit`
- `"Steering Claude Code" skills hooks rules subagents output styles decision table when to use which surface`
- `Claude Code skill description frontmatter trigger writing tips skill not firing invoked reliably 2026`

**Sources mined (cross-checked against primary docs):**

- **Anthropic primary (the H1 anchor):** [Steering Claude Code: skills, hooks, subagents and more](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more) — the seven steering surfaces + the skill-vs-subagent criterion ("subagent when a side task would clutter your main conversation with intermediate results you won't reference again; skill when you want the procedure to play out inside the main thread so you can see and steer each step"). Also [Extend Claude with skills](https://code.claude.com/docs/en/skills), [Sub-agents](https://code.claude.com/docs/en/sub-agents).
- **Practitioner aggregations (several Reddit-sourced, read via search snippets):** MorphLLM ("Claude Code Reddit: What Developers Actually Say"), Nimbalyst / Totalum / Tembo subagent guides (the "3–5 concurrent subagents sweet spot"), agensi.io ("Skills Not Working? Troubleshooting"), buildtolaunch ("Skills Not Working? 5 Fixes") — the description-as-trigger lesson (H2) and the fresh-session-vs-degraded lesson (H4).

---

## 2. Findings (4 — all checked against the 27-rule core set + the 12 prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Choose skill vs subagent by the isolate-vs-steer axis, not by "can it run in parallel."** A subagent runs in its own context and returns only a distilled result — right when the intermediate results are *clutter you won't reference again* (a deep search, a log/dependency audit). A skill plays out in the main thread — right when you want to *see and steer each step*, or the intermediate state *is* the value. | **Genuine gap (consumer-facing).** The delegation/routing rules own adjacent axes: [`route-before-spawning.md`](../../../plugins/ravenclaude-core/best-practices/route-before-spawning.md) = *which* specialist; [`delegate-reads-fan-out-...`](../../../plugins/ravenclaude-core/best-practices/delegate-reads-fan-out-keep-branch-writes-in-main.md) / [`isolate-parallel-claude-instances-...`](../../../plugins/ravenclaude-core/best-practices/isolate-parallel-claude-instances-in-git-worktrees.md) = *parallelism*; [`domain-plugins-extend-via-skills-not-parallel-agents.md`](../../../plugins/ravenclaude-core/best-practices/domain-plugins-extend-via-skills-not-parallel-agents.md) = the upstream *should-this-be-a-new-agent-at-all?* (parallel-role forks). **None states the isolate-vs-steer criterion for a *single* capability.** Grep of `best-practices/` for it → zero hits. |
| **H2** | **The SKILL.md `description` is the trigger, not documentation — write it for Claude's fuzzy matcher (concrete trigger phrases + keywords the user would type), or the skill silently never fires.** | **Denied — adjacent/covered.** [`keep-skill-bodies-lean-...`](../../../plugins/ravenclaude-core/best-practices/keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md) already states the description "must say what the skill does AND when to use it … that sentence is what routes Claude to the body at all," and [`AGENTS.md`](../../../AGENTS.md) caps it at ≤300 chars + "lead with … distinctive keywords." The community's *phrasing-failure-mode* refinement (documentation-prose → fires less reliably) is real but a near-duplicate of existing coverage; belongs as an enhancement to `keep-skill-bodies-lean`, not a new rule. **Deferred enhancement candidate.** |
| **H3** | **Output styles inject into the system prompt (never compacted, highest instruction-following weight) — use judiciously; don't put durable project rules there.** | **Denied — generic + not a marketplace-authored surface.** Same disposition as the 2026-07-03 H2: generic Claude-Code tool-usage advice, not a constitution-grounded marketplace-authoring lesson (the core best-practices README forbids "generic coding advice"), and no plugin in this marketplace ships an output style. |
| **H4** | **After several auto-compactions a long session slows/degrades — start a fresh session rather than pushing through the degraded one.** | **Denied — covered.** The just-landed (v0.185.0) [`compact-proactively-and-persist-state-before-compaction.md`](../../../plugins/ravenclaude-core/best-practices/compact-proactively-and-persist-state-before-compaction.md) already carries this as its `/compact` vs `/clear` edge case: "*a fresh, sharply-prompted session beats a long one full of failed attempts.*" |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to every prior scan: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no *action* on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably.

**Approval criteria** (approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** the isolate-vs-steer criterion for a single capability is stated by no rule — the three adjacent rules own *which-specialist*, *parallelism*, and *new-agent-or-not*, all different axes. **In-scope:** skill-vs-subagent is the core authoring fork for a plugin that ships both; grounded in the Anthropic primary steering blog, not generic tips. **Load-bearing:** getting it backwards has a real, recurring cost — a skill for a noisy audit floods the window (the context-cost the budget rules fight); a subagent for a steer-as-you-go procedure hides the steps you needed to watch. **Low-blast:** additive markdown. | Keep it tightly cross-linked to the routing/fan-out/domain-plugin rules so the axes stay distinct and it doesn't read as a fourth near-duplicate delegation rule. Mark the "3–5 concurrent subagents sweet spot" + dynamic-workflows ceiling `[verify-at-use]` — practitioner/feature guidance that evolves. |
| **H2** | ❌ Deny | Fails #1 (adjacent/covered) — `keep-skill-bodies-lean` + the AGENTS.md description cap already own the description-as-router surface; the phrasing-failure-mode refinement is a near-duplicate. | Logged as a **deferred enhancement** to `keep-skill-bodies-lean` (add the "write it for the matcher, not humans" failure-mode sentence) rather than a standalone rule — pick it up in a future scan if it recurs. |
| **H3** | ❌ Deny | Fails #2 — generic tool-usage advice (2026-07-03 H2 precedent) and not a surface this marketplace's plugins author. | None — revisit only if a plugin ever ships an output style. |
| **H4** | ❌ Deny | Fails #1 — covered by the v0.185.0 compaction rule's `/compact` vs `/clear` edge case. | None — cleanly covered. |

**Net:** 1 approved (H1), 3 denied (H2 adjacent/deferred, H3 generic, H4 covered). One solid, well-grounded, primary-sourced addition beats padding a mature repo with near-duplicates or generic tips — consistent with house-rule #4 and every prior scan's one-tight-rule discipline.

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "Choose a subagent to isolate clutter, a skill to keep the work in the thread." Sections: Why (the isolate-vs-steer axis; both failure modes) / How to apply (the "watch it happen or just get the answer?" question; keep it distinct from the parallelism axis; author for the choice) / Edge cases (whole-role → agent; can-be-both; must-happen → hook; non-Claude hosts) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/subagent-isolates-clutter-skill-keeps-the-work-in-thread.md` | One-rule-per-file format of the existing rules. |
| 2 | Index update: → **28 rules**; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump 0.186.1 → **0.187.0** across all three mirrors. | `plugins/ravenclaude-core/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and the generated `copilot/plugin.json` (via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. |
| 4 | CHANGELOG top entry for 0.187.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-07-08-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**`, `plugins/*/copilot/**`, and `docs/**` are all already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook — so no count-string sync is needed. Markdown + manifest diff only; run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- **Anthropic primary:** [Steering Claude Code: skills, hooks, subagents and more](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more) (the skill-vs-subagent criterion — the H1 anchor) · [Extend Claude with skills](https://code.claude.com/docs/en/skills) · [Sub-agents](https://code.claude.com/docs/en/sub-agents) · [Orchestrate subagents at scale with dynamic workflows](https://code.claude.com/docs/en/workflows) (the concurrency ceiling — `[verify-at-use]`).
- Practitioner aggregations (read via search snippets; several Reddit-sourced): MorphLLM "Claude Code Reddit: What Developers Actually Say"; Nimbalyst / Totalum / Tembo subagent guides (the 3–5 concurrent sweet spot); agensi.io + buildtolaunch skill-troubleshooting (the H2 description-as-trigger lesson).
- Cross-checked against this repo: `best-practices/route-before-spawning.md`, `delegate-reads-fan-out-keep-branch-writes-in-main.md`, `isolate-parallel-claude-instances-in-git-worktrees.md`, `domain-plugins-extend-via-skills-not-parallel-agents.md`, `keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md`, `compact-proactively-and-persist-state-before-compaction.md`.
- Prior runs: [`2026-07-02`](../2026-07-02-claude-subreddit-scan/README.md) · [`2026-07-03`](../2026-07-03-claude-subreddit-scan/README.md).
- **Route-reality note:** direct Reddit access was blocked this session (OAuth2 creds unset; page UA-blocked; the primary blog 403'd on WebFetch and was recovered via WebSearch snippets). Findings are from indexed aggregations + primary docs/blog, not direct subreddit reads — see §1.
