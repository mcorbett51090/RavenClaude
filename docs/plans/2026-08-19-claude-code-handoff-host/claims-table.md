# G1 — Claims table — claude-code-handoff-host

Every row below was measured **this session, in this working tree**, with controls in both
directions. `kind` ∈ observation | inference. `tier`: BLOCK = outside-repo/behavioural fact,
WARN = repo-structural confirmed by a visible in-session tool call.

| # | claim | kind | tier | source / control | settling-gate |
|---|---|---|---|---|---|
| 1 | `normalize_host()` maps `claude-code`, `claude`, `claudecode` → `claude-code` | observation | WARN | read `handoff-spawn.sh:107-113` | SETTLED |
| 2 | `detect_origin_host()` returns `claude-code` on `CLAUDECODE` or `CLAUDE_CODE_ENTRYPOINT` | observation | WARN | read `handoff-spawn.sh:144-147` | SETTLED |
| 3 | `--host claude-code --dry-run` emits a correct Claude Code recipe (`cd <repo>` / `claude` / paste) | observation | BLOCK | ran it; **control**: `--host chat` emitted the Chat recipe and `--host cli` the CLI one on the same invocation shape | SETTLED |
| 4 | The **v0.282.0 cache** copy also carries claude-code — 10 mentions in `handoff-spawn.sh`, 5 in `context-handoff.py` | observation | WARN | grep -c on the cache paths | SETTLED |
| 5 | Therefore the capability was present in the exact build that produced the wrong Chat artifact — the failure was interface-reading, not a missing feature | inference | — | from 3 + 4 | SETTLED |
| 6 | The usage string advertises `[--host grok|cli|chat]` and omits claude-code | observation | WARN | `handoff-spawn.sh:19` | SETTLED |
| 7 | `SKILL.md` says *"Pass `--host grok|cli|chat`"* and lists other-host adapters as out of scope | observation | WARN | `SKILL.md:23` + its Out-of-scope section | SETTLED |
| 8 | ⛔ With `CLAUDECODE` set, `--host codex` resolves to `host=claude-code` and prints a Claude Code recipe | observation | BLOCK | ran it | SETTLED |
| 9 | ⛔ With `CLAUDECODE` **and** `CLAUDE_CODE_ENTRYPOINT` cleared, the same command reaches `host=unknown` and prints the safe host-agnostic block — **no grok** | observation | BLOCK | `env -u … --host codex`; **control**: `--host cli` under the same cleared env still honoured the flag, so the clearing did not simply disable flag handling | SETTLED |
| 10 | So the case-(b) guard (`named_but_unknown`, lines 201-203) fires only when env detection ALSO fails, because `detect_origin_host()` falls through to detection when the flag is unrecognised rather than preserving the named-but-unknown state | inference | — | from 8 + 9 + reading 116-131 and 201-203 | SETTLED |
| 11 | My first attempt at control 9 cleared the WRONG variables (`TERM_PROGRAM`, `CLAUDE_CODE`, …) and still returned `claude-code`; only clearing `CLAUDE_CODE_ENTRYPOINT` reproduced `unknown` | observation | BLOCK | both runs; the failed attempt is recorded because it nearly read as "the flag is simply ignored, always" | SETTLED |
| 12 | Gates 215 and 227 exist at `plugins/ravenclaude-core/hooks/tests/` and **both pass today** | observation | WARN | ran both, exit 0 | SETTLED |
| 13 | Gate 215 pins `"unset host still grok"` — the exact default D1 flips | observation | WARN | `test-gate227-…:198` cites it; `test-gate215-…:2` names the gate | SETTLED |
| 14 | Gate 215 carries mutant checks that abort with *"handoff-spawn.sh drifted — update Gate 215 mutant"* | observation | WARN | `test-gate215-…:111,125` | SETTLED — the gate detects drift in the file it pins, so an edit that changes those regions must update the mutants |
| 15 | Plugin version is `0.282.0` | observation | WARN | `plugin.json` | SETTLED |
| 16 | `generate-copilot-plugin.py` is **absent** from this repo | observation | WARN | `ls` — file not found | SETTLED — the remembered "version bump → regen copilot" step may no longer apply here; **verify against the release checklist before bumping** |
| 17 | `rc-artifacts.py` is absent from v0.282.0, and `rc` reports it at a path one level too shallow | observation | BLOCK | `find` returned nothing; `rc artifacts new` failed | SETTLED — out of scope, recorded |
| 18 | `context-handoff.py` and `handoff-spawn.sh` are deliberately kept in step — the comment states they "write the seed for the SAME handoff, so a host either resolves in both or the pair disagrees about who the successor is" | observation | WARN | `handoff-spawn.sh:140-143` | SETTLED — any host change MUST touch both |

## The one thing NOT measured

Whether flipping the unset-host default breaks a *consumer* outside this repo (a hook, another skill,
or a user's muscle memory) that relies on `grok` being the fallback. Nothing in-repo was found that
does, but "I grepped this repo" is not "nothing depends on it". → G5 red-team.

---

## ⛔ G1 CORRECTIONS — two rows above are WRONG, both my errors, both caught by Panel A

| # | correction | how it happened |
|---|---|---|
| **16 — FALSE** | `generate-copilot-plugin.py` **EXISTS** at `scripts/generate-copilot-plugin.py` (repo root), 39,358 B, in both the primary checkout and the worktree. **The regen step APPLIES.** | I ran `ls plugins/ravenclaude-core/scripts/generate-copilot-plugin.py`, got nothing, and wrote "absent". A search of ONE directory reported as absence from the REPO. `find` over the whole tree finds it immediately. This is the project's recurring failure shape — a check that could only ever look in one place, reporting a global conclusion. |
| **15 — WRONG TREE** | Version is **0.283.0** in the worktree (cut from `origin/main`); `0.282.0` is the **stale primary checkout**, which I had *myself* measured as 1 commit behind origin in my very first command. | I took every claim from the primary checkout while the work happens in the worktree. Noting "behind: 1" and then reading that tree anyway is worse than not checking — the staleness was measured and then ignored. |

**Both rows are BLOCK-tier facts a build phase rests on**: the regen step is a release-checklist
requirement (`regenerate-artifacts.yml` runs it `--check`), and the version determines the bump target.
A plan built on "no regen needed, bump 0.282.0 → 0.283.0" would have collided with a 0.283.0 that
already exists and skipped a gate CI enforces.

## Additional facts Panel A measured that this table lacked

| # | claim | kind | tier |
|---|---|---|---|
| 19 | **THREE** gates pin `handoff-spawn.sh`, not two — Gate 213 also pins the grok default and carries its own drift mutant | observation | WARN |
| 20 | The file named `test-gate227-handoff-seed-host.sh` is actually **Gate 230**; Gate 227 is `guard-probe-validity` | observation | WARN |
| 21 | ⛔ The bash/python pair is **ALREADY out of step today**: bash `normalize_host` maps `claude`/`claudecode` → `claude-code`; python `_normalize_handoff_host` maps neither and returns the raw string. So `--host claude` already yields a Claude Code recipe from one writer and host-neutral text from the other. D2 makes that divergence FATAL (one side exits 2, the other succeeds). | observation | BLOCK |
| 22 | Two doc surfaces the scope missed: `bin/rc:51` (the only invocation path on Copilot/Codex — no slash command exists there) and `commands/handoff.md:9` (the sentence an agent literally executes — the exact shape that caused the measured failure) | observation | WARN |
| 23 | A **different live session** (`dd4804c3…`, pid 30864) holds an actively-refreshed `worktree-guard` lease on the primary checkout, so a subagent's write there was DENIED while a write into the run's own worktree succeeded | observation | BLOCK |

Row 23's consequence: `plan-A.md` is at
`.claude/worktrees/forge-claude-code-handoff-host/.ravenclaude/runs/forge/claude-code-handoff-host/plan-A.md`,
not the primary run dir. Downstream gates must be handed that path. Panel A took the guard's own
documented remedy rather than tunnelling around it or editing the posture, which is the correct move.
