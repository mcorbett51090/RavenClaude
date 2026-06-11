# Claude subreddit scan — research, panel decision & build plan (2026-06-11)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 fresh findings surfaced (none overlapping the 2026-06-09 or 2026-06-10 scans) → **1 approved**, 1 deferred-as-covered, 2 deferred/denied. The approved item shipped as one new consumer-facing best-practice in `ravenclaude-core` (v0.155.0).

> This is the **third** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — covered hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — covered checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
>
> Today's findings are deliberately disjoint from both sets.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest — corrected after the scan):** the WebFetch/WebSearch 403 is on **Anthropic's crawler user-agent**, not on Reddit's data — and the repo **already shipped the sanctioned front door**: [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (2026-06-10), which pulls real subreddit listings via **Reddit's official OAuth2 Data API**. See [`docs/research/2026-06-10-data-access-routes/README.md`](../2026-06-10-data-access-routes/README.md) §1. **That is the correct route for this scan, and this run should have used it.**

**Why this run fell back to web search anyway:** the script `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and both env vars were **unset this session** (verified — `os.environ` check returned unset for both). The one-time setup (create a "script" app at <https://www.reddit.com/prefs/apps>, export the two creds locally or as CI/Codespace secrets) hadn't landed in this environment. So the *structural* block is solved; the *operational* gap is just the missing credentials.

The crawler-route table below is still accurate as a record of what's blocked, but it is **not** the reason for the aggregation-sourced provenance — the missing creds are:

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session |
| `WebFetch www.reddit.com/....json` | "Claude Code is unable to fetch from www.reddit.com" (crawler-UA block) |
| `WebFetch old.reddit.com/....json` | same block |
| `WebFetch safereddit.com` / `redlib.catsarch.com` (mirrors) | HTTP 403 |
| `WebSearch allowed_domains:[reddit.com]` | **400 — "domains not accessible to our user agent"** |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion snippets + practitioner write-ups |

**Provenance of the findings below:** drawn from Reddit-discussion aggregations + practitioner write-ups via unrestricted web search, cross-checked against primary Anthropic docs — **not** from direct subreddit reads. This is the documented fallback, **not** the preferred route. **Next scan: set the two Reddit creds and run `reddit-scan.py` first** so findings come from real subreddit listings (closing the provenance gap for good).

**Queries run (fallback route — unrestricted web search):**

- `Claude Code Agent Skills SKILL.md authoring progressive disclosure when to use skill vs subagent 2026`
- `Claude Code headless mode claude -p GitHub Actions CI automation best practices 2026`
- `Claude Code ultrathink thinking budget keyword think harder extended thinking when to use`
- `Claude Code permissions allow deny ask settings.json security posture dangerously-skip-permissions lessons`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Configure permissions](https://code.claude.com/docs/en/permissions) (primary — eval order, bypass-mode guidance)
- [Anthropic — Extend Claude with skills](https://code.claude.com/docs/en/skills) + [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) (primary)
- [Anthropic — Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions) (primary)
- Practitioner aggregations (read via search snippets; several 403 on direct fetch): Code With Seb "Headless Mode CI/CD playbook", Steve Kinney "Claude Code Thinking", levelup.gitconnected "A Mental Model for Claude Code: Skills, Subagents, and Plugins", ClaudeCodeLab / Vincent Qiao permission guides.

---

## 2. Findings (4 — all fresh vs. the 2026-06-09 & 2026-06-10 scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Skills vs. subagents vs. MCP — pick the right primitive.** A *skill* modifies how the main agent behaves (inline guidance, progressive disclosure, stays in context); a *subagent* is a context-isolated worker the main agent delegates to; an *MCP server* provides a capability/tool. "Skill = expertise, MCP = capability, subagent = context boundary." | **Partially covered, different audience.** `best-practices/domain-plugins-extend-via-skills-not-parallel-agents.md` + the CLAUDE.md house rule cover the **marketplace-authoring** angle (should *this plugin* ship a domain agent?); `claude-app-engineering/mcp-vs-in-process-tool.md` covers MCP-vs-tool. No **consumer-facing** "which of the three primitives for my task" rule — but it risks restating the Anthropic docs' own explainer. |
| **H2** | **Headless `claude -p` in CI needs cost guardrails.** Per-workflow token caps (review ≈20K, fix ≈60K, scheduled-maintenance ≈100K weekly), a minimal tool surface, a non-interactive permission mode, GitHub-Secrets for keys, and **alert on weekly spend, not per-run**. | **Adjacent, not core.** Core's `runaway-brake.sh` (depth) + `dod-gate.sh` (correctness) already bound unsupervised runs; `claude-app-engineering` has `agent-guardrail-the-loop.md` / `cost-and-secrets-observability.md` (Agent-SDK app building). A *Claude-Code-in-CI* token-cap rule is genuinely net-new but belongs in a **domain plugin** (`devops-cicd`), not domain-neutral core. |
| **H3** | **Thinking budgets are a cost dial, not a boolean.** Claude Code keyword tiers (`think` ≈4K, `megathink`/`think hard` ≈10K, `ultrathink`/`think harder` ≈32K); match the level to problem complexity; overusing wastes time and money. (Active churn: auto-thinking vs. explicit keyword — issue #19098.) | **Covered in principle.** `claude-app-engineering/best-practices/thinking-budget-as-a-dial.md` teaches the *exact* principle (classify task tier → assign budget; don't set a large fixed budget). The net-new nugget is only the **Claude-Code-CLI keyword names** — thin, and a moving target given the deprecation churn. |
| **H4** | **Permissions are a three-tier posture (`deny`/`ask`/`allow`), not an on-off switch.** Eval order is `deny` → `ask` → `allow`, first match wins, specificity does *not* reorder (a `deny` always beats an `allow`). Sort by reversibility: idempotent reads → `allow`, intent-changing → `ask`, irreversible/secret → `deny`. `allow` is a convenience layer; `deny` is the boundary. `--dangerously-skip-permissions` skips *everything* incl. `deny` — isolated envs only. Treat `settings.json` like code, review changes in a PR. | **No general rule — genuine gap.** Core ships `web-access-allow-deny-list-before-first-fetch.md` (the **WebFetch-specific subset**) and the comfort-posture system *is* a permission surface, but there is **no consumer-facing best-practice** generalizing the `deny`/`ask`/`allow` taxonomy + eval order to *all* tools (Bash/Edit/Write/MCP). And **the repo's own `.claude/settings.json` deny list is the worked example** — it lives this rule yet never states it. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to the two prior scans: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no _action_ on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (If Matt wants the live tribunal applied retroactively, `decision-review` over this doc's decisions is the surface.)

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (in core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H4** | ✅ **Approve** | Passes all four. **Additive:** no general permission-posture rule exists — `web-access-allow-deny-list` is the WebFetch-only special case; this is its parent. **In-scope:** permission governance *is* RavenClaude's domain (the entire comfort-posture / guardrail stack), and the repo's own 20-entry `.claude/settings.json` deny list is the canonical worked example — the least-generic topic possible for this repo. **Load-bearing:** the `deny`→`ask`→`allow` eval order (a `deny` beats any `allow`; specificity doesn't reorder) is non-obvious and miscategorizing has real cost in both directions; the "bypass-mode skips the `deny` backstop too" point closes a genuine footgun. **Low-blast:** additive markdown. | Kept tight and cross-linked to `web-access-allow-deny-list` (declares itself the general parent), `prefer-a-deterministic-gate-over-a-prose-rule` (a `deny` IS a deterministic gate), and `checkpoints-are-the-recovery-layer` (irreversible → `deny`, not `ask`, because checkpoints can't undo a `Bash` side-effect). The CI/headless half is scoped into the edge-cases section so it doesn't bloat the core rule. |
| **H1** | ⏸️ Defer | Borderline #1 and #2. The **authoring** half is covered by `domain-plugins-extend-via-skills-not-parallel-agents.md`; the net-new **consumer** "which primitive" decision risks restating the Anthropic Skills-vs-subagents docs verbatim — generic-platform-101, which the core set excludes. | If a consumer-authoring guide is ever built (e.g. an `/init-agent-ready` companion on "structuring your own Claude Code setup"), fold the skill/subagent/MCP/plugin primitive-selection table in there, grounded in RavenClaude's explicit-dispatch model — not as a standalone core rule. |
| **H2** | ⏸️ Defer (to a domain plugin) | Fails #2 for **core** (not domain-neutral-foundation-shaped — it only helps consumers running Claude Code *in CI*) and partially #1 (core's runaway-brake + DoD gate already bound unsupervised cost/correctness). The token-cap heuristic itself is real and valuable. | Strong candidate for a `devops-cicd` best-practice (`ci-cap-the-agent-token-budget-per-workflow.md`) or a `claude-app-engineering` scenario — noted for a future domain-plugin scan, not shipped to core here. |
| **H3** | ❌ Deny | Fails #1 — duplicate. `claude-app-engineering/thinking-budget-as-a-dial.md` already teaches the exact principle (tier the task → size the budget; don't fix a large budget). The only delta is the Claude-Code-CLI keyword names, which are thin **and** in active deprecation churn (issue #19098) — canonizing a moving target is the wrong move. | If the keyword tiers stabilize and a concrete "wrong thinking tier cost X" case appears, add the keyword table to the *existing* `thinking-budget-as-a-dial.md` as a Claude-Code-CLI subsection — not a new rule. |

**Net:** 1 approved, 1 denied, 2 deferred. One solid, well-grounded addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 ("don't restate what's already enforced/covered") and the two prior scans' discipline (each landed exactly one tight rule).

---

## 4. Build plan (approved: H4)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "Permissions are a three-tier posture (`deny`/`ask`/`allow`), not an on-off switch." Sections: Why / How (eval-order + reversibility taxonomy + the repo's own deny-list as the worked example) / Edge cases (CI-headless, non-Claude hosts, solo-dev) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/permissions-are-deny-ask-allow-not-an-on-off-switch.md` | Follows the one-rule-per-file format of the existing 17 rules. |
| 2 | Index update: 17 → 18 rules; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.153.1 → **0.155.0**, mirrored. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` | CI fails on version drift between the two. |
| 4 | CHANGELOG top entry for 0.155.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-06-11-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. Markdown-only diff, but run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Configure permissions](https://code.claude.com/docs/en/permissions) (eval order `deny`→`ask`→`allow`; bypass-mode guidance)
- [Anthropic — Extend Claude with skills](https://code.claude.com/docs/en/skills) · [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic — Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)
- [Anthropic support — does Anthropic crawl the web / how site owners block the crawler](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) (the Reddit-block evidence)
- Practitioner aggregations (read via search snippets): Code With Seb (headless CI playbook), Steve Kinney (Claude Code thinking), levelup.gitconnected (skills/subagents/plugins mental model), ClaudeCodeLab + Vincent Qiao (permissions guides)
- Prior runs: [`docs/research/2026-06-09-claude-subreddit-scan/README.md`](../2026-06-09-claude-subreddit-scan/README.md) · [`docs/research/2026-06-10-claude-subreddit-scan/README.md`](../2026-06-10-claude-subreddit-scan/README.md)
