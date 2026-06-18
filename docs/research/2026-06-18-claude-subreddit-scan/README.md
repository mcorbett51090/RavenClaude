# Claude subreddit scan — research, panel decision & build plan (2026-06-18)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 5 findings surfaced (disjoint from the 2026-06-09/10/11 scans) → **1 approved**, 1 deferred, 2 denied-as-covered, 1 deferred-to-domain-plugin. The approved item shipped as one new consumer-facing best-practice in `ravenclaude-core` (v0.158.0).

> This is the **fourth** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions three-tier (approved), skills-vs-subagents-vs-MCP, headless-CI cost, thinking budgets.
>
> Today's findings are deliberately disjoint from all three sets.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest — same as the 2026-06-11 run):** the repo ships the sanctioned front door — [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py), which pulls real subreddit listings via Reddit's official OAuth2 Data API. **It is still the correct route, and this run still couldn't use it:** the script `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars were unset this session** (verified — `python3 -c "os.environ..."` returned UNSET for both; `python3 scripts/reddit-scan.py` printed its usage/`_die` with no creds). The one-time setup (create a "script" app at <https://www.reddit.com/prefs/apps>, export the two creds as session/CI secrets) still hasn't landed in this environment.

So this run used the **documented fallback** again — unrestricted `WebSearch` over Reddit-discussion aggregations + practitioner write-ups, cross-checked against primary Anthropic docs. **Next scan: set the two Reddit creds and run `reddit-scan.py` first** so findings come from real subreddit listings (closing the provenance gap for good).

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ the sanctioned route — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session |
| `WebFetch www.reddit.com` / mirrors | crawler-UA block / 403 (unchanged from prior runs) |
| `WebFetch morphllm.com/claude-code-reddit` (a Reddit aggregation) | HTTP 403 on direct fetch — read via search snippet only |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion snippets + practitioner write-ups |

**Queries run (fallback route):**

- `Claude Code CLAUDE.md too long context bloat keep under 200 lines lessons reddit 2026`
- `Claude Code MCP server too many tools context window token budget disable lessons 2026`
- `Claude Code output styles vs CLAUDE.md vs subagents when to use reddit 2026`
- `Claude Code slash command vs skill vs subagent authoring reusable workflow reddit lessons 2026`
- `Claude Code verification loop test self-review hallucinated done not actually working reddit 2026`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp) (primary — MCP connection model)
- [Anthropic — Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) (primary)
- Practitioner aggregations (read via search snippets; several 403 on direct fetch): morphllm "Claude Code Reddit: What Developers Actually Say (2026)", Scott Spence "Optimising MCP Server Context Usage in Claude Code", BSWEN "Stop MCP Servers From Eating Your Claude Context Tokens", Joe Njenga (Medium) "Claude Code Just Cut MCP Context Bloat by 46.9% with Tool Search", Start Debugging "Reduce the Number of MCP Tools Claude Loads", alexop.dev "Claude Code Customization: CLAUDE.md, Slash Commands, Skills, and Subagents".
- Claude Code issue [#11364](https://github.com/anthropics/claude-code/issues/11364) "Lazy-load MCP tool definitions to reduce context usage" (the feature-history anchor for Tool Search).

---

## 2. Findings (5 — all fresh vs. the three prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **MCP tool definitions are a context budget paid at session start.** Every connected MCP server loads all its tool defs into the system prompt before the first message (community: ~67K tokens / ~34% of 200K for 7 servers). Levers: defer/Tool Search (`defer_loading` — ~47% cut), enable only what's needed this session, prune chatty servers. | **Net-new — genuine gap.** `grep` over `best-practices/` for `defer_loading`/`Tool Search`/`tool definitions`/`MCP context budget` → **no rule**. AGENTS.md covers the ~15K **agent-description** budget (subagent routing) — a *different* budget. The root CLAUDE.md documents the deferred-MCP/`ToolSearch` *mechanism* but never as a consumer-facing cost rule. |
| **H2** | **CLAUDE.md is always-on context — keep it lean (≤200 lines), use hooks for must-happen-every-time actions, start ~20-30 lines and add rules only when you catch repetition.** | **Half-covered + generic risk.** The hooks-vs-prose half is squarely `prefer-a-deterministic-gate-over-a-prose-rule.md`. The "keep it lean" half is real but is platform-101 the Anthropic docs already state, and the repo's own (huge) CLAUDE.md is a deliberate constitution, not a counter-example to cite. |
| **H3** | **Slash command vs skill vs subagent vs CLAUDE.md — pick the right primitive** (explicit terminal entry / auto-applied richer workflow / context isolation / always-true convention). | **Already adjudicated.** This is materially H1 from the 2026-06-11 scan, which was **deferred** as covered-by-authoring-rule + generic-platform-explainer. No change in disposition. |
| **H4** | **Force a self-verification pass before claiming done — it eliminates 80-90% of confident hash/path hallucinations** (Opus states invented commit hashes/paths with the same certainty as real ones). | **Heavily covered — duplicate.** `three-epistemic-protocols.md`, the Claim-Grounding & Source-Honesty protocol (cite-the-this-session-check-or-mark-`[unverified]`), and the `dod-gate.sh` definition-of-done gate already target exactly this. |
| **H5** | **After several auto-compactions a long session degrades (one benchmark: 18 min vs 4.5 min) — start a fresh session and commit frequently rather than pushing a degraded one.** | **Adjacent — covered in principle.** The 2026-06-10 scan covered context-compaction; CLAUDE.md's "Context & Session Hygiene" + `checkpoints-are-the-recovery-layer` cover the commit-frequently + recovery half. The "start fresh after N compactions" heuristic is a thin, host-version-sensitive delta. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to the three prior scans: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no *action* on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (If Matt wants the live tribunal applied retroactively, `decision-review` over this doc's decisions is the surface.)

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** confirmed by `grep` — no best-practice covers the MCP tool-definition context tax; the ~15K agent-description budget in AGENTS.md is a *different* budget on a *different* lever (routing, not the conversation window). **In-scope:** maximally on-brand — this marketplace ships ~100 plugins and many MCP servers, and **its own architecture defers MCP tools behind `ToolSearch`**, so the rule documents a discipline the repo already lives. **Load-bearing:** losing ~34% of the window before the first message is a measured, non-obvious cost with a concrete fix. **Low-blast:** additive markdown. | Token figures are community benchmarks → marked `[unverified — community benchmarks]` inline and cited as order-of-magnitude, not guarantees. Kept tight; cross-linked to the permissions rule (manage-your-tool-surface sibling) and the root CLAUDE.md deferred-tools note. The "different from the agent-description budget" distinction is stated explicitly to prevent the two being conflated. |
| **H2** | ⏸️ Defer | Fails #1 partially (hooks-vs-prose half is `prefer-a-deterministic-gate-over-a-prose-rule.md`) and brushes #2 (the lean-CLAUDE.md half is platform-101 the docs already teach). | If a consumer-authoring guide is built (an `/init-agent-ready` companion), fold a "keep CLAUDE.md lean; promote repeated rules to hooks" note there, grounded in the existing deterministic-gate rule — not as a standalone core rule. |
| **H3** | ⏸️ Defer (already adjudicated) | Same finding the 2026-06-11 scan deferred (its H1). Disposition unchanged — the authoring half is covered, the consumer "which primitive" half risks restating the Anthropic docs. | Revisit only if a primitive-selection table earns a home in a future authoring guide. |
| **H4** | ❌ Deny | Fails #1 — duplicate. The three-epistemic-protocols triad + Claim-Grounding (cite-or-`[unverified]`) + the `dod-gate.sh` Stop gate already encode "verify before you claim done," with *enforced* teeth the prose nugget lacks. | Nothing to add; the existing stack is stronger (a hook, not just advice). |
| **H5** | ⏸️ Defer (to a domain plugin / existing coverage) | Fails #1 — the commit-frequently + recovery half is covered (`checkpoints-are-the-recovery-layer`, CLAUDE.md Context & Session Hygiene); the residual "start fresh after N compactions" heuristic is thin and host-version-sensitive. | If a concrete "degraded-session cost X" case appears, add a one-line note to `checkpoints-are-the-recovery-layer` rather than a new rule. |

**Net:** 1 approved, 2 deferred, 1 deferred-as-already-adjudicated, 1 denied. One solid, well-grounded addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 ("don't restate what's already enforced/covered") and the three prior scans' discipline (each landed exactly one tight rule).

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "MCP tool definitions are a context budget — defer or disable, don't connect-and-forget." Sections: Why (the startup tax + the agent-description-budget distinction) / How (3 levers cheapest-first: defer/Tool Search, enable-only-needed, prune) / Edge cases (always-on servers, hosts without deferral, headless CI) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/mcp-tool-definitions-are-a-context-budget-not-free.md` | Follows the one-rule-per-file format of the existing 18 rules. |
| 2 | Index update: 18 → 19 rules; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.157.0 → **0.158.0**, mirrored. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` | CI fails on version drift between the two. |
| 4 | CHANGELOG top entry for 0.158.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-06-18-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. Markdown + two one-line JSON version edits, but run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)
- [Anthropic — Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
- Claude Code issue [#11364 — Lazy-load MCP tool definitions to reduce context usage](https://github.com/anthropics/claude-code/issues/11364)
- Practitioner aggregations (read via search snippets): morphllm "Claude Code Reddit: What Developers Actually Say (2026)", Scott Spence (MCP context optimisation), BSWEN (MCP token optimization), Joe Njenga / Medium (Tool Search 46.9% cut), Start Debugging (reduce MCP tools loaded), alexop.dev (Claude Code customization)
- Prior runs: [`2026-06-09`](../2026-06-09-claude-subreddit-scan/README.md) · [`2026-06-10`](../2026-06-10-claude-subreddit-scan/README.md) · [`2026-06-11`](../2026-06-11-claude-subreddit-scan/README.md)
