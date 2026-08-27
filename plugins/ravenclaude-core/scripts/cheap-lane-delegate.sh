#!/usr/bin/env bash
# cheap-lane-delegate.sh — agent-agnostic dispatcher over the per-agent delegate
# scripts (grok-delegate.sh, copilot-delegate.sh, …). Added 2026-08-26 so the
# cheap lane is a matrix of {coding agent} x {model} x {effort level} x
# {turn/timeout budget}, not a single vendor with everything else hardcoded to it.
#
# Usage:
#   cheap-lane-delegate.sh --agent grok|copilot [any flag the target script takes]
#
# All flags after --agent (and --agent itself, stripped) pass through VERBATIM to
# the selected <agent>-delegate.sh — this script owns only agent SELECTION, never
# the per-agent flag shape (those differ: Grok's --sandbox/--max-turns have no
# Copilot analogue; Copilot's --deny-tool has no Grok analogue — see each
# script's own header for what is and is not verified for that agent).
#
# Exit codes: passes through the selected script's exit code unchanged (0 ok,
# 2 CLI absent / bad args, 4 the agent failed, 7 recursion guard, 8 secret
# refused pre-egress, 9 worktree provisioning failed) plus:
#   2  --agent missing, or names an agent with no delegate script
#
# codex is DELIBERATELY NOT a case here. The Codex CLI was not installed on the
# host this dispatcher was built and tested against (2026-08-26; confirmed
# absent from PATH and every common install location — a bash-not-found result
# alone did not license this conclusion, so the negative was corroborated
# before being trusted), so its one-shot invocation syntax could not be
# live-verified the way Grok's and Copilot's were. This repo already has real,
# `[docs-verified]` facts about Codex's sandbox_mode/approval_policy
# (CLAUDE.md's "OpenAI Codex CLI is a supported host" milestone) — what is
# missing is specifically the non-interactive PROMPT invocation this script
# would need to shell out to. Add `codex-delegate.sh` + a `codex` case here
# once that is verified against a real install, following the same
# verify-before-ship discipline as the other two scripts.

set -uo pipefail

_self="$(basename "$0")"
_dir="$(cd "$(dirname "$0")" && pwd)"

agent=""
args=()
while [ $# -gt 0 ]; do
  case "$1" in
    --agent) agent="${2:-}"; shift 2 ;;
    *) args+=("$1"); shift ;;
  esac
done

case "$agent" in
  grok)    exec bash "$_dir/grok-delegate.sh" "${args[@]}" ;;
  copilot) exec bash "$_dir/copilot-delegate.sh" "${args[@]}" ;;
  "")
    echo "$_self: --agent is required (grok|copilot)" >&2
    exit 2
    ;;
  *)
    echo "$_self: unknown --agent '$agent' (supported: grok, copilot — codex is a deferred, documented gap; see this script's header)" >&2
    exit 2
    ;;
esac
