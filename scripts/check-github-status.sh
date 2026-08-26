#!/usr/bin/env bash
# Checks GitHub's own status API for unresolved incidents before you spend time
# diagnosing what looks like a repo/token/code problem. Run this FIRST whenever
# CI behaves abnormally: runs stuck queued with no jobs provisioned, contradictory
# cancel/delete errors, or checks that never start. See docs/remote-ci-autotrigger-runbook.md
# "Stuck queued with zero jobs provisioned" section for the incident this was written from
# (2026-08-26: a live critical Actions outage produced exactly these symptoms for ~an hour).
#
# Always exits 0 (advisory) — never gate on this script's exit code.
set -uo pipefail

STATUS_URL="https://www.githubstatus.com/api/v2/incidents/unresolved.json"
OUT_FILE="$(mktemp -t gh-status.XXXXXX.json)"
trap 'rm -f "$OUT_FILE"' EXIT

# curl piped straight into an interpreter trips this repo's guard-destructive
# pattern match — write to a file first, then read it.
if ! curl -s --connect-timeout 5 -m 10 "$STATUS_URL" -o "$OUT_FILE" 2>/dev/null; then
  echo "⚠ could not reach githubstatus.com — network issue or the check itself failed; treat as UNKNOWN, not clean" >&2
  exit 0
fi

python3 - "$OUT_FILE" <<'PY'
import json, sys

path = sys.argv[1]
try:
    with open(path) as f:
        data = json.load(f)
except Exception as e:
    print(f"⚠ could not parse githubstatus.com response ({e}) — treat as UNKNOWN, not clean")
    sys.exit(0)

incidents = data.get("incidents", [])
relevant = [
    i for i in incidents
    if any(c.get("name") in ("Actions", "Pages", "API Requests", "Git Operations")
           for c in i.get("incident_updates", [{}])[0].get("affected_components", []))
]

if not incidents:
    print("✓ githubstatus.com: no unresolved incidents")
elif not relevant:
    print(f"✓ githubstatus.com: {len(incidents)} unresolved incident(s), none affecting Actions/Pages/API/Git")
else:
    for inc in relevant:
        latest = inc["incident_updates"][0]
        print(f"⛔ LIVE INCIDENT: {inc['name']} — status={inc['status']} impact={inc['impact']}")
        print(f"   started: {inc['created_at']}")
        print(f"   latest update ({latest['created_at']}): {latest['body'][:300]}")
    print()
    print("This is a GitHub-side issue, not your code/token/account. Retrying")
    print("cancel/delete/re-dispatch will not help — wait for GitHub to resolve it.")
PY
