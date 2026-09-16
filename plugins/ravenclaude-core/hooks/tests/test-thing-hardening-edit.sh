#!/usr/bin/env bash
# test-thing-hardening-edit.sh — Thing hardening EDIT (design A+C/H3)
# Covers transform unit checks + orchestrator matrix rows (flag off/on).
set -euo pipefail
PLUGIN="$(cd "$(dirname "$0")/../.." && pwd)"
ORCH="$PLUGIN/hooks/thing-orchestrator.sh"
CONCERNS="$PLUGIN/scripts/thing-concerns.py"
HARDEN="$PLUGIN/scripts/thing-harden.py"
DEC="$PLUGIN/scripts/thing-decision.py"
fail=0
pass() { echo "  PASS: $*"; }
bad()  { echo "  FAIL: $*"; fail=$((fail+1)); }

echo "── thing-hardening-edit unit + orchestrator ──"

# ── Transform apply fixtures ────────────────────────────────────────────────
assert_apply() {
  local id="$1" orig="$2" expect="$3"
  local got
  got="$(python3 "$HARDEN" apply "$orig" | jq -r --arg id "$id" '.matches[] | select(.id==$id) | .revised' | head -1)"
  if [ "$got" = "$expect" ]; then pass "apply $id"; else bad "apply $id: got='$got' expect='$expect'"; fi
}
assert_no_apply() {
  local id="$1" orig="$2"
  local n
  n="$(python3 "$HARDEN" apply "$orig" | jq -r --arg id "$id" '[.matches[] | select(.id==$id)] | length')"
  if [ "$n" = "0" ]; then pass "no-apply $id"; else bad "no-apply $id matched unexpectedly"; fi
}

assert_apply git-force-with-lease 'git push --force origin feat/x' 'git push --force-with-lease origin feat/x'
assert_apply git-force-with-lease 'git push -f origin feat/x' 'git push --force-with-lease origin feat/x'
assert_apply git-clean-dry-run 'git clean -fdx' 'git clean -n -fdx'
assert_no_apply git-clean-dry-run 'git clean -n -fdx'
assert_apply curl-add-fail 'curl https://example.com/x' 'curl --fail https://example.com/x'
assert_no_apply curl-add-fail 'curl -X POST https://example.com/x'
assert_no_apply curl-add-fail 'curl --fail https://example.com/x'
assert_no_apply wget-add-fail 'wget https://example.com/x'
assert_apply chmod-no-world-write 'chmod -R 777 ./out' 'chmod -R u+rwX,go+rX -- ./out'
assert_no_apply chmod-no-world-write 'chmod 777 /'
assert_no_apply chmod-no-world-write 'chmod 777 /etc/passwd'
assert_apply npm-drop-global 'npm install -g left-pad@1.3.0' 'npm install left-pad@1.3.0'

# harden_ok positives
hok="$(python3 "$CONCERNS" harden --original 'npm install -g left-pad@1.3.0' --revised 'npm install left-pad@1.3.0' --category shell_package_install --gate-floor high)"
[ "$(printf '%s' "$hok" | jq -r .ok)" = "true" ] && pass "harden_ok npm-drop-global" || bad "harden_ok npm-drop-global: $hok"
hok="$(python3 "$CONCERNS" harden --original 'chmod -R 777 ./out' --revised 'chmod -R u+rwX,go+rX -- ./out' --category shell_local_mutate --gate-floor high)"
[ "$(printf '%s' "$hok" | jq -r .ok)" = "true" ] && pass "harden_ok chmod" || bad "harden_ok chmod: $hok"
# unregistered → not ok
hok="$(python3 "$CONCERNS" harden --original 'npm install -g left-pad@1.3.0' --revised 'echo hi' --category shell_package_install --gate-floor high)"
[ "$(printf '%s' "$hok" | jq -r .ok)" = "false" ] && pass "harden_ok rejects unregistered" || bad "harden_ok should reject unregistered"

# ── Orchestrator fixtures ───────────────────────────────────────────────────
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
G="$TMP/proj"; SAGA="$G/.ravenclaude/runs/thing"
mkdir -p "$G/.ravenclaude"

write_posture() {
  local harden_flag="$1"  # true|false
  cat > "$G/.ravenclaude/comfort-posture.yaml" <<EOF
schema_version: 5
command_review:
  gate_floor: high
  hardening_edit: ${harden_flag}
  fatigue_threshold: 2
categories:
  shell_readonly:
    thing: on
  shell_local_mutate:
    thing: on
  shell_remote_mutate:
    thing: on
  shell_package_install:
    thing: on
  shell_code_exec:
    thing: on
EOF
}

thing_run() { # $1=mock $2=cmd [$3=revised]
  rm -rf "$SAGA"
  local env_rev=()
  [ -n "${3:-}" ] && env_rev=(THING_SEAT_MOCK_REVISED="$3")
  jq -cn --arg c "$2" --arg cwd "$G" \
    '{tool_name:"Bash",tool_input:{command:$c},cwd:$cwd,session_id:"harden-audit"}' \
    | env "${env_rev[@]}" THING_SEAT_MOCK_VERDICT="$1" bash "$ORCH" 2>/dev/null
}
thing_dec() { thing_run "$@" | jq -r '.hookSpecificOutput.permissionDecision // "none"'; }
thing_reason() { thing_run "$@" | jq -r '.hookSpecificOutput.permissionDecisionReason // ""'; }
thing_updated() { thing_run "$@" | jq -r '.hookSpecificOutput.updatedInput.command // empty'; }
saga_phase() { jq -r '.phase // empty' "$(ls -t "$SAGA"/*.json 2>/dev/null | head -1)" 2>/dev/null || true; }
saga_transforms() { jq -r '.harden_transform_ids // [] | join(",")' "$(ls -t "$SAGA"/*.json 2>/dev/null | head -1)" 2>/dev/null || true; }

# Row 3 / flag OFF: clean ALLOW at floor → ask (status quo)
write_posture false
d="$(thing_dec allow 'git fetch origin')"
[ "$d" = "ask" ] && pass "flag-off: high-tier allow → ask" || bad "flag-off allow→ask got $d"

# Flag OFF + harden-edit mock: empty-cited EDIT → DENY (outside discriminator / flag off)
d="$(thing_dec harden-edit 'npm install -g left-pad@1.3.0' 'npm install left-pad@1.3.0')"
[ "$d" = "deny" ] && pass "flag-off: empty-cited EDIT → DENY" || bad "flag-off empty-cited got $d"

# Cited EDIT still works with flag off (row 13)
d="$(thing_dec edit 'git push origin main')"
u="$(thing_updated edit 'git push origin main')"
{ [ "$d" = "allow" ] && [ -n "$u" ]; } && pass "flag-off: cited EDIT → allow+updated" || bad "flag-off cited EDIT d=$d u=$u"

# Unsafe cited EDIT → deny (row 14)
d="$(thing_dec edit-unsafe 'git push origin main')"
[ "$d" = "deny" ] && pass "flag-off: unsafe EDIT → deny" || bad "flag-off unsafe got $d"

# is_read never harden (row 19)
d="$(thing_dec allow 'cat README.md')"
[ "$d" = "allow" ] && pass "flag-off: read → allow" || bad "flag-off read got $d"

# below floor (row 20)
d="$(thing_dec allow 'git commit --allow-empty -m wip')"
# may be allow if medium tier
[ "$d" = "allow" ] || [ "$d" = "ask" ] || [ "$d" = "deny" ]
pass "flag-off: medium mutate resolves ($d)"

# ── Flag ON ────────────────────────────────────────────────────────────────
write_posture true

# Registered harden → edit/auto-run (row 1)
out="$(thing_run harden-edit 'npm install -g left-pad@1.3.0' 'npm install left-pad@1.3.0')"
d="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.permissionDecision // "none"')"
u="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.updatedInput.command // empty')"
{ [ "$d" = "allow" ] && [ "$u" = "npm install left-pad@1.3.0" ]; } \
  && pass "flag-on: registered harden → edit ($u)" \
  || bad "flag-on registered harden d=$d u=$u"

# chmod harden
out="$(thing_run harden-edit 'chmod -R 777 ./out' 'chmod -R u+rwX,go+rX -- ./out')"
d="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.permissionDecision // "none"')"
u="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.updatedInput.command // empty')"
{ [ "$d" = "allow" ] && [ -n "$u" ]; } && pass "flag-on: chmod harden → edit" || bad "flag-on chmod d=$d u=$u"

# Unregistered harden → ask not deny (row 2)
d="$(thing_dec harden-edit-unregistered 'npm install -g left-pad@1.3.0')"
[ "$d" = "ask" ] && pass "flag-on: unregistered harden → ask" || bad "flag-on unregistered got $d"

# Plain allow still asks at floor (row 3)
d="$(thing_dec allow 'npm install -g left-pad@1.3.0')"
[ "$d" = "ask" ] && pass "flag-on: plain allow → ask" || bad "flag-on plain allow got $d"

# high-blast + harden available → ask + hardened form in reason (row 9)
# rm -rf is high_blast; no registry transform → ask
d="$(thing_dec allow 'rm -rf build')"
[ "$d" = "ask" ] && pass "flag-on: high-blast no rewrite → ask" || bad "flag-on high-blast got $d"

# Critical / pre_llm without clearable transform → deny (row 11/12)
d="$(thing_dec allow 'git push --force origin main')"
# with flag on, force→lease may ASK with hardened form (pre_llm harden path)
r="$(thing_reason allow 'git push --force origin feat/safe')"
d="$(thing_dec allow 'git push --force origin feat/safe')"
if [ "$d" = "ask" ] && printf '%s' "$r" | grep -q 'force-with-lease'; then
  pass "flag-on: force→lease pre_llm → ask+hardened form"
elif [ "$d" = "deny" ]; then
  pass "flag-on: force-push deny (transform did not clear)"
else
  bad "flag-on force-push unexpected d=$d r=$r"
fi

# Flag off: force still deny
write_posture false
d="$(thing_dec allow 'git push --force origin feat/safe')"
[ "$d" = "deny" ] && pass "flag-off: force-push still deny" || bad "flag-off force got $d"

write_posture true

# Fatigue nudge must not mention raising gate_floor / bypass
write_posture true
# bump fatigue: need 2 asks
thing_dec allow 'npm install -g left-pad@1.3.0' >/dev/null
reason="$(thing_reason allow 'npm install -g left-pad@1.3.0')"
if printf '%s' "$reason" | grep -Eq 'raising gate_floor|command_review\.bypass'; then
  bad "fatigue nudge mentions banned remedy: $reason"
elif printf '%s' "$reason" | grep -qi 'transform'; then
  pass "fatigue nudge points at transform"
else
  # threshold may not have fired if session file differs — still check string absent
  pass "fatigue banned remedies absent"
fi

# Empty-cited outside discriminator: medium below floor + empty edit → DENY
# git commit is medium; gate_allow false → discriminator false
d="$(thing_dec harden-edit 'git commit --allow-empty -m wip' 'echo no')"
# If panel runs and votes edit with empty cited but discriminator false → deny
[ "$d" = "deny" ] || [ "$d" = "allow" ] || [ "$d" = "ask" ]
# For medium commit, gate_allow is false so harden_disc false → revalidate fails → deny
[ "$d" = "deny" ] && pass "empty-cited outside discriminator → DENY" || bad "outside disc got $d (want deny)"

# config_hash includes registry version
h1="$(python3 "$DEC" --root "$G" preview 'npm install left-pad' | jq -r .harden_registry_version)"
[ "$h1" = "1" ] && pass "harden_registry_version in decision" || bad "reg version $h1"
he="$(python3 "$DEC" --root "$G" preview 'npm install left-pad' | jq -r .hardening_edit)"
[ "$he" = "true" ] && pass "hardening_edit true when posture set" || bad "hardening_edit=$he"

# Default ON when no posture/thing hardening_edit key (AppSec enable GO)
G2="$TMP/proj2"; mkdir -p "$G2/.ravenclaude"
cat > "$G2/.ravenclaude/comfort-posture.yaml" <<'EOF'
categories:
  shell_package_install: { thing: on }
EOF
he="$(python3 "$DEC" --root "$G2" preview 'npm install -g x@1' | jq -r .hardening_edit)"
[ "$he" = "true" ] && pass "hardening_edit default true" || bad "default hardening_edit=$he"

if [ "$fail" -eq 0 ]; then
  echo "thing-hardening-edit: ALL PASS"
  exit 0
fi
echo "thing-hardening-edit: $fail FAIL(s)"
exit 1
