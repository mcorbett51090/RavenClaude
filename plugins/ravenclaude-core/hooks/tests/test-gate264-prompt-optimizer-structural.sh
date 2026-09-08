#!/usr/bin/env bash
# test-gate264-prompt-optimizer-structural.sh
# Gate 264 — prompt-optimizer's ≤5-fixture structural regression subset (Phase 9,
# red-team Finding 2's resolution — the audit-gates 600s-ceiling trap). ZERO live
# judge-model calls anywhere in this file: every `claude` invocation is a stub
# that `cat`s a pre-built canned JSON file selected via $STUB_CLAUDE_OUTPUT_FILE.
# The full 42-entry golden-set LLM-judge quality pass (Phases 3/4's
# `wild_assumption` over-flagging arbitration) is a SEPARATE, non-required,
# standalone script — scripts/prompt-optimizer-judge-soak.sh — never invoked from
# here or from audit-gates.sh's own dispatcher. See that script's own header.
#
# Covers exactly the 5 items the task brief names for this gate's scope:
#   1. Schema validity of all THREE frozen JSON shapes (design-lock.md §1/§2/§3):
#      classifier output, emit_optimized_prompt, emit_dispatch_plan — a positive
#      case per shape plus one negative (invalid-enum) control on the classifier.
#   2. The fail-open teeth (Phases 2/3/4's patterns) across all three scripts,
#      WITH a must-fail-half mutant proving the assertion has teeth.
#   3. The no-egress check (Phase 2, design-lock.md §4): confidence=="low" forces
#      action=="skip", which emits NOTHING — the classifier's ambiguity_reason
#      never reaches stdout on that path.
#   4. The semantic-screen teeth (Phase 5) — prompt-optimizer-format.py's OWN
#      `--self-test` already IS the must-fail-then-pass proof (its
#      PROMPT_OPTIMIZER_FORMAT_DISABLE_SCREEN=1 env-var teeth, AT2/AT6 in
#      task-5-report.md) — reused here, not reimplemented.
#   5. The short-circuit regression fixture (Phases 2/6): an adjacent
#      `dispatch_config` block never leaks into `prompt_optimizer.enabled`'s
#      YAML-block-scoped read, in both block orderings, plus the negative case.

set -uo pipefail

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$(cd "$HOOKS_DIR/../scripts" && pwd)"
GATE_SH="$SCRIPTS_DIR/prompt-optimizer-gate.sh"
REWRITE_SH="$SCRIPTS_DIR/prompt-optimizer-rewrite.sh"
DISPATCH_SH="$SCRIPTS_DIR/prompt-optimizer-dispatch.sh"
FORMAT_PY="$SCRIPTS_DIR/prompt-optimizer-format.py"

PASS=0
FAIL=0
note() { printf '  %s %s\n' "$1" "$2"; }
ok() {
  PASS=$((PASS + 1))
  note "✓" "$1"
}
bad() {
  FAIL=$((FAIL + 1))
  note "✗" "$1"
}

for f in "$GATE_SH" "$REWRITE_SH" "$DISPATCH_SH" "$FORMAT_PY"; do
  [ -f "$f" ] || {
    echo "FATAL: missing $f"
    exit 2
  }
done

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

STUBDIR="$TMP/bin"
mkdir -p "$STUBDIR"
cat >"$STUBDIR/claude" <<'STUB'
#!/usr/bin/env bash
# Stub: ignore all args (including the untrusted prompt) — cat a pre-built canned
# JSON file selected by the test harness. Zero live model calls anywhere here.
[ -n "${STUB_CLAUDE_OUTPUT_FILE:-}" ] && [ -f "$STUB_CLAUDE_OUTPUT_FILE" ] || exit 1
cat "$STUB_CLAUDE_OUTPUT_FILE"
STUB
chmod +x "$STUBDIR/claude"

# A project root with prompt_optimizer ENABLED (schema/fail-open/no-egress fixtures).
PROJ="$TMP/proj"
mkdir -p "$PROJ/.ravenclaude"
cat >"$PROJ/.ravenclaude/comfort-posture.yaml" <<'YAML'
prompt_optimizer:
  enabled: true
  mode: advisory
YAML

# A PATH with jq + python3 but deliberately NO `claude` binary (verified this
# session: claude resolves to ~/.local/bin, jq/python3 both resolve under
# /usr/bin — so this PATH targets "claude missing" precisely, not "jq missing").
BARE_PATH="/usr/bin:/bin"

# Two backticked anchors force Tier-0 fallthrough (anchor_count=2 != 1) regardless
# of cluster-keyword hits, so every fixture below reliably reaches Tier-1.
PROMPT_2ANCHORS='Fix the bug in `auth/session.py` and `auth/token.py`.'

echo "── Gate 264: prompt-optimizer structural regression subset (≤5 fixtures) ───"

# ═════════════════════════════════════════════════════════════════════════════
# Fixture 1 — schema validity of all THREE frozen JSON shapes
# ═════════════════════════════════════════════════════════════════════════════

# 1a. Classifier output schema (design-lock.md §1) via gate.sh's Tier-1 call.
CLASSIFIER_JSON="$TMP/classifier.json"
cat >"$CLASSIFIER_JSON" <<'JSON'
{"action":"rewrite","confidence":"medium","domain_count":1,"anchor_count":1,"assumption_count":0,"ambiguity_reason":"none"}
JSON
out="$(printf '{"prompt":"%s"}' "$PROMPT_2ANCHORS" |
  PATH="$STUBDIR:$PATH" STUB_CLAUDE_OUTPUT_FILE="$CLASSIFIER_JSON" \
    CLAUDE_PROJECT_DIR="$PROJ" CLAUDE_SESSION_ID="g264-1a" PROMPT_OPTIMIZER_DEBUG=1 \
    bash "$GATE_SH" 2>&1 >/dev/null)"
if printf '%s' "$out" | grep -Eq 'TIER1_VERDICT action=rewrite confidence=medium domain_count=1 anchor_count=1 assumption_count=0'; then
  ok "1a: classifier schema (§1) — all 5 required fields parsed + validated"
else
  bad "1a: classifier schema — TIER1_VERDICT debug line missing/mismatched (out=$out)"
fi

# 1a-neg: an invalid enum (action="banana") must NOT validate — fails open silently.
CLASSIFIER_BAD_JSON="$TMP/classifier-bad.json"
cat >"$CLASSIFIER_BAD_JSON" <<'JSON'
{"action":"banana","confidence":"medium","domain_count":1,"anchor_count":1,"assumption_count":0}
JSON
out="$(printf '{"prompt":"%s"}' "$PROMPT_2ANCHORS" |
  PATH="$STUBDIR:$PATH" STUB_CLAUDE_OUTPUT_FILE="$CLASSIFIER_BAD_JSON" \
    CLAUDE_PROJECT_DIR="$PROJ" CLAUDE_SESSION_ID="g264-1a-neg" PROMPT_OPTIMIZER_DEBUG=1 \
    bash "$GATE_SH" 2>&1 >/dev/null)"
if printf '%s' "$out" | grep -q 'TIER1_FAILOPEN reason=invalid_verdict_shape'; then
  ok "1a-neg: an invalid action enum is REJECTED (classifier schema validation has teeth)"
else
  bad "1a-neg: invalid action enum should have failed open on shape (out=$out)"
fi

# 1b. Rewrite-generator schema (design-lock.md §2) via rewrite.sh, standalone.
REWRITE_JSON="$TMP/rewrite.json"
cat >"$REWRITE_JSON" <<'JSON'
{"rewritten_prompt":"Fix the login latency in auth/session.py.","explicit_constraints":["must not change the public API"],"surfaced_missing_context":[],"wild_assumption":{"present":false,"confidence":"high"}}
JSON
out="$(printf '%s' '{"prompt":"fix login latency"}' |
  PATH="$STUBDIR:$PATH" STUB_CLAUDE_OUTPUT_FILE="$REWRITE_JSON" \
    CLAUDE_PROJECT_DIR="$PROJ" bash "$REWRITE_SH" 2>/dev/null)"
if printf '%s' "$out" | jq -e '
    (.rewritten_prompt | type == "string") and
    (.explicit_constraints | type == "array") and
    (.surfaced_missing_context | type == "array") and
    (.wild_assumption.present == false) and
    (.wild_assumption.confidence == "high")
  ' >/dev/null 2>&1; then
  ok "1b: emit_optimized_prompt schema (§2) — all required fields present + typed"
else
  bad "1b: emit_optimized_prompt schema validation failed (out=$out)"
fi

# 1c. Dispatch-plan-generator schema (design-lock.md §3) via dispatch.sh, standalone.
# Uses a REAL agent name (architect) and a REAL agent-routing-matrix.json
# task_classes key (coding-implementation) so the roster-hallucination guard +
# matrix-citation check both pass and the recommendation is not silently dropped.
DISPATCH_JSON="$TMP/dispatch.json"
cat >"$DISPATCH_JSON" <<'JSON'
{"domains":["backend","security"],"per_domain":[{"domain":"backend","recommended_agents":[{"agent":"architect","rationale":"owns cross-cutting design","matrix_basis":"coding-implementation"}],"tailored_brief":"design the boundary"}],"wild_assumption":{"present":false,"confidence":"high"}}
JSON
out="$(printf '%s' '{"prompt":"design a new service boundary and its auth model"}' |
  PATH="$STUBDIR:$PATH" STUB_CLAUDE_OUTPUT_FILE="$DISPATCH_JSON" \
    CLAUDE_PROJECT_DIR="$PROJ" bash "$DISPATCH_SH" 2>/dev/null)"
if printf '%s' "$out" | jq -e '
    (.domains | type == "array") and
    (.per_domain | type == "array") and
    ((.per_domain[0].recommended_agents | length) >= 1) and
    (.wild_assumption.present == false)
  ' >/dev/null 2>&1; then
  ok "1c: emit_dispatch_plan schema (§3) — domains/per_domain/wild_assumption present, real roster entry kept"
else
  bad "1c: emit_dispatch_plan schema validation failed (out=$out)"
fi

# ═════════════════════════════════════════════════════════════════════════════
# Fixture 2 — fail-open teeth (Phases 2/3/4's patterns), WITH a must-fail half
# ═════════════════════════════════════════════════════════════════════════════

for pair in "$GATE_SH:g264-2a:gate.sh" "$REWRITE_SH:g264-2b:rewrite.sh" "$DISPATCH_SH:g264-2c:dispatch.sh"; do
  script="${pair%%:*}"
  rest="${pair#*:}"
  sid="${rest%%:*}"
  label="${rest##*:}"
  out="$(printf '%s' '{"prompt":"anything"}' |
    PATH="$BARE_PATH" CLAUDE_PROJECT_DIR="$PROJ" CLAUDE_SESSION_ID="$sid" \
      bash "$script" 2>/dev/null)"
  rc=$?
  if [ "$rc" -eq 0 ] && [ -z "$out" ]; then
    ok "2: $label fails open (exit 0, empty stdout) when the claude binary is absent"
  else
    bad "2: $label did NOT fail open on missing claude (rc=$rc out=$out)"
  fi
done

# MUST-FAIL HALF: neuter gate.sh's claude-missing fail-open branch so it LEAKS a
# marker to stdout instead of exiting silently — the assertion above MUST catch
# it, proving this fixture actually measures the fail-open guarantee.
MUTANT="$TMP/prompt-optimizer-gate.MUTANT.sh"
sed '/TIER1_FAILOPEN reason=claude_missing/{n;s/  exit 0/  echo "MUTANT-LEAK"; exit 0/;}' "$GATE_SH" >"$MUTANT"
chmod +x "$MUTANT"
if ! diff -q "$GATE_SH" "$MUTANT" >/dev/null 2>&1; then
  out="$(printf '%s' '{"prompt":"anything"}' |
    PATH="$BARE_PATH" CLAUDE_PROJECT_DIR="$PROJ" CLAUDE_SESSION_ID="g264-2mut" \
      bash "$MUTANT" 2>/dev/null)"
  if [ -n "$out" ]; then
    ok "MUST-FAIL teeth: a neutered claude-missing fail-open branch LEAKS and IS caught"
  else
    bad "MUST-FAIL: the mutant should have leaked to stdout but produced nothing — teeth are missing"
  fi
else
  bad "MUST-FAIL: the sed mutation did not change gate.sh — the mutant fixture is broken"
fi

# ═════════════════════════════════════════════════════════════════════════════
# Fixture 3 — no-egress (Phase 2, design-lock.md §4): action=="skip" emits
# NOTHING — confidence=="low" forces the override regardless of the model's own
# `action` field, and the flagged ambiguity_reason never reaches stdout.
# ═════════════════════════════════════════════════════════════════════════════

SKIP_JSON="$TMP/skip.json"
cat >"$SKIP_JSON" <<'JSON'
{"action":"rewrite","confidence":"low","domain_count":1,"anchor_count":1,"assumption_count":0,"ambiguity_reason":"MARKER_SHOULD_NEVER_LEAK"}
JSON
out="$(printf '{"prompt":"%s"}' "$PROMPT_2ANCHORS" |
  PATH="$STUBDIR:$PATH" STUB_CLAUDE_OUTPUT_FILE="$SKIP_JSON" \
    CLAUDE_PROJECT_DIR="$PROJ" CLAUDE_SESSION_ID="g264-3" \
    bash "$GATE_SH" 2>/dev/null)"
if [ -z "$out" ]; then
  ok "3: confidence=low forces action=skip -> NOTHING emitted (ambiguity_reason never leaks)"
else
  bad "3: confidence=low should force a silent skip, got: $out"
fi

# ═════════════════════════════════════════════════════════════════════════════
# Fixture 4 — semantic-screen teeth (Phase 5): prompt-optimizer-format.py's OWN
# --self-test IS the must-fail-then-pass proof (its env-var-gated teeth,
# task-5-report.md AT2/AT6) — reused directly, not reimplemented.
# ═════════════════════════════════════════════════════════════════════════════

FMT_OUT="$TMP/format-selftest.out"
if python3 "$FORMAT_PY" --self-test >"$FMT_OUT" 2>&1; then
  ok "4: prompt-optimizer-format.py --self-test passes (screen + delivery-shape + teeth)"
else
  bad "4: prompt-optimizer-format.py --self-test FAILED — see $FMT_OUT"
fi

# ═════════════════════════════════════════════════════════════════════════════
# Fixture 5 — short-circuit regression (Phases 2/6): an adjacent dispatch_config
# block never leaks into prompt_optimizer.enabled's YAML-block-scoped read, both
# orderings, plus the negative (prompt_optimizer disabled) case.
# ═════════════════════════════════════════════════════════════════════════════

PROJ_ADJ_TRUE1="$TMP/proj-adj-true1"
mkdir -p "$PROJ_ADJ_TRUE1/.ravenclaude"
cat >"$PROJ_ADJ_TRUE1/.ravenclaude/comfort-posture.yaml" <<'YAML'
dispatch_config:
  enabled: false
  mode: shadow
prompt_optimizer:
  enabled: true
  mode: advisory
YAML

PROJ_ADJ_TRUE2="$TMP/proj-adj-true2"
mkdir -p "$PROJ_ADJ_TRUE2/.ravenclaude"
cat >"$PROJ_ADJ_TRUE2/.ravenclaude/comfort-posture.yaml" <<'YAML'
prompt_optimizer:
  enabled: true
  mode: advisory
dispatch_config:
  enabled: false
  mode: shadow
YAML

PROJ_ADJ_FALSE1="$TMP/proj-adj-false1"
mkdir -p "$PROJ_ADJ_FALSE1/.ravenclaude"
cat >"$PROJ_ADJ_FALSE1/.ravenclaude/comfort-posture.yaml" <<'YAML'
dispatch_config:
  enabled: true
  mode: shadow
prompt_optimizer:
  enabled: false
YAML

check_short_circuit() {
  # $1=proj $2=expect(true|false) $3=session-id-suffix
  local proj="$1" expect="$2" sid="g264-5$3"
  local out
  out="$(printf '{"prompt":"%s"}' "$PROMPT_2ANCHORS" |
    PATH="$BARE_PATH" CLAUDE_PROJECT_DIR="$proj" CLAUDE_SESSION_ID="$sid" \
      PROMPT_OPTIMIZER_DEBUG=1 bash "$GATE_SH" 2>&1 >/dev/null)"
  if [ "$expect" = "true" ]; then
    # No claude on PATH -> an enabled+fallthrough run reaches TIER1_FAILOPEN,
    # proving the config gate read enabled=true and proceeded past the
    # short-circuit (rather than exiting silently before Tier-0 even ran).
    if printf '%s' "$out" | grep -q 'TIER1_FAILOPEN\|TIER0_'; then
      ok "5$3: adjacent dispatch_config block does NOT mask prompt_optimizer.enabled=true"
    else
      bad "5$3: expected the config gate to read enabled=true and proceed, got: $out"
    fi
  else
    if [ -z "$out" ]; then
      ok "5$3: adjacent dispatch_config.enabled=true does NOT leak into prompt_optimizer's own read"
    else
      bad "5$3: expected a silent short-circuit (prompt_optimizer.enabled=false), got: $out"
    fi
  fi
}

check_short_circuit "$PROJ_ADJ_TRUE1" true "a"
check_short_circuit "$PROJ_ADJ_TRUE2" true "b"
check_short_circuit "$PROJ_ADJ_FALSE1" false "c"

echo "  ── Gate 264 result: $PASS passed, $FAIL failed ──"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
