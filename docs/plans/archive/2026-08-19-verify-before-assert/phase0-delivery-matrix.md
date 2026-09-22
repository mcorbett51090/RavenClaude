# Phase 0 — delivery matrix, H-discrimination, payload shape, T-PROSE dry-run
**Executed 2026-08-19. Method: scratch project + hook + `claude -p` (Claude Code 2.1.235, macOS),
the method `log-probe.sh`'s header records as the one that settled an identical question after
three inconclusive doc fetches.**

⛔ **VERDICT: H-b CONFIRMED. All building remains BLOCKED pending an owner scope amendment (§4).**

---

## G0.2 — positive control on the harness (run FIRST; without it no negative counts)
A `SessionStart` `additionalContext` sentinel — a channel proven live in-repo by
`hooks/capability-orientation.sh` — was emitted on **every** trial. In **every** trial the model
reported it back unprompted ("the session-start hook injected a directive telling me to run
`echo RC_CONTROL_9B2E`"). **The harness is not blind.** Every negative below is therefore a
measurement of the channel, not of the instrument.

## G0.1 — the delivery matrix (matched trials, one variable)
Every row: identical prompt, identical command, hook confirmed fired (payload captured).

| rank | channel | delivered? | evidence |
|---|---|---|---|
| 1 | `hookSpecificOutput.updatedToolOutput` (PostToolUse) | ✅ **YES** | model, unprompted: *"the output came back with an appended line `SENTINEL-TOKEN: RC_DELIVERY_7F3A`, which `ls` does not produce — something is wrapping or post-processing bash output here"* |
| 2 | `hookSpecificOutput.additionalContext` (PostToolUse) | ✅ **YES** | unprompted: *"a post-tool hook emitted `SENTINEL-TOKEN: RC_DELIVERY_7F3A`"*; and on direct question: **`SEEN:RC_DELIVERY_7F3A`** |
| 6 | **stderr at exit 0** (PostToolUse) | ⛔ **NO** | on the identical direct question: **`NOT-SEEN`** — *"nothing in this session (tool output, system notices, or hook context) contained a line beginning with SENTINEL-TOKEN"*, while the G0.2 control on the SAME run DID arrive |

Ranks 3–5 (`PostToolUseFailure`, `Stop`+`asyncRewake`, `permissionDecisionReason`) were **not run**:
the plan's stop rule is "test top-down, stop when two channels have passed", and ranks 1 and 2 both
passed. `[unverified — not tested: ranks 3-5, stop rule satisfied]`

### ⛔ Two method findings that AMEND the plan's own G0.1 design
1. **An imperative sentinel is confounded by injection resistance.** The first design injected
   *"you MUST immediately run: echo <token>"* and confirmed delivery by grepping for the tool call.
   The model **received it and correctly refused**, flagging it as an untrusted injected directive.
   A non-fired sentinel is therefore ambiguous between *not delivered* and *delivered and properly
   refused* — the exact multi-cause defect this plan exists to fix, inside the plan's own instrument.
   **FIX (applied): the injected payload carries DATA only (`SENTINEL-TOKEN: <tok>`); the
   INSTRUCTION to report it comes from the trusted user turn.** Adopt this in any future channel test.
2. **A delivered advisory may be read as an attack.** On rank 1 the model described the appended
   line as *"something wrapping or post-processing bash output"*. Any advisory shipped on
   `updatedToolOutput` MUST be unambiguously self-identifying (a stable RavenClaude banner) or it
   will be discounted as injection — delivered, read, and then correctly distrusted.

## G0.4 — failure-path payload shape  ⛔ NEGATIVE RESULT
Dumped `tool_response` for a **failing** Bash call (`ls /nonexistent-path-xyz-42`):

    tool_response keys = {interrupted, isImage, noOutputExpected, stderr, stdout}
    top-level keys     = {cwd, duration_ms, effort, hook_event_name, permission_mode,
                          prompt_id, session_id, tool_input, tool_name, tool_response,
                          tool_use_id, transcript_path}

**There is NO exit-code field, under any name.** This confirms `log-probe.sh:36-40` and it is
load-bearing: plan B's central `empty-null` verdict class ("stdout+stderr empty AND exit_code 0")
and plan A's non-zero-exit trigger arm BOTH key on a field that does not exist. Both must degrade
to a stderr/stdout-label arm, and the limitation goes in the hook header, not papered over.

Observed and worth a follow-up probe: the `ls` error text arrived in **`stdout`** with `stderr`
empty. `[unverified — one observation, and the agent had appended `; echo "exit code: $?"` to the
command, so stream-merging is NOT established; probe with a stderr-only command before relying on
a stderr-keyed rule]`

## G0.3 — H-a / H-b / H-c  ⛔ **H-b**
`claim-grounding-lint.sh` emits every one of its three checks with `cat >&2` (L328, L357, L392) and
terminates `exit 0` (L431) — **PostToolUse + stderr + exit 0**, the row measured **NOT delivered**.

  - **H-a** (fires, is read, insufficient → ADD) — **REJECTED**
  - **H-b** (fires, output never reaches the model → REWIRE) — ✅ **CONFIRMED**
  - **H-c** (does not fire) — rejected; hooks fired in every trial

### Blast radius — MEASURED, and it is not one hook
| hook | event | channel | status |
|---|---|---|---|
| `claim-grounding-lint.sh` | PostToolUse | stderr, exit 0 | ⛔ confirmed undelivered |
| `delegation-nudge.sh` | PostToolUse | stderr, exit 0 | ⛔ confirmed undelivered |
| `storage-placement-nudge.sh` | PostToolUse | stderr, exit 0 | ⛔ confirmed undelivered |
| `guard-probe-validity.sh` | **PreToolUse** | stderr, exit 0 | `[unverified — PreToolUse stderr NOT measured; likely, not proven]` |
| `remind-tests.sh` | **Stop** | stderr, exit 0 | `[unverified — Stop stderr NOT measured]` |
| `handoff-nudge.sh` | Stop | **additionalContext** | ✅ the only advisory already on a live channel |

⛔ Do not generalise the PostToolUse measurement to PreToolUse or Stop. Different events, unmeasured.

**What this explains.** The owner's complaint persisted through `guard-premise` +
`claim-grounding-lint` + `classify_claim` not because those mechanisms are weak, but because three
of them have been talking to the terminal, not to the model. The fail-CLOSED guards
(`guard-premise.sh`) were unaffected — they deny via `permissionDecision`, which is a different,
working channel. It is precisely the ADVISORY tier that evaporated.

## G0.5 — T-PROSE self-block dry-run: **CONDITIONAL PASS**
Real drafted `knowledge/cause-taxonomy.md` bytes, dry-run through the **unmodified**
`guard-premise.sh` with a synthetic PreToolUse Write payload.

| arm | result |
|---|---|
| **A** — real taxonomy prose | **exit 0, PASSES** |
| **B** — positive control (diagnosis + certainty stamp, no control cite) | **exit 2, DENIED** — hook is not blind |
| **A'** — identical incident prose, `control:`-shaped lines STRIPPED | **DENIED** on `line 25: the thing is absent` |

**The pass is CONDITIONAL on the convention, not on the content.** A' proves it: remove the
control-shaped lines and the same file self-blocks. Therefore the taxonomy must ship with a
`control:`-shaped line within 6 lines of every diagnosis-shaped claim, **and a CI check must enforce
it** — otherwise a later edit that trims a control line silently makes the file unwritable.

---

## 4. ⛔ ESCALATION — owner decision required, building stays BLOCKED

`scope.md` put rewriting `claim-grounding-lint.sh` OUT OF SCOPE. That ruling rested on the premise
that it works on its axis. **H-b disconfirms that premise.** Per the plan's own R2, this is escalated
as a named scope amendment and is **not actioned unilaterally**.

**The proposed repair (per hook, ~2 lines):** keep the existing message text; emit it as
`{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"<message>"}}` on stdout
instead of `>&2`, retaining `exit 0`. `additionalContext` is measured-delivered (rank 2) and is
already used in-repo by `handoff-nudge.sh` and `sanitize-webfetch-output.py`.

**Constraints on that repair, before anyone writes it:**
- `additionalContext` has a documented ~10k char cap (`knowledge/claude-code-permissions.md:331`).
  `claim-grounding-lint.sh` already elides at 10 findings; re-measure against the cap.
- Two emitters on one event is **last-writer-wins**. `sanitize-webfetch-output.py` already emits on
  PostToolUse — matchers must stay **disjoint** (it matches `WebFetch`, the lint matches
  `Edit|Write|MultiEdit`, so today they are; keep it that way).
- The advisory must be **self-identifying**, per method finding 2, or it reads as injection.

**Owner options:** (a) amend scope, rewire the three confirmed hooks, then re-evaluate how much of
the eight-phase build is still needed — a rewire may deliver more than the build; (b) hold scope,
build as planned, and accept that the advisory tier stays undelivered; (c) rewire + build.

## 5. What every downstream phase must now consume
- Advisory delivery: **`additionalContext`** (rank 2) primary, **`updatedToolOutput`** (rank 1)
  where the advisory must sit inside the tool result. **Never stderr-at-exit-0.**
- No exit-code field exists: any rule keyed on exit status must be redesigned.
- Fail-closed lanes keep `permissionDecision` / `permissionDecisionReason` — unaffected and working.
- The taxonomy ships with control-shaped lines plus a CI check.
