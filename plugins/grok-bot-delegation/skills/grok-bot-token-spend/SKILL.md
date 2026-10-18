---
name: Grok Bot token spend
description: >-
  Oct 12 2026 direct-handoff rule. Use when optimizing Grok Bot fleet token spend or stamping personas. Fleet
  3-model DONE; Matthew widgets recommended-first+primary; NEVER same-model
  sequential / bare menus. Advisory: skill ≠ meter.
---
# Grok Bot token spend

Use after research or when fleet usage is tight / on-demand pressure is up. Companion to fleet-pattern-routing (box workflow `fleet-pattern-routing`). Apply on every roster/persona/skill stamp.


- **HARD direct handoffs (Matthew 2026-10-12):** outside model work (research/code/review) → bot sends draft prompt straight to Prompt Engineer (f3399be9) → gets it back → runs on the box: Claude Code → Grok Build CLI (`grok -p`, SuperGrok) → Codex (Cursor only while monthly Cursor use <80%, check usage first; last 20% reserved for Bugbot/routines/PR review) → xAI Grok API last resort. Read back verdict line/report only, never transcripts. Bots hand off bot-to-bot directly (not via CoS). CoS gets only finished results, Matthew decisions, failures/blockers — no routine status/acks.

## Hard rules

1. **Condensed returns:** specialists → CoS ≤~1.5–2k digest + file paths; no raw dumps.
2. **Effort ladder before spawn:** fact 0–1 | compare 2–4 | breadth ≤8–10 | serial = 0 parallel.
3. **CLI model (HARD):** Intent → **Prompt Engineer crafts the prompt pack** (CLI Claude Code→Grok Build→Cursor(PR only)→Codex order, max parallel / real concurrency levers, success criteria, DIGEST schema) → **domain specialist runs** Claude Code/Grok Build themselves on the box. Re-ask PE only for **material** prompt redesign. **Never skip PE craft** on heavy drafting/coding. PE may still **run** the CLI for meta/eval work or when the specialist is blocked. Sage sole SCM; Cursor ≤80% monthly (last 20% Bugbot/routines/PR review).
4. **Surface ladder (coding/agent work):** prefer **Claude Code → Codex → Grok** on the shared box **before** Cursor cloud agents; raise cloud/`xhigh` only when the gap is reasoning/capacity, not default thrift — and only after the PE pack path above.
5. **Claude Max concurrency stamp:** paste PE SSOT `/workspace/ravenpower-website-build/cli-out/prompts/_MAX-PARALLEL.md` — **real** levers (Agent subagents, workflows/`/effort ultracode`, `--worktree`, ultrathink, plan mode). **No `/max-parallel` slash command** — do not invent one. This is inside-session concurrency, **not** roster-wide fan-out (still use effort ladder before spawning other bots).
6. **Routines:** prefer events; skip when noop; never broad “every message” listeners. Min schedule interval ≥5m.
7. **Connectors > browser/vision;** one owner per stage; no duplicate handoffs.
8. **CPCT** = Σ(spend including failures) / successful tasks — not $/token vanity. Mark **`[collectability:unproven]`** until field telemetry is proven collectable.
9. **No Grok Bot model picker** — cut overhead; don’t hunt Settings for a cheaper model.
10. **Box recovery (HARD):** Never recommend [Reset Grok Bot's Computer](grokbot://app/v1/settings?id=reset-computer). Wedged/stale box → [Update Grok Bot's Computer](grokbot://app/v1/settings?id=update-computer) only, then After Update Computer reinstall (box workflow `after-update-computer-reinstall`).
11. **Never Delete agent (HARD):** Never urge sidebar **Delete** (wipes agent + transcript). Matthew-only. Declutter → `hidden_from_sidebar` / hide. Don’t recreate-as-delete without Matthew GO.
12. **App Updates hygiene (HARD):** Prefer [Update Track](grokbot://app/v1/settings?id=update-channel) = **Stable** + [automatic updates](grokbot://app/v1/settings?id=automatic-updates) **on**. Never conflate with Update/Reset Computer.
13. **Billing:** Plan / on-demand / cancel-trial → Grok Bot billing safeguard (box workflow `grok-bot-billing-safeguard`); Matthew widget OK required. Never auto-enable spend.
14. **Never BMA identity (HARD):** Never include `mcorbett@bma.bm` (or BMA Matthew) on communications, PR reviews, CODEOWNERS, Cursor Bugbot/auto-review assignees, or CreateAgent reviewer decks. Prefer `@mcorbett51090` only; flag configs that email BMA.
15. **Talent materials (HARD):** Resume/LinkedIn/cover/recruiter packaging → People Ops craft DIGEST first. CoS thin-relays only; no CoS/executor resume prose; computerUse only after READY paste pack; Research never writes resumes.
16. **Fleet 3-model DONE (HARD, Matthew 2026-09-20):** ANY iterative loop across assistants must use a **different model each pass** — Claude Code → Grok Build → Codex. NEVER same-model sequential. NOT DONE until 3 models each PASS (or ladder-documented skip). Talent forge uses this too (orthogonal lenses). Cursor cloud last-resort one lens only.
17. **Matthew choice widgets (HARD):** Recommended option MUST be first + `primary`; explicit recommendation — never bare menus.

## Persona / skill stamp defaults

- Lean Bot descriptions (ALWAYS/NEVER/NOT-MY-JOB); no essay skill catalogs.
- Enable skills only where needed; point bots at this skill + fleet-pattern-routing when routing/spend matters.
- Fresh thread per distinct task; file-back large outputs.
- Bots that dispatch Claude Max CLI work: require PE pack + concurrency stamp (real levers only); specialist executes unless meta/eval or blocked.
- Recovery: Update-only + after-update-computer-reinstall; never Reset; never urge Delete; App Updates ≠ Computer Update; never BMA on reviews.

## Non-claims (B-E6) — mandatory

- **skill ≠ meter.** This playbook advises; it does **not** meter or close unmetered Grok Bot weekly burn.
- **No invented numeric Bot weekly quotas.**
- **No Bot Compact/cache toggles** as product knobs (not exposed).
- Landing this skill in the fleet library ≠ spend control enforced by the product.

## Do / don’t

Do: lean descriptions; connectors first; canary 1 worker before N-way; PE pack → specialist execute; Update Computer + reinstall for box recovery; Stable + auto app updates; hide_from_sidebar for declutter; billing widget before money moves; personal GH only for reviews.

Don’t: invent `/max-parallel`; skip PE craft on heavy work; fan out for “more reasoning”; copy Max burn onto Bot weekly; claim this skill “fixed burn”; **recommend Reset Computer**; **urge Delete agent**; **conflate app Updates with Update/Reset Computer**; **auto on-demand/plan/cancel-trial**; **include mcorbett@bma.bm / BMA on PR reviews or Bugbot**; **CoS drafting resume/LinkedIn prose** (tip People Ops); **same-model sequential iterative loops** (must Claude Code→Grok Build→Codex); **bare Matthew menus** (recommended must be first + primary).

## RavenClaude placement

Prefer adding/updating under **`grok-bot-delegation`** (version bump only — **not** a new plugin). Distinct from Max `token-budget-playbook`, `claude-app-engineering` context-budget, and `ai-coding-model-guidance`. Sage lands repo PR; CoS applies fleet-side.

Evidence: `/workspace/rc-deep-research-token-spend/REPORT.md`

## SCM carve-out (HARD, Matthew Oct 12)

Claude Code/Grok Build runs a bot launches may edit files and make LOCAL commits in a worktree only. They must never push, open/edit/merge/close PRs, rebase or force-push shared branches, or touch GitHub/Origin — every brief must say so. All mutating git/GitHub/Origin work (push once per PR, PR create/edit, merge, branch delete, mirror sync) is handed DIRECTLY to Source Control Sage, not relayed through CoS. Approval cards for gated steps still run in CoS chat. Sage is the exclusive executor.


## DH guards (HARD, Matthew Oct 12)
HARD direct-handoff guards (Matthew Oct 12): bot-launched Claude/Grok runs NEVER (1) deploy (wrangler deploy, Deploy Commerce, workflow_dispatch, Wallet push), write prod D1/KV or apply migrations: hand to Platform, with Matthew's gate where required; (2) print/log/commit secrets: RavenPower 1Password vault only, never the personal vault or Apple Passwords; secret-setting stays with Auth/Platform; (3) send email/Slack/X/messages: bots draft, Matthew sends via a draft card; (4) trigger/re-run GitHub Actions or shard tests; Cursor models only while monthly Cursor use is below 80% (check usage before any Cursor build; last 20% reserved for Bugbot, routines, PR reviews), no tests/builds in Grok Bot workers. (5) Grok reviews cover only the diff since the last reviewed commit (about 20 chunks max, 8 in parallel); commits that only merge main or update the branch need no AppSec or Grok re-review; a passing run writes /workspace/state/ready/<repo>-<pr>.json and SendToAgents Sage, which owns push/merge-main/merge order per the Oct 12 2:35 PM work flow. (6) Direct is not quiet: Sage verifies push/merge and Platform verifies deploy end to end; the owner sends CoS a final DONE/FAILED; on failure, fix or re-dispatch at once. (7) Heavy box work ONLY via /workspace/bin/box-run <claude|grok|admin> (memory-based admission, reserve 2.5 GB free, no fixed cap; gate queues; Platform owns gate); nohup/bg; never kill others' runs. (8) Read the last response before archiving Claude sessions, never touch running ones, archive Cursor agents after merge, and log the owner and next steps for leftovers. (9) Never route around Auto-review: gated steps go to CoS so the card shows in CoS chat. (10) Every brief: never BMA (mcorbett@bma.bm); Matthew widgets put the recommended option first, styled primary.

Work flow (Matthew Oct 12, 2:35 PM ET):
1. Source Control Sage owns ALL source control end to end: branches, merge-from-main, conflict resolution (Sage asks the code owner for code decisions, then commits), pushes, PR create/update/ready, and merge order and timing.
2. Code-owner bots own only code. They write the brief and launch the Claude or Grok run, which makes local commits in its worktree only. They launch fixes in the same turn findings arrive, and they never touch remotes or PRs.
3. A passing run writes /workspace/state/ready/<repo>-<pr>.json (worktree, sha, review verdicts) and sends a SendToAgent to Sage. Sage pushes within 30 minutes.
4. Grok review covers the diff only and runs in parallel with AppSec. AppSec reviews only security and logic changes. Sage merges main in just before the merge and merges within 30 minutes of green.
5. Platform deploys only from merged main, behind the prod gate.
6. Matthew's decisions never get a default action.
Watchdog (Routines Ops, every 20 minutes) flags changes idle over 30 minutes and unpushed local commits over 15 minutes.
Prompt Engineer brief template: every returned brief must include guards 1-4, 7, 9 and the SCM carve-out verbatim.

Admin rule (Matthew Oct 12, 3:40 PM ET): system/account admin (plan upgrades, settings, dashboard config) is done by the bot that OWNS the system, in its own browser/desktop, per /workspace/state/SYSTEM-OWNERS.md. Spend or plan changes need Matthew's approval card via CoS, then the owner executes. Never route admin execution through CoS. RavenPower vault only. Owner reports DONE/FAILED to CoS.

HARD box-run (Matthew Oct 12 4:24 PM ET): launch ALL heavy box work ONLY via `/workspace/bin/box-run <claude|grok|admin> <cmd...>` (claude max 2, grok max 2 with diff chunks queued in one process, admin never blocked; memory/load gate queues runs, never fails). Run under nohup or in the background; never kill other bots' runs; log at /workspace/state/box-run/log. Example: nohup /workspace/bin/box-run claude claude -p ... < brief.md > log 2>&1 &

HARD blocker-first+parallel (Oct 13 6:22): check P&D critical path first, take earliest unblocked item; fill free box-run slots (memory-based, reserve 2.5 GB free; Platform owns gate) with independent work, never idle with an unblocked queue; spread reviews across models (Claude/Cursor while Grok 402); Sage merges green unheld PRs ≤30 min, red CI→owner at once; batch Matthew decisions per PR; idle capacity + queued work→report CoS.
