# Whole-repo review — 2026-09-13

**Run:** scheduled autonomous routine (comprehensive review → categorize → tie-break → implement).
**Reviewer:** Claude Code (Opus), 4 parallel expert-review sub-agents (Sonnet) for Panel 1.
**Branch:** `claude/awesome-wright-99v8m2` · **PR:** (this branch)
**Local run dir:** `.ravenclaude/runs/repo-review-20260913/` (gitignored).

---

## TL;DR

The repo is **CI-green and unusually well-hardened**. A four-panel sweep of every executable
surface (125 Python scripts, 195 shell scripts/hooks, 21 Node scripts, 17 GitHub workflows) found
**one clean auto-fixable defect** (shipped in this PR) and **three genuine security-hardening
findings that a guard structurally prevents an automated agent from applying** — they are written up
below as ready-to-apply patches for a human to land. No architectural rot, no broken gates, no
supply-chain gaps were found.

| ID | Sev | File | Status |
|----|-----|------|--------|
| F1 | P1 | `plugins/ravenclaude-core/hooks/log-probe.sh` | **Patch below — blocked from auto-apply** (tribunal substrate guard) |
| F2 | P1 | `plugins/ravenclaude-core/hooks/triage-outcome.sh` | **Patch below — blocked from auto-apply** (tribunal substrate guard) |
| F3 | P2 | `plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh` | **Patch below — blocked from auto-apply** (tribunal substrate guard) |
| F4 | P3 | `scripts/check-vscode-extension-config-defaults.py` | ✅ **Fixed in this PR** |

---

## Method (panels & model assignment)

- **Grounded baseline first (observations, not inferences):** `bash -n` on 195 scripts → exit 0;
  `json.tool` on 186 manifests → all parse; `ruff check .` → clean; `scripts/ci-preflight.py` →
  **19 PASS / 0 FAIL / 0 UNAVAILABLE** (floors + all freshness/ratchet/inventory hotspots + toctou).
  So there was **no** lint/format/freshness/manifest fruit — every finding here is a genuine logic or
  security defect CI cannot catch.
- **Panel 1 (expert review, Sonnet ×4, parallel):** py-scripts A / py-scripts B / shell / (mjs +
  workflows). Instructed to report only high-confidence defects with a concrete failure scenario and a
  minimal fix; "no findings" was an accepted answer.
- **Panel 2 (analysis, Opus — this session):** every Panel-1 finding re-verified against source,
  including a repo-wide sweep for the same defect class (`session_id` → path) to confirm the finding
  set was complete and not over/under-scoped.
- **Panel 3 (tie-break, Opus):** the only ambiguous call was P1-vs-P2 for F1/F2 — resolved to **P1**
  to match the repo's own classification of the identical primitive in `guard-premise.sh`, with the
  reachability caveat stated honestly below.

Two of the four Panel-1 surfaces (py-scripts A, mjs + workflows) returned **zero** findings with
thorough justification (SHA-pinned actions, no `pull_request_target`, no `${{ github.event.* }}`→`run:`
injection, no `paths:` on required checks; every behavioral gate ships a must-fail mutant test).

---

## Findings needing a human to land (F1–F3)

### Root cause (shared by F1, F2, F3)

`session_id` rides the tool payload and is **attacker-influenceable** — the repo's own threat model
asserts this in `guard-premise.sh` ("session_id is attacker-influenceable (it rides the … payload)")
and `guard-web-access.sh` (`_ee_sanitize_session`, citing PR #363), both of which already sanitize it
before using it to build a path. A `../../../../tmp/pwn`-shaped id resolves `os.makedirs()` / file
writes **outside** `.ravenclaude/runs/` — a CWE-22 path-traversal write primitive. The sanitizer
(`strip to [A-Za-z0-9._-]`, cap 128, reject `.`/`..`) was applied to some hooks but **not** to the
three below, even though F2's own header comment says to keep it "IN SYNC WITH ITS TWIN IN
log-probe.sh AND guard-premise.sh."

**Reachability caveat (honest):** `session_id` is normally assigned by the host CLI. I could not
prove from this codebase alone that an attacker controls it end-to-end; the P1 rating follows the
repo's own stated threat model and the fact that it patched the identical primitive twice, plus that
F1/F2 fire on **every** relevant tool call. If the maintainer's model is that `session_id` is fully
trusted, F1/F2 drop to P3 hardening — but the fix is cheap and defense-in-depth either way.

### Why these three could not be auto-applied

All three live under `plugins/ravenclaude-core/hooks/`, which is the command-review tribunal's
**substrate**. `thing-decision.py`'s `screen_substrate_path` (§B.9.5) denies *any* Write/Edit whose
target is a substrate file **pre-LLM, category-independently, and non-overridably** (matched by
lexical path, realpath, and inode). This is correct, intended behavior: the tribunal cannot
distinguish a hardening edit from a tampering edit, so it refuses all automated substrate mutation and
directs a human to apply it (or toggle the Thing via the comfort-posture dashboard). Bypassing that
guard would itself violate house rule #5, so these are handed off as patches rather than forced.

The edits are mechanical (no design decision) — a maintainer can apply them directly, or re-run this
work in a session where the substrate guard is configured to allow it.

### F1 — `plugins/ravenclaude-core/hooks/log-probe.sh` (P1)

`sid = d.get("session_id", "nosession")` (≈line 72) is used raw at
`sess = os.path.join(proj, ".ravenclaude", "runs", "premise", sid)` (≈line 260), then
`os.makedirs(run, exist_ok=True)` + the `probe-ledger.jsonl` write. This PostToolUse hook fires on
every Bash/WebFetch. `re` is already imported. Add the canonical sanitizer right after `sid` is set,
mirroring `guard-premise.sh`:

```python
sid  = d.get("session_id", "nosession")

# ⛔ session_id is attacker-influenceable; unsanitized it resolves the runs/premise/<sid>/
# paths OUTSIDE the run tree (CWE-22). guard-premise.sh (the gate half) already hardens this
# field with rc_sanitize_session(); the recorder half never mirrored it.
def rc_sanitize_session(s):
    s = re.sub(r"[^A-Za-z0-9._-]", "", str(s))[:128]
    if s in ("", ".", ".."):
        return "nosession"
    return s

sid = rc_sanitize_session(sid)
```

### F2 — `plugins/ravenclaude-core/hooks/triage-outcome.sh` (P1)

Identical defect: `sid = str(d.get("session_id", "nosession") or "nosession")` (≈line 455) → raw in
`sess = os.path.join(proj, ".ravenclaude", "runs", "cause-triage", sid)` (≈line 456) → `os.makedirs`
+ `open.jsonl` write. This file's header already says to keep this block in sync with its twins. Same
fix — insert after the `sid = …` line (its Python block imports `re`):

```python
sid = str(d.get("session_id", "nosession") or "nosession")

def rc_sanitize_session(s):
    s = re.sub(r"[^A-Za-z0-9._-]", "", str(s))[:128]
    if s in ("", ".", ".."):
        return "nosession"
    return s

sid = rc_sanitize_session(sid)
```

### F3 — `plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh` (P2)

`sid="$(… jq -r '.sessionId // .session_id // empty' …)"` (≈line 80) is used raw in the diagnostic
path `_diag_dir="${CLAUDE_PROJECT_DIR:-.}/.ravenclaude/runs/${sid:-unknown}"` (≈line 207), which then
`mkdir -p`s and appends `adapter-trace.jsonl`. Lower severity because it only fires under the opt-in
`RAVENCLAUDE_DIAGNOSE=1`. (The `export CLAUDE_SESSION_ID="$sid"` at ≈line 82 is **safe** downstream —
`_emit-event.sh` re-sanitizes via `_ee_sanitize_session` before building a path — but sanitizing at
the source is cleaner and closes the `_diag_dir` write too.) Sanitize `sid` right where it is read,
mirroring `_ee_sanitize_session`:

```sh
sid="$(printf '%s' "$payload" | jq -r '.sessionId // .session_id // empty' 2>/dev/null)"
# Harden the attacker-influenceable session id before it lands in any path (CWE-22),
# matching _emit-event.sh's _ee_sanitize_session (PR #363).
sid="$(printf '%s' "$sid" | tr -dc 'A-Za-z0-9._-' | cut -c1-128)"
case "$sid" in .|..) sid="" ;; esac
```

**Suggested follow-up (optional):** factor `rc_sanitize_session` into a single sourced helper so the
"keep in sync" comment is enforced by construction rather than by prose, and add a must-fail fixture
(a `../`-shaped session_id) to the hooks self-test so a future twin can't regress silently.

---

## Fixed in this PR

### F4 — `scripts/check-vscode-extension-config-defaults.py` (P3) ✅

The per-key validation loop shared one `ok` flag: once any key failed, `if ok:` suppressed the
`OK: '<key>' …` success line for **every** later valid key, so the report read as if those keys were
never checked. (The aggregate pass/fail verdict was always correct, so the gate never mis-fired — this
is a diagnostic-output defect. It is currently inert because the real manifest has a single key, so
there was no positive control for the multi-key case.) Fixed with a per-key `key_ok` local that
carries the current key's verdict for its success line and is folded into the aggregate `ok` at the
end of the loop. Self-test: **6 pass, 0 fail**; `ruff check` clean.

_Note:_ the repo's `format-on-write.sh` PostToolUse hook ran `ruff format` on the touched file
(incremental format-on-touch adoption — the repo is otherwise lint-only per `ruff.toml`), so the diff
includes mechanical line-wrapping of pre-existing long lines alongside the logic change.

---

## Questions for the maintainer

1. **Landing F1–F3:** apply the three patches directly, or would you prefer they ride a session with
   the tribunal substrate guard relaxed? (They're mechanical; no design call.)
2. **F1/F2 severity:** is `session_id` trusted end-to-end in your model, or attacker-influenceable as
   `guard-premise.sh` asserts? That's the P1-vs-P3 hinge (see reachability caveat).
3. **Optional follow-up:** want the shared-`rc_sanitize_session`-helper + `../`-shaped must-fail
   fixture, to make the "keep in sync" invariant enforced rather than commented?
