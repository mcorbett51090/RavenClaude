# Claude subreddit scan — research, panel decision & build plan (2026-07-06)

**Author:** `claude` (automated scheduled routine)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new, the pre-teed-up 07-02 deferral), 2 denied-as-covered, 1 deferred. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.185.0 — 27 rules, was 26).

> This is a recurring scan (the 9th run). Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions three-tier `deny`/`ask`/`allow` (approved), skills-vs-subagents-vs-MCP, headless-CI cost guardrails, thinking budgets.
> - [2026-06-13](../2026-06-13-claude-subreddit-scan/README.md) — git-worktrees for parallel Claude instances (approved) + a correction to the `subagent-isolation` premise.
> - [2026-06-15](../2026-06-15-claude-subreddit-scan/README.md) — scope-the-reviewer-to-correctness (approved), interview→SPEC, `claude -p` fan-out, `/clear`+`/btw` hygiene.
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — `CLAUDE_CODE_SUBAGENT_MODEL` resolution order (approved) + the MCP tool-context budget; CLAUDE.md memory hygiene (deferred).
> - [2026-06-24](../2026-06-24-claude-subreddit-scan/README.md) — SKILL.md progressive-disclosure body budget (approved); procedural-instructions-belong-in-skill (folded), model-tiering (denied dup), config-as-execution-vector (deferred).
> - [2026-07-02](../2026-07-02-claude-subreddit-scan/README.md) — **the Bash-sandbox rule (approved → v0.183.0)**; **and (same day) the verification-loop umbrella** ([verification-loop run](../2026-07-02-claude-subreddit-scan-verification-loop/README.md), approved → v0.184.4). The 07-02 run **deferred H2 — "compact proactively; persist load-bearing state before compaction" — as the explicit next-scan candidate.**
>
> **Today's net-new finding (H1) is that deferred 07-02 candidate, now promoted.** It is disjoint from all prior approved rules: the context-window rules the repo ships govern how to keep the window *small* (`mcp-tool-context-is-a-budget`, `claude-md-imports`); H1 governs *what happens when it fills anyway* — the compaction event itself, which no prior rule states.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode and adjacent communities about using Claude Code effectively.

**Route note (honest — unchanged from every prior scan):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py), which pulls real subreddit listings via Reddit's official OAuth2 Data API. It `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars were unset this session** (verified — `os.environ` check returned `False` for both). So — exactly as in the prior runs — this scan fell back to **unrestricted web search**, the documented fallback.

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ the sanctioned route — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session (re-verified) |
| `WebFetch https://www.reddit.com/...` + `old.reddit.com` + `.json` endpoints | ❌ "unable to fetch from www.reddit.com" (Anthropic crawler-UA block — the structural block `reddit-scan.py` exists to route around) |
| `WebSearch allowed_domains:[reddit.com]` | ❌ **400 — "domains not accessible to our user agent"** (crawler-UA block) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion aggregations + practitioner write-ups + GitHub issues |
| `WebFetch` of the **primary Anthropic doc** (`code.claude.com/docs/en/costs`) | ✅ works — fetched + quoted this session for the approved item |

**Provenance of the findings below:** Reddit-discussion aggregations + practitioner write-ups via unrestricted web search, **cross-checked against the primary Anthropic manage-costs/compaction doc** (fetched and quoted this session) and this repo's own surface. **Not** direct subreddit reads. **Standing next-scan action (carried again): set the two Reddit creds and run `reddit-scan.py` first** to close the provenance gap.

**Queries run (fallback route — unrestricted web search):**

- `Claude Code /compact proactive persist state before compaction lose context reddit 2026`
- `Claude Code advanced best practices hooks subagents context management 2026 techniques`
- `Claude Code output styles custom slash commands plan mode reddit tips 2026 lesser known`
- `best Claude Code skills 2026 curated directory community favorites`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Manage costs effectively](https://code.claude.com/docs/en/costs) (primary — auto-compaction summarizes conversation history near the limit; `/compact Focus on …` + a `CLAUDE.md` compact-instructions block tell it what to preserve; fetched + quoted this session for H1)
- [`anthropics/claude-code` issue #25999 — "Persistent state across context compaction"](https://github.com/anthropics/claude-code/issues/25999) (community — the compaction-loses-state pain, in the maintainer's own tracker)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): claudefa.st (context-buffer mechanics + threshold backups), the recurring _"what are we working on?"_ post-compaction thread, third-party memory-layer tools built to survive compaction.
- Cross-checked against this repo: [`plugins/ravenclaude-core/knowledge/concepts/context-window.md`](../../../plugins/ravenclaude-core/knowledge/concepts/context-window.md), the two shipped context-budget rules, and the constitution's Context & Session Hygiene + Run Artifacts sections.

---

## 2. Findings (4 — all checked against the 26-rule core set + the 8 prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Compact proactively (before quality degrades, not at ~95% full), and persist load-bearing state to disk *before* compaction — because compaction is lossy summarization that discards the *intermediate reasoning* (rejected approaches, verbose output, the "why we ruled out X"), not just chatter.** A plan/decision/acceptance-criterion that lived only in the conversation becomes a summary of a summary; the recurring _"what are we working on?"_ after auto-compaction is that loss in the wild. The fix: write it to a file/test first, and compact on your terms at a clean boundary, telling the summarizer what to keep. | **Genuine gap (consumer-facing) — the pre-teed-up 07-02 deferral.** Grep of `best-practices/` for "compact"/"compaction" returns only `mcp-tool-context-is-a-budget` + `claude-md-imports` — both about keeping the window *small* (context **cost**), neither about the compaction **event**. `knowledge/concepts/context-window.md` teaches *that* compaction happens ("it's now a summary … durable facts belong in CLAUDE.md or committed files") but is a foundations concept card, not a consumer-facing rule; and no rule states the *proactive-not-reactive + persist-before-compact* discipline. The 07-02 panel already vetted this as "real and net-new," deferring it only to keep one-tight-rule-per-round; this is its round. |
| **H2** | **`/insights` (and similar usage-history commands) surface repetitive prompts you type by hand → convert them into a custom command / skill.** A discovery aid for "what should I be automating?" | **Covered / thin.** Custom-command + skill authoring is owned by [`docs/best-practices/authoring-plugin-slash-commands.md`](../../best-practices/authoring-plugin-slash-commands.md) and the `keep-skill-bodies-lean` rule; "notice a repeated prompt and turn it into a command" is generic-platform-101 (adjacent to the 06-15 `claude -p` finding) and the `/insights`-command specifics are volatile UI facts, not a durable domain-neutral rule. Deny. |
| **H3** | **`/output-style` + custom output modes (Concise / Educational / Code-Reviewer / Rapid-Prototyping) reshape how Claude formats its answers.** | **Covered — dispositioned N-A.** The core `CLAUDE.md` "Value-add completeness" table already dispositions **output-styles / themes as N-A** for a domain-neutral orchestration foundation: "Output shape is governed by the Structured Output Protocol + the dashboard's themed SVGs; no per-style asset is warranted here." A rule teaching a generic output-style knob would restate a platform feature the repo deliberately doesn't lean on. Deny. |
| **H4** | **Third-party memory layers / threshold-backup hooks (write session state at 30/15/5% remaining, MCP memory tools) exist to make work survive compaction cycles.** | **Adjacent to H1 — the tooling side, out of scope to ship.** The *principle* (persist load-bearing state before compaction) is exactly H1; the *tooling* (a bundled memory-layer MCP / a StatusLine-threshold backup hook) is neither domain-neutral nor something a foundation plugin should ship (the Value-add table dispositions a bundled MCP as N-A, and the repo's **own** `.ravenclaude/runs/<id>/` run-artifacts substrate already IS the persist surface). Fold the evidence into H1's provenance ("the gap is felt"); don't ship external tooling. Defer. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to every prior scan: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no *action* on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably.

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** grep of `best-practices/` for "compact"/"compaction" returns zero rule hits on the *event* (only the two window-size-cost rules); the compaction discipline itself is stated nowhere, and the 07-02 panel already classified it net-new and deferred it *only* for round-discipline — this is the promotion it named. **In-scope:** session/context hygiene is core's home turf (the constitution already carries Context & Session Hygiene + the run-artifacts substrate — this rule is the compaction-boundary application of both), and the repo's own long multi-agent/overnight runs are the least-generic possible worked case. **Load-bearing:** the failure (post-compaction _"what are we working on?"_, re-litigating a settled call, redoing ruled-out work) has a real, repeatedly-observed cost with a concrete fix. **Low-blast:** additive markdown. | Keep it tight and cross-linked to the two context-cost rules (small-window siblings), the checkpoints rule (the within-session-vs-durable twin), and `context-window.md` (the mechanism). Frame the persistence half as universal and the `/compact`/`/clear` half as Claude-Code-specific (same portable/non-portable split as the checkpoints rule). Cite the memory-layer tooling as *evidence the gap is felt*, not as something to ship. |
| **H2** | ❌ Deny | Fails #1/#3 — covered + thin. Command/skill authoring is owned by `authoring-plugin-slash-commands.md` + `keep-skill-bodies-lean`; "notice a repeated prompt → make a command" is generic-platform-101 and the `/insights` specifics are volatile UI facts, not a durable rule. | If a concrete "usage-history → automation" workflow ever earns depth, fold it into the existing command-authoring best-practice, not a new rule. |
| **H3** | ❌ Deny | Fails #1/#2 — the core `CLAUDE.md` Value-add table **already dispositions output-styles/themes as N-A** for this foundation, with the stated reason (output shape is governed by the Structured Output Protocol). A rule here would contradict a standing, deliberate disposition. | None — cleanly dispositioned. |
| **H4** | ⏸️ Defer (fold into H1) | Borderline #1/#2. The principle is H1; the tooling (bundled memory MCP / threshold-backup hook) is out of scope for a domain-neutral foundation (bundled MCP is N-A per the Value-add table; the run-artifacts substrate is the persist surface the repo already owns). The evidence belongs in H1's provenance as "the gap is felt," not as a shipped mechanism. | If a future scan finds a *portable, dependency-free* compaction-survival mechanism that fits the foundation (not a vendored MCP), revisit — but the durable-state-write is already H1 + run-artifacts. |

**Net:** 1 approved (H1), 2 denied (H2, H3), 1 deferred-and-folded (H4). One solid, well-grounded addition — the exact candidate the prior run teed up — beats padding a mature repo with near-duplicates, consistent with house-rule #4 ("don't restate what's already enforced/covered") and the prior scans' one-tight-rule discipline.

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "Compact proactively — and persist load-bearing state *before* compaction, because compaction discards intermediate reasoning." Sections: Why (the compaction event = lossy summarization; reactive-vs-proactive; state-that-lived-only-in-chat) / How (persist-when-decided, compact-at-a-boundary, tell-the-summarizer-what-to-keep, `/clear` for unrelated work) / Edge cases (short sessions, portable-vs-Claude-only, not-a-substitute-for-commits) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/compact-proactively-persist-load-bearing-state-before-compaction.md` | Follows the one-rule-per-file format of the existing rules. |
| 2 | Index update: → **27 rules**; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.184.4 → **0.185.0**, mirrored across all three. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json` via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. |
| 4 | CHANGELOG top entry for 0.185.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-07-06-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook — so no count-string sync is needed. Markdown + manifest diff only; run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive consumer-facing markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Manage costs effectively](https://code.claude.com/docs/en/costs) (auto-compaction + `/compact Focus on …` + `CLAUDE.md` compact-instructions)
- [`anthropics/claude-code` issue #25999 — Persistent state across context compaction](https://github.com/anthropics/claude-code/issues/25999)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): claudefa.st context-buffer mechanics; the recurring _"what are we working on?"_ post-compaction thread; third-party memory-layer / threshold-backup tooling.
- Cross-checked against this repo: `plugins/ravenclaude-core/knowledge/concepts/context-window.md`, `best-practices/mcp-tool-context-is-a-budget-enable-only-what-you-need.md`, `best-practices/claude-md-imports-organize-they-dont-shrink-context.md`, `best-practices/checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md`, and the constitution's Context & Session Hygiene + Run Artifacts sections.
- Prior runs: [`2026-06-09`](../2026-06-09-claude-subreddit-scan/README.md) · [`2026-06-10`](../2026-06-10-claude-subreddit-scan/README.md) · [`2026-06-11`](../2026-06-11-claude-subreddit-scan/README.md) · [`2026-06-13`](../2026-06-13-claude-subreddit-scan/README.md) · [`2026-06-15`](../2026-06-15-claude-subreddit-scan/README.md) · [`2026-06-22`](../2026-06-22-claude-subreddit-scan/README.md) · [`2026-06-24`](../2026-06-24-claude-subreddit-scan/README.md) · [`2026-07-02`](../2026-07-02-claude-subreddit-scan/README.md) · [`2026-07-02 (verification-loop)`](../2026-07-02-claude-subreddit-scan-verification-loop/README.md)
