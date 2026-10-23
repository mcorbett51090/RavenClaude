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
# -f: an HTTP error (a 5xx from the status page, a proxy error) is a failure here, not a body.
if ! curl -sf --connect-timeout 5 -m 10 "$STATUS_URL" -o "$OUT_FILE" 2>/dev/null; then
  echo "⚠ could not reach githubstatus.com — network issue or the check itself failed; treat as UNKNOWN, not clean" >&2
  exit 0
fi

python3 - "$OUT_FILE" <<'PY'
import json, re, sys

path = sys.argv[1]
try:
    with open(path) as f:
        data = json.load(f)
except Exception as e:
    print(f"⚠ could not parse githubstatus.com response ({e}) — treat as UNKNOWN, not clean")
    sys.exit(0)

if not isinstance(data, dict) or not isinstance(data.get("incidents"), list):
    print("⚠ UNKNOWN: githubstatus.com returned an unexpected response shape (no 'incidents' list) — treat as UNKNOWN, not clean")
    sys.exit(0)
incidents = [i for i in data["incidents"] if isinstance(i, dict)]

WATCH = re.compile(r"\b(actions|pages|api|git)\b", re.I)


def component_names(inc):
    """Every component name an incident carries: its own `components` plus the
    `affected_components` of every update (either may be null/missing)."""
    names = [c.get("name") for c in (inc.get("components") or []) if isinstance(c, dict)]
    for u in inc.get("incident_updates") or []:
        names += [c.get("name") for c in ((u or {}).get("affected_components") or []) if isinstance(c, dict)]
    return [n for n in names if isinstance(n, str)]


def latest_update(inc):
    ups = [u for u in (inc.get("incident_updates") or []) if isinstance(u, dict)]
    return ups[0] if ups else {}


relevant, unattributed = [], []
for inc in incidents:
    names = component_names(inc)
    if any(WATCH.search(n) for n in names) or WATCH.search(str(inc.get("name") or "")):
        relevant.append(inc)
    elif not names:
        # GitHub's own open incidents (e.g. "Incident with Actions") often carry no component
        # data at all, so absence of a component is NOT evidence the incident is unrelated.
        unattributed.append(inc)

if not incidents:
    print("✓ githubstatus.com: no unresolved incidents")
elif not relevant and not unattributed:
    print(f"✓ githubstatus.com: {len(incidents)} unresolved incident(s), none affecting Actions/Pages/API/Git")
else:
    for inc in relevant + unattributed:
        latest = latest_update(inc)
        if inc in relevant:
            print(f"⛔ LIVE INCIDENT: {inc.get('name')} — status={inc.get('status')} impact={inc.get('impact')}")
        else:
            print(f"⚠ INCIDENT WITH NO COMPONENT DATA (unattributed - may affect you): {inc.get('name')} — status={inc.get('status')} impact={inc.get('impact')}")
        print(f"   started: {inc.get('created_at')}")
        print(f"   latest update ({latest.get('created_at')}): {str(latest.get('body') or '')[:300]}")
    print()
    if relevant:
        print("This is a GitHub-side issue, not your code/token/account. Retrying")
        print("cancel/delete/re-dispatch will not help — wait for GitHub to resolve it.")
    else:
        print("An incident is open but GitHub attached no component data to it, so this script")
        print("cannot rule it out. Read its name/body above before assuming the fault is yours.")
PY
