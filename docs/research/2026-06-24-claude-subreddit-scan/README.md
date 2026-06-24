# Claude subreddit scan — research, panel decision & build plan (2026-06-24)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), 1 denied-as-covered, 2 deferred. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.172.0).

> This is the **sixth** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions three-tier `deny`/`ask`/`allow` (approved), skills-vs-subagents-vs-MCP, headless-CI cost guardrails, thinking budgets.
> - [2026-06-13](../2026-06-13-claude-subreddit-scan/README.md) — git-worktrees for parallel Claude instances (approved → v0.160.0) + a correction to the `subagent-isolation` premise.
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — **MCP tool-context budget (approved → v0.161.0, the count→cost rule)**; CLAUDE.md memory hygiene (deferred), git-worktrees (already-shipped), spec-driven checkable-criteria (denied dup).
>
> Today's net-new finding (H1) is disjoint from all five prior sets. It is the **skill-authoring** sibling of the 06-22 MCP-budget rule: the same count→cost mechanic, one context tier down.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest — unchanged from the prior two scans):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py), which pulls real subreddit listings via Reddit's official OAuth2 Data API. It `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars were unset this session** (verified this session — `os.environ` check returned `False` for both). So — exactly as in the 2026-06-11 and -06-22 runs — this scan fell back to unrestricted web search.

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session (re-verified) |
| `WebFetch https://www.reddit.com/...` | ❌ **"unable to fetch from www.reddit.com"** (Anthropic crawler-UA block — the structural block `reddit-scan.py` exists to route around) |
| `WebSearch allowed_domains:[reddit.com]` / `site:reddit.com` | ❌ no usable links (crawler-UA block) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion aggregations + practitioner write-ups + primary Anthropic docs |

**Provenance of the findings below:** drawn from Reddit-discussion aggregations + practitioner write-ups via unrestricted web search, cross-checked against **primary Anthropic docs** and **this repo's own surface** — **not** from direct subreddit reads. This is the documented fallback, **not** the preferred route. **Standing next-scan action (carried for the third run): set the two Reddit creds and run `reddit-scan.py` first** so findings come from real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `Claude Code skills authoring progressive disclosure SKILL.md best practices 2026`
- `Claude Code 2.0 subagent verification pitfalls overengineering reddit June 2026`
- `Claude Code weekly usage limits Opus rate limit strategy switch sonnet reddit 2026`
- `Claude Code prompt injection MCP security untrusted data lethal trifecta 2026 mitigation`
- `Claude Code CLAUDE.md tips that actually work agents hooks output styles reddit`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Extend Claude with skills](https://code.claude.com/docs/en/skills) and [Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices) (primary — the three-tier load model + the ~500-line / progressive-disclosure guidance)
- [Anthropic — Steering Claude Code: skills, hooks, rules, subagents and more](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more) (primary — "procedural instructions belong in a skill, not CLAUDE.md")
- [Anthropic — Models, usage, and limits in Claude Code](https://support.claude.com/en/articles/14552983-models-usage-and-limits-in-claude-code) (primary — plan-with-Opus/execute-with-Sonnet, weekly caps)
- [Anthropic — Security](https://code.claude.com/docs/en/security) (primary — config-as-execution-vector, MCP trust)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): SmartScope (advanced best practices), ofox.ai (hooks/subagents/skills guide), Daniel Avila & Gideon Nguyen (progressive disclosure step-by-step), CSO Online / TrueFoundry / airia (MCP security + lethal trifecta).

---

## 2. Findings (4 — all checked against the five prior scans + the 21-rule core set)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Author `SKILL.md` for progressive disclosure: keep the body lean (~1,500–2,000 words / under ~500 lines) and push long/conditional detail into referenced files that load on demand.** A skill loads in three tiers — frontmatter (`name`+`description`) preloaded for *every* skill every session, the body read only when the skill is relevant, reference files read only when the body points at them and the case arises. So the body is a real **on-invoke context budget**; a fat body is resident for the whole task and dilutes the instructions that matter. | **Genuine gap (consumer-facing).** Grep of `docs/` + `plugins/ravenclaude-core/` for "progressive disclosure" / "SKILL.md" / "under 500 lines" returns **no skill-authoring rule** — the only core hit is `operational-console-design.md` (a UX doc, unrelated). The repo has authoring docs for *agents* (`agent-scenario-authoring.md`, the `AGENTS.md` agent-description 15K budget), *slash commands* (`authoring-plugin-slash-commands.md`), and *hooks* (`hook-authoring.md`) — but **nothing on the SKILL.md body budget.** And the repo is the worked example: it ships **~670 `SKILL.md` files**, the largest (`data-platform/.../cross-system-identity-resolution`, 583 lines) **over** the documented 500-line guideline, several more in the 300–410 range. |
| **H2** | **Procedural instructions belong in a *skill*, not in CLAUDE.md** — "a section of CLAUDE.md that has grown into a procedure rather than a fact" should move to a skill (loads on demand, costs ~nothing until used); CLAUDE.md is for *facts*. | **Partially covered + adjacent to a prior deferral.** `prefer-a-deterministic-gate-over-a-prose-rule.md` covers "prune CLAUDE.md, move enforceable rules to a hook/gate," and the 06-22 scan **deferred** the CLAUDE.md-memory-hygiene finding (stable-vs-discovered, prune history-only). The facts-vs-procedures boundary is a real, crisp decision rule, but it overlaps both — and it is best folded into H1's See-also as the "where does this content live" companion, not shipped standalone. |
| **H3** | **Model tiering: plan with Opus, execute with Sonnet; Opus burns quota faster, switch to it deliberately. Max plans carry a separate weekly cap (all-models + Sonnet-only) on top of the 5-hour session window.** | **Covered — duplicate.** `model-tiering` was a 06-09-scan finding, and the marketplace ships a whole **`ai-coding-model-guidance`** plugin plus `model-selection` as a Learn-tab concept. The weekly-cap specifics are volatile platform facts (verify-at-use), not a durable rule. Deny. |
| **H4** | **Config files are execution vectors: `.claude/settings.json` (hooks) and `.mcp.json` run code/redirect traffic before the trust dialog; review agent-config paths like code, and starve the lethal trifecta (Meta's "Rule of Two" — an unsupervised agent holds at most 2 of {private data, untrusted content, external comms}).** | **Substantially covered (core) + a domain plugin owns the depth.** The lethal trifecta was a 06-10-scan finding (not shipped as a rule); the repo's own tribunal **denies** Bash/file mutation of its own hooks/scripts (`xc.tribunal-self-disable`), `web-access-allow-deny-list-before-first-fetch.md` governs WebFetch egress, and the **`cybersecurity-grc` / `security-engineering`** plugins own agent-security depth. A net-new *consumer* rule here is plausible but security-heavy and overlaps covered territory — defer rather than rush a half-grounded security rule. |

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
| **H1** | ✅ **Approve** | Passes all four. **Additive:** no skill-authoring / progressive-disclosure rule exists in the 21-rule core set or `docs/` (grep-verified); the existing authoring docs cover agents/commands/hooks but not the SKILL.md body budget. **In-scope:** skill authoring is core's home turf, and **this marketplace's own ~670 SKILL.md files (one over the 500-line guideline) are the least-generic possible worked example** — the same framing strength as the 06-22 MCP-budget approval. **Load-bearing:** a fat body is resident for the whole task on every invocation by every consumer, *and* dilutes the skill — a real, measurable cost with a concrete fix. **Low-blast:** additive markdown. | Keep it tight and cross-linked to the 06-22 MCP-budget rule (the sibling count→cost budget, one tier up), `focused-task-delegation-...` (same desk-not-filing-cabinet discipline), and `domain-plugins-extend-via-skills-...` (the prior "should this be a skill at all" question). Fold H2's facts-vs-procedures boundary in as a See-also. Frame the word/line numbers as Anthropic's stated guidance + verify-at-use so the rule doesn't rot. |
| **H2** | ⏸️ Defer (fold into H1) | The facts-vs-procedures boundary is real and crisp, but it overlaps `prefer-a-deterministic-gate-over-a-prose-rule.md` and the 06-22 deferred memory-hygiene finding. Shipping it standalone would near-duplicate; it earns its place as H1's companion See-also ("where this content lives"), not a separate rule. | If an `/init-agent-ready` companion on "structuring your CLAUDE.md" is ever built, fold the facts-vs-procedures + stable-vs-discovered discipline in there, grounded in RavenClaude's memory model. |
| **H3** | ❌ Deny | Fails #1 — duplicate. `model-tiering` (06-09 scan) + the `ai-coding-model-guidance` plugin + the `model-selection` concept already cover plan-with-Opus/execute-with-Sonnet; the weekly-cap numbers are volatile platform facts, not a durable rule. | None — cleanly covered. |
| **H4** | ⏸️ Defer | Borderline #1. The core tribunal self-disable guard + the web-access rule + the `cybersecurity-grc`/`security-engineering` plugins already hold most of this; a net-new consumer rule is plausible but security-sensitive and overlaps covered ground. Per the prior scans' one-tight-rule discipline, don't rush a half-grounded security rule alongside the clearly-net-new H1. | If a future scan finds the config-as-execution-vector angle recurring AND under-covered for *consumers* specifically (not the marketplace's own substrate), revisit as a standalone rule grounded in `knowledge/claude-code-permissions.md` + the security plugins. |

**Net:** 1 approved (H1), 1 deferred-and-folded (H2), 1 denied (H3), 1 deferred (H4). One solid, well-grounded addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 ("don't restate what's already enforced/covered") and the prior five scans' discipline (each landed exactly one tight rule).

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "Keep SKILL.md bodies lean — let progressive disclosure carry the detail." Sections: Why (the three-tier load model → the body is the on-invoke budget) / How (lean-body target, push depth to referenced files, the frontmatter-description cost, do/don't) / Edge cases / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md` | Follows the one-rule-per-file format of the existing rules. |
| 2 | Index update: → **21 rules**; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.171.1 → **0.172.0**, mirrored across all three. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json` via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. |
| 4 | CHANGELOG top entry for 0.172.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-06-24-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook — so no count-string sync is needed (verified this session). Markdown + manifest diff only; run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Extend Claude with skills](https://code.claude.com/docs/en/skills) · [Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Anthropic — Steering Claude Code: skills, hooks, rules, subagents and more](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)
- [Anthropic — Models, usage, and limits in Claude Code](https://support.claude.com/en/articles/14552983-models-usage-and-limits-in-claude-code)
- [Anthropic — Security](https://code.claude.com/docs/en/security)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): SmartScope (advanced best practices), ofox.ai (hooks/subagents/skills guide), Daniel Avila & Gideon Nguyen (progressive disclosure step-by-step), CSO Online / TrueFoundry / airia (MCP security + lethal trifecta).
- Prior runs: [`2026-06-09`](../2026-06-09-claude-subreddit-scan/README.md) · [`2026-06-10`](../2026-06-10-claude-subreddit-scan/README.md) · [`2026-06-11`](../2026-06-11-claude-subreddit-scan/README.md) · [`2026-06-13`](../2026-06-13-claude-subreddit-scan/README.md) · [`2026-06-22`](../2026-06-22-claude-subreddit-scan/README.md)
