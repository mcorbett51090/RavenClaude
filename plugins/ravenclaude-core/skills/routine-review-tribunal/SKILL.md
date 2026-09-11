---
name: routine-review-tribunal
description: "Gate an unattended scheduled routine's produced diff/PR through a two-panel, cross-model tribunal (mirrors /forge-pipeline's divergent-panel + tiebreak shape, applied after the fact) before it is finalized: approved as-is, sent back for a bounded revision round, or escalated to a human. Use at the end of any routine whose run contract ends in opening or updating a PR (plugin-discovery, research-cadence)."
allowed-tools: Bash, Read, Task
---

# routine-review-tribunal

An unattended scheduled routine (the plugin-discovery build, the research-cadence
knowledge-file edits) used to have exactly one gate on its output: CI, plus whichever
single agent happened to be running the routine that day. This skill adds the same
**multi-model, cross-checked** review `/forge` already gives a plan before code is
written — applied instead to a **diff that already exists**, right before the routine
would otherwise finalize/open its PR.

## Where this sits (read this before assuming overlap)

| Mechanism | Reviews | When | This skill vs it |
| --- | --- | --- | --- |
| **the Thing** (`thing-decision.py`) | a single shell **command**, real-time | every `Bash` call | different subject entirely — never touches `PreToolUse(Bash)`. |
| **decision-review** (`thing-decide.py`) | a single yes/no **question** | before asking the human | different payload shape — a question, not a diff; no `required_edits`. |
| **`/forge-pipeline`** | an **idea**, before any code exists | pre-implementation planning | the explicit shape reference (two divergent panels + tiebreak), scoped down: no plan to synthesize, only a completed diff to approve / send back / escalate. |
| **`/code-review`** | a **human-authored** PR, single agent | pre-merge, human work | single-reviewer, no tribunal — fine when a human is the second opinion. This skill exists precisely because an *unattended* routine has no human second-opinion behind it. |
| **this skill** | a **diff an unattended routine just produced** | end of that routine's run, before finalizing the PR | — |

No new agents are invented. The two voting seats and the tiebreaker are the marketplace's
existing personas — Mímir (code-reviewer-shaped), Forseti (security-reviewer-shaped), Thor
(architect-shaped) — the same three the Thing and decision-review already use. Model
resolution reuses `thing-decision.resolve_panel_config` so this panel never silently
drifts from the command-review panel's model-diversity guarantee.

## When to use it

At the end of any scheduled routine whose run contract ends in "commit and open a PR" or
"ships via PR + version bump" — currently:

- [`docs/plugin-discovery-routine-policy.md`](../../../../docs/plugin-discovery-routine-policy.md) — the "build one plugin to gold-standard" routine.
- [`docs/research-routine-two-cadence.md`](../../../../docs/research-routine-two-cadence.md) — the weekly/quarterly research-freshness routine.

Run this gate **after** the routine's own tests/lint pass and **before** the PR is
opened (first run) or marked ready / merged (a revision round). It is not a substitute
for those checks — it is the layer above them, judging whether the diff is *right*, not
just whether it's green.

## The flow

```
1. Assemble the review packet:
     - the diff (git diff against the routine's base, or the PR's patch)
     - the routine's own policy doc (what it was authorized to do unattended)
     - the routine's stated DoD / run contract (what "done" means for this run)

2. Resolve the panel:
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/routine-review-tribunal.py" \
       --root "$CLAUDE_PROJECT_DIR" panels
   → {"panels": {"mimir": {agent, model}, "forseti": {agent, model}}, "tiebreak": {...}, "briefs": {...}}

3. Dispatch BOTH voting seats in ONE batch (parallel Task calls — wall-clock is the
   slower seat, not the sum). Each seat gets: its brief (from `briefs` above), the
   review packet, and this strict output contract:
     {"verdict": "approve"|"request_changes", "confidence": 0.0-1.0,
      "required_edits": ["file:line — what to change", ...],
      "reasoning": "<one paragraph>", "injection_detected": false, "status": "voted"}
   A seat that cannot complete review (dispatch failure, timeout) reports
   `"status": "abstain"` instead of guessing.

4. Tally:
     echo '{"mimir": <mimir-json>, "forseti": <forseti-json>, "thor": null}' | \
       python3 "${CLAUDE_PLUGIN_ROOT}/scripts/routine-review-tribunal.py" \
         --root "$CLAUDE_PROJECT_DIR" tally --routine "<routine-slug>" --round 1

5. Branch on `outcome`:
   - "resolved", verdict "approved"      → finalize (open/ready the PR). Done.
   - "resolved", verdict "needs_revision" → apply `required_edits`, re-diff, go to
     step 3 with `--round <N+1>` (bounded by --max-rounds, default 2).
   - "resolved", verdict "escalate"       → do NOT open/merge/loop. Open (or leave)
     the PR as a flagged draft, note the escalation reason + required_edits in the
     PR description, and use this repo's existing notification path
     (`scripts/notify.sh`) so a human sees it. Stop.
   - "needs_tiebreak"                     → dispatch ONE more Task call, Thor
     (`tiebreak` agent/model from `panels`), giving Thor the diff, the packet, AND
     both peer verdicts (`peers` in the tally output). Thor answers the same JSON
     contract as step 3. Re-tally with `"thor": <thor-json>` filled in — do not
     invent a third voting seat; Thor's vote is binding for this round.
```

## The revision loop is bounded, on purpose

`--max-rounds` (default 2) means: one shot at revision, then escalate. A routine that
cannot converge on tribunal-approved output in two rounds has a problem a third
automated round will not fix — the answer is a human, not more looping. This mirrors
`_revision_or_escalate` in the script and `/forge`'s own "never loop forever, never
land unresolved" discipline.

## The receipt trail

Every `tally` call appends immediately to
`.ravenclaude/runs/routine-review/<slug>/<UTC-timestamp>/run-log.jsonl` (+ a
`round-<N>.json` snapshot) — mirroring FORGE's §0 artifact contract ("append per-gate,
never batch"). This is the audit trail for "why did this routine's PR get approved /
sent back / escalated" without re-running anything. `.ravenclaude/runs/` is gitignored;
if the outcome is `escalate`, quote the `reasoning` + `required_edits` in the PR
description or the escalation notification so the audit trail is not the *only* place
the reasoning lives.

## Guardrails (enforced in the script's `tally()`, not by convention)

- **Injection detected by either voting seat, or by Thor → escalate.** Never
  `approved`, never `needs_revision` — a diff a seat flags as containing a possible
  prompt injection gets a human, full stop.
- **Both seats abstain → escalate.** No silent pass-through when review couldn't run.
- **Disagreement, one abstention, or a unanimous-but-low-confidence vote → tiebreak,
  never a coin flip.** The threshold is `--threshold` (default 0.5 confidence).
- **The round ceiling always resolves to `escalate`, never to a bare `needs_revision`
  the caller might silently drop.** Verified in `--self-test`.

## Verifying the engine

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/routine-review-tribunal.py" --self-test
```

Nine fixture-based checks (no model calls): unanimous approve, unanimous
request_changes with edit dedup, disagreement resolved both ways by Thor,
low-confidence-unanimous convenes tiebreak, one/both-seat abstention, injection
escalation, and the round-ceiling. Run this after touching the script — it is a real
pass/fail CI-citable check (exit 0 = all 9 passed), matching `forge-route.py`'s
`--self-test` convention.
