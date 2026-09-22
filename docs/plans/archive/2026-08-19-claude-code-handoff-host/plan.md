# G6 — Synthesis plan — `claude-code-handoff-host`

**Status:** `pass` · **Target version:** `0.284.0` · **Date:** 2026-08-19
**Worktree (authoritative):** `/Users/matthewcorbett/RavenClaude/.claude/worktrees/forge-claude-code-handoff-host`
**Branch:** `forge/claude-code-handoff-host` · **Plugin version on disk:** `0.283.0`

This is the ONE plan a builder executes. It supersedes `plan-A.md` and `plan-B.md`, both of which
were written under D1 and carry elements that no longer exist. Where those plans disagreed, §2.4
records the resolution; there are no dangling forks.

Every number in this file was **re-measured in this worktree on 2026-08-19** unless marked
`[from red-team.md]` or `[from claims-table.md]`. Commands and controls are quoted so a reviewer can
falsify them.

---

## 1. What this is

**`--host claude-code` already worked. It has worked since 0.276.0.** The defect is a *documented
interface that denies a capability the code has*, and an argument path that resolves the flag by
guessing when it does not recognise the name.

Measured, this session, in this worktree:

```
$ env -i PATH=/usr/bin:/bin HOME="$HOME" bash plugins/ravenclaude-core/scripts/handoff-spawn.sh \
    --task-id t1 --project-root $P --dry-run --host claude-code
EXIT=0  BYTES=443   # emits `# copy-paste … (Claude Code, not grok)` + `claude`
```

The cost is not hypothetical. In the session immediately prior, an agent read
`handoff-spawn.sh:19` — `Usage: … [--host grok|cli|chat]` — and `SKILL.md:23` — *"Pass
`--host grok|cli|chat` from what you actually are"* — concluded Claude Code was unsupported, passed
`--host chat`, and produced a **Copilot-Chat seed telling a Claude Code successor to press Cmd+N**.
It then hand-corrected the brief and deleted `chat-resume.md`. (`scope.md:26-28`.)

For an agent reading the interface, **a capability the interface denies is absent.** So the change
set is: make the docs tell the truth, make a named host that we cannot serve fail *honestly* instead
of guessing, fix the two argument-handling defects the critic and red team found on the way in, and
pin all of it with one new gate.

Three things this is **not**:

- Not a default flip. See §2.2 — D1 is reversed, measured to have had a zero-case benefit.
- Not a redesign of `handoff-spawn.sh`. The eager `seed="grok \"…"` at `:95`, the case-(a)
  grok-first fallback, and the `TERM_PROGRAM=vscode` carve-out are all **left exactly as they are**
  (§2.3, §3.9).
- Not a gate-expectation change. **No pinned gate's expectation moves.** Gates 213, 215 and 230 keep
  asserting what they assert today, and all three are green at HEAD:
  `bash scripts/audit-gates.sh --check 213|215|230` → `rc=0, rc=0, rc=0` (measured 2026-08-19).

---

## 2. Decision record

### 2.1 Surviving decisions

| # | Decision | Why | Where it lands |
|---|---|---|---|
| **DOC** | Every `--host` doc surface leads with `claude-code` and stops implying the list is `grok\|cli\|chat` | This is where the measured failure happened. Five surfaces: `handoff-spawn.sh:19`, `SKILL.md:23`+`:29`+`:40`, `bin/rc:51`, `commands/handoff.md:9`, `skills/session-handoff/templates/handoff.md:55` | §3.1–3.5 |
| **D2** (split, G5 owner ruling) | Registry-known-but-unmapped → **host-neutral, exit 0**. Neither-enum-nor-registry → **copy-paste block, then exit 2** | The hard error as first specified would have destroyed a **working** path for 5 of the 7 hosts the marketplace officially declares, and would have pressured an agent on an unlisted host toward `cli` — the exact wrong-vendor failure this run exists to fix | §3.7, §3.8 |
| **D3** | Fix the arity bug on all five value-taking flags | `--host` as the final argument: `shift 2` cannot shift, `$#` never decreases, **infinite loop**. Re-measured 2026-08-19: `EXIT=142 BYTES=0` under a 5 s `perl alarm`; control with a value `EXIT=0 BYTES=443` | §3.6 |
| **D4** | `RC_HOST` must be read **before** `THING_HOST` in `context-handoff.py:64` | `main()` writes the explicit `--host` into `RC_HOST`, so ambient adapter state outranked what the caller asked for. ⛔ Pinned as an **invariant**, not a live failure — see §2.5 | §3.11 |
| **ROW-21** | bash and python `normalize` agree on **every** input, both directions | Measured divergence today, 4 rows: `--host claude`/`claudecode` → bash Claude recipe / python host-neutral; `--host CLAUDE-CODE`/`GROK`/`Chat`/`CLI` → bash `unknown` / python resolves. The two write the seed for the **same** handoff (`handoff-spawn.sh:140-143`) | §3.7, §3.10 |
| **FLAG-AUTHORITY** | An explicit `--host` is the whole answer; `detect_origin_host()` no longer falls through to the environment when it does not recognise the name | Root cause of `claims-table` row 8: with `CLAUDECODE` set, `--host codex` printed a **Claude Code recipe**. Answering a named successor with a different agent's launch command is the defect this file exists to prevent | §3.7 (edit 6) |
| **MED-7** | A host named through `RC_HOST`/`THING_HOST` that we do not recognise must not inherit the grok fallback | Measured: `THING_HOST=gemini` + no flag → a live `grok "…"` launch. Every existing gate clears `THING_HOST`, so no gate can see this | §3.7 (edit 7), §4 row 15 |
| **D5** | Keep the `TERM_PROGRAM=vscode` ambiguity carve-out | G4b tiebreak, synthesis in B's favour. The red team then found it **load-bearing today**: `THING_HOST=cursor`+`CURSOR_TRACE_ID`+`TERM_PROGRAM=vscode` gets the safe comment, while the same shape without vscode gets grok. It is currently the only thing between a Cursor session and a grok launch | §3.9 — **no edit** |
| **GATE** | ONE new gate, **Gate 232** | Pins all of the above across **both** writers, with a named must-fail mutant per property | §4 |

### 2.2 DROPPED — D1 and everything downstream. Do not re-add any of these.

D1 said: *flip the no-host-detected fallback from `grok` to `claude-code`.* **Reversed at G4a on
measurement.** Claude Code resolves at `handoff-spawn.sh:144-147` by **detection** and never reaches
the default at all; the default's documented population is Grok, the one host that cannot be reliably
detected (`handoff-spawn.sh:73-79`, `SKILL.md:22`). D1's benefit for Claude Code was **zero cases**;
its cost was three edited gates plus removing the fallback from the only host it protected.

⛔ **Delete-list. Each of these existed ONLY to serve D1. If you find one in a diff, it is a
re-import, not a refinement:**

| Dropped element | Origin | Why it dies with D1 |
|---|---|---|
| The `host_source ∈ {flag, env, detected, default}` label threaded through both scripts | plan-A A2/A5, gap-delta row 5 | Its whole job was to mark a **defaulted** `claude-code` as a guess. With the default still `grok`, nothing is guessed into a named host. The surviving cases need one bit, not four values, and `named_but_unknown` **is** that bit — see §2.3 |
| The `host_source` caveat line in the copy-paste block | plan-A A2 | Same. Also: it would have added prose to the block that Gate 213/215/230 read by substring |
| Gate 215 expectation edit (`"unset host still grok"`) | plan-A §2.2 | The expectation is correct and unchanged |
| Gate 213 expectation edit + the `GROK_AGENT=1` mutant-harness patch | plan-A §2.2, gap-delta row 2 | Only needed because a flipped default would have made the bare-env mutant resolve to `claude-code` before reaching the mutated grok arm. Verified 2026-08-19: Gate 213's mutant invocation passes **no** `--host` and clears all markers via `_HOST_ENV_CLEAR`, so it still lands on the eager grok default and the teeth still bite |
| Gate 230 case-(a) row edit | plan-A §2.2 | `spawn_out ''` must still assert grok. Unchanged |
| CHANGELOG framing about a default flip | both plans | §7 gives the real 0.284.0 entry shape |
| plan-A S9 — deleting the `TERM_PROGRAM=vscode` seed override | plan-A S9 | Reversed by the D5 tiebreak *and* independently by the red team's Cursor measurement |
| plan-A S5 — deleting the eager `seed="grok \"…"` at `:95` | plan-A S5, gap-delta row 7 | See §2.3 — **leave it alone** |
| plan-A P6 — threading the resolved host into `stamp_meta()` | plan-A P6, gap-delta row 4 | See §2.3 — **made unnecessary by D4** |
| plan-A S4's **ordering** (validate before `detect_origin_host()` and before the handoff-file check) | plan-A S4 | Structurally incompatible with AC-2. See §2.4 row 8 |

### 2.3 Three places where the honest answer is "leave it alone"

1. **The eager `seed="grok \"Continue task ${task_id}…"` at `handoff-spawn.sh:95`** — plan-A called
   it "the structural cause" and proposed deleting it (S5). It is not vestigial: it **is** the
   case-(a) mechanism. When nothing is named and nothing is detected, no branch in the `:211-225`
   chain fires and `$seed` retains this value — which is exactly the grok-first fallback Gate 215
   pins. Deleting it means adding an explicit case-(a) branch to reproduce the same behaviour, for
   no functional gain, on a line that carries **Gate 213's only mutant anchor**
   (`test-gate213-handoff-spawn.sh:117`). plan-A's underlying observation is real — a future host
   branch that forgets to set `$seed` inherits grok silently — but that is a hardening for a
   different PR. **Not in this change set.** Recorded as follow-up F-2 (§9).

2. **`stamp_meta()`'s independent `detect_host()` call** (`context-handoff.py:252`) — gap-delta row 4
   flagged that it ignores `--host` and would write the wrong `last_handoff_host`. **The D4 fix makes
   this correct for free.** `main()` sets `os.environ["RC_HOST"] = args.host` at `:313-314` *before*
   `cmd_write()` runs; once `detect_host()` reads `RC_HOST` first, every call site inside the write
   path — `_ensure_run_dir():108`, `cmd_write():275`, `stamp_meta():252` — sees the flag. Threading a
   parameter through would be a second mechanism for a fact one mechanism already carries.
   **No edit.** Gate 232 row 20 asserts `meta.json.last_handoff_host` matches the flag, so the claim
   is measured rather than argued.

3. **The `TERM_PROGRAM=vscode` seed override at `:207-209`** (D5). No edit. The red team's Cursor
   measurement is in the risk table (§6 R-7).

### 2.4 Every A-vs-B divergence, resolved

`gap-delta.md` enumerates 16. All 16 are settled here; none is left open.

| Row | Subject | Resolution |
|---|---|---|
| 1 | Bump target | **A.** `0.284.0`. Re-verified: worktree `plugin.json` = `0.283.0`, marketplace catalog = `0.283.0`. B read the stale primary checkout |
| 2 | Gate 213 exists (A found it, B missed it) | **Moot under D1's reversal** — no gate expectation changes at all. Gate 213 is still **run** (base + `--must-fail-headless`) as a phase acceptance test (§5 P4) |
| 3 | python lacks bash's `claude`/`claudecode` aliases | **A.** Adopted as ROW-21, §3.10 edit P1. It is a **prerequisite**, not an afterthought |
| 4 | `stamp_meta()` second `detect_host()` | **Superseded.** D4 fixes it; no parameter threading — §2.3 item 2 |
| 5 | `host_source` label | **DROPPED with D1** — §2.2. The surviving cases need one bit and `named_but_unknown` already is it |
| 6 | Delete the vscode carve-out? | **B / D5.** Keep it. Tiebreak verdict + red-team measurement |
| 7 | Delete the eager grok pre-assignment? | **Neither, this PR.** §2.3 item 1; follow-up F-2 |
| 8 | Where D2 validates | **Against A.** AC-2 is binding and A's early ordering cannot satisfy it — `copy_paste_block` needs `$host`, `$seed` and `$project_root`, none of which exist that early. Validation moves **late**, immediately after `copy_paste_block()`'s definition. A's testability argument is real but costs one `mkdir -p` + `printf` in the fixture, which the gate harness already does |
| 9 | Third doc surface: `skills/session-handoff/templates/handoff.md:55` | **A.** Adopted, §3.5, including A's principle: state the **invariant** ("a non-Grok successor must never be handed a `grok` launch command"), do not re-enumerate hosts — re-enumeration is how the list went stale in the first place |
| 10 | Byte-identical regression floor for the grok/cli/chat seeds | **A's strength, simpler mechanism.** A proposed capturing seeds from `origin/main` and diffing; that needs `git` inside a gate that runs children under `env -i`. Gate 232 pins the three seeds as **exact literal strings** instead — same byte-exactness, no git dependency (§4 rows 21-23) |
| 11 | Gate number = 232 | **Converged, A's method.** Verified against the thing CI actually reads: `audit-gates.sh:1289` `Supported:` string ends at `231`; `ls hooks/tests/` highest is `test-gate231-*`. 232 is free |
| 12 | Five-element rule for a changed gate expectation | **Moot** — no expectation changes. Retained as the comment standard for Gate 232's own header (§4) |
| 13 | `RC_HOST`/`THING_HOST` non-fatal on an unrecognised value | **Converged (both plans) — and now refined.** D2's hard error stays scoped to the `--host` flag. But an env-named **unknown** host must still not inherit grok: MED-7, §3.7 edit 7. Loud path fatal, silent path neutral — never the reverse |
| 14 | Shared `handoff-hosts.json` SSOT vs duplicated tables | **A.** Duplicate the table as a bash literal (the script runs under `env -i PATH=/usr/bin:/bin`, so it may not shell out to `python3`/`jq`), and add a **behavioural parity assertion** (Gate 232 row 19) so it cannot drift silently. In-repo precedent: `_read_heimdall` / `_read_mimir` |
| 15 | Commit-boundary discipline | **A.** `handoff-spawn.sh` + `context-handoff.py` land in **one commit** (§5) |
| 16 | B's disproof that a real Claude-Code-in-VS-Code session never reaches the vscode-ambiguity branch | **Keep B's finding.** Recorded in §6 R-7 so nobody re-derives it |

### 2.5 One correction the build must carry into the code

The red team **corrected the critic brief** on D4. The critic wrote *"Four live adapters
(cursor/gemini/codex/copilot) export `THING_HOST`… Under D2 this would make a valid
`--host claude-code` exit 2 on Codex."* The red team could not reach that path: `THING_HOST` is
exported only **inside hook processes**, no hook invokes `context-handoff.py`, `handoff-nudge.py`
contains zero spawn references, and `bin/rc` sets neither variable. `RC_HOST` is written in exactly
one place — `context-handoff.py:314`, by `--host` itself.

**So: fix D4, and say in the test's own comment that it pins an invariant with no measured live
trigger.** Do not sell it as pinning a measured failure — the next reader would inherit a false
premise about how often it fires.

---

## 3. File-by-file change list

Ten edits across five files, plus one new file and three `audit-gates.sh` registrations.
All paths are relative to the worktree root.

> ⛔ **Substrate note for the builder.** `plugins/ravenclaude-core/{hooks,scripts}/` is Bash-denied by
> the tribunal's substrate guard even for read-only commands; `Read`/`Edit`/`Write` pass. Make every
> edit in this section with `Edit`/`Write`, never with `sed -i` or a heredoc. Verification commands
> that *run* the scripts are fine (they invoke, they do not write).

### 3.1 `plugins/ravenclaude-core/scripts/handoff-spawn.sh:17-21` — usage string

**Before**

```
usage() {
  cat >&2 <<'EOF'
Usage: handoff-spawn.sh --task-id <id> [--dry-run] [--host grok|cli|chat] [--recipe copy-paste|same-host|os-terminal] [--project-root DIR] [--wait-ack-seconds N]
EOF
}
```

**After**

```
usage() {
  cat >&2 <<'EOF'
Usage: handoff-spawn.sh --task-id <id> [--dry-run] [--host HOST] [--recipe copy-paste|same-host|os-terminal] [--project-root DIR] [--wait-ack-seconds N]

  --host  claude-code | grok | cli (Copilot CLI) | chat (Copilot Chat)
            -> that host's own launch recipe.
          codex | cursor | gemini | aider | windsurf   (knowledge/host-support.json)
          other | generic
            -> host-neutral copy-paste block, exit 0. No launch command is invented.
          anything else
            -> the copy-paste block, then exit 2. Pass `other`, never a host you are not.
EOF
}
```

### 3.2 `plugins/ravenclaude-core/skills/session-handoff/SKILL.md` — three lines

**`:23`, before**

```
- **Never infer Chat from `TERM_PROGRAM=vscode` alone.** That is also Grok-in-VS-Code. Pass `--host grok|cli|chat` from what you actually are.
```

**`:23`, after**

```
- **Never infer Chat from `TERM_PROGRAM=vscode` alone.** That is also Grok-in-VS-Code. Pass `--host` from what you actually are: `claude-code` | `grok` | `cli` | `chat` each have their own recipe; `codex` | `cursor` | `gemini` | `aider` | `windsurf` | `other` get a host-neutral block. ⛔ **Never substitute a host you are not.** An agent that read an older, shorter list here passed `--host chat` from a Claude Code session and produced a Copilot-Chat seed for a Claude Code successor (2026-08-18).
```

**`:29`, before**

```
2. Resolve **origin host** (you are Chat / Grok TUI / Copilot CLI — do not guess from `TERM_PROGRAM=vscode` alone) → `grok` | `cli` | `chat`.
```

**`:29`, after**

```
2. Resolve **origin host** (you are Claude Code / Grok TUI / Copilot CLI / Copilot Chat — do not guess from `TERM_PROGRAM=vscode` alone) → `claude-code` | `grok` | `cli` | `chat`. On any other host, pass its `host-support.json` name (`codex` | `cursor` | `gemini` | `aider` | `windsurf`) or `other`; you will get a host-neutral block, which is correct.
```

**`:40`, before**

```
- Other-host adapters beyond Grok / Copilot CLI / Copilot Chat.
```

**`:40`, after**

```
- A per-host **launch recipe** beyond Claude Code / Grok / Copilot CLI / Copilot Chat. The other `host-support.json` hosts are accepted and answered host-neutrally; inventing a launch command for them is what is out of scope.
```

⛔ `:3` (the frontmatter `description`) also reads *"Grok TUI, Copilot Chat new session, or Copilot
CLI"*. Add Claude Code: `"— Claude Code, Grok TUI, Copilot Chat new session, or Copilot CLI."`
Keep it under the description budget (it is a skill, not an agent, so the 300-char agent cap does not
bind — but `scripts/check-frontmatter.py` runs over `agents/*.md` only; verify with
`bash scripts/audit-gates.sh --check 226` and the full suite regardless).

### 3.3 `plugins/ravenclaude-core/bin/rc:51-52`

**Before**

```
  rc handoff --task-id <id> [--dry-run] [--host grok|cli|chat]
                                        [--recipe copy-paste|same-host|os-terminal]
```

**After**

```
  rc handoff --task-id <id> [--dry-run] [--host claude-code|grok|cli|chat|other]
                                        [--recipe copy-paste|same-host|os-terminal]
```

> This is the **only** invocation path on Copilot and Codex — no slash command exists there
> (`claims-table` row 22). Keep it to one line; the full vocabulary lives in
> `handoff-spawn.sh --help`.

### 3.4 `plugins/ravenclaude-core/commands/handoff.md:9`

**Before**

```
Optional `$ARGUMENTS` is the `task-id`. If empty, resolve per the skill (most-recent run dir, else propose a slug). Resolve the originating host (`grok` / `cli` / `chat`) and pass `--host`. Then write the handoff and call `rc handoff --task-id <id> --host <pair>`. Do not hard-code grok.
```

**After**

```
Optional `$ARGUMENTS` is the `task-id`. If empty, resolve per the skill (most-recent run dir, else propose a slug). Resolve the originating host — `claude-code` / `grok` / `cli` / `chat`, or its `host-support.json` name, or `other` — and pass it. Then write the handoff and call `rc handoff --task-id <id> --host <host>`. ⛔ Always quote the value (`--host "$HOST"`) and never pass `--host` with nothing after it. Do not hard-code grok. Do not substitute a host you are not.
```

⛔ **This line is the one an agent literally executes, and it is where the arity bug is reachable.**
It documented `--host` **last**; with an unquoted empty value the flag becomes the final argument.
Measured 2026-08-19 through `bin/rc`: `EXIT=142 BYTES=0` at a 5 s alarm.

### 3.5 `plugins/ravenclaude-core/skills/session-handoff/templates/handoff.md:55`

**Before**

```
… A Chat or CLI successor must not launch `grok`. …
```

**After**

```
… A non-Grok successor must never be handed a `grok` launch command — that includes Claude Code, Copilot Chat, Copilot CLI, and every host in `knowledge/host-support.json`. …
```

State the invariant, do not re-enumerate. Re-enumeration is how the list went stale.

### 3.6 `handoff-spawn.sh:23-41` — D3, the arity fix (AC-3, MED-8)

**Before** (`:23-41`)

```bash
task_id=""
dry_run=0
recipe="copy-paste"
project_root=""
wait_ack=45
host_flag=""

while [ $# -gt 0 ]; do
  case "$1" in
    --task-id) task_id="${2:-}"; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    --host) host_flag="${2:-}"; shift 2 ;;
    --recipe) recipe="${2:-}"; shift 2 ;;
    --project-root) project_root="${2:-}"; shift 2 ;;
    --wait-ack-seconds) wait_ack="${2:-45}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "handoff-spawn: unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done
```

**After**

```bash
task_id=""
dry_run=0
recipe="copy-paste"
project_root=""
wait_ack=45
host_flag=""
host_flag_seen=0
host_flag_bad=0

# ⛔ `shift 2` WHEN THE FLAG IS THE LAST ARGUMENT DOES NOT SHIFT AT ALL.
# bash reports "shift count out of range" and returns non-zero; $# never
# decreases and this loop spins forever at 100% CPU. Measured 2026-08-19 through
# the DOCUMENTED shape (`rc handoff … --host $H` with H empty, per
# commands/handoff.md): 0 bytes emitted, still running at 5 s, killed by SIGALRM
# (exit 142). Control, same command with a value: exit 0, 443 bytes. Every
# value-taking flag now shifts ONCE, then again only if an argument remains.
#
# A value that is missing, empty, or itself a `--flag` is a CALLER ERROR, not a
# value. For --host it is RECORDED here and rejected later (see the D2 block,
# after copy_paste_block is defined) so the file-header invariant "Copy-paste is
# ALWAYS printed" survives. For the other four it is fatal here, matching the two
# argument errors that already exit 2 without a block: the `unknown arg` arm
# below and the --task-id check.
#
# ⛔ Do NOT "uniformise" --wait-ack-seconds to `${2:-}`. Its default of 45 is
# load-bearing: `[ "$wait_ack" -gt 0 ] 2>/dev/null` is false on an empty string,
# which SILENTLY skips the successor-ack wait — the handshake dies with no error.
while [ $# -gt 0 ]; do
  case "$1" in
    --task-id)
      case "${2:-}" in
        ""|--*) echo "handoff-spawn: --task-id requires a value" >&2; usage; exit 2 ;;
        *) task_id="$2" ;;
      esac
      shift; if [ $# -gt 0 ]; then shift; fi ;;
    --dry-run) dry_run=1; shift ;;
    --host)
      host_flag_seen=1
      case "${2:-}" in
        ""|--*) host_flag_bad=1 ;;
        *) host_flag="$2" ;;
      esac
      shift
      if [ "$host_flag_bad" -eq 0 ] && [ $# -gt 0 ]; then shift; fi ;;
    --recipe)
      case "${2:-}" in
        ""|--*) echo "handoff-spawn: --recipe requires a value" >&2; usage; exit 2 ;;
        *) recipe="$2" ;;
      esac
      shift; if [ $# -gt 0 ]; then shift; fi ;;
    --project-root)
      case "${2:-}" in
        ""|--*) echo "handoff-spawn: --project-root requires a value" >&2; usage; exit 2 ;;
        *) project_root="$2" ;;
      esac
      shift; if [ $# -gt 0 ]; then shift; fi ;;
    --wait-ack-seconds)
      case "${2:-}" in
        ""|--*) echo "handoff-spawn: --wait-ack-seconds requires a value" >&2; usage; exit 2 ;;
        *) wait_ack="$2" ;;
      esac
      shift; if [ $# -gt 0 ]; then shift; fi ;;
    -h|--help) usage; exit 0 ;;
    *) echo "handoff-spawn: unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done
```

Three details the builder must not smooth over:

- **`--host` does not consume a `--*` next token** (`host_flag_bad` guard on the second shift). That
  is MED-8: today `--host --dry-run` swallows `--dry-run`, and with `--recipe same-host` + an owner
  spawn flag set, a caller who asked for a dry run gets a **live launch**.
- `set -uo pipefail` is in force and **`set -e` is not** (`:15`), so `if [ $# -gt 0 ]; then shift; fi`
  is safe. Do not "simplify" it to `[ $# -gt 0 ] && shift` — that leaves the case arm with exit
  status 1, which is harmless today and a trap for whoever adds `set -e`.
- **Do not add `--host=value` (equals-form) support.** It is already a loud error
  (`handoff-spawn: unknown arg: --host=claude-code`, exit 2) via the `*)` catch-all, the naive fix
  does not touch it, and adding it for one flag makes the interface inconsistent per-flag. Recorded
  as follow-up F-3.

### 3.7 `handoff-spawn.sh:104-150, 201-204` — normalization, classification, flag authority

**Edit 4 — `:104-113`, case + whitespace parity (ROW-21, direction "bash is stricter")**

**Before**

```bash
normalize_host() {
  case "$1" in
    grok|grok-tui) echo grok ;;
    cli|copilot-cli|copilot) echo cli ;;
    chat|copilot-chat) echo chat ;;
    claude-code|claude|claudecode) echo claude-code ;;
    "") echo "" ;;
    *) echo unknown ;;
  esac
}
```

**After**

```bash
_lc() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//'
}

# ⛔ CASE AND SURROUNDING WHITESPACE ARE NORMALISED HERE BECAUSE
# context-handoff.py's _normalize_handoff_host ALREADY DOES `.strip().lower()`,
# and the two write the seed for the SAME handoff (see detect_origin_host below).
# Measured 2026-08-19 before this change:
#   --host GROK        -> bash `unknown`  / python a LIVE `grok "…"` seed
#   --host CLAUDE-CODE -> bash `unknown`  / python the claude recipe
#   --host Chat / CLI  -> bash `unknown`  / python the correct chat / cli seed
# bash was the stricter half, so the pair named different successors on four
# inputs. `${var,,}` is bash 4.0+; this file is bash 3.2-safe, hence tr.
normalize_host() {
  local h
  h="$(_lc "$1")"
  case "$h" in
    grok|grok-tui) echo grok ;;
    cli|copilot-cli|copilot) echo cli ;;
    chat|copilot-chat) echo chat ;;
    claude-code|claude|claudecode) echo claude-code ;;
    "") echo "" ;;
    *) echo unknown ;;
  esac
}

# The seven hosts the marketplace officially declares in
# knowledge/host-support.json. Duplicated as a literal ON PURPOSE: Gate 230 and
# Gate 232 drive this script under `env -i PATH=/usr/bin:/bin`, so it may not
# shell out to python3/jq to read the JSON. Gate 232 asserts this list and the
# JSON agree, so the duplication cannot drift silently. Same pattern as
# _read_heimdall / _read_mimir elsewhere in this plugin.
is_registry_host() {
  case "$(_lc "$1")" in
    claude-code|copilot|codex|cursor|gemini|aider|windsurf) return 0 ;;
    *) return 1 ;;
  esac
}

# ⛔ D2, owner ruling 2026-08-19. Three classes, not two:
#   recipe  — we have a launch command for it.
#   neutral — a host this marketplace officially supports, or an explicit
#             `other`, for which we have NO launch command. Host-neutral
#             copy-paste, exit 0. Measured as the WORKING behaviour before this
#             change (`--host codex` exits 0 with the neutral block) and
#             deliberately retained: hard-erroring here would destroy a working
#             handoff for five supported hosts AND pressure an agent on an
#             unlisted host into picking the nearest recognised token — almost
#             certainly `cli` — which is the wrong-vendor failure this file
#             exists to prevent.
#   reject  — a name in neither vocabulary. A typo. The copy-paste block is
#             printed and then this exits 2.
classify_host_flag() {
  local n
  n="$(normalize_host "$1")"
  if [ -n "$n" ] && [ "$n" != "unknown" ]; then echo recipe; return; fi
  case "$(_lc "$1")" in
    other|generic) echo neutral; return ;;
  esac
  if is_registry_host "$1"; then echo neutral; return; fi
  echo reject
}
```

⛔ **The line `    claude-code|claude|claudecode) echo claude-code ;;` must stay byte-identical.**
It is Gate 230's mutant anchor #1 (`test-gate227-handoff-seed-host.sh:90`). Lowercasing into `$h`
before the `case` is what lets the anchor survive.

**Edit 6 — `:115-121`, flag authority**

**Before**

```bash
detect_origin_host() {
  local from
  from="$(normalize_host "$host_flag")"
  if [ -n "$from" ] && [ "$from" != "unknown" ]; then
    echo "$from"
    return
  fi
  from="$(normalize_host "${RC_HOST:-}")"
```

**After**

```bash
detect_origin_host() {
  local from
  # ⛔ AN EXPLICIT --host IS THE WHOLE ANSWER, INCLUDING WHEN WE DO NOT KNOW THE
  # NAME. This used to fall THROUGH to environment detection whenever the flag
  # did not normalise to a recipe host, so with CLAUDECODE set `--host codex`
  # printed a CLAUDE CODE recipe (measured 2026-08-18, claims-table row 8) and
  # `--host <typo>` printed whatever the ambient session happened to be. That
  # fall-through is the mechanism behind the whole defect class this file
  # documents at the top: the caller told us who the successor is, and we
  # answered with a different agent's launch command. Control that the flag is
  # still honoured, not merely disabled: `--host cli` under the same env still
  # emits the Copilot CLI recipe.
  if [ "$host_flag_seen" -eq 1 ]; then
    from="$(normalize_host "$host_flag")"
    if [ -n "$from" ] && [ "$from" != "unknown" ]; then
      echo "$from"
    else
      echo unknown
    fi
    return
  fi
  from="$(normalize_host "${RC_HOST:-}")"
```

The rest of `detect_origin_host` (`:122-150`) is **unchanged**, including
`  if [ -n "${CLAUDECODE:-}" ] || [ -n "${CLAUDE_CODE_ENTRYPOINT:-}" ]; then` — Gate 230's mutant
anchor #2. Insert above it; do not touch it.

**Edit 7 — `:198-204`, `named_but_unknown` widened (D3 empty value + D2 neutral/reject + MED-7)**

**Before**

```bash
named_but_unknown=0
if [ -n "$host_flag" ] && [ "$host" = "unknown" ]; then
  named_but_unknown=1
fi
```

**After**

```bash
# One bit, three sources. It is set when a successor WAS named and we cannot
# name a launch command for it:
#   (i)   --host <registry host | other | typo>            -> host_flag_seen
#   (ii)  --host with a missing / empty / --flag value     -> host_flag_seen
#   (iii) RC_HOST / THING_HOST naming a host we do not know
#
# (iii) is new and was measured 2026-08-19: `THING_HOST=gemini` with no flag
# emitted a LIVE `grok "…"` launch for a session that had named itself gemini,
# because this test keyed on $host_flag only. Every existing gate clears
# THING_HOST (`-u THING_HOST`, or `env -i`), which is correct hygiene for the
# flag rows and is exactly why no gate could see it. Gate 232 row 15 drives it,
# with a THING_HOST=grok control on row 16 proving grok still keeps its own seed.
named_but_unknown=0
if [ "$host" = "unknown" ] && { [ "$host_flag_seen" -eq 1 ] || [ -n "${RC_HOST:-}" ] || [ -n "${THING_HOST:-}" ]; }; then
  named_but_unknown=1
fi
```

⛔ `elif [ "$named_but_unknown" -eq 1 ]; then` at `:220` and the refusal guard at `:239` are Gate
230's anchors #4 and #5. **Neither line changes.** The edit is to the *assignment* at `:202`, not to
either consumer.

### 3.8 `handoff-spawn.sh` — the D2 rejection block (AC-1, AC-2, AC-3)

**Insert immediately after the closing `}` of `copy_paste_block()` at `:282`, before
`spawn_flag=""` at `:284`.**

```bash
# ⛔ D2 — REFUSE A NAME WE DO NOT KNOW; NEVER REFUSE A HOST WE SUPPORT.
#
# Owner ruling 2026-08-19 (G5): a host declared in knowledge/host-support.json
# but with no launch recipe here — codex / cursor / gemini / aider / windsurf —
# resolves to the HOST-NEUTRAL block and exits 0. That was measured as the
# working behaviour BEFORE this change and is deliberately retained. Only a name
# in neither vocabulary is fatal, and `other` is always available as a truthful
# value for a host that is in neither.
#
# ⛔ WHY THE BLOCK IS PRINTED BEFORE THE EXIT, AND WHY THIS SITS HERE AND NOT UP
# BY THE ARGUMENT LOOP. The file header states "Copy-paste is ALWAYS printed",
# and both existing fatal branches below (unknown --recipe, unflagged same-host)
# call copy_paste_block and THEN exit 2. Validating up beside the argument loop
# reads cleaner and is what the first draft specified — it cannot print the
# block, because the block needs $host, $seed and $project_root, none of which
# exist that early. The invariant wins: a user at a full context window who
# mistypes a host name must still get something to paste.
#
# $seed is host-neutral text on both paths below, because named_but_unknown is 1
# in both — see its assignment above. That is what stops a malformed --host from
# falling to case (a) and printing a grok launch.
if [ "$host_flag_bad" -eq 1 ]; then
  echo "handoff-spawn: --host requires a value. Pass claude-code | grok | cli | chat | a host-support.json name | other." >&2
  copy_paste_block
  exit 2
fi
if [ "$host_flag_seen" -eq 1 ] && [ "$(classify_host_flag "$host_flag")" = "reject" ]; then
  echo "handoff-spawn: unrecognised --host '$host_flag'. Use claude-code | grok | cli | chat, a host from knowledge/host-support.json (codex|cursor|gemini|aider|windsurf), or 'other' for a host-neutral handoff. Do NOT substitute a host you are not." >&2
  copy_paste_block
  exit 2
fi
```

Exact behaviour table for this block (all eight verified against the design in §4):

| `--host` | `classify_host_flag` | `$host` | exit | printed |
|---|---|---|---|---|
| `claude-code` / `claude` / `CLAUDE-CODE` | recipe | `claude-code` | 0 | Claude Code recipe |
| `grok` / `GROK` | recipe | `grok` | 0 | grok launch |
| `cli` / `CLI` / `copilot` | recipe | `cli` | 0 | Copilot CLI recipe |
| `chat` / `Chat` | recipe | `chat` | 0 | Chat recipe |
| `codex` `cursor` `gemini` `aider` `windsurf` | neutral | `unknown` | **0** | host-neutral block |
| `other` / `generic` | neutral | `unknown` | **0** | host-neutral block |
| `codxe` (typo) | reject | `unknown` | **2** | host-neutral block, **then** exit |
| missing / empty / `--dry-run` | — (`host_flag_bad`) | `unknown` | **2** | host-neutral block, **then** exit |

### 3.9 `handoff-spawn.sh:206-209` — D5, no edit

```bash
# vscode without a Grok/CLI marker is not Chat and is not a grok TUI we can prove.
if [ "$host" = "unknown" ] && [ "${TERM_PROGRAM:-}" = "vscode" ]; then
  seed="# host=unknown (TERM_PROGRAM=vscode without Grok/CLI markers) — copy-paste only. Do not launch grok. Do not infer Chat."
fi
```

**Unchanged.** G4b tiebreak. It is load-bearing today: the red team measured that
`THING_HOST=cursor` + `CURSOR_TRACE_ID` + `TERM_PROGRAM=vscode` gets this safe comment while the same
`THING_HOST` shape *without* vscode got a grok launch. (After edit 7, MED-7 closes the second half of
that asymmetry, and the carve-out keeps covering the case where nothing named anything at all.)

### 3.10 `context-handoff.py:52-60` — ROW-21, python side

**Before**

```python
def _normalize_handoff_host(raw: str) -> str:
    val = (raw or "").strip().lower()
    if val in ("grok", "grok-tui"):
        return "grok"
    if val in ("cli", "copilot-cli", "copilot"):
        return "cli"
    if val in ("chat", "copilot-chat"):
        return "chat"
    return val
```

**After**

```python
def _normalize_handoff_host(raw: str) -> str:
    val = (raw or "").strip().lower()
    if val in ("grok", "grok-tui"):
        return "grok"
    if val in ("cli", "copilot-cli", "copilot"):
        return "cli"
    if val in ("chat", "copilot-chat"):
        return "chat"
    # ⛔ PARITY WITH handoff-spawn.sh's normalize_host(). Without this row the two
    # writers named DIFFERENT successors for the SAME handoff: measured
    # 2026-08-19, `--host claude` gave bash the Claude Code recipe and python
    # host-neutral text, because "claude" fell through here as a raw string.
    # handoff-spawn.sh:140-143 states the contract these two are keeping.
    if val in ("claude-code", "claude", "claudecode"):
        return "claude-code"
    return val
```

Case parity needs **no** python edit — `.strip().lower()` was already the lenient half; edit 4 brings
bash up to it.

**No D2 hard error is added to python.** Stated as a decision, not an omission:

> `context-handoff.py write` is the **brief writer**. Refusing to write `handoff.md` because the
> successor's name is misspelled destroys the artifact that matters most — losing the brief is worse
> than an imperfect seed. The pair-in-step contract at `handoff-spawn.sh:140-143` is about **who the
> successor is**, and on an unrecognised name both writers already agree the answer is *host-neutral*.
> Only the **exit code** differs, and only bash gates the spawn. Gate 232 therefore asserts
> agreement on the **resolved host and seed class** for every row, with the bash exit code as its own
> column. The red team reached the same conclusion independently (HIGH-4 mitigation, preferred form).

### 3.11 `context-handoff.py:63-66` — D4, precedence

**Before**

```python
def detect_host() -> str:
    explicit = os.environ.get("THING_HOST") or os.environ.get("RC_HOST")
```

**After**

```python
def detect_host() -> str:
    # ⛔ RC_HOST BEFORE THING_HOST. main() writes the explicit `--host` flag into
    # RC_HOST (see main()), so reading THING_HOST first let ambient adapter state
    # outrank what the caller actually asked for: THING_HOST=copilot with
    # --host claude-code made this write a `copilot` seed while handoff-spawn.sh
    # emitted the Claude Code recipe, for one handoff.
    #
    # ⛔ THIS PINS AN INVARIANT, NOT A MEASURED LIVE FAILURE. The red team could
    # not reach it from any shipped caller: THING_HOST is exported only inside
    # hook processes (four adapters), no hook invokes this script, bin/rc sets
    # neither variable, and RC_HOST is written in exactly one place — main(),
    # by --host itself. An explicit flag outranking ambient environment is right
    # regardless of how often it fires; do not re-tell this as a live incident.
    explicit = os.environ.get("RC_HOST") or os.environ.get("THING_HOST")
```

Consequence worth stating so nobody adds a second mechanism: this single swap also fixes
`_ensure_run_dir():108`, `cmd_write():275` and `stamp_meta():252`, all of which call `detect_host()`
independently. See §2.3 item 2.

### 3.12 `scripts/audit-gates.sh` — three registrations

⛔ The file's own rule, stated at `:8303-8305`: *"Registered in BOTH this main sequence AND the
`--check` dispatcher above + the `Supported:` string. After adding a gate, run the full suite and
GREP ITS OUTPUT FOR the SCRIPT NAME on an executed line."* Do all three or the gate is one of the 39
that no workflow invokes.

**(a) `--check` dispatcher — insert a new arm immediately after the `231)` arm (ends `:586`):**

```bash
    232)
      echo "── Gate 232: handoff --host contract — both writers, one vocabulary ──"
      rc=0
      bash plugins/ravenclaude-core/hooks/tests/test-gate232-handoff-host-contract.sh || rc=$?
      for mf in --must-fail-arity --must-fail-d2 --must-fail-registry \
                --must-fail-parity --must-fail-precedence --must-fail-flagauthority; do
        bash plugins/ravenclaude-core/hooks/tests/test-gate232-handoff-host-contract.sh "$mf" || rc=$?
      done
      exit $rc
      ;;
```

**(b) `Supported:` string at `:1289`** — change the tail `…, 229, 230, 231. Run without --check…`
to `…, 229, 230, 231, 232. Run without --check…`.

**(c) Main sequence — insert after the Gate 230 block (ends `:8312`), before the
`── Gate 231:` header at `:8313`:**

```bash
echo "── Gate 232: handoff --host contract — both writers, one vocabulary ───────"
# Registry hosts resolve host-neutral and exit 0; a name in neither vocabulary
# prints the copy-paste block and THEN exits 2; --host with no value exits 2 and
# never falls to the grok fallback; bash and python agree on every row.
# ⛔ Registered in BOTH this main sequence AND the --check dispatcher above +
# the Supported: string.
rc=0
bash plugins/ravenclaude-core/hooks/tests/test-gate232-handoff-host-contract.sh >/dev/null 2>&1 || rc=$?
gate "handoff --host: registry hosts neutral, typos fatal, writers agree" must_pass "$rc"
for mf in --must-fail-arity --must-fail-d2 --must-fail-registry \
          --must-fail-parity --must-fail-precedence --must-fail-flagauthority; do
  rc=0
  bash plugins/ravenclaude-core/hooks/tests/test-gate232-handoff-host-contract.sh "$mf" >/dev/null 2>&1 || rc=$?
  gate "handoff --host teeth: ${mf#--must-fail-} mutant IS caught" must_pass "$rc"
done
```

⛔ `must_pass`, not `must_fail` — following **Gate 230's** convention (`:8310-8312`), where the test
file itself returns **0** when the mutant was caught. Gates 213/215 use the opposite convention;
copying the wrong one is a silent inversion.

### 3.13 No layout change needed

`.repo-layout.json` `allowed_globs` already contains `plugins/*/hooks/**`, which covers
`plugins/ravenclaude-core/hooks/tests/test-gate232-handoff-host-contract.sh`. Verified 2026-08-19.
Do **not** add a glob.

---

## 4. The new gate — Gate 232

**File:** `plugins/ravenclaude-core/hooks/tests/test-gate232-handoff-host-contract.sh`
**Shape:** modelled on `test-gate227-handoff-seed-host.sh` (Gate 230) — same `ok`/`no` counters, same
`env -i` child environment, same `pass=/fail=` verdict, same must-fail-half return convention.

### 4.0 Header requirements (the five-element rule, gap-delta row 12)

The header must carry, in prose: (1) what each row asserts and the date it was measured; (2) the
owner ruling behind the D2 split, quoted; (3) what is deliberately **unchanged** (case (a), the vscode
carve-out, the three existing gates); (4) where else each property is pinned (Gates 213/215/230); and
(5) ⛔ **the D4 row must state that it pins an invariant with no measured live trigger** (§2.5).

Plus MED-6's acceptance criterion, verbatim in the header:

> ⛔ If a mutant anchor below stops matching, do not "fix" it by pasting the new source. Re-derive
> that the mutant reconstructs the **original defect** the row was written for, then confirm the
> must-fail half reports `fail > 0` **on that row**, not on an incidental one.

### 4.1 ⛔ AC-5 — the timeout preflight, before any assertion runs

```bash
. "$PLUGIN_ROOT/hooks/_portable.sh"   # _rc_timeout: timeout -> gtimeout -> perl alarm

# ⛔ NEVER BARE `timeout`. Measured on this host 2026-08-19:
#     command -v timeout   -> rc=1  ABSENT
#     command -v gtimeout  -> rc=1  ABSENT
#     command -v perl      -> /usr/bin/perl
# In the repo's usual shape `out="$(timeout 5 cmd)" || …`, an absent `timeout` is
# exit 127 — the command under test NEVER RUNS — and an "exits non-zero"
# assertion passes VACUOUSLY. Green on Linux CI, green-for-the-wrong-reason on
# macOS. That is why every bounded row below uses _rc_timeout.
#
# ⛔ AND _rc_timeout's LAST fallback is `"$@"` — UNBOUNDED. On a host with none
# of the three, the arity mutant would run the infinite loop to the GitHub
# Actions 6-hour job ceiling and block every PR in the repo, because
# audit-gates.sh wraps ZERO gate invocations in a timeout (13 `timeout` hits in
# that file, none of them wrapping a gate — control: the same grep finds them in
# prose, so the empty result is a real absence, not a broken probe).
# A skip is not a pass: loud-skip locally, HARD FAIL in CI.
if ! command -v timeout >/dev/null 2>&1 \
   && ! command -v gtimeout >/dev/null 2>&1 \
   && ! command -v perl >/dev/null 2>&1; then
  echo "Gate 232: NO WALL-CLOCK BOUND AVAILABLE (timeout/gtimeout/perl all absent)." >&2
  echo "  The arity rows execute a known infinite loop. THIS IS NOT A PASS." >&2
  if [ -n "${CI:-}" ]; then exit 1; fi
  exit 1
fi
```

(Both branches exit 1 — the local branch exists only to carry a different message. An unrunnable
Gate 232 is never a silent skip, matching Gate 10's actionlint precedent.)

### 4.2 Helpers

```bash
BOUND=10   # seconds. The measured hang emits 0 bytes and never terminates;
           # the fixed path returns in well under 1 s.

spawn_run() {   # $1=label-only; remaining args passed through. Echoes "EXIT<tab>BYTES<tab>OUT"
  local out rc
  out="$(_rc_timeout "$BOUND" env -i PATH=/usr/bin:/bin HOME="$HOME" \
          ${PRE:+$PRE} bash "$SPAWN" --task-id t1 --project-root "$REPO" --dry-run "$@" 2>&1)"
  rc=$?
  printf '%s\t%s\t%s' "$rc" "$(printf '%s' "$out" | wc -c | tr -d ' ')" "$out"
}
```

Seed-class recognisers — **every one of these is a presence test**, which is what AC-6 requires:

| class | bash marker | python marker |
|---|---|---|
| `grok` | `grok "` or `grok -p` | same |
| `claude` | `(Claude Code, not grok)` | `claude  # then:` |
| `cli` | `(Copilot CLI, not grok)` | `copilot  # then:` |
| `chat` | `Copilot Chat resume` | `NEW Copilot Chat session` |
| `neutral` | `NEW session of THIS host` | `Read the handoff at` |

⛔ Do **not** assert the bare substring `claude` on bash output: the copy-paste block prints
`cd <repo>`, and any checkout under `.claude/` satisfies it regardless of the seed. Gate 230's
comment at `:168-171` records that this exact false-pass was verified.

### 4.3 The row table — 23 rows, both writers (AC-4, AC-6)

Every row asserts **bash exit code**, **bash seed class (presence)**, and **python seed class
(presence)**. Rows marked ⊘ are bash-only (python's argparse handles the shape natively and exits 2 —
measured: `context-handoff.py write … --host` → `error: argument --host: expected one argument`).

| # | input | bash exit | bash class | py class | proves |
|---|---|---|---|---|---|
| 1 | `--host grok` | 0 | grok | grok | **POSITIVE CONTROL** — the harness can still observe a seed |
| 2 | `--host GROK` | 0 | grok | grok | case parity (was: bash `unknown`) |
| 3 | `--host claude-code` | 0 | claude | claude | the headline capability |
| 4 | `--host claude` | 0 | claude | claude | alias parity (was: py neutral) |
| 5 | `--host claudecode` | 0 | claude | claude | alias parity |
| 6 | `--host CLAUDE-CODE` | 0 | claude | claude | case parity (was: bash `unknown`) |
| 7 | `--host cli` | 0 | cli | cli | regression floor |
| 8 | `--host CLI` | 0 | cli | cli | case parity |
| 9 | `--host copilot` | 0 | cli | cli | alias, already agreed — keep as a control |
| 10 | `--host chat` | 0 | chat | chat | regression floor |
| 11 | `--host Chat` | 0 | chat | chat | case parity |
| 12 | `--host codex` | **0** | neutral | neutral | **AC-1** |
| 13 | `--host cursor` | **0** | neutral | neutral | AC-1 |
| 14 | `--host gemini` | **0** | neutral | neutral | AC-1 |
| 15 | `--host aider` | **0** | neutral | neutral | AC-1 |
| 16 | `--host windsurf` | **0** | neutral | neutral | AC-1 |
| 17 | `--host other` | 0 | neutral | neutral | the truthful value for an unlisted host |
| 18 | `--host codxe` (typo) | **2** | neutral | neutral | **D2 + AC-2** — assert the block was printed AND `BYTES>0` AND exit 2 |
| 19 | `--host codex` **with `CLAUDECODE=1`** | 0 | neutral, **not** claude | neutral | claim-8 regression: flag authority |
| 20 | no `--host`, empty env | 0 | grok | grok | **case (a) must not regress** (also pinned by Gates 215/230) |
| 21 | `PRE="THING_HOST=gemini"`, no flag | 0 | **neutral** | neutral | **MED-7 / AC-6** — was a live grok launch |
| 22 | `PRE="THING_HOST=grok"`, no flag | 0 | grok | grok | **AC-6 control** for row 21 |
| 23 | `PRE="THING_HOST=copilot"` **+** `--host claude-code` | 0 | claude | **claude** | **D4** — py must not write a copilot seed |

Bounded-arity rows (⊘ bash-only, each under `_rc_timeout $BOUND`):

| # | input | assert | proves |
|---|---|---|---|
| 24 | `--host` as the **final** argument | exit `2` **AND** `BYTES>0` **AND** class `neutral` **AND** no grok launch | **AC-3 + AC-5.** `BYTES>0` is what separates "refused fast, block printed" from the defect's measured signature `EXIT=142 BYTES=0`, and from a missing-`timeout` exit 127 |
| 25 | `--host ""` (explicit empty) | exit `2`, `BYTES>0`, class `neutral` | AC-3 — the naive shift fix turns the hang into a **silent grok seed** here |
| 26 | `--host --dry-run` | exit `2`, `BYTES>0`, class `neutral` | MED-8 — the flag is not swallowed |
| 27 | `--host claude-code` **in the same harness** | exit `0` **AND** `BYTES>0` | **AC-5 positive control.** Without it, a harness that cannot run the script at all scores a free green |
| 28 | `--task-id` as the final argument | exit `2`, terminates within the bound | the arity fix is not `--host`-only |
| 29 | `--recipe` / `--project-root` / `--wait-ack-seconds` as the final argument | exit `2` each, terminates | ditto |
| 30 | `--wait-ack-seconds` absent → default still `45` | grep the source for `wait_ack=45` **and** run `--wait-ack-seconds 1` to a successful exit | HIGH-2 second-order: a `${2:-}` "uniformisation" silently kills the successor-ack wait |

Structural rows:

| # | assertion | proves |
|---|---|---|
| 31 | `is_registry_host`'s literal list == `json.load(host-support.json)["hosts"].keys()`, as **sets** | the duplicated table cannot drift (gap-delta row 14). Runs in the gate process, which is not under `env -i`, so `python3` is available |
| 32 | The grok seed emitted on row 1 equals its pinned literal, **byte for byte** | gap-delta row 10 — a one-character change in an unrelated arm turns this red |
| 33 | Same for the `cli` and `chat` copy-paste blocks | the scope constraint "`grok\|cli\|chat` behaviour is unchanged", mechanised |
| 34 | `bash -n "$SPAWN"` and `python3 -m py_compile "$PY"` | syntax floor, matching Gate 213's `bash -n` |
| 35 | After `--host claude-code`, `meta.json.last_handoff_host == "claude-code"` | §2.3 item 2 — that the D4 swap really did reach `stamp_meta()` |

### 4.4 Must-fail halves — six mutants, each named, each with the row it must turn red

Every mutant is an **exact-string** replacement in a **copy**, in python, with an
`if old not in text: raise SystemExit(1)` existence check on every anchor — Gate 230's discipline. A
half-applied mutant proves teeth it does not have.

| flag | mutation | anchor | must turn red |
|---|---|---|---|
| `--must-fail-arity` | restore `    --host)\n      host_flag_seen=1` … → `    --host) host_flag="${2:-}"; shift 2 ;;` | the whole `--host)` arm | rows 24, 25, 26. ⛔ **This mutant executes the infinite loop** — every invocation of it must go through `_rc_timeout $BOUND`, and the gate asserts the mutant produced `BYTES=0` / non-2, i.e. that the fix is what turns it green |
| `--must-fail-d2` | `if [ "$host_flag_seen" -eq 1 ] && [ "$(classify_host_flag "$host_flag")" = "reject" ]; then` → `if false; then` | that `if` line | row 18 (typo would exit 0) |
| `--must-fail-registry` | delete `codex\|` from `is_registry_host`'s case pattern | `    claude-code\|copilot\|codex\|cursor\|gemini\|aider\|windsurf) return 0 ;;` | rows 12 and 31. **This is the mutant that proves AC-1 is measured** and not merely asserted |
| `--must-fail-parity` | delete the `claude-code\|claude\|claudecode` row from **python**'s `_normalize_handoff_host` | `    if val in ("claude-code", "claude", "claudecode"):\n        return "claude-code"\n` | rows 4, 5 (py class ≠ bash class) |
| `--must-fail-precedence` | revert python to `os.environ.get("THING_HOST") or os.environ.get("RC_HOST")` | `    explicit = os.environ.get("RC_HOST") or os.environ.get("THING_HOST")` | row 23 |
| `--must-fail-flagauthority` | delete the `if [ "$host_flag_seen" -eq 1 ]; then … return; fi` early-return from `detect_origin_host` | that block | row 19 (`--host codex` under `CLAUDECODE=1` would print the Claude Code recipe again — the original claim-8 defect) |

Verdict convention (copy Gate 230's `:235-248`): in a must-fail half, `fail > 0` → print
`teeth confirmed`, `exit 0`; `fail == 0` → print `MUTANT NOT CAUGHT`, `exit 1`.

### 4.5 What Gate 232 deliberately does **not** do

- It does not drive a **live spawn**. Exercising the launch-successor branch end-to-end starts a real
  interactive agent, which no CI gate may do. Same honest-scope limit Gate 230 states at `:27-32`.
- It does not re-assert what Gates 213/215/230 already pin. Row 20 is the one deliberate overlap,
  because the D2 work narrows the grok fallback and a gate that only checked the narrowing would be
  satisfied by deleting the fallback outright.

---

## 5. Phase plan + dependency DAG

```
P0  read + baseline  ──┬──> P1 docs (5 files)        ──┐
                       │                               ├──> P5 gate wiring ──> P6 version+release
                       ├──> P2 code  (2 files, ONE commit) ──> P4 gate file ──┘
                       │        ^ P2 depends on nothing but P0
                       └──> P3 regression baseline capture (for rows 32/33)
```

**Critical path:** `P0 → P2 → P4 → P5 → P6`. P1 and P3 run in **parallel** with P2.

### P0 — Baseline (blocks everything)

- `git branch --show-current` → must print `forge/claude-code-handoff-host`. Empty is a state to
  resolve, never a pass.
- `bash scripts/audit-gates.sh --check 213`, `--check 215`, `--check 230` → all `rc=0`.
  **Measured 2026-08-19: 0, 0, 0.** If any is red at HEAD, stop — you are not on the tree this plan
  was written against.
- Record the three seed literals for rows 32/33 (P3 can do this).

### P1 — Docs (parallel; own commit)

Files: `handoff-spawn.sh:17-21` (§3.1), `SKILL.md:3,23,29,40` (§3.2), `bin/rc:51` (§3.3),
`commands/handoff.md:9` (§3.4), `templates/handoff.md:55` (§3.5).

**Acceptance:** `grep -rn "grok|cli|chat" plugins/ravenclaude-core/` returns **only**
`CHANGELOG.md:389` (a historical release note — do not rewrite history). Measured today it returns
four live surfaces plus that one.

> ⛔ The `handoff-spawn.sh` usage edit is in P1 but the file is also edited in P2. Sequence P1's
> usage-string edit **into the P2 commit** if they would otherwise conflict; the doc/code split is a
> review convenience, not a file boundary.

### P2 — Code (critical path; **ONE commit** with `handoff-spawn.sh` + `context-handoff.py`)

Edits §3.6, §3.7 (edits 4/6/7), §3.8, §3.10, §3.11.

**Why one commit:** `handoff-spawn.sh:140-143` states the pair-in-step contract. Committing the bash
half alone leaves the two writers disagreeing on the alias rows at a commit boundary — the exact
invariant this PR exists to restore.

**Acceptance (run in this order):**

1. `bash -n plugins/ravenclaude-core/scripts/handoff-spawn.sh` → exit 0.
2. `python3 -m py_compile plugins/ravenclaude-core/scripts/context-handoff.py` → exit 0.
3. Re-run the §4.3 row table **by hand** before the gate exists (the table is the spec; the gate is
   its mechanisation). Rows 12, 18, 19, 21, 23, 24, 27 are the ones that would have been green
   before and must now differ.
4. `bash scripts/audit-gates.sh --check 213 && … --check 215 && … --check 230` → **all still 0.**
   ⛔ This is the single most important acceptance test in the plan. All five of Gate 230's mutant
   anchors and both of Gate 215's and the one of Gate 213's are preserved **by construction** in
   §3.7 — if any of the three now aborts with *"drifted — update the mutant"*, an edit strayed off
   the spec. Re-read §3.7's anchor callouts before touching a test file.
5. `ruff check .` → exit 0 (install with `python3 -m pip install --quiet --user ruff`; bare `pip` is
   absent on stock macOS).

### P3 — Regression baseline (parallel with P2, must finish before P4)

Capture the exact `grok`, `cli` and `chat` outputs from **HEAD before P2** and paste them into Gate
232 as literals (rows 32/33). Capture them under `env -i PATH=/usr/bin:/bin HOME="$HOME"` with a
fixture repo at a **short, fixed path**, because the block prints `cd <project_root>` — a temp path
would make the literal machine-specific. Use `--project-root` pointing at a fixture the gate itself
creates.

### P4 — Gate 232 (critical path)

Write `plugins/ravenclaude-core/hooks/tests/test-gate232-handoff-host-contract.sh` per §4. Use the
`Write` tool (Bash is denied on that directory).

**Acceptance:**
- `bash plugins/ravenclaude-core/hooks/tests/test-gate232-handoff-host-contract.sh` → `pass=N fail=0`.
- Each of the six must-fail flags → exit 0 with `teeth confirmed`, and each names the row that went
  red. ⛔ Read the output; a must-fail half that goes green **because a different row broke** is a
  false tooth.
- `chmod +x` is **not** required for `hooks/tests/*.sh` (they are invoked as `bash <path>`), and is
  blocked by the substrate guard anyway. Check: the existing test files' mode — match it.

### P5 — Wire the gate (critical path)

Three registrations, §3.12.

**Acceptance:**
- `bash scripts/audit-gates.sh --check 232` → exit 0.
- `bash scripts/audit-gates.sh --check 999` → the `Supported:` string now ends `…, 231, 232.`
- `bash scripts/audit-gates.sh 2>&1 | grep -c "test-gate232-handoff-host-contract.sh"` → **≥ 1 on an
  executed line.** ⛔ The file's own instruction. A gate registered in the dispatcher but not the main
  sequence is invoked by nothing.
- Full suite: `bash scripts/audit-gates.sh` → 0 failures.

### P6 — Version + release (critical path) — see §7

### Parallelisation summary

| Can run in parallel | Must be serial |
|---|---|
| P1 (docs) ‖ P2 (code) ‖ P3 (baseline capture) | P2 → P4 (the gate drives the new behaviour) |
| — | P4 → P5 (wiring a non-existent file fails) |
| — | P5 → P6 (the version bump's regen check runs in the same CI) |

---

## 6. Risk matrix (critic + red team, merged)

| # | Risk | Source | Mitigation | Phase |
|---|---|---|---|---|
| **R-1** | D2 hard-errors 5 of the 7 registry hosts and destroys a **working** handoff path | red-team HIGH-1 | The D2 **split**: `classify_host_flag` returns `neutral` for registry hosts and `other` → exit 0 (§3.7). Gate 232 rows 12-17; `--must-fail-registry` proves the row is measured | P2, P4 |
| **R-2** | D2 breaks the `handoff-spawn.sh:8` "copy-paste is ALWAYS printed" invariant, killing the `SKILL.md:33` recovery instruction | red-team HIGH-1 (2)(3) | The rejection block sits **after** `copy_paste_block()`'s definition and calls it before `exit 2` (§3.8), matching both existing fatal branches. Gate 232 row 18 asserts `BYTES>0` alongside exit 2 | P2, P4 |
| **R-3** | The naive D3 fix converts the hang into a **silent grok seed** | red-team HIGH-2 | `host_flag_seen` tracks **presence** separately from **value**; `named_but_unknown` keys on presence (§3.7 edit 7), so an empty value gets host-neutral text and exit 2, never case (a). Gate 232 rows 24, 25 | P2, P4 |
| **R-4** | The D3 gate hangs CI unbounded, and bare `timeout` is a **vacuous pass** on this macOS | red-team HIGH-3 | `_rc_timeout` only + a preflight that HARD-FAILS if no bound exists + a positive control in the same harness + `BYTES>0` (§4.1, rows 24/27). ⛔ `audit-gates.sh` wraps 0 gates in a timeout, so the bound must live **inside** the gate file | P4 |
| **R-5** | D2 in bash alone makes the two writers disagree on 6 inputs; `GROK` refuses in bash while python emits a **live grok launch** | red-team HIGH-4 | Case+whitespace parity in bash (§3.7 edit 4) + the alias row in python (§3.10), so all 6 rows agree. D2's exit code stays bash-only by explicit decision (§3.10), and Gate 232 asserts host+seed-class agreement on every row | P2, P4 |
| **R-6** | Gate 230's `codex` row passes **vacuously** once codex stops producing a seed | red-team MED-5 | Under the D2 split, `--host codex` still exits 0 with the neutral block, so Gate 230's row keeps measuring a choice — **the split removes the failure mode rather than papering it**. Gate 232 additionally carries a same-row presence assertion on every absence assertion (AC-6) | P2 |
| **R-7** | Row 21 + D2 break Gate 230's mutant anchors, and the "repair" is to make the test agree with the code | red-team MED-6, `scope.md:71-73` | **All five Gate 230 anchors, both Gate 215 anchors and Gate 213's single anchor are preserved by construction** — §3.7 lowercases into a local before the `case` so the anchor line stays byte-identical; the `named_but_unknown` edit touches the assignment, not either consumer; the D2 block is new text inserted between functions. P2 acceptance step 4 is the check. If an anchor does move, §4.0's rule binds: re-derive that the mutant reconstructs the **original** defect | P2 |
| **R-8** | `THING_HOST`/`RC_HOST`-named-but-unknown gets a grok launch; every gate's env hygiene hides it | red-team MED-7 | §3.7 edit 7 + Gate 232 rows 21/22 (with a `THING_HOST=grok` control). ⛔ This row must **not** use `env -i` alone — it must inject `THING_HOST` explicitly | P2, P4 |
| **R-9** | `--host --dry-run` swallows the next flag; with `--recipe same-host` + an owner spawn flag, a dry run becomes a **live launch** | red-team MED-8 | The `--*` guard in §3.6 + Gate 232 row 26 | P2, P4 |
| **R-10** | D4 is shipped with a **false premise** about its blast radius | red-team "attacks that failed" | §3.11's comment states plainly that it pins an invariant with no measured live trigger. §2.5 tells the CHANGELOG the same thing | P2, P6 |
| **R-11** | A real Claude-Code-in-VS-Code session is affected by the vscode carve-out | plan-B §7 #3 | **Disproved and recorded so nobody re-derives it:** `CLAUDECODE` resolves at `detect_origin_host` before any fall-through to `unknown`, so a real Claude Code session never reaches the carve-out. Preserved here because the reasoning that rules it out is itself not CI-testable | — |
| **R-12** | Adding `other`/`generic` makes them resolve as a *host* and hit the refusal guard with the eager grok seed | this synthesis, design review | `other` is handled in `classify_host_flag`, **not** in `normalize_host`, so `$host` stays `unknown` and `named_but_unknown` supplies the neutral seed. If a future edit moves `other` into `normalize_host`, `handoff-spawn.sh:239` fires and the script exits 2 with *"refuse to emit a grok seed for host=other"* — loud, but wrong. Gate 232 row 17 catches it | P2, P4 |
| **R-13** | Gate 232 registered in the dispatcher but invoked by no workflow (the "unrun gate" class) | repo history | P5 acceptance: grep the **full-suite output** for the script name on an executed line, per `audit-gates.sh:8303-8305` | P5 |
| **R-14** | A concurrent forge branch also claims gate number 232 | both plans | Re-verify at P4 start against `audit-gates.sh`'s `Supported:` string and `ls hooks/tests/`, not against a remembered number | P4 |
| **R-15** | The version bump lands without the copilot regen, failing `regenerate-artifacts.yml:273`'s `--check` | claims-table row 16 **correction** | §7 step 3. Measured 2026-08-19: `scripts/generate-copilot-plugin.py` **exists** at repo root (39,085 B), `--check` currently returns 0, and `copilot/plugin.json:4` carries `"version": "0.283.0"` — so a bump **will** make it stale | P6 |
| **R-16** | A write to the primary checkout is DENIED by another session's `worktree-guard` lease | claims-table row 23 | Everything lands in the worktree. Do not tunnel around the guard; do not edit `worktree_lease` in the posture | all |

---

## 7. Version + release

**Target: `0.284.0`.** Minor bump: new accepted `--host` values and a new exit-2 path are
user-visible behaviour changes, additive rather than breaking.

⛔ The primary checkout reads `0.282.0` and is **stale** — it was measured 1 commit behind
`origin` and then read anyway. The worktree is authoritative: `plugin.json` = `0.283.0`, catalog =
`0.283.0` (both re-verified 2026-08-19).

**Release steps, in order:**

1. `plugins/ravenclaude-core/.claude-plugin/plugin.json` → `"version": "0.284.0"`. **Single source of
   truth — do not hand-edit the catalog.**
2. `python3 scripts/sync-plugin-versions.py` — derives the `.claude-plugin/marketplace.json` entry.
   Gate 226 (`sync-plugin-versions.py --check`) fails if the catalog is not derived.
3. `python3 scripts/generate-copilot-plugin.py` — **this step APPLIES.** `claims-table` row 16 said
   the script was absent; that was **FALSE** (a one-directory `ls` reported as a repo-wide absence).
   It exists at the repo root and `regenerate-artifacts.yml:273` runs it `--check`.
   Then `python3 scripts/generate-copilot-plugin.py --check` → exit 0.
   *Note:* the projected `copilot/` tree carries **no** `grok|cli|chat` string, so the doc edits do
   not change its content — only the version does. Verified 2026-08-19.
4. `npx --yes prettier@3.9.4 --write .` then `--check .` → exit 0 (the bump touches `.json`).
5. `ruff check .` → exit 0.
6. `bash scripts/audit-gates.sh` → 0 failures.

### CHANGELOG — the gap is three versions, not two

Measured 2026-08-19: `plugins/ravenclaude-core/CHANGELOG.md`'s top entry is **`## 0.280.0 — 2026-08-18`**
while `plugin.json` is `0.283.0`. **`0.281.0`, `0.282.0` and `0.283.0` are all missing.**

**Ruling for this PR:** add the `0.284.0` entry at the top. **Do not backfill the three missing
versions here** — each needs its own merged PR read to be written honestly, and inventing them is
worse than the gap. Record the backfill as follow-up **F-1** (§9).

An observation the builder should not over-read: `grep -n CHANGELOG scripts/audit-gates.sh` returns
**nothing**, so CHANGELOG freshness is a **convention** (`AGENTS.md` § "CHANGELOG convention"), not an
enforced gate. That is why the gap could open silently. It does not license leaving `0.284.0` out.

**`0.284.0` entry — required content:**

- **Fixed — `--host` with a missing value spun forever.** The `shift 2` arity bug, all five flags,
  with the measured `EXIT=142 BYTES=0` and its control.
- **Fixed — an explicit `--host` no longer falls through to environment detection.** With `CLAUDECODE`
  set, `--host codex` printed a Claude Code recipe.
- **Fixed — the two seed writers disagreed on six inputs.** The case/alias parity table.
- **Fixed — `RC_HOST` now outranks `THING_HOST` in `context-handoff.py`.** ⛔ State it as an
  invariant with **no measured live trigger** (§2.5). Do not narrate it as an incident.
- **Changed — `--host` vocabulary.** `claude-code` documented on every surface; the five
  registry-only hosts and `other` accepted and answered host-neutrally, exit 0; a name in neither
  vocabulary now prints the copy-paste block and exits 2.
- **Unchanged, deliberately** — the grok-first fallback when nothing is named and nothing is
  detected (case (a)), and the `TERM_PROGRAM=vscode` carve-out. Say *why*, and name Gates 213/215/230
  as the pins that did not move.

**PR conventions:** branch is `forge/claude-code-handoff-host` (already cut); this touches `plugins/`
and `.github`-adjacent CI, so it goes through a **PR**, not straight to `main`. No migration note is
needed: no consumer behaviour breaks on `/plugin marketplace update` — the only newly-fatal input is
a host name that was never a supported value.

---

## 8. Alternatives rejected

| Alternative | One-line reason |
|---|---|
| Flip the default to `claude-code` (D1) | Measured zero benefit — Claude Code resolves by detection and never reaches the default — against three edited gates and removing the fallback from the only host it protects. |
| D2 as originally written (any unrecognised `--host` is fatal) | Hard-errors 5 of the 7 hosts the marketplace officially declares, destroying a working path and pressuring an agent toward `cli`. |
| Validate `--host` early, before `detect_origin_host()` and the handoff-file check (plan-A S4) | Cannot print the copy-paste block, which needs `$host`/`$seed`/`$project_root` — breaks the `:8` invariant AC-2 makes binding. |
| Thread a `host_source ∈ {flag,env,detected,default}` label through both scripts | Existed only to mark a **defaulted** `claude-code` as a guess; with D1 dropped the surviving cases need one bit, and `named_but_unknown` already is it. |
| Delete the eager `seed="grok \"…"` at `:95` | It **is** the case-(a) mechanism and carries Gate 213's only mutant anchor; removing it means re-adding the same behaviour under a new name. Follow-up F-2. |
| Delete the `TERM_PROGRAM=vscode` carve-out | Measured load-bearing today: it is the only thing between a Cursor session and a grok launch. |
| Thread the resolved host into `stamp_meta()` | The D4 precedence swap already makes every `detect_host()` call site see the flag; a second mechanism for one fact. |
| A shared `handoff-hosts.json` read by both scripts at runtime | Forces `jq`/`python3` into a bash path the gates deliberately run under `env -i PATH=/usr/bin:/bin`. Duplicated literal + a parity assertion instead. |
| Give `context-handoff.py` a matching D2 hard error | Refusing to write `handoff.md` over a misspelled successor name destroys the artifact that matters most; the two writers already agree on the *seed*, and only bash gates the spawn. |
| Add `--host=value` (equals form) | Already a loud error via the `*)` catch-all; adding it for one flag and not the other four makes the interface inconsistent per-flag. Follow-up F-3. |
| Bound the arity gate with bare `timeout` | Both `timeout` and `gtimeout` are **absent** on this macOS, so `timeout N cmd` is exit 127 and an "exits non-zero" assertion passes vacuously. |
| Capture the grok/cli/chat regression baseline by diffing against `origin/main` in-gate | Needs `git` inside a gate whose children run under `env -i`; pinned literal strings give the same byte-exactness with no dependency. |
| Rename `test-gate227-handoff-seed-host.sh` to match its gate number | Renaming anything under `hooks/` is blocked by the tribunal's substrate guard, and filename ≠ gate number is already the norm here. |

---

## 9. Definition of done

**Behaviour** — every one of these is a command a reviewer can run:

- [ ] `--host claude-code` / `claude` / `claudecode` / `CLAUDE-CODE` → exit 0, Claude Code recipe, from **both** writers.
- [ ] `--host grok|GROK`, `cli|CLI|copilot`, `chat|Chat` → exit 0, their own recipes, **byte-identical** to HEAD-before for the three canonical spellings.
- [ ] `--host codex|cursor|gemini|aider|windsurf|other` → **exit 0**, host-neutral block, from both writers. **(AC-1)**
- [ ] `--host <typo>` → the copy-paste block is printed, **then** exit 2, `BYTES>0`. **(AC-2)**
- [ ] `--host` with a missing / empty / `--`-prefixed value → exit 2, `BYTES>0`, host-neutral, **no grok launch**, terminating well inside a 10 s bound. **(AC-3)**
- [ ] `--host codex` with `CLAUDECODE=1` → host-neutral, **not** a Claude Code recipe.
- [ ] `THING_HOST=gemini` with no flag → host-neutral. `THING_HOST=grok` → still grok. **(AC-6)**
- [ ] `THING_HOST=copilot` + `--host claude-code` → python writes a **claude** seed. **(D4)**
- [ ] Nothing named + nothing detected → **still grok**. Case (a) has not moved.

**Gates**

- [ ] Gates 213, 215, 230 pass, base **and** must-fail halves, with **no test-file edits**. If any test file changed, this box does not tick.
- [ ] Gate 232 exists, passes, and its six must-fail halves each report `teeth confirmed` naming the intended row. **(AC-4, AC-5)**
- [ ] Gate 232 is registered in the `--check` dispatcher, the `Supported:` string, **and** the main sequence; the full-suite output contains its script name on an executed line.
- [ ] `bash scripts/audit-gates.sh` → 0 failures.

**Docs**

- [ ] `grep -rn "grok|cli|chat" plugins/ravenclaude-core/` returns only `CHANGELOG.md:389`.
- [ ] All five doc surfaces lead with `claude-code` and name the neutral path.

**Release**

- [ ] `plugin.json` = `0.284.0`; `sync-plugin-versions.py --check` → 0; `generate-copilot-plugin.py --check` → 0.
- [ ] `prettier --check .` → 0; `ruff check .` → 0.
- [ ] CHANGELOG has a `0.284.0` entry containing the six bullets in §7, including the D4 invariant framing.

**Follow-ups recorded, not done here**

- **F-1** — backfill CHANGELOG entries for `0.281.0`, `0.282.0`, `0.283.0` (each needs its merged PR read).
- **F-2** — remove the eager `seed="grok \"…"` pre-assignment at `handoff-spawn.sh:95` in favour of an explicit case-(a) branch; requires updating Gate 213's mutant anchor, so it is its own PR.
- **F-3** — decide `--host=value` (equals form) for all five flags at once, or not at all.
- **F-4** — `rc-artifacts.py` is absent from the installed `0.282.0` cache and `bin/rc` reports it at a path one level too shallow (`claims-table` row 17). Separate defect, out of scope, recorded.

---

## Open questions for the Team Lead

**None that block a build.** Every fork in `gap-delta.md` is resolved in §2.4, and all six binding
acceptance criteria are adopted. Two items are recorded as *decisions taken here* rather than
questions, because deferring them would stall P2 — flag them to the owner at PR review if either
reads as an overreach:

1. **`other` / `generic` as accepted tokens** (§3.7). Not in the owner's D2 ruling; adopted from
   red-team mitigation (b) because the ruling's own rationale — *"pressure an agent on an unlisted
   host to pick the nearest recognised token"* — is only fully answered if an unlisted host has a
   truthful value to pass. One case arm, reversible in one line.
2. **python does not get D2's hard error** (§3.10). Reasoned, red-team-endorsed, and it is the one
   place where the two writers deliberately differ (in exit code, never in seed).
