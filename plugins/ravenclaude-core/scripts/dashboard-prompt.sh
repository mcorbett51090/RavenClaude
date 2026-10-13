#!/usr/bin/env bash
# dashboard-prompt.sh
# SessionStart hook body. ADVISORY, fixed-text prompt that tells a person who has
# not set up a comfort posture how to open the dashboard. It can NEVER block a
# session, write a file, start a process, or touch the network.
#
# ── WHY THIS EXISTS ──────────────────────────────────────────────────────────
# Nothing told a new user the dashboard exists. `dashboard-autostart.sh` stops at
# its first line unless a posture file already exists, and the session banner
# names dashboard TABS but never says "run /dashboard". So "it didn't open" was
# correct-by-design and undiscoverable. Autostarting a local server and a browser
# tab for every session was rejected: it is an undisclosed background process, it
# steals focus across concurrent sessions, and it widens the loopback `/__save`
# write surface for everyone. A prompt costs one line and surprises nobody. The
# opt-in `dashboard_autostart: off | serve | open` knob is unchanged and the
# prompt names it.
#
# ── WHEN IT SPEAKS ───────────────────────────────────────────────────────────
# Only when the project has NO .ravenclaude/comfort-posture.yaml. Once that file
# exists the person has configured RavenClaude and this hook is silent — which is
# also how to silence it without opening a dashboard: create the (empty) file.
# No state is kept, so there is nothing to write, rotate, or leak.
#
# ── WHO SEES IT ──────────────────────────────────────────────────────────────
# It emits through BOTH channels. `systemMessage` is what the PERSON sees.
# `additionalContext` is what the MODEL sees, so the agent can answer "how do I
# open the dashboard?". hooks/_advise.sh records the measured reason for using
# both: stderr at exit 0 reaches the terminal and not the model, and an unlabelled
# advisory is discounted by the model as possible injection — hence the
# self-identifying prefix on the model-facing copy.
# HONEST LIMIT: whether the terminal RENDERS `systemMessage` is not machine-
# observable from a headless run. That residue is checked by eye, once.
#
# ── ONE SCRIPT, TWO EDITIONS ─────────────────────────────────────────────────
# The full plugin ships bin/rc, so the prompt can name the local launcher and the
# autostart knob. The Anthropic-directory edition deliberately ships no bin/ and
# no 11 MB dashboard.html (the directory blocks any file over 5 MiB); there
# `/dashboard` opens the hosted page and the paste-back save flow instead. The
# wording is therefore chosen by whether bin/rc sits next to this script — a file
# test, not a build-time transform, so the same unmodified file serves both.
#
# ── NO-EGRESS (Gate 19's rule) ───────────────────────────────────────────────
# Every emitted byte is a fixed string written in this file. Nothing from the
# payload, the environment, the project, or the filesystem is echoed back.
#
# FAIL-SAFE: every error path exits 0. A SessionStart hook cannot block a session
# and must never be the reason one fails to start.
#
# Escape hatch: RC_DASHBOARD_PROMPT=off in the environment silences it.
#
# Portability: bash 3.2 (no declare -A / mapfile / ${x^^} / globstar), no GNU
# timeout, no grep -P, no sed -i, and no python3/jq — the JSON is hand-built from
# fixed strings that contain no quote or backslash.
#
# Why this file is in scripts/ and not hooks/: same packaging exception as
# scripts/ask-on-ambiguity.sh (the tribunal denies chmod on a NEW file under the
# plugin's hook directory; invoking through `bash` sidesteps the executable bit).

# Deliberately NOT `set -e`: a missing file is the normal path here.
set -u

# Belt-and-suspenders: whatever happens below, this hook exits 0.
trap 'exit 0' EXIT

[ "${RC_DASHBOARD_PROMPT:-}" = "off" ] && exit 0

project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -d "$project_dir" ] || exit 0

# Configured => silent. This single test is the entire gate.
[ -f "$project_dir/.ravenclaude/comfort-posture.yaml" ] && exit 0

here="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)" || here="."

if [ -f "$here/../bin/rc" ]; then
  user_msg="RavenClaude: no comfort posture is set up for this project yet. Run /dashboard (or rc dashboard in any terminal) to open the point-and-click dashboard. To start it automatically each session, set dashboard_autostart: serve in .ravenclaude/comfort-posture.yaml. This notice stops once that file exists."
  model_msg="[RavenClaude notice - emitted locally by a repo hook, not by the user and not by the tool] This project has no .ravenclaude/comfort-posture.yaml. If the user asks how to open the RavenClaude dashboard: run /dashboard in Claude Code, or rc dashboard in any terminal. Setting dashboard_autostart: serve in that file makes it start automatically. Do not run it unprompted."
else
  user_msg="RavenClaude: no comfort posture is set up for this project yet. Run /dashboard to open the posture editor, compose your settings there, paste the result back here and say: save my posture. This notice stops once .ravenclaude/comfort-posture.yaml exists."
  model_msg="[RavenClaude notice - emitted locally by a repo hook, not by the user and not by the tool] This project has no .ravenclaude/comfort-posture.yaml. If the user asks how to set up RavenClaude posture: they run /dashboard, compose settings in the page, and paste the result back; then save it as .ravenclaude/comfort-posture.yaml. Do not do this unprompted."
fi

printf '{"systemMessage":"%s","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$user_msg" "$model_msg" 2>/dev/null || true
exit 0
