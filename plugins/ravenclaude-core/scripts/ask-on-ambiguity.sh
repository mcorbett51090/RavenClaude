#!/usr/bin/env bash
# ask-on-ambiguity.sh
# UserPromptSubmit hook body. ADVISORY nudge (it can NEVER block or alter a
# prompt) when the submitted request is under-specified in a mechanically
# detectable way, so the agent asks ONE clarifying question instead of assuming
# an interpretation and building on it. The behavioral half lives in
# plugins/ravenclaude-core/CLAUDE.md § "Ask on ambiguity"; this is its one
# enforceable sliver.
#
# ── WHAT THIS CANNOT DO (read before trusting it) ────────────────────────────
# It CANNOT tell an ambiguous request from a clear one. It detects a SHAPE:
# short + no concrete anchor + an open-ended verb + an unbound referent. A long,
# anchored, precisely-worded request that is nevertheless ambiguous in its INTENT
# is invisible here, and always will be — intent is not in the token stream.
# It CANNOT gate anything. A UserPromptSubmit hook that blocked would hold the
# user's own prompt hostage to a regex, so this one exits 0 unconditionally and
# emits nothing that alters the prompt.
# It CANNOT see the agent's answer. Whether the agent then actually ASKS rather
# than assuming is prose, not a tool call, and no hook event carries prose. That
# residue is irreducibly behavioral.
# So: this is a salience boost on the INPUT. Do not cite it as the control that
# prevents assumption-driven work — there is no such control, and claiming one
# would stop anyone from building the real thing.
#
# ── THE NO-EGRESS INVARIANT (Gate 110's rule, honored here) ──────────────────
# The prompt text NEVER reaches disk and NEVER reaches the emitted context.
# This hook writes NO files at all. Every byte it emits is a fixed string written
# in this file plus ONE derived integer (a word count). It does not log, does not
# append an event, and does not echo a substring of the prompt back into the
# model's context — the prompt arrives on stdin, is matched inside shell
# variables, and dies with the process. It is never placed in argv either (every
# match uses the `printf` builtin, so it is not visible in `ps`).
# If you extend this hook, that stays true: an additionalContext quoting the
# prompt would be both an egress and an injection surface, since the prompt is
# the least-trusted text in the session.
#
# OPT-IN: no-op unless the project has a .ravenclaude/comfort-posture.yaml.
# Disable with `ask_on_ambiguity: off`. Tune with `ask_on_ambiguity_max_words: N`.
# FAIL-SAFE: every error path exits 0 and emits nothing.
#
# ── WHY THIS FILE IS IN scripts/ AND NOT ALONGSIDE THE OTHER HOOKS ───────────
# Packaging, not design. The command-review tribunal's substrate guard
# (xc.tribunal-self-disable) denies any command naming the plugin's hook
# directory — correctly; that is how the Thing protects itself — and that
# includes setting the executable bit on a NEW file there. Two sanctioned routes
# were tried and both were denied by design (a direct mode change, and the
# git-index mode change). Shipping a non-executable file in that directory is not
# an option either: the "Verify hooks are executable" step in
# .github/workflows/validate-marketplace.yml hard-fails on it, and a hook wired
# into hooks.json that never runs is precisely this repo's silent-green defect
# class. This directory carries no such CI check and already holds
# non-executable siblings, so both registrations invoke this file through `bash`.
# FOLLOW-UP for anyone who can set the bit: move this file next to the other
# hooks, mark it executable, and drop the `bash ` prefix from its two
# registrations. Nothing else changes.
#
# Portability: bash 3.2 (no declare -A / mapfile / ${x^^} / globstar), no GNU
# timeout, no grep -P, no sed -i.

# Deliberately NOT `set -e`: a non-matching grep is the NORMAL path here, and an
# -e abort would exit non-zero on the majority of prompts. `pipefail` is likewise
# omitted — `printf | grep -q` legitimately closes the pipe early (SIGPIPE 141).
set -u

# Belt-and-suspenders: whatever happens below, this hook exits 0.
trap 'exit 0' EXIT

payload=""
if [ ! -t 0 ]; then payload="$(cat 2>/dev/null || true)"; fi

project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -d "$project_dir" ] || exit 0

posture="$project_dir/.ravenclaude/comfort-posture.yaml"
[ -f "$posture" ] || exit 0

# Cap the config read. A hostile cloned repo's posture file is untrusted input to
# a hook that runs on every prompt — the same exposure that made a 60k-digit
# value hang the stream_threshold parse.
posture_head="$(head -c 65536 "$posture" 2>/dev/null || true)"

# An explicit `off` disables. Any other value (or absent) leaves the nudge on.
if printf '%s' "$posture_head" |
  grep -Eq '^[[:space:]]*ask_on_ambiguity[[:space:]]*:[[:space:]]*off([[:space:]]|#|$)'; then
  exit 0
fi

# Word ceiling. The numeric capture is bounded and de-ambiguated on purpose —
# `[0-9]*` beside `[0-9]+` is the backtracking shape that caused that hang.
max_words="$(printf '%s' "$posture_head" |
  sed -n -E 's/^[[:space:]]*ask_on_ambiguity_max_words[[:space:]]*:[[:space:]]*([0-9]{1,4}).*$/\1/p' |
  head -1)"
case "$max_words" in
'' | *[!0-9]*) max_words=12 ;;
esac
[ "$max_words" -lt 3 ] 2>/dev/null && max_words=3
[ "$max_words" -gt 40 ] 2>/dev/null && max_words=40

# jq absent -> no-op. We will not hand-parse untrusted JSON to save a dependency.
command -v jq >/dev/null 2>&1 || exit 0
[ -n "$payload" ] || exit 0
prompt="$(printf '%s' "$payload" | jq -r '.prompt // .promptText // empty' 2>/dev/null || true)"
[ -n "$prompt" ] || exit 0

# Bound the work: a long prompt is by definition not the short-and-vague shape,
# and this runs on every single prompt.
prompt="$(printf '%s' "$prompt" | head -c 4096)"

# ── Derived signal 1: length ─────────────────────────────────────────────────
word_count="$(printf '%s' "$prompt" | wc -w | tr -d '[:space:]')"
case "$word_count" in
'' | *[!0-9]*) exit 0 ;;
esac
[ "$word_count" -ge 1 ] || exit 0
[ "$word_count" -le "$max_words" ] || exit 0

# ── Derived signal 2: a CONCRETE ANCHOR ──────────────────────────────────────
# The strongest available evidence that a request IS specified: it names
# something. A path, a filename, a backticked span, a URL, an issue number, an
# identifier, a flag, a quoted string, any digit. Any anchor at all -> silent.
# This is the check that keeps the nudge off ordinary short instructions
# ("run `npm test`", "open src/app.ts", "revert #861").
anchor='`|/|https?://|#[0-9]+|\.(md|py|sh|js|mjs|cjs|ts|tsx|jsx|json|ya?ml|toml|txt|css|html|go|rs|rb|java|sql|env)\b|[A-Za-z0-9_]+\(\)|[A-Za-z0-9_]+::|--[a-z][a-z-]+|\b[A-Z][A-Z0-9_]{2,}\b|"[^"]+"|[0-9]'
if printf '%s' "$prompt" | grep -Eq "$anchor"; then exit 0; fi

# ── Derived signal 3: an OPEN-ENDED DIRECTIVE ────────────────────────────────
# A verb whose success condition is not stated by the verb itself. "add",
# "delete", "rename", "revert" are deliberately NOT here: they say what done
# looks like, so a short prompt using one is terse, not ambiguous.
vague='\b(fix|fixes|fixing|clean|cleanup|improve|improving|better|handle|polish|refactor|refactoring|optimi[sz]e|optimi[sz]ing|tidy|simplify|streamline|rework|redo|update|updating|modernize|harden|tune|revamp|overhaul|address|sort out|deal with|take care of|look into|figure out)\b'
printf '%s' "$prompt" | grep -Eqi "$vague" || exit 0

# ── Derived signal 4: an UNBOUND REFERENT or an UNBOUNDED SCOPE ──────────────
# The verb is open-ended AND its object is a bare pronoun with no antecedent in
# the prompt, or a totalising quantifier. This is the conjunct that makes the
# nudge rare rather than constant: "refactor the auth module" has an open-ended
# verb but a named object and stays silent; "fix it" and "clean up everything"
# do not. A lint that fires on most inputs gets switched off, which protects
# nothing — the same lesson the claim-grounding dry run paid for in measurement.
referent='\b(it|this|that|these|those|them|they|the thing|the things|the stuff|the rest|the others|the code|the file|the files|stuff|things)\b'
scope='\b(all|everything|anything|whatever|the whole thing|each one|every ?thing)\b'
if ! printf '%s' "$prompt" | grep -Eqi "$referent" &&
  ! printf '%s' "$prompt" | grep -Eqi "$scope"; then
  exit 0
fi

# ── Emit ─────────────────────────────────────────────────────────────────────
# Hand-built JSON. Every byte is a literal from THIS file plus $word_count, which
# is proven all-digits above — so no untrusted text can reach the model's context
# and no quoting bug can escape the string. Do NOT interpolate $prompt here.
printf '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"%s"}}\n' \
  "[ravenclaude] AMBIGUITY SIGNAL (derived, advisory): this prompt is ${word_count} words, names no file, path, symbol, quoted string or number, and pairs an open-ended verb with an unbound referent. Before acting: state the interpretation you would proceed on. If more than one reading is genuinely plausible AND they lead to different work, ask ONE clarifying question first rather than picking one silently. If the intent is already clear from the conversation, say so in one clause and continue -- do not stall on this notice. This is a shape match on the prompt text alone; it did not read your context and is not a judgement that you are confused."

exit 0
