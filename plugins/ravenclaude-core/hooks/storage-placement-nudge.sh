#!/usr/bin/env bash
# storage-placement-nudge.sh
# PostToolUse(Write|Edit|MultiEdit) — ADVISORY. Never blocks, always exits 0.
#
# WHAT IT IS FOR. The cross-CLI storage contract (AGENTS.md § "Where work files
# go") says working notes belong in `.ravenclaude/runs/<task-id>/` and keepable
# output in `docs/`. A file written anywhere else is not *wrong* — it is
# INVISIBLE to the next CLI, which is worse, because nothing errors and the work
# simply is not where the next tool looks.
#
# WHY ADVISORY AND NOT A DENY (owner decision 2026-07-29). A hard deny on
# scratch-looking root files would also block legitimate ones, and the failure
# mode of a false deny — the human fighting the guard — is worse than the failure
# mode of a missed nudge. The deterministic layer that DOES bind is
# `enforce-layout.sh` (the allow-list) and CI; this is the reminder for the case
# neither of those considers illegal, only unfindable.
#
# DELIBERATELY NARROW. It fires only on a scratch-NAMED file at the REPO ROOT.
# Not "any file outside the tiers" — that would fire on every legitimate edit to
# a source file and be trained away within a day. A nudge that cries wolf is a
# nudge that gets ignored, which is the exact failure this whole thread is about.
#
# Opt out per-write by including `placement-ok` anywhere in the file.
set -uo pipefail

# ── ADVISORY DELIVERY (added 2026-08-19) ────────────────────────────────────
# stderr at exit 0 is MEASURED UNDELIVERED to the model (see _advise.sh header).
# Buffer fd2 and re-emit it at exit as additionalContext, which IS delivered,
# while still printing the original UI notice. No call site below changes.
_rc_hd="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || printf '.')"
if [ -f "$_rc_hd/_advise.sh" ]; then . "$_rc_hd/_advise.sh"; rc_advise_init PostToolUse; fi

command -v jq >/dev/null 2>&1 || exit 0

payload=""
[ ! -t 0 ] && payload="$(cat 2>/dev/null || true)"
[ -z "$payload" ] && exit 0

fp="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null)"
[ -z "$fp" ] && exit 0

root="${CLAUDE_PROJECT_DIR:-$PWD}"
# Make the path relative to the project root, if it is under it.
rel="${fp#"$root"/}"
case "$rel" in
  /*) exit 0 ;;                       # outside the project entirely — not ours to judge
esac

# Already in one of the two tiers -> nothing to say.
case "$rel" in
  .ravenclaude/runs/*) exit 0 ;;
  docs/*) exit 0 ;;
esac

# Only consider files at the REPO ROOT (no directory component).
case "$rel" in
  */*) exit 0 ;;
esac

# ...and only ones NAMED like scratch output. Anchored, lowercase compare.
base="$(printf '%s' "$rel" | tr '[:upper:]' '[:lower:]')"
case "$base" in
  notes.md | notes.txt | scratch.md | scratch.txt | tmp.md | temp.md \
  | output.md | output.txt | output.json | results.md | results.json \
  | plan.md | summary.md | draft.md | todo.md | wip.md | log.txt | log.md \
  | findings.md | analysis.md | report.md) ;;
  *) exit 0 ;;
esac

# Per-write opt-out, mirroring claim-grounding-lint.sh's escape hatch.
if [ -f "$fp" ] && grep -q 'placement-ok' "$fp" 2>/dev/null; then
  exit 0
fi

cat >&2 <<EOF

RavenClaude — placement note (advisory, nothing was blocked):
  You wrote '$rel' at the repository root.

  Another CLI will NOT find it there. Per AGENTS.md § "Where work files go":
    working notes  -> .ravenclaude/runs/<task-id>/   (local, gitignored)
    keepable output -> docs/plans|decisions|research/ (committed)

  Start one with:  bin/rc artifacts new <task-id>
  See what exists: bin/rc artifacts list
  Intentional? Put 'placement-ok' in the file to silence this.
EOF

exit 0
