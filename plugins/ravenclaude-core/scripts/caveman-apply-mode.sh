#!/usr/bin/env bash
# caveman-apply-mode.sh — P2 of the caveman auto-routing plan
# (.ravenclaude/runs/forge/caveman-routing-decision-tree/plan.md § "P2 — Applier").
#
# The applier: writes caveman's per-session mode by calling caveman's OWN
# `writeSessionMode`, resolved fresh at runtime (never hardcoding its
# content-hash-keyed cache path). This file is the ⛔ ONE-WAY-DOOR component —
# it is built here (P2), and the door OPENS only when a future phase (P3+)
# actually wires something to call it against a live session. Until then this
# script exists, is self-tested, and nothing invokes it. The three mandatory
# rollback/kill-switch parts below are NOT optional — see plan.md's "P2 —
# Applier" section and the risk-matrix's "One-way-door phases" row.
#
# ─────────────────────────────────────────────────────────────────────────────
# Usage
# ─────────────────────────────────────────────────────────────────────────────
#   caveman-apply-mode.sh <session_id> <mode> [--typed-caveman-command]
#       Apply <mode> ("off" | "lite" | "full" | ... — whatever caveman's own
#       VALID_MODES accepts) for <session_id>. On the FIRST call for a given
#       session, snapshots the entry state before touching anything (mitigation
#       1). --typed-caveman-command marks that the user typed a literal
#       `/caveman …` command this session (mitigation 2's second trigger); the
#       caller (a future hook body) is responsible for detecting that from the
#       transcript and passing this flag — this script has no transcript access
#       of its own.
#
#   caveman-apply-mode.sh --restore <session_id>
#       Write this session's snapshotted `user_mode_at_entry` back AND restore
#       the legacy mirror `.caveman-active` to its captured pre-entry state
#       (mitigation 3 -- see the header note below on HOW the mirror half is
#       done, without ever writing to the mirror file directly). Undoes a PAST
#       write; does not touch the posture knob that gates FUTURE ones (that is
#       `caveman_routing: off`, read by the not-yet-built hook body, not by
#       this script).
#
#   caveman-apply-mode.sh --self-test
#       Runs the built-in fixture suite (isolated temp dirs only, never real
#       host state). Exit 0 = all pass, 1 = a failure. Safe to run anywhere.
#
# ─────────────────────────────────────────────────────────────────────────────
# Output contract
# ─────────────────────────────────────────────────────────────────────────────
# On stdout, exactly ONE line of hand-built JSON (mirrors forge-worktree.sh's
# own printf-JSON receipt convention — no jq dependency, every value is either
# an internally-controlled fixed token or has been run through a restricted-
# charset filter before being interpolated, so no untrusted file content can
# break the JSON or smuggle anything through it):
#
#   {"status":"<token>","candidates":"<N>","resolved_via":"<cache|standalone|none>",
#    "applied_mode":"<mode|>","restored_mode":"<mode|>","readback_ok":"<true|false|>",
#    "manual_override":"<true|false|>","mirror_restore_ok":"<true|false|>","error":"<token|>"}
#
# `mirror_restore_ok` is present only on a --restore call (empty otherwise): it
# reports whether the legacy mirror `.caveman-active` was successfully brought
# back to its captured `legacy_mirror_at_entry` state, independently of
# `readback_ok` (which reports only the per-session mode). `status` is
# `restore-readback-mismatch` if EITHER check fails, so a mirror-only failure
# still routes through the same warn-emission path as a session-mode mismatch.
#
# status is one of: applied | restored | held-manual-override |
#   readback-mismatch | restore-readback-mismatch | noop-no-node |
#   noop-no-caveman | snapshot-failed-aborted | write-failed |
#   restore-write-failed | restore-failed-no-snapshot | noop-invalid-session-id
#
# Exit code is ALWAYS 0 for apply/restore (fail-safe by contract — every path
# above is a legitimate, handled outcome, never a crash) except a genuinely
# unrecoverable internal error, which the `set -euo pipefail` below still
# converts into a clean non-zero exit rather than a partial write. --self-test
# exits 0 (pass) or 1 (fail).
#
# ─────────────────────────────────────────────────────────────────────────────
# The three mandatory rollback / kill-switch parts (plan.md, all required)
# ─────────────────────────────────────────────────────────────────────────────
#   1. Pre-write snapshot. On the FIRST apply call of a session (no state file
#      yet), reads `readSessionModeRaw` (the literal, no-fallback value) AND
#      stats the legacy mirror `.caveman-active` directly (caveman exports no
#      mirror reader — plan.md explicitly instructs "stat the legacy mirror",
#      a read of its DATA file, not a write/patch of its CODE, so this stays
#      inside the C11 black-box constraint), BEFORE any write. Both go to
#      `.ravenclaude/runs/<session>/caveman-route-state.json` as
#      `user_mode_at_entry` / `legacy_mirror_at_entry`. If the snapshot cannot
#      be written (no CLAUDE_PROJECT_DIR, unwritable run dir, readSessionModeRaw
#      throws), the write is ABORTED — status=snapshot-failed-aborted, no
#      writeSessionMode call is ever made.
#   2. Manual-override latch. If the snapshotted entry mode is present AND its
#      canonical form is not "off" (caveman treats "off" as its own quiescent
#      base state everywhere — the collapse target of both writeSessionMode's
#      null-handling and resolveActiveMode's offToNull), OR the caller passed
#      --typed-caveman-command, `manual_override: true` is written into the
#      state file and this and every SUBSEQUENT apply call this session holds
#      (status=held-manual-override, no write). ⛔ INTERPRETATION NOTE: the
#      plan says "a non-default value"; caveman's true default is whatever
#      getDefaultMode() would produce, which this script does not require as
#      one of its three load-bearing exports (only writeSessionMode /
#      readSessionModeRaw / resolveActiveMode are required per this phase's
#      spec). Comparing against "off" specifically — rather than calling an
#      optional, unknown-signature getDefaultMode() — is the deliberate,
#      documented choice here; see the P2 coder's final report for the
#      reasoning. --restore is exempt from this latch (it must always be able
#      to undo a past write, even a held-manual-override session's own).
#   3. --restore. Reads the snapshot and writes `user_mode_at_entry` back via
#      the same sanctioned writer (never a raw file write — that would be
#      exactly the reimplementation-risk plan.md rejected plan-B's writer for).
#      ⛔ HONEST LIMIT (R10 residual, session-file half, stated rather than
#      glossed over): when `user_mode_at_entry` is null (no prior per-session
#      value), restoring writes the literal string "off" rather than deleting
#      the session file to recreate true absence — caveman's own fail-safe
#      property makes the two behaviorally equivalent for `resolveActiveMode`
#      (both collapse to "no active mode"), but they differ for
#      `readSessionModeRaw`. Recreating true absence would require
#      re-deriving caveman's un-exported `sessionActivePath()`
#      path-construction + `validateSessionId()` whitelist ourselves —
#      exactly the "reimplement caveman's internals" risk the whole
#      plan-A-over-plan-B verdict was decided to avoid.
#      ⛔ THE MIRROR HALF (fixed here -- previously a real gap, caught by Gate
#      265's dev-only round trip; see the "restore" action below for the
#      code). `writeSessionMode(claudeDir, sessionId, modeOrNull)` couples ONE
#      argument to BOTH the session file AND the machine-wide mirror -- there
#      is no way to ask it for "session -> X, mirror -> Y" in a single call
#      when X and Y differ. The naive restore (call it once with
#      `restoreMode`) therefore let the session-file write's OWN coupled
#      mirror side-effect silently clobber the mirror to whatever
#      `restoreMode` implies, regardless of what `legacy_mirror_at_entry`
#      actually captured -- e.g. restoring a session with no prior value
#      (`restoreMode = null` -> canonical `off`) always UNLINKS the mirror,
#      even when the snapshot shows the mirror held `full` before this
#      session's first write. Fixed by comparing the mirror's state
#      immediately after the session-file restore against the captured
#      `legacy_mirror_at_entry`, and — ONLY when they disagree — making a
#      SECOND `writeSessionMode` call against a throwaway, freshly-generated
#      scratch session id (never the real one, never a real prior session)
#      whose sole purpose is to aim that same coupled mirror side-effect at
#      the captured value without re-touching the just-restored session file
#      (the mirror path is not session-scoped, so any valid session id reaches
#      it). The scratch call's own harmless session-file byproduct is deleted
#      immediately after (best-effort, direct unlink of a file this script
#      itself just created via the scratch id — not a read/write of caveman's
#      OWN data, and not a reimplementation of its writer). Still "the same
#      sanctioned writer, never a raw file write" — plan.md's explicit
#      instruction for --restore — just invoked twice with two different
#      session identities instead of once. This is still bounded, not
#      absolute: a CONCURRENT session that mutates the shared mirror in the
#      narrow window between our restore and its own read can still see its
#      write clobbered by ours (or vice versa) — the same last-write-wins
#      exposure plan.md's R10 already documents as "bounded and mitigated —
#      not eliminated," now applying to --restore's mirror write instead of
#      only to a live apply's.
#
# ─────────────────────────────────────────────────────────────────────────────
# Read-back verification (adopted from plan-B, plan.md)
# ─────────────────────────────────────────────────────────────────────────────
# Immediately after every writeSessionMode call, re-read via the SAME resolved
# module's resolveActiveMode and confirm it decodes to the intended mode
# (off → null; anything else → that literal value — resolveActiveMode's own
# offToNull collapse). On mismatch: status=readback-mismatch (or
# restore-readback-mismatch), AND a warn-tier hook event is emitted —
# `_emit_hook_event "caveman-apply-mode.sh" "warn" "" "" \
#   "caveman-route-readback-mismatch" 0` — sourced from the shared
# hooks/_emit-event.sh substrate. This is NOT `_advise.sh`'s additionalContext
# channel: this script is a subprocess invoked BY a future hook body (never a
# registered hook itself), so it has no stdout envelope Claude Code will ever
# read as model-facing output — C9's discipline ("stderr at exit 0 is
# undelivered to the model") is exactly why a silent stderr line is not enough
# here either, and the audit-substrate emit (the same mechanism every other
# warn-tier verdict in this repo already uses) is the reachable, observable
# channel for a subprocess at this position in the call chain.
#
# ─────────────────────────────────────────────────────────────────────────────
# Version-drift resolution order (runtime, every invocation — C11: caveman is
# a read-only black box; nothing under its plugin cache is ever written)
# ─────────────────────────────────────────────────────────────────────────────
#   1. ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/cache/caveman/caveman/*/src/hooks/caveman-config.js
#      (glob, newest mtime wins — candidate COUNT is always reported so a
#      multi-version cache, which makes "newest" a guess, is visible)
#   2. ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/caveman-config.js  (standalone install)
#   3. neither resolves, OR the resolved module is missing any of
#      writeSessionMode / readSessionModeRaw / resolveActiveMode as a function
#      → status=noop-no-caveman, never an error.
# (The plan's own code block writes step 1 as bare $CLAUDE_CONFIG_DIR and step
# 2 with the ${:-$HOME/.claude} default; this script applies the default
# uniformly to both, matching how P0.2/P0.3 resolved it against real host
# state and avoiding two different bases for one conceptual "claude dir".)
#
# ─────────────────────────────────────────────────────────────────────────────
# Other requirements
# ─────────────────────────────────────────────────────────────────────────────
# `node` absent → exit 0, status=noop-no-node. `set -euo pipefail`. Bash-3.2-
# safe (C10 — no `declare -A`, `mapfile`, `${x^^}`, `shopt -s globstar`; no GNU
# `timeout` / `grep -P` / `sed -i`). Every filesystem write this script makes
# is a direct bash/node process write — never the agent's Write/Edit tool
# (C14); that constraint is about this script's OWN runtime behavior when it
# is eventually invoked as part of a hook's call chain, which is naturally
# true of a bash script with no callback into the authoring agent.

set -euo pipefail

SESSION_ID_RE='^[A-Za-z0-9_-]{1,128}$'

# ---- tiny JSON-string helpers (no jq dependency; every value we build the
#      JSON from is either a fixed internal token or has been run through
#      _safe_enum below, so hand-building is safe) --------------------------

_print_json() {
  # $1..$N are "key=value" pairs; value may be empty.
  local kv k v out="{"
  local first=1
  for kv in "$@"; do
    k="${kv%%=*}"
    v="${kv#*=}"
    if [ "$first" -eq 1 ]; then first=0; else out="${out},"; fi
    out="${out}\"${k}\":\"${v}\""
  done
  out="${out}}"
  printf '%s\n' "$out"
}

_json_field() {
  # $1=json blob $2=field name -> prints the field's string value (or "")
  printf '%s' "$1" | grep -o "\"$2\":\"[^\"]*\"" | head -n1 | sed -E "s/\"$2\":\"([^\"]*)\"/\1/"
}

# ---- resolve where to run node from ----------------------------------------

_resolve_claude_dir() {
  printf '%s' "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
}

# The embedded node script. Written to a scratch temp file per invocation
# (mktemp + trap cleanup, matching thing-seat.sh's own pattern) rather than
# `node -e "$huge_string"`, to avoid quoting hazards with a script this size.
_write_node_script() {
  # $1 = destination path
  cat > "$1" <<'RC_CAVEMAN_APPLY_JS'
'use strict';
const fs = require('fs');
const path = require('path');

function out(kv) {
  const parts = [];
  for (const k of Object.keys(kv)) {
    parts.push(JSON.stringify(k) + ':' + JSON.stringify(String(kv[k])));
  }
  process.stdout.write('{' + parts.join(',') + '}\n');
}

// Restrict any value derived from caveman's own on-disk data (never a value
// we control ourselves) to a safe charset before it can reach our own JSON
// output — caveman's contract already caps these at VALID_MODES membership
// and 64 bytes, but this is defense-in-depth, not trust.
function safeEnum(v) {
  if (v === null || v === undefined) return '';
  const s = String(v);
  if (/^[A-Za-z0-9_.-]{0,64}$/.test(s)) return s;
  return 'unrecognized';
}

const argv = process.argv.slice(2);
const claudeDir = argv[0];
const stateFile = argv[1];
const sessionId = argv[2];
const modeArg = argv[3] === '' ? null : argv[3];
const manualTyped = argv[4] === '1';
const action = argv[5];

// ---- version-drift resolution ---------------------------------------------

function globNewestCacheModule(dir) {
  const base = path.join(dir, 'plugins', 'cache', 'caveman', 'caveman');
  let entries = [];
  try {
    entries = fs.readdirSync(base, { withFileTypes: true });
  } catch (e) {
    return { count: 0, newest: null };
  }
  const found = [];
  for (const ent of entries) {
    if (!ent.isDirectory || !ent.isDirectory()) continue;
    const p = path.join(base, ent.name, 'src', 'hooks', 'caveman-config.js');
    try {
      const st = fs.statSync(p);
      if (st.isFile()) found.push({ p: p, mtime: st.mtimeMs });
    } catch (e) { /* candidate dir has no caveman-config.js — skip */ }
  }
  found.sort(function (a, b) { return b.mtime - a.mtime; });
  return { count: found.length, newest: found.length ? found[0].p : null };
}

function fnsOk(c) {
  return !!c
    && typeof c.writeSessionMode === 'function'
    && typeof c.readSessionModeRaw === 'function'
    && typeof c.resolveActiveMode === 'function';
}

const globResult = globNewestCacheModule(claudeDir);
const candidates = globResult.count;
let cfg = null;
let resolvedVia = 'none';

if (globResult.newest) {
  try {
    delete require.cache[require.resolve(globResult.newest)];
    const candidate = require(globResult.newest);
    if (fnsOk(candidate)) { cfg = candidate; resolvedVia = 'cache'; }
  } catch (e) { /* fall through to standalone */ }
}

if (!cfg) {
  const standalone = path.join(claudeDir, 'hooks', 'caveman-config.js');
  try {
    if (fs.existsSync(standalone)) {
      delete require.cache[require.resolve(standalone)];
      const candidate = require(standalone);
      if (fnsOk(candidate)) { cfg = candidate; resolvedVia = 'standalone'; }
    }
  } catch (e) { /* fall through to noop */ }
}

if (!fnsOk(cfg)) {
  out({ status: 'noop-no-caveman', candidates: candidates, resolved_via: 'none' });
  process.exit(0);
}

// ---- direct read of the legacy mirror's DATA file (never its own writer —
//      plan.md explicitly says "stat the legacy mirror"; this is a read of
//      caveman's mode-store data, not a write/patch of its code, so it stays
//      inside C11's black-box boundary) -------------------------------------

const legacyMirrorPath = path.join(claudeDir, '.caveman-active');
function mirrorState() {
  try {
    const st = fs.statSync(legacyMirrorPath);
    if (!st.isFile()) return { exists: false, contents: null };
    const raw = fs.readFileSync(legacyMirrorPath, 'utf8').trim();
    return { exists: true, contents: raw };
  } catch (e) {
    return { exists: false, contents: null };
  }
}

function canonicalOf(mode) {
  if (!mode || mode === 'off') return 'off';
  return mode;
}
function decodedOf(canonical) {
  return canonical === 'off' ? null : canonical;
}

function writeStateFileAtomic(obj) {
  fs.mkdirSync(path.dirname(stateFile), { recursive: true });
  const tmp = stateFile + '.tmp-' + process.pid;
  fs.writeFileSync(tmp, JSON.stringify(obj, null, 2) + '\n', { mode: 0o600 });
  fs.renameSync(tmp, stateFile);
}

if (action === 'apply') {
  let stateExists = false;
  let priorState = null;
  try {
    if (fs.existsSync(stateFile)) {
      const raw = fs.readFileSync(stateFile, 'utf8');
      priorState = JSON.parse(raw);
      stateExists = true;
    }
  } catch (e) {
    // Unreadable/corrupt state reads as "no valid snapshot yet" — we will
    // re-snapshot below rather than trust a broken file. This is the safe
    // direction: a corrupt state file cannot silently disable the latch,
    // because a fresh, valid snapshot always overwrites it before any write.
    stateExists = false;
    priorState = null;
  }

  if (stateExists && priorState && priorState.manual_override === true) {
    out({ status: 'held-manual-override', candidates: candidates, resolved_via: resolvedVia, manual_override: 'true' });
    process.exit(0);
  }

  if (!stateExists) {
    // ---- mitigation 1: pre-write snapshot, BEFORE any write --------------
    let rawEntry;
    try {
      rawEntry = cfg.readSessionModeRaw(claudeDir, sessionId);
    } catch (e) {
      out({ status: 'snapshot-failed-aborted', candidates: candidates, resolved_via: resolvedVia, error: 'readSessionModeRaw-threw' });
      process.exit(0);
    }
    const userModeAtEntry = (rawEntry === undefined) ? null : rawEntry;
    const legacyMirrorAtEntry = mirrorState();

    // ---- mitigation 2: manual-override latch ------------------------------
    // See the script header's INTERPRETATION NOTE: "non-default" is read as
    // "present and not canonically off" rather than requiring caveman's own
    // (optional, unknown-signature) getDefaultMode().
    const nonDefaultEntry = (userModeAtEntry !== null) && (canonicalOf(userModeAtEntry) !== 'off');
    const manualOverride = nonDefaultEntry || manualTyped;

    const snapshot = {
      user_mode_at_entry: userModeAtEntry,
      legacy_mirror_at_entry: legacyMirrorAtEntry,
      manual_override: manualOverride,
      session_id: sessionId,
      snapshotted_at: new Date().toISOString()
    };

    try {
      writeStateFileAtomic(snapshot);
    } catch (e) {
      out({ status: 'snapshot-failed-aborted', candidates: candidates, resolved_via: resolvedVia, error: 'snapshot-write-failed' });
      process.exit(0);
    }

    if (manualOverride) {
      out({ status: 'held-manual-override', candidates: candidates, resolved_via: resolvedVia, manual_override: 'true' });
      process.exit(0);
    }
  }

  // ---- perform the write + immediate read-back verification --------------
  const canonical = canonicalOf(modeArg);
  try {
    cfg.writeSessionMode(claudeDir, sessionId, modeArg);
  } catch (e) {
    out({ status: 'write-failed', candidates: candidates, resolved_via: resolvedVia, error: 'writeSessionMode-threw' });
    process.exit(0);
  }

  let decodedActual;
  try {
    decodedActual = cfg.resolveActiveMode(claudeDir, sessionId);
  } catch (e) {
    decodedActual = undefined;
  }
  const expectedDecoded = decodedOf(canonical);
  const readbackOk = (decodedActual === expectedDecoded);

  out({
    status: readbackOk ? 'applied' : 'readback-mismatch',
    candidates: candidates,
    resolved_via: resolvedVia,
    applied_mode: safeEnum(canonical),
    readback_ok: readbackOk ? 'true' : 'false',
    manual_override: 'false'
  });
  process.exit(0);
}

if (action === 'restore') {
  let priorState;
  try {
    priorState = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
  } catch (e) {
    out({ status: 'restore-failed-no-snapshot', candidates: candidates, resolved_via: resolvedVia });
    process.exit(0);
  }

  const restoreMode = (typeof priorState.user_mode_at_entry === 'undefined') ? null : priorState.user_mode_at_entry;
  // Old-format defensive fallback only -- this script has ALWAYS captured
  // legacy_mirror_at_entry unconditionally on every first apply call (see the
  // "apply" branch above), so this branch is reachable only against a state
  // file written by a version that predates that capture.
  const mirrorSnapshotRaw = priorState.legacy_mirror_at_entry;
  const mirrorSnapshot = (mirrorSnapshotRaw && typeof mirrorSnapshotRaw === 'object')
    ? mirrorSnapshotRaw
    : { exists: false, contents: null };

  try {
    // ⛔ HONEST LIMIT (see header): when restoreMode is null, this writes the
    // literal "off" rather than deleting the session file — see the R10
    // discussion in the header comment for why.
    cfg.writeSessionMode(claudeDir, sessionId, restoreMode);
  } catch (e) {
    out({ status: 'restore-write-failed', candidates: candidates, resolved_via: resolvedVia });
    process.exit(0);
  }

  // ---- restore the legacy mirror to its captured pre-entry state ---------
  // See the header's "THE MIRROR HALF" note for the full reasoning. In short:
  // writeSessionMode's mirror side-effect above is driven entirely by
  // restoreMode, not by what the mirror held before this session's first
  // write -- so it only happens to land on the captured value when the two
  // coincide. Detect the (common) case where they already agree and do
  // nothing further; otherwise make a second writeSessionMode call against a
  // throwaway scratch session id whose only job is to aim that same coupled
  // side-effect at the captured mirror value, without re-touching the
  // session file we just correctly restored above.
  const mirrorAfterSessionRestore = mirrorState();
  const mirrorAlreadyMatches = mirrorSnapshot.exists
    ? (mirrorAfterSessionRestore.exists && mirrorAfterSessionRestore.contents === mirrorSnapshot.contents)
    : !mirrorAfterSessionRestore.exists;

  if (!mirrorAlreadyMatches) {
    const sessionsDirPath = path.join(claudeDir, '.caveman-sessions');
    let scratchSid = null;
    for (let attempt = 0; attempt < 5 && !scratchSid; attempt++) {
      const candidate = 'rc-mirror-restore-' + process.pid + '-' + Date.now() + '-' +
        Math.random().toString(36).slice(2);
      // 128-char whitelist ceiling shared with caveman's own
      // validateSessionId -- stay comfortably under it.
      if (candidate.length > 100) continue;
      if (!fs.existsSync(path.join(sessionsDirPath, candidate + '.mode'))) scratchSid = candidate;
    }
    if (scratchSid) {
      try {
        // mirrorSnapshot.exists -> land its captured contents through the
        // SAME sanctioned writer (writeSessionMode itself refuses anything
        // outside its own VALID_MODES, so a corrupt/foreign snapshot value
        // silently no-ops here rather than writing garbage -- no VALID_MODES
        // check needed on our side). !exists -> null triggers the unlink
        // branch, restoring true absence.
        cfg.writeSessionMode(claudeDir, scratchSid, mirrorSnapshot.exists ? mirrorSnapshot.contents : null);
      } catch (e) { /* mirrorRestoredOk below reflects whatever actually happened */ }
      // Best-effort cleanup of the scratch call's own harmless session-file
      // byproduct -- a direct unlink of a file THIS SCRIPT just created via
      // the scratch id, not a read/write of caveman's own pre-existing data
      // and not a reimplementation of its writer.
      try {
        fs.unlinkSync(path.join(sessionsDirPath, scratchSid + '.mode'));
      } catch (e) { /* best-effort */ }
    }
  }

  let decodedActual;
  try {
    decodedActual = cfg.resolveActiveMode(claudeDir, sessionId);
  } catch (e) {
    decodedActual = undefined;
  }
  const canonical = canonicalOf(restoreMode);
  const expectedDecoded = decodedOf(canonical);
  const readbackOk = (decodedActual === expectedDecoded);

  const mirrorAfterFixup = mirrorState();
  const mirrorRestoredOk = mirrorSnapshot.exists
    ? (mirrorAfterFixup.exists && mirrorAfterFixup.contents === mirrorSnapshot.contents)
    : !mirrorAfterFixup.exists;

  out({
    status: (readbackOk && mirrorRestoredOk) ? 'restored' : 'restore-readback-mismatch',
    candidates: candidates,
    resolved_via: resolvedVia,
    restored_mode: safeEnum(canonical),
    readback_ok: readbackOk ? 'true' : 'false',
    mirror_restore_ok: mirrorRestoredOk ? 'true' : 'false'
  });
  process.exit(0);
}

out({ status: 'noop-unknown-action', candidates: candidates, resolved_via: resolvedVia });
process.exit(0);
RC_CAVEMAN_APPLY_JS
}

# Run the embedded node script once; prints its single JSON line to stdout.
# $1=claude_dir $2=state_file $3=session_id $4=mode(may be "") $5=manual_typed(0/1) $6=action
_run_node() {
  local scratch
  scratch="$(mktemp -d "${TMPDIR:-/tmp}/rc-caveman-apply.XXXXXX")" || {
    _print_json 'status=snapshot-failed-aborted' 'candidates=0' 'resolved_via=none' 'error=scratch-dir-failed'
    return 0
  }
  # shellcheck disable=SC2064
  trap "rm -rf '$scratch'" RETURN
  local js="$scratch/caveman-apply.js"
  _write_node_script "$js"
  node "$js" "$1" "$2" "$3" "$4" "$5" "$6" 2>/dev/null || \
    _print_json 'status=write-failed' 'candidates=0' 'resolved_via=none' 'error=node-invocation-failed'
}

# ---- emit the readback-mismatch audit event --------------------------------

_emit_readback_mismatch() {
  # $1 = session_id (used only to scope the event's session dir via
  # CLAUDE_SESSION_ID, matching _emit-event.sh's own resolution order)
  local hooks_dir
  hooks_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../hooks" 2>/dev/null && pwd || true)"
  [ -n "$hooks_dir" ] || return 0
  [ -f "$hooks_dir/_emit-event.sh" ] || return 0
  # shellcheck source=/dev/null
  . "$hooks_dir/_emit-event.sh" 2>/dev/null || return 0
  command -v _emit_hook_event >/dev/null 2>&1 || return 0
  CLAUDE_SESSION_ID="$1" _emit_hook_event "caveman-apply-mode.sh" "warn" "" "" \
    "caveman-route-readback-mismatch" 0 || true
}

# ---- top-level commands -----------------------------------------------------

cmd_apply() {
  local session_id="$1" mode="$2" manual_typed="0"
  if [ "${3:-}" = "--typed-caveman-command" ]; then manual_typed="1"; fi

  if ! printf '%s' "$session_id" | grep -Eq "$SESSION_ID_RE"; then
    _print_json 'status=noop-invalid-session-id' 'candidates=0' 'resolved_via=none'
    return 0
  fi

  if ! command -v node >/dev/null 2>&1; then
    _print_json 'status=noop-no-node' 'candidates=0' 'resolved_via=none'
    return 0
  fi

  local project_dir="${CLAUDE_PROJECT_DIR:-}"
  if [ -z "$project_dir" ]; then
    _print_json 'status=snapshot-failed-aborted' 'candidates=0' 'resolved_via=none' 'error=no-project-dir'
    return 0
  fi

  local claude_dir state_file result_json status
  claude_dir="$(_resolve_claude_dir)"
  state_file="$project_dir/.ravenclaude/runs/$session_id/caveman-route-state.json"

  result_json="$(_run_node "$claude_dir" "$state_file" "$session_id" "$mode" "$manual_typed" "apply")"
  status="$(_json_field "$result_json" status)"

  if [ "$status" = "readback-mismatch" ]; then
    _emit_readback_mismatch "$session_id"
  fi

  printf '%s\n' "$result_json"
}

cmd_restore() {
  local session_id="$1"

  if ! printf '%s' "$session_id" | grep -Eq "$SESSION_ID_RE"; then
    _print_json 'status=noop-invalid-session-id' 'candidates=0' 'resolved_via=none'
    return 0
  fi

  if ! command -v node >/dev/null 2>&1; then
    _print_json 'status=noop-no-node' 'candidates=0' 'resolved_via=none'
    return 0
  fi

  local project_dir="${CLAUDE_PROJECT_DIR:-}"
  if [ -z "$project_dir" ]; then
    _print_json 'status=restore-failed-no-snapshot' 'candidates=0' 'resolved_via=none' 'error=no-project-dir'
    return 0
  fi

  local claude_dir state_file result_json status
  claude_dir="$(_resolve_claude_dir)"
  state_file="$project_dir/.ravenclaude/runs/$session_id/caveman-route-state.json"

  result_json="$(_run_node "$claude_dir" "$state_file" "$session_id" "" "0" "restore")"
  status="$(_json_field "$result_json" status)"

  if [ "$status" = "restore-readback-mismatch" ]; then
    _emit_readback_mismatch "$session_id"
  fi

  printf '%s\n' "$result_json"
}

# =============================================================================
# --self-test
# =============================================================================
# Every fixture below is isolated: a fresh temp dir stands in for
# CLAUDE_CONFIG_DIR and CLAUDE_PROJECT_DIR, so nothing ever touches real host
# state. Each destructive/negative case carries a positive control per this
# repo's own probe-discipline convention (a probe that always reads clean is
# worthless) — see the per-test comments for what each control proves.

_ST_FAIL=0
_ok()   { printf '  OK   %s\n' "$1"; }
_fail() { printf '  FAIL %s\n' "$1"; _ST_FAIL=1; }

_st_good_fixture() {
  # $1 = destination .js path. A faithful, in-memory-file-backed re-
  # implementation of caveman-config.js's documented public surface (the
  # verbatim writeSessionMode body from plan.md, plus the matching
  # readSessionModeRaw/resolveActiveMode/getDefaultMode).
  cat > "$1" <<'RC_GOOD_FIXTURE'
'use strict';
const fs = require('fs');
const path = require('path');
const VALID_MODES = ['off', 'lite', 'full'];
function sessionActivePath(claudeDir, sessionId) {
  if (!/^[A-Za-z0-9_-]{1,128}$/.test(sessionId)) return null;
  return path.join(claudeDir, '.caveman-sessions', sessionId + '.mode');
}
function legacyFlagPath(claudeDir) { return path.join(claudeDir, '.caveman-active'); }
function safeWriteFlag(p, val) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  const tmp = p + '.tmp-' + process.pid;
  fs.writeFileSync(tmp, val, { mode: 0o600 });
  fs.renameSync(tmp, p);
}
function readFlag(p) { try { return fs.readFileSync(p, 'utf8').trim(); } catch (e) { return null; } }
function offToNull(v) { return (!v || v === 'off') ? null : v; }
function writeSessionMode(claudeDir, sessionId, modeOrNull) {
  const canonical = (!modeOrNull || modeOrNull === 'off') ? 'off' : modeOrNull;
  if (!VALID_MODES.includes(canonical)) return;
  const sessionPath = sessionActivePath(claudeDir, sessionId);
  if (sessionPath) safeWriteFlag(sessionPath, canonical);
  const legacy = legacyFlagPath(claudeDir);
  if (canonical === 'off') { try { fs.unlinkSync(legacy); } catch (e) {} }
  else { safeWriteFlag(legacy, canonical); }
}
function readSessionModeRaw(claudeDir, sessionId) {
  const p = sessionActivePath(claudeDir, sessionId);
  if (!p) return null;
  return readFlag(p);
}
function resolveActiveMode(claudeDir, sessionId) {
  const sessionPath = sessionActivePath(claudeDir, sessionId);
  if (sessionPath) {
    const stored = readFlag(sessionPath);
    if (stored !== null) return offToNull(stored);
  }
  return offToNull(readFlag(legacyFlagPath(claudeDir)));
}
function getDefaultMode() { return 'off'; }
module.exports = { writeSessionMode, readSessionModeRaw, resolveActiveMode, getDefaultMode, VALID_MODES };
RC_GOOD_FIXTURE
}

_st_broken_fixture() {
  # $1 = destination .js path. Same public surface EXCEPT writeSessionMode
  # ignores the requested mode and always writes "lite" — used to prove
  # read-back verification actually detects a real contract violation.
  cat > "$1" <<'RC_BROKEN_FIXTURE'
'use strict';
const fs = require('fs');
const path = require('path');
const VALID_MODES = ['off', 'lite', 'full'];
function sessionActivePath(claudeDir, sessionId) {
  if (!/^[A-Za-z0-9_-]{1,128}$/.test(sessionId)) return null;
  return path.join(claudeDir, '.caveman-sessions', sessionId + '.mode');
}
function legacyFlagPath(claudeDir) { return path.join(claudeDir, '.caveman-active'); }
function safeWriteFlag(p, val) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  const tmp = p + '.tmp-' + process.pid;
  fs.writeFileSync(tmp, val, { mode: 0o600 });
  fs.renameSync(tmp, p);
}
function readFlag(p) { try { return fs.readFileSync(p, 'utf8').trim(); } catch (e) { return null; } }
function offToNull(v) { return (!v || v === 'off') ? null : v; }
function writeSessionMode(claudeDir, sessionId, modeOrNull) {
  // BROKEN ON PURPOSE (self-test fixture only): ignores modeOrNull.
  const canonical = 'lite';
  const sessionPath = sessionActivePath(claudeDir, sessionId);
  if (sessionPath) safeWriteFlag(sessionPath, canonical);
  safeWriteFlag(legacyFlagPath(claudeDir), canonical);
}
function readSessionModeRaw(claudeDir, sessionId) {
  const p = sessionActivePath(claudeDir, sessionId);
  if (!p) return null;
  return readFlag(p);
}
function resolveActiveMode(claudeDir, sessionId) {
  const sessionPath = sessionActivePath(claudeDir, sessionId);
  if (sessionPath) {
    const stored = readFlag(sessionPath);
    if (stored !== null) return offToNull(stored);
  }
  return offToNull(readFlag(legacyFlagPath(claudeDir)));
}
module.exports = { writeSessionMode, readSessionModeRaw, resolveActiveMode };
RC_BROKEN_FIXTURE
}

cmd_self_test() {
  # NOTE: st_root is intentionally NOT `local` — this function's own `return`
  # (carrying a possibly-nonzero $_ST_FAIL) triggers `set -e`'s script-exit,
  # which fires the EXIT trap below AFTER this function's local scope is torn
  # down. A `local st_root` would then be unbound by the time the trap reads
  # it. A plain (script-global) variable survives the scope exit.
  local sid script_self
  st_root="$(mktemp -d "${TMPDIR:-/tmp}/rc-caveman-apply-st.XXXXXX")"
  trap 'rm -rf "${st_root:-}"' EXIT
  script_self="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)/$(basename "${BASH_SOURCE[0]:-$0}")"

  # ---- Test 1: resolve-success (cache-path glob) + doubles as the positive
  # control every later "should not have applied" assertion is compared
  # against. ------------------------------------------------------------
  local t1_cfg t1_proj t1_hash_dir out1 status1 readback1
  t1_cfg="$st_root/t1/claude-config"
  t1_proj="$st_root/t1/project"
  t1_hash_dir="$t1_cfg/plugins/cache/caveman/caveman/abc123def456/src/hooks"
  mkdir -p "$t1_hash_dir" "$t1_proj"
  _st_good_fixture "$t1_hash_dir/caveman-config.js"
  sid="t1-session-$$"
  out1="$(CLAUDE_CONFIG_DIR="$t1_cfg" CLAUDE_PROJECT_DIR="$t1_proj" bash "$script_self" "$sid" off 2>/dev/null)"
  status1="$(_json_field "$out1" status)"
  readback1="$(_json_field "$out1" readback_ok)"
  if [ "$status1" = "applied" ] && [ "$readback1" = "true" ]; then
    _ok "resolve-success: cache-path glob resolves, write+readback agree ($out1)"
  else
    _fail "resolve-success: expected status=applied readback_ok=true, got: $out1"
  fi

  # ---- Test 2: resolve-failure (no caveman anywhere). Positive control:
  # test 1 (same harness, same code path) proves resolution CAN succeed, so
  # this failure is a real discrimination, not a probe that always says no. -
  local t2_cfg t2_proj out2 status2
  t2_cfg="$st_root/t2/claude-config"
  t2_proj="$st_root/t2/project"
  mkdir -p "$t2_cfg" "$t2_proj"
  sid="t2-session-$$"
  out2="$(CLAUDE_CONFIG_DIR="$t2_cfg" CLAUDE_PROJECT_DIR="$t2_proj" bash "$script_self" "$sid" off 2>/dev/null)"
  status2="$(_json_field "$out2" status)"
  if [ "$status2" = "noop-no-caveman" ]; then
    _ok "resolve-failure: empty CLAUDE_CONFIG_DIR -> noop-no-caveman (control: test 1 proves resolution can succeed)"
  else
    _fail "resolve-failure: expected status=noop-no-caveman, got: $out2"
  fi

  # ---- Test 3: snapshot-failure-aborts-write. Positive control: reuse the
  # good fixture that DID write in test 1; here the run-dir path is blocked
  # by a FILE where a directory needs to exist, so mkdir -p fails and the
  # write must never happen — verified by reading the fixture's own session
  # file directly and confirming it was never created. -----------------
  local t3_cfg t3_proj t3_hash_dir out3 status3 t3_mode_file
  t3_cfg="$st_root/t3/claude-config"
  t3_proj="$st_root/t3/project"
  t3_hash_dir="$t3_cfg/plugins/cache/caveman/caveman/abc123def456/src/hooks"
  mkdir -p "$t3_hash_dir" "$t3_proj/.ravenclaude/runs"
  _st_good_fixture "$t3_hash_dir/caveman-config.js"
  sid="t3-session-$$"
  # Block the run dir: a FILE at the exact path the state dir needs to be.
  : > "$t3_proj/.ravenclaude/runs/$sid"
  out3="$(CLAUDE_CONFIG_DIR="$t3_cfg" CLAUDE_PROJECT_DIR="$t3_proj" bash "$script_self" "$sid" off 2>/dev/null)"
  status3="$(_json_field "$out3" status)"
  t3_mode_file="$t3_cfg/.caveman-sessions/$sid.mode"
  if [ "$status3" = "snapshot-failed-aborted" ] && [ ! -e "$t3_mode_file" ]; then
    _ok "snapshot-failure-aborts-write: blocked run dir -> aborted, no write occurred (control: test 1 shows the fixture DOES write normally)"
  else
    _fail "snapshot-failure-aborts-write: expected status=snapshot-failed-aborted and no mode file, got status=$status3 mode-file-exists=$([ -e "$t3_mode_file" ] && echo yes || echo no)"
  fi

  # ---- Test 4: readback-mismatch, with a positive control that the SAME
  # request against the GOOD fixture emits no such warn event. -----------
  local t4_cfg t4_proj t4_hash_dir sid4 out4 status4 events4
  t4_cfg="$st_root/t4/claude-config"
  t4_proj="$st_root/t4/project"
  t4_hash_dir="$t4_cfg/plugins/cache/caveman/caveman/abc123def456/src/hooks"
  mkdir -p "$t4_hash_dir" "$t4_proj"
  _st_broken_fixture "$t4_hash_dir/caveman-config.js"
  sid4="t4-session-$$"
  out4="$(CLAUDE_CONFIG_DIR="$t4_cfg" CLAUDE_PROJECT_DIR="$t4_proj" CLAUDE_SESSION_ID="$sid4" bash "$script_self" "$sid4" off 2>/dev/null)"
  status4="$(_json_field "$out4" status)"
  events4=""
  if [ -f "$t4_proj/.ravenclaude/runs/$sid4/hook-events.jsonl" ]; then
    events4="$(grep -c "caveman-route-readback-mismatch" "$t4_proj/.ravenclaude/runs/$sid4/hook-events.jsonl" 2>/dev/null || echo 0)"
  fi
  if [ "$status4" = "readback-mismatch" ] && [ "${events4:-0}" -ge 1 ]; then
    _ok "readback-mismatch: broken fixture detected, warn event emitted (control below shows the good fixture emits none for the same request)"
  else
    _fail "readback-mismatch: expected status=readback-mismatch and >=1 warn event, got status=$status4 events=$events4"
  fi
  # Positive control leg: same request, good fixture, same session-shaped
  # project dir but a fresh session id -> must NOT emit the warn event.
  local t4b_cfg t4b_proj t4b_hash_dir sid4b out4b events4b
  t4b_cfg="$st_root/t4b/claude-config"
  t4b_proj="$st_root/t4b/project"
  t4b_hash_dir="$t4b_cfg/plugins/cache/caveman/caveman/abc123def456/src/hooks"
  mkdir -p "$t4b_hash_dir" "$t4b_proj"
  _st_good_fixture "$t4b_hash_dir/caveman-config.js"
  sid4b="t4b-session-$$"
  out4b="$(CLAUDE_CONFIG_DIR="$t4b_cfg" CLAUDE_PROJECT_DIR="$t4b_proj" CLAUDE_SESSION_ID="$sid4b" bash "$script_self" "$sid4b" off 2>/dev/null)"
  events4b="0"
  if [ -f "$t4b_proj/.ravenclaude/runs/$sid4b/hook-events.jsonl" ]; then
    events4b="$(grep -c "caveman-route-readback-mismatch" "$t4b_proj/.ravenclaude/runs/$sid4b/hook-events.jsonl" 2>/dev/null || echo 0)"
  fi
  if [ "${events4b:-0}" -eq 0 ]; then
    _ok "readback-mismatch control: good fixture, same-shaped request -> zero warn events (proves the emit is conditional, not unconditional)"
  else
    _fail "readback-mismatch control: expected zero warn events from the good fixture, got $events4b (out=$out4b)"
  fi

  # ---- Test 5: restore, full round trip with an intermediate-state check
  # that proves the write really took effect before restoring. Entry is left
  # ABSENT (not seeded) — a non-off entry would legitimately trip the
  # manual-override latch (test 8 proves that path), which would make this
  # test about the latch instead of about --restore. So: absent entry ->
  # apply('lite') proceeds normally -> mid should be 'lite' -> --restore ->
  # final should be 'off' (this also directly exercises the header's
  # documented HONEST LIMIT: restoring a null entry writes literal 'off'). --
  local t5_cfg t5_proj t5_hash_dir sid5 out5a mid5 out5b final5
  t5_cfg="$st_root/t5/claude-config"
  t5_proj="$st_root/t5/project"
  t5_hash_dir="$t5_cfg/plugins/cache/caveman/caveman/abc123def456/src/hooks"
  mkdir -p "$t5_hash_dir" "$t5_proj"
  _st_good_fixture "$t5_hash_dir/caveman-config.js"
  sid5="t5-session-$$"
  out5a="$(CLAUDE_CONFIG_DIR="$t5_cfg" CLAUDE_PROJECT_DIR="$t5_proj" bash "$script_self" "$sid5" lite 2>/dev/null)"
  mid5="$(cat "$t5_cfg/.caveman-sessions/$sid5.mode" 2>/dev/null || echo '')"
  out5b="$(CLAUDE_CONFIG_DIR="$t5_cfg" CLAUDE_PROJECT_DIR="$t5_proj" bash "$script_self" --restore "$sid5" 2>/dev/null)"
  final5="$(cat "$t5_cfg/.caveman-sessions/$sid5.mode" 2>/dev/null || echo '')"
  if [ "$mid5" = "lite" ] && [ "$final5" = "off" ]; then
    _ok "restore: absent entry -> apply(lite) intermediate=lite -> restore -> off (round trip proven, both directions observed)"
  else
    _fail "restore: expected intermediate=lite final=off, got intermediate='$mid5' final='$final5' (apply=$out5a restore=$out5b)"
  fi

  # ---- Test 6 (bonus): node-absent. Positive control: test 1 (normal PATH)
  # already proves the success path. ---------------------------------------
  local out6 status6
  out6="$(CLAUDE_CONFIG_DIR="$t1_cfg" CLAUDE_PROJECT_DIR="$t1_proj" PATH="/usr/bin:/bin" bash "$script_self" "t6-session-$$" off 2>/dev/null)"
  status6="$(_json_field "$out6" status)"
  if [ "$status6" = "noop-no-node" ]; then
    _ok "node-absent: PATH without node -> noop-no-node, exit 0 (control: test 1 succeeds with node on PATH)"
  else
    _fail "node-absent: expected status=noop-no-node, got: $out6"
  fi

  # ---- Test 7 (bonus): standalone install path resolution (step 2 of the
  # version-drift order), with no cache-path candidate present at all. -----
  local t7_cfg t7_proj out7 status7 via7
  t7_cfg="$st_root/t7/claude-config"
  t7_proj="$st_root/t7/project"
  mkdir -p "$t7_cfg/hooks" "$t7_proj"
  _st_good_fixture "$t7_cfg/hooks/caveman-config.js"
  out7="$(CLAUDE_CONFIG_DIR="$t7_cfg" CLAUDE_PROJECT_DIR="$t7_proj" bash "$script_self" "t7-session-$$" off 2>/dev/null)"
  status7="$(_json_field "$out7" status)"
  via7="$(_json_field "$out7" resolved_via)"
  if [ "$status7" = "applied" ] && [ "$via7" = "standalone" ]; then
    _ok "standalone-install resolution: no cache candidate, standalone path resolves -> applied (control: test 2 shows truly nothing found returns noop-no-caveman)"
  else
    _fail "standalone-install resolution: expected status=applied resolved_via=standalone, got: $out7"
  fi

  # ---- Test 8 (bonus): manual-override latch. Entry mode is non-off before
  # the first apply call -> held, no write. Positive control: test 1 (fresh
  # session, entry absent) proceeds to write normally under the identical
  # harness. ------------------------------------------------------------
  local t8_cfg t8_proj t8_hash_dir sid8 out8 status8 t8_mode_after
  t8_cfg="$st_root/t8/claude-config"
  t8_proj="$st_root/t8/project"
  t8_hash_dir="$t8_cfg/plugins/cache/caveman/caveman/abc123def456/src/hooks"
  mkdir -p "$t8_hash_dir" "$t8_proj" "$t8_cfg/.caveman-sessions"
  _st_good_fixture "$t8_hash_dir/caveman-config.js"
  sid8="t8-session-$$"
  printf 'full' > "$t8_cfg/.caveman-sessions/$sid8.mode"
  out8="$(CLAUDE_CONFIG_DIR="$t8_cfg" CLAUDE_PROJECT_DIR="$t8_proj" bash "$script_self" "$sid8" off 2>/dev/null)"
  status8="$(_json_field "$out8" status)"
  t8_mode_after="$(cat "$t8_cfg/.caveman-sessions/$sid8.mode" 2>/dev/null || echo '')"
  if [ "$status8" = "held-manual-override" ] && [ "$t8_mode_after" = "full" ]; then
    _ok "manual-override latch: non-off entry mode -> held, mode file untouched (control: test 1's absent-entry session writes normally)"
  else
    _fail "manual-override latch: expected status=held-manual-override and mode file still 'full', got status=$status8 mode-after='$t8_mode_after' ($out8)"
  fi

  # ---- Test 9 (bonus): --restore's mirror fixup. Constructs the exact
  # divergent scenario the fix closes: the snapshot captured the legacy
  # mirror holding 'full' (as if some OTHER session had it active at this
  # session's first-apply moment), this session's own restoreMode is null
  # (absent entry -> canonical 'off'), and the CURRENT on-disk mirror is
  # already absent (as a live apply('off') would have left it -- see the
  # header's "THE MIRROR HALF" note). Restoring the session mode ALONE would
  # naturally leave the mirror absent too (canonical 'off' unlinks it) --
  # which does NOT match the captured 'full'. Positive control built in:
  # session9 and mirror9 are asserted independently, so a fixup that
  # corrupted the just-restored session file to fix the mirror (the exact
  # bug shape the header warns about -- reusing the real session id for the
  # second call) would be caught by session9 != 'off', not just by mirror9. -
  local t9_cfg t9_proj t9_hash_dir sid9 out9 status9 mirror9 session9 scratch_residue9
  t9_cfg="$st_root/t9/claude-config"
  t9_proj="$st_root/t9/project"
  t9_hash_dir="$t9_cfg/plugins/cache/caveman/caveman/abc123def456/src/hooks"
  mkdir -p "$t9_hash_dir" "$t9_proj/.ravenclaude/runs" "$t9_cfg/.caveman-sessions"
  _st_good_fixture "$t9_hash_dir/caveman-config.js"
  sid9="t9-session-$$"
  mkdir -p "$t9_proj/.ravenclaude/runs/$sid9"
  printf 'off' > "$t9_cfg/.caveman-sessions/$sid9.mode"
  cat > "$t9_proj/.ravenclaude/runs/$sid9/caveman-route-state.json" <<EOF
{
  "user_mode_at_entry": null,
  "legacy_mirror_at_entry": {"exists": true, "contents": "full"},
  "manual_override": false,
  "session_id": "$sid9",
  "snapshotted_at": "2020-01-01T00:00:00.000Z"
}
EOF
  out9="$(CLAUDE_CONFIG_DIR="$t9_cfg" CLAUDE_PROJECT_DIR="$t9_proj" bash "$script_self" --restore "$sid9" 2>/dev/null)"
  status9="$(_json_field "$out9" status)"
  mirror9="$(cat "$t9_cfg/.caveman-active" 2>/dev/null || echo '<absent>')"
  session9="$(cat "$t9_cfg/.caveman-sessions/$sid9.mode" 2>/dev/null || echo '<absent>')"
  scratch_residue9="$(find "$t9_cfg/.caveman-sessions" -maxdepth 1 -name '*.mode' ! -name "$sid9.mode" 2>/dev/null | wc -l | tr -d ' ')"
  if [ "$status9" = "restored" ] && [ "$mirror9" = "full" ] && [ "$session9" = "off" ] && [ "$scratch_residue9" = "0" ]; then
    _ok "restore mirror fixup: snapshot mirror ('full') diverged from what restoring the session ('off') alone implies -- mirror restored to 'full' via a scratch-id writeSessionMode call, the real session file stayed correctly 'off', zero scratch residue left behind ($out9)"
  else
    _fail "restore mirror fixup: expected status=restored mirror=full session=off scratch_residue=0, got status=$status9 mirror=$mirror9 session=$session9 scratch_residue=$scratch_residue9 ($out9)"
  fi

  echo
  if [ "$_ST_FAIL" -eq 0 ]; then
    echo "caveman-apply-mode.sh self-test: PASS (9/9)"
  else
    echo "caveman-apply-mode.sh self-test: FAIL"
  fi
  return "$_ST_FAIL"
}

# ---- dispatch ----------------------------------------------------------------

main() {
  local sub="${1:-}"
  case "$sub" in
    --self-test|self-test)
      cmd_self_test
      ;;
    --restore)
      shift || true
      cmd_restore "${1:-}"
      ;;
    "")
      echo "caveman-apply-mode.sh: missing arguments (session_id + mode, --restore <session_id>, or --self-test)" >&2
      return 0
      ;;
    *)
      cmd_apply "$1" "${2:-off}" "${3:-}"
      ;;
  esac
}

main "$@"
