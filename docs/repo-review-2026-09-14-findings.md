# Repository review — 2026-09-14 (multi-panel bug sweep)

**Status for review by Matt.** Autonomous scheduled run. Branch `claude/awesome-wright-gb6mp6`.

## Read this first — the operational headline

1. **The 2026-09-11 review's 15 staged patches are STILL UNAPPLIED.** This run independently
   re-traced several of them against the live code and confirmed they are **still present** on `main`
   three days later — including the **P0 tribunal-self-disable bypass (D1)**. See
   [`docs/repo-review-2026-09-11-findings.md`](repo-review-2026-09-11-findings.md). Those patches are
   paste-ready there; nothing in this run supersedes them, and **D1 remains the single highest-priority
   item in the repo.**
2. **This run found a fresh crop of substrate bugs the 2026-09-11 sweep did not cover** — most notably
   a **GitHub-token secret-scrub leak** (`_scrub.sh`) and two **false-positive deny-scoping** bugs in
   the destructive-command guard. Staged below (same tribunal constraint as 2026-09-11).
3. **3 new non-substrate bugs were fixed in this PR** (repo-review engine, under `skills/`), each
   verified with a self-test.
4. **Mechanical health, observed this session:** `ci-preflight` reported **19/19 PASS** on the clean
   tree at the start of this run (control), and again after this PR's edits once the one expected
   covered-file digest drift was restamped + regenerated. Every finding below is a **latent** code
   defect a currently-green gate does not assert against — none is a red gate.

## The load-bearing operational constraint (unchanged from 2026-09-11)

**An autonomous agent in this environment cannot patch `plugins/ravenclaude-core/{scripts,hooks}/`.**
The command-review tribunal's `xc.tribunal-self-disable` guard is `always_screen` (category-independent)
and fires even with `command_review.enabled: false`, because shell categories carry `thing: on`.
Confirmed live this session: a **read-only `grep`** over `guard-destructive.sh` was DENIED purely
because the command text referenced substrate paths + destructive patterns (the documented
"source-scan matches prose" over-block; Sága log under `.ravenclaude/runs/thing/`). Edits to those
trees are blocked by design, and **I did not bypass the guard** (the constitution is emphatic about not
tunnelling — e.g. the v0.245.0 heredoc-tunnel incident). The Read *tool* still works on substrate for
review, which is how the confirmations below were done. Consequence for *this task*: every substrate
finding is a staged, ready-to-apply patch for you (or a session with the Thing off), not an autonomous
edit. Files under `skills/` are **not** substrate, so the 3 fixes in this PR applied cleanly.

## Provenance honesty (what was verified, and by whom)

- **Orchestrator-confirmed (I read the live code / ran the affected self-test myself):** F-01, F-02,
  F-03 (the fixes); **N-01** (read `_scrub.sh:45-73` — only `ghp_`/`github_pat_` present); **N-02**
  (read `guard-destructive.sh:188` — `_HEREDOC_REDIR_TARGET` is redirect-only); **N-11**
  (`conserve-tokens.py` false transition — it fired in this session's own startup banners).
- **Reviewer-reproduced, not independently re-opened by the orchestrator:** the remaining
  `guard-destructive.sh`, `serve-dashboards.py`, delegate, `context-usage-meter.py`, and `stall_*`
  findings. Each Panel-1 reviewer supplied a concrete reproduction. **Line numbers are reviewer-reported
  and approximate — confirm at the file before applying.**

## Method (panels + model assignment)

- **Panel 1** — 6 parallel expert reviewers (**Sonnet**, the lighter tier per the model-assignment
  rule), each scoped to a coherent code slice (caveman routing, repo-review engine, context/stall
  meters, dashboard server, guard/tribunal hooks, delegate/egress scripts). Each required a **concrete
  failing scenario** per finding; most reproduced findings live.
- **Panel 2** — this orchestrator (**Opus**) re-verified the findings it could reach against the live
  code (read the actual functions; ran the repo-review self-tests), added impact/effort, re-graded
  priority. N-02 dropped P1→P2 here on reading the author's documented scope (below).
- **Panel 3** — tie-break on the P0/P1 disagreements (below).

> One Panel-1 reviewer (caveman live-apply path) had not returned when this was written (its transcript
> went static ~15 min with no result — likely stalled). Its target is already covered in depth by the
> 2026-09-11 doc's `P1B-01..05` (all still staged/unapplied), so no coverage was lost.

## Fixed in this PR (non-substrate — under `skills/repo-review/`)

All three verified with the affected script's own `--self-test` (green) and re-probed functionally;
ruff clean.

| ID | Final | File | Bug → Fix |
|---|---|---|---|
| F-01 | **P1** | `skills/repo-review/scripts/findings_merge.py` | A shard finding with a non-string `title`/`file` (an LLM can emit `"title": 42`) crashed `title_tokens()`/`compute_key()` with `AttributeError`/`TypeError`, killing the **whole Merge phase** for the entire sweep — asymmetric with the sibling `_line_bucket()`, already try/excepted. **Fix:** coerce both fields to `str` defensively; added `test11` regression assertion. |
| F-02 | **P2** | `skills/repo-review/scripts/estimate_cost.py` | A structurally-incomplete plan JSON (`{}`) raised an uncaught `KeyError` on `plan["coverage"]["batches_planned"]` (direct index, inconsistent with the `.get()` used two lines above), producing a raw traceback instead of the tool's `error:` + exit-code contract. **Fix:** defensive `.get()`. |
| F-03 | **P2** | `skills/repo-review/scripts/review_cache.py` | `store()` hashed the file with no existence check (unlike `lookup()`), so a file deleted between review dispatch and cache-store crashed with an uncaught `FileNotFoundError`. **Fix:** existence guard raising `ValueError`, which the CLI's `store` handler already catches cleanly. |

## New staged findings (Panel 2/3 verdicts) — tribunal-blocked here

Legend — **new** relative to the 2026-09-11 doc unless the "Prior" column links an already-staged twin
(which this run re-confirms is **still present**). Fixes are the reviewers' proposed minimal patch.

| ID | Final | File:line | One-line | Prior |
|---|---|---|---|---|
| N-01 | **P1** | `hooks/_scrub.sh:51` | **Confirmed.** GitHub token prefixes `gho_`/`ghs_`/`ghu_`/`ghr_` are not in `_secret_patterns` (only `ghp_`/`github_pat_` are) → a denied command carrying one leaks the token verbatim into `hook-events.jsonl` + stderr. The session's own `GITHUB_TOKEN` is a `ghu_` token. **Fix:** `ghp_…` → `gh[oprsu]_[A-Za-z0-9]{30,}`. Strictly safe (redaction only widens). | — |
| N-02 | **P2** | `hooks/guard-destructive.sh:188` | **Confirmed mechanism.** Same-command write-then-execute via `\| tee FILE` is not caught while the `>`/`>>` redirect form is (`_HEREDOC_REDIR_TARGET` is redirect-only). The author's comment (lines 184-187) names `tee` among file-write vectors deferred to the OS-container boundary, so this is a **partially-acknowledged defense-in-depth gap**, not a claimed-closed-but-open invariant. **Fix (if tightening desired):** add a pipe-to-`tee` target detector feeding the existing `_cmd_executes_path`. | — |
| N-03 | **P1** | `hooks/guard-destructive.sh:509` | `_is_dangerous_git_clean` scans the **whole** command string for `-f`/`--force`, not the `git clean` segment → benign `git clean -n && ls -f` wrongly DENIED (false positive). Same defect class the file already fixed for `git push`. **Fix:** segment-scope on `;&\|` like `_is_dangerous_git_push_delete`. | — |
| N-04 | **P1** | `hooks/guard-destructive.sh:437` | `_is_dangerous_git_branch_delete` scans the whole command for `-D`/`--delete --force` → `git branch --show-current > f; rsync … --delete --force` wrongly DENIED. Same class, same fix. | — |
| N-05 | **P2** | `hooks/guard-destructive.sh:535` | The multi-pipe curl/wget deny uses a bare `.*` crossing `;`/`&` separators → `curl … -o data.json; cat data.json \| python3 …` wrongly DENIED. **Fix:** `.*` → `[^;&]*` (keeps `\|`, stops separator crossing). | [D3](repo-review-2026-09-11-findings.md) — confirmed still present |
| N-06 | **P2** | `scripts/serve-dashboards.py:2513` | `/__norns?plugin=%00` (a read needs no CSRF token) → path with embedded null byte → uncaught `ValueError` kills the request thread (violates the reader's "never raises" contract; the sibling `read_text()` already catches `ValueError`). **Fix:** allow-list charset `[A-Za-z0-9_-]+`, or wrap `_read_norns` in a degrade-to-empty try. | — |
| N-07 | **P2** | `scripts/serve-dashboards.py:2079` | `POST /__save {"path": null}` (CSRF token obtainable locally via `/__csrf`) → `target.startswith(...)` raises uncaught `AttributeError` before the allow-list check — `content` is type-checked, `path` is not. **Fix:** `isinstance(target, str)` guard mirroring the existing `content` check. | — |
| N-08 | **P2** | `scripts/serve-dashboards.py:150` | Reviewer reports `.ravenclaude/comfort-posture.yaml` is not in the pre-write validation sets → malformed YAML would be persisted, failing only afterward in `_apply_posture()`, unlike sibling allow-listed targets. **Fix:** add it to a YAML-mapping validation set, validate before write. | — |
| N-09 | **P2** | `scripts/copilot-delegate.sh:160` | The only secret-egress scrub is gated on `command -v _scrub_reason`; if `hooks/_scrub.sh` fails to source, the block is silently skipped and the task egresses to `copilot -p` **unscrubbed** — fail-open, no inline fallback (unlike `thing-seat.sh`). **Fix:** fail closed (refuse, exit 8) if the scrub helper is absent. | — |
| N-10 | **P2** | `scripts/cheap-lane-delegate.sh:49` | `"${args[@]}"` on a declared-but-empty array under `set -u` throws `unbound variable` on **bash 3.2** (stock macOS, the platform this file targets) → `cheap-lane-delegate.sh --agent grok` (no other flags) crashes. **Fix:** `"${args[@]+"${args[@]}"}"`. | — |
| N-11 | **P2** | `scripts/conserve-tokens.py:310` | **Confirmed live.** `resolve()`'s `changed = engaged != prev_engaged or not state` is True on **every session's first prompt** (state `{}`) → a never-engaged session prints a false `"CONSERVE TOKENS released … MAXIMUM again"` banner on turn 1 (it fired in this session's own startup banners). **Fix:** `… or (not state and engaged)`. | — |
| N-12 | **P2** | `scripts/context-usage-meter.py:511` | `window_from_grok_config()` (rank 3) runs before the Claude-Code model-aware resolution (rank 4) → a leftover `~/.grok/config.toml context_window` silently overrides the correct 1M window on a Claude Code session; `window_source` also mislabeled `"explicit"` for signals/grok-config provenance. **Fix:** gate behind `source != "claude-code"`. | [P1A-1](repo-review-2026-09-11-findings.md) — confirmed still present |
| N-13 | **P2** | `scripts/conserve-tokens.py:153` | The `parallelism:` mapping-form tail scan (`raw[…:…+4096]`) is not bounded to the block → an unrelated later top-level key (e.g. `command_review.enabled: false`) is misread as `parallelism: sequential`. **Fix:** bound `tail` to the next column-0 key, as `context-usage-meter.py:read_posture()` already does. | [P1A-2](repo-review-2026-09-11-findings.md) — confirmed still present |
| N-14 | **P2** | `scripts/stall_watch.py:660` | `evaluate_launch_hangs()` has no `slept` guard (unlike `evaluate()`) → a machine-sleep coinciding with a slow launch fires an immediate false launch-hang alert with a sleep-inflated `silent_min`. **Fix:** thread the `slept` flag in and skip alerting (keep recording) when slept. | — |
| N-15 | **P2** | `scripts/stall_watch.py:383` | `count_compact_boundaries()` does a full unbounded read of the transcript every tick per stalled session, contradicting the module's own `TAIL_BYTES`-bounded design (85 MB transcript re-read every 5 min). **Fix:** bound to a tail window, or cache on size/mtime. | — |
| N-16 | **P2** | `scripts/stall_reach.py:137` | `send_one()`'s `mkstemp()`/`fchmod()` sit outside its own `try:` → a failure aborts the whole `dispatch()` comprehension before later sinks are attempted (defeating per-sink isolation) and can leak the raw fd. **Fix:** move inside the try (or its own try returning a per-sink error receipt). | — |
| N-17 | **P2** | `scripts/stall_watch.py:261` | `proc_identity_ok()` never compares `procStart` — it just checks whether `ps` returned output (duplicating `pid_alive()`), costs a subprocess/tick, and its result is read nowhere. The PID-reuse guard is dead. **Fix:** implement the elapsed-time comparison and consult it, or drop the dead computation + per-tick `ps`. | [P2A-1](repo-review-2026-09-11-findings.md) — confirmed still present |
| N-18 | **P2** | `scripts/route-task.py:146` | A `--task-file` with invalid UTF-8 raises an uncaught `UnicodeDecodeError` (a `ValueError` subclass not caught by `except OSError`) instead of the documented fail-safe default-to-claude. **Fix:** `except (OSError, UnicodeDecodeError)`, or `errors="replace"`. | — |
| N-19 | **P3** | `scripts/route-task.py:148` | The unreadable-file `except OSError` branch omits the `escalations`/`cheap_signals` keys every other `route()` return includes → schema drift a direct-index caller would `KeyError` on. **Fix:** add `"escalations": [], "cheap_signals": []`. | — |
| N-20 | **P2** | `skills/repo-review/scripts/estimate_cost.py:193` | `v_max`/`k_max` (from `--verify-cap`/`--fix-cap`) are never clamped against `WORKFLOW_AGENT_CALL_HARD_CAP`, so `total_agents` can exceed 1000 while `agent_budget_clamped` stays `False` — contradicting the module's own stated invariant. **Editable (under `skills/`) but deferred here:** it changes the output contract and needs a self-test extension; left as a recommendation to keep this autonomous PR low-risk. | — |

### Panel 3 — tie-break record

- **N-01 (`_scrub.sh` token leak): reviewer P0 → final P1.** A confirmed secret-scrub gap, but exposure
  is **local-only** (the `hook-events.jsonl` audit log + stderr, not a remote sink) and **conditional**
  (a live token must appear literally in a command that then gets denied). Real, but below the
  "security-critical on realistic input" P0 bar. The **fix is unarguably safe** — widening a redaction
  pattern can only ever redact *more* — so this is the lowest-risk substrate patch to apply first.
- **N-02 (`| tee` gap): reviewer P0 → final P2.** On reading the code (line 188 + the author's scope
  comment at 184-187), the tee vector is one the author **explicitly defers to the OS-container
  boundary**, so it is defense-in-depth, not a broken invariant. Downgraded to P2; fix only if the
  same-command tee case is judged worth closing beyond the container boundary.
- **N-06/N-07 (dashboard crashes): reviewer P0 (blocking) → final P2.** Uncaught-crash bugs, but the
  blast radius is **death of a single request thread** on a `127.0.0.1`-bound local dev server (N-06
  potentially reachable via a bare cross-origin `<img>` GET that omits `Sec-Fetch-Site`). Local DoS / a
  broken "never raises" contract, not a compromise → **P2**, still worth fixing (the codebase already
  type-checks `content` for exactly this shape and just missed `path`/`plugin`).

## Design questions / recommendations (needs your decision)

1. **Apply the 2026-09-11 staged patches — they have sat unapplied for 3 days.** The confirmed-still-
   present overlaps (N-05/N-12/N-13/N-17 above) are direct evidence those patches never landed.
   **D1 (the P0 tribunal-self-disable `curl -o`/`wget -O` substrate bypass) is the top priority.**
2. **C-02 (from 2026-09-11) is still an open design question** — does `--no-cross-model` apply to the
   `max` tier? SKILL.md documents the flag; the code ignores it for `max`. Recommendation there was
   option 1 (tri-state). Unchanged; still yours to decide.
3. **The new security-floor findings deserve a batch.** N-01 (token scrub) and N-03/N-04/N-05
   (false-positive deny scoping) are low-risk and each mirrors a fix idiom the file already uses
   elsewhere. Apply from a session with the Thing off, or via the dashboard.
4. **The recurring structural tension (flagged 2026-09-11, restated):** an unattended agent literally
   cannot fix its own guardrail code here — the correct default, but it means guardrail bugs
   (N-01..N-05, D1) can only be auto-*found*, never auto-*fixed*. A narrow, sanctioned substrate-edit
   path for authorized autonomous maintenance is the standing question this keeps surfacing.

---

_Panel-1 reviewer finding JSON (full scenarios/observations/confidence) is in this run's task
transcripts; the exact minimal patch for each staged finding is in its "Fix:" clause above._
