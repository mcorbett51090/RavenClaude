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

RELEVANT = {"Actions", "Pages", "API Requests", "Git Operations"}


def _affected_names(inc):
    # Union the incident-level `components` with EVERY update's affected_components,
    # each guarded with `or []`. Two bugs this fixes: (1) reading only the latest
    # update ([0]) false-greened the moment a non-status-changing update cleared the
    # component set, hiding a still-live Actions outage; (2) a `null` affected_components
    # (common on an administrative update) made `for c in None` raise TypeError, which
    # was uncaught and broke this script's always-exit-0 contract.
    names = set()
    for c in inc.get("components") or []:
        if isinstance(c, dict) and c.get("name"):
            names.add(c["name"])
    for upd in inc.get("incident_updates") or []:
        for c in upd.get("affected_components") or []:
            if isinstance(c, dict) and c.get("name"):
                names.add(c["name"])
    return names


try:
    incidents = data.get("incidents") or []
    relevant = [i for i in incidents if _affected_names(i) & RELEVANT]
    if not incidents:
        print("✓ githubstatus.com: no unresolved incidents")
    elif not relevant:
        print(
            f"✓ githubstatus.com: {len(incidents)} unresolved incident(s), "
            "none affecting Actions/Pages/API/Git"
        )
    else:
        for inc in relevant:
            updates = inc.get("incident_updates") or [{}]
            latest = updates[0] if updates else {}
            print(
                f"⛔ LIVE INCIDENT: {inc.get('name', '?')} — "
                f"status={inc.get('status', '?')} impact={inc.get('impact', '?')}"
            )
            print(f"   started: {inc.get('created_at', '?')}")
            print(
                f"   latest update ({latest.get('created_at', '?')}): "
                f"{str(latest.get('body', ''))[:300]}"
            )
        print()
        print("This is a GitHub-side issue, not your code/token/account. Retrying")
        print("cancel/delete/re-dispatch will not help — wait for GitHub to resolve it.")
except Exception as e:  # noqa: BLE001 - an advisory status check must NEVER raise
    print(f"⚠ could not evaluate githubstatus.com response ({e}) — treat as UNKNOWN, not clean")
sys.exit(0)
PY
