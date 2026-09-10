# Outstanding-work close-out queue

**Date:** 2026-09-10  
**Audience:** Chief of Staff → Matthew  
**Scope:** RavenClaude marketplace checkout `fe8c9929` (`main` = `origin/main`) plus live GitHub state this session.  
**Method:** repo glob/grep + file reads + GitHub issues/PRs/branches/checks. Granola was unauthorized this session; `.ravenclaude/runs/` is gitignored and empty in this clone (only ledger + posture files are committed).

This is a **triage queue**, not a build plan. Each row is one close action. Do not re-scan the tree — act from this list, then mark the row done in a follow-up commit.

---

## How to use this

| Priority | Meaning | Default action |
|---|---|---|
| **P0** | Broken, blocking, half-merged, or a required check that flakes | Close this week |
| **P1** | Parked with an expired trigger, owner-gated leftover, or live PR/issue | Close or re-park with a new trigger |
| **P2** | Design-only, on-demand backlog, or already-shipped docs that still say "not started" | Archive or ignore until asked |

**Already closed — do not reopen:** analog-repos increment (`docs/follow-ups/2026-08-14-analog-repos-leftovers.md` + `docs/decisions/2026-08-14-analog-repos-gap-fill.md`); succinct-skill-descriptions P8 STOP (`docs/plans/2026-09-03-succinct-skill-descriptions/p8-decision.md`); session-context handoff shipped enabled-off (#931/#934); Víðarr / Norns / Ragnarök / streaming-media / self-storage / HOA / funeral / chaos plugins already exist on disk.

---

## P0 — must-close

| # | Item | Status (this session) | Close action |
|---|---|---|---|
| P0.1 | [PR #1153](https://github.com/mcorbett51090/RavenClaude/pull/1153) `fix/repo-review-recovery-batch-20260910` — "39 CONFIRMED findings across 9 plugins" | Open, created 2026-09-10 18:33 UTC. Required layout/schema/secret/zizmor checks **green**. Marketplace gate-audit + macOS-portability still **in progress** at snapshot. | Watch checks; squash-merge when green. Do not admin-bypass. |
| P0.2 | [PR #1152](https://github.com/mcorbett51090/RavenClaude/pull/1152) `cursor/ci-preflight-coordinator-78fc` — `ci-preflight.py` | Open, created 2026-09-10 16:29 UTC. **Only 3 Cursor agent checks visible** (Bugbot / Approval / Security) — **no** `validate-marketplace` / `validate-layout` / `validate-schemas` runs on the head at snapshot. | Confirm a GitHub Actions run exists for head `2903b0b`. If none, re-trigger per `docs/remote-ci-autotrigger-runbook.md`. Then merge or close. |
| P0.3 | [Issue #1075](https://github.com/mcorbett51090/RavenClaude/issues/1075) — Gate 242 self-test flakes on concurrent PRs | Open since 2026-09-02. Required check. Content-independent; worse on rerun. Trains admin-bypass (happened on #1071). **No closing PR.** | Snapshot merge-base / committed `index.html` at job start (or retry-with-backoff). Do not leave as "just rerun." |
| P0.4 | `docs/research/2026-08-14-chat-ceiling-probes.md` | **UNFILLED.** CL-3 / CL-19b tables blank. Chat stays `supported: false`. Prior probe files were gitignored and lost. | Matthew fills the two tables in VS Code Copilot Chat Agent mode, or formally decline and keep Chat as operator-lane. Until then, **never** claim Chat is protected. |

---

## P1 — should-close soon

### Live GitHub issues (scheduled / parked)

| # | Item | Status | Close action |
|---|---|---|---|
| P1.1 | [Issue #1124](https://github.com/mcorbett51090/RavenClaude/issues/1124) Researcher Weekly Deep Research Sweep | Open 2026-09-07, bot-filed, **zero comments**. Covers Tier-A news plugins only. | Spawn `deep-researcher` **or** close as "null week / declined." Do not leave open as a fake backlog. |
| P1.2 | [Issue #1125](https://github.com/mcorbett51090/RavenClaude/issues/1125) Monthly Skill-Gap Audit | Open 2026-09-07, bot-filed, **zero comments**. Prompt still says "all 7 plugins" (catalog is ~184). | Run a scoped audit **or** decline per the issue's own decline conditions, then close. Update the template's plugin count if kept. |
| P1.3 | [Issue #283](https://github.com/mcorbett51090/RavenClaude/issues/283) "Tailored Power BI Copilot prep for a real model" | Open since 2026-06-04; last update 2026-08-17. | Close as stale consumer work **or** move to the Contoso/Power BI repo. Not a marketplace close. |

### Owner-gated / blocked-on-human

| # | Item | Status | Close action |
|---|---|---|---|
| P1.4 | `docs/plans/2026-09-02-llm-stats-agent-routing-citations/plan.md` | Ready to execute. **Blocked on** a free bearer token from https://llm-stats.com/developer. | Sign up → apply the exact diff in the plan. Do **not** land placeholder numbers (Gate 255). Or archive as "won't subscribe." |
| P1.5 | `docs/plans/2026-09-03-succinct-skill-descriptions/` | P1 closed inconclusive; P8 STOP. Native `claude plugin eval` still account-gated. Linter + ratchet shipped (#1100 / #1130). | **Archive the plan directory.** Leave `p8-decision.md` as the close record. Do not rebuild P4–P10. |
| P1.6 | `docs/follow-ups/2026-06-04-overnight-parked-work.md` | Re-check dates were **2026-06-18 / 2026-07-16**. Still parked: adaptive-run-classifier `enabled: false` (eval never wired into `rc-deep-research.js`); dispatch-evaluator P5/P6 + live SubagentStart DENY verify; Mímir `claude --status --json` watch. | Either unpark with a **2026-09** trigger or delete expired rows. File currently lies about being current. |
| P1.7 | `docs/follow-ups/2026-06-04-comfort-posture-agent-category.md` | `subagent_dispatch` category still missing; workaround was a hand-added `Agent` allow that `/set-posture` can clobber. | Add the 13th posture category **or** close as "workaround is enough." |
| P1.8 | `docs/follow-ups/2026-08-14-analog-repos-leftovers.md` Q1 / L4 MCP quarantine | Still parked. Trigger: owner asks, or unsanitized `mcp__.*` output reaches the model. **Do not** extend the WebFetch sanitizer matcher. | Leave parked **or** forge as its own plan. Hygiene worktrees listed are on Matt's laptop (`~/.grok/worktrees/...`), not this clone. |
| P1.9 | Analog leftovers Q2 — closeness scorecard | Pickup sheet still says parked. **Skill already exists:** `plugins/ravenclaude-core/skills/analog-closeness-scorecard/`. | Mark Q2 shipped in the leftovers file. Do not re-build. |

### Shipped-but-inert / half-finished product

| # | Item | Status | Close action |
|---|---|---|---|
| P1.10 | `prompt-optimizer` | Skill + hook + Gate 264 **exist**. Default `prompt_optimizer.enabled: false`. SKILL.md still says "nothing wired yet — Phase 6" while `hooks.json` already registers the gate. Plan still reads as to-do. | Reconcile SKILL.md vs hook. Decide: leave default-off (honest) **or** opt-in on this repo. Archive `docs/plans/2026-09-03-prompt-optimizer/` once the doc matches disk. |
| P1.11 | Caveman auto-routing | Shadow-only shipped (`caveman_routing` absent ⇒ no-op). Applier exists; **nothing calls it** until a future P7. Gate 265 is **dev-only**, not required CI. | Leave shadow **or** explicitly decline P7 in a one-line decision. Do not "finish" by flipping live. |
| P1.12 | `docs/plans/2026-09-03-harden-rc-deep-research/plan.md` | Authoritative G6 plan (2026-09-03). CHANGELOG has **no** matching "hardening" entry through 0.321.0. `verify_policy` exists in the JS; the adaptive-loop / trust-tier / saturation work is **not** claimed shipped. | Implement from the plan **or** archive as "forged, not built." Next free gate was 263 at plan time — re-read `audit-gates.sh` before claiming a number. |
| P1.13 | Session-handoff verify leftovers | `/handoff` shipped enabled-off. `docs/plans/2026-08-14-session-handoff-verify/plan.md` still open for Copilot Chat / CLI same-host spawn. Chat probes (P0.4) block any "Chat is protected" claim. | Ship host-paired spawn **or** archive the verify plan as "Grok path is enough." |
| P1.14 | Copilot Chat worktree lanes leftover | FOREIGN-TREE + lane stamp shipped. Phase 6 adapter remains a documented no-op (`docs/plans/2026-08-14-chat-write-deny.md`). | Keep as operator-lane. Close only after P0.4 probes. |

### Plugin backlog (roadmap vs disk)

July 2026 roadmap (`docs/plugin-roadmap-2026-07.md`) is **mostly stale**. Built since then: `self-storage-operations`, `hoa-community-association-management`, `funeral-home-operations`, `chaos-engineering-resilience`, `streaming-media-engineering` (as `streaming-media-engineering`, not the roadmap name).

| # | Still missing on disk | Close action |
|---|---|---|
| P1.15 | `urgent-care-operations` | Build from SMB vertical-ops template **or** strike from the roadmap. |
| P1.16 | `franchise-multi-unit-operations` | Same. |
| P1.17 | `moving-relocation-operations` | Same. |
| P1.18 | `docs/plugin-roadmap-2026-07.md` + older candidate lists | Rewrite the "remaining eight" table to match disk, or add a 2026-09 "built / dropped" header so the next Researcher does not rebuild shipped plugins. |

### Packaging / honesty gaps (not draft plugins)

No plugin was found in a `draft` / `build-in-progress` manifest state. The live honesty gaps:

| # | Item | Status | Close action |
|---|---|---|---|
| P1.19 | `plugins/ravenclaude-core/skills/repo-review/SKILL.md` honest-status | Intentional. `--converge` unmeasured at scale; `Workflow` tool never executed; `judge` near-dup tier not built. Plugin description still says "build-in-progress." | Keep the honest-status. After #1153 merges, refresh the section so it does not under-claim the recovery batch. |
| P1.20 | `docs/live-dispatch-checklist.md` | Status **open** since 2026-05-21. Still says SOP is "runtime untested" against a v0.1.0 cache. Core is now **0.321.2**. | Run the SOP smoke test once **or** rewrite the checklist as historical. The 0.4.0 claim is three months stale. |

---

## P2 — optional / on-demand

### Stale "TEE-UP / not started" docs for features that shipped

These four still say **TEE-UP (not started)** in the opening line. Knowledge files + commands on disk contradict that. **Archive or stamp SHIPPED** — they pollute every unfinished-doc grep.

| Path | Reality on disk |
|---|---|
| `docs/vidarr-posture-log-tee-up.md` | Víðarr tab + reader shipped (core knowledge `concepts/vidarr.md`) |
| `docs/norns-lineage-view-tee-up.md` | Norns tab + live endpoint shipped |
| `docs/ragnarok-reset-plugin-cache-tee-up.md` | `/reset-plugin-cache` (`/ragnarok`) shipped |
| `docs/route-permission-awareness-tee-up.md` | Still analysis-only — keep **or** fold into a host-support note |

### Design drafts with no ship commitment

Close only if Matthew wants a clean `docs/` tree. None are blocking.

| Path | One-line status | Suggested close |
|---|---|---|
| `docs/whitelist-blacklist-design.md` | `status: design-draft` (2026-05-23). Internally contradictory on whitelist vs bare-tool deny. Spike in §13-Q4 never recorded. | Archive, or run the 5-minute spike and then decide. |
| `docs/dev-lockout-and-pipeline-dashboard-plan-2026-05-29.md` | PLAN / awaiting approval. Runaway default is already **1200** (v0.59.0). | Likely obsolete — confirm lockout still happens, else archive. |
| `docs/dashboard-buildout-plan.md` / `docs/dashboard-ux-build-plan.md` / `docs/analytics-dashboard-plan.md` | Design space, not a commitment. Redesign blocker **CLEARED** 2026-07-16. | Leave as product backlog. |
| `docs/tribunal-review-feature-design.md` / `docs/tribunal-tool-review-design.md` | DESIGN. Tribunal (`the Thing`) already ships opt-in. | Stamp "shipped as command-review" or archive. |
| `docs/huginn-muninn-recon-design.md` | DESIGN, not a commitment. | Leave until asked. |
| `docs/design-token-delta.md` | `[blocked]` — this agent had no `DesignSync`. | Unblock only from a session that holds DesignSync. |
| `docs/best-practices-section-scope-2026-05-29.md` | SCOPE ONLY — post-import flow activation. | Forge if Power Platform pain returns. |
| `docs/accuracy-and-learning-gap-closure-plan.md` | Plan; honesty stack already large. | Leave. |
| `docs/ci-gates-efficiency-and-currency-plan.md` | Plan (2026-06-03). | Revisit only if CI minutes hurt. |
| `.claude/agent-memory/ravenclaude-core-architect/project_orchestrator_relay_scope.md` | Architect note: `orchestrator_scope: team\|all` never built. | Build only if relay-all is still wanted; needs a security re-check. |

### Out-of-marketplace / consumer work

| Path | Status | Close action |
|---|---|---|
| `docs/plans/2026-08-11-on-course-app-brief.md` + `docs/plans/2026-08-11-phase1-pace-spec.md` | Golf player-pace product. Not a plugin. | Move to the app repo or leave as research. Do not treat as RavenClaude unfinished work. |
| `docs/research/2026-06-25-contoso-fipa-dispatch/TODO.md` | OPEN consumer FIPA dispatch bug (Contoso DEV). | Track in the Contoso repo. Marketplace cannot close it. |
| `docs/research/2026-06-10-data-access-routes/linkedin-partner-application-draft.md` | DRAFT for Matthew to submit. | Fill placeholders and submit, or delete. |
| `docs/staging/incoming/2026-06-09-surface-credential-location-in-environment-context.md` | Empty `Status:` | Accept into environment-discovery **or** drop. |

### Historical candidate / proposal docs

These are **research deliverables that already shipped a plugin beside them**. They still contain the phrase "not yet implemented" and will keep showing up in greps:

- `docs/proposals/2026-06-12` … `2026-07-15-ten-new-plugin-candidates.md`
- `docs/new-plugin-candidates-2026-07-14.md`
- `docs/plugin-candidates-2026-06-10.md`
- `docs/research/2026-06-08-twenty-candidate-plugins/`
- `docs/plugin-roadmap-2026-06-17.md`

**Close action:** add a one-line "historical — plugins listed as built have shipped" banner, or move to `docs/plans/archive/`. No code work.

---

## Claude / agent session leftovers

| Surface | Finding | Close action |
|---|---|---|
| `.ravenclaude/runs/` | Gitignored. This clone has **no** committed run leftovers (only `comfort-posture.yaml`, `ledger/2026-09.jsonl`, `plugins/sweep-tiers.yaml`, `design-project.json`). Ledger has a single `ledger_init` event (2026-09-09). | None in-repo. Local machines may still hold analog / forge run dirs — that is expected. |
| `.claude/` | Project config + workflow mirrors + architect memory. **No** incomplete `/wrap` or `/handoff` notes. | None. |
| Remote branches | Only `main` + the two open PR heads. **No abandoned remote branches.** | After PRs merge, let GitHub auto-delete heads. |
| Analog worktrees (pickup sheet) | Paths under `/Users/matthewcorbett/.grok/worktrees/...` — **not this environment**. | Clean on the Grok `update` machine with `cleanup-worktrees`. Never `git branch -D`. |

---

## CI snapshot (2026-09-10 ~18:35 UTC)

**Observation** (what the API returned), not a cause:

- **#1153** — 21 check runs. Completed successes include layout, schemas, TruffleHog, zizmor, prettier, ruff, actionlint, semantic title, hook fail-closed (ubuntu + macos). Still in progress at snapshot: marketplace gate-audit, macOS toolchain suite, Cursor Bugbot / Approval / Security.
- **#1152** — 3 check runs, all Cursor agents, all in progress. **No GitHub Actions required-check runs attached.** Treat as "CI may not have auto-fired" until `gh run list --branch cursor/ci-preflight-coordinator-78fc` shows a `pull_request` run for head `2903b0b`.
- **#1075** — still the only documented flake. No new flake issues since 2026-09-02.

**Inference (named):** #1152's missing Actions runs are consistent with the remote-session "push updated the PR head without creating a run" failure mode in `CLAUDE.md` / `docs/remote-ci-autotrigger-runbook.md`. Discriminating probe: `gh run list --branch cursor/ci-preflight-coordinator-78fc --json headSha,status` vs `gh pr view 1152 --json headRefOid`. Not run here after the first snapshot.

---

## Recommended Matthew sequence (15 minutes of decisions)

1. **Merge #1153** when required checks are green.  
2. **Unstick #1152** — confirm Actions ran; if not, `workflow_dispatch`. Then merge or close.  
3. **Assign or close #1075** — this is the only item that will keep burning admin-bypass.  
4. **Fill or formally decline** the Chat ceiling probes (`docs/research/2026-08-14-chat-ceiling-probes.md`).  
5. **Close or decline** the two 2026-09-07 Researcher issues (#1124, #1125).  
6. **One yes/no:** archive expired June parked-work, or re-date the adaptive-classifier / dispatch-evaluator rows.  
7. **One yes/no:** build the three missing verticals (urgent-care / franchise / moving) or strike them from the July roadmap.

Everything else is on-demand and should not interrupt those seven.

---

## What this inventory did not cover

- Local gitignored run dirs on other machines (`.ravenclaude/runs/`, analog worktrees).  
- Consumer repos (Contoso FIPA, golf app).  
- Live `claude plugin eval` enrollment (account-level; already decided STOP).  
- A full per-plugin skill-gap audit (that is issue #1125's job).  
- Whether #1153/#1152 eventually went green after this snapshot.
