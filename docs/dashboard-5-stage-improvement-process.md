# Dashboard 5-stage improvement process

**Started:** 2026-05-31 · **Owner:** Matt + `ravenclaude-core` dashboard authors
**Goal:** give the dashboard a **named, repeatable self-improvement loop** so each lap is auditable, grounded, and ships behind the same gates — instead of an ad-hoc "improve the dashboard" pass.

> This doc formalizes the loop the dashboard already followed implicitly through **round 1** (#158, `ravenclaude-core` v0.80.0). It does not change any dashboard code; it names the stages, points each one at the artifact/skill/gate that already implements it, and defines the cadence and entry/exit criteria for every future round.

---

## Why name it

The repo already runs a generic self-improvement loop for repo quality — `gap-analysis → build-plan → expert-review → execute → re-score` ([`repo-quality-loop.md:3`](./repo-quality-loop.md)). The dashboard's round 1 followed the **same shape** but across a different artifact trail (UX audit → gap analysis → build plan → ship → re-score). Naming the five stages does three things:

1. **Makes each lap legible** — anyone can see which stage a round is in and what the exit criterion is.
2. **Stops premise-drift** — Stage 2 (adversarial gap analysis) is a *required* gate, not an optional nicety; it is what caught the v1 build-plan premises that were "**factually wrong**" ([`dashboard-ux-build-plan.md:5`](./dashboard-ux-build-plan.md)).
3. **Routes the loop through the existing safety envelope** — re-score + the post-PR decision-review retrospective ([`post-pr-decision-review.md`](./post-pr-decision-review.md)) close every lap, so improvements never silently widen the security surface.

---

## The five stages

| # | Stage | Question it answers | Primary artifact (round 1) | Skill / engine | Exit criterion |
|---|---|---|---|---|---|
| 1 | **Inventory & Audit** | *What is the dashboard, honestly, right now?* | [`ux-handoff-repo-inventory.md`](./ux-handoff-repo-inventory.md) + [`ux-dashboard-analysis.md`](./ux-dashboard-analysis.md) + [`nine-realms-dashboard-assessment.md`](./nine-realms-dashboard-assessment.md) | manual audit / `Explore` | A current-state map with every tab, command surface, and server-parity fact captured **from code** (`file:line`), not memory. |
| 2 | **Adversarial Gap Analysis** | *Which premises are wrong, and what did the audit miss?* | [`dashboard-ux-gap-analysis.md`](./dashboard-ux-gap-analysis.md) | `code-review` / cold-review panel | A verdict — *sound* / *sound-with-fixes* / *unsound* — with every factually-wrong premise corrected and tagged. |
| 3 | **Tactical Build Plan** | *How do we ship it, in what order, behind which gates?* | [`dashboard-ux-build-plan.md`](./dashboard-ux-build-plan.md) | `two-panel-plan-review` | A phased PR plan with **security delta front-loaded to zero**, a per-change **gate-impact** table, and per-PR semver bumps. |
| 4 | **Execute (one round = one PR)** | *Does the change work on every host without breaking a gate?* | the round's PR (round 1 = **#158**, v0.80.0) | `verify` + `code-review` + `security-review` | All gates green — freshness (Gate 13), parity (Gate 32), round-trip (Gate 35), prettier, full `audit-gates.sh`; `node --check` clean; core semver bumped. |
| 5 | **Re-score & Retrospective** | *Did it actually improve, and what did we learn?* | re-score block + PR decision-review comment | two-expert re-score + `decision-review` ([`thing-decide.py`](../plugins/ravenclaude-core/scripts/thing-decide.py)) | A re-scored rubric delta **and** a post-PR decision-review retrospective; surviving gaps feed Stage 1 of the next lap. |

### Stage detail

**Stage 1 — Inventory & Audit ("what is").**
Map the dashboard exactly as it ships: tabs, command cards (Class A served-only `/__run` vs. Class B in-Claude slash commands), the served-vs-static banner, and the two-server parity boundary. Every load-bearing claim is cited to code, because a from-memory audit is how the v1 premises went wrong. Output is the *what/why*, never the *how*.

**Stage 2 — Adversarial Gap Analysis ("the check").**
A fresh reviewer cold-reads the audit **and** any draft plan and hunts for premises that are factually wrong. Round 1's gap analysis corrected four — e.g. inline Mermaid is **not** a `render-concepts.py` reuse, and `/__run` is **intentionally excluded** from the bundled/consumer server so Class-A buttons are dead for consumers ([`dashboard-ux-build-plan.md:13-15`](./dashboard-ux-build-plan.md)). Exit verdict gates entry to Stage 3.

**Stage 3 — Tactical Build Plan ("how").**
Turn the corrected audit into a phased, shippable plan. The discipline: **security delta = 0 in the first PR**, defer anything that widens `/__run`'s allow-list or adds infra to a *separate, separately-reviewed* PR, and write a **gate-impact line for every change** (especially the Gate-35 largest-`<script>` hazard). The current plan is three PRs — PR-1 (shipped), PR-2 (`/__run` widening + argv-integrity gate), PR-3 (inline decision-tree SVGs).

**Stage 4 — Execute ("ship one round").**
One round is one PR with one `ravenclaude-core` minor bump (per AGENTS.md "bump on every user-visible change"). Regenerate `dashboard.html`, keep all new tab JS **inside the existing app `<script>`** so Gate 35's longest-script extraction stays valid, run `verify` for runtime behavior, `code-review` + `security-review` for the diff, drive CI green, merge-when-green. Round 1 shipped the Overview tab, clickable command cards with mandatory tooltips, best-practice text preview-on-click, and P1 consolidation — **zero security delta**.

**Stage 5 — Re-score & Retrospective ("close the loop").**
Two independent expert agents re-score the post-merge tree against the rubric below; the synthesized delta says whether the round paid off. Then run the **post-PR decision-review** over the PR's decisions — classify tribunal-eligible vs. needs-human, route the eligible ones through [`thing-decide.py`](../plugins/ravenclaude-core/scripts/thing-decide.py), and log the verdict as a PR comment ([`post-pr-decision-review.md`](./post-pr-decision-review.md)). Surviving gaps become the Stage 1 inventory for the next lap.

---

## Scoring rubric (dashboard-scoped, /100)

Reuses the repo-quality weighting ([`repo-quality-loop.md:5`](./repo-quality-loop.md)) narrowed to the surface a dashboard round can move:

| # | Dimension | Weight |
|---|---|---|
| 1 | First-run clarity — does the Overview tell a newcomer what this is? | 20 |
| 2 | Command honesty — every card states *exactly* what runs; no fake execution | 20 |
| 3 | Graceful degradation — correct served/static + consumer-vs-root behavior on every host | 15 |
| 4 | Accessibility — non-hover tooltips, `aria-*`, keyboard reachable | 15 |
| 5 | Security posture — `/__run` allow-list unchanged or separately reviewed | 15 |
| 6 | Gate integrity — freshness / parity / round-trip stay green, no Gate-35 breakage | 15 |

Two independent expert agents score each round; the synthesized score is their average, reconciling divergences.

---

## Cadence — the loop

```
Stage 1 Inventory ─► Stage 2 Gap analysis ─► Stage 3 Build plan
   ▲                                                   │
   │                                                   ▼
Stage 5 Re-score & retrospective ◄──────── Stage 4 Execute (1 PR / round)
```

- **One lap = one round = one PR.** Stages 1–3 may be amortized across laps when the build plan already covers the next PR (e.g. PR-2/PR-3 are pre-planned), but **Stage 5 runs every lap** — re-score is never skipped.
- **High-blast / irreversible changes never auto-resolve.** Any round that touches `/__run`, force-push, deletes, or prod actions defers to Matt regardless of the decision-review mode ([`CLAUDE.md`](../CLAUDE.md) § Decision review).
- **A round is only "done" when re-scored**, not when merged — a green PR that didn't move the rubric is a signal, not a success.

---

## Where the loop stands now

| Round | Stage reached | Status |
|---|---|---|
| **Round 1** — tab a11y + clarity + copy-fallback (#158, v0.80.0) | Stage 4 ✅ shipped | Stage 5 re-score pending |
| **Round 2** — PR-2: `/__run` allow-list widening + argv-integrity gate | Stage 3 planned ([`dashboard-ux-build-plan.md:30`](./dashboard-ux-build-plan.md)) | not started — security-reviewed in isolation |
| **Round 3** — PR-3: inline decision-tree SVGs in Guidance | Stage 3 planned ([`dashboard-ux-build-plan.md:34`](./dashboard-ux-build-plan.md)) | not started — net-new infra, sized on its own |

**Next action:** run **Stage 5** over round 1 (two-expert re-score + post-PR decision-review retrospective on #158), then open round 2 against the PR-2 plan.

---

## Relationship to existing docs

- [`repo-quality-loop.md`](./repo-quality-loop.md) — the **repo-wide** parent loop this specializes for the dashboard surface.
- [`dashboard-ux-build-plan.md`](./dashboard-ux-build-plan.md) — the live Stage 3 artifact (the three-PR "how").
- [`dashboard-ux-gap-analysis.md`](./dashboard-ux-gap-analysis.md) — the live Stage 2 artifact (the adversarial check).
- [`post-pr-decision-review.md`](./post-pr-decision-review.md) — the Stage 5 retrospective mechanism.
