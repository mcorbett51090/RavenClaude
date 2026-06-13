# Claude subreddit scan — research, panel decision & build plan (2026-06-13)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 fresh findings surfaced (none overlapping the 2026-06-09 / 2026-06-10 / 2026-06-11 scans) → **1 approved**, 1 deferred-as-covered, 1 denied-as-duplicate, 1 deferred. The approved item shipped as one new consumer-facing best-practice in `ravenclaude-core` (v0.158.0).

> This is the **fourth** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (**approved**), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (**approved**), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions-three-tier (**approved**), skills-vs-subagents-vs-MCP, headless-CI-cost-guardrails, thinking-budgets.
>
> Today's findings are deliberately disjoint from all three sets.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (unchanged from 2026-06-11 — the operational gap persists):** the sanctioned front door for this scan is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (Reddit's official OAuth2 Data API). It `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars are still unset this session** (verified — `os.environ` check returned unset for both). The one-time credential setup (a "script" app at <https://www.reddit.com/prefs/apps>, two creds exported locally or as CI/Codespace secrets) still hasn't landed in this environment. So the *structural* block (Reddit blocks Anthropic's crawler UA) was solved long ago by `reddit-scan.py`; the *operational* gap is purely the missing credentials.

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session |
| `WebFetch www.reddit.com/....json` | crawler-UA block (per prior scans) |
| `WebSearch allowed_domains:[reddit.com]` | 400 — "domains not accessible to our user agent" (per prior scans) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion snippets + practitioner write-ups |

**Provenance of the findings below:** drawn from Reddit-discussion aggregations + practitioner write-ups via unrestricted web search, cross-checked against primary Anthropic docs + the git-worktree docs — **not** from direct subreddit reads. This is the documented fallback, **not** the preferred route. **Next scan: set the two Reddit creds and run `reddit-scan.py` first** so findings come from real subreddit listings (closing the provenance gap for good — this is now the third scan to record the same unmet setup step).

**Queries run (fallback route — unrestricted web search):**

- `r/ClaudeAI CLAUDE.md memory file bloat lean keep short imports hierarchy lessons 2026`
- `Claude Code git worktrees parallel sessions multiple agents reddit workflow`
- `Claude Code spec-driven development write plan first verification loop self-review subagent reddit`
- `Claude Code custom slash commands output styles reusable prompts best practices 2026`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Claude Code best practices](https://code.claude.com/docs/en/best-practices) (primary)
- [git-worktree documentation](https://git-scm.com/docs/git-worktree) (primary — the shared-`.git`/private-working-tree+index model)
- [Anthropic — Memory / CLAUDE.md](https://docs.anthropic.com/en/docs/claude-code/memory) (primary — hierarchical loading, keep-it-short guidance)
- Practitioner aggregations (read via search snippets): DEV Community "Running multiple Claude Code sessions in parallel with git worktree" (datadeer/yooi), MindStudio "Claude Code git worktree support", Augment Code / heeki.substack "spec-driven development with Claude Code", alexop.dev / The Prompt Shelf "Claude Code slash commands."

---

## 2. Findings (4 — all fresh vs. the three prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Run multiple Claude Code instances in parallel, each in its own git worktree** so they don't stomp each other's files. A worktree gives each instance a private working tree + index over one shared `.git`; reconcile through merge/PR. The named failure mode is two writers in one checkout silently clobbering each other. | **Genuine gap.** The sub-agent rule [`delegate-reads-fan-out-keep-branch-writes-in-main.md`](../../../plugins/ravenclaude-core/best-practices/delegate-reads-fan-out-keep-branch-writes-in-main.md) **explicitly excludes** this case (edge-case line: "this rule governs the sub-agent relationship, **not peer-process parallelism**"). The repo ships the *tooling* (`new-worktree`/`cleanup-worktrees` skills + the Sleipnir convention) but **no consumer-facing rule** naming the posture. The sub-agent rule literally hands this off. |
| **H2** | **Keep `CLAUDE.md` lean + hierarchical** — Anthropic's own guidance is ~200 lines; use nested per-directory files loaded on demand; import selectively (every `@import` costs context); make every line a project-specific decision, not generic boilerplate. | **Covered.** The approved 2026-06-09 rule [`prefer-a-deterministic-gate-over-a-prose-rule.md`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md) already canonizes "keep `CLAUDE.md` lean enough that every line earns its place; periodically prune" (line 32) **and** "use hierarchical / nested `CLAUDE.md` files instead of growing one root file" (line 33), with the "over-long file gets half-ignored" rationale (line 14). The only net-new sliver is the `@import` mechanism + the 200-line number — thin, platform-101. |
| **H3** | **Spec-driven development: write the plan/spec first, then a test-first verify loop** (run/test/review after each change, self-review the spec in rounds). | **Covered.** Plan-mode-TDD was covered in the 2026-06-09 scan; the correctness half is the shipped `dod-gate.sh` Stop gate + [`definition-of-done-gate-makes-done-mean-done.md`](../../../plugins/ravenclaude-core/best-practices/definition-of-done-gate-makes-done-mean-done.md). The plan-first half is the plugin's plan-mode default (root `CLAUDE.md` "Plan-mode default"). Duplicate. |
| **H4** | **Treat `.claude/commands/` + skills as version-controlled code** — commit them to the repo, review them, prune them like any other asset; one command per workflow, imperative verbs, explicit output format. | **Mostly covered, thin net-new.** The "config as code, reviewed in a PR" theme is already stated for `settings.json` in [`permissions-are-deny-ask-allow-not-an-on-off-switch.md`](../../../plugins/ravenclaude-core/best-practices/permissions-are-deny-ask-allow-not-an-on-off-switch.md), and pruning/one-rule-per-file is the deterministic-gate rule's discipline. A standalone "commands-as-code" rule risks restating the Anthropic skills-authoring docs. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to the three prior scans: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no _action_ on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (If Matt wants the live tribunal applied retroactively, `decision-review` over this doc's decisions is the surface.)

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (in core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** this is the rare case where an existing rule _names its own gap_ — `delegate-reads-fan-out-keep-branch-writes-in-main.md`'s edge case explicitly defers "peer-process parallelism" to a future rule, and the worktree _skills_ exist as tooling with no rule stating the posture. **In-scope:** multi-agent / branch management is RavenClaude's core domain, and the repo's own `new-worktree`/`cleanup-worktrees`/Sleipnir tooling is the least-generic-possible worked example. **Load-bearing:** two parallel writers on one working tree silently lose work — a high-cost, hard-to-spot failure the worktree boundary deterministically prevents. **Low-blast:** additive markdown. | Kept tight and cross-linked to the sub-agent rule (declares itself its peer-process complement), `checkpoints-are-the-recovery-layer` (commits are the durable unit), and the two worktree skills. Explicitly carves out the single-instance and sub-agent cases so it doesn't bleed into the sibling rule's lane. |
| **H2** | ⏸️ Defer (covered) | Fails #1. The approved 2026-06-09 rule already canonizes lean + hierarchical `CLAUDE.md` (lines 32–33) with the half-ignored rationale (line 14). The only delta is the `@import` mechanism + 200-line number — too thin to justify a new rule and a candidate to restate the Anthropic memory docs. | If a consumer-authoring companion to `/init-agent-ready` is ever built, fold the `@import`-budget + 200-line heuristic into the _existing_ deterministic-gate rule as a sub-section rather than a standalone rule. |
| **H3** | ❌ Deny (duplicate) | Fails #1. Plan-first is the plugin's plan-mode default; the verify-loop is the shipped `dod-gate.sh` + `definition-of-done-gate-makes-done-mean-done.md`; plan-mode-TDD was already covered 2026-06-09. Canonizing it again would duplicate three existing surfaces. | None — the lesson is genuinely already lived end-to-end (prose default + deterministic gate). |
| **H4** | ⏸️ Defer | Borderline #1. The "config-as-code, reviewed-in-a-PR" theme is stated for `settings.json` (permissions rule) and "prune like code" is the deterministic-gate rule; a standalone commands-as-code rule is thin net-new and risks restating the Anthropic skills-authoring docs (generic-platform-101, which the core set excludes). | If a concrete "an un-reviewed `.claude/commands/` change cost X" case appears, add a short commands-as-code paragraph to the permissions rule's "treat settings.json like code" section rather than a new file. |

**Net:** 1 approved, 1 denied, 2 deferred. One solid, well-grounded addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 ("don't restate things the lint / CI / hook already enforces / a rule already covers") and the three prior scans' discipline (each landed exactly one tight rule). The H2 near-miss is itself evidence the discipline works: the 2026-06-09 scan already absorbed the leanness lesson, so this scan correctly declined to ship it twice.

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "Run parallel Claude Code instances in separate git worktrees — never aim two writers at one working tree." Sections: Why (the two parallelism kinds + the working-tree/index race) / How (one worktree per writer, the `git worktree add`/`remove` lifecycle, reconcile via merge-PR) / Edge cases (single instance, sub-agents → sibling rule, full clones, web/remote container) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/isolate-parallel-claude-instances-in-git-worktrees.md` | Follows the one-rule-per-file format of the existing 18 rules. |
| 2 | Index update: 18 → 19 rules; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.157.0 → **0.158.0**, mirrored. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` | CI fails on version drift between the two. |
| 4 | CHANGELOG top entry for 0.158.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-06-13-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. Markdown-only diff, but run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Claude Code best practices](https://code.claude.com/docs/en/best-practices)
- [git-worktree documentation](https://git-scm.com/docs/git-worktree) (the shared-`.git` / private-working-tree+index isolation model H1 rests on)
- [Anthropic — Memory / CLAUDE.md](https://docs.anthropic.com/en/docs/claude-code/memory) (H2 — hierarchical on-demand loading, keep-it-short)
- Practitioner aggregations (read via search snippets): DEV Community "Running multiple Claude Code sessions in parallel with git worktree", MindStudio "Claude Code git worktree support", Augment Code / heeki.substack "spec-driven development with Claude Code", alexop.dev / The Prompt Shelf "Claude Code slash commands"
- Prior runs: [`docs/research/2026-06-09-claude-subreddit-scan/README.md`](../2026-06-09-claude-subreddit-scan/README.md) · [`docs/research/2026-06-10-claude-subreddit-scan/README.md`](../2026-06-10-claude-subreddit-scan/README.md) · [`docs/research/2026-06-11-claude-subreddit-scan/README.md`](../2026-06-11-claude-subreddit-scan/README.md)
