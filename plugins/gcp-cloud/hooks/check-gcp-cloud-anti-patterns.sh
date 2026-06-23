#!/usr/bin/env bash
# check-gcp-cloud-anti-patterns.sh — advisory PreToolUse hook for the gcp-cloud plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set GCPCLOUD_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "(roles/owner|roles/editor)\\b" "$file" >/dev/null 2>&1; then
  findings+=("Primitive role (Owner/Editor) — use a scoped predefined/custom role; primitive roles are over-broad in prod.")
fi
if grep -nEi "(private_key.*BEGIN PRIVATE KEY|\\\"type\\\"\\s*:\\s*\\\"service_account\\\"|sa.*\\.json)" "$file" >/dev/null 2>&1; then
  findings+=("Possible exported service-account key file — use Workload Identity Federation; disable SA key creation via org policy.")
fi
if grep -nEi "(source_ranges.*0\\.0\\.0\\.0/0|0\\.0\\.0\\.0/0).*(22|3389|3306|5432)" "$file" >/dev/null 2>&1; then
  findings+=("Firewall open to 0.0.0.0/0 on an admin/DB port — target by tag/service-account and restrict the range.")
fi
if grep -Pzi "(external_ip|nat_ip|access_config)\\b(?![\\s\\S]{0,80}#\\s*public)" "$file" >/dev/null 2>&1; then
  findings+=("VM external IP configured — confirm public reachability is required; prefer Private Google Access + Cloud NAT.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── gcp-cloud advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${GCPCLOUD_STRICT:-0}" = "1" ]; then
  echo "(blocking: GCPCLOUD_STRICT=1)" >&2
  exit 2
fi
exit 0
