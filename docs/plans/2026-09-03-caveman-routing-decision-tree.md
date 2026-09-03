# plan.md — caveman auto-routing (G6 synthesis, authoritative)

**Run:** `forge/caveman-routing-decision-tree` · **Depth:** `quick` · **Date:** 2026-09-03
**Inputs reconciled:** `scope.md`, `claims-table.md`, `plan-A.md` (architect lens, Opus),
`plan-B.md` (scanner lens, Sonnet), `gap-delta.md` (empty — plan-A did not exist when plan-B's author
looked; G6 performed the gap analysis instead).

This is the **only** artifact the orchestrator reads in full. It is self-contained: everything a Coder
agent needs to execute is in this file. Nothing below requires re-reading plan-A or plan-B.

> **G6 was the reconciliation step.** This is a `quick`-depth run, so no G4a critic / G4b tiebreak /
> G5 red-team gate ran. Where the two panels diverged, G6 made the call and states why. Where a panel
> asserted something G6 could verify cheaply, G6 verified it and cites the check.

---

## Goal

An always-on, RavenClaude-owned mechanism that reads the live session transcript's per-turn tool-call
density and drives the installed third-party `caveman` plugin's own per-session mode store to `off`
before a tool-heavy stretch accrues its measured net-negative cost — and back on for a prose-heavy
stretch — with zero manual toggling, an auditable per-decision record, and a single posture knob that
defaults to inert.

**Success signal (from `scope.md`):** a session that turns tool-heavy is caught mid-session (not
first-prompt-only) and caveman is disabled before the bulk of the loss accrues; a session that stays
prose-heavy keeps caveman on; every toggle is logged with when and why, so the mechanism's own
accuracy can later be measured as rigorously as the two baseline numbers were.

---

## Constraints

Each is a fact read from the repo or the installed plugin. `[G6-verified]` marks the ones G6 re-read
itself this session; the rest are carried from a panel with its cited source.

| # | Constraint | Source |
|---|---|---|
| C1 | **`chmod +x` is denied on this substrate.** A NEW file under `plugins/*/hooks/` is unshippable: CI hard-fails a non-executable `hooks/*.sh` and the tribunal denies the chmod. | `hooks/stream-prompt-attribute.sh:51-59` states it verbatim; `plugins/ravenclaude-core/CLAUDE.md` § v0.273.0 "Packaging exception". **Both panels found this independently.** |
| C2 | Three sanctioned escapes exist for new hook logic: **(a)** a delimited block inside an already-executable hook; **(b)** a body in `plugins/*/scripts/` registered as `bash ${CLAUDE_PLUGIN_ROOT}/scripts/x.sh`; **(c)** a bare `.py` engine under `scripts/` invoked from *inside* an already-registered `.sh` wrapper. | `[G6-verified]` (b) is used in `hooks/hooks.json:121,125,198,241` (`preflight-command-review.sh`, `guard-remediation-cause.sh`, `guard-cause-closure.sh`, `ask-on-ambiguity.sh`). (c) is pervasive: `compact-anchor.sh:28`, `capability-orientation.sh:36`, `handoff-nudge.sh:14`, `precompact-digest.sh:96`, `route-decision-review.sh:123`, `agent-dispatch-evaluator.sh:100`. |
| C3 | Every new hook **registration** needs two entries: `hooks/hooks.json` (`${CLAUDE_PLUGIN_ROOT}`) and the dev-mirror `.claude/settings.json` (`${CLAUDE_PROJECT_DIR}`). | root `CLAUDE.md` § "Marketplace-dev hooks". |
| C4 | A new hook entry must also be dispositioned in **three projectors** — `scripts/generate-{copilot,cursor,gemini}-hooks.py` — each keyed by script **basename** via a `_SKIP` dict. Copilot's carries a `stale = set(_SKIP) - canonical` check. | `generate-cursor-hooks.py:70,168`; `generate-gemini-hooks.py:69,200`; `generate-copilot-hooks.py:113,159,257`. |
| C5 | `transcript_path` is a common input field on every hook event. `session_id` is on every payload; `source` is on `SessionStart`. | `docs/plans/2026-08-08-premise-gate/plan.md:8`; host-verified by P0.4 below. |
| C6 | Claude Code writes **one JSONL line per content block**; summing every line inflates tokens 1.5–2.1×. Dedupe on `(requestId, message.id)`. | `caveman-stats.js:174-190` (their own measured comment). |
| C7 | Posture reads use a `sed`/`grep` scalar idiom, **never PyYAML**. | `worktree-guard.sh:227-239`; `stream-prompt-attribute.sh:84`; `runaway-brake.sh:47`. |
| C8 | Anything reaching the model's context or a log must be **derived values only** — fixed strings, enums, validated integers. | Gate 19 / `capability-orientation.sh` / `compact-anchor.sh` invariant. |
| C9 | **stderr at exit 0 is measured UNDELIVERED to the model.** Advisory text goes through `_advise.sh`'s `additionalContext`; `_advise.sh` also takes a `silent` arg (added 2026-09-02) to deliver to the model without spamming the terminal. | `hooks/_advise.sh:4-27`. |
| C10 | bash 3.2-safe; no `declare -A`, `mapfile`, `${x^^}`, `shopt -s globstar`; no GNU `timeout` / `grep -P` / `sed -i`. Use `_rc_timeout` from `hooks/_portable.sh`. | `CLAUDE.md` macOS doors 1-4 (v0.193.0–v0.196.0). |
| C11 | Caveman is a **black box**. Its upstream repo is out of scope. Integration is via its documented public surface only; nothing under its cache is written or patched. | `scope.md` § "Explicit out of scope". |
| C12 | Latency, not tokens, is this hook's real cost. A per-turn hook emits **zero** tokens unless it deliberately writes `additionalContext`. The design must stay silent on the steady state. | `_advise.sh` header; `stream-prompt-attribute.sh:61-65`. |
| C13 | **Next free gate slot is 264** — `[G6-verified]`: max `Gate N` header in `scripts/audit-gates.sh` on this worktree is **263**. Re-census against a **freshly-merged `origin/main`** before authoring, because FORGE Phase 0 consumed 261–263 and a stale base is how 261 was once double-allocated. | `audit-gates.sh`; `CLAUDE.md` § v0.316.1. |
| C14 | Hook-process **direct filesystem writes** (bash `>`, Python `open()`) never pass through the agent's `Write`/`Edit` tool and are therefore never subject to `worktree-guard.sh`'s PreToolUse lease. Every state write in this plan MUST stay a direct hook-process write. | plan-B Finding 3, from `worktree-guard.sh` + `runaway-brake.sh`. **Code-review redline** — routing any of these through the `Write` tool re-imports lease contention for zero benefit. |
| C15 | `plugins/*/scripts/**`, `plugins/*/hooks/**`, `plugins/*/hooks/tests/**`, `plugins/*/knowledge/**` are already in `.repo-layout.json` `allowed_globs`. **No layout edit is needed.** | plan-A, verified this session. Re-confirm with the AGENTS.md layout snippet before push. |

---

## Current State

### What caveman actually exposes — `[G6-verified]` by direct read this session

Install: `/Users/matthewcorbett/.claude/plugins/cache/caveman/caveman/3b74643f4d91/` — **one** cache
directory, name is a **content hash, not a semver** (`ls` this session). Plugin-installed as
`caveman@caveman` in `~/.claude/settings.json`; it is **not** registered in this repo's
`.claude/settings.json`.

- **Mode store:** `$CLAUDE_CONFIG_DIR/.caveman-sessions/<session_id>.mode` (default `~/.claude` when
  `CLAUDE_CONFIG_DIR` is unset — unset on this host, files present under `~/.claude`), plus a
  machine-wide legacy mirror `$CLAUDE_CONFIG_DIR/.caveman-active`.
- **Single writer — `writeSessionMode(claudeDir, sessionId, modeOrNull)`, `caveman-config.js:487-500`.**
  `[G6-verified]` verbatim body:

  ```js
  function writeSessionMode(claudeDir, sessionId, modeOrNull) {
    const canonical = (!modeOrNull || modeOrNull === 'off') ? 'off' : modeOrNull;
    if (!VALID_MODES.includes(canonical)) return;
    const sessionPath = sessionActivePath(claudeDir, sessionId);
    if (sessionPath) safeWriteFlag(sessionPath, canonical);
    const legacy = legacyFlagPath(claudeDir);
    if (canonical === 'off') { try { fs.unlinkSync(legacy); } catch (e) {} }
    else { safeWriteFlag(legacy, canonical); }
  }
  ```

- **Guards inherited for free by calling it:** `validateSessionId` (`:412-415`, whitelist
  `^[A-Za-z0-9_-]{1,128}$` — the path-traversal defence), `safeWriteFlag` (`:168` — symlink-refusing,
  `O_NOFOLLOW`, atomic temp+rename, `0600`), `sessionStatePath`'s redundant containment check
  (`:429-436`), `VALID_MODES` membership.
- **Readers `[G6-verified]`:** `resolveActiveMode(claudeDir, sessionId)` (`:455-461`) reads the
  per-session file first and **falls back to the legacy mirror only when the per-session file has no
  stored value**. `readSessionModeRaw` (`:470-474`) returns this session's literal value with **no**
  legacy fallback — exactly what a snapshot-before-overwrite needs.
- **Exports `[G6-verified]`** at `:628-636` include `resolveActiveMode, readSessionModeRaw,
  writeSessionMode`.
- **Reset semantics:** `caveman-activate.js` re-derives `getDefaultMode()` only on
  `RESET_SOURCES = {startup, clear}`; `compact`/`resume`/`fork` read the stored mode (claim 6).
- **Per-turn reinforcement:** `caveman-mode-tracker.js` responsibility 3 emits a `hookSpecificOutput`
  reminder every turn while the mode is non-independent.
- **Fail-safe read property:** the reader is symlink-refused, size-capped at 64 bytes
  (`MAX_FLAG_BYTES`), and **any value not in `VALID_MODES` is silently treated as absent**. So the
  worst case of any contract drift is *"our toggle silently stops working"* — never a crash, never
  corruption.

### Transcript block shape — observed, not assumed

plan-A parsed the newest transcript under `~/.claude/projects/`:

```
distinct responses: 2   tool_use: 2   text: 0   out_tokens: 22   cache_read: 73866
block types: {'thinking': 1, 'tool_use': 2}
```

**Observation:** the discriminating signal is present and cheap — count `tool_use` vs `text` blocks in
`message.content[]` per assistant response. **Inference:** that the ratio tracks the economics — this
is claims-table **row 3**, the load-bearing inference, and is what P5's offline replay tests.

### RavenClaude surfaces this plugs into

- `hooks/hooks.json` — `UserPromptSubmit` has 2 entries (both `timeout: 10`); `SessionStart` has a
  `startup|resume|clear|fork` group of 7 and a separate `compact` entry.
- `hooks/_emit-event.sh:122-140` — `_emit_hook_event <hook> <verdict> <tool> <path> <rule> <exit>`;
  scrubs `rule` **and** `path` at the substrate.
- `hooks/_advise.sh` — `rc_advise_init <Event> [forced_exit] [silent]`.
- `hooks/_portable.sh` — `_rc_timeout` shim (stock macOS has no GNU `timeout`).
- `node` present at `/Users/matthewcorbett/.local/bin/node`, v26.5.0.

---

## Proposed Design

Three components, one seam, one knob. Registered via the C2-(b) escape.

```
UserPromptSubmit ─┐
                  ├─► bash ${CLAUDE_PLUGIN_ROOT}/scripts/caveman-route-hook.sh --event {prompt|session}
SessionStart ─────┘        │
 (startup|resume|          │  1. posture short-circuit: [ -f ] + one anchored grep  ── absent/off → exit 0
  clear|fork)              │  2. python3 scripts/caveman-route.py   ── PURE. incremental transcript
                           │       tail from a byte cursor → {verdict, why, metrics}
                           │  3. if verdict != current AND posture == live AND no manual_override:
                           │       bash scripts/caveman-apply-mode.sh <sid> <mode>
                           │         └─ node -e: RUNTIME-RESOLVE caveman-config.js (glob, newest mtime)
                           │                     → snapshot → writeSessionMode(...) → READ-BACK verify
                           │  4. _emit_hook_event  (derived labels only) + route log line
                           └─ always exit 0
```

**The seam is caveman's own `writeSessionMode`, resolved fresh at runtime.** See the A-vs-B verdict
below for why.

**The policy is asymmetric, deliberately.** Enabling caveman is the risky direction (it can cost
tokens and, in principle, fidelity); disabling it is the safe direction (it costs at most the ~26.5%
we might have saved). **Enable slowly, disable instantly** — mirroring the routing asymmetry already
ruled load-bearing in `skills/cheap-lane-delegation`.

**Default is inert.** The knob is `caveman_routing: off | shadow | live` in
`.ravenclaude/comfort-posture.yaml`, absent ⇒ `off`. This deliberately reuses
`decision_review: off | advisory | binding`'s established three-tier vocabulary (never mutate without
either being fully off, or having a human-legible dry-run first). For a non-adopter the hook is one
`test -f` plus one `grep` — the same zero-cost floor `stream-prompt-attribute.sh:84` and
`route-decision-review.sh` already set.

### Classifier contract (`caveman-route.py`)

Pure function, stdlib only, no writes, `--self-test`.

- **Input (stdin JSON):** `{transcript_path, session_id, cursor_byte, prior_verdict, streak}`
- **Output (stdout JSON):** `{verdict: "on"|"off"|"hold", mode, why, metrics, cursor_byte, streak}`
- **Window:** trailing `W` deduped assistant responses. Per response, from `message.content[]`:
  `tool_use_blocks`, `text_blocks`, `text_chars`, plus `usage.output_tokens`, deduped on
  `(requestId, message.id)` per C6.
- **Cost bound:** incremental byte cursor persisted in
  `.ravenclaude/runs/<session>/caveman-route-state.json`; each turn reads only `[cursor, EOF)` with a
  4 MiB tail cap (the bound `context-usage-meter.py` already uses). Bootstrap seeks to
  `max(0, size − 512 KiB)`; the bootstrap verdict is `off` regardless, so a full first read buys
  nothing.

### ⚠ Thresholds — every number below is `[unverified]`

Both panels proposed numbers. **None is measured.** They are inputs to P5, not conclusions from it.
Writing them as settled defaults would be exactly the confident-inference error this pipeline's G1
discipline exists to prevent.

| Parameter | Merged provisional value | Status | Cheapest step that settles it |
|---|---|---|---|
| `W` — classification window (responses) | **6** | `[unverified — n=1; plan-A's proposal, no measurement behind the 6]` | **P5 offline replay** (see below) |
| → `off` trigger | any of the last **2** responses has `tool_use_blocks ≥ 2`, **or** window `tool_uses/response ≥ 1.0` | `[unverified — n=1; derived from claim 1's single 14-turn session]` | P5 offline replay |
| → `on` trigger | **4 consecutive** responses with `tool_use_blocks == 0` **and** `text_chars > 0` | `[unverified — n=1; claim 2 measured isolated prose prompts, not a streak length]` | P5 offline replay |
| Cadence `N` (plan-B's every-Nth-turn) | **rejected — cadence is per-turn**, see Q1 | n/a | n/a |
| Hysteresis `M` (plan-B's clean-window count) | folded into the 4-consecutive-response `on` streak | `[unverified — same basis]` | P5 offline replay |
| Latency budget `RC_CAVEMAN_ROUTE_BUDGET_S` | **3s** | `[unverified — an engineering guess, not a measurement]` | P3/P5 record the actual per-turn wall time in the route log; replace the guess with the measured p95 |
| plan-A's "≈17 h of build" | carried below | `[unverified — an estimate, not a measurement]` | n/a — do not treat as a commitment |
| plan-A's "one turn of lag ≈ 7% of the loss" | carried below as R1 | `[unverified — arithmetic on the single n=1 session]` | P5 replay reports the real per-turn distribution |

**The cheapest settling step — and it is cheaper than either panel proposed.** plan-A gated P7 on ≥10
**live** shadow sessions (wall-clock weeks); plan-B on ≥5. G6 adds a step that costs **zero API
dollars and zero wall-clock**: **replay the classifier offline over the transcripts that already exist
under `~/.claude/projects/`**, and correlate each replayed verdict trace against `caveman-stats.js`
run on that same transcript. The corpus is already on disk. This is the second data point `scope.md`
says is missing, obtainable now. Live shadow (P7's entry gate) then confirms the offline calibration
under real conditions rather than discovering it there.

---

## The A-vs-B verdict: how the mode file gets written

**This was the only substantive divergence between the panels, and G6 resolves it here.**

### What each panel proposed

- **plan-A:** call caveman's own `writeSessionMode` through `node -e`, resolving
  `caveman-config.js` **at runtime by glob** (`.../caveman/caveman/*/src/hooks/caveman-config.js`,
  newest mtime, with a standalone-install fallback), then `typeof` check before calling. Inherits
  `validateSessionId`, `safeWriteFlag`, `VALID_MODES`, mirror handling.
- **plan-B:** build a RavenClaude-owned hardened writer replicating the file contract
  (same session-id regex, symlink refusal, atomic temp+rename), never resolving caveman's install path
  at runtime at all.

### ✅ Verdict: **plan-A's seam — call caveman's own `writeSessionMode`, resolved fresh at runtime.**

**Reason 1 — the premise of plan-B's objection is not what plan-A proposed.** plan-B's Finding 2
argues against "`require()`-ing `caveman-config.js`… means globbing that hash path on every hook
invocation — fragile, and it re-derives on every caveman release." But **plan-A never hardcodes the
hash** (plan-A lines 218-222): it globs `*/` and picks newest mtime, which is precisely the
"detect the install path fresh at runtime rather than hardcoding" third option. The two panels wrote
their plans without seeing each other's, and plan-B's rebuttal lands on a version of (b) that plan-A
did not propose. **The conflict is narrower than it looked.**

**Reason 2 — plan-B's claimed blast-radius advantage does not exist.** plan-B's case is that its
writer degrades to "our write is silently ignored" on contract drift. But `[G6-verified]`
plan-A's route degrades to *the same outcome*: if the glob resolves nothing, or
`typeof cfg.writeSessionMode !== 'function'`, the applier exits 0 as a no-op and emits a warn. Both
designs fail to "the toggle silently stops working." Since the failure modes are equivalent, the
tiebreak goes to whichever design has **less code that can be wrong**, and that is the one that does
not reimplement a path-traversal whitelist, a symlink-refusing atomic writer, and a mixed-version
mirror protocol.

**Reason 3 — the mirror protocol is genuinely subtle, and reimplementing it is a live drift hazard.**
`[G6-verified]` caveman's own source comment at `caveman-config.js:480-486` explains that the legacy
mirror **must never hold the literal `off`**, because an older `caveman-mode-tracker.js` reading it
would clear its `!INDEPENDENT_MODES` check and inject `"CAVEMAN MODE ACTIVE (off)"`, and an older
`caveman-statusline.sh` would render `[CAVEMAN:OFF]`. That is a non-obvious, cross-version behavioural
rule encoded in eight lines of their writer. plan-B's design explicitly *never touches the mirror at
all* — which sidesteps that rule but produces a different, also-wrong state (see the new risk R10
below). Caveman's maintainers document the hazard themselves: their two statusline scripts
re-implement path resolution by hand and are held together only by a grep for drift. **We do not
become a third such copy.**

**Reason 4 — the version-bump objection is answerable, and answered.** The cache directory is
content-hash-keyed (`3b74643f4d91`, `[G6-verified]` — one directory, hash name, no semver to pin
against), so a caveman update **does** move the path. Runtime glob resolution plus a `typeof` check
survives that by construction; a hardcoded path would not; plan-B's contract-replication survives it
too but by *not looking*, which is why it cannot detect a contract change. Runtime resolution keeps
the reuse **and** keeps a detection surface.

### What plan-B contributed that is adopted verbatim into the merged design

The verdict goes to plan-A's seam, but **four of plan-B's findings are strictly better and are
merged in**. This is not a consolation prize; the plan is worse without them.

1. **Read-back verification after every write (plan-B P3).** Immediately after `writeSessionMode`,
   re-read via the **same resolved module's** `resolveActiveMode`/`readSessionModeRaw` and confirm it
   decodes to the intended mode. On mismatch, emit a `warn`-tier hook event. This converts *"silently
   stops working"* — the shared worst case of both designs — into a **detected** condition. It is
   nearly free under plan-A's seam because the module is already loaded in the same `node -e`.
2. **The fail-safe read property is a documented, load-bearing bound**, not a footnote: any value not
   in `VALID_MODES` is treated as absent, so contract drift can never crash or corrupt caveman.
3. **Never write `.caveman-active` ourselves** — and the newly-surfaced consequence that we *do*
   unlink it via caveman's own writer (R10 below).
4. **`worktree-guard` non-issue by construction** (C14) and the code-review redline that keeps it so.

### What is explicitly rejected

- **plan-B's own hardened writer** — rejected. It buys no blast-radius advantage (Reason 2) and costs
  a permanent obligation to track a third party's file format, including the mirror rule at
  `caveman-config.js:480-486` that it would have to either replicate or knowingly violate.
- **Vendoring/forking a mode-writer (`scope.md` option c)** — rejected, same reasoning, plus it drops
  the `node` dependency that caveman itself already requires (so a consumer with caveman installed
  necessarily has `node`).

---

## Alternatives considered and rejected

Every `scope.md` open question, decided, with the runner-up named and why it lost.

### Q1 — Classification cadence → **per `UserPromptSubmit`, incremental cursor**

| Option | Verdict | Trade-off |
|---|---|---|
| **Every `UserPromptSubmit`, incremental byte cursor** | ✅ **chosen** (plan-A) | Catches the pivot within one turn; costs one subprocess of latency and **zero tokens** while holding. |
| Every N turns, N=3 (plan-B's pick) | 🥈 runner-up | ~⅓ the subprocess cost, but a 3-turn lag on a 14-turn session leaves ~21% of it at the wrong setting — it under-serves the exact case claim 1 measured. |
| `SessionStart` only | ❌ | Directly falsified by `scope.md`: it would have held caveman on through the entire −5,204-token session. |
| `PostToolUse` counter | ❌ | Fires once per tool call — far more often than per-turn — inverting the cost it exists to save. |

**Why the runner-up lost.** plan-B's cadence argument is that a per-turn hook "reproduces caveman's
own fixed-overhead problem." That is the right instinct pointed at the wrong cost: caveman's overhead
is **tokens injected into context** (~1,250/turn, claim 1); this hook's overhead is **subprocess
latency and zero tokens** (C12). They are not the same currency. Meanwhile the entire justification
for building this is a mid-session pivot the first-prompt classifier misses; accepting a 3-turn lag
re-imports a smaller version of that same defect. **If per-turn latency later measures as material,
the fix is to make the classifier cheaper (it is already a bounded incremental tail read), not to make
it blinder.** plan-B's O(1)-floor discipline is nonetheless adopted as a design rule: the posture
short-circuit runs *before* anything else, so a non-adopter pays two greps and nothing more.

### Q2 — Classification signal → **live transcript tool-call density over a trailing window**

Both panels chose this independently. Runner-up: **prompt-text + transcript combined** — the keyword
half would give a turn-1 prior the transcript cannot, but turn-1's correct answer is already `off`, so
the prior buys nothing at its only unique moment. Rejected outright: **prompt-text keywords alone** —
`scope.md` states the pivot is density "**not task topic**," and a keyword classifier is a topic
classifier wearing a costume; plan-B further notes caveman's own source records two real
false-positive incidents from this exact technique (#598, #838 — quoted trigger phrases).

*Kept as a named, deferred extension:* if P5 shows the 4-response enable streak is too slow in
practice, a prompt-shape prior is the first thing to add. It is additive to this design, not a
rewrite of it.

### Q3 — Integration mechanism → **(b), via caveman's own `writeSessionMode`, runtime-resolved**

Decided above. Runner-up: plan-B's contract-replicating writer. Rejected outright:

**⛔ Option (a) — natural-language trigger phrases — is structurally dead, not a trade-off.**
**Both panels found this independently, from the same line.** `caveman-mode-tracker.js:126,135` reads
`data.prompt` from **its own stdin payload**. A sibling `UserPromptSubmit` hook's `additionalContext`
is added to the *model's* context; it does not mutate the payload delivered to other hook processes.
plan-B adds the strongest corroborating evidence: `hooks/_advise.sh`'s own header documents a
matched-trial bake-off finding that two `additionalContext` emitters on the same event
**CONCATENATE — they do not chain or override one another's input.** So the only way (a) fires is if
a human literally types "stop caveman", which is the manual toggle this engagement exists to remove.

`[observation: the data.prompt read at caveman-mode-tracker.js:135, and the _advise.sh concatenation
finding.]` `[inference: that additionalContext never reaches a sibling hook's payload — falsifiable in
one probe. **P0.1 runs it.** If it comes back the other way, (a) becomes viable and Q3 is re-decided
before P2.]`

### Q4 — Threshold tuning → **conservative default (favour `off`) + asymmetric hysteresis + a mandatory shadow phase before any write**

| Option | Verdict | Trade-off |
|---|---|---|
| **Conservative-off + hysteresis + shadow, calibrated by offline replay first** | ✅ chosen (both panels converged; G6 adds the offline-replay step) | Bounds the worst case at "we forgo some of the 26.5%", and produces the missing second data point from transcripts already on disk at zero API cost. |
| One more instrumented A/B before picking numbers | 🥈 runner-up | Cleaner numbers, but it spends real API dollars to answer a question offline replay answers for free — and an A/B measures *isolated prompts*, while what needs calibrating is a *classifier over live mixed sessions*. **Not cancelled — sequenced after the cheaper evidence.** |
| A fitted numeric density ratio picked now | ❌ | Curve-fitting from n=1 is the false precision this repo's own conventions reject (`agent-routing-matrix` milestone: *"no numeric confidence field… an ungrounded heuristic cannot bear it"*). |
| Pick a number now and ship live | ❌ | The whole point of `scope.md` Q4 is that n=1 does not support a threshold. |

### Rejected structural alternative — plan-B's zero-new-registrations wiring

plan-B proposed adding the routing call **inside** two already-registered hooks
(`stream-prompt-attribute.sh` and `capability-orientation.sh`), giving zero new `hooks.json` /
`settings.json` entries and zero projector `_SKIP` edits. `[G6-verified]` — the pattern is real and
pervasive (`compact-anchor.sh:28`, `capability-orientation.sh:36`, `handoff-nudge.sh:14`,
`precompact-digest.sh:96`, `route-decision-review.sh:123`), and the saving is genuine.

**Rejected anyway**, on two grounds. (1) `stream-prompt-attribute.sh` already carries a second,
unrelated concern (the conserve-tokens delimited block) and documents that fact as an exception, not a
pattern; a third concern makes that file the thing it is explicitly trying not to become, and the cost
is paid forever by whoever next reads it. (2) `scope.md`'s success signal requires the toggle to be
**auditable**; burying caveman routing inside two hooks whose names say nothing about caveman makes
the mechanism invisible to exactly the person auditing it. The registration cost is paid **once** and
is gate-checked (P6 verifies all three projector `_SKIP` entries and the copilot `stale` check); the
concern-mixing cost is paid on every future read. **We take the C2-(b) escape** —
`bash ${CLAUDE_PLUGIN_ROOT}/scripts/caveman-route-hook.sh`, matching `ask-on-ambiguity.sh`'s
registration exactly, which is itself an opt-in, advisory, fail-open `UserPromptSubmit` hook —
structurally the same shape as this one.

---

## G3b consistency check

**G3b's deterministic verdict:** `premise-gate: CLEAN — 7 claims, 16 phases, no unsettled inference is
load-bearing.`

**G6 confirms the verdict is consistent with what is synthesized here**, with one correction applied
rather than silently dropped.

- Claims 1, 2, 4, 5, 6, 7 are WARN-tier **observations**, all reproduced in-session. Nothing in this
  plan asserts them beyond what was observed. Claims 4, 5 and 6 were additionally re-read by G6 this
  session (`writeSessionMode`, `resolveActiveMode`, `readSessionModeRaw`, exports, `VALID_MODES`).
- **Claim row 3 — "the economic pivot is prose-density vs tool-call-density, and a session's shape can
  change mid-conversation" — is an inference, and it is the load-bearing one.** It is settled at G3b
  as *disconfirmable cheaply* and is carried, not laundered: it is cited on every phase whose
  correctness depends on it, and P5's offline replay is the disconfirming probe.

**Correction applied — three phases implicitly depended on row 3 without citing it.** Rather than drop
the gap, G6 adds the citations:

| Phase | Panel's `depends_on_claims` | Merged | Why row 3 was added |
|---|---|---|---|
| **P4 — SessionStart re-arm** | plan-A: `[6]` | **`[3, 6]`** | Preserving cursor+streak across `resume`/`fork` only *matters* because the session's shape changes mid-conversation. If row 3 were false, state preservation would be pointless and the phase would have no content. |
| **P5 — Observability + replay** | plan-A: `[7]` | **`[3, 7]`** | The route log exists to record **transitions**. A transition is only a meaningful event under row 3. P5 is also the phase that *tests* row 3, so the citation is doubly required. |
| **P1 — knob schema half** (plan-B P1) | plan-B: `[]` | folded into **P1 `[1, 3]`** | `caveman_routing_window` and hysteresis parameters are only meaningful quantities if shape changes mid-session. plan-B carried them at `[]`. |

No phase in the merged plan now rests on row 3 without citing it. **The G3b verdict stands.**

---

## Execution plan

Eight phases, P0–P7. Every phase carries `depends_on_claims`, `reversibility`, an acceptance test with
teeth, and a pre-build gate. Owner is the specialist the Team Lead should dispatch; the architect does
not spawn them.

The merged phase set reconciles plan-A's P0–P7 with plan-B's P0–P7: plan-B's P1 (knob schema) folds
into P1; plan-B's P2 (counter + reset) folds into P4; plan-B's P3 (writer) folds into P2; plan-B's P4
(wiring) splits across P3 (shadow) and P7 (live flip); plan-B's P5 (shadow validation) becomes P7's
entry gate, preceded by P5's cheaper offline replay.

---

### P0 — Pre-build probes (no product code)

`depends_on_claims: []` · `reversibility: two-way-door`
**Owner: backend-coder** — probe scripts only, all output under
`.ravenclaude/runs/forge/caveman-routing-decision-tree/p0/`

Five probes, **each with a positive control**, because this repo's own record is that a probe failing
toward "clean" is the dominant defect class.

| Probe | Question | Positive control |
|---|---|---|
| **P0.1** | Does a sibling `UserPromptSubmit` hook's `additionalContext` mutate `.prompt` in another hook's payload? *(settles Q3-(a); merges plan-A P0.1 + plan-B P0a)* | A throwaway dumper hook must first show the **unmodified** prompt text it was given — proving the dumper works before its silence means anything. |
| **P0.2** | Does `node -e` `require()` of the runtime-globbed `caveman-config.js` succeed, and are `writeSessionMode`, `readSessionModeRaw` **and** `resolveActiveMode` all functions? | Assert `typeof cfg.getDefaultMode === 'function'` too — a module that loads but exports nothing would otherwise read as "absent". |
| **P0.3** | Does `writeSessionMode(dir, sid, 'off')` produce a session file containing literal `off` **and** unlink the legacy mirror — and **does `resolveActiveMode` read it back as intended**? | Write `'lite'` first and assert the mirror **exists**; then `'off'` and assert it is **gone**. Both directions or the assertion is vacuous. **Additionally record the mirror's pre-existing state and whether any other `.caveman-sessions/*.mode` file exists on this host — this is R10's measurement.** |
| **P0.4** | Are `transcript_path`, `session_id` (and on `SessionStart`, `source`) actually present on real payloads **on this host**? *(C5 is docs-verified; this is host-verified. Merges plan-A P0.4 + plan-B's P2 pre-build gate.)* | Dump the **full payload key set**, not just the fields of interest. |
| **P0.5** | **(G6 addition)** How many transcripts exist under `~/.claude/projects/`, and can `caveman-stats.js` be run against an arbitrary one non-interactively? *(This is what makes P5's offline replay cheap; if the corpus is thin or the stats runner needs a live session, P5's design changes.)* | Run `caveman-stats.js` against a transcript **known** to be tool-heavy and confirm it returns a non-trivial number — a runner that returns 0 for everything would otherwise read as "corpus is clean". |

**Acceptance:** five probe transcripts, each recording the exact command, verbatim output, and its
control. **A probe that could not run records `indeterminate`, never `negative`** (`log-probe.sh`'s
taxonomy; per the cause taxonomy, class **I** and class **H** are not interchangeable).

**⚠ Pre-build gate on the whole plan:** if **P0.1** comes back showing `additionalContext` *does* reach
a sibling hook's payload, **stop and re-decide Q3 with the architect before P2.** That is the one
result that invalidates the chosen seam. If **P0.5** comes back thin, escalate to the Team Lead — P7's
entry criterion falls back to plan-A's ≥10 live shadow sessions.

---

### P1 — Classifier + knob schema (`plugins/ravenclaude-core/scripts/caveman-route.py`)

`depends_on_claims: [1, 3]` · `reversibility: two-way-door` — a pure function with no side effects;
deleting the file removes it entirely.
**Owner: backend-coder**

- Stdlib only; `from __future__ import annotations` (stock macOS Python 3.9 — the v0.213.0 RT-5
  lesson).
- Reads the transcript tail from `cursor_byte`, 4 MiB cap. A torn/partial last line is dropped
  silently, never raised (`_read_mimir`'s per-line discipline).
- **Dedupe on `(requestId, message.id)`** — C6. Entries with no `message.id` keep per-line counting,
  matching caveman's own fallback.
- Emits **no** raw prompt, tool input, or tool result — only counts (C8; the Gate 110 no-egress shape,
  applied here by construction).
- **Knob schema settled here** so P2/P3/P4 are not guessing at names:
  `caveman_routing: off | shadow | live` (absent ⇒ `off`), `caveman_routing_window: N` (default 6),
  `caveman_routing_enable_streak: M` (default 4). Read with the C7 anchored-grep idiom, e.g.
  `grep -Eq '^[[:space:]]*caveman_routing:[[:space:]]*(shadow|live)[[:space:]]*$'` — **never PyYAML**.
  All three defaults carry the `[unverified]` marker from the thresholds table into the code comments.

**Acceptance test:** `python3 plugins/ravenclaude-core/scripts/caveman-route.py --self-test` exits 0
with an `N/N` pass line **computed, never a hardcoded literal** (the Gate 260 lesson). ≥8 fixtures,
including: the 14-turn tool-heavy shape → `off`; a 6-response prose-only shape → `on`; a **mid-window
pivot** (prose then tools) → `off` within 1 response of the pivot; a torn final line → no crash; an
empty transcript → `hold`; **and a must-fail mutant** that removes the dedupe and shows the density
metric changes — proving the dedupe is load-bearing, not decoration.

**Pre-build gate:** P0.4 confirms `transcript_path` on this host.

---

### P2 — Applier (`plugins/ravenclaude-core/scripts/caveman-apply-mode.sh`)

`depends_on_claims: [4, 5]` · `reversibility:` **⛔ one-way-door — authored here, armed at P7**
**Owner: backend-coder** · **Reviewer: security-reviewer (mandatory, blocks P7 not P3)**

**Reconciling the two panels' reversibility calls.** plan-A classed the applier (its P2) as the
one-way door; plan-B classed the wiring that calls it (its P4). **Both are half right, and the honest
statement is the union:** the applier *existing* is fully reversible (nothing calls it); the
irreversible event is the **first automatic write against a live session**, which under this plan does
not occur until P7 flips `live`. So: the door is **built at P2, opened at P7**. The three mandatory
rollback components below are built at P2 precisely so the door **cannot** be opened without them.

**Why it is a one-way door at all.** Every *individual* write is reversible, but the first automatic
write **destroys the user's own manually-set caveman mode with no record of what it was**. That is
irreversible at the data level and invisible — the exact silent-toward-clean shape this repo keeps
recording.

**Mandatory rollback / kill-switch — all three required, none optional:**

1. **Snapshot before the first write of a session.** Call `readSessionModeRaw` (`:470` — literal
   value, no legacy fallback, exactly what a snapshot needs) **and** stat the legacy mirror
   `.caveman-active`, persisting both to
   `.ravenclaude/runs/<session>/caveman-route-state.json` as `user_mode_at_entry` and
   `legacy_mirror_at_entry` **before** any `writeSessionMode`. **If the snapshot fails, do not
   write** — abort the apply and emit a warn. *(The mirror half of the snapshot is G6's addition, for
   R10.)*
2. **Manual-override latch.** If `user_mode_at_entry` is a non-default value **or** the user typed a
   `/caveman …` command this session, set `manual_override: true` and the router **holds for the rest
   of the session**. A human instruction beats standing configuration — the same precedence
   `conserve-tokens.py` gives its session phrase.
3. **`--restore`.** An explicit restore path that writes `user_mode_at_entry` back (and restores the
   mirror state), documented as a one-liner in the knowledge file. The kill switch is
   `caveman_routing: off`, which stops **future** writes; `--restore` undoes **past** ones.

**Version-drift resolution order (runtime, every invocation):**

```
1. $CLAUDE_CONFIG_DIR/plugins/cache/caveman/caveman/*/src/hooks/caveman-config.js   (newest mtime)
2. ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/caveman-config.js                      (standalone install)
3. none found  ->  exit 0, emit `caveman-route-noop-no-caveman`, never an error
```

Then `typeof cfg.writeSessionMode === 'function'` **and** `typeof cfg.readSessionModeRaw ===
'function'` **and** `typeof cfg.resolveActiveMode === 'function'` before any call. Missing any → path
3. **Log the candidate count** from step 1 in the route event, so a multi-version cache (which makes
newest-mtime a guess) is visible rather than silent.

**Read-back verification (adopted from plan-B P3).** Immediately after `writeSessionMode`, re-read via
the **same resolved module's** `resolveActiveMode` and confirm it decodes to the intended mode. On
mismatch, emit a `warn`-tier hook event (`caveman-route-readback-mismatch`) rather than failing
silently. This is the early-warning mechanism for contract drift.

Other requirements: `node` absent → exit 0 no-op; caveman not installed → exit 0 no-op;
`set -euo pipefail`; bash 3.2-safe (C10); direct filesystem writes only, never the `Write` tool (C14);
`--self-test` covering resolve-success, resolve-failure, snapshot-failure-aborts-write,
readback-mismatch, and restore.

**Acceptance test:** self-test green **plus** a live round-trip against the real installed caveman —
write `off`, read the session file, assert literal `off`, assert `resolveActiveMode` agrees, assert
the legacy mirror unlinked; `--restore`, assert the prior value **and** the prior mirror state return.
**Both directions**, per P0.3's reasoning. Must-fail half: remove the snapshot-abort and show a write
proceeding with no snapshot.

**Pre-build gate:** P0.1 (Q3 not re-opened), P0.2 and P0.3 all green.

---

### P3 — Hook body, wired in SHADOW (`plugins/ravenclaude-core/scripts/caveman-route-hook.sh`)

`depends_on_claims: [1, 2, 3]` · `reversibility: two-way-door` — remove two `hooks.json` entries and
two `settings.json` entries.
**Owner: backend-coder**

- Lives in `scripts/`, registered `bash ${CLAUDE_PLUGIN_ROOT}/scripts/caveman-route-hook.sh --event …`
  — the C2-(b) pattern, matching `ask-on-ambiguity.sh:241` exactly. **Not** in `hooks/` (C1).
- **First two lines are the short-circuit:** `[ -f "$posture" ] || exit 0`, then one anchored `grep`.
  Absent or `off` → exit 0, **zero file writes of any kind**. This is plan-B's O(1)-floor discipline,
  adopted.
- **`shadow` is what "enabled" means for this phase:** decide, record, **never call the applier**.
  `live` is not wired until P7.
- Latency budget `RC_CAVEMAN_ROUTE_BUDGET_S` (default 3s `[unverified]`) enforced through
  `_rc_timeout` (`hooks/_portable.sh` — stock macOS has no GNU `timeout`, macOS door 2). **Record the
  actual elapsed time in the route log** so the guess is replaced by a measurement.
- **Fail-open unconditionally.** Every path exits 0. It can never block or alter a prompt.
- Registrations (C3): `hooks/hooks.json` — `UserPromptSubmit` (no matcher, `timeout: 10`) and
  `SessionStart` (matcher `startup|resume|clear|fork`, `timeout: 10`) — **and** the dev-mirror
  `.claude/settings.json` with `${CLAUDE_PROJECT_DIR}`.
- **Projector disposition (C4):** add `caveman-route-hook.sh` to `_SKIP` in all three of
  `scripts/generate-{copilot,cursor,gemini}-hooks.py`, reason: *"routes a Claude-Code-only third-party
  plugin; the target mode store does not exist on this host."* Regenerate and confirm the copilot
  generator's `stale = set(_SKIP) - canonical` check stays clean.
- **No `compact` matcher entry.** It would be a re-fire with nothing to do, and the v0.302.0-era
  incident was seven `SessionStart` hooks re-firing on every mid-conversation compaction for want of a
  matcher.

**Acceptance tests:** (a) absent posture → hook exits 0 having written nothing (assert positively: the
state file is **not created**); (b) `caveman_routing: off` → same; (c) `caveman_routing: shadow` → a
decision line lands in the route log **and the caveman session mode file is byte-identical before and
after** (the shadow invariant, asserted positively, with a must-fail half that removes the shadow gate
and shows the file changing); (d) a malformed transcript → exit 0, no state corruption.

**Pre-build gate:** P1 and P2 self-tests both green. P2 need not be *called* here, but it must exist
and pass, or P7's flip has nothing to enable.

---

### P4 — SessionStart re-arm and the reset race

`depends_on_claims: [3, 6]` ← **row 3 citation added by G6** · `reversibility: two-way-door`
**Owner: backend-coder**

Caveman re-derives `getDefaultMode()` on `RESET_SOURCES = {startup, clear}` and reads the stored mode
on `compact`/`resume`/`fork` (claim 6). So:

- **`startup` / `clear`** — our stored verdict is discarded by caveman; the router must re-evaluate
  from scratch: bootstrap verdict `off`, streak reset, cursor reset. **This is also the fix for the
  race plan-B named:** without it, a user's `/clear` resets caveman to default but our stale
  hysteresis state could immediately flip it back `off` on the next classification, silently
  overriding the user's explicit fresh start.
- **`resume` / `fork`** — caveman preserves the stored mode, so the router **preserves its own state
  too** (cursor + streak reloaded from the run dir), or the two go out of sync and the router spends
  the full enable-streak re-earning a state caveman already holds.
- **`compact`** — caveman preserves; our cursor points into a transcript that has *appended*, not
  truncated (v0.245.0's measured finding), so the cursor stays valid. No matcher entry is added
  (see P3).
- **State scoping:** `.ravenclaude/runs/<session_id>/caveman-route-state.json`, scoped by `cwd` +
  `session_id` per `runaway-brake.sh`'s `rc-state-key` convention — two sibling worktrees under one
  `session_id` must not share routing state (plan-B).

**Acceptance test:** four fixtures, one per `source`, asserting state **reset** on `startup|clear` and
state **preserved** on `resume|fork`, with a must-fail half that treats all four alike and shows
`resume` losing its streak. Plus: a fabricated `source: "compact"` does **not** reset state.

---

### P5 — Observability + offline replay calibration

`depends_on_claims: [3, 7]` ← **row 3 citation added by G6** · `reversibility: two-way-door`
**Owner: backend-coder (observability) → tester-qa (replay harness)**

**Observability (no new file):**

- `_emit_hook_event "caveman-route-hook.sh" "warn" "" "" "<verdict-token>" 0` on every **transition**,
  never on `hold` (the v0.273.0 lesson: emitting the allow path buries the denies). Verdict tokens are
  a **fixed enum** (C8): `caveman-route-on`, `caveman-route-off`, `caveman-route-shadow-on`,
  `caveman-route-shadow-off`, `caveman-route-noop-no-caveman`, `caveman-route-manual-override`,
  `caveman-route-readback-mismatch`.
- Per-session route log `.ravenclaude/runs/<session>/caveman-route.jsonl`:
  `{ts, verdict, why, tool_uses_in_window, responses_in_window, streak, elapsed_ms, flap_count,
  applied: bool}`. **Derived integers and enums only** — no prompt text, no tool names, no file paths.
  This log is the dataset P7's threshold decision reads.
- **No SessionStart banner line.** `capability-orientation.py` is already dense and this is an opt-in,
  off-by-default mechanism; a banner for a feature nobody has enabled is per-turn tax on the budget
  the feature exists to protect.
- **No dashboard control this pass — deferred and named, not dropped.** Gate 132's DOM budget is a
  monotonic ratchet at zero slack; a control costs an owner-approved raise (the `dashboard_autostart`
  precedent, v0.216.0). This is an **owner decision**, surfaced as open question 3.

**Offline replay calibration (G6's addition — this is the cheapest step that settles the thresholds):**

A `--replay <transcript>` mode on `caveman-route.py` that streams an existing transcript through the
classifier turn-by-turn and emits the verdict trace it *would* have produced. Run it across the corpus
under `~/.claude/projects/` (census taken in P0.5), and for each transcript run `caveman-stats.js`
to get the measured net token delta. **Correlate.** This costs zero API dollars and zero wall-clock,
and it is the disconfirming probe for claims-table row 3: *if the verdict trace does not inflect where
the token-cost curve inflects, row 3 is wrong and the classifier's premise fails.*

**Acceptance tests:** (a) a shadow-mode session produces ≥1 JSONL line; (b) **no-egress** — `grep` the
route log for a sentinel planted in the prompt **and** in a tool result; it must not appear, with a
must-fail half that echoes a raw field and shows the sentinel leaking (the Gate 110 / Gate 186 shape);
(c) `--replay` over ≥10 archived transcripts produces a written correlation table, committed as a
dated addendum to `knowledge/caveman-auto-routing.md`, **including the case where correlation is
absent** — a null result is the finding, not a failure to report.

---

### P6 — Gate 264 + CI registration

`depends_on_claims: []` · `reversibility: two-way-door`
**Owner: tester-qa**

New `plugins/ravenclaude-core/hooks/tests/test-gate264-caveman-routing.sh`, invoked by
`scripts/audit-gates.sh` via `bash`. `hooks/tests/*.sh` is believed to be outside the
`plugins/*/hooks/*.sh` executability glob (which is non-recursive), so the file is shippable without a
chmod — **but confirm it at build time**, because C1 is the load-bearing constraint of the whole plan
(risk R9 carries the fallback).

Checks, each with teeth (a must-fail half):

1. `caveman-route.py --self-test` exits 0; must-fail: dedupe removed → density metric changes.
2. `caveman-apply-mode.sh --self-test` exits 0; must-fail: snapshot-abort removed → a write proceeds
   with no snapshot.
3. Short-circuit floor: absent posture and `off` posture both produce **zero** state writes; must-fail:
   short-circuit removed → state file appears.
4. Shadow invariant: `shadow` never mutates the caveman mode file; must-fail: shadow gate removed →
   the file changes.
5. No-egress: planted sentinel absent from the route log; must-fail: raw field echoed → sentinel
   present.
6. `_SKIP` present in all three projectors and the copilot `stale` check clean.
7. Read-back verification fires: mutate the applier to write a bogus value and confirm a
   `caveman-route-readback-mismatch` warn event is emitted.

**Plus a second, deliberately NON-required test** (plan-B): `test-caveman-write-contract-dev-only.sh`
— registered as an optional `--check N` target that globs the installed caveman **for the test only**
and round-trips a real write through its own reader. It **LOUD-skips** ("THIS IS NOT A PASS") when
caveman is absent, matching Gate 10's actionlint precedent. It is excluded from the required/blocking
CI set because it depends on a third-party plugin being installed, which CI cannot guarantee.
**A skip is not a pass.**

**Registration — all three surfaces, each verified by a separate `grep` after the edit:** the
`--check` dispatcher arm, the main sequence, and the `Supported:` string. Then **run the full suite,
grep its output for `Gate 264`, and confirm the assertion count moved.** This is the Gate 184 lesson:
a gate registered in only one of three surfaces ran nowhere for a whole release while the suite
reported green.

**Pre-build gate:** re-census the max gate slot against a **freshly-merged `origin/main`** (C13 —
`[G6-verified]` max on this worktree is 263, so 264 is next *here*; a stale base is how 261 was once
double-allocated). If `origin/main` has advanced, take the next free slot and update every reference.

⚠ **Do not run `scripts/audit-gates.sh` in the foreground** — the Bash tool's timeout is clamped at
600000ms and the suite outgrew it; use `run_in_background: true` or `--check 264` for the single gate.
Also: a full clean run performs a teeth-test `git checkout` that can revert uncommitted
`plugin.json` / `marketplace.json` edits — **version-bump AFTER the suite, not before.**

---

### P7 — Flip to `live`, docs, version

`depends_on_claims: [1, 2, 3]` · `reversibility: two-way-door` — `caveman_routing: off` disables
future writes; `--restore` undoes past ones. **This is the phase that opens P2's one-way door.**
**Owner: architect (threshold ruling) → backend-coder (edits) → code-reviewer → security-reviewer**

**Entry criterion — a real gate, not a formality. Two stages:**

1. **Offline replay (P5) must show correlation**, or the thresholds change before anything proceeds.
2. **≥10 real shadow sessions logged**, of which ≥3 are tool-heavy and ≥3 prose-heavy by manual
   inspection, each shadow verdict trace compared against `caveman-stats.js` on the same transcript.

**If the shadow verdict does not correlate with the measured net token delta, the thresholds change
before the flip — or the flip does not happen.** A null result at stage 1 is a legitimate outcome that
stops the plan; it does not license proceeding to stage 2 to "see if it works live."

Then:

- `plugins/ravenclaude-core/knowledge/caveman-auto-routing.md` — the contract, the Q1–Q4 decisions with
  their runners-up, the runtime version-drift resolution order, the kill-switch procedure, and the
  **honest limits** below, each marked observation vs inference.
- `plugins/ravenclaude-core/CLAUDE.md` — one dated milestone entry naming what was built, why, and
  what is explicitly deferred (no dashboard control; no numeric-threshold tuning beyond the
  hysteresis rule; contract-drift risk monitored via read-back, not eliminated).
- `.claude-plugin/plugin.json` version bump → `python3 scripts/sync-plugin-versions.py` →
  `python3 scripts/generate-copilot-plugin.py` (**both** required; the sync script deliberately does
  not call the generator). Bump **after** the full gate suite (see P6's warning).
- **Do NOT seed `caveman_routing` into `templates/comfort-posture-balanced.yaml` as anything but a
  comment.** Default stays `off`. A consumer who has never heard of caveman must see **no** behaviour
  change on `/plugin marketplace update`. *(Confirm the actual seed-template path at build time —
  plan-B correctly flagged that the templates directory was not enumerated.)*

**Acceptance test:** full `scripts/audit-gates.sh` green (backgrounded); `prettier --check .` and
`ruff check .` green; a live `live`-mode session shows the mode file transitioning and the route log
recording it, with `applied: true`. **Run the built-in `/code-review` on the full diff before opening
the PR for review** — G8 addition: the plan named `code-reviewer`/`security-reviewer` as owners in the
phase headers but omitted the repo's standard pre-merge tool itself from any acceptance test; this is
that correction, applied rather than dropped, per this pipeline's own G8 convention (`plan.md`'s own §
"Any phase that lands as a PR with real code changes names `/code-review` in its DoD").

---

## Dependency DAG (reconciled)

```
                       ┌──────────────────┐
                       │        P0        │  5 probes, each with a positive control
                       │  pre-build       │  ⚠ GATE: P0.1 can force a Q3 re-decision
                       │  (~2 h)          │  ⚠ GATE: P0.5 sizes P5's replay corpus
                       └───┬──────────┬───┘
                ┌──────────┘          └──────────┐
                ▼                                ▼
        ┌──────────────┐                 ┌──────────────┐
        │      P1      │                 │      P2      │  ← PARALLEL (different files,
        │ classifier + │                 │  applier     │     no shared symbol)
        │ knob schema  │                 │  ⛔ one-way  │  → security-reviewer (blocks P7)
        │ (~4 h)       │                 │  (~3 h)      │     door BUILT here, OPENED at P7
        └──────┬───────┘                 └───────┬──────┘
               └───────────┬────────────────────┘
                           ▼
                    ┌──────────────┐
                    │      P3      │  hook body, registered, SHADOW only
                    │  (~4 h)      │  ★ CRITICAL PATH
                    └───┬──────┬───┘
             ┌──────────┘      └──────────┐
             ▼                            ▼
      ┌──────────────┐            ┌──────────────┐
      │      P4      │            │      P5      │  ← PARALLEL work, SERIAL commits
      │ SessionStart │            │ observability│     (both edit caveman-route-hook.sh)
      │ re-arm (~2 h)│            │ + REPLAY(~3h)│
      └──────┬───────┘            └───────┬──────┘
             └───────────┬────────────────┘
                         ▼
                  ┌──────────────┐
                  │      P6      │  Gate 264, 3-surface registration, suite grep
                  │  (~4 h)      │  + non-required dev-only contract test
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │      P7      │  ⏸ TWO-STAGE GATE:
                  │ flip + docs  │     (1) P5 replay correlation, then
                  │  (~3 h)      │     (2) ≥10 live shadow sessions
                  └──────────────┘
```

**Critical path:** P0 → P1 → P3 → P6 → P7 ≈ **17 h of build** `[unverified — an estimate carried from
plan-A, not a measurement; do not treat as a commitment]`, plus the shadow soak, which is wall-clock
and not billable engineering time.

**Parallelizable:**
- **P1 ∥ P2** — different files, no shared symbol. A second implementer can build and unit-test P2
  entirely independently (plan-B made the same call about its writer phase).
- **P4 ∥ P5** — different concerns, but **both edit `caveman-route-hook.sh`**: the *work* parallelizes,
  the *commit* does not. Serialize the two edits or take one branch each.

**Blocks:**
- P0.1 blocks the Q3 ruling, therefore blocks P2.
- P0.5 blocks P5's replay design (not P5's observability half).
- P2's security review blocks **P7**, not P3 — shadow never calls the applier.
- P5's replay correlation blocks P7 stage 1; the shadow soak blocks P7 stage 2. Nothing else.

**Every step leaves the tree green:** P1/P2 add self-tested scripts nothing calls. P3 registers a hook
that is inert without a posture key. P4/P5 refine an inert hook. P6 gates it. P7 flips a default that
is still `off` for every consumer.

---

## Risk matrix

Every risk, with its mitigation. **One-way-door phases are listed first and their mitigations are
mandatory build content, not advice.**

### One-way-door phases

| Phase | Why it is one-way | Mandatory mitigation (all parts required) |
|---|---|---|
| **P2 (built) / P7 (armed)** — the first automatic write to a live caveman session mode | The write **destroys the user's own manually-set mode with no record of what it was** — irreversible at the data level and invisible. Both panels independently flagged this as the plan's one-way door. | **(1) Pre-write snapshot** of `readSessionModeRaw` **and** the legacy mirror's state to `.ravenclaude/runs/<session>/caveman-route-state.json`, taken **before** any write; **snapshot failure aborts the write.** **(2) Manual-override latch** — a non-default entry mode, or any `/caveman …` typed this session, sets `manual_override: true` and the router holds for the rest of the session. **(3) `--restore`** writes `user_mode_at_entry` (and the mirror state) back. **Kill switch:** `caveman_routing: off` stops future writes; `--restore` undoes past ones. **Nuclear option** (documented in the knowledge file): delete `~/.claude/.caveman-sessions/<session_id>.mode` — caveman's reader treats a missing file identically to `off`, so this is always safe. **P6 check 2 is the must-fail test that proves (1) is load-bearing.** |

### All other risks

| # | Risk | Mitigation |
|---|---|---|
| R1 | **Hook-ordering race.** Matching hooks run in parallel, so our `writeSessionMode` may land after caveman's `mode-tracker` has already read the mode for this turn → one turn of lag. | Accept and document. plan-A estimated ~7% of the loss `[unverified — arithmetic on the n=1 session]`. **Do not attempt ordering guarantees — there are none to have.** |
| R2 | **Turning `off` mid-session does not evict the already-injected SessionStart ruleset.** It stops the per-turn reinforcement; the resident ruleset keeps costing cache-read tokens for the rest of the session. | State it plainly in the knowledge file. The savings claim is *"stops the per-turn reinforcement"*, **not** *"recovers the full ~1,250/turn."* Overclaiming here is the exact defect this repo's record keeps naming. |
| R3 | **Caveman version bump moves `caveman-config.js` or changes `writeSessionMode`.** The cache dir is content-hash-keyed with **no semver to pin against** (`[G6-verified]`). | Runtime glob resolution (newest mtime) across both install shapes; `typeof` check on all three needed exports before any call; any failure → silent no-op + one warn event. **Plus read-back verification**, which turns a drifted contract from "silently stops working" into an emitted `caveman-route-readback-mismatch`. Log the resolution candidate count so a multi-version cache is visible. |
| R4 | **We overwrite a mode the user set by hand.** | The one-way-door mitigation above, all three parts. |
| R5 | **Thresholds are n=1 guesses.** | Marked `[unverified]` everywhere they appear. P5's offline replay settles them at zero cost; P7's two-stage gate makes correlation a hard entry criterion. The design is such that wrong thresholds during shadow cost **nothing but forgone savings**. |
| R6 | **Per-turn subprocess latency.** | Two-grep short-circuit for non-adopters; incremental byte cursor + 4 MiB cap for adopters; hard `_rc_timeout` budget. **Measure it during shadow (`elapsed_ms` in the route log) and report the number rather than asserting it is small.** |
| R7 | **Our hook flaps** (on/off/on across adjacent turns), paying SessionStart re-injection repeatedly. | Asymmetric hysteresis (4-response streak to enable, 1 to disable) makes flapping structurally hard; `flap_count` in the route log makes it **visible** if it happens anyway, so P7 can check for it. |
| R8 | **Fidelity regression.** Claim 2 observed no fidelity loss on 6 prose prompts — a small sample that says nothing about agentic turns. | The design never enables caveman during tool-heavy stretches, which is where a fidelity loss would be most costly. Prose-only is the only regime we enable in — the regime claim 2 actually measured. |
| R9 | **The `hooks/tests/` executability assumption is wrong** and P6's test file needs a chmod we cannot do. | Confirm during P6, not at merge. Fallback: put the checker at `plugins/ravenclaude-core/scripts/check-caveman-routing.sh` (the `check-*.py` precedent) and invoke it from `audit-gates.sh` with `bash`. |
| **R10** | **⚠ NEW — surfaced by G6, unreconciled by either panel: our writes touch a MACHINE-WIDE file.** `[G6-verified]` `writeSessionMode` unlinks `$CLAUDE_CONFIG_DIR/.caveman-active` whenever it writes `off` (`caveman-config.js:494-497`). plan-B correctly warned that this mirror is last-write-wins across **all** sessions; plan-A adopted the seam that touches it without noting the cross-session consequence. | **Bounded, measured, and mitigated — not eliminated.** `[G6-verified]` `resolveActiveMode` (`:455-461`) reads the **per-session file first** and falls back to the mirror **only when the per-session file has no stored value**. So the blast radius is: *another concurrent session that has no per-session mode file yet (a fresh window before caveman's own SessionStart has written one, or an older/standalone install) silently loses caveman.* Not corruption, not data loss, and it degrades in the **safe** direction (caveman off ⇒ no rule overhead ⇒ forgone savings only). **Mitigations:** (a) snapshot the mirror's pre-state alongside the per-session snapshot and restore both on `--restore` (built into P2's mitigation 1); (b) P0.3 measures whether other `.caveman-sessions/*.mode` files exist on this host, sizing the real exposure; (c) state it verbatim in the knowledge file's honest limits. **Do NOT "fix" this by writing the mirror ourselves** — caveman's comment at `:480-486` documents why the mirror must never hold the literal `off` (an older `mode-tracker` would inject `"CAVEMAN MODE ACTIVE (off)"`, an older statusline would render `[CAVEMAN:OFF]`), and that is exactly the rule we chose the seam to avoid reimplementing. |
| R11 | **A new source module trips `guard-premise.sh`'s unresolved-negative check** during implementation. | Standard FORGE-worktree development friction, not a design risk. Resolve via the file-based `control.md` escape this repo already ships (v0.245.0) — **an env var cannot reach a PreToolUse hook from inside the gated command**. |
| R12 | **State written through the agent's `Write` tool re-imports `worktree-guard` lease contention.** | C14 — every state write stays a direct hook-process filesystem operation. **Code-review redline** for this PR and any future revision. |

**Global kill switch:** `caveman_routing: off` in `.ravenclaude/comfort-posture.yaml`, or delete the
two `hooks.json` entries and the two `.claude/settings.json` entries. Neither leaves residue beyond a
per-session state file under gitignored `.ravenclaude/runs/`, and caveman's own `gcSessionStore` sweeps
its side at a 14-day TTL.

---

## Concrete file-level plan

Paths relative to
`/Users/matthewcorbett/RavenClaude/.claude/worktrees/forge-caveman-routing-decision-tree/`.

### New files

| Path | Phase | What |
|---|---|---|
| `plugins/ravenclaude-core/scripts/caveman-route.py` | P1, P5 | Pure classifier + knob schema + `--self-test` + `--replay`. Stdlib only. |
| `plugins/ravenclaude-core/scripts/caveman-apply-mode.sh` | P2 | Runtime-resolved `node -e` bridge to `writeSessionMode`; snapshot; read-back verify; `--restore`; `--self-test`. |
| `plugins/ravenclaude-core/scripts/caveman-route-hook.sh` | P3 | Hook body, `--event {prompt,session}`. Invoked via `bash` (C1/C2-b). |
| `plugins/ravenclaude-core/hooks/tests/test-gate264-caveman-routing.sh` | P6 | Gate 264 checker, 7 checks each with a must-fail half (verify the executability assumption first — R9). |
| `plugins/ravenclaude-core/hooks/tests/test-caveman-write-contract-dev-only.sh` | P6 | **NOT in the required CI set.** Optional `--check N`; LOUD-skips when caveman is absent. |
| `plugins/ravenclaude-core/knowledge/caveman-auto-routing.md` | P7 | Contract, Q1-Q4 decisions, runtime resolution order, kill-switch, honest limits, P5's replay addendum. |

**No `.repo-layout.json` edit** — C15.

### Edited files

| Path | Phase | Edit |
|---|---|---|
| `plugins/ravenclaude-core/hooks/hooks.json` | P3 | +1 `UserPromptSubmit` entry (no matcher, `timeout: 10`), +1 `SessionStart` entry inside the existing `startup\|resume\|clear\|fork` group. Both `bash ${CLAUDE_PLUGIN_ROOT}/scripts/caveman-route-hook.sh --event …`. |
| `.claude/settings.json` | P3 | The same two entries with `${CLAUDE_PROJECT_DIR}` paths (C3). |
| `scripts/generate-copilot-hooks.py` | P3 | `_SKIP["caveman-route-hook.sh"]` + reason; re-run; confirm the `stale` check (`:257`). |
| `scripts/generate-cursor-hooks.py` | P3 | `_SKIP` entry (`:70`). |
| `scripts/generate-gemini-hooks.py` | P3 | `_SKIP` entry (`:69`). |
| `scripts/audit-gates.sh` | P6 | Gate 264 in **three** places: `--check` arm, main sequence, `Supported:` string. Grep-verify each separately. |
| `plugins/ravenclaude-core/templates/comfort-posture-balanced.yaml` *(confirm path at build time)* | P7 | A **commented-out** `caveman_routing: off` block only — matching the `context_handoff` precedent. The key stays absent so the seed never enables it. |
| `plugins/ravenclaude-core/.claude-plugin/plugin.json` | P7 | `version` bump (single source of truth). **After** the gate suite. |
| `.claude-plugin/marketplace.json` | P7 | **Derived** — `python3 scripts/sync-plugin-versions.py`, never hand-edited. |
| `plugins/ravenclaude-core/copilot/plugin.json` | P7 | **Generated** — `python3 scripts/generate-copilot-plugin.py`. |
| `plugins/ravenclaude-core/CLAUDE.md` | P7 | Dated milestone entry. |

### Untouched, deliberately

- `plugins/ravenclaude-core/hooks/stream-prompt-attribute.sh` — we take the C2-**(b)** escape, not the
  delimited-block escape. It already carries a second concern; a third would make it the thing it is
  explicitly trying not to become. *(This is the rejection of plan-B's zero-registration wiring.)*
- `plugins/ravenclaude-core/hooks/capability-orientation.sh` — same reasoning.
- `plugins/ravenclaude-core/hooks/reapply-posture.sh` — plan-B correctly self-corrected here: its sole
  job is regenerating permission rules from the posture YAML; third-party plugin state is not its
  concern.
- Anything under `/Users/matthewcorbett/.claude/plugins/cache/caveman/` — read-only, black box (C11).
  Globbed at runtime for **resolution**, never written or patched.
- `scripts/generate-dashboards.py` — no dashboard control this pass (owner decision, open question 3).

---

## Honest limits — carry verbatim into `knowledge/caveman-auto-routing.md`

- **This stops the per-turn reinforcement, not the resident ruleset.** A mid-session `off` does not
  evict the SessionStart-injected rules already in context.
- **One turn of lag is expected** and cannot be removed — matching hooks run in parallel.
- **The thresholds are n=1-derived and provisional.** Every number in this plan carries an
  `[unverified]` marker until P5's replay says otherwise.
- **Our `off` write unlinks a machine-wide file** (`.caveman-active`). The exposure is bounded to
  concurrent sessions that have no per-session mode file yet, and it degrades in the safe direction —
  but it is a real cross-session side effect and it is not zero. (R10.)
- **Nothing here is a control.** It is a routing convenience gated by a posture knob; it blocks
  nothing, denies nothing, and fails open on every path.
- **The 26.5% figure is from 6 isolated prose prompts with `--tools ""`.** It is not a prediction about
  a mixed live session, and this mechanism must not be described as delivering it.
- **The contract-drift risk is monitored, not eliminated.** Read-back verification emits a warn; it
  does not repair.

---

## Open questions for the Team Lead

1. **Does `additionalContext` from one `UserPromptSubmit` hook reach a sibling hook's `.prompt`?**
   Both panels independently concluded no, from `caveman-mode-tracker.js:135` plus `_advise.sh`'s
   concatenation finding. That conclusion is an **inference**, and it is the one that kills Q3 option
   (a). **P0.1 settles it.** *(Blocks the Q3 ruling, therefore blocks P2.)*
2. **Is `plugins/*/hooks/tests/*.sh` genuinely outside the executability gate?** The CI glob is
   non-recursive, but the chmod denial is the load-bearing constraint of this whole plan and deserves
   a direct check. R9 carries the fallback. *(Blocks P6.)*
3. **Owner ruling: does the dashboard control ship now or later?** It needs an owner-approved Gate 132
   DOM-budget ratchet raise. G6 defers it rather than spend the raise on an off-by-default feature —
   but the `dashboard_autostart` precedent is that the owner wanted the control, not just the YAML
   key. *(Blocks nothing; changes P5's scope if answered "now.")*
4. **Is the two-stage entry criterion for P7 acceptable** — offline replay first (free, immediate),
   then ≥10 live shadow sessions — or does the owner want the second isolated A/B (Q4's runner-up) run
   first at real API cost? G6 recommends replay-first: it is free, it uses transcripts already on disk,
   and it measures a classifier over mixed live sessions rather than isolated prompts. *(Blocks P7.)*
5. **`node` is a hard dependency of the chosen seam.** Present here (v26.5.0), and caveman itself
   cannot run without it, so a consumer with caveman installed necessarily has it. Confirm this
   reasoning is acceptable rather than requiring a node-free fallback. *(Blocks nothing; would reopen
   Q3 toward plan-B's writer if rejected.)*
6. **Is the R10 cross-session mirror side effect acceptable?** It is bounded and degrades safely, but
   it is a side effect on sessions this plan does not own, and neither panel surfaced it. *(Blocks
   nothing; would reopen Q3 if the owner wants zero cross-session footprint — note that plan-B's writer
   also does not solve it cleanly, it merely leaves the mirror stale instead of absent.)*

---

## G6 synthesis record

| Item | Resolution |
|---|---|
| **A-vs-B write mechanism** | **plan-A's seam wins** — caveman's own `writeSessionMode`, resolved fresh at runtime by glob. plan-B's objection targeted a hardcoded-hash version of (b) that plan-A did not propose; the "detect the path fresh at runtime" third option **is already plan-A's design**. Both designs fail identically ("toggle silently stops working"), so the tiebreak goes to less reimplemented code. plan-B's **read-back verification** is adopted on top, converting that shared failure mode into a detected one. |
| **Cadence (Q1)** | plan-A's per-turn wins over plan-B's every-3-turns; plan-B's O(1)-floor discipline adopted as the short-circuit rule. |
| **Wiring** | plan-A's new C2-(b) script wins over plan-B's zero-registration edits to two existing hooks, on concern-separation and auditability. plan-B's structural finding was `[G6-verified]` as real — it was rejected on cost-of-ownership, not on being wrong. |
| **Convergences merged, not concatenated** | NL-trigger (option a) structurally dead — both panels, same line, merged with plan-B's stronger `_advise.sh` corroboration. `chmod +x` denial → `scripts/` + `bash` escape — both panels. Transcript tool-call density signal — both panels. Conservative-off + asymmetric hysteresis + shadow-before-live — both panels. |
| **New finding (neither panel)** | **R10** — the chosen seam unlinks a machine-wide file. `[G6-verified]` from `caveman-config.js:487-500` + `:455-461`. Bounded, mitigated, documented. |
| **New step (neither panel)** | **Offline replay** in P5 — settles every `[unverified]` threshold from transcripts already on disk, at zero API cost and zero wall-clock, before any live soak. |
| **Unverified numbers flagged** | `W=6`, the `off` trigger, the 4-response `on` streak, `M`, the 3s latency budget, the ~17 h estimate, and the "~7% of the loss" figure — each marked `[unverified]` with the cheapest settling step named. |
| **G3b verdict** | **Consistent and confirmed.** Row 3 remains the load-bearing inference and is cited on every phase that depends on it — **including three phases (P1, P4, P5) where a panel had omitted the citation**; the citations were added rather than the gap dropped. |
