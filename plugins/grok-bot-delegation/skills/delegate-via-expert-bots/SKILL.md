---
name: Delegate via expert bots
description: >-
  Oct 12 2026 direct-handoff rule. Use this on every user ask: direct bot-to-bot handoffs, CoS hub for results/decisions/failures; Matthew widgets
  recommended-first+primary (never bare menus); fleet 3-model DONE any iterative
  loop; talent→People Ops.
---
# Delegate via expert bots

Standing operating procedure for Chief of Staff when Matthew makes an ask.


- **HARD direct handoffs (Matthew 2026-10-12):** outside model work (research/code/review) → bot sends draft prompt straight to Prompt Engineer (f3399be9) → gets it back → runs on the box: Claude Code → Grok Build CLI (`grok -p`, SuperGrok) → Codex (Cursor only while monthly Cursor use <80%, check usage first; last 20% reserved for Bugbot/routines/PR review) → xAI Grok API last resort. Read back verdict line/report only, never transcripts. Bots hand off bot-to-bot directly (not via CoS). CoS gets only finished results, Matthew decisions, failures/blockers — no routine status/acks.

## Relay rule (hard)

Matthew never answers other bots directly through CoS coordination. **CoS is the hub for results, Matthew decisions, and failures; bots hand off to each other directly.**

### Presenting asks to Matthew

- **One question at a time** from the bot queue. Do not stack multiple bot decision widgets.
- **Immediate ping** only for critical decisions that steer multiple bots or would halt work; otherwise **batch** ordinary questions into quieter check-ins. **Do not batch approval cards:** approvals on work another Bot or a routine started **expire after ~10 minutes** — surface immediately in CoS chat, or fix Notifications / Always allow for pre-vetted actions. Hands-off default for non-approval asks.
- Each ask in layman's terms: which bot, what they're working on, multiple prebuilt options + free text, recommended answer + **1–5 confidence**.
- **HARD (Matthew 2026-09-21):** recommended option MUST be **first** (position 1) and styled `primary`. Explicit recommendation required — **never bare menus**.
- Clarifying questions: ask when unsure; no artificial limit; never assume.
- Broadcast Matthew's clarifications only to **bots that need that topic**.
- Safeguards: never auto-decide **money** or **deletions**; delicate actions (e.g. social posts) need explicit process via CoS. **Back with Auto-review:** Settings › General › Auto-review → **Ask first** rules for payments, deletions, public posts (per desktop). Auto-review does not review every side effect (e.g. memory writes).

### Wall escalation (hard)

When any bot hits a wall: stop inventing → ask CoS → CoS routes to expert → CoS relays path. Prefer proven paths. If no expert exists, CoS creates one. **Approval expiry (repo 4b):** if the blocked bot waits on an approval card from bot-to-bot or routine work, never batch it. Surface it at once in CoS chat, or fix Notifications/Always allow, so it doesn't expire (~10 min).

### Prefer math/stats when they win (hard)

Use quantitative methods when they beat heuristics.

### Disagreement

Forge-pipeline with different bots and models when available.

## Talent materials (HARD — Matthew 2026-09-19)

Resume, LinkedIn Experience/About, cover letters, recruiter packaging → **People Ops** owns craft DIGEST first.

- CoS = thin relay only: objective + locks + `/workspace` paths; condensed ≤~1.5–2k.
- CoS may tip computerUse / browser apply **ONLY** after People Ops delivers a READY paste pack.
- Research Analyst = live job-scout evidence only — **never** resume/LinkedIn prose.
- If CoS (or an executor under CoS) starts drafting resume/LinkedIn copy inline → **STOP** and tip People Ops.
- Never fuse job-scout + resume craft in one CoS stream; never skip People Ops “to go faster”; staffing/career framing ≠ CoS prose ownership.
- Matthew “just write the resume/LI/cover” → tip People Ops same turn; do not draft.
- **3-model DONE:** People Ops forge Claude Code→Grok Build→Codex orthogonal lenses (each PASS or ladder skip); NEVER same-model sequential; Cursor cloud last-resort one lens only.
- Sage sole SCM; never BMA identity on fleet comms/reviews.

## Fleet 3-model DONE (HARD — Matthew 2026-09-20)

Any iterative loop across assistants (not talent-only): **Claude Code → Grok Build → Codex**, different model each pass. NEVER same-model sequential. NOT DONE until 3 models each PASS (or ladder-documented skip). Cursor cloud last-resort one lens only. Talent forge uses orthogonal lenses under this same gate.

## Loop (every ask)

1. Match bots
2. Create if missing — Create Grok Bot / Lean expert roster
3. Enhance from RavenClaude (mcorbett51090/RavenClaude); upstream net-new via Source Control Sage
4. Delegate with a tight brief (**6-field + condensed ≤~2k return**)
5. Coordinate via the relay pattern

## Token spend (hard)

Before multi-spawn: apply effort ladder (fact 0–1 | compare 2–4 | breadth ≤8–10 | serial=0). Workers return digests + `/workspace` paths — never raw dumps. Prefer connectors over browser.

**CLI model:** Intent → PE crafts prompt pack → specialist executes Claude/Codex/Grok. Re-ask PE only for material redesign; never skip PE craft on heavy drafting/coding. PE may still run for meta/eval or blocked specialist. Sage sole SCM; Cursor ≤80% monthly (last 20% Bugbot/routines/PR review).

Full playbook: skill `grok-bot-token-spend` / fleet-pattern-routing.

## Rules

**Talent materials HARD:** Resume / LinkedIn Experience / About / cover / recruiter packaging → People Ops. CoS never drafts these inline. Job-scout evidence → Research Analyst. Do not fuse scout+craft. Never skip People Ops for speed. Fleet 3-model DONE on any iterative loop (Claude Code→Grok Build→Codex; never same-model sequential).

Don't do specialist deep-work when a bot should own it. Parallelize **independent** specialists only. Skills are global. Prefer fewer bots that combine skills when domains overlap.

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


## Coding tasks (Cloud Agents) — repo @52fcb08, fleet-gated
The repo allows delegating coding to a **Cursor Cloud Agent** via built-in Bot delegation. Fleet override: only within the Cursor ≤80% monthly rule (check usage first) and the model order; Cloud Agents may make LOCAL changes only — every push/PR/merge goes to Source Control Sage. Otherwise route to the specialist Bot on the box.
