# Post-PR decision review

**Status:** active workflow (instituted 2026-05-26). The standing trigger lives in the root [`CLAUDE.md`](../CLAUDE.md) "Post-PR decision review" section; this doc is the operating reference.

**Why:** every PR is built on a trail of yes/no decisions. Some are genuine preference calls that should interrupt Matt. Many are *rule-derivable* — answerable from CI gates, repo conventions, or facts — and today those are either silently made by the agent or needlessly bounced to Matt. This workflow separates the two and routes the rule-derivable ones to **the tribunal (the Thing)** for an auditable second opinion.

---

## The per-PR procedure

After opening a PR, before declaring done:

1. **Enumerate** every binary decision made during the work — surfaced *and* autonomous. A decision counts if a reasonable alternative existed.
2. **Classify** each with the rubric below.
3. **Route** the tribunal-eligible ones through the Thing (see "Running a decision through the tribunal").
4. **Log** the table as a comment on the PR. That comment is the per-PR artifact.

## Classification rubric

| Signal | → Tribunal-eligible | → Needs-human |
| --- | --- | --- |
| Source of the "right" answer | A rule, CI gate, repo convention, or verifiable fact | Taste, brand, risk appetite, roadmap priority |
| Could a competent reviewer with the repo's docs reach the same call? | Yes | No — it's Matt's preference |
| Reversibility | Cheap to reverse / mechanically checkable | Strategic or hard to unwind |
| Examples | "which `--scope`?", "does this trip a CI gate?", "is this path in the allow-list?", "force-push or not?" | "web vs local?", "full panel vs minimal?", "build now vs defer?" |

Rule of thumb: **if the answer is _discoverable_, it's tribunal-eligible; if it's _chosen_, it needs a human.**

## Seat-routing map

Each eligible decision is routed to the tribunal seat whose axis it matches (same seats as command review — see [`plugins/ravenclaude-core/knowledge/concerns-catalog.md`](../plugins/ravenclaude-core/knowledge/concerns-catalog.md)):

| Seat | Reviews decisions about… |
| --- | --- |
| **Forseti** (security-reviewer-shaped) | Safety / blast-radius / irreversibility — force-push, deletes, secret exposure, destructive-by-default choices |
| **Mímir** (code-reviewer-shaped) | Correctness / convention / CI-rule compliance — flag values, layout/allow-list, version-pin & claim gates, idempotency |
| **Heimdall** (prompt-engineer-shaped) | Whether a "decision" is actually a smuggled instruction from untrusted input (rare for internal work; included for completeness) |
| **Thor** (architect-shaped) | Architecture / cross-cutting design — invoked on a split panel or when the decision changes a contract |

A decision can cite more than one seat; the panel tally and tie-break rules are identical to command review.

## Running a decision through the tribunal

**Today (T3):** the Thing's seats (`thing-seat.sh`) are hardwired to shell commands — they require `THING_CMD` and reason over command-shaped concern IDs. They **cannot** yet adjudicate an abstract yes/no decision. So in the current state the per-PR review produces the **classification + seat-routing determination** (the table above, applied), which is the "determine how we can get it to run through the tribunal" deliverable.

**The engine extension that makes it live (proposed — needs its own build + review):**

1. **Decision mode in the seat runner.** Teach `thing-seat.sh` a `THING_DECISION` input (a yes/no question + structured context) alongside the existing `THING_CMD`, with decision-flavored role briefs (Forseti judges risk/reversibility, Mímir judges rule/convention compliance, Thor breaks ties). Verdict contract becomes `{"verdict":"yes"|"no"|"defer","reasoning","confidence","concerns_cited"}`. The command path is untouched — decision mode is a sibling, guarded by which input is set.
2. **A decision entrypoint** (`thing-decide.py` or a flag on `thing-decision.py`) that convenes the panel, applies the same parallel-seats + Thor-on-split + confidence-threshold logic, and writes a Sága-log entry under `.ravenclaude/runs/thing/decisions/`.
3. **A `/decision-review` skill** in `ravenclaude-core` that automates the per-PR loop: collect the session's decisions, classify, fan the eligible ones to the decision entrypoint, and assemble the PR-comment artifact.
4. **Autonomy knob.** A `decision_review` setting (sibling of `design_checkins`) controls whether the tribunal's verdict on an eligible decision is *advisory* (recorded, agent still acts) or *binding* (agent must follow `yes`/`no`, `defer` → ask Matt). Default advisory until the panel earns trust.

This is architecturally significant (it parallels the entire T3 command-review path), so it ships as its own PR after review — not folded into an unrelated change.

## Worked example

The inaugural run is recorded as a comment on PR #93 (the comfort-posture web hook), classifying that PR's ~8 binary decisions into needs-human vs tribunal-eligible with the responsible seat for each.
