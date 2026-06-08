#!/usr/bin/env bash
# check-embedded-iot-firmware-anti-patterns.sh — advisory PreToolUse hook for the
# embedded-iot-firmware plugin. Flags mechanically-detectable firmware anti-patterns on
# Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice to stderr);
# set EMBEDDED_IOT_FIRMWARE_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect source, header, config, and markdown files; skip binaries and object files.
case "$file" in
*.c | *.cpp | *.cc | *.cxx | *.h | *.hpp | *.rs | *.md | *.yaml | *.yml | *.json | *.toml | *.cmake | *.txt) ;;
*) exit 0 ;;
esac

findings=()

# 1. malloc or new inside an ISR or a function marked as hot/safety-critical.
#    Heuristic: file contains an IRQHandler / ISR marker AND also contains malloc/new,
#    OR a comment marking the function hot/safety-critical precedes malloc/new on a nearby line.
if grep -nEi "\bIRQHandler\b|\bISR\b|__irq\b|IRAM_ATTR\b" "$file" >/dev/null 2>&1 &&
   grep -nEi "\bmalloc\s*\(|\bnew\s+[A-Za-z]|\bnew\s*\[" "$file" >/dev/null 2>&1; then
  findings+=("malloc/new detected in a file containing ISR handlers — dynamic allocation inside an ISR or hot path is non-deterministic and unsafe. Use static pool allocators (best-practices/no-dynamic-allocation-in-hot-or-safety-critical-paths.md).")
fi

# 2. Standalone malloc/new in a file annotated with a hot/safety-critical comment marker.
if grep -nEi "@hot|@safety.critical|hot.path|safety.critical" "$file" >/dev/null 2>&1 &&
   grep -nEi "\bmalloc\s*\(|\bnew\s+[A-Za-z]|\bnew\s*\[" "$file" >/dev/null 2>&1; then
  findings+=("malloc/new in a path annotated @hot or @safety-critical — replace with a static pool allocator (best-practices/no-dynamic-allocation-in-hot-or-safety-critical-paths.md).")
fi

# 3. Blocking delay inside an ISR handler function body.
#    Heuristic: a function whose name ends in IRQHandler or is prefixed ISR_ contains
#    a call to delay(, HAL_Delay(, sleep(, usleep(, vTaskDelay(, or a busy-while.
if grep -nEi "\bIRQHandler\b|\bISR_" "$file" >/dev/null 2>&1 &&
   grep -nEi "\bdelay\s*\(|\bHAL_Delay\s*\(|\bsleep\s*\(|\busleep\s*\(|\bvTaskDelay\s*\(|\bosDelay\s*\(|\bwhile\s*\(\s*1\s*\)" "$file" >/dev/null 2>&1; then
  findings+=("Blocking delay (delay(), HAL_Delay(), sleep(), vTaskDelay(), busy-while) detected in a file containing ISR handlers — blocking in an ISR starves the system. Move processing to a deferred task (best-practices/never-block-in-an-isr.md).")
fi

# 4. OTA-related file with no mention of rollback, A/B, or fallback.
#    Heuristic: filename or content mentions OTA/firmware-update/fota, but there is no
#    mention of rollback, fallback, a_slot/b_slot, slot_0/slot_1, or boot_counter.
if echo "$file" | grep -iE "ota|fota|firmware.update|firmware_update|dfu" >/dev/null 2>&1 ||
   grep -niE "\bota\b|\bfota\b|\bfirmware.update\b|\bdfu\b" "$file" >/dev/null 2>&1; then
  if ! grep -niE "rollback|fallback|a_slot|b_slot|slot_0|slot_1|partition_0|partition_1|boot.count|boot_counter|mcuboot" "$file" >/dev/null 2>&1; then
    findings+=("OTA/firmware-update logic detected with no mention of rollback, A/B slots, or boot counter — every OTA scheme must have a tested rollback path (best-practices/design-ota-with-a-b-partitions-and-rollback.md).")
  fi
fi

# 5. Hard-coded key, secret, password, or API key in firmware source.
#    Grep for common patterns: PRIVATE_KEY =, api_key =, password =, secret =, AWS_SECRET, etc.
if grep -nEi "(private_key|api_key|apikey|secret_key|access_token|aws_secret|azure_key|password)\s*[=:]\s*\"[A-Za-z0-9+/=_\-]{8,}\"" "$file" >/dev/null 2>&1; then
  findings+=("Possible hard-coded key, secret, or credential in firmware source — secrets must not be committed to source. Use a flash-encrypted NVS region, a secure element, or injection at manufacturing (best-practices/secure-boot-and-signed-firmware-images.md).")
fi

# Also flag PEM-style key blocks in source files
if grep -nE "\-\-\-\-\-BEGIN (PRIVATE KEY|RSA PRIVATE KEY|EC PRIVATE KEY|CERTIFICATE)\-\-\-\-\-" "$file" >/dev/null 2>&1; then
  findings+=("PEM private key or certificate block detected in source file — private keys and production certificates must not be committed to source (best-practices/secure-boot-and-signed-firmware-images.md).")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── embedded-iot-firmware advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${EMBEDDED_IOT_FIRMWARE_STRICT:-0}" = "1" ]; then
  echo "(blocking: EMBEDDED_IOT_FIRMWARE_STRICT=1)" >&2
  exit 2
fi
exit 0
