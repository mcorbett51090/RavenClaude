#!/usr/bin/env bash
# check-fintech-payments-engineering-anti-patterns.sh — advisory PreToolUse hook for the fintech-payments-engineering plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set PAY_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "(float|double|decimal\\s*\\(|Number)\\s*[\\s\\S]{0,30}(price|amount|total|cost|money|cents|balance)" "$file" >/dev/null 2>&1; then
  findings+=("Possible floating-point money — store/compute money as integer minor units (cents) + currency; floats cause rounding disputes.")
fi
if grep -nEi "(card_number|pan|cvv|cvc|card\\.number|securityCode)\\s*[=:]" "$file" >/dev/null 2>&1; then
  findings+=("Handling/logging raw card data (PAN/CVV) — never let it touch your servers/logs; use PSP tokenization (PCI scope).")
fi
if grep -nEi "log[\\s\\S]{0,40}(card_number|pan|cvv|cvc)" "$file" >/dev/null 2>&1; then
  findings+=("Logging card data — a PAN/CVV in logs is a serious PCI violation; never log it.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── fintech-payments-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${PAY_STRICT:-0}" = "1" ]; then
  echo "(blocking: PAY_STRICT=1)" >&2
  exit 2
fi
exit 0
