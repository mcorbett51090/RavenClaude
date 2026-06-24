# Claude subreddit scan — research, panel decision & build plan (2026-06-15)

**Author:** `claude` (automated scan, scheduled routine)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 fresh findings surfaced (none overlapping the 2026-06-09 / -10 / -11 scans) → **1 approved**, 1 deferred-as-covered, 1 deferred-to-domain-plugin, 1 denied. The approved item shipped as one new consumer-facing best-practice in `ravenclaude-core` (v0.158.0).

> This is the **fourth** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions-deny/ask/allow (approved), skills-vs-subagents-vs-MCP, headless-CI cost, thinking-budgets.
>
> Today's findings are deliberately disjoint from all three sets.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest — same operational gap as the 2026-06-11 run, re-confirmed this session):** the sanctioned front door for this scan is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (Reddit's official OAuth2 Data API). It **`_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and both env vars are still unset this session** (verified — `os.environ.get` returned `False` for both). So the *structural* block (Reddit's crawler-UA ban on Anthropic's user agent) remains solved by the script, but the *operational* gap — the two creds have never been provisioned into this environment — persists, exactly as the 06-11 run flagged. **The one-time setup is still pending** (create a "script" app at <https://www.reddit.com/prefs/apps>, export the two creds as session/CI secrets). Until it lands, every run of this routine falls back to web search and the provenance gap stays open.

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session (re-verified) |
| `WebFetch www.reddit.com/....json` | "Claude Code is unable to fetch from www.reddit.com" (crawler-UA block) |
| `WebSearch allowed_domains:[reddit.com]` | **400 — "domains not accessible to our user agent"** |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion snippets + practitioner write-ups |

**Provenance of the findings below:** drawn from Reddit-discussion aggregations + practitioner write-ups via unrestricted web search, **cross-checked against primary Anthropic docs** — not from direct subreddit reads. Documented fallback, not the preferred route. **Next scan: provision the two Reddit creds and run `reddit-scan.py` first.**

**Queries run (fallback route — unrestricted web search):**

- `Claude Code adversarial reviewer subagent finds gaps over-engineering flag only correctness 2026`
- `Claude Code interview me AskUserQuestion write spec SPEC.md fresh session implement workflow`
- `Claude Code fan out claude -p loop allowedTools batch migration parallel files`
- `Claude Code /clear /btw side questions context hygiene between tasks`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) (primary — adversarial review step, explore→plan→code, interview-me spec workflow, fan-out, failure patterns)
- Practitioner write-ups via search snippets (several 403 on direct fetch): adversarial-review skill repos (`dementev-dev/adversarial-review`, `wan-huiyan/agent-review-panel`, `alecnielsen/adversarial-review`), VelvetShark "Stop prompting Claude Code — let it interview you", alexop.dev "Spec-Driven Development with Claude Code", aitooldiscovery "Claude Code Reddit: what developers actually use it for".

---

## 2. Findings (4 — all fresh vs. the prior three scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **F1** | **A gap-finding reviewer always finds gaps — scope it to correctness, or it manufactures work.** A reviewer/panel prompted to find gaps reports some even when the work is sound (that's the task it was given); an obedient implementer then chases every finding into over-engineering (extra abstraction, defensive code, tests for impossible states). Fix: tell the reviewer to flag only correctness/requirement gaps and that passing clean is valid; point it at the criteria; let the implementer triage, not auto-apply. | **Genuine gap — and squarely in this repo's domain.** `grep` over `plugins/ravenclaude-core` for `over-engineer\|flag only\|gap-inflat\|reviewer.*bias` found **no** best-practice covering it. The repo runs review-by-panel *pervasively* (tribunal seats, `decision-review`, `two-panel-plan-review`, `code-review`, `agent-dispatch-evaluator`) yet none documents how to scope a seat so it doesn't inflate findings. The repo *lives* this rule without stating it. |
| **F2** | **Interview-me → `SPEC.md` → fresh session to implement.** For a larger feature, start minimal and have Claude interview you with `AskUserQuestion` (edge cases, tradeoffs) → write a self-contained `SPEC.md` → start a **fresh** session to build against it (clean context, no interview bias). | **Partially covered, borderline-generic.** `skills/spec-reread-ritual` + `knowledge/concepts/task-scope-gate.md` cover the *execution-side* spec discipline; the *authoring handoff* (interview→spec→fresh-session) is net-new but risks restating the Anthropic best-practices doc near-verbatim. |
| **F3** | **Fan out across files with a `claude -p` loop + `--allowedTools`.** For large migrations/analyses, generate a task list, loop `claude -p "migrate $file…"` per file with a scoped `--allowedTools`, refine on the first 2-3, then run at scale. | **Adjacent, not core-shaped.** Core's `delegate-reads-fan-out-keep-branch-writes-in-main.md` covers the *in-session sub-agent* fan-out; this is the *headless multi-process* recipe — a generic Claude-Code scaling technique that fits a `devops-cicd` scenario more than the domain-neutral core. |
| **F4** | **Context hygiene between tasks — `/clear` + `/btw` for throwaway questions.** `/clear` between unrelated tasks; use `/btw` for side-questions whose answer shouldn't enter conversation history. | **Duplicate.** `/clear` hygiene was the 06-09 scan's coverage; `/btw` is a thin UI nicety, not a load-bearing lesson. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to the three prior scans: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no *action* on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably.

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **F1** | ✅ **Approve** | Passes all four. **Additive:** grounded `grep` confirms no existing rule on review-seat scoping / gap-inflation. **In-scope:** review-by-panel *is* RavenClaude's signature — the tribunal, `decision-review`, `two-panel-plan-review`, `code-review`, `agent-dispatch-evaluator` are all "a model asked to find problems"; a rule on how to scope those seats is the least-generic topic possible here. **Load-bearing:** the failure (manufactured findings → over-engineering in unattended runs) is exactly the place this repo leans hardest on panels, with no human to filter. **Low-blast:** additive markdown. | Kept tight: cross-linked to `structured-output-protocol` (the finding-envelope), `focused-task-delegation` (hand the seat the criteria), `command-review-when-to-enable` (the tribunal it scopes), and `three-epistemic-protocols` (Last-Mile ceiling read against this floor). **Explicitly carves out the security floor** so it can't be misread as "lower the bar on safety findings." |
| **F2** | ⏸️ Defer | Borderline #1/#2. Execution-side spec discipline is covered by `spec-reread-ritual`; the net-new authoring handoff risks restating the Anthropic best-practices "let Claude interview you" section near-verbatim — generic-platform-101, which the core set excludes. | If an `/init-agent-ready` companion on "structuring your own Claude Code setup" is ever built, fold the interview→spec→fresh-session handoff there, grounded in RavenClaude's own spec-reread ritual — not as a standalone core rule. |
| **F3** | ⏸️ Defer (to a domain plugin) | Fails #2 for **core** — the headless `claude -p` fan-out only helps consumers running batch migrations, not a domain-neutral foundation. The recipe is real and valuable. | Strong candidate for a `devops-cicd` best-practice or a `claude-app-engineering` scenario (`fan-out-with-claude-p-and-allowedtools.md`) — noted for a future domain-plugin scan, not shipped to core here. |
| **F4** | ❌ Deny | Fails #1 — duplicate. `/clear` hygiene was the 06-09 scan's coverage; `/btw` alone is a thin UI nicety, not a load-bearing lesson. | If a concrete "context-pollution cost X" case appears, fold a one-line `/btw` note into the existing `/clear`-hygiene material rather than a new rule. |

**Net:** 1 approved, 1 denied, 2 deferred. One solid, well-grounded addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 ("don't restate what's already enforced/covered") and the three prior scans' discipline (each landed exactly one tight rule).

---

## 4. Build plan (approved: F1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "Scope a review seat to correctness — a gap-finding reviewer always finds gaps." Sections: Why / How (reviewer-prompt + implementer-triage + criteria-handed-to-seat) / Edge cases (security floor, exploratory asks, thin spec) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/scope-the-reviewer-to-correctness-or-it-manufactures-work.md` | Follows the one-rule-per-file format of the existing 18 rules. |
| 2 | Index update: 18 → 19 rules; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.157.0 → **0.158.0**, mirrored. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` | CI fails on version drift between the two. |
| 4 | CHANGELOG top entry for 0.158.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-06-15-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. Markdown-only diff, but run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) (the adversarial-review-step callout that grounds F1; explore→plan→code; interview-me spec workflow; fan-out; common failure patterns)
- [Anthropic support — does Anthropic crawl the web / how site owners block the crawler](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) (the Reddit-block evidence)
- Practitioner aggregations + adversarial-review skill repos (read via search snippets): `dementev-dev/adversarial-review`, `wan-huiyan/agent-review-panel`, `alecnielsen/adversarial-review`; VelvetShark "let it interview you"; alexop.dev spec-driven-development; aitooldiscovery "Claude Code Reddit"
- Prior runs: [`2026-06-09`](../2026-06-09-claude-subreddit-scan/README.md) · [`2026-06-10`](../2026-06-10-claude-subreddit-scan/README.md) · [`2026-06-11`](../2026-06-11-claude-subreddit-scan/README.md)
