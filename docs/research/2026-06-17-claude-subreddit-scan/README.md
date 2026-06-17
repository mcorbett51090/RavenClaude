# Claude subreddit scan — research, panel decision & build plan (2026-06-17)

**Author:** `claude` (automated scan, scheduled routine)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 fresh findings surfaced (none overlapping the 2026-06-09, 06-10, or 06-11 scans) → **1 approved**, 3 deferred/denied (covered, or a moving-target). The approved item shipped as one new consumer-facing best-practice in `ravenclaude-core` (v0.158.0).

> This is the **fourth** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions three-tier `deny`/`ask`/`allow` (approved), skills-vs-subagents-vs-MCP, headless-CI cost caps, thinking budgets.
>
> Today's findings are deliberately disjoint from all three sets.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest — same operational gap as 2026-06-11):** the repo ships the sanctioned front door — [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py), which pulls real subreddit listings via Reddit's official OAuth2 Data API. **That is the correct route for this scan.** It `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars were unset this session** (verified — `${REDDIT_CLIENT_ID:-NO}` / `${REDDIT_CLIENT_SECRET:-NO}` both returned `NO`). So the *structural* block (the crawler-UA 403 on reddit.com) is solved by the script; the *operational* gap — the one-time credential setup (create a "script" app at <https://www.reddit.com/prefs/apps>, export the two creds as session/CI secrets) — still hasn't landed in this environment.

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session (verified) |
| `WebFetch www.reddit.com/….json` | crawler-UA block (per the 2026-06-10 data-access-routes finding) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion snippets + practitioner write-ups |

**Provenance of the findings below:** drawn from Reddit-discussion aggregations + practitioner write-ups via unrestricted web search, cross-checked against primary Anthropic docs and this repo's own manifests — **not** from direct subreddit reads. This is the documented fallback, **not** the preferred route. **Carry-forward (now two scans running):** set the two Reddit creds and run `reddit-scan.py` first next time so findings come from real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `r/ClaudeAI best Claude Code tips workflows June 2026`
- `r/ClaudeAI Claude Code MCP server security risks scoping too many tools context bloat lessons 2026`
- `Claude Code CLAUDE.md memory file best practices imports hierarchy what to put what to avoid 2026`
- `Claude Code custom slash commands subagent output styles biggest community complaints June 2026 reddit`
- `Claude Code context window /compact auto-compact mid-task loss best practice avoid 2026`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Security (Claude Code)](https://code.claude.com/docs/en/security) (primary — MCP trust + tool-layer manipulation)
- Practitioner / community aggregations (read via search snippets): CSO Online "Claude Code has an MCP security problem", The Hacker News + Dark Reading (TrustFall / RCE), the "Complete Guide to CLAUDE.md" (Medium/Bijit Ghosh) + Buildcamp / Serenities CLAUDE.md guides, "Stop Claude Code from Lobotomizing Itself Mid-Task" + "Never Let Claude Code Auto-Compact Again" (auto-compact context-collapse write-ups).
- This repo's own [`AGENTS.md`](../../../AGENTS.md) §"The agent-description token budget (~15K)" — the internal anchor that makes Finding F1 high-fit and non-generic.

---

## 2. Findings (4 — all fresh vs. the three prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **F1** | **MCP tool definitions are per-turn context cost — prune the connected server set.** Every connected MCP server loads its tool definitions (names + descriptions + schemas) into context on **every turn**, not once. A community-cited figure is "up to ~18K tokens/turn" for a heavy server. Over-connecting servers silently eats the window and adds routing noise (a bigger menu to disambiguate) whether or not the tools are used. The fix: connect per-task, measure with `/context`, prefer the narrowest surface. | **Genuine gap.** No best-practice covers the MCP-tool-definition *runtime* budget. Closest neighbors: `focused-task-delegation-beats-full-context-dumps.md` (sub-agent context, not tools), `permissions-are-deny-ask-allow…` (`mcp_tools` as a *trust* category, not a *budget* one), and `docs/best-practices/bundled-mcp-servers.md` (server *packaging*, not how many a consumer connects). **And it is the exact mirror of the repo's own `AGENTS.md` ~15K agent-description budget** — RavenClaude already lives this rule one layer up. |
| **F2** | **CLAUDE.md: "less is more" — signal-to-noise beats volume; personality instructions ("act as a senior engineer") have near-zero measurable effect; use `/memory` to audit what's actually loaded; the import (`@file`) hierarchy expands inline and still counts against the window.** | **Partially covered.** `prefer-a-deterministic-gate-over-a-prose-rule.md`'s own "Use when" is *"reviewing a `CLAUDE.md` … and pruning the file"* — the pruning angle is already the rule's job. Net-new deltas (personality-instructions-are-noise; `/memory` as the audit command; imports-don't-reduce-tokens) are thin and risk restating the Anthropic memory docs verbatim. |
| **F3** | **Untrusted-repo auto-execution is a live RCE class (TrustFall and related, 2026): opening/cloning an untrusted repo can execute via hooks / MCP config / env vars and exfiltrate API keys; MCP manipulation is invisible because it happens at the tool layer, not in the visible conversation.** | **Covered in posture, moving in specifics.** The 2026-06-10 scan shipped the lethal-trifecta; core already ships the containment posture (`security_deny` floor over `~/.ssh`/`~/.aws`/…, devcontainer/worktree boundary), the web-access guardrail, and `SECURITY.md`. The net-new is a *specific, dated CVE-class advisory* — durable as a security-note, but a fast-moving target for a canonical best-practice. |
| **F4** | **Auto-compact mid-task causes "context collapse": it fires at a token threshold, not a clean task boundary, and the agent loses which files it edited / forgets repeated constraints. Mitigate by disabling auto-compact (`/config`) or compacting manually (`/compact`) at a clean boundary (~50–75%), finishing the micro-task first.** | **Covered.** The 2026-06-10 scan already covered context-compaction; the constitution's §"Context & Session Hygiene" + §"Context management" (summaries at natural boundaries, reference artifacts not raw history) teach the same principle. The Claude-Code-CLI knob names (`/compact`, `/config` toggle) are the only delta — thin. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to the three prior scans: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no _action_ on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (If Matt wants the live tribunal applied retroactively, `decision-review` over this doc's decisions is the surface.)

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **F1** | ✅ **Approve** | Passes all four. **Additive:** no rule covers the MCP-tool-definition runtime budget — the three neighbors cover sub-agent context, MCP *trust*, and MCP *packaging*, none the per-turn token cost. **In-scope & maximally on-theme:** context-budget discipline *is* RavenClaude's domain — the repo's own `AGENTS.md` documents the parallel ~15K agent-description budget and prescribes the identical "enable only what you need" response, so this is the least-generic possible framing (it states one layer down a rule the repo already lives). **Load-bearing:** per-turn definition cost is non-obvious (people assume startup-only), and the two failure modes (window pressure → earlier compaction; routing noise → wrong tool calls) both have observable cost. **Low-blast:** additive markdown. | Keep the specific ~18K figure marked `[unverified — community-reported]` and point at `/context` as the this-session check; ground the durable claim on the *mechanism* (per-turn definitions), not the number. Cross-link to the agent-description budget, the focused-task rule, and the permissions rule so it reads as a sibling, not a standalone. Scope the security angle to a "security still leads" edge-case so it doesn't drift into F3's territory. |
| **F2** | ⏸️ Defer | Borderline #1. The pruning angle is already `prefer-a-deterministic-gate-over-a-prose-rule.md`'s stated job; the genuinely-new deltas (personality-instructions-are-noise, `/memory`, imports-still-count) are thin and risk restating the Anthropic memory docs — generic-platform-101, which the core set excludes. | If a consumer-authoring guide is ever built (an `/init-agent-ready` companion on "structuring your own Claude Code setup"), fold the "less is more / `/memory` audit / imports-still-count" guidance there — not as a standalone core rule. |
| **F3** | ⏸️ Defer (to `SECURITY.md` / a domain plugin) | Fails #1 for a *durable best-practice*: the posture is covered (containment, `security_deny` floor, web-access guardrail, lethal-trifecta). A dated CVE-class advisory is real and valuable but is a **moving target** — canonizing a specific named vuln (TrustFall) in a best-practice ages badly; security advisories belong in `SECURITY.md` or a `cybersecurity-grc` knowledge note that's expected to churn. | Add a short "untrusted-repo auto-execution" note to `SECURITY.md` (or a `cybersecurity-grc` knowledge entry) the next time that surface is touched — with the date + CVE reference and an explicit "verify current status" marker. Not a core best-practice. |
| **F4** | ❌ Deny | Fails #1 — duplicate. The 2026-06-10 scan covered context-compaction and the constitution's §"Context & Session Hygiene" / §"Context management" teach the same principle (summaries at natural boundaries; reference artifacts not raw history). The only delta is the Claude-Code-CLI knob names (`/compact`, `/config` toggle), which are thin and host-specific. | If the prior compaction coverage is ever expanded, add the `/compact` / disable-auto-compact knob names as a Claude-Code-CLI subsection there — not a new rule. |

**Net:** 1 approved, 1 denied, 2 deferred. One solid, well-grounded addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 ("don't restate what's already enforced/covered") and the three prior scans' discipline (each landed exactly one tight rule).

---

## 4. Build plan (approved: F1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "MCP tool definitions cost context every turn — enable only the servers you need." Sections: Why (per-turn cost + the two failure modes + the `AGENTS.md` budget mirror) / How (per-task connect, `/context` to measure, narrowest surface, audit) / Edge cases (the every-turn server earns its place; bundled-vs-connected is a different question; security leads) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/mcp-tool-definitions-cost-context-every-turn-prune-the-server-set.md` | Follows the one-rule-per-file format of the existing 18 rules. |
| 2 | Index update: 18 → 19 rules; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.157.0 → **0.158.0**, mirrored. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` | CI fails on version drift between the two. |
| 4 | CHANGELOG top entry for 0.158.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-06-17-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. Markdown-only diff, but run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Security (Claude Code)](https://code.claude.com/docs/en/security) (MCP trust + tool-layer manipulation invisibility)
- Community / practitioner aggregations (read via search snippets): CSO Online ("Claude Code has an MCP security problem"), The Hacker News + Dark Reading (TrustFall / RCE class), the MCP context-overhead "~18K tokens/turn" write-ups, the "Complete Guide to CLAUDE.md" + Buildcamp / Serenities CLAUDE.md guides, "Stop Claude Code from Lobotomizing Itself Mid-Task" + "Never Let Claude Code Auto-Compact Again"
- This repo: [`AGENTS.md`](../../../AGENTS.md) §"The agent-description token budget (~15K)" (the internal anchor for F1)
- Prior runs: [`2026-06-09`](../2026-06-09-claude-subreddit-scan/README.md) · [`2026-06-10`](../2026-06-10-claude-subreddit-scan/README.md) · [`2026-06-11`](../2026-06-11-claude-subreddit-scan/README.md)
