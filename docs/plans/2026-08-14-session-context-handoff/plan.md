# Session-context handoff — reconciled plan (G6)

> **Implement-time correction (2026-08-14):** tip was `0.265.0` after rebase onto `origin/main`, so this ships as **`0.266.0`**. Gates **201/202 were already taken**; the new gates are **212** (nudge) and **213** (spawn). Skill-count literals are forbidden by Gate 206 — README table only.


Owner: `ravenclaude-core`. Stay local. Grok-first; other-host spawn adapters out of scope.

## 1. Intent

Ship a **Grok-first, preventive quality reset** inside `ravenclaude-core`. A running Grok session detects (hook-side) when the context window is about to auto-compact, writes a **host-agnostic handoff** into the existing `.ravenclaude/runs/<task-id>/` contract (same `task-id`, via `bin/rc artifacts new`), and starts a **fresh interactive** successor whose first turn is seeded from that document — not compacted mush. Detection is a **Stop hook** that reads the live C26 meter and nags via `hookSpecificOutput.additionalContext`. A **script** derive-fills a skeleton from git / files / the run-dir. The **`/handoff` skill** (or the nudged model) fills the narrative brief the hook cannot see. Spawn is positional `grok "<prompt>"` in a new OS terminal **if the owner flag is on**; otherwise (and always as fallback) the originating session prints the exact copy-paste resume prompt. Compact-anchor stays the post-compaction pointer. No PreCompact persist hook. No 40% lore threshold. Default soft threshold **70**, always below auto-compact ~85%, owner-tunable. Motive is **quality**, not durability.

## 2. Alternatives (rejected)

| # | Alternative | Trade-off | Why rejected |
|---|---|---|---|
| R1 | **Skill-only `/handoff`** (Plan A alone). Model self-diagnoses rot and writes the brief; hook is a mute optional nudge. | Cheapest wiring; brief quality is high when the model is lucid. | Fails the product premise: quality rot is exactly when the model will not self-diagnose. Happy path must not require undegraded judgment. |
| R2 | **Detector-only autonomous brief** (Plan B extreme). Hook/script writes `handoff.md` with no model turn. | Deterministic under rot; works if the model is already mush. | Hook cannot see the plan or the decisions (C35/C36 host-split). Derive-fill is a floor, not a brief. A skeleton-only successor is better than nothing and worse than a filled brief. |
| R3 | **Grok `SessionStart` stdout / `additionalContext` seed** (G0). | Matches Claude Code compact-anchor / SessionStart injection (C9). | Falsified on Grok (C6–C8). `SessionStart` stdout is ignored. Do not conflate hosts. |
| R4 | **PreCompact / auto-compact interceptor**, or `/fork`, or headless `grok -p`. | Fires at a known compact moment; `/fork` is one keystroke; `-p` is scriptable. | PreCompact persist is retracted (C35/C45); `/fork` copies history (C17–C18); `-p` exits after one turn (C3). Opposite of a fresh-window quality reset. |

Dashboard dispatch (C43) is a named non-path, not an alternative to implement.

**Chosen synthesis (A ∪ B, G3b-shaped).** Hook detects via the C26 meter and nags via Stop `additionalContext`. Script writes a *skeleton* from git/files/run-dir. `/handoff` (or the nudged model) fills the brief. Spawn uses positional `grok` in a new OS terminal if `context_handoff.spawn: os-terminal`, else prints the copy-paste prompt. Copy-paste is always printed.

## 3. Reconciled dependency DAG + critical path

G3b already ran (`g3b.md`, `g3b-receipt.json`). Do **not** re-probe C5/C8/C24/C26/C30 as a product blocker. Residual C14 is unused. Residual C40 is one owner-flagged reversible spawn script.

```
G3b (done — design branches locked)
 │
 ├─► P1  Usage meter (updates.jsonl _meta.totalTokens; hook-side GROK_SESSION_ID)
 │
 ├─► P2  Skeleton writer (git / files / run-dir → handoff.md shell)
 │         ∥ P1
 │
 ├─► P3  /handoff skill + command (model fills narrative; same task-id)
 │         ∥ P1, P2
 │
 ├─► P4  Stop-hook nudge (C26 meter → additionalContext; never UPS)
 │         needs P1 + P3 (skill name in the nag string)
 │
 ├─► P5  Spawn (owner-flagged OS terminal) + always-print copy-paste
 │         needs P2 (refuses to invent a brief)
 │
 └─► P6  Wire hooks.json + posture + version + G8 regen + Gates 201/202
           needs P2–P5 on disk
```

- **Parallel:** P1 ∥ P2 ∥ P3 after G3b. P4 ∥ P5 after their deps.
- **Critical path:** P2 + P3 → P6. A usable `/handoff` + on-disk brief + copy-paste seed ships even if the meter is silent and OS-terminal spawn is off.
- **Degradation (not a blocker):** P1/P4 without a resolvable window → hook silent, skill remains the path. P5 without a proven recipe → copy-paste only (scope §4b success).
- **Do not start P6** until P2–P5 exist on disk (G8 counts the new skill + command + hook).

### Names (unified — one of each)

| Kind | Name | Role |
|---|---|---|
| Skill | `session-handoff` | Model-fill + gotchas. Primary *author* of the narrative brief. |
| Command | `/handoff` | Thin wrapper that loads the skill. Optional `task-id`. |
| Hook | `handoff-nudge.sh` | `Stop` only. Fail-open. Reads meter, emits `additionalContext`. Never writes the brief. |
| Engine | `scripts/handoff-nudge.py` | Parse stdin, call meter, emit JSON or silence. |
| Meter | `scripts/context-usage-meter.py` | Live used = last `updates.jsonl` `params._meta.totalTokens`. |
| Writer | `scripts/context-handoff.py` | Derive-fill skeleton + seed text. Invoked by skill and by `rc handoff`. |
| Spawn | `scripts/handoff-spawn.sh` | Positional `grok "…"` + always-print copy-paste. OS-terminal only if flagged. |
| `rc` verb | `rc handoff` | Routes to spawn (run-dir tool stays `rc artifacts`). |
| Config | `context_handoff:` in comfort-posture | `mode`, `threshold_percent`, `spawn`, optional `context_window_tokens`. |
| Artifact | `.ravenclaude/runs/<task-id>/handoff.md` | Same run-dir. Optional `handoff-seed.txt`. |
| State | `.ravenclaude/handoff-nudge-state.json` | Once-per-session throttle (gitignored). |

Do **not** name anything `PreCompact`, `compact-anchor`, or `fork`. Do not register a Grok `SessionStart` seed injector. Do not add a `UserPromptSubmit` detector.

## 4. Phases

### P1 — Usage-signal meter (hook-side, C26 only)

**Goal.** One module answers “current context percent used?” from the **live** meter G3b settled. Detection belongs in a **hook process** (C28), never in a skill that “just checks env” (C30 falsified).

**Files.**
- Create `plugins/ravenclaude-core/scripts/context-usage-meter.py`
- Create `plugins/ravenclaude-core/hooks/tests/test-context-usage-meter.py` (or `.sh` fixture wrapper)

depends_on_claims: [15, 16, 22, 24, 25, 26, 28, 30, 42]

**Pre-build gates.**
- Live used tokens = last `~/.grok/sessions/<enc>/<id>/updates.jsonl` → `params._meta.totalTokens` (C26 settled).
- Session dir resolved from **hook** `GROK_SESSION_ID` (C28) + `GROK_HOME`/`~/.grok` + encoded cwd (`GROK_WORKSPACE_ROOT` / `CLAUDE_PROJECT_DIR`). Never require agent-process `GROK_SESSION_ID` (C30 falsified).
- **Do not poll `signals.json` as a live used-token detector** (C24 falsified). Same-session `signals.json.contextWindowTokens` may be read *only* as a window-size source if the file happens to exist.
- Window resolver, ranked: (1) same-session `signals.json.contextWindowTokens` if present; (2) owner knob `context_handoff.context_window_tokens`; (3) a Grok config path **if found at implement time and cited**. **Never** hardcode `500000` as a product constant (C22 is one finished-session sample, not a contract).
- Missing used-tokens or missing window → JSON status `unknown` (fail-open; no false handoff storm).
- Percent = `used / window * 100`. Threshold compare is a pure function. Default `threshold_percent: 70`. Clamp `1 ≤ n < auto_compact` where `auto_compact` is Grok `[session] auto_compact_threshold_percent` if readable, else **85** (C15). Never default to 85 or above. Never encode 40 / 30 / 300K (C41/C42).

**Acceptance tests.**
- Fixture `updates.jsonl` lines with rising `_meta.totalTokens` → last-line used.
- Fixture `signals.json` with `contextWindowTokens` → window from that field; used still from `updates.jsonl`.
- Absent `signals.json` + no owner window knob → status `unknown`, no percent.
- Threshold comparison unit-tested; clamp of `90` against auto-compact `85` → below 85.
- A mutant that reads `signals.json.contextTokensUsed` as the live used-meter fails.

**Blast radius.** New script only. No hooks registered. No compact-anchor touch.

---

### P2 — Handoff skeleton writer (run-dir contract)

**Goal.** Given a `task-id` (create-or-continue via `bin/rc artifacts new`), write a non-empty handoff *shell* the successor can start from even if the model is already degraded. Derive-fill first; model-fill second.

**Files.**
- Create `plugins/ravenclaude-core/scripts/context-handoff.py` (`write` subcommand)
- Create `plugins/ravenclaude-core/skills/session-handoff/templates/handoff.md`
- Modify `scripts/rc-artifacts.py` `detect_host()`: if `GROK_AGENT` or `GROK_HOOK_EVENT` is set, return `"grok"`. **Do not** key this on `GROK_SESSION_ID` (C30). **Do not** add `handoff.md` to `STANDARD_FILES` — an empty handoff on every `artifacts new` is a lie.

depends_on_claims: [1, 2, 5, 31, 32, 33, 44]

**Pre-build gates.**
- Path = `.ravenclaude/runs/<task-id>/handoff.md` in the **same** dir (C32). `rc artifacts new <id>` continue-in-place (this checkout, `scripts/rc-artifacts.py` L241–249).
- Derive-fill (no model): branch, dirty status, recent commits, last N `events.jsonl` lines if present, paths of `summary.md` / `decisions.md` / `structured-output.json`, timestamp, originating `GROK_SESSION_ID` **only if the caller is a hook** (C28), threshold + measured percent if the meter returned them.
- Model-fill markers (`<!-- MODEL FILL -->`) for: Goal, Done, Remaining, Decisions + WHY, Paths, Next 3 steps, Do-not-redo, Blockers. Skeleton is a form, not a blank page, and not fake content.
- `handoff-seed.txt`: short **pointer** prompt — “read `handoff.md` in this run dir and continue; do not re-derive from compacted history.” If the seed would exceed argv limits, seed is `Read the handoff at <abs-path> and continue.`
- Additive `meta.json` stamp: `last_handoff_at`, `last_handoff_host`, `last_handoff_session_id` (only if known). Do not clobber `created` / `host` / `task`.

**Acceptance tests.**
- `context-handoff.py write --task-id <id>` creates `handoff.md` + `handoff-seed.txt`; exit 0 even in an empty git repo (non-empty shell).
- Idempotent re-write does not create a second run-dir. Second `rc artifacts new <same-id>` prints “already exists — continue in it” and does not clobber a filled `handoff.md`.
- Seed string never includes `-p`, `--single`, `--prompt-file`, `--prompt-json`, `/fork`, or `SessionStart`.
- `detect_host()` returns `grok` when `GROK_AGENT=1`; returns `unknown` when those vars are unset.

**Blast radius.** New script + small `detect_host` branch. No auto-spawn yet.

---

### P3 — `/handoff` skill (model fills what the hook cannot see)

**Goal.** The model (user-invoked or Stop-nudged) fills the narrative sections. This is the portable artifact. Spawn is P5.

**Files.**
- Create `plugins/ravenclaude-core/skills/session-handoff/SKILL.md`
  - Frontmatter: `name: session-handoff`; **quoted** `description:` (will contain `:` / trigger phrases — Gate 12 / `check-frontmatter.py`); `user-invocable: true`; do **not** set `disable-model-invocation`; `allowed-tools` include Bash, Read, Write, Edit. Description must name: `/handoff`, “fresh window”, “context is hot”, “quality reset”, “before auto-compact”, Stop-hook nudge.
  - Body is **gotchas**, not a happy-path essay: same `task-id` (C32); hook cannot write this file’s narrative; seed is positional `grok "…"` (C1/C5); never `grok -p` (C3); never `/fork` (C18); never Grok SessionStart injection (C8); never replace compact-anchor (C34); never a PreCompact persist hook (C35); never a 40% / 30% / 300K quality number (C41/C42); trigger is “before auto-compact (~85%)” as a **compact** threshold (C15), not a rot percent; skill must not read `GROK_SESSION_ID` from the agent env (C30).
- Create `plugins/ravenclaude-core/commands/handoff.md` — thin `/handoff` wrapper. Quoted `description:`. Argument hint: optional `task-id`.

**Skill procedure**
1. Resolve `task-id`: user arg → most-recently-touched `.ravenclaude/runs/<id>/` in this repo → else propose a slug and `bin/rc artifacts new <slug>`. Never invent a parallel id.
2. `bin/rc artifacts new <task-id>` — continue-in-place.
3. Run `context-handoff.py write --task-id <id>` to refresh derive-fill, then **fill** the `<!-- MODEL FILL -->` sections from current knowledge. Update `summary.md` / `decisions.md` only when there is real content; never stamp empty files.
4. Call P5 spawn. On spawn fail (or `spawn: copy-paste-only`), print the exact copy-paste block. Report which path was taken.

depends_on_claims: [1, 3, 5, 8, 15, 18, 30, 31, 32, 33, 34, 35, 41, 42, 44]

C24/C26 are **not** required here — the user or the (later) nudge invokes the skill.

**Pre-build gates.**
- `python3 scripts/check-frontmatter.py` clean on the new SKILL.md + command.
- Layout: `plugins/*/skills/**` and `plugins/*/commands/**` already in `.repo-layout.json`. No new glob.
- Do not write to `docs/`. Do not add a new run-dir layout.

**Acceptance tests.**
- Dry run against a scratch `--base`: `handoff.md` is non-empty and sits next to `meta.json`. No second directory.
- SKILL.md + `commands/handoff.md` parse under `yaml.safe_load`; `description` is a non-empty quoted string.
- Skill body contains `grok -p`, `/fork`, `SessionStart`, and `40%` only inside **negations**. A reviewer grep must not find a positive instruction to use any of them.

**Blast radius.** New skill + command. Consumer-visible only after P6 version bump. G8-counted (P6 owns regen). Do not bump versions here.

---

### P4 — Stop-hook nudge (detect + nag; never UPS)

**Goal.** Make detection **not optional** once the owner enables it. On every eligible `Stop`, meter current usage; if ≥ threshold, emit Grok `Stop` `additionalContext` (C12) telling the model to fire `session-handoff` **now**. The hook does **not** write `handoff.md`. The hook does **not** become a compact hook. The hook does **not** register `UserPromptSubmit` (C14 owner-gated).

**Files.**
- Create `plugins/ravenclaude-core/hooks/handoff-nudge.sh` — thin fail-open wrapper (`trap 'exit 0' EXIT`; no `set -e`; bash 3.2). Mirrors `compact-anchor.sh` shape, **separate file**.
- Create `plugins/ravenclaude-core/scripts/handoff-nudge.py`
- Modify `plugins/ravenclaude-core/hooks/hooks.json` — append to the existing `Stop` array (after `thing-denial-kb-sync.sh`). `timeout: 10`. Comment: advisory nudge; fail-open; not a compact hook; not a brief writer.
- Modify `.claude/settings.json` — marketplace-dev **Stop** mirror with `${CLAUDE_PROJECT_DIR}/plugins/ravenclaude-core/hooks/handoff-nudge.sh` (same reason compact-anchor is mirrored).
- Modify `plugins/ravenclaude-core/templates/comfort-posture-balanced.yaml` — commented block (no `schema_version` bump):

  ```yaml
  # context_handoff:
  #   mode: nag                    # off | nag | block. Absent / off = silent.
  #   threshold_percent: 70        # before auto-compact (~85). Not a quality-rot %.
  #   spawn: copy-paste-only       # copy-paste-only | os-terminal
  #   # context_window_tokens: 500000   # owner-supplied window; do not guess.
  ```

- Create `plugins/ravenclaude-core/hooks/tests/test-gate201-handoff-nudge.sh` + `--must-fail-leak` teeth.

**Hook rules (absorb Plan A’s Stop gating).**
- Gate only `reason == "end_turn"`. Silent on `channel_closed` / `shutdown`.
- If `stopHookActive` is true → silent (do not burn the continuation cap).
- `mode: off` or absent → silent. **Ship default off** (opt-in). First-release `nag` after the owner sets the block. `mode: block` is **opt-in only**, `max_blocks` ceiling like `dod-gate.sh`; v1 happy path is advisory `additionalContext`, never `decision: block` unless the owner asked.
- Once-per-session throttle via `.ravenclaude/handoff-nudge-state.json` (`session_id`, `fired_at`).
- If a non-empty `handoff.md` exists in the most-recent run dir **and** its mtime is newer than this session start → silent.
- `additionalContext` contains derived values only (integer percent, fixed strings, skill name, handoff path). **Never** echo transcript / `lastAssistantMessage` / plan text (Gate 186 invariant).
- Missing meter / missing python3 / missing posture → exit 0, no block.
- **Forbidden:** `PreCompact` / `PostCompact` matcher (C45, C35). Do not edit `compact-anchor.sh` / `compact-anchor.py` / the `SessionStart` `matcher: "compact"` block (C34). No `PostToolUse` poll in v1 (C24 falsified; Stop is enough). No `UserPromptSubmit` hook (C14).

depends_on_claims: [12, 13, 14, 15, 16, 24, 26, 28, 30, 34, 35, 36, 42, 45]

**Pre-build gates.**
- P1 meter exists and implements only the C26 reader for live used.
- P3 skill name is `session-handoff` (the nudge string must match).
- C12 settled — no further probe.

**Acceptance tests.**
- Fixture `updates.jsonl` at 80% of a known window + `reason=end_turn` + `stopHookActive=false` + `mode: nag` → stdout JSON with `additionalContext` containing `session-handoff` and `~80%`.
- Same fixture at 10% → empty stdout, exit 0.
- Missing meter / `unknown` window → empty stdout, exit 0.
- `reason=channel_closed` / `shutdown` / `stopHookActive=true` / `mode: off` / threshold `0` → empty stdout.
- Threshold `90` with auto-compact 85 → clamped below 85.
- Default stdout is `hookSpecificOutput.additionalContext`, never `decision: block` unless `mode: block` is set in the fixture.
- Sentinel `ZZINJECTIONSENTINELZZ` in `lastAssistantMessage` / a fake transcript line is **absent** from stdout. `--must-fail-leak` mutant that echoes it is caught.
- Second fire, same `GROK_SESSION_ID`, state file present → empty stdout.
- `bash -n` on the wrapper; always exit 0 even if python3 is missing.

**Blast radius.** New Stop hook on every Grok turn end once `mode != off`, plus marketplace-dev mirror. Fail-open, advisory, throttled. Reversible. Adding a hook is G8-counted (P6).

---

### P5 — Spawn: owner-flagged OS terminal + always-print copy-paste

**Goal.** After `handoff.md` exists, start a **fresh interactive** Grok TUI whose first turn is the positional seed (C1–C2, C5). Never headless `-p` (C3). Never `/fork` (C18). Never SessionStart injection (C8). OS-terminal open is **one reversible script, owner-flagged** (C40 partially-settled; window-open was **not** executed). Copy-paste is the **guaranteed** path and is **always printed**, even on spawn success.

**Files.**
- Create `plugins/ravenclaude-core/scripts/handoff-spawn.sh`
  - Usage: `bash …/handoff-spawn.sh --task-id <id> [--dry-run] [--recipe <name>]`
  - Resolves project root the same way `rc-artifacts.py` does.
  - Requires non-empty `.ravenclaude/runs/<task-id>/handoff.md`. Missing/empty → exit 1, no `grok` launch.
  - Seed is **only** positional:

    ```
    grok "Continue task <task-id> in this repo. Read .ravenclaude/runs/<task-id>/handoff.md first (then meta.json, decisions.md, summary.md if present). Fresh window. Do not /fork. Do not /compact. Do not re-derive the brief from history you do not have. Execute the next steps in the brief."
    ```

  - Default recipe = `copy-paste`. `os-terminal` recipes (`open -na Terminal --args …`, iTerm/Ghostty, VS Code external terminal) run **only** when `context_handoff.spawn: os-terminal`. Do not invent an AppleScript API. Do not treat inventory-on-PATH as a proven window-open (C40 marker stands until a human enables the flag and a window actually opens).
  - `--dry-run` prints the chosen command and the copy-paste block; launches nothing. **Always** print the copy-paste block.
  - Spawn failure: exit 2, copy-paste on stdout. Handoff already on disk — failure is not a lost brief.
- Modify `plugins/ravenclaude-core/bin/rc`: add verb `handoff` → `handoff-spawn.sh`. Update `_usage`.
- Create `plugins/ravenclaude-core/hooks/tests/test-gate202-handoff-spawn.sh` — bash 3.2; fixtures only; **no live Terminal.app in CI**.

depends_on_claims: [1, 2, 3, 5, 8, 17, 18, 37, 38, 39, 40, 43]

**Pre-build gates.**
- P2 `handoff.md` contract exists (script refuses to invent a brief).
- `command -v grok` for a **manual** live check; CI uses `--dry-run` only.
- Explicit deny-list in comments/tests: no `grok -p`, no `--single`, no SessionStart marker, no `/fork`. Dashboard dispatch (C43) is not used.

**Acceptance tests.**
- Missing `handoff.md` → exit 1; dry-run shows no `grok` argv.
- `--dry-run` with a fixture brief → stdout contains `grok "` and the run-dir path; does **not** contain `grok -p`, `--single`, `--prompt-file`, `--prompt-json`, `/fork`, or `SessionStart`.
- Copy-paste block is a single copy-ready command a human can paste into an existing terminal. Present on success and on failure.
- **Teeth:** a mutant that emits `grok -p` fails (`--must-fail-headless`). Bidirectional, same shape as Gate 186.
- Default (`spawn: copy-paste-only` or unset) never execs `open` / `osascript` / `code`. `--recipe` anything other than `copy-paste` without the owner flag exits non-zero with “os-terminal spawn is owner-flagged”.

**Blast radius.** New script + `rc` verb + test. Live spawn can open a terminal window — `--dry-run` is the test default; the skill calls the live path only after the brief is on disk **and** the flag is on. Fail-open to copy-paste.

---

### P6 — Wire, version, G8 regen, DoD

**Goal.** Make the new skill / command / hook a counted, versioned, gated plugin change so CI and `/plugin marketplace update` stay honest.

**Files.**
- Bump **both** `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` `ravenclaude-core` entry: `0.255.0` → **`0.256.0`** (verified this session, 2026-08-14: plugin.json L5 and marketplace.json L279 both read `0.255.0`).
- Skill count **53 → 54** in:
  - `plugins/ravenclaude-core/.claude-plugin/plugin.json` `description` (currently “53 skills”)
  - `.claude-plugin/marketplace.json` plugin entry `description`
  - `plugins/ravenclaude-core/copilot/plugin.json` (or let `generate-copilot-plugin.py` rewrite it)
- Add `/handoff` to the slash-command lists in those descriptions **and** `plugins/ravenclaude-core/README.md`. Recount live command files at implement time (this checkout already has 8 command files under `commands/`; the plugin.json description currently lists 7 slash commands and omits `/ragnarok` / `/stream` — do not invent a “7→8” filesystem claim; add `/handoff` and keep Gate 12 honest).
- `plugins/ravenclaude-core/CHANGELOG.md` — new **0.256.0** top entry (file exists; current top is 0.253.1 — the 0.254/0.255 gap is pre-existing and is not this feature’s job).
- `plugins/ravenclaude-core/CLAUDE.md` — short “session-handoff” pointer: quality reset, not compact-anchor, Grok-first.
- `scripts/audit-gates.sh` — register **Gate 201** (`test-gate201-handoff-nudge.sh` + `--must-fail-leak`) and **Gate 202** (`test-gate202-handoff-spawn.sh` + `--must-fail-headless`). Do **not** reuse 195/196 — those slots are taken (Gate 195 = gate-introspection; Gate 196 = regex-catalog). Highest existing slot this session: Gate 200.
- Update any fixture literal that hardcodes `53 skills` so the must_fail half still has teeth.
- Regen (G8 — this phase **adds a skill and a command and a hook**):
  1. Quote any `description:` that contains `:` / `{` / `}` (`check-frontmatter.py`).
  2. Counts as above (Gate 12).
  3. `python3 scripts/generate-dashboards.py` → `plugins/ravenclaude-core/dashboard.html`
  4. `python3 scripts/generate-index-dashboard.py` → `index.html`
  5. `python3 scripts/generate-copilot-plugin.py`
  6. `audit-gates.sh` fixture literals
  7. Strip session-bound `.ravenclaude/comfort-posture.yaml` mutations before commit
- Do **not** add globs to `.repo-layout.json` (skills / hooks / commands / scripts already allowed).
- Do **not** expand `knowledge/host-support.json` with a full `grok` host row in v1.

depends_on_claims: [31, 34, 44]

**Pre-build gates.**
- P2–P5 files exist on `feat/ravenclaude-core-session-handoff` (or `forge/session-context-handoff`). `git branch --show-current` is **not** `main` (Claude.md 2026-08-11 lesson). An empty `git branch --show-current` is detached HEAD — resolve it, do not treat it as a pass.
- Versions in `plugin.json` and `marketplace.json` match before commit.

**Acceptance tests (falsifiable).**

```
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool plugins/ravenclaude-core/.claude-plugin/plugin.json >/dev/null
python3 scripts/check-frontmatter.py
python3 scripts/check-marketplace-claims.py
bash -n plugins/ravenclaude-core/hooks/handoff-nudge.sh \
        plugins/ravenclaude-core/scripts/handoff-spawn.sh
npx --yes prettier@3.9.4 --write . --log-level warn
npx --yes prettier@3.9.4 --check . --log-level warn
python3 -m pip install --quiet --user ruff && ruff check .
bash plugins/ravenclaude-core/hooks/tests/test-compact-anchor.sh
bash plugins/ravenclaude-core/hooks/tests/test-gate201-handoff-nudge.sh
bash plugins/ravenclaude-core/hooks/tests/test-gate201-handoff-nudge.sh --must-fail-leak; test $? -ne 0
bash plugins/ravenclaude-core/hooks/tests/test-gate202-handoff-spawn.sh
bash plugins/ravenclaude-core/hooks/tests/test-gate202-handoff-spawn.sh --must-fail-headless; test $? -ne 0
scripts/audit-gates.sh
```

- `git diff --name-only` does **not** include `hooks/compact-anchor.sh` or `scripts/compact-anchor.py`.
- Layout snippet from AGENTS.md reports no violations.

**Blast radius.** User-visible plugin release. Reversible by reverting the version bump + new files. Consumer update path: `/plugin marketplace update ravenclaude` then `/reload-plugins`. **No migration for default-off:** users who never set `context_handoff.mode` see no new Stop nag. Enabling `nag` or `os-terminal` is an owner action. Document the knobs in the skill.

## 5. Risk matrix

| Risk | Source | Severity | Mitigation |
|---|---|---|---|
| Live `signals.json` poll no-ops forever | G3b C24 **falsified** | High (would silent-kill detect) | Do not poll it as used-meter. Live used = C26 `updates.jsonl`. |
| Window size unknown → percent never computed → hook always silent | G3b C24 + Plan A “no 500000 constant” | High (detector becomes dead) | Ranked window resolver + owner knob. Skill still ships (critical path P2+P3). Hook fail-open is a valid v1. |
| Skill “just checks `GROK_SESSION_ID`” and finds nothing | G3b C30 **falsified** | High (false “I can’t meter”) | Detection is hook-only (C28). Skill never requires the env var. Hook injects the percent via `additionalContext`. |
| OS-terminal spawn does not open a window under VS Code-family TTY | G3b C40 **partial** | Med | Flag default `copy-paste-only`. One reversible script. Always print copy-paste. Scope §4b treats copy-paste as success. |
| Model ignores the nag | Plan A/B | Med | Derive-filled skeleton still written by `/handoff` or by the writer when invoked. `mode: block` is opt-in + `max_blocks`. Do not ship block as default. |
| Hook echoes transcript into `additionalContext` | Plan A / Gate 186 | High (injection) | Derived-values-only + Gate 201 `--must-fail-leak`. |
| Successor launched with `grok -p` / `/fork` / SessionStart seed | G0 miss + C3/C8/C18 | High (defeats quality reset) | Gate 202 `--must-fail-headless`. Skill body only names those strings inside negations. |
| Compact-anchor / PreCompact creep | Scope §2, C34–C36, C45 | High (re-litigates retracted claim) | Explicit out-of-scope tests: those files byte-identical; no new PreCompact matcher. |
| Thrash: nudge every Stop | Plan B | Med | Once-per-session state file + skip if recent `handoff.md`. |
| Argv-length blow-up on full brief | Plan B | Low | Seed is a file pointer. |
| Consumer surprise on marketplace update | AGENTS.md house rule 3 | Med | Ship `mode: off`. Migration note: opt-in knob only. |
| C14 UPS injection assumed later | G3b owner-gated | Med if someone “just adds UPS” | v1 happy path is Stop C12. Any UPS work = one reversible file, feature-flagged. |
| Versions / skill-count drift | Plan A G8, 2026-06-03 hotfix chain | High (CI red) | P6 regen list + Gate 12. Confirm 0.255.0→0.256.0 at implement if tip moved. |
| Half-landed on `main` after a denied `checkout && …` | Claude.md 2026-08-11 | Med | Print branch before the edit run. Empty `git branch --show-current` is not a pass. |

## 6. Every G1 `[unverified]` / owner-gated claim — settling or containing step

| id | Status after G3b | Marker | Step that settles or contains it |
|---|---|---|---|
| **14** | **owner-gated** | `[unverified — premise not disconfirmed: UPS probe not installed]` | **Contained.** No `UserPromptSubmit` detector in v1. Happy path is Stop `additionalContext` (C12, settled). Any later UPS probe = one reversible file, feature-flagged. P4 `depends_on_claims` lists 14 so the contain is explicit. |
| **24** | **falsified** | live parent had no `signals.json`; finished G0 session does | **Contained.** P1 must not poll `signals.json` as a live used-meter. File may supply `contextWindowTokens` only if present. Mutant test forbids using `contextTokensUsed` as live used. |
| **26** | **settled** | 293 hits, 59363→170458 on live parent `updates.jsonl` | **Used.** P1/P4 live meter. |
| **30** | **falsified** (agent process) | `GROK_SESSION_ID` unset; only `GROK_AGENT=1`. Hooks still get it (C28). | **Contained.** Detection lives in the hook, not the skill. `detect_host()` keys on `GROK_AGENT` / `GROK_HOOK_EVENT`, never `GROK_SESSION_ID`. |
| **40** | **partially-settled** | `[unverified — premise not disconfirmed: window-open not executed]`; `open`/`osascript`/`code`/`grok` on PATH; `TERM_PROGRAM=vscode` | **Contained.** P5 is one reversible spawn script, owner-flagged (`spawn: os-terminal`). Default and CI path = copy-paste. Do not claim a working window-open until a human runs the flag and a window actually opens. |
| **5** | **settled** | `grok --help` shows positional `[PROMPT]`; no `--prompt` | **Used.** P3/P5 seed is `grok "<prompt>"`. |
| **8** | **settled** | follows C6 (SessionStart stdout ignored) | **Used as a forbid.** Never Grok SessionStart injection. Compact-anchor stays Claude/post-compact only. |

No other G1 row is still `[unverified]`. C36 is settled as host-split (do not treat Claude compact-anchor facts as Grok facts).

## 7. Versioning

Verified this session (2026-08-14):

| Artifact | From | To |
|---|---|---|
| `plugins/ravenclaude-core/.claude-plugin/plugin.json` `version` | **0.255.0** | **0.256.0** |
| `.claude-plugin/marketplace.json` `ravenclaude-core.version` | **0.255.0** (L279) | **0.256.0** |
| Skill count in those descriptions + copilot package | 53 (filesystem count this session) | **54** |
| Slash-command lists in descriptions | add `/handoff` | recount at implement; do not invent 7→8 |
| `plugins/ravenclaude-core/CHANGELOG.md` | top is 0.253.1 | new **0.256.0** top entry (file exists → keep current) |
| `.repo-layout.json` | unchanged | no new dirs |

Minor bump: new user-visible skill, command, and hook. Re-read both version fields at implement time; if tip has moved past 0.255.0, bump one minor from the then-current lockstep pair. Marketplace catalog `metadata.version` (0.92.0) is **not** this plugin’s version — do not touch it unless a separate catalog rule requires it.

## 8. Layout globs

No new purpose-dirs. Expected paths already match `.repo-layout.json`:

- `plugins/*/hooks/**`
- `plugins/*/hooks/hooks.json` (covered by the hooks glob)
- `plugins/*/scripts/**`
- `plugins/*/skills/**`
- `plugins/*/commands/**`

Run-dir artifacts (`.ravenclaude/runs/<task-id>/handoff.md`, state files) are gitignored local-run tier — not layout-gated.

**Action at implement:** run the AGENTS.md layout-verification snippet before push. Add globs only if a new purpose-dir appears (this plan introduces **none**).

## 9. Definition of done

- [ ] A Grok session **below** auto-compact (~85%) can `/handoff` (or accept a Stop nag when `mode: nag`) and produce a non-empty `.ravenclaude/runs/<task-id>/handoff.md` + updated `meta.json` in the **same** task dir (`bin/rc artifacts new`, no parallel id).
- [ ] Skeleton is derive-filled by `context-handoff.py`; narrative sections are model-filled by `session-handoff`. Hook never writes the brief.
- [ ] Successor seed is positional `grok "<pointer prompt>"` in a fresh TUI **or** the originating session printed that exact command. Never a compacted summary. Never `grok -p`. Never `/fork`. Never SessionStart injection.
- [ ] Live detector uses `updates.jsonl` `params._meta.totalTokens` (C26) from a **hook** process (`GROK_SESSION_ID`, C28). Does not poll `signals.json` as a live used-meter (C24). Does not read `GROK_SESSION_ID` from the agent env (C30).
- [ ] Soft threshold owner-tunable, default **70**, always `<` auto-compact. No 40% constant anywhere as a trigger. Ship `context_handoff.mode: off`.
- [ ] OS-terminal spawn is owner-flagged; copy-paste is the guaranteed path and is always printed.
- [ ] `compact-anchor` untouched; no PreCompact persist hook; no UPS detector.
- [ ] Prettier / ruff / `scripts/audit-gates.sh` (including new Gates **201** / **202** + Gate 186 still green) pass on the whole tree before the PR.
- [ ] `python3 scripts/check-frontmatter.py` clean on the new skill + command.
- [ ] G8 regen complete (dashboards, index, copilot package, Gate 12 counts); plugin.json and marketplace.json versions in lockstep at **0.256.0**.

## 10. Out of scope

- Replacing, wrapping, or re-authoring `hooks/compact-anchor.sh` / `scripts/compact-anchor.py`.
- A `PreCompact` / `PostCompact` persist-before-compaction hook.
- Grok `SessionStart` stdout / `additionalContext` as the successor seed.
- Headless `grok -p` / `--single` / `--prompt-file` / `--prompt-json` as the successor.
- `/fork` as a quality reset.
- Other-host spawn adapters (Claude Code `/fork`, Codex, Copilot CLI, Cursor). The **document** is host-agnostic; detect + spawn are Grok-native.
- Dashboard dispatch as the v1 spawn path (C43).
- A `UserPromptSubmit` detector or seed path (C14).
- Encoding a quality-degradation percent (40% / 30% / 300–400K).
- Blocking or retuning Grok auto-compact.
- Committed-tier (`docs/plans/`, `docs/decisions/`) as the handoff home.
- A second parallel run-dir for the same `task-id`.
- `PostToolUse` mid-turn polling in v1.
- Expanding `knowledge/host-support.json` with a full Grok host row.
- Shipping `mode: block` or `spawn: os-terminal` as the install default.
