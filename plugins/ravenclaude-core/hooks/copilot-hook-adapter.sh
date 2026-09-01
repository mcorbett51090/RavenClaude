#!/usr/bin/env bash
# copilot-hook-adapter.sh — run a RavenClaude (Claude Code) hook under GitHub Copilot CLI.
#
# Claude Code and Copilot CLI both have lifecycle hooks with the same EVENTS
# (SessionStart, PreToolUse, PostToolUse, …) but DIFFERENT I/O envelopes:
#
#                      Claude Code                         Copilot CLI
#   PreToolUse stdin   {tool_name, tool_input:{...}, cwd}  {toolName, toolArgs:"<json string>", cwd}
#   PreToolUse stdout  {hookSpecificOutput:{permission     {permissionDecision, permissionDecisionReason}
#                        Decision, permissionDecisionReason, (top-level — no hookSpecificOutput wrapper)
#                        updatedInput}}  OR  exit 2 = block
#   SessionStart out   {hookSpecificOutput:{additionalContext}}  plain stdout is added to context
#
# This adapter translates Copilot's envelope <-> the Claude envelope so the EXISTING
# hook scripts (thing-orchestrator.sh, guard-destructive.sh, enforce-layout.sh,
# capability-orientation.sh) run unmodified under Copilot. The generated Copilot
# hooks.json invokes hooks through this adapter.
#
# Usage (from a Copilot hooks.json `bash` entry):
#   copilot-hook-adapter.sh <mode> <real-hook> [real-hook-args...]
#     mode = bash-pretool | file-pretool | sessionstart | posttool | stop |
#            userpromptsubmit | precompact
#
# Fail-open is Copilot's default on hook error; for the PreToolUse command hooks
# we translate a Claude `exit 2` (block) into a Copilot `deny` so the block still
# holds. Always exits 0 after emitting (so a translation hiccup never wedges the
# tool); the decision is carried in the emitted JSON, not the exit code.
#
# VERIFY-IN-COPILOT (could not be tested without a live Copilot CLI):
#   - the exact SessionStart context-injection shape (we emit BOTH a structured
#     {additionalContext} and the plain banner text, which covers both documented
#     behaviors);
#   - the "modify tool call" (updatedInput) shape — we pass the revised command
#     through as `updatedInput` best-effort and fall back to surfacing it in the
#     reason if Copilot ignores it.

set -uo pipefail

# Source the shared scrub helper (fail-safe: if absent, define a no-op passthrough).
# Mirror the sourcing pattern used by _emit-event.sh:45-51.
_adapter_scrub_helper="$(dirname "${BASH_SOURCE[0]:-$0}")/_scrub.sh"
if [ -f "$_adapter_scrub_helper" ]; then
  # shellcheck source=/dev/null
  . "$_adapter_scrub_helper" 2>/dev/null || true
fi
command -v _scrub_reason >/dev/null 2>&1 || _scrub_reason() { printf '%s' "${1:-}"; }

mode="${1:-}"; real="${2:-}"
shift 2 2>/dev/null || true
[ -z "$mode" ] || [ -z "$real" ] && exit 0          # misconfigured -> no-op (fail open)
command -v jq >/dev/null 2>&1 || exit 0
[ -f "$real" ] || exit 0

payload=""
[ ! -t 0 ] && payload="$(cat)"

cw="$(printf '%s' "$payload" | jq -r '.cwd // .workspaceRoot // empty' 2>/dev/null)"
[ -z "$cw" ] && cw="$PWD"
sid="$(printf '%s' "$payload" | jq -r '.sessionId // .session_id // empty' 2>/dev/null)"
# (b) Export so _emit_hook_event in spawned hooks writes to runs/<real-sid>/ not runs/unknown/.
[ -n "$sid" ] && export CLAUDE_SESSION_ID="$sid"

case "$mode" in
  bash-pretool)
    # Copilot toolArgs is a JSON STRING; parse it, then re-shape to Claude stdin.
    #
    # TOOL-NAME NORMALISATION (added 2026-07-28 — this was a silent P0).
    # The envelope was translated but the tool-name VALUE was passed through
    # verbatim, and Copilot's vocabulary is not Claude's: GitHub documents its
    # tools as lowercase `bash` / `edit` / `view`
    # (docs.github.com/en/copilot/concepts/agents/hooks, retrieved 2026-07-28:
    # "before the agent uses any tool (such as `bash`, `edit`, `view`)").
    # thing-orchestrator.sh:113-116 dispatches on a CASE-SENSITIVE
    # `Bash | Read | Write | Edit | MultiEdit | WebFetch | WebSearch | mcp__*`
    # and falls to `*) exit 0` — "no decision, proceed". So under Copilot the
    # command-review tribunal AND guard-web-access.sh were complete, silent
    # no-ops: the flagship guardrails looked wired and reviewed nothing.
    #
    # The old `// "Bash"` default was wrong in BOTH directions — an ABSENT name
    # was reviewed as Bash, while a PRESENT lowercase name was skipped. Now an
    # absent name maps to "" and is handled by the unmapped branch below.
    #
    # SOURCING, stated honestly: `bash`/`edit`/`view` are docs-verified above.
    # `create`, `str_replace`, `web_fetch`, `web_search` are NOT — GitHub's page
    # gives only that partial "such as" list, so they are mapped defensively on
    # the same lowercase convention and marked here so a future editor knows
    # which lines rest on a source and which do not.
    claude_stdin="$(printf '%s' "$payload" | jq -c \
      '(.toolName // .tool_name // "") as $raw
       | ($raw | ascii_downcase) as $lc
       | {
           bash: "Bash", shell: "Bash",
           view: "Read", read: "Read",
           create: "Write", write: "Write",
           edit: "Edit", str_replace: "Edit", multiedit: "MultiEdit",
           web_fetch: "WebFetch", webfetch: "WebFetch",
           web_search: "WebSearch", websearch: "WebSearch"
         } as $map
       | {tool_name: ($map[$lc] // $raw),
          tool_input: ((.toolArgs // "{}") | (try fromjson catch {command: .})),
          cwd: (.cwd // .workspaceRoot // "."),
          session_id: (.sessionId // .session_id // "")}' 2>/dev/null)"
    # An unmapped tool name still passes through UNCHANGED (behaviour preserved
    # for anything not in the map) but must not be silent: a name we cannot map
    # is precisely the gap that hid this P0 for so long. Record it so the blind
    # spot is visible in the event substrate instead of being invisible.
    _rawname="$(printf '%s' "$payload" | jq -r '.toolName // .tool_name // ""' 2>/dev/null)"
    _mapped="$(printf '%s' "$claude_stdin" | jq -r '.tool_name // ""' 2>/dev/null)"
    if [ -n "$_rawname" ] && [ "$_rawname" = "$_mapped" ] && ! printf '%s' "$_rawname" | grep -q '^mcp__'; then
      case "$_rawname" in
        Bash | Read | Write | Edit | MultiEdit | WebFetch | WebSearch) ;;
        *)
          printf 'RavenClaude: unmapped Copilot tool name %s — review shapes may not apply. Add it to the adapter map.\n' \
            "$_rawname" >&2
          ;;
      esac
    fi
    # (e) Signal to downstream hooks (PR B: per-seat cap raise) that we are running under Copilot.
    export THING_HOST=copilot
    # (a) Capture stderr separately so the real hook's deny reason is not swallowed.
    # Fall back to /dev/null (NOT a PID-predictable /tmp path) if mktemp fails — a
    # predictable /tmp/rc-adapter-err.$$ is a symlink-attack target on shared hosts.
    # On the /dev/null fallback the diagnostic stderr is lost (reason degrades to the
    # generic deny), but the structured deny still lands in hook-events.jsonl.
    err_file="$(mktemp 2>/dev/null || echo /dev/null)"
    out="$(printf '%s' "$claude_stdin" | THING_SEAT_ACTIVE="${THING_SEAT_ACTIVE:-}" bash "$real" "$@" 2>"$err_file")"; rc=$?
    hook_stderr="$(cat "$err_file" 2>/dev/null)"
    [ "$err_file" = /dev/null ] || rm -f "$err_file" 2>/dev/null
    if [ "$rc" -eq 2 ]; then
      # Scrub secrets first, then assemble the reason. The 512-byte cap is applied
      # to the FINAL reason (body + JSONL pointer) so the emitted field is always
      # bounded — capping just the body would let the pointer push it over.
      scrubbed_reason="$(_scrub_reason "${hook_stderr:-}")"
      reason="${scrubbed_reason:-Blocked by RavenClaude guard.}"
      # (c) Append a JSONL pointer so the user knows where to find the structured deny record.
      if [ -n "$sid" ]; then
        reason="${reason} (see .ravenclaude/runs/${sid}/hook-events.jsonl)"
      else
        reason="${reason} (see .ravenclaude/runs/*/hook-events.jsonl)"
      fi
      # Cap the FINAL reason at 512 bytes.
      if [ "${#reason}" -gt 512 ]; then
        reason="${reason:0:509}..."
      fi
      # (f) Optional diagnostic trace when RAVENCLAUDE_DIAGNOSE=1.
      if [ "${RAVENCLAUDE_DIAGNOSE:-0}" = "1" ]; then
        _diag_dir="${CLAUDE_PROJECT_DIR:-.}/.ravenclaude/runs/${sid:-unknown}"
        mkdir -p "$_diag_dir" 2>/dev/null || true
        _diag_ts="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || true)"
        jq -cn \
          --arg ts "$_diag_ts" \
          --arg tool "${mode}" \
          --argjson payload "$(printf '%s' "$payload" | jq -c '.' 2>/dev/null || echo 'null')" \
          --argjson stdin "$(printf '%s' "$claude_stdin" | jq -c '.' 2>/dev/null || echo 'null')" \
          --argjson rc "$rc" \
          --arg stderr_first256 "${hook_stderr:0:256}" \
          --arg emitted_reason "$reason" \
          '{ts:$ts,tool:$tool,inbound_copilot_payload:$payload,translated_claude_stdin:$stdin,hook_exit_code:$rc,hook_stderr_first_256_bytes:$stderr_first256,emitted_reason:$emitted_reason}' \
          >> "$_diag_dir/adapter-trace.jsonl" 2>/dev/null || true
      fi
      jq -cn --arg r "$reason" '{permissionDecision:"deny",permissionDecisionReason:$r}'
      exit 0
    fi
    # Claude verdict JSON -> Copilot top-level shape.
    dec="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.permissionDecision // empty' 2>/dev/null)"
    if [ -n "$dec" ]; then
      reason="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.permissionDecisionReason // ""' 2>/dev/null)"
      revised="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.updatedInput.command // empty' 2>/dev/null)"
      if [ -n "$revised" ]; then
        jq -cn --arg d "$dec" --arg r "$reason" --arg c "$revised" \
          '{permissionDecision:$d,permissionDecisionReason:($r + " [revised command: " + $c + "]"),updatedInput:{command:$c}}'
      else
        jq -cn --arg d "$dec" --arg r "$reason" '{permissionDecision:$d,permissionDecisionReason:$r}'
      fi
    fi
    exit 0
    ;;
  file-pretool)
    # Claude path hooks (enforce-layout) take the file path as argv, not stdin.
    fp="$(printf '%s' "$payload" | jq -r \
      '(.toolArgs // "{}") | (try fromjson catch {}) | (.file_path // .path // .filePath // empty)' 2>/dev/null)"
    [ -z "$fp" ] && exit 0
    CLAUDE_PROJECT_DIR="$cw" bash "$real" "$fp" >/dev/null 2>&1; rc=$?
    if [ "$rc" -eq 2 ]; then
      jq -cn --arg p "$fp" '{permissionDecision:"deny",permissionDecisionReason:("RavenClaude layout guard: " + $p + " is off the allow-list (.repo-layout.json).")}'
    fi
    exit 0
    ;;
  sessionstart)
    out="$(CLAUDE_PROJECT_DIR="$cw" bash "$real" "$@" 2>/dev/null)"
    ctx="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null)"
    if [ -n "$ctx" ]; then
      # Emit a structured additionalContext AND the plain text, covering both the
      # documented Copilot context-injection behaviors (structured field + stdout).
      jq -cn --arg c "$ctx" '{additionalContext:$c}'
      printf '%s\n' "$ctx"
    fi
    exit 0
    ;;
  posttool)
    # Side-effecting hooks (format-on-write, remind-tests): run, ignore output.
    fp="$(printf '%s' "$payload" | jq -r \
      '(.toolArgs // "{}") | (try fromjson catch {}) | (.file_path // .path // .filePath // empty)' 2>/dev/null)"
    CLAUDE_PROJECT_DIR="$cw" bash "$real" "$fp" >/dev/null 2>&1 || true
    exit 0
    ;;
  userpromptsubmit)
    # UserPromptSubmit hooks (stream-prompt-attribute, ask-on-ambiguity) — FAIL-OPEN,
    # never block. Reshape Copilot's userPromptSubmitted payload to the Claude stdin
    # {prompt, session_id, cwd} and run the hook.
    #
    # (P2c, claim 21) FIXED — this used to `>/dev/null 2>&1` the wrapped hook's
    # stdout unconditionally, on the theory that "the hook never alters the prompt".
    # That's true, but wrong reasoning for discarding EVERYTHING: a UserPromptSubmit
    # hook can still emit hookSpecificOutput.additionalContext (ask-on-ambiguity.sh
    # does, exactly like SessionStart hooks do) — and claim 20/21 establish that VS
    # Code natively supports additionalContext injection on UserPromptSubmit, so
    # dropping it here was OUR OWN adapter bug, not a platform limitation. Forward it
    # through, mirroring the sessionstart mode's dual-emit (a structured field AND
    # plain stdout, since the exact Copilot envelope for this event is unverified —
    # see VERIFY-IN-COPILOT at the top of this file).
    claude_stdin="$(printf '%s' "$payload" | jq -c \
      '{prompt: (.prompt // .promptText // .userPrompt // ""),
        cwd: (.cwd // .workspaceRoot // "."),
        session_id: (.sessionId // .session_id // "")}' 2>/dev/null)"
    out="$(printf '%s' "$claude_stdin" | CLAUDE_PROJECT_DIR="$cw" bash "$real" "$@" 2>/dev/null)"
    ctx="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null)"
    if [ -n "$ctx" ]; then
      jq -cn --arg c "$ctx" '{additionalContext:$c}'
      printf '%s\n' "$ctx"
    fi
    exit 0
    ;;
  stop)
    # Stop hooks (dod-gate, remind-tests). Re-shape Copilot's stop payload to the
    # Claude stdin {cwd, session_id} and translate a Claude Stop block back.
    claude_stdin="$(printf '%s' "$payload" | jq -c \
      '{cwd: (.cwd // .workspaceRoot // "."),
        session_id: (.sessionId // .session_id // "")}' 2>/dev/null)"
    out="$(printf '%s' "$claude_stdin" | CLAUDE_PROJECT_DIR="$cw" bash "$real" "$@" 2>/dev/null)"; rc=$?
    # A Claude Stop block is either {"decision":"block","reason":...} on stdout or exit 2.
    dec="$(printf '%s' "$out" | jq -r '.decision // empty' 2>/dev/null)"
    reason="$(printf '%s' "$out" | jq -r '.reason // empty' 2>/dev/null)"
    if [ "$dec" = "block" ] || [ "$rc" -eq 2 ]; then
      [ -z "$reason" ] && reason="RavenClaude definition-of-done gate: work is not yet verified done."
      # Best-effort: emit BOTH a structured decision and the plain reason, mirroring
      # the sessionstart dual-emit, since Copilot's exact stop-block shape is
      # unverified (VERIFY-IN-COPILOT). Fail-open if Copilot ignores it.
      jq -cn --arg r "$reason" '{decision:"block",reason:$r}'
      printf '%s\n' "$reason" >&2
    fi
    exit 0
    ;;
  precompact)
    # PreCompact hooks (precompact-digest.sh) — ARCHIVAL ONLY, must never block or
    # warn. Claim 20 (precompact-critical-context claims-table) proves PreCompact's
    # continue/stopReason/systemMessage are a VERIFIED NO-OP on VS Code Copilot
    # Chat — executePreCompactHook() has no consumer for any of them, and the event
    # never fires there on a manual /compact at all — so this mode deliberately
    # discards BOTH the wrapped hook's stdout and its exit code and always exits 0,
    # regardless of what the real hook does. The payload's field names
    # (transcript_path, session_id, cwd, timestamp) already match Claude Code's own
    # PreCompact schema, so it is passed straight through as stdin with no reshape.
    printf '%s' "$payload" | CLAUDE_PROJECT_DIR="$cw" bash "$real" "$@" >/dev/null 2>&1 || true
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
