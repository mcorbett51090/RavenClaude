# Repo review — 2026-10-14 (autonomous scheduled routine)

A whole-repo review run as three parallel expert panels (`sonnet`) over the highest-risk executable
slice, on top of the repo's own CI gate tooling (the objective panel). Findings were validated and
tie-broken; the confirmed, mechanical, low-risk ones were fixed in the accompanying PR, and the rest
are written up here for your decision.

**Why this split:** this is an unattended run against security/governance-critical, heavily-gated
code. I auto-fixed only what I could confirm and verify against a self-test/regression. The
security-adapter envelope rewrites, the sanitizer DoS/fail-open, and the routine-reserve
metering/budget changes are real but interacting, multi-file, and partly judgment calls — shipping
them blind in an unattended run is the wrong trade. Each is below with an exact patch so adopting it
is a quick review, not a re-investigation.

## Objective-layer health (run first)

All green except the prettier drift (fixed). 19/19 ci-preflight hotspots, ruff clean, 488 py compile,
41 js/mjs parse, 186 JSON valid, 204 shell OK, md-links / frontmatter / gate-registration /
model-tier-fit / nested-dispatch all pass.

## Implemented in the PR (grouped by priority)

| Pri | Finding |
|---|---|
| **P0** | 1a-1: all four host-hook projectors emitted shell-syntax-invalid commands (silent cross-host guardrail disarm / outage) + the hollow Gate 158/160/165 teeth that let it ship |
| P1 | 1c-7: a commented `# context_handoff:` block shadowed the real one → handoff nudge silently off |
| P1 | 1b-1: the project-root walk-up loop hung on a relative cwd (`.`) in runaway-brake, dod-gate, guard-probe-validity **and thing-orchestrator (the tribunal)** |
| P2 | 1c-6: one non-numeric `t` crashed `compute`, leaving hooks on a stale reserve.json |

Each carries a regression test or an existing self-test re-run; the full `audit-gates.sh` suite was run
green before the PR.

**Follow-through (not findings):** (a) O-1 "prettier drift" was a **false positive** — my local
prettier 3.8.1 disagreed with CI's pinned 3.9.4; the files were already 3.9.4-clean, so my reformat
was a regression and is **reverted**. (b) The fixes above edit files covered by 4 concept-inventory
entries, so their covers-digest drifted; re-verified each claim is orthogonal to the edit, re-stamped,
and regenerated `concepts.json` / `dashboard.html` / `index.html` / `docs/concepts.md`.

## Needs your decision / review (NOT auto-fixed)

Ordering note: **1a-1 (fixed) had to land first** — until the projected commands were valid shell, the
hooks did not run at all on Copilot/Cursor/Gemini, so the adapter-envelope findings below were moot.
They are now live and worth fixing.

### Security-adapter envelope (Copilot/Gemini/Cursor) — all reproduced by the panel

- **1a-2 (P1, security) — `copilot-hook-adapter.sh:161`.** Copilot's file-tool argument names
  (`path`/`file_text`/`old_str`/`new_str`) are passed through untranslated; the tribunal + self-tamper
  guard read `file_path`/`content`/`old_string`/`new_string`. So on Copilot a `view` of `~/.ssh/id_rsa`
  and a `create`/`edit` onto the tribunal's own substrate get NO decision. Fix: in the jq program, for
  non-Bash tools alias `file_path=($ti.file_path//$ti.path)`, `content=($ti.content//$ti.file_text)`,
  `old_string=(…//$ti.old_str)`, `new_string=(…//$ti.new_str)`. **Land together with 1a-9** — once the
  guard sees `file_path`, `guard-premise.sh` would start denying new source modules as "blind" on
  Copilot unless posttool stdin is also forwarded.
- **1a-3 (P1, security) — `gemini-hook-adapter.sh:125`.** `_normalise` passes the whole payload as an
  argv element; a payload ≥128 KiB (Linux `MAX_ARG_STRLEN`) makes the exec fail and the hook sees the
  raw, un-normalised payload → every Bash/file guard falls through `*) exit 0`. A large `write_file` or
  a padded command disarms every Gemini guard. Fix: read the payload from stdin inside python; in
  pretool mode treat a normalisation failure as fail-closed (exit 2).
- **1a-4 (P1, parity) — `copilot-hook-adapter.sh:159`.** Args are read only from `.toolArgs`, and the
  `catch {command: .}` binds the jq error message, not the input. A snake_case `tool_input` (what
  PascalCase events send, per the repo's own docs) → empty command → guard allows. Fix: coalesce
  `.toolArgs // .tool_input`, capture the original before the try, fail-closed on empty for
  security-gate modes. Add a snake_case fixture to Gate 167.
- **1a-5 (P1, security, DESIGN) — `copilot-hook-adapter.sh:229`.** A tribunal EDIT verdict →
  `allow` + `updatedInput`; if Copilot ignores the key (copilot-cli#2013), the **original unsafe
  command runs**. **Recommendation:** translate EDIT → `deny` with the revised command in the reason
  (mirroring the Cursor adapter) until the rewrite channel is verified live. **Your call.**
- **1a-6..1a-9 (P2):** Gemini MCP name rewrite loses the server/tool boundary (every allow-listed MCP
  call pre-LLM-denied); Gemini JSON-deny reason dropped (blind retries); Copilot `timeoutSec: 90` <
  the 105 s Copilot-aware panel deadline (reasonless timeout-deny); Copilot `sessionstart`/`posttool`
  forward no stdin (several PostToolUse hooks blind; premise-gate beacon never written).
- **1a-10..1a-12 (P3):** Codex SessionStart derivation ignores `_SKIP` (wires routine-reserve + caveman
  on Codex); Cursor projects non-file PostToolUse hooks onto `afterFileEdit` (inert but read as
  coverage); Cursor `dod-gate` wired on `stop` where output is discarded.
- **Gap — `generate-codex-hooks.py` has no `--check` gate** in audit-gates.sh (the other three do), so
  the command-syntax floor I added to it is present but unexercised. Recommend a gate mirroring 158/160/165.

### Sanitizers / spectate

- **1b-3 (P1, DoS) — `scripts/sanitize-webfetch-body.py:113` + the wrappers.** The injection-pattern
  regex uses `^\s*` (where `\s` spans newlines), so a run of blank lines is O(n²): measured 40 KB =
  45 s, ~150 KB > 600 s. An untrusted MCP body stalls the session every call. Fix: make the pattern
  line-local (`^[ \t]*`) and wrap the sanitizer in `_rc_timeout` (fail-closed on timeout).
- **1b-2 (P2, security, DESIGN) — `sanitize-mcp-output.sh:24` / `sanitize-webfetch-output.sh:24`.**
  `|| exit 0` fails OPEN on any crash (e.g. a missing transitive dep) → an unscanned body reaches the
  model. **Your call:** should a sanitizer crash block or pass through? Recommend block + add the real
  dependency to the preflight check.
- **1b-4 (P2) — `spectate_store.py:1342`.** `list_sessions` reduces every session before paging and
  wipes the reduce cache wholesale at 256 → ~27 s per 5 s poll at 300 sessions. Fix: stat-sort + page
  first, reduce only the page, LRU eviction.
- **1b-5 (P2) — `spectate-emit.sh:44`.** Payload via env var → E2BIG drops the event silently at
  ≥128 KiB. Fix: pipe the payload on stdin.
- **1b-6 / 1b-7 / 1b-8 / 1b-9 (P3):** runaway-brake read-only allowlist too loose
  (`python3 -m json.tool IN OUT` writes, `node --check -r MOD` executes → thrash-counter evasion);
  SSE replay lacks the tail-window clamp; `apply_steer` uses `ID_RE.match` (accepts a trailing newline)
  and persists state before validating; `watch-spectate.sh` echoes store fields with no charset/enum
  check (defence-in-depth; no in-repo writer produces bad values today).

### routine-reserve / context engines

- **1c-1 (P1) — `routine-reserve.py:428`.** `meter_plan` keys "settled" on the session, not the run's
  `fired_at`, so later runs of a **persistent-session** Routine are never metered.
- **1c-2 (P1) — `routine-reserve.py:1077/1056/1201`.** `hook_warn` / `hook_guard` / the statusline read
  a `reserve.json` only SessionStart refreshes, so in a long run-non-stop session the reserve state is
  frozen at session start. Fix: recompute from `rate-limits.json` at hook time, or treat a stale
  reserve.json as stale.
- **1c-3 / 1c-4 (P2):** the manual-budget estimate anchors its window at `now` when no reset is known
  (always ~0 %); `calibrate` counts spend past the reading's window end, deflating k — **the unsafe
  direction** (shrinks the reserve). Both reproduced.
- **1c-5 (P2):** a deleted Routine stays reserved up to 35 days (assumes `list_triggers` omits deleted —
  unverified against the live API).
- **1c-10 (P2) — `context-handoff.py:923/865`.** `finalize`/`fill` rewrite `handoff.md` in place
  (truncate-then-write), so a failed write destroys the agent-authored brief. Fix: temp-file + fsync +
  `os.replace` (also closes the 0644-then-chmod window).
- **1c-8 (P2, DESIGN) — `context-usage-meter.py:513`.** The Grok-config `context_window` is applied to
  Claude Code sessions (rank-3 precedence, ahead of model-aware resolution). **Your call:** is
  cross-host Grok-config precedence intended? If not, gate it on `source != "claude-code"`.
- **1c-9 (P2, DESIGN) — `context-usage-meter.py:337`.** An unrecognized non-haiku model id gets a 1M
  window (the documented heuristic); an older/pinned snapshot whose real window is 200K would be
  understated ~5×, firing the nudge/conserve triggers late. **Your call:** conservative 200K for
  non-current ids, or keep the 1M optimism?
- **1c-11 / 1c-12 / 1c-13 (P3):** `splitlines()` splits on U+2028/2029 (reads the previous turn's
  usage); the fallback transcript-path encoding differs from the mimir algorithm; cheap-lane /
  orchestrate non-zero exits are all reported as "provider unavailable" (hides the secret-refusal /
  recursion-guard exits).

### D-1 (P2, DESIGN) — committed `.claude/settings.json` drifts from the posture generator

SessionStart `reapply-posture.sh` regenerates `.claude/settings.json` from `comfort-posture.yaml`,
silently **dropping the 6 hand-added Gmail MCP `allow` entries**, adding a spawn-depth default, and
re-serializing (em-dashes). Every session → a dirty tree + a silent permission removal. **Your call:**
move the Gmail allows into `comfort-posture.yaml` (so the generator stops dropping them), or change the
generator. Left uncommitted and excluded from the PR — not an autonomous permissions change to make.
Relevant: `plugins/ravenclaude-core/hooks/reapply-posture.sh`,
`plugins/ravenclaude-core/scripts/apply-comfort-posture.py`.

---
_Autonomous review. The panel reproductions and full per-finding detail are in the session run dir
(`.ravenclaude/runs/repo-review-2026-10-14/`, gitignored)._
