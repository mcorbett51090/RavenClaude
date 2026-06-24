# Claude subreddit scan — research, panel decision & build plan (2026-06-20)

**Author:** `claude` (automated scheduled scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 fresh findings surfaced (none overlapping the 2026-06-09/-10/-11 scans) → **1 approved**, 1 deferred-as-covered, 2 denied/deferred. The approved item shipped as a **correction + reconciliation** inside an existing knowledge file (`ravenclaude-core` v0.158.0) — not a new best-practice, because the topic already lives in `knowledge/dynamic-workflows.md` and the right move was to sharpen it, not duplicate it.

> This is the **fourth** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions-deny/ask/allow (approved), skills-vs-subagents-vs-MCP, headless-CI cost caps, thinking-budget keyword tiers (denied — churn).
>
> Today's findings are deliberately disjoint from all three sets.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest — same operational gap as the 2026-06-11 run):** the sanctioned front door for this scan is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (Reddit's official OAuth2 Data API). It `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars are still unset this session** (verified — `os.environ` check returned unset for both). So the *structural* block (the crawler can't read reddit.com) remains solved by that script, but the *operational* gap — the two creds were never set in this environment — persists. **Next scan: set the two Reddit creds (one-time `script`-app at <https://www.reddit.com/prefs/apps>) and run `reddit-scan.py` first** so findings come from real subreddit listings, closing the provenance gap for good.

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session |
| `WebFetch www.reddit.com/....json` | "Claude Code is unable to fetch from www.reddit.com" (crawler-UA block) |
| `WebSearch allowed_domains:[reddit.com]` | **400 — "domains not accessible to our user agent"** |
| Several practitioner aggregators (substack/mlearning/aicodingdaily/dev.to) on direct `WebFetch` | **HTTP 403** (publisher UA blocks) |
| Unrestricted `WebSearch` (fallback used) | ✅ works — Reddit-discussion snippets + practitioner write-ups |
| `WebFetch code.claude.com/docs/en/agent-teams` (primary grounding) | ✅ **succeeded** — the approved finding is grounded in the official doc, not a secondary source |

**Provenance of the findings below:** community *themes* drawn from Reddit-discussion aggregations + practitioner write-ups via unrestricted web search (the documented fallback, **not** the preferred route); **every claim that landed in the repo was then cross-checked against the primary Anthropic doc** ([code.claude.com/docs/en/agent-teams](https://code.claude.com/docs/en/agent-teams), which WebFetch *did* return) per the Claim-Grounding protocol.

**Queries run (fallback route — unrestricted web search):**

- `r/ClaudeAI best Claude Code workflow CLAUDE.md plugins subagents`
- `Claude Code context management compaction token waste reddit tips`
- `Claude Code Agent Teams feature peer-to-peer agents communicate directly experimental enable environment variable how it works`
- `Claude Code output styles subagent context pollution reddit complaint pitfall 2026`
- `Claude Code multi-agent orchestration parallel worktrees reddit workflow 2026`

---

## 2. Findings (4 — all fresh vs. the three prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Native "Agent Teams" (Opus 4.6, Feb 2026) is peer-to-peer, not hub-and-spoke.** Enabled via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`; teammates **message each other directly** through a mailbox (`SendMessage`) and self-claim from a shared task list — they don't only report to the lead. This is the exact thing RavenClaude's constitution governs ("only the Team Lead dispatches; sub-agents don't directly invoke each other"). | **Partially covered — but with an inaccuracy.** `knowledge/dynamic-workflows.md` already lists "agent-team" in its orchestration-shape chooser, **but** its rationale said *"the lead still decides turn by turn"* — which understates the peer mailbox. **Genuine gap:** no reconciliation of the peer-mesh against the hub-and-spoke constitution, and the enable flag/limits were absent. The boundary is subtle and worth pinning exactly (peer-**spawn** is forbidden by the feature too; peer-**communication** is the part that's relaxed). |
| **H2** | **The `/compact` "60% rule" + targeted compaction directives** ("compact at ~60%, not 95%"; `"/compact keep the API endpoints + auth decisions + current error"`; put compaction-preservation rules in `CLAUDE.md`). | **Covered.** The [2026-06-10 scan](../2026-06-10-claude-subreddit-scan/README.md) already surfaced context-compaction; [`docs/token-budget-playbook.md`](../../token-budget-playbook.md) is the throughput/budget home. The CLAUDE.md-preserves-across-compaction nugget is real but thin and adjacent to already-covered ground. |
| **H3** | **Worktree-per-agent isolation + `WorktreeCreate`/`WorktreeRemove` settings hooks** for non-git VCS, plus naming/color-coding terminal tabs to stay oriented across many parallel sessions. | **Covered / tooling-tip.** Sleipnir worktree convention + `skills/new-worktree`, `skills/cleanup-worktrees`, and `best-practices/delegate-reads-fan-out-keep-branch-writes-in-main.md` already own the worktree-isolation story for this repo. The settings-hook detail is niche and host-version-specific. |
| **H4** | **Output styles modify the system prompt** (non-default styles drop Claude Code's built-in code-gen/efficiency instructions); subagents preserve context "for free" while bad subagent use burns it. | **Covered / generic.** Subagent context-isolation is covered by `knowledge/subagent-isolation-and-tooling.md` + `best-practices/focused-task-delegation-beats-full-context-dumps.md`; "output styles swap the system prompt" is generic platform-101 the core set excludes. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to the three prior scans: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no *action* on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (If Matt wants the live tribunal applied retroactively, `decision-review` over this doc's decisions is the surface.)

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered (or, if partly covered, the delta is a correction or a load-bearing gap, not a restatement).
2. **In-scope** — domain-neutral and constitution-grounded; the core set forbids generic platform-101.
3. **Load-bearing** — encodes a lesson whose absence has an observable cost.
4. **Low-blast** — additive/corrective markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive (twofold):** (a) it *corrects an inaccuracy* already in `dynamic-workflows.md` ("the lead still decides turn by turn" — false; teammates message each other directly per the official doc), and (b) it adds the missing **reconciliation against the core dispatch rule**, which is the single most constitution-adjacent feature Anthropic has shipped. **In-scope:** orchestration topology *is* RavenClaude's domain — the entire guardrail/observability stack assumes lead-mediated handoffs. **Load-bearing:** a consumer enabling `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` in a tribunal-gated repo silently trades away the SOP/run-artifact/Heimdall-Víðarr audit trail on inter-peer traffic; naming that tradeoff + the mitigations (gating hooks, hardened-subagent-as-teammate, permission inheritance) has clear cost-of-absence. **Low-blast:** corrective/additive markdown in one knowledge file. | Shipped as an **edit to the existing knowledge file**, not a new best-practice rule — the topic already lives there, and the dynamic-workflows reconciliation precedent (v0.118.0) put platform-feature reconciliation in the knowledge file. A standalone best-practice was considered and **declined**: Agent Teams is experimental + actively churning (TeamCreate/TeamDelete already removed by v2.1.178), and canonizing a moving feature as an absolute rule is exactly what got the thinking-budget item denied on 2026-06-11. Every platform claim carries an inline `[verified — official docs, retrieved 2026-06-20]` marker + the experimental caveat. |
| **H2** | ⏸️ Defer (covered) | Fails #1 — the 2026-06-10 scan covered context-compaction and `token-budget-playbook.md` is the budget home. The "preserve-across-compaction in CLAUDE.md" nugget is thin. | If a concrete "compaction dropped a load-bearing constraint and cost X" case appears, fold a one-liner into `token-budget-playbook.md` — not a new artifact. |
| **H3** | ⏸️ Defer (covered/niche) | Fails #1 and partly #3 — the Sleipnir worktree convention + two worktree skills + the fan-out best-practice already own this; the `WorktreeCreate`/`WorktreeRemove` settings hooks are a niche, host-version-specific tooling detail. | Revisit only if a non-git-VCS consumer hits a concrete worktree-isolation failure the current skills don't cover. |
| **H4** | ❌ Deny | Fails #1 and #2 — subagent context-isolation is already covered; "output styles swap the system prompt" is generic platform-101 the core best-practice set explicitly excludes. | None — the existing subagent-isolation knowledge + focused-delegation rule are the right homes; nothing to add. |

**Net:** 1 approved, 2 deferred, 1 denied. One accurate, well-grounded correction-plus-reconciliation beats padding a mature repo with near-duplicates — consistent with house-rule #4 ("don't restate what's already enforced/covered") and the three prior scans' one-tight-change discipline.

---

## 4. Build plan (approved: H1)

**Deliverable:** correction + reconciliation inside the existing `dynamic-workflows.md` knowledge file (no new file, no new best-practice rule).

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | Header: bump `Last reviewed` 2026-06-04 → 2026-06-20 + a dated update note linking the new section. | `plugins/ravenclaude-core/knowledge/dynamic-workflows.md` | — |
| 2 | **Accuracy fix:** rewrite the agent-team rationale line (drop "the lead still decides turn by turn"; state the peer mailbox + that the lead doesn't mediate every inter-peer message). | same file | grounded in the official doc |
| 3 | **New section** `### Agent teams & RavenClaude's hub-and-spoke constitution`: enable flag + experimental caveat; the four-part architecture (lead/teammates/task-list/mailbox); a 3-row boundary table (peer-spawn ✅ preserved / lead-fixed ✅ preserved / peer-communication ⚠️ relaxed); the observability tradeoff; mitigations (`TaskCreated`/`TaskCompleted`/`TeammateIdle` gating hooks, hardened-subagent-as-teammate, permission-inherited-at-spawn); when-not-to-use. Every platform fact carries `[verified — official docs, 2026-06-20]`. | same file | placed before `## Runtime facts & constraints` |
| 4 | Version bump 0.157.0 → **0.158.0**, mirrored. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` | CI fails on version drift between the two |
| 5 | CHANGELOG top entry for 0.158.0 (`### Changed`). | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 6 | This research + panel doc. | `docs/research/2026-06-20-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change |

**Layout/gate notes:** `plugins/*/knowledge/**`, `plugins/*/CHANGELOG.md`, and `docs/**` are all already in `.repo-layout.json` `allowed_globs` → no manifest change. No new `## Decision Tree:` heading was added (the new section is prose + a tradeoffs table), so the `render-trees.py` SVG gate is not triggered. Markdown-only diff; run `prettier --write .` before push (CI checks the whole tree).

**Why a knowledge-file edit, not a CLAUDE.md milestone:** the change is corrective/additive *within* a knowledge file (not a new component or behavior), and is fully traced by the CHANGELOG entry + this research doc + the version bump. Adding a milestone to the already-large CLAUDE.md was considered and judged unnecessary blast.

**Migration:** none — corrective/additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Orchestrate teams of Claude Code sessions](https://code.claude.com/docs/en/agent-teams) — **primary, WebFetch-retrieved 2026-06-20** (enable flag, peer mailbox / `SendMessage`, shared task list + file-locking, no-nested-teams, lead-fixed, `TaskCreated`/`TaskCompleted`/`TeammateIdle` hooks, subagent-definition-as-teammate, permission inheritance, experimental limitations, v2.1.178 framing).
- [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) · [Configure permissions](https://code.claude.com/docs/en/permissions) (cross-checks).
- Practitioner aggregations (read via search snippets; several 403 on direct fetch): aitooldiscovery "Claude Code Reddit", mindstudio token-management/compaction series, medium/kumaran "Beyond Sub-Agents: peer-to-peer agent teams", mindstudio "Agent Teams vs Sub-Agents", FlorianBruniaux claude-code-ultimate-guide.
- [Anthropic support — does Anthropic crawl the web / how site owners block the crawler](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) (the Reddit-crawler-block evidence).
- Prior runs: [`2026-06-09`](../2026-06-09-claude-subreddit-scan/README.md) · [`2026-06-10`](../2026-06-10-claude-subreddit-scan/README.md) · [`2026-06-11`](../2026-06-11-claude-subreddit-scan/README.md).
