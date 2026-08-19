# Owner decisions — binding

## D1 — **REVERSED at G4a. The default is NOT flipped.**

Original (G0): *"Make Claude Code the DEFAULT host"* — flip the no-host-detected fallback
`grok` → `claude-code`. Owner's stated reason: *"the primary method is claude code."*

**Reversed after the critic measured the premise false, and the orchestrator re-measured it:**

| probe | result |
|---|---|
| bare `handoff-spawn.sh --dry-run`, `CLAUDECODE`+`CLAUDE_CODE_ENTRYPOINT` present | `host=claude-code` |
| same, both markers cleared (**control**) | `host=unknown` |

Claude Code resolves at `handoff-spawn.sh:144-147` by **detection** and **never reaches the default
at all**. The default's documented population is the host that *cannot* be reliably detected — Grok
(`handoff-spawn.sh:73-79`, `SKILL.md:22`): the grok-first fallback exists precisely because a real
Grok session can fail detection, and Gate 215 pins that.

So D1's measurable benefit for Claude Code was **zero cases**, and its cost was three gates edited
plus removing the fallback from the only host it was protecting. The owner chose to drop it with that
information in hand.

⛔ **This is the single most valuable thing the pipeline did on this run.** The premise came from the
owner, was accepted by the orchestrator, and was built on by BOTH panels — Plan A wrote a
`host_source` label, a caveat line and three gate rows for a branch Claude Code never enters. Panel B
got one inference short of catching it (§7 #3). Only the critic, told explicitly to attack the
premise, measured it.

**What survives from D1's intent:** the docs lead with Claude Code. That is where the failure actually
happened — an agent read `--host grok|cli|chat` and believed it.

## D2 — UNCHANGED. A named-but-unrecognised `--host` is a HARD ERROR, exit non-zero.

Implementation must follow **Plan A's S4**: validate `normalize_host "$host_flag"` **before**
`detect_origin_host()` runs *and* before the handoff-file existence check.

⛔ **Plan B's version does not work.** It keys the error on `named_but_unknown`
(`handoff-spawn.sh:202`) — the exact variable claim 10 proves broken — and never edits
`detect_origin_host()`. Measured: `--host codex` under `CLAUDECODE` still prints a Claude Code recipe.
Worse, B's own gate rows run under `env -i`, so they would be **GREEN while the defect survives**.

## D3 — NEW, from the critic. Fix the arity bug.

`--host) host_flag="${2:-}"; shift 2` with `--host` as the final argument: `shift 2` fails, `$#` never
decreases, **infinite loop**. Re-measured by the orchestrator: still running after 4 s having emitted
**0 bytes**; control with a value exits 0 with 944 bytes. The same shape affects `--task-id`,
`--recipe`, `--project-root`, `--wait-ack-seconds`.

This is worse than it looks: both plans expand the doc surfaces that tell agents to pass `--host`, so
the change as originally scoped would have **increased** the traffic into a hang.

## D4 — NEW, from the critic. `THING_HOST` must not outrank an explicit `--host`.

`context-handoff.py:64` reads `THING_HOST or RC_HOST`, and `main()` injects the flag as `RC_HOST`.
Measured: `THING_HOST=copilot` + `--host claude-code` → bash emits the Claude Code recipe while python
writes a `copilot` seed. Four live adapters (cursor / gemini / codex / copilot) export `THING_HOST`.
Under D2 this would make a **valid** `--host claude-code` exit 2 on Codex.

## D5 — Keep the VS Code ambiguity carve-out (G4b tiebreak).

Verdict was synthesis in B's favour. With D1 dropped its urgency falls — `unknown` no longer lands on
a named host — but the ruling stands on its own reasoning: a caveat asks the agent to evaluate a prose
conditional about its own identity, which is the exact question that failed and put it in the unknown
branch. Cost asymmetry: kept-wrongly = six keystrokes, loud and self-correcting; deleted-wrongly = the
handoff silently proceeds in the wrong vendor's agent.

## Consequence of dropping D1

**No pinned gate needs its expectation changed.** Gates 213, 215 and 230 keep asserting the grok
default, and they keep passing. The change set shrinks to: docs, D2, D3, D4, alias/case parity
(row 21), and ONE new gate. The riskiest edit in the original plan is simply gone.

---

## D2 — REFINED at G5 (owner ruling). Split by registry membership.

The red team measured that D2-as-written would hard-error **five hosts the repo officially supports**.
`plugins/ravenclaude-core/knowledge/host-support.json` declares seven — `claude-code`, `copilot`,
`codex`, `cursor`, `gemini`, `aider`, `windsurf` — and five of them are absent from
`normalize_host()`. Verified by the orchestrator: `--host codex|cursor|gemini` each exit **0 today
with a 573-byte host-neutral copy-paste block**.

Under D2-as-written they would exit 2 with nothing. That would:
- destroy a working handoff path for five supported hosts,
- break the script's own invariant (`handoff-spawn.sh:8` — the copy-paste block is ALWAYS printed;
  both existing fatal-arg branches print it *then* exit 2),
- kill the recovery instruction at `SKILL.md:33` for those hosts, and
- ⛔ pressure an agent on an unlisted host to pick the nearest recognised token — almost certainly
  `cli` — which is **the exact wrong-vendor failure this entire run exists to fix.**

**Owner ruling:**
- A host **in `host-support.json` but unmapped** → resolve to the **host-neutral** copy-paste block,
  exit 0. Never a different agent's launch command, and never a hard stop on a supported host.
- A string in **neither** the enum nor the registry (typo, garbage) → **exit 2**, as D2 intended.

D2's intent is unchanged and now actually achieved: *never silently answer with a different agent's
launch command.* Host-neutral is not a different agent's command; it is the honest absence of one.

⛔ Note how close this came to inverting itself. My own framing of D2 — "unrecognised host = hard
error" — came from a probe (`--host codex` → claude-code recipe) where I never checked whether `codex`
was a supported host. It is. The bug was the **environment override**, not the absence of an error.

## G5 acceptance criteria — BINDING on G6

The red team passes with **no loop-back required** only if the synthesis adopts all six:

| AC | requirement | why |
|---|---|---|
| **AC-1** | registry hosts resolve host-neutral, exit 0 | the owner ruling above; revisits Plan A S4's ORDERING, not D2's intent |
| **AC-2** | print the copy-paste block **before** any D2 exit 2 | preserves the `:8` always-printed invariant both existing fatal branches honour |
| **AC-3** | `--host` with a missing / empty / `--`-prefixed value exits 2 and **never** falls to case (a) | measured: the naive shift fix turns the hang into a **silent `grok` seed** via the documented `--host $H` shape with `H` empty |
| **AC-4** | the new gate drives **both** writers across all 8 rows | D2 in bash alone breaks the pair-in-step contract at `:140-143`; measured 8-row divergence table |
| **AC-5** | `_rc_timeout` only, plus a positive control and a `BYTES>0` assertion | ⛔ `timeout` and `gtimeout` are **both absent** on this macOS, so bare `timeout N cmd` is exit 127 — the command never runs and an "exits non-zero" assertion passes **vacuously**. Green on Linux CI, green-for-the-wrong-reason locally. `audit-gates.sh` wraps 0 gates in a timeout, so a must-fail half planting `shift 2` would run the infinite loop to the 6-hour job ceiling and block every PR. |
| **AC-6** | every absence assertion carries a same-row presence assertion, plus a `THING_HOST` row with a `THING_HOST=grok` control | Gate 230's existing absence row would pass identically on zero bytes; and every gate clears `THING_HOST`, so the one env path four shipped adapters set is untested |

**Red-team correction to the critic:** D4's blast radius is **unsubstantiated** — nothing sets
`THING_HOST` in any process that reaches either script. The precedence bug is real; the "four live
adapters break it" framing is not. Fix it, but do not justify it with a claimed live impact.
