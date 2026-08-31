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
# check 3 pipes its candidate lines through that module's `--lines` batch mode
# (ONE interpreter start per file) and keeps a line only if the module reports the
# `causal` family. Re-implementing those five families in bash would guarantee the
# two drift apart, and the module is the one with a planted canary, fixtures and a
# must-fail battery. What the HOOK owns is narrower and is a SCOPE decision, not a
# typing one: which lines are consequential enough to be worth a nudge (the
# outcome-word prefilter below) and which are already grounded (the evidence and
# meta suppressions). Do not move family grammar into this file.
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

# Specific unhedged-absolute capability phrasings (NOT a generic "cannot").
phrase='(you can'\''?t|it'\''?s impossible|impossible to|there'\''?s no way|there is no way|cannot be done|isn'\''?t possible|is not possible|not possible to|never works)'
# A conditional lead earlier on the line makes the phrase legitimate guidance.
conditional='\b(if|when|whenever|unless|because|since|until)\b'

# ── Check 2: contract-provenance (PR 9 / P15) ────────────────────────────────
# A SPECIFIC set of capability/contract phrasings, not a generic "supports".
# Everything below survived a hand-classified dry run over the live tree; the
# candidates it THREW OUT are the useful part of the record:
#   "natively" (58 hits, ~all prose), "defaults to"/"the default is" (31 hits,
#   ~13% precision — mostly our own flags), "(supports|accepts|returns) only"
#   (32 hits, ~all `grep` result counts), "added/introduced in <version>" (3
#   hits, all doc-changelog rows). Each was measured, not guessed, and each was
#   dropped for precision. Do not re-add one without re-running the dry run.
contract='(does not|doesn'\''?t|do not|don'\''?t) support|(is|are|was|were) (not )?supported|ha(s|ve) no (native|public|documented|official|supported)'
# Inline provenance markers that make the claim grounded. `[verify-at-…` and a
# bare ISO date are here because the dry run produced REAL false positives on
# lines that carried them — this repo already writes provenance in those forms.
provenance='\[docs-verified|\[verify-at-|\[unverified|\bverified\b|20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
# Sense disambiguation: "supported BY evidence/sources/documents" is the
# evidentiary sense of the word, not a capability claim. 4 real hits.
contract_sense='supported by'
# Elided-object rule: a genuine contract claim NAMES what is unsupported ("does
# not support MERGE", "does not support PCRE lookahead"). When the verb ends the
# clause with no object, the sense is evidentiary/rhetorical ("a count the
# sources don't support."). Measured: suppresses 3 real false positives and
# ZERO true findings.
contract_elided='support(ed)?[[:space:])".,;:]*$'

# ── Check 3: inference-as-observation (causal claim, no this-session check) ───
# SCOPE prefilter, NOT a typing rule (see the header): a causal sentence only
# matters here if it attributes an OUTCOME — that is the shape an agent acts on.
# Without this, every explanatory "X exists because Y" in a design doc would trip,
# and a lint that fires constantly gets ignored, which protects nothing.
outcome='fail(s|ed|ing|ure|ures)?|break(s|ing)?|broke(n)?|bug|regress|error|crash|hang|flake|flaky|leak|outage|timed out|timeout|denied|blocked|stale|red|green|pass(es|ed|ing)?|work(s|ing)?|correct|incorrect|wrong|missing|slow|down|exit[[:space:]]+[0-9]|\b[45][0-9][0-9]\b'
# DIAGNOSTIC prefilter — the second scope narrowing, and the one that MEASUREMENT
# forced. A first cut used every causal marker classify_claim.py recognises and
# fired on 92 of 240 sampled live knowledge/docs files (38%). Hand-reading the
# hits showed the cause: bare `because` and bare `so` are overwhelmingly
# EXPLANATORY in this repo's prose — design rationale ("the skip is correct
# because Bash command payloads are small"), purposive ("so they can install it").
# A lint that fires on a third of the tree gets switched off, which protects
# nothing.
#
# ⛔ WHAT THIS COSTS, stated rather than hidden: separating an EXPLANATORY
# "because" from a DIAGNOSTIC one is not mechanically decidable — "the page is
# green because the check passed" and "the skip is correct because payloads are
# small" are the same sentence to a regex. So check 3 keeps only the subset that
# IS separable: attribution ("caused by", "root cause", "due to") and conclusion
# connectives ("therefore", "which means"). It therefore MISSES a causal claim
# whose only marker is `because` — including the real "the status page is
# correctly green because the health check passed". That is a known, measured gap,
# not an oversight. Do not close it by re-adding bare `because` without re-running
# the dry run; the last attempt cost 38%.
#
# MEASURED END STATE (same 240-file sample, same command): 92 -> 13 -> 9 files
# (38% -> 5.4% -> 3.75%) across the diagnostic narrowing and the two suppressions
# below, landing in the same band as check 1 (9/240) and check 2 (4/240). Checks 1
# and 2 read 9 and 4 on ALL THREE runs, which is the regression proof that adding
# check 3 did not disturb them.
diagnostic='caused[[:space:]]+(by|the|it|this|that)|causing|root[[:space:]]+cause[[:space:]]*(is|was|of|:|=)|due[[:space:]]+to|owing[[:space:]]+to|led[[:space:]]+to|leads[[:space:]]+to|resulted[[:space:]]+in|result(s|ing)[[:space:]]+from|stems[[:space:]]+from|that[[:space:]]+is[[:space:]]+why|the[[:space:]]+reason[[:space:]]+(is|was|for|why)|therefore|hence|thus|consequently|as[[:space:]]+a[[:space:]]+result|which[[:space:]]+means|mean(s|ing)[[:space:]]+that|it[[:space:]]+follows[[:space:]]+that|attributable[[:space:]]+to|to[[:space:]]+blame|at[[:space:]]+fault|the[[:space:]]+culprit'
# GROUNDED — a this-session check cited inline. Deliberately generous: the cost of
# a missed nudge is one un-nudged line; the cost of nagging a line that DOES cite
# its evidence is that the whole check gets switched off. Covers this repo's own
# citation vocabulary (`cmd -> output`, file:line, a dated marker, "control:").
evidence='\[docs-verified|\[verify-at-|\[unverified|verified this session|verified against|\bverified\b|\bmeasured\b|\breproduced\b|\bcontrol:|20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]|[A-Za-z0-9_./-]+\.(sh|py|mjs|js|ts|json|ya?ml|md|toml|txt):[0-9]+|(->|=>|→)'
# META — the line DESCRIBES the anti-pattern instead of committing it. This repo
# has a documented, recurring failure where a source-scan gate flags the prose
# explaining the very pattern it hunts (nine such blocks in one session), and a
# doc teaching observation-vs-inference necessarily writes causal example
# sentences. Quotation marks count: a quoted claim is a specimen, not an
# assertion. Tested explicitly in both directions by Gate 224.
# PRESCRIPTIVE — a sentence issuing an instruction is not asserting a diagnosis.
# "P8 must therefore rebase onto post-#959 main" uses a conclusion connective to
# derive an ACTION, not a cause. Measured: this class plus the bare-noun "root
# cause" (a table header, "triaged by root cause") were the two residual
# false-positive shapes left after the diagnostic narrowing.
prescriptive='\b(must|should|shall|needs?[[:space:]]+to|ought[[:space:]]+to|have[[:space:]]+to|has[[:space:]]+to|plan[[:space:]]+to|going[[:space:]]+to)\b'
meta='anti-?pattern|for example|for instance|\be\.g\.|example:|counter-?example|(do not|don'\''?t|never)[[:space:]]+(write|say|claim|assert|state)|would (be )?(get )?flagged|this (hook|lint|check|gate|nudge|rule)|\binference\b|\binferences\b|\bobservation\b|\bobservations\b|\bhypothes|hypothetical|\bsuppose\b|imagine|"[^"]*"|“[^”]*”'

violations=()
contract_violations=()
c3_nums=()
c3_texts=()
in_fence=0
in_frontmatter=0
lineno=0
first_nonblank_seen=0

while IFS= read -r line || [[ -n "$line" ]]; do
  lineno=$((lineno + 1))

  # YAML frontmatter: a leading `---` as the very first non-blank line opens it;
  # the next `---` closes it.
  if [[ "$first_nonblank_seen" -eq 0 && -n "${line// /}" ]]; then
    first_nonblank_seen=1
    if [[ "$line" == "---" ]]; then in_frontmatter=1; continue; fi
  fi
  if [[ "$in_frontmatter" -eq 1 ]]; then
    [[ "$line" == "---" ]] && in_frontmatter=0
    continue
  fi

  # Fenced code blocks (``` or ~~~) — toggle and skip their contents.
  if [[ "$line" =~ ^[[:space:]]*(\`\`\`|~~~) ]]; then
    in_fence=$((1 - in_fence)); continue
  fi
  [[ "$in_fence" -eq 1 ]] && continue

  # Blockquotes often quote bad examples / external text — skip.
  [[ "$line" =~ ^[[:space:]]*\> ]] && continue

  # Markdown headings are titles, not consequential platform claims (and often
  # carry idioms like "you can't manage what you don't track") — skip.
  [[ "$line" =~ ^[[:space:]]*#{1,6}[[:space:]] ]] && continue

  # Inline escape hatch.
  echo "$line" | grep -qiF 'claim-lint-ok' && continue

  # Check 3 — collect candidates FIRST, deliberately. Checks 1 and 2 below use
  # bare `continue` for their suppressions, which skips the REST OF THE LINE, not
  # just their own check (a line suppressed by check 1 already never reaches check
  # 2). Running check 3 ahead of them keeps checks 1-2 byte-identical in behavior
  # while giving check 3 every surviving line. Do not move this block downward.
  if echo "$line" | grep -qiE "$outcome" && echo "$line" | grep -qiE "$diagnostic"; then
    if ! echo "$line" | grep -qiE "$evidence" &&
      ! echo "$line" | grep -qiE "$meta" &&
      ! echo "$line" | grep -qiE "$prescriptive"; then
      # Typing is classify_claim.py's call, not ours — batched after the loop.
      c3_nums+=("$lineno")
      c3_texts+=("$line")
    fi
  fi

  # Does the line contain an absolute phrasing?
  if echo "$line" | grep -qiE "$phrase"; then
    # Suppress if it's a conditional ("if you can't…").
    echo "$line" | grep -qiE "$conditional" && continue
    # Suppress if the claim already carries a provenance marker on the line.
    echo "$line" | grep -qiE '\[unverified|verified this session|verified against' && continue
    trimmed="$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    violations+=("  $file:$lineno: $trimmed")
  fi

  # Check 2 — contract provenance. Independent of check 1 (a line can trip both
  # or either). Uses the same $file the stdin/arg parse already resolved above
  # — no second stdin read (a duplicate parse would desync the two checks).
  # Ordered cheapest-first: the contract match gates every other subprocess,
  # so a non-matching line costs exactly one grep.
  if echo "$line" | grep -qiE "$contract"; then
    # Same conditional carve-out as check 1 ("when X doesn't support Y" is
    # guidance, not an asserted contract).
    echo "$line" | grep -qiE "$conditional" && continue
    # Already carries an inline provenance marker -> grounded, stay silent.
    echo "$line" | grep -qiE "$provenance" && continue
    # "supported by <evidence>" — wrong sense of the word.
    echo "$line" | grep -qiE "$contract_sense" && continue
    # Verb ends the clause with no object -> evidentiary/rhetorical sense.
    echo "$line" | grep -qiE "$contract_elided" && continue
    trimmed2="$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    contract_violations+=("  $file:$lineno: $trimmed2")
  fi
done < "$file"

# ── Check 3, second pass: type the candidates via classify_claim.py ───────────
# ONE interpreter start for the whole file. Every failure path here degrades to
# "check 3 emitted nothing" and leaves checks 1-2 untouched — a missing python3, a
# missing module, a non-zero exit, garbage on stdout. Check 3 is the newest and
# least-proven of the three; it must never be able to take the other two down.
inference_violations=()
if [[ ${#c3_nums[@]} -gt 0 ]] && command -v python3 >/dev/null 2>&1; then
  # Resolve the classifier: ${CLAUDE_PLUGIN_ROOT} when installed, else in-repo.
  cc=""
  if [[ -n "${CLAUDE_PLUGIN_ROOT:-}" && -f "${CLAUDE_PLUGIN_ROOT}/scripts/classify_claim.py" ]]; then
    cc="${CLAUDE_PLUGIN_ROOT}/scripts/classify_claim.py"
  else
    _hookdir="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || true)"
    [[ -n "$_hookdir" && -f "$_hookdir/../scripts/classify_claim.py" ]] && cc="$_hookdir/../scripts/classify_claim.py"
  fi
  if [[ -n "$cc" ]]; then
    c3_in="$(mktemp 2>/dev/null || true)"
    c3_out="$(mktemp 2>/dev/null || true)"
    if [[ -n "$c3_in" && -n "$c3_out" ]]; then
      for t in "${c3_texts[@]}"; do printf '%s\n' "$t"; done >"$c3_in" 2>/dev/null || true
      if python3 "$cc" --lines <"$c3_in" >"$c3_out" 2>/dev/null; then
        while IFS=$'\t' read -r idx kind fams || [[ -n "$idx" ]]; do
          [[ "$kind" == "inference" ]] || continue
          # ONLY the causal family. An "every"/"all" quantifier or a modal is a
          # different failure shape and would fire on ordinary doc prose.
          case ",$fams," in *,causal,*) ;; *) continue ;; esac
          case "$idx" in ''|*[!0-9]*) continue ;; esac
          _i=$((idx - 1))
          [[ "$_i" -ge 0 && "$_i" -lt ${#c3_nums[@]} ]] || continue
          _trim="$(printf '%s' "${c3_texts[$_i]}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
          inference_violations+=("  $file:${c3_nums[$_i]}: $_trim")
        done <"$c3_out"
      fi
      rm -f "$c3_in" "$c3_out" 2>/dev/null || true
    fi
  fi
fi

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
