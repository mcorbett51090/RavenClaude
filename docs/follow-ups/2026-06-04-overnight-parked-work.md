# Parked work — 2026-06-04 overnight session

A calendar marker for items the 2026-06-04 overnight session **deliberately did
not ship**, with the trigger condition that should unpark each one and the
person/agent best positioned to act on it.

Written for the *next* session, which won't have this one's context. The point
is the **trigger**: "do this when X is true." If the trigger fires before the
re-check date, act earlier. If the date passes and the trigger hasn't fired,
either re-park with a new trigger or close as "no longer applicable."

---

## Why these were parked (not "missed")

This session shipped #261/#262/#263 (the Mímir Session-state tab trio) and
#264 (the Gate 32 body-diff that closes Mímir RM6). The items below were
**out of scope for the overnight, but in scope for the originating plans** —
each was deferred because (a) it needed user input I couldn't get with the user
asleep, (b) it required real-world verification (web access / live browser /
multi-day soak) I couldn't do remotely, or (c) it was architecturally
significant enough to warrant the "ask first" path per the PR-activity
webhook contract.

The rule: **a parked item is a known follow-up with a trigger, not a
forgotten task.** This file gives each one its trigger.

---

## 1. Adaptive-run-classifier Phase 6 — flag-flip + release

**Plan:** [`docs/plans/2026-06-03-adaptive-run-classifier/plan.md`](../plans/2026-06-03-adaptive-run-classifier/plan.md) §Phase 6.

**What it does when shipped:** flips `templates/run-config.json` `enabled: true`, bumps `plugins/ravenclaude-core/.claude-plugin/plugin.json` + `marketplace.json` minor (lockstep), adds the CLAUDE.md milestone, writes the 5-line dashboard pointer card, regenerates artifacts. The classifier is currently fully built (Phases 1-5 merged across #244, #246-#247, #250-#251, #253) but ships **disabled by default** — so the workflow is byte-identical to the pre-port baseline (Gate 51 holds).

**Why parked:** the plan requires re-running the **verify-at-use** check on two claims the day before merge: claim #8 (Anthropic Batch API ~50% off pricing) and claim #9 (substrate tier SKUs per `plugins/ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md` dated 2026-05-31). The overnight session had no live web access to `anthropic.com/pricing`, so a faithful verify-at-use was impossible.

**Trigger to unpark:** any session with web access to anthropic.com.

**Action:** re-read the two cited sources, confirm the numbers haven't drifted, then ship Phase 6 per the plan. If either has drifted, **defer the flip** and ship a docs-only PR noting the drift instead (per the plan's settling step).

**Re-check by:** 2026-06-18 (two weeks). If unverified by then, leave the classifier disabled in `main` and document why in a follow-up commit.

---

## 2. Agent-dispatch-evaluator Phases 2-6 — workflow integration onward

**Plan:** [`docs/plans/2026-06-03-agent-dispatch-evaluator/plan.md`](../plans/2026-06-03-agent-dispatch-evaluator/plan.md) §Phases 2-6.

**What's shipped already:** Phase 1 (SKILL.md + tier table — #249) and the Phase 2 wrapper *reference snippet* (`plugins/ravenclaude-core/skills/agent-dispatch-evaluator/reference/evaluate-dispatch.js` — #254). The reference is not yet integrated into `.claude/workflows/deep-research.js`.

**What's parked:**

| Phase | Scope | Re-check by |
|---|---|---|
| **P2 integration** | Copy the wrapper into `deep-research.js`, wrap each `agent()` call site, add Gate 52 (byte-identical-when-disabled regression floor). | When the user explicitly OKs the two-classifier composition design. |
| **P3 SubagentStart hook** | New `plugins/ravenclaude-core/hooks/agent-dispatch-evaluator.sh` + dev-mirror. **CRITICAL caveat:** Panel B R1 calls out that `SubagentStart` fires post-spawn; deny may be a late-stage cancel. Phase 3 acceptance MUST verify deny actually prevents dispatch. Until that's verified live, the hook should ship as **audit-only**. | When a session can run a live Claude Code dispatch with the hook armed and measure whether deny is pre-commit. |
| **P4 tribunal-seat shadow** | `scripts/thing-decide.py` calls `evaluateDispatch(caller_context='tribunal_seat', ...)` and logs `evaluator_shadow` to the seat Sága record. **Never mutates** `cfg["panel"][seat]["model"]`. | Same as P2 — needs user OK on the two-classifier interaction. |
| **P5 sampler + dashboard tab** | `scripts/eval-dispatch-quality.py` + `/__evaluator` endpoint + dashboard `#/evaluator` tab + auto-revert circuit. | After P2 + P4 land. |
| **P6 binding flip** | Flip `dispatch-config.json` `enabled: true` + `mode: 'binding'`. | Blocked on a **2-week dev-repo shadow soak** — earliest 2026-06-18 *if* P5 shipped immediately, which it didn't. Realistic earliest: 2026-07-02. |

**Why parked (Phases 2-5):** the wrapper's interaction with the **adaptive-run-classifier**'s per-phase tier (which the same `deep-research.js` reads) is non-trivial. The plan's precedence rules (downgrade binding; upgrade-above-`run_config.tiers[phase]` advisory only) require composing the two classifiers without one's verdict silently overriding the other's. The overnight contract was "ask first if architecturally significant" — this qualifies.

**Action when unparked:** start with P3 + P4 (parallelizable, smaller blast radius). Then P2 once the user explicitly approves the composition shape. Then P5 once P2 has accumulated ≥1 week of shadow-mode logs to seed the eval fixture.

**Re-check by:** 2026-06-18. If the dispatch-evaluator stays unshipped for >4 weeks total, re-read the plan's "Why we're doing this" section and decide whether the cost case still holds.

---

## 3. Unified-dashboard-shell Phase 3 — visual-regression DoD

**Plan:** [`docs/plans/2026-06-04-unified-dashboard-shell/plan.md`](../plans/2026-06-04-unified-dashboard-shell/plan.md) §Phase 3.

**What's shipped:** Phases 1 (router), 2 (smart-fallback + mode banner), 4 (Gate 51 — the structural router gate), 5 (version bump + invariant comments + milestone) — all landed in #259 as `v0.114.0`. The milestone explicitly notes Phase 3 is "manual verify — not gate-enforced at this depth."

**What's parked:** the 4-surface manual diff checklist (dashboard standalone vs in-shell; repo-guide standalone vs in-shell; shell standalone unchanged; mobile viewport per RM4). The overnight session has no live browser, so it can't be done remotely.

**Trigger to unpark:** the next session where the user is at a desktop with the dashboards open.

**Action:** open each surface, eyeball-compare against the standalone, fix any visual drift in `index.html` or the iframe sizing rules. Document the result in a 5-line `docs/best-practices/dashboard-visual-regression.md` so the next person doesn't have to re-derive the comparison set.

**Re-check by:** **no urgency.** If no one notices a visual problem in a month of use, the manual VR was de facto fine.

---

## 4. Mímir SKILL parked open question — `claude --status --json`

**Plan:** [`docs/plans/2026-06-03-mimir-session-tab/plan.md`](../plans/2026-06-03-mimir-session-tab/plan.md) §"Open questions parked."

**What's parked:** the Mímir reader currently surfaces session state from on-disk JSONL + settings + stats-cache files. If Anthropic ships a `claude --status --json` (or equivalent machine-readable CLI subcommand), the reader should re-route to that as the **primary source** (the on-disk read becomes the fallback for the in-process-only fields).

**Trigger to unpark:** any of —
- Anthropic ships the CLI subcommand (watch the [Claude Code changelog](https://github.com/anthropics/claude-code/releases)).
- A new Claude Code release surfaces a `claude --version` / `claude --help` flag that exposes JSON.
- The user / a consumer asks for richer live data than the JSONL surface provides.

**Action when unparked:** re-probe the available CLI surface in a fresh session, update `_read_mimir` to prefer the JSON output if present, falling back to the current on-disk shape. Update Gate 49's fixtures to exercise both paths.

**Re-check by:** 2026-06-18 (two weeks — Researcher cadence). If nothing surfaced, re-park with a 2026-07-04 re-check.

---

## How to mark an item "done"

When an item ships, delete its entry from this file in the same PR (don't just strike-through — the file should always show only the current parked set). If a re-check finds the item still valid but with a new trigger, update the entry rather than letting the date silently slide.

If a new follow-up gets parked, add it here in the next overnight session's wrap-up commit. The file is the **stack** of "things known to be missing"; an item is on the stack until it ships or the trigger fires.
