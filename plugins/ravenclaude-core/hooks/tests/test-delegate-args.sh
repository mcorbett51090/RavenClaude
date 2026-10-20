#!/usr/bin/env bash
# test-delegate-args.sh — the cheap-lane delegates (grok-delegate.sh,
# copilot-delegate.sh, cheap-lane-delegate.sh). 2026-10-19 repo review:
#
#   A1 corescripts-10  a value-taking flag given LAST exits 2, never hangs
#                      (`shift 2` past $# is a silent no-op under set -uo pipefail)
#   A2 scripts-10      SIGINT / SIGTERM stop the script (130 / 143) and the
#                      cleanup trap runs EXACTLY once
#   A3 corescripts-11  with hooks/_scrub.sh absent the script exits 8 before any
#                      egress (the vendor CLI is never invoked)
#   A4 corescripts-29  a benign task ending in a newline is not refused as
#                      secret-shaped; a secret-shaped task still is
#   A5 corescripts-1   a kebab-case task (a ta+sk- name) is not refused
#
# Each fix has a teeth mutant built in a scratch copy: reverting it must turn the
# matching assertion red. Vendor CLIs are stubs on PATH; nothing leaves the host.
# Synthetic secrets are built by concatenation.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE="$(cd "$HERE/../.." && pwd)"
SCRIPTS="$CORE/scripts"
# shellcheck source=/dev/null
. "$CORE/hooks/_portable.sh"
command -v _rc_timeout >/dev/null 2>&1 || { echo "FATAL: _rc_timeout unavailable" >&2; exit 1; }
command -v perl >/dev/null 2>&1 || { echo "FATAL: perl is needed to deliver SIGINT" >&2; exit 1; }
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  ok   %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  FAIL %s\n' "$1"; }

# Stub vendor CLIs: record that they ran, optionally sleep, print a result.
mkdir -p "$TMP/bin"
for cli in grok copilot; do
  cat > "$TMP/bin/$cli" <<'STUB'
#!/usr/bin/env bash
[ -n "${STUB_MARK:-}" ] && : > "$STUB_MARK"
sleep "${STUB_SLEEP:-0}"
echo stub-ok
STUB
  chmod +x "$TMP/bin/$cli"
done
export PATH="$TMP/bin:$PATH"
unset RAVENCLAUDE_GROK_ACTIVE RAVENCLAUDE_COPILOT_ACTIVE THING_SEAT_ACTIVE 2>/dev/null || true

# A scratch plugin tree holding a copy of one delegate, so a mutant or a missing
# helper never touches the real files. $1 = delegate name, $2 = with _scrub.sh (1/0)
tree() {
  local d="$TMP/tree-$1-$RANDOM"
  mkdir -p "$d/scripts" "$d/hooks" "$d/knowledge"
  cp "$SCRIPTS/$1" "$d/scripts/"
  cp "$CORE/hooks/_portable.sh" "$d/hooks/"
  [ "$2" = 1 ] && cp "$CORE/hooks/_scrub.sh" "$d/hooks/"
  [ -f "$CORE/knowledge/substrate-tier-map.json" ] && cp "$CORE/knowledge/substrate-tier-map.json" "$d/knowledge/"
  # instrument cleanup so its runs can be counted
  sed 's/^_cleanup() { /_cleanup() { echo run >> "${CLEANUP_LOG:-\/dev\/null}"; /' \
    "$d/scripts/$1" > "$d/scripts/$1.tmp" && mv "$d/scripts/$1.tmp" "$d/scripts/$1"
  printf '%s' "$d"
}

echo "── A1: a value flag given last exits 2 (no hang) ────────────────────────"
for flag in --task --task-file --tier --mode --repo --timeout --max-turns --effort; do
  rc=0; _rc_timeout 4 bash "$SCRIPTS/grok-delegate.sh" "$flag" >/dev/null 2>"$TMP/err" || rc=$?
  if [ "$rc" = 2 ] && grep -q "requires a value" "$TMP/err"; then ok "grok $flag (last) -> rc 2"
  else bad "grok $flag (last) -> rc $rc (124/142 = hung)"; fi
done
for flag in --task --task-file --tier --mode --repo --timeout --effort --model; do
  rc=0; _rc_timeout 4 bash "$SCRIPTS/copilot-delegate.sh" "$flag" >/dev/null 2>"$TMP/err" || rc=$?
  [ "$rc" = 2 ] && ok "copilot $flag (last) -> rc 2" || bad "copilot $flag (last) -> rc $rc"
done
rc=0; _rc_timeout 4 bash "$SCRIPTS/cheap-lane-delegate.sh" --agent grok --task >/dev/null 2>&1 || rc=$?
[ "$rc" = 2 ] && ok "cheap-lane-delegate --agent grok --task (last) -> rc 2" \
  || bad "cheap-lane-delegate --agent grok --task -> rc $rc"
# teeth: without the guard the trailing flag spins until the bound kills it.
d="$(tree grok-delegate.sh 1)"
sed 's/_need_value \$# "\$1"; //' "$d/scripts/grok-delegate.sh" > "$d/scripts/mut.sh"
rc=0; _rc_timeout 2 bash "$d/scripts/mut.sh" --task >/dev/null 2>&1 || rc=$?
[ "$rc" != 2 ] && ok "[teeth] guard removed -> --task (last) no longer exits 2 (rc $rc)" \
  || bad "[teeth] guard removed and --task still exits 2: A1 measures nothing"

# Launch a delegate in the background with SIGINT reset to default (a background
# job in a non-interactive shell starts with SIGINT ignored, and a signal ignored
# on entry cannot be trapped), send $2, and report "<rc> <cleanup-runs>".
sigrun() {  # $1 = script path, $2 = INT|TERM
  local log="$TMP/cleanup.$RANDOM" pid rc=0
  : > "$log"
  CLEANUP_LOG="$log" STUB_SLEEP=2 \
    perl -e '$SIG{INT}="DEFAULT"; $SIG{TERM}="DEFAULT"; exec @ARGV' \
    bash "$1" --task "summarise the readme" >/dev/null 2>&1 &
  pid=$!
  sleep 1
  kill "-$2" "$pid" 2>/dev/null
  wait "$pid" || rc=$?
  printf '%s %s' "$rc" "$(grep -c run "$log")"
}

echo "── A2: SIGINT/SIGTERM stop the script; cleanup runs once ────────────────"
for name in grok-delegate.sh copilot-delegate.sh; do
  d="$(tree "$name" 1)"
  r="$(sigrun "$d/scripts/$name" INT)"
  [ "$r" = "130 1" ] && ok "$name: SIGINT -> rc 130, cleanup once" || bad "$name: SIGINT -> rc/cleanups = $r"
  r="$(sigrun "$d/scripts/$name" TERM)"
  [ "$r" = "143 1" ] && ok "$name: SIGTERM -> rc 143, cleanup once" || bad "$name: SIGTERM -> rc/cleanups = $r"
  # teeth: the old shared trap resumes after the handler and cleans up twice.
  sed -e "/^trap 'exit 130' INT\$/d" -e "/^trap 'exit 143' TERM\$/d" \
      -e 's/^trap _cleanup EXIT$/trap _cleanup EXIT INT TERM/' \
      "$d/scripts/$name" > "$d/scripts/old-trap.sh"
  if grep -q '^trap _cleanup EXIT INT TERM$' "$d/scripts/old-trap.sh"; then
    r="$(sigrun "$d/scripts/old-trap.sh" INT)"
    [ "$r" != "130 1" ] && ok "$name: [teeth] old shared trap -> $r (not 130 1)" \
      || bad "$name: [teeth] old shared trap still gives 130 1: A2 measures nothing"
  else
    bad "$name: [teeth] could not rebuild the old trap line"
  fi
done

SKD="s""k-"
SECRET="deploy with AK""IA""ABCDEFGHIJKLMNOP"
echo "── A3: hooks/_scrub.sh absent -> exit 8, nothing sent ───────────────────"
for name in grok-delegate.sh copilot-delegate.sh; do
  d="$(tree "$name" 0)"
  mark="$TMP/mark-$name"; rm -f "$mark"
  rc=0; STUB_MARK="$mark" _rc_timeout 10 bash "$d/scripts/$name" --task "$SECRET" >/dev/null 2>&1 || rc=$?
  if [ "$rc" = 8 ] && [ ! -e "$mark" ]; then ok "$name: no scrub helper -> rc 8, vendor CLI never ran"
  else bad "$name: no scrub helper -> rc $rc, vendor ran: $([ -e "$mark" ] && echo yes || echo no)"; fi
  # teeth: without the fail-closed line the secret-shaped task is sent.
  awk '/^command -v _scrub_reason >\/dev\/null 2>&1 \|\| \{$/ {skip=2} skip {skip--; next} {print}' \
    "$d/scripts/$name" > "$d/scripts/open.sh"
  rm -f "$mark"
  rc=0; STUB_MARK="$mark" _rc_timeout 10 bash "$d/scripts/open.sh" --task "$SECRET" >/dev/null 2>&1 || rc=$?
  [ -e "$mark" ] && ok "$name: [teeth] fail-closed line removed -> the secret task is sent (rc $rc)" \
    || bad "$name: [teeth] removing the fail-closed line changed nothing: A3 measures nothing"
done

echo "── A4/A5: newline-terminated and kebab tasks are not refused ────────────"
for name in grok-delegate.sh copilot-delegate.sh; do
  rc=0; _rc_timeout 10 bash "$SCRIPTS/$name" --task "summarise this file
" >/dev/null 2>&1 || rc=$?
  [ "$rc" = 0 ] && ok "$name: a task ending in a newline is not refused" || bad "$name: newline task -> rc $rc"
  rc=0; _rc_timeout 10 bash "$SCRIPTS/$name" --task "refactor the ta${SKD}management-and-planning module" \
    >/dev/null 2>&1 || rc=$?
  [ "$rc" = 0 ] && ok "$name: a ta+sk- kebab task is not refused" || bad "$name: kebab task -> rc $rc"
  rc=0; _rc_timeout 10 bash "$SCRIPTS/$name" --task "$SECRET" >/dev/null 2>&1 || rc=$?
  [ "$rc" = 8 ] && ok "$name: a secret-shaped task is still refused (rc 8)" || bad "$name: secret task -> rc $rc"
  d="$(tree "$name" 1)"
  sed 's/\[ "\$_scrubbed" != "\$_task_cmp" \]/[ "$_scrubbed" != "$task" ]/' \
    "$d/scripts/$name" > "$d/scripts/nl.sh"
  rc=0; _rc_timeout 10 bash "$d/scripts/nl.sh" --task "summarise this file
" >/dev/null 2>&1 || rc=$?
  [ "$rc" = 8 ] && ok "$name: [teeth] raw comparison refuses the newline task (rc 8)" \
    || bad "$name: [teeth] raw comparison gave rc $rc: A4 measures nothing"
done

printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
