#!/usr/bin/env bash
# check-embedded-iot-engineering-anti-patterns.sh — advisory PreToolUse hook for the embedded-iot-engineering plugin.
# Flags mechanically-detectable embedded/IoT anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set EMBEDDED_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. A heavy/blocking call inside an ISR/IRQ handler — the §4 #3 flag-and-defer rule.
# Heuristic: the file defines an interrupt handler AND uses a heavy call (printf/float/delay/malloc) somewhere.
if grep -qiE "(void\s+\w*(IRQHandler|_isr|_ISR|_irq)\s*\(|__attribute__\s*\(\s*\(\s*interrupt|#\[\s*interrupt\s*\])" "$file" 2>/dev/null; then
  if grep -qiE "\b(printf|sprintf|fprintf|malloc|free|HAL_Delay|delay\s*\(|sleep\s*\(|vTaskDelay)\b" "$file" 2>/dev/null; then
    findings+=("Possible heavy/blocking call near an interrupt handler — ISRs must flag-and-defer (no printf/malloc/delay/blocking in interrupt context).")
  fi
fi

# 2. A TLS/MQTT/connectivity config that disables verification or hardcodes a key.
if grep -qiE "(verify\s*=\s*(false|0|none)|tls_?insecure|insecure\s*=\s*true|ssl_?verify\s*=\s*(false|0|none)|TLSVerify\s*:\s*false)" "$file" 2>/dev/null; then
  findings+=("TLS/DTLS verification disabled (verify=false / insecure) — a connected device with no peer verification is a cloned fleet. Use mutual TLS with per-device certs.")
fi
if grep -qiE "(psk\s*=|pre_?shared_?key\s*=|api_?key\s*=|private_?key\s*=|secret\s*=)\s*[\"'][A-Za-z0-9+/=_-]{8,}[\"']" "$file" 2>/dev/null; then
  findings+=("Hardcoded key/secret in source — keys belong in a secure element / secure storage, provisioned per device, never baked into firmware.")
fi

# 3. A connectivity/provisioning doc that relies on one shared secret across the fleet.
if grep -qiE "(shared|fleet|global|common|same)\s+(provisioning\s+)?(secret|key|credential|psk)|one\s+key\s+for\s+(all|the\s+fleet)" "$file" 2>/dev/null; then
  findings+=("Shared/fleet-wide provisioning secret — one extraction compromises every device. Provision per-device identity (cert/key in a secure element).")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── embedded-iot-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${EMBEDDED_STRICT:-0}" = "1" ]; then
  echo "(blocking: EMBEDDED_STRICT=1)" >&2
  exit 2
fi
exit 0
