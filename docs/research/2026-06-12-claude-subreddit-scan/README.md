# Claude subreddit scan — research, panel decision & build plan (2026-06-12)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 fresh findings surfaced (none overlapping the 2026-06-09, -10, or -11 scans) → **1 approved**, 1 already-validated, 2 deferred-as-covered. The approved item shipped as additive subagent-mechanics knowledge + one best-practice edge case in `ravenclaude-core` (v0.156.0).

> This is the **fourth** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions deny/ask/allow (approved), skills-vs-subagents-vs-MCP (deferred), headless-CI cost (deferred to domain), thinking-budgets (denied).
>
> Today's findings are deliberately disjoint from all three sets.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest — unchanged from the 2026-06-11 scan).** The sanctioned front door for this scan is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (2026-06-10), which pulls real subreddit listings via **Reddit's official OAuth2 Data API** — the Anthropic-crawler 403 is on the *crawler user-agent*, not on Reddit's data. **But the script `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and both were unset this session** (verified — `os.environ` check returned `unset` for both). So the *structural* block is solved; the *operational* gap (missing creds in this environment) persists for the second scan running. **Next scan: set the two Reddit creds and run `reddit-scan.py` first** to close the provenance gap for good.

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session |
| `WebFetch www.reddit.com/...` | "Claude Code is unable to fetch from www.reddit.com" (crawler-UA block) |
| `WebSearch allowed_domains:[reddit.com]` | **400 — "domains not accessible to our user agent"** |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion snippets + practitioner write-ups |
| `WebFetch code.claude.com/docs/...` (primary-doc grounding) | ✅ works — used to verify the approved finding against the official source |

**Provenance of the findings below:** drawn from Reddit-discussion aggregations + practitioner write-ups via unrestricted web search, **cross-checked against primary Anthropic docs** (the approved item is verified against [`code.claude.com/docs/en/sub-agents`](https://code.claude.com/docs/en/sub-agents) this session, not from training recall). This is the documented fallback, **not** the preferred route.

**Queries run (fallback route — unrestricted web search):**

- `r/ClaudeAI Claude Code subagents CLAUDE.md context engineering best tips discussion 2026`
- `r/ClaudeAI Claude Code hooks output styles skills MCP power user workflow 2026`
- `Claude Code skills vs subagents vs slash commands when to use which 2026 community`
- `Claude Code CLAUDE.md context window degradation instruction limit best practice 2026`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Create custom subagents](https://code.claude.com/docs/en/sub-agents) (primary — "What loads at startup", Explore/Plan exception, resume mechanics) — **fetched and quoted this session.**
- Practitioner aggregations (read via search snippets): ClaudeKit "Subagents: Common Mistakes & Best Practices", okhlopkov.com "My Claude Code Setup 2026", aistackinsights / blakecrosley power-user guides, MindStudio / claudefa.st context-window guides.

---

## 2. Findings (4 — all fresh vs. the prior three scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **D1** | **The built-in `Explore` and `Plan` subagents skip `CLAUDE.md` + the parent's git status; every other built-in/custom subagent loads both — and there's no setting to change it.** Consequence: a project rule that must constrain an Explore/Plan run has to be *restated in the delegation prompt*; it will not arrive through memory. Also: Explore/Plan are **one-shot** (no agent ID → can't be resumed); use `general-purpose`/custom when a research thread may need continuation. | **Genuine gap.** [`knowledge/subagent-isolation-and-tooling.md`](../../../plugins/ravenclaude-core/knowledge/subagent-isolation-and-tooling.md) covers the *runtime* git-write constraint and the frontmatter field-set, but **not** the *declarative load surface* (what reaches a subagent at startup). [`best-practices/focused-task-delegation-beats-full-context-dumps.md`](../../../plugins/ravenclaude-core/best-practices/focused-task-delegation-beats-full-context-dumps.md) preaches "pass the load-bearing slice" generically but never names the concrete Explore/Plan-skip mechanic that makes the rule *mandatory* for those two agents. |
| **D2** | **Subagents rarely auto-summon; add a CLAUDE.md line reminding Claude the agent exists** to get reliable delegation. | **Covered.** This marketplace's whole dispatch model is explicit Team-Lead routing ([`route-before-spawning.md`](../../../plugins/ravenclaude-core/best-practices/route-before-spawning.md) + [`knowledge/agent-routing.md`](../../../plugins/ravenclaude-core/knowledge/agent-routing.md)); the orchestrator already loads every agent's `description` for routing (the ~15K budget rule in AGENTS.md). The "remind it in CLAUDE.md" nugget is the unstructured version of what the routing tree already does structurally. |
| **D3** | **Context rot at 20–40% of the window; keep CLAUDE.md lean (<~200 lines / ~150 instruction slots), `/compact` *before* you see degradation, front-load constraints.** | **Covered.** [`docs/token-budget-playbook.md`](../../token-budget-playbook.md), the `context-window` + `context-compaction` Learn-tab concepts, and the `prefer-a-deterministic-gate-over-a-prose-rule.md` pruning guidance already carry this. (Mild irony: this repo's own `CLAUDE.md` is far over 200 lines by design — a marketplace constitution, not a consumer's project file.) |
| **D4** | **Skill = expertise (stays in context) · subagent = context boundary · slash command = typed entry point; pick by "small & in front of you vs. big & side-process."** | **Covered / deferred (same as 2026-06-11 H1).** [`knowledge/dynamic-workflows.md`](../../../plugins/ravenclaude-core/knowledge/dynamic-workflows.md) §"Choosing an orchestration shape" + [`orchestration-decision-trees.md`](../../../plugins/ravenclaude-core/knowledge/orchestration-decision-trees.md) (skill-vs-agent tree) already carry the selection logic; the consumer-authoring "which primitive" guide was explicitly deferred last scan. No new move. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to the three prior scans: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no *action* on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (If Matt wants the live tribunal applied retroactively, `decision-review` over this doc's decisions is the surface.)

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (core **or** domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **D1** | ✅ **Approve** | Passes all four. **Additive:** the *declarative load surface* of a subagent is documented nowhere in the repo — the existing subagent-isolation file is about *runtime* git-writes, and the focused-task rule is generic. **In-scope:** subagent dispatch *is* this marketplace's core domain (Team-Lead orchestration); the Explore/Plan-skip mechanic is the least-generic topic possible here, and it directly underwrites why the focused-task brief is shaped the way it is. **Load-bearing:** the failure it prevents is concrete and silent — delegating to Explore/Plan and *assuming* a `CLAUDE.md` rule (e.g. "ignore `vendor/`", "`generated/` is read-only") reached them when it never did. The one-shot/non-resumable corollary prevents a second silent failure (trying to "continue" an Explore run that has no agent ID). **Low-blast:** additive markdown. | Grounded against the official doc *this session* (not training recall) and carries a provenance marker per Claim-Grounding. Placed in the canonical knowledge file (not a new best-practice — that would near-duplicate `focused-task-delegation`); the consumer-facing rule gets one cross-linked edge-case bullet so the discipline has concrete teeth without a redundant file. |
| **D2** | ☑️ Already-validated | Fails #1 — the explicit routing tree + the orchestrator's description-loading is the *structured* form of "remind Claude the agent exists." Worth noting as external corroboration, not a new artifact. | Folded into the approved knowledge section's "external validation" note (the doc also corroborates "subagents cannot spawn subagents" = the Team-Lead-only-dispatch / `guard-recursive-spawn` invariant). |
| **D3** | ⏸️ Defer (covered) | Fails #1 — `token-budget-playbook.md` + the context Learn concepts already teach context-rot + lean-CLAUDE.md + compact-early. | If a concrete "CLAUDE.md bloat cost X" case appears, add it to the playbook — not a new rule. |
| **D4** | ⏸️ Defer (covered) | Fails #1 — duplicate of 2026-06-11 H1, already deferred with a clear future home (an `/init-agent-ready` authoring companion). | No change; the deferral still stands. |

**Net:** 1 approved, 1 already-validated (folded in), 2 deferred. One solid, official-doc-grounded addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 and the three prior scans' one-tight-artifact discipline.

---

## 4. Build plan (approved: D1)

**Deliverable:** additive subagent-mechanics knowledge + one cross-linked best-practice edge case in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New section "What loads at a subagent's startup — and the Explore/Plan exception" (the skip mechanic, the restate-in-prompt consequence, resume-vs-one-shot, and the external validation of the no-nesting rule), with a 2026-06-12 official-doc provenance marker. | `plugins/ravenclaude-core/knowledge/subagent-isolation-and-tooling.md` | Canonical home for subagent mechanics. |
| 2 | New edge-case bullet: the rule is *mandatory* (not optional) for Explore/Plan because they skip `CLAUDE.md`; cross-link to the knowledge section. Review-date bumped. | `plugins/ravenclaude-core/best-practices/focused-task-delegation-beats-full-context-dumps.md` | The consumer-facing rule that gains concrete teeth. |
| 3 | Version bump (new user-visible content) 0.155.0 → **0.156.0**, mirrored. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` | CI fails on version drift between the two. |
| 4 | CHANGELOG top entry for 0.156.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-06-12-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/knowledge/**`, `plugins/*/best-practices/**`, and `docs/**` are all already in `.repo-layout.json` `allowed_globs` → no manifest change. Markdown + manifest diff only; run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed. The best-practices index count (18) is unchanged — no new rule file, so `best-practices/README.md` needs no edit.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Create custom subagents](https://code.claude.com/docs/en/sub-agents) (§ "What loads at startup": *"Explore and Plan are the only subagents that omit CLAUDE.md and git status. There is no frontmatter field or per-agent setting to change which agents skip them."*; § "Resume subagents"; *"subagents cannot spawn other subagents"*) — **fetched + quoted this session.**
- [Anthropic support — does Anthropic crawl the web / how site owners block the crawler](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) (the Reddit-crawler-block evidence)
- Practitioner aggregations (read via search snippets): ClaudeKit subagents best-practices, okhlopkov.com "My Claude Code Setup 2026", aistackinsights / blakecrosley power-user guides, MindStudio / claudefa.st context-window guides
- Prior runs: [`2026-06-09`](../2026-06-09-claude-subreddit-scan/README.md) · [`2026-06-10`](../2026-06-10-claude-subreddit-scan/README.md) · [`2026-06-11`](../2026-06-11-claude-subreddit-scan/README.md)
- Sanctioned future route: [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (set `REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET` and run it first next scan)
</content>
</invoke>
