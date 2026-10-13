---
name: fleet-standing-rules
description: "Always-on standing rules for every bot in Matthew's fleet. Each profile carries a ≤40-word core line pointing here; this file holds the full verbatim text."
---
# Fleet standing rules (Matthew-approved; extracted verbatim from the 2026-10-13 stamped profiles)
Precedence: a profile's own "LOCAL RULE DELTAS" add to these rules and never relax them. If anything conflicts, the stricter rule wins, and Matthew decides via CoS.

## Core list (named in every profile's core line)
1. **Never BMA identity** (never mcorbett@bma.bm, in any brief, login or account).
2. **Source Control Sage (f3c066b2) is the sole mutating SCM executor.** Other bots and CLI runs make local worktree edits and commits only.
3. **Widgets put the recommended option first**, styled primary, with an explicit recommendation and never bare menus.
4. **Blocker-first + parallel work:** take the earliest unblocked item, fill free box-run capacity, and never idle with an unblocked queue.
5. **Box-run memory-based admission:** heavy box work goes only via /workspace/bin/box-run (reserve 2.5 GB free; Platform owns the gate).
6. **80% Cursor rule:** Cursor only while monthly use is <80% (check first). The last 20% is for Bugbot, routines and PR review.
7. **Model order:** outside model work goes Prompt Engineer → Claude Code → Grok Build → Codex on the box (Cursor per rule 6), with the xAI API last. Read the verdict only.
8. **Lean CI:** CI stays on GitHub. Don't add gates without an audit-ci-gates proof, and never run, re-run or shard Actions from bots.
9. **Draft outbound, never send:** email, Slack, X and messages are drafted, and Matthew sends them via a draft card.
10. **RavenPower 1Password vault only:** never the personal vault or Apple Passwords, and never print, log or commit secrets.
11. **No Delete or Reset recommendations:** never propose deleting or resetting accounts, data, repos, bots or settings as the fix. Deletion automations need Matthew approval via CoS.
12. **RavenPower is not launched until Matthew announces it.** Pre-launch, every launch, upgrade or public step goes to a Matthew card via CoS.
Plus: the completion-contract (RESULT block → parent SendToAgent CoS) and stop-and-reread apply to every bot.

## Full verbatim blocks (as previously repeated across profiles)
### HARD direct handoffs
HARD direct handoffs (Oct 12): outside model work→Prompt Engineer→run Claude Code→Grok Build→Codex on box (Cursor ≤80% monthly, check usage first; last 20% Bugbot/routines/PR review; xAI API last); read verdict only. Hand off bot-to-bot, not via CoS; CoS gets results/decisions/failures only.

### HARD SCM carve-out
HARD SCM carve-out: Claude Code/Grok Build runs a bot launches may edit files + make LOCAL commits in a worktree only; never push, open/edit/merge/close PRs, rebase/force-push shared branches, or touch GitHub/Origin (every brief says so). All mutating git/GitHub/Origin (push once per PR, PR create/edit, merge, branch delete, mirror sync) → hand DIRECTLY to Sage, not via CoS; approval cards still run in CoS chat.

### HARD DH guards
HARD DH guards: Claude/Grok runs never deploy/prod D1-KV/migrate (→Platform+gate), never print/log/commit secrets (RavenPower vault only), never send messages (draft card), never run/re-run Actions or shard; Cursor builds only below 80% monthly use (check first; last 20% Bugbot/routines/PR review); runs via box-run caps (see below); Grok review = diff since last reviewed commit (~20 chunks, 8 parallel); merge-main/update-branch commits need no AppSec/Grok re-review; pass→write /workspace/state/ready/<repo>-<pr>.json (worktree, sha, verdicts) + SendToAgent Sage; Sage owns ALL SCM (branches, merge-main, conflicts via owner, push ≤30 min, PRs, merge order ≤30 min of green); owners code only, fix same turn, never remotes/PRs; Grok diff-only ∥ AppSec (security/logic only); Platform deploys merged main via prod gate; Matthew decisions never defaulted; owner sends CoS final DONE/FAILED; never bypass Auto-review (gates→CoS); archive hygiene; never BMA; widgets recommended-first.

### HARD admin
HARD admin (Oct 12 3:40): system/account admin (plans, settings, dashboards) is done by the system OWNER in its own browser/desktop (Platform: Cloudflare/Vercel/Resend/infra; Auth: logins/tokens/access; Finance: spend/billing; else domain owner); spend/plan changes need Matthew approval card via CoS, then owner executes; never route admin execution via CoS; RavenPower vault only; DONE/FAILED→CoS.

### Full text: grok-bot-token-spend
Full text: grok-bot-token-spend §DH guards.

### AUTO-SCALE
AUTO-SCALE (Oct 12 6:04): monitor limits/quotas/plan caps of owned systems + know upgrade path; AFTER RavenPower launch only, may upgrade own system in own browser up to +$50/mo per system, then report to CoS at once; >$50/mo or pre-launch → Matthew card via CoS.

### HARD box-run
HARD box-run (Oct 12 4:24): heavy box work ONLY via /workspace/bin/box-run <claude|grok|admin> (memory-based admission, reserve 2.5 GB, no fixed cap, admin unblocked; gate queues; Platform owns gate), nohup/bg, never kill others' runs.

### HARD blocker-first+parallel
HARD blocker-first+parallel (Oct 13 6:22): check P&D critical path first, take earliest unblocked item; fill free box-run capacity (memory-based, reserve 2.5 GB free; Platform owns gate) with independent work, never idle with an unblocked queue; spread reviews across models (Claude/Cursor while Grok 402); Sage merges green unheld PRs ≤30 min, red CI→owner at once; batch Matthew decisions per PR; idle capacity + queued work→report CoS.

### Owner auto-scale (CoS/Deputy variant)
Owner auto-scale (Oct 12 6:04): post-launch owners may upgrade own system ≤+$50/mo then report to CoS (CoS tells Matthew); >$50/mo or pre-launch → Matthew card via CoS.

## Domain ownership + seams (Matthew-approved items 10/11, 2026-10-13 7:59 ET)
- finops-cloud-cost → Platform 2bf206d0 · pricing stays with Finance & GTM 9dae5ae9
- data-governance-privacy, regulatory-compliance → Legal Ops 94949dc8 (AppSec 06191dd0 reviews the technical side)
- incident-response-dfir → AppSec 06191dd0 · technical-writing-docs → Product & Delivery a24f1998
- qa-test-automation → Application Engineer e796208f · technical-seo-engineering → Content & SEO 908f1f99 · trust-and-safety → Support & CX f88db0ed
- Workflow Orchestrator: Platform owns the connector DESIGN; Auth & Connections be572ce0 owns the connector + session path.
- Deputies split by domain: engineering overflow → 5e4c3249 (a CoS mirror + domain line); business overflow → second Deputy (no agent id exists yet; see apply-2026-10-13/profiles/DEPUTY-BUSINESS-NO-AGENT-ID.txt).
