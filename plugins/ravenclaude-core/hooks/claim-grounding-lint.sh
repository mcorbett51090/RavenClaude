#!/usr/bin/env bash
# claim-grounding-lint.sh
# PostToolUse hook for Edit | Write | MultiEdit. ADVISORY nudge (never blocks)
# when an UNHEDGED ABSOLUTE capability claim is written into a knowledge/ or
# docs/ markdown file without an inline provenance marker. Implements the
# enforced-complement of the Claim Grounding & Source Honesty protocol
# (plugins/ravenclaude-core/CLAUDE.md): a confident-wrong "you can't…" baked into
# a knowledge file becomes a durable false prior the next session trusts.
#
# It carries THREE independent checks over the same scan:
#   1. UNHEDGED ABSOLUTE  — "you can't…", "it's impossible…" with no marker.
#   2. CONTRACT PROVENANCE (added by PR 9 / defect P15 "building to an unverified
#      contract") — a capability/contract claim about some OTHER system ("X does
#      not support Y", "Z is supported", "W has no public API") written down with
#      no inline provenance marker. That is the shape that turns an unverified
#      belief into a durable contract the next session builds against.
#   3. INFERENCE-AS-OBSERVATION (added 2026-08-18) — a CAUSAL claim about an
#      outcome ("the failure is caused by my change", "the page is green because
#      the health check passed") asserted with no cited this-session check.
#
# WHY CHECK 3 IS A DIFFERENT AXIS FROM CHECKS 1-2, AND WHY IT NEEDED ADDING.
# Checks 1 and 2 both ask "is this claim SOURCED?". The failure that motivated
# check 3 (a real session, 2026-08-18) was NOT unsourced: an agent stated "the
# failure is caused by my change" and "the status page is correctly green" as
# FACTS. Both rested on true, in-session observations. Both were INFERENCES drawn
# from those observations, and both were wrong. Sourced-vs-unsourced cannot see
# that gap; OBSERVATION-vs-INFERENCE is the distinction that can.
#
# DIVISION OF LABOUR — the hook does NOT own the grammar. Typing a sentence
# observation-vs-inference is `scripts/classify_claim.py`'s job and only its job:
# check 3's candidates are typed in-process by `claim_grounding_scan.py` via
# `classify_claim.families()` and kept only for the `causal` family. Re-implementing
# those five families in bash (or a second Python copy) would guarantee drift, and
# the module is the one with a planted canary, fixtures and a must-fail battery.
# What the HOOK owns is narrower: path scope, comfort-posture opt-in, and advisory
# emit. Line skips + check regexes live in the scanner (SH-F9). Do not move family
# grammar into this file.
#
# HONEST SCOPE (read this — it bounds BOTH checks): this hook can only see
# WRITTEN FILE CONTENT — never the chat answer, which is where the confident
# error usually lands. It is one narrow, defense-in-depth surface (the
# durable-artifact case), NOT a control, and specifically NOT contract
# verification: it cannot tell a true claim from a false one, only a *marked*
# claim from an unmarked one. A hook that claimed to verify contracts would
# itself be exactly the false claim this protocol exists to stop. It is ADVISORY
# (exit 0 always), OPT-IN (no-op unless the project has a
# .ravenclaude/comfort-posture.yaml), and FAIL-SAFE (any error -> exit 0).
#
# Deliberately OUT OF SCOPE for check 2 (stated so the gap is not mistaken for
# coverage): generators and other non-markdown sources. Detecting a claim inside
# a .py/.sh comment needs a second, code-shaped skip machinery, and the whole
# point of this hook's low false-positive rate is the markdown machinery below.
# Check 2 is the durable-artifact subset only.
#
# HONEST LIMIT ON CHECK 3, stated because an overclaimed control is worse than an
# admitted gap: this is still the DURABLE-ARTIFACT subset. No hook event carries
# the model's chat answer — prose is not a tool call — so the place the confident
# inference is most often spoken is structurally out of reach here and always will
# be. Check 3 does not verify anything either: it cannot tell a true causal claim
# from a false one, only an UNCITED one from a cited one. It is the enforced
# sliver beneath a behavioral rule, not the rule's enforcement.
#
# False-positive discipline (Panel C): scoped to knowledge/**+docs/** .md only
# (excludes *.svg + concepts/visuals/**); skips YAML frontmatter, fenced code
# blocks, and blockquotes (where bad-examples are quoted); suppresses conditional
# phrasings ("if you can't…"); honors an inline `claim-lint-ok` escape comment;
# and matches a SPECIFIC set of absolute phrasings, not a generic "cannot".
# Check 2's pattern set + its two extra suppressions were derived from a dry run
# over the whole live knowledge/+docs/ tree (1,162 files) with every finding
# hand-classified — not from invented fixtures. See the header of the
# contract-provenance block below for what that measurement threw out.

set -euo pipefail

# ── ADVISORY DELIVERY (added 2026-08-19) ────────────────────────────────────
# ⛔ This hook's three checks all wrote to stderr and exited 0. That channel is
# MEASURED UNDELIVERED to the model (matched-trial bake-off with a positive
# control — see _advise.sh's header). Every advisory this file has ever emitted
# went to the terminal and never reached the model it was written for.
# rc_advise_init buffers fd2 and, at exit, re-emits it as additionalContext —
# which IS delivered — while still printing the original UI notice unchanged.
# No `>&2` call site below needs to change.
_rc_hd="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || printf '.')"
if [ -f "$_rc_hd/_advise.sh" ]; then . "$_rc_hd/_advise.sh"; rc_advise_init PostToolUse; fi

file="${1:-}"
# $CLAUDE_TOOL_FILE_PATH (passed as $1 by hooks.json) is NOT a real Claude Code
# hook variable, so under Claude Code the arg is empty and the path arrives only
# via the canonical stdin JSON contract. Fall back to it — same dual-source
# pattern regen-on-manifest-change.sh / guard-destructive.sh already use.
if [[ -z "$file" ]] && [[ ! -t 0 ]] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [[ -n "$payload" ]]; then
    file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
  fi
fi
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

# Path scope: only knowledge/ or docs/ markdown. Accept absolute (Claude Code) or
# relative (test) paths. Exclude generated SVGs and the visuals dir.
case "$file" in
  *.md) ;;
  *) exit 0 ;;
esac
case "$file" in
  */concepts/visuals/*) exit 0 ;;
esac
# SELF-NON-RECURSION (deliberate + visible). This hook's own source and its
# sibling hooks are not lintable material: this file's header necessarily SPELLS
# OUT the very phrasings it matches ("does not support …"), so a lint that ever
# reached it would flag itself forever. The .md scope above already excludes .sh,
# so this case is belt-and-suspenders — it stays because the failure it prevents
# is silent and self-inflicted. Do not delete it when widening the scope.
case "$file" in
  */hooks/claim-grounding-lint.sh | */hooks/*) exit 0 ;;
esac
case "$file" in
  */knowledge/*|knowledge/*|*/docs/*|docs/*) ;;
  *) exit 0 ;;
esac

# OPT-IN: no-op unless the project has adopted a comfort-posture. Walk up from the
# file's directory looking for .ravenclaude/comfort-posture.yaml (bounded).
posture_found=0
dir="$(cd "$(dirname "$file")" 2>/dev/null && pwd || true)"
for _ in 1 2 3 4 5 6 7 8 9 10; do
  [[ -z "$dir" ]] && break
  if [[ -f "$dir/.ravenclaude/comfort-posture.yaml" ]]; then posture_found=1; break; fi
  [[ "$dir" == "/" ]] && break
  dir="$(dirname "$dir")"
done
[[ "$posture_found" -eq 0 ]] && exit 0

# ── Single-process scan (SH-F9) ──────────────────────────────────────────────
# Patterns + line skips + check-3 typing live in claim_grounding_scan.py so a
# large doc does not pay a per-line `echo|grep` fork storm (~14–20 s on
# docs/concepts.md before this change). The hook still owns path scope, opt-in
# posture, and advisory emit. Typing for check 3 stays classify_claim.py's job
# (imported in-process by the scanner) — do not re-implement the five families
# here. Pattern rationale (dry-run precision notes, measured gaps) lives in the
# scanner module header and CLAUDE.md § Claim Grounding.
#
# CLAIM_GROUNDING_SCAN overrides the scanner path (Gate 224 C1 teeth: a temp
# copy with EVIDENCE/META/PRESCRIPTIVE neutered). Unset in normal use.
violations=()
contract_violations=()
inference_violations=()

if command -v python3 >/dev/null 2>&1; then
  _scan=""
  if [[ -n "${CLAIM_GROUNDING_SCAN:-}" && -f "${CLAIM_GROUNDING_SCAN}" ]]; then
    _scan="${CLAIM_GROUNDING_SCAN}"
  elif [[ -n "${CLAUDE_PLUGIN_ROOT:-}" && -f "${CLAUDE_PLUGIN_ROOT}/scripts/claim_grounding_scan.py" ]]; then
    _scan="${CLAUDE_PLUGIN_ROOT}/scripts/claim_grounding_scan.py"
  else
    _hookdir="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || true)"
    [[ -n "$_hookdir" && -f "$_hookdir/../scripts/claim_grounding_scan.py" ]] &&
      _scan="$_hookdir/../scripts/claim_grounding_scan.py"
  fi
  if [[ -n "$_scan" ]]; then
    # Fail-safe: any scanner error → no findings (advisory; never block).
    _scan_out="$(python3 "$_scan" --file "$file" 2>/dev/null || true)"
    while IFS=$'\t' read -r _chk _ln _txt || [[ -n "${_chk:-}" ]]; do
      [[ -n "${_chk:-}" ]] || continue
      case "$_chk" in
        c1) violations+=("  $file:$_ln: $_txt") ;;
        c2) contract_violations+=("  $file:$_ln: $_txt") ;;
        c3) inference_violations+=("  $file:$_ln: $_txt") ;;
      esac
    done <<<"$_scan_out"
  fi
fi
unset _scan _scan_out _chk _ln _txt _hookdir 2>/dev/null || true

if [[ ${#violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Claim-grounding nudge — ${#violations[@]} unhedged absolute claim(s) written to:
       $file
EOF
  count=0
  for v in "${violations[@]}"; do
    echo "$v" >&2
    count=$((count + 1))
    [[ $count -ge 10 ]] && { echo "  …(more elided)" >&2; break; }
  done
  cat >&2 <<'EOF'

  An absolute capability claim in a knowledge/doc file becomes a durable PRIOR
  that the next session reads as verified fact. If you verified it THIS session,
  cite the check inline (the command + output, or file:line). If it's training
  knowledge, mark it `[unverified — training knowledge]` so the provenance is
  persisted — the marker spoken only in chat does not travel into the file.
  See plugins/ravenclaude-core/CLAUDE.md § "Claim Grounding & Source Honesty".

  Add `claim-lint-ok` on the line to suppress (e.g. a verified platform fact or a
  quoted example). This hook is ADVISORY — the write was not blocked.
────────────────────────────────────────────────────────────────────

EOF
fi

if [[ ${#contract_violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Contract-provenance nudge — ${#contract_violations[@]} unmarked capability/contract claim(s) in:
       $file
EOF
  count=0
  for v in "${contract_violations[@]}"; do
    echo "$v" >&2
    count=$((count + 1))
    [[ $count -ge 10 ]] && { echo "  …(more elided)" >&2; break; }
  done
  cat >&2 <<'EOF'

  A claim about ANOTHER system's contract ("X does not support Y", "Z is
  supported", "W has no public API") is the shape that gets BUILT AGAINST. Once
  it is in a knowledge/doc file it reads as verified fact, and the code written
  to it inherits the error silently.

  Mark the provenance INLINE, on the line, so it travels with the claim:
    • `[docs-verified 2026-08-13]`  — you read the vendor's docs this session
    • `<url> (retrieved 2026-08-13)` — a source plus the date you fetched it
    • `[unverified — training knowledge]` — you are recalling it, not checking it
    • `[verify-at-use — 2026-08-13]`  — true when written, re-check before acting
  A marker spoken only in chat does not travel into the file.

  THIS HOOK DOES NOT VERIFY ANYTHING. It cannot tell a true claim from a false
  one — only a marked claim from an unmarked one. It is ADVISORY; the write was
  not blocked. Add `claim-lint-ok` on the line to suppress.
────────────────────────────────────────────────────────────────────

EOF
fi

if [[ ${#inference_violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Inference-as-observation nudge — ${#inference_violations[@]} uncited causal claim(s) in:
       $file
EOF
  count=0
  for v in "${inference_violations[@]}"; do
    echo "$v" >&2
    count=$((count + 1))
    [[ $count -ge 10 ]] && { echo "  …(more elided)" >&2; break; }
  done
  cat >&2 <<'EOF'

  These lines assert a CAUSE for an outcome. `classify_claim.py` types them
  `inference`, not `observation` — and an inference written into a durable file
  reads to the next session exactly like a measured fact.

  The distinction is NOT sourced-vs-unsourced. The claims that motivated this
  check were sourced — true observations, wrong conclusions drawn from them:
    "the failure is caused by my change"   (the change was innocent)
    "the page is green because X passed"   (green for an unrelated reason)
  Both were stated with the confidence of a measurement. Neither was measured.

  So cite the check that would have come out DIFFERENTLY if the cause were
  something else — the command and its output, or file:line — on the line. If you
  did not run one, say what you actually saw and mark the leap:
    "X failed and my change touched X [unverified — not isolated]"

  Add `claim-lint-ok` on the line to suppress (a quoted example, or a cause you
  really did isolate). This hook is ADVISORY — the write was not blocked — and it
  sees only WRITTEN FILES. It cannot see the chat answer, which is where this
  failure usually lands; there is no hook event that can. Treat this as one narrow
  surface under the behavioral rule, never as coverage of it.
────────────────────────────────────────────────────────────────────

EOF
fi

exit 0
