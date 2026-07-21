# Claude subreddit scan — research, panel decision & build plan (2026-07-21)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), 3 denied-as-covered/adjacent. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.207.0): **build a capability as CLI + Skill first — reach for MCP only when the state lives in someone else's running system.**

> This is the **sixteenth** run of this recurring scan. Prior runs (most recent first):
>
> - [2026-07-15](../2026-07-15-claude-subreddit-scan/README.md) — **drop-a-tier-for-grunt-work-subagents** (approved; the cost axis of the spawn decision).
> - [2026-07-14](../2026-07-14-claude-subreddit-scan/README.md) — **treat-repo-committed-`.claude`-config-as-untrusted-input** (approved; the _inbound_ trust-boundary sibling).
> - [2026-07-09](../2026-07-09-claude-subreddit-scan/README.md) — **scope-a-skill-to-one-workflow / the-description-is-the-trigger** (approved).
> - [2026-07-03](../2026-07-03-claude-subreddit-scan/README.md) — **compact-proactively / persist-state-before-compaction** (approved).
> - [2026-07-02](../2026-07-02-claude-subreddit-scan/README.md) — **the OS-enforced Bash sandbox** (approved).
> - [2026-06-24](../2026-06-24-claude-subreddit-scan/README.md) — **keep-SKILL.md-bodies-lean / progressive disclosure** (approved).
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — **MCP tool-context budget** (approved → the count→cost rule).
> - earlier: 2026-06-09 · 06-10 · 06-11 · 06-13 · 06-15 · 06-19 · 06-20 · 06-21.
>
> Today's net-new finding (H1) is the **design-time upstream** of the 06-22 MCP-budget rule. That rule owns the _runtime_ question — "which of the MCP servers I've enabled should stay on, given the schema tax?" H1 owns the disjoint _authoring_ question it doesn't touch: "should this new capability be an MCP server **at all**, or a CLI + Skill?" The discriminator (Skill = _how_ here / MCP = _what's true over there_) recurs across independent 2026 practitioner guides and is the same knowledge-names-it / no-rule-teaches-it shape the 07-15 and 07-14 rules were each approved to close.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent dev communities about using Claude Code effectively.

**Route note (honest — same hard block as the 07-02 / 07-03 / 07-09 / 07-14 / 07-15 runs):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (Reddit's official OAuth2 Data API), which `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`. Both env vars were **unset this session** (verified: both UNSET), and every direct Reddit route stayed hard-blocked:

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session |
| `WebSearch` with `allowed_domains:["reddit.com"]` | ❌ `400 — reddit.com is not accessible to our user agent` (Anthropic-crawler UA block — unchanged from prior runs) |
| `WebFetch https://www.reddit.com/...json` (+ `old.reddit.com`) | ❌ "Claude Code is unable to fetch from www.reddit.com" / `old.reddit.com` (same UA block) |
| `WebFetch` of a public redlib mirror + practitioner-aggregation pages (jngiam.bearblog.dev) | ❌ `403 Forbidden` (same UA block class) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — surfaces practitioner write-ups + Reddit-discussion **aggregations** via search snippets |

That is **≥5 distinct routes probed** before falling back — the same falsifiability bar this scan holds for a positive claim (per the repo's own "don't falsely claim you can't" discipline). Reddit's first-party listings are genuinely unreachable by this agent's crawler; the fallback is documented and unchanged from the prior five runs.

**Provenance of the findings below:** practitioner write-ups + Reddit-discussion aggregations read via unrestricted web-search snippets, cross-checked against **this repo's own surface** (the 34-rule core best-practice set + the `knowledge/` bank + the 15 prior scans) and, for the approved item, the closest existing rules read in full ([`mcp-tool-context-is-a-budget`](../../../plugins/ravenclaude-core/best-practices/mcp-tool-context-is-a-budget-enable-only-what-you-need.md), [`claude-md-imports`](../../../plugins/ravenclaude-core/best-practices/claude-md-imports-organize-they-dont-shrink-context.md), [`prefer-a-deterministic-gate`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md)). This is the documented fallback — **not** direct subreddit reads (unreachable this session). **Standing next-scan action (carried again):** set `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` in the routine's environment and run `reddit-scan.py` first — with the web route to Reddit UA-blocked, the OAuth2 API is the only path to real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `r/ClaudeAI Claude Code best tips subagents hooks 2026 discussion`
- `ClaudeAI subreddit CLAUDE.md context management multi-agent workflow tips July 2026`
- `Claude Code July 2026 CLAUDE.md ignored too long instruction adherence degrades curate`
- `Claude Code skills vs MCP server prefer CLI wrapper 2026 community best practice`
- `Claude Code subagents parallel context isolation gotcha return only summary 2026`

**Sources mined (cross-checked against this repo):**

- **Skills-vs-MCP practitioner guides** — jngiam.bearblog.dev ("MCPs, CLIs, and skills: when to use what?"), Verdent ("Claude Skills vs MCP: When CLI+Skills Beats MCP"), DEV Community ("Claude Code Skills vs MCP Servers … in 2026"), morphllm ("Skills vs MCP vs Plugins: Complete Guide 2026"). The recurring formulations: _"A Skill tells the agent 'how do we do X here?' while an MCP server tells the agent 'what is true right now over there?'"_ and _"build everything you can as CLI + Skill first, and reach for MCP only when the useful state genuinely lives inside someone else's running system"_ (many Skills, few MCP servers).
- **CLAUDE.md-adherence discourse (H2)** — Pathrule ("Why Claude Code Ignores CLAUDE.md"), DEV ("I Wrote 200 Lines of Rules for Claude Code. It Ignored Them All."), TECHSY ("CLAUDE.md Best Practices: 9 Rules for 2026"): the attention-budget framing ("~150–200 instructions before signal degrades", "every rule you add makes every other rule slightly less likely to be followed").
- **Subagent-isolation guides (H4)** — Tembo, HackerNoon, ClaudeWorld, the Anthropic sub-agents docs: "the lead sees only the summary the subagent returns; subagents cannot see the parent context."
- **Cross-checked against this repo:** [`mcp-tool-context-is-a-budget`](../../../plugins/ravenclaude-core/best-practices/mcp-tool-context-is-a-budget-enable-only-what-you-need.md), [`claude-md-imports-organize-they-dont-shrink-context`](../../../plugins/ravenclaude-core/best-practices/claude-md-imports-organize-they-dont-shrink-context.md), [`prefer-a-deterministic-gate-over-a-prose-rule`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md), [`keep-skill-bodies-lean`](../../../plugins/ravenclaude-core/best-practices/keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md), and the `structured-output` / `subagent-isolates-clutter-skill` / `delegate-reads-fan-out` rules.

---

## 2. Findings (4 — all checked against the 34-rule core set + the 15 prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Build a new capability as CLI + Skill first; reach for MCP only when the state lives in someone else's running system.** The 2026-hardened discriminator: a **Skill** answers "how do we do X _here_?" (a procedure/methodology, ~30–50 tokens until invoked); an **MCP server** answers "what is true right now _over there_?" (live external state, full schema tax every session). Modern models write and run code reliably, so a thin CLI + Skill is a native loop; teams run many Skills and few MCP servers. | **Genuine gap at the best-practice tier.** [`mcp-tool-context-is-a-budget`](../../../plugins/ravenclaude-core/best-practices/mcp-tool-context-is-a-budget-enable-only-what-you-need.md) owns the **runtime** axis ("enable only what you need", lazy-load, prune the enabled set) and explicitly says "the lesson isn't 'MCP is bad'" — it assumes you already have servers. **No rule owns the design-time selection heuristic** — "should this be a Skill or an MCP server _at all_?" Grep of `best-practices/` for `CLI`/`prefer.*skill`/`how to do x`/`whats true` → only incidental hits (Copilot-host notes in the skill rules), none owning the choice. **Additive**, and doubly on-brand for a marketplace that ships **both** skills and bundled MCP servers (the `mcp-builder` skill exists for when MCP _is_ right). |
| **H2** | **CLAUDE.md has a count-based adherence budget, not just a token budget — past ~150–200 instructions / ~200 lines, adherence degrades uniformly; curate ruthlessly, every rule you add weakens the others.** The dominant 2026 community complaint ("I wrote 200 lines of rules, it ignored them all"). | **Denied — substantially covered / residue too thin for a standalone rule.** Squeezed between two existing rules: [`claude-md-imports`](../../../plugins/ravenclaude-core/best-practices/claude-md-imports-organize-they-dont-shrink-context.md) already cites the "keep it under ~200 lines" guidance **and** the adherence penalty ("longer always-loaded instructions consume more context and reduce adherence") and owns the token/relocation axis, and [`prefer-a-deterministic-gate-over-a-prose-rule`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md) owns "prune the file / escalate a critical prose rule to a hook or CI gate." The non-overlapping residue (curation against a _count_ ceiling) is real but thin — better as a one-sentence augmentation to the imports rule than a 35th standalone file. **Deny; note as a candidate micro-edit to `claude-md-imports`.** |
| **H3** | **Plan-mode-first — always enter plan mode (read-only architect pass) before letting the agent touch files; it proposes and defends a plan up front for a better result.** | **Denied — covered + host-specific.** The repo's root [`CLAUDE.md`](../../../CLAUDE.md) already sets a **"Plan-mode default"** for non-trivial changes (Keep/Update/Deny before writing), and `design_checkins` in the plugin constitution owns the "surface the structural decision first" discipline. Plan mode is also a Claude-Code UI affordance, not a portable cross-tool consumer discipline. Nothing net to author. Deny. |
| **H4** | **Subagent context-isolation gotcha: a subagent runs in its own window and returns only its final summary — the parent can't see the subagent's context, so hand it a self-contained brief and require a structured return.** | **Denied — duplicate, fully owned.** Owned by [`structured-output-protocol-for-all-agent-handoffs`](../../../plugins/ravenclaude-core/best-practices/structured-output-protocol-for-all-agent-handoffs.md), [`focused-task-delegation-beats-full-context-dumps`](../../../plugins/ravenclaude-core/best-practices/focused-task-delegation-beats-full-context-dumps.md), [`subagent-isolates-clutter-skill-keeps-the-work-in-thread`](../../../plugins/ravenclaude-core/best-practices/subagent-isolates-clutter-skill-keeps-the-work-in-thread.md), and the `knowledge/subagent-isolation-and-tooling.md` file. Deny. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to every prior scan: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no _action_ on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (The repo rule — CLAUDE.md "Decision review" — routes yes/no _decisions_ through the tribunal; a content-additivity judgment is not one.)

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (core **or** a domain plugin). _For a heuristic that IS gestured at by an adjacent rule but NOT owned by any rule, "additive" is satisfied only if the non-overlapping core is load-bearing enough to stand alone — otherwise it's a micro-edit, not a new rule (the H2 disposition)._
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** the design-time Skill-vs-MCP selection heuristic is stated by no rule; the MCP-budget rule is the _runtime_ sibling and explicitly assumes the servers already exist. **In-scope:** integration-mechanism selection is core's home turf, and it's _doubly_ on-point for a marketplace that ships both skills and bundled MCP servers (and an `mcp-builder` skill) — "which mechanism for this capability" is a live authoring decision here. **Load-bearing:** the wrong default (reach for MCP) pays the full schema tax every session for a job a CLI + Skill delivers for ~30–50 tokens — an observable, recurring cost. **Low-blast:** additive markdown. | Keep it distinct from the runtime MCP-budget rule — frame it explicitly as the _upstream, design-time_ choice ("add a server at all?") vs. that rule's _runtime_ prune ("keep the servers I enabled?"). Mark the token figures + "many Skills, few servers" shape `verify-at-use` (community measurements move); state the discriminator (Skill=how-here / MCP=what's-true-over-there) as the durable part. State the honest MCP case (genuinely live external state) so the rule reads as a tie-breaker, not a ban. |
| **H2** | ❌ Deny | Fails #1 at the standalone-rule bar. The adherence-degradation angle is already cited by `claude-md-imports` and the "prune / escalate to a gate" action is owned by `prefer-a-deterministic-gate`; the residue (count-based curation) is too thin to justify a 35th file. | Real enough to be worth a **one-sentence augmentation** to `claude-md-imports` ("even always-loaded instructions compete for a finite adherence budget measured in rule count — curate, don't just relocate"). Logged for a future micro-edit; not a new rule. |
| **H3** | ❌ Deny | Fails #1 and #2 — covered by the root CLAUDE.md "Plan-mode default" + `design_checkins`, and it's a Claude-Code UI habit, not a portable cross-tool discipline. | None. |
| **H4** | ❌ Deny | Fails #1 — duplicate. Owned by the structured-output + focused-delegation + subagent-isolation rules and the isolation knowledge file. | None. |

**Net:** 1 approved (H1), 3 denied (H2 residue-too-thin/logged-as-micro-edit, H3 covered/host-specific, H4 duplicate). One solid, well-grounded addition — the missing _design-time_ upstream to the runtime MCP-budget rule — beats padding a mature 34-rule set. Consistent with house-rule #4 ("don't restate what's already enforced/covered") and every prior scan's one-tight-rule discipline.

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "Build a capability as CLI + Skill first — reach for MCP only when the state lives in someone else's running system." Sections: Why (the discriminator; runtime-budget sibling; the count→cost tax) / How (the discriminator table + Do/Don't) / Edge cases (genuinely-live-state = the MCP case; marketplace ships both; token figures verify-at-use; non-Claude hosts) / See also / Provenance. Mirrors the one-rule-per-file structure of the existing rules. | `plugins/ravenclaude-core/best-practices/build-cli-plus-skill-first-reach-for-mcp-for-live-external-state.md` | Follows the existing rule format (structure mirrors the mcp-budget rule). |
| 2 | Index update: → **35 rules**; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.206.0 → **0.207.0**, mirrored across all three surfaces. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json` via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. |
| 4 | CHANGELOG top entry for 0.207.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-07-21-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook — so no count-string sync is needed. Markdown + manifest diff only; ran `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- Skills-vs-MCP practitioner guides (read via search snippets; several Reddit-sourced): jngiam.bearblog.dev ("MCPs, CLIs, and skills: when to use what?"), Verdent ("Claude Skills vs MCP: When CLI+Skills Beats MCP"), DEV Community ("Claude Code Skills vs MCP Servers … in 2026"), morphllm ("Claude Code Skills vs MCP vs Plugins: Complete Guide 2026").
- CLAUDE.md-adherence discourse (H2): Pathrule ("Why Claude Code Ignores CLAUDE.md"), DEV ("I Wrote 200 Lines of Rules for Claude Code. It Ignored Them All."), TECHSY ("CLAUDE.md Best Practices: 9 Rules for 2026").
- Subagent-isolation guides (H4): Tembo, HackerNoon, ClaudeWorld, the Anthropic [sub-agents docs](https://code.claude.com/docs/en/sub-agents).
- Cross-checked against this repo: [`mcp-tool-context-is-a-budget`](../../../plugins/ravenclaude-core/best-practices/mcp-tool-context-is-a-budget-enable-only-what-you-need.md) · [`claude-md-imports`](../../../plugins/ravenclaude-core/best-practices/claude-md-imports-organize-they-dont-shrink-context.md) · [`prefer-a-deterministic-gate`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md).
- Prior runs: [`2026-07-15`](../2026-07-15-claude-subreddit-scan/README.md) · [`2026-07-14`](../2026-07-14-claude-subreddit-scan/README.md) · [`2026-07-09`](../2026-07-09-claude-subreddit-scan/README.md) · [`2026-07-03`](../2026-07-03-claude-subreddit-scan/README.md) · [`2026-06-22`](../2026-06-22-claude-subreddit-scan/README.md)
