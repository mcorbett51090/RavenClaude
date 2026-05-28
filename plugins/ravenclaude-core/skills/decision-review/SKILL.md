---
description: Route a yes/no decision through the command-review tribunal (the Thing) for a binding verdict instead of pausing the human. Use before asking the user any yes/no question, and in the post-PR decision review. The tribunal auto-decides rule/fact-derivable calls and defers genuine preferences (and irreversible/high-blast calls) back to the human.
allowed-tools: Bash, Read
---

# decision-review

Routes a **yes/no decision** through the tribunal's seats (Forseti / Mímir / Heimdall, + Thor on a split) and returns `yes` / `no` / `defer`. This is the decision-mode sibling of command review — it reuses the same panel config but never touches the live `PreToolUse(Bash)` path.

## When to use it

1. **Before asking the user any yes/no question.** Route it here first. If the tribunal returns a binding `yes`/`no`, act on it; if it returns `defer`, ask the user. **Now enforced** (added 2026-05-28): the `PreToolUse(AskUserQuestion)` hook [`hooks/route-decision-review.sh`](../../hooks/route-decision-review.sh) intercepts binary yes/no `AskUserQuestion` calls and runs this routing automatically, so it no longer depends on remembering to invoke the skill manually. The hook handles the **real-time** path; this skill is still the surface for #2.
2. **In the post-PR decision review** (see [`docs/post-pr-decision-review.md`](../../../../docs/post-pr-decision-review.md)) — enumerate the PR's decisions and route the tribunal-eligible ones.

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

## Guardrails (enforced in `thing-decide.py`)

- **Only the tribunal-eligible get decided.** Genuine preference questions surface as `defer` (Mímir votes low-confidence → escalate → Thor → defer).
- **High-blast / irreversible decisions never auto-resolve** — always `defer`, regardless of mode or panel confidence.
- **`defer`, low confidence, a split-to-defer, panel abstention, or detected injection all escape to the human.** Binding ≠ "the panel must answer."
- **Every routed decision is Sága-logged** under `.ravenclaude/runs/thing/decisions/`.
