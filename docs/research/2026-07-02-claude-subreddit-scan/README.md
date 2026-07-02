# Claude subreddit scan — research, panel decision & build plan (2026-07-02)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), 1 deferred-as-next-candidate, 2 denied-as-covered. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.183.0).

> This is the **eleventh** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions three-tier `deny`/`ask`/`allow` (approved).
> - [2026-06-13](../2026-06-13-claude-subreddit-scan/README.md) — git-worktrees for parallel Claude instances (approved) + a correction to the `subagent-isolation` premise.
> - [2026-06-15](../2026-06-15-claude-subreddit-scan/README.md) · [2026-06-19](../2026-06-19-claude-subreddit-scan/README.md) · [2026-06-20](../2026-06-20-claude-subreddit-scan/README.md) · [2026-06-21](../2026-06-21-claude-subreddit-scan/README.md).
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — **MCP tool-context budget** (approved → the count→cost rule).
> - [2026-06-24](../2026-06-24-claude-subreddit-scan/README.md) — **keep-SKILL.md-bodies-lean / progressive disclosure** (approved).
>
> Today's net-new finding (H1) is disjoint from all prior sets. It is the **OS-enforcement sibling** of the 06-11 `permissions-are-deny-ask-allow` rule: that rule owns the *model-evaluated* layer (`deny`/`ask`/`allow`); H1 owns the *OS-enforced* layer (the Bash sandbox) that closes a gap the model layer structurally can't reach.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest — unchanged from the prior scans):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py), which pulls real subreddit listings via Reddit's official OAuth2 Data API. It `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars were unset this session** (verified this session — `os.environ` check returned `False` for both). So — exactly as in the prior runs — this scan fell back to unrestricted web search.

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session (re-verified) |
| `WebFetch https://www.reddit.com/...` | ❌ Anthropic crawler-UA block (the structural block `reddit-scan.py` exists to route around) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion aggregations + practitioner write-ups + primary Anthropic docs |

**Provenance of the findings below:** drawn from Reddit-discussion aggregations + practitioner write-ups via unrestricted web search, cross-checked against **primary Anthropic docs** and **this repo's own surface** — **not** from direct subreddit reads. This is the documented fallback, **not** the preferred route. **Standing next-scan action (carried again): set the two Reddit creds and run `reddit-scan.py` first** so findings come from real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `Claude Code reddit June 2026 new feature workflow discovery subagents context`
- `Claude Code sandbox bash permissions autonomous long-running agent reddit 2026`
- `Claude Code output styles plan mode context compaction microcompact tips 2026`
- `r/ClaudeAI Claude Code tips best practices July 2026`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Configure the sandboxed Bash tool](https://code.claude.com/docs/en/sandboxing) (primary — Seatbelt/bubblewrap OS enforcement, auto-allow mode, the `sandbox.*` settings + `credentials` block, the both-halves warning, the TLS/host-not-inspected limitation) and [Making Claude Code more secure and autonomous with sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing) (the 84%-prompt-reduction + autonomy framing)
- [Anthropic — Best practices](https://code.claude.com/docs/en/best-practices), [Sub-agents](https://code.claude.com/docs/en/sub-agents), [Orchestrate subagents at scale with dynamic workflows](https://code.claude.com/docs/en/workflows) (primary — for the H3/H4 already-covered checks)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): claudefa.st (sandbox guide), paulgp.substack (permissions/sandboxes/autonomous agents), SmartScope (advanced best practices), MindStudio / okhlopkov / knightli (context compaction + microcompact).

---

## 2. Findings (4 — all checked against the 24-rule core set + the 10 prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Enable the OS-enforced Bash sandbox — it's the complement to `deny`/`ask`/`allow`, not an alternative.** Permission rules are evaluated *before* a command runs, from the command string; the sandbox (Seatbelt on macOS, bubblewrap on Linux/WSL2) is enforced *while* it runs, by the OS, on the process and every child — so it holds "regardless of what the model chose to run and even if an allowed command does more than its name suggests." It closes the subprocess-access hole `deny` rules can't (`Read(**/.env)` deny ≠ blocking `python -c "open('.env')"`), and in **auto-allow mode** it earns prompt-free autonomy (Anthropic: **84% fewer prompts**) without `--dangerously-skip-permissions`. | **Genuine gap (consumer-facing).** The 06-11 `permissions-are-deny-ask-allow` rule owns the *model layer*; the `containment-posture` **concept card** + the CLAUDE.md "Containment posture" milestone mention the sandbox but frame it around the **Copilot-portability caveat** ("Claude-only; we don't ship a portable sandbox config"). `knowledge/claude-code-permissions.md:93` explicitly *names the gap the sandbox fills* — "OS-level enforcement requires the Claude Code sandbox feature" — but **no best-practice teaches a consumer to actually turn it on**, configure the both-halves (fs + network) defaults, or close the credential-read default. Grep of `best-practices/` for "sandbox" → **zero rule hits.** |
| **H2** | **Compact context proactively (~before quality degrades, not at 95% full), and persist load-bearing state to the filesystem *before* compaction** — `/compact` discards intermediate reasoning, rejected approaches, and verbose tool output, so a plan/decision that lives only in the conversation is lost; write it to a file or a test first. Microcompact runs a cheap noise-cleanup pass before the expensive summarization. | **Adjacent / partially covered — the strongest *next* candidate.** `checkpoints-are-the-recovery-layer` covers `/rewind` vs commits, `claude-md-imports` + `mcp-tool-context-is-a-budget` cover context *cost*, and the CLAUDE.md "Context & Session Hygiene" section covers "reference artifacts, not full history." But **no rule states the compaction discipline itself** (proactive-not-reactive; persist-before-compact because reasoning is discarded). Real and net-new, but partially shadowed — hold to the one-tight-rule discipline this round; H1 is the cleaner net-new. |
| **H3** | **Delegate read/search to a subagent (the built-in `Explore` agent) so file discovery burns the subagent's context, not the main window; write dynamic workflows to orchestrate fleets at zero coordination-token cost.** | **Covered.** `delegate-reads-fan-out-keep-branch-writes-in-main.md` + `focused-task-delegation-beats-full-context-dumps.md` own the read-delegation pattern; `knowledge/dynamic-workflows.md` + the Learn-tab `subagents`/`forge` concepts own the orchestration story. Deny — duplicate. |
| **H4** | **`/clear` between unrelated tasks; a fresh session with a sharper prompt beats a long session full of failed attempts; prune CLAUDE.md ("if I remove this line, will Claude make a mistake?").** | **Covered — duplicate.** `/clear` hygiene was a 06-09-scan finding; CLAUDE.md pruning is owned by `prefer-a-deterministic-gate-over-a-prose-rule.md` + `claude-md-imports-organize-they-dont-shrink-context.md`. Generic session hygiene, already surfaced. Deny. |

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
| **H1** | ✅ **Approve** | Passes all four. **Additive:** grep of `best-practices/` for "sandbox" returns zero rule hits; the topic is mentioned only in a concept card + a milestone, both framed around the *Copilot-portability caveat*, not the *consumer should enable it* guidance — and the repo's own `knowledge/claude-code-permissions.md:93` names the exact gap ("OS-level enforcement requires the Claude Code sandbox feature") with no rule closing it. **In-scope:** permission posture is core's home turf; this is the OS-enforced sibling of the shipped `permissions-are-deny-ask-allow` rule. **Load-bearing:** the deny/ask/allow rule has a documented, exploitable hole (subprocess reads) that *only* the sandbox closes, plus the 84%-fewer-prompts autonomy dividend — a real, measurable cost + benefit. **Low-blast:** additive markdown. | Keep it tight and cross-linked to `permissions-are-deny-ask-allow` (the model-layer sibling) and `claude-code-permissions.md` (the gap + the sandbox-escape CVE history). Frame it as a *risk reducer, not a hard boundary* (TLS-not-inspected, broad-domain exfil, `enableWeakerNestedSandbox`), keep the Claude-only caveat consistent with `containment-posture`, and mark the version/platform facts verify-at-use (the feature is evolving — `credentials` landed v2.1.187). |
| **H2** | ⏸️ Defer (next-scan candidate) | Real and net-new (no rule states the compaction discipline), but partially shadowed by `checkpoints-...`, the context-cost rules, and the CLAUDE.md hygiene section. Per the prior scans' one-tight-rule discipline, don't ship two adjacent context rules in one round — H1 is the cleaner net-new. | Promote next scan as **"compact proactively; persist load-bearing state before compaction (intermediate reasoning is discarded)"**, grounded in the Anthropic compaction docs + `knowledge/concepts/context-window.md`. |
| **H3** | ❌ Deny | Fails #1 — duplicate. Read-delegation is owned by `delegate-reads-fan-out-...` + `focused-task-delegation-...`; dynamic-workflow orchestration by `knowledge/dynamic-workflows.md`. | None — cleanly covered. |
| **H4** | ❌ Deny | Fails #1 — duplicate. `/clear` hygiene was a 06-09 finding; CLAUDE.md pruning is owned by two existing rules. Generic session hygiene. | None. |

**Net:** 1 approved (H1), 1 deferred-as-next-candidate (H2), 2 denied (H3, H4). One solid, well-grounded addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 ("don't restate what's already enforced/covered") and the prior scans' discipline (each landed exactly one tight rule).

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "The Bash sandbox is the OS-enforced complement to deny / ask / allow." Sections: Why (before-vs-during, the subprocess gap it closes, the 84%-autonomy dividend) / How (turn it on + prefer it over bypass, both-halves fs+network, close the credential-read default, the two layers stack) / Edge cases (platform, risk-reducer-not-boundary, scope, non-Claude hosts) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow.md` | Follows the one-rule-per-file format of the existing rules. |
| 2 | Index update: → **25 rules**; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.182.1 → **0.183.0**, mirrored across all three. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json` via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. |
| 4 | CHANGELOG top entry for 0.183.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-07-02-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook — so no count-string sync is needed. Markdown + manifest diff only; run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Configure the sandboxed Bash tool](https://code.claude.com/docs/en/sandboxing) · [Making Claude Code more secure and autonomous with sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [Anthropic — Best practices](https://code.claude.com/docs/en/best-practices) · [Sub-agents](https://code.claude.com/docs/en/sub-agents) · [Orchestrate subagents at scale with dynamic workflows](https://code.claude.com/docs/en/workflows)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): claudefa.st, paulgp.substack, SmartScope, MindStudio / okhlopkov / knightli.
- Cross-checked against this repo: `plugins/ravenclaude-core/knowledge/claude-code-permissions.md` (the subprocess-access gap), `best-practices/permissions-are-deny-ask-allow-not-an-on-off-switch.md` (the model-layer sibling), `knowledge/concepts/containment-posture.md` (the Claude-only caveat).
- Prior runs: [`2026-06-09`](../2026-06-09-claude-subreddit-scan/README.md) · [`2026-06-11`](../2026-06-11-claude-subreddit-scan/README.md) · [`2026-06-22`](../2026-06-22-claude-subreddit-scan/README.md) · [`2026-06-24`](../2026-06-24-claude-subreddit-scan/README.md)
