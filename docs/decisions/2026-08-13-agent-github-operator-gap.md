# Decision record — closing the agent-as-primary-GitHub-operator gap (v0.251.0)

**Date:** 2026-08-13 · **Branch:** `forge/claude-github-primary` · **Owner:** Matt · **Method:** `/forge --depth deep` (autonomous-to-merge)

## 0. Status at merge (authoritative)

- **Re-measured gap: the agent-as-operator lens exposed 7 shippable gaps; 6 CLOSED this increment, 1 DEFERRED-with-pointer** (agent-driven issue triage — lower leverage; the frontier research gives a consumer somewhere to look). See the table in §4.
- **Reviews: `security-reviewer` CLEAR (0 P0/P1)** — the anti-self-approval template's RT-1 (injection floor) and RT-2 (soundness) invariants each verified; two hardening findings (P2 write-access approver filter, P3 NaN fail-closed) applied. **`code-reviewer`: mechanics all correct**; three documentation defects (an `EXCLUDED_APPROVERS` casing mismatch, a WARN-wording error, a duplicate question number) fixed. **Zero P0–P3 remaining.**
- **`audit-gates.sh`: 730 pass / 0 fail** (Gate 9b `ruff` skipped for the `ruff`-on-PATH probe only — ruff verified clean via `python3 -m ruff`; it runs in CI). **plugin-detail render: consistent** (no RC_BASELINE drift). prettier `--check` exit 0. Version mirror **0.251.0** (plugin.json + marketplace.json), copilot/codex/dashboard/index projections regenerated in lockstep.

## 1. Context — the lens, not the target

This is the *agent-as-primary-GitHub-operator* complement to v0.246.0 (PR #875), which covered how elite **human teams** run GitHub. The re-scoped question: how should an **AI agent** — the account that opens the PR, drives CI, and (sometimes) arms the merge — operate GitHub safely. Corpus: Anthropic's Claude-as-GitHub-user surface (`claude-code-action`, the GitHub MCP server) anchored, enriched by the autonomous-coding-agent frontier (Copilot coding agent, Cursor, OpenHands, SWE-agent, aider, Devin) — quality-gated, 12 sources qualified (verified via authenticated `gh api` + official docs, 2026-08-12).

## 2. What shipped (by phase)

| Phase | Ships | Closes |
|---|---|---|
| P1 | Conservative reconciliation of the shipped merge-authority divergence (additive cross-ref subordinating the auto-merge teaching to the human-approval rule, inline at the arm-auto-merge step; **no existing rule text changed**) | gap #6 |
| P2–P4 | 3 knowledge files: `claude-in-ci.md`, `github-mcp-tool-surface.md`, `agent-pr-identity.md` | gaps #1, #5, #2 |
| P5 | `github-actions-hardening.md` Rule 7 — agent-triggered least-privilege `permissions:` + the default-`GITHUB_TOKEN` downstream-suppression trap | gaps #4a, #4b |
| P6 | Opt-in agent PR template (`PULL_REQUEST_TEMPLATE-agent.md.template`) via `/init-agent-ready` | gap #2 |
| P7 | Opt-in, security-reviewed structural anti-self-approval workflow (`agent-approval-check.yml.template`) + a branch-protection dry-run WARN + Gate 188 coverage | gap #3 |
| P8 | `check-workflow-hygiene.py.template` advisory Rule 3 (token-suppression heuristic) + `--self-test` + new Gate 191 (with a must-fail mutant) | gap #4b (measured) |
| P9 | `github-gold-standard` scorecard: +3 agent-operability rows, N/A-as-a-group, **proportional banding** (dynamic /18-or-/24 denominator) | measurability |
| P10 | Regen + version mirror 0.251.0; **no RC_BASELINE change** | close-out |

## 3. Decisions & tiebreaks (settled by the FORGE panels + critic + expert tiebreaks + red-team)

| Decision | Verdict | Basis |
|---|---|---|
| **C3 — agent-PR identity: own knowledge file vs folded into git-workflow.md** | **B (own file)** | distinct reader; matches the repo's one-concept-per-file convention; keeps the preference-tier merge rule lean |
| **C4 — anti-self-approval: ship the opt-in workflow template vs prose + a scorecard row only** | **B (ship the mechanism)** | an inert opt-in scaffold is not a live control (unlike prior-C4's `--apply`); the no-padding ethos forbids a scorecard row a consumer has no mechanism to satisfy |
| **C5 — hygiene template: `--self-test` + new gate + must-fail mutant vs a minimal fixture** | **synthesis (lean B)** | the new-rule gate + teeth mutant is mandatory per gate-audit doctrine; the Rules-1/2/5 retrofit rides the same harness (non-blocking) |
| **CE-1 — `RC_BASELINE.templates` bump** | **NO bump** | control: `ls -1 templates/` = 23; new `.template` files nest under `templates/agent-ready-repo/`, below the non-recursive top-level scan |
| **CE-2 — `RC_BASELINE.knowledge` counter** | **does not exist** | control: `grep knowledge check-plugin-detail-render.mjs` → no match; knowledge feeds only the projection regen |
| **CE-3 — merge-authority reconciliation shape (preference-tier — claim 40)** | **conservative clarification only** | additive subordinating cross-ref; **no existing rule text changed**; surfaced here + in the PR for Matt. It clarifies (does not reverse) the maintainer's stated human-approves-the-merge preference: `remote-mcp-pr-landing.md`'s auto-merge teaching is now explicitly a *post-approval mechanic*, subordinate to `git-workflow.md`'s rule. |

## 4. Re-measured gap table

| # | Agent-as-operator gap (from G1) | Status |
|---|---|---|
| 1 | Running Claude safely inside CI (`claude-code-action`/`@claude`) — the trust boundary, config-restore, signing | **CLOSED** — `claude-in-ci.md` |
| 2 | Agent-PR identity/attribution (bot vs named principal, GitHub-App signing, Co-Authored-By, agent PR template) | **CLOSED** — `agent-pr-identity.md` + the opt-in PR template |
| 3 | Structural anti-self-approval + agent-safe merge | **CLOSED** — the security-reviewed opt-in workflow (initiator excluded, write-access reviewers only, base-branch execution) |
| 4a | Least-privilege `permissions:` for an agent-triggered workflow | **CLOSED** — `github-actions-hardening.md` Rule 7 |
| 4b | The default-`GITHUB_TOKEN` downstream-suppression trap | **CLOSED** — Rule 7 teaches it; hygiene Rule 3 heuristically flags it (advisory) |
| 5 | GitHub MCP tool-surface + least-privilege reference | **CLOSED** — `github-mcp-tool-surface.md` |
| 6 | The shipped merge-authority divergence (human-merge rule vs auto-merge teaching) | **CLOSED** — reconciled (clarification, CE-3) |
| 7 | Agent-driven issue triage | **DEFERRED-with-pointer** — lower leverage than PR/merge/CI authority; frontier research names OpenHands/SWE-agent as where to look |

## 5. Deferred (with reasons, not silent gaps)

- **Agent-driven issue triage** (gap #7) — deferred as above.
- **A deterministic "required-checks-actually-ran" verifier** — measured via the scorecard, not built (the tribunal's opt-in `srm.pr-merge-without-checks` remains the sharpest existing content).
- **A GitHub-App / dedicated-bot identity scaffold** — `agent-pr-identity.md` documents the trade-off; no App-manifest template ships (a credential-adjacent surface deserving its own scoped design).
- **SBOM/provenance** — deferred at v0.246.0 (claim 38); **not** re-opened.
- **Cross-host projection of any new guardrail** — N/A: no new hook shipped, and the copilot/codex projections are agents-only, so new knowledge/templates do not project. Disclosed, not built.

## 6. House Rule 3 walkthrough

Simulated `/plugin marketplace update`: nothing fires automatically. The 3 knowledge files are dormant until read; the 2 templates are opt-in (never default-selected) and only scaffold via a user-invoked `/init-agent-ready`; the hygiene Rule 3 is advisory-only (never hard-fails a consumer's CI); the branch-protection WARN is advisory (never gates `--apply`); no new hook, no auto-install.

## 7. Provenance

FORGE gate artifacts (scope, claims-table, plan-A/B, gap-delta, critic-brief, tiebreaks, red-team, red-team-2, plan) live under `.ravenclaude/runs/forge/claude-github-primary/` (gitignored). Best-practices + the 12 verified sources are summarized in that run's `research/agentic-github-gold-standard.md`.
