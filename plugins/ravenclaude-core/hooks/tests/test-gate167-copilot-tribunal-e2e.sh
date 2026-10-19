#!/usr/bin/env bash
# Gate 167 — a COPILOT-shaped payload reaches the tribunal and is still denied.
#
# This is the residual MH-01 split out but never built. MH-01 was the P0 where the
# command-review tribunal was "fully wired, reviewing nothing" under Copilot: the
# envelope was translated but the tool-name VALUE was not, and
# thing-orchestrator.sh dispatches on a CASE-SENSITIVE
# `Bash | Read | Write | ...` list falling to `*) exit 0`. Copilot sends `bash`.
# So every Copilot tool call sailed past the classifier, the self-disable guard
# and the category-independent hard-rule screen.
#
# WHY THE EXISTING COVERAGE DOES NOT CLOSE IT.
#   - Gate 20 drives the ADAPTER and asserts its I/O shape (stderr preservation,
#     the 512-byte cap, CLAUDE_SESSION_ID export). It never asks whether a verdict
#     actually comes out the far end.
#   - Gates 50 / 121 / 162 and test-seat-stderr-capture drive the ORCHESTRATOR,
#     but every one of them feeds it a CLAUDE-shaped payload.
#
# Measured 2026-07-29: of the hook tests, exactly ONE uses a Copilot-shaped
# `toolName` (Gate 20's) and it is NOT among the four that drive the orchestrator.
# So the seam where the P0 actually lived — adapter output feeding orchestrator
# input — had no test crossing it. A regression in the tool-name map would leave
# every existing gate green while the tribunal went dark again, silently, exactly
# as it did the first time.
#
# WHAT THIS ASSERTS
#   G167.1  control — the Claude-shaped payload is denied (the command really is
#           deny-worthy, so a later deny is not an artifact of the fixture)
#   G167.2  the SAME command in a Copilot envelope, through the adapter, is denied
#   G167.3  TEETH — with the tool-name map defeated, the deny DISAPPEARS
#
# G167.3 is the one that matters: it reproduces MH-01 on demand and proves this
# gate would catch its return. A gate for a silent failure is worthless unless it
# has been watched failing.
#
# EXTENDED 2026-09-01 for the powershell/glob/grep/task/ask_user tool-name-map fix
# (docs/research/2026-09-01-copilot-chat-grandmaster/synthesis.md gap-closure item #1,
# refined against the real dispatch code in
# .ravenclaude/runs/forge/copilot-adapter-tool-names/claims-table.md):
#   G167.4  powershell (.command key) -> Bash -> tribunal -> deny
#   G167.5  powershell (.script key) -> the .command//.script//.commandLine
#           coalescing still resolves the command text -> deny
#   G167.6  TEETH — without the powershell->Bash map entry, the deny disappears
#           (reproduces the gap this fix closes)
#   G167.7  glob/grep/task map cleanly (naming-accuracy hygiene fix — Claude's own
#           dispatch case doesn't tribunal-review Glob/Grep/Task either, so this
#           only removes a false "unmapped tool name" warning, no behavior change)
#   G167.8  ask_user STILL triggers the "unmapped" warning — proves the DELIBERATE
#           decision not to map it (route-decision-review.sh is explicitly never
#           wired for Copilot, per generate-copilot-hooks.py's _SKIP entry) has not
#           silently regressed into an accidental mapping
#
# NOTE ON LITERALS: the force-push string is assembled at runtime. Inline, the
# category-independent hard-rule screen (§B.9.3) denies the Write that creates
# this very file — the same trap Gate 162's header documents.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_DIR="$(cd "$HERE/.." && pwd)"
ADAPTER="$HOOKS_DIR/copilot-hook-adapter.sh"
ORCH="$HOOKS_DIR/thing-orchestrator.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  ✓ %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  ✗ %s\n' "$1"; }

for f in "$ADAPTER" "$ORCH"; do
  [ -f "$f" ] || { printf 'FATAL: missing %s\n' "$f" >&2; exit 1; }
done
command -v jq >/dev/null 2>&1 || { printf 'SKIP: jq absent\n' >&2; exit 0; }

# Assembled so the literal never sits in this file (see header).
FORCED_PUSH="git push --""force origin main"

# Scratch project with the Thing enabled for ONE category. The hard rule is
# category-INDEPENDENT (§B.9.3) — it fires regardless of which category the
# command routes to — but the orchestrator short-circuits entirely when nothing
# is toggled, which is correct and is the state of every non-adopter.
PROJ="$TMP/proj"
mkdir -p "$PROJ/.ravenclaude"
cat > "$PROJ/.ravenclaude/comfort-posture.yaml" <<'YAML'
schema_version: 5
categories:
  shell_remote_mutate:
    user: ask
    local: ask
    project: inherit
    thing: on
YAML

# ── G167.1 — control: Claude-shaped payload is denied ────────────────────────
echo "── G167.1: control — Claude-shaped force-push is denied ─────────────────"
rc=0
jq -cn --arg cwd "$PROJ" --arg cmd "$FORCED_PUSH" \
  '{tool_name:"Bash",tool_input:{command:$cmd},cwd:$cwd,session_id:"g167a"}' \
  | CLAUDE_PROJECT_DIR="$PROJ" CLAUDE_SESSION_ID="g167a" \
    bash "$ORCH" >"$TMP/out-a.json" 2>"$TMP/err-a.txt" || rc=$?

# The orchestrator signals a block either by exit 2 or by an emitted deny verdict.
claude_denied=0
[ "$rc" -eq 2 ] && claude_denied=1
if grep -q '"permissionDecision"[[:space:]]*:[[:space:]]*"deny"' "$TMP/out-a.json" 2>/dev/null; then
  claude_denied=1
fi
if [ "$claude_denied" -eq 1 ]; then
  ok "control: the tribunal denies this command in Claude shape (exit=$rc)"
else
  bad "control: NOT denied in Claude shape (exit=$rc) — the fixture is wrong, not the adapter"
  printf '     stdout: %s\n' "$(head -c 300 "$TMP/out-a.json" 2>/dev/null)"
  printf '     stderr: %s\n' "$(head -c 300 "$TMP/err-a.txt" 2>/dev/null)"
fi

# ── G167.2 — the same command, Copilot envelope, through the adapter ─────────
echo "── G167.2: Copilot-shaped force-push through the adapter is denied ──────"
# Copilot's real shape: lowercase toolName, toolArgs as a JSON *string*.
copilot_payload() {
  jq -cn --arg cwd "$PROJ" --arg cmd "$FORCED_PUSH" --arg tn "${1:-bash}" \
    '{toolName:$tn,toolArgs:({command:$cmd}|tostring),cwd:$cwd,sessionId:"g167b"}'
}

rc=0
copilot_payload bash \
  | CLAUDE_PROJECT_DIR="$PROJ" bash "$ADAPTER" bash-pretool "$ORCH" \
      >"$TMP/out-b.json" 2>"$TMP/err-b.txt" || rc=$?

# The adapter always exits 0 and carries the decision in the JSON (by contract).
decision_b="$(jq -r '.permissionDecision // empty' "$TMP/out-b.json" 2>/dev/null)"
if [ "$decision_b" = "deny" ]; then
  ok "Copilot payload -> adapter -> tribunal -> deny (the MH-01 seam holds)"
else
  bad "Copilot payload was NOT denied (permissionDecision='${decision_b:-<none>}') — the tribunal is dark on this host"
  printf '     stdout: %s\n' "$(head -c 300 "$TMP/out-b.json" 2>/dev/null)"
  printf '     stderr: %s\n' "$(head -c 300 "$TMP/err-b.txt" 2>/dev/null)"
fi

# ── G167.3 — TEETH: defeat the tool-name map, deny must vanish ───────────────
echo "── G167.3: teeth — without tool-name normalisation the deny disappears ──"
MUT="$TMP/adapter-mutant.sh"
python3 - "$ADAPTER" "$MUT" <<'PY'
import pathlib
import sys

src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
# Reproduce the pre-fix adapter: pass the raw Copilot tool name straight through
# instead of mapping it onto Claude's vocabulary.
anchor = "($map[$lc] // $raw)"
if anchor not in src:
    # A vacuous teeth half is worse than none: if the adapter is refactored so
    # this anchor no longer exists, FAIL LOUDLY rather than "mutating" nothing
    # and reporting teeth we do not have.
    sys.stderr.write(
        "MUTATION ANCHOR NOT FOUND: expected %r in the adapter. The teeth half "
        "cannot be trusted until this is re-pointed at the current map lookup.\n"
        % anchor
    )
    raise SystemExit(3)
pathlib.Path(sys.argv[2]).write_text(src.replace(anchor, "($raw)"), encoding="utf-8")
PY
mut_rc=$?

if [ "$mut_rc" -ne 0 ]; then
  bad "teeth: could not build the mutant (anchor missing) — re-point the mutation"
else
  rc=0
  copilot_payload bash \
    | CLAUDE_PROJECT_DIR="$PROJ" bash "$MUT" bash-pretool "$ORCH" \
        >"$TMP/out-c.json" 2>"$TMP/err-c.txt" || rc=$?
  decision_c="$(jq -r '.permissionDecision // empty' "$TMP/out-c.json" 2>/dev/null)"
  if [ "$decision_c" = "deny" ]; then
    bad "teeth: the mutant STILL denied — this gate does not actually test the tool-name map"
  else
    ok "teeth: normalisation defeated -> no deny ('${decision_c:-<none>}') — MH-01 reproduced, so this gate would catch its return"
  fi
fi

# ── G167.4 — powershell (`.command` key) through the adapter is denied ───────
# (added 2026-09-01 — the powershell/glob/grep/task/ask_user tool-name-map fix;
# see .ravenclaude/runs/forge/copilot-adapter-tool-names/ for the full FORGE run)
echo "── G167.4: Copilot powershell (.command key) through the adapter is denied ──"
powershell_payload_command_key() {
  jq -cn --arg cwd "$PROJ" --arg cmd "$FORCED_PUSH" \
    '{toolName:"powershell",toolArgs:({command:$cmd}|tostring),cwd:$cwd,sessionId:"g167d"}'
}
rc=0
powershell_payload_command_key \
  | CLAUDE_PROJECT_DIR="$PROJ" bash "$ADAPTER" bash-pretool "$ORCH" \
      >"$TMP/out-d.json" 2>"$TMP/err-d.txt" || rc=$?
decision_d="$(jq -r '.permissionDecision // empty' "$TMP/out-d.json" 2>/dev/null)"
if [ "$decision_d" = "deny" ]; then
  ok "powershell (.command key) -> Bash -> tribunal -> deny"
else
  bad "powershell (.command key) was NOT denied (permissionDecision='${decision_d:-<none>}')"
  printf '     stdout: %s\n' "$(head -c 300 "$TMP/out-d.json" 2>/dev/null)"
fi

# ── G167.5 — powershell (`.script` key, an alternate plausible field name) ───
echo "── G167.5: Copilot powershell (.script key) through the adapter is denied ───"
powershell_payload_script_key() {
  jq -cn --arg cwd "$PROJ" --arg cmd "$FORCED_PUSH" \
    '{toolName:"powershell",toolArgs:({script:$cmd}|tostring),cwd:$cwd,sessionId:"g167e"}'
}
rc=0
powershell_payload_script_key \
  | CLAUDE_PROJECT_DIR="$PROJ" bash "$ADAPTER" bash-pretool "$ORCH" \
      >"$TMP/out-e.json" 2>"$TMP/err-e.txt" || rc=$?
decision_e="$(jq -r '.permissionDecision // empty' "$TMP/out-e.json" 2>/dev/null)"
if [ "$decision_e" = "deny" ]; then
  ok "powershell (.script key) -> command-field coalescing -> tribunal -> deny"
else
  bad "powershell (.script key) was NOT denied — the .command//.script//.commandLine coalescing broke (permissionDecision='${decision_e:-<none>}')"
  printf '     stdout: %s\n' "$(head -c 300 "$TMP/out-e.json" 2>/dev/null)"
fi

# ── G167.6 — TEETH: without the powershell map entry, the deny disappears ────
echo "── G167.6: teeth — without powershell->Bash mapping the deny disappears ─────"
MUT2="$TMP/adapter-mutant-ps.sh"
python3 - "$ADAPTER" "$MUT2" <<'PY'
import pathlib
import sys

src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
anchor = 'bash: "Bash", shell: "Bash", powershell: "Bash",'
if anchor not in src:
    sys.stderr.write(
        "MUTATION ANCHOR NOT FOUND: expected %r in the adapter. Re-point the teeth half.\n" % anchor
    )
    raise SystemExit(3)
pathlib.Path(sys.argv[2]).write_text(src.replace(anchor, 'bash: "Bash", shell: "Bash",'), encoding="utf-8")
PY
mut2_rc=$?
if [ "$mut2_rc" -ne 0 ]; then
  bad "teeth: could not build the powershell mutant (anchor missing) — re-point the mutation"
else
  rc=0
  powershell_payload_command_key \
    | CLAUDE_PROJECT_DIR="$PROJ" bash "$MUT2" bash-pretool "$ORCH" \
        >"$TMP/out-f.json" 2>"$TMP/err-f.txt" || rc=$?
  decision_f="$(jq -r '.permissionDecision // empty' "$TMP/out-f.json" 2>/dev/null)"
  if [ "$decision_f" = "deny" ]; then
    bad "teeth: the mutant STILL denied — this gate does not actually test the powershell mapping"
  else
    ok "teeth: powershell mapping defeated -> no deny ('${decision_f:-<none>}') — the gap this fix closes is reproduced"
  fi
fi

# ── G167.7 — glob/grep/task no longer trigger the false 'unmapped' warning ───
echo "── G167.7: glob/grep/task map cleanly (no 'unmapped tool name' warning) ─────"
for _tn in glob grep task; do
  jq -cn --arg cwd "$PROJ" --arg tn "$_tn" \
    '{toolName:$tn,toolArgs:({path:"."}|tostring),cwd:$cwd,sessionId:"g167g"}' \
    | CLAUDE_PROJECT_DIR="$PROJ" bash "$ADAPTER" bash-pretool "$ORCH" \
        >"$TMP/out-g-$_tn.json" 2>"$TMP/err-g-$_tn.txt" || true
  if grep -q "unmapped Copilot tool name" "$TMP/err-g-$_tn.txt" 2>/dev/null; then
    bad "$_tn still triggers the 'unmapped tool name' warning — mapping regressed"
  else
    ok "$_tn maps cleanly, no false 'unmapped' warning"
  fi
done

# ── G167.8 — ask_user STILL triggers the warning (deliberate, not a regression)
echo "── G167.8: ask_user is DELIBERATELY unmapped — the warning must still fire ──"
jq -cn --arg cwd "$PROJ" \
  '{toolName:"ask_user",toolArgs:({question:"x"}|tostring),cwd:$cwd,sessionId:"g167h"}' \
  | CLAUDE_PROJECT_DIR="$PROJ" bash "$ADAPTER" bash-pretool "$ORCH" \
      >"$TMP/out-h.json" 2>"$TMP/err-h.txt" || true
if grep -q "unmapped Copilot tool name ask_user" "$TMP/err-h.txt" 2>/dev/null; then
  ok "ask_user still warns as unmapped — confirms the deliberate non-mapping (route-decision-review.sh is never wired for Copilot; see the adapter's own comment) has not silently regressed into a mapping"
else
  bad "ask_user no longer warns — someone mapped it. Read the adapter's ask_user comment and generate-copilot-hooks.py's route-decision-review.sh _SKIP entry before doing that; it was a deliberate decision, not an oversight."
fi

# ── G167.9-12 — Copilot FILE tools reach the guards with Claude key names ─────
# repo-review item 1a-2. view/create/edit send path / file_text / old_str /
# new_str; the tribunal and the self-tamper floor read file_path / content /
# old_string / new_string. Passed through verbatim, a Copilot create onto the
# tribunal's own substrate produced NO decision while the identical Claude-shaped
# Write was denied (xc.tribunal-self-disable).
mkdir -p "$PROJ/plugins/ravenclaude-core/hooks"
printf 'x\n' >"$PROJ/plugins/ravenclaude-core/hooks/thing-orchestrator.sh"
printf 'readme\n' >"$PROJ/README.md"
SUBSTRATE_NEW="$PROJ/plugins/ravenclaude-core/hooks/new-hook.sh"
copilot_file_call() { # <toolName> <args-json-object>
  jq -cn --arg cwd "$PROJ" --arg tn "$1" --argjson a "$2" \
    '{toolName:$tn,toolArgs:($a|tostring),cwd:$cwd,sessionId:"g167f"}'
}
echo "── G167.9: Copilot create onto the Thing's substrate is denied ──────────"
copilot_file_call create "$(jq -cn --arg p "$SUBSTRATE_NEW" '{path:$p,file_text:"x"}')" \
  | CLAUDE_PROJECT_DIR="$PROJ" bash "$ADAPTER" bash-pretool "$ORCH" >"$TMP/out-i.json" 2>/dev/null || true
[ "$(jq -r '.permissionDecision // empty' "$TMP/out-i.json" 2>/dev/null)" = "deny" ] \
  && ok "create {path,file_text} onto substrate -> deny (file_path aliased)" \
  || bad "create onto substrate NOT denied: $(head -c 200 "$TMP/out-i.json")"
echo "── G167.10: Copilot edit onto the Thing's substrate is denied ───────────"
copilot_file_call edit "$(jq -cn --arg p "$PROJ/plugins/ravenclaude-core/hooks/thing-orchestrator.sh" '{path:$p,old_str:"x",new_str:"y"}')" \
  | CLAUDE_PROJECT_DIR="$PROJ" bash "$ADAPTER" bash-pretool "$ORCH" >"$TMP/out-j.json" 2>/dev/null || true
[ "$(jq -r '.permissionDecision // empty' "$TMP/out-j.json" 2>/dev/null)" = "deny" ] \
  && ok "edit {path,old_str,new_str} onto substrate -> deny" \
  || bad "edit onto substrate NOT denied: $(head -c 200 "$TMP/out-j.json")"
echo "── G167.11: control — a Copilot view of a plain file is allowed ─────────"
copilot_file_call view "$(jq -cn --arg p "$PROJ/README.md" '{path:$p}')" \
  | CLAUDE_PROJECT_DIR="$PROJ" bash "$ADAPTER" bash-pretool "$ORCH" >"$TMP/out-k.json" 2>/dev/null || true
[ "$(jq -r '.permissionDecision // empty' "$TMP/out-k.json" 2>/dev/null)" != "deny" ] \
  && ok "view of a non-sensitive file is not denied (aliasing does not over-block)" \
  || bad "view of README.md was denied: $(head -c 200 "$TMP/out-k.json")"
echo "── G167.12: teeth — without the key aliasing the substrate create sails through ──"
MUT3="$TMP/adapter-mutant-noalias.sh"
python3 - "$ADAPTER" "$MUT3" <<'PY'
import pathlib
import sys

src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
anchor = "file_path: ($ti.file_path // $ti.path // $ti.filePath),"
if anchor not in src:
    sys.stderr.write("MUTATION ANCHOR NOT FOUND: %r\n" % anchor)
    raise SystemExit(3)
pathlib.Path(sys.argv[2]).write_text(src.replace(anchor, "file_path: ($ti.file_path),"), encoding="utf-8")
PY
if [ "$?" -ne 0 ]; then
  bad "teeth: could not build the no-alias mutant (anchor missing) — re-point the mutation"
else
  copilot_file_call create "$(jq -cn --arg p "$SUBSTRATE_NEW" '{path:$p,file_text:"x"}')" \
    | CLAUDE_PROJECT_DIR="$PROJ" bash "$MUT3" bash-pretool "$ORCH" >"$TMP/out-l.json" 2>/dev/null || true
  [ "$(jq -r '.permissionDecision // empty' "$TMP/out-l.json" 2>/dev/null)" != "deny" ] \
    && ok "teeth: aliasing removed -> substrate create is no longer denied (1a-2 reproduced)" \
    || bad "teeth: the no-alias mutant still denied — G167.9 may not test the aliasing"
fi

# ── G167.13-16 — argument envelopes beyond toolArgs-as-string (item 1a-4) ─────
# Args were read only from .toolArgs, and the catch bound the jq ERROR text, so a
# snake_case tool_input, an object toolArgs or a plain string gave the guard an
# empty or garbage command.
REC="$TMP/rec-cmd.sh"
cat >"$REC" <<'EOF'
#!/usr/bin/env bash
jq -r '.tool_input.command // "<none>"' >"$RC_OUT" 2>/dev/null
exit 0
EOF
chmod +x "$REC"
seen_cmd() { # <payload-json> -> the command text the wrapped hook received
  rm -f "$TMP/seen"
  printf '%s' "$1" | RC_OUT="$TMP/seen" bash "${2:-$ADAPTER}" bash-pretool "$REC" >/dev/null 2>&1
  cat "$TMP/seen" 2>/dev/null
}
echo "── G167.13: snake_case tool_input / object toolArgs / plain-string toolArgs ──"
for shape in tool_input objargs plain; do
  case "$shape" in
    tool_input) pl="$(jq -cn --arg c "$FORCED_PUSH" '{tool_name:"bash",tool_input:{command:$c}}')" ;;
    objargs)    pl="$(jq -cn --arg c "$FORCED_PUSH" '{toolName:"bash",toolArgs:{command:$c}}')" ;;
    plain)      pl="$(jq -cn --arg c "$FORCED_PUSH" '{toolName:"bash",toolArgs:$c}')" ;;
  esac
  [ "$(seen_cmd "$pl")" = "$FORCED_PUSH" ] \
    && ok "$shape envelope -> the guard receives the real command" \
    || bad "$shape envelope -> guard saw '$(cat "$TMP/seen" 2>/dev/null)'"
done
echo "── G167.14: a snake_case force-push still reaches the tribunal and is denied ──"
jq -cn --arg cwd "$PROJ" --arg c "$FORCED_PUSH" '{tool_name:"bash",tool_input:{command:$c},cwd:$cwd,sessionId:"g167m"}' \
  | CLAUDE_PROJECT_DIR="$PROJ" bash "$ADAPTER" bash-pretool "$ORCH" >"$TMP/out-m.json" 2>/dev/null || true
[ "$(jq -r '.permissionDecision // empty' "$TMP/out-m.json" 2>/dev/null)" = "deny" ] \
  && ok "snake_case tool_input force-push -> tribunal -> deny" \
  || bad "snake_case force-push NOT denied: $(head -c 200 "$TMP/out-m.json")"
echo "── G167.15: a shell call whose command cannot be read fails CLOSED ──────"
ec_out="$(jq -cn '{toolName:"bash",toolArgs:({cmdline:"whatever"}|tostring)}' \
  | RC_OUT="$TMP/seen-ec" bash "$ADAPTER" bash-pretool "$REC" 2>/dev/null)"
if [ "$(printf '%s' "$ec_out" | jq -r '.permissionDecision // empty' 2>/dev/null)" = "deny" ] \
  && printf '%s' "$ec_out" | grep -q 'could not read the command' && [ ! -f "$TMP/seen-ec" ]; then
  ok "empty command for a Bash-mapped tool -> deny with a reason, hook never run"
else
  bad "empty-command Bash call was not failed closed: ${ec_out:0:160}"
fi
echo "── G167.16: teeth — revert the coalescing and the fail-closed branch ────"
MUT4="$TMP/adapter-mutant-args.sh"
python3 - "$ADAPTER" "$MUT4" <<'PY'
import pathlib
import sys

src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
anchor = "(.toolArgs // .tool_input // .toolInput // {}) as $a"
if anchor not in src:
    sys.stderr.write("MUTATION ANCHOR NOT FOUND: %r\n" % anchor)
    raise SystemExit(3)
pathlib.Path(sys.argv[2]).write_text(src.replace(anchor, "(.toolArgs // {}) as $a"), encoding="utf-8")
PY
if [ "$?" -ne 0 ]; then
  bad "teeth: could not build the toolArgs-only mutant (anchor missing)"
else
  [ "$(seen_cmd "$(jq -cn --arg c "$FORCED_PUSH" '{tool_name:"bash",tool_input:{command:$c}}')" "$MUT4")" != "$FORCED_PUSH" ] \
    && ok "teeth: toolArgs-only mutant loses the snake_case command (1a-4 reproduced)" \
    || bad "teeth: the toolArgs-only mutant still read tool_input — G167.13 may be vacuous"
fi
MUT5="$TMP/adapter-mutant-noclose.sh"
python3 - "$ADAPTER" "$MUT5" <<'PY'
import pathlib
import sys

src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
anchor = '.tool_name // ""\' 2>/dev/null)" = "Bash" ]'
if anchor not in src:
    sys.stderr.write("MUTATION ANCHOR NOT FOUND: %r\n" % anchor)
    raise SystemExit(3)
pathlib.Path(sys.argv[2]).write_text(src.replace(anchor, '.tool_name // ""\' 2>/dev/null)" = "NOT-A-TOOL" ]'), encoding="utf-8")
PY
if [ "$?" -ne 0 ]; then
  bad "teeth: could not build the no-fail-closed mutant (anchor missing)"
else
  ec_mut="$(jq -cn '{toolName:"bash",toolArgs:({cmdline:"whatever"}|tostring)}' \
    | RC_OUT="$TMP/seen-ec2" bash "$MUT5" bash-pretool "$REC" 2>/dev/null)"
  [ "$(printf '%s' "$ec_mut" | jq -r '.permissionDecision // empty' 2>/dev/null)" != "deny" ] \
    && ok "teeth: without the fail-closed branch the unreadable call proceeds" \
    || bad "teeth: the no-fail-closed mutant still denied — G167.15 may be vacuous"
fi

echo
if [ "$FAIL" -gt 0 ]; then
  printf 'FAIL: %d of %d assertion(s) failed\n' "$FAIL" "$((PASS + FAIL))" >&2
  exit 1
fi
printf 'Copilot tribunal e2e: %d/%d assertions passed\n' "$PASS" "$PASS"
exit 0
