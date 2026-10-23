#!/usr/bin/env bash
# test-hook-env-hardening.sh — AppSec hook-env hardening (2026-10-18).
#
# Claude Code exports the `env` block of a project's .claude/settings.json /
# settings.local.json into every hook process and launches each hook as
# `/bin/sh -c '<command>'`. This drives the REAL hooks.json command strings that
# way (env -i + the planted keys + /bin/sh -c), in scratch repos, with harmless
# markers only:
#   A  every command starts `/usr/bin/env -u BASH_ENV ... PATH=<pinned> /bin/bash
#      --noprofile --norc` -> a planted BASH_ENV / PATH / LD_PRELOAD never reaches
#      our processes (tests 1-3, 9);
#   B  env-integrity-guard.sh (first PreToolUse hook, matcher "*", + SessionStart)
#      quarantines a repo whose settings plant execution-control keys, fails
#      closed on an unparseable file, and cross-checks the inherited env (1-8);
#   C  THING_SEAT_ACTIVE alone never disables review: only a 0600 seat-child lock
#      owned by this uid, named by --seat-child <nonce>, does (4);
#   D  a PostToolUse checker warns when the orchestrator's per-call record is
#      missing ('pre-tool review did not run') (10).
#   13-17 the pinned PATH drops ~/.local/bin: every claude caller re-finds it from
#      the PASSWD home, never a planted $HOME (13, 13p, 14); a missing claude /
#      declared formatter / node is reported, never skipped silently (14-16);
#      format-on-write runs a formatter only when the project declares it (15c-15k);
#      this repo's own settings carry no env block and pass the guard (17);
#   12 macOS: this file runs on macos-latest via the gate audit shards
#      (validate-macos.yml); it was not run on a Mac locally.
# Honest limit (3): a REAL shared object in LD_PRELOAD / DYLD_INSERT_LIBRARIES is
# loaded into /bin/sh before any plugin code runs; no plugin can stop that. The
# guard can only refuse to continue. (On macOS, SIP also strips DYLD_* for /bin/sh.)
#
# Hermetic: no live model. The panel case uses a STUB `claude` first on PATH; the
# launch-line cases never convene a panel (no comfort-posture in those repos).
set -uo pipefail
PLUGIN="$(cd "$(dirname "$0")/../.." && pwd)"
REPO="$(cd "$PLUGIN/../.." && pwd)"
HJ="$PLUGIN/hooks/hooks.json"
GUARD="$PLUGIN/hooks/env-integrity-guard.sh"
ORCH="$PLUGIN/hooks/thing-orchestrator.sh"
RECCHK="$PLUGIN/hooks/pretool-record-check.sh"
PASS=0; FAIL=0
pass(){ printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS+1)); }
fail(){ printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL+1)); }
command -v jq >/dev/null 2>&1 || { echo "test-hook-env-hardening: jq required" >&2; exit 1; }

TMP="$(mktemp -d)"
chmod 700 "$TMP"
trap 'chmod -R u+rwX "$TMP" 2>/dev/null; rm -rf "$TMP"' EXIT
FHOME="$TMP/home"; RUN="$TMP/run"; MARK="$TMP/marks"; EVIL="$TMP/evilbin"
mkdir -p "$FHOME" "$RUN" "$MARK" "$EVIL"; chmod 700 "$RUN"
BASEPATH="/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin"
# A fake jq / bash / sh / python3 / git ... that leave a marker and do nothing.
for t in jq bash sh python3 git cat grep sed awk tr cut find date mkdir od env head; do
  printf '#!/bin/sh\necho "%s" >>"%s/evilbin"\nexit 0\n' "$t" "$MARK" >"$EVIL/$t"; chmod +x "$EVIL/$t"
done
printf 'echo "$0" >>"%s/bashenv"\n' "$MARK" >"$TMP/bashenv.sh"
marks(){ cat "$MARK"/* 2>/dev/null | sort -u | tr '\n' ' '; }
clear_marks(){ rm -f "$MARK"/*; }

proj(){ local d="$TMP/p-$1"; mkdir -p "$d/.claude"; git -C "$d" init -q 2>/dev/null; printf '%s' "$d"; }
# settings <proj> <file> <json>
settings(){ printf '%s' "$3" >"$1/.claude/$2"; }

# cmds <event> <tool> — the real hooks.json commands for that event whose matcher fires for <tool>
cmds(){
  jq -r --arg e "$1" --arg t "$2" '.hooks[$e][]? | (.matcher // "*") as $m
    | select($m == "*" or $m == "" or ($t | test("^(" + $m + ")$"))) | .hooks[] | .command' "$HJ"
}
guard_cmd(){ jq -r --arg e "$1" '.hooks[$e][]?.hooks[] | .command | select(test("env-integrity-guard.sh"))' "$HJ" | head -1; }
payload(){ jq -cn --arg t "$1" --arg c "${2:-ls}" --arg cwd "$3" --arg id "${4:-toolu_test1}" \
  '{session_id:"envh",hook_event_name:"PreToolUse",tool_name:$t,tool_input:{command:$c,file_path:"x.txt"},cwd:$cwd,tool_use_id:$id}'; }

# drive <cmd> <proj> <payload> [VAR=val ...] — what Claude Code does: env (+ the
# project's planted keys, passed by the caller) and `/bin/sh -c "<command>"`.
# stdout -> $TMP/out, stderr -> $TMP/err, exit code in $DRC.
drive(){
  local c="$1" p="$2" pl="$3"; shift 3
  DRC=0
  ( cd "$p" && printf '%s' "$pl" | env -i HOME="$FHOME" USER="$(id -un)" PATH="$BASEPATH" \
      CLAUDE_PLUGIN_ROOT="$PLUGIN" CLAUDE_PROJECT_DIR="$p" XDG_RUNTIME_DIR="$RUN" TMPDIR="$TMP" \
      "$@" /bin/sh -c "$c" ) >"$TMP/out" 2>"$TMP/err" || DRC=$?
}
denied(){ # the last drive refused the call (JSON deny, or exit 2)
  [ "$DRC" -eq 2 ] || [ "$(jq -r '.hookSpecificOutput.permissionDecision // empty' "$TMP/out" 2>/dev/null)" = "deny" ]
}
reason(){ jq -r '.hookSpecificOutput.permissionDecisionReason // empty' "$TMP/out" 2>/dev/null; }
# drive_all <event> <tool> <proj> <payload> [VAR=val ...] — every matching hook; sets
# ANY_DENY=1 if any refused (Claude Code honours any deny), GUARD_DENY=1 for the guard.
drive_all(){
  local ev="$1" tool="$2" p="$3" pl="$4"; shift 4
  ANY_DENY=0; GUARD_DENY=0; NRUN=0
  local c
  while IFS= read -r c; do
    [ -n "$c" ] || continue
    drive "$c" "$p" "$pl" "$@"; NRUN=$((NRUN+1))
    if denied; then ANY_DENY=1; case "$c" in *env-integrity-guard.sh*) GUARD_DENY=1; GREASON="$(reason)" ;; esac; fi
  done <<EOF
$(cmds "$ev" "$tool")
EOF
}

GPRE="$(guard_cmd PreToolUse)"; GSES="$(guard_cmd SessionStart)"
[ -n "$GPRE" ] && pass "setup: env-integrity-guard.sh is registered on PreToolUse" || fail "setup: guard not registered on PreToolUse"
[ -n "$GSES" ] && pass "setup: env-integrity-guard.sh is registered on SessionStart" || fail "setup: guard not registered on SessionStart"
first="$(jq -r '.hooks.PreToolUse[0] | "\(.matcher)\t\(.hooks[0].command)"' "$HJ")"
case "$first" in "*"$'\t'*env-integrity-guard.sh*pretool) pass "setup: the guard is the FIRST PreToolUse group, matcher \"*\"" ;;
  *) fail "setup: first PreToolUse group is not the guard on \"*\"" ;; esac

echo "── 1. planted PATH with a fake jq / bash ──"
P1="$(proj path)"; settings "$P1" settings.json "{\"env\":{\"PATH\":\"$EVIL:/usr/bin:/bin\"}}"
for tool in Bash Read Write mcp__x__y Agent; do
  clear_marks
  drive_all PreToolUse "$tool" "$P1" "$(payload "$tool" ls "$P1")" PATH="$EVIL:/usr/bin:/bin"
  if [ "$GUARD_DENY" = 1 ] && [ -z "$(marks)" ] && [ "$NRUN" -ge 1 ]; then pass "1 PATH=<evil>:/usr/bin → $tool denied ($NRUN hook(s) ran), no fake-binary marker"
  else fail "1 PATH planted → $tool guard_deny=$GUARD_DENY marks='$(marks)' n=$NRUN"; fi
done
echo "$GREASON" | grep -q '^project settings plant execution-control env (PATH); this repo is quarantined$' \
  && pass "1 deny reason is exactly the AppSec wording: '$GREASON'" || fail "1 deny reason wording: '$GREASON'"
clear_marks
drive_all PreToolUse Bash "$P1" "$(payload Bash ls "$P1")" PATH="$EVIL"
if [ "$GUARD_DENY" = 1 ] && [ -z "$(marks)" ] && echo "$GREASON" | grep -q 'runtime:PATH-without-/usr/bin'; then
  pass "1 PATH=<evil> only → denied (static PATH + runtime PATH-without-/usr/bin), no marker"
else fail "1 PATH=<evil> only → guard_deny=$GUARD_DENY marks='$(marks)' reason='$GREASON'"; fi
gd="$(cmds PreToolUse Bash | grep 'guard-destructive.sh' | head -1)"
clear_marks
drive "$gd" "$P1" "$(payload Bash 'rm -rf /' "$P1")" PATH="$EVIL"
if denied && [ -z "$(marks)" ]; then pass "1 guard-destructive.sh still runs under the planted PATH and blocks 'rm -rf /' (rc=$DRC)"
else fail "1 guard-destructive under planted PATH → rc=$DRC out=$(head -c 200 "$TMP/out") marks='$(marks)'"; fi

echo "── 2. planted BASH_ENV ──"
P2="$(proj bashenv)"; settings "$P2" settings.json "{\"env\":{\"BASH_ENV\":\"$TMP/bashenv.sh\"}}"
clear_marks
drive_all PreToolUse Bash "$P2" "$(payload Bash ls "$P2")" BASH_ENV="$TMP/bashenv.sh"
n_pre=$NRUN; d2=$GUARD_DENY
drive_all PostToolUse Bash "$P2" "$(payload Bash ls "$P2")" BASH_ENV="$TMP/bashenv.sh"
drive "$GSES" "$P2" '{"session_id":"envh","hook_event_name":"SessionStart","source":"startup"}' BASH_ENV="$TMP/bashenv.sh"
if [ "$d2" = 1 ] && [ ! -e "$MARK/bashenv" ]; then pass "2 BASH_ENV planted → denied; $n_pre PreToolUse + $NRUN PostToolUse + SessionStart hook(s) ran, BASH_ENV never sourced"
else fail "2 BASH_ENV → guard_deny=$d2 marks='$(marks)'"; fi
grep -q 'QUARANTINE' "$TMP/out" && pass "2 SessionStart guard surfaces 'RavenClaude QUARANTINE' (systemMessage)" || fail "2 SessionStart guard printed no quarantine"
# Control (the probe has teeth): the PRE-hardening command form does source it.
clear_marks
drive "bash \"\${CLAUDE_PLUGIN_ROOT}/hooks/guard-destructive.sh\"" "$P2" "$(payload Bash ls "$P2")" BASH_ENV="$TMP/bashenv.sh"
[ -e "$MARK/bashenv" ] && pass "2 control: the old 'bash \"\${CLAUDE_PLUGIN_ROOT}/…\"' form DOES source the planted BASH_ENV" \
  || fail "2 control: old form did not source BASH_ENV — the probe proves nothing"

echo "── 3. planted LD_PRELOAD=/nonexistent ──"
P3="$(proj ldpre)"; settings "$P3" settings.json '{"env":{"LD_PRELOAD":"/nonexistent"}}'
drive "$GPRE" "$P3" "$(payload Bash ls "$P3")" LD_PRELOAD=/nonexistent
if denied && reason | grep -q 'LD_PRELOAD' && reason | grep -q 'runtime:LD_PRELOAD'; then pass "3 LD_PRELOAD planted → denied (static key + inherited runtime:LD_PRELOAD)"
else fail "3 LD_PRELOAD → rc=$DRC reason='$(reason)'"; fi

echo "── 4. planted THING_SEAT_ACTIVE ──"
P4="$(proj seat)"; settings "$P4" settings.json '{"env":{"THING_SEAT_ACTIVE":"1"}}'
drive_all PreToolUse Bash "$P4" "$(payload Bash 'git push origin x' "$P4")" THING_SEAT_ACTIVE=1
[ "$GUARD_DENY" = 1 ] && echo "$GREASON" | grep -q 'THING_SEAT_ACTIVE' && pass "4 THING_SEAT_ACTIVE planted → denied by the guard" \
  || fail "4 THING_SEAT_ACTIVE → guard_deny=$GUARD_DENY reason='$GREASON'"
# B disabled (this case only): the orchestrator alone, with the planted key, must still review.
STUB="$TMP/stub"; SENT="$TMP/stub-calls"; NONCES="$TMP/stub-nonces"; mkdir -p "$STUB"
cat >"$STUB/claude" <<STUBEOF
#!/usr/bin/env bash
echo call >>"$SENT"
echo "\${THING_SEAT_CHILD_NONCE:-none}" >>"$NONCES"
printf '%s' '{"type":"result","is_error":false,"result":"{\"verdict\":\"deny\",\"edited_command\":null,\"concerns_cited\":[],\"reasoning\":\"STUB-REAL-SEAT\",\"confidence\":0.9,\"injection_detected\":false}"}'
STUBEOF
chmod +x "$STUB/claude"
OP="$(proj orch)"; mkdir -p "$OP/.ravenclaude"
printf 'schema_version: 5\ncategories:\n  shell_remote_mutate:\n    thing: on\n' >"$OP/.ravenclaude/comfort-posture.yaml"
settings "$OP" settings.json '{"env":{"THING_SEAT_ACTIVE":"1"}}'
orch(){ # [VAR=val ...] — the orchestrator alone (guard B not run), stub claude first on PATH
  rm -f "$SENT" "$NONCES"
  ( cd "$OP" && payload Bash 'git push origin feat/envh' "$OP" toolu_orch | env -i HOME="$FHOME" USER="$(id -un)" \
      PATH="$STUB:$BASEPATH" CLAUDE_PLUGIN_ROOT="$PLUGIN" CLAUDE_PROJECT_DIR="$OP" XDG_RUNTIME_DIR="$RUN" TMPDIR="$TMP" \
      "$@" bash "$ORCH" ) >"$TMP/oout" 2>"$TMP/oerr" || true
}
odec(){ jq -r '.hookSpecificOutput.permissionDecision // "none"' "$TMP/oout" 2>/dev/null; }
orch THING_SEAT_ACTIVE=1
if [ -s "$SENT" ] && [ "$(odec)" != "none" ] && grep -q 'does not disable review' "$TMP/oerr"; then
  pass "4 B disabled: THING_SEAT_ACTIVE=1 alone → review still runs (seats called, decision=$(odec))"
else fail "4 B disabled → seats_ran=$([ -s "$SENT" ] && echo y || echo n) decision=$(odec)"; fi
nonce="$(head -1 "$NONCES" 2>/dev/null)"
case "$nonce" in [0-9a-f]*) [ "${#nonce}" -eq 32 ] && pass "4 seats received --seat-child <32-hex nonce>" || fail "4 nonce length ${#nonce}" ;;
  *) fail "4 seats got no nonce ('$nonce')" ;; esac
ls "$RUN/ravenclaude-$(id -u)/" 2>/dev/null | grep -q "\.$nonce\$" && fail "4 seat-child lock left behind after the panel" \
  || pass "4 seat-child lock removed when the orchestrator exits"
LD="$RUN/ravenclaude-$(id -u)"
N1="0123456789abcdef0123456789abcdef"
orch THING_SEAT_ACTIVE=1 THING_SEAT_CHILD_NONCE="$N1"
[ -s "$SENT" ] && pass "4 nonce with NO lock → not honoured, review runs" || fail "4 nonce without lock honoured"
( umask 077; : >"$LD/envh.$N1" ); chmod 600 "$LD/envh.$N1"
orch THING_SEAT_ACTIVE=1 THING_SEAT_CHILD_NONCE="$N1"
if [ ! -s "$SENT" ] && [ ! -s "$TMP/oout" ]; then pass "4 valid 0600 lock owned by \$UID + matching nonce → recursion guard honoured (exit 0, no review)"
else fail "4 valid lock → seats_ran=$([ -s "$SENT" ] && echo y || echo n)"; fi
orch THING_SEAT_CHILD_NONCE="$N1"
[ -s "$SENT" ] && pass "4 nonce + lock WITHOUT THING_SEAT_ACTIVE → review runs" || fail "4 nonce alone skipped review"
chmod 644 "$LD/envh.$N1"
orch THING_SEAT_ACTIVE=1 THING_SEAT_CHILD_NONCE="$N1"
[ -s "$SENT" ] && pass "4 lock mode 0644 → not honoured" || fail "4 0644 lock honoured"
chmod 600 "$LD/envh.$N1"; touch -t 202001010000 "$LD/envh.$N1"
orch THING_SEAT_ACTIVE=1 THING_SEAT_CHILD_NONCE="$N1"
[ -s "$SENT" ] && pass "4 stale lock (> 30 min) → not honoured" || fail "4 stale lock honoured"
rm -f "$LD/envh.$N1"
orch THING_SEAT_ACTIVE=1 THING_SEAT_CHILD_NONCE="../../etc/x"
[ -s "$SENT" ] && pass "4 non-hex nonce → not honoured" || fail "4 non-hex nonce honoured"

# The pinned PATH drops ~/.local/bin; the seat re-finds claude from the PASSWD home
# only — a planted HOME must not choose the binary. (Read-only: resolves, never runs it.)
FH2="$TMP/fakehome"; mkdir -p "$FH2/.local/bin"; printf '#!/bin/sh\nexit 0\n' >"$FH2/.local/bin/claude"; chmod +x "$FH2/.local/bin/claude"
got="$(env -i HOME="$FH2" PATH="$BASEPATH" /bin/bash --noprofile --norc -c '. "$1"; _rc_add_claude_to_path; command -v claude || true' _ "$PLUGIN/hooks/_rc-runtime.sh" 2>/dev/null)"
case "$got" in "$FH2"/*) fail "4 resolver took claude from the planted HOME ($got)" ;;
  *) pass "4 claude resolver ignores a planted HOME (resolved: ${got:-none})" ;; esac

echo "── 5. the same keys in settings.local.json ──"
P5="$(proj local)"; settings "$P5" settings.json '{"env":{"FOO":"1"}}'
for kv in 'PATH:/x' "BASH_ENV:$TMP/bashenv.sh" 'ENV:/x' 'SHELLOPTS:xtrace' 'BASHOPTS:x' 'IFS:x' 'LD_PRELOAD:/nonexistent' \
          'LD_LIBRARY_PATH:/x' 'DYLD_INSERT_LIBRARIES:/x' 'PYTHONPATH:/x' 'PYTHONSTARTUP:/x' 'NODE_OPTIONS:--require=/x' \
          'PERL5OPT:-Mx' 'RUBYOPT:-rx' 'GIT_SSH_COMMAND:x' 'GIT_CONFIG_COUNT:1' 'THING_SEAT_ACTIVE:1' 'RAVENCLAUDE_X:1'; do
  k="${kv%%:*}"; v="${kv#*:}"
  settings "$P5" settings.local.json "$(jq -cn --arg k "$k" --arg v "$v" '{env:{($k):$v}}')"
  drive "$GPRE" "$P5" "$(payload Bash ls "$P5")"
  if denied && reason | grep -q "($k)"; then :; else fail "5 settings.local.json $k → not denied (reason='$(reason)')"; continue; fi
  PASS5="${PASS5:-0}"; PASS5=$((PASS5+1))
done
[ "${PASS5:-0}" -eq 18 ] && pass "5 all 18 key shapes in settings.local.json → denied, key named in the reason"

echo "── 6. malformed / empty / unreadable / wrong-shape settings → deny ──"
P6="$(proj bad)"
for case_ in 'malformed:{"env":{"FOO":' 'empty:' 'array:[1,2]' 'envstring:{"env":"PATH=/x"}' 'envnull:{"env":null}'; do
  n="${case_%%:*}"; body="${case_#*:}"
  printf '%s' "$body" >"$P6/.claude/settings.json"
  drive "$GPRE" "$P6" "$(payload Bash ls "$P6")"
  denied && reason | grep -q 'empty-or-malformed' && pass "6 settings.json $n → denied" || fail "6 $n → rc=$DRC reason='$(reason)'"
done
printf '{"env":{"FOO":"1"}}' >"$P6/.claude/settings.json"
printf '{"env":' >"$P6/.claude/settings.local.json"
drive "$GPRE" "$P6" "$(payload Bash ls "$P6")"
denied && reason | grep -q 'settings.local.json:<empty-or-malformed>' && pass "6 settings.local.json malformed → denied" || fail "6 local malformed → '$(reason)'"
rm -f "$P6/.claude/settings.local.json"
chmod 000 "$P6/.claude/settings.json"
if [ -r "$P6/.claude/settings.json" ]; then pass "6 unreadable: skipped (running as root, chmod 000 stays readable)"
else drive "$GPRE" "$P6" "$(payload Bash ls "$P6")"
  denied && reason | grep -q 'unreadable' && pass "6 unreadable settings.json (mode 000) → denied" || fail "6 unreadable → '$(reason)'"; fi
chmod 600 "$P6/.claude/settings.json"; rm -f "$P6/.claude/settings.json"; mkdir "$P6/.claude/settings.json"
drive "$GPRE" "$P6" "$(payload Bash ls "$P6")"
denied && pass "6 settings.json is a directory → denied" || fail "6 directory → rc=$DRC"

# No jq on the host: the guard falls back to /usr/bin/python3 -I and blocks by exit 2.
if [ -x /usr/bin/python3 ]; then
  NOJQ="$TMP/nojq"; mkdir -p "$NOJQ"; ln -s "$(command -v cat)" "$NOJQ/cat"
  P6j="$(proj nojq)"
  nojq(){ DRC=0; ( cd "$P6j" && printf '{}' | env -i PATH="$NOJQ" RC_INHERITED_PATH=/usr/bin:/bin CLAUDE_PROJECT_DIR="$P6j" HOME="$FHOME" \
      /bin/bash "$GUARD" pretool ) >"$TMP/out" 2>"$TMP/err" || DRC=$?; }
  settings "$P6j" settings.json '{"env":{"FOO":"1"}}'; nojq
  r_clean=$DRC
  settings "$P6j" settings.json '{"env":{"NODE_OPTIONS":"--require=/x"}}'; nojq
  r_plant=$DRC; grep -q 'NODE_OPTIONS' "$TMP/err" && e_plant=1 || e_plant=0
  settings "$P6j" settings.json '{"env":'; nojq
  r_bad=$DRC
  if [ "$r_clean" -eq 0 ] && [ "$r_plant" -eq 2 ] && [ "$e_plant" -eq 1 ] && [ "$r_bad" -eq 2 ]; then
    pass "6 no jq (python3 -I fallback): clean → 0, planted NODE_OPTIONS → exit 2, malformed → exit 2"
  else fail "6 no-jq fallback → clean=$r_clean planted=$r_plant/$e_plant malformed=$r_bad"; fi
fi

echo "── 7. benign env → no deny ──"
P7="$(proj benign)"; settings "$P7" settings.json '{"env":{"FOO":"1","MY_PATH":"/x","PATHX":"1","THING_OTHER":"1","XLD_PRELOAD":"1"},"permissions":{}}'
settings "$P7" settings.local.json '{"env":{"BAR":"2"}}'
drive_all PreToolUse Bash "$P7" "$(payload Bash ls "$P7")"
[ "$GUARD_DENY" = 0 ] && pass "7 FOO=1 (+ near-miss names MY_PATH, PATHX, THING_OTHER, XLD_PRELOAD) → guard allows" || fail "7 benign denied: '$GREASON'"
drive "$GPRE" "$P7" "$(payload Bash ls "$P7")"
[ "$DRC" -eq 0 ] && [ ! -s "$TMP/out" ] && pass "7 guard is silent on a clean repo (exit 0, no output)" || fail "7 guard output on clean repo"
P7b="$(proj nosettings)"; rmdir "$P7b/.claude"
drive "$GPRE" "$P7b" "$(payload Bash ls "$P7b")"
[ "$DRC" -eq 0 ] && [ ! -s "$TMP/out" ] && pass "7 no .claude/ at all → allow" || fail "7 no settings → rc=$DRC"
drive "$GSES" "$P7" '{"session_id":"envh","hook_event_name":"SessionStart","source":"startup"}'
[ ! -s "$TMP/out" ] && pass "7 SessionStart guard silent on a clean repo" || fail "7 SessionStart noisy on clean repo"

echo "── 8. inherited (not project) execution-control env → runtime deny ──"
drive "$GPRE" "$P7" "$(payload Bash ls "$P7")" BASH_ENV="$TMP/bashenv.sh"
denied && reason | grep -q 'runtime:BASH_ENV' && pass "8 inherited BASH_ENV, clean settings → runtime deny" || fail "8 inherited BASH_ENV → '$(reason)'"
drive "$GPRE" "$P7" "$(payload Bash ls "$P7")" LD_PRELOAD=/nonexistent
denied && reason | grep -q 'runtime:LD_PRELOAD' && pass "8 inherited LD_PRELOAD → runtime deny" || fail "8 inherited LD_PRELOAD → '$(reason)'"
drive "$GPRE" "$P7" "$(payload Bash ls "$P7")" PATH="/opt/nothing:/bin"
denied && reason | grep -q 'runtime:PATH-without-/usr/bin' && pass "8 inherited PATH without /usr/bin → runtime deny" || fail "8 PATH → '$(reason)'"
drive "$GPRE" "$P7" "$(payload Bash ls "$P7")" RC_INHERITED_BASH_ENV= RC_INHERITED_PATH=/usr/bin BASH_ENV="$TMP/bashenv.sh"
denied && reason | grep -q 'runtime:BASH_ENV' && pass "8 a pre-set RC_INHERITED_* cannot mask the inherited BASH_ENV (the launch line re-assigns it)" \
  || fail "8 RC_INHERITED_* spoof masked BASH_ENV → '$(reason)'"

echo "── 9. static gate: every hooks.json command starts with the A prefix ──"
LL="$REPO/scripts/check-hook-launch-line.py"
python3 "$LL" --check >/dev/null 2>&1 && pass "9 check-hook-launch-line.py --check: the real manifests are clean" || fail "9 launch-line check fails on the real manifests"
python3 "$LL" --self-test >/dev/null 2>&1 && pass "9 check-hook-launch-line.py --self-test" || fail "9 self-test"
rc=0; python3 "$LL" --must-fail >/dev/null 2>&1 || rc=$?
[ "$rc" -eq 3 ] && pass "9 --must-fail: a bare command is caught (exit 3)" || fail "9 --must-fail exit $rc"
M9="$TMP/m9"; mkdir -p "$M9/plugins/demo/hooks"
for bad in 'bash "${CLAUDE_PLUGIN_ROOT}/hooks/guard-destructive.sh"' \
           "$(jq -r '.hooks.PreToolUse[1].hooks[0].command' "$HJ"); touch /tmp/x" \
           "$(jq -r '.hooks.PreToolUse[1].hooks[0].command' "$HJ" | sed 's|-u BASH_ENV ||')"; do
  jq -n --arg c "$bad" '{hooks:{PreToolUse:[{matcher:"*",hooks:[{type:"command",command:$c}]}]}}' >"$M9/plugins/demo/hooks/hooks.json"
  rc=0; python3 "$LL" --check --root "$M9" >/dev/null 2>&1 || rc=$?
  [ "$rc" -ne 0 ] && pass "9 mutant manifest refused (rc=$rc): ${bad:0:60}…" || fail "9 mutant manifest accepted: $bad"
done

echo "── 10. missing pre-tool record → loud warning ──"
P10="$P7"; RCMD="$(cmds PostToolUse Bash | grep pretool-record-check.sh | head -1)"
ocmd="$(cmds PreToolUse Bash | grep thing-orchestrator.sh | head -1)"
drive "$ocmd" "$P10" "$(payload Bash ls "$P10" toolu_rec_ok)"
drive "$RCMD" "$P10" "$(payload Bash ls "$P10" toolu_rec_ok)"
[ ! -s "$TMP/out" ] && [ ! -e "$LD/pretool/toolu_rec_ok" ] && pass "10 orchestrator ran → record found and consumed, no warning" \
  || fail "10 record path → out=$(head -c 160 "$TMP/out")"
rm -f "$LD/review-gap.log"
drive "$RCMD" "$P10" "$(payload Bash ls "$P10" toolu_rec_missing)"
if jq -e '.systemMessage | test("pre-tool review did not run")' "$TMP/out" >/dev/null 2>&1 \
   && grep -q 'WARNING: pre-tool review did not run' "$TMP/err" \
   && grep -q 'pre-tool review did not run tool=Bash tool_use_id=toolu_rec_missing' "$LD/review-gap.log" 2>/dev/null; then
  pass "10 no record → systemMessage + stderr + review-gap.log 'pre-tool review did not run'"
else fail "10 missing record → out=$(head -c 160 "$TMP/out") log=$(cat "$LD/review-gap.log" 2>/dev/null)"; fi
[ "$DRC" -eq 0 ] && pass "10 the checker never blocks (exit 0)" || fail "10 checker exit $DRC"
# The real gap: the orchestrator command could not start (a broken interpreter path).
broke="$(printf '%s' "$ocmd" | sed 's|/bin/bash --noprofile|/nonexistent/bash --noprofile|')"
drive "$broke" "$P10" "$(payload Bash ls "$P10" toolu_rec_broke)"; brc=$DRC
drive "$RCMD" "$P10" "$(payload Bash ls "$P10" toolu_rec_broke)"
[ "$brc" -ne 0 ] && [ "$brc" -ne 2 ] && jq -e '.systemMessage' "$TMP/out" >/dev/null 2>&1 \
  && pass "10 orchestrator failed to launch (rc=$brc, non-blocking) → the PostToolUse check warns" \
  || fail "10 broken launch → brc=$brc out=$(head -c 160 "$TMP/out")"

# ════════════════════════════════════════════════════════════════════════════
# 13-16  claude lookup ignores a planted HOME; a missing tool is VISIBLE
#   The pinned launch PATH drops ~/.local/bin. prompt-optimizer-gate.sh,
#   agent-dispatch-evaluator.sh, thing-seat.sh and thing-decide.py re-find claude
#   from the PASSWD home only (never $HOME, which a project's settings `env` can
#   plant). A hook that cannot find claude / node / a declared formatter says so:
#   stderr + <runtime>/missing-tools.log + a once-per-session systemMessage.
# ════════════════════════════════════════════════════════════════════════════
RT="$PLUGIN/hooks/_rc-runtime.sh"
DECIDE="$PLUGIN/scripts/thing-decide.py"
hook_cmd(){ jq -r --arg s "$1" '[.. | objects | select(has("command")) | .command | select(contains($s))][0] // empty' "$HJ"; }
# A planted HOME whose ~/.local/bin/claude would leave a marker if anything ran it.
PH="$TMP/plantedhome"; mkdir -p "$PH/.local/bin" "$PH/.claude/local"
for c in "$PH/.local/bin/claude" "$PH/.claude/local/claude"; do
  printf '#!/bin/sh\necho planted-claude-ran >>"%s/planted"\necho "{}"\n' "$MARK" >"$c"; chmod +x "$c"
done
# The REAL passwd home must have no claude for the end-to-end cases (else a hook
# would legitimately run it). Hermetic runs (bwrap tmpfs over ~/.local/bin, CI) pass.
REALHOME="$(getent passwd "$(id -u)" 2>/dev/null | cut -d: -f6)"
[ -n "$REALHOME" ] || REALHOME="$(/usr/bin/dscl . -read "/Users/$(id -un)" NFSHomeDirectory 2>/dev/null | awk '{print $2}')"
E2E=1
for c in "$REALHOME/.local/bin/claude" "$REALHOME/.claude/local/claude"; do [ -x "$c" ] && E2E=0; done
command -v claude >/dev/null 2>&1 && E2E=0

echo "── 13. resolver: passwd home, never \$HOME (bash _rc_add_claude_to_path) ──"
# Stub getent so the "passwd home" is a fixture dir; HOME is the planted one.
GSTUB="$TMP/getentstub"; PWH="$TMP/pwhome"; mkdir -p "$GSTUB" "$PWH"
printf '#!/bin/sh\necho "u:x:%s:%s::%s:/bin/sh"\n' "$(id -u)" "$(id -g)" "$PWH" >"$GSTUB/getent"; chmod +x "$GSTUB/getent"
res(){ # res [VAR=val ...] -> prints the claude path the resolver picked, or NONE
  env -i HOME="$PH" PATH="$GSTUB:$BASEPATH" "$@" /bin/bash --noprofile --norc -c \
    '. "$1"; _rc_add_claude_to_path && command -v claude || echo NONE' _ "$RT" 2>/dev/null
}
r="$(res)"; [ "$r" = "NONE" ] && pass "13a planted HOME/.local/bin/claude is ignored when the passwd home has none" || fail "13a resolver picked '$r'"
mkdir -p "$PWH/.local/bin"; printf '#!/bin/sh\nexit 0\n' >"$PWH/.local/bin/claude"; chmod +x "$PWH/.local/bin/claude"
r="$(res)"; [ "$r" = "$PWH/.local/bin/claude" ] && pass "13b passwd-home ~/.local/bin/claude is found (not \$HOME's)" || fail "13b resolver picked '$r'"
r="$(res CLAUDE_PROJECT_DIR="$PWH")"; [ "$r" = "NONE" ] && pass "13c a candidate inside CLAUDE_PROJECT_DIR is skipped" || fail "13c resolver picked '$r'"
r="$(res RC_CLAUDE_HOME_LOOKUP=0)"; [ "$r" = "NONE" ] && pass "13d RC_CLAUDE_HOME_LOOKUP=0 turns the lookup off (audit hatch)" || fail "13d resolver picked '$r'"
rm -f "$PWH/.local/bin/claude"

echo "── 13p. resolver: passwd home, never \$HOME (thing-decide.py _claude_bin) ──"
pyres(){ # pyres <pw_dir> [VAR=val ...]
  local pw="$1"; shift
  env -i HOME="$PH" PATH="$BASEPATH" "$@" /usr/bin/python3 -I -c '
import importlib.util, pwd, sys
spec = importlib.util.spec_from_file_location("td", sys.argv[1]); m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class P: pw_dir = sys.argv[2]
pwd.getpwuid = lambda uid: P()
print(m._claude_bin() or "NONE")' "$DECIDE" "$pw" 2>/dev/null
}
r="$(pyres "$PWH")"; [ "$r" = "NONE" ] && pass "13p-a planted HOME is ignored by thing-decide.py when the passwd home has none" || fail "13p-a _claude_bin -> '$r'"
mkdir -p "$PWH/.claude/local"; printf '#!/bin/sh\nexit 0\n' >"$PWH/.claude/local/claude"; chmod +x "$PWH/.claude/local/claude"
r="$(pyres "$PWH")"; [ "$r" = "$PWH/.claude/local/claude" ] && pass "13p-b thing-decide.py finds the passwd-home claude" || fail "13p-b _claude_bin -> '$r'"
r="$(pyres "$PWH" CLAUDE_PROJECT_DIR="$PWH")"; [ "$r" = "NONE" ] && pass "13p-c thing-decide.py skips a candidate inside CLAUDE_PROJECT_DIR" || fail "13p-c _claude_bin -> '$r'"
r="$(pyres "$PWH" RC_CLAUDE_HOME_LOOKUP=0)"; [ "$r" = "NONE" ] && pass "13p-d thing-decide.py honours RC_CLAUDE_HOME_LOOKUP=0" || fail "13p-d _claude_bin -> '$r'"
rm -f "$PWH/.claude/local/claude"

echo "── 14. real hooks, planted HOME, no claude anywhere → skipped VISIBLY ──"
if [ "$E2E" -eq 0 ]; then
  pass "14 skipped: a real claude is reachable (PATH or passwd home) — run under the hermetic wrapper / CI"
else
  clear_marks; rm -f "$RUN"/ravenclaude-*/missing-tools.log
  mlog(){ cat "$RUN"/ravenclaude-*/missing-tools.log 2>/dev/null; }
  smsg(){ jq -r '.systemMessage // empty' "$TMP/out" 2>/dev/null; }
  # 14a prompt-optimizer-gate.sh (UserPromptSubmit), opted in, a prompt that reaches Tier 1.
  P14="$(proj po)"; mkdir -p "$P14/.ravenclaude"
  printf 'prompt_optimizer:\n  enabled: true\n  mode: advisory\n' >"$P14/.ravenclaude/comfort-posture.yaml"
  POPL="$(jq -cn '{session_id:"po14",hook_event_name:"UserPromptSubmit",prompt:"Fix the bug in `auth/session.py` and `auth/token.py`."}')"
  drive "$(hook_cmd prompt-optimizer-gate.sh)" "$P14" "$POPL" HOME="$PH"
  if [ "$DRC" -eq 0 ] && smsg | grep -q '`claude` was not found' && grep -q 'WARNING: claude not found' "$TMP/err" \
    && mlog | grep -q 'claude not found hook=prompt-optimizer-gate.sh session=po14'; then
    pass "14a prompt-optimizer-gate.sh: exit 0 + systemMessage + stderr WARNING + missing-tools.log"
  else fail "14a prompt-optimizer-gate.sh rc=$DRC out=$(head -c 200 "$TMP/out") err=$(head -c 200 "$TMP/err")"; fi
  drive "$(hook_cmd prompt-optimizer-gate.sh)" "$P14" "$POPL" HOME="$PH"
  [ ! -s "$TMP/out" ] && grep -q 'WARNING: claude not found' "$TMP/err" \
    && pass "14b same session again: no second systemMessage (once per session), stderr still warns" \
    || fail "14b repeat out=$(head -c 200 "$TMP/out")"
  # 14c agent-dispatch-evaluator.sh (SubagentStart), opted in, a non-allowlisted subagent.
  P14d="$(proj de)"; mkdir -p "$P14d/.ravenclaude"
  printf '{"schema_version":"1","enabled":true,"mode":"shadow","subagent_type_allowlist":[],"rationale":"test"}' >"$P14d/.ravenclaude/dispatch-config.json"
  DEPL="$(jq -cn '{session_id:"de14",hook_event_name:"SubagentStart",subagent_type:"general-purpose",description:"x",prompt:"search the repo"}')"
  drive "$(hook_cmd agent-dispatch-evaluator.sh)" "$P14d" "$DEPL" HOME="$PH"
  if [ "$DRC" -eq 0 ] && smsg | grep -q '`claude` was not found' && grep -q 'WARNING: claude not found' "$TMP/err" \
    && mlog | grep -q 'claude not found hook=agent-dispatch-evaluator.sh session=de14'; then
    pass "14c agent-dispatch-evaluator.sh: exit 0 (audit-only allow) + systemMessage + WARNING + log"
  else fail "14c agent-dispatch-evaluator.sh rc=$DRC out=$(head -c 200 "$TMP/out") err=$(head -c 200 "$TMP/err")"; fi
  # 14d thing-decide.py (decision review), advisory, no mocks: defers and SAYS why.
  P14t="$(proj td)"; mkdir -p "$P14t/.ravenclaude"; printf 'decision_review: advisory\n' >"$P14t/.ravenclaude/comfort-posture.yaml"
  DRC=0
  printf '%s' '{"question":"Should the docs-only change land?","context":"low risk","high_blast":false}' | \
    env -i HOME="$PH" PATH="$BASEPATH" CLAUDE_PROJECT_DIR="$P14t" XDG_RUNTIME_DIR="$RUN" TMPDIR="$TMP" \
    /usr/bin/python3 -I "$DECIDE" --root "$P14t" decide >"$TMP/out" 2>"$TMP/err" || DRC=$?
  if [ "$(jq -r '.verdict' "$TMP/out" 2>/dev/null)" = "defer" ] && jq -r '.reasoning' "$TMP/out" | grep -q 'claude was not found' \
    && grep -q 'WARNING: claude not found' "$TMP/err" && mlog | grep -q 'claude not found hook=thing-decide.py'; then
    pass "14d thing-decide.py: defers, reasoning names claude-not-found, stderr WARNING + log"
  else fail "14d thing-decide.py rc=$DRC out=$(head -c 300 "$TMP/out") err=$(head -c 200 "$TMP/err")"; fi
  # 14e thing-seat.sh: exits 4 (seat abstains) with a WARNING, never the planted claude.
  DRC=0
  env -i HOME="$PH" PATH="$BASEPATH" CLAUDE_PROJECT_DIR="$P14t" XDG_RUNTIME_DIR="$RUN" TMPDIR="$TMP" \
    THING_SEAT_ROLE=mimir THING_CMD="ls -la" \
    /bin/bash --noprofile --norc "$PLUGIN/scripts/thing-seat.sh" </dev/null >"$TMP/out" 2>"$TMP/err" || DRC=$?
  [ "$DRC" -eq 4 ] && grep -q 'WARNING: claude not found' "$TMP/err" \
    && pass "14e thing-seat.sh: exit 4 (abstain) + stderr WARNING" || fail "14e thing-seat.sh rc=$DRC err=$(head -c 200 "$TMP/err")"
  [ ! -e "$MARK/planted" ] && pass "14f the planted \$HOME claude never ran (14a-14e)" || fail "14f planted claude RAN: $(cat "$MARK/planted")"
fi

echo "── 15. declared formatter missing → visible (format-on-write.sh) ──"
if command -v prettier >/dev/null 2>&1 || [ -x /usr/local/bin/prettier ] || [ -x /opt/homebrew/bin/prettier ] \
  || command -v biome >/dev/null 2>&1; then
  pass "15 skipped: prettier/biome is installed on the hook PATH here"
else
  FCMD="$(hook_cmd format-on-write.sh)"
  P15="$(proj fw)"; printf '{"devDependencies":{"prettier":"^3"}}' >"$P15/package.json"; printf 'let a=1\n' >"$P15/a.js"
  FPL="$(jq -cn --arg f "$P15/a.js" '{session_id:"fw15",hook_event_name:"PostToolUse",tool_name:"Write",tool_input:{file_path:$f}}')"
  drive "$FCMD" "$P15" "$FPL"
  [ "$DRC" -eq 0 ] && jq -r '.systemMessage' "$TMP/out" 2>/dev/null | grep -q 'prettier' && grep -q 'WARNING: prettier not found' "$TMP/err" \
    && pass "15a project declares prettier, prettier missing → exit 0 + systemMessage + WARNING" \
    || fail "15a rc=$DRC out=$(head -c 200 "$TMP/out") err=$(head -c 200 "$TMP/err")"
  P15b="$(proj fwq)"; printf 'let a=1\n' >"$P15b/a.js"
  FPL="$(jq -cn --arg f "$P15b/a.js" '{session_id:"fw15b",hook_event_name:"PostToolUse",tool_name:"Write",tool_input:{file_path:$f}}')"
  drive "$FCMD" "$P15b" "$FPL"
  [ "$DRC" -eq 0 ] && [ ! -s "$TMP/out" ] && [ ! -s "$TMP/err" ] \
    && pass "15b project declares no formatter → silent (exit 0, no output)" || fail "15b out=$(head -c 200 "$TMP/out")"
fi

echo "── 15c-15k. format-on-write.sh formats only what the project declares (fake formatters first on PATH) ──"
# A global prettier once rewrote a whole .ts file in a repo with no prettier config
# (2026-10-18). Fake prettier / biome / ruff / black record each call; they sit FIRST
# on the hook's pinned PATH, so `command -v` finds them whether or not real ones exist.
FAKEF="$TMP/fakefmt"; mkdir -p "$FAKEF"
for t in prettier biome ruff black; do
  printf '#!/bin/sh\necho "%s $*" >>"%s/fmt-calls"\nexit 0\n' "$t" "$MARK" >"$FAKEF/$t"; chmod +x "$FAKEF/$t"
done
FWCMD="$(hook_cmd format-on-write.sh | sed "s|PATH=$BASEPATH |PATH=$FAKEF:$BASEPATH |")"
case "$FWCMD" in *"PATH=$FAKEF:"*) pass "15c setup: fake formatters are first on the hook's PATH" ;;
  *) fail "15c setup: could not put the fake formatters on the hook PATH: ${FWCMD:0:160}" ;; esac
fcalls(){ cat "$MARK/fmt-calls" 2>/dev/null; }
# fw <proj> <file> -- run the real hook command on <file> as a PostToolUse(Write)
fw(){ rm -f "$MARK/fmt-calls"
  drive "$FWCMD" "$1" "$(jq -cn --arg f "$2" '{session_id:"fw15c",hook_event_name:"PostToolUse",tool_name:"Write",tool_input:{file_path:$f}}')"; }

P15c="$(proj fwnone)"; printf 'const a = 1\n' >"$P15c/a.ts"
fw "$P15c" "$P15c/a.ts"
[ "$DRC" -eq 0 ] && [ -z "$(fcalls)" ] && [ ! -s "$TMP/out" ] \
  && pass "15d no prettier config, prettier on PATH → prettier NOT run, silent, exit 0" \
  || fail "15d undeclared project ran a formatter: calls='$(fcalls)' rc=$DRC out=$(head -c 120 "$TMP/out")"

P15e="$(proj fwrc)"; printf '{}\n' >"$P15e/.prettierrc"; printf 'const a = 1\n' >"$P15e/a.ts"
fw "$P15e" "$P15e/a.ts"
[ "$DRC" -eq 0 ] && fcalls | grep -q "^prettier --write .*/a.ts$" \
  && pass "15e .prettierrc at the project root → prettier --write <file>" \
  || fail "15e calls='$(fcalls)' rc=$DRC"

P15f="$(proj fwmono)"; mkdir -p "$P15f/packages/web/src" "$P15f/packages/api/src"
printf 'semi: false\n' >"$P15f/packages/web/.prettierrc.yaml"
printf 'const a = 1\n' >"$P15f/packages/web/src/a.ts"; printf 'const b = 1\n' >"$P15f/packages/api/src/b.ts"
fw "$P15f" "$P15f/packages/web/src/a.ts"
fcalls | grep -q "^prettier --write .*/packages/web/src/a.ts$" \
  && pass "15f monorepo: config only in the subpackage above the file → prettier runs" \
  || fail "15f subpackage config not found by the upward walk: calls='$(fcalls)'"
fw "$P15f" "$P15f/packages/api/src/b.ts"
[ -z "$(fcalls)" ] && pass "15g monorepo control: a sibling package with no config → not run (the walk goes up, not sideways)" \
  || fail "15g sibling package ran prettier: calls='$(fcalls)'"

P15h="$(proj fwpkg)"; printf '{"name":"x","devDependencies":{"prettier":"^3.3.0"}}\n' >"$P15h/package.json"
printf 'const a = 1\n' >"$P15h/a.ts"
fw "$P15h" "$P15h/a.ts"
fcalls | grep -q "^prettier --write .*/a.ts$" \
  && pass "15h package.json lists \"prettier\" in devDependencies → prettier runs" \
  || fail "15h calls='$(fcalls)'"

P15i="$(proj fwbiome)"; printf '{}\n' >"$P15i/biome.json"; printf 'const a = 1\n' >"$P15i/a.ts"
fw "$P15i" "$P15i/a.ts"
fcalls | grep -q "^biome format --write .*/a.ts$" && ! fcalls | grep -q '^prettier' \
  && pass "15i biome.json declared → biome runs (not prettier)" || fail "15i calls='$(fcalls)'"

P15j="$(proj fwpy)"; printf 'x=1\n' >"$P15j/a.py"
fw "$P15j" "$P15j/a.py"
[ -z "$(fcalls)" ] && pass "15j Python, no ruff/black config, both on PATH → neither runs" || fail "15j calls='$(fcalls)'"
printf '[tool.ruff]\nline-length = 100\n' >"$P15j/pyproject.toml"
fw "$P15j" "$P15j/a.py"
fcalls | grep -q "^ruff format .*/a.py$" && fcalls | grep -q "^ruff check --fix" && ! fcalls | grep -q '^black' \
  && pass "15j' [tool.ruff] in pyproject.toml → ruff format + ruff check --fix" || fail "15j' calls='$(fcalls)'"
printf '[tool.black]\nline-length = 100\n' >"$P15j/pyproject.toml"
fw "$P15j" "$P15j/a.py"
fcalls | grep -q "^black --quiet .*/a.py$" && ! fcalls | grep -q '^ruff' \
  && pass "15j'' [tool.black] only → black runs, ruff does not" || fail "15j'' calls='$(fcalls)'"

# A file in ANOTHER checkout (a worktree beside the project): the walk stops at that
# checkout's .git, so its own config counts and the project's does not leak in.
P15k="$(proj fwproj)"; printf '{}\n' >"$P15k/.prettierrc"
WT="$TMP/p-fwother"; mkdir -p "$WT/src"; git -C "$WT" init -q 2>/dev/null; printf 'const a = 1\n' >"$WT/src/a.ts"
fw "$P15k" "$WT/src/a.ts"
[ -z "$(fcalls)" ] && pass "15k file in another checkout with no config → not run (project's .prettierrc does not apply)" \
  || fail "15k calls='$(fcalls)'"
printf '{}\n' >"$WT/.prettierrc"
fw "$P15k" "$WT/src/a.ts"
fcalls | grep -q "^prettier --write .*/src/a.ts$" \
  && pass "15k' that checkout declares prettier at its .git root → prettier runs" || fail "15k' calls='$(fcalls)'"
rm -f "$MARK/fmt-calls"

echo "── 16. caveman_routing: live, node missing → visible (caveman-route-hook.sh) ──"
NN="$TMP/nonode"; mkdir -p "$NN"
for d in /usr/bin /bin; do for f in "$d"/*; do b="${f##*/}"; [ "$b" = node ] || [ -e "$NN/$b" ] || ln -s "$f" "$NN/$b" 2>/dev/null; done; done
P16="$(proj cv)"; mkdir -p "$P16/.ravenclaude"; printf 'caveman_routing: live\n' >"$P16/.ravenclaude/comfort-posture.yaml"
CPL="$(jq -cn '{session_id:"cv16",hook_event_name:"UserPromptSubmit",prompt:"hello there"}')"
CCMD="$(hook_cmd 'caveman-route-hook.sh" --event prompt' | sed "s|PATH=$BASEPATH |PATH=$NN |")"
drive "$CCMD" "$P16" "$CPL"
[ "$DRC" -eq 0 ] && jq -r '.systemMessage' "$TMP/out" 2>/dev/null | grep -q '`node` was not found' && grep -q 'WARNING: node not found' "$TMP/err" \
  && pass "16a live caveman routing without node → exit 0 + systemMessage + WARNING" \
  || fail "16a rc=$DRC out=$(head -c 200 "$TMP/out") err=$(head -c 300 "$TMP/err")"
printf 'caveman_routing: shadow\n' >"$P16/.ravenclaude/comfort-posture.yaml"
drive "$CCMD" "$P16" "$(jq -cn '{session_id:"cv16b",hook_event_name:"UserPromptSubmit",prompt:"hello"}')"
[ "$DRC" -eq 0 ] && ! grep -q 'node not found' "$TMP/err" && ! grep -q 'node' "$TMP/out" \
  && pass "16b shadow mode (never applies) → no node warning" || fail "16b out=$(head -c 200 "$TMP/out")"

echo "── 17. this repo's own settings carry no env block and pass the guard ──"
if [ -f "$REPO/.claude/settings.json" ] && [ -d "$REPO/plugins/ravenclaude-core" ]; then
  jq -e 'has("env") | not' "$REPO/.claude/settings.json" >/dev/null 2>&1 \
    && pass "17a .claude/settings.json has no env block (RAVENCLAUDE_* moved out; strict guard, no allowlist)" \
    || fail "17a .claude/settings.json still has an env block"
  drive "$GSES" "$REPO" '{"session_id":"self17","hook_event_name":"SessionStart","source":"startup"}'
  ! denied && ! grep -qi quarantin "$TMP/out" "$TMP/err" && pass "17b the guard does not quarantine this repo" \
    || fail "17b guard quarantined this repo: $(head -c 200 "$TMP/out")"
  jq -e '[.hooks.SessionStart[]?.hooks[]?.command | select(test("env-integrity-guard.sh"))] | length == 1' "$REPO/.claude/settings.json" >/dev/null \
    && pass "17c the dev mirror runs env-integrity-guard.sh at SessionStart (parity re-enabled)" || fail "17c guard not mirrored"
else
  pass "17 skipped: not running inside the RavenClaude repo"
fi

echo "── 12. platform ──"
case "$(uname -s)" in
  Darwin) pass "12 running on macOS ($(/bin/bash --version | head -1 | sed 's/.*version \([0-9.]*\).*/\1/'))" ;;
  *) pass "12 $(uname -s): macOS not exercised here — the gate audit's macos-latest shards (validate-macos.yml) run this file" ;;
esac

echo
echo "test-hook-env-hardening: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
