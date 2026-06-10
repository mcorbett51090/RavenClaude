# Claude subreddit scan — research, panel decision & build plan (2026-06-10)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 fresh findings surfaced (none overlapping the 2026-06-09 scan) → **1 approved**, 1 denied, 2 deferred. The approved item shipped as one new consumer-facing best-practice in `ravenclaude-core` (v0.149.0).

> This is the second run of this recurring scan. The [2026-06-09 scan](../2026-06-09-claude-subreddit-scan/README.md) covered the obvious community lessons (deterministic-hooks-vs-advisory-CLAUDE.md, model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene) and approved one (the deterministic-gate rule, shipped in v0.139.0). Today's findings are deliberately disjoint from that set.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, and adjacent communities about using Claude Code effectively.

**Route note (honest — re-verified this session, six routes):** `reddit.com` is **blocked at the source for Anthropic's web crawler**, not merely by this environment's network policy. The evidence:

| Route | Result |
| --- | --- |
| `WebFetch www.reddit.com/...` | "Claude Code is unable to fetch from www.reddit.com" |
| `WebFetch old.reddit.com/...` | same block |
| `WebFetch reddit.com/....json` | same block |
| `WebFetch reddit.com/....rss` | same block |
| `redlib` privacy mirror | HTTP 403 |
| `WebSearch allowed_domains:[reddit.com]` | **400 — "domains not accessible to our user agent"** (the definitive signal: Reddit blocks Anthropic's crawler — see the linked Anthropic support article) |

Per the repo's Capability-Grounding / accuracy discipline, that is a verified property of **the Reddit↔Anthropic-crawler route**, not a failure to try. The working route was **unrestricted web search**, which surfaces Reddit-discussion content via search snippets and third-party aggregations. **Findings below are therefore drawn from Reddit-discussion aggregations + practitioner write-ups, cross-checked against primary Anthropic docs — not from direct subreddit reads.** Flagged so a future session doesn't over-trust the provenance.

**Queries run (working route):**

- `Claude Code checkpoints rewind Esc Esc feature undo community reaction 2026`
- `MCP lethal trifecta prompt injection private data exfiltration Claude Code security 2026`
- `Claude Code context compaction microcompact /compact managing context window best practice 2026`
- `Claude Code subagent description routing dispatch how Claude chooses agent best practice writing descriptions`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Claude Code checkpointing](https://code.claude.com/docs/en/checkpointing) (primary)
- [Anthropic — Manage context / costs](https://code.claude.com/docs/en/costs) + [Compaction (API docs)](https://platform.claude.com/docs/en/build-with-claude/compaction) (primary)
- [Anthropic — Create custom subagents](https://code.claude.com/docs/en/sub-agents) (primary)
- [Simon Willison — lethal-trifecta tag](https://simonwillison.net/tags/lethal-trifecta/) + [OWASP MCP Top 10 coverage / UpGuard MCP incidents](https://www.upguard.com/blog/mcp-security-incidents) (community/security)
- Practitioner aggregations: dev.to "Double Esc to Rewind", BSWEN "/clear, /compact, /rewind explained", builder.io subagents guide (read via search snippets; several 403 on direct fetch)

---

## 2. Findings (4 — all fresh vs. the 2026-06-09 scan)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| G1 | **Checkpoints / `/rewind` (Esc-Esc) are Claude Code's recovery layer** — every prompt is snapshotted; restore code, conversation, or both. Community frames it as "fearless experimentation." The non-obvious corollary: a checkpoint reverts Claude's **edits + conversation**, NOT `Bash` side-effects / network / external state. | **No consumer-facing rule.** `grep -ri 'rewind\|checkpoint'` over the repo returns only Flink/data-streaming checkpoints, git checkpoints, and FORGE — nothing on Claude Code's session checkpoints. `knowledge/concepts/context-window.md` covers compaction, not rewind. The repo has rich _prevention_ (runaway/dod/task-scope/guard-destructive/tribunal/containment) + git recovery (`branch-archive`) but no _recovery-layer_ rule. **Genuine gap.** |
| G2 | **The "lethal trifecta"** — an agent with (a) access to private data, (b) exposure to untrusted content, and (c) an exfiltration vector is unconditionally exploitable by indirect prompt injection. 2026 incidents + the concrete Claude-Code `ANTHROPIC_BASE_URL` hijack (Check Point, Feb 2026). | **Substantially covered.** `claude-app-engineering/best-practices/untrusted-content-stays-untrusted.md` names the posture + the three dangerous outcomes (widen tools / auto-approve destructive / exfiltrate); core ships the web-access allow/deny list, the MCP server allowlist, the containment posture, the tribunal's injection hardening + egress-secret backstop, and a WebFetch body sanitizer. |
| G3 | **Context-compaction discipline** — run `/compact` at phase boundaries (before degradation, not after), use `/context` to monitor, and know the root `CLAUDE.md` survives compaction while nested/path-scoped rules can be dropped. | **Covered + borderline-generic.** `knowledge/concepts/context-window.md` teaches the compaction model (desk-not-filing-cabinet, root-CLAUDE.md-survives, durable facts → committed files); `claude-app-engineering/knowledge/context-engineering-2026.md` covers context editing/compaction. The close cousin (the `/clear` hygiene rule, F5) was **deferred** in the 2026-06-09 scan as borderline-generic. |
| G4 | **Subagent description = trigger-condition triage rule + job-shaped names; auto-selection is unreliable** ("Use this agent when X; it returns Y." Job-shaped names like `repo-explorer` route better than `frontend-engineer". Claude often handles tasks in the main session even when an agent matches). | **Mostly covered by template + architecture.** `templates/agent-definition-template.md` already mandates "Clear trigger conditions" + "explicit conditions for when *not* to use it"; `AGENTS.md` caps each description ≤300 chars for routing. RavenClaude's orchestrator-worker model (the Team Lead **explicitly** dispatches; sub-agents never self-spawn) is designed *around* auto-selection unreliability rather than relying on it. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to the 2026-06-09 scan: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no _action_ on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (If Matt wants the live tribunal applied retroactively, `decision-review` over this doc's decisions is the surface.)

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (in core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **G1** | ✅ **Approve** | Passes all four. The repo proves it cares about the prevention↔recovery axis (the whole guardrail stack) yet ships **no** recovery-layer rule — a real gap for the `/init-agent-ready` audience. It is in-scope because the load-bearing content is _not_ "how to press a button" but the **boundary** (checkpoints can't undo `Bash` side-effects/external state) and how it **composes** with this repo's own `guard-destructive` / `branch-archive` / containment posture — that framing is RavenClaude-grounded, not generic. High cost when missed (a session "rewinds" and acts as if a destructive side-effect never happened). | Kept tight + cross-linked to the prevention rules and `branch-archive` to avoid drift; the Claude-Code-specific `/rewind` half is explicitly scoped away from Copilot in the edge-cases section. |
| **G2** | ❌ Deny | Fails #1 and #2. The posture is already named in `claude-app-engineering/untrusted-content-stays-untrusted.md` and lived by core's web-access list + MCP allowlist + containment posture + tribunal injection hardening. A core restatement duplicates and crosses house-rule #1 (core stays domain-neutral; deep AI-app security lives in its plugin) and #4 (don't restate what's enforced/covered). | The concrete `ANTHROPIC_BASE_URL` hijack is a real, recent, Claude-Code-specific threat — but it belongs in the `security-engineering` plugin (or a `claude-app-engineering` scenario), **not** core. Noted as a candidate for a future security-plugin scan, not shipped here. |
| **G3** | ⏸️ Defer | Fails #1 (covered by `context-window.md` + `context-engineering-2026.md`) and borderline #2 (generic). Directly consistent with the 2026-06-09 deferral of its `/clear` cousin. | Revisit only if a concrete compaction-survival failure is observed (e.g. a nested-CLAUDE.md rule silently dropped mid-task with a measurable cost). |
| **G4** | ⏸️ Defer | Borderline #1: the actionable half (trigger-condition descriptions, when-NOT conditions) is already in `agent-definition-template.md`; the net-new nugget (auto-selection unreliability) is real but thin for a standalone rule, and RavenClaude's explicit-dispatch architecture already mitigates it by design. | If a consumer-authored-subagent guide is ever built, fold the "job-shaped names + auto-selection is unreliable, so dispatch explicitly" nugget in there rather than as a one-off rule. |

**Net:** 1 approved, 1 denied, 2 deferred. One solid, well-grounded addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 ("don't restate what's already enforced/covered") and with the prior scan's discipline.

---

## 4. Build plan (approved: G1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "Checkpoints / `/rewind` are the recovery layer — they undo Claude's edits, not the world's side-effects." | `plugins/ravenclaude-core/best-practices/checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md` | Follows the one-rule-per-file format (Why / How / Edge cases / See also / Provenance). |
| 2 | Index update: 16 → 17 rules; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.148.0 → **0.149.0**, mirrored. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` | CI fails on version drift between the two. |
| 4 | CHANGELOG top entry for 0.149.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-06-10-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. Markdown-only diff, but run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Claude Code checkpointing](https://code.claude.com/docs/en/checkpointing)
- [Anthropic — Manage context / costs](https://code.claude.com/docs/en/costs) · [Compaction — Claude API](https://platform.claude.com/docs/en/build-with-claude/compaction)
- [Anthropic — Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Simon Willison — lethal-trifecta](https://simonwillison.net/tags/lethal-trifecta/) · [UpGuard — Six MCP security incidents](https://www.upguard.com/blog/mcp-security-incidents)
- [Anthropic support — does Anthropic crawl the web / how site owners block the crawler](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) (the Reddit-block evidence)
- Prior run: [`docs/research/2026-06-09-claude-subreddit-scan/README.md`](../2026-06-09-claude-subreddit-scan/README.md)
