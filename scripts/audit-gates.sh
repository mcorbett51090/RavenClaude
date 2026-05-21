#!/usr/bin/env bash
# audit-gates.sh — prove every CI gate can fail on a known-bad fixture
# AND pass on a known-good fixture.
#
# Rule: docs/best-practices/ci-gate-audit.md
# Why:  a CI step that runs is not necessarily a CI step that gates.
#       A CI step that gates can gate the wrong thing. Both failure modes
#       are invisible from inside a green CI dashboard.
#
# How:  for each gate in .github/workflows/, this script defines two
#       fixtures (must_fail_on, must_pass_on), exercises the underlying
#       check, and reports per-gate verdicts. Exits nonzero if any gate
#       failed its audit.
#
# When: (a) on every PR via CI, (b) locally before adding/changing any
#       gate. New gates must add a fixture-pair here in the same PR.
#
# Idempotent: backs up any file it temporarily mutates and restores before
# exit (even on failure or interrupt).

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

# ─────────────────────────────────────────────────────────────────────────────
# Bookkeeping
# ─────────────────────────────────────────────────────────────────────────────
PASS=0
FAIL=0
FAILED_GATES=()
TMP=$(mktemp -d)
trap 'cleanup' EXIT INT TERM

BACKUPS=()

backup() {
  local f=$1
  local b="$TMP/$(echo "$f" | tr / _).bak"
  cp -p "$f" "$b"
  BACKUPS+=("$f|$b")
}

cleanup() {
  for entry in "${BACKUPS[@]}"; do
    local f=${entry%%|*}
    local b=${entry#*|}
    [[ -f "$b" ]] && cp -p "$b" "$f"
  done
  rm -rf "$TMP"
}

gate() {
  local name=$1
  local direction=$2 # "must_fail" or "must_pass"
  local actual=$3    # exit code we observed (or 0 / 1 for bool)
  local expected
  case "$direction" in
    must_fail) expected="nonzero" ;;
    must_pass) expected="zero" ;;
    *) echo "internal: bad direction '$direction'"; exit 2 ;;
  esac

  local ok=0
  if [[ "$direction" == "must_fail" && "$actual" -ne 0 ]]; then ok=1; fi
  if [[ "$direction" == "must_pass" && "$actual" -eq 0 ]]; then ok=1; fi

  if [[ "$ok" -eq 1 ]]; then
    printf '  ✓ %-40s %s (exit=%s)\n' "$name" "$direction" "$actual"
    PASS=$((PASS + 1))
  else
    printf '  ✗ %-40s %s expected %s, got exit=%s\n' "$name" "$direction" "$expected" "$actual"
    FAIL=$((FAIL + 1))
    FAILED_GATES+=("$name [$direction]")
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Gate fixtures
# ─────────────────────────────────────────────────────────────────────────────

echo "── Gate 1: JSON validity (python3 -m json.tool) ──────────────────────────"
backup .claude-plugin/marketplace.json
echo 'not json' > .claude-plugin/marketplace.json
rc=0; python3 -m json.tool .claude-plugin/marketplace.json >/dev/null 2>&1 || rc=$?
gate "json-validity (marketplace.json)" must_fail "$rc"
cp -p "$TMP/.claude-plugin_marketplace.json.bak" .claude-plugin/marketplace.json
rc=0; python3 -m json.tool .claude-plugin/marketplace.json >/dev/null 2>&1 || rc=$?
gate "json-validity (marketplace.json)" must_pass "$rc"

echo
echo "── Gate 2: Plugin manifest version field ─────────────────────────────────"
backup plugins/ravenclaude-core/.claude-plugin/plugin.json
python3 -c "import json;p='plugins/ravenclaude-core/.claude-plugin/plugin.json';d=json.load(open(p));d.pop('version',None);json.dump(d,open(p,'w'),indent=2)"
v=$(python3 -c "import json;print(json.load(open('plugins/ravenclaude-core/.claude-plugin/plugin.json')).get('version',''))")
rc=0; [[ -n "$v" ]] || rc=1
gate "manifest-version-field" must_fail "$rc"
cp -p "$TMP/plugins_ravenclaude-core_.claude-plugin_plugin.json.bak" plugins/ravenclaude-core/.claude-plugin/plugin.json
v=$(python3 -c "import json;print(json.load(open('plugins/ravenclaude-core/.claude-plugin/plugin.json')).get('version',''))")
rc=0; [[ -n "$v" ]] || rc=1
gate "manifest-version-field" must_pass "$rc"

echo
echo "── Gate 3: Bash hook syntax (bash -n) ────────────────────────────────────"
backup plugins/ravenclaude-core/hooks/guard-destructive.sh
echo 'if [' >> plugins/ravenclaude-core/hooks/guard-destructive.sh
rc=0; bash -n plugins/ravenclaude-core/hooks/guard-destructive.sh 2>/dev/null || rc=$?
gate "bash-syntax (guard-destructive.sh)" must_fail "$rc"
cp -p "$TMP/plugins_ravenclaude-core_hooks_guard-destructive.sh.bak" plugins/ravenclaude-core/hooks/guard-destructive.sh
rc=0; bash -n plugins/ravenclaude-core/hooks/guard-destructive.sh 2>/dev/null || rc=$?
gate "bash-syntax (guard-destructive.sh)" must_pass "$rc"

echo
echo "── Gate 4: Hook executable bit ───────────────────────────────────────────"
backup plugins/ravenclaude-core/hooks/guard-destructive.sh
chmod -x plugins/ravenclaude-core/hooks/guard-destructive.sh
rc=0; test -x plugins/ravenclaude-core/hooks/guard-destructive.sh || rc=$?
gate "hook-executable-bit" must_fail "$rc"
chmod +x plugins/ravenclaude-core/hooks/guard-destructive.sh
rc=0; test -x plugins/ravenclaude-core/hooks/guard-destructive.sh || rc=$?
gate "hook-executable-bit" must_pass "$rc"

echo
echo "── Gate 5: Behavioral guard-destructive ──────────────────────────────────"
rc=0; plugins/ravenclaude-core/hooks/guard-destructive.sh "git reset --hard mybranch" >/dev/null 2>&1 || rc=$?
gate "guard-destructive (--hard ref)" must_fail "$rc"
rc=0; plugins/ravenclaude-core/hooks/guard-destructive.sh "git reset --soft HEAD~1" >/dev/null 2>&1 || rc=$?
gate "guard-destructive (--soft HEAD~1)" must_pass "$rc"

echo
echo "── Gate 6: Behavioral enforce-layout ─────────────────────────────────────"
mkdir -p "$TMP/proj/docs"
cat > "$TMP/proj/.repo-layout.json" <<EOF
{ "allowed_globs": ["docs/**"], "forbidden_globs": [], "suggestions": {} }
EOF
rc=0; CLAUDE_PROJECT_DIR="$TMP/proj" plugins/ravenclaude-core/hooks/enforce-layout.sh "$TMP/proj/random/file.txt" >/dev/null 2>&1 || rc=$?
gate "enforce-layout (off-pattern)" must_fail "$rc"
rc=0; CLAUDE_PROJECT_DIR="$TMP/proj" plugins/ravenclaude-core/hooks/enforce-layout.sh "$TMP/proj/docs/x.md" >/dev/null 2>&1 || rc=$?
gate "enforce-layout (in-pattern)" must_pass "$rc"
rc=0; CLAUDE_PROJECT_DIR="$TMP/proj" plugins/ravenclaude-core/hooks/enforce-layout.sh "$TMP/proj/docs/../../etc/passwd" >/dev/null 2>&1 || rc=$?
gate "enforce-layout (..-traversal scrub)" must_fail "$rc"

echo
echo "── Gate 7: Email-leak guard ──────────────────────────────────────────────"
backup .claude-plugin/marketplace.json
sed -i 's/"Matt Corbett"/"Matt Corbett","email":"matt@ravenpower.net"/' .claude-plugin/marketplace.json
rc=0
if grep -rn "matt@ravenpower.net" .claude-plugin/ plugins/*/.claude-plugin/ >/dev/null 2>&1; then rc=1; fi
gate "email-leak-guard" must_fail "$rc"
cp -p "$TMP/.claude-plugin_marketplace.json.bak" .claude-plugin/marketplace.json
rc=0
if grep -rn "matt@ravenpower.net" .claude-plugin/ plugins/*/.claude-plugin/ >/dev/null 2>&1; then rc=1; fi
gate "email-leak-guard" must_pass "$rc"

echo
echo "── Gate 8: Version pin cross-check ───────────────────────────────────────"
backup plugins/ravenclaude-core/.claude-plugin/plugin.json
python3 -c "import json;p='plugins/ravenclaude-core/.claude-plugin/plugin.json';d=json.load(open(p));d['version']='0.999.0';json.dump(d,open(p,'w'),indent=2)"
pv=$(jq -r '.version' plugins/ravenclaude-core/.claude-plugin/plugin.json)
cv=$(jq -r --arg n "ravenclaude-core" '.plugins[] | select(.name == $n) | .version' .claude-plugin/marketplace.json)
rc=0; [[ "$pv" == "$cv" ]] || rc=1
gate "version-pin-cross-check" must_fail "$rc"
cp -p "$TMP/plugins_ravenclaude-core_.claude-plugin_plugin.json.bak" plugins/ravenclaude-core/.claude-plugin/plugin.json
pv=$(jq -r '.version' plugins/ravenclaude-core/.claude-plugin/plugin.json)
cv=$(jq -r --arg n "ravenclaude-core" '.plugins[] | select(.name == $n) | .version' .claude-plugin/marketplace.json)
rc=0; [[ "$pv" == "$cv" ]] || rc=1
gate "version-pin-cross-check" must_pass "$rc"

echo
echo "── Gate 9: Prettier format check ─────────────────────────────────────────"
if command -v npx >/dev/null 2>&1; then
  backup .claude-plugin/marketplace.json
  echo '{   "x"  :  "y"   }' > .claude-plugin/marketplace.json
  rc=0; npx --yes prettier --check .claude-plugin/marketplace.json --log-level error >/dev/null 2>&1 || rc=$?
  gate "prettier-check (intentional bad format)" must_fail "$rc"
  cp -p "$TMP/.claude-plugin_marketplace.json.bak" .claude-plugin/marketplace.json
  rc=0; npx --yes prettier --check . --log-level error >/dev/null 2>&1 || rc=$?
  gate "prettier-check (tree clean)" must_pass "$rc"
else
  echo "  ~ npx unavailable, skipping prettier gate"
fi

echo
echo "── Gate 10: Actionlint (parse + lint) ────────────────────────────────────"
if command -v docker >/dev/null 2>&1; then
  docker pull --quiet rhysd/actionlint:1.7.7 >/dev/null 2>&1 || true
  backup .github/workflows/validate-layout.yml
  sed -i '5a\    BROKEN: **bad' .github/workflows/validate-layout.yml
  out=$(docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint:1.7.7 -color 2>/dev/null || true)
  # CI gate exits 1 when out is non-empty; translate that into rc for audit:
  rc=0; [[ -n "$out" ]] && rc=1
  gate "actionlint (injected YAML parse error)" must_fail "$rc"
  cp -p "$TMP/.github_workflows_validate-layout.yml.bak" .github/workflows/validate-layout.yml
  out=$(docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint:1.7.7 -color 2>/dev/null || true)
  rc=0; [[ -n "$out" ]] && rc=1
  gate "actionlint (clean tree)" must_pass "$rc"
else
  echo "  ~ docker unavailable, skipping actionlint gate"
fi

echo
echo "── Gate 11: repo-guide.html freshness ────────────────────────────────────"
# must_fail: mutate marketplace description in-memory, the freshness check should
# detect that the committed HTML no longer matches what would be regenerated.
backup .claude-plugin/marketplace.json
python3 -c "import json;p='.claude-plugin/marketplace.json';d=json.load(open(p));d['metadata']['description']='AUDIT FIXTURE — should diff against committed HTML';json.dump(d,open(p,'w'),indent=2)"
rc=0; scripts/check-guide-fresh.sh >/dev/null 2>&1 || rc=$?
gate "repo-guide freshness (mutated marketplace.json)" must_fail "$rc"
cp -p "$TMP/.claude-plugin_marketplace.json.bak" .claude-plugin/marketplace.json
# must_pass: pristine tree, the check should pass.
rc=0; scripts/check-guide-fresh.sh >/dev/null 2>&1 || rc=$?
gate "repo-guide freshness (clean tree)" must_pass "$rc"

echo
echo "═══════════════════════════════════════════════════════════════════════════"
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
if [[ "$FAIL" -gt 0 ]]; then
  echo
  echo "Failed audits:"
  for g in "${FAILED_GATES[@]}"; do
    echo "  - $g"
  done
  exit 1
fi
echo "all gates audited and verified bidirectional (fail-on-bad AND pass-on-good)"
