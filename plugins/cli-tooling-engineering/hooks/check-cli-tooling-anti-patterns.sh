#!/usr/bin/env bash
# check-cli-tooling-anti-patterns.sh — advisory PreToolUse hook for the cli-tooling-engineering plugin.
# Flags mechanically-detectable CLI anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set CLI_STRICT=1 to make it blocking (exit 2). Heuristic greps may
# false-positive — they are notices to review, not verdicts.
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# Raw ANSI escape sequences emitted directly (color/styling not gated behind a TTY check).
if grep -nE '\\(033|x1[bB]|u001[bB]|e)\[' "$file" >/dev/null 2>&1; then
  findings+=("Raw ANSI escape sequence in source — gate color/styling behind an isatty check and honor NO_COLOR (and FORCE_COLOR), or it ends up in piped/redirected output.")
fi

# Error/usage text printed to stdout (diagnostics belong on stderr).
if grep -nE '(console\.log|print|fmt\.Print(ln|f)?)\(.*([Ee]rror|[Uu]sage:)' "$file" >/dev/null 2>&1; then
  findings+=("Looks like an error/usage message on stdout — write diagnostics to stderr (console.error / print(..., file=sys.stderr) / fmt.Fprintln(os.Stderr, ...)) so stdout stays clean for data.")
fi

# Boolean used as an exit code (exits non-zero/zero unexpectedly across languages).
if grep -nE '(sys\.exit|process\.exit|os\.Exit)\((true|false|True|False)\)' "$file" >/dev/null 2>&1; then
  findings+=("Boolean passed as an exit code — exit codes are integers (0 success, distinct non-zero per failure class); a bool exits 1/0 by surprise.")
fi

# Secrets accepted as a CLI flag (leak into shell history and the process table).
if grep -nE '(--password|--token|--secret|--api-key|--apikey)\b' "$file" >/dev/null 2>&1; then
  findings+=("Secret accepted as a CLI flag — flags leak into shell history and 'ps'; accept secrets via an env var or a file path instead.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── cli-tooling-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${CLI_STRICT:-0}" = "1" ]; then
  echo "(blocking: CLI_STRICT=1)" >&2
  exit 2
fi
exit 0
