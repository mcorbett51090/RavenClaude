# Claude subreddit scan — research, panel decision & build plan (2026-07-18)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), 3 denied (2 covered, 1 volatile). The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.207.0): **a `PostToolUse` hook is the deterministic quarantine for untrusted tool output — generalize the WebFetch sanitizer to every content channel.**

> This is the **twenty-second** run of this recurring scan. Prior runs (most recent first):
>
> - [2026-07-15](../2026-07-15-claude-subreddit-scan/README.md) — **drop-a-tier-for-grunt-work-subagents** (approved; the model-tier axis of the spawn decision).
> - [2026-07-14](../2026-07-14-claude-subreddit-scan/README.md) — **treat-repo-committed-`.claude`-config-as-untrusted-input** (approved; the _inbound static-config_ trust boundary).
> - [2026-07-09](../2026-07-09-claude-subreddit-scan/README.md) — **scope-a-skill-to-one-workflow / the-description-is-the-trigger** (approved).
> - [2026-07-07](../2026-07-07-claude-subreddit-scan/README.md) — **precompact-hook-is-the-deterministic-enforcer** (approved; the prose → hook mechanization shape).
> - [2026-07-03](../2026-07-03-claude-subreddit-scan/README.md) — **compact-proactively / persist-state-before-compaction** (approved).
> - [2026-07-02](../2026-07-02-claude-subreddit-scan/README.md) — **the OS-enforced Bash sandbox** (approved).
> - earlier: 2026-06-09 · 06-10 · 06-11 · 06-13 · 06-15 · 06-19 · 06-20 · 06-21 · 06-22 · 06-24 · 06-29 · 07-01 · 07-08 · 07-11.
>
> Today's net-new finding (H1) is the **runtime-tool-output** injection boundary. Two prior approvals bracket it without covering it: the 07-14 rule audits _static committed config_ (the inbound-config surface), and the `webfetch-hardening` skill sanitizes _one tool_ (`WebFetch`) via a per-agent contract. Neither generalizes the injection-quarantine to **every content-bearing tool result** (MCP issue/PR/ticket bodies, `Read`s of untrusted repos) nor turns it into a **deterministic hook** — the same knowledge/skill-names-it / no-rule-teaches-it gap the 07-07 `PreCompact` rule and the 07-14 config rule were each approved to close.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent dev communities about using Claude Code effectively.

**Route note (honest — same hard block as the 07-02 → 07-15 runs):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (Reddit's official OAuth2 Data API), which `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`. Both env vars were **UNSET this session** (verified), and the direct Reddit routes stayed hard-blocked:

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ the sanctioned route — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` UNSET this session |
| `WebSearch` with `allowed_domains:["reddit.com"]` | ❌ `400 — reddit.com is not accessible to our user agent` (Anthropic-crawler UA block — unchanged from every prior run) |
| `WebFetch` of reddit.com thread URLs | ❌ same UA block |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — surfaces practitioner write-ups + Reddit-discussion **aggregations** via search snippets |

**Provenance of the findings below:** practitioner write-ups + Reddit-discussion aggregations read via unrestricted web-search snippets, cross-checked against **this repo's own surface** (the 34-rule core best-practice set + the `webfetch-hardening` skill + the `knowledge/` bank + the 21 prior scans) and, for the approved item, **this-session primary-doc verification** of the `PostToolUse` hook payload (`hookSpecificOutput.updatedToolOutput` "replaces the tool's result" before the model reads it — confirmed against [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks) via WebFetch). This is the documented fallback — **not** direct subreddit reads (unreachable this session). **Standing next-scan action (carried again):** set `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` in the routine's environment and run `reddit-scan.py` first — with the web route to Reddit UA-blocked, the OAuth2 API is the only path to real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `r/ClaudeAI Claude Code tips hooks skills subagents 2026`
- `Claude Code hooks security risk prompt injection PostToolUse malicious 2026 discussion`
- `Claude Code context compaction /compact microcompact long session degradation community tips 2026`
- `reddit ClaudeAI Claude Code best practices CLAUDE.md agent orchestration July 2026`

**Sources mined (via search snippets):** SmartScope (Claude Code advanced best-practices — hooks/subagents/context), Totalum + ofox.ai (Skills vs Hooks vs Subagents vs MCP), MarkTechPost (Claude Code 2026 features), TrueFoundry + MintMCP + Pluto Security + SC Media + Lasso Security (prompt-injection defenses, the `PostToolUse` scanning hook, the leaked-source deny-rule subcommand-cap bypass), MindStudio + StackNotice + hidekazu-konishi + x-cmd (context-rot / `/compact` / microcompact).

---

## 2. Findings (4 — all checked against the 34-rule core set + the `webfetch-hardening` skill + the 21 prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Register a `PostToolUse` hook that scans/sanitizes _tool output_ for prompt-injection before Claude reads it.** Consensus, driven by Lasso Security's open-source `claude-hooks` (a `PostToolUse` hook "sitting between the untrusted world and Claude's context window") and the enterprise-security write-ups: the injection channel isn't only `WebFetch` — an MCP tool result (a GitHub issue/PR/review-comment body, a Jira ticket, an API response) and a `Read` of an untrusted repo carry the same untrusted bytes into the same window. A `PostToolUse` hook can return `updatedToolOutput`, which _replaces the result before the model sees it_ — the deterministic quarantine point. | **Genuine gap at the best-practice tier.** The [`webfetch-hardening`](../../../plugins/ravenclaude-core/skills/webfetch-hardening/SKILL.md) skill hardens **one tool** (`WebFetch`) via a **per-agent contract** (fires only if the agent remembers). No best-practice generalizes the boundary to _all_ content-bearing tool results, and none turns it into a **registered `PostToolUse` hook** (the deterministic-vs-advisory gap [`prefer-a-deterministic-gate`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md) warns about). Grep of `best-practices/` for `PostToolUse` / `updatedToolOutput` → **zero** rule-tier hits. Same shape as the approved 07-07 `PreCompact` rule (prose → hook) and the 07-14 config rule (knowledge-names-it → rule-teaches-it). **Additive.** |
| **H2** | **The leaked Claude Code source (npm, Mar 31 2026) contained a deny-rule bypass: `bashPermissions.ts` caps enforcement at 50 subcommands; exceed the cap and a denied command falls back to _ask_ instead of _block_.** | **Denied — volatile + product-version-specific.** A real, interesting mechanic, but it's a specific (likely-patched) implementation bug tied to one leaked build — exactly the volatility bar that denied 07-15's H2 (`/effort`) and 07-14's H2 (nested-`.claude` precedence). The durable lesson (don't lean on a deny-list as your only guard; layer the OS-enforced boundary) is already owned by [`the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow`](../../../plugins/ravenclaude-core/best-practices/the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow.md). Deny the standalone; nothing durable is lost. |
| **H3** | **Context rot in long sessions — run `/compact` proactively (~60% utilization), append `keep:` preservation instructions, persist load-bearing state first.** | **Denied — covered.** Owned by [`compact-proactively-and-persist-state-before-compaction`](../../../plugins/ravenclaude-core/best-practices/compact-proactively-and-persist-state-before-compaction.md) + [`precompact-hook-is-the-deterministic-enforcer`](../../../plugins/ravenclaude-core/best-practices/precompact-hook-is-the-deterministic-enforcer-of-persist-before-compaction.md) (07-03 / 07-07) + [`claude-md-imports-organize-they-dont-shrink-context`](../../../plugins/ravenclaude-core/best-practices/claude-md-imports-organize-they-dont-shrink-context.md). Deny (house-rule #4: don't restate what's covered). |
| **H4** | **"When to use which" — Skills (recurring expertise) vs Hooks (deterministic, every time) vs Subagents (clean context window) vs MCP (external tools).** | **Denied — covered.** The isolate-vs-steer axis is owned by [`subagent-isolates-clutter-skill-keeps-the-work-in-thread`](../../../plugins/ravenclaude-core/best-practices/subagent-isolates-clutter-skill-keeps-the-work-in-thread.md); the deterministic-gate axis by [`prefer-a-deterministic-gate-over-a-prose-rule`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md); the MCP-budget axis by [`mcp-tool-context-is-a-budget-enable-only-what-you-need`](../../../plugins/ravenclaude-core/best-practices/mcp-tool-context-is-a-budget-enable-only-what-you-need.md); plus [`orchestration-decision-trees.md`](../../../plugins/ravenclaude-core/knowledge/orchestration-decision-trees.md). Deny. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to every prior scan: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no _action_ on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably.

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook. _(For a lesson that IS in a skill/knowledge file but NOT in any consumer-facing best-practice, "additive" is satisfied at the best-practice tier — the 07-07 `PreCompact` / 07-14 committed-config precedent: a skill hardening one channel does not mean a rule teaches the generalized action.)_
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** zero `best-practices/` hits for `PostToolUse`/`updatedToolOutput`; the injection floor lives only as a WebFetch-scoped per-agent skill, and the best-practices are the consumer-facing surface. Two prior approvals _bracket_ this surface (07-14 static config; the WebFetch skill) without covering the runtime-tool-output channel or the deterministic-hook form. **In-scope:** injection defense on tool results is a Claude-Code/harness-specific mechanic (a `PostToolUse` hook + `updatedToolOutput`), not generic coding advice, and this repo _ships_ hooks + subscribes to `github-webhook-activity` events whose comment bodies are attacker-authored — doubly load-bearing. **Load-bearing:** the cost of omission is observable — an unsanitized MCP/issue-body injection is read at prompt-trust in the same window; the WebFetch skill fires only if an agent remembers its contract. **Low-blast:** additive markdown. | Keep it distinct from the `webfetch-hardening` skill: pitch at the **channel generalization** (WebFetch → all content-bearing tools) + the **deterministic-hook form** (`updatedToolOutput` replaces the result before the model reads it), not by re-teaching the injection threat model. Mark the hook payload field **verify-at-use** (the payload evolves; the durable fact is that `PostToolUse` can rewrite a tool result pre-read). Frame the hook as **fail-open** — the model-layer "treat output as DATA" discipline is the complement, not replaced. |
| **H2** | ❌ Deny | Fails on volatility (a specific, likely-patched bug in one leaked build — the 07-15 / 07-14 H2 bar). The durable "don't rely on a deny-list alone; layer the OS sandbox" half is already owned. | Revisit only if the class (not the single bug) recurs across releases. |
| **H3** | ❌ Deny | Fails #1 — covered by the proactive-compaction pair + the imports rule. | None. |
| **H4** | ❌ Deny | Fails #1 — covered by the three orchestration/MCP rules + the decision-trees knowledge file. | None. |

**Net:** 1 approved (H1), 3 denied (H2 volatile, H3+H4 covered). One solid, primary-doc-verified, load-bearing addition — the missing _runtime-tool-output_ injection boundary — beats padding a mature 34-rule set. Consistent with house-rule #4 and every prior scan's one-tight-rule discipline.

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "A `PostToolUse` hook is the deterministic quarantine for untrusted tool output." Sections: Why (the WebFetch skill's two boundaries — one-tool + remember-the-contract; the prose → hook shape) / How (register the hook; scope the matcher to externally-authored channels; return `updatedToolOutput`; reuse `sanitize-webfetch-body.py`; fail-open + bounded) / Edge cases (don't sanitize self-authored output; `PostToolUse` can't un-run a side effect — that's `PreToolUse`; replaces the read-copy not the raw bytes; model-layer discipline still primary; verify-at-use; non-Claude-Code hosts) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/posttooluse-hook-is-the-deterministic-quarantine-for-untrusted-tool-output.md` | Mirrors the one-rule-per-file format of the existing rules. |
| 2 | Index update: → **35 rules**; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.206.0 → **0.207.0**, mirrored across all three surfaces. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json` via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. |
| 4 | CHANGELOG top entry for 0.207.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-07-18-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook — so no count-string sync is needed. Markdown + manifest diff only; ran `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- Practitioner aggregations (read via unrestricted web-search snippets; several Reddit-sourced): SmartScope (Claude Code advanced best-practices — hooks/subagents/context), Totalum + ofox.ai (Skills vs Hooks vs Subagents vs MCP), MarkTechPost (Claude Code 2026 features), TrueFoundry / MintMCP / Pluto Security / SC Media (Claude Code prompt-injection risks + the deny-rule subcommand-cap bypass), Lasso Security ([`lasso-security/claude-hooks`](https://github.com/lasso-security/claude-hooks) — the open-source `PostToolUse` injection-defense hook), MindStudio / StackNotice / hidekazu-konishi / x-cmd (context-rot / `/compact` / microcompact).
- **Primary-doc verification (this session):** [Claude Code hooks reference](https://code.claude.com/docs/en/hooks) — `PostToolUse` fires "after a tool call succeeds"; `hookSpecificOutput.updatedToolOutput` "replaces the tool's result" before the model reads it; `PreToolUse` (not `PostToolUse`) is the event that blocks a call via `permissionDecision: "deny"`.
- Cross-checked against this repo: [`skills/webfetch-hardening/SKILL.md`](../../../plugins/ravenclaude-core/skills/webfetch-hardening/SKILL.md) (the WebFetch-only floor + `sanitize-webfetch-body.py` + the two 2026-06-02 in-wild injections), [`best-practices/treat-repo-committed-claude-config-as-untrusted-input.md`](../../../plugins/ravenclaude-core/best-practices/treat-repo-committed-claude-config-as-untrusted-input.md), [`best-practices/precompact-hook-is-the-deterministic-enforcer-of-persist-before-compaction.md`](../../../plugins/ravenclaude-core/best-practices/precompact-hook-is-the-deterministic-enforcer-of-persist-before-compaction.md), [`best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md).
- Prior runs: [`2026-07-15`](../2026-07-15-claude-subreddit-scan/README.md) · [`2026-07-14`](../2026-07-14-claude-subreddit-scan/README.md) · [`2026-07-07`](../2026-07-07-claude-subreddit-scan/README.md) · [`2026-07-03`](../2026-07-03-claude-subreddit-scan/README.md) · [`2026-07-02`](../2026-07-02-claude-subreddit-scan/README.md).
