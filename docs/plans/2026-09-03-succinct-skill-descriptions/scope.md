# G0 — Scope: Succinct skill descriptions, marketplace-wide

> **P0 amendments applied 2026-09-08** (plan.md §5.5(a)/(b)) — both marked inline below.

## Scoped intent
Build a **procedure** (script + workflow, not a one-off manual edit) that rewrites `SKILL.md`
`description:` frontmatter across the whole RavenClaude marketplace to cut per-turn token spend
from the skill listing injected into every session's system context, **without degrading routing
quality** (a skill still gets picked when relevant, still skipped when irrelevant). Ships as a
standing gate so new/edited skills stay within a description budget going forward, not just a
today-only cleanup.

## Baseline

**⛔ P0 amendment (a) — the original motivation below cited the wrong budget. Corrected.**

- **Original G0 measurement (2026-09-03):** 946 `SKILL.md` files, 310,359 chars, mean 328, median
  283, max 1018 (`report-regeneration:powerbi-ingest`).
- **P0 re-measurement (2026-09-08, `scripts/skill-description-baseline.py`, the plan's canonical
  instrument — see `description-baseline.json` in this directory):** **956** skills (organic growth
  since G0 — new skills landed on `main` in the interim, expected drift, not an error), **310,284**
  chars, **66,511 tokens** via `tiktoken cl100k_base` — an **[interpretation]** proxy, not Claude's
  real tokenizer (unavailable in this environment; no `anthropic` SDK, no API key, no `claude` CLI
  token-count subcommand — all checked). The char figure (310,284) is within 0.02% of the original
  310,359 despite +10 skills, consistent with a mix of additions and small organic edits elsewhere;
  no reconciliation action needed beyond naming the method (plan.md P0 build item 4 — the ~0.9%
  spread across the plan's three cited numbers, 310,359/307,672/308,229, is inside error bars from
  different measurement methods on slightly different tree states, not a defect).
- **⛔ CORRECTED (was: "Confirms [[agent-description-budget]] memory: ~15K token budget scales with
  enabled-plugin count — this is why 131 plugins are disabled today.").** That memory concerns a
  **different pool**: the ~15K-token budget in `AGENTS.md` § "The agent-description token budget"
  governs `name`+`description` frontmatter under `plugins/*/agents/*.md` — **agent** definitions,
  injected by a separate Claude Code mechanism (subagent routing) from the **skill** listing this
  plan targets. `scripts/check-frontmatter.py`'s `_AGENT_DESCRIPTION_MAX_CHARS = 300` cap already
  enforces the agent pool and applies **only** to files under `plugins/*/agents/` — confirmed by
  direct read this session; no equivalent length cap exists for `SKILL.md` descriptions today. The
  two pools are related in spirit (both are "always-loaded routing text") but are not the same
  budget, are not enforced by the same gate, and citing one to justify action on the other was the
  error. See `red-team.md` RT-1 / `critic-brief.md` C10 for the full finding.
- **⛔ The #1 open risk (RT-1, plan.md §2) is UNMITIGATED and governs how any of the above numbers
  should be read.** Rendering into a session's context appears usage-gated (~13% of installed
  skills render a description at all; 22/22 skills with any invocation history render, 0
  exceptions). **None of the totals above are a per-turn injected cost** — they are corpus-on-disk
  totals. No phase may denominate savings in corpus chars/tokens without stating the rendering
  model and posture. See plan.md §2 in full before treating any number here as a savings figure.

## In scope
1. A **length/style linter** (script) flagging descriptions over a budget (e.g. p75 or a hard char
   cap) and structural bloat (redundant phrases, restated skill name, filler).
2. A **rewrite procedure** — likely LLM-assisted batch rewrite with a human/automated quality gate,
   not manual per-file editing across 946 files.
3. A **routing eval harness** — a golden set of (prompt → expected skill) pairs, run against
   descriptions before and after a rewrite, gating on no regression (or an accepted, disclosed
   regression list).
4. A **standing CI/audit-gate** enforcing the description budget + eval-pass on any PR touching a
   `SKILL.md` description.
5. Rollout plan: batch by plugin, land incrementally (not one 946-file PR).

## Out of scope
- Rewriting skill **bodies** (the instructions after frontmatter) — only the `description:` field
  that lives in the always-loaded listing.
- Changing which plugins are enabled/disabled (that's the existing [[agent-description-budget]]
  lever, separate decision — see the corrected Baseline note above on why that memory does not
  govern this effort's own budget math).
- Non-RavenClaude-marketplace skills (user/project-local skills outside `plugins/`).
- **⛔ P0 amendment (b) — cross-host eval coverage (plan.md §6, accepted-risk waiver, `tiebreaks.md`
  m10).** Cross-host routing evaluation (GitHub Copilot CLI and OpenAI Codex CLI, which receive the
  same projected skill descriptions via `scripts/generate-copilot-plugin.py` and `.agents/skills`)
  is **out of scope for this effort: no eval instrument exists for those routers, and cross-host
  routing regressions are an accepted, unmeasured risk of this change.**

## Owner
matt@ravenpower.net (repo owner), this FORGE run executes the design; landed plan requires owner
merge per repo norms.

## Success signal
A rewrite procedure exists, is proven on a representative sample (not all 946/956) to cut
description token weight materially — **denominated per plan.md §2's rendering model, never as a
raw corpus total** — with zero routing-eval regressions on the golden set, and a standing gate
blocks future over-budget/unrewritten descriptions from merging.

## Risk-based depth floor check
No auth/secrets/PII/destructive-operation/prod-surface signal — this is a text-content rewrite in a
git-tracked repo, fully reversible via git revert, no runtime/production blast radius. Floor stays
at requested depth: **standard** (user-selected: whole-marketplace scope + eval harness + standing
gate = non-trivial multi-file change with new tooling, per the depth ladder).
