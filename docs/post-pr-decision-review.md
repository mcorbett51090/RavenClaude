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

## Scope: all yes/no questions route through the tribunal

This is not only a post-PR retrospective. **Every yes/no decision routes through the tribunal before it reaches the human** — the post-PR pass is just one application. The flow:

1. Facing a yes/no decision (real-time, or while reviewing a PR), invoke the `decision-review` skill.
2. A **binding** `yes`/`no` → act on it without pausing the human.
3. `defer` → ask the human. The panel defers genuine preferences, low-confidence / split calls, anything tagged `high_blast`, and any decision when `decision_review` is `off`.

## Running a decision through the tribunal (shipped)

The engine is [`plugins/ravenclaude-core/scripts/thing-decide.py`](../plugins/ravenclaude-core/scripts/thing-decide.py), driven by the [`decision-review`](../plugins/ravenclaude-core/skills/decision-review/SKILL.md) skill. It is **self-contained** — it convenes its own seats and does **not** touch the live `PreToolUse(Bash)` command path (`thing-seat.sh` / `thing-orchestrator.sh`), so command review stays pristine. It reuses `thing-decision.resolve_panel_config`, so the decision panel never drifts from the command panel.

```bash
echo '{"question":"<yes/no>","context":"<why + the rule/fact that bears on it>","high_blast":false}' \
  | python3 "${CLAUDE_PLUGIN_ROOT}/scripts/thing-decide.py" --root "$CLAUDE_PROJECT_DIR" decide
```

- Seats run sequentially (a review is not latency-critical); abstention / low-confidence / split-to-defer / injection all fail safe to `defer`.
- `decision_review: off | advisory | binding` in `.ravenclaude/comfort-posture.yaml` controls autonomy; **off by default**.
- `high_blast: true` decisions never auto-resolve — always `defer`.
- Every routed decision is Sága-logged under `.ravenclaude/runs/thing/decisions/`.

**Verification caveat:** the seats call `claude -p`, which can't run in CI or some sandboxes. The engine is tested via the `THING_DECIDE_MOCK_VERDICT` hook (every tally + envelope path) and the gate-audit; true live behavior needs a real session with the CLI present.

## Worked example

The inaugural run is recorded as a comment on PR #93 (the comfort-posture web hook), classifying that PR's ~8 binary decisions into needs-human vs tribunal-eligible with the responsible seat for each.
