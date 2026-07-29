#!/usr/bin/env bash
# dod-fast.sh — the fast definition-of-done check the Stop gate runs.
#
# WHAT THE STOP GATE DOES. `hooks/dod-gate.sh` runs this on Stop whenever source
# files changed this session, and BLOCKS the session from ending until it exits
# 0. That is the strongest "follow through" lever in the repo: a CLI cannot
# declare success while this fails. It fires identically on every host — Claude
# Code, Copilot, Codex — because the hook projects to all of them.
#
# WHY A WRAPPER INSTEAD OF A ONE-LINER IN THE POSTURE FILE. The obvious
# configuration is `cmd: "ruff check . && python3 scripts/check-storage-contract.py"`.
# That is brittle in a way that bites exactly when it hurts most: `ruff` is
# frequently NOT on PATH (it lives in a per-user Python bin dir), so on a machine
# where it is missing the command fails, the Stop gate blocks, and the session is
# stuck until it burns through max_blocks — punishing the user for a tool that was
# never installed rather than for anything they did wrong.
#
# So the two checks are treated differently, matching `audit-gates.sh` Gate 9b's
# existing discipline:
#
#   storage contract — stdlib only, ALWAYS runnable, so a failure is a real
#                      failure and blocks. This is the check with teeth.
#   ruff            — runnable only if installed. Present -> a violation BLOCKS.
#                     Absent -> LOUD skip, does not block. A missing linter is
#                     not a defect in the work being checked.
#
# A skip is never silent: the whole point of this repo's gate discipline is that
# "did not run" must never read as "passed".
set -uo pipefail

# ── Anchor on THIS SCRIPT'S location, never on the session's idea of "project".
#
# The first version used `cd "${CLAUDE_PROJECT_DIR:-...}"` and it was wrong in a
# way that only showed up on the first real run: CLAUDE_PROJECT_DIR is the
# SESSION's project directory, which is NOT necessarily the repo this script
# lives in. Launch the CLI from $HOME and work on a repo underneath it — a
# completely ordinary thing to do — and that variable is $HOME. The gate then ran
# `ruff check .` across the entire home directory, reported 81 errors from
# ~/.local/share/doc/node/ and an unrelated sibling repo, and blocked the session
# over lint in files nobody here owns.
#
# The script's own path is the one thing that cannot be wrong: it is at
# <repo>/scripts/dod-fast.sh, so the repo root is one level up. No environment
# variable, no cwd, no git invocation that could resolve somewhere else.
# FAIL CLOSED here, not open. `|| exit 0` would report "definition of done met"
# when the truth is "the checks never ran" — the precise shape of dishonesty this
# gate exists to prevent, and the same one the LOUD ruff skip below avoids. If we
# cannot locate the repo we cannot assert anything about it; say so and block.
# max_blocks (8) is what stops that from becoming a deadlock.
if ! REPO="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"; then
  echo "dod: cannot resolve the repo root from \$0 — refusing to report success" >&2
  exit 1
fi
if ! cd "$REPO"; then
  echo "dod: cannot enter $REPO — refusing to report success" >&2
  exit 1
fi

FAILED=0

# ── 1. The storage contract (stdlib — always runnable, always binding) ────────
if [ -f "$REPO/scripts/check-storage-contract.py" ]; then
  if ! python3 "$REPO/scripts/check-storage-contract.py"; then
    echo "dod: storage-contract check FAILED — see above" >&2
    FAILED=1
  fi
else
  echo "dod: scripts/check-storage-contract.py missing — cannot verify placement" >&2
  FAILED=1
fi

# ── 2. Ruff, if it is available at all (PATH, module, or the user bin dir) ────
RUFF=""
if command -v ruff >/dev/null 2>&1; then
  RUFF="ruff"
elif python3 -c "import ruff" >/dev/null 2>&1; then
  RUFF="python3 -m ruff"
fi

if [ -n "$RUFF" ]; then
  if ! $RUFF check "$REPO"; then
    echo "dod: ruff FAILED — fix the lint errors above before finishing" >&2
    FAILED=1
  fi
else
  # LOUD skip. Not a pass — an absence, named.
  echo "dod: ruff NOT INSTALLED — python lint was NOT checked (this is a SKIP," >&2
  echo "     not a pass). Install it with: pip3 install --user ruff" >&2
fi

if [ "$FAILED" -ne 0 ]; then
  echo "" >&2
  echo "dod: definition-of-done NOT met. The session is blocked until this passes." >&2
  echo "     Fix the failures above, then finish again." >&2
  exit 1
fi

echo "dod: fast checks passed."
exit 0
