# Claude subreddit scan — research, panel decision & build plan (2026-06-21)

**Author:** `claude` (automated scan, scheduled routine)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 fresh findings surfaced (none overlapping the 2026-06-09 / -10 / -11 scans) → **1 approved**, 1 denied, 2 deferred. The approved item ships as a one-paragraph, docs-verified enhancement to `AGENTS.md`'s agent-description token-budget section — no plugin behavior changes.

> This is the **fourth** run of this recurring scan. Prior runs and what they approved:
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — deterministic-gate rule (core v0.139.0).
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` are the recovery layer (core v0.149.0).
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions are a three-tier `deny`/`ask`/`allow` posture (core v0.155.0).
>
> Today's findings are deliberately disjoint from all three. Already-covered community lessons explicitly **not** re-proposed: deterministic-hooks-vs-advisory, model-tiering, subagent-isolation, plan-mode-TDD, `/clear` & `/compact` hygiene, checkpoints/rewind, the lethal trifecta, subagent-description triage, and the permission three-tier model.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively — anything that should change a convention, best-practice, or knowledge file in this marketplace.

**Route note (honest — re-verified this session, consistent with the prior three runs):** `reddit.com` is **blocked at the source for Anthropic's web crawler**, not merely by this environment's network policy. Re-probed this session:

| Route | Result (2026-06-21) |
| --- | --- |
| `WebFetch www.reddit.com/r/ClaudeAI/top` | "Claude Code is unable to fetch from www.reddit.com" |
| `WebFetch www.reddit.com/r/ClaudeCode/top/.json` | same block |
| `WebSearch allowed_domains:[reddit.com]` | **400 — "domains not accessible to our user agent"** (the definitive signal: Reddit blocks Anthropic's crawler — see the linked support article) |
| `redlib` / `redlib` privacy mirrors (2 instances) | HTTP 403 |
| `WebFetch html.duckduckgo.com` / `www.bing.com` / `www.google.com/search` | 403 / blocked by network policy |
| **Unrestricted `WebSearch`** | ✅ works — surfaces Reddit-discussion aggregations via snippets + practitioner/official write-ups |
| **`WebFetch` of GitHub raw + `code.claude.com/docs`** | ✅ works — used to cross-check every claim against primary sources |

Per the repo's Capability-Grounding / accuracy discipline, that is a verified property of **the Reddit↔Anthropic-crawler route**, not a failure to try (≥6 routes probed). **Findings below are drawn from Reddit-discussion aggregations + practitioner write-ups, cross-checked against primary Anthropic docs — not from direct subreddit reads.** Flagged so a future session doesn't over-trust the provenance.

**Queries run (working route):**

- `Claude Code best practices reddit ClaudeAI June 2026`
- `Claude Code subagents skills hooks tips reddit discussion`
- `"Claude Code" workflow agents reddit 2026 plugin marketplace`
- `Claude Code CLAUDE.md context window agents skills tips`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Discover and install plugins](https://code.claude.com/docs/en/discover-plugins) (primary — the `/plugin` Context-cost UI, Will-install inventory, `/reload-plugins --force` cache semantics, LSP/code-intelligence plugins, community-marketplace SHA pinning)
- [`shanraisshan/claude-code-best-practice`](https://github.com/shanraisshan/claude-code-best-practice) — a GitHub distillation that explicitly aggregates r/ClaudeAI + r/ClaudeCode discussion (community context heuristics, hook patterns, vertical-slice advice)
- [`shinpr/claude-code-workflows`](https://github.com/shinpr/claude-code-workflows) · [claudemarketplaces.com](https://claudemarketplaces.com/) (ecosystem framing)

---

## 2. Findings (4 — all fresh vs. the 2026-06-09/-10/-11 scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **The `/plugin` Discover tab now quantifies install cost _before_ you commit.** v2.1.143+ shows a per-plugin **Context cost** estimate (tokens added to every turn); v2.1.145+ shows a **Will install** inventory of the plugin's commands/agents/skills/hooks/MCP+LSP servers. For a ~100-plugin / 400+-agent marketplace whose central consumer pitfall is the ~15K agent-description budget, this turns "enable only what you need" from a guess into a measured decision. | **Not stated anywhere.** `grep -ri "context cost\|will install"` returns only an `ai-rag` agent + the `context-budget-planner` skill (which is about _session_ context sections, not the `/plugin` install UI). `AGENTS.md`'s token-budget section gives the _advice_ ("enable only what you need") but predates and never names the native UI signal that now operationalizes it. **Genuine, tightly-scoped gap.** |
| H2 | **MCP tool-search defers tool schemas; `/reload-plugins --force` and cache invalidation matter** — a plugin that provides non-deferred MCP servers invalidates the prompt cache and re-reads the whole conversation on the next request. | **Covered.** `CLAUDE.md` already has the deep "MCP tools are deferred + lazy-loaded" treatment (the permanent ToolSearch trap), and `docs/token-budget-playbook.md` + the prompt-caching discipline are documented. Net-new nugget (the `--force` cache-invalidation warning) is thin and Claude-Code-mechanical, not a marketplace convention. |
| H3 | **Community context heuristics** — "dumb zone around 40% context," "context rot at 300–400K tokens," "keep usage below 30%," "rewind rather than correct (double-Esc)." | **Covered / unverifiable.** The rewind half shipped as 2026-06-10 **G1**; the numeric thresholds are **community lore with no primary-source backing** — the repo's accuracy discipline discourages encoding unverified numbers as durable fact. `knowledge/concepts/context-window.md` already teaches the compaction model qualitatively. |
| H4 | **LSP / code-intelligence plugins give Claude automatic post-edit diagnostics** (type errors, missing imports) without running a compiler, plus precise navigation — a real 2026 native capability. | **Out of marketplace-meta scope.** Useful, but it's an _engineering-plugin_ enrichment (where it'd inform agents that write code), not a convention for working _on_ the marketplace. Broad surface, no single obvious home, and not a gap in the meta-repo's own rules. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to the three prior scans: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no _action_ on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (If Matt wants the live tribunal applied retroactively, the `decision-review` skill over this doc's decisions is the surface.)

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, hook, or boundary doc.
2. **In-scope** — relevant to working _on_ this marketplace (or domain-neutral + constitution-grounded for a core rule); no generic coding advice.
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; **no** consumer breakage on `/plugin marketplace update`.
5. **Verifiable** — backed by a primary source checked this session, not unverified community lore.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all five. The token-budget section is one of the few places this repo's _own_ scale (~100 plugins) is a documented consumer pitfall, and it gives advice ("enable only what you need") without naming the native instrument that now makes that advice measurable. Verified directly against the official discover-plugins doc this session (v2.1.143 / v2.1.145 gating cited inline). Lands as **one paragraph in the section that already owns the topic** — maximally additive, minimally invasive. | Kept to one paragraph with the doc citation inline so it ages gracefully; placed in `AGENTS.md` (the meta-repo boundary file) rather than a core best-practice, because the concern is marketplace-consumer budgeting, not agent operating discipline. |
| **H2** | ❌ Deny | Fails #1. `CLAUDE.md`'s MCP-deferral section + the prompt-caching discipline already own this; the `--force` nugget is a thin Claude-Code mechanic, not a convention. House-rule #4 (don't restate what's covered). | If a "plugin authoring & cache cost" guide is ever written, fold the `--force` invalidation note there. |
| **H3** | ⏸️ Defer | Fails #5 (numeric thresholds are unsourced community lore) and partially #1 (rewind shipped 2026-06-10). | Revisit only if Anthropic publishes primary numbers, or a concrete context-rot failure is observed with a measurable cost. |
| **H4** | ⏸️ Defer | Fails #2 for the _meta-repo_ — it's an engineering-plugin enrichment, not a marketplace convention. | Candidate for a future engineering-plugin scan (e.g. `backend-engineering` / `frontend-engineering` knowledge: "LSP plugins give Claude automatic post-edit diagnostics — prefer them over grep for type-accuracy"). Not shipped here. |

**Net:** 1 approved, 1 denied, 2 deferred. One solid, primary-source-verified addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 and all three prior scans' discipline.

---

## 4. Build plan (approved: H1)

**Deliverable:** one verified paragraph appended to the existing token-budget lever #2 in `AGENTS.md`, plus this research/panel doc.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | Append the native `/plugin` **Context cost** (v2.1.143+) + **Will install** (v2.1.145+) signal to token-budget lever #2 ("Enable only what you need"), with the discover-plugins doc citation inline. | `AGENTS.md` | None — `AGENTS.md` is already allow-listed. `CLAUDE.md` imports it via `@AGENTS.md`, so the note reaches the Claude-Code path automatically; no `CLAUDE.md` edit needed. |
| 2 | This research + panel doc. | `docs/research/2026-06-21-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Why no plugin version bump:** the change touches the repo-root boundary file (`AGENTS.md`), not any `plugins/<plugin>/` content, so no `plugin.json` / `marketplace.json` semver bump is required (and no version-drift CI risk). This is also why the deliverable is _not_ a new core best-practice: the lesson is "budget what you enable as a marketplace consumer," which `AGENTS.md`'s token-budget section already owns — a core best-practice (agent operating discipline) would be the wrong home and a near-duplicate of existing guidance.

**Layout/gate notes:** `AGENTS.md` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. Markdown-only diff, but run `prettier --write .` before push (CI checks the whole tree; markdown is excluded from prettier but the YAML/JSON in the tree must stay clean). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown to a boundary doc; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Discover and install plugins](https://code.claude.com/docs/en/discover-plugins) (primary; Context-cost UI v2.1.143+, Will-install inventory v2.1.145+, `/reload-plugins --force`, LSP plugins, community-marketplace SHA pinning — fetched & verified 2026-06-21)
- [`shanraisshan/claude-code-best-practice`](https://github.com/shanraisshan/claude-code-best-practice) (community distillation of r/ClaudeAI + r/ClaudeCode discussion)
- [`shinpr/claude-code-workflows`](https://github.com/shinpr/claude-code-workflows) · [claudemarketplaces.com](https://claudemarketplaces.com/)
- [Anthropic support — does Anthropic crawl the web / how site owners block the crawler](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) (the Reddit-block evidence)
- Prior runs: [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) · [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) · [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md)
