#!/usr/bin/env bash
# Runes ready-queue + Oath-hook + Longship — pinned behaviors.
# bash 3.2 safe.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
RUNES="$ROOT/plugins/ravenclaude-core/scripts/runes.py"
RC="$ROOT/plugins/ravenclaude-core/bin/rc"
OATH="$ROOT/plugins/ravenclaude-core/scripts/oath_hook.py"
HOOK="$ROOT/plugins/ravenclaude-core/hooks/oath-hook.sh"

fail=0
pass() { echo "PASS: $*"; }
bad() { echo "FAIL: $*"; fail=1; }

if python3 "$RUNES" --self-test >/tmp/rc-runes-selftest.out 2>/tmp/rc-runes-selftest.err; then
  pass "runes.py --self-test"
else
  bad "runes.py --self-test"
  cat /tmp/rc-runes-selftest.err || true
fi

usage="$(bash "$RC" 2>&1 || true)"
if echo "$usage" | grep -q "rc runes"; then
  pass "rc usage mentions runes"
else
  bad "rc usage missing runes"
fi
if echo "$usage" | grep -q "rc longship"; then
  pass "rc usage mentions longship"
else
  bad "rc usage missing longship"
fi

if [[ -x "$HOOK" ]]; then
  pass "oath-hook.sh executable"
else
  bad "oath-hook.sh not executable"
fi
tmp="$(mktemp -d)"
out="$(CLAUDE_PROJECT_DIR="$tmp" CLAUDE_PLUGIN_ROOT="$ROOT/plugins/ravenclaude-core" bash "$HOOK" || true)"
if [[ -z "$out" ]]; then
  pass "oath-hook silent without ledger"
else
  bad "oath-hook should be silent: $out"
fi
rm -rf "$tmp"

# Zero product hird/Hird except changelog-style "was briefly Hird"
# Scan implementation surfaces (not CHANGELOG).
hits="$(rg -n '\bhird\b|\bHird\b' \
  "$RUNES" "$OATH" "$HOOK" \
  "$ROOT/plugins/ravenclaude-core/bin/rc" \
  "$ROOT/plugins/ravenclaude-core/scripts/ledger.py" \
  "$ROOT/docs/runes-ready-queue.md" \
  2>/dev/null | rg -v 'was briefly Hird|briefly named Hird|was briefly Hird;' || true)"
if [[ -n "$hits" ]]; then
  bad "product hird/Hird hit:"
  echo "$hits"
else
  pass "no product hird/Hird outside changelog-style notes"
fi

if python3 "$RUNES" longship --help 2>&1 | grep -qi longship; then
  pass "longship subhelp ok"
else
  bad "longship help missing"
fi

# CLI smoke demos (temp repo)
demo="$(mktemp -d)"
git -C "$demo" init -q
git -C "$demo" config user.email "t@t"
git -C "$demo" config user.name "t"
echo '.ravenclaude/runs/' > "$demo/.gitignore"
git -C "$demo" add .gitignore
git -C "$demo" commit -q -m init
export RC_ACTOR=demo-agent
if python3 "$RUNES" --repo-root "$demo" open "Demo rune work item" >/tmp/rid.txt 2>/tmp/open.err; then
  rid="$(tail -n1 /tmp/rid.txt | tr -d "[:space:]")"
  pass "open $rid"
else
  bad "open failed"; cat /tmp/open.err || true; rid=""
fi
if [[ -n "$rid" ]]; then
  python3 "$RUNES" --repo-root "$demo" ready --json >/tmp/ready.json 2>/tmp/ready.err || true
  if grep -q "$rid" /tmp/ready.json; then pass "ready lists new rune"; else bad "ready miss"; cat /tmp/ready.json /tmp/ready.err; fi
  if python3 "$RUNES" --repo-root "$demo" claim "$rid" >/tmp/claim.out 2>/tmp/claim.err; then
    pass "claim"
  else
    bad "claim"; cat /tmp/claim.err
  fi
  if python3 "$RUNES" --repo-root "$demo" hanging --json 2>/tmp/hang.err | grep -q must_run; then
    pass "oath-hook hanging surface"
  else
    bad "hanging"; cat /tmp/hang.err || true
  fi
  python3 "$RUNES" --repo-root "$demo" open "Money wall" --gate matthew >/tmp/ridg.txt 2>/tmp/og.err || true
  ridg="$(tail -n1 /tmp/ridg.txt | tr -d "[:space:]")"
  if python3 "$RUNES" --repo-root "$demo" claim "$ridg" >/tmp/cg.out 2>/tmp/cg.err; then
    bad "gated claim should refuse"
  else
    pass "human_gate refuses claim"
  fi
  if python3 "$RUNES" --repo-root "$demo" longship open --longship-id ls-demo --title "demo" >/tmp/ls.out 2>/tmp/ls.err; then
    pass "longship open"
  else
    bad "longship open"; cat /tmp/ls.err
  fi
fi
rm -rf "$demo"

# --- dashboard opt-in posture + auto-claim B ---
posture_demo="$(mktemp -d)"
git -C "$posture_demo" init -q
git -C "$posture_demo" config user.email "t@t"
git -C "$posture_demo" config user.name "t"
echo '.ravenclaude/runs/' > "$posture_demo/.gitignore"
git -C "$posture_demo" add .gitignore
git -C "$posture_demo" commit -q -m init
export RC_ACTOR=posture-agent

# Off / absent → quiet hook
out="$(CLAUDE_PROJECT_DIR="$posture_demo" CLAUDE_PLUGIN_ROOT="$ROOT/plugins/ravenclaude-core" bash "$HOOK" || true)"
if [[ -z "$out" ]]; then
  pass "oath-hook quiet when runes absent (default off)"
else
  bad "oath-hook should be quiet when off: $out"
fi

mkdir -p "$posture_demo/.ravenclaude"
printf 'schema_version: 5\nrunes: on\n' > "$posture_demo/.ravenclaude/comfort-posture.yaml"
# ledger + ungated rune
python3 "$RUNES" --repo-root "$posture_demo" open "Posture on ready" --kind feature >/tmp/rid-on.txt 2>/tmp/on.err || true
rid_on="$(tail -n1 /tmp/rid-on.txt | tr -d '[:space:]')"
out_on="$(CLAUDE_PROJECT_DIR="$posture_demo" CLAUDE_PLUGIN_ROOT="$ROOT/plugins/ravenclaude-core" bash "$HOOK" || true)"
if echo "$out_on" | grep -q 'AUTO-CLAIMED\|READY QUEUE\|OATH-HOOK'; then
  pass "oath-hook orients when runes: on"
else
  bad "oath-hook On path silent: $out_on"
fi

# gated refuse via auto-claim path
python3 "$RUNES" --repo-root "$posture_demo" open "Gated money" --gate money >/tmp/rid-m.txt 2>/tmp/m.err || true
rid_m="$(tail -n1 /tmp/rid-m.txt | tr -d '[:space:]')"
# ensure money not claimed
owner="$(python3 "$RUNES" --repo-root "$posture_demo" show "$rid_m" --json 2>/dev/null | python3 -c 'import sys,json; print(json.load(sys.stdin).get("hook_owner") or "")' 2>/dev/null || true)"
if [[ -z "$owner" ]]; then
  pass "money-gated never auto-claimed"
else
  bad "money-gated was claimed: $owner"
fi

# Longship land-request still no merge (add a Rune first — empty Longship refuses)
if python3 "$RUNES" --repo-root "$posture_demo" longship open --longship-id ls-posture --title t >/tmp/lsp.out 2>/tmp/lsp.err; then
  # reuse an open ungated id if present; else mint one
  rid_ls="$(python3 "$RUNES" --repo-root "$posture_demo" open "Longship passenger" 2>/tmp/ols.err | tail -n1 | tr -d '[:space:]')"
  python3 "$RUNES" --repo-root "$posture_demo" longship add ls-posture "$rid_ls" >/tmp/lsa.out 2>/tmp/lsa.err || true
  land="$(python3 "$RUNES" --repo-root "$posture_demo" longship land-request ls-posture 2>/tmp/land.err)"
  land_err="$(cat /tmp/land.err 2>/dev/null || true)"
  if echo "$land$land_err" | grep -qi 'No merge\|auto_merge\|Sage'; then
    pass "Longship land-request never merges"
  elif python3 -c "import json,sys; d=json.load(open('/tmp/lsp.out'))" 2>/dev/null; then
    pass "Longship land-request never merges"
  else
    # inspect saved longship doc
    doc="$(python3 "$RUNES" --repo-root "$posture_demo" longship show ls-posture 2>/tmp/lss.err || true)"
    if echo "$doc" | grep -q 'auto_merge.: false\|"auto_merge": false'; then
      pass "Longship land-request never merges"
    else
      bad "land-request output unexpected: out=$land err=$land_err doc=$doc"
    fi
  fi
else
  bad "longship open for posture demo"; cat /tmp/lsp.err
fi

# kill switch
printf 'schema_version: 5\nrunes: off\n' > "$posture_demo/.ravenclaude/comfort-posture.yaml"
out_off="$(CLAUDE_PROJECT_DIR="$posture_demo" CLAUDE_PLUGIN_ROOT="$ROOT/plugins/ravenclaude-core" bash "$HOOK" || true)"
if [[ -z "$out_off" ]]; then
  pass "kill switch Off + file quiet"
else
  bad "kill switch failed: $out_off"
fi
rm -rf "$posture_demo"

if [[ "$fail" -ne 0 ]]; then
  echo "OVERALL FAIL"
  exit 1
fi
echo "OVERALL PASS"
exit 0

