# Changelog — ravenclaude-core

All notable changes to the `ravenclaude-core` plugin. Versioning is semver; the `version` field in `.claude-plugin/plugin.json` (mirrored in the marketplace catalog) is the authoritative source of truth, and this file tracks the user-visible arc. Larger architectural narratives live in [`CLAUDE.md`](CLAUDE.md) milestones; this file is the scannable per-version log.

## 0.308.0 — 2026-08-30

### Added

- **`check-trigger-scoping-consistency.py` (Gate 253)** — PR 6 / Phase 9 of the
  2026-08-13 recurring-defect-hardening initiative, the last un-shipped PR from
  that 17-PR set. Statically flags a bare unscoped `.*` trigger sitting beside
  a properly separator-scoped sibling in the same command-review category —
  the exact shape of the `srm.force-push` (v0.242.0) and `sce.curl-pipe-shell`
  (v0.244.0/.1) incidents, this time caught before merge instead of after.

### Fixed

- **Two previously-uncaught instances of that same defect class**, found by
  the new checker's first real run and fixed in the same change:
  `xc.no-undo`'s `curl … -X DELETE` trigger and
  `srm.push-to-protected-branch`'s trigger both used a bare `.*` beside an
  already-scoped sibling in their own category/entry. Both now use the same
  `[^|&;\n]*` convention as their siblings. Neither was independently
  exploitable as a security bypass (the bare `.*` only risked over-triggering
  across a chained command, never under-detecting); both are real consistency
  defects the new gate exists to catch.

## 0.307.0 — 2026-08-28

### Fixed

- **Stale Claude Code platform facts (draft #987, recut).** `main` still taught
  "nested sub-agents up to 5 levels deep (v2.1.172)" after the changelog
  superseded it. Recut from current main (do **not** merge #987 as-is — that
  commit rewinds the plugin to 0.283.0). Facts, re-checked against the changelog
  through 2.1.250 (2026-08-28):
  - Nesting default is **depth 3** (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`;
    v2.1.217 disabled-by-default, v2.1.219 set 3). House single-orchestrator
    policy is unchanged.
  - Native concurrent cap **20** (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`,
    v2.1.217). The 200 per-session cap was **removed** in v2.1.224.
  - `/reload-plugins` is often unnecessary since v2.1.221.
  - Marketplace `archive` (v2.1.224) and `command` (v2.1.229) source types.

## 0.306.1 — 2026-08-28

### Fixed

- **`session-handoff` vs `cheap-lane-delegation` are two products, not one
  "give this to Grok".** Skill descriptions now route the fork (bounded job
  that returns vs new unbounded TUI). `handoff-spawn.sh` prints a `PRODUCT`
  line before launch; when `cheap_lane` is `advise`/`agent` it also names the
  spawn as a host-switch. Measured 2026-08-28: "pass remaining work to grok"
  from a quota-limited Claude session spawned an interactive grok-4.6 TUI via
  `/handoff` and never called `cheap-lane-delegate.sh`. Gate 213 asserts the
  product line and the cheap_lane clause.

## 0.306.0 — 2026-08-28

### Added

- **Cause-taxonomy phases 1–11 + P1-3 must-fail teeth.** The verify-before-assert
  surface: SSOT cause grammar, post-failure triage, remediation-cause and
  cause-closure guards (shipping at `warn`), a portable cause floor, outcome-eval
  that the ship gate is satisfiable, and anti-rot parity/fired-count checks.
  Gates 245–250 plus Gate 252 (pre-flight command review — WARN-only, one
  measured rule). Pre-flight was Gate 244 on this branch; #1023 had already
  shipped stall-watchdog as Gate 244, so the merge yields the number rather
  than colliding. P1-3 closed: the remaining three `--must-fail` halves now
  call `check()`, so blinding `check()` turns them red.

### Migration

None — additive gates and warn-level hooks. Nothing in an installed plugin
behaves differently on `/plugin marketplace update`.

## 0.305.3 — 2026-08-28

### Fixed

- **SessionStart hooks that had no `timeout` now cap at 10s.** `reapply-posture.sh`,
  `ensure-default-mode.sh`, and `worktree-guard.sh register` were the remaining
  SessionStart entries without a host timeout. Claude Code's SessionStart contract
  is still additive (it cannot deny a session), but an unbounded hook subprocess
  can still sit on stdin. This is defense-in-depth for a fresh-session TUI that
  never reaches `/usage`; the load-bearing hang observed 2026-08-27 was MCP
  needs-auth (Figma/Vercel/fal), not these hooks. Dev-mirror in `.claude/settings.json`
  matches.

## 0.303.0 — 2026-08-26

### Added

- **The cheap lane — `skills/cheap-lane-delegation`, `scripts/route-task.py`,
  `scripts/grok-delegate.sh` — route everyday work to Grok, escalate the hard
  work to Claude.** Measured (14-day, main-loop output): 41.2M tokens, 83.2%
  top-tier model, essentially none of it on a cheap model, and none of it
  sub-agent spend — `agent-dispatch-evaluator` tunes sub-agent tier and cannot
  touch this. The fix is upstream of tier selection: decide whether a task needs
  the main Claude session's reasoning loop at all.

  `route-task.py` is a deterministic text classifier, no model call, self-tested
  (`--self-test`, 17 cases + 2 teeth checks: one proves the router is not a
  constant `claude`, one proves an escalation rule dominates a co-occurring cheap
  rule rather than the reverse). **The default is `claude`, deliberately
  asymmetric** — an unmatched, ambiguous, or both-lanes task all resolve to
  `claude`; a task wrongly sent to Grok can produce a confidently wrong
  multi-file change that costs more to unwind than it saved, a task wrongly kept
  on Claude only costs money.

  `grok-delegate.sh` is the transport, mirroring `claude-orchestrate.sh`'s
  hardening pointed the other way: a recursion guard (nested delegation, or
  called from inside a tribunal seat), a pre-egress secret scrub (refuses
  before anything leaves the machine, never after), and a bounded timeout with
  fall-back-to-local on any non-zero exit.

  ⛔ **Containment is two independent layers, verified with a positive control
  after an initial false conclusion.** The first version of this file claimed
  Grok's `--sandbox` flags do not contain, based on a probe run *inside* one of
  `--sandbox read-only`'s own always-writable temp paths — a write there is not
  a containment failure. Re-tested outside every allowlisted path: the kernel
  (Seatbelt on macOS) genuinely refused the write and logged it to
  `~/.grok/sandbox-events.jsonl`. Fixed same-session — `--sandbox <profile>` is
  the real, kernel-enforced boundary (`advise`→`read-only`, `agent`→`workspace`);
  the disposable worktree/scratch-dir is what Grok can reach in the first place
  and, for `agent` mode, the reviewable diff before merge. Neither layer
  replaces the other.

  **Off by default**, matching `design_checkins` / `decision_review` /
  `parallelism` / `orchestrator`: `cheap_lane: { mode: off | advise | agent,
  tier: fast | balanced }` in `.ravenclaude/comfort-posture.yaml`. `off` is
  inert — nothing runs until a consumer opts in. Full contract:
  [`skills/cheap-lane-delegation/SKILL.md`](skills/cheap-lane-delegation/SKILL.md);
  the composition with `spawn-team` and `agent-dispatch-evaluator`, and why
  this milestone does **not** flip the evaluator's own gated `binding`-mode
  default, in [`CLAUDE.md`](CLAUDE.md) § "The cheap lane".

  **Migration:** none — `cheap_lane` defaults to `off`; nothing in an installed
  plugin changes on `/plugin marketplace update` until a consumer sets the
  knob. Skill count 55 → 56; script-tool count 32 → 33 (`route-task.py`;
  `grok-delegate.sh` is bash and is not counted by `_scan_scripts`'s `*.py`
  glob).

### Fixed

- **`scripts/inventory-nuance-judge.py` re-ran the full 24-item golden-set
  calibration on every invocation, and it is invoked independently by at least
  two callers in one `audit-gates.sh` run.** Measured: gate 238 (inventory
  sweep) 540.1s, gate 241 (nuance floor) 146.1s. Now content-hash + a
  short, disclosed TTL (default 1h — `--cache-ttl-hours` / `INVENTORY_JUDGE_CACHE_TTL_HOURS`,
  `--no-cache` / `INVENTORY_JUDGE_CACHE=off` restores the exact prior behavior).
  The report line reads `cached, verified <age> ago`, never blended into
  "verified now" — the file's own strongest stated invariant ("calibration
  must hold IN THE SAME RUN") is honored by disclosure and a short window,
  not silently reinterpreted. Per-entry verdicts cache without a TTL (the key
  IS the judged text, so a hit means the question is byte-identical) but are
  only ever read when calibration is CURRENTLY valid.

  Verified with a new `--self-test` (12 assertions, 5 of them mutation-style
  teeth) rather than a live model call: a live nested `claude -p` from inside
  this repo's own working directory was found to hang intermittently during
  this work (up to 60s+, no answer — isolated with a positive control to a
  directory with no `.claude/settings.local.json`, which answers in ~6s every
  time). That is a separate, unfixed finding, not something this caching fix
  addresses or depends on.

  **Migration:** none — cache lives at `.ravenclaude/cache/` (gitignored),
  read/write is fail-safe on every error path, and `--must-fail`/
  `--must-fail-convention`'s existing structural teeth are unchanged.

## 0.302.0 — 2026-08-26

### Added

- **`hooks/guard-foreground-suite.sh` — a PreToolUse(Bash) guard that denies a FOREGROUND
  invocation of a suite that provably cannot finish inside the Bash tool's hard ceiling.**

  The Bash tool clamps `timeout` at **600000 ms**, and `scripts/audit-gates.sh` (917 gates)
  outgrew it. A foreground full-suite run is therefore **structurally guaranteed** to wedge the
  session for the full ten minutes and then be auto-backgrounded anyway — the operator sees a
  stall, and the run they were waiting on was never going to return in-band.

  **control (session `94d2ba9f`, 2026-08-25):** foreground call at `02:21:45Z`, result at
  `02:31:49Z` — *"Command did not complete within its 600s timeout and was moved to the
  background (ID: bg7y7j7s7)."*

  ⛔ **Raising the timeout is a non-fix, and it fails silently.** The same session tried
  `timeout: 900000` at `07:17:42Z` and received the byte-identical *"within its 600s timeout"*
  message at `07:27:45Z`. 900000 is clamped to 600000 with no warning, so the guard now calls
  that out explicitly in its denial rather than letting the next person rediscover it.

  ⛔ **Why a hook and not a note.** This fired 3+ times in one week, and the third time it fired
  at a session that had **already adopted `run_in_background: true`** — five clean runs that
  morning — and regressed off it hours later. A written note demonstrably did not hold. This is
  the control that does.

  **Three escapes, all allowed:** `run_in_background: true` (the right answer for a full suite),
  `--check N` (one gate, seconds), and a literal `RC_SUITE_FOREGROUND_ACK=1` prefix. The ACK is
  read out of the **command text**, not the environment — an env var cannot reach a PreToolUse
  hook from inside the command it gates, so spelling it as a prefix is what makes it reachable.

  ⛔ **Matching is INVOCATION-only, never substring.** The command is split into segments and
  each segment's **first word** is checked, so `grep`, `sed`, `git show` and `wc` that merely
  **name** the suite still run. A guard that cannot tell a command from a description of one
  blocks its own repair — this repo has already paid for that twice.

  **Posture: fails OPEN.** An unreadable payload, absent `jq`, or absent `python3` all ALLOW and
  emit a `warn` event. This is an ergonomic guard, not a trust boundary; denying a tool call
  because a convenience hook could not read its own input would be a worse failure than the ten
  minutes it prevents. (Contrast `worktree-guard.sh`, which gates a trust boundary and fails
  closed.) It reads its own payload with `_rc_timeout`+`cat`, never `read -t` — the latter
  deadlines a *complete line* and bash reads a pipe one byte per `read(2)`, which turns the
  deadline into a payload-size cap.

  **Pinned by Gate 251** (`hooks/tests/test-guard-foreground-suite.sh`, 23 assertions), registered
  in the `--check` dispatcher, the main sequence, and the `Supported:` string. The load-bearing
  half is the **must-fail** one: it neuters the matcher and asserts the deny disappears, and it
  carries its **own vacuity control** — if the mutation fails to apply, the half fails rather
  than reporting green against a byte-identical copy.

  **Migration:** none required. If you genuinely want to spend the ten minutes, prefix the
  command with `RC_SUITE_FOREGROUND_ACK=1`. Extend coverage to another long suite via
  `RC_FOREGROUND_SUITES` (space-separated basenames; default `audit-gates.sh`).

## 0.301.0 — 2026-08-25

### Added

- **Stall watchdog** — an out-of-session detector for wedged Claude Code sessions
  (`scripts/stall_watch.py` + `scripts/stall_reach.py` + `scripts/install_stall_watch.py`),
  installed as a macOS LaunchAgent on a 300s interval. Verified end-to-end under launchd against a
  real 174-minute stall: detected, `0600` secret read from the launchd context, sink returned
  **HTTP 200**, escalation rung advanced only after the receipt.

  **Why this cannot be a hook, measured:** all 39 registered hooks fire on a turn or tool boundary
  (SessionStart 9, PreToolUse 12, PostToolUse 10, UserPromptSubmit 2, SubagentStart 1, Stop 5). A
  stall is *defined* by the absence of a turn boundary. `handoff-nudge.sh` — the guard built for a
  hot window — is a **Stop** hook: if the turn never stops it never runs. Detection must come from
  outside the process.

  **The observable is last-ASSISTANT-record age.** Every alternative failed toward "looks alive",
  which is the dangerous direction: last-entry-of-any-type **masked the real stall by 44.3 min**
  (the owner's own queued prompts plus a product-generated `system/away_summary` reset the clock —
  the stalled session's last six timestamped records contain *zero* assistant records); file mtime
  diverges up to 100 min the same way, and 99.03% of transcripts end in an untimestamped record;
  registry `statusUpdatedAt` is a genuine but coarse progress signal (~17-min bump cadence, measured
  over 35 samples — **not** the "transition latch" an earlier analysis claimed) and is simply
  superseded, since the assistant-record distribution has p99.9 = 4.52 min.

  **The registry (`~/.claude/sessions/<pid>.json`) is used for liveness and idle-exclusion only.**
  It does *not* close the killed-session class structurally: `SIGKILL` **orphans** the `.json`/`.key`/
  `.sock` (measured, with a clean-exit positive control that *did* remove them), so dedup state is
  retained rather than demoted.

  Security invariants: the webhook URL never enters `argv` (`curl --config` over a `0600` file —
  `ps -Ao args` would otherwise expose it 288×/day, and a real bootstrapped LaunchAgent sees only 12
  env vars with `RAVENCLAUDE_NOTIFY_WEBHOOK` **absent**); no untrusted text is ever interpolated into
  `osascript` (a cloned repo names its own directory); payloads carry a salted-hash project key and
  validated integers only. `scripts/notify.sh` is deliberately **not** reused — its
  `curl … >/dev/null 2>&1 || true` discards the HTTP status that is the entire justification for the
  channel. A 2xx means "accepted by the sink", never "a human saw it"; a zero-subscriber topic
  returns 200, and that limit is carried as an explicit accepted-risk waiver.

- **Gate 244** (`hooks/tests/test-stall-watch.py`) — one gate slot, five check groups, each with a
  must-fail half **proven to flip**: the RT-2 mutant drops a naive detector to 1.0 min (a miss) while
  the whitelist detector still reads 141.0 min; widening the whitelist moves the answer 141.0 → 96.7;
  the `time.mktime` variant differs by the zone offset, so the UTC bug is detectable here. Registered
  in `scripts/audit-gates.sh` in **both** the `--check` dispatcher and the main sequence, and verified
  to *bite* (mutating the observable turns it red) — a gate no workflow invokes and a gate that cannot
  fail are both this repo's documented silent-green classes.

- **Frozen fixtures** (`tests/fixtures/stall-watchdog/`) — derived skeletons of one positive and three
  negative sessions, **timestamps and record types only, no message content**: raw transcripts carry
  credentials, tool output and fetched web bodies and must never be committed. 14.7 MB → 606 KB, and
  the skeletons reproduce the ground truth including the 44.3-min masking effect.

## 0.299.1 — 2026-08-25

### Fixed

- **`worktree-guard.sh` no longer hangs forever on an inherited pipe.** The hook read its stdin
  payload with a bare `cat`, gated on `[ ! -t 0 ]`. That test cannot distinguish *"a payload is on
  its way"* from *"fd 0 is an open pipe nobody will ever write to"* — both are simply not-a-tty — so
  the gate was satisfied in precisely the case that blocks, and the read never returned. Every caller
  downstream stalled with it, `audit-gates.sh` Gate 140 included, which invokes this hook and
  inherits whatever stdin the harness was launched with.

  Measured under a FIFO with a held-open writer: `status --json` and `check` both hung until killed
  at 6s, while a control script that reads no stdin exited in 1s under the identical descriptor — the
  differential is the read, not the environment.

  The read is bounded with **`_rc_timeout` + `cat`** (`_portable.sh`'s existing `timeout → gtimeout →
  perl alarm` ladder, already sourced by this hook), so the ceiling applies to the **writer** —
  `RC_GUARD_STDIN_TIMEOUT`, default 10s, arithmetically clamped, `0` restores the old blocking read.

  ⛔ **`read -t` was the wrong instrument, and that took two attempts to see.** It deadlines a
  **complete line**, and bash reads a pipe one byte per `read(2)`. A Claude Code payload is
  single-line JSON, so the deadline ends up racing bash's byte loop instead of the writer, and payload
  **size** consumes the budget meant for writer latency. A `Write` of this repo's own `dashboard.html`
  JSON-encodes to **~11 MB on one line** (escaping turns all ~17k newlines into `\n`). Measured
  through a real pipe on bash 3.2.57: `read -t 10` took **4.6s idle** and lost the **entire payload at
  10.04s under a load of ~4 on 10 cores**, while `_rc_timeout 10 cat` did the same bytes in **0.3s**
  either way. Any deadline on `read` is a bet against payload size × machine load. It also bounds the
  **whole** read — `read` plus an unbounded `cat` drain still hung once one line had arrived (measured
  past 14s), so only the zero-byte case had actually been fixed. And it sidesteps a platform split
  this host cannot test: bash 3.2 discards partial input on timeout (measured — the variable is left
  untouched) while bash ≥4 documents retaining it, which on a Linux runner would hand the parser a
  **truncated** payload. There is no partial-line branch any more, so neither behaviour is reachable.

  ⛔ **An unreadable payload now fails CLOSED on `check`.** A payload with no `tool_name` sends every
  classifier to its `*)` default — "not mutating / no deny / no enforcement" — so the default-block
  FOREIGN-TREE deny and the session lease both silently disarm. The boundary is deliberate: a
  zero-byte **clean EOF** is the documented no-payload contract (a bare CLI or test invocation) and
  still allows; what denies is a **timeout** or an **unparseable** payload, the shapes a stalled or
  truncating writer produces. `register` is exempt by contract and `status` no longer reads stdin at
  all — it carries no payload and was paying the full deadline ~15× per Gate 140 run.

  ⛔ **The knob is clamped arithmetically, not by character class.** `00` and
  `99999999999999999999` are all-digits, so a `*[!0-9]*` filter passed them and the timeout tool then
  rejected them as an argument error — an empty payload in 0s, i.e. the guard disarmed by the most
  natural attempt to configure it. Out-of-range falls back to the **default**, never the ceiling:
  clamping `2000` to 3600 would hand an operator who assumed milliseconds a 33-minute deadline.

  Pinned by **T18** in `test-worktree-guard-core.sh` (Gate 140), in seven halves — (a) the hook exits
  under a held-open FIFO; (b) a must-fail half restores the bare `cat` and asserts it *still* hangs,
  so (a) measures the read and not the fixture; (c) payload fidelity, labelled as a **fidelity**
  detector rather than a bound detector because the pre-fix hook passes it too; (d) a truncated
  payload fails closed while clean-EOF-empty and a readable payload still allow; (e) a 3s-late writer
  is served by the shipped deadline **and starved by a 1s one**, so the margin is tested rather than
  asserted; (f) eight malformed/extreme knob values all still read the payload; (g) a 3 MB
  single-line payload is read whole. `audit-gates.sh` also redirects Gate 140's three invocation
  sites from `/dev/null` — the suites drive a stdin-reading hook, and a bound is a ceiling, not a
  reason to hand a suite an open pipe.

  ⛔ **Not fixed here, and the count is reported with its command because three regexes gave three
  answers.** Of the **169** plugin hook scripts (`find plugins -path '*/hooks/*.sh' -not -path
  '*/tests/*'`), **145** slurp stdin with a bare `cat` and **134** of those gate on `-t 0`
  (`grep -lE '\$\(cat( 2>/dev/null)?( \|\| (true|printf|:))?\)'`, 2026-08-25). Two independent
  recounts produced 143/138 and 148/137 on different patterns — so treat any single number as a
  function of its regex, not a fact.

  What all three agree on, and the worse class: **11 hooks read stdin with an unconditional bare
  `cat` and no tty test at all** — `agent-dispatch-evaluator.sh`, `codex-hook-env.sh`,
  `cursor-hook-adapter.sh`, `enforce-portability.sh`, `ensure-default-mode.sh`,
  `gemini-hook-adapter.sh`, `guard-premise.sh`, `log-probe.sh`, `route-decision-review.sh`,
  `stream-session-close.sh`, and `power-platform/hooks/nudge-dataverse-preflight.sh`. All of these are
  invoked by Claude Code, which writes the payload and closes the descriptor, so none is *known* to
  hang in practice — but the shape is the one just fixed, and this fix is not applied to them. Out of
  scope for this patch; recorded so the survey is not mistaken for a clean bill of health.

## 0.299.0 — 2026-08-25

### Added

- **The org-skill studio** (`skills/authoring-org-skills/`) — lint, pack and verify a claude.ai
  Organization Skill. 41 rules across a fail/warn split, hard refusals `R1`–`R4` with no override, a
  `pack`/`verify` separation that shares data and never code, and tiers that are **derived from a
  recorded evidence file** rather than hand-set, so a constraint the vendor contradicts itself on
  ships as WARN instead of a guess. (Backfilled entry — the 0.299.0 bump landed in #1021 without one.)

## 0.298.0 — 2026-08-24

### Changed

- **Re-verified and re-stamped the seven `platform-fact` "Foundations" concepts** — `agent-harness-loop`,
  `tool-use`, `context-window`, `subagents`, `mcp`, `model-selection`, `source-control-basics` — refreshing
  each `last_verified` from 2026-06-05/04 → 2026-08-24. All seven were re-read and confirmed current
  against how agentic AI works today; several were empirically re-confirmed this session (the agent loop,
  tool-gating, compaction, the Explore subagent dispatch, MCP servers connecting).

  This **honors the concept-inventory design** (`docs/plans/2026-08-19-product-inventory/plan.md` §5.3):
  `platform-fact` entries carry a **90-day BLOCKING** calendar gate on PRs — deliberately stricter than
  the 180-day warn-on-PR inventory corpus — because the ~17-entry population is small enough to service by
  re-verification rather than by relaxing the gate. The seven were ~80 days old and would have crossed 90
  within ~10 days, taking every subsequent PR's `scripts/concepts.py --check` down with them in a wave.
  This is the scheduled service, done early — **the gate logic is unchanged**. Regenerated `concepts.json`
  + `dashboard.html` + `index.html` (they render the `verified <date>` span); `concepts.py --check` passes
  with 0 calendar warnings.

  **Migration:** none — knowledge-freshness metadata only; nothing in an installed plugin behaves
  differently on `/plugin marketplace update`.

## 0.297.0 — 2026-08-24

### Fixed

- **`context_handoff` was the last comfort-posture block the dashboard serializer did not
  model, so a "Save & apply" silently deleted it** (the v0.61.0 data-loss class that already
  ate `runaway` / `decision_review` / `definition_of_done` and `stream_classify`). `emitYaml()`
  rebuilds the whole `.ravenclaude/comfort-posture.yaml` from `state`, and `context_handoff`
  had no `state` slot, no hydrate parse, and no emit line — so the successor-spawn recipe
  (`spawn:`) and Stop-nudge mode (`mode:`) read by `handoff-nudge.sh` / `handoff-spawn.sh` /
  `context-usage-meter.py` vanished on the next Save.

  It is now round-tripped exactly like `worktree_bound` — modelled in the schema + `state` +
  `emitYaml` + `applyGuardrailConfig`, emitted only when non-default, with **no editable DOM
  control** (so no Gate 132 ratchet raise). `spawn` validates against the union of both readers'
  enums (`copy-paste-only` | `same-host` | `os-terminal`) so a Save preserves whatever the owner
  set rather than canonicalizing. **Gate 35** gained emit + hydrate coverage, a spawn-only
  round-trip test (the live-posture shape), and a must-fail mutant that strips the
  `context_handoff:` emit.

  **Migration:** none — `context_handoff` defaults absent (⇒ no handoff behavior), so an
  untouched posture is byte-identical on `/plugin marketplace update`; the only change is that a
  dashboard Save now preserves the block instead of dropping it.

## 0.280.0 — 2026-08-18

### Fixed

- **`git push` delete-detection matched tokens belonging to other commands.**
  `_is_dangerous_git_push_delete` ran its flag regexes over the **whole command
  string** as soon as any `git push` appeared in it, so a short delete flag on an
  unrelated command in the same line was read as `git push --delete` and the push was
  blocked.

  control (2026-08-18): an ordinary `git push -u origin <branch>`, followed in the same
  line by a `tr` carrying a short delete flag, was **DENIED** as
  `git-push-remote-branch-delete`. Nothing was being deleted. Removing the `tr` from
  that same line allowed it — so the trigger was the unrelated token, not the push.
  Observed live: it blocked a real push during this session's work.

  The predicate's own comment said *"-d is the ONLY push short flag containing a
  lowercase d"*. That is true of `git push` and irrelevant — the regex was never
  looking only at `git push`. The flag and refspec searches are now scoped to the
  `git push` **segment**.

  ⛔ **Third instance of one defect class**, after `srm.force-push` (v0.242.0) and
  `sce.curl-pipe-shell` (v0.244.0): a rule that matches on a token, applied to a string
  wider than the command that token belongs to. The repo's own record says *"when you
  fix a pattern, enumerate every instance of that pattern before you close it"* — this
  one was missed both times, because **nothing exercised the predicate**.

  ⛔ **The remedy is not portable across the siblings.** Splitting on the shell
  separators is correct *here*, because a push flag never crosses one.
  `curl-pipe-shell` deliberately must **not** exclude the pipe — a fetch piped into an
  interpreter is precisely what it hunts. Same class, opposite correct fix.

### Gates

- **Gate 231** — 12 assertions over the extracted predicate. Every allow case is paired
  with a deny case, including a deletion in a **later** segment, so a "fix" that only
  inspected the first segment cannot pass. The false-negative half is the load-bearing
  one: a predicate that never fires would satisfy every "did it stop crying wolf?"
  assertion. The must-fail half restores the whole-string match and the two
  false-positive rows go red. The gate refuses rather than passing green if the
  extraction anchor moves.

### Migration

None in the permissive direction. Every genuine deletion still denies — `--delete`, a
bare or bundled short flag, and the empty-source colon refspec — including when it
appears in a later segment of a compound command. What stops being denied is an
ordinary push that merely shares a command line with some other tool's delete flag.

## 0.279.0 — 2026-08-18

### Fixed

- **The session handoff wrote a command that launches a different agent.** Both seed writers defaulted to the grok launch command and overrode it only for hosts they recognised **by name**, so every host they did not recognise inherited it — silently, onto disk, at `.ravenclaude/runs/<id>/handoff-seed.txt`, where the next person pastes it without a second thought.

  - `scripts/context-handoff.py` — `seed_text()`'s fall-through **default** was the grok seed, so `claude-code`, `codex`, `unknown` and `""` all received it. `detect_host()` had resolved `claude-code` correctly all along; only the seed selector lacked the branch, and its default was the most host-specific option rather than the most neutral.
  - `scripts/handoff-spawn.sh` — `seed=grok "…"` was assigned ~90 lines **before** the host was resolved, and only `chat` / `cli` / (`unknown` + `TERM_PROGRAM=vscode`) overrode it. Its refusal guard was scoped to `chat|cli`, so it could not see the case it most needed to catch: an unrecognised host inheriting the default.

  Measured 2026-08-18 against the shipped 0.271.4 copy: `--host claude-code` in a plain terminal emitted `grok "…"`, while the **same** invocation under `TERM_PROGRAM=vscode` emitted a safe comment. ⛔ That asymmetry is why the defect reads as absent if you sample only a VS Code session — and it is why Gate 230 drives `env -i` rather than inheriting the runner's environment.

  The live path was worse than the printed one: `handoff-spawn.sh`'s launch-successor writer ended in `exec $seed`, so an unrecognised host got a script that **launches** the wrong agent, not merely a suggestion to. That branch now writes an `exit 0` launcher — no proven recipe means launch nothing, because a successor a human starts beats one the script guesses at.

  Both writers are now host-keyed: `grok` keeps the grok seed, `chat`/`cli` keep theirs, `claude-code` gets `claude`, and everything else — `codex`, `unknown`, and any host added later — degrades to *"read the handoff and continue"*, which is correct on every host including ones that do not exist yet.

### Added

- **`claude-code` is a recognised host in `handoff-spawn.sh`** — in `normalize_host()` (`claude-code|claude|claudecode`), in `detect_origin_host()` (via `CLAUDECODE` / `CLAUDE_CODE_ENTRYPOINT`, the same markers `context-handoff.py` already keyed on), and as its own copy-paste recipe. Previously `--host claude-code` reported `host=unknown`, which was the honest symptom of the bug above rather than a cosmetic mislabel.

- **The refusal guard now has teeth on the case that mattered.** It was `chat|cli`-scoped; it is now `host != grok`, so a grok launch cannot reach `claude-code`, `codex`, `unknown`, or any future host.

### Gates

- **Gate 230** (`hooks/tests/test-gate227-handoff-seed-host.sh`) — 18 assertions pinning the seed each writer selects per host, across both writers, under `env -i`. **Positive control built in:** two rows assert grok *does* get the grok seed, because a blanket "no grok anywhere" suite would pass identically against a writer that emitted nothing. The must-fail half rebuilds the pre-fix file in all four parts and requires the assertions to go red. ⛔ **Honest scope:** it pins the seed value on the copy-paste/dry-run surface; it does not drive a live spawn, since that would start a real interactive agent.
## 0.278.0 — 2026-08-18

### Fixed

- **⛔ The worktree guard called every in-tree write "foreign", so worktree isolation
  did not exist.** `_wg_is_foreign` returned on the **first** worktree whose path
  prefixed the target — and this repo's own convention puts worktrees at
  `<primary>/.claude/worktrees/<name>` ("worktrees UNDER the repo, never `/tmp`"),
  which makes the primary checkout an **ancestor of every linked worktree**. So from
  inside any worktree, writing your own files matched the primary and read as foreign.

  control (2026-08-18): cwd = a linked worktree, target = a file **inside that same
  worktree** → `FOREIGN — ... not <that worktree>`, naming the very tree the file
  lives in. Positive control on the same harness: a genuine sibling → FOREIGN, a
  `/tmp` path → silent, so the own-tree reading was real and not a dead probe.

  Ownership is now the **longest** matching worktree prefix. It had been set to `warn`
  on main with a comment saying the deadlock left *"no legal place to edit"* — the
  guard had been switched off rather than fixed, so the isolation it advertised was
  not there.

  ⛔ **`worktree_bound` deliberately stays `warn` in this release** (owner decision).
  Hooks execute from the **installed plugin cache**, so flipping to `block` in the
  same change that fixes the predicate would re-arm the *old, buggy* guard for any
  session whose cache is stale — re-creating the exact deadlock this removes. That
  was observed while building this. Flip to `block` **after**
  `/plugin marketplace update ravenclaude` has refreshed every live session's cache.
  The knob only decides whether a correct verdict blocks or warns; Gate 229 pins the
  verdict itself either way.

  ⛔ **A suppressed message is not a negative result.** The guard throttles a repeated
  nudge per (path key, session, kind); reading that silence as "the predicate stopped
  firing" produced one false *regression* report while this was being fixed. Gate 229
  drives a fresh guard home per probe for exactly that reason.

### Added

- **Session lease — one worktree, one session.** CONTENTION only ever *nudged*: it
  reported that another session was in the tree and let both proceed. The lease is the
  enforcement — a session claims a worktree, and another session's mutating ops there
  are **denied**, naming the holder and how long it has been idle.

- **The stale fallback, which is what makes enforcement safe.** A lock with no expiry
  strands the tree the moment a session crashes or is closed, and a lock nobody can
  exit is one people route around. After `worktree_lease_idle_minutes` (default **20**)
  with no activity, the next session **takes over** — auto-committing the holder's work
  first as a `wip(worktree-lease)` checkpoint so the takeover cannot lose it. Tracked
  **and** untracked (owner ruling; `.gitignore` still applies).

  ⛔ **It refuses on the anchor branch.** `main`/`master` is the shared anchor here, so
  a stale lease there is reported rather than auto-committed — the guard must not
  create the mess it exists to prevent.

- **`worktree_lease: on|warn|off` and `worktree_lease_idle_minutes: N`**, deliberately
  **independent** of the other two knobs: `worktree_guard: off` + `worktree_bound: off`
  used to short-circuit before the lease clause could run, so silencing the two nudges
  would have silently removed cross-session exclusion with nothing saying so.

### Gates

- **Gate 229** — 18 assertions. Every deny is paired with a case that must **not** deny
  (a guard that denies everything passes any "did it deny?" test), and the takeover case
  asserts the holder's work **survived**, including the untracked file. Two vacuity
  controls: the fixture is proven to have the nested layout (without it the defect
  cannot appear at all), and each ownership probe uses a fresh guard home. The must-fail
  half restores first-prefix ownership and **8** assertions go red.

### Migration

**`worktree_bound` stays `warn`.** The false positives stop — that is the fix — but a
correct FOREIGN verdict still only warns. Flip to `block` once caches are refreshed
(`RC_WORKTREE_BOUND_ACK=1` remains the per-command escape).

The lease is **on by default**: a second session writing into a worktree another
session is actively using is denied until the holder has been idle 20 minutes. Set
`worktree_lease: off` to disable, or `warn` to report without blocking.

⛔ **Hooks run from the installed plugin cache, so nothing here takes effect until
`/plugin marketplace update ravenclaude`.** Until that refresh a stale session keeps
the old predicate — which is exactly why `worktree_bound` is NOT flipped to `block` in
the same change: the new knob plus the old predicate is the deadlock, not the fix.
Refresh first, then flip.

⛔ **The lease is on and enforcing**, so it reaches a session the moment its cache
refreshes. If two sessions legitimately share one worktree today, set
`worktree_lease: warn` before refreshing, or expect the latecomer to be denied until
the holder has been idle 20 minutes.

## 0.277.0 — 2026-08-18

### Fixed

- **`ravenclaude update` reported success over a checkout that had not moved.** It ran
  `git pull --ff-only >/dev/null 2>&1` and then printed **"up to date."** unconditionally, so the
  commonest stall produced a green line over stale content — and discarded the one message that
  would have explained it. The stall is structural, not user error: the marketplace clone is *both*
  the thing you pull into *and* the live runtime surface, so `.ravenclaude/comfort-posture.yaml` and
  `.claude/settings.json` are **tracked** files that normal use rewrites and upstream also edits,
  which is exactly what `--ff-only` refuses to overwrite. The real git error, the dirty-file list,
  and a keep-your-tuning remedy are now printed, and the closing line says **NOT up to date**.

- **⛔ The exit status was the half a human cannot see, and it had the same bug.**
  `serve-dashboards.py` derives the dashboard's success flag from `proc.returncode == 0`, so the
  Update button reported `ok: true` for a run that did not update. `update` now exits non-zero when
  a pull was **attempted and failed**. Prose honesty that stops at the terminal is half a fix.

- **A failure that never happened is no longer announced.** When `$MARKET` is not a git checkout,
  nothing is attempted — the closing line used to say *"the pull above failed"* anyway. That is the
  same dishonesty pointed the other way, and it now reports the honest case (and exits **0**).

- **git's stderr is redacted before it is echoed.** git names the remote in its error text, so a
  clone whose origin carries a token would have had that token printed by the very line added to
  improve diagnostics. URL-embedded credentials only — not a general secret scanner, and it does not
  claim to be.

### Changed

- **The `rc` function and the suggested alias chain with `;`, not `&&`.** With `update` now exiting
  non-zero on a failed pull, `&&` would stop launching Copilot for precisely the people hitting the
  stall — their own posture tuning. A stale checkout is still a working checkout. The detector for
  the *legacy* `&&` alias in `~/.bashrc` deliberately still matches `&&`, since its job is to find
  old installs.

### Gates

- **Gate 228** (`hooks/tests/test-gate228-update-pull-report.sh`) — the fix shipped without one, which
  is the shape this repo's record says regresses. The pull step was extracted into
  `_rc_pull_marketplace()` so it can be driven without `regen` and the launcher self-heal; the gate
  extracts that function and **refuses rather than passing green** if the anchor moves. 13 assertions
  over three outcomes (pulled / attempted-and-failed / not-a-checkout) plus credential redaction,
  asserting the **return code** as well as the text, with two vacuity controls — the clone is proven
  *behind* before the success case, and the redaction case is proven to have produced a report. The
  must-fail half rebuilds the swallow-output/always-succeed shape and 6 assertions go red.

### Migration

`ravenclaude update` now exits non-zero when a pull was attempted and failed (it still exits 0 when
there was nothing to pull). If you chain it with `&&`, switch to `;` — `ravenclaude setup` writes the
`;` form from this version on, but an alias already in your `~/.bashrc` is not rewritten.

## 0.276.0 — 2026-08-18
### Added

- **Merged forward from `feat/vacuity-guard-grep-quiet`.** The gate below was authored as **Gate 223** and renumbered to **227** on merge: `main` landed its own Gate 223 (parallelism posture) concurrently, 224 is claimed by `feat/assumption-claiming-layer`, and 225/226 were already taken. The test file keeps its original `test-gate223-probe-validity.sh` name — renaming it would be a `git mv` under the plugin's own hooks directory, which `xc.tribunal-self-disable` hard-denies pre-LLM, and the gate's grep discipline keys on the script basename rather than the number.

- **`guard-probe-validity.sh` — a twelfth `PreToolUse(Bash)` gate, carrying exactly ONE rule: `grep -v` used in QUIET MODE.** The existing eleven gates each answer *is this dangerous / in the right place / premise-settled / portable?* **None answers *"will this command answer the question the agent thinks it is answering?"*** This is the first that does.

  Outside quiet mode, `grep -v` exits 0 when a line was **selected** — "something does NOT match". In quiet mode that guarantee is lost: the status starts reporting whether the **pattern is absent**. The two disagree on any input holding **both** a matching and a non-matching line, and **the disagreement reads as clean**. Quiet is entered **two** ways, and the second is the one nobody expects: a `-q`/`--quiet`/`--silent` flag (possibly buried in a bundled cluster — `-qv`, `-vq`, `-rqv`, `-qvE`), **or stdout redirected to `/dev/null` specifically**, with no `-q` anywhere. Measured in the agent's own Bash-tool shell (ugrep 7.5.0, genuinely mixed fixture): `grep -v alpha mixed.txt >/dev/null` → **rc=1**, where BSD/GNU give 0.

  **ONE rule, not three, because the corpus said so.** The detector was run over **17,410 distinct real agent-issued Bash commands** (43 transcripts). This rule fires **once**, and that catch was real and consequential — a PR `ALL_GREEN` verdict decided by `grep -qvE`. The two sibling candidates measured on the same corpus were **rejected and must not be added**: `find … -exec test` fired **0 times, ever**, and `$?`-after-a-pipe fired 13 times at an **85 % false-positive rate** — and its dominant false-positive idiom is *this repo's own standard hook-testing idiom*, so it would have warned on the fixtures written to prove it. A channel that is wrong 85 % of the time is how an agent learns to stop reading the channel.

### Design constraints worth not re-litigating

- **⛔ WARN-only, with no host probe — and the hook's header says so at length so a future maintainer does not "improve" it back into unreachability.** Two earlier designs decided WARN-vs-DENY from a host probe. Both were overturned on a mechanical fact: **the probe would run in the hook's shell; the judged command runs in the agent's shell, and they are not the same `grep`.** Measured on one machine at one instant — the Bash tool resolves `grep` to a shell function execing under `ARGV0=ugrep` (7.5.0, **inverts**), while a hook subprocess (`/bin/sh -c`, or even `env -i /bin/bash -c`) resolves BSD grep 2.6.0 (**does not**). So on the exact machine where the defect is documented, a hook-side probe answers *"this host is fine"* and the DENY branch is unreachable, on every host, forever — **and it is testable-green**, since a test that fakes the probe "proves" a branch that is dead in the live path. That is a green test over a dead rule: precisely the vacuity class this gate is named after. Caching does not rescue it either — the same shell delegates to BSD grep on any `-Z`/`--null`/`-z`/`-@` argument, so `grep --version` and `grep --null --version` print **different products from the same word in the same shell** (same cache key, opposite answer), and computing the key costs ~7.6 ms against the ~4.1 ms probe it caches. Warning unconditionally is correct advice everywhere, costs nothing at ~1-in-17,410, and removes the whole wrong-shell failure mode **by construction rather than by care**. There is no exit-2 path in the file; an EXIT trap armed before anything else pins every error path to 0.
- **⛔ The 5-rule prototype was NOT promoted.** It shipped two rules both prior plans explicitly excluded, and promoting it would have multiplied warn volume 11× (14 → 157) *entirely* from those two. The one rule was written fresh.

- **Gate 227 — and its must-fail half is an exit-code contract, not a mutant.** The prototype's runner exited **0 whether 11 assertions failed or none did** — a gate green forever, this repo's own documented Gate-184 shape one layer down. So `test-gate223-probe-validity.sh` exits 1 on any failure **and** ships `--prove-nonzero`, which routes a deliberately false claim through the real assertion path; Gate 227 asserts `must_fail` on that invocation, so *"the harness reddens"* is re-proved on every CI run instead of being a claim in a commit message. Per-rule teeth are two in-test mutants that neuter the quiet detector and the invert detector and require every fire case to go silent — without them, "fires" would print identically if the hook simply warned on anything containing the word `grep`.

  **⛔ The fixture is asserted MIXED.** ugrep and BSD/GNU **agree** unless the input holds both a matching and a non-matching line, so 2 of the 3 plausible fixtures report *"no bug"* and silently prove nothing. Mixedness is a first-class, count-based assertion (`awk 'END{print NR}'` + `grep -c`), never an assumption.

  Registered in all three Gate-195 sites (dispatcher arm, `Supported:` string, main sequence) and proven to run in the full suite by grepping the suite's own output **for the script name on an executed line** — never for the string "Gate 227", because a batched header once made a by-number grep report seven gates unrun that had all executed. Gate numbers **219–221 remain claimed** by unmerged PR #961.

  ⛔ Nothing in the hook, the test, or the gate uses `grep -q -v` — that *is* the defect, and it inverts here. Every assertion is count-based, and the bad forms appear only as command **strings** handed to the hook as data.

- **`probe_validity: off | warn` (default `warn`)** in `.ravenclaude/comfort-posture.yaml`, read with the same minimal `sed` idiom `worktree-guard.sh` uses. There is no `block` value — the hook has no deny path. An **absent posture file is a no-op**, so consumers who never opted in are never surprised.
## 0.273.0 — 2026-08-18

### Changed

- **Parallelism now defaults to MAXIMUM.** `PARALLELISM_DEFAULT` is `{enabled: true, max_workers: 4, unlimited: true}`, and **an absent `parallelism:` block now means maximum**, not "unchanged".

  **Migration — one behavior change, and only one.** A consumer with **no** `parallelism:` block gets maximum fan-out where they previously got the agent's ad-hoc judgment. Every *explicit* setting is unchanged: `enabled: false` is still sequential, `max_workers: N` is still batches of ≤N, `max_workers: unlimited` is still uncapped, scalar `parallelism: on` is still enabled. Nothing breaks — `parallelism` is a behavioral commitment with no enforcement path, so no permission changes and no hook denies anything new; the cost is token spend and concurrency, which is what the conserve-tokens exception bounds. To opt out: `parallelism: off`, or tick **Conserve tokens** in the dashboard.

  The alternative (keep `absent ⇒ unchanged`, re-seed only the dashboard default) was rejected: it reaches only consumers who open the dashboard and press Save, leaving every untouched posture on the old behavior forever — the opposite of the ask.

- **Fixed: the scalar `parallelism: off` was silently ignored.** It fell through every hydration branch. Harmless while the default was OFF; with the default flipped it would have meant the **opposite** of what it reads.

### Added

- **The conserve-tokens exception, with three triggers and one precedence.** Engaged ⇒ the posture is read as `enabled: false` (sequential). No fourth mode.
  1. **Prompt phrase** — per-session, sticky, **both directions** (`conserve tokens` engages; `maximum parallelism` / `stop conserving` releases). Rides the existing `UserPromptSubmit` hook.
  2. **Posture switch** — `conserve_tokens: true`, a new checkbox on the dashboard's Pipeline page. Engage-only.
  3. **Context pressure** — live usage ≥ `conserve_tokens_auto_pct` (default `80`; `0` disables), read from the existing `context-usage-meter.py`, not a second meter.

  `engaged = phrase_override if a phrase fired this session else (posture_switch or context_pressure)`. The phrase wins in both directions (otherwise a phrase-engaged session has no exit short of editing config mid-conversation); the switch is engage-only (otherwise a stale config could silently suppress trigger 3). Engine: `scripts/conserve-tokens.py`.

- **A serial-dispatch detector.** `scripts/parallelism-detector.py`, riding the existing `SubagentStart` hook, groups subagent starts into batches by start-time proximity, counts singles vs parallel batches, and emits at most 3 advisory `warn` events (`rule: serial-dispatch`, empty `path`) into `hook-events.jsonl`. **It never blocks** — a hook can stop an action, it cannot compel one. Its limits ship in its own output: it infers batching from start times, so a single dispatch may be a genuine dependency, and *zero batches means no subagents ran*, not perfect parallelism.

- **A standing SessionStart directive.** The capability banner gains a four-line **PARALLELISM** section stating the resolved mode and the observed serial ratio. Derived labels only (Gate 19).

### Gates

- **Gate 35** extended: the two conserve keys round-trip (emit-when-non-default + hydrate-back), the new default emits **no** block, sequential is written explicitly, and `parallelism: off` hydrates to sequential. Two new must-fail halves (conserve emit stripped; default reverted to OFF).
- **Gate 223** (new): all three conserve triggers, each with a control in the opposite direction, the precedence ordering, and the detector's serial-vs-parallel discrimination — 32 assertions, three must-fail mutants.

## 0.271.5 — 2026-08-17

### Fixed

- **`forge-route.py`'s `layout-allowlist-edit` signal matched PROSE, inverting tiebreak F3.** The detector was `re.compile(r"\.repo-layout\.json|allowed_globs", re.IGNORECASE)` — a bare substring match on a **filename**. So a plan stating the *opposite* of a pre-commitment (*"`.repo-layout.json` needs **no edit** — settled by a bidirectional probe"*) fired the "this plan carries an engineering pre-commitment" signal and was forced to a draft PR.

  That is this repo's own recorded **"source-scan gates match PROSE"** defect, sitting in the router that *enforces* F3 — and F3 exists precisely so a **pure design/analysis plan can land on `main`**. Every analysis plan that merely *discussed* the layout file was denied that path. Found by running the router against a real 153 KB FORGE plan whose definition-of-done explicitly asserts `.repo-layout.json` is **unmodified**.

  The detector is now scoped **per line** and requires all three of: the token, an **edit verb**, and **no negation** on that line. ⛔ **The direction of error is deliberate and documented in-file:** firing wrongly costs a needless draft PR, while *not* firing wrongly lets a stale pre-commitment sit canonically in `main` — the harm F3 was written to prevent. Never widen the negation list to quiet a noisy PR verdict.

### Added

- **Gate 222 — because `forge-route.py --self-test` was registered by NOTHING.** It shipped with fixtures, is cited in the FORGE skill as *"a registered, citable canonical route"*, and **no gate or workflow ever invoked it** (a grep of `scripts/` and `.github/` returned zero hits). The fixtures could have rotted indefinitely with nothing to say so. **The detector fix is only half this change; the registration is the other half.**

  Registered in all three Gate-195 sites (dispatcher arm, `Supported:` string, main sequence) and **proven to run in the full suite by grepping the suite's own output** — the check v0.241.0 skipped, which left Gate 184 unreachable for an entire release while the suite reported green. Assertion count moved **815 → 817**, exactly the two new assertions.

  Ships a **must-fail half** (`scripts/_mutate-forge-route.py`): it reverts the detector in a throwaway copy and requires the two negative fixtures to redden. Without it, *"fixtures OK"* would print identically if the detector had gone **blind** and matched nothing at all — a false-negative detector and a correct one are indistinguishable from the positive fixtures alone. The mutator **refuses to write an unmutated copy** if its anchor text stops matching, because an unmutated copy would pass its own self-test and the gate would report teeth it does not have.

  Gate numbers **219–221 were deliberately skipped** — an in-flight `forge/forms-process-expertise` build claims them, and a collision would redden Gate 195 (number-uniqueness), which masks every later gate in the same CI step.

## 0.271.4 — 2026-08-17

### Fixed

- **`cleanup-worktrees`: a detached-HEAD worktree holding the only copy of a commit is no longer deleted as `clean`.** Every prior state answers *"is there **uncommitted** content here?"*. A detached worktree can be spotless by that measure and still be the one thing holding a commit — `git status` is rightly silent, and `git worktree remove` then makes it unreachable.

  **The reflog does not rescue it.** Controlled: before removal `.git/worktrees/<name>/logs/HEAD` exists; after, it is gone with the admin dir, the commit is contained by **0 refs**, and only `git fsck --unreachable` still finds it (positive control: the same reflog probe returns 2 hits for a reachable SHA, so the zeros are a fact about the subject, not a broken probe). Recovery is `git fsck --lost-found` until gc prunes.

  New **DETACHED** state: `--all` skips it, names the SHA, and prints the one-command rescue `git branch <name> <sha>`; `remove_one` refuses bare and **honours `--force`** (the DIRTY contract, not UNKNOWN's — we can see exactly what is at risk).

  **The discriminator is reachability, not detachment.** Measured: detached-with-own-commits is contained by no ref; detached at a ref tip is contained by `refs/heads/main`; a branch-backed worktree has a symbolic HEAD. Only the first is flagged — flagging every detached worktree would fire constantly on the harmless middle case, and a guard that fires on the harmless case is one that gets ignored on the harmful one.

  Gate 216 covers both directions, including the **no-false-positive** assertion (a reachable detached tree must still read `clean` and still be removed) and a narrow stand-in that strips only the reachability check and confirms the commit-bearing worktree is then destroyed.

## 0.271.3 — 2026-08-17

### Fixed

- **`cleanup-worktrees`: a worktree holding only ignored files is no longer treated as empty.** `git status --porcelain` is **silent on ignored files by design**, so a worktree containing nothing but `.env`, `node_modules/` or a local database produced empty output and classified `clean` — and `--all` removed it. Nothing failed: git ran, against the right tree, exited 0, honoured no misleading config. The probe was simply answering a narrower question ("is anything *tracked* here?") than the caller needed ("is anything here?").

  The `.env` case is the one that hurts: a file is ignored *precisely because* it is not in git, so the rule that hides it from the probe is the same rule that guarantees no other copy exists.

  `worktree-clean.sh` now emits a fourth state, **IGNORED**, and the skill documents it. `--all` skips such a tree and names what it holds; `remove_one` refuses it without `--force` and **honours** `--force` — deliberately the `DIRTY` contract, not the `UNKNOWN` one. The difference is knowledge, not danger: for UNKNOWN we cannot see what would be destroyed, so `--force` is refused; here we can see it and we print it, so `--force` is a considered choice. Collapsing the two would either strand every `node_modules` tree forever or keep deleting `.env` files unexamined.

  Measured before building: a **fresh worktree of this repo shows 0 ignored entries**, so the new state does not fire on every newly created tree (a guard that always fires is a guard that gets switched off), and `--ignored=traditional` collapses a wholly-ignored directory to one line rather than walking it. The extra git call runs **only** when the tree is otherwise a deletion candidate.

  Gate 216 covers it in both directions — including the over-blocking half (`--force` must still remove it, or a safety fix has quietly become a broken tool) and a narrow stand-in that strips **only** the ignored probe and confirms the `.env` worktree is then destroyed.

## 0.271.2 — 2026-08-17

### Fixed

- **`skills/cleanup-worktrees/SKILL.md` no longer prescribes a remedy that does
  nothing, and now documents both causes of `UNKNOWN`.** The entry told the
  reader to "repair it first (`git worktree repair` / `git worktree prune`)".
  Both were **measured to be no-ops on every UNKNOWN shape tested** — a corrupt
  index and a `chmod 000` `.git` were unchanged by either command — so an agent
  or operator following that advice loops indefinitely, which is the pressure
  that produces a manual `rm -rf`. `scripts/worktree-clean.sh` had already
  dropped the advice for that reason; the skill had not.

  It also described only one of the two causes. `UNKNOWN` arises when
  `git status` **fails** (empty stdout, non-zero exit) *and* when `git status`
  **succeeds against an ancestor** — a directory that is not a worktree, or a
  worktree whose `.git` file is missing, where git's discovery walks up and
  reports the parent. Because `.claude/worktrees/` is gitignored the parent
  reports nothing, so that case also comes back empty, with **exit 0**. That is
  the more common shape and the reason a successful `git status` is not by
  itself evidence that anything was inspected.

**Migration:** none — documentation only. Describes behaviour already shipped in
0.271.1; no code changed.

## 0.271.1 — 2026-08-17

### Fixed

- **`scripts/branch-hygiene.sh` no longer aborts the whole sweep when a
  worktree cannot be inspected.** Gate 2 read
  `git -C "$wt" status --porcelain 2>/dev/null | wc -l`. A FAILED `git status`
  — a stale linked worktree whose admin dir under `.git/worktrees/` is gone, a
  corrupt `.git`, git off `PATH`, permission denied — writes nothing and exits
  non-zero. Because the script runs `set -euo pipefail`, that 128 propagates
  through the command substitution and **`set -e` kills the run mid-loop**:
  every later branch goes unexamined and the summary never prints. It now
  captures the exit code separately and HOLDs that one worktree with the real
  reason, so the sweep completes.

  Measured on the same fixture — before: `EXIT=128` after the first bad
  worktree, second branch never reported. After: both branches reported,
  `would delete: 0  held: 2`, `EXIT=0`.

  **Honest severity:** an availability/correctness fix, **not** a data-loss
  fix. Nothing was ever deleted that should not have been — gate 4
  (`git worktree remove` without `--force`, then `git branch -d`) independently
  guards deletion. The reason to fix it anyway is that a sweep which stops
  silently at branch 3 of 30 looks exactly like a sweep that found nothing.

  > **Correction, recorded rather than quietly amended.** The first version of
  > this entry claimed the pipe "yields `0` … so gate 2 PASSED on a worktree it
  > had never inspected", and stamped it *Measured*. That was an **inference**
  > drawn from a true observation (status exits 128 with empty stdout), and it
  > is false under `pipefail`. Controlled both directions: with `pipefail` the
  > substitution aborts at 128; only without it does the pipe yield `0`.
  > Grounding an observation is not grounding an inference drawn from it — see
  > `docs/best-practices/verification-probe-discipline.md`.

**Migration:** none. A worktree that cannot be inspected is now HELD with a
stated reason instead of aborting the sweep. No branch that was previously
retained is now deleted, and no branch that was previously deleted is now
retained.

## 0.271.0 — 2026-08-14

### Added

- **Host-paired `/handoff` spawn.** `--host grok|cli|chat` (aliases `copilot-cli` /
  `copilot-chat`). Chat writes `chat-resume.md` and prints Cmd+N / New Chat +
  paste — never `grok`. CLI prints interactive `copilot`. Grok positional seed
  is unchanged. `--host` wins; never infer Chat from `TERM_PROGRAM=vscode`.
- Gate **215** (Chat/CLI must not emit `grok`; `--must-fail-chat-grok` teeth).
  Gate 213 Grok teeth kept.

### Not claimed

- Copilot Chat Stop/nudge fire (Preview hooks). Chat path is skill-invoke.
- URI `prompt=` / `query` starting a **new** Chat session and prefilling.
- Chat is not a protected install host. No `copilot-chat` marketplace column.
- Origin `context_handoff` stays off.

## 0.270.1 — 2026-08-14

### Fixed

- **FORGE G8 publishes the host session `plan.md`.** Grok's `exit_plan_mode` reads
  `~/.grok/sessions/<encoded-cwd>/<id>/plan.md`, not the Sága run-dir file. A
  `/forge` that called `ExitPlanMode` without that copy opened **No plan written
  yet**. New `scripts/forge-publish-session-plan.sh` copies the run-dir plan
  (size-matched, refuse empty) before exit. Honest skip when there is no Grok
  session tree.

## 0.270.0 — 2026-08-14

### Added

- Host-keyed substrate tier map (`knowledge/substrate-tier-map.json`) so FORGE / dispatch / classifier / Thing seats resolve haiku/sonnet/opus to live host SKUs. Grok `fast`/`balanced` share `grok-4.5` and diverge on effort + perspective (CLI probe: `grok-build-0.1` is not a selectable id). `RC_BASELINE.tools` 26 → 27 (`load-substrate-tier-map.py`; the JS twin is not counted — `_scan_scripts` is `*.py` only).

## 0.269.0 — 2026-08-14

### Added

- **Same-host spawn.** `context_handoff.spawn: same-host` opens a **new
  terminal in the same app** as the originating session. `TERM_PROGRAM=vscode`
  → new VS Code integrated terminal (never Terminal.app). Cursor is the same
  shape. Explicit `os-terminal` still means Terminal.app.
- **Successor handshake.** SessionStart (`startup`) writes
  `successor-ack.json`. The originating `rc handoff` waits and prints
  `SUCCESSOR_ACK` so the original session knows the successor has begun.
  The original session then **stops**; it cannot `/quit` the TUI.
- Gate **214** (successor-ack). `RC_BASELINE.hooks` 34 → 35; tools 25 → 26.

### Not claimed

- VS Code has no CLI to create an integrated terminal and run a command
  (`code --help`, 2026-08-14). Same-host uses Accessibility keystrokes
  (Ctrl+Shift+`) and falls back to copy-paste if that fails.
- The originating Grok TUI cannot be closed from inside the agent.

## 0.268.0 — 2026-08-14

### Added

- **FOREIGN-TREE** clause in `hooks/worktree-guard.sh` plus `worktree_bound: off|warn|block`
  (default **block** when absent). A Write/Edit/MultiEdit or mutating `git -C` /
  `GIT_WORK_TREE` whose target is a **sibling worktree** is denied. Independent of
  `worktree_guard` (still default warn for two-writers-one-tree). Escape:
  `RC_WORKTREE_BOUND_ACK=1`. T8–T16 + Gate 140 F3/P4/MF2.
- **Lane stamp + one-window operator default.** `rcwt new` writes
  `.ravenclaude/lane.md`, opens `code -n <worktree>`, and pins
  `chat.useCustomizationsInParentRepositories: false`. Templates under
  `templates/worktree-lane/`. `RC_BASELINE.templates` 23 → 24 (top-level
  dir only; files inside that pack do not increment).
- **`knowledge/copilot-chat-customization.md`** — VS Code Copilot Chat is a
  distinct product from Copilot CLI.

### Changed

- `worktree_guard: off` no longer short-circuits FOREIGN-TREE (T13).
- Isolate-parallel best-practice gained a dated host table (Chat ≠ CLI).
- Codex consumers must `/hooks` after this hook-script change (hash-trust).

### Not claimed

- VS Code Copilot Chat is **not** protected. Preview hook fire and sibling
  built-in Write stay `[unverified]` until owner probes (CL-19, CL-3).
  Do not read this bump as Chat enforcement.

## 0.267.0 — 2026-08-14

### Added

- **WebFetch result quarantine.** New PostToolUse hook `sanitize-webfetch-output.sh`
  (matcher `WebFetch` only) rewrites the fetched body via
  `hookSpecificOutput.updatedToolOutput` after `sanitize-webfetch-body.py`. The
  model no longer has to remember the webfetch-hardening skill contract for this
  channel. **Fail-open** on parse/IO/sanitizer errors. Does **not** match
  `mcp__.*` (accepted-limit: product-shaped default change). House Rule 3: this
  rewrites every WebFetch result a consumer's agent sees; fail-open is the
  default-break mitigator. `RC_BASELINE.hooks` 33 → 34.

## 0.266.0 — 2026-08-14

### Added

- **Session-context handoff** (`/handoff`, skill `session-handoff`). A Grok-first
  preventive quality reset: write a host-agnostic brief into the existing
  `.ravenclaude/runs/<task-id>/` contract and continue in a **fresh** interactive
  TUI (`grok "<prompt>"`). Not `/fork`, not `grok -p`, not compacted mush.
- **Stop-hook nudge** (`handoff-nudge.sh`) — opt-in (`context_handoff.mode: nag`).
  Live meter is `updates.jsonl` `params._meta.totalTokens`. Default **off**.
  Soft threshold default 70, always below auto-compact (~85).
- **`rc handoff`** — always prints the copy-paste resume command. OS-terminal
  spawn is owner-flagged (`context_handoff.spawn: os-terminal`) and unverified
  until a human enables it and a window actually opens.
- Gates **212** (nudge, derived-values-only + leak teeth) and **213** (spawn,
  `--must-fail-headless`).

### Not claimed

- Other-host auto-spawn adapters. Compact-anchor is unchanged. Window-open from
  a VS Code-family TTY was inventoried, not proven.

## 0.265.0 — 2026-08-14

### Added

- **`scripts/resolve-plugin-root.sh`.** Prints the `ravenclaude-core` plugin root only when
  `forge-route.py`, `forge-worktree.sh`, and `premise-gate.py` are all present. Works with
  `$CLAUDE_PLUGIN_ROOT` set **or** unset (skill-symlink walk, invoke-by-path, `rc`,
  `$RAVENCLAUDE_MARKET`). A partial set is exit 2 — never a "routing exists,
  premise/worktree do not" split. `--self-test` ships six fixtures. Gate 211.

### Changed

- **FORGE operational citations** (`skills/forge-pipeline/SKILL.md` §0.4,
  `commands/forge.md`, `reference/premise-gate.md`) resolve helpers via
  `$FORGE_PLUGIN_ROOT` after the resolver runs. `${CLAUDE_PLUGIN_ROOT}` remains
  the Claude Code equivalent, not a requirement.
- **`bin/rc`** gained `forge-worktree` / `forge-route` / `premise-gate` /
  `classify-claim` verbs (convenience; not the close).

### Not claimed

- VS Code Copilot Chat is not a first-class RavenClaude host. No new
  `host-support.json` row.

## 0.264.0 — 2026-08-14

### Fixed

- **MH-40 leftover in generated dashboard JS.** The Settings `dashboard_autostart`
  control shipped in v0.216.0; CLAUDE.md was corrected; the generator kept
  emitting "No DOM control ships with it" into `dashboard.html` and `index.html`.
  Gate 210 denylists that shipping-state lie.

## 0.263.0 — 2026-08-14

### Changed

- **Packaging move (Gate 187 `_DEFERRED_PACKAGING` emptied).** `premise-gate.py`,
  `classify_claim.py`, and `check-design-schema.py` now ship at
  `plugins/ravenclaude-core/scripts/`. Marketplace-root `scripts/` keeps thin shims so
  `python3 scripts/premise-gate.py` (audit-gates, existing citations) still works.
  FORGE / design-clone / brand-extraction operational citations now point at the
  shipped `${CLAUDE_PLUGIN_ROOT}/scripts/…` (or in-plugin relative) path.

## 0.262.0 — 2026-08-14

### Fixed

- **MH-28 leftover call sites.** `init-agent-ready`'s consumer `AGENTS.md.template` still claimed
  Cursor / Codex / Aider / Copilot / Windsurf all read `AGENTS.md` natively (false for Aider) —
  the command's summary was corrected in v0.222.1, the file it *writes* was not. The
  `external-agent-onboarding` skill still said "the one doc every supported host reads is
  AGENTS.md" and lumped Cursor (hooks **are** wired) with Aider / Devin Desktop (not wired).
  Both now point at `knowledge/host-support.json` and carry per-row provenance markers.

### Added

- **Gate 208 — host-capability citation lint + adapter round-trip (P17).** Uncited
  host+supported/natively claims on generator output / `knowledge/` / the root `AGENTS.md`
  table fail the build (exit 2) when a `host-support.json` cell exists to gate against;
  free-form `docs/` stays advisory. Adapter deny + reason must survive translation
  (generalizing Gate 167 / the v0.250.0 reason-loss regression); a mutant that drops
  the reason is exit 2. Gate 154 now also rejects a generated manifest that advertises
  slash commands on a host the map says has none (MH-27).

## 0.261.0 — 2026-08-14

### Added

- **Behavioral canary at the end of every `--host` install (Gate 207, advisory).**
  Each host lane now fires the host's real adapter / shim with a planted marker
  and confirms the marker wrote — not a files-exist check (P16, generalizing
  Gate 167). A miss WARNS and the install continues (D4: advisory first, not a
  hard onboarding bar). Live-host behavior stays owner-verified (M10).
- **Per-host `activation_gate` on `knowledge/host-support.json`** (`hash_trust` |
  `version_floor` | `none`), pinned by Gate 154 in the same commit. Codex is
  `hash_trust` (MH-17); Copilot is `version_floor` (MH-23).
- **Shared `_rc_rearm_notice` helper** consumed at install / update / status, so
  the Codex hash-trust and Copilot version-floor notices are one abstraction
  instead of per-host copies (P18 silent-disarm).

## 0.260.0 — 2026-08-14

### Changed

- Dropped hand-maintained artifact-count literals from the plugin description (D1). The roster enumerates itself (`agents (a, b, c)` not `15 specialists, 53 skills`); Gate 206 forbids the digit.

**Migration:** catalog text only — `/plugin marketplace update` shows the shorter description. No hook, skill, or runtime change. Derived counts (`| Skills | 53 |`, `ships **N plugins**`) stay and remain self-healed.

## 0.259.0 — 2026-08-14

### Added

- **Contract-provenance check on `claim-grounding-lint.sh` (PR 9 / P15).** The
  existing advisory PostToolUse hook now has a second, independent scan over the
  same knowledge/** + docs/** markdown: a capability/contract claim about another
  system ("X does not support Y", "Z is supported", "W has no public API") with
  no inline provenance marker nudges the author. It does **not** verify the
  claim — only whether it is marked. Exit 0 always. Honor `[docs-verified
  <date>]`, `[unverified]`, `[verify-at-use]`, a bare ISO date, and the existing
  `claim-lint-ok` escape. Reuses the hook's single stdin/arg parse (no second
  read). Gate 34 extended (no new gate number) with fires-on-bad / silent-on-good
  / suppression-honored / stdin-reuse teeth; registered in both regions.

## 0.253.1 — 2026-08-13

### Fixed

- **The Copilot version floor went silently unverified on a build-qualified version.**
  `copilot_version_check` (`scripts/ravenclaude`) extracted the version by splitting the
  `copilot --version` line into whitespace-delimited tokens and requiring a **whole** token to be
  exactly `x.y.z`. A four-component version such as `1.0.52.3` therefore matched **nothing**, and
  the check reported `could not parse a version` — so a copilot **comfortably above** the 1.0.52
  safety floor was treated as unverified. Below that floor a sub-agent's tool calls are not hooked
  at all, which is the whole reason the floor exists, and the parser could reach the unverified
  state on a compliant install. Now the first `x.y.z` token is matched as a **substring**
  (`grep -Eo`, never `grep -P` — BSD/macOS grep exits 2 on `-P`, which reads as no-match), so
  `1.0.52.3` → `1.0.52`, `v1.0.75-beta.1` → `1.0.75`, `copilot@1.0.52 (2026-05-23)` → `1.0.52`.
  POSIX ERE is leftmost-longest and `[0-9]+` cannot cross a `.`, so a four-component string yields
  its first three components rather than a truncated or greedy match.
- **A parse failure now says what it saw and what it needed.** The old one-line
  `could not parse a version … floor unverified` named neither the raw output nor the expected
  shape, so an operator could not tell a nightly build from a broken shim without re-running
  `copilot --version` by hand. The diagnostic now prints the raw line (control-stripped and capped
  at 200 chars so a garbled version cannot scramble the terminal), the expected `x.y.z` format, the
  required floor, and the consequence. **It still returns 0** — owner ruling 2026-08-13: make the
  message clear, do *not* make it exit non-zero. Gate 157 pins all three unparseable paths at
  exit 0 because an earlier revision of this same check aborted `ravenclaude status` mid-run, and a
  version check that kills the installer is strictly worse than no version check.

### Changed

- **Gate 157: 10 → 18 assertions.** The gate previously grepped only for the literal string
  `could not parse a version`, which the pre-fix one-liner satisfied — so the diagnostic's content
  and the build-qualified parse were **ungated**, and a regression dropping either would have
  stayed green. It now asserts the raw output, the expected format, the required floor, the
  `(no output)` rendering, and the four-component / prerelease parses, plus a **third teeth half**
  that drops `-o` from the extractor and requires the build-qualified assertion to fail. Verified
  bidirectionally: the extended gate scores 18/0 against the fix and 11/7 against the pre-fix
  parser.

## 0.253.0 — 2026-08-13

> **Backfilled 2026-08-13, after the fact.** This release shipped in PR #890 (`e56b1261`) without a
> CHANGELOG entry, leaving a version gap between `0.253.1` and `0.252.0`. Reconstructed from that
> squash commit's five phase messages and the `CLAUDE.md` milestone — **not** written by the author of
> the change. Treat `CLAUDE.md` § "`design-clone`" and the commit itself as authoritative if they
> disagree with anything here.

### Added

- **`design-clone` skill** (`skills/design-clone/`) — the capture-and-apply contract for mimicking a
  site's design *schema*, not just its tokens. `apply_schema.py` carries a **hard structural no-read
  identity invariant**: `apply()` never reads the reference's `logos[]` or `palette`, and a
  shadow/border color is neutralized to a target token — so the reference's identity is unreachable by
  construction rather than by policy, with `flag_identity_risks` as the advisory second layer.
  `sanitizers.py` adds strict `css_length` / `css_shadow` / `css_number` allowlists that
  **reject-on-unknown with no partial salvage**.
- **Design-schema contract** — `schemas/design-schema.schema.json` (Draft-07) plus the stdlib
  `scripts/check-design-schema.py` validator (`--self-test`, named per-field errors).
- **Five design-schema collectors in `brand-extraction`** (`extract_brand.py`) — spacing scale, type
  scale, grid, elevation and component recipes, emitted as a schema-valid `design-schema.json`
  alongside the existing brand kit. **Every dimension is stamped `capture_method: "static"`**: static
  parsing cannot resolve the cascade or computed styles, so the schema is a seed, never fidelity.
- **Gates 193 and 194** — 193 covers the collectors (7 per-collector must-fail mutants + a
  byte-identical regression proof that the existing brand kit is unchanged); 194 covers the apply path
  with **bidirectional** teeth: a legitimate `8px` / `box-shadow` / `1200px` must survive verbatim
  **and** a hostile `url(javascript:)` / `expression()` / exfil must be dropped whole. The
  false-negative half is load-bearing — a sanitizer that dropped everything would otherwise ship an
  empty stylesheet green.

### Changed

- **`visual-feedback-loop` gained a render-compare pair** (`driver.py`): an offline structural
  design-schema diff — the **floor**, a "declares the same design system" sanity check that is
  deliberately never called fidelity — and a browser-captured `ssim_score` gate, the actual fidelity
  verifier. When ssim is absent the driver degrades **loudly** ("visual fidelity not verified — no
  browser tool") rather than silently passing. Folded into Gate 100 (+3 must-fail mutants) rather than
  taking a new gate number.
- **Design-schema mimicry priors** added to the two existing `web-design` agents
  (`visual-designer`, `frontend-implementer`) — body-only, no new agent, so the ~15K
  agent-description budget is untouched. `web-design` bumped 0.15.0 → 0.16.0 alongside.

### Fixed

- **`_fetch` was not SSRF-bounded.** Now **http(s)-only** (drops `FileHandler`/`FTPHandler`), blocks
  private / loopback / cloud-metadata destinations, and **re-validates after redirects** — so a
  `file://` or `169.254.169.254` sub-resource is refused rather than followed.
- **`ssim_score` is domain-clamped to `[0,1]`**, so a page-controllable `5.0` or `NaN` can never fake
  a pass. The same clamp closes an inherited hole in `_gate_lighthouse`.

### Security

- **The custom-property emit is now sanitizer-gated**, so a `url()` beacon can no longer reach
  `brand.css` via a `<link>`-ed stylesheet.

  **This has a consumer-visible side effect, named honestly:** a value that is not *wholly* a matched
  color / length / number / shadow is **dropped**. That catches the hostile beacon (the point) **and**
  a legitimate complex declaration — `linear-gradient(...)`, a multi-value shorthand, an `!important`
  — which no longer round-trips into `brand.css`. `brand.css` was deliberately excluded from the
  byte-identical regression floor for exactly this reason.

### Known residuals (reviewer-accepted, not merge blockers)

- The `_fetch` SSRF guard is **resolve-then-connect**, so a DNS-rebinding record is a standard TOCTOU
  residual. Closing it fully needs a pinned custom connector; the size cap and timeout bound the blast
  radius, and this is an offline dev tool.
- `getaddrinfo` is not bounded by the fetch timeout (a low-risk DNS hang).
- The `check-design-schema.py` packaging move (marketplace-root → plugin) is deferred.

### Owner disclosures (accepted at merge)

- **Fidelity is browser-gated.** The offline path is a structural sanity check; stdlib cannot compare
  pixels.
- **Trade-dress residual risk is the owner's.** The tool clones functional craft and re-skins with the
  target's brand, but overall look-and-feel is exactly what pixel-faithful mimicry reproduces, and the
  tool cannot detect it. A clean `identity_flags[]` is **not** legal clearance; distinctiveness calls
  route to `security-reviewer`. Not legal advice.

## 0.252.0 — 2026-08-13

### Added

- **Agent issue-triage knowledge** (`knowledge/agent-issue-triage.md`) — how an agent operates
  GitHub Issues as a primary actor (triage, labeling, closing with a reference), grounded in the
  frontier issue-resolution shape (OpenHands / SWE-agent) and GitHub's own API semantics: closing
  keywords cross-reference an issue only from a **default-branch** PR, and `state_reason` is
  silently dropped unless `state` also changes. Pairs with the existing
  `srm.issue-close-without-reference` tribunal anchor rather than adding a new hook.
- **`ravenclaude init-agent-ci`** — a host-agnostic installer subcommand that scaffolds the
  agent-in-CI GitHub protocol set (the `github-protocol-*` workflows, the anti-self-approval
  `agent-approval-check.yml` **plus its companion `check-workflow-hygiene.py`**, and an agent PR
  template) into a consumer's `.github/`. This is the path a **Copilot or Codex** consumer uses to
  adopt what only Claude Code's `/init-agent-ready` reached before. Opt-in and non-destructive
  (never overwrites without `--force`; `--only <list>` cherry-picks). Surfaced in `ravenclaude
  status`, the root `AGENTS.md`, and the generated `copilot/AGENTS.md`.
- **Gate 192** (`audit-gates.sh`) — proves the `init-agent-ci` scaffold is **runnable**, not merely
  present: every copied workflow's local script dependency must resolve on disk (catching the
  "green-but-broken" scaffold where the hygiene workflow's companion `.py` is missing), and a
  pre-existing target is never overwritten without `--force`. Both invariants carry must-fail
  mutants, and the gate executes a real scaffold so a future bash-4-ism fails under `validate-macos`.

### Changed

- **Agent-identity runbook** — `claude-in-ci.md §6` extended into a verified-commit-signing
  operational runbook (three signing paths, minimum GitHub-App permissions, `id-token: write` for
  OIDC only); `agent-pr-identity.md` points at it. Guidance-only — no App-manifest template.
- **Tribunal issue-mutation anchors sharpened** — `srm.issue-close-without-reference` and
  `shr.gh-api-rate-limit-risk` in `concerns-catalog.md` gained resolution + see-also detail.

### Migration

None — additive and opt-in. `init-agent-ci` does nothing until explicitly invoked; nothing
auto-installs into a consumer's `.github/`.

## 0.251.0 — 2026-08-13

### Added

- **Agent-as-primary-GitHub-operator gold-standard pass** (PR #887) — new knowledge
  (`claude-in-ci.md`, `github-mcp-tool-surface.md`, `agent-pr-identity.md`) plus agent-ready
  templates: an `agent-approval-check.yml` anti-self-approval workflow (trusted-approver filter,
  fail-closed quorum), an agent PR template, and a `check-workflow-hygiene.py` scanner with a
  Rule-3 default-`GITHUB_TOKEN` downstream-suppression advisory + a `--self-test`. Gate 191 proves
  the self-test has teeth (a Rule-3-neutered mutant fails it).

## 0.250.0 — 2026-08-12

### Fixed

- **The Gemini and Cursor hook adapters discarded every deny REASON.** Both ran the guard
  with `>/dev/null 2>&1`, so the block still fired (exit 2 propagates / is translated) but the
  explanation was thrown away. Measured with a baseline control: the guard emits **233 bytes**
  of reason directly and **0 bytes** through the adapter. This is the diagnostic-blindness class
  the Copilot adapter fixed in v0.111.0, reintroduced on two hosts by one redirect.
  - The Gemini adapter's own comment said *"stderr already carries the reason"* while the code
    two lines below sent it to `/dev/null`. **A comment is not a control** — the claim and the
    code disagreed for the adapter's entire life and no gate could see the difference.
  - Cursor's fixed-literal JSON verdict is **unchanged on purpose**: Cursor fails OPEN on
    malformed JSON, so interpolating guard stderr into the verdict would convert a noisy reason
    into a silently-allowed command. Stderr goes to the adapter's stderr; the verdict stays byte-fixed.
- **`cleanup-branches.sh` — the remote delete is now SHA-guarded** (plugin copy; the root path is
  a shim). The LOCAL delete was already SHA-guarded via `git update-ref -d … "$_tip"` and the
  REMOTE delete three lines below it was unconditional, so a branch re-pushed with new,
  never-verified commits between verdict and delete was still deleted. Fetch-then-compare — a
  smaller TOCTOU window, not a closed one (the ref-delete API has no compare-and-swap) — and it
  fails SAFE: a mismatch refuses, and can never delete more than predicted.

⛔ Not claimed: this does NOT fix a deny that failed to fire. Both adapters were verified to
block correctly before and after — the earlier report that they degraded DENY→ALLOW was wrong,
and was retracted after driving the hooks rather than counting references to a field name.

## 0.249.0 — 2026-08-12

> **Landed from PR #833.** Renumbered on integration — the non-substrate subset of this review
> already shipped via #835/#845/#846, so what remains here is the tribunal-substrate half
> (`guard-destructive.sh`, `route-decision-review.sh`, `thing-concerns.py`, `thing-seat.sh`,
> `claude-orchestrate.sh`) plus the `summarize_permissions` precedence fix.

Security + robustness fixes from the autonomous three-panel repo review (find →
adversarially verify → analyze → tie-break; 31 confirmed findings). Full report +
the design-input items deferred for maintainer decision:
[`docs/reviews/2026-08-05-three-panel-repo-review.md`](../../docs/reviews/2026-08-05-three-panel-repo-review.md).

### Fixed — P0 (security-critical)

- **`scripts/thing-concerns.py`** — the category-independent `screen_always()` hard-rule/self-disable screen now decodes base64 payloads (shared `_iter_decoded_texts` generator), closing a bypass where a base64-obfuscated `curl|sh` / force-push / self-disable command that classified to `None`/an untoggled category evaded the screen entirely. `evaluate()`'s decode path is unchanged (Gates 14/15/24 green).
- **`hooks/route-decision-review.sh`** — the AskUserQuestion `header` + option `description` now feed both the local high-blast grep and the tribunal engine context (size-capped), so a high-blast decision stating its stakes there can no longer auto-resolve without the human. The §4a injection-echo hardener already treats those fields as untrusted.
- **`hooks/guard-destructive.sh`** — added an order-independent deny for remote-branch deletion (`git push <remote> --delete <ref>` / `git push <remote> :<ref>`), an always-on guard gap for a destructive op in its stated scope.

### Fixed — P1 (high)

- **`hooks/guard-destructive.sh`** — `git clean -d -f` (separated-token force flag) now denied via order-independent `_is_dangerous_git_clean` (the old contiguous-anchor regex missed it). Audit-gates fixtures added for both new guards.
- **`scripts/capability-orientation.py`** — SessionStart banner permission-rule strings now routed through `_sanitize_banner_field` (a committed rule with a newline + frame tag could otherwise break the untrusted-data frame).
- **`skills/rc-deep-research/rc-deep-research.js`** (both copies) — Verify-phase adversarial `agent()` calls now carry the `.catch()` the search/fetch phases already had (one rejected vote no longer crashes the run). Dispatch-evaluator floor (Gate 52) untouched.
- **`skills/two-panel-plan-review/two-panel-plan-review.js`** — Panel 1/2 lens fan-outs now per-agent `.catch()`-guarded.
- **`skills/brand-extraction/extract_brand.py`** — fetched title/site_name/URL are `html.escape`d and font-family names stripped of CSS-breakout chars (was stored HTML/CSS injection into the generated report).
- **`skills/svg-report-lint/lint.py` + `skills/declarative-visualization/lint.py`** — the remote-href "security floor" now flags protocol-relative URLs (`//host`) and strips tab/CR/LF before scheme-matching (closes the `jav&#9;ascript:` bypass).
- **`skills/visual-feedback-loop/driver.py`** — path guard now uses `realpath` (not `abspath`) on both sides, restoring the symlink-escape parity it claims with the layout linter.

### Fixed — P2 / P3

- **`scripts/generate-bi-report.py`** — column `key` constrained to a safe identifier grammar before use as an HTML attribute name (attribute-name injection); shipped reports byte-identical.
- **`scripts/capability-orientation.py`** — EFFECTIVE PERMISSIONS banner now reconciles project+local layers with deny>ask>allow precedence (a rule could previously appear under both allow and deny).
- **`scripts/thing-seat.sh` + `scripts/claude-orchestrate.sh`** — inline secret-scrub fallback arrays re-synced byte-for-byte with the canonical `hooks/_scrub.sh` (were missing several newer secret types).
- **`skills/pbir-layout-engine/lint.py`** — `check_column_alignment` now honors the caller-supplied tolerance when grouping rows (was hardcoded 1px).

**Migration:** `guard-destructive.sh` now denies two additional destructive command shapes for any consumer who has it wired — `git push <remote> --delete <ref>` / `:<ref>` (remote-branch deletion) and `git clean -d -f` (separated-token). Both are unarguable destructive ops; the sanctioned branch-deletion path (`scripts/archive-branch.sh`, GitHub's UI) is unaffected. Everything else is internal robustness/security hardening with no consumer-facing surface change.

## 0.248.0 — 2026-08-12

> **Landed from PR #835 (authored as 0.237.0).** Renumbered on integration — `main` had moved
> to 0.247.0 while the branch was open. All 16 code files merged clean; the only conflicts were
> the three version manifests and this file.

### Fixed

- **Three-panel repo review — the landable (non-substrate) subset.** A scheduled whole-repo review
  (find → adversarially verify → analyze → tie-break) raised 32 findings; this release lands every
  confirmed fix that does **not** touch the tribunal's own substrate (`hooks/` + plugin `scripts/`).
  The 3 **P0** fixes all live in that substrate and could not be applied in the headless review
  environment (the `xc.tribunal-self-disable` guard blocks substrate edits when `gh` is absent, so the
  dev-repo exemption cannot verify ownership); they are written up as ready-to-apply patches in
  [`docs/reviews/2026-08-05-three-panel-repo-review.md`](../../docs/reviews/2026-08-05-three-panel-repo-review.md)
  for an interactive session. Three findings were **already fixed (as well or better) on current
  `main`** and were re-verified and dropped: `serve-dashboards.py` static-fallback gating and
  `capability-orientation.py` `_fmt_rules` (both v0.236.1), and the `cleanup-branches.sh` delete TOCTOU
  (current `main` already uses an atomic SHA-guarded `git update-ref -d`, stronger than the reviewed fix).
  - **`svg-report-lint` + `declarative-visualization` lint** — the `href`/URL sanitizer now also
    rejects protocol-relative (`//host`) URLs and strips embedded tab/CR/LF control characters, closing
    two ways a crafted link slipped the scheme allow-list.
  - **`brand-extraction/extract_brand.py`** — the generated `brand.css` / report now HTML- and
    CSS-escape the extracted title/URL and validate font values (`_css_font_safe`), so a hostile home
    page cannot inject markup/CSS into the emitted kit.
  - **`visual-feedback-loop/driver.py`** — `_resolve_safe` uses `os.path.realpath` (not `abspath`) on
    both the input and the repo root, so an in-repo **symlink** pointing outside the sandbox is caught
    (restoring the containment parity the docstring claimed).
  - **`pbir-layout-engine/lint.py`** — overlap tolerance is floored at 1 (`max(tolerance, 1)`), so a
    zero/negative tolerance can no longer disable the overlap check.
  - **`content-scan.py`** — SSRF guard now re-screens **every** redirect hop (`_GuardedRedirectHandler`)
    rather than only the final URL, plus a `JSONDecodeError` guard on the search response.
  - **`generate-bi-report.py`** — data-attribute names are sanitized to a safe key charset
    (`_safe_attr_key`) before interpolation into HTML.
  - **`check-lineup-citations.py`** / **`check-run-actions-argv.py`** — broadened citation-context
    matching to raw-digit magnitudes; added a `len >= 2` argv-shape guard.
  - **`rc-deep-research.js`** (both copies) + **`two-panel-plan-review.js`** — `.catch()` guards on
    `agent()` dispatch so one failed subagent can no longer reject the whole workflow.
  - **`.github/workflows/regenerate-artifacts.yml`** — the self-heal step now runs the layout allow-list
    check and the markdown-link gate before committing regenerated artifacts.
  - **`.repo-layout.json`** — allow-listed `.ravenclaude/task-scope.json` + `.ravenclaude/self-heal-setup.md`;
    removed 3 globs already covered by a broader entry (`tests/fixtures/data-viz/**`,
    `scripts/generate-dashboards.py`, `scripts/serve-dashboards.py`).

## 0.247.0 — 2026-08-12

> **Gate renumbered 186 → 190 on integration.** `main` already shipped Gate 186 (compact-anchor, #871) before this branch merged; two arms sharing one number makes the `--check` dispatcher reach only the first and silently strand the other.

### Fixed

- **The premise gate's ledger was shared by every parallel agent, and its only escape was
  unreachable from the agents that needed it.** The ledger was keyed on
  `(CLAUDE_PROJECT_DIR, session_id)` — `guard-premise.sh:246` and `log-probe.sh:162` — and neither
  component varies per agent. Measured against a real 6-agent parallel run (not inferred): **one**
  `session_id` carried **14,322** transcript events spanning **49 distinct `cwd` values** across
  **15+ git worktrees**, and the single ledger it produced held **2,825 entries with 50 unresolved
  negative families**. A negative recorded by the agent in worktree A therefore denied an unrelated
  new module in worktree B. Three agents hit it in one run; one lost finished work rather than
  tunnel, and one routed around the hook by writing files through Bash heredocs.

  The ledger is now scoped to the **git worktree root** containing the payload's `cwd` (a linked
  worktree carries its own `.git` **file**, so the walk stops at the worktree, not the primary
  checkout) — `…/runs/premise/<sid>/scopes/<scope>/probe-ledger.jsonl`. `cwd` is the one payload
  field that varies per agent. The `recorder-alive` beacon deliberately stays **session-level**: a
  per-scope beacon would make a never-probed worktree indistinguishable from an unwired recorder,
  and the gate fails closed on that, so every fresh worktree's first write would be denied as blind.

  **This narrows WHO a negative blocks, never WHAT counts as one.** A probe and the module built on
  it share a working context, so the incident the gate was built from still trips it — pinned by the
  second half of the new gate, without which "scoping" would be indistinguishable from switching the
  gate off.

### Added

- **A file-based control the escape a subagent can actually reach.** `RC_PREMISE_CONTROL` and
  `RC_PREMISE_OVERRIDE` are **environment variables**, and a variable exported inside a `Bash` tool
  call never reaches the `PreToolUse(Write)` hook process — so a dispatched subagent that had
  genuinely done the control work had **no** sanctioned way to say so. A guardrail whose only exit is
  unreachable does not get respected; it gets tunnelled.

  Every deny now prints the exact path to write with the `Write` tool
  (`…/runs/premise/<sid>/scopes/<scope>/control.md`), and the file clears the gate only when it
  carries **all four** keys with non-empty values:

  ```
  premise-control: <subject this covers, or * for all>
  who: <which agent/session ran the control>
  subject: <the claim that was under test>
  control: <the probe you ran -> the result it returned>
  ```

  It is scoped to one session **and** one worktree, so it cannot clear a sibling agent; a
  subject-scoped entry clears only matching families; only an explicit `premise-control: *` clears
  the BLIND state (blindness is not a claim about one subject). Every use appends a `file-control`
  line naming who/subject/control/cleared to the existing
  `.ravenclaude/runs/premise/overrides.log`, deduped by content signature — **the escape is
  recorded, not silent**. An incomplete file clears nothing and the deny says which key is missing by
  name, because an escape hatch nobody tested is one everybody uses.

- **Gate 190** (`hooks/tests/test-premise-scoping.sh`, registered in both the `--check` dispatcher
  and the main sequence) — 22 assertions over **real `git worktree add` worktrees**, not simulated
  ones, since the detector keys on the real `.git` file. It carries both halves plus two teeth:
  collapsing the scope key in both hooks turns 22/0 into 16/6, and making every control file "valid"
  turns it into 19/3.


## 0.245.1 — 2026-08-12

### Fixed

- **The premise gate fired on a section header no author wrote.** `## Edge cases / when the rule
  does NOT apply` is boilerplate in **all 35** best-practice files, and it parses as
  `<named subject> + <failure predicate>` — `_SUBJ` matches `the rule`, `_FAILS` matches
  `does NOT apply`. So T-PROSE tripped on any such file that happened to carry a date inside
  the ±6-line `_STAMP` window: **4 of 35** measured on 2026-08-12. It fires on the file's own
  structure, which is the definition of a false positive.

  **The fix is a conditional-clause guard, not a predicate deletion.** `when the rule does not
  apply` states a **case**; `the rule does not apply` states a **fact**. Only the second is a
  premise, and this gate exists for premises. A new `_COND` check skips a match preceded on the
  same line by `when`/`whenever`/`if`/`unless`/`whether`/`where`/`in case`, within a 24-char
  window that breaks on `.!?` **and `,`**.

  ⛔ **Both tempting fixes were worse, and were rejected on inspection:** dropping
  `apply|applies` from `_FAILS` loses a genuine predicate ("the patch does not apply"), and
  skipping markdown headings loses *more* — this repo routinely states real diagnoses in
  headings (`## macOS door 2 — timeout is absent…`, `## The gate that never ran`), which are
  exactly the confident claims the trigger is for. The comma in the window is load-bearing too:
  without it, *"When we checked, the decoder is broken"* would be skipped, and that is an
  assertion with a temporal preamble, not a conditional.

  **Gate 177** gains three fixtures that differ *only* in what precedes an identical
  subject+predicate span — the boilerplate heading (allowed), the bare assertion (still
  DENIED), and the temporal preamble (still DENIED) — so the discriminator itself is what is
  under test. 20 → **23 assertions**, and all four previously-tripping best-practice files were
  re-run through the real hook and now pass.

- **⛔ Caught in the act: one apostrophe in a comment silently disarmed the whole gate.** The
  first draft of the fix put `(3)'s` and `FILE'S OWN` in the new comment block. That Python is
  embedded in a **single-quoted** bash `$(...)`, so the apostrophe closed the string and the
  hook died with `bad substitution` → **exit 1** — which Claude Code treats as a *non-blocking*
  error, so the premise gate **failed open and silently stopped gating every write**. Gate 177
  went 23/23 → 0/23 and caught it immediately. The prohibition is now written into the block
  itself, next to the pre-existing `doesn\x27t` that was already there for this reason. This is
  the v0.193.0 exit-code lesson (a loud exit-2 is safe; exit 1 is the silent fail-open) landing
  on a *comment*.

## 0.245.0 — 2026-08-12

### Added

- **`compact-anchor` — the SessionStart(compact) addressability pointer.** The build that
  v0.244.1's retraction identified as the *actual* gap. v0.244.1 established that compaction is
  **append-only** — the transcript keeps every pre-boundary turn, so the post-compaction agent does
  not lack the data, it lacks the **knowledge that the data exists**. That is an addressability
  problem, and it needs one line of injected context, not a persistence mechanism.

  `hooks/compact-anchor.sh` + `scripts/compact-anchor.py`, registered on `SessionStart` with
  `matcher: "compact"` in both wiring paths. On a compacted session it emits the transcript path,
  which line the last boundary fell on (of how many), how many compactions this session has had, the
  `preTokens → postTokens` accounting, and the two-command grep recipe for searching the pre-boundary
  half. **`SessionStart` is the only placement that works** — `PreCompact`'s stdout is not injected;
  only `UserPromptSubmit` / `UserPromptExpansion` / `SessionStart` have theirs added as context.

  ⛔ **The load-bearing invariant is DERIVED VALUES ONLY.** This hook's stdout goes straight into the
  model's context, and the transcript holds tool results and fetched web bodies from earlier turns —
  untrusted text. Every emitted byte is one of exactly four things: a fixed string authored in the
  script, an integer validated as an integer, a `trigger` matched against a two-item allowlist, or
  the path from the trusted harness payload. **No line of transcript content is ever echoed** — the
  same rule the capability banner, the run-state monitor and the Muninn recall digest follow.

  **Fail-safe:** the EXIT trap is armed first and `-e` is deliberately absent, so a missing field,
  unreadable file, torn line, oversized transcript or non-JSON stdin all end in a silent `exit 0`.
  Scoped to `compact` by the matcher *and* re-checked against `payload.source` in the engine, so a
  matcher-less wiring cannot make it fire on every session start. bash 3.2-safe; no GNU `timeout`,
  `grep -P` or `sed -i`.

  **Gate 186** (`hooks/tests/test-compact-anchor.sh`, 22 assertions) plants a sentinel inside a
  `tool_result` **before** the cut and asserts it never reaches the output; the `--must-fail-leak`
  half mutates the emitter to append a raw transcript line and requires the no-leak assertion to
  catch it. Registered in **both** the main sequence and the `--check` dispatcher, and the full
  suite's output was grepped for the gate by name — per v0.243.0, a passing suite is not evidence
  your gate is in it.

  **Migration:** none — a new hook that fires only when a session resumes from a compaction, emits
  only derived values, and exits 0 on every error path.

## 0.244.1 — 2026-08-12

### Fixed

- **A prescriptive best-practice told agents to build a hook that solves a problem that does not
  exist — and mis-stated the one safety fact that matters about it.**
  `precompact-hook-is-the-deterministic-enforcer-of-persist-before-compaction.md` instructed authors
  to register a `PreCompact` command hook that "flushes the plan / open decisions / rejected
  approaches to disk," on the premise that compaction destroys them. Reviewed **before** implementing
  it here; two independent checks falsified it.

  1. **`PreCompact` CAN block.** The file said it is *"not a place to block compaction … not a veto."*
     The current [hooks reference](https://code.claude.com/docs/en/hooks) (retrieved 2026-08-12) lists
     `PreCompact` → **Can block? Yes**, exit 2 → blocks compaction. That inverts the hazard model: a
     hook that exits non-zero on any error path does not merely fail to persist, it **wedges a session
     whose window is already full**. Anyone following the old file would have written it fail-closed.
  2. **Nothing is destroyed.** Compaction **appends**. Measured on this project's own transcripts: 44
     `compact_boundary` records; one 12,398-line transcript with its first boundary at line 4031 and
     **1,942 pre-boundary turns still present**; every block type retained including **939 `thinking`
     blocks**; and the boundary record itself carrying `preTokens 1000599 → postTokens 32828`,
     `cumulativeDroppedTokens`, and a `preservedSegment` naming the surviving span **by UUID**.

  ⛔ **The remedy was also unmechanizable, which is the sharper lesson.** A command hook receives a
  JSON payload on stdin and nothing else — it has no access to "the model's plan." The prescribed
  `flush-plan-state.sh` could only ever have appended a timestamp and a path: this repo's own
  *gate-that-asserts-nothing* class, shipped as advice. **A prose rule being real does not mean a
  hook-shaped answer exists.**

  The real gap is **addressability, not durability** — the post-compact agent does not know the record
  exists or where the boundary fell. The file now teaches retrieval (`grep compact_boundary
  "$transcript_path"`) and points at `SessionStart` with a `compact` matcher, the only surface whose
  stdout reaches the model. **No hook was added**: adding one would have been the defect this review
  found.

- **The false framing had propagated to three citing surfaces**, all corrected in the same change:
  `best-practices/README.md` (the index entry repeated the prescription verbatim),
  `a-policy-hook-only-gates-if-it-fails-closed.md` (cited it as *"a concrete deterministic-enforcer
  hook"* — it is now labelled as that rule's **documented exception**, since `PreCompact` must fail
  **open**), and `posttooluse-hook-is-the-deterministic-quarantine-for-untrusted-tool-output.md`
  (twice — it claimed the PreCompact rule *"closed"* the compaction gap, and cited it as the same
  mechanization shape; it is now the counter-example). `compact-proactively-and-persist-state-before-compaction.md`
  keeps its *when to compact* half and gets a scoping correction: the loss is to the **window**, not
  the **disk**, and the reason to write decisions down is legibility + cross-CLI reach, not rescue.

  The filename is retained deliberately — six files link to it, two are dated research records this
  repo's convention says not to rewrite. **The name asserts the retracted claim; the content is the
  correction**, per the v0.196.0 supersession rule.
## 0.244.0 — 2026-08-11

### Fixed

- **#861's fix was half-done: the OTHER category-independent hard rule had the identical defect.**
  v0.242.0 scoped `srm.force-push`'s bare `.*` and left `sce.curl-pipe-shell` untouched. Both are
  `pre_llm_deny` + `always_screen` — non-overridable, category-independent, the floor everything else
  sits on. Measured today when shipping an ordinary Python file was **hard-denied**: its docstring
  mentioned a fetch tool, and its code carried a file-extension alternation. The unscoped `.*` walked
  from the prose mention all the way to a pipe character **inside a regex literal**. Nothing was piped
  to any shell.

  ⛔ **The fix is deliberately NOT the force-push fix, and copying it would have created a false
  NEGATIVE.** Force-push excludes `|` — a push flag never crosses a pipe. This rule **must allow** `|`,
  because a fetch routed through an intermediate stage and then into an interpreter is a genuine
  attack. It therefore excludes only the command separators (`&`, `;`, newline). **Same defect class,
  different correct fix — read what the rule is for before reusing a sibling's remedy.**

  Verified **6/6** on true and false positives (was 1 wrong), including that the
  through-an-intermediate-stage form still blocks. The 131 catalog triggers all compile — checked
  explicitly, because `_matches` swallows a malformed regex (`except re.error: continue`), so a typo
  here would **silently disable the hard rule** rather than fail loudly.

- **A Gate 15 fixture asserted a bypass the shell forbids** — the same class the owner ruled on in
  #861, applied to its sibling. It required a **bare** newline between the fetch and the interpreter;
  `bash` parses that as two commands, and a pipe at the start of a line is a syntax error. Replaced
  with the line-continuation form, which the shell really does join and which still denies. This is
  the established precedent, not a new decision.

### Known limitation — now demonstrated three times in one session

**The guard cannot distinguish a command from a description of a command**, and this release hit it
three more times: the Edit that *fixes* the rule, a comment *explaining* the correct behaviour, and
the test that *verifies* it were each denied for containing the pattern they documented — including a
regex literal that **matches itself**. Fixtures and comments are written around it (`printf`
assembly, no literal forms). That is a workaround. The sanctioned door (an exempt fixtures path, or an
honoured in-file marker) remains deliberately unbuilt — it widens what the guard ignores and earns its
own review.

## 0.243.0 — 2026-08-11

### Fixed

- **⛔ Gate 184 never ran. It was unreachable for a whole release, and the suite reported green.**
  v0.241.0 inserted the memory-compaction guard's **main-sequence** block *inside* the `--check`
  dispatcher, between the `178)` case label and its body. Two silent consequences, both measured:
  a full-suite run contained **0** references to the gate, and **`--check 178`** (the claim
  classifier) ran the memory block and then died on `gate: command not found`. The suite said
  **701 pass** with a security-adjacent gate entirely absent.

  This is this repo's own recorded *"unrun variant"* — *a gate nothing runs reports green* —
  shipped in the very PR whose milestone claims it was *"registered in **both** the `--check`
  dispatcher and the main sequence."* **Writing the claim is not the same as placing the code.**
  Both gates are now in both places, and the fix is proved by the assertion count moving
  **701 → 703** plus a grep of the suite output for each gate by name. That grep is now written
  into the gate's own comment as the required step when adding a gate.

- **A non-result was recorded as an absence (issue #860).** `log-probe.sh` matched its NEGATIVE
  list first, over the whole combined output of one tool call. Two shapes were mis-classified,
  and both manufacture the exact false premise the mechanism exists to stop:

  1. **A bidirectional control recorded as `negative`.** One command probing a known-good *and* a
     known-absent subject emits a 2xx **and** a 4xx; the 4xx matched first. But that command is
     precisely the disconfirming probe the gate demands — it proves the probe **can** return
     something else. So running the printed remedy **added** an unresolved negative instead of
     clearing one, and the more thorough the control, the more stuck the author became. **The gate
     printed a remedy its own recorder punished.** Now: both present ⇒ `positive`
     (`control-bidirectional`), in either order.
  2. **Rate-limiting recorded as `negative`** — "I could not ask" stated as "it is not there". New
     `indeterminate` class, checked first, covering 429 / 5xx / timeout / unreachable. It neither
     blocks (a non-result is not evidence of absence) nor resolves (it proves no capability). A
     429 returns 429 on every retry, so treating it as a negative would be an **unclearable** block
     whose only exit is `RC_PREMISE_OVERRIDE` — and a gate whose sole remedy is its own override
     teaches the override. `guard-premise.sh` carries a comment forbidding a future "completion"
     of that branch.

  A **real** 404 and a `command not found` still record as `negative` and still block. Verified
  10/10 against the live recorder; pinned by new **Gate 185** with an end-to-end assertion.

### Corrected in the issue itself

- **#860's claim that a shell `curl` control "can never resolve the family" was wrong.**
  `guard-premise.sh`'s `family()` collapses a subject to its **host**, and the subject regex runs on
  `tool_input.command` for `Bash` as well as `url` for `WebFetch` — so a curl control on the same
  host *does* resolve. The real cause was the verdict mis-classification above.

### Known limitation (deferred, with the diagnosis corrected)

- **`premise-gate.py` and `classify_claim.py` do not ship to consumers.** Both live at the
  **marketplace-root** `scripts/`, and `forge-pipeline/SKILL.md` cites them repo-relative
  (`python3 scripts/premise-gate.py`) — which resolves inside RavenClaude and **cannot** resolve in
  a consumer repo. Their siblings `forge-route.py` and `forge-worktree.sh` ship inside the plugin
  and are cited `${CLAUDE_PLUGIN_ROOT}/scripts/…`, so the pattern is established and these two are
  the outliers. The plan that specified them even says *"Build. `plugins/ravenclaude-core/scripts/
  classify_claim.py`"* — the implementation drifted from its own plan. **Not fixed here:** moving
  them is a packaging change touching 6 `audit-gates.sh` call sites plus the SKILL citations, and
  it deserves its own diff rather than riding along with a verdict-classification fix.

## 0.242.0 — 2026-08-11

### Fixed

- **The force-push hard rule fired on four benign commands (issue #861), and missed a real one.**
  `srm.force-push` is `pre_llm_deny` + `always_screen` — the hardest, **non-overridable** rule in the
  catalog. It denied four measured, working commands in one session. Two independent causes:

  1. **`re.IGNORECASE` made the short-flag alternative match its CAPITAL twin.** `_matches` compiles
     every trigger case-insensitively, so the rule matched a common, harmless flag carried by `awk`,
     `grep` and `sort` — a letter that is **no git-push flag at all**. Case-insensitivity bought
     nothing here and cost a hard deny on ordinary commands. Now scoped case-sensitive via an inline
     `(?-i:…)`.
  2. **`_match_variants._flatten` turned a BARE newline into a SPACE**, so the trigger's `.*` bled out
     of the push and matched an **unrelated later command's** flags. A bare newline is a command
     *separator*; it now flattens to `; `, and the trigger is scoped `[^|&;\n]*` — matching the
     sibling refspec rule, which was **already** segmented. The line-continuation case (`\` +
     newline), which *is* a real single-command evasion, still flattens to a space and still denies.

  **A false NEGATIVE was closed in the same pass:** the old short-flag alternative required a bare
  `-f` and therefore missed a **bundled** cluster (`-uf` / `-fu`) — a genuine force-push.
  `guard-destructive.sh` already caught that form, so the two guards **disagreed on the same
  command**. The cluster form now matches both.

  Verified **15/15** on a matrix of true and false positives (was 8 wrong). `xc.no-undo` carries the
  same trigger and its own comment says the two *"must agree on"* it — both were updated together.

- **Gate 15's newline fixture asserted a bypass the shell does not permit.** It required a **bare**
  newline between the program and the flag to hard-deny. Asked directly, `bash` parses that as **two**
  commands and reports the flag as `command not found` — no force-push executes. The fixture is now
  the **line-continuation** form, which the shell really does join into one command and which the
  guard still denies. This was an **owner-approved** change to a security fixture, not a quiet
  relaxation.

### Known limitation (structural, reproduced while fixing it)

- **The guard blocks the authoring of its own regression fixtures.** Every fixture that pins these
  false positives must contain a literal destructive string as *test data*, and `Write`/`Edit` are in
  the `PreToolUse` matcher and scan content. During this fix the guard denied: a test harness, a JSON
  fixtures file, the issue body **twice**, and two code comments **explaining the bug** — because each
  contained the pattern it documented. The new fixtures are therefore assembled with `printf` rather
  than written literally, with the reason recorded inline. A sanctioned door (an exempt fixtures path,
  or an honoured in-file marker) is the real fix and is **not** included here.

## 0.241.0 — 2026-08-11

### Added

- **`guard-memory-compaction.sh`** — the missing control for Memory Engineering Protocol **Rule 4**.
  Rule 4 (*"bound the growth or lose the index… an unbounded store is a decision that was never
  made"*) shipped as **prose only**, and **Rule 3** of the same protocol says prose is not a control:
  *"to actually block an action, use a hook or a permission deny."* This is that hook.

  ⛔ **The incident, on the maintainer's own machine.** On 2026-08-10 an agent rewrote `MEMORY.md`
  from **20,853 B to 12,324 B — −41%, 57 → 51 lines — in one unreviewed edit seventeen minutes
  wide**. The directory is not a git repo, and `tmutil destinationinfo` returns *"No destinations
  configured"*: there was **no undo of any kind**. Eight prose clauses were destroyed store-wide and
  had to be recovered from an undocumented content-addressed cache under a session UUID. What was
  lost was not trivia — it was **provenance and owner rulings**: *"⛔ Byte-equivalent rollback RETIRED
  by owner"*, a gate-ladder escape hatch, a merge-skew PR reference.

  **What it does.** Two things, and the first matters more than the second:

  1. **Snapshots** the file before **any** write to a guarded memory index. This runs whether or not
     the write is blocked, and it is what converts *unrecoverable* into *recoverable*.
  2. **Denies** a write that shrinks the index past `memory_guard.max_shrink_pct` (default **15%**),
     with the diff-first remedy in the deny message.

  **What it deliberately does not do.** It never blocks growth and never blocks small edits.
  Appending a memory is the normal path and must stay frictionless — *a guard that fires constantly
  gets disabled, and a disabled guard protects nothing.* Escape hatches are explicit, because the
  target is the **silent** compaction, not the considered one: `compaction-approved` in the content,
  or `RC_MEMORY_COMPACTION_OK=1`.

  **Fail-safe by contract.** Every error path exits 0. A guard that cannot parse its input must not
  block the session; the snapshot is best-effort for the same reason. The **only** non-zero exit is
  the deliberate shrink deny (exit **2** — the one code Claude Code treats as blocking; exit 1 is a
  *non-blocking* error and would silently allow).

  **Portability.** bash 3.2-safe, and free of GNU `timeout` / `grep -P` / `sed -i` — re-introducing
  any of those would silently disarm it on every macOS session, which is precisely the four-door
  failure the v0.193.0–v0.197.1 arc closed.

  **Gate 184** (`hooks/tests/test-memory-compaction-guard.sh`), registered in the `--check` dispatcher
  **and** the main sequence. It carries its own **must-fail half**: it builds a mutant with the deny
  branch removed and fails unless that mutant lets the shrink through — so the assertion is proven to
  be measuring the deny, not passing for an unrelated reason.

### Known limitation (discovered while building this, not fixed here)

- **`guard-premise.sh`'s advertised resolution path does not reach its own ledger.** The gate tells
  you *"run the control → the ledger resolves itself"*, and `family(subject)` groups by **host**. But
  the recorder derives a URL subject from **`WebFetch`**, not from a shell command — so a positive
  control run via `curl` **can never resolve the family**, and the gate keeps firing on every new
  source module. Observed twice this session; worked around with the recorded
  `RC_PREMISE_OVERRIDE=1` escape. Related: the same ledger recorded
  `pypi.org/pypi/graphiti-core/json` as a **negative (404)** for a package that demonstrably exists
  (0.29.3) — a throttle artifact from a run that also logged `http-429` and `http-453`, i.e. **the
  ledger can record rate-limiting as absence.**

## 0.240.0 — 2026-08-08

### Added

- **The premise gate** — two hooks that stop construction on an unfalsified premise.
  `log-probe.sh` (PostToolUse `Bash|WebFetch`) records negative results as **derived labels only** —
  never the raw command or output. `guard-premise.sh` (PreToolUse `Write`) then refuses to **create a
  new source module** while one is unresolved, and releases the moment a positive control on the same
  subject lands.

  ⛔ **The incident.** A probe of a Cloudflare email-obfuscation href returned 404. From that one
  negative result: _"the decoder is broken, every visitor is affected."_ Then an 85-line component, 10
  converted call sites, 15 addresses opted **out** of anti-scraping protection, an owner go-live
  checklist item, and two turns of architectural advice. That URL is a placeholder nothing fetches — it
  is _supposed_ to 404. `/cdn-cgi/trace` → 200 would have ended it in ten seconds. **No user ever
  experienced the defect.** The wrong hypothesis was cheap and normal; the damage came from it being
  silently promoted to a premise **by being written down**, with nothing ever returning to test it.

  ⛔ **It fires when the author is certain.** At the moment of the incident the author was confident,
  with a real tool call behind them — so anything keyed on self-reported doubt would never have fired.
  The trigger reads only objective shape: a negative probe on the ledger, a Write that _creates_, a
  source-module target. Confidence is not an input, so it cannot be an exemption.

  ⛔ **Fails closed.** The recorder drops a liveness beacon; no beacon and no recorder installed means
  **DENY, "I am blind"** — never "all clear". Owner ruling 2026-08-08: _"friction please. Failing
  silently is no bueno."_ "Clean because I looked" and "clean because I couldn't see" are
  indistinguishable afterward, which is how a green gate ends up protecting nothing.

  Friction is bounded: one `test -e` short-circuits every edit to an existing file, every doc, every
  test at any depth, every scratch write. Escape hatches: `RC_PREMISE_CONTROL` (name the control you
  ran) and `RC_PREMISE_OVERRIDE=1` (proceed — and it is written to an override log, never silent).

- **`knowledge/verification-discipline.md`** — seven rules for knowing a claim is true before making
  it, each carrying the incident that produced it, **wired into five agents + `spawn-team`** rather
  than left to be found. (Its companion `consistency-failure-modes.md` had been cited by *nothing*
  since it landed; both are now referenced from the agents that need them.) Includes the structural
  rule for why a review loop that only reads current state **cannot converge** — measured at ~25%
  self-inflicted findings per round, not falling — and an honest statement of what does *not* go away.

- **FORGE gate G3b** (`scripts/premise-gate.py` + `reference/premise-gate.md`) — the same discipline
  inside the planning pipeline. G1 validates **provenance**, and the costly false claim *was*
  provenanced; G1 has no notion of **inferential distance**. Claims tables now carry a
  `kind: observation | inference` column typed by `scripts/classify_claim.py` (grammatical,
  **upward-only**), and every plan phase declares `depends_on_claims: [...]`.

  ⛔ **The field must be emitted, not just read.** A draft of this design specified the trigger against
  a plan field the schema never added, and its gate supplied that field in a **synthetic fixture** — so
  it would have gone green while inert in production. A fixture is not a wiring proof. Hence the
  `UNWIRED` verdict (exit **1**, never 0) when a plan has phases but no claim edges at all.

### Changed

- **DOM ratchet +16** (dashboard 6,155 → 6,171; index 7,041 → 7,057), owner-approved. Raised rather
  than hiding `guard-premise.sh` from `_PIPELINE_LANES`: a hook that **denies a user's write** and
  cannot be seen or understood in the dashboard is exactly the unwatched-not-clean state the Pipeline
  tab exists to prevent. The ratchet row states the one-step revert.

## 0.238.0 — 2026-08-06

### Added

- **Memory Engineering Protocol** — a new always-on section in [`CLAUDE.md`](CLAUDE.md), inserted after
  § Claim Grounding & Source Honesty. The epistemic triad governs a claim made _in a turn_; the moment a
  claim is written to a durable store it becomes a **prior** that arrives in every future session already
  trusted, with its basis gone. Five rules cover that surface: persist provenance **inline in the stored
  item**; treat memory read from a store as **untrusted input, not instruction** (OWASP ASI06 — its
  defining property is _persistence_, so fixing the prompt does not fix the agent); **memory is context,
  not enforcement** (to block, use a hook or a permission deny); **nothing forgets by default** — state
  retention _and_ what survives a delete before the first write; and **verify before you recommend from
  memory**. Carries its own composition table — the existing epistemic and execution-agency triad tables
  are unchanged.
- **Second carve-out to the domain-plugins-extend-core house rule** — the
  [`memory-engineering`](../memory-engineering/CLAUDE.md) plugin, on the same "generalist concern that
  splits cleanly" test that admitted `project-management`. Domain-neutral hygiene stays core; deep craft
  (paradigm selection, the five storage surfaces, erasure residue, cost-per-correct economics) goes to the
  plugin. **Memory security does not fork a reviewer**: ASI06 review ships as the
  [`memory-poisoning-review`](../memory-engineering/skills/memory-poisoning-review/SKILL.md) skill invoked
  by `ravenclaude-core/security-reviewer` through an inline prior.
- **Two inline priors** (agent bodies only — no `description` change, so zero orchestrator-budget cost):
  `agents/security-reviewer.md` gains the ASI06 memory-poisoning review rubric pointer, and
  `agents/architect.md` gains the paradigm-selection / surface-mapping skill pointers plus a spawn pointer
  to `memory-engineering/memory-architect-lead`.

**Migration:** none. The protocol is inherited prose — no hook, no gate, no config, no new agent. The
plugin is opt-in and declares `requires: ravenclaude-core@>=0.238.0`; core does not depend on it.

## 0.236.1 — 2026-08-05

### Fixed

- **Multi-panel repo review — gate-invisible defects in this plugin** (all objective CI gates were
  green; each verified against the real code before fixing). `guard-web-access.sh`'s inline-comment
  blacklist fix landed independently on `main` (0.236.0), so it is not repeated here.
  - **`serve-dashboards.py` — static GET/HEAD fallback was un-gated (DNS-rebinding read primitive).**
    The `/__*` endpoints called `_local_request_ok()`, but the `super().do_GET()`/`do_HEAD()` static
    path did not, so a DNS-rebinding page could read `.git/config`, `.claude/settings.json`,
    `.ravenclaude/runs/**`. Now gated (403 on a forged/rebind Host); every legitimate load still passes
    (`_ALLOWED_HOSTS` already covers 127.0.0.1/localhost/forwarded-Codespace/LAN). Verified end-to-end.
  - **`sanitize-webfetch-body.py` — a nested-decoy tag bypassed the `<system-reminder>`/
    `<system-instruction>` strip.** The non-greedy `.*?` stopped at the first close, leaving the real
    payload as bare text. Made greedy (consistent with the file's over-strip philosophy).
  - **`worktree-guard.sh` (block mode)** — a Write into a not-yet-existing subdirectory was classed
    "not under tree" and slipped the deny; and `git reset`/`restore`/`clean` were missing from the
    mutating-command set. Both fixed.
  - **`apply-comfort-posture.py`** — the no-PyYAML fallback parser now caps recursion depth and raises a
    catchable `ValueError` instead of a raw `RecursionError` on a hostile deeply-nested posture file.
  - **`guard-recursive-spawn.sh`** — corrected the misleading "STRICT mode makes it blocking" claim
    (it's a `PostToolUse` hook; it surfaces a post-edit error, it cannot block/undo the edit).

## 0.235.0 — 2026-07-29

**Turned this session's lessons into a gate, a rule, and eight more fixes.** The UI/UX audit
in 0.234.0 found 24 defects on two surfaces. This release asks the question that matters
more: *what did the audit teach, and where else does each defect class live?*

### The lesson that generalises

The audit harness produced **3,337 findings, ~99% of them false**, across six successive
wrong checks — each of which is the version a competent person writes first. Acting on the
batch would have made the product worse in four places. That is the
[silent-green defect](CLAUDE.md) shape moved up one level, into the instrument you were
going to use to *find* defects, where it corrupts every downstream conclusion.

New **Primary diagnostic**:
[`docs/best-practices/validating-a-measuring-instrument.md`](../../docs/best-practices/validating-a-measuring-instrument.md)
— *a new measuring tool's first output is a claim about the tool, not about the subject.*
Three cheap triage steps (implausible volume is a bug report about the checker · trace
exactly one finding to source before fixing anything · ask the platform instead of
modelling it), the six wrong checks as a table, and the mutation-test-between-clean-passes
rule that makes "0 findings" mean something. Story form, with what was tried first, is a
dated entry in [`docs/memory-bank/lessons-learned.md`](../../docs/memory-bank/lessons-learned.md),
per this repo's own lessons-vs-best-practices convention.

### Added — Gate 174: token misuse that renders unreadable

[`scripts/check-css-token-hygiene.py`](../../scripts/check-css-token-hygiene.py). Three of
0.234.0's classes were **wrong by construction** — no measurement needed to know the answer —
so they are now gated statically, stdlib-only, no browser:

1. a **hairline token as a foreground colour** (`--border` is 7% alpha → ~1.2:1),
2. a **theme-blind literal on a themed fill** (`#fff` on `var(--accent)` is 1.95:1, and a
   literal cannot follow the light/dark swap at all),
3. a **bare `minmax(<N>px, 1fr)` track** in an `auto-fit`/`auto-fill` grid, which scrolls
   the whole document sideways once a container is narrower than N,

plus a generated dashboard surface with **no bare-`a` colour rule** — the defect that shipped
in `dashboard.html` while the portal masked it.

It **deliberately does not compute contrast**: that needs a browser, and a hand-rolled
approximation of one is precisely what produced the 3,337 false findings. The scope
statement is in the file's own header. `--must-fail` asserts **7 known-bad caught AND 8
known-good left alone** — the inverted direction matters here, because an audit tool's
costly failure is inventing defects, not missing them. Suite: **684 → 686 pass, 0 fail.**

### Fixed — eight more instances, found by asking "how many siblings does this class have?"

The audit found one `--border`-as-text-colour rule; a grep found a **second the browser
could not see**, because it coloured an SVG icon rather than text. Applying that question to
each class surfaced defects on surfaces the audit never visited:

- **`.review-scales-icon[data-review-state="off"]`** — the same hairline-token defect, in the
  review-state icon.
- **`generate-bi-report.py` and `generate-feedback-report.py`** — three `#fff`-on-accent
  controls (1.95:1) in **stakeholder-facing report generators that had never been audited**.
- **`::selection`** — `#000` on accent is 3.9:1 in light theme; now `var(--bg)`.
- **18 `minmax()` tracks** across four generators, and **two consumer templates**
  (`repo-build-studio/{dashboard,marketing-page}.html`) — the class eliminated rather than
  the two instances that happened to bite.
- **Two `flex-wrap: nowrap` rows** (`.topbar .actions`, `.layer-radios`) that pushed content
  45px and 64px past a 320px viewport.

### On coverage, stated honestly

0.234.0 tested 1280/768/375px. Extending the audit to **320px** flipped a negative result:
"no `minmax` grid overflows — measured" was true at 375 and **false at 320**, where a 340px
track blew out every route. A negative result without its coverage is not a result. All
three surfaces (portal, standalone, `pitch.html`) are now clean at **4 widths × 2 themes**.

Two findings were again verified **correct by design** and left alone, and one 1/64-pixel
threshold artifact was resolved with a documented tolerance rather than `min-height: 25px` —
CSS that lies about its intent is worse than a tolerance that states one.

## 0.234.0 — 2026-07-29

**Looped a measured UI/UX audit over both dashboard surfaces until two consecutive
passes found nothing.** Every finding came from a headless Chrome measuring real
computed layout — contrast ratios, pointer-target geometry, resolved tokens — across
**21 routes × 3 viewports × 2 themes**, on the portal *and* the shipped standalone.
**94 raw findings → 24 real defects fixed → 0.** Zero new DOM elements: 6,154 / 7,040
unchanged, so no Gate 132 ratchet raise.

### Fixed — P1: text that could not be read

- **The shipped `dashboard.html` had no link colour rule at all.** Every inline link
  in its prose fell back to the browser default `#0000EE` — about **2:1** on these
  dark surfaces. 18 instances. The dev portal looked fine because the *shell* defines
  `a { color: var(--teal-2) }`, so the broken surface was the one consumers actually
  get from `rc dashboard`. `--teal-2` aliases `--rc-accent`, so the fix changes the
  portal by nothing.
- **`.cr-summary-micro[data-state="off"]` used `var(--border)` as a text colour** —
  the 7%-alpha hairline token. The word **"off"**, i.e. the review state you most need
  to notice, rendered at **1.17:1**. Now `--muted`: 7.7:1 dark / 5.9:1 light.
- **`color: #fff` / `var(--rc-text)` on accent- and danger-filled controls** —
  1.81–1.95:1 on the green, **2.76:1** on the dark-theme red. Six controls, including
  the Prompt Builder's primary action and the Gjallarhorn alert banner. All now use
  `var(--bg)`, this codebase's existing pairing (`.seg-label:checked`): **10.3:1** dark
  / 5.0:1 light on accent, 7.3:1 / 5.4:1 on danger. Two were hardcoded `#fff`, which
  could not follow the theme swap at all.
- **A file path escaped its button at 375px.** `.btn-sub` rendered 417px wide inside a
  297px button, spilling out both sides, where its on-accent dark text sat on the dark
  panel — **1.00:1**. Now wraps.

### Fixed — P1: layout that broke the page sideways

- **`minmax(320px, 1fr)` in the Heimdall grid.** A track minimum cannot shrink below
  itself, so a 287px container got 320px tracks and the cards hung off-screen,
  scrolling the *whole page* horizontally on a phone. Now `minmax(min(320px, 100%), 1fr)`.
- **A `flex-wrap: nowrap` stage header** pushed its trailing value pill 79px past the
  card at 1280px. Now wraps.
- **Two tables wider than a phone** (the 7-column concern-stats table, 464px min-content;
  the plugin-drift table) now scroll inside their own container instead of widening the
  document.

### Fixed — P1: controls with no accessible name

Five fields were announced as unnamed edit boxes: the web-access **Allow**/**Deny**
lists, per-plugin extra variables, and the Prompt Builder's repeated rule rows. A
`placeholder` is not a name — it disappears on input. Now `aria-label`led, including
the few-shot example rows that share the defect but are not visible in the default mode.

### Fixed — P2/P3

- **`scope=` on every header cell** across 8 tables (4 applied in one pass over `#hc-root`
  rather than at ~10 call sites).
- **24px pointer targets** (WCAG 2.2 SC 2.5.8) for `select`, disclosure rows, the
  Gjallarhorn link, a best-practice toggle, and the sidebar footer links. The 18px help
  dot keeps its **visual** size — an `::after` with `inset: -3px` enlarges the *target*
  to 24px, so density is unchanged. It also gained `flex: 0 0 auto`, having been
  squeezed to **8px** wide by its siblings.
- **Prose links are underlined.** Accent-on-body-text is only **1.31–1.70:1**, below the
  3:1 that lets colour be the sole cue that something is a link (WCAG 1.4.1). Scoped to
  prose containers, so nav items and link-buttons stay undecorated.
- **A skipped heading level** (h2 → h4) on the Guidance tab.

### On the audit itself — six of its own bugs were found and fixed first

Raw output started at 94 findings and peaked at **3,337**; most were the harness lying,
and each was corrected before any code was touched. Recorded because the wrong version
of each check is the obvious one to write:

| Wrong check | What it claimed | Why it was wrong |
|---|---|---|
| DOM-ancestor backdrop | `.rec-badge` invisible at 1.00:1 | An `absolute; bottom:-16px` badge paints over the page, not its parent's fill |
| `elementsFromPoint` backdrop | amber/green backdrops behind ordinary body copy | It returns elements *above* the target; a fixed banner became the "backdrop" of the header behind it |
| Accessible name without labels | 15 correctly-`<label for>`-ed inputs unnamed | Never resolved label association |
| `el.focus()` + style diff | 3,187 elements with "no focus indicator" | `.focus()` does not match `:focus-visible`; and an *unfocused* element's computed `outlineStyle` is `none` for nearly everything |
| Bare `bbox < 24x24` | 2,397 diagram toggles | Ignored SC 2.5.8's spacing/inline/UA exceptions |
| Hand-rolled visibility | 185 "overlapping" targets | Chrome gives a **closed** `<details>` `content-visibility: hidden`, not `display: none`, so its contents keep layout boxes — 126 of 128 concept cards are closed, and their invisible contents pile up at the same coordinates |

Two findings were verified as **correct by design** and deliberately not "fixed": routes
that render identically because a section resolves to its own default tab, and the Help
page's documented redirects. The dead-route check now only fires when two *primary* nav
destinations collide.

The harness was mutation-tested between the two clean passes — three defects
reintroduced, all three caught — so the final zero is a measured result, not a broken
checker.

## 0.233.0 — 2026-07-29

**The Host & context page: made it look like the rest of the product, and made it readable.**

### Fixed — the page had zero styling of its own

Every `.hc-*` class the generator emits — the support matrix, the MCP table, the storage-contract
table, the intro paragraphs, the live-probe card — had **no CSS rule anywhere**. The page rendered on
browser defaults (Times New Roman tables, full-bleed paragraphs, no rhythm) while the design-token
system it sits inside (`--surface`, `--border`, `--ok`, `--font-mono`, `--radius-sm`) went unused. Now
styled in the house idiom: hairline section rules, a 68ch reading measure, uppercase tracked table
headers, mono for paths, and a responsive breakpoint.

**The signature element:** `.hc-yes` / `.hc-no` render as status dots via `::before` — filled for
supported, a hollow ring for not-wired — so the matrix is scannable as a shape before it is read as
text. Colour is not the only channel (the ✓/✗ glyph stays), so it survives a colour-blind read.

**Cost: zero new elements.** Both surfaces held at 6,154 / 7,040 — no Gate 132 ratchet raise. That
constraint is why this is `::before` on the existing cells rather than a wrapper span.

### Changed — plain English

The page explained itself in the vocabulary of the people who built it. Five fixes:

- A column headed **"Installed for you?"** — a yes/no question — whose answers were *automatic*,
  *opt-in (by name)*, and *not wired*. Now **"How you get it"**.
- **"Every claim carries a basis: verified / docs-verified / inferred"** → *"how we know it — checked
  in this repo, read in the vendor's own docs, or inferred — so you can tell a tested fact from an
  educated guess."*
- **"Which RavenClaude components actually run on which CLI"** → *"What actually works on each coding
  tool today — guardrails, skills, agents and the rest."*
- **"anything mid-flight"** → *"anything still in progress"*.
- **"Host-private state … never crosses over"** → *"Each tool also keeps its own private files … and
  those never reach the others."*

Nothing was softened: the "no" cells still say why, and the gaps are still named as gaps.

## 0.232.2 — 2026-07-29

**Looped code review over the ~4,400 lines added today, until two consecutive passes found nothing.**
Seven passes: **11 findings, all fixed.** Every finding came from *executing* the code, not reading it.

### Fixed — P1

- **TOML injection in the Codex MCP installer.** `render_server()` interpolated the server name
  straight into `[mcp_servers.<name>]` with no validation. A name carrying `]` and a newline —
  `ok]\n[mcp_servers.evil]` — **opens a second table**, installing a server the user never named.
  That directly defeats the property the whole opt-in design rests on: *naming the server is the
  consent*. Names come from a plugin's `plugin.json`, which is only as trustworthy as the plugin.
  Server names, config keys and `env` keys are now validated (`[A-Za-z0-9_.-]`, ≤64) and **raise**
  rather than render.
- **The Copilot MCP installer silently destroyed a config it could not parse.** `load_installed()`
  caught `JSONDecodeError` and returned `{}`, so a hand-broken or half-written
  `~/.copilot/mcp-config.json` was **overwritten** — losing every server the user had configured by
  hand, in their **global** config, with a success message. Now: absent → `{}`, present-but-unparseable
  → **refuse**. *Note the asymmetry this exposed: the Codex sibling was given a structural
  append-only guarantee and its JSON counterpart never got the equivalent promise.*

### Fixed — P2

- **The dispatch reader repeated a bug fixed hours earlier in the same file.** It read the log with
  the 50 KiB *head* cap and no truncation flag — so a busy log reported a partial count as a total.
  This is the identical defect corrected in the session scan (a 14.5 MB transcript whose first 50 KiB
  held nothing), reintroduced in a reader written afterwards. Now bounded like the session scan, and
  the UI says *"partial"* when the bound is hit.
- **`rc artifacts` was wrong from any subdirectory** — `list` reported *"No work directories yet"*
  while 84 sat one level up, and `new` would have created a **second** `.ravenclaude/runs/` inside the
  subdirectory. A storage contract with two storage locations is not a contract. It now resolves the
  project root (`.ravenclaude/` or `.git/`), bounded, falling back to cwd.
- **The storage gate's Cursor assertion could pass on a gutted rule.** It searched the whole
  `scripts/ravenclaude` file, where the tier strings appear **twice** in unrelated blocks — so the
  Cursor rule could lose the contract entirely and the gate would stay green. Now scoped to the
  `.mdc` heredoc, and verified to fail on a fully gutted rule.
- **`check-generated-headers`' pointer assertion was satisfied by the marker itself.** The pattern
  accepted a bare `\bedit\b`, which every header already contains (*"do not edit by hand"*) — so the
  claim *"names the SOURCE to edit"* asserted almost nothing. Tightened to require a real source file
  or directory path; `copilot/README.md`, the one file that passed only on the weak alternative, now
  names its generator.
- **Path traversal in the Codex agent generator.** The agent `name` became a filename with no
  validation. Canonical agents are trusted and frontmatter-gated, so this was defence in depth — but a
  generator that builds a path from unvalidated data is one bad frontmatter line from writing outside
  its output directory.
- **`rc artifacts new` crashed on a long task id** — a raw `OSError: File name too long` traceback
  where a one-line message belongs. Capped at 64 characters.

### Fixed — P3

- **The Stop gate ran an arbitrary user command with no time bound.** A command that hangs (a suite
  waiting on a port, anything touching the network) would wedge every session end, and `max_blocks`
  could never advance because the command never returns. Now wrapped in the repo's portable
  `_rc_timeout` shim at 600s — verified bounding a 30s command at 2s — with a fail-safe stub so a
  missing helper cannot disable the gate.
- **`dod-fast.sh` failed OPEN** if it could not resolve the repo: `|| exit 0` reports *"definition of
  done met"* when the truth is *"the checks never ran"* — the exact dishonesty the gate exists to
  prevent. Now blocks and says why.
- **The artifact index followed symlinks** out of the project, listing a foreign directory as though
  it were work in this repo.

### Notes on the review itself

- **One finding was reached by a flawed demonstration.** The Cursor-lane issue was first "proved" by a
  mutant that removed *one* of two mentions of the tier — which proved nothing. The conclusion held
  anyway (verified separately: the strings occur twice outside the rule, so a gutted rule really would
  have passed), but the first demonstration was worthless and is recorded as such.
- **Two probes produced false alarms**, both caught before being reported as defects: a malformed
  cwd-independence test (argparse errors read as failures) and a `--dest /dev/null` status check
  (which was the new unreadable-config guard working correctly).

## 0.232.1 — 2026-07-29

**The dashboard was making three false claims about work shipped in the last few releases.** Found by
asking "are the user interfaces up to date?" — they were not, and the failures were the same
stale-claim class this repo keeps auditing itself for. **All fixed at zero DOM cost** (every one of
these surfaces is JS-built from an inlined payload, so correcting the text costs no elements).

### Fixed

- **The MCP wiring table said Copilot and Codex were "not wired".** Both got opt-in wiring in 0.227.0
  and 0.230.0. Worse, the table still gave the *old reasons* — *"nothing generates that file"* and
  *"too risky to automate"* — which those releases explicitly corrected. The boolean `wired` is now a
  three-state `automatic` / `opt-in (by name)` / `not wired`, because "yes/no" could not express the
  consent model the whole design rests on.
- **The host matrix said Codex agents don't exist** (`supported: false`, *"no generated Codex
  projection exists"*). 0.228.0 shipped exactly that projection — 15 agents with per-agent
  `sandbox_mode`. Flipped, with the honest caveat preserved: docs-verified but never watched being
  enforced by a running Codex session.
- **The Help drawer was wrong three ways in a single sentence** — while citing `host-support.json` as
  its source of truth:
  - *"Cursor … not wired at all — no hooks fire"* — **Cursor's hooks do fire**; the installer writes
    `.cursor/hooks.json` and the matrix has said `supported: true` all along.
  - **Gemini CLI was omitted entirely**, despite being a supported host since v0.222.0 with hooks.
  - It implied **Aider** gets nothing; Aider receives a projected `CONVENTIONS.md`.
  - **The durable fix: that sentence is now COMPUTED from `host-support.json`.** Prose that summarises
    data must be derived from it, or it becomes a second source of truth that silently disagrees with
    the first — which is exactly what happened here.

### Added

- **"Where work files go" now has a UI surface.** The cross-CLI storage contract (0.231.0) existed
  only in `AGENTS.md` and the session-start banner — neither of which a human ever looks at. The Host
  & context page now shows both tiers, who can see each, and the deciding test, rendered into the
  existing mount for zero elements.

### Notes

- Two self-inflicted defects caught during the fix and worth recording: the derived sentence initially
  used **two** `<strong>` tags where the hand-written one had one (+1 element against a zero-slack
  budget — a derived summary must not quietly cost a ratchet raise), and spliced in with a full stop
  where the template expected a semicolon, producing *"…hidden feature. the per-component truth…"*.

## 0.232.0 — 2026-07-29

**Making the storage contract stick — enforcement, not more prose.**

### Added

- **The Stop gate is configured and live.** It was built long ago and never switched on. A session
  that changed files now **cannot end** until `scripts/dod-fast.sh` passes, on every host. This is the
  strongest follow-through lever in the repo: a CLI can announce success as often as it likes, the
  gate decides.
  - The command is a **wrapper, not a one-liner**, deliberately. `ruff` is frequently not on `PATH`,
    so the obvious `cmd: "ruff check . && ..."` would block sessions on machines that never had it —
    punishing the user for a missing tool. The storage-contract check is stdlib and **always binding**;
    ruff **blocks when present** and **loudly skips when absent** (a skip is never silent).
- **`storage-placement-nudge.sh`** — a PostToolUse advisory noting when a work file lands at the repo
  root instead of one of the two tiers, where the next CLI would never look. **Deliberately narrow:**
  only root-level *scratch names* (`notes.md`, `plan.md`, `output.txt`…). It stays silent on
  `AGENTS.md`, `README.md`, `docs/` and all source files, because a nudge that cries wolf is trained
  away within a day. Never blocks; opt out per-file with `placement-ok`.
- **The storage contract is now INJECTED at session start**, not merely linked. A pointer is advisory
  and the reported complaint is precisely that some hosts do not read what they are pointed at. The
  capability banner is placed *into the model's context*, so it is not something a host can decline to
  open.
- **Gate 173 — every generated file must say so, and say what to edit.**
  - **Why this is the one file-stamp worth its cost.** A general "who touched this, when" stamp fails
    three ways here: **1,560 tracked files (16%)** cannot hold a comment at all (`.json`/`.svg`/`.png`/
    `.jsonl`), so coverage is partial and an *absent* stamp becomes ambiguous; generated files carry
    byte-exact freshness gates, so a stamp breaks them or must be excluded — removing provenance
    exactly where confusion is highest; and **`git blame` already answers it, derived**, so it cannot
    go stale the way a maintained stamp can.
  - **The test a stamp must pass is whether it changes what the next CLI DOES.** *"claude-code edited
    this at 3pm"* changes nothing. *"This is generated — edit the source"* changes everything.
  - **And it was missing from half of them: 18 of 36**, including `index.html` and all 15 projected
    Copilot agents. A session could edit `copilot/agents/architect.agent.md` and have the work
    silently reverted by the next regen.
  - The gate also requires a **pointer**, not just the word GENERATED — "stop" with nowhere to go is
    half a message. That stricter half immediately caught a **19th** case: `dashboard.html` declared
    itself but never named its generator.

### Fixed

- **`dod-fast.sh` linted the wrong directory — caught by the gate on its first real run.** It used
  `cd "${CLAUDE_PROJECT_DIR:-…}"`, but that variable is the **session's** project directory, not the
  repo the script lives in. With the CLI launched from `$HOME` — an entirely ordinary thing to do — it
  ran `ruff check .` across the whole home directory, reported 81 errors from `~/.local/share/doc/node/`
  and an unrelated sibling repo, and blocked the session over lint in files nobody here owns. It now
  anchors on the script's own path (`<repo>/scripts/` → repo root is one level up), which no
  environment variable or cwd can move. Verified from a foreign cwd *and* with `CLAUDE_PROJECT_DIR`
  deliberately pointed at `$HOME`.

### Notes

- **Authorship is deliberately NOT recorded in files, and that is a design position.** A CLI that
  learns *"Copilot wrote this, be suspicious"* has acquired a prejudice, not evidence — it would
  distrust correct work and trust wrong work from a favoured tool. Quality in this repo has a real
  answer (the gates), and it is about whether something is **verified**, not who vouched for it.
- Owner-approved **+14 DOM** (6,140 → 6,154 / 7,026 → 7,040) to draw the new nudge in the Pipeline tab
  beside its two already-drawn siblings; leaving it out would make the guardrail map read as though
  the guardrail does not exist. **Measured, not estimated** — trimming the stage description from 4
  steps to 2 saved only 2 elements, so ~12 is the stage's fixed cost.

## 0.231.0 — 2026-07-29

### Added

- **A cross-CLI storage contract — every host is now told where work files go, identically.** Any CLI
  may be the one working in a repo, and the next session may be a different one, so where a file is
  put is the only thing that lets the next tool find it.
  - **The convention existed, but only Claude Code was told.** It lived in
    `plugins/ravenclaude-core/CLAUDE.md` — the Claude-only constitution. Codex, Cursor, Gemini and
    Aider never saw it, and Copilot received only one unrelated section of that file. Root
    `AGENTS.md`, the actual **cross-tool** file, had no file-organisation section at all; it mentioned
    `.ravenclaude/runs/` exactly once, incidentally, inside a branch-deletion rule. Same shape as the
    multi-host audit: a discipline in one host's file, assumed universal.
  - **Two tiers, now named**, because they already existed and nothing said so:
    | tier | path | visibility |
    |---|---|---|
    | local run | `.ravenclaude/runs/<task-id>/` | **this machine only** — gitignored |
    | committed | `docs/plans|decisions|research/` | teammates + CI, via git |

    The deciding test is written down: *would a teammate cloning this repo need it?*
  - **It says what is NOT shared** — host-private state (`~/.claude/` transcripts and memory,
    `~/.copilot/`, `~/.codex/`, conversation history, caches) never crosses over. An admitted gap
    beats a false promise of parity.
- **`rc artifacts list` / `rc artifacts new <id>`** — the index that makes the contract usable.
  `list` shows both tiers, newest first, **with which CLI wrote each one**; `new` creates a directory
  in the right shape stamped with the calling CLI.
  - **The listing is derived by scanning, never maintained**, so it cannot go stale — a hand-kept
    index is a file that goes wrong the first time somebody skips it, and a stale index is worse than
    none because it is believed. This repo has been bitten by that class repeatedly.
  - Host detection uses **positive signals only** and reports `unknown` rather than guessing; a wrong
    provenance stamp is worse than an absent one, because it will be trusted.
  - `new` **never clobbers** an existing directory (it reports who made it and tells you to continue
    there — two half-records is the failure the contract forbids), and **only ever writes the
    gitignored local tier**. Promoting to the committed tier stays a deliberate `git add`.
  - Nested layouts resolve correctly: `.ravenclaude/runs/forge/<slug>/` is a *container*, and listing
    it as one artifact under-reported by 12 directories and would have pointed the next CLI at the
    wrong path.
- **Gate 172** — the contract is canonical in `AGENTS.md`, names both tiers, says what is not shared,
  and **every lane carries it**; plus the index finds both tiers with provenance and never clobbers.
  **The teeth half removes it from one lane** — what adding a host, or tidying a projector's section
  list, actually looks like.
  - The gate is **lane-aware on purpose**: Copilot and Aider receive the section verbatim, so the
    header must be present; Cursor reads neither `AGENTS.md` nor a projection, so what must be true
    there is that its rule names the section **and states both tiers inline**. The first draft checked
    all three identically and failed on correct work — a gate wrong about its own subject.

### Fixed

- **The Aider and Cursor lanes could not have received it.** Aider's projection carries a fixed list
  of sections (the new one is added); Cursor's rule pointed at `AGENTS.md` but enumerated only
  testing, layout and PR conventions — so a Cursor session had no reason to read the part that
  matters here. It now names the section and carries the essentials inline.

## 0.230.0 — 2026-07-29

### Added

- **MCP servers can now be wired for Codex too — opt-in by name, and by pure append** (audit MH-19,
  Codex half; the last open piece of the multi-host audit).
  `ravenclaude install --host codex --with-mcp <server>` adds `[mcp_servers.<name>]` tables to
  `.codex/config.toml`. Nothing is added unless named — the same consent model as the Copilot half,
  and for the same reason: neither `~/.codex/config.toml` nor a project one offers a per-plugin step.
  - **The deferral said *"a bad TOML merge would clobber a hand-tuned config."* That worry was sound,
    and it was retired by structure rather than by care.** This repo already records the sharper
    version in 0.216.0: appending a **bare key** attaches it to the most recent table, so
    `sandbox_mode` appended to a file containing `[mcp_servers.github]` silently became
    `mcp_servers.github.sandbox_mode` — valid TOML, wrong meaning, invisible in a diff.
  - **But bare keys and table headers are opposites in exactly that respect:**

    | | |
    |---|---|
    | a bare key | position-**dependent** → appending is dangerous |
    | a `[table]` header | position-**independent** → appending is safe |

    An MCP server *is* a table. So it is added by **pure append**, and a pure append cannot clobber
    because it never rewrites an existing byte. The safety argument is therefore a one-line
    assertion, checked before every write: `new_text.startswith(original_text)`.
  - Three rules make it total: a server whose table **already exists is skipped, never rewritten**
    (it may be your own tuning, and a duplicate table is a TOML error); the result is **parsed before
    it is saved** (the `network_access`-as-a-quoted-string lesson: verify with a parser, never by
    eye); and only renderable shapes are emitted — anything else **raises** rather than guessing at
    the TOML.
- **Gate 171** — append-only asserted byte-for-byte, hand-tuned tables/root keys/**comments** all
  survive (verified by parsing both sides), idempotent with no duplicate tables, result parses,
  unknown names fail without writing. **The teeth half is the tidier-looking implementation** that
  parses the file and re-emits it — which silently discards your comments and ordering.

### Fixed

- **The installer's own note about this was wrong in two ways.** It said MCP lived at
  `.codex/config.toml` **`[mcp]`** — the table is **`[mcp_servers.<name>]`** `[docs-verified
  2026-07-29]` — and it said the merge was unbuildable because it would clobber, which was a
  statement about one possible implementation, not about the problem.

### Notes

- Both halves read the **same** generated catalogue, so one inventory serves both hosts.
- Stated at install time, not buried: a project `.codex/config.toml` is read **only in trusted
  projects**, so writing the file is not the same as Codex loading it — the same honest caveat the
  hook-trust and sandbox work carries.

## 0.229.0 — 2026-07-29

### Added

- **Subagent dispatch log on the Session page, with a three-state honest empty state** (audit MH-20,
  remedy 2 — the "fuller version" the ledger tracked as open).
  - **Checking the producer first changed the design.** `agent-dispatch-evaluator.sh:77`
    **short-circuits** unless `.ravenclaude/dispatch-config.json` carries `"enabled": true`, and line
    28 states plainly *"enabled:false is the shipped default."* Neither that config nor
    `runs/dispatch-eval/` exists on this machine. **So the reader as specified would have shipped a
    permanently-empty panel** — the exact defect class this audit has spent the session closing (the
    always-empty session card; the MCP step reporting "not configured"; the emitter nothing called).
  - It therefore reports **three distinct states**, because a bare *"nothing recorded"* is
    indistinguishable from a broken reader — and that ambiguity *is* the bug:
    - **off** — nothing will ever be recorded until you opt in; says so, and how.
    - **idle** — enabled, nothing logged yet.
    - **recorded** — totals plus the agent types.
  - **Zero DOM cost and no new endpoint.** The card is appended into the existing `#panel-mimir`
    container and rides `/__mimir`, so no Gate 132 ratchet raise was needed (6,140 / 7,026 unchanged)
    — better than the page-budget cost this option was quoted at.
  - **Derived-only**, like the 0.223.0 counts: totals and validated agent-type labels. The evaluator's
    JSONL may carry a prompt or reasoning; neither is read.
- **Gate 49 extended** with assertions that keep the three states distinct — the `off` state must say
  it is off *and* how to change it, and must not degrade to a bare empty message. **Verified to fail
  (2 assertions) when the states are collapsed into one generic message**, which is what a
  "simplify this" edit looks like.

### Notes

- Per-session subagent counts (shipped 0.223.0, read from transcripts) need **no** opt-in and remain
  the surface most people will actually use; this log adds the evaluator's own records on top, for
  anyone who has turned it on.

## 0.228.0 — 2026-07-29

### Added

- **The 15 agents now project to Codex custom agents, with least privilege enforced.**
  `scripts/generate-codex-agents.py` emits `plugins/ravenclaude-core/codex/agents/*.toml`; the
  installer copies them into a consumer's `.codex/agents/`. The 5 review-only agents
  (`security-reviewer`, `code-reviewer`, `architect`, `deep-researcher`, `viz-spec-reviewer`) get
  `sandbox_mode = "read-only"`; the 10 that declare a write tool get `workspace-write`.
  - **Omission is the dangerous case, and that is what makes this a security fix.** Codex documents
    `sandbox_mode` per agent and that **the parent turn's permission mode is inherited when it is
    omitted** `[docs-verified 2026-07-29]`. So a file without it does **not** fail safe — a
    review-only agent would run with whatever the session has. That is the identical shape to MH-10
    on Copilot (an omitted `tools:` silently granted every tool): two hosts, two mechanisms, one bug.
    `sandbox_mode` is therefore **always** emitted, never left to inheritance.
  - **The recorded blocker was stale.** The deferral said *"there is no verified Codex agent-file
    contract in this repo; projecting 15 agents from a guessed schema is the same don't-guess call
    made on the Copilot `tools:` gap."* Correct at the time — and the contract **is** published, on
    the page for local Codex clients including the CLI. That is the sixth blocker this audit has had
    dissolve against a primary source.
  - **TOML bodies use literal (`'''`) blocks, not basic (`"""`) blocks.** Agent bodies are markdown
    full of backslashes and quotes, every one of which would need escaping in a basic string; a
    literal block needs none. Its one hazard — the terminator, which cannot be escaped inside a
    literal string — is handled by **raising** rather than emitting a corrupt file. No agent body
    currently contains one.
  - Output validated with a **real TOML parser**, not a substring scan — the lesson from the
    `network_access`-written-as-a-string bug that shipped green in 0.216.0.
- **Gate 170** — freshness, valid TOML, required fields non-empty, the agent body actually travelled,
  no orphans, and the two that matter: `sandbox_mode` present on **every** file, and `read-only` for
  every agent whose canonical `tools:` declares no write tool. Asserted against the **canonical
  agents**, not against the generator — a gate that asks the generator what it meant to do proves
  nothing. **The teeth half stops emitting `sandbox_mode`**, which is exactly what a "the default is
  fine" edit looks like.

### Notes

- `[unverified — no Codex CLI on this machine]` Two things could not be settled by execution, and are
  named at install time rather than assumed: whether a kebab-case `name` is accepted (the docs' one
  example pairs `pr_explorer` with `pr-explorer.toml`, so name and filename may differ; a mismatch
  fails **loudly** as agent-not-found, never as a silent privilege widening), and
  [openai/codex#26868](https://github.com/openai/codex/issues/26868), which reports subagent `.toml`
  files not always applying on spawn. Both settle by running Codex and spawning a projected agent —
  the same route that settled the Copilot allowlist in 0.224.0.
- `.repo-layout.json` gains `plugins/*/codex/**`. It is added **now that it is used** — an unused
  allow-list glob silently pre-authorizes an unreviewed directory, which is why it was withheld
  before.

## 0.227.0 — 2026-07-29

### Added

- **MCP servers can now reach the Copilot host — by name, never wholesale** (audit MH-19, Copilot
  half). `ravenclaude install --host copilot --with-mcp <server>` installs exactly the servers you
  name; the default installs **nothing**. `ravenclaude status` lists what is available, who ships it,
  and what you have enabled.
  - **Why opt-in is a security property here, not a preference.** On Claude Code you receive a
    plugin's MCP server *because you installed that plugin* — consent is structural and per-plugin.
    Copilot's `~/.copilot/mcp-config.json` is **global**; there is no per-plugin step. So wiring all
    four wholesale would not restore parity, it would install third-party software from plugins you
    never chose — including a write-capable one (`powerbi-editor`), which
    `docs/best-practices/bundled-mcp-servers.md` treats as an Absolute-rule gate. **Naming the server
    is the consent step**, standing in for the per-plugin choice the host does not offer.
  - New `copilot/mcp-catalog.json` (generated) lists all 4 servers with provenance. **Deliberately
    not named `.mcp.json`** — the installer's legacy auto-merge keys on that name, so the filename is
    what stops the catalogue being swept into a global config by the old code path. The name *is* the
    safety property, and Gate 169 asserts it.
  - An **unknown server name fails loudly** and writes nothing. Asking for a server, getting none,
    and being told "ok" is the exact failure shape this replaces.
- **Gate 169** — catalogue completeness (no drift from what plugins declare), the filename property,
  opt-in installs *that* server and no other, unknown names fail without mutating the config, and
  every entry carries provenance. **The teeth half is the tempting refactor** — "just wire them all,
  it's friendlier" — caught.

### Fixed

- **`ravenclaude status` said "mcp: not configured", which is misleading rather than wrong.** It
  reads as *"you haven't set this up"*, when the truth is *"ravenclaude-core ships no MCP servers of
  its own; the four that exist live in other plugins and are opt-in on this host."* It now says
  which, and lists them.
  - **The old auto-merge step was NOT a bug, read correctly** — it merged `<copilot-pkg>/.mcp.json`,
    a file nothing generates, because it was written for core's own servers and **core ships none**.
    It was correctly inert. Only the reporting was misleading. Recorded because "obviously broken,
    delete it" was the wrong read, and the right fix followed from the accurate one.

### Notes

- `copilot/mcp-catalog.json` is added to `.prettierignore`. Python's `json.dumps` expands short
  arrays one-per-line and prettier collapses them inline; both are valid JSON, but the generator's
  `--check` gate is a **byte** comparison, so the two tools fight and the gate can never be
  satisfied — the unsatisfiable-golden trap already recorded in the `/wireframe` v1.1 milestone.

## 0.226.0 — 2026-07-29

### Fixed

- **Saving your posture in the dashboard now actually reaches Codex** (audit MH-16 part 2, dashboard
  half). `emit-codex-config.py` shipped in 0.216.0, but it was invoked from **exactly one place** —
  `scripts/ravenclaude`, the installer. Nothing on the save path called it, and
  `apply-comfort-posture.py` has no Codex awareness at all. So you could set every category to `deny`,
  click Save, watch it report success, and still be running at Codex's default `workspace-write`. The
  product's headline feature silently did nothing on that host.
  - **The honesty half needed the gate more than the wiring did.** The emitter's rule is *never
    silently weaken*: a posture looser than what is already on disk is **refused**. But a refusal
    **exits 0** — it tightens what it can and declines the rest — so the obvious wrapper reports
    unqualified success while settings were deliberately skipped. That is the same false assurance,
    moved one layer out. Refusals now come back as `codex_refusals`, and **Gate 168's teeth half is
    exactly that naive wrapper**, caught.
  - **Deliberately narrow:** only projects that already use Codex (a `.codex/` directory) are touched.
    Writing an OS-sandbox config into every repo that ever saves a posture would be a surprising side
    effect. And a failure here can never fail the save — the YAML is already on disk.
  - **Still not parity, and it says so:** coarse by design (two enum keys cannot express twelve
    categories), and a project `.codex/config.toml` loads **only in trusted projects** — writing the
    file is not the same as bounding the session.

### Added

- **Gate 168** — pins all of it: a non-Codex project is left untouched, a Codex project gets the
  projection, a stricter on-disk value **survives and the refusal is reported**,
  `danger-full-access` / `approval_policy = "never"` are never emitted at any posture, and **both**
  server copies carry the helper (the plugin copy is what consumers run, so a root-only fix would have
  shipped nothing).
  - The gate's own first draft failed on a *correct* emitter: it scanned the whole config for the
    forbidden values and matched the **header comment**, which names them while promising never to
    emit them. It now checks live config lines only.

### Notes

- The plugin `CLAUDE.md` "Known gap (MH-16 part 2, open)" block is **updated in the same change that
  made it false** — the discipline this audit kept catching itself failing. Last release it was
  deliberately left alone, because at that point it was still accurate.

## 0.225.0 — 2026-07-29

### Added

- **Gate 167 — a Copilot payload now has to survive the whole path to the tribunal.** This is the
  MH-01 residual the audit split out as P0/S and never built. MH-01 was the finding where the
  command-review tribunal was *"fully wired, reviewing nothing"* under Copilot: the envelope was
  translated but the tool-name **value** was not, and `thing-orchestrator.sh` dispatches on a
  case-sensitive `Bash | Read | Write | …` list that falls to `*) exit 0`. Copilot sends `bash`.
  - **The coverage gap was structural, not sloppiness** `[verified 2026-07-29]`. Of all hook tests,
    **exactly one** uses a Copilot-shaped `toolName` — Gate 20's — and it is **not** among the four
    that drive the orchestrator (`test-gate121`, `test-gate162`, `test-phase0-emit-and-scrub`,
    `test-seat-stderr-capture`), all of which feed it Claude-shaped payloads. Gate 20 asserts the
    adapter's **I/O shape**; it never asks whether a verdict comes out the far end. **No test crossed
    the seam where the P0 actually lived**, so a regression in the tool-name map would have left every
    gate green while the tribunal went dark again — silently, exactly as the first time.
  - Three assertions: a control (the command really is deny-worthy in Claude shape), the same command
    in a Copilot envelope through the adapter, and — **the one that matters** — a teeth half that
    defeats the tool-name map and asserts the deny **disappears**. That reproduces MH-01 on demand.
    A gate for a silent failure is worth nothing until it has been watched failing.
  - The teeth half **fails loudly if its mutation anchor is ever missing**, rather than "mutating"
    nothing and reporting teeth that don't exist.

### Fixed (documentation — stale claims, which this repo treats as live defects)

- **The MH-01 residual note said the Gate 20 fixture still hard-codes `toolName:"shell"`.** It does
  not — it reads the docs-verified `"bash"`. Struck. Also corrected: `shell` was described as a
  "third, invented" name. It is a **real** name — in the *agent-profile* tool vocabulary (see 0.224.0
  / MH-10). It was simply the wrong vocabulary for a **hook** fixture.
- **The MH-16 part-2 note said "the emitter is unchanged and still open".** Half-stale: the emitter
  **shipped** (`scripts/emit-codex-config.py`, Gate 156).
  - **But only half, and the other half was re-verified rather than assumed** `[verified 2026-07-29]`.
    The emitter is invoked from exactly one place — `scripts/ravenclaude:736`, the installer. The
    dashboard's save path never calls it and `apply-comfort-posture.py` has no Codex awareness at all.
    So **editing your posture in the dashboard and clicking Save still changes nothing on a Codex
    host**; only a fresh `ravenclaude install --host codex` does. The plugin `CLAUDE.md` sentence
    saying exactly that is **accurate and was deliberately left alone** — flipping it on the strength
    of the emitter merely existing would have introduced a false claim, which is precisely how
    stale-claim defects get made. The remaining gap is tracked as the **dashboard→Codex save path**.

## 0.224.0 — 2026-07-29

**The multi-host audit closes: 42 of 42 findings fixed.**

### Fixed

- **Every agent projected to GitHub Copilot ran with ALL tools, including the ones built to have
  none** (audit MH-10, P0). Copilot gives an agent every tool unless `tools:` restricts it, and the
  projection dropped that field — so `security-reviewer`, canonically `Read, Grep, Glob, Bash,
  WebFetch` with **Write/Edit deliberately withheld**, could write files and run shell the moment it
  was used under Copilot. It now emits
  `["read","view","grep","search","glob","shell","bash","powershell","web"]` — **no `edit`**.
  - **The blocker was stale, not real.** The standing reason not to fix this was *"the complete
    Copilot tool list is NOT published at a fetchable URL."* That is true of the **hook `toolName`**
    vocabulary, whose doc pages 404. The **agent-profile `tools:`** vocabulary is a *different list*
    and **is** published — on the page the CLI's own custom-agents how-to designates as authoritative
    `[docs-verified 2026-07-29]`, which confirms the field applies to *"the Copilot CLI"*, that
    omitting it *"defaults to all tools"*, and that ***"All unrecognized tool names are ignored."***
  - **⚠ The audit's own prescribed remedy would have shipped a wrong allowlist**, by reusing the hook
    vocabulary table. The two lists overlap but differ: `web_fetch`/`ask_user`/`create` are not
    agent-profile names, and `read`/`search`/`web`/`todo`/`agent` are not hook names.
  - **Verified against a running Copilot session** (CLI 1.0.70), not only the docs: a control agent
    with no `tools:` created a file via shell; the restricted agent replied `CANNOT_WRITE` and created
    nothing; and told explicitly to leak via `curl`/`git` it returned `LEAK_FAILED`.
  - **`read` and `search` were silently dropped** — the restricted agent got exactly
    `view`/`grep`/`glob`. That is the ignored-names rule observed in the wild, and it is why each
    Claude tool maps to *every* equal-privilege spelling: a map that guessed `read` alone would have
    left every agent **with no file-reading tool at all**, a silent amputation no CI check could see.
  - **An agent's self-report of its own tools is not evidence.** Asked to list them, the probe named
    `git` and `curl`; neither exists (the leak attempt died with *"Skill 'curl' not found"*). Taken at
    face value that reads as a leaky allowlist and would have been filed as a live security hole.
    Test the behaviour — *can it write?* — never the description.

### Added

- **Gate 166** — the least-privilege projection cannot silently regress. It holds the floor by **class
  subset**, not a max-privilege ceiling: a ceiling would license `edit` for any agent declaring Bash,
  i.e. for `security-reviewer` itself. The gate's first draft used a ceiling and **could not fail on
  its own worked example**; its teeth half caught that before merge.

### Notes

- **MH-35** amended `docs/plans/2026-07-28-prompt-engineering-learn/plan.md` as §6.2a. Measuring the
  planned host detector's liveness probe showed it requires `session.cwd == project_root` *exactly*,
  and during a live Claude Code session on this repo (`cwd=/Users/matthewcorbett` vs project root
  `/Users/matthewcorbett/RavenClaude`) it does not match — so the page would render *"cannot
  determine"* while running inside the host it describes, for every `$HOME`-launched session, monorepo
  subdirectory, and worktree. It fails *safe*, so it was surfaced as a decision: **owner chose to
  accept an ancestor cwd**, with liveness still required so the reused-server wrong-host hazard stays
  closed.

## 0.223.0 — 2026-07-29

### Fixed

- **The Session card's "Recent project sessions" list was empty on every real machine, and looked
  correct while doing it.** `_mimir_encode_key` computed the `~/.claude/projects/<key>/` directory
  name by stripping the leading `/` and leaving `.` alone — so `/Users/me/repo` produced
  `Users-me-repo` while the platform writes `-Users-me-repo`. It matched nothing, anywhere.
  - **Why nothing caught it for ~7 months.** The miss path returns `exists: False`, which the UI
    renders as the same honest *"no sessions yet"* empty state a genuinely-new host produces. **A card
    that is always empty and a card that is correctly empty are pixel-identical**, so no one could
    read the defect off the screen.
  - **Why the tests couldn't catch it either.** `make_claude_home()` built its fixture directory by
    calling `_mimir_encode_key` — fixture and reader agreed by construction, so the suite asserted
    only that the encoder is self-consistent. Test 4 went further and hardcoded `"foo-bar-baz"` as the
    expected canonical name, i.e. **asserted the broken convention as correct**. This is the same
    fixture-agrees-with-reader trap the happy-path test's own comment already described for the
    nested-`usage` shape, one function away.
  - **The repo had documented the right answer all along:** the `mimir` skill's worktree rule states
    `/.claude/worktrees/foo` → `--claude-worktrees-foo`, and that double dash is only reachable if the
    leading `/` **and** the `.` both encode. The docs were right; the code never matched them.
  - Re-derived from the platform artifact, not from the reader: of **161** real project dirs on this
    machine, **161** begin with `-` and **0** contain a literal `.` `[verified 2026-07-29]`.
  - Fix: encode every `/` and `.` as `-`, with the old stripped shape retained as a second candidate
    so a host genuinely using it keeps working. New **test 3b** asserts the key against hand-written
    literals with a *"do not rewrite these to call the encoder"* note; verified to fail (3 assertions,
    exit 1) against the old encoder.
- **Every session row reported 0 events and 0 output tokens — a second, independent cause.** The
  summary loop read the **first** 50 KiB of each transcript, but a real transcript's opening 50 KiB is
  session preamble (attachments, the file-history snapshot, the first user turn) and contains **zero**
  assistant events. Measured against a 14.5 MB transcript: 0 assistant events in the first 50 KiB,
  2,395 in the file. So the counts were structurally 0 regardless of activity — including after
  0.222.x fixed the *nesting* those counts read from.
  - Replaced with `_mimir_scan_session`, a bounded streaming scan with a byte-level prefilter that
    runs `json.loads` only on lines that could matter: **14.8 MB across three transcripts parses in
    ~0.04 s**. Bounded at 64 MiB/file, and hitting that bound sets `counts_truncated`, which the UI
    renders as *"counts partial"* rather than presenting a floor as a total.

### Added

- **MCP servers are now visible, with an honest per-host wiring answer** (audit MH-19). The Host &
  context page lists the 4 MCP servers this marketplace ships, which plugins ship them, and — the part
  that matters — **which hosts actually receive them**. Today that is Claude Code only.
  - This surfaced a live defect it now reports: `scripts/ravenclaude` merges
    `<copilot-package>/.mcp.json` into `~/.copilot/mcp-config.json`, but **no generator ever writes
    that file**, so the step is a permanent no-op guarded by `[ -f ... ]` — it fails silently, and
    `status` says *"mcp: not configured"*, which reads as *"you haven't set it up"* rather than
    *"this cannot be set up."* Every one of these servers also lives in a **non-core** plugin, and the
    Copilot projection only covers core. Named in the UI with the manual workaround; the projection
    itself is separate work.
- **Subagent dispatch is visible** (audit MH-20). Each session row now shows how many subagents it
  dispatched and of which types (e.g. `33 subagents (general-purpose×15, backend-coder×7, …)`).
  Previously a session that fanned out to a dozen agents and one that did everything inline rendered
  identically.
  - **Derived-only, by contract:** a count and a type label validated against a strict charset
    (anything else counts as `unnamed` — the dispatch still happened, and under-reporting it would be
    the worse error). The `Task` block's `prompt`/`description` — the largest free-text field in the
    transcript — is never read at any length.
- Both additions cost **zero DOM elements** (6,140 / 7,026, unchanged): they render into the existing
  `#hc-root` mount and the existing session `<li>`, so no Gate 132 ratchet raise was needed.

### Notes

- `ensure-default-mode.sh` gained a comment recording that **not** matching `plan` is deliberate, not
  an omission (audit MH-32): the hook warns about modes that make the posture *weaker*, and `plan` is
  strictly more restrictive. The audit read the absent branch as a gap; a future one should not
  "fix" it.

## 0.222.3 — 2026-07-29

### Fixed

- **`GET /__sleipnir` returned HTTP 500 on the marketplace dev portal.** `do_GET` has dispatched it to
  `self._handle_sleipnir()` since the endpoint shipped, but **that method existed only in the bundled
  plugin copy** — the root dev server raised `AttributeError`, so the Activity tab's Sleipnir stables
  widget was simply broken there. The plugin copy's own docstring described itself as a *"mirror of
  the root dev server's `/__sleipnir`"* — of a method that did not exist.
  - **Gate 32 passed the entire time**, because its endpoint check regexes the *string* `/__sleipnir`,
    which appears in the dispatch line of **both** files. It compared endpoint **names** and never
    asked whether a handler existed.
  - Found by the MH-33 guard-coverage check below, which reported *"handler not found"* while looking
    for something else entirely.
- **MH-33 — two enforcement holes in the parity gate.**
  - `_ENDPOINT_RE = r"/__\w+"` is **hyphen-blind** (`\w` excludes `-`), so `/__concern-stats` was
    compared as `/__concern` and `/__knowledge-health` as `/__knowledge`. Two endpoints differing only
    after a hyphen compared as **identical** — and the truncation was visible in the gate's own PASS
    output all along, reading as if those were the real names.
  - The server's invariant — *"any NEW data-returning GET endpoint MUST call
    `self._local_request_ok()` first"* — was **a comment, enforced by nothing.** That guard is the
    DNS-rebinding / cross-origin defense. It is now checked statically, scoped to `do_GET`'s body.
    *(The first version scanned the whole file, flagged the POST-only `/__classify`, and looked
    exactly like a real security hole — it was a broken check. Diagnose before concluding.)*
- **MH-27 — the Copilot manifest advertised seven slash commands on a host that has none.** Its
  `description` ended *"Slash commands: /init-agent-ready, /wrap, /set-posture, /dashboard, /forge,
  /wireframe, /reset-plugin-cache"* while the plugin's own CLAUDE.md states plainly that Copilot CLI
  has no user slash commands. Corrected **in the projector, not the canonical manifest** — the
  sentence is true for Claude Code and false only for this host, so the host-specific correction
  belongs in the host's projection; editing the canonical file would make it wrong for Claude Code.

## 0.222.2 — 2026-07-29

### Fixed

- **The run-state monitor was silently inert on macOS** (`monitors/watch-run-state.sh`). `newest_log()`
  used `find … -printf '%T@\t%p\n'` to pick the newest `hook-events.jsonl`, but `-printf` is a GNU-find
  extension — stock macOS/BSD `find` exits with `unknown primary -printf`, the `2>/dev/null` swallowed
  it, and the pipeline returned empty. Result: on every macOS session the monitor idle-polled forever
  and **never emitted a single push notification** — the entire push-notification complement to the
  read-only Heimdall/Víðarr tabs was dead on that host. This is the same silent, unconditional,
  every-macOS-session failure class the "macOS doors" milestones (v0.193.0–v0.199.0) exist to close,
  and it was not covered by `check-macos-portability.sh`. Replaced with a portable enumeration that
  resolves the newest file by mtime itself, using the repo's established `stat -c '%Y' || stat -f '%m'`
  BSD fallback (as in `worktree-guard.sh`); bash-3.2-safe (no `mapfile`/assoc-arrays/`globstar`) and
  space-safe (`-print0` + NUL read). Behavior on Linux/CI is unchanged. **Migration:** none — a
  Claude-Code-only, opt-in (`on-skill-invoke:spawn-team`) monitor; macOS consumers now receive the
  guardrail notifications that were previously silently dropped.

## 0.222.1 — 2026-07-29

### Fixed

Four surfaces that told a reader something untrue or unusable. All content; no behaviour change.

- **MH-28 — the claim-grounding double standard's last call site.** `init-agent-ready.md` still told
  every new repo that *"AGENTS.md is read by Cursor / Codex / Aider / Copilot natively"*. **That is
  false for Aider** (it reads `CONVENTIONS.md`, opt-in only) and unconfirmed for Cursor. Replaced with
  a per-host list carrying each basis, and a pointer to `host-support.json` as the authority. The
  sibling call site was already closed by the MH-23 rewrite.
- **MH-34 — the pre-PR checklist requires network installs a sandbox blocks, and nothing said so.**
  `npx --yes prettier@…` and `pip install ruff` both download, and Codex's default
  `sandbox_mode = workspace-write` has network **off**. An agent got a denial and no way to name the
  cause — while this repo's own Capability Grounding Protocol requires *"read the actual error first
  and name its specific mechanical cause."* The block now names `sandbox_mode`, lists fixes
  cheapest-first, and says plainly **not** to skip the steps (CI runs them whole-tree anyway).
- **MH-36 — two different Geminis were conflated.** `AGENTS.md` now separates the supported **host**
  lane from the Power Platform visual-QA **model** integration. They ran together because the second
  was the repo's only Gemini anything and was buried in a skill resource, so a reader looking for
  "Gemini support" found neither.
- **MH-22 — the consumer dashboard pointed at a portal consumers do not have.** The Plugin-variables
  intro said to *"open the plugin in the portal's Marketplace section"* — but the portal is
  `index.html` at the **marketplace repo** root, and a consumer who installs the plugin and runs the
  dashboard gets that page and no portal at all. It now points at the plugin's own directory and says
  what the old text got wrong. **Zero DOM**: the first draft came in at +1 and was trimmed rather than
  spend a ratchet raise on one element.

## 0.222.0 — 2026-07-29

### Added

- **Gemini CLI is a supported host** (multi-host audit MH-30 + MH-41). The audit framed this as a
  decision — support it, or formally unsupport it and strip the 17 name-checks. **Build won**, and the
  research is why: Gemini's hook contract turned out to be **nearer Claude Code's than Copilot's is**.

  | | Claude Code | **Gemini CLI** | Copilot CLI |
  |---|---|---|---|
  | stdin fields | `session_id`, `cwd`, `tool_name`, `tool_input` | **identical names** | `toolName`, `toolArgs` (JSON *string*) |
  | Blocking | `exit 2` + stderr | **identical** | JSON `permissionDecision` |
  | Matcher | yes | **yes**, with regex | none in the native format |

  - **So it is a shim, not an adapter** — blocking needs *no* translation, which is the opposite of
    Cursor (where a malformed response silently allows, so the deny had to be a fixed literal).
  - **The one real translation is the tool-name vocabulary**, and it is not optional. Gemini sends
    `run_shell_command` / `read_file` / `write_file` / `replace`; the guardrails dispatch on Claude's
    PascalCase and fall through to `*) exit 0` on anything unrecognised. **That exact mismatch is
    MH-01** — under Copilot the tribunal was fully wired and reviewed *nothing* because `bash` is not
    `Bash`. Shipping unnormalised would have reproduced it on a fifth host, looking wired throughout.
    **Gate 164** asserts the mapping name by name, with teeth.
  - **`GEMINI.md` @-imports `AGENTS.md`** rather than receiving a copy. Gemini supports `@file.md`
    imports, making it the **only** non-Claude host that can include the canonical file — nothing to
    project, nothing to drift. (Aider needed a real projection only because `CONVENTIONS.md` has no
    import mechanism.)
  - Hooks are **projected** from the canonical manifest (17 wired, 8 explicitly skipped) and **merged**
    into `.gemini/settings.json` rather than overwriting it — that file also carries the user's model,
    theme and MCP config. **Gate 165** additionally asserts every emitted matcher is in *Gemini's*
    vocabulary: one left in PascalCase would register a hook that can never fire.

### Honest scope

The **layout gate is not enforced** on Gemini. Its path arrives as argv, and Gemini's `tool_input`
path *field name* is unverified — the docs' rewrite example shows `filepath`, other tools may use
`file_path`. Wiring it would have registered a guard that receives no path and **silently no-ops,
which is worse than not wiring it because it would look enforced.** CI is the backstop, and the skip
list ships inside `.gemini/settings.json`. One line to enable once the field name is read.
`Stop` / `UserPromptSubmit` are unmapped for the same reason: `AfterAgent`/`BeforeAgent` are plausible
by name, and mapping a lifecycle event by name-similarity is how a lane asserts coverage it lacks.
**This lane is docs-verified but UNTESTED against a running Gemini CLI.**

## 0.221.1 — 2026-07-29

### Fixed

- **P0 — the session card reported the session's *opening* permission mode as its current one**
  (multi-host audit MH-06). It said `default` while the session was in `auto`. **A permissions surface
  reporting a laxer state than reality is the bad direction to be wrong in** — it tells an operator
  they are more constrained than they are.
  - **Two independent causes, and fixing either alone leaves the bug.** The loop kept the *first*
    `permission-mode` event — in the very same pass that deliberately *overwrites* to keep the newest
    model, two lines above. One loop, two opposite policies, one of them wrong. And
    `_mimir_iter_jsonl_bounded` read the first 50 KiB from offset 0, so on any transcript past the cap
    the scanned slice is the **oldest** part of the session; even a correct last-wins loop would have
    reported the last value *from the opening minutes*.
  - The reader gained an opt-in `from_end`. Only the caller that claims *current* / *last used* sets
    it; the aggregate caller (counts, token sums) stays on the head read, because neither end is more
    correct there and flipping it would silently change reported numbers.
  - **`last_model` was wrong the same way** and is fixed by the same change — its comment said "newest
    seen in scanned slice", which was honest, but the slice was the wrong end of the file.
  - **Gate 163** asserts both server copies, on a fixture deliberately larger than the cap so head and
    tail genuinely differ — and asserts that *fixture validity* first, because on a small enough file
    both ends agree and every other assertion would pass for free.

## 0.221.0 — 2026-07-28

### Fixed

- **The tribunal denied the documentation it requires** (multi-host audit MH-42).
  `xc.tribunal-self-disable` is critical, `pre_llm_deny`, `always_screen` — no seat convenes and there
  is no override short of the dashboard. Its regexes are **shell-shaped**, but for a file shape the
  screened text is `"<path>\n<content>"`, so they ran over ordinary **prose** and matched:
  - a markdown blockquote whose first token is a plugin `hooks/`/`scripts/` path, and
  - an angle-bracket placeholder — a `<core>` token *ends* in `>`, so `<core>/hooks/…` is literally
    `>` followed by a substrate path.

  **Blast radius: every audit, plan, decision record, postmortem and knowledge file that cites a
  substrate path with `file:line` — exactly what this repo's own Claim-Grounding protocol requires.**
  It fired **seven times in a single session**, including twice while the fix was being written, and
  once on marking a brand-new hook executable.
  - **The narrowing is deliberately minimal:** only `self_disable`, only for file shapes, and only
    when the **path alone** is also clean. The §B.9.3 hard rules still screen the full text; the
    shell-shape screen is untouched; `screen_error` still fails closed; and the narrowing is recorded
    in the Sága entry rather than happening silently.
  - **Why it is not a weakening:** a substrate *write* is caught by the target-path screen, which
    resolves realpaths and inodes (catching symlinks and hardlinks) and runs **after** the regex
    screen, re-asserting the deny. Canonicalization is strictly stronger than a regex over content —
    this removes a redundant, lossy check, not the load-bearing one.
  - **Gate 162 is bidirectional by necessity**: a one-directional test on a control like this would be
    indistinguishable from having turned it off. Its teeth force the narrowing *unconditionally* and
    prove a substrate write is still denied.

### Note on how two files are written

`test-gate162-…` and the fixtures inside it assemble substrate paths and the curl-pipe-shell pattern
**at runtime** rather than as literals — because with them inline, the shell-shape screen denies the
Write that creates the test. That is the same false-positive family, met while building the gate for
it, and the file says so rather than leaving a future reader to rediscover it.

## 0.220.0 — 2026-07-28

### Added

- **Cursor is a supported host** (multi-host audit MH-13 + MH-25). It had **zero in-loop enforcement**:
  not the layout gate, not `guard-destructive`, not the command-review tribunal, not the runaway brake.
  CI was the only backstop, and CI runs after the damage.
  - `ravenclaude install --host cursor` wires **two** surfaces Cursor has and this repo served neither
    of: `.cursor/hooks.json` (guardrails) and `.cursor/rules/*.mdc` (Cursor's own rules convention,
    which its docs call the *scoped alternative* to `AGENTS.md`, not a superset).
  - Hooks are **projected from the canonical manifest** — 20 wired, 5 explicitly skipped with reasons
    that ship in the file. Not a second hand-maintained list: MH-12 had just proved those drift
    silently, and repeating that on a new host was the obvious trap. **Gate 160** additionally asserts
    something is actually wired to the enforcing event, because a lane that enforces nothing would pass
    a pure accounting check while protecting nobody.
  - The **glob-scoped layout rule** is the point of the `.mdc` half: a rule that fires on the paths it
    governs is exactly what a flat, always-on `AGENTS.md` structurally cannot express.
- **⚠ The safety fact that shaped every line of it: CURSOR FAILS OPEN.** *"malformed JSON response
  silently allows command instead of blocking"* `[docs-verified — Cursor's own bug tracker]`. Every
  other supported host fails **closed** on a broken hook. So on Cursor a guardrail that emits
  slightly-wrong JSON does not fail loudly — **it vanishes.** The adapter therefore emits its deny
  verdict as a **fixed literal with no interpolation**, carries **both** documented and
  community-reported field spellings, and reserves silence for genuine allows. **Gate 159** over-covers
  that path deliberately, including a hostile command string that must never reach the payload.

### Fixed

- **MH-13's own event list was incomplete.** It named five events from third-party write-ups; Cursor's
  published set is a superset that includes Claude-named events (`preToolUse`, `postToolUse`,
  `sessionStart`, `subagentStart`, `stop`, `preCompact`) and supports `matcher`. Third-party
  corroboration has now been wrong three times this release — `.codex/skills`, the Copilot version
  floors, and this — against zero times for a primary source.

- **Aider gets its real mechanism** (MH-26). Aider reads `CONVENTIONS.md`, and **only on explicit
  opt-in** — `--read`, or a `read:` entry in `.aider.conf.yml`. It does **not** read `AGENTS.md`; that
  claim was false and was corrected in prose earlier, which left Aider users with nothing *actionable*.
  `install --host aider` now projects `AGENTS.md` → `CONVENTIONS.md` **and** writes the opt-in. Both
  halves were required: a pointer file would not be read, and documentation alone would not opt in.
  A renamed upstream section **raises** rather than silently shipping a file with a hole (**Gate 161**).
  - **This is the only lane that bridges no enforcement.** Aider has no hooks API, so nothing here can
    gate an Aider session in-loop and CI is the only backstop. The generated file leads with that
    rather than implying coverage — and the gate fails if that warning is ever removed.
- **Both hook projectors now invoke their adapter via `bash "…"`** rather than executing it directly,
  so the wiring survives a checkout that lost its exec bits (Windows, zip exports, the installer's own
  `cp -r` fallback). Worth noting the asymmetry: on Copilot that failure is **loud** (`preToolUse`
  fails closed, so a non-executable adapter denies everything and is noticed in seconds); on Cursor it
  is **silent**. Same fix, very different blast radius.

### Honest scope

`preToolUse`/`postToolUse` are **not** wired: their per-event payload fields were not published on the
page verified, and guessing a payload shape on a host that treats a wrong guess as *allow* is the trade
this repo refuses. The layout gate and web-access guard are **not** enforced on Cursor either — no
verified event carries a file path pre-write or an agent web fetch — and the generated rules say so
rather than implying coverage. **This lane is docs-verified but UNTESTED against a running Cursor**;
there is no Cursor binary here, and `host-support.json` records that limitation rather than eliding it.

## 0.219.0 — 2026-07-28

### Fixed

- **14 shipped guardrails never fired under GitHub Copilot CLI** (multi-host audit MH-12). The Copilot
  hooks file was a hand-written list inside the installer. It wired **11**; the canonical manifest
  registers **24**. Missing entirely: the web-access guard, the worktree guard (both modes), both
  Muninn hooks, the delegation nudge, the recursive-spawn guard, the posture reapply, and more — and
  **nothing enforced that the two lists agreed**, so the drift was invisible and grew every release.
  - Now **projected** from the canonical manifest by `scripts/generate-copilot-hooks.py`: **23 wired**,
    2 explicitly skipped **with reasons that ship in the generated file**, so a consumer can see what
    is *not* protecting them. **Gate 158** fails the build if any canonical hook is neither wired nor
    explicitly skipped — silent omission was the defect, so silence is what the gate forbids.
  - The adapter **mode is derived**, not listed (`PreToolUse` + argv ⇒ `file-pretool`, else
    `bash-pretool`, etc.), so adding a hook to the manifest is the only edit ever needed.
- **"Copilot CLI has no per-tool matcher" was FALSE** (MH-24 — and that entry *was itself* the audit's
  self-described *"highest leverage in the ledger: the guardrail against the next MH-01"*). Copilot
  supports **two hook formats selected by event-name casing**: native camelCase has no tool matcher,
  but **Claude-compatible PascalCase applies Claude's matcher semantics**
  `[docs-verified — docs.github.com/en/copilot/reference/hooks-configuration]`, honored from **1.0.62**
  (*"matchers … now honored instead of silently dropped"*). **The generated file has always used
  PascalCase**, so matchers were available the whole time and simply unused. They are now projected.
  Below 1.0.62 an unhonored matcher means the hook fires for every tool — exactly today's behaviour —
  so this degrades safely and is applied unconditionally.
- **A gate that tested the implementation instead of the outcome.** Gate 114's Copilot-parity check
  grepped the installer for the literal strings `userpromptsubmit` / `stream-prompt-attribute.sh`.
  When the wiring became a projection those literals vanished and the gate failed — while the hook was
  still wired. It now **runs the projector and asserts the hook is in the emitted config**. A gate that
  greps for *how* something is implemented breaks every time the implementation improves, and trains
  the next maintainer to fix the gate rather than read it.

## 0.218.0 — 2026-07-28

### Fixed

- **Four surfaces that overstated their own scope** (multi-host audit MH-37 · MH-38 · MH-39 · MH-29).
  One shape, four places: a surface describing a capability without saying where it stops.
  - **The Learn concept card** taught, as settled fact, that *"a hook adapter translates the I/O
    envelopes so the **unmodified** hook scripts run under Copilot"* — the marketplace's own teaching
    surface making exactly the unhedged capability claim its Claim-Grounding protocol forbids. True of
    the *translation*, false of the *coverage*: **12+ shipped hooks are not in the Copilot hooks file
    at all** and never fire there (MH-12, still open). Now scoped to *"for the hooks the installer
    actually wires"*, with `host-support.json` named as the authority if the two disagree.
  - **The Help drawer held exactly two onboarding lanes** — Claude Code and Copilot CLI — that
    cross-linked only each other, while its own self-description named them as the whole world. Codex
    had become a genuinely supported host one release earlier. A **third lane** now covers Codex
    (install command + the hash-trust warning, the one thing that silently disarms that host) and says
    plainly that Cursor, Aider and Devin Desktop are **not wired at all** — *"a gap, not a hidden
    feature."* Owner-approved **+12 DOM**; see the ratchet row for why the first estimate was 4× low.
  - **The Prompt Builder never said which models it targets.** Its linter rules are
    Claude-version-specific (prefill is a 400 on Claude 4.6+; the imperative-stacking penalty is tuned
    to current Claude behaviour), and a Copilot operator routing GPT or Grok was handed them as
    universal prompt hygiene. The lead now says so.
  - **"Windsurf" was a stale brand** at the last two call sites — Cognition rebranded it **Devin
    Desktop on 2026-06-02**, and `docs.windsurf.com` now 307-redirects to `docs.devin.ai`. A reader
    would reasonably have taken "Windsurf" and "Devin" for two hosts on separate tracks. Both now name
    the product currently, and say explicitly they are **one product under two names**.

## 0.217.0 — 2026-07-28

### Fixed

- **Claude-only invocation was taught as universal** (multi-host audit MH-18). `bin/rc` shipped in
  v0.158.0 precisely to give non-Claude hosts a launch verb, and was never wired to the surfaces that
  teach invocation. Three of them, one root cause:
  - **The Commands catalog** renders **533** cards, every one of which said *"copy it, then paste into
    Claude Code"* — with no alternative even where one exists and is documented in the same file. Cards
    now carry an **"any host:"** equivalent where a real one exists, and the tab intro says plainly that
    the rest are Claude-Code-only and that this is *"a gap, not a hidden feature."*
    **Only verified verbs appear:** `bin/rc` implements exactly three (`dashboard`, `streams`,
    `converge`), so exactly two commands get a mapping. Inventing a plausible-looking equivalent would
    reproduce the very defect — an invocation confidently taught to a host that cannot run it.
    Deliberately **not** stamped "Claude Code only" onto the other 530 cards: they already name the
    host, and 530 repetitions is noise, not honesty.
  - **The posture editor** promised *"you pick Deny / Ask / Allow"* with no scope note, while Save &
    apply writes only `.claude/settings.json`. It now states where those levels actually bind — Claude
    Code natively, Copilot via the wired hooks + command review, Codex via its own OS sandbox, and
    advisory everywhere else with CI as the backstop. Same false-assurance shape the Pipeline tab had
    (MH-04).
  - **`AGENTS.md` § Setup** showed only the Claude Code slash commands — so the first substantive thing
    a Codex or Copilot agent read (their onboarding says *"read AGENTS.md end-to-end, don't skim"*) was
    a procedure it structurally could not execute, followed by a pointer to a command that does not
    exist on its host. Now a **three-row host table**, each row carrying the command that actually
    works, with the launcher given by **full path** (per MH-11, a bare `rc` can be shadowed) and
    `/dashboard` marked as the Claude Code shorthand.
  - **Zero DOM cost**, verified: the Commands tab is JS-built from `#commands-payload` so its cards are
    uncounted, and the posture note is plain text inside an existing element. Both surfaces stayed at
    6,128 / 7,014 — no Gate 132 ratchet raise needed.

## 0.216.0 — 2026-07-28

### Added

- **`dashboard_autostart: off | serve | open` — the dashboard can now come up on its own at
  session start.** The only auto-launch RavenClaude ever shipped was the Codespace devcontainer
  (`postStartCommand` + `portsAttributes.onAutoForward: openBrowser`); on a local/desktop machine
  **nothing** started the dashboard at session start, so "it didn't open automatically" was
  correct-by-design and completely undiscoverable. New `SessionStart` hook
  `hooks/dashboard-autostart.sh` reads the knob from `.ravenclaude/comfort-posture.yaml` —
  `serve` starts the local server headless, `open` also opens a browser tab. **Opt-in;
  absent ⇒ off**, and it no-ops after a single `grep` for everyone who hasn't set it, so an
  update changes nothing until you opt in. **It never duplicates:** it probes
  `127.0.0.1:<port>/__csrf` first and stands down if a dashboard already answers there, so
  concurrent sessions in one project can't each spawn a server and steal focus with a new tab.
  **Honest limit:** that probe answers "is a dashboard live on this port?", not "is it *this*
  project's dashboard" — if another project holds the port, the hook stands down rather than
  starting a competing one. Fail-safe (EXIT trap armed first; always exits 0 — a SessionStart
  hook cannot block, and a dashboard that fails to launch must never be why a session doesn't
  start), and bash-3.2/BSD-clean per the macOS-door milestones. **Gate 151**
  (`hooks/tests/test-gate151-dashboard-autostart.sh`) drives the real hook against a recording
  stub launcher: 5 must-not-launch cases (no posture / `off` / key absent / already-live /
  an unrecognised value), 2 must-launch cases asserting `--no-open` is present for `serve` and
  absent for `open`, every case exits 0, plus a teeth half that neuters the mode gate and proves
  `off` then launches. The key is also wired into the dashboard's `state`/`emitYaml`/
  `applyGuardrailConfig` (covered by Gate 35) — **not** cosmetic: `emitYaml` rebuilds the whole
  posture file from `state`, so a key with no state slot is silently **deleted** on the next
  Save & apply (the v0.61.0 data-loss class).
- **…and it ships with a visible control** (Settings panel, beside the other behavioral flags): a
  three-option select — *off* / *serve* / *open*. It was very nearly YAML-only, because Gate 132's
  budget sat at exact zero slack — which would have reproduced the very discoverability problem that
  started this release (a setting nobody can find is a setting nobody uses). **Owner-approved +6
  ratchet raise** on both surfaces (6,114 → 6,120 and 7,000 → 7,006), tails lifted in lockstep to stay
  monotonic. The +6 is **measured, not estimated**: the first cut came in at **ten** elements (a
  behavioral-flag `<span>`, an explainer `<p>` and two `<b>`) and would have silently blown the
  approved figure. It was trimmed to exactly six by making the ⚙ marker a *glyph in the heading text*
  rather than the badge element, and moving the explainer into a `title=` attribute — both zero-cost
  substitutions that keep the house conventions. Anyone adding a heading, description or icon here
  must re-measure rather than assume +6 still holds.

### Changed

- **The portal is now on-brand with the RavenPower commerce site — the teal secondary accent is
  retired.** `dashboard.html` already matched the site *exactly* (canvas `#07080a`, panel `#0c0e12`,
  accent `#56D08A`, hover `#6EE0A1`, text `#f5f7fa`, muted `#9aa3b2` — 6/6 byte-identical, with both
  Inter/Space Grotesk and both motion easings already shared). `index.html` was the one surface off
  brand: it aliased its accent to `--rc-teal` (`#3aa391`). Its five `--teal*` variables now resolve to
  the green tokens — a **repoint, not a rename**, so all ~20 usage rules are unchanged and none could
  be missed. Teal was verified purely decorative on that surface (links, nav-active, brand mark, hero
  hairline, chips, buttons) — no semantic distinction was collapsed.
- **Radii pulled to the site's sharper scale** — `--rc-radius-sm` → `4px` and `--rc-radius-lg` → `10px`
  now match the commerce `--radius` / `--radius-lg` exactly (dashboard was `8px`/`12px`), with the
  intermediate steps tightened in proportion. This was the widest measured drift once the palette was
  confirmed identical, and it is most of why the site reads crisp rather than soft. A 5-step scale is
  kept (the site ships 2) because an admin surface has more component sizes than a marketing page.
- **The commerce per-discipline tints are now tokens** — `--rc-tint-pp` (lavender), `--rc-tint-bi`
  (teal-mint), `--rc-tint-web` (copper), plus `--rc-tint-ai` aliased to the accent. Declared only;
  wiring them to plugin categories is deliberately a separate step.
- **Deliberately NOT adopted: the site's spatial rhythm** (`--container`, `--gutter`,
  `--section-y: clamp(80px, 12vw, 140px)`). That is marketing-page rhythm; applying it to a
  6,114-element admin surface would multiply scroll length on the posture editor and run feeds and
  partly reverse the v0.208.0 density re-cut. Owner-ratified: adopt the site's *proportions*, keep the
  dashboard's density.
- **Every change here is CSS/token-only, so Gate 132's DOM budget did not move** (6,114 / 7,000
  unchanged) and no concept SVG re-render was triggered — the palette was already identical, so the
  Mermaid→token normalizer is untouched.

### Fixed

- **Two accessibility defects surfaced and fixed by the accent unification** — one pre-existing, one
  that would have been introduced:
  - **Pre-existing:** the portal's primary button was `color: #fff` on teal — **3.08:1, already failing
    WCAG AA** before this change. Now `var(--bg)` ink on green: **10.29:1 dark / 4.98:1 light**.
  - **Nearly introduced:** mapping `--teal-2` to `--rc-accent-2` measured **4.04:1 on the light
    canvas** — a regression for every inline link, since `--teal-2` is body-size *text* on that surface
    (links, nav-active, eyebrows, chips). `--rc-accent-2` is documented as "AA-large / UI" only. It maps
    to `--rc-accent` instead: **10.29:1 dark / 4.98:1 light** — also an improvement on the teal it
    replaces, which was itself a marginal 4.45:1.
  - The site hardcodes `color: #000` on its accent; we deliberately use `var(--bg)` instead, because the
    site has no light theme and `#000` on the light green measures **3.9:1**. Mimic the intent, not the
    literal value.
  - **The focus ring collapsed to one colour.** Two rings existed because the system had two accents;
    `--rc-focus-ring` was still teal in both themes and would have been the only teal left rendering.
- **The Prompt Builder was homed under a different destination on each surface, so the portal
  hid it.** v0.214.0 moved the nav link "Learn & Help" → **Control** on the standalone
  `dashboard.html`, but the portal (`index.html`) was never moved with it: `DASH_OWNER` still
  mapped `prompt-builder` → `catalog`, and the clickable link lived in the Catalog accordion —
  which `renderNav` only emits when Catalog is the **active** nav item. So on the portal the
  Prompt Builder was invisible until you first clicked Catalog, and it was absent from Control
  where the release notes said to look. Fixed by homing it under `control` on the portal too,
  first in the sub-nav (above The Thing), matching the standalone's slot exactly.
- **Gate 144 could not see the skew — it asserted presence, not placement.** The portal half of
  `scripts/check-prompt-builder-render.mjs` only checked that `DASH_OWNER` had *some* entry for
  `prompt-builder` and that *some* `href="#/prompt-builder"` existed anywhere in the file; both
  were true throughout the regression, so CI stayed green across v0.214.0 and v0.215.1. The gate
  now **derives** the home destination from the folded standalone `ds-nav` chrome (present on both
  surfaces, so it is a single source of truth rather than a hardcoded expectation) and asserts the
  portal's `DASH_OWNER` **and** the destination's own sub-nav branch both agree with it. Two new
  must-fail halves verified: regressing `DASH_OWNER` back to `catalog` and moving the link out of
  the Control branch each fail the gate (exit 1). **Migration:** none — no storage-key or route
  change; `#/prompt-builder` resolved before and resolves now.
- **`scripts/render-concepts.py` could not render on a host where puppeteer fails to resolve its own
  browser — which is every concept diagram, and the post-merge `regenerate-artifacts.yml` self-heal.**
  mermaid-cli drives puppeteer-core, which locates Chrome itself; that resolution can fail even when the
  browser is correctly installed (reproduced 2026-07-28 on macOS/arm64: Chrome 148.0.7778.97 present and
  complete at 353 MB, yet every render died with `Could not find Chrome (ver. 148.0.7778.97)`). The script
  passed no `env=` to `subprocess.run`, so there was no way to correct it short of exporting a variable by
  hand. It now discovers a Puppeteer-managed Chrome and supplies `PUPPETEER_EXECUTABLE_PATH` — but only as
  a **repair**, never as the default path:
  - **Attempt 1 is byte-for-byte the historical invocation** (puppeteer's own resolution, `env` inherited).
    Only if that fails does the fallback engage, and the chosen executable is then cached for the rest of
    the run so the remaining diagrams don't each pay a doomed first attempt. **This ordering is
    load-bearing:** committed SVGs are byte-compared and text metrics move with the browser build — the
    same 2-node diagram rendered 12,520 bytes under Chrome 148 and 12,453 under 151 in testing, so
    substituting a different engine on a host that already worked would silently churn every committed SVG.
  - **An operator-set `PUPPETEER_EXECUTABLE_PATH` always wins** and is never second-guessed.
  - **Truncated downloads are rejected, not handed over.** The cache entry that caused this held a
    plausible 68 KB launcher stub at `Contents/MacOS/…` while missing `Contents/Frameworks` entirely — so
    `is_file()` and `os.access(X_OK)` both passed on a browser that could never launch. `_looks_complete()`
    requires the bundle's `Frameworks` payload (or, off macOS, a >1 MB executable); verified bidirectionally
    against the real 353 MB good bundle (accepted) and the preserved 448 KB broken one (rejected).
  - **Failures now carry an actionable hint** naming both observed causes — no managed Chrome at all, or a
    truncated one, including the trap that `puppeteer browsers install` **silently no-ops** when the version
    directory already exists (so it must be moved aside before reinstalling).
  - Deliberately **no `shutil.which("google-chrome")` fallback**: a system Chrome is an arbitrary version,
    and byte-reproducible SVGs are this renderer's contract. Failing loudly with an install hint beats
    silently rendering against a different engine.
  Verified end-to-end through the real `_render_one` path: fallback engages once and caches, an operator
  override is honored on attempt 1, `--check` reports all 58 concepts in sync, and the mutated-manifest
  gate still fails as designed. **No committed SVG changed.**
- **The Copilot lane never said the Prompt Builder was a browser tab.** `copilot/AGENTS.md`'s
  generated dashboard block told a Copilot session how to *launch* the dashboard but never named
  what is in it — so "where's the prompt builder?" in a Copilot terminal had nothing to route on
  and looked like a missing feature. The block now names it (`#/prompt-builder`, under Control),
  says plainly that nothing in a terminal session renders it, and points at `dashboard_autostart`.
- **OpenAI Codex CLI is a supported host** (multi-host audit MH-07 + MH-08 + MH-17, shipped together).
  `ravenclaude install --host codex` wires the lane: all **50 skills** symlinked into
  `<project>/.agents/skills/`, and `<project>/.codex/hooks.json` written in the **Claude-shaped**
  schema. Verified end-to-end in a scratch project.
  - **No adapter, and there must never be one.** Codex speaks the Claude hook contract natively —
    identical PascalCase events, identical stdin fields, identical `exit 2` blocking, identical
    PascalCase tool-name *values*. Copilot needed a 456-line generator plus ~300 lines of envelope
    translation and a tool-name map; Codex needs none of it. Reading Codex through Copilot's model is
    the mis-scoping that made this lane look expensive for months.
  - **The one real difference is two absent environment variables.** `CLAUDE_PROJECT_DIR` (25 hooks
    read it) and `CLAUDE_SESSION_ID` (14 read it) are not in Codex's environment, so the guardrail
    substrate would stay dark. A new ~100-line wrapper lifts them out of the **stdin payload** — the
    documented, reliable source — passing stdin through **byte-identical** and propagating the hook's
    exit code **verbatim** (exit 2 = block). **Gate 155** proves all four invariants with two
    must-fail halves; without them, "exit 2 propagates" would be an assertion nobody had seen fail.
  - **Note what this avoided:** the existing `_rc_host_env` alias falls back to `CODEX_PROJECT_ROOT` /
    `SESSION_ID` / `PROJECT_DIR` — **none of which are in Codex's documented environment.** It looked
    like the fix and closed nothing. The audit's own remedy called for editing all 18 hooks to call
    it; that would have changed nothing. **No hook was modified.**
  - **MH-17 shipped in the same commit, deliberately.** Codex tracks hook trust **by hash**, so every
    `git pull` — this repo's entire update model — invalidates each changed hook and Codex **skips it
    until re-trusted**. Nothing announces it, because the SessionStart banner *is itself a hook*.
    Shipping the installer alone would have manufactured the silently-inert-guardrail class this
    audit exists to close, on the host it was closing it for. The re-trust notice fires at install,
    at **`update`** (where the disarm actually happens), in `status`, and inside the generated file.
    `--dangerously-bypass-hook-trust` is named **only to refuse it** — it turns an honest "your
    guardrails are off" into a dishonest "your guardrails are on". `requirements.toml` managed hooks
    are documented as the only unattended-survival path.
  - **Backward compatible:** host auto-detection resolves *any* ambiguity to `copilot`, so an
    existing user who happens to have `codex` on PATH gets a byte-identical install to yesterday's.
  - **The comfort posture now reaches Codex's OS sandbox** (MH-16 part 2). `emit-codex-config.py`
    projects it onto `sandbox_mode` / `approval_policy` / `[sandbox_workspace_write] network_access`.
    **The governing rule is one-directional: never silently weaken** — write when absent, tighten
    freely, and *refuse* to loosen a hand-set value, printing the exact line to change. The rejected
    alternative (mirror the posture both ways) would let a dashboard click silently widen a sandbox
    somebody had deliberately locked down. `danger-full-access` and `approval_policy = "never"` are
    never emitted at any posture. **Gate 156**, two must-fail halves.
    - **Two caveats stated at install time, not buried:** the mapping is **coarse** (two enum keys
      cannot express twelve categories), and a project `.codex/config.toml` **loads only in trusted
      projects** — a second trust gate beside the hook hashing, so writing the file is not the same as
      bounding the session.
    - **A TOML placement bug caught in testing:** a root key appended below an existing `[table]`
      becomes a member of that table — valid TOML, wrong meaning, invisible in a diff, and Codex would
      have fallen back to its default sandbox while the tool reported success. Fixed with a placement
      anchor, pinned by a must-fail half, and verified with an independent TOML parser rather than by
      eye. No `tomllib` is used at all: it is stdlib only on 3.11+, and stock macOS ships 3.9.6.
    - **A second bug, and the sharper lesson:** `network_access` is a TOML **boolean**, so writing it
      quoted produced the *string* `"false"` — not what Codex expects. It shipped broken in the
      **tighten** path (the security-relevant direction), and **Gate 156 was green while it was live**,
      because the self-test never exercised a boolean tighten. A gate is only as good as the paths it
      reaches. Now asserted both directions and confirmed by a parser reporting `type: bool`.
  - **Honest gap, printed at install time rather than discovered later:** MCP (`.codex/config.toml`
    `[mcp_servers.*]`) is not wired — a bad merge would clobber a hand-tuned config. The generated
    agent projection is
    **deliberately deferred**: there is no verified Codex agent-file contract in this repo, and
    projecting 15 agents from a guessed schema is the same "don't guess at a contract" call made on
    the Copilot `tools:` gap.
  - The Pipeline tab's host-scope sentence had a **hardcoded** "nowhere else" list beside its derived
    supported list, so flipping Codex on made it name Codex as supported and unsupported *in the same
    sentence*. Both halves are now derived from the map.
- **`codex-onboarding` → `external-agent-onboarding`, and its evidence base rebuilt** (MH-23).
  **⚠ MIGRATION — the only breaking change in this release.** The skill directory is renamed, so a
  consumer with the old skill symlinked will have a dangling link after `/plugin marketplace update`.
  **Fix: re-run `ravenclaude install` (or `rc`)** — one command, and already the documented update
  path. Skill count is unchanged at 50.
  - **The old name was the defect.** It owned the Codex discovery keyword while the content was
    almost entirely Copilot/Cursor — no Codex row in its version table, no `codex --version`, and no
    mention of `.agents/skills`, `sandbox_mode`, or `/hooks`. Same name-laundering class as Gate 70
    (MH-31), one directory away.
  - **Every factual row cited `/tmp/research-codex-2026-updates.md` — a path that does not exist**
    (`No such file or directory`, verified). This repo's own rule requires a durable claim to cite a
    check a later reader can run; a `/tmp` path is unfalsifiable by construction.
  - **The version table was not merely unsourced — it was wrong.** Re-derived verbatim from the
    [copilot-cli changelog](https://github.com/github/copilot-cli/blob/main/changelog.md): the
    claimed *"preToolUse silent-allow regression fixed (1.0.59)"* and *"diff-not-reported-to-ACP fixed
    (1.0.48)"* **appear nowhere in it**, and the config-leak fix is **1.0.57**, not 1.0.56. Rows that
    could not be re-sourced were **deleted, not re-dated**. The real safety floor is **1.0.52**
    (*"Hooks … now fire correctly for sub-agent tool…"*) — below it a **sub-agent's tool calls are
    not hooked at all**, so a subagent runs Bash past every guardrail while `install` reports success.
  - **That floor is now enforced, not just documented.** `ravenclaude install`/`status` run
    `copilot --version` and warn below 1.0.52 — the same silent-disarm shape as Codex hash-trust, on
    the flagship non-Claude host, previously checked by nothing. **Gate 157**, two must-fail halves.
  - **The check itself had to be made fail-safe, and that bug was real:** under `set -euo pipefail` a
    bare `$(… | grep …)` on an unparseable version **aborted `ravenclaude status` outright** (verified
    exit 1). A version check that kills the installer is strictly worse than none. Every degradation
    path — absent, non-zero, unparseable, no output — now warns and continues.
- **Two false claims in the plugin constitution, both of which had already misled a reader** (multi-host
  audit MH-40 + MH-16 part 1). The shape is identical and is this repo's own documented failure mode — a
  stale claim in a file every session loads is an active defect, not a bookkeeping lag:
  - **`CLAUDE.md` said "No DOM control ships"** for `dashboard_autostart`. True when written, false hours
    later: the owner approved the ratchet raise and `_render_dashboard_autostart()` shipped a three-option
    control on **both** surfaces at a measured 6 elements. An audit lens read the stale sentence and
    reported closed work as open. Superseded inline, after verifying the control actually renders.
  - **`CLAUDE.md` said "Claude Code's OS sandbox is Claude-only"** and generalized from Copilot to every
    non-Claude host. **False for OpenAI Codex CLI**, in the costliest direction: it sends a Codex operator
    to add a devcontainer while saying nothing about the knob that actually bounds them. Codex ships the
    *same* primitives (Seatbelt / bubblewrap / Windows sandbox) **default-on** at
    `sandbox_mode = workspace-write`, and its docs state the sandbox *"applies to spawned commands"* — so it
    closes the **subprocess** gap that section exists to name, by default, where Claude Code's is opt-in.
    The Copilot half (genuinely unevidenced) is preserved. Verified against the primary source
    (`learn.chatgpt.com/docs/sandboxing`) **before** writing, because `knowledge/codex-cli-customization.md`
    had marked the model `[inferred]` with a standing "verify before building on it" rule; that marker was
    upgraded to `[docs-verified]` in the same change. **The emitter half is still open** — nothing writes
    `.codex/config.toml`, so the corrected section says plainly that a saved comfort-posture does not bound
    a Codex session today.

## 0.215.1 — 2026-07-27

### Fixed

- **Corrected a dead source link on the `run-context-bundle` Learn-tab concept** (relanded from the
  stale routine PR #710): the `sources:` `url` pointed `capture-run-context.py` at
  `plugins/ravenclaude-core/scripts/…`, which does not exist — the script lives at repo-root
  `scripts/capture-run-context.py` (the convention every other repo-root-script source already uses).
  The fix is in the concept source; the generated `concepts.json`, `docs/concepts.md`, `dashboard.html`,
  and `index.html` were regenerated to match (no DOM-budget change — the source link is CDATA payload).

## 0.215.0 — 2026-07-27

### Added

- **Consolidated 4 subreddit-scan best-practices into one release** — relanded fresh off `main` from the
  stale routine PRs #687 / #721 / #729 / #734 (each was 48–87 commits behind and un-mergeable), after a
  read-only triage confirmed all four are genuine gaps not already on `main`:
  - **Plan Mode is a tool-enforced gate, not advisory "think first"** — the enforcement is a real
    permission gate, not a prose reminder.
  - **A `PostToolUse` hook is the deterministic quarantine for untrusted tool output** — its central
    claim (a `PostToolUse` hook can rewrite the result the model sees via
    `hookSpecificOutput.updatedToolOutput`; the tool already ran, so side effects stick) was **verified
    TRUE against the current Claude Code hooks reference this session** before shipping.
  - **Build CLI + Skill first; reach for MCP only for live external-system state** — the design-time
    discriminator upstream of the runtime MCP-context budget rule.
  - **A policy hook only gates if it fails closed — exit 2 or a JSON `deny`, never `exit 1`.**

### Fixed

- **`docs/best-practices/hook-authoring.md` "Pick the right event" table had two wrong rows** (surfaced
  by the two hook best-practices above): `PreToolUse` said "exit 1 blocks the call" — it is **exit 2**
  that blocks; exit 1 is a _non-blocking_ error, so the tool still runs — and `PostToolUse` said "exit
  code is logged only", omitting that `hookSpecificOutput.updatedToolOutput` **rewrites the result the
  model sees**.

## 0.214.0 — 2026-07-27

### Changed

- **Prompt Builder — one template toggle row, per-field canned pickers, and a Control-section home.**
  The dashboard's Prompt Builder (`#/prompt-builder`) gets three changes: (1) the two overlapping
  "starting point" controls — the Task/System/Few-shot mode toggle _and_ the separate "Preset…"
  dropdown — collapse into **one toggle-button row of templates** (Agent system prompt first, the
  most-used); picking a template sets the mode and fills the fields, so there is one control, not two.
  (2) Each System-mode field (role, standing rules, tone, boundaries, output policy) gains an **"Insert
  a canned …" dropdown** — a vetted, best-practice-grounded, anti-folklore-clean list you can drop in
  and then edit freely; the free-text input is untouched (the pick fills an empty field, appends to a
  non-empty one, or adds a list item). (3) The **Prompt Builder nav link moves from "Learn & Help" to
  "Control"**, above The Thing, in the sidebar (and the mirrored tab-bar). Fresh visits now open on the
  Agent system prompt template. Everything stays client-side, DOM built with
  `createElement`/`textContent` (the XSS floor the render gate enforces). **Migration:** none — no
  storage-key change; saved builder state loads unchanged (the new `template` marker defaults to null).

## 0.213.0 — 2026-07-27

### Added

- **`/wireframe` v1.1 — the deferred renderers, archetype library, and multi-screen extension.** Extends
  the existing skill (no new skill/agent; skill count stays 50). Ships: the deterministic **`_layout.py`**
  box-packer (integer grid units, overlap-free by construction, two-predicate self-check); **`render_ascii.py`**
  and **`render_svg.py`** (the SVG clears `svg-report-lint`/Gate 103 by construction, with viewBox aspect
  padded into 0.05..20); a two-level **named-archetype library** (`archetypes/`, 12 models across
  marketing/app/data) + **`archetype_score.py`** (structural conformance ≥ 80, honest "completeness not
  taste" scope); and the **multi-screen (v2)** `screens[]`/`flow_edges[]` model shape with a new
  `emit_screen_flow` Mermaid nav-map emitter and an `ascii_text` sanitizer in `wireframe_lint.py`. New
  must-fail **gates 146–150** in `audit-gates.sh`. Built via `/forge` (two-panel + critic + red-team).
  Committed goldens use prettier-ignored extensions (`.txt`/`.svg`/`.mmd`) and are LF-pinned via
  `.gitattributes`. **Migration:** none — additive files under the existing skill.

## 0.212.0 — 2026-07-27

### Added

- **`/wireframe` skill (v1) — describe anything → validated model + high-fidelity HTML Artifact +
  Mermaid.** A main-session skill in `ravenclaude-core` that turns a plain-language description into a
  schema-validated wireframe model, a Claude-authored self-contained HTML Artifact (via `artifact-design`),
  and a Mermaid flowchart for flows. Ships `schemas/wireframe-model.schema.json`, the stdlib-only
  `wireframe_lint.py` (validator + context-aware sanitizers + deterministic Mermaid emitter), starter
  skeletons, and **Gate 145**. No new agent (`check-frontmatter.py` N/A). **Migration:** none — additive.

## 0.211.1 — 2026-07-27

### Fixed

- **Prompt Builder is now reachable in the marketplace portal (`index.html`), not just the standalone
  dashboard.** The v0.211.0 tab worked in the standalone `dashboard.html` (whose `validTabs` derives from
  the tab button) but the **portal shell router** never owned `#/prompt-builder`: `DASH_OWNER` (the
  dashboard-tab → destination map that drives `route()`, `payloadKind()`, and nav-highlight) was missing
  the entry, so the portal's sidebar link fell through to the default section (Settings). Fixed by adding
  `"prompt-builder": "catalog"` to `DASH_OWNER` (in `scripts/_index_dashboard_template.py`) — which routes
  `#/prompt-builder` to the dashboard host + highlights Catalog — plus a **Prompt Builder** link in the
  Catalog sub-nav (its literal `href` also registers it as a Gate-51 committed route). Standalone
  `dashboard.html` was already correct and is untouched.
- **Regression guard:** `scripts/check-prompt-builder-render.mjs` (Gate 144) now, when run on the shell
  (`index.html`), asserts `DASH_OWNER` routes `#/prompt-builder` and the sidebar surfaces the link — the
  render gate already runs on both surfaces, so a future drop of the portal route is caught (verified
  fail-on-tamper). The check no-ops on the standalone (no `DASH_OWNER`).
- **CI: greened three gates v0.211.0 shipped red** (it was admin-merged with CI failing). All three are
  Prompt-Builder / self-heal artifacts surfaced by this version bump — none is a runtime change: (1)
  **copilot package freshness** — the generated `copilot/plugin.json` was never regenerated for v0.211.0
  (it sat at 0.210.2); regenerated. (2) **committed-routes fixture**
  (`tests/fixtures/routes/committed-routes.json`) — the v0.211.0 `#/prompt-builder` tab added hrefs on
  both surfaces without updating the fixture; re-emitted (the PB-2 anti-laundering `required_routes` floor
  is carried through verbatim). (3) **DOM-budget structural check** (Gate 132) — the prompt-builder panel
  is the **16th**; the hardcoded `SUM(panels)+shell, 15 panels` assertion in `scripts/audit-gates.sh` was
  bumped 15 → 16 (the partition identity holds on both surfaces).
- **Skill-count self-heal (48 → 49).** The core `plugin.json` + `marketplace.json` descriptions
  undercounted skills (49 dirs, claimed 48) — a pre-existing drift on `main` that the full `audit-gates`
  self-heal (`check-marketplace-claims.py --fix`) surfaces into the copilot-freshness gate for **every**
  PR (which is why v0.211.0 had to be admin-merged). Synced to 49 via the sanctioned `--fix` and
  regenerated copilot + dashboards, so the count is honest and CI is green. Also resolved stray git
  conflict markers left in this CHANGELOG by the v0.211.0 re-integration.

## 0.211.0 — 2026-07-26

### Added

- **Prompt Builder — a new dashboard tab (`#/prompt-builder`, under Learn & Help).** A deterministic,
  100% client-side tool that assembles a best-practice **Claude** prompt from form inputs, in three
  modes — **Task** / **System** / **Few-shot** — with a live preview, a **cited anti-folklore quality
  linter** (the hero surface), a structure-completeness score, a rough token-size estimate, starter
  presets + a one-click pattern library, and copy/export (`.md`/`.json`). No server, no API, no external
  deps. Built via `/forge` (two-panel cross-model design → correlated-error critic → red-team →
  synthesis); grounded in Anthropic's consolidated _Prompting best practices_ (retrieved 2026-07-26).
  Research-driven groundings: **prefilling is deprecated** (400 on Claude 4.6+) so the builder never
  emits it and the linter penalizes it; the token number is honestly **an estimate** (per-model divisor
  3.6/4.0, `[interpretation]`, ±20% band) that never gates an action; and the linter **penalizes**
  stacked `CRITICAL/MUST` emphasis rather than rewarding folklore.
- **Gate 144 — `scripts/check-prompt-builder-render.mjs`.** The builder echoes user input into a live
  preview, so its security floor is **no HTML-string sink anywhere in its JS** (the whole UI is built via
  a `createElement`/`textContent` factory, `pbEl`). The gate enforces it **structurally** — a static
  source grep over the whole `PROMPT-BUILDER:START..END` region — because the shared render DOM-stub
  (`check-nidhoggr-render.mjs`) has no `innerHTML` setter and can't catch an `innerHTML` regression on
  its own (the correlated error the FORGE critic found in both design panels; precedent
  `check-concern-stats-render.mjs`). It also behaviorally exercises the pure assembler / linter / token
  logic, with a must-fail half wired into `audit-gates.sh`.
- **DOM budget (Gate 132) raised +6** (dashboard 6,097→6,103, index 6,809→6,815) to seat the new tab —
  the frozen zero-slack tail was lifted in lockstep to keep the ratchet monotonic; the interactive UI is
  JS-built (uncounted), so only the ~6 nav+mount elements are added. Owner-approved.

**Migration:** none — a new read-only-to-the-repo tab (state is `localStorage` only). Reviewed by
`code-reviewer` (approve-with-nits, all applied) + `security-reviewer` (DOM-XSS floor holds).
## 0.210.2 — 2026-07-26

### Fixed

- **Command-card header wraps instead of clipping.** The dashboard/portal `.cmd-card-head` now wraps (`flex-wrap: wrap`, `gap: 6px 8px`) and `.cmd-card-title` takes a full-width flex row with `overflow-wrap: anywhere` (was `word-break: break-all` on a `space-between` row) — long mono command names/badges no longer collide or truncate awkwardly on narrow widths. Generator-only (`scripts/generate-dashboards.py`); `dashboard.html` + `index.html` regenerated.

## 0.210.1 — 2026-07-26

### Added

- **Thing-denial knowledge base (Muninn)** — when the command/decision tribunal DENIES/DEFERS an action, a new per-repo KB turns the raw Sága records into a `denial shape → known resolution` lookup so a blocked agent can identify why it recurs and apply the fix. Engine [`scripts/thing-denial-kb.py`](scripts/thing-denial-kb.py) (`sync`/`recall`/`resolve`/`record`); seed [`knowledge/thing-denial-resolutions.json`](knowledge/thing-denial-resolutions.json); `thing-denial-kb` skill + [`knowledge/thing-denial-kb.md`](knowledge/thing-denial-kb.md). A `Stop` hook syncs from the Sága logs (hot-path-safe, read-only); a `SessionStart` hook surfaces the digest.
  - **Security-hardened (2 blockers fixed in review), proven by Gate 143:** derived-labels-only banner (raw `sample` never auto-injected — only `recall --json`); `sample`+`reasoning` secret-scrubbed before storage (port of `hooks/_scrub.sh`); decision resolutions match on the derived reason class, correct-by-design rules first. **Migration:** none — additive, opt-in, fail-safe.

## 0.210.0 — 2026-07-26

### Added

- **FORGE always provisions a worktree + checkpoints.** `/forge` now provisions an isolated `forge/<slug>` git worktree and checkpoints its tracked work at every gate boundary, at **every depth** (`micro`→`deep`). New deterministic helper `scripts/forge-worktree.sh` (`init` / `checkpoint` / `--self-test`), `bash`-3.2-safe and free of GNU `timeout`/`grep -P`/`sed -i`. **Fail-safe by contract** — every can't-provision case (not-a-git-repo, already-in-worktree nesting-guard, opted-out) exits 0 with a status receipt so the pipeline proceeds in the primary checkout (a safety anchor, never a gate). Opt-out: `forge_worktree: off` in `.ravenclaude/comfort-posture.yaml` or `FORGE_WORKTREE=off` (absent ⇒ on). Wired into `skills/forge-pipeline/SKILL.md` §0.5, `commands/forge.md`, and reconciled with the deep-depth atomic-write/resume. **Migration:** additive + fail-safe; set `forge_worktree: off` to keep the prior in-place behavior.

## 0.207.0 — 2026-07-21

### Added

- **Dual-analytics default for HTML-serving templates.** `templates/repo-build-studio/marketing-page.html` (public) ships the **GA4 (Consent Mode v2) + Cloudflare Web Analytics** placeholder block — empty IDs ⇒ inert (no `<script>`, zero network); each beacon is independently PROD-host-gated **and** valid-id-gated (the guard rejects dummy shapes like `G-XXXXXXXXXX`, not just empty strings). `dashboard.html` (internal) ships the same block **commented-off by default** — authed/internal surfaces do not auto-fire. A domain-neutral pointer in `CLAUDE.md` + one conditional line in the `agent-ready-repo` `CLAUDE.md.template` route to the full policy in `web-design/skills/third-party-script-hygiene` §8–9 (this plugin stays domain-neutral). IDs are PUBLIC identifiers, never secrets.

## 0.202.0 — 2026-07-16

### Added

- **FORGE domain-prior lens (`skills/forge-pipeline`) — the orchestrator now brings a domain lens to its gates, the constitution-correct way.** At `standard`+ only (the default `quick` path is byte-identical), the pipeline derives a one-line domain tag and injects the **same** domain-concern prior into both G2/G3 panels (and optionally G4a/G4b/G5) — cross-model divergence (B≠A) untouched; `security` is a non-exclusive overlay, so a security signal always adds the security prior. It is **inject-prior only**: it names domain concerns + the always-present [`agent-routing.md`](knowledge/agent-routing.md), never a hard cross-plugin link, so a disabled/uninstalled domain plugin never degrades it. New machinery lives in `reference/gates-standard.md` (loaded only at standard+); `quick`/`micro` pay nothing.
  - **Why not dispatch a real specialist `agentType`** (the seductive answer two panels proposed, and the pipeline's own G4a critic + G5 red-team both cut): the house-rule litmus ("core agent + right skill = indistinguishable"), most advisory specialists lack `Write` (a `Bash`-heredoc workaround silently passes §0's "non-empty" floor on a truncated artifact — a regression), specialists emit their native schema not FORGE's receipt, and a domain→`agentType` map rots with no CI gate. Real dispatch is **deferred** with explicit preconditions recorded inline in `gates-standard.md`.

### Fixed

- **FORGE now honors the `parallelism:` posture cap** (`SKILL.md` §3) exactly as `spawn-team` Step 5 does — previously FORGE was the one orchestrator in the marketplace that ignored it. A cap, not a floor (composes with the Opus 4.8 under-spawn tuning).
- **The "Sága run record" promised by `commands/forge.md` Step 5 now has a concrete shape** (`SKILL.md` §0): each gate's receipt is appended to `.ravenclaude/runs/forge/<slug>/run-log.jsonl` with `model`/`subagent_type`/`effort`. It was named in `forge.md` but never defined in the skill's artifact contract — unimplementable as written.

**Cost (honest, char/4):** the **domain-prior lens adds nothing to `quick`/`micro`** (it lives in `reference/gates-standard.md`, loaded only at `standard`+; ≈ +1,000 tok there). The two hygiene fixes above touch always-loaded core, so `quick`'s fixed prompt grows **≈ +130 tok (~4%)** — a deliberate trade for a real correctness fix (the parallelism cap) + a real observability fix (the run-log). **Migration:** none — additive + behavioral; the lens degrades to today's generic behavior on an unrecognized domain or a disabled plugin. Found by dogfooding `/forge` on FORGE itself.

## 0.199.1 — 2026-07-15

### Fixed

- **The constitution told every agent that loads it that the tribunal was broken on macOS. It wasn't — and this one had teeth.** `plugins/ravenclaude-core/CLAUDE.md`'s v0.193.0 / v0.195.0 / v0.196.0 milestones still carried *"`thing-orchestrator.sh` … is NOT fixed here"*, *"Still open"* for the `macos-latest` runner, and two **"Do not claim 'macOS supported' until…"** gates. **All shipped**: the tribunal in [#672](https://github.com/mcorbett51090/RavenClaude/pull/672) (v0.197.0 — the C4 trap navigated, `declare -A` now only in warning comments `[verified 2026-07-15 — no live-code match]`), the runner in [#679](https://github.com/mcorbett51090/RavenClaude/pull/679) (v0.197.1 — `.github/workflows/validate-macos.yml`, `runs-on: macos-latest` `[verified]`), door 3 in v0.196.0. Two doors found after those entries were written (door 4's BSD `sed -i`, and the BSD-`sed` JudgeDeceiver hole in [#670](https://github.com/mcorbett51090/RavenClaude/pull/670)) are now recorded there too. **Superseded in place, not deleted** — per this file's own convention (cf. the v0.114.0 entry), the dated record stays and a supersession note leads it.
  - **Why this is a defect and not bookkeeping.** On 2026-07-15 an agent read the stale text, took it at face value, and told the maintainer **twice** that his command-review tribunal was broken on macOS — while it had been working since v0.197.0. That is this repo's own **Claim-Grounding** failure mode (a confident claim resting on an unverified prior) landing *on the repo's own constitution*, and the reader it fooled was the constitution's primary audience: an agent. A stale **"Still open"** in a file every session loads is an **active defect**. The rule now stated in-place: **when you close a door, supersede the entry that says it's open, in the same PR.**

### Added

- **CHANGELOG backfill — 0.193.0 through 0.198.0** (six versions, eight entries incl. two patches) were missing while `plugin.json` read 0.198.0. Reconstructed from **git history + PR numbers + the `CLAUDE.md` milestones** — never from memory. `AGENTS.md` names the `version` field plus git history as the authoritative record, so this is transcription, not reconstruction-by-inference; every entry links its PR so it stays falsifiable. Two honest gaps kept visible: **0.198.0 has no `CLAUDE.md` milestone**, and its commit subject is labelled `(v0.192.0)` — **stale** (PR [#655](https://github.com/mcorbett51090/RavenClaude/pull/655) was authored against 0.192.0 and landed at 0.198.0); `plugin.json` wins.

## 0.199.0 — 2026-07-15

### Fixed

- **FORGE's thinking-budget lever was a workaround for a flag that now exists — and the vendor now tells you not to use it.** `reference/provenance.md` asserted that "`claude -p` exposes **no** thinking-budget flag (verified: `claude --help` shows only `--max-budget-usd`)" and that the sanctioned lever is the in-prompt `ultrathink` keyword. Both halves are now false. `claude --help` on **v2.1.210** exposes `--effort <level>` (`low`/`medium`/`high`/`xhigh`/`max`), there is a persisted `effortLevel` settings key, and the `Task`/`Agent` dispatch option takes `effort` directly `[verified 2026-07-15]`. More pointedly, [Prompting Claude Opus 4.8](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8) says to *"raise effort to `high` or `xhigh` **rather than prompting around it**"* — appending `ultrathink` to a brief **is** prompting around it. G2/G3/G4a/G5 now dispatch with `effort: 'xhigh'` (the dispatch option, not brief text); G4b stays at the session default. Corrected in `SKILL.md`, `reference/gates-standard.md`, and `reference/provenance.md` (which carries the dated correction, the sources, and the reasoning).
- **The old framing reasoned about the wrong surface.** A FORGE gate is a **subagent dispatch**, not a `claude -p` call — so even when the CLI genuinely had no flag, the `Task` `effort` option was the right lever, not the brief text.
- **`code-reviewer`'s rubric could cap its own coverage on the diffs that most need it.** The rubric said *"Walk the diff in this order. **Don't proceed past a category until it's clean.**"* Read literally — and *"Claude Opus 4.8 interprets prompts literally and explicitly"* — that means **stop at the first dirty category**: a diff with a correctness bug never reaches the Tests, Design, Performance, Security-adjacency, or Consistency passes. Now reads: walk **all seven**; finish each before the next; a category that isn't clean is a **finding, not a stop**. The old text is quoted in-place so the hazard isn't silently re-introduced.

### Added

- **`code-reviewer` — a concrete bar for Blocker-vs-Suggestion, replacing a qualitative one.** The tiers stated their *consequence* ("must fix before merge" / "consider, not required") but never the *test* for which tier a finding lands in. Anthropic's guidance for a reviewer that self-filters in one pass is to *"be concrete about where the bar is rather than using qualitative terms like 'important'"* ([Prompting Claude Opus 4.8](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8), retrieved 2026-07-15) — Opus 4.8 honors a stated bar **more faithfully** than prior models, so a vague bar silently costs recall. The bar is now the guide's shape: **Blocker** = could cause incorrect behavior, data loss, a test failure, a security/privacy exposure, or a misleading result (plus the rubric's outright blockers); **Suggestion** = everything else worth the author's attention, *explicitly including* uncertain and low-severity findings; **Omit** = only pure style/naming already matching convention, and restatements of what the linter enforces. Uncertainty is now stated as a reason to *file* under Suggestions, never to drop.

- **`spawn-team` Step 1.5 — the *whether-to-delegate* fork, argued in both directions.** Every lever in the dispatch path bounded fan-out from **one side only**: the `parallelism` cap bounds breadth, the runaway brake bounds depth, `agent-routing.md`'s tradeoffs table prices every specialist as a **"spawn cost" to be justified**, `guard-recursive-spawn.sh` warns on nesting, briefs carry reporting caps. Nothing anywhere treated **under**-delegation as a failure mode. That framing is right for a model that over-dispatches and wrong for this one: *"Claude Opus 4.8 tends to spawn fewer subagents by default. However, this behavior is steerable through prompting; give Claude Opus 4.8 explicit guidance around when subagents are desirable"* ([Prompting Claude Opus 4.8](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8), retrieved 2026-07-15). An under-spawning model plus a uniformly restraining harness **compound** — the model hesitates and the playbook agrees. Step 1.5 is the counterweight and names both tells (spawning to do a ≤10-line tweak; reading six files into your own context instead of dispatching six subagents in one turn).
- **`spawn-team`'s load trigger widened — the guidance was otherwise partly self-defeating.** The skill's `description` said to load it *"whenever you are about to dispatch more than one agent"*, so a Team Lead that under-spawns never loads the playbook that would tell it to spawn. The description now also fires when *weighing whether a request warrants delegation at all*.
- **`agent-routing.md` — a whether-vs-which note above the tradeoffs table**, pointing at Step 1.5 first, since the table's "spawn cost" framing is exactly the one-directional pull and it answers *which specialist*, not *whether to delegate*.

### Changed

- **`.claude/settings.json` now sets `"effortLevel": "xhigh"`.** The repo had no effort key, so every dev session ran at the API default `high` while Anthropic's Opus 4.8 guidance is to *start* at `xhigh` for coding and agentic work — the exact workload this repo is. *"Effort is likely to be more important for this model than for any prior Opus."* This is a **cost/latency trade**: `xhigh` means measurably more tokens and longer turns per session. Drop it to `high` (or delete the key) if that isn't worth it here.
- **Recorded the per-model effort inversion**, so a future model swap doesn't inherit the wrong posture: Opus 4.8 starts at `xhigh`; **Claude Fable 5 starts at `high`** (its default), reserving `xhigh` for capability-sensitive work, because *"lower effort settings on Claude Fable 5 still perform well and often exceed `xhigh` performance on prior models"* `[retrieved 2026-07-15]`. Porting an `xhigh`-everywhere posture to Fable overspends for nothing.

### Notes

- **Step 1.5 relaxes nothing.** The `parallelism` cap still bounds breadth, sub-agents still never spawn peers (single-orchestrator, soft-enforced by `guard-recursive-spawn.sh`), and the routing tree still decides *which* specialist. It decides only *whether*, and "spawn more" is never a licence to skip the cap, the tree, or the Step-2 shape choice.
- **Step 1.5 is behavioral, not enforced** — like `design_checkins`, `decision_review`, and the Agentic-Default Principle, no hook can see the intake fork (an under-delegation is the *absence* of a tool call, which is unobservable by construction). Stated plainly rather than implied to be a control.
- **It is calibrated to Opus 4.8 and will invert.** Fable 5 *"dispatches parallel subagents more readily than prior models"* `[retrieved 2026-07-15]`, so on Fable the restraining levers do the work and Step 1.5 needs re-reading, not copying. The step says so in-place so a future model swap doesn't inherit the wrong direction.
- **Not fixed here:** `docs/session-log.md:13` still restates the stale no-flag finding. It is a dated historical record and the repo's convention leaves those as-is.
- **CHANGELOG gap (pre-existing, not this change):** this file's top entry was **0.192.0** while `plugin.json` read **0.198.0** — 0.193.0–0.198.0 were absent. Backfilled in **0.199.1**.

## 0.198.0 — 2026-07-15

### Added

- **Best practice — drop a tier for grunt-work subagents** ([#655](https://github.com/mcorbett51090/RavenClaude/pull/655)). Set the model **explicitly** at a subagent dispatch / workflow fan-out: fast (Haiku-class) for grunt legwork, frontier reserved for the hardest reasoning. From the 15th recurring Claude-subreddit scan (4 findings → 1 approved, 3 denied). _No `CLAUDE.md` milestone. The commit subject is labelled `(v0.192.0)` — stale; it was authored against 0.192.0 and landed at 0.198.0._

## 0.197.1 — 2026-07-15

### Fixed

- **macOS doors 6 + 7** — the 4 gates the tribunal fix unmasked now pass on macOS ([#674](https://github.com/mcorbett51090/RavenClaude/pull/674)).

### Added

- **The `macos-latest` CI runner** — `.github/workflows/validate-macos.yml`, which **executes** the hooks on a stock toolchain rather than linting them ([#679](https://github.com/mcorbett51090/RavenClaude/pull/679)). Closes the last item on the v0.196.0 "what remains before macOS supported" list.

## 0.197.0 — 2026-07-15

### Fixed

- **The command-review tribunal now runs on macOS (bash 3.2)** ([#672](https://github.com/mcorbett51090/RavenClaude/pull/672)) — the last of the stock-macOS doors, and the one the v0.195.0 entry had deliberately left unrushed because it is a security control carrying the **C4 trap** (deleting `declare -A` alone silently collides every role key on index 0). Navigated, not dodged: `declare -A` now appears in `thing-orchestrator.sh` **only inside comments warning against re-introducing it**, and the seat calls route through door 2's `_rc_timeout` shim. See the `CLAUDE.md` v0.196.0 supersession note.

## 0.196.1 — 2026-07-15

### Fixed

- **BSD `sed` silently disabled a JudgeDeceiver hardener layer on macOS** ([#670](https://github.com/mcorbett51090/RavenClaude/pull/670)) — a door not in the original three-door plan, found while closing them.

## 0.196.0 — 2026-07-15

### Fixed

- **macOS door 3 — BSD `grep` has no `-P`**, so **12** `check-*-anti-patterns.sh` hooks across 12 plugins never fired (exit 2 reads as no-match; the hook then exits 0, silently) ([#666](https://github.com/mcorbett51090/RavenClaude/pull/666)). Fixed with `_rc_pcre_match` over stock `/usr/bin/perl` — perl **is** the PCRE engine, so no install step.
- **macOS door 4 — BSD `sed -i` killed `audit-gates` at gate 7 of 87** ([#669](https://github.com/mcorbett51090/RavenClaude/pull/669)).

### Added

- **The macOS portability gate (Gate 131)** — a runner that **executes** the hooks on a stock toolchain; LOUD-skips on Linux ([#668](https://github.com/mcorbett51090/RavenClaude/pull/668)).

## 0.195.0 — 2026-07-15

### Fixed

- **macOS door 2 — `timeout` is absent, and it silently disarmed decision-review** ([#664](https://github.com/mcorbett51090/RavenClaude/pull/664)). `route-decision-review.sh` took its error path on **every** macOS session, so the tribunal was never consulted and every routed yes/no silently allowed. Added `hooks/_portable.sh` (`_rc_timeout` via `timeout` → `gtimeout` → stock `/usr/bin/perl`; `_rc_upper` for bash-4-only `${v^^}`).

## 0.194.0 — 2026-07-15

### Fixed

- **FORGE tiebreak F7's "shared rubric" claim was false** — corrected in all three files that asserted it ([#662](https://github.com/mcorbett51090/RavenClaude/pull/662)). The two-panel workflow's rubric/lens/schema consts are module-private; no shared module ever existed. The rubric was deliberately **not** ported, with the reasoning recorded in-repo so a future reader doesn't "close the gap".

## 0.193.0 — 2026-07-15

### Fixed

- **macOS bash 3.2 silently bypassed the layout gate on every session** ([#660](https://github.com/mcorbett51090/RavenClaude/pull/660)). `enforce-layout.sh` ran `shopt -s globstar` (bash 4.0+); under `set -e` an invalid shopt option exits 1, which Claude Code treats as a non-blocking error — so one of the repo's two enforcement layers was dead on macOS. Gate 6 was 4/8 red and passing **for the wrong reason** (exit 1 = crash, not deny); now 8/8 with real exit-2 denies.

## 0.192.0 — 2026-07-15

### Added

- **`best-practices/drop-a-tier-for-grunt-work-subagents-strong-model-supervises.md`** — new consumer-facing best-practice (rule #34): at a subagent dispatch / workflow fan-out, set the model explicitly instead of default-inheriting the orchestrator's tier — fast (Haiku-class) for grunt legwork, frontier reserved for the hardest reasoning + the review/verify step (strong supervises, cheap executes). Covers the two-sided failure (under-tiering forces a redo) and the review-panel carve-out (panels want model _diversity_, not the cheapest tier). Operationalizes the `model-selection` knowledge concept at the dispatch decision — the knowledge-names-it / no-rule-teaches-it gap, per the 2026-07-15 subreddit-scan panel.
- **`best-practices/README.md`** — index row + count 33 → 34.
- **`docs/research/2026-07-15-claude-subreddit-scan/README.md`** — the 15th recurring Claude-community scan: research, documented Keep/Update/Deny panel, and build plan (4 findings surfaced → 1 approved, 3 denied-as-covered/volatile).

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes on `/plugin marketplace update`.

## 0.191.0 — 2026-07-14

### Added

Consolidated reland of the subagent-permission-inheritance knowledge + least-privilege tools gate + hook de-nesting (originally PRs #538, #615, and the rc-core portion of #536) into one landing.

- **`knowledge/claude-code-permissions.md`** — new **"Subagents inherit the parent's permission mode"** section: a subagent's `tools:` line bounds its tool set but not its permission mode; under `bypassPermissions`/`acceptEdits` a subagent inherits the parent mode and cannot be restricted below it, so the `tools:` line + a hook `deny` are the real bounds. **Accuracy fix (2026-07-14):** a per-subagent `permissionMode` field *has* since shipped and can restrict a subagent below the parent — except under `bypassPermissions`/`acceptEdits` (verified against the sub-agents doc; #20264 tracked the earlier gap).
- **`knowledge/claude-code-permissions.md`** — five dated Claude Code CHANGELOG permission facts folded into the existing sections: `Tool(param:value)` / `Agent(model:opus)` rule syntax (v2.1.178) + the `Agent(type)` enforcement fix (v2.1.186); `deny:["*"]` all-tools glob (v2.1.166); the `sandbox.credentials` setting (v2.1.187) blocking sandboxed subprocesses from reading credentials; the `post-session` lifecycle hook (v2.1.169) firing before workspace deletion; and the hyphenated-matcher exact-match fix (v2.1.195). Version-specific claims carry `[verify-at-use]`.
- **`scripts/check-frontmatter.py`** — new least-privilege gate: every `agents/*.md` must declare an explicit `tools:` allowlist (`tools: "*"` is a valid explicit opt-in; Copilot `.agent.md` adapters are excluded). A missing/empty `tools` fails the build.
- **`AGENTS.md`** — new item 9 in "Adding a new plugin": the explicit-`tools:` least-privilege rule, referencing the knowledge doc + noting `check-frontmatter.py` gates it.
- **`scripts/audit-gates.sh`** — frontmatter tools fixtures (`notools.md` must-fail, `withtools.md` must-pass; `tools:` added to `okdesc.md`) + a new **Gate 3b** static lint that flags a `python3 - <<'PY' … PY` heredoc nested in `$()` in any `plugins/*/hooks/*.sh` (a bash-3.2 parse-abort footgun).
- `docs/research/2026-07-01-claude-subreddit-scan/README.md` — the scan panel that sourced the subagent section.

### Changed

- **`hooks/dod-gate.sh`** (3 sites) and **`hooks/guard-web-access.sh`** (1 site) — de-nested the heredoc-in-`$()` anti-pattern to the sanctioned `read -r -d '' VAR <<'PY' … PY` + `python3 -c "$VAR"` form (behavior-preserving; `guard-destructive.sh` was already fixed).

**Migration:** none — additive knowledge + gates + a behavior-preserving hook refactor.

## 0.190.0 — 2026-07-14

### Added

Consolidated the net-new best-practices from the 2026 Claude-subreddit-scan research campaign (originally proposed as PRs #531, #572, #575, #613, #632) into one landing — same end-state, one version bump. Roster grows 28 → 33 rules.

- **`best-practices/output-styles-replace-the-system-prompt-keep-coding-instructions-when-still-coding.md`** — a custom Claude Code output style silently replaces the software-engineering system prompt unless `keep-coding-instructions: true` is set; keep it whenever the style is still doing coding work.
- **`best-practices/precompact-hook-is-the-deterministic-enforcer-of-persist-before-compaction.md`** — register a `PreCompact` command hook (trigger `manual`/`auto`) that flushes plan/decisions/rejected-approaches to disk, turning the "persist before compaction" prose rule into a gate that fires whether or not the model remembers.
- **`best-practices/subagent-isolates-clutter-skill-keeps-the-work-in-thread.md`** — choose skill-vs-subagent by the isolate-vs-steer axis (subagent when intermediate results are clutter; skill when you want to see and steer each step), not by "can it run in parallel."
- **`best-practices/a-skills-body-is-the-gotchas-the-model-doesnt-know-not-the-happy-path.md`** — fill a skill body with the failure modes / gotchas the model can't infer, not the happy path it already knows; re-teaching the baseline just spends the on-invoke budget.
- **`best-practices/treat-repo-committed-claude-config-as-untrusted-input.md`** — a cloned repo's committed `.claude/settings.json`, `.mcp.json`, and hook scripts are executable config that can fire around the workspace-trust dialog (real 2026 RCE/exfil CVEs); audit those four surfaces before opening it. The inbound sibling to `permissions-are-deny-ask-allow`.
- The five dated `docs/research/2026-*-claude-subreddit-scan/README.md` scan panels that sourced these rules.

**Migration:** none — additive documentation only.

## 0.189.2 — 2026-07-14

### Fixed

- **Portability (macOS bash 3.2):** `hooks/guard-destructive.sh` now parses under macOS's stock **bash 3.2** (`/usr/bin/env bash` when no Homebrew bash is on PATH). The command preprocessor loaded its Python via a here-document nested inside `$(…)` command substitution — a construct bash 3.2 mis-parses (it starts reading the paren/quote-heavy Python regex as shell → `syntax error near unexpected token )`). A bash parse failure exits 2, and Claude Code treats exit 2 as **block**, so the un-parseable hook silently denied **every** Bash tool call. Fixed by loading the preprocessor into a shell variable via a here-doc fed to `read` (a *simple* command, **not** nested in `$()`, so every bash parses it), then running it with `python3 -c` — **no temp file**. CI runs bash 5.x, where the original construct is legal, so this was invisible in CI.
- **Fail-open closed — preprocessor has no filesystem dependency (security review):** using `python3 -c` (rather than a `mktemp`/`cat` temp-file loader) is deliberate. A temp-file loader silently no-ops the whole preprocessor whenever `$TMPDIR` is unwritable/full/read-only (common in CI, hardened containers, cleaned macOS `/var/folders`), which **drops the ANSI-C (`$'…'`) anti-obfuscation decode layer** — so an obfuscated destructive command (`rm -rf $'\057'` → `rm -rf /`, `git push origin $'\053HEAD:main'` → force-push) would be **allowed (exit 0)** with no warning. The `python3 -c` loader has no filesystem dependency, so the decoder runs whenever `python3` exists. A regression fixture in `scripts/audit-gates.sh` (Gate 5) asserts the ANSI-C payload still exits 2 under a hostile `TMPDIR`.
- **Fail-closed under `set -u`:** `__preproc` is initialized before the `python3` block, so the `[ -n "$__preproc" ]` consume is always defined even when `python3` is absent (an unbound read would abort the guard with a non-2 exit → non-blocking → command runs unchecked).

**Migration:** none — consumers on bash 5.x see no change; consumers on stock macOS bash 3.2 get a hook that no longer blocks all Bash commands.

## 0.189.1 — 2026-07-13

### Fixed

- **Security (P1):** `hooks/guard-destructive.sh` now blocks `curl|sh`-style pipe-to-shell RCE when the interpreter is **path-qualified** (`curl … | /bin/bash`, `| sudo /bin/sh`, `| /usr/bin/python3`, `| ./sh`). The two deny patterns anchored the interpreter name immediately after the pipe, so a leading `/bin/`/`./` path segment slipped the guard while the bare form was correctly blocked. An optional path-prefix group closes it; the audit-gates corpus gained path-qualified block fixtures + benign path-bearing pass fixtures.
- **Security (P2):** `scripts/capability-orientation.py` now frame-break-sanitizes the run-config `task_class` and per-phase tier values before inlining them into the always-injected SessionStart banner — they were the only unsanitized siblings of the already-guarded `rationale`, so a hostile/cloned repo's `run-config.json` could break out of the untrusted-data frame.
- **P3:** `skills/terminal-status-indicators/terminal-watcher.py` — a recycled PID no longer inherits its predecessor's stale controlling PTY (start-time identity check on `ProcState`), and `running_pid()` no longer crashes on a foreign-owned pidfile (EPERM from `os.kill(pid,0)` is treated as "alive"; the unlink is now fail-safe).
- **P3:** `skills/refine-to-rubric/scripts/derive_rubric.py` tolerates a markdown-bold weight cell (`**40**`, mirroring the `**yes**` the hard_gate column already accepts) instead of silently dropping the whole dimension and its hard gate; a genuinely non-numeric weight now warns.

## 0.189.0 — 2026-07-09

### Added

- **`terminal-status-indicators` skill** — makes VS Code terminal tabs show 🔔 + play a chime the
  moment a background agent session needs input, across many parallel Copilot/Claude terminals. Three
  layers: workspace settings (tab bell icon + audio cue + ⟳ shell-integration indicator), a `~/.bashrc`
  prompt hook (bell on command completion, interactive shells only), and a background watcher
  (`terminal-watcher.py`) that reads `/proc/<pid>/io` `wchar` and rings a terminal's PTY bell when its
  agent process goes idle after responding. Ships an idempotent `setup-terminal-indicators.sh`
  installer (non-destructive settings merge + marker-bounded shell block + version-agnostic watcher
  path) wired into this repo's `.devcontainer/post-create.sh` and the `codespace-copilot` consumer
  template so a new Codespace self-configures. The watcher carries fixes for six real failure modes
  (accumulate-across-ticks so streaming responses ring; ring-once-per-PTY so a shell wrapper + binary
  don't double-bell; PTY re-resolution; single-instance pidfile guard; no spurious startup bell;
  interactive-shell guard) — design + proof-of-failure in
  [`knowledge/vscode-terminal-status-indicators.md`](knowledge/vscode-terminal-status-indicators.md).
  Skill count 47 → 48.

## 0.188.4 — 2026-07-09

### Changed

- **Completed the client-codename pseudonymization — lowercase forms** (follow-up to 0.188.3, which only caught the uppercase codename). The lowercase form survived in example/fixture data: a Dataverse publisher prefix in the `dataverse-payload-preflight` test fixtures, the `mimir` encoded-path example, the `environment-context.md` template's example env slugs, a web-design knowledge doc's cross-link to a (since-renamed) research dir, and an architect agent-memory note. All replaced case-preservingly with the neutral `Contoso`/`contoso` placeholder; `BMA` (public regulator) retained. Behavior-neutral — fixtures are internally consistent, tests pass unchanged.

## 0.188.3 — 2026-07-09

### Changed

- **Pseudonymized a private client codename out of all shipped plugin content** (replaced with the neutral Microsoft `Contoso*` placeholder). The codename (and its example identifiers, e.g. `Contoso*Reporting` / `Contoso*FlowFix`) had leaked into shipped knowledge docs, this constitution's milestone narratives, a hook comment, a test fixture comment, and a skill docstring; each occurrence was replaced so worked examples stay coherent. The public regulator name `BMA` (Bermuda Monetary Authority) is intentionally retained. Behavior-neutral: no code literal was load-bearing on the string. Internal `docs/` and git history are out of scope (flagged separately).

## 0.188.2 — 2026-07-09

### Fixed

- **`refine-to-rubric`: judge-graded hard gates are no longer silently unenforced** (2026-07-09 repo review, Decision 3 — approved). A library rubric row combining `hard_gate=yes` with a judge-only (empty / `_(judge)_`) `objective_signal` was parsed into a dimension carrying `hard_gate=true`, but `evaluate.py` routes empty-signal dims to `judge_dims` and never records a `hard_gates` entry — so that gate could never block convergence. `derive_rubric.py`'s `parse_library` now **warns and neutralizes** the unenforceable flag (downgrades it to a scored, non-gating dimension), matching the design invariant that objective gates are deterministic and judge scorecards are never tripwires. No shipped rubric declared this shape, so behavior on the shipped library is unchanged.

## 0.188.1 — 2026-07-09

### Fixed

_From an autonomous 3-panel repo review (2026-07-09). Security + robustness fixes; the accompanying design-questions doc is [`docs/2026-07-09-repo-review-design-questions.md`](../../docs/2026-07-09-repo-review-design-questions.md)._

- **P0 — guard bypass (`hooks/guard-destructive.sh`).** The git global-option strip was a curated allow-list that omitted the real short globals `-p` (`--paginate`) and `-P` (`--no-pager`), so `git -p push --force` / `git -P reset --hard` / `git -p branch -D main` / `git -p clean -f` dodged **every** git deny at once — a trivial, non-obvious full bypass of the consumer's primary irreversible-action guard. The strip now tolerates any dash-prefixed global while still consuming separate-token values (`-c key=val`, `--git-dir path`). Empirically reproduced; regression fixtures added to `audit-gates.sh` Gate 5.
- **P1 — SessionStart banner injection (`scripts/capability-orientation.py`).** The stream classifier's suggestion / auto-switch path surfaced a raw registry **key** into the always-injected capability banner with no slug validation — a repo-planted `.ravenclaude/streams/registry.json` (not gitignored) key containing a newline + a `</ravenclaude-capabilities>` close tag + fake instructions could break the banner's data frame and inject into trusted session context. The suggestion/auto-switch id is now validated (`_SLUG_OK` + membership) exactly like the active pointer.
- **P2 — tribunal self-disable evasion (`scripts/thing-decision.py`).** A >4 KiB `Edit`/`MultiEdit` to `comfort-posture.yaml` could push the disabling change past the `\A`-anchored 4000-char `screen_always` window (only the `Write` shape was parse-screened). `_posture_write_disables` now reconstructs the post-edit document from the on-disk file + the edits and screens it identically; an unreconstructable edit fails closed (DENY).
- **P2 — web-access session-id traversal (`hooks/_emit-event.sh`, `hooks/guard-web-access.sh`, `hooks/mark-web-domain-seen.sh`).** Both web-access hooks built `runs/$sess/…` paths from an unsanitized session id, skipping the PR #363 `.`/`..` hardening (a `mkdir`/`touch` write primitive outside the sandbox via `mark-web-domain-seen.sh`). Factored `_ee_sanitize_session()` into the shared helper; both hooks (and `_emit_hook_event`) route through it.
- **P3 — misc robustness.** `scripts/stream-ops.py`: dropped `stream_id` from `_ALLOWED_EVENT_FIELDS` so `extra={"stream_id":…}` can't desync the in-body id from its directory. `skills/pbir-layout-engine/lint.py`: `abspath`→`realpath` so an in-repo symlink can't escape the sandbox. `skills/declarative-visualization/lint.py`: the security-surface advisory now covers the canonical Vega `signals[].on[].update`/`test` expression shape.

## 0.188.0 — 2026-07-09

### Added

- **New best-practice: [`scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md`](best-practices/scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md)** (28 rules total). Scope a skill to **one workflow** and write its `description` as the **trigger** (`Use when …`), because the `name`+`description` is the only tier Claude preloads and matches on to decide whether the skill fires — the body loads only afterward. A skill that does too much fails both ways: it won't fire when it should (a compound/abstract description can't match a concrete request) and it fires at the wrong moment (it triggers on a request that wanted only one of its five jobs). The **scope/trigger** sibling of `keep-skill-bodies-lean` (which owns the body **token-budget** axis) and the skill-tier counterpart of the marketplace's own ≤300-char agent-description routing cap. Distilled from the 2026-07-09 Claude-community subreddit scan; grounded against the Anthropic Agent Skills primary docs. Additive markdown — no consumer migration.

## 0.187.4 — 2026-07-08

### Fixed

- **P2 — decision-review safety envelope (`scripts/thing-decide.py`).** A **unanimous** panel `defer` (every voting seat independently says "this is a human call") could be routed into the Thor tie-breaker — whose `yes`/`no` verdict then becomes **binding** in `binding` mode — auto-resolving a decision the whole panel deferred. The `heimdall`-abstain re-screen (2b, added the same day) made this worse: a lone injection-seat abstention *also* forced a Thor convene on a unanimous defer. `_tally` now short-circuits `distinct == {"defer"}` straight to `defer` **before** the Thor branch (fail-safe — it can only send more decisions to the human). New `audit-gates.sh` Gate 17 case + a `defer-thor-flip` test mock prove Thor is never reached on a unanimous defer. _(From the autonomous 3-panel repo review, run 2026-07-08; the other findings in that run were already fixed on main via #585/#588.)_

## 0.187.2 — 2026-07-08

### Fixed

- **`guard-destructive.sh` interpreter-heredoc fail-open (P1, security).** `_strip_heredoc` blanked _every_ inert heredoc body before the deny-pattern scan, on the premise that a heredoc body is data-written-to-a-file. That premise is false when the heredoc feeds an interpreter (`bash <<EOF … rm -rf / … EOF`, `sh <<'X'`, `python3 <<PY`) — there the body IS the executed script, so a destructive payload was stripped and sailed through as ALLOW. The strip now fires only when the heredoc's command word is NOT an interpreter (skips `bash`/`sh`/`dash`/`zsh`/`ksh`/`python*`/`perl`/`ruby`/`node`/…, incl. leading `VAR=`/`env`/`\` forms); interpreter heredocs are scanned as code. Data heredocs (`cat`/`tee` → file) that merely document a destructive pattern are still stripped. Closes the internal inconsistency where `<(curl` / `$(curl` to a shell were caught but the equivalent heredoc-to-shell was not. Gate 5 gained interpreter-heredoc block fixtures + benign-data-heredoc pass fixtures.
- **Tribunal `network_write` classifier missed `gh api` implicit-POST (P2).** `classify()`'s flag-aware network-write override detected write bodies for `curl` and `wget` but had no `gh` branch, so `gh api … -f/-F/--field/--raw-field/--input` (an implicit POST that creates issues/PRs/comments) classified as `None` and auto-allowed unreviewed under a toggled-on `network_write` category. Added the `gh_body` branch; a bare `gh api <path>` GET still classifies as a read. Gate 21 #17e gained the implicit-POST forms + a bare-GET negative control.
- **`thing-orchestrator.sh` non-portable millisecond clock (P3).** `date +%s%3N` is a GNU-date extension; on BSD/macOS `date` exits 0 and emits a non-numeric `<seconds>N`, so the `|| echo 0` guard never fired and the audit `duration_ms` arithmetic errored (telemetry corruption). Replaced both call sites with a portable `_now_ms` helper that validates all-digits output and falls back to whole-second precision.

## 0.187.0 — 2026-07-08

### Added

- **Document-discovery pattern for cold agents (`DOCUMENT-MAP.md`).** Non-Claude-Code agents (Copilot CLI, Cursor, Aider) auto-load their instruction files but not a document-location index, so they re-run find/grep every turn to relocate known docs. New guidance closes the gap (forged via the FORGE two-panel + correlated-error-critic pipeline, which corrected the original "no persistent memory" framing):
  - `knowledge/copilot-cli-customization.md` §7 — the canonical mechanism: inline-vs-standalone placement, ~50–300-doc sizing, and seed-then-hand-curate maintenance ("a stale map is worse than none").
  - `codex-onboarding` skill — a session-start "read the document map first" step + matching done-check.
  - `docs/best-practices/agent-onboarding.md` (new, repo-level) — the cross-tool Pattern, pointing at §7 rather than restating it.
  - `scripts/generate-document-map.py` (new, repo-level) — a stdlib-only, deterministic, config-driven **seed** generator (`--self-test` / `--check`). Ships as a reusable tool, **not** a committed map: RavenClaude's own durable docs are already indexed elsewhere, and its `docs/` is mostly dated one-offs. No CI gate.

## 0.186.1 — 2026-07-06

### Fixed

Autonomous 3-panel repo review (run 2026-07-06) — 24 confirmed findings, P1→P3, all mechanical (no design input). Rebased onto 0.186.0; complements the 0.184.5 security pass. Plugin-internal fixes:

- **P1 — tribunal false-positive on sibling plugins (`thing-decision.py`).** `THING_SUBSTRATE` used `plugins/*/hooks` and `plugins/*/scripts` wildcards, so in any repo shaped like a plugin monorepo a `Write`/`Edit` to an _unrelated_ plugin's hooks/scripts was pre-LLM denied with `xc.tribunal-self-disable`. Scoped the globs to `plugins/ravenclaude-core/…` (the Thing's actual substrate). Verified: core substrate still denied, siblings now allowed; Gate 24 green.
- **P2 — `enforce-layout.sh` silent fail on corrupt manifest.** An invalid `.repo-layout.json` (trailing comma, merge marker) made both jq reads empty → the forbid-only branch allowed every write with no signal. Now validates the manifest and warns to stderr + emits a `warn` hook event instead of silently disabling enforcement.
- **P2 — `runaway-brake.sh` counter race.** The per-session counter read-modify-write is now wrapped in a bounded `flock` (fails open) so concurrent tool calls can't clobber each other's increment and evade `max_total`/`max_consecutive`.
- **P2 — `dod-gate.sh` code-change detection.** Switched to `git status --porcelain=v1 -z` + suffix grep; the prior `awk $2` field-parse silently missed changed source files with spaces in the path (and split rename lines), skipping the gate.
- **P2 — tribunal seat kill robustness (`thing-orchestrator.sh`).** Per-seat `timeout` now uses `--kill-after=5s` so a `claude -p` ignoring SIGTERM is force-killed; the misleading watchdog comment was corrected (the per-seat timeout, not the watchdog, reaps the claude tree).
- **P2 — `apply-comfort-posture.py` clean errors.** `parse_yaml` now catches `yaml.YAMLError`, and `main()`/`run_v5` surface a bad YAML/level value as an actionable one-liner + exit 1 instead of a raw traceback.
- **P2 — `stream-ops.py` label no-egress cap + registry race.** Extends the 0.184.5 `terms` single-token cap to `label` (whitespace-collapse + length-cap, incl. the `extra={…}` bypass path) and serializes the registry read-modify-write with an advisory lock + a per-process unique temp file so concurrent writers can't clobber the event-count bump.
- **P3 — `thing-decide.py`** bounds the untrusted-input substring scan to avoid quadratic cost on attacker-sized fields; **`thing-seat.sh`** truncation detection now compares byte lengths (not locale char counts); **`sanitize-webfetch-body.py`** checks `stat().st_size` before reading a file into memory.

Marketplace-level fixes (CI + scripts, same review): `validate-marketplace.yml` (case-insensitive email guard; duplicate-catalog-entry detection), `check-marketplace-claims.py` (anchor the `<N> plugins` count regex to total-count forms), `generate-bi-report.py`, `eval-adaptive-classifier.py`, `render-trees.py`, `cleanup-branches.sh`, `archive-branch.sh`, `thing-golden-eval.py`.

**Migration:** none — backward-compatible bug fixes and hardening.

## 0.185.0 — 2026-07-03

### Added

- **New best-practice — `compact-proactively-and-persist-state-before-compaction.md`** (27 rules, was 26). The actionable compaction discipline the `context-window` concept card only _described_: (1) compact **proactively** at task boundaries — auto-compact fires late (~80% of the window) when context rot has already started, so `/compact` while clean yields a sharper summary; and (2) **persist load-bearing state before compaction** — a compact recap is a _summary_, so intermediate reasoning, rejected approaches, and plans that live only in the conversation are discarded; write them to a file/commit/test first, or anchor them with `/compact <preservation instructions>`. Grounded in [Anthropic's best-practices guide](https://code.claude.com/docs/en/best-practices) and cross-checked against `knowledge/concepts/context-window.md`. This was the candidate the [2026-07-02 scan](../../docs/research/2026-07-02-claude-subreddit-scan/README.md) explicitly deferred as the strongest next candidate; surfaced by the 12th recurring Claude-subreddit scan ([`docs/research/2026-07-03-claude-subreddit-scan/README.md`](../../docs/research/2026-07-03-claude-subreddit-scan/README.md) — 4 findings, 1 approved). **Migration:** none — additive consumer-facing markdown.

## 0.184.5 — 2026-07-06

### Fixed

- **Security (P1) — `guard-destructive.sh` command-substitution boundary gap.** `_is_dangerous_find` / `_is_dangerous_truncate` / `_is_dangerous_git_branch_delete` used a boundary class that omitted the command-substitution openers `(`/backtick that `_is_dangerous_rm` deliberately includes, and a trailing `-delete)` (closed by the subst paren) dodged the action check — so `$(find / -delete)`, `$(truncate -s 0 /etc/passwd)`, and `$(git branch -D main)` slipped the guard while the same `$(rm -rf ~)` wrap was caught. All three now use `_CMD_BOUNDARY`; a new `_CMD_END` boundary recognizes the trailing subst closer. Gate 5 fixtures added.
- **Security (P1) — SessionStart capability-banner prompt-injection break-out.** `capability-orientation.py` inlined repo-controlled `design-project.json` `name`/`mirror_dir` and `run-config.json` `rationale` with only `.strip()`, so a hostile cloned repo could embed a newline + a literal `</ravenclaude-capabilities>` close tag to break out of the untrusted-data frame. Added `_sanitize_banner_field()` (strips CR/LF + U+2028/U+2029, removes any frame tag, caps length) applied to all three fields. Gate 19 frame-break fixtures added.
- **Security (P2) — `guard-destructive.sh` silent fail-open when `jq` is absent.** The guard read the command only via `jq`; a host without `jq` left `cmd` empty and `exit 0` (allow-all) with no warning. Added a `python3` fallback extractor and a loud stderr warning when neither parser is available.
- **Security (P2) — `guard-web-access.sh` blacklist fail-open on flow-style YAML.** `parse_section` parsed only block-style lists, so a `deny: [evil.com]` (the syntax the header comment + template advertise) yielded an empty deny list. Now parses both flow- and block-style. Gate added.
- **Robustness (P2) — `stream-ops.py` `append_event` `terms`** are now length-capped and rejected if they carry whitespace (single-token contract), matching the `summary` no-egress hardening.

## 0.184.4 — 2026-07-02

### Added

- **New best-practice — `give-the-agent-a-verification-signal-it-can-read.md`** (26 rules, was 25). The umbrella principle that the repo's existing enforcement leaves (the definition-of-done Stop gate, expensive-test front-loading, the visual render→see→iterate loop, the adversarial reviewer) each instantiate but that no single rule named: every task should carry a check that emits a machine-readable pass/fail, and the agent should iterate to green and show the evidence before reporting done. Grounded in [Anthropic's best-practices guide](https://code.claude.com/docs/en/best-practices) § "Give Claude a way to verify its work" (its four enforcement levels map onto the four existing leaves); surfaced by the 7th recurring Claude-subreddit scan ([`docs/research/2026-07-02-claude-subreddit-scan-verification-loop/README.md`](../../docs/research/2026-07-02-claude-subreddit-scan-verification-loop/README.md) — 4 findings, 1 approved). **Migration:** none — additive consumer-facing markdown.

## 0.184.2 — 2026-07-02

### Fixed

- **Security — `guard-destructive.sh` command-substitution bypasses.** The `-m "…"` / heredoc-body stripping blanked a **double-quoted** `-m "$(…)"` body and a **bare** `<<EOF` heredoc body before the destructive-pattern scan, while bash still executed the substitution at run time — so `git commit -m "$(rm -rf ~)"` and `cat <<EOF … $(rm -rf ~) … EOF` slipped the guard. A quoted body is now stripped only when it carries no command substitution (`$(`/backtick), and the command-word boundary was extended to treat `(`/backtick as boundaries (composing with the `/` path-qualified boundary from the same-day review) so `$(rm …` is caught. Gate 5 regression fixtures added.
- **Security — secret leakage.** `guard-destructive.sh`'s `_deny()` echoed the raw command to stderr (captured into the transcript) and `_emit_hook_event` wrote the free-form `path` field (the full command) to `hook-events.jsonl` unscrubbed; both now pass through `_scrub_reason()`.
- **Robustness — tribunal engines** (`thing-decide.py` / `thing-decision.py`) now fail safe on valid-but-non-object stdin JSON instead of raising `AttributeError`.

**Migration:** none — backward-compatible hardening.

## 0.184.1 — 2026-07-02

### Fixed

- **`guard-destructive.sh` path-qualified evasion closed (P0).** The four structural danger checks (`_is_dangerous_rm`/`_chmod`/`_find`/`_truncate`) anchored the command name only after start-of-string / `;` / `&` / `|` / whitespace, so a **path-qualified** invocation (`/bin/rm -rf /`, `./rm -rf ~`, `/usr/bin/chmod -R 777 /`) slipped past the primary consumer guard untouched — no `deny_patterns[]` entry backstops rm/chmod/find/truncate. The left-boundary character class now also matches after `/`. The same pass closes two missed forms: `find … -execdir` (the per-match twin of `-exec`) and `truncate --size=0` (the long-option spelling of `-s 0`). Verified with an adversarial + regression harness (10 blocks incl. the new evasions, 6 no-false-positive controls). (Autonomous 3-panel repo review, P0 + two P2s.)

## 0.183.1 — 2026-07-02

### Fixed

Autonomous 3-panel repo review (categorize → validate → tie-break) → the design-free confirmed fixes. Plugin-scoped items in this release:

- **`guard-destructive.sh` bypasses closed (P0/P1/P2).** `$IFS`/`${IFS}` whitespace-substitution and a leading backslash (`\rm -rf /`) are now neutralized during normalization; git global options (`git -c x=y push --force`, `git --git-dir=… push`) are stripped so every `git` subcommand pattern re-anchors; force-branch-delete is caught order-independently (`git branch --delete --force`, `git branch main -D`); the fork-bomb pattern tolerates whitespace inside the parens. Verified with an adversarial + regression harness (21 blocks, 0 false positives).
- **Tribunal fails CLOSED on catalog error (P0).** `thing-decision.py` `_screen_always` now denies (with a `screen_error` flag) if the concerns catalog can't be loaded/evaluated, instead of silently clearing the force-push / `curl|sh` / self-disable hard rules. Reproduced + verified fixed.
- **`enforce-layout.sh` relative-path bypass closed (P1).** A relative `$file` (as Copilot's file-pretool adapter forwards) is normalized to absolute before the in-project prefix test, so it no longer silently skips the layout + task-scope gates.
- **Honesty fixes (P2/P3).** `reset-plugin-cache.py` docstring/comment corrected to stop overstating `--confirm` as proof-of-human (the tribunal `xc.ragnarok-non-user-invocation` concern is the real user-only enforcement); `pseudonymize-brief.py` docstring corrected to match its actual fail-closed behavior (writes nothing on error, not the raw input).
- **`evaluate-dispatch.js` reference fixed (P2).** Replaced raw `Date.now()`/`new Date()` (which throw under the dynamic-workflow runtime) with a resume-safe `_now()`/`_isoNow()` shim, and added the `rc-deep-research` search fan-out `.catch()` mirror so one failed search angle can't abort a research run.

**Migration:** none — the guard/layout/tribunal changes only *close* bypasses and *fail safer*; nothing a consumer relies on changes on `/plugin marketplace update`.

## 0.183.0 — 2026-07-02

### Added

- **New best-practice (Claude subreddit scan, 2026-07-02):** [`best-practices/the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow.md`](best-practices/the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow.md) — enable Claude Code's OS-enforced Bash sandbox (Seatbelt/bubblewrap) to close the subprocess-access gap that `deny`/`ask`/`allow` rules structurally can't reach (a `Read(**/.env)` deny doesn't stop a `python -c "open('.env')"` subprocess — the gap the repo's own `knowledge/claude-code-permissions.md` names), and to earn prompt-free autonomy without `--dangerously-skip-permissions`. The OS-enforced complement to the existing `permissions-are-deny-ask-allow` rule (→ 25 rules). Grounded in the Anthropic [sandboxing docs](https://code.claude.com/docs/en/sandboxing) + this repo's containment-posture caveat. Research + panel: [`docs/research/2026-07-02-claude-subreddit-scan/README.md`](../../docs/research/2026-07-02-claude-subreddit-scan/README.md). **Migration:** none — additive markdown.

## 0.182.1 — 2026-07-01

### Fixed

- **Research-sweep (Tier-A news cadence):** `knowledge/orchestrator-data-egress.md` — the ZDR aside noted Fable 5 / Mythos 5 as "_availability suspended 2026-06-12_"; the US export controls were **lifted 2026-06-30** and access is restoring from 2026-07-01, so the aside now reads "suspension lifted 2026-06-30; access restoring — re-verify per surface." The ZDR-ineligibility fact itself is unchanged (both models still force 30-day retention and cannot run under ZDR). Fan-out sibling of `claude-app-engineering` 0.9.6 / `ai-coding-model-guidance` 0.3.9. **Migration:** none — knowledge-file content only.

## 0.171.1 — 2026-06-24

### Fixed

- **Count-string sync.** The streams (P1/P4) + convergence (P1) builds added hooks (17→19) and a skill (43→44), but the descriptive count strings in `README.md` (Skills/Hooks table + prose), `plugin.json`, and the marketplace entry weren't bumped — `marketplace-claims` (Gate 12) flagged the drift on integrated `main`. Synced to the actual counts (44 skills, 19 hooks) + regenerated artifacts. **Migration:** none.

## 0.171.0 — 2026-06-24

### Added

- **Convergence engine — P4 (`rc converge` verb + report hardening).** `rc converge` runs the refine-to-rubric loop + renders the honest report (`rubric-pass | capped | plateaued | budget-exhausted` + residual gaps); the renderer rejects over-claims. Completes the engine (P0–P4). Proven by **Gate 119** (must-fail-overclaim teeth). **Migration:** none.

## 0.170.0 — 2026-06-24

### Added

- **Convergence engine — P3 (full loop + cross-model judge).** `loop.py` runs derive→evaluate→refine→re-evaluate→terminate, emitting the **best** iteration (keep-best, never the last) with a constrained no-overclaim report. `judge.sh` is the subjective judge — it **REFUSES (exit 5) when the judge model family equals the author's** (never self-grade). Security-reviewed (cross-model `claude -p` path): no blocker; anti-self-grade normalization broadened (closes -v2/-latest/-preview bypass) + `is_error`/verdict validation + secret-scrub synced to `_scrub.sh`. Proven by **Gate 118** (loop + judge≠author + keep-best + constrained report, with a must-fail-keepbest teeth half). **Migration:** none.

## 0.169.0 — 2026-06-24

### Added

- **Convergence engine — P2 (evaluate, objective-gates-first).** `evaluate.py` runs the deterministic/objective gates FIRST; a red hard gate short-circuits straight to refine with **0 model-judge calls** (cheap + defends the plateau/sycophancy failure mode). Proven by **Gate 117** (broken artifact ⇒ 0 judge calls, with a must-fail-judge-first teeth half). **Migration:** none.

## 0.168.0 — 2026-06-24

### Added

- **Convergence engine — P1 (rubric library + derive).** Externalized versioned rubric library (`knowledge/convergence-rubrics.md`) + `derive_rubric.py`: explicit requirements become top-weighted dims, best-practices retrieved per artifact-kind, and an **additive-only** "commonly-missed" pass proposes the unknown-unknowns forced to `derived`+`verified=false` (a model can only ADD, never auto-grade, even if the proposal lies). `agent-file` delegates to `agent-quality-rubric`. Proven by **Gate 116** (schema-valid + explicit=weight-max + derived-forced-unverified, teeth half). **Migration:** none.

## 0.167.0 — 2026-06-24

### Added

- **Convergence engine (`refine-to-rubric`) — P0 (deterministic core).** The model-free foundation: `skills/refine-to-rubric/scripts/converge.py` `terminate()` (the stop decision is NEVER a model judgment) + `weighted_score()` + keep-best argmax (emit the best iteration, never the last) + rubric/scorecard JSON schemas. Verdict vocabulary is `rubric-pass | capped | plateaued | budget-exhausted` — the engine never claims "perfect". Proven by **Gate 115** (7 stop cases + keep-best + no-overclaim, with a must-fail-redgate teeth half). **Migration:** none — additive skill scaffolding.

## 0.166.0 — 2026-06-23

### Added

- **Agentic work-streams — P4 (opt-in per-prompt attribution hook).** A fail-open `UserPromptSubmit` hook (`hooks/stream-prompt-attribute.sh`) that attributes each prompt to the active stream — **opt-in, default OFF** (session-boundary remains the default; this is the locked tiebreak's optional upgrade). It is **fail-open** (any error/timeout exits 0 and never blocks the prompt), **derived-labels-only** (never egresses prompt text), and ships Copilot parity via the repo-level adapter. Security-reviewer: CLEAR-TO-MERGE (all 6 invariants pass). Proven by **Gate 114** (fail-open + no-egress + opt-in-default + latency ceiling + Copilot parity, with teeth). **Migration:** none — default OFF, so byte-identical behavior until a consumer sets `stream_hook: per_prompt`.

## 0.165.0 — 2026-06-23

### Added

- **Agentic work-streams — P3 (dashboard "Streams" Observe tab).** A read-only Streams view in the dashboard Observe section, served by a new `/__streams` endpoint added **byte-identically to both `serve-dashboards.py` copies** (Gate 32 parity holds). The reader **whitelists** event fields, so a hand-corrupted history line carrying a `prompt` field is dropped before it can reach the dashboard (no-prompt-egress at the read boundary). Proven by **Gate 113** (render + `/__streams` parity + no-prompt-egress field whitelist). **Migration:** none — additive read-only tab; degrades to an honest empty state on a static host.

## 0.164.0 — 2026-06-23

### Added

- **Agentic work-streams — P2 (sticky session-boundary classify + `/stream` override).** `scripts/stream-session-start.py` classifies at SessionStart from a PROMPT-FREE signal (git branch + recent commit subjects — never prompt text) when no stream is active and SUGGESTS one; when a stream IS active it is a **sticky no-op** (the false-new-stream / 'fix it' / 'continue' mitigation). Config: `stream_classify: off|label_only(default)|auto` + clamped `stream_threshold`. Adds the `/stream` override command. **Security:** a ReDoS in the threshold regex (reachable from the SessionStart banner via a hostile cloned `comfort-posture.yaml`) was found + fixed (de-ambiguated numeric capture + 64 KiB cap + a 10s hook timeout). Proven by **Gate 112** (sticky-no-reclassify + override round-trip + threshold bounds + ReDoS-bounded, with a must-fail-sticky teeth half). **Migration:** none — defaults to label_only (suggest-only), banner appears only once a stream exists.

## 0.163.0 — 2026-06-23

### Added

- **Agentic work-streams — P1 (CLI + session-boundary tracking, no prompt-hook).** `rc streams` verb (list/show/status/create/set-active/get-active) over the P0 store; an `active-stream` pointer; a SessionStart banner line (`capability-orientation.py`) surfacing the active stream + count (slug/counts only, never history content) and stating the sticky rule; and a fail-safe Stop hook (`hooks/stream-session-close.sh`) that appends one DERIVED `session_closed` event + refreshes `state.md` for crash-resume (session_id FK; never prompt text; never blocks the stop). Proven by **Gate 111** (slug anti-traversal + banner no-egress + session-close derived-only, with a must-fail-traversal teeth half). **Migration:** none — additive CLI verb + fail-safe Stop hook; the banner only appears once a stream exists.

## 0.162.0 — 2026-06-23

### Added

- **Agentic work-streams — P0 (store + deterministic classifier).** The model-free foundation for organizing agentic work into named streams under `.ravenclaude/streams/`: `scripts/stream-classify.py` (stdlib TF-IDF/cosine classifier — emits DERIVED features only: `terms`/`word_count`/`label`, never raw prompt text) + `scripts/stream-ops.py` (registry + per-stream `history.jsonl` + `state.md`, slug anti-traversal, a no-egress tripwire that rejects raw `prompt`/`text`/`content` keys, session_id FK back to `runs/`). Proven by **Gate 110** (no-egress + determinism + classify-accuracy, with a must-fail-egress teeth half). No deps, no model call. **Migration:** none — additive libs + one gate.

## 0.161.8 — 2026-06-23

### Changed

- **Decision-review: verify-the-premise-before-you-prompt + batch.** Analysis of a consumer-repo yes/no prompt log found all the prompts were *correctly* deferred by the tribunal (genuine preferences / high-blast safety / product-intent) — the avoidable cost was **re-asking** the same decision because it was surfaced before its load-bearing claim was verified (a 'missing columns' claim that turned out false cost three rounds). Extended the CGP "verify the load-bearing assumption" clause and `skills/decision-review/SKILL.md` with a **Before you prompt at all** discipline (verify the factual premise, then batch related decisions into one post-verification ask) and added a dashboard-disambiguation prior (`commands/dashboard.md`: unqualified "open the dashboard" → the RavenClaude comfort-posture dashboard). Also added a **prompt-legibility** rule to the same skill: a surfaced `AskUserQuestion` must be succinct — the question states the specific action + blast radius in one line, and each option is labeled by its **consequence** (`Hard-deny — blocks every PROD query` / `Ask each time — prompts per query`) rather than bare `Yes`/`No`, so the human knows exactly what approve-vs-deny does without reading the context. Behavioral/doc only — no engine change, no auto-deciding of genuine preferences. **Migration:** none.

## 0.161.7 — 2026-06-23

### Fixed

- **Heimdall (command-review injection seat) false-positived on legitimate Markdown doc edits.** For a `file_edit_project` review the seat screened the agent's own authored file content with the same injection heuristics used for untrusted external data, so a normal collapsible block (`<details>`/`<summary>`/`</details>`) read as a "forged closing delimiter" and a status-word diff (a line changing `DONE` → `IN PROGRESS`) read as "task-state manipulation" — a single Heimdall `injection_detected` then denied the whole edit despite a high-confidence Mímir allow (observed in a consumer repo blocking routine `docs/` rollups). Added a static, trusted resolved-fact line to the seat prompt (`thing-seat.sh`) — **scoped to `file_edit_project` only** — telling the seat the payload is the agent's own authored edit to a realpath-verified trusted file, that structural Markdown/HTML and status-word transitions are normal authored content, and that `injection_detected` is reserved for text targeting the tribunal itself. The deterministic concern screen (which never flagged these) and every other tool shape (Bash, network, MCP, `file_edit_global`) are unchanged — they keep the full injection screen. Proven by **Gate 105** (carve-out present + scoped to `file_edit_project` only + deterministic screen still clean + a stripped-carve-out teeth half).

## 0.161.6 — 2026-06-23

### Fixed (residual repo-review fixes — re-checked against current `main`)

A re-run of the 2026-06-22 repo review against the moved `main` (0.161.5) found several
issues still unfixed; the rest had already landed via the parallel #441/#445/#449/#457/#461/#479
work (skill/rule/hook counts, CHANGELOG currency, feedback-report freshness, the `check-layout`
`**` semantics — now documented-intentional). Still-open fixes, landed here:

- **`guard-web-access.sh` session resolution (P1).** The web-access guard read the session id
  from `$CLAUDE_SESSION_ID` only — which native Claude Code does not export to hooks — so every
  native session collapsed into `runs/unknown/` and the per-session web-allow + first-use trust
  markers leaked across sessions. Now resolves via the shared `_ee_resolve_session()`
  (`$CLAUDE_SESSION_ID` → payload `.session_id` → `unknown`), with a jq-free fallback. Coexists
  with the v0.161.4 consent-ordering change (different code region). Gate 70 stays green.
- **`format-on-write.sh` (P3).** Guarded the absolute-path `cd` so a directory that vanished
  between the existence check and the resolve can't abort the PostToolUse formatter under `set -e`.
- **`scripts/check-md-links.py` (P2).** Titled-link parsing splits on the ` "` delimiter, not
  arbitrary whitespace, so a relative path containing a space is no longer truncated/false-flagged.
- **Dashboard-server endpoint claims corrected (accuracy).** `CLAUDE.md` (scripts/ bullet) said
  serve-dashboards exposes "`/__save` + `/__read` + `/__classify` only, no `/__run`" while a later
  line said it exposes `/__run` — a direct self-contradiction, and `README.md` repeated the stale
  "limited to 3 endpoints" claim. The server actually exposes 15 endpoints; the docs now state the
  accurate surface (CSRF-guarded `/__save`/`/__read`/`/__classify` + allow-listed `/__run`
  install/update/status — **no arbitrary shell** — + read-only observability feeds).
- **Component counts + roster (accuracy).** README still said 14 agents / 16 hooks / 4 slash
  commands and omitted `viz-spec-reviewer`; corrected to 15 agents / 17 hooks / 7 commands and added
  the missing specialist. Manifest descriptions now list `/forge` + `/reset-plugin-cache`.
- **`scripts/content-scan.py` redirect re-validation (P3).** The SSRF scheme check ran on the
  input URL only; urllib follows redirects, so it's now re-validated on the final resolved URL.
  (Operator-invoked script, not the agent hot path.)

### Notes

- **Migration:** none — hook fixes are fail-safe and behavior-preserving on the common path;
  the rest are doc-accuracy and an operator-script hardening. Regenerated `dashboard.html` /
  `index.html` / `feedback-report.html` / copilot package for the version bump.

## 0.161.5 — 2026-06-23

### Fixed

- **`skills/cross-platform-determinism/SKILL.md`** — the skill's runnable "repro recipe" code blocks still pointed at `scripts/generate-repo-guide.py` and `scripts/check-guide-fresh.sh`, both deleted when Gate 11 was retired (v0.124.0) — `No such file or directory` for anyone following them. Repointed the recipes to the live successor `scripts/generate-index-dashboard.py` (same `--check` strip-before-diff freshness contract); kept the historical bug attribution honest. Markdown-only; no behavior change.

## 0.161.4 — 2026-06-23

### Fixed (residual repo-review fixes not already on main)

A 2026-06-19 repo review surfaced ten fixes; six were independently landed on `main` via the parallel #449 work (option-polarity guard, `archive-branch` base-branch resolution, the two-panel lens-key fix, the stale feedback-report regen, etc.). These four were **not** on `main` and are landed here:

- **`guard-web-access.sh` consent ordering (P2).** The first-use "ask" for a YAML-whitelisted domain wrote its per-session "seen" marker **before** the user answered, so a DENIED first fetch silently auto-allowed on retry. Consent is now recorded by a **new PostToolUse(WebFetch) hook, [`mark-web-domain-seen.sh`](hooks/mark-web-domain-seen.sh)**, which fires only after a fetch proceeds; a denied first fetch re-prompts. Wired in `hooks/hooks.json` + the dev-mirror `.claude/settings.json`. (Hook count 16 → 17.)
- **Engine-level deterministic high-blast floor in `thing-decide.py` (P2).** `decide()` now screens the decision question/context against a destructive vocabulary (`_screen_high_blast`, mirroring `route-decision-review.sh` §3) and forces `defer`, so "high-blast never auto-resolves" no longer depends on the caller's flag or an LLM seat. Can only **add** a defer — purely fail-safe.
- **`route-decision-review.sh` nested `decision_review` form (P3).** The hook now parses the nested `decision_review:\n  mode: binding` form (the engine already accepted it), not just the flat form — and its high-blast heuristic gained `force-with-lease`/`truncate`/`wipe`/`revoke`/`purge` (word-anchored `drop`).
- **`rc-deep-research.js` latency-trip event (P3).** The dispatch-evaluator latency circuit-breaker now surfaces its trip on Heimdall via a fire-and-forget `agent()` emit (the documented TODO), applied identically across all three byte-identical copies (the reference + both mirrors). Unawaited + rejection-swallowed, so a telemetry failure can never affect the run.

### Notes

- **Migration:** none — the web-access fix only makes first-use confirmation *stricter* (a denied domain re-prompts) and adds an opt-in PostToolUse hook; the high-blast floor only adds defers under the opt-in `decision_review` posture; the nested-parse and latency-event changes alter no consumer-facing schema. Gate 70's web-access subtest was updated to the corrected consent-ordering contract (+ a teeth subtest proving a no-consent retry re-asks). All audit-gates pass.

## 0.161.1 — 2026-06-16

### Fixed

- **`route-decision-review.sh` mapped a binding yes/no verdict to an option by index, not semantics.** The eligibility gate accepts any two yes/no-shaped options regardless of order, but the act-block hard-coded `yes → options[0]` / `no → options[1]`. An `AskUserQuestion` phrased with the negative option first (`["Cancel","Proceed"]`, `["No","Yes"]`, `["Reject","Approve"]`) would receive a _binding_ deny instructing the agent to choose the **opposite** option — and, being auto-resolved, the human never saw it. Each option's polarity is now classified and the verdict maps to the matching option; ambiguous polarity fails safe to ALLOW. Proven by a new reverse-ordered fixture in Gate 31 (`audit-gates.sh`).
- **`thing-concerns.py` `screen-always` catastrophe floor failed OPEN on an embedded newline.** The two `always_screen` + `pre_llm_deny` hard rules (force-push to a protected branch, `curl … | sh`) bridge program→argument with `.*`, but the regexes were searched without `re.DOTALL` and the screening variants were not newline-flattened — so a command carrying a real newline (a shell line-continuation) between `git push`/`curl` and the dangerous flag silently dodged the hard DENY. A newline-flattened screening variant is now matched alongside the raw + normalized command (only ever ADDS a match, never removes one). Proven by a new Gate 15 fixture. **Security-floor change.**
- **`apply-comfort-posture.py` PyYAML-less fallback parser mis-split a quoted override key containing a colon** (`"Bash(ls:*)": deny` → key `"Bash(ls`), aborting `/set-posture` on a no-PyYAML consumer. The scalar split is now quote-aware; unquoted keys are unchanged.
- **`guard-destructive.sh` `git push -f` pattern over-matched a branch name ending in `-f`** (`git push origin feature-f` was blocked). The pattern now requires `-f` to be a standalone flag; `-f` / `--force` force-pushes are still blocked (fails closed regardless).
- **`thing-decision.py` self-disable guard missed non-canonical falsy `thing` values** (`thing: 0` / `"0"` / `disabled` / `none`) that `thing_enabled_for` treats as off; it now mirrors that truthiness exactly. Also: the seat/panel timeout config excludes `bool` so `seat_timeout_seconds: true` isn't coerced to a 1-second timeout.
- **`rc-deep-research.js` eval stats under-counted verify agents** (both copies) — a flat `voted.length * VOTES_PER_CLAIM` that ignored per-claim fan-out + escalation; now a real `verifyAgentsFired` counter (baseline unchanged; Gate 52 untouched).
- **`two-panel-plan-review.js` could mislabel lens results** (both copies) when a panel agent returned null; each result is now paired with its lens key before `filter(Boolean)`.
- **New cross-plugin agent-name-uniqueness check** in `scripts/check-frontmatter.py` (resolves the `partner-success-manager` collision — `edtech-partner-success` renamed its specialist to `edtech-partner-success-manager`).

### Notes

- **Migration:** none — `decision_review` is off by default; the catastrophe-floor fix only closes a bypass (never relaxes a deny).

## 0.161.0 — 2026-06-22

### Added

- **New best-practice — "MCP tool context is a budget — enable only what you need"** ([`best-practices/mcp-tool-context-is-a-budget-enable-only-what-you-need.md`](best-practices/mcp-tool-context-is-a-budget-enable-only-what-you-need.md), 20 rules total). Every enabled MCP server preloads its full tool schemas (names + descriptions + JSON schemas) into the context window before any work — a widely-shared community measurement put 7 servers at ≈67K tokens (~⅓ of a 200K budget). The rule's levers: right-size the enabled-server set per kind of work, prefer tool-search / lazy-loading (load schemas on demand) over preloading, and measure with `/context`. The worked example is **this repo's own deferred-MCP-via-`ToolSearch` session model** (tools surfaced name-only, schema fetched just-in-time) — the count→cost tax paid down to near-zero by design. Sibling to the `AGENTS.md` agent-description ~15K budget (the authoring-side analog) and the generic `knowledge/concepts/context-window.md` concept (this rule is its MCP-specific, actionable corollary). Sourced from the [2026-06-22 Claude subreddit scan](../../docs/research/2026-06-22-claude-subreddit-scan/README.md) (1 of 4 findings approved; the worktree finding was already shipped by the 2026-06-13 scan, the other two deferred/denied as covered).

### Notes

- **Migration:** none — additive markdown; nothing in a consumer's installed plugin changes on `/plugin marketplace update`.

## 0.160.0 — 2026-06-22

### Added

- **New best-practice — "Run parallel Claude Code instances in separate git worktrees — never aim two writers at one working tree"** ([`best-practices/isolate-parallel-claude-instances-in-git-worktrees.md`](best-practices/isolate-parallel-claude-instances-in-git-worktrees.md), 19 rules total). Names the **peer-process** parallelism posture the sub-agent rule [`delegate-reads-fan-out-keep-branch-writes-in-main.md`](best-practices/delegate-reads-fan-out-keep-branch-writes-in-main.md) explicitly defers: give each concurrent Claude Code instance its own `git worktree`/branch so two writers don't stomp one working tree's files + index, reconcile via merge/PR. Leads with native `--worktree`/`-w` + `claude agents` support; cites the bundled `new-worktree`/`cleanup-worktrees` skills + the Sleipnir convention. Sourced from the [2026-06-13 Claude subreddit scan](../../docs/research/2026-06-13-claude-subreddit-scan/README.md) (1 of 4 findings approved).

### Changed

- **Corrected a falsified premise in `delegate-reads-fan-out-keep-branch-writes-in-main.md` + CLAUDE.md §"Delegating branch-mutating work" + `knowledge/subagent-isolation-and-tooling.md`.** The original "background sub-agents are auto-denied git checkout/commit/push (confirmed behavior)" / "`isolation: "worktree"` strips `Read`" claims were re-verified against current primary docs ([sub-agents.md](https://code.claude.com/docs/en/sub-agents)) **and a direct this-session probe** (a non-isolated foreground sub-agent ran `git checkout -b` + `git commit`, both exit 0, no permission gate) and found **not universal**: a sub-agent's writes are governed by its `tools`/`disallowedTools` grant + permission mode, and `isolation: "worktree"` isolates the working directory, not the tool grant. The advice (serialize branch-writes, or isolate each writer in its own worktree) is re-grounded in the real hazard — concurrent writers racing on one shared working tree — and the best-practice's status was downgraded **Absolute → Pattern**. The 2026-05-23 denials are scoped as conditionally true (`run_in_background: true` × an `ask`-tier posture, where a background agent can't surface the approval prompt). **Not re-tested:** sub-agent `git push`, background agents, and the web/remote git-proxy mode.

### Notes

- **Migration:** none — one additive best-practice + corrected guidance/status in existing best-practice/knowledge/constitution files; no hook, script, or settings change. Nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

## 0.159.1 — 2026-06-21

### Changed

- **Research-sweep:** `knowledge/orchestrator-data-egress.md` — the ZDR note citing Fable 5 / Mythos 5 forcing 30-day retention now carries a dated **availability-suspended (2026-06-12)** aside pointing at the model lineup. The ZDR-ineligibility fact itself is unchanged; only an availability pointer was added so the egress guidance reflects that both models are currently disabled across all surfaces (US export-control directive). No migration — knowledge-file content only.

## 0.159.0 — 2026-06-22

### Added

- **Visual-feedback-loop `parity` gate — diff a visual against a known-good exemplar** ([`skills/visual-feedback-loop/driver.py`](skills/visual-feedback-loop/driver.py), v0.2.0). Surfaces a structural class the layout linter can't see: a visual that is *perfectly placed* yet renders **blank** because its render skeleton is missing something its working twin has. The new `parity` config (`{"candidate": "...visual.json", "reference": "...visual.json"}`) extracts a PBIR render skeleton from each and is **asymmetric** — it **fails** (`next_action: match-reference-exemplar`) on what the candidate is **MISSING** relative to the exemplar (a missing query role `Values`/`Data`/`Indicator`; a dropped objects key, e.g. a `card` that dropped `labels` and substituted `calloutValue`; a missing per-item `$id`) and **passes benign additions** (an extra cosmetic object key, an optional role). It is a **diff surfacer, not a render oracle** — it validates the exemplar first (refuses a self-reference or a degenerate no-query-role reference → `not_captured`, so a bad exemplar can't launder a ship), and a different `visualType`/non-PBIR shape is also `not_captured`. Echoes only allowlist-sanitized schema tokens (`\A…\Z` + fullmatch, so a trailing-newline token can't slip through), never raw `visual.json` content. Documented generically for all declarative-viz (Vega-Lite, Tableau) in [`knowledge/visual-feedback-loop.md`](knowledge/visual-feedback-loop.md); runnable differ is PBIR-first. Hardened by an adversarial FORGE review (12 Gate-100 parity cases incl. benign-superset must-pass, pure-drop/partial-`$id`/degenerate-reference/self-reference, candidate-path traversal, + two teeth mutants). Origin: a Fabric/PBIR field session that burned four deploy-and-eyeball cycles before diffing against the confirmed-working exemplar cracked it.

### Notes

- **Migration:** none — additive `parity` gate (off unless a config supplies it); the driver envelope shape is unchanged. Nothing changes on `/plugin marketplace update`.

## 0.158.0 — 2026-06-22

### Added

- **`rc` launcher — host-agnostic dashboard front door** ([`bin/rc`](bin/rc), new `plugins/*/bin/**` layout glob). The `rc dashboard` "one-verb front door" the docs referenced was a phantom (no `rc` on disk); it now exists for real as a thin bash dispatcher (one verb today: `rc dashboard [--port N] [--no-open]`). It **never `cd`s** — `serve-dashboards.py` resolves the project root from `Path.cwd()`, so the launcher `exec`s the server with the caller's cwd preserved (`.ravenclaude/` lands in the consumer's repo) and works identically under Claude Code, GitHub Copilot CLI, or a bare terminal.
- **Copilot dashboard discoverability** — [`scripts/generate-copilot-plugin.py`](../../scripts/generate-copilot-plugin.py) appends an always-applicable **"Launch the comfort-posture dashboard"** block to the generated [`copilot/AGENTS.md`](copilot/AGENTS.md) (parallel to the opt-in Relay-mode block). Copilot reads `AGENTS.md` natively, so "open the dashboard" now Just Works in a Copilot repo — closing the gap where there's no `/dashboard` slash command (Claude-Code-only) and Copilot had to reverse-engineer the launch each time.

### Fixed

- **Phantom `rc dashboard` references made real.** [`commands/dashboard.md`](commands/dashboard.md) now documents where `rc` lives, the PATH one-liner, and the Copilot "just ask" path; the N-A `bin/` disposition in the CLAUDE.md Value-add table is updated to BUILT.

## 0.155.0 — 2026-06-11

### Added

- **New best-practice — "Permissions are a three-tier posture (`deny`/`ask`/`allow`), not an on-off switch"** ([`best-practices/permissions-are-deny-ask-allow-not-an-on-off-switch.md`](best-practices/permissions-are-deny-ask-allow-not-an-on-off-switch.md), 18 rules total). Distills the Claude Code permission model: eval order is `deny` → `ask` → `allow` (first match wins; specificity doesn't reorder — a `deny` always beats an `allow`), sort operations by reversibility (idempotent reads → `allow`, intent-changing → `ask`, irreversible/secret → `deny`), `allow` is a convenience layer while `deny` is the boundary, `--dangerously-skip-permissions` skips the `deny` backstop too (isolated envs only), and `settings.json` is reviewed-in-a-PR like code. The repo's own 20-entry `.claude/settings.json` deny list is the worked example. Generalizes the existing WebFetch-specific `web-access-allow-deny-list-before-first-fetch.md` (which it declares itself the parent of). Sourced from the [2026-06-11 Claude subreddit scan](../../docs/research/2026-06-11-claude-subreddit-scan/README.md) (1 of 4 findings approved; the other three deferred/denied as covered or out-of-core-scope).

### Notes

- **Migration:** none — additive markdown; nothing in a consumer's installed plugin changes on `/plugin marketplace update`.

## 0.152.0 — 2026-06-10

### Added

- **`orchestrator: off | decide | full` behavioral knob** — the fourth behavioral commitment in `.ravenclaude/comfort-posture.yaml`. Routes team-lead orchestration to Claude when the host CLI is not Claude Code (e.g. GitHub Copilot routing GPT/Grok). Read directly by `spawn-team` at dispatch time; no new hook, no `apply-comfort-posture.py` change. Inert under Claude Code (host already IS Claude). Default: `full` (owner choice — route orchestration to Claude by default under a non-Claude host). Seeded as `orchestrator: full` in `templates/comfort-posture-balanced.yaml`.
- **`scripts/claude-orchestrate.sh`** — thin wrapper copying `thing-seat.sh`'s `claude -p` plumbing: plain `claude -p` (OAuth-compatible, never `--bare`), `mktemp` scratch dir, `_scrub.sh` sourced for egress backstop, `CLAUDE_PROJECT_DIR` defanged. **Three-layer recursion guard:** (1) `RAVENCLAUDE_ORCH_ACTIVE=1` env-var check at entry; (2) `THING_SEAT_ACTIVE=1` check; (3) `--tools ""` structural layer for both modes (the nested session has zero tools regardless of injection). Secret scrub on brief + roster before egress. **Fail-safe:** any non-zero exit → caller falls back to host orchestration; never hard-blocks. `decide` mode returns a JSON dispatch plan; `full` mode returns artifact content.
- **spawn-team Step 4.5** — orchestrator routing step in `skills/spawn-team/SKILL.md`: check `THING_HOST` + the knob, route to `claude-orchestrate.sh`, fall back to host on any failure.
- **Dashboard: Claude orchestrator control** (Pipeline/Configure tab) — three-radio `off`/`decide`/`full` select with per-mode cost callout and a `[host-only — inert under Claude Code]` badge. Round-trips via the existing `state`/`emitYaml`/`/__save` path (no new server endpoint).
- **Gate 102** (`audit-gates.sh`) — mock-claude-driven gate: recursion guard fires, seat guard fires, scrub fires on secret brief, fallback on absent claude, happy path passes. Must-fail halves prove both guards are real code: stripped guard lets re-entry through; stripped scrub lets secret through.

### Security

✅ **`ravenclaude-core/security-reviewer` sign-off COMPLETE (2026-06-10) — CLEAR-TO-MERGE.** The `claude -p` exec path was reviewed: all controls verified by execution + teeth-stripping (3-layer recursion guard incl. `--tools ""` for both `decide` and `full`, pre-egress secret scrub, nonce-wrapped injection envelope, scratch-dir isolation, total fail-safe-to-host). No blocking findings.

### Notes

- **Migration:** `orchestrator` defaults to `full` — a consumer on a NON-Claude CLI who hasn't set the key routes orchestration through `claude -p` by default on `/plugin marketplace update` (inert under Claude Code; set `orchestrator: off` to opt out).
- No existing hook, agent, rule, or other script was modified except `spawn-team/SKILL.md` (new routing step added) and `audit-gates.sh` (new gate appended).

## 0.151.0 — 2026-06-10

### Fixed

- **Gate 101 SVG linter hardened — `<foreignObject>` and remote/`javascript:` href now enforced** ([`skills/declarative-visualization/lint.py`](skills/declarative-visualization/lint.py)). `lint.py`'s `_check_svg()` previously only caught `<script>` elements and `on*` event attributes. Two additional SVG injection vectors are now flagged at exit 1:
  - `<foreignObject>` elements (XSS-escalation vector — embedded HTML can carry arbitrary scripts).
  - `href` or `xlink:href` whose value begins with `http://`, `https://`, or `javascript:` (network call + potential JS execution). **Safe local fragment refs like `href="#id"` are explicitly allowed** — the pattern matches only remote/script schemes, not intra-document references.
- **Gate 101 test extended** ([`hooks/tests/test-gate101-declarative-viz-linter.sh`]). Three new must-fail fixtures (`bad-svg-foreign-object.svg`, `bad-svg-remote-href.svg`, `bad-svg-javascript-href.svg`) and one new must-pass fixture (`good-svg-local-ref.svg` — safe local `href="#id"` + `xlink:href="#id"`). Mutant (always-pass) half extended to cover the two new bad SVG fixtures, proving the new checks are logic, not luck.
- **`knowledge/declarative-visualization.md` §4b reconciled**: the `<foreignObject>` and `xlink:href` rows' "Caught by" column updated from `security-reviewer (NOT yet linter-enforced)` to `lint.py (Gate 101)`. The "Honest scope" note updated to reflect that all four SVG vector classes are now linter-caught; Vega `signals`/`expr` remain security-reviewer-gated. The tracked follow-up note removed (it was this change).

### Notes

- **Migration:** none — the new checks only add rejections (stricter); no valid committed SVG that passed before should contain `<foreignObject>` or remote/`javascript:` hrefs, and the safe local-fragment carve-out preserves the `xlink:href="#id"` pattern used in `<use>` elements.

## 0.150.0 — 2026-06-10

### Added

- **New skill: `declarative-visualization`** ([`skills/declarative-visualization/`](skills/declarative-visualization/SKILL.md)). Cross-surface Vega-Lite/Deneb/SVG spec-authoring for any visual agent. Ships: a 6-step authoring method (pick grammar → bind data → encode → wire interactivity → test null/empty → verify via render loop); a surface-agnostic `spec-patterns/` library of 6 starter templates (diverging bar, dumbbell, small-multiples facet, heatmap, sparkline strip, annotated line); a runnable stdlib-only `lint.py` security linter (no `data.url`, no remote `transform.lookup`, no custom `loader`, no remote `$schema`, no SVG `<script>`/`on*` — exit-coded for CI); and Gate 101 (bidirectional: clean fixtures pass, 6 security-vector fixtures fail, path traversal rejected, always-pass mutant lets a bad spec through = logic has teeth). Any PR adding/modifying a `spec-patterns/` template routes through `ravenclaude-core/security-reviewer` (load-bearing invariant).
- **New knowledge file: `knowledge/declarative-visualization.md`** — cross-surface canon: when to use Vega-Lite vs Vega vs Deneb vs SVG, grammar essentials, surface→delivery map (web/Power BI/Tableau/SVG-in-DAX), the full security model (Vega network-access vectors + SVG script-injection vectors), visual-feedback-loop integration, null/empty data handling, and a pre-publish checklist. Claim grounding markers on unverified Vega/Deneb specifics.
- **Cross-surface priors on 6 viz agents** — a `## Declarative visualization (Deneb / Vega-Lite / SVG)` section added to: `power-platform/power-bi-engineer` (Deneb + SVG-in-DAX), `data-platform/dashboard-builder` (vega-embed/react-vega/Evidence), `ravenclaude-core/frontend-coder` (vega-embed/react-vega + inline SVG), `tableau/tableau-viz-engineer` (extension iframe + SVG export), `web-design/frontend-implementer` (vega-embed/Evidence), `frontend-engineering/react-implementation-engineer` (react-vega). Each prior points to the neutral skill, states the Gate 101 security rule, and degrades gracefully (guidance even without a render tool).
- **Skill count** bumped `40 → 41` in `plugin.json` description and marketplace catalog.
- **Version** `0.149.4 → 0.150.0` in `.claude-plugin/plugin.json`, the `copilot/plugin.json` mirror, and the `marketplace.json` catalog entry (lockstep).

### Notes

- **Security is load-bearing:** Gate 101 must-fail half (a mutant template with `data.url` must exit 1) is the teeth assertion that makes the linter a real gate. Any PR adding a `spec-patterns/` template routes through `security-reviewer` — this is declared in the SKILL.md as an invariant, not a suggestion.
- **Migration:** none — additive skill, knowledge file, and agent priors; nothing in a consumer's installed plugin wiring changes on `/plugin marketplace update`.
- **Coordination caveat:** the queued `data-viz-designer` phases 2–7 (currently unrealized) will inherit this skill when they land. The plan specifies that `data-viz-designer` invokes `declarative-visualization` rather than re-implementing spec authoring.

## 0.149.4 — 2026-06-11

### Added

- **New always-on agent discipline: "Verify the load-bearing assumption before a high-impact activity"** ([`CLAUDE.md`](CLAUDE.md) § Capability Grounding Protocol). Before an activity whose impact is large or hard to reverse (delete / recreate / drop / migrate / force-overwrite / mass-edit / publish / prod change), the agent must name the single assumption the activity rests on and verify it — cheapest means first (authoritative doc, inspect the real artifact, or a reversible probe) — and prefer the smaller-blast-radius path that tests the premise before reaching for the irreversible one. Closes the costliest shape of the confident-reasoning error: a wrong premise driving an irreversible activity that "succeeds" mechanically while solving the wrong problem, where the cleanup dwarfs the task. Composes with "Read the error before you re-route" (verify a failure's *cause*) and "Check why a constraint exists" (verify a *constraint*); this verifies the *premise*. Distinct from `design_checkins` (which pauses for the human's judgment) — this is the agent checking its *own* belief. Grounded in a real 2026-06-11 case (a managed-solution import: 19 Dataverse entities deleted + recreated *twice* to "move them out of the Active layer," a non-goal the docs flag; the real fix was an in-place behavior flag, no delete). Adds a matching anti-pattern bullet.
- Version **0.149.3 → 0.149.4** in `.claude-plugin/plugin.json`, the `copilot/plugin.json` mirror, **and** the `marketplace.json` catalog entry (lockstep).

### Notes

- **Migration:** none — an additive behavioral discipline in the constitution (inherited by every agent + ported to Copilot CLI via the auto-loaded `CLAUDE.md`/`AGENTS.md`); nothing in a consumer's installed plugin wiring changes on `/plugin marketplace update`.

## 0.149.3 — 2026-06-10

### Added

- **New consumer-facing best-practice: "Checkpoints / `/rewind` are the recovery layer — they undo Claude's edits, not the world's side-effects"** ([`best-practices/checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md`](best-practices/checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md)). The repo shipped a thorough _prevention_ stack (runaway brake / dod-gate / task-scope / `guard-destructive` / tribunal / containment posture) and git-based recovery (`branch-archive`), but no rule on Claude Code's native _recovery layer_ — checkpoints + `/rewind` (Esc-Esc). The rule pairs the feature with its load-bearing boundary: a checkpoint reverts Claude's file edits + the conversation, but **not** `Bash` side-effects, network/external state, or DB writes — so it complements git commits + the destructive-action guards, never replaces them. Index bumped 16 → 17 rules. Surfaced by the 2026-06-10 Claude-subreddit scan ([`docs/research/2026-06-10-claude-subreddit-scan/README.md`](../../docs/research/2026-06-10-claude-subreddit-scan/README.md)); 1 of 4 findings approved, the rest denied/deferred as already-covered or out-of-core-scope.
- **Official-API data-access tooling** — `scripts/reddit-scan.py` (Reddit OAuth Data API) + `scripts/content-scan.py` (Brave Search discovery, open-web body fetch with a ToS-respecting `NEVER_FETCH` boundary + an http/https SSRF guard). Both stdlib-only, credentials via env vars.

### Notes

- **Migration:** none — additive markdown (a new best-practice + the index row) + repo-level scripts; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.
- **Version note:** re-versioned `0.149.0 → 0.149.3` on merge so it lands above the `0.149.2` lint-fix that took the catalog first.

## 0.149.2 — 2026-06-10

### Fixed

- **`skills/pbir-layout-engine/lint.py` couldn't find its PBIR reference when installed as a symlink into a consumer repo** (the `ravenclaude setup` default for GitHub Copilot CLI). `_repo_root()` locates the sibling-plugin reference `plugins/power-platform/knowledge/pbir-enhanced-reference.md` via `os.path.abspath(__file__)` four-dirs-up — but `abspath` does **not** follow symlinks, so under a symlinked install (`<consumer>/.claude/skills/pbir-layout-engine/` → the marketplace clone) it resolved to the consumer's parent dir (e.g. `/workspaces`) and `parse_visual_type_enum()` raised `EnumParseError` (exit 3), breaking `check-7` (PBIR `visualType` validation) for every Copilot-CLI consumer. **Fix:** a new `_reference_file_root()` resolves the reference via `os.path.realpath(__file__)` (follows the symlink back to the marketplace), with a `$RAVENCLAUDE_DIR` override for forks / the non-symlink `cp -r` install path, falling back to `_repo_root()` for the run-from-checkout (dev) case. **The `_resolve_safe()` input-path sandbox boundary is untouched** — it stays anchored to `_repo_root()` (the consumer's working tree), so no security boundary changes. Replaces the brittle per-repo `/workspaces/plugins → ~/RavenClaude/plugins` symlink workaround with a root-cause fix every consumer inherits. Verified end-to-end (resolves from both the checkout and a simulated symlink install); Gate 92 stays green.
- Version **0.149.1 → 0.149.2** in `.claude-plugin/plugin.json`, the `copilot/plugin.json` mirror, **and** the `marketplace.json` catalog entry (lockstep).

## 0.148.1 — 2026-06-10

### Added

- **`skills/webfetch-hardening/SKILL.md`** — a new "**When the fetch itself is blocked — the 403 / refusal route ladder**" section. Complements the existing return-envelope sanitizer (which hardens a body you *received*) with what to do when `WebFetch` returns `403 Forbidden` / "unable to fetch". Grounded in a live 2026-06-10 route-test: a 403 is **target-side bot-blocking, per-target, not a blanket egress block** (`raw.githubusercontent.com` fetched while `anthropic.com`/`github.blog`/`example.com` 403'd); `archive.org` is refused at the tool layer and `WebFetch` exposes no UA/header controls, so Wayback + UA-spoofing are unavailable. The ladder: **`WebSearch` (reads bot-blocked content) → domain MCP (Microsoft-Learn / GitHub) → a non-blocked host → secondaries last.** Surfaced by, and consumed by, the freshness-anchor docs in `claude-app-engineering` + `ai-coding-model-guidance`.
- Version **0.148.0 → 0.148.1** in `.claude-plugin/plugin.json` **and** the `marketplace.json` catalog entry (lockstep).

## 0.148.0 — 2026-06-10

### Fixed

- **`rc-deep-research` workflow crashed at startup under the current workflow runtime (`Date.now()` / `new Date()` forbidden).** The v0.140.0 eval-stats wiring added per-phase wall-clock timing (`_runStartedMs`, `_phaseWindows`, `duration_ms`, `run_window`, plus a per-op `latency` and an ISO `ts`) that calls `Date.now()` / `new Date()` **unconditionally** (top-level + per-`phase()`, not gated by `runId`). The workflow runtime forbids those APIs (they break in-session resume) and throws, so **every** `rc-deep-research` invocation failed at startup — surfaced when deepening the power-platform scout finds. Replaced the 10 call sites with a deterministic, resume-safe monotonic time source (`_now()` / `_isoNow()`) in **both** byte-identical copies (`.claude/workflows/rc-deep-research.js` + the bundled `skills/rc-deep-research/rc-deep-research.js` mirror). Gate 52 (dispatch-evaluator disabled-floor) stays green — the copied wrapper block is untouched.

### Notes

- **Known limitation (documented inline):** the eval-stats timing fields are now monotonic ORDINALS, not wall-clock ms. The adaptive-run-classifier **Phase 6** eval grader buckets real transcript `usage` by these per-phase windows, which now needs a separate runtime-legal time source (an agent-returned timestamp, or a base time passed via `args`). Phase 6 was already deferred; this is tracked as its follow-up. The **research output itself does not depend on timing**, so interactive runs are fully restored.
- **Migration:** none — the workflow lives in the marketplace repo's own `.claude/workflows/` (the bundled mirror changed but its behavior is a bug-fix-to-runnable); nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

## 0.147.0 — 2026-06-10

### Changed

- **`scout` now persists every run to disk — the full detail no longer dies in the chat transcript.** The skill's Step 5 (and Output Contract) gained an explicit two-tier storage step: (1) write the **full run report** — ranked shortlist with per-find reasoning, the *dropped-and-why* + ToS-flagged items, the per-lane/per-source detail, and the load-bearing finding(s) — to `docs/research/<YYYY-MM-DD>-scout-<slug>/report.md` (the same committed research-persistence home `rc-deep-research` uses; `docs/` commits straight to `main`, no PR); (2) append the **distilled keepers** as rows to `docs/idea-board.md`, the run-section header linking to the report. Both committed. Prior behavior only wrote the distilled idea-board rows, so the richer per-lane detail was lost to the transcript. Added a matching anti-pattern ("letting the run die in the chat transcript").

### Notes

- **Migration:** none — a skill-content change; the next `/scout` run writes the report + idea-board rows. Nothing in an installed plugin's wiring changes on `/plugin marketplace update`.
- Version note: 0.146.0 (the `monitors.json` path fix, PR #385) merged immediately before this; this change took 0.147.0 to avoid a version collision while both PRs were open.

## 0.146.0 — 2026-06-09

### Fixed

- **`monitors.json` load failure (`/doctor` ENOENT).** `plugin.json`'s `experimental.monitors` field pointed at `./monitors.json`, but the file ships at `./monitors/monitors.json` (inside the `monitors/` directory, beside `watch-run-state.sh`). Claude Code resolved the manifest path to a non-existent file and reported `monitors load failed … ENOENT` on every session start. Corrected the manifest path; aligned the `CLAUDE.md` milestone and [`knowledge/run-state-monitor.md`](knowledge/run-state-monitor.md), which both documented the same wrong path. No file move — the `monitors/` directory is the file's correct home.

### Notes

- **Migration:** none — a manifest path correction; the reactive run-state monitor now loads as intended on `/plugin marketplace update`. Consumers on a prior version simply stop seeing the `/doctor` load-failure line.

## 0.140.0 — 2026-06-09

### Added

- **Eval-harness wiring — the `rc-deep-research` workflow now honors the eval contract end-to-end.** Completes the deliberate follow-up the Agent-dispatch-evaluator Phase 2 milestone (0.121.0) carved out ("the eval-harness args-shape/runId/stats wiring … different regions"). Two halves land together: (1) the **harness side** — [`scripts/eval-adaptive-classifier.py`](../../scripts/eval-adaptive-classifier.py) gains the transcript-token acquisition path (`collect_metrics` reads per-agent `usage` from `~/.claude` transcripts post-hoc and buckets it into per-phase wall-clock windows, since a workflow script structurally cannot see per-agent token usage), the mismatch-1 `{question, runId}` invocation form, the mismatch-4 baseline knobs, and a second self-test sub-test that proves the transcript bucketing (verify_default cache-hit-rate = 0.75); (2) the **workflow side** — both `rc-deep-research.js` copies ([`.claude/workflows/`](../../.claude/workflows/rc-deep-research.js) + the bundled `skills/rc-deep-research/` mirror) accept a `{question, runId}` object as well as a plain string, fall back to `BASELINE_KNOBS` for the two vote knobs the run-config schema excludes, persist per-phase wall-clock windows + the grader's `stats` contract (`subagent_tokens`/`agent_count`/`duration_ms`/`confirmed_claim_count`/`run_window`/`per_phase`), and — when a `runId` is set — persist `structured-output.json` + `synthesis.md` under `.ravenclaude/runs/<runId>/` via the `rc-audit-emit` agent()-write pattern (with `_predispatch:"skip"` so the dispatch-evaluator leaves the infra writes alone).
- **Unblocks adaptive-run-classifier Phase 6.** The Phase-6 pre-build gate was "Phase 5 eval gate green," which was unrunnable because the harness↔workflow contract had never been wired (5 documented mismatches). With this wiring the eval can run; the `enabled:true` flip stays deferred pending a live eval run + the tier-framing re-confirm.

### Notes

- **Invariant preserved:** a plain-string `/rc-deep-research` call (legacy / interactive) is byte-identical to before — `runId` gates all eval-only behavior. Gate 52 (dispatch-evaluator disabled-floor, byte-identical) stays green; the copied wrapper block is untouched.
- **Migration:** none — the workflow lives in the marketplace repo's own `.claude/workflows/`; the bundled skills mirror changed but the string-arg path is unchanged, so nothing in a consumer's installed plugin behaves differently on `/plugin marketplace update`.

## 0.139.0 — 2026-06-09

### Added

- **New consumer-facing best-practice: [`best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md`](best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md)** (16th rule). Encodes the two most-repeated, independently-validated Claude Code community lessons — _"hooks are deterministic, `CLAUDE.md` is advisory; encode must-happen rules as hooks/CI, not prose"_ and _"an over-long `CLAUDE.md` gets half-ignored — prune it"_ — as a named rule the core agents surface to consumer-repo users (the `/init-agent-ready` audience). The repo already practiced this on its _authoring_ side (`AGENTS.md` house-rule #4, the hook+CI layout enforcement) but shipped no consumer-facing version. Sourced from a 2026-06-09 Claude-subreddit scan cross-checked against Anthropic's Claude Code best-practices docs; research + panel record in [`docs/research/2026-06-09-claude-subreddit-scan/README.md`](../../docs/research/2026-06-09-claude-subreddit-scan/README.md). Index count 15 → 16.

### Notes

- **Migration:** none — additive best-practice markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

## 0.138.0 — 2026-06-09

### Added

- **`spawn-team` honors the parallelism posture (behavioral enforcement).** The Pipeline page's `parallelism` control (toggle + max-workers + "unlimited", shipped in 0.137.0) gains its first consumer: [`skills/spawn-team/SKILL.md`](skills/spawn-team/SKILL.md) Step 5 now reads the `parallelism:` block from `.ravenclaude/comfort-posture.yaml` and caps how wide the Team Lead fans independent agents out — `enabled: false` → sequential, `max_workers: N` → batches of ≤N, `max_workers: unlimited` → uncapped. Behavioral commitment (like `design_checkins` / `decision_review`), not a hook-enforced gate; bounds *breadth* where the runaway brake bounds *depth*.

### Notes

- **Migration:** none — the `parallelism:` block defaults absent, and an absent block preserves the Team Lead's existing parallel-fan-out behavior, so nothing changes on `/plugin marketplace update` unless a consumer sets it.
## 0.126.0 — 2026-06-05

### Added

- **`scenarios/` bank (net-new).** The plugin shipped the `scenario-retrieval` skill but had no bank of its own. Added a domain-neutral **orchestration** scenarios bank — four dated, scope-tagged, unverified narratives that teach the plugin's own protocols, plus a [`scenarios/README.md`](scenarios/README.md) index:
  - `2026-06-05-keyword-routed-to-wrong-specialist` — route-before-spawning (traverse the routing tree, don't keyword-match; earliest-blocking gate wins).
  - `2026-06-05-subagent-tried-to-spawn-subagents` — orchestrator-worker hierarchy + recursion guard (escalate a handoff, don't dispatch peers).
  - `2026-06-05-blocked-report-skipped-alternate-methods` — Capability Grounding (read the error, enumerate alternatives, load the deferred/MCP route before reporting "can't").
  - `2026-06-05-decision-routed-to-tribunal-not-human` — decision-review envelope (route every yes/no, but high-blast + genuine-preference always `defer` to the human).
- **`CLAUDE.md` §"Value-add completeness (build-out 2026-06-05)"** — disposition table for every value-add menu item (scenarios BUILT; the runtime-tier items N-A or already-present for a foundation plugin that already ships hooks/scripts/a dashboard).

### Notes

- No existing hook, script, skill, rule, or agent was modified. The only changes are additive files (`scenarios/`, this CHANGELOG) plus a `CLAUDE.md` append and the version bump. `plugins/*/scenarios/**` was already an allowed glob in `.repo-layout.json`, so no layout-manifest change was needed.
- **Migration:** none — additive content; nothing in a consumer's installed plugin changes on `/plugin marketplace update`.

