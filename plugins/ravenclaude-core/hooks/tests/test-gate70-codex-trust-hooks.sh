#!/usr/bin/env bash
# test-gate70-codex-trust-hooks.sh — fixture tests for Gate 70:
# EXTERNAL TRUST-REVIEW REMEDIATION (STRICT hooks + dod-gate + web-access).
#
# ⚠ THE FILENAME IS A MISNOMER AND IS KEPT ONLY FOR STABILITY (audit MH-31).
#
# "codex-trust-hooks" does NOT mean this tests Codex-as-a-host. It means these
# fixtures remediate findings that Codex produced **while reviewing RavenClaude** —
# good work, entirely unrelated to running ON Codex. Nothing below invokes a Codex
# envelope, config file, path, or CLI; the six subtests exercise three STRICT smell
# hooks, the dod-gate first-run trust check, and the web-access first-use ask.
#
# WHY THIS COMMENT EXISTS: the name laundered into a capability claim. It was cited
# as evidence that a Codex lane already existed — in the brief for the very audit
# that then found there was no Codex install path at all. A test name is read as a
# support claim by anyone grepping for a host.
#
# The real Codex-as-host gates are **155** (the env shim's invariants) and **156**
# (the sandbox posture emitter). If you are looking for what proves Codex support,
# it is those two, not this file.
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

# G70.4a — first run, no confirm file. The reason is JSON on stdout (exit 0).
# Copilot drops stderr when the hook exits 2 and shows only "code 2", so the
# authorize-file text never arrived. The text must name NOT DONE, forbid the
# re-ask, and tell the agent not to create the confirm file itself.
rc_dod1=0
out_dod1="$(CLAUDE_PROJECT_DIR="$sb_dod" bash "$HOOK_DOD" <<< "{\"cwd\":\"$sb_dod\",\"session_id\":\"s1\"}" 2>/dev/null)" || rc_dod1=$?
if [ "$rc_dod1" -eq 0 ] && printf '%s' "$out_dod1" | jq -e '.decision=="block" and .hookSpecificOutput.decision=="block" and (.reason | contains("VERDICT: NOT DONE")) and (.reason | contains("do not ask if the work is done")) and (.reason | contains("Do not create the confirm file"))' >/dev/null 2>&1; then
  pass "G70.4a untrusted first run -> stdout NOT DONE, human-only approve"
else
  fail "G70.4a trust block should be JSON NOT DONE on stdout; rc=$rc_dod1 got: $(printf '%s' "$out_dod1" | head -c 180)"
fi

# G70.4b — after touching OUT-OF-TREE confirm file -> exit 0 (proceeds).
# AppSec #1427: confirm lives under RC_DOD_CONFIRM_HOME (default ~/.ravenclaude/dod-confirm).
hash_dod="$(printf '%s' "echo dod-trust-test" | sha256sum | cut -c1-16)"
confirm_home_dod="$(mktemp -d)"
repo_key_dod="$(printf '%s' "$sb_dod" | sha256sum | tr -dc '0-9a-f' | cut -c1-16)"
mkdir -p "$confirm_home_dod/$repo_key_dod/s1"
touch "$confirm_home_dod/$repo_key_dod/s1/confirmed-$hash_dod"
rc_dod2=0
RC_DOD_CONFIRM_HOME="$confirm_home_dod" CLAUDE_PROJECT_DIR="$sb_dod" bash "$HOOK_DOD" \
  <<< "{\"cwd\":\"$sb_dod\",\"session_id\":\"s1\"}" >/dev/null 2>&1 || rc_dod2=$?
if [ "$rc_dod2" -eq 0 ]; then
  pass "G70.4b out-of-tree confirm-file present -> exit 0 (proceeds)"
else
  fail "G70.4b confirm-file present should exit 0; got rc=$rc_dod2"
fi
# G70.4b2 — in-tree legacy confirm path MUST NOT authorize (AppSec #1427).
mkdir -p "$sb_dod/.ravenclaude/runs/dod-gate/s1"
touch "$sb_dod/.ravenclaude/runs/dod-gate/s1/confirmed-$hash_dod"
rc_dod_intree=0
out_dod_intree="$(CLAUDE_PROJECT_DIR="$sb_dod" bash "$HOOK_DOD" \
  <<< "{\"cwd\":\"$sb_dod\",\"session_id\":\"s1\"}" 2>/dev/null)" || rc_dod_intree=$?
if [ "$rc_dod_intree" -eq 0 ] && printf '%s' "$out_dod_intree" | jq -e '.decision=="block"' >/dev/null 2>&1; then
  pass "G70.4b2 in-tree confirmed-* does not authorize (AppSec #1427)"
else
  fail "G70.4b2 in-tree confirm must still block; rc=$rc_dod_intree got: $(printf '%s' "$out_dod_intree" | head -c 180)"
fi

# G70.4c — trusted:true bypass -> exit 0, but ONLY when git blame shows the
# `trusted:` line and the `cmd:` line were last touched in DIFFERENT commits
# (b26-dodgate-cmd-exec-trusted-bypass — see dod-gate.sh's own comment block).
# Trust granted as a genuinely separate act, after the cmd already existed.
sb_dod_trusted="$(mktemp -d)"
mkdir -p "$sb_dod_trusted/.ravenclaude"
git -C "$sb_dod_trusted" init -q
git -C "$sb_dod_trusted" config user.email "test@example.com"
git -C "$sb_dod_trusted" config user.name "test"
cat > "$sb_dod_trusted/.ravenclaude/comfort-posture.yaml" <<'YAML'
definition_of_done:
  cmd: "echo trusted-bypass"
  trusted: false
YAML
git -C "$sb_dod_trusted" add .ravenclaude/comfort-posture.yaml
git -C "$sb_dod_trusted" commit -q -m "add cmd"
cat > "$sb_dod_trusted/.ravenclaude/comfort-posture.yaml" <<'YAML'
definition_of_done:
  cmd: "echo trusted-bypass"
  trusted: true
YAML
git -C "$sb_dod_trusted" add .ravenclaude/comfort-posture.yaml
git -C "$sb_dod_trusted" commit -q -m "trust it, separately"
echo "x" > "$sb_dod_trusted/x.py"
git -C "$sb_dod_trusted" add x.py 2>/dev/null
rc_dod3=0
CLAUDE_PROJECT_DIR="$sb_dod_trusted" bash "$HOOK_DOD" <<< "{\"cwd\":\"$sb_dod_trusted\",\"session_id\":\"s2\"}" >/dev/null 2>&1 || rc_dod3=$?
if [ "$rc_dod3" -eq 0 ]; then
  pass "G70.4c trusted:true, separate commit from cmd -> exit 0 (bypass)"
else
  fail "G70.4c trusted:true (separate commit) should exit 0; got rc=$rc_dod3"
fi

# G70.4d — the b26 regression itself: trusted:true set in the SAME commit as
# cmd (the finding's exact trigger — one PR/commit setting both fields
# together) must NOT bypass -> JSON block, confirm-file challenge stands.
sb_dod_samecommit="$(mktemp -d)"
mkdir -p "$sb_dod_samecommit/.ravenclaude"
git -C "$sb_dod_samecommit" init -q
git -C "$sb_dod_samecommit" config user.email "test@example.com"
git -C "$sb_dod_samecommit" config user.name "test"
cat > "$sb_dod_samecommit/.ravenclaude/comfort-posture.yaml" <<'YAML'
definition_of_done:
  cmd: "echo same-commit-attack"
  trusted: true
YAML
git -C "$sb_dod_samecommit" add .ravenclaude/comfort-posture.yaml
git -C "$sb_dod_samecommit" commit -q -m "one commit sets both cmd and trusted"
echo "x" > "$sb_dod_samecommit/x.py"
git -C "$sb_dod_samecommit" add x.py 2>/dev/null
rc_dod4=0
out_dod4="$(CLAUDE_PROJECT_DIR="$sb_dod_samecommit" bash "$HOOK_DOD" <<< "{\"cwd\":\"$sb_dod_samecommit\",\"session_id\":\"s3\"}" 2>/dev/null)" || rc_dod4=$?
if [ "$rc_dod4" -eq 0 ] && printf '%s' "$out_dod4" | jq -e '.decision=="block" and (.reason | contains("VERDICT: NOT DONE"))' >/dev/null 2>&1; then
  pass "G70.4d same-commit cmd+trusted:true (b26 attack) -> JSON block (still blocked)"
else
  fail "G70.4d same-commit cmd+trusted:true should still block; rc=$rc_dod4 got: $(printf '%s' "$out_dod4" | head -c 160)"
fi
# G70.4e — trust refusals count toward max_blocks, then the turn is released
# without ever running the command. The old path exited 2 forever, so Copilot
# re-prompted "are we done?" on every Stop.
sb_cap="$(mktemp -d)"
mkdir -p "$sb_cap/.ravenclaude"
cat > "$sb_cap/.ravenclaude/comfort-posture.yaml" <<'YAML'
definition_of_done:
  cmd: "touch ran-marker"
  max_blocks: 2
  trusted: false
YAML
git -C "$sb_cap" init -q
echo "x" > "$sb_cap/x.py"
git -C "$sb_cap" add x.py 2>/dev/null
rc_cap1=0
out_cap1="$(CLAUDE_PROJECT_DIR="$sb_cap" bash "$HOOK_DOD" <<< "{\"cwd\":\"$sb_cap\",\"session_id\":\"cap\"}" 2>/dev/null)" || rc_cap1=$?
rc_cap2=0
err_cap2="$(CLAUDE_PROJECT_DIR="$sb_cap" bash "$HOOK_DOD" <<< "{\"cwd\":\"$sb_cap\",\"session_id\":\"cap\"}" 2>&1 >/dev/null)" || rc_cap2=$?
if [ "$rc_cap1" -eq 0 ] && printf '%s' "$out_cap1" | jq -e '.decision=="block"' >/dev/null 2>&1 \
  && [ "$rc_cap2" -eq 0 ] && printf '%s' "$err_cap2" | grep -q 'VERDICT: STOP' \
  && [ ! -e "$sb_cap/ran-marker" ]; then
  pass "G70.4e trust blocks hit max_blocks then STOP without running cmd"
else
  fail "G70.4e expected JSON block then STOP and no ran-marker; got rc1=$rc_cap1 rc2=$rc_cap2 marker=$([ -e "$sb_cap/ran-marker" ] && echo yes || echo no)"
fi

# G70.4f — an authorized failing command blocks with VERDICT: NOT DONE (JSON).
sb_fail="$(mktemp -d)"
mkdir -p "$sb_fail/.ravenclaude"
cat > "$sb_fail/.ravenclaude/comfort-posture.yaml" <<'YAML'
definition_of_done:
  cmd: "false"
  trusted: false
YAML
git -C "$sb_fail" init -q
echo "x" > "$sb_fail/x.py"
git -C "$sb_fail" add x.py 2>/dev/null
hash_fail="$(printf '%s' "false" | sha256sum | tr -dc '0-9a-f' | cut -c1-16)"
confirm_home_fail="$(mktemp -d)"
repo_key_fail="$(printf '%s' "$sb_fail" | sha256sum | tr -dc '0-9a-f' | cut -c1-16)"
mkdir -p "$confirm_home_fail/$repo_key_fail/fail1"
touch "$confirm_home_fail/$repo_key_fail/fail1/confirmed-$hash_fail"
out_fail="$(RC_DOD_CONFIRM_HOME="$confirm_home_fail" CLAUDE_PROJECT_DIR="$sb_fail" bash "$HOOK_DOD" <<< "{\"cwd\":\"$sb_fail\",\"session_id\":\"fail1\"}" 2>/dev/null)" || true
if printf '%s' "$out_fail" | jq -e '.decision=="block" and .hookSpecificOutput.decision=="block" and .hookSpecificOutput.hookEventName=="Stop" and (.reason | contains("VERDICT: NOT DONE")) and (.reason | contains("do not ask if the work is done"))' >/dev/null 2>&1; then
  pass "G70.4f failing command -> JSON NOT DONE checklist (top-level and Local Chat)"
else
  fail "G70.4f failing command should emit VERDICT: NOT DONE; got: $(printf '%s' "$out_fail" | head -c 180)"
fi

# G70.4g — Copilot stop adapter forwards that verdict (top-level AND nested)
# and does not substitute the old "not yet verified done" prompt.
ADAPTER="$REPO_ROOT/plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh"
out_ad="$(printf '%s' "{\"cwd\":\"$sb_dod\",\"sessionId\":\"s-adapter\",\"stop_hook_active\":false}" | CLAUDE_PROJECT_DIR="$sb_dod" bash "$ADAPTER" stop "$HOOK_DOD" 2>/dev/null)" || true
if printf '%s' "$out_ad" | jq -e '.decision=="block" and .hookSpecificOutput.decision=="block" and .hookSpecificOutput.hookEventName=="Stop" and (.reason | contains("VERDICT: NOT DONE")) and (.reason | contains("not yet verified done") | not)' >/dev/null 2>&1; then
  pass "G70.4g Copilot stop adapter forwards NOT DONE, not the vague fallback"
else
  fail "G70.4g adapter stop verdict wrong; got: $(printf '%s' "$out_ad" | head -c 220)"
fi

# G70.4h — after max_blocks the adapter allows the stop and shows STOP to the
# user. It must not emit decision:block (that text would be the next prompt).
sb_stop="$(mktemp -d)"
mkdir -p "$sb_stop/.ravenclaude"
cat > "$sb_stop/.ravenclaude/comfort-posture.yaml" <<'YAML'
definition_of_done:
  cmd: "false"
  max_blocks: 1
  trusted: false
YAML
git -C "$sb_stop" init -q
echo "x" > "$sb_stop/x.py"
git -C "$sb_stop" add x.py 2>/dev/null
out_stop="$(printf '%s' "{\"cwd\":\"$sb_stop\",\"sessionId\":\"stopcap\",\"stop_hook_active\":true}" | CLAUDE_PROJECT_DIR="$sb_stop" bash "$ADAPTER" stop "$HOOK_DOD" 2>/dev/null)" || true
if printf '%s' "$out_stop" | jq -e '(.systemMessage | contains("VERDICT: STOP")) and (.decision == null)' >/dev/null 2>&1; then
  pass "G70.4h cap release is systemMessage STOP, not another block prompt"
else
  fail "G70.4h cap release should warn STOP without decision block; got: $(printf '%s' "$out_stop" | head -c 220)"
fi

# G70.4i / G70.4j — AppSec #1428: Stop reason and systemMessage must scrub
# secret-shaped tokens (ghp_/sk_live_/xoxb-) before they reach Copilot.
# Assemble at runtime so the contiguous literals never land in git (push
# protection otherwise blocks the fake Stripe-shaped fixture).
_FAKE_GHP="ghp_$(printf 'A%.0s' {1..36})"
_FAKE_SK="sk_""live_$(printf 'B%.0s' {1..28})"
_FAKE_XOXB="xoxb-$(printf 'C%.0s' {1..20})"
sb_scrub="$(mktemp -d)"
# Fake Stop hook: exit 2 + secret-bearing stderr (block path, no JSON reason).
cat > "$sb_scrub/hook-block.sh" <<HOOK
#!/usr/bin/env bash
printf 'blocked with %s and %s and %s\n' '$_FAKE_GHP' '$_FAKE_SK' '$_FAKE_XOXB' >&2
exit 2
HOOK
chmod +x "$sb_scrub/hook-block.sh"
out_scrub_block="$(printf '%s' "{\"cwd\":\"$sb_scrub\",\"sessionId\":\"scrub1\",\"stop_hook_active\":false}" \
  | CLAUDE_PROJECT_DIR="$sb_scrub" bash "$ADAPTER" stop "$sb_scrub/hook-block.sh" 2>/dev/null)" || true
if printf '%s' "$out_scrub_block" | jq -e '.decision=="block"' >/dev/null 2>&1 \
  && ! printf '%s' "$out_scrub_block" | grep -qF "$_FAKE_GHP" \
  && ! printf '%s' "$out_scrub_block" | grep -qF "$_FAKE_SK" \
  && ! printf '%s' "$out_scrub_block" | grep -qF "$_FAKE_XOXB"; then
  pass "G70.4i Stop block reason scrubs ghp_/sk_live_/xoxb- (AppSec #1428)"
else
  fail "G70.4i secrets leaked in block reason; got: $(printf '%s' "$out_scrub_block" | head -c 220)"
fi
# JSON stdout reason path (also must scrub).
cat > "$sb_scrub/hook-json.sh" <<HOOK
#!/usr/bin/env bash
jq -cn --arg r "json reason ${_FAKE_GHP} ${_FAKE_SK} ${_FAKE_XOXB}" \
  '{decision:"block",reason:\$r,hookSpecificOutput:{hookEventName:"Stop",decision:"block",reason:\$r}}'
exit 0
HOOK
chmod +x "$sb_scrub/hook-json.sh"
out_scrub_json="$(printf '%s' "{\"cwd\":\"$sb_scrub\",\"sessionId\":\"scrub1b\",\"stop_hook_active\":false}" \
  | CLAUDE_PROJECT_DIR="$sb_scrub" bash "$ADAPTER" stop "$sb_scrub/hook-json.sh" 2>/dev/null)" || true
if printf '%s' "$out_scrub_json" | jq -e '.decision=="block"' >/dev/null 2>&1 \
  && ! printf '%s' "$out_scrub_json" | grep -qF "$_FAKE_GHP" \
  && ! printf '%s' "$out_scrub_json" | grep -qF "$_FAKE_SK" \
  && ! printf '%s' "$out_scrub_json" | grep -qF "$_FAKE_XOXB"; then
  pass "G70.4i2 Stop JSON reason scrubs ghp_/sk_live_/xoxb- (AppSec #1428)"
else
  fail "G70.4i2 secrets leaked in JSON reason; got: $(printf '%s' "$out_scrub_json" | head -c 220)"
fi
# Fake Stop hook: exit 0 + VERDICT: STOP on stderr with secrets (systemMessage path).
cat > "$sb_scrub/hook-stop.sh" <<HOOK
#!/usr/bin/env bash
printf 'VERDICT: STOP\nrelease with %s and %s and %s\n' '$_FAKE_GHP' '$_FAKE_SK' '$_FAKE_XOXB' >&2
exit 0
HOOK
chmod +x "$sb_scrub/hook-stop.sh"
out_scrub_stop="$(printf '%s' "{\"cwd\":\"$sb_scrub\",\"sessionId\":\"scrub2\",\"stop_hook_active\":true}" \
  | CLAUDE_PROJECT_DIR="$sb_scrub" bash "$ADAPTER" stop "$sb_scrub/hook-stop.sh" 2>/dev/null)" || true
if printf '%s' "$out_scrub_stop" | jq -e '(.systemMessage | contains("VERDICT: STOP")) and (.decision == null)' >/dev/null 2>&1 \
  && ! printf '%s' "$out_scrub_stop" | grep -qF "$_FAKE_GHP" \
  && ! printf '%s' "$out_scrub_stop" | grep -qF "$_FAKE_SK" \
  && ! printf '%s' "$out_scrub_stop" | grep -qF "$_FAKE_XOXB"; then
  pass "G70.4j Stop systemMessage scrubs ghp_/sk_live_/xoxb- (AppSec #1428)"
else
  fail "G70.4j secrets leaked in systemMessage; got: $(printf '%s' "$out_scrub_stop" | head -c 220)"
fi

rm -rf "$sb_dod" "$sb_dod_trusted" "$sb_dod_samecommit" "$sb_cap" "$sb_fail" "$sb_stop" "$sb_scrub" 2>/dev/null || true

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
