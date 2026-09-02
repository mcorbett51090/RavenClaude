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
# CONFIRMED 2026-09-01 (docs.github.com/en/copilot/reference/hooks-reference, cross-corroborated by
# 4 more official docs.github.com pages + github/copilot-cli issues #2013/#3349 — see
# docs/research/2026-09-01-copilot-chat-grandmaster/synthesis.md):
#   - the PreToolUse response envelope really is top-level {permissionDecision,
#     permissionDecisionReason} with NO hookSpecificOutput wrapper (a verbatim-quote search of the
#     reference page found zero occurrences, and copilot-cli#2013 confirms a Claude-shaped wrapped
#     payload is silently ignored);
#   - toolArgs really is a stringified JSON string (not a nested object) — 4 independent sources
#     plus copilot-cli#3349;
#   - SessionStart injects context via the additionalContext JSON key (the structured half of the
#     dual-emit below is load-bearing); plain unstructured stdout is preserved in the hook's output
#     stream but is NOT itself parsed into model context, so the plain-text half is likely inert for
#     injection — harmless to keep, not worth removing;
#   - PreCompact is notification-only (cannot block/modify compaction), independently confirming
#     this file's own precompact-mode reasoning below;
#   - the Stop/agentStop block shape ({decision:"block", reason}) is confirmed, and `reason` becomes
#     the PROMPT for the forced next turn, not just a rejection message.
#
# STILL VERIFY-IN-COPILOT (not settled by the 2026-09-01 research — needs a live Copilot session):
#   - the exact "modify tool call" (updatedInput) wire shape — passed through best-effort, falling
#     back to surfacing it in the reason if Copilot ignores it;
#   - whether Copilot's PascalCase / "Claude matcher semantics" mode (>=1.0.62, see the TOOL-NAME
#     NORMALISATION comment below) does its OWN native tool-name translation before evaluating a
#     projected matcher, and if so, whether that translation covers `powershell` the same way it
#     must already cover `bash`/`edit`/`view` for the existing wiring to work at all. Unverified
#     either way — this determines whether a `powershell` call reaches THIS adapter on modern
#     Copilot in the first place. See scripts/generate-copilot-hooks.py's "MATCHERS ARE PROJECTED"
#     section and .ravenclaude/runs/forge/copilot-adapter-tool-names/claims-table.md.

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
    # TOOL-NAME NORMALISATION (added 2026-07-28 — this was a silent P0; extended 2026-09-01).
    # The envelope was translated but the tool-name VALUE was passed through
    # verbatim, and Copilot's vocabulary is not Claude's: GitHub documents its
    # tools as lowercase `bash` / `edit` / `view`
    # (docs.github.com/en/copilot/concepts/agents/hooks, retrieved 2026-07-28:
    # "before the agent uses any tool (such as `bash`, `edit`, `view`)").
    # thing-orchestrator.sh:126 dispatches on a CASE-SENSITIVE
    # `Bash | Read | Write | Edit | MultiEdit | WebFetch | WebSearch | mcp__*`
    # and falls to `*) exit 0` — "no decision, proceed". So under Copilot the
    # command-review tribunal AND guard-web-access.sh were complete, silent
    # no-ops: the flagship guardrails looked wired and reviewed nothing.
    #
    # The old `// "Bash"` default was wrong in BOTH directions — an ABSENT name
    # was reviewed as Bash, while a PRESENT lowercase name was skipped. Now an
    # absent name maps to "" and is handled by the unmapped branch below.
    #
    # SOURCING (2026-09-01 update): the FULL authoritative Copilot CLI tool list is now confirmed —
    # docs.github.com/en/copilot/reference/hooks-reference, cross-corroborated (see
    # docs/research/2026-09-01-copilot-chat-grandmaster/synthesis.md §3.4):
    #   ask_user, bash, create, edit, glob, grep, powershell, task, view, web_fetch, web_search.
    # `create`, `web_fetch`, `web_search` (previously marked defensive/unconfirmed) are now
    # CONFIRMED real. `str_replace` (mapped below to Edit) is NOT in the authoritative list — kept
    # as a harmless dead/speculative alias; costs nothing, never fires against real Copilot output.
    #
    # `powershell` -> Bash closes a REAL gap: it is Copilot's Windows command-execution tool, the
    # direct analogue of bash — an unmapped `powershell` command silently bypassed the tribunal
    # exactly like the original bash/edit/view P0. ⛔ RESIDUAL RISK, security-reviewed 2026-09-01
    # (verdict: CLEAR-WITH-CHANGES, applied below): (1) whether a `powershell` call reaches this
    # adapter AT ALL on Copilot >=1.0.62 is unverified — see the VERIFY-IN-COPILOT block above; (2)
    # the tribunal's Bash-shaped catalog triggers (knowledge/concerns-catalog.md) are POSIX-only by
    # construction and were measured (thing-decision.py classify, this session) to NOT trip on
    # PowerShell-native dangerous forms (`iwr|iex`, `-EncodedCommand`, `Invoke-Expression`,
    # `DownloadString`) — coverage is gained for shell-portable text (git/npm/gh/curl-literal
    # commands) and the category-independent hard-rule + self-disable floor, not for
    # PowerShell-specific attack syntax. A catalog extension for PowerShell-shaped triggers is
    # tracked follow-up work, not done here. (3) the command-text JSON key Copilot's `powershell`
    # tool actually uses is unverified (assumed `.command` like bash) — defended below by
    # coalescing `.command // .script // .commandLine`, scoped to Bash-mapped calls only so
    # non-Bash tool_input shapes are untouched.
    #
    # `glob` / `grep` / `task` are mapped for NAMING ACCURACY ONLY — hygiene, not a security fix.
    # thing-orchestrator.sh's dispatch case (line 126) does not include Glob/Grep/Task either, so
    # neither the Claude nor the Copilot version of these tool types is tribunal-reviewed — this is
    # PARITY, not a gap. Mapping them removes the false "unmapped tool name" warning below for tool
    # types that are correctly, deliberately unreviewed.
    #
    # `ask_user` is DELIBERATELY LEFT UNMAPPED — do not "fix" this without reading
    # scripts/generate-copilot-hooks.py's `_SKIP` entry for route-decision-review.sh first. That
    # hook (the Claude-side AskUserQuestion handler — ask_user's semantic equivalent) is
    # EXPLICITLY, deliberately never wired for Copilot: below Copilot 1.0.62 an unhonored matcher
    # makes a hook fire for EVERY tool call, and route-decision-review.sh expects an
    # AskUserQuestion-shaped payload — wiring it "would be a liability on exactly the versions
    # where the matcher cannot protect it" (generate-copilot-hooks.py comment, verbatim). Mapping
    # ask_user -> "AskUserQuestion" here would be purely cosmetic (that hook is never invoked under
    # Copilot regardless of tool_name) and would misrepresent a security decision the maintainers
    # already made on purpose. Full reasoning chain:
    # .ravenclaude/runs/forge/copilot-adapter-tool-names/claims-table.md.
    claude_stdin="$(printf '%s' "$payload" | jq -c \
      '(.toolName // .tool_name // "") as $raw
       | ($raw | ascii_downcase) as $lc
       | {
           bash: "Bash", shell: "Bash", powershell: "Bash",
           view: "Read", read: "Read",
           create: "Write", write: "Write",
           edit: "Edit", str_replace: "Edit", multiedit: "MultiEdit",
           web_fetch: "WebFetch", webfetch: "WebFetch",
           web_search: "WebSearch", websearch: "WebSearch",
           glob: "Glob", grep: "Grep", task: "Task"
         } as $map
       | ($map[$lc] // $raw) as $tn
       | ((.toolArgs // "{}") | (try fromjson catch {command: .})) as $ti
       | {tool_name: $tn,
          tool_input: (if $tn == "Bash" then ($ti + {command: ($ti.command // $ti.script // $ti.commandLine // "")}) else $ti end),
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
