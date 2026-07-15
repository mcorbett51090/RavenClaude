#!/usr/bin/env bash
# test-gate70-codex-trust-hooks.sh — fixture tests for Gate 70 (Codex desktop
# trust review remediation: Findings 1, 2, 5).
#
# Proves that:
#   G70.1 — data-platform smell hook with STRICT=1 + violation exits 2 (BLOCK).
#   G70.2 — applied-statistics smell hook with STRICT=1 + violation exits 2.
#   G70.3 — edtech-partner-success smell hook with STRICT=1 + violation exits 2.
#   G70.4 — dod-gate.sh first-run trust check: blocks (exit 2) without confirm
#            file, allows execution after `touch <confirm-path>`, and bypasses
#            entirely when `definition_of_done.trusted: true` in posture YAML.
#   G70.5 — guard-web-access.sh first-use ask: emits permissionDecision:ask on
#            first hit to a YAML-whitelisted domain, silent allow on subsequent
#            hits same session, silent allow when `web_access.trusted: true`,
#            and the deny-list still wins over the ask.
#   G70.6 — Must-fail half: patch one STRICT branch back to `exit 1`, assert
#            the gate now detects the regression (proves G70.1-3 have teeth).
#
# Run directly:   bash plugins/ravenclaude-core/hooks/tests/test-gate70-codex-trust-hooks.sh
# Run via gate:   invoked by scripts/audit-gates.sh Gate 70.
#
# Design notes:
#   * Exit-code assertions are LITERAL — must be exactly 2, not just "non-zero".
#     A sloppy non-zero check would pass the pre-fix code (which returned 1).
#   * Each smell hook is invoked with $CLAUDE_TOOL_FILE_PATH pointing at a
#     synthetic file that trips one of its rules. The body content has to
#     actually match the regex the hook scans — different hooks have different
#     rule sets, so the test rigs a hook-specific known-bad payload for each.
#   * dod-gate test uses an `echo` cmd (zero side-effects) — the trust gate
#     itself doesn't care what the cmd does, only that it ran.
#   * web-access test uses an empty `deny:` list + a single `example.com`
#     `allow:` entry; the `permissionDecision: ask` JSON is parsed via grep.
#   * All tmp state cleaned up on exit (deterministic teardown).

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
FAILED=0
pass() { printf '  \xe2\x9c\x93 %s\n' "$1"; }
fail() { printf '  \xe2\x9c\x97 %s\n' "$1"; FAILED=$((FAILED + 1)); }

# ── G70.1 — data-platform smell hook: STRICT=1 + violation -> exit 2 ─────────
echo "── G70.1 — data-platform STRICT=1 blocks via exit 2 ─────────────────────"
HOOK_DP="$REPO_ROOT/plugins/data-platform/hooks/flag-data-platform-smells.sh"
tmp_dp="$(mktemp -d)"
# Trigger §3 #2 violation: a per-viewer-priced BI reference in a
# stack-decision-record.md file.
viol_dp="$tmp_dp/stack-decision-record.md"
printf '# Stack decision\n\nUse Looker for the embedded dashboards.\n' > "$viol_dp"
rc_dp=0
DATA_PLATFORM_STRICT=1 bash "$HOOK_DP" "$viol_dp" >/dev/null 2>&1 || rc_dp=$?
if [ "$rc_dp" -eq 2 ]; then
  pass "G70.1 STRICT=1 on violation -> exit 2 (block)"
else
  fail "G70.1 STRICT=1 on violation should exit 2; got rc=$rc_dp"
fi

# Negative half: STRICT=0 (default) on the same violation -> exit 0 (advisory).
rc_dp_adv=0
DATA_PLATFORM_STRICT=0 bash "$HOOK_DP" "$viol_dp" >/dev/null 2>&1 || rc_dp_adv=$?
if [ "$rc_dp_adv" -eq 0 ]; then
  pass "G70.1 STRICT=0 on same violation -> exit 0 (advisory)"
else
  fail "G70.1 STRICT=0 on violation should exit 0; got rc=$rc_dp_adv"
fi
rm -rf "$tmp_dp" 2>/dev/null || true

# ── G70.2 — applied-statistics smell hook: STRICT=1 + violation -> exit 2 ────
echo ""
echo "── G70.2 — applied-statistics STRICT=1 blocks via exit 2 ────────────────"
HOOK_AS="$REPO_ROOT/plugins/applied-statistics/hooks/flag-statistical-smells.sh"
tmp_as="$(mktemp -d)"
# Trigger correlation-as-causation pitfall (§4): correlation language + causal verbs in .md
viol_as="$tmp_as/analysis.md"
printf '# Analysis\n\nThe correlation between X and Y shows that X causes Y.\nThis correlation drives the outcome.\n' > "$viol_as"
rc_as=0
APPLIED_STATS_STRICT=1 bash "$HOOK_AS" "$viol_as" >/dev/null 2>&1 || rc_as=$?
if [ "$rc_as" -eq 2 ]; then
  pass "G70.2 STRICT=1 on violation -> exit 2 (block)"
else
  fail "G70.2 STRICT=1 on violation should exit 2; got rc=$rc_as"
fi
rc_as_adv=0
APPLIED_STATS_STRICT=0 bash "$HOOK_AS" "$viol_as" >/dev/null 2>&1 || rc_as_adv=$?
if [ "$rc_as_adv" -eq 0 ]; then
  pass "G70.2 STRICT=0 on same violation -> exit 0 (advisory)"
else
  fail "G70.2 STRICT=0 on violation should exit 0; got rc=$rc_as_adv"
fi
rm -rf "$tmp_as" 2>/dev/null || true

# ── G70.3 — edtech-partner-success smell hook: STRICT=1 + violation -> exit 2 ─
echo ""
echo "── G70.3 — edtech STRICT=1 blocks via exit 2 ────────────────────────────"
HOOK_PS="$REPO_ROOT/plugins/edtech-partner-success/hooks/flag-psm-anti-patterns.sh"
tmp_ps="$(mktemp -d)"
# Trigger boilerplate violation (§3 #11): "We value your partnership" in a
# qbr-shaped file.
viol_ps="$tmp_ps/q3-qbr-deck.md"
printf '# Q3 QBR Deck\n\nWe value your partnership.\n\nNext steps:\n- Follow up next quarter.\n' > "$viol_ps"
rc_ps=0
EDTECH_PS_STRICT=1 bash "$HOOK_PS" "$viol_ps" >/dev/null 2>&1 || rc_ps=$?
if [ "$rc_ps" -eq 2 ]; then
  pass "G70.3 STRICT=1 on violation -> exit 2 (block)"
else
  fail "G70.3 STRICT=1 on violation should exit 2; got rc=$rc_ps"
fi
rc_ps_adv=0
EDTECH_PS_STRICT=0 bash "$HOOK_PS" "$viol_ps" >/dev/null 2>&1 || rc_ps_adv=$?
if [ "$rc_ps_adv" -eq 0 ]; then
  pass "G70.3 STRICT=0 on same violation -> exit 0 (advisory)"
else
  fail "G70.3 STRICT=0 on violation should exit 0; got rc=$rc_ps_adv"
fi
rm -rf "$tmp_ps" 2>/dev/null || true

# ── G70.4 — dod-gate first-run trust check ───────────────────────────────────
echo ""
echo "── G70.4 — dod-gate first-run trust check ───────────────────────────────"
HOOK_DOD="$REPO_ROOT/plugins/ravenclaude-core/hooks/dod-gate.sh"
sb_dod="$(mktemp -d)"
mkdir -p "$sb_dod/.ravenclaude"
cat > "$sb_dod/.ravenclaude/comfort-posture.yaml" <<'YAML'
definition_of_done:
  cmd: "echo dod-trust-test"
  trusted: false
YAML
git -C "$sb_dod" init -q
echo "x" > "$sb_dod/x.py"
git -C "$sb_dod" add x.py 2>/dev/null

# G70.4a — first run, no confirm file, trusted:false -> exit 2 (block)
rc_dod1=0
CLAUDE_PROJECT_DIR="$sb_dod" bash "$HOOK_DOD" <<< "{\"cwd\":\"$sb_dod\",\"session_id\":\"s1\"}" >/dev/null 2>&1 || rc_dod1=$?
if [ "$rc_dod1" -eq 2 ]; then
  pass "G70.4a untrusted first run -> exit 2 (block)"
else
  fail "G70.4a untrusted first run should exit 2; got rc=$rc_dod1"
fi

# G70.4b — after touching confirm file -> exit 0 (proceeds; the echo cmd passes)
hash_dod="$(printf '%s' "echo dod-trust-test" | sha256sum | cut -c1-16)"
mkdir -p "$sb_dod/.ravenclaude/runs/dod-gate/s1"
touch "$sb_dod/.ravenclaude/runs/dod-gate/s1/confirmed-$hash_dod"
rc_dod2=0
CLAUDE_PROJECT_DIR="$sb_dod" bash "$HOOK_DOD" <<< "{\"cwd\":\"$sb_dod\",\"session_id\":\"s1\"}" >/dev/null 2>&1 || rc_dod2=$?
if [ "$rc_dod2" -eq 0 ]; then
  pass "G70.4b confirm-file present -> exit 0 (proceeds)"
else
  fail "G70.4b confirm-file present should exit 0; got rc=$rc_dod2"
fi

# G70.4c — trusted:true bypass -> exit 0 without confirm
sb_dod_trusted="$(mktemp -d)"
mkdir -p "$sb_dod_trusted/.ravenclaude"
cat > "$sb_dod_trusted/.ravenclaude/comfort-posture.yaml" <<'YAML'
definition_of_done:
  cmd: "echo trusted-bypass"
  trusted: true
YAML
git -C "$sb_dod_trusted" init -q
echo "x" > "$sb_dod_trusted/x.py"
git -C "$sb_dod_trusted" add x.py 2>/dev/null
rc_dod3=0
CLAUDE_PROJECT_DIR="$sb_dod_trusted" bash "$HOOK_DOD" <<< "{\"cwd\":\"$sb_dod_trusted\",\"session_id\":\"s2\"}" >/dev/null 2>&1 || rc_dod3=$?
if [ "$rc_dod3" -eq 0 ]; then
  pass "G70.4c trusted:true -> exit 0 (bypass)"
else
  fail "G70.4c trusted:true should exit 0; got rc=$rc_dod3"
fi
rm -rf "$sb_dod" "$sb_dod_trusted" 2>/dev/null || true

# ── G70.5 — guard-web-access first-use ask ───────────────────────────────────
echo ""
echo "── G70.5 — guard-web-access first-use ask ───────────────────────────────"
HOOK_WEB="$REPO_ROOT/plugins/ravenclaude-core/hooks/guard-web-access.sh"
sb_web="$(mktemp -d)"
mkdir -p "$sb_web/.ravenclaude"
cat > "$sb_web/.ravenclaude/web-access.yaml" <<'YAML'
allow:
  - example.com
deny: []
YAML

# G70.5a — first hit on whitelisted domain (no posture) -> emits "ask"
out_web1=$(CLAUDE_PROJECT_DIR="$sb_web" CLAUDE_SESSION_ID=w1 bash "$HOOK_WEB" <<< '{"tool_name":"WebFetch","tool_input":{"url":"https://example.com/x"}}' 2>/dev/null || true)
if printf '%s' "$out_web1" | grep -q '"permissionDecision":"ask"'; then
  pass "G70.5a first hit on YAML-whitelisted domain -> permissionDecision:ask"
else
  fail "G70.5a first hit should emit ask; got: $(printf '%s' "$out_web1" | head -c 200)"
fi

# G70.5b — CONSENT-ORDERING FIX: the seen-file is written by the PostToolUse hook
# (mark-web-domain-seen.sh) ONLY after a fetch proceeds — NOT pre-emptively by the
# PreToolUse hook. So a second PreToolUse WITHOUT an intervening allowed fetch must
# STILL ask (a denied first fetch must not silently auto-allow on retry).
HOOK_WEB_SEEN="$REPO_ROOT/plugins/ravenclaude-core/hooks/mark-web-domain-seen.sh"
out_web2_noconsent=$(CLAUDE_PROJECT_DIR="$sb_web" CLAUDE_SESSION_ID=w1 bash "$HOOK_WEB" <<< '{"tool_name":"WebFetch","tool_input":{"url":"https://example.com/y"}}' 2>/dev/null || true)
if printf '%s' "$out_web2_noconsent" | grep -q '"permissionDecision":"ask"'; then
  pass "G70.5b retry WITHOUT recorded consent -> still ask (no silent auto-allow)"
else
  fail "G70.5b retry without consent should ask; got: $(printf '%s' "$out_web2_noconsent" | head -c 200)"
fi

# G70.5b2 — once the PostToolUse hook records consent (a real fetch proceeded),
# the next PreToolUse hit silently allows for the rest of the session.
CLAUDE_PROJECT_DIR="$sb_web" CLAUDE_SESSION_ID=w1 bash "$HOOK_WEB_SEEN" <<< '{"tool_name":"WebFetch","tool_input":{"url":"https://example.com/x"}}' >/dev/null 2>&1 || true
out_web2=$(CLAUDE_PROJECT_DIR="$sb_web" CLAUDE_SESSION_ID=w1 bash "$HOOK_WEB" <<< '{"tool_name":"WebFetch","tool_input":{"url":"https://example.com/y"}}' 2>/dev/null || true)
if printf '%s' "$out_web2" | grep -q '"permissionDecision":"allow"'; then
  pass "G70.5b2 after PostToolUse records consent -> permissionDecision:allow"
else
  fail "G70.5b2 post-consent hit should emit allow; got: $(printf '%s' "$out_web2" | head -c 200)"
fi

# G70.5c — trusted:true posture -> silent allow on first hit
sb_web_trust="$(mktemp -d)"
mkdir -p "$sb_web_trust/.ravenclaude"
cat > "$sb_web_trust/.ravenclaude/web-access.yaml" <<'YAML'
allow:
  - example.org
deny: []
YAML
cat > "$sb_web_trust/.ravenclaude/comfort-posture.yaml" <<'YAML'
web_access:
  trusted: true
YAML
out_web3=$(CLAUDE_PROJECT_DIR="$sb_web_trust" CLAUDE_SESSION_ID=w2 bash "$HOOK_WEB" <<< '{"tool_name":"WebFetch","tool_input":{"url":"https://example.org/x"}}' 2>/dev/null || true)
if printf '%s' "$out_web3" | grep -q '"permissionDecision":"allow"'; then
  pass "G70.5c trusted:true -> permissionDecision:allow (no ask)"
else
  fail "G70.5c trusted:true should emit allow; got: $(printf '%s' "$out_web3" | head -c 200)"
fi

# G70.5d — deny-list still wins (the ask path doesn't relax denylist)
sb_web_deny="$(mktemp -d)"
mkdir -p "$sb_web_deny/.ravenclaude"
cat > "$sb_web_deny/.ravenclaude/web-access.yaml" <<'YAML'
allow: []
deny:
  - evil.com
YAML
rc_web4=0
CLAUDE_PROJECT_DIR="$sb_web_deny" CLAUDE_SESSION_ID=w3 bash "$HOOK_WEB" <<< '{"tool_name":"WebFetch","tool_input":{"url":"https://evil.com/x"}}' >/dev/null 2>&1 || rc_web4=$?
if [ "$rc_web4" -eq 2 ]; then
  pass "G70.5d deny-list still wins -> exit 2 (block)"
else
  fail "G70.5d deny-list should exit 2; got rc=$rc_web4"
fi
rm -rf "$sb_web" "$sb_web_trust" "$sb_web_deny" 2>/dev/null || true

# ── G70.6 — Must-fail half: patch a STRICT branch back to `exit 1` and prove
#             the gate detects the regression ────────────────────────────────
echo ""
echo "── G70.6 — must-fail half (patched STRICT->exit 1 must be caught) ───────"
tmp_patched="$(mktemp -d)"
# Copy the data-platform hook into a tmp dir and patch its STRICT branch back
# to `exit 1` (the pre-fix broken behavior).
cp "$HOOK_DP" "$tmp_patched/flag-data-platform-smells.sh"
# PORTABILITY: `sed -i` (no suffix arg) is GNU-only — BSD/macOS sed reads the NEXT TOKEN
# as the backup suffix, so the s/// became the suffix and the file became the script:
# "invalid command code f". The patch then never applied, the must-fail half did not fail,
# and this teeth assertion silently had NO TEETH on macOS. perl -pi is identical on both.
perl -pi -e 's/^  exit 2$/  exit 1/' "$tmp_patched/flag-data-platform-smells.sh"
viol_patched="$tmp_patched/stack-decision-record.md"
printf '# Stack decision\n\nUse Tableau Embedded for the dashboards.\n' > "$viol_patched"
rc_patched=0
DATA_PLATFORM_STRICT=1 bash "$tmp_patched/flag-data-platform-smells.sh" "$viol_patched" >/dev/null 2>&1 || rc_patched=$?
# The patched (broken) hook should exit 1, NOT 2. If our gate is asserting
# exit-2-literally, then this run should NOT match exit 2. If it returned 2,
# the gate is sloppy (would pass a non-zero check too).
if [ "$rc_patched" -eq 1 ]; then
  pass "G70.6 patched hook exits 1 (broken) — gate's exit-2-literal check has teeth"
elif [ "$rc_patched" -eq 2 ]; then
  fail "G70.6 patched hook returned 2 — gate would pass broken code (no teeth)"
else
  fail "G70.6 patched hook unexpected rc=$rc_patched (expected 1)"
fi
rm -rf "$tmp_patched" 2>/dev/null || true

# ── Summary ─────────────────────────────────────────────────────────────────
echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "Gate 70: all subtests passed"
  exit 0
else
  echo "Gate 70: $FAILED subtest(s) failed"
  exit 1
fi
