#!/usr/bin/env bash
# worktree-swarm.sh — fan out N isolated worktrees for parallel agent work.
#
# Thin orchestration layer over worktree-new.sh. Given several task slugs, it
# creates one worktree per slug (each on its own `agent/<slug>` branch under
# .claude/worktrees/<slug>) and prints a ready-to-paste `claude --bg` dispatch
# line for each — so launching a parallel background-agent swarm is one command.
# It builds on the existing helpers rather than reimplementing them:
#   - creation  -> worktree-new.sh   (slug shape + collision checks live there)
#   - status    -> worktree-clean.sh --status
#   - cleanup   -> worktree-clean.sh --all  (clean trees only) / <slug> [--force]
#
# Usage:
#   scripts/worktree-swarm.sh <slug> [<slug> ...]
#       Create a worktree per slug and emit a dispatch line for each.
#   scripts/worktree-swarm.sh --task "<prompt>" <slug> [<slug> ...]
#       Embed <prompt> in each emitted dispatch line (otherwise a TODO placeholder).
#   scripts/worktree-swarm.sh --status
#       List all worktrees with clean/dirty state (delegates to worktree-clean.sh).
#   scripts/worktree-swarm.sh --clean-all
#       Remove every clean worktree (delegates to worktree-clean.sh --all).
#
# Each slug must match [A-Za-z0-9._-]+ (enforced downstream by worktree-new.sh).
#
# Note: `claude --bg` is the Claude Code CLI's background-session flag; this
# script does not launch the agents for you (it can't see your session), it
# prepares the isolated trees and prints the exact commands to paste.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel)"

usage() {
  cat <<EOF >&2
usage: $0 <slug> [<slug> ...]
       $0 --task "<prompt>" <slug> [<slug> ...]
       $0 --status
       $0 --clean-all
EOF
  exit 2
}

TASK_PROMPT=""
SLUGS=()

# --- parse args -------------------------------------------------------------
while [ $# -gt 0 ]; do
  case "$1" in
    --status)
      exec "$SCRIPT_DIR/worktree-clean.sh" --status
      ;;
    --clean-all)
      exec "$SCRIPT_DIR/worktree-clean.sh" --all
      ;;
    --task)
      [ $# -ge 2 ] || usage
      TASK_PROMPT="$2"
      shift 2
      ;;
    --help | -h | "")
      usage
      ;;
    -*)
      printf 'error: unknown flag: %s\n' "$1" >&2
      usage
      ;;
    *)
      SLUGS+=("$1")
      shift
      ;;
  esac
done

[ "${#SLUGS[@]}" -gt 0 ] || usage

# --- create worktrees -------------------------------------------------------
CREATED=()
for slug in "${SLUGS[@]}"; do
  printf '\n--- creating worktree: %s ---\n' "$slug"
  if "$SCRIPT_DIR/worktree-new.sh" "$slug"; then
    CREATED+=("$slug")
  else
    printf 'warning: skipped %s (worktree-new.sh failed — already exists?)\n' "$slug" >&2
  fi
done

[ "${#CREATED[@]}" -gt 0 ] || {
  printf '\nno worktrees created; nothing to dispatch.\n' >&2
  exit 1
}

# --- emit dispatch lines ----------------------------------------------------
prompt="${TASK_PROMPT:-<your task prompt here>}"
printf '\n== Swarm ready: %d worktree(s) ==\n' "${#CREATED[@]}"
printf 'Paste each line to launch an isolated background agent:\n\n'
for slug in "${CREATED[@]}"; do
  wt="$REPO_ROOT/.claude/worktrees/$slug"
  printf '  (cd %q && claude --bg --name %q %q)\n' "$wt" "$slug" "$prompt"
done

cat <<EOF

When the swarm is done:
  scripts/worktree-swarm.sh --status        # see which trees have changes
  scripts/worktree-clean.sh <slug>          # remove one (refuses if dirty)
  scripts/worktree-swarm.sh --clean-all     # remove all clean trees
EOF
