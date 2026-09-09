#!/usr/bin/env bash
# prompt-optimizer-judge-soak.sh
# Thin wrapper around prompt-optimizer-judge-soak.py — the Phase 9 held-out
# LLM-judge quality pass over the Phase 1 golden set (47 entries -- 42
# original + 5 adversarial paraphrases added by the final whole-branch
# review's round 2). See that
# file's own module docstring for the full contract, including WHY this is
# explicitly OUT of scripts/audit-gates.sh's required suite and its own
# `--check N` per-gate dispatcher (red-team Finding 2's resolution; the
# audit-gates 600s-ceiling trap this whole phase exists to avoid repeating).
#
# Standalone, weekly-soak / on-demand tool. NEVER invoked from
# scripts/audit-gates.sh — that file must never reference this filename.
#
# Usage:
#   bash prompt-optimizer-judge-soak.sh --self-test        # deterministic, zero live calls
#   bash prompt-optimizer-judge-soak.sh                     # dry-run (default, zero live calls)
#   bash prompt-optimizer-judge-soak.sh --run                # REAL claude calls, full 47-entry set
#   bash prompt-optimizer-judge-soak.sh --run --limit 5       # REAL claude calls, bounded smoke run
#
# All flags pass through verbatim to the python3 engine (--help for the full
# list: --golden-set, --limit, --judge-model, --no-judge, --run,
# --per-entry-timeout, --judge-timeout, --out-dir, --self-test).
set -euo pipefail
exec python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/prompt-optimizer-judge-soak.py" "$@"
