#!/usr/bin/env bash
# check-cloud-native-kubernetes-anti-patterns.sh — advisory PreToolUse hook for the cloud-native-kubernetes plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set K8S_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "image:\\s*\\S+:latest|image:\\s*[^@\\s]+\\s*$" "$file" >/dev/null 2>&1; then
  findings+=("Container image not pinned by digest (':latest' or floating tag) — pin by digest for reproducibility.")
fi
if grep -nEi "runAsNonRoot:\\s*false|privileged:\\s*true|runAsUser:\\s*0\\b" "$file" >/dev/null 2>&1; then
  findings+=("Privileged/root container — run as non-root and unprivileged; drop capabilities.")
fi
if grep -nEi "kind:\\s*Deployment(?![\\s\\S]*resources:)" "$file" >/dev/null 2>&1; then
  findings+=("Deployment without resources block nearby — set requests AND limits (scheduling + cap).")
fi
if grep -nEi "kind:\\s*(Deployment|StatefulSet)(?![\\s\\S]*readinessProbe)" "$file" >/dev/null 2>&1; then
  findings+=("Workload without a readinessProbe nearby — readiness gates traffic; add it.")
fi
if grep -nEi "clusterrolebinding[\\s\\S]*cluster-admin" "$file" >/dev/null 2>&1; then
  findings+=("Binding to cluster-admin — workloads should use namespace-scoped least-privilege RBAC.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── cloud-native-kubernetes advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${K8S_STRICT:-0}" = "1" ]; then
  echo "(blocking: K8S_STRICT=1)" >&2
  exit 2
fi
exit 0
