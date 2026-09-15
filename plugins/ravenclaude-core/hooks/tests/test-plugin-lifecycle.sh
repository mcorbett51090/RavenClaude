#!/usr/bin/env bash
# test-plugin-lifecycle.sh — audit fixture for the plugin-lifecycle ledger
# (scripts/plugin-lifecycle.py + the sweep/telemetry hook bodies).
#
# Drives the REAL engine + REAL hook bodies against throwaway mktemp projects,
# proving the Matthew locks (M1-M7) and the AppSec SHIP-WITH-CONDITIONS hold:
#
#   TRACK  telemetry bumps last_used on skill / agent / slash …
#   NOSS   … but a SessionStart sweep NEVER bumps last_used (presence != use)
#   M2     auto_uninstall OFF  => would_uninstall is EMPTY (zero uninstalls)
#   M3     ravenclaude-core is NEVER in would_uninstall, even with
#          auto_uninstall ON + empty pins + an ancient timestamp
#   PIN    a pinned plugin is skipped from uninstall
#   MID    a plugin used THIS session (mid-flight) is skipped (AppSec #2)
#   ASK    ask-install: off => CTA; ask + cited need => confirm; ask, no
#          citation => CTA (AppSec #6, no empty-cited install)
#   ALLOW  allowlist rejects a non-ravenclaude marketplace / bad install path (M4)
#   NORG   the sweep hook body NEVER references the cache-reset DR command (#7)
#   JAIL   a symlinked .ravenclaude / ledger is refused (path jail, no escape)
#   MF     teeth — neuter the core hard-pin and assert core THEN appears in
#          would_uninstall, proving M3 is real code and not a vacuous pass
#
# Self-contained: every fixture is a throwaway mktemp project. Run directly:
#   bash plugins/ravenclaude-core/hooks/tests/test-plugin-lifecycle.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENGINE="$PLUGIN_ROOT/scripts/plugin-lifecycle.py"
SWEEP="$PLUGIN_ROOT/scripts/plugin-lifecycle-sweep.sh"
TELEMETRY="$PLUGIN_ROOT/scripts/plugin-lifecycle-telemetry.sh"

PASS=0
FAIL=0
pass() {
  printf '  \033[32m✓\033[0m %s\n' "$1"
  PASS=$((PASS + 1))
}
fail() {
  printf '  \033[31m✗\033[0m %s\n' "$1"
  FAIL=$((FAIL + 1))
}

[ -f "$ENGINE" ] || {
  echo "FAIL: engine not found at $ENGINE"
  exit 1
}

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PY() { python3 "$ENGINE" "$@"; }

# mk_project <name> [tracking] [auto_uninstall] [auto_install] [pins-inline]
mk_project() {
  local d="$TMP/$1"
  mkdir -p "$d/.ravenclaude"
  {
    printf 'schema_version: 5\n'
    printf 'plugin_lifecycle:\n'
    printf '  tracking: %s\n' "${2:-on}"
    printf '  unused_days: 90\n'
    printf '  auto_uninstall: %s\n' "${3:-off}"
    printf '  auto_install: %s\n' "${4:-off}"
    printf '  pins: %s\n' "${5:-[]}"
  } >"$d/.ravenclaude/comfort-posture.yaml"
  printf '%s' "$d"
}

# An ISO timestamp well past the 90-day window (fixed, so tests are deterministic).
OLD_TS="2020-01-01T00:00:00Z"
NOW_TS="2026-09-15T12:00:00Z"

json_get() { python3 -c "import json,sys;print(json.load(sys.stdin)$1)"; }

echo "── plugin-lifecycle: ledger engine + hooks ──────────────────────────────"

# ── TRACK: telemetry bumps last_used on skill / agent / slash ────────────────
p="$(mk_project track)"
PY --project "$p" record --plugin api-engineering --signal skill >/dev/null
sig="$(PY --project "$p" list --json | json_get "['plugins']['api-engineering@ravenclaude']['last_used_signal']")"
[ "$sig" = "skill" ] && pass "TRACK skill signal recorded" || fail "TRACK skill: got '$sig'"

PY --project "$p" record --plugin power-platform --signal agent >/dev/null
sig="$(PY --project "$p" list --json | json_get "['plugins']['power-platform@ravenclaude']['last_used_signal']")"
[ "$sig" = "agent" ] && pass "TRACK agent signal recorded" || fail "TRACK agent: got '$sig'"

PY --project "$p" record --plugin finance --signal slash >/dev/null
sig="$(PY --project "$p" list --json | json_get "['plugins']['finance@ravenclaude']['last_used_signal']")"
[ "$sig" = "slash" ] && pass "TRACK slash signal recorded" || fail "TRACK slash: got '$sig'"

# telemetry hook body: an Agent payload records the plugin from subagent_type
if [ -f "$TELEMETRY" ]; then
  echo '{"tool_name":"Agent","tool_input":{"subagent_type":"api-engineering:api-design-architect"}}' \
    | env CLAUDE_PROJECT_DIR="$p" bash "$TELEMETRY" >/dev/null 2>&1
  sig="$(PY --project "$p" list --json | json_get "['plugins']['api-engineering@ravenclaude']['last_used_signal']")"
  [ "$sig" = "agent" ] && pass "TRACK telemetry Agent payload -> agent" || fail "TRACK telemetry Agent: got '$sig'"

  # a built-in agent (no plugin namespace) is a no-op — no row created
  echo '{"tool_name":"Agent","tool_input":{"subagent_type":"general-purpose"}}' \
    | env CLAUDE_PROJECT_DIR="$p" bash "$TELEMETRY" >/dev/null 2>&1
  has="$(PY --project "$p" list --json | json_get ".get('plugins',{}).get('general-purpose@ravenclaude') is not None")"
  [ "$has" = "False" ] && pass "TRACK telemetry ignores built-in (no namespace)" || fail "TRACK telemetry recorded a namespaceless agent"
else
  fail "TRACK telemetry hook body missing at $TELEMETRY"
fi

# ── NOSS: a SessionStart sweep NEVER bumps last_used (presence != use) ────────
p="$(mk_project noss)"
PY --project "$p" seed --plugins finance --installed-at "$OLD_TS" >/dev/null
before="$(PY --project "$p" list --json | json_get "['plugins']['finance@ravenclaude']['last_used_at']")"
PY --project "$p" sweep-hook --now "$NOW_TS" >/dev/null
after="$(PY --project "$p" list --json | json_get "['plugins']['finance@ravenclaude']['last_used_at']")"
[ "$before" = "$after" ] && pass "NOSS sweep leaves last_used_at unchanged (not a use)" || fail "NOSS sweep bumped last_used ($before -> $after)"
after_sig="$(PY --project "$p" list --json | json_get "['plugins']['finance@ravenclaude']['last_used_signal']")"
[ "$after_sig" = "seed" ] && pass "NOSS sweep leaves last_used_signal unchanged" || fail "NOSS sweep changed signal to '$after_sig'"

# ── M2: auto_uninstall OFF => would_uninstall empty ──────────────────────────
p="$(mk_project m2 on off off '[]')"
PY --project "$p" seed --plugins finance,edtech --installed-at "$OLD_TS" >/dev/null
n="$(PY --project "$p" sweep-plan --now "$NOW_TS" --assume-no-deps --json | json_get "['would_uninstall'].__len__()")"
[ "$n" = "0" ] && pass "M2 auto_uninstall OFF => 0 would_uninstall (even with --assume-no-deps)" || fail "M2 got $n would_uninstall with auto_uninstall off"
dep="$(PY --project "$p" sweep-plan --now "$NOW_TS" --json | json_get "['deprecated'].__len__()")"
[ "$dep" = "2" ] && pass "M2 deprecated still computed + surfaced (notice always)" || fail "M2 deprecated count $dep (expected 2)"

# ── M3: core is NEVER in would_uninstall (auto ON, empty pins, ancient ts) ───
p="$(mk_project m3 on on off '[]')"
PY --project "$p" seed --plugins ravenclaude-core,finance --installed-at "$OLD_TS" >/dev/null
plan="$(PY --project "$p" sweep-plan --now "$NOW_TS" --assume-no-deps --json)"
core_in_wu="$(printf '%s' "$plan" | python3 -c "import json,sys;d=json.load(sys.stdin);print('ravenclaude-core@ravenclaude' in d['would_uninstall'])")"
[ "$core_in_wu" = "False" ] && pass "M3 core NOT in would_uninstall (auto on + empty pins)" || fail "M3 CORE WOULD BE UNINSTALLED"
core_dep="$(printf '%s' "$plan" | python3 -c "import json,sys;d=json.load(sys.stdin);print('ravenclaude-core@ravenclaude' in d['deprecated'])")"
[ "$core_dep" = "False" ] && pass "M3 core never marked deprecated" || fail "M3 core marked deprecated"
core_skip="$(printf '%s' "$plan" | python3 -c "import json,sys;d=json.load(sys.stdin);print('ravenclaude-core@ravenclaude' in d['skipped']['core'])")"
[ "$core_skip" = "True" ] && pass "M3 core surfaced in skipped.core (hard pin documented)" || fail "M3 core not in skipped.core"
fin_wu="$(printf '%s' "$plan" | python3 -c "import json,sys;d=json.load(sys.stdin);print('finance@ravenclaude' in d['would_uninstall'])")"
[ "$fin_wu" = "True" ] && pass "M3 a non-core eligible plugin DOES reach would_uninstall (control)" || fail "M3 finance not eligible — cannot prove core exclusion is meaningful"

# ── PIN: a pinned plugin is skipped ──────────────────────────────────────────
p="$(mk_project pin on on off '[finance]')"
PY --project "$p" seed --plugins finance,edtech --installed-at "$OLD_TS" >/dev/null
plan="$(PY --project "$p" sweep-plan --now "$NOW_TS" --assume-no-deps --json)"
fin_pin="$(printf '%s' "$plan" | python3 -c "import json,sys;d=json.load(sys.stdin);print('finance@ravenclaude' in d['skipped']['pinned'])")"
[ "$fin_pin" = "True" ] && pass "PIN pinned plugin in skipped.pinned" || fail "PIN pinned plugin not skipped"
fin_wu="$(printf '%s' "$plan" | python3 -c "import json,sys;d=json.load(sys.stdin);print('finance@ravenclaude' in d['would_uninstall'])")"
[ "$fin_wu" = "False" ] && pass "PIN pinned plugin NOT in would_uninstall" || fail "PIN pinned plugin would be uninstalled"

# ── MID: a plugin used this session is skipped (AppSec #2) ────────────────────
p="$(mk_project mid on on off '[]')"
PY --project "$p" seed --plugins finance --installed-at "$OLD_TS" >/dev/null
plan="$(PY --project "$p" sweep-plan --now "$NOW_TS" --assume-no-deps --session-used finance@ravenclaude --json)"
fin_mid="$(printf '%s' "$plan" | python3 -c "import json,sys;d=json.load(sys.stdin);print('finance@ravenclaude' in d['skipped']['mid_flight'])")"
[ "$fin_mid" = "True" ] && pass "MID mid-flight plugin in skipped.mid_flight" || fail "MID mid-flight plugin not skipped"
fin_wu="$(printf '%s' "$plan" | python3 -c "import json,sys;d=json.load(sys.stdin);print('finance@ravenclaude' in d['would_uninstall'])")"
[ "$fin_wu" = "False" ] && pass "MID mid-flight plugin NOT in would_uninstall" || fail "MID mid-flight plugin would be uninstalled"

# ── FAILCLOSED: without --assume-no-deps, unknown requires => not uninstalled ─
p="$(mk_project failclosed on on off '[]')"
PY --project "$p" seed --plugins finance --installed-at "$OLD_TS" >/dev/null
plan="$(PY --project "$p" sweep-plan --now "$NOW_TS" --json)"
uk="$(printf '%s' "$plan" | python3 -c "import json,sys;d=json.load(sys.stdin);print('finance@ravenclaude' in d['skipped']['unknown_requires'])")"
wu="$(printf '%s' "$plan" | python3 -c "import json,sys;d=json.load(sys.stdin);print(len(d['would_uninstall']))")"
[ "$uk" = "True" ] && [ "$wu" = "0" ] && pass "FAILCLOSED unknown requires => skipped, 0 uninstalls (default, no dep resolver)" || fail "FAILCLOSED did not fail closed (uk=$uk wu=$wu)"

# ── ASK: ask-install modes (M5, AppSec #5/#6) ────────────────────────────────
p="$(mk_project askoff on off off '[]')"
mode="$(PY --project "$p" ask-install --plugin finance --json | json_get "['mode']")"
[ "$mode" = "cta" ] && pass "ASK auto_install off => CTA (Bifröst only)" || fail "ASK off got mode '$mode'"

p="$(mk_project askask on off ask '[]')"
out="$(PY --project "$p" ask-install --plugin finance --need "user asked for finance memo" --json)"
mode="$(printf '%s' "$out" | json_get "['mode']")"
conf="$(printf '%s' "$out" | json_get "['confirm_required']")"
rel="$(printf '%s' "$out" | json_get "['reload_cmd']")"
[ "$mode" = "ask" ] && [ "$conf" = "True" ] && [ "$rel" = "/reload-plugins" ] && pass "ASK ask + cited need => confirm path w/ reload reminder" || fail "ASK confirm path wrong (mode=$mode conf=$conf rel=$rel)"

mode="$(PY --project "$p" ask-install --plugin finance --json | json_get "['mode']")"
[ "$mode" = "cta" ] && pass "ASK ask WITHOUT a cited need => CTA (AppSec #6, no empty-cited install)" || fail "ASK uncited got mode '$mode'"

# ── ALLOW: allowlist rejects non-ravenclaude marketplace / bad path (M4) ─────
p="$(mk_project allow)"
PY --project "$p" allowlist-check --plugin evil --marketplace sketchy >/dev/null 2>&1
rc=$?
[ "$rc" -eq 3 ] && pass "ALLOW non-ravenclaude marketplace rejected (exit 3)" || fail "ALLOW non-ravenclaude not rejected (rc=$rc)"
PY --project "$p" allowlist-check --plugin finance --marketplace ravenclaude >/dev/null 2>&1
rc=$?
[ "$rc" -eq 0 ] && pass "ALLOW ravenclaude marketplace allowed (exit 0)" || fail "ALLOW ravenclaude rejected (rc=$rc)"
PY --project "$p" allowlist-check --plugin finance --marketplace ravenclaude --install-path /home/x/.claude/plugins/cache/ravenclaude/finance/1.0.0 >/dev/null 2>&1
rc=$?
[ "$rc" -eq 0 ] && pass "ALLOW ravenclaude + cache path allowed (AppSec #4)" || fail "ALLOW ravenclaude cache path rejected (rc=$rc)"
PY --project "$p" allowlist-check --plugin finance --marketplace ravenclaude --install-path /tmp/evil/finance >/dev/null 2>&1
rc=$?
[ "$rc" -eq 3 ] && pass "ALLOW ravenclaude + non-cache path rejected (AppSec #4)" || fail "ALLOW bad install path not rejected (rc=$rc)"

# ── NORG: the sweep hook body never references the cache-reset DR command (#7)─
if [ -f "$SWEEP" ]; then
  # needle deliberately carries no '--execute' token (would trip the DR concern)
  if grep -Eiq 'ragnarok|reset-plugin-cache' "$SWEEP"; then
    fail "NORG sweep body references the cache-reset DR command (AppSec #7 violated)"
  else
    pass "NORG sweep body has zero cache-reset DR references (AppSec #7)"
  fi
else
  fail "NORG sweep hook body missing at $SWEEP"
fi

# ── JAIL: a symlinked .ravenclaude is refused (path jail, no escape) ─────────
JAILBASE="$TMP/jailproj"
mkdir -p "$JAILBASE"
mkdir -p "$TMP/outside"
ln -s "$TMP/outside" "$JAILBASE/.ravenclaude"
PY --project "$JAILBASE" list --json >/dev/null 2>&1
rc=$?
[ "$rc" -eq 4 ] && pass "JAIL symlinked .ravenclaude refused (exit 4)" || fail "JAIL symlink NOT refused (rc=$rc)"

# ── MF teeth: neuter is_core_key entirely; core must THEN reach would_uninstall.
# is_core_key protects core in FOUR ways (excluded from deprecated, from the
# uninstall loop, auto-pinned at seed, surfaced in skipped.core). Neutering the
# one function collapses all four, so we must SEED with the mutant too (else the
# real engine's auto-pin persists in the ledger). If core still can't be removed
# after that, the M3 passes above are vacuous.
MUTANT="$TMP/mutant-engine.py"
sed -e 's/^    return plugin_of(key) == CORE_PLUGIN$/    return False/' "$ENGINE" >"$MUTANT"
if cmp -s "$ENGINE" "$MUTANT"; then
  fail "MF teeth: the mutation did not apply (re-target the sed)"
else
  p="$(mk_project mf on on off '[]')"
  python3 "$MUTANT" --project "$p" seed --plugins ravenclaude-core --installed-at "$OLD_TS" >/dev/null
  core_wu="$(python3 "$MUTANT" --project "$p" sweep-plan --now "$NOW_TS" --assume-no-deps --json | python3 -c "import json,sys;d=json.load(sys.stdin);print('ravenclaude-core@ravenclaude' in d['would_uninstall'])")"
  if [ "$core_wu" = "True" ]; then
    pass "MF teeth: neutering is_core_key makes core uninstallable (M3 is real code)"
  else
    fail "MF teeth: core still excluded with is_core_key neutered — the M3 pass is vacuous"
  fi
fi

echo
if [ "$FAIL" -gt 0 ]; then
  printf '  \033[31m%d pass, %d fail\033[0m\n' "$PASS" "$FAIL"
  exit 1
fi
printf '  \033[32m%d pass, 0 fail\033[0m\n' "$PASS"
exit 0
