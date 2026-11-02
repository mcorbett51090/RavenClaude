#!/usr/bin/env bash
# assert-not-required-check.sh — CI-04
#
# Assert that a named job/check context is NOT listed among any branch
# ruleset's required status checks.
#
# Why a script: four workflows used to `gh api …/rulesets` (the LIST endpoint)
# and grep the JSON for their job name. That list payload has no check contexts
# (only id/name/enforcement/…) — so the grep could never fire. The DETAIL
# endpoint (`…/rulesets/{id}`) carries `required_status_checks[].context`.
#
# Usage:
#   scripts/assert-not-required-check.sh 'Atlas data validates'
#
# Exit codes:
#   0 — name absent from every ruleset's required checks, OR the API was
#       unreachable (inconclusive: warn, do not fail the scheduled run).
#   1 — name IS a required check (fatal: would hang PRs that skip this workflow).
#   2 — usage error.
#   3 — INCONCLUSIVE: a ruleset body was read but is unparseable or not the expected
#       shape (no `rules` array / an unrecognised required_status_checks rule), so the
#       assertion cannot be made. Never OK. (An unreachable API stays exit 0 above.)
set -uo pipefail

NAME="${1:-}"
if [ -z "$NAME" ]; then
  echo "usage: $0 '<required-check context or job name>'" >&2
  exit 2
fi

REPO="${GITHUB_REPOSITORY:-}"
if [ -z "$REPO" ]; then
  # Local convenience: derive from git remote when not in Actions.
  REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || true)"
fi
if [ -z "$REPO" ]; then
  echo "::warning::assert-not-required-check: no GITHUB_REPOSITORY / gh repo — inconclusive"
  exit 0
fi

if ! ids="$(gh api "repos/${REPO}/rulesets" --jq '.[].id' 2>&1)"; then
  echo "::warning::could not read branch rulesets ($ids) — assertion inconclusive, not OK"
  exit 0
fi

contexts=""
while IFS= read -r id; do
  [ -n "$id" ] || continue
  if ! detail="$(gh api "repos/${REPO}/rulesets/${id}" 2>&1)"; then
    echo "::warning::could not read ruleset ${id} ($detail) — assertion inconclusive, not OK"
    exit 0
  fi
  # Validate the body's SHAPE before trusting it. Previously a jq failure (unparseable body)
  # or a differently-shaped body yielded "no contexts" and the script printed OK, so a
  # required check could hide behind a body it never actually read. Anything that is not a
  # `rules` array whose required_status_checks rules each carry an array of string `context`s
  # is INCONCLUSIVE (exit 3), never OK.
  if ! shape="$(printf '%s' "$detail" | jq -r '
    if (.rules | type) != "array" then "no `rules` array"
    elif ([.rules[] | select(.type=="required_status_checks")]
          | all(.parameters.required_status_checks
                | type == "array" and all(.[]; (.context | type) == "string")))
    then "ok"
    else "a required_status_checks rule has an unrecognised shape"
    end
  ' 2>/dev/null)"; then
    shape="the body is not valid JSON"
  fi
  if [ "$shape" != "ok" ]; then
    echo "::error::assert-not-required-check: INCONCLUSIVE — ruleset ${id}: ${shape}. Not reporting OK."
    exit 3
  fi
  # Collect every required-status-check context from this ruleset.
  more="$(printf '%s' "$detail" | jq -r '
    [.rules[]?
      | select(.type=="required_status_checks")
      | .parameters.required_status_checks[]?.context
    ] | .[]
  ' 2>/dev/null || true)"
  if [ -n "$more" ]; then
    contexts="${contexts}${more}"$'\n'
  fi
done <<<"$ids"

if [ -z "$contexts" ]; then
  echo "OK: no required_status_checks found on any ruleset (or none configured)."
  exit 0
fi

if grep -Fqi -- "$NAME" <<<"$contexts"; then
  echo "::error::'${NAME}' appears in a branch ruleset's required status checks."
  echo "::error::A paths-filtered or scheduled workflow that is required hangs PRs forever."
  echo "Matched against contexts:"
  printf '%s' "$contexts" | sed 's/^/  - /'
  exit 1
fi

echo "OK: '${NAME}' is not named in any branch ruleset's required status checks."
exit 0
