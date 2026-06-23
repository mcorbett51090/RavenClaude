---
description: Route a yes/no decision through the command-review tribunal (the Thing) for a binding verdict instead of pausing the human. Use before asking the user any yes/no question, and in the post-PR decision review. The tribunal auto-decides rule/fact-derivable calls and defers genuine preferences (and irreversible/high-blast calls) back to the human.
allowed-tools: Bash, Read
---

# decision-review

Routes a **yes/no decision** through the tribunal's seats (Forseti / Mímir / Heimdall, + Thor on a split) and returns `yes` / `no` / `defer`. This is the decision-mode sibling of command review — it reuses the same panel config but never touches the live `PreToolUse(Bash)` path.

## When to use it

1. **Before asking the user any yes/no question.** Route it here first. If the tribunal returns a binding `yes`/`no`, act on it; if it returns `defer`, ask the user. **Now enforced** (added 2026-05-28): the `PreToolUse(AskUserQuestion)` hook [`hooks/route-decision-review.sh`](../../hooks/route-decision-review.sh) intercepts binary yes/no `AskUserQuestion` calls and runs this routing automatically, so it no longer depends on remembering to invoke the skill manually. The hook handles the **real-time** path; this skill is still the surface for #2.
2. **In the post-PR decision review** (see [`docs/post-pr-decision-review.md`](../../../../docs/post-pr-decision-review.md)) — enumerate the PR's decisions and route the tribunal-eligible ones.

## Before you prompt at all: verify the premise, then batch

Most of a human's decision-prompt burden is **not** the prompts the tribunal correctly defers (genuine preferences, naming, product-intent, high-blast safety) — those *should* reach the human. The avoidable cost is **re-asking the same decision** because it was surfaced before its premise was checked. Two disciplines, applied **before** any `AskUserQuestion`:

1. **Verify the load-bearing claim first.** If a decision's answer depends on a *fact* — a count, whether a field/entity exists, an API behavior, "X is missing" — **verify that claim before you prompt** (read the artifact, run the check, cross-confirm). A prompt built on an unverified premise that later flips forces a re-ask; a worked case lost three prompt rounds to a "missing columns" claim that turned out false. This is the [`CLAUDE.md`](../../CLAUDE.md) § "Verify the load-bearing assumption before a high-impact activity" clause applied to *soliciting a decision*, not just to destructive acts.
2. **Batch related decisions into one post-verification prompt.** Don't fragment one design surface (e.g. a feature's scope + its sub-choices) across rounds. Verify the premises, then ask the related decisions together in a single consolidated `AskUserQuestion`.

This reduces *rounds*, not the legitimate deferrals — it never auto-decides a genuine preference (the guardrails below still own that).

## How to invoke

```bash
echo '{"question":"<yes/no question>","context":"<why, options, the rule/fact that bears on it>","high_blast":false}' \
  | python3 "${CLAUDE_PLUGIN_ROOT}/scripts/thing-decide.py" --root "$CLAUDE_PROJECT_DIR" decide
```

- Set `"high_blast": true` for irreversible / high-stakes decisions (force-push, deletes, prod actions, anything in the `security_deny` family). These **never auto-resolve** — the tribunal always defers them to the human, even in binding mode.
- Output is one JSON object: `{"verdict":"yes"|"no"|"defer","mode":...,"binding":true|false,"reasoning":...,"seats":[...],"saga_log":...}`.

## Acting on the verdict

| `verdict` | `binding` | What you do |
| --- | --- | --- |
| `yes` / `no` | `true` | **Act on it** without pausing the user. The Sága log records the panel's reasoning. |
| `yes` / `no` | `false` (advisory mode) | Treat as a **recommendation**; you still decide / surface it. |
| `defer` | — | **Ask the user.** The decision is a genuine preference, was high-blast, or the panel couldn't reach confident agreement. |

## The mode knob

`decision_review` in `.ravenclaude/comfort-posture.yaml` controls this:

| Mode | Behavior |
| --- | --- |
| `off` (default) | Every decision returns `defer` — the human decides. Nothing is auto-resolved. |
| `advisory` | The panel renders a verdict, but it's a recommendation; the agent/human still decides. |
| `binding` | A confident, non-high-blast `yes`/`no` stands and the agent acts on it. `defer` still escapes to the human. |

Off-by-default means no one is auto-decided into without opting in. The seats run via `claude -p`, so live verdicts need the CLI available; absent it (or on any seat error/timeout), the panel abstains and the verdict fails safe to `defer`.

## Reasoning depth — where extended thinking belongs (and where it deliberately doesn't)

A natural question (gap **B1** of the [2026-06-04 features gap analysis](../../../../docs/research/2026-06-04-claude-features-gap-analysis/gap-analysis.md)): should the tribunal **seats** engage extended thinking for high-stakes calls? The deliberate answer is **no — not in the seat engine**, for two grounded reasons:

1. **The seats are narrow JSON adjudications, not open reasoning.** Each seat gets a small, bounded `(question, context)` and must return a strict verdict JSON. That shape benefits little from a large thinking budget, and the seats already run under a tight soft cap (cold-start `claude -p` latency is the binding constraint — see `CLAUDE.md` → "Copilot-aware tribunal seat soft cap"). Adding `ultrathink` to seat prompts would push more seats into the **abstain-on-timeout** path, which fails *closed* — i.e. it would make the panel *less* decisive, not more.
2. **`thing-decide.py` is guarded by byte-identical invariants + gates.** The engine carries explicit "byte-identical" / shadow-evaluator invariants (Gate 91, `thing-golden-eval.py`); mutating the seat prompt is exactly the kind of change those gates exist to catch. The right lever stays **opt-in and default-off**.

**Where the reasoning depth *does* belong:** the **caller**. When *you* (the agent, or the post-PR review pass #2 above) are weighing a genuinely high-stakes decision **before** routing it, reason with extended thinking on your side — frame the question, surface the rule/fact that bears on it, enumerate options — then hand the tribunal a crisp yes/no. The depth lives in how the question is *prepared*, not in the seat subprocess. For the **planning** analog (forge's critic / red-team, which *are* open-ended reasoning), the `ultrathink`-in-the-brief convention is documented in [`forge-pipeline/SKILL.md`](../forge-pipeline/SKILL.md) → "Thinking budget for the reasoning gates."

## Guardrails (enforced in `thing-decide.py`)

- **Only the tribunal-eligible get decided.** Genuine preference questions surface as `defer` (Mímir votes low-confidence → escalate → Thor → defer).
- **High-blast / irreversible decisions never auto-resolve** — always `defer`, regardless of mode or panel confidence.
- **`defer`, low confidence, a split-to-defer, panel abstention, or detected injection all escape to the human.** Binding ≠ "the panel must answer."
- **Every routed decision is Sága-logged** under `.ravenclaude/runs/thing/decisions/`.
