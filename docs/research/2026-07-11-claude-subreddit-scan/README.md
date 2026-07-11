# Claude subreddit scan — research, panel decision & build plan (2026-07-11)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 5 findings surfaced → **1 approved** (net-new), 4 denied-as-covered / denied-by-precedent. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.190.0): **a skill's body is the gotchas the model doesn't know — not the happy path it does.**

> This is the **fourteenth** run of this recurring scan. Prior runs (most recent first):
>
> - [2026-07-09](../2026-07-09-claude-subreddit-scan/README.md) — **scope a skill to one workflow / the description is the trigger** (approved — the skill scope/trigger axis).
> - [2026-07-03](../2026-07-03-claude-subreddit-scan/README.md) — **compact-proactively / persist-state-before-compaction** (approved).
> - [2026-07-02](../2026-07-02-claude-subreddit-scan/README.md) — **the OS-enforced Bash sandbox** (approved) + deferred proactive-compaction.
> - [2026-06-24](../2026-06-24-claude-subreddit-scan/README.md) — **keep-SKILL.md-bodies-lean / progressive disclosure** (approved).
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — **MCP tool-context budget** (approved).
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) · [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) · [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) · [2026-06-13](../2026-06-13-claude-subreddit-scan/README.md) · [2026-06-15](../2026-06-15-claude-subreddit-scan/README.md) · [2026-06-19](../2026-06-19-claude-subreddit-scan/README.md) · [2026-06-20](../2026-06-20-claude-subreddit-scan/README.md) · [2026-06-21](../2026-06-21-claude-subreddit-scan/README.md).
>
> Today's net-new finding (H1) is the **third skill-authoring sibling.** The 06-24 rule (`keep-skill-bodies-lean`) owns the body's **length** (on-invoke token budget); the 07-09 rule (`scope-a-skill-to-one-workflow`) owns the **description** (whether the skill fires). Neither states **which content earns a place in the lean body** — the axis H1 owns: the failure modes the model can't infer, not the happy path it already knows.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using and authoring for Claude Code effectively.

**Route note (honest — same hard block as the 07-02/07-03/07-09 runs):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (Reddit's official OAuth2 Data API), which `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` — **both env vars were unset this session** (re-verified: `os.environ.get(...)` returned `False` for both). Reddit remained hard-blocked on the direct routes:

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session (re-verified) |
| `WebFetch` a Reddit URL / a `claude.com` blog | ❌ HTTP 403 (Anthropic-crawler UA block on Reddit; `claude.com/blog` also 403'd this session — re-routed via `WebSearch` per the route ladder) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — surfaces practitioner write-ups + Reddit-discussion **aggregations** + primary Anthropic docs/blog *content* (via search snippets), even where a direct `WebFetch` of the page 403s |

**Provenance of the findings below:** practitioner write-ups + Reddit-discussion aggregations via unrestricted web search, cross-checked against **primary Anthropic sources** (the *Lessons from building Claude Code: How we use skills* engineering blog; the Skill authoring best-practices doc; the Agent Skills overview; the Agent Teams doc; the Output styles doc) read **via search snippets** (a direct `WebFetch` of `claude.com/blog/...` 403'd — the WebFetch→WebSearch re-route is the documented route-ladder move), and against **this repo's own surface** (the 28-rule core best-practice set + the 13 prior scans). **Standing next-scan action (carried again):** set `REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET` in the routine's environment and run `reddit-scan.py` first — it is the only path to real subreddit listings while the web route stays UA-blocked.

**Queries run (fallback route — unrestricted web search):**

- `r/ClaudeAI Claude Code tips best practices July 2026`
- `Claude Code agent teams multi-agent communication vs subagents 2026 when to use` / `…overkill cost when NOT to use…`
- `Claude Code output styles vs CLAUDE.md when to use community 2026` / `…replaces system prompt lost coding instructions footgun keep-coding-instructions`
- `Claude Code plan mode discipline lessons reddit 2026`
- `Claude Code subagent model selection haiku sonnet opus cost per-agent 2026 tip reddit`
- `Claude Code CLAUDE.md too long ignored context rot "under 200 lines" reddit 2026 lesson`
- `Anthropic "lessons from building Claude Code" how we use skills gotchas section failure points what model already knows`

**Sources mined (cross-checked against primary docs — see §5):** morphllm / aitooldiscovery ("Claude Code Reddit: what developers actually say/use, 2026"), knightli / claudefast / turingcollege / shipyard / dailydoseofds (agent teams vs subagents), heyclau.de / eesel / explainx (output styles), claudedirectory / codewithmukesh / vibecodingacademy (plan mode), Roan Monteiro on Medium + claudefast (subagent model routing), xda-developers / buildthisnow ("200-line CLAUDE.md" context-rot), genaiunplugged + the two Anthropic primaries (the Gotchas-section lesson).

---

## 2. Findings (5 — all checked against the 28-rule core set + the 13 prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **A skill's body should be the failure modes / gotchas the model can't infer, not the happy path it already knows.** Claude already knows the happy path (write the SQL, call the API); the marginal value a skill adds is the local, non-inferable truth — an append-only `subscriptions` table whose "current" row is the highest version not the newest `created_at`; a `@request_id`/`trace_id` field-name mismatch across two services; a staging endpoint that returns `200` even when the webhook never processed. Anthropic (running hundreds of skills in Claude Code): *"the highest-signal content in any skill is the Gotchas section"*; the authoring docs: *"only add context Claude doesn't already have."* A body padded with happy-path exposition spends the on-invoke budget AND buries the gotchas that would have changed the outcome. | **Genuine gap (consumer-facing).** The two existing skill rules own different axes: [`keep-skill-bodies-lean`](../../../plugins/ravenclaude-core/best-practices/keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md) owns body **length** (target ~1,500 words, push depth to `references/`); [`scope-a-skill-to-one-workflow`](../../../plugins/ravenclaude-core/best-practices/scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md) owns the **description/trigger**. Grep of `best-practices/` for `gotcha` / `already know` / `only add context` / `failure mode`-as-content / `happy path` → **zero hits** on the content-value axis. **Additive.** |
| **H2** | **Agent Teams vs subagents — reach for a *team* only when parallel *exploration with cross-talk* adds value; default to subagents.** Teammates message each other + share a task list (coordination); subagents are fire-and-forget isolated workers. Overreach = a team where a subagent (or single agent) suffices. | **Denied — covered.** [`knowledge/dynamic-workflows.md`](../../../plugins/ravenclaude-core/knowledge/dynamic-workflows.md) (reconciled after the 2026-06-20 scan) already carries the full agent-teams treatment: the four parts (lead / teammates / shared task list / mailbox), the peer-messaging-vs-report-back distinction, the "Choosing an orchestration shape" aid, and the hub-and-spoke-constitution tradeoff. Deny. |
| **H3** | **Output styles replace the default coding system prompt; set `keep-coding-instructions: true` (a real footgun); output styles = communication, CLAUDE.md = project policy.** | **Denied — precedent (twice) + generic.** Proposed and denied as **generic Claude-Code usage advice** (not a constitution-grounded marketplace-authoring lesson) in the [2026-06-20 scan (H4)](../2026-06-20-claude-subreddit-scan/README.md) and the [2026-07-03 scan (H2)](../2026-07-03-claude-subreddit-scan/README.md). Both left the standing revisit condition "if a future scan finds a marketplace-specific angle (e.g. a plugin *authoring* an output style)" — not met this run. Deny. |
| **H4** | **Subagent model routing — pin a cheaper model (Haiku) to read-only / mechanical subagents in their frontmatter; reserve Opus for reasoning/review. "Haiku triages, Sonnet builds, Opus reviews."** | **Denied — covered (and owned by dedicated plugins).** [`knowledge/concepts/model-selection.md`](../../../plugins/ravenclaude-core/knowledge/concepts/model-selection.md) states the exact lesson verbatim — *"Subagents are the natural place to drop a tier: the lead reasons in Sonnet/Opus, the workers grind in Haiku"* — and the general routing-ladder craft is owned by [`claude-app-engineering/best-practices/right-size-with-a-routing-ladder.md`](../../../plugins/claude-app-engineering/best-practices/right-size-with-a-routing-ladder.md) + the `llm-routing-ladder` skill + `ai-coding-model-guidance`. Deny. |
| **H5** | **Keep CLAUDE.md short (~150–200 lines) — it's loaded every turn; every vague rule dilutes attention on the critical ones ("context rot").** | **Denied — covered.** [`prefer-a-deterministic-gate-over-a-prose-rule.md`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md) states it verbatim — *"an over-long CLAUDE.md makes every rule weaker … the model effectively ignores half of it — and you can't predict which half"* — and [`claude-md-imports-organize-they-dont-shrink-context.md`](../../../plugins/ravenclaude-core/best-practices/claude-md-imports-organize-they-dont-shrink-context.md) owns the length/prune half (opens on the "keep it under ~200 lines" guidance). Deny. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to every prior scan: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no *action* on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (The repo rule routes yes/no *decisions* through the tribunal; a content-additivity judgment is not one.)

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** the content-value axis is stated by no rule — grep of `best-practices/` for `gotcha`/`already know`/`only add context`/`happy path` returns zero, and the two existing skill rules provably own *length* and *trigger*, not *content*. **In-scope:** skill-authoring craft grounded in **two Anthropic primaries** (the engineering blog + the authoring-best-practices doc), directly serving a marketplace of ~670 SKILL.md files — the same lane that admitted the 06-24 and 07-09 skill rules, not generic tool-usage advice. **Load-bearing:** a skill that re-teaches the happy path adds on-invoke cost for zero marginal value (the "73% of audited community skills scored below 60" failure), and a missing gotcha is exactly the silent failure the rule prevents. **Low-blast:** additive markdown. | Keep it tightly cross-linked to its two siblings so the three axes (trigger / length / content) stay distinct and it doesn't read as a near-duplicate of `keep-skill-bodies-lean`. Mark the platform specifics + the "73%" figure `verify-at-use`. |
| **H2** | ❌ Deny | Fails #1 — `knowledge/dynamic-workflows.md` already carries the full agent-teams-vs-subagents treatment (reconciled after the 06-20 scan). | None — revisit only if a genuinely new coordination lever surfaces. |
| **H3** | ❌ Deny | Fails #2 (generic) with two standing denial precedents; the marketplace-specific revisit condition is unmet. | None — revisit if a plugin ever ships/authors an output style. |
| **H4** | ❌ Deny | Fails #1 — `knowledge/concepts/model-selection.md` states the subagent-drop-a-tier lesson verbatim, and the routing-ladder craft is owned by two dedicated plugins. | None — cleanly covered. |
| **H5** | ❌ Deny | Fails #1 — covered verbatim by `prefer-a-deterministic-gate` (attention dilution) + `claude-md-imports` (length/prune). | None — cleanly covered. |

**Net:** 1 approved (H1), 4 denied (H2/H4/H5 covered, H3 covered-by-precedent + generic). One solid, well-grounded addition — the missing content-value sibling to the two existing skill rules, uniquely backed by two Anthropic primaries — beats padding a mature 28-rule set with near-duplicates or generic tips. Consistent with house-rule #4 ("don't restate what's already covered") and every prior scan's one-tight-rule discipline.

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "A skill's body is the gotchas the model doesn't know — not the happy path it does." Sections: Why (the model knows the happy path; the marginal value is non-inferable failure modes; the content-value axis vs its two siblings; the two Anthropic primaries) / How to apply (give every non-trivial skill a Gotchas section; the "does the model already know this?" cut test; grow gotchas from real runs; question a gotcha-less skill) / Edge cases (new *capabilities* are the exception; a single orienting sentence is fine; long gotchas → `references/`; non-Claude hosts) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/a-skills-body-is-the-gotchas-the-model-doesnt-know-not-the-happy-path.md` | Follows the one-rule-per-file format of the existing rules. |
| 2 | Index update: → **29 rules**; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.189.0 → **0.190.0**, mirrored across all three. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json` via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. |
| 4 | CHANGELOG top entry for 0.190.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-07-11-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook — so no count-string sync is needed. Markdown + manifest diff only; run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- **Anthropic primary** — [Lessons from building Claude Code: How we use skills](https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills) (the "highest-signal content is the Gotchas section" lesson + the three concrete gotcha examples) · [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) ("only add context Claude doesn't already have; the context window is a public good") · [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) · [Extend Claude with skills](https://code.claude.com/docs/en/skills) · [Best practices](https://code.claude.com/docs/en/best-practices) · [Agent Teams](https://code.claude.com/docs/en/agent-teams) (H2 covered-check) · [Output styles](https://code.claude.com/docs/en/output-styles) (H3 covered-check). Read via search snippets — a direct `WebFetch` of `claude.com/blog/...` 403'd this session.
- Practitioner aggregations (read via search snippets; several Reddit-sourced): [morphllm — Claude Code Reddit](https://www.morphllm.com/claude-code-reddit), [genaiunplugged — skills/commands/hooks/agents](https://genaiunplugged.substack.com/p/claude-code-skills-commands-hooks-agents), [knightli — subagents vs agent teams](https://knightli.com/en/2026/04/22/claude-code-subagents-vs-agent-teams/), [heyclau.de — output styles without losing coding instructions](https://heyclau.de/entry/guides/claude-code-output-styles-keep-coding-instructions), [Roan Monteiro — subagent model routing (Medium)](https://medium.com/@roanmonteiro/claude-code-subagent-model-routing-stop-paying-for-opus-on-haiku-work-ee76dc32cb88), [xda-developers — the 200-line CLAUDE.md](https://www.xda-developers.com/gave-claude-code-200-line-claudemd-worst-decision-made/).
- Cross-checked against this repo: [`keep-skill-bodies-lean-...`](../../../plugins/ravenclaude-core/best-practices/keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md) + [`scope-a-skill-to-one-workflow-...`](../../../plugins/ravenclaude-core/best-practices/scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md) (the two skill-authoring siblings), [`knowledge/dynamic-workflows.md`](../../../plugins/ravenclaude-core/knowledge/dynamic-workflows.md) (H2), [`knowledge/concepts/model-selection.md`](../../../plugins/ravenclaude-core/knowledge/concepts/model-selection.md) + [`claude-app-engineering/best-practices/right-size-with-a-routing-ladder.md`](../../../plugins/claude-app-engineering/best-practices/right-size-with-a-routing-ladder.md) (H4), [`prefer-a-deterministic-gate-...`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md) + [`claude-md-imports-...`](../../../plugins/ravenclaude-core/best-practices/claude-md-imports-organize-they-dont-shrink-context.md) (H5).
- Prior runs: [`2026-07-09`](../2026-07-09-claude-subreddit-scan/README.md) (the trigger sibling) · [`2026-06-24`](../2026-06-24-claude-subreddit-scan/README.md) (the length sibling) · [`2026-07-03`](../2026-07-03-claude-subreddit-scan/README.md) + [`2026-06-20`](../2026-06-20-claude-subreddit-scan/README.md) (the H3 output-styles denials).
- **Route-reality note:** direct Reddit access was blocked this session (OAuth2 creds unset; `reddit.com` UA-blocked on WebSearch/WebFetch; `claude.com/blog` 403 on WebFetch → re-routed via WebSearch). Findings are from indexed aggregations + primary-doc snippets, not direct subreddit/blog reads — see §1.
