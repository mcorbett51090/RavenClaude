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
      "reasoning": "<one paragraph>", "injection_detected": false,
      "design_decision": false, "status": "voted"}
   A seat that cannot complete review (dispatch failure, timeout) reports
   `"status": "abstain"` instead of guessing. `design_decision` is a SECOND,
   independent vote (see "Merge authority" below) — a seat still casts `verdict`
   as normal even when it flags `design_decision: true`; the two axes are not
   coupled.

4. Tally:
     echo '{"mimir": <mimir-json>, "forseti": <forseti-json>, "thor": null}' | \
       python3 "${CLAUDE_PLUGIN_ROOT}/scripts/routine-review-tribunal.py" \
         --root "$CLAUDE_PROJECT_DIR" tally --routine "<routine-slug>" --round 1

5. Branch on `outcome`:
   - "resolved", verdict "approved", `merge_authority: "auto"` → the diff is both
     correct AND not a design/architecture call — merge it directly, per Matt's
     explicit directive (2026-09-11): "I'm probably not going to read the PR before
     calling for a merge, so I want as much auto-merged as possible. The only thing
     I should review is something that is a design or architecture decision." See
     "Auto-merge procedure" below for the exact steps. Done.
   - "resolved", verdict "approved", `merge_authority: "human"` → the diff is
     correct but a seat judged it a design/architecture call — open/ready the PR,
     note in the PR description WHICH seat flagged `design_decision` and its
     `reasoning`, and notify per the routine's own notification discipline. A
     person merges. Do NOT merge this one yourself. Done.
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

## Merge authority — a second, independent axis (added 2026-09-11)

An `approved` verdict answers "is this diff good work?" It does NOT by itself answer
"should this merge itself, unattended?" Every voting seat (and Thor, if convened)
also casts `design_decision: true|false` — does the diff embody a real design or
architecture decision (multiple reasonable options existed and judgment picked one),
as opposed to a mechanical/correctness/build-to-spec change with no real alternative?

- **Any** seat that voted flags `design_decision: true` → `merge_authority: "human"`,
  even if every seat approved the diff's quality. Same any-seat-raises-it-wins shape
  as `injection_detected`. A design-decision diff can still be fine work — it just
  doesn't get to merge itself.
- **Every** seat that voted says `design_decision: false` → `merge_authority: "auto"`.
- `merge_authority` is only present on the JSON payload when `verdict == "approved"` —
  it is meaningless on a diff that was sent back or escalated, so the field is
  omitted there rather than printed as a misleading no-op.

This is the mechanism, not a suggestion: before this addition, NOTHING in this
skill, in `routine-review-tribunal.py`, or in either routine's policy doc
(`docs/plugin-discovery-routine-policy.md`, `docs/research-routine-two-cadence.md`)
ever called a merge tool — "finalize" meant only "open/ready the PR." The two PRs
this mechanism was built to replace a human-driven merge for (#1160, #1161) were
merged by a human operator acting on an explicit chat instruction that turn, not by
the routine itself. `merge_authority: "auto"` is what makes the routine's own merge
call authorized without a live human in the loop for that specific run.

## Auto-merge procedure (`merge_authority: "auto"` only)

1. If the PR is still a draft, mark it ready for review
   (`ManagePullRequest` `update_pr` with `draft: false`). This re-triggers checks
   that don't run on drafts — confirmed empirically on PR #1160: the "Semantic PR
   title" check re-ran, and the three Cursor bot checks (Bugbot, Security Agent,
   Approval Agent) fired for the first time.
2. Wait for `main`'s **required** status checks to report success. As of
   2026-09-11 (verified via `gh api repos/<owner>/<repo>/rules/branches/main`) these
   are exactly: *Validate manifests and hooks*, *Validate file paths against
   .repo-layout.json*, *Validate plugin and marketplace JSON Schemas*, *Semantic PR
   title (Conventional Commits)*, *Scan for committed secrets (TruffleHog)*, *Lint
   workflow permissions + action pins*, *Lint GitHub Actions (zizmor)*. Re-check
   this list if it may have drifted — do not hard-code it as permanent.
3. The three Cursor bot checks (Bugbot, Security Agent, Approval Agent) are **not**
   required — they may legitimately stay `pending` indefinitely. Do not wait on
   them, and do not treat a pending Cursor-bot check as a blocker.
4. Merge via the GitHub MCP `merge_pull_request` tool (`CallDynamicTool`, namespace
   `Github` or `GitHub-PAT` — whichever is connected this session), `merge_method:
   "squash"`, matching how #1160 and #1161 were merged. Do NOT use `gh pr merge` —
   this repo's `gh` access is read-only by house rule, and `ManagePullRequest` has
   no merge action (only `create_pr`/`update_pr`/`post_comment`/`resolve_comment`/
   `get_ci_status`/`set_pr_status`).
5. If any required check fails (not just pending), do NOT merge — fall back to
   `merge_authority: "human"` handling: leave the PR open, note the failure, notify.
   A required check failing is new information the tribunal never saw; it does not
   get silently retried into a merge.

**Honest limit, stated rather than assumed:** this procedure has been exercised
manually (by a human-directed session) but not yet by a routine running fully
unattended end-to-end. If a genuinely unattended run's own platform-level
instructions constrain it from calling a merge tool without a live user message,
this written, dated, Matt-sourced policy is intended to serve as that "explicit
instruction" going forward — but that has not been empirically verified by an actual
unattended run yet. Treat the first few auto-merges as a thing to spot-check, not a
settled fact.

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
- **Any seat flagging `design_decision: true` → `merge_authority: "human"`, even on
  an otherwise-unanimous `approved`.** A design/architecture call never merges
  itself, no matter how confident or unanimous the quality verdict was.
- **`merge_authority` is never printed on a non-`approved` verdict.** The field is
  only meaningful once the diff has actually been approved — omitted otherwise
  rather than defaulted to a value the caller might misread as a green light.

## Verifying the engine

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/routine-review-tribunal.py" --self-test
```

Twelve fixture-based checks (no model calls): unanimous approve, unanimous
request_changes with edit dedup, disagreement resolved both ways by Thor,
low-confidence-unanimous convenes tiebreak, one/both-seat abstention, injection
escalation, the round-ceiling, and (added 2026-09-11) four `merge_authority` checks —
unanimous-no-flag auto, unanimous-one-flag human, Thor-tiebreak-with-flag human,
Thor-tiebreak-no-flag auto — plus a check that `merge_authority` is absent on a
non-approved verdict. Run this after touching the script — it is a real pass/fail
CI-citable check (exit 0 = all 12 passed), matching `forge-route.py`'s `--self-test`
convention.
