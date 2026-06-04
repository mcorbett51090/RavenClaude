#!/usr/bin/env bash
# check-devops-cicd-anti-patterns.sh — advisory PreToolUse hook for the devops-cicd plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set DEVOPS_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "uses:\\s*[^@]+@(v?[0-9]+|main|master|latest)\\b" "$file" >/dev/null 2>&1; then
  findings+=("Action pinned to a moving tag/branch — pin to a SHA (supply-chain surface in your own pipeline).")
fi
if grep -nEi "(aws_access_key_id|aws_secret_access_key|AKIA[0-9A-Z]{16})" "$file" >/dev/null 2>&1; then
  findings+=("Possible long-lived AWS key in a pipeline/config — use OIDC federation + short-lived tokens instead.")
fi
if grep -nEi "image:\\s*\\S+:latest" "$file" >/dev/null 2>&1; then
  findings+=("Container image pinned to ':latest' — pin a version/digest; 'latest' is not a version.")
fi
if grep -nEi "kubectl\\s+apply.*\\b(prod|production)\\b" "$file" >/dev/null 2>&1; then
  findings+=("Direct kubectl apply to prod — under GitOps this is drift; promote via a PR that the reconciler enforces.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── devops-cicd advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${DEVOPS_STRICT:-0}" = "1" ]; then
  echo "(blocking: DEVOPS_STRICT=1)" >&2
  exit 2
fi
exit 0
