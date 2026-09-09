---
description: "Run the prompt-optimizer's classify -> generate -> format pipeline on a prompt/ask as the assistant's own in-turn action, so a flagged wild assumption triggers a real AskUserQuestion call — the reliable fallback the passive UserPromptSubmit hook structurally cannot provide. Works regardless of the prompt_optimizer.enabled posture knob."
allowed-tools: Bash, Write, Read, AskUserQuestion
argument-hint: <the prompt or ask to optimize>
---

# /optimize

Run the same classify -> generate -> format pipeline the `prompt_optimizer` hook path
runs (`prompt-optimizer-gate.sh` Tier-0/Tier-1 classifier -> `prompt-optimizer-rewrite.sh`
or `prompt-optimizer-dispatch.sh` -> `prompt-optimizer-format.py`), but as **this turn's
own action** instead of a passive hook injection.

## Why this command exists — the reliability gap it closes

The `UserPromptSubmit` hook (`prompt-optimizer-gate.sh`, when
`.ravenclaude/comfort-posture.yaml`'s `prompt_optimizer.enabled: true`) can only inject
advisory `additionalContext` into the turn. A hook **cannot** synchronously call
`AskUserQuestion` — it can only write text into context and hope the assistant reading
that context complies. `/optimize` runs as the assistant's **own** turn, where
`AskUserQuestion` genuinely **is** synchronously callable. So when the pipeline flags
`wild_assumption.present == true`, this command's own instructions (Step 5 below) direct
you to actually call `AskUserQuestion`, not just relay advisory text.

## It does NOT depend on `prompt_optimizer.enabled`

This command is a **deliberate, independent entry point**. It never reads the active
project's `prompt_optimizer.enabled` value and never gates on it — the pipeline below
always runs, whether the posture knob is `true`, `false`, or the block is absent
entirely (the shipped default). It achieves this by running the classifier/generator/
formatter scripts against a **synthetic, throwaway scratch project directory** that
always carries `prompt_optimizer: {enabled: true, mode: binding-context}` — never the
real project's own posture file. This is orchestration of the existing Phase 2-5
scripts exactly as shipped; none of their logic is reimplemented or modified.

(If you are auditing this file for a stray `prompt_optimizer.enabled` check against the
**real** project posture: there isn't one. Step 2 below is the only place this command
touches that key, and it always writes `true` into a scratch directory, never reads or
branches on the real project's value.)

## Step 1 — Get the prompt/ask text safely into a file

The argument is `$ARGUMENTS`. Prompts can be long, multi-line, or contain characters
that are hazardous to splice into a shell command line (backticks, quotes, `$(...)`).
**Use the Write tool** (not a Bash heredoc) to write the argument text verbatim to a
temp file — this sidesteps all shell-quoting hazards, since Write takes the content
directly with no shell interpretation:

- If `$ARGUMENTS` is empty, tell the user `/optimize` needs a prompt/ask to evaluate
  (e.g. `/optimize fix the login bug and make it faster`) and stop here.
- Otherwise, `Write` the literal argument text (nothing added, nothing stripped) to
  `/tmp/rc-optimize-prompt.txt` (or any other writable temp path).

## Step 2 — Run the pipeline (one Bash call)

Run this script with the **Bash** tool. Use a generous timeout (e.g. 180000ms) — the
Tier-1 classifier call plus a generator call are each real model calls with their own
internal timeouts (25s / 30s / 40s respectively) and can legitimately take that long.
Substitute the real path to the file you wrote in Step 1 for `PROMPT_FILE` below.

```bash
set -u
PROMPT_FILE="/tmp/rc-optimize-prompt.txt"          # the file Step 1 wrote
REAL_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"      # capture BEFORE overriding
SESSION_ID="${CLAUDE_SESSION_ID:-optimize-$(date +%s)}"

SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT

mkdir -p "$SCRATCH/.ravenclaude"
cat >"$SCRATCH/.ravenclaude/comfort-posture.yaml" <<'YAML'
# Synthetic posture for /optimize's own independent pipeline run. This file
# lives ONLY in a throwaway scratch directory -- it is never the real
# project's posture and this command never reads the real project's
# prompt_optimizer.enabled value. Always enabled, mode binding-context (the
# strongest of the two non-shadow modes; shadow/advisory/binding-context are
# behaviorally identical for emission purposes -- binding-context is chosen
# for clarity of intent, an approval-gate invocation).
prompt_optimizer:
  enabled: true
  mode: binding-context
YAML

PAYLOAD="$(jq -Rs '{prompt: .}' <"$PROMPT_FILE")"

# Point the pipeline at the scratch project dir ONLY for this pipeline run.
export CLAUDE_PROJECT_DIR="$SCRATCH"
export CLAUDE_SESSION_ID="$SESSION_ID"

GATE_OUT="$(printf '%s' "$PAYLOAD" | bash "${CLAUDE_PLUGIN_ROOT}/scripts/prompt-optimizer-gate.sh" 2>/dev/null || true)"

echo "--- prompt-optimizer verdict ---"
if [ -z "$GATE_OUT" ]; then
  echo "(no verdict -- Tier-0 free skip, or a Tier-1/generator step failed open. Proceed with the prompt as given.)"
  echo "OPTIMIZE_WILD_ASSUMPTION_FLAGGED=false"
  echo "OPTIMIZE_HAS_CONTEXT=false"
else
  CTX="$(printf '%s' "$GATE_OUT" | jq -r '.hookSpecificOutput.additionalContext // empty')"
  if [ -z "$CTX" ]; then
    echo "(empty context. Proceed with the prompt as given.)"
    echo "OPTIMIZE_WILD_ASSUMPTION_FLAGGED=false"
    echo "OPTIMIZE_HAS_CONTEXT=false"
  else
    printf '%s\n' "$CTX"
    if printf '%s' "$CTX" | grep -q 'Call AskUserQuestion as your first tool call'; then
      echo "OPTIMIZE_WILD_ASSUMPTION_FLAGGED=true"
    else
      echo "OPTIMIZE_WILD_ASSUMPTION_FLAGGED=false"
    fi
    echo "OPTIMIZE_HAS_CONTEXT=true"
  fi
fi
echo "--- end verdict ---"

# Copy any audit artifacts this run produced into the REAL project's runs
# dir, so /optimize's output lands in the same discoverable location the
# hook path uses (same output vocabulary/location as the hook path).
REAL_AUDIT_DIR="$REAL_PROJECT_DIR/.ravenclaude/runs/$SESSION_ID/prompt-optimizer"
mkdir -p "$REAL_AUDIT_DIR" 2>/dev/null || true
for f in "$SCRATCH"/.ravenclaude/runs/*/prompt-optimizer/*.json; do
  [ -f "$f" ] || continue
  cp "$f" "$REAL_AUDIT_DIR/$(basename "$f")" 2>/dev/null || true
done
```

## Step 3 — Read the verdict

The Bash output between `--- prompt-optimizer verdict ---` and `--- end verdict ---` is
**exactly** the `additionalContext` text the hook path would have injected for this same
prompt — it comes from the identical `prompt-optimizer-format.py` formatter, unmodified
(this is why its schema matches the hook path byte-for-byte: it IS the hook path's own
formatter, called directly).

- `OPTIMIZE_HAS_CONTEXT=false` (or no verdict at all) — nothing was flagged. Proceed with
  the original prompt/ask unmodified. Do not fabricate a rewrite or a dispatch plan that
  the pipeline didn't produce.
- `OPTIMIZE_HAS_CONTEXT=true` and `OPTIMIZE_WILD_ASSUMPTION_FLAGGED=false` — a rewrite or
  dispatch plan was produced with no wild assumption. Show the verdict text to the user,
  then proceed using the rewritten prompt (rewrite path) or treat the dispatch plan as
  advisory guidance (dispatch-plan path — you still decide whether/how to act on it;
  nothing was auto-dispatched).
- `OPTIMIZE_WILD_ASSUMPTION_FLAGGED=true` — go to Step 4. **Do not proceed with the
  original request yet.**

## Step 4 — The approval gate (the reliability fix this phase exists to ship)

When `OPTIMIZE_WILD_ASSUMPTION_FLAGGED=true`, **your very next tool call must be
`AskUserQuestion`** — not a continuation of the original task, not more Bash, not a
restatement in prose. This is the one behavior a passive hook cannot force and a slash
command can: do it for real, every time this flag is true.

Present the flagged assumption (the "Flagged assumption (confidence: ...): ..." line
from the verdict text) to the user as the question, with options such as:

- **Yes, that assumption is correct** — proceed with the rewrite/plan as drafted.
- **No, here's the correct context** — let the user supply what was missing, then
  proceed using their correction instead of the flagged guess.
- **Let me rephrase the request** — abandon this pass; ask the user for a clearer ask.

Only after the user answers do you proceed with the (possibly corrected) task.

## Step 5 — Proceed with the work

With any wild assumption resolved (or none flagged), do the actual work the user asked
for — using the rewritten prompt as your working directive on the rewrite path, or your
own judgment informed by the dispatch plan on the dispatch-plan path. `/optimize` is a
pre-flight check on the request, not the end of the interaction; per this plugin's
Agentic-Default Principle, don't stop and hand back a to-do when the request itself is
now clear enough to act on.

## Troubleshooting / fail-open behavior

Every stage of the underlying pipeline fails open by design (missing `claude`/`jq`/
`python3`, a timeout, unparseable model output, an invalid schema) — the worst case is
an empty verdict (Step 3's first bullet), never a crash or a stall. If the Bash call
itself times out before the pipeline finishes, re-run Step 2 with a longer timeout, or
tell the user the optimizer step could not complete this time and proceed with the
prompt as given.
