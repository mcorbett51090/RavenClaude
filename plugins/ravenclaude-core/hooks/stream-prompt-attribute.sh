#!/usr/bin/env bash
# stream-prompt-attribute.sh
# UserPromptSubmit hook (P4, Agentic Work-Streams) — OPT-IN, FAIL-OPEN per-prompt
# attribution. The plan's per-prompt surface, deferred behind a posture toggle.
#
# DEFAULT OFF: no-ops (a single grep, zero cost) unless .ravenclaude/comfort-posture.yaml
# sets `stream_hook: per_prompt`. The default `session_boundary` (or absent) → instant exit 0.
#
# WHAT IT DOES when per_prompt is on:
#   - STICKY SHORT-CIRCUIT (the cheap path): if a stream is ACTIVE, attribute this prompt
#     to it as ONE derived event — it does NOT re-classify (the sticky rule). This is a
#     `test -f active-stream` + a derive-features call; no model, no git.
#   - If NO stream is active AND `stream_classify: auto`, classify the prompt + (only on a
#     confident match) set the active stream. label_only/off here → suggest nothing
#     (the SessionStart banner is the suggest surface; per-prompt only attributes/auto-sets).
#
# THE TWO LOAD-BEARING INVARIANTS (the highest-risk surface — security-reviewed):
#   1. NO-EGRESS: the prompt is read to DERIVE features only; stream-ops.append_event
#      refuses any raw-content field, so only labels/terms/word-count/session_id reach disk.
#      The prompt text NEVER egresses.
#   2. FAIL-OPEN: this hook can NEVER block a prompt. It always exits 0 and emits NOTHING on
#      stdout that would alter the prompt — a classifier error, a missing python3, a timeout,
#      anything → silent exit 0. A latency budget (RC_STREAM_HOOK_BUDGET_S, default 3s) caps
#      the inner work so a slow disk can't stall the prompt.
#
# Wired in hooks.json (UserPromptSubmit) + the dev-mirror .claude/settings.json + the
# Copilot installer (.github/hooks via the adapter's `userpromptsubmit` mode).

set -euo pipefail

# Read the UserPromptSubmit payload (carries .prompt + .session_id).
payload=""
[ ! -t 0 ] && payload="$(cat 2>/dev/null || true)"

project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -d "$project_dir" ] || exit 0

posture="$project_dir/.ravenclaude/comfort-posture.yaml"
# Fast opt-in gate: do nothing unless `stream_hook: per_prompt` is set. A single grep.
[ -f "$posture" ] || exit 0
grep -Eq '^[[:space:]]*stream_hook[[:space:]]*:[[:space:]]*per_prompt([[:space:]]|#|$)' "$posture" 2>/dev/null || exit 0

# python3 required for the derive/classify work. Absent -> fail-open no-op.
command -v python3 >/dev/null 2>&1 || exit 0

# Resolve the helper libs: ${CLAUDE_PLUGIN_ROOT} when installed, else in-repo.
scripts_dir="${CLAUDE_PLUGIN_ROOT:-}/scripts"
if [ ! -f "$scripts_dir/stream-ops.py" ]; then
  scripts_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../scripts" 2>/dev/null && pwd || true)"
fi
[ -f "$scripts_dir/stream-ops.py" ] || exit 0

# Resolve the session id (FK back to runs/<id>/) — best-effort, derived metadata only.
session_id="${CLAUDE_SESSION_ID:-}"
if [ -z "$session_id" ] && [ -n "$payload" ] && command -v jq >/dev/null 2>&1; then
  session_id="$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null || true)"
fi

# Extract the prompt text from the payload (for DERIVATION only — never persisted raw).
prompt=""
if [ -n "$payload" ] && command -v jq >/dev/null 2>&1; then
  prompt="$(printf '%s' "$payload" | jq -r '.prompt // .promptText // empty' 2>/dev/null || true)"
fi
# If we somehow got no payload (arg-only invocation), there is nothing to attribute.
[ -z "$prompt" ] && exit 0

# Hard latency budget: cap the inner python so a slow disk can't stall the prompt.
budget="${RC_STREAM_HOOK_BUDGET_S:-3}"
timeout_bin=""
command -v timeout >/dev/null 2>&1 && timeout_bin="timeout ${budget}s"

# All work is in python (fail-open by contract). The prompt is passed via an ENV VAR
# (RC_STREAM_PROMPT) so it is never visible in `ps`/argv AND does not collide with the
# heredoc on stdin. Any failure -> exit 0 below (the prompt is never blocked).
RC_STREAM_PROMPT="$prompt" $timeout_bin python3 - "$scripts_dir" "$project_dir" "$session_id" <<'PY' 2>/dev/null || true
import importlib.util
import os
import sys

scripts_dir, root, session_id = sys.argv[1], sys.argv[2], (sys.argv[3] or None)
prompt = os.environ.get("RC_STREAM_PROMPT", "")


def _load(name):
    p = scripts_dir + "/" + name
    spec = importlib.util.spec_from_file_location(name.replace(".py", "").replace("-", "_"), p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


try:
    ops = _load("stream-ops.py")
    clf = _load("stream-classify.py")
except Exception:
    sys.exit(0)

try:
    # DERIVE features from the prompt (the only thing we may persist).
    feats = clf.derive_features(prompt)

    active = ops.read_active(root)
    if active:
        # STICKY: attribute this prompt to the active stream — NO reclassify.
        ops.append_event(
            root, active,
            kind="prompt_attributed",
            label=feats["label"],
            terms=feats["terms"],
            word_count=feats["word_count"],
            session_id=session_id,
        )
        sys.exit(0)

    # No active stream. Only `auto` mode acts here (label_only/off → do nothing; the
    # SessionStart banner is the suggest surface).
    try:
        sss = _load("stream-session-start.py")
        cfg = sss.read_config(__import__("pathlib").Path(root))
    except Exception:
        sys.exit(0)
    if cfg.get("mode") != "auto":
        sys.exit(0)

    centroids = ops.get_centroids(root)
    if not centroids:
        sys.exit(0)
    res = clf.classify(prompt, centroids, threshold=cfg["threshold"])
    if res["confident"] and res["best_stream"]:
        try:
            ops.set_active(root, res["best_stream"])
            ops.append_event(
                root, res["best_stream"],
                kind="prompt_attributed",
                label=feats["label"],
                terms=feats["terms"],
                word_count=feats["word_count"],
                session_id=session_id,
                score=res["best_score"],
            )
        except ValueError:
            pass
except Exception:
    sys.exit(0)
PY

# ALWAYS exit 0 — this hook is fail-open and never alters/blocks the prompt.
exit 0
