#!/usr/bin/env bash
# Gate — dataverse-payload-preflight validate() (offline, fixture-driven).
#   A bad payload surfaces ALL the Contoso-retro violation classes in ONE pass
#     (nonexistent-column, invalid-option-set, malformed-lookup-bind, lookup-needs-bind,
#      missing-required, owner-not-provided).
#   A clean payload validates with zero errors.
#   Teeth: a mutant where validate() returns [] no longer flags the bad payload.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SK="$(cd "$HERE/../.." && pwd)/skills/dataverse-payload-preflight/preflight.py"
fails=0
pass() { echo "  ✓ $1"; }
fail() {
  echo "  ✗ $1"
  fails=$((fails + 1))
}
TMP="$(mktemp -d)"

cat >"$TMP/meta.json" <<'EOF'
{
  "logical_name": "btcsi_balancesheet", "entity_set": "btcsi_balancesheets",
  "primary_id": "btcsi_balancesheetid", "ownership": "UserOwned",
  "attributes": {
    "btcsi_name": {"type": "String", "required": "ApplicationRequired", "valid_for_create": true},
    "btcsi_sourcechannel": {"type": "Picklist", "required": "None", "valid_for_create": true, "options": [1, 2, 3]},
    "btcsi_accountid": {"type": "Lookup", "required": "None", "valid_for_create": true, "targets": ["account"]},
    "btcsi_balancesheetid": {"type": "Uniqueidentifier", "required": "SystemRequired", "valid_for_create": true}
  }
}
EOF

cat >"$TMP/bad.json" <<'EOF'
{
  "btcsi_doesnotexist": "x",
  "btcsi_sourcechannel": 942760000,
  "btcsi_AccountId@odata.bind": "/accounts()",
  "btcsi_accountid": "raw-guid"
}
EOF

cat >"$TMP/good.json" <<'EOF'
{
  "btcsi_name": "Q2 close",
  "btcsi_sourcechannel": 2,
  "btcsi_AccountId@odata.bind": "/accounts(11111111-1111-1111-1111-111111111111)",
  "ownerid@odata.bind": "/systemusers(22222222-2222-2222-2222-222222222222)"
}
EOF

run() { python3 "$1" --entity btcsi_balancesheet --metadata "$TMP/meta.json" --payload "$2" 2>/dev/null; }

# A — bad payload surfaces every class
outB="$(run "$SK" "$TMP/bad.json")"
kinds="$(printf '%s' "$outB" | python3 -c "import json,sys; d=json.load(sys.stdin); print(','.join(sorted({v['kind'] for v in d['violations']})))" 2>/dev/null)"
need="nonexistent-column invalid-option-set malformed-lookup-bind lookup-needs-bind missing-required owner-not-provided"
miss=""
for k in $need; do printf '%s' "$kinds" | grep -q "$k" || miss="$miss $k"; done
[ -z "$miss" ] && pass "bad payload surfaces all 6 violation classes in one pass" || fail "bad payload missed:$miss (got: $kinds)"
printf '%s' "$outB" | python3 -c "import json,sys; sys.exit(0 if json.load(sys.stdin)['ok'] is False else 1)" \
  && pass "bad payload -> ok:false" || fail "bad payload not marked ok:false"

# B — clean payload validates with zero errors
outG="$(run "$SK" "$TMP/good.json")"
printf '%s' "$outG" | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d['ok'] and d['error_count']==0 else 1)" \
  && pass "clean payload -> ok:true, 0 errors" || fail "clean payload flagged errors: $outG"

# C — teeth: a mutant validate() that returns [] no longer flags the bad payload
MUT="$TMP/mut.py"
sed 's/^    return v$/    return []/' "$SK" >"$MUT"
if ! grep -q "^    return \[\]$" "$MUT"; then
  fail "could not neuter validate() (sed no-op — fixture stale)"
else
  printf '%s' "$(run "$MUT" "$TMP/bad.json")" | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d['ok'] is True else 1)" \
    && pass "must-fail half: neutered validate() passes the bad payload (validator is load-bearing)" \
    || fail "must-fail: neutered validate() still flagged the bad payload (no teeth)"
fi

echo ""
if [ "$fails" -eq 0 ]; then
  echo "preflight gate PASS — one-pass payload validation: catches all classes, clean on good, has teeth."
  exit 0
else
  echo "preflight gate FAIL — $fails subtest(s)."
  exit 1
fi
