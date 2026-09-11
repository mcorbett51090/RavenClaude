# Lessons Learned

> Running log of trial-and-error findings from work that touches the domains this hub covers. **Newest entries at the top.** Read this file at the start of any task touching a covered domain — the "we already learned this" cycle is what makes the hub valuable.

## Format

Each entry is a dated section. Reverse-chronological order (newest first).

```markdown
## YYYY-MM-DD — Short title naming the rule or finding

**Context:** What we were trying to do. 1–2 sentences.

**What we tried first:** The path that failed. 1–2 sentences.

**Why it failed:** The actual reason, with technical detail. 2–4 sentences.

**What works:** The canonical solution. 2–4 sentences.

**How to apply:** When this rule fires, what to do. 1–2 bullet points.

**Trace:** Origin project, origin session ID if useful. Optional.
```

---

## 2026-09-10 — A merged permission-rule cleanup reappeared after a reapply: check whether the file is generated before suspecting a race

**Context:** A consumer project removed four permission rules from `.claude/settings.json` that Claude's settings validator flags as inert (`Write`/`MultiEdit`/`NotebookEdit` path-shaped rules are matched as `Edit`, and `Glob` as `Read`, per the SDK's own validator), confirmed the warnings cleared, and merged the change.

**What we tried first:** When the rules reappeared hours later with no error and no visible actor, the natural read was a concurrent session clobbering the edit — so the investigation started chasing a race condition.

**Why it failed:** `.claude/settings.json`'s allow-list in a RavenClaude-managed project is *generated output* from `apply-comfort-posture.py`'s `EMISSIONS` table, which is idempotent-by-reapply. A later reapply regenerated the same four inert rules the fix had removed. `.ravenclaude/posture-events.jsonl` recorded the exact diff (`added: ["MultiEdit(**)", "Write(**)", "Write(//**)", "Write(~/**)"]`) at the reapply timestamp — a deterministic regenerator, not a race, and the tool's own event log said so before any process-timing analysis was needed.

**What works:** Before suspecting a concurrent-write race on any file that reappeared unchanged after a clean merge, check whether the file is a generated artifact and read its own event/audit log first. A regenerator and a race present identically in `git status`, but a regenerator usually leaves an audit trail.

**How to apply:**
- Treat `.claude/settings.json`'s allow/ask/deny lists as build output when RavenClaude's comfort posture is active — hand edits to path-shaped rules for `Write`/`MultiEdit`/`NotebookEdit`/`Glob` don't survive a reapply and won't raise an error when reverted.
- When a merged fix reappears, check the tool's own event log (here, `posture-events.jsonl`) before reasoning about process timing — it is cheaper and conclusive.

**Trace:** Consumer project (BTCSI), 2026-09-10. The underlying defect (four inert `Write`/`MultiEdit` path-shaped entries in the `EMISSIONS` table's `file_edit_project`/`file_edit_global` categories) was fixed directly in `apply-comfort-posture.py` the same day.

---

## 2026-09-10 — An Agent Host session can be bound but unusable when a provisional URI is subscribed before materialization

**Context:** A newly opened Claude session in VS Code accepted a first prompt but then stopped
indefinitely. The visible symptom resembled an MCP startup hang, yet the SDK backend and MCP child
were both alive and idle-healthy.

**What we tried first:** We initially treated repeated stalls as launcher or resource-exhaustion
problems. Those are common and can produce the same frozen UI, but process-state inspection showed
no blocked launcher, no overloaded host, and no orphan accumulation in the decisive reproduction.

**Why it failed:** The workbench briefly addressed the new session as
`<provider>:/untitled-<A>`. A UI observer opened a state subscription for that provisional URI.
Two milliseconds later, first-send materialization bound a different real URI,
`<provider>:/<B>`. The provisional subscription failed with `AHP_SESSION_NOT_FOUND`; retrying it
could never succeed because the identity had changed. The real scope recorded a bind but never
registered an active client, leaving the turn pending forever. An earlier create-before-subscribe
fix covered stable identities but not this provisional-to-real remapping path.

**What works:** Treat an untitled session resource as a workbench placeholder, never as a stable
wire identity. Components that observe session state must defer subscription while the resource is
`untitled-*`, then re-evaluate when the view model publishes the materialized real resource. A
generic retry at the protocol layer is insufficient because it lacks the mapping and would retry
the obsolete URI. Recovery for an already half-bound tab is to abandon the tab, or run
"Developer: Reload Window" if several tabs are affected at once; **never `pkill`/`killall` any
process to try to recover it** — terminate only a confirmed-dead SDK backend by PID, and only
after confirming via process state that it has no live client, since killing a live backend can
take other, healthy sessions down with it. Cleanup cannot make the stale subscription valid.

**How to apply:**
- Diagnose this class when logs show `Bound chat` for a real scope but no corresponding
  `active client`, especially when an immediately preceding subscribe targeted `untitled-*`.
- Before blaming MCP, distinguish idle-healthy processes (`ep_poll`, `do_wait`,
  `futex_wait_queue`) from blocked launchers (`pipe_read`, `tty_read`, or process state `D`).
- Watch for this most often right after opening several new tabs in quick succession — each
  new-tab materialization is a fresh race window. Waiting for a tab to show as ready before
  opening the next is a cheap, free preventive habit, not a fix.
- Session logs can carry either a `[Claude` or `[Copilot` prefix for the same underlying Agent
  Host mechanism depending on which chat participant is active — don't assume the prefix tells
  you which host component is involved.
- In client code, guard every session-state observer that can see provisional resources. Subscribe
  only after materialization supplies the real backend URI.
- Test the lifecycle, not only ordering: assert that an untitled resource opens no wire
  subscription and that changing to the real resource opens exactly the expected subscription.
- Do not patch an installed minified client bundle or add blind retries for the provisional URI.
- **Scope:** this is a VS Code Agent Host (Copilot Chat / Claude session-target) defect. The
  Claude Code CLI, which has no untitled-URI concept, is unaffected.

**Trace:** Generalized from a consumer-project diagnosis, 2026-09-10. Upstream tracking, state as
of 2026-09-10: [`microsoft/vscode#335473`](https://github.com/microsoft/vscode/issues/335473)
(open). Proposed fix and cross-browser regression test:
[`microsoft/vscode#335472`](https://github.com/microsoft/vscode/pull/335472) (open, unmerged as of
2026-09-10). Related original bug and first fix:
[`microsoft/vscode#330531`](https://github.com/microsoft/vscode/issues/330531) and
[`microsoft/vscode#330761`](https://github.com/microsoft/vscode/pull/330761).

---

## 2026-09-10 — MCP cost is **per live session**, not per machine, and dead sessions leave orphaned servers behind: the box starves and the symptom looks like a hang

**Context:** In a consumer project, a Claude session bound normally, started its MCP servers in
about a second, emitted two tool calls — and then stopped. Process alive, no error, turn never
completed. The user's read was "it's stuck starting MCP servers," which is exactly what it looks
like.

**What we tried first:** Reached for the known MCP failure mode — a launcher blocking during the
startup handshake (the sibling lesson below, "An MCP launcher that blocks at session start or
plugin reload hangs the host UI"). That hypothesis was wrong, and the check that killed it took
one command: two tool calls had already been emitted successfully, which rules out a
startup-handshake block — a launcher stuck in the handshake never gets that far.

**Why it failed:** `wchan` said every MCP process was idle-healthy — `ep_poll`, `do_wait`,
`futex_wait_queue`. A genuinely blocked launcher sits in `pipe_read`/`tty_read` or process state
`D`. Nothing was blocked. There were simply far too many of them. The box was carrying 51 MCP
processes / 2.7 GB resident / load average 16.4 on 8 cores, with 309 MB free. The stall
co-occurred with a starved machine; the two are linked by resource contention, not by the session
itself being wedged.

**The mechanism (the part worth keeping).** Two independent things accumulate, and they have
different fixes, so conflating them wastes the diagnosis:

1. **Per-session multiplication is architectural for stdio-transport servers, not a bug.** MCP's
   stdio transport wires each server's stdin/stdout to *its client* as the protocol channel, so a
   stdio server **cannot** be shared between sessions — it is a child process of one client by
   construction. (A server exposed over HTTP/SSE instead of stdio does not have this constraint
   and can be shared; this lesson is about the stdio case, which is the common one for
   locally-launched plugin servers.) Every concurrent stdio-based session owns a complete,
   unshared MCP set. Measured here: ~313 MB per session, so four open chats is four copies of
   everything. No amount of tooling reclaims this; only closing sessions does.
2. **Orphans make it ratchet.** When a session ends, its MCP children are not reliably torn down.
   They get reparented (to the agent host, or to init) and keep their memory indefinitely.
   Nothing reaps them. 22 of those 51 processes belonged to sessions that had already ended. This
   is why the problem survives restarts and why closing a chat does not necessarily give the
   memory back.

**The cost is wildly unevenly distributed, and the expensive plugin is not the obvious one.** Two
plugins accounted for 100% of the memory. One of them — a Power Platform editor plugin whose
purpose has nothing to do with browsers — bundles Playwright with a Chromium browser and cost 733
MB, 78% of the total, because it is spawned once per session. Nobody would guess that from the
plugin's name or description. Its `npx`-based launch also leaves a three-process chain resident
(`sh -c npx …` → `npm exec` → the actual `node` server); the two wrappers held ~94 MB doing
nothing but babysitting the child in this measurement — a property of the `npx` wrapper chain,
not a universal per-server cost, and it disappears with a direct, pinned launcher invocation. Note
the corollary: swapping that plugin for a lighter equivalent still leaves an unpinned/non-`-y`
launcher able to re-arm the sibling lesson's startup-hang risk — reducing memory cost and reducing
hang risk are two separate fixes, not one.

**What works:** Measure at runtime, not just in config. Static launcher audits (the sibling
lesson's contribution) predict which servers *could* block; they say nothing about how many are
*actually running* or who owns them. The portable detection rule for an orphan is: an MCP process
whose parent is neither a live agent-session process nor another MCP process — its owner is gone
and it has been reparented. In a container, reparenting can land orphans on PID 1 rather than a
recognizable agent-host process, so the check needs a positive liveness test (confirm the claimed
owner process actually exists and is a live session) rather than only a negative absence check.
Reaping orphans is safe and is the single biggest win because it costs no open work, but reaping
must be opt-in, read-only by default, run as a dry-run first, and must refuse to signal anything
that resolves to a live session's child — never a name-based kill (`pkill`/`killall`), which
cannot make that distinction. Cleanup here took 51→30 processes, 2.7 GB→1.5 GB, load 8.2→4.0.

**How to apply:**
- When a session stalls, check `wchan` first: `ep_poll`/`do_wait`/`futex_wait_queue` =
  idle-healthy, so suspect exhaustion, not a hang. `pipe_read`/`tty_read`/`D` = genuinely blocked,
  so suspect the launcher.
- Treat open agent sessions as resource reservations sized by measurement, not a fixed per-core
  rule: divide available RAM by the measured per-session RSS (~313 MB here) to size how many
  concurrent sessions are comfortable on a given machine, rather than assuming a fixed count like
  "2-3 sessions" generalizes to other hardware or other plugin sets.
- Audit what your plugins actually spawn, not what they claim to do — a plugin can quietly bundle
  a browser.
- Expect zombies (state `Z`, 0 RSS) after reaping. They hold no memory and only the parent can
  clear them; don't chase them.
- A session already wedged mid-turn will not recover. Cleanup lets new work run; it cannot unstick
  that tab. Close it.
- For the reusable orphan-reaping procedure itself (opt-in, dry-run, liveness-checked, never
  name-based), see
  [`docs/best-practices/audit-mcp-runtime-cost-not-just-launcher-config.md`](../best-practices/audit-mcp-runtime-cost-not-just-launcher-config.md)
  — this entry keeps the story and the measurements, that doc owns the rule.

**Trace:** Consumer project, generalized, 2026-09-10. Diagnosed by process-state inspection
(`ps -eo pid,ppid,stat,wchan,rss,args`) plus session transcripts; conclusions are measurements, not
estimates. Adjacent to but distinct from "An MCP launcher that blocks at session start or plugin
reload hangs the host UI" (below in this file, dated 2026-09-09) — that lesson is one server
blocking, this one is too many healthy servers. Same subsystem, opposite failure; recommend
reviewing the two together. Notably, the Playwright launcher exonerated in that lesson (it passes
`-y`, so it never hangs) is the dominant memory cost here — a launcher can be blameless on startup
and still be the main problem.

---

## 2026-09-10 — `guard-destructive.sh`'s `tool_name`-blind matcher fires on native VS Code tools that were never shell commands, and the fix is deferred

**Context:** A Claude session running as VS Code Copilot Chat's "Claude" session target called
two native, read-only VS Code tools bridged in as MCP (`mcp__client__problems`,
`mcp__client__testFailure`). Neither takes a `command` argument and neither can be destructive.

**What we tried first:** Read the resulting
`[guard-destructive] WARNING: could not parse the command (jq and python3 both unavailable); the
destructive-command guard is DEGRADED for this call.` message as a real environment problem —
missing `jq`/`python3` — worth fixing in the consumer project's devcontainer.

**Why it failed:** The warning is a symptom of a narrower bug: `hooks.json`'s `PreToolUse` matcher
(`Bash|Read|Write|Edit|MultiEdit|WebFetch|WebSearch|mcp__.*`) runs `guard-destructive.sh` against
every `mcp__*` call, but the hook reads only `tool_input.command` — it never checks `tool_name`
first. For a tool call like `mcp__client__problems` that legitimately has no `command` field, the
hook can't tell "there was never a command to find" from "I couldn't parse one." In this
environment, the VS Code-spawned SDK subprocess backing the session target had a `PATH` that
didn't carry `jq`/`python3` (both present and reachable in a normal terminal-launched session), so
command extraction failed and the DEGRADED warning fired — on a tool call that was never
shell-shaped and never needed either binary.

**Why it costs more than it looks:** The warning itself is cosmetic, but every `mcp__*` call —
including calls that structurally cannot be a destructive Bash command — pays a `PreToolUse`
round-trip through `guard-destructive.sh`, `thing-orchestrator.sh`, and `runaway-brake.sh` before
any permission prompt is shown. In the session that surfaced this, the first such call never got a
permission answer at all (`AbortError: Tool permission stream closed before response received`,
~2m17s), and the second, already-queued call auto-cancelled. Whether the extra `PreToolUse` hop
contributed to that timeout is `[unverified]` — the hooks themselves ran in ~24ms each — but a
hook scoped to "shell commands" running on tool calls it was never meant to guard is the finding
regardless of that timeout's cause.

**Proposed fix (found, NOT applied — deferred):** Give `guard-destructive.sh` an early, silent
no-op for any tool call that isn't shell-shaped, using the `tool_name` field the hook payload
already carries:

```bash
tool_name="$(printf '%s' "$payload" | jq -r '.tool_name // empty' 2>/dev/null || true)"
[ -n "$tool_name" ] && [ "$tool_name" != "Bash" ] && exit 0
```

placed before the jq/python3 command-extraction attempt, with the same jq/python3 fallback (or a
plain string-match fallback) the rest of the hook already uses, so it degrades no worse than today
when both parsers are absent. This does not touch `hooks.json`'s matcher — `thing-orchestrator.sh`
and `runaway-brake.sh` share that matcher and may have their own reasons to see every `mcp__*`
call; only `guard-destructive.sh`'s command-string logic is provably Bash-only. **This diff has
deliberately not been applied.** It is recorded here as a found-and-reasoned fix for a maintainer
to evaluate and land on its own terms, not as a patch pushed through review substitution.

**What works (for now):** Nothing has been changed. This entry exists so the finding and the
reasoned fix are not lost, while the actual edit to `guard-destructive.sh` waits on a maintainer
who can weigh it against `thing-orchestrator.sh` and `runaway-brake.sh`'s use of the same matcher.

**How to apply:**
- If you hit the DEGRADED warning on an `mcp__*` call with no `command` field, this is why — it is
  not a real missing-binary problem for that call.
- Do not apply the diff above without maintainer review; it is deferred, not vetted, and is
  recorded here specifically so the finding isn't lost rather than as a ready patch.
- Separate, upstream-shaped issue (not a RavenClaude fix): the
  `AbortError: Tool permission stream closed before response received` / auto-cancel pattern looks
  like a VS Code Copilot Chat ↔ Claude Code SDK permission-prompt bridge issue specific to the
  `sdk-ts` / session-target entrypoint family — the same family as the untitled-session-URI entry
  above. RavenClaude cannot make a VS Code permission dialog render; cross-link rather than
  attempting a fix from this side.

**Trace:** Found in a consumer project (BTCSI) VS Code Copilot Chat "Claude" session-target
session with no project directory (`cwd` was `~/.copilot/chats/<uuid>`), 2026-09-10, while
investigating a stalled tool-permission prompt. Both of the session's own tool calls demonstrated
the defect directly.

---

## 2026-09-09 — An MCP launcher that blocks at session start or plugin reload hangs the host UI: `npx` without `-y` prompts on stdin, which is the MCP transport, so nobody can ever answer

**Context:** In a consumer project (BTCSI), starting a new VS Code Copilot Chat session with
Session Target "Claude" was very slow to become usable, and sometimes stuck entirely — text
enterable, Send never enabled, eventually erroring. It looked at first like a RavenClaude problem,
since RavenClaude is the largest, most visible tooling wired into that project.

**What we tried first:** Investigated RavenClaude's skill-catalogue size, `.claude/settings.json`
hook wiring, and a project-local `SessionStart` hook that hard-blocked with `exit 2`. That hook was
a genuine bug (fixed separately as that project's own FM-017) but it was locally authored, not
RavenClaude-templated, and the symptom persisted after fixing it. The first pass then inspected one
suspected plugin (a Playwright launcher) in isolation and concluded it was the cause — a mistake
corrected below.

**Why it failed:** The remaining cause was an editor agent plugin installed per-editor-profile
under `~/.vscode-remote/data/agentPlugins/`, not per-repo — invisible to `git status`, referenced
by no file in the project, updating out-of-band with no local commit. An MCP server declared by a
plugin is spawned during a new session's startup handshake, with its stdin/stdout wired to the
host as the protocol transport; the composer's Send button stays disabled until that handshake
settles. So anything that makes the launcher block, blocks the UI, and the responsible subprocess
is invisible from the editor, which surfaces only "Send doesn't work." Session start is not the
only trigger — any plugin-system reload re-spawns the whole MCP set with the same handshake cost
mid-session, so the symptom can appear on the second prompt of a session that opened fine. The
tell is that the agent-host process is newer than the session it belongs to (observed: session
created 00:13:47, host started 00:15:49, MCP spawn completing 00:16:07 — ~18s of dead composer on
an already-warm cache). Three blocking behaviours, descending severity: (1) `npx` without
`-y`/`--yes` asks `Ok to proceed? (y)` on stdin on a cold cache — but stdin belongs to the MCP
protocol, so no human and no client will ever answer it, making this an unbounded, completely
silent hang, and the sharpest finding here; (2) floating version specs (`@latest`, `:latest`,
`--prerelease`) force a registry round-trip on every cold start, bounded by network speed but paid
every session; (3) container starts (`docker run ...:latest`) need a reachable daemon plus a
possible image pull. Critically, as audited 2026-09-09 across every installed plugin (not just the
suspect), the originally-suspected Playwright launcher does pass `-y` and only ever stalls on
network, never hangs — the real unbounded-hang candidate was a different, unrelated plugin running
`npx <pkg>@latest` with no `-y` at all. Inspecting only the suspect had confirmed a plausible story
instead of testing it; the full inventory is what produced the right answer.

**What works:** Warm the package/image caches so the launcher resolves locally rather than over
the network (converts the prompt-hang into a non-event), and remove plugins you don't use — every
installed plugin declaring a server adds startup cost to every session whether or not you ever
call its tools. Deliberately not recommended: hand-editing `.mcp.json` inside an installed plugin
directory to add `-y` or pin a version — it works until the next plugin update overwrites it, and
produces a machine whose behaviour can't be reproduced from any repo state. Separate a stall from a
hang before reaching for a fix — they have different causes and remedies, and static config
analysis can't tell you which one you're in; live process state can. Launchers parked in normal
idle sleep (`ep_poll`, `do_wait`, `futex_wait_queue`, Linux/procfs `wchan` states) are waiting out a
spawn and will recover — warming a cache is the fix. A launcher blocked reading stdin never
recovers, because stdin is the transport — only pinning or removing it helps. Cost is per agent
host, not per machine: each host spawns its own complete MCP set, so two concurrent hosts (e.g.
Claude and Copilot side by side) pay both the spawn wait and the memory twice (~1.2 GB resident in
the observed case) — the concrete argument for keeping bundled servers few and lazy. This confirms
and sharpens RavenClaude's own existing rule at
[`docs/best-practices/bundled-mcp-servers.md`](../best-practices/bundled-mcp-servers.md) (pin the
version, recommend-don't-bundle) and the classification already in
[`plugins/qa-test-automation/CLAUDE.md`](../../plugins/qa-test-automation/CLAUDE.md) /
[`plugins/frontend-engineering/CLAUDE.md`](../../plugins/frontend-engineering/CLAUDE.md) /
[`plugins/web-design/CLAUDE.md`](../../plugins/web-design/CLAUDE.md) (Playwright MCP: recommend,
don't bundle, never a bundled auto-start) — those were justified as a supply-chain/trust concern;
the gap this incident fills is that an unpinned or non-`-y` launcher is *also* a
startup-availability concern that can hang the host UI unboundedly, and the `-y`-prompts-on-stdin
mechanism wasn't previously stated anywhere.

**How to apply:**
- If you bundle or auto-launch an MCP server: pass `-y`, pin an exact version, and — if you
  control the server's own implementation — have it defer expensive initialization (browser
  launch, model load, network warmup) until its first real tool call rather than doing it in the
  process's startup path. This is a property of the server binary itself, not something a plugin
  author can configure via `plugin.json`'s `mcpServers` block: RavenClaude currently spawns every
  declared server eagerly at session start regardless of `defaultEnabled`, and
  `bundled-mcp-servers.md` Step 3 is explicit that a bundled server cannot be made dormant that
  way. An eager, unpinned, non-consenting launch is a session-availability risk, not only a
  supply-chain risk.
- When diagnosing "the agent tooling is slow or hung," don't assume RavenClaude just because it's
  the biggest thing wired in. Check for other agent plugins installed into the same editor
  profile — grep the suspect config/command against the RavenClaude checkout; no hit means a
  different plugin ecosystem. Watch for marketplace name collisions when triaging (e.g.
  RavenClaude's own `power-platform` plugin vs. the unrelated `microsoft/power-platform-skills`
  marketplace) — that similarity misdirected the first pass here.
- When a plausible culprit is identified, still enumerate the whole population before concluding —
  inspecting only the suspect confirms a story, inventorying everything tests it.
- Maintainer suggestion, not yet implemented: `scripts/check-mcp-attribution.py` already parses
  every `mcpServers` block in `plugins/*/plugin.json` at PR time — flagging a missing `-y` or a
  floating tag on RavenClaude's own bundled servers there would turn this rule from advisory into
  enforceable for RavenClaude's own plugins. That is distinct from the consumer project's runtime
  audit tool, which scans a live machine's editor-profile directory and checks cache state — a
  different tree and lifecycle from a PR-time gate over this repo's own plugins.

**Trace:** Originated in a consumer project (BTCSI) session diagnosing a stuck Send button under
VS Code Session Target "Claude"; documented there as FM-018 alongside a static audit of installed
agent-plugin MCP launchers (8 local MCP servers across ~20 installed plugins). Revised 2026-09-10
after the full inventory corrected the original single-plugin misattribution; plugin names are
omitted above because they are machine-specific and volatile — the transferable content is the
mechanism and the inventory-before-concluding method. Extended the same day after the symptom
recurred mid-session on a plugin reload rather than at session start. Companion best-practice
covering the runtime/orphan-accounting side of MCP cost:
[`docs/best-practices/audit-mcp-runtime-cost-not-just-launcher-config.md`](../best-practices/audit-mcp-runtime-cost-not-just-launcher-config.md).

---

## 2026-09-09 — A skill-catalogue prune script that skips symlinks doesn't shrink anything `ravenclaude setup` wired

**Context:** A consumer project hit "prompt token count exceeds the limit" in GitHub Copilot
Chat/CLI. Both surfaces read `.claude/skills/*/SKILL.md` and inject name+description every turn —
attributed to VS Code's native "Agent Skills" feature; confirmed for Copilot Chat, `[unverified]`
for the Copilot CLI half and for the "every turn" frequency, which the diagnosis assumed by
analogy rather than checking independently. The project had a local prune script, ran it the day
before — the error recurred anyway.

**What we tried first:** Trusted the prune script's own report ("0 entries to cut") as proof the
catalogue was already minimal, and looked elsewhere for the regression (session history growth,
instruction-file bloat, MCP overhead).

**Why it failed:** The prune script explicitly skipped every symlink (`[ -L "$d" ] && continue`,
comment: "leave the marketplace wiring alone"). It could only ever shrink in-repo copies of
marketplace bundles. Symlinks made up 208 of 231 entries (~90% at the time of this incident) —
everything `ravenclaude setup --with-plugin <name>` wires in bulk via `wire_plugin_skills()`. The
"0 to cut" report was true and completely misleading: the overwhelming majority of injected cost
sat in a category the tool structurally couldn't see. Local pruning of symlinked content is undone
on the next `ravenclaude setup`/update since `wire_plugin_skills()` re-wires the full roster
unconditionally, with (at the time) no concept of persisted exclusion.

**What works:** Treat wholesale-wired content as first-class in any local curation tool, not
exempted. A curation tool that only touches what it directly owns while silently reporting "0 to
fix" on the majority of actual cost is worse than no tool — it should report what category of
content it structurally cannot see, not stay silent about its own scope. The durable fix is making
the wiring step itself consult a persisted policy, not a better prune script. Both halves have
since landed: the consumer project's prune script now reports both categories (in-repo and
symlinked) instead of skipping the latter, and `ravenclaude-core` 0.321.0 added
`is_skill_wiring_denied()` / a `skills.deny_plugins` posture key so `wire_plugin_skills()` itself
can honor a persisted exclusion — see
[`docs/best-practices/bulk-wiring-needs-persistent-exclusion-policy.md`](../best-practices/bulk-wiring-needs-persistent-exclusion-policy.md)
for the general rule this landed fix follows.

**How to apply:**
- When a repeatable install/setup/generate step writes into a directory a human or downstream tool
  also curates, check whether it's idempotent-and-full-overwrite or additive-only before
  designing an exclusion pass.
- Before trusting a "nothing to do" report, verify the tool's own scope — what category of content
  can it structurally not see. Measure the actual byte/token cost before and after any prune,
  rather than trusting an entry count alone as a proxy for prompt cost.

**Trace:** Originated diagnosing a Copilot Chat/CLI "prompt too long" recurrence one day after an
apparent fix; generalized from the specific fix to the underlying pattern. Rule form:
[`docs/best-practices/bulk-wiring-needs-persistent-exclusion-policy.md`](../best-practices/bulk-wiring-needs-persistent-exclusion-policy.md).

---

## 2026-07-29 — A newly-written audit harness produced 3,337 findings, ~99% false. Verify the instrument before you fix the subject.

**Context:** Looping a UI/UX audit over both dashboard surfaces (portal + the shipped standalone) until two consecutive passes came back clean. The harness drove headless Chrome and measured real computed layout — contrast ratios, pointer-target geometry, resolved tokens — across 21 routes x 4 viewports x 2 themes.

**What we tried first:** Reading the harness's first report as a report about the *dashboard*. It opened at 94 findings, peaked at **3,337**, and every one carried precise, credible numbers ("contrast 1.00:1", "target 46x24 and crowded"). Nothing crashed; the tool exited 0.

**Why it failed:** About 99% of those findings were the harness lying, across six successive wrong checks — and in each case the wrong implementation is the one a competent person writes first. A DOM-ancestor backdrop walk called a perfectly readable badge "invisible at 1.00:1" (an `absolute; bottom:-16px` badge paints over the page, not its parent's fill). Switching to `elementsFromPoint` was worse — it returns elements *above* the target, so a fixed banner became the "backdrop" of the header it covered. An accessible-name check that never resolved `<label for>` reported 15 correctly-labelled inputs as unnamed. `el.focus()` plus a computed-style diff reported 3,187 elements with "no focus indicator" — `.focus()` does not match `:focus-visible`, and an *unfocused* element's computed `outlineStyle` is `none` for nearly everything. A bare `bbox < 24x24` test flagged 2,397 diagram toggles because it implemented WCAG 2.5.8 without its spacing/inline/UA exceptions. And a hand-rolled visibility test manufactured 185 "overlapping targets": Chrome implements a **closed `<details>`** with `content-visibility: hidden`, not `display: none`, so 126 of 128 collapsed cards kept layout boxes and their invisible contents piled up at the same coordinates. Acting on the batch would have made the product worse in at least four places.

**What works:** Treat a new measuring tool's first output as a claim about the tool. Three cheap steps, in order: (1) **implausible volume is a bug report about the checker** — 2,397 findings on one component is not credible for a codebase in daily use, and this alone caught three of the six; (2) **trace exactly one finding to its source** before fixing anything — six of six bugs fell to a single lookup each; (3) **ask the platform instead of modelling it** — `Element.checkVisibility()` existed and was correct, while the hand-rolled equivalent encoded our beliefs rather than the behaviour. Then **mutation-test between clean passes**: reintroduce two or three of the defects you just fixed and confirm each is caught, because otherwise "0 findings" and "the checker is broken" are indistinguishable.

**How to apply:**
- Before acting on a batch from any checker you just wrote, verify one finding against a source that did not come from the same code path (read the source it names, do the arithmetic, check the primary doc).
- After fixing any real defect, spend one grep asking how many siblings its *class* has — the browser audit found `--border` used as a text colour in one rule; a grep found a second the browser could not see because it coloured an SVG icon.
- Check the cause, not just the finding: a real 45px overflow named a correctly-scrolling 881px table as its culprit, because elements inside an `overflow-x: auto` container are legitimately wider than the viewport.
- State the coverage of any negative result. "No `minmax` grid overflows" was true at 375px and false at 320px.

**Trace:** Rule form: [`../best-practices/validating-a-measuring-instrument.md`](../best-practices/validating-a-measuring-instrument.md). Gate that came out of it: `scripts/check-css-token-hygiene.py` (Gate 174). PRs #814, #816.

---

## 2026-05-21 (late) — The "did you try X?" round-trip is a smell. Agents must enumerate alternative paths before declaring blocked.

**Context:** Matt ran ~136 cloud-flow creates in a customer DEV environment via service principal. The agent driving the script hit the Power Automate Management API with the SPN's token, got HTTP 401 (token `roles` claim was `null`), and stopped — reporting "this can't be done programmatically without Global Admin consent." Matt had to prompt the agent: *is there another way?* The agent then immediately found the Dataverse Web API workaround that was sitting right there with the same SPN already authorized.

**What we tried first:** Treating the Capability Grounding Protocol as a "check skills → state limitation" pipeline. The protocol said "consider partial progress" and "consider team composition" but didn't explicitly require enumeration of alternative implementation surfaces. So agents stopped at the first failure.

**Why it failed:** The protocol's failure mode wasn't dishonesty — it was incomplete reasoning under pressure. When one tool fails, the agent's instinct is to stop and report, not to brainstorm a sibling path. The user-prompt round-trip ("did you try X?") was the visible symptom; the missing structural step was the cause.

**What works:** Step 3 of the Capability Grounding Protocol now requires explicit enumeration of 2–3 alternative implementation paths, ranked by cost, with the next-easiest attempted *before* the blocked status can leave. The mandatory phrasing template changed from `"After checking [skills], I cannot…"` to `"After trying [A — outcome] and [B — outcome], I am blocked on…"` — the report now communicates effort and narrows the user's decision space. Per-plugin §5 sections carry domain-specific enumeration ladders (Power Platform: REST → SDK → CLI → portal-with-automation; PA Mgmt API → Dataverse Web API → Power Apps API → CDS plugin; web-design: grid → flex → subgrid; etc.).

**How to apply:**
- When stuck, brainstorm 2–3 alternatives same-outcome-different-surface. Rank by cost. Try the cheapest unattempted one before reporting.
- Blocked reports must list what was tried (with one-line outcomes) AND what was ruled out (with reason).
- Anti-pattern: asking the user to fix the original approach (e.g., "can you have your Global Admin grant Flows.Manage.All?") *before* demonstrating the lower-friction paths were tried.

**Trace:** PR #22 (marketplace 0.10.0, ravenclaude-core 0.7.0). Case study at `plugins/power-platform/knowledge/programmatic-flow-creation.md`. Memory: `feedback_alternate_methods_grounding.md`.

---

## 2026-05-21 (late) — Knowledge-bank pattern: when a production lesson is worth keeping, store it as a single source-of-truth file + compact inline priors on the affected agents.

**Context:** Two production lessons surfaced same-day that needed to land in the plugins: a curated "cutting edge yet simple" web-design reference set (Linear, Vercel, Raycast, etc.) and the Power Automate Management API trap + Dataverse Web API workaround. Both needed to be accessible to agents *immediately* on invocation, not lazily on user prompt.

**What we tried first:** Embedding the full brief in every relevant agent's prompt. Rejected on first read — agent prompts would balloon and the same content would have to be edit-amended across 4+ files every time the brief refreshes.

**Why the alternative also failed:** A standalone reference file with NO inline pointer in the agents means the agent doesn't know the rule exists until the user prompts it. That defeats the entire point of capturing the lesson.

**What works:** Hybrid pattern. Single source of truth at `plugins/<plugin>/knowledge/<topic>.md` with a `Last reviewed:` date, refresh trigger, source citations, and the full content. Plus compact inline priors (~10 lines) added to the 3–5 agents most likely to apply it, summarizing the rule and pointing at the knowledge file for depth. Plus a `Knowledge bank` sub-section in the plugin's `CLAUDE.md` indexing the files. Opinions are immediately active; the depth is on-demand; refreshes touch one canonical file.

**How to apply:**
- When a production lesson or external research finding is worth keeping, default to this shape — don't ask where to put it.
- The reviewed-on date is mandatory — references rot.
- Domain-tailor the inline priors per agent (visual-designer gets aesthetic priors; web-architect gets stack priors; flow-engineer gets API-surface priors).
- Version-bump the affected plugin minor. The plugin's catalog description in `marketplace.json` should mention the knowledge bank.

**Trace:** PRs #20 (web-design 0.2.0, design-references), #21 (power-platform 0.8.0, programmatic-flow-creation). Memory: `feedback_knowledge_bank_pattern.md`.

---

## 2026-05-21 (late) — Stacked-PR rebase choreography: squash merges break SHA chains. Plan for it.

**Context:** Across two big sessions today, ~8 PRs in two stacks all touched the same handful of files (`marketplace.json`, plugin `plugin.json` versions, `CHANGELOG.md`, `docs/architecture.md`, `repo-guide.html`). Every squash merge invalidated the downstream PRs' bases.

**What we tried first:** Hoping GitHub's auto-merge would handle the cascade. It didn't — the squash collapses commit SHAs, so the downstream PR's earlier commits no longer apply cleanly even though their content is already in main.

**Why it failed:** Squash merge creates a single new commit on main with a fresh SHA. The downstream PR's recorded base is the old branch SHA, which is now orphaned. Git can't trivially detect that the content is upstream because the SHAs differ.

**What works:** Treat each downstream PR as needing a rebase + regen after the upstream merge. Concretely:

1. Merge PR N → `git fetch origin main` → checkout downstream PR's branch → `git rebase origin/main`.
2. Expect conflicts on the shared files. Resolve manifest versions by re-bumping forward (if both wanted the same bump, downstream goes one higher). Resolve CHANGELOG by renumbering. For `repo-guide.html`, `git checkout --ours` (or `--theirs`); it's generated, regenerate after rebase completes.
3. After rebase: `python3 scripts/generate-repo-guide.py` → `git add repo-guide.html` → `git commit --amend --no-edit`.
4. If the downstream PR added a hook, the +x bit drops during replay — `chmod +x` + amend.
5. `git push --force-with-lease` → wait for CI → merge.

The "patch contents already upstream" message from `git rebase --skip` is the right behavior when the rebase replays a commit whose content already landed via a sibling PR.

**How to apply:**
- Plan the merge order before starting (foundational PRs first; HTML/docs regen PRs last).
- Don't wait for one PR's CI to clear before queuing the next — work in parallel.
- After each merge, do the rebase + regen on the *next* PR immediately, before kicking off its CI.

**Trace:** Sessions on 2026-05-21 covering PRs #14–#23 (12 merges total). Memory: `feedback_stacked_pr_choreography.md`.

---

## 2026-05-21 — A step that runs is not necessarily a step that gates: audit every CI check with a known-bad fixture

**Context:** Round-6 of the marketplace's self-review chain. PR 9/10 had added `rhysd/actionlint:1.7.7` as a Docker container action in `validate-marketplace.yml`. CI on commit `de21250` passed. Score moved to 91/100 (architect) / 87/100 (Team Lead) with "Test/verification depth = 10/10" specifically credited to the new actionlint step.

**What we tried first:** Treated `CI green` as proof of `CI correct`. The actionlint step ran, found nothing wrong with the repo, exited 0. Score went up. Plan agent and architect declared "internal review done."

**Why it failed:** A researcher dispatched to verify the CI behavior empirically returned a sharp finding: actionlint 1.7.7 has **no `-exit-code` flag**. By design it reports findings via stdout/stderr (which surface as PR annotations) but exits 0 regardless. I ran the sanity probe: injected a real YAML parse error, actionlint correctly reported it, then **exited 0**. The CI step that scored us a 10/10 was informational-only — it could never fail a build. Score retroactively corrected: R5 was actually 90, not 91. The Plan agent then identified the meta-pattern: *verification artifacts are being graded on presence, not efficacy.*

**What works:** Two interlocking practices.

1. **Shell-wrap any linter that doesn't exit nonzero on findings.** Replace `uses: docker://...` with a `run:` block that captures the binary's output and converts non-empty output into `exit 1`. Pattern:

   ```yaml
   run: |
     set -euo pipefail
     out=$(docker run --rm -v "$PWD:/repo" -w /repo <image>:<tag> -color 2>&1) || rc=$?
     rc=${rc:-0}
     echo "$out"
     if [[ -n "$out" ]]; then echo "::error::<name> reported findings"; exit 1; fi
   ```

   Keeps the pinned image (supply chain), keeps annotations, turns findings into a failing build.

2. **Audit every gate with a known-bad fixture.** For each CI step that claims to enforce a property, write a one-line repro that violates that property and confirm the step fails. Don't trust "green CI" until each gate has produced a red CI on its target violation class. In RavenClaude this is a 10-gate / ~5-minute exercise; the result is that "test/verification depth = N/10" becomes a defensible claim instead of a hopeful one.

**How to apply:**
- When a CI step uses a third-party action or binary, check its exit-code semantics before counting it as a gate. Common offenders: linters with `--report-only` defaults, security scanners that print but don't fail, custom scripts that `|| true` for "robustness."
- Before declaring a CI workflow "robust", run the audit-by-known-bad-fixture exercise. The script lives in `.github/workflows/validate-marketplace.yml` execution logs as the proof artifact — keep at least one CI run where each gate is exercised against a fixture that should trip it.
- The vague principle "a step that runs is not necessarily a step that gates" has a sharper actionable form: **"For every CI step, prove it can fail by introducing a known-bad input."**

**Trace:** Commit history `cfbd5aa..PR13` in RavenClaude. PR 9/10 shipped the informational-only actionlint step. PR 12's shell-wrapper attempted to fix it but introduced its own bug — captured docker's image-pull stderr via `2>&1` and false-positive-tripped on a fresh CI runner. PR 13 fixed PR 12 by separating concerns (pre-pull image silently, capture only actionlint's stdout). Both failure modes — paper-tiger gate AND gate that gates the wrong thing — were caught by the same audit-by-fixture practice. **Corollary worth keeping in mind:** "a step that runs is not necessarily a step that gates" has a twin — "a step that gates can gate the wrong thing." The same fixture-pair exercise catches both. Codified as a runnable script at [`scripts/audit-gates.sh`](../../scripts/audit-gates.sh) and a canonical rule at [`docs/best-practices/ci-gate-audit.md`](../best-practices/ci-gate-audit.md); the audit script itself runs in CI as a meta-gate so any future regression in any gate's behavior gets caught at the next PR.

---

## 2026-05-11 — Rebase orphans local branches; `git branch -D` is the routine cleanup, not a destructive act

**Context:** PR #1 (`propose-lesson-diagrams-in-docs`) merged on GitHub with only the first commit. The inline-mermaid-demo commit was pushed to the feature branch *after* the PR merged, so local `main` and `origin/main` diverged by one commit each. After rebasing local onto origin and pushing, the original feature branch needed to be deleted locally.

**What we tried first:** `git branch -d propose-lesson-diagrams-in-docs` — the safe-delete that refuses if the branch isn't merged.

**Why it failed:** Safe-delete checks by **SHA reachability**, not content. The rebase replayed `d5ccc5b` as `cd496e0`, so the demo commit's content was on `main` but the original SHA was orphaned. Git's safety check correctly refused. The real problem was downstream: we'd added `Bash(git branch -D:*)` to both the project deny list AND the `guard-destructive.sh` PreToolUse hook, treating force-delete as inherently destructive — even after the user explicitly approved it, the hook double-blocked the command.

**What works:** `git branch -D` is the **correct** operation after any rebase that moved your local commits. It's not destructive in practice: the commits remain in `git reflog` for ~90 days, and (in this case) their content was already on `main` under a new SHA. The destructive layer of git is *reflog clearing* (`git reflog expire --expire=now --all && git gc --prune=now`), which is hard to do accidentally. Removed `git branch -D` from the project deny list and the hook deny patterns. Genuinely destructive operations stay blocked: `rm -rf /`, `git push --force`, `git reset --hard origin`, `git clean -fd`.

**How to apply:**
- After any rebase that moved local commits onto a new base, the original branch ref is orphaned — use `git branch -D <branch>` to clean it up. `-d` will refuse and the refusal isn't informative.
- Don't blanket-deny `git branch -D` in agent tooling. Reserve hook-level denials for commands that can actually destroy work (force-push to a remote, hard reset to a remote ref, `clean -fd`).
- Before reaching for `-D`, sanity-check the content is reachable elsewhere — `git log <branch>..main` should be empty when the rebased commits are on `main`. If it's not, the branch has work that isn't yet anywhere else.

**Trace:** Driven by today's PR #1 rebase reconciliation and subsequent `chore/apply-mermaid-lesson` cleanup. Codified in commit `f0d58d1` (ravenclaude-core 0.1.0 → 0.1.1) which removed `git branch -D` from the project deny list and `guard-destructive.sh`.

---

## 2026-05-11 — Mermaid for conceptual diagrams in markdown; ASCII only for folder trees

**Context:** Refreshing `docs/architecture.md` from the old central-hub + Expert-repos model to the plugin-marketplace model. The original doc used ASCII box-art diagrams (`┌──┐`, `└──┘`, etc.) and I had to decide whether to preserve that style or upgrade.

**What we tried first:** Kept the ASCII box-art format on the reasoning that "the rest of your docs use plain markdown and switching here would introduce a tooling dependency for one file." Flagged the choice as a judgment call I'd defer to Matt on.

**Why it failed:** GitHub renders `mermaid` code fences natively in markdown — no tooling dependency exists for the *reader*. The only "tooling" is the author learning mermaid syntax, which is shallow. ASCII box-art looks fine in a monospace editor and looks ragged in GitHub's web UI. For a repo whose primary collaborator access path is the GitHub web UI (per `docs/access.md`), defaulting to ASCII is the wrong tradeoff.

**What works:** **Use `mermaid` code fences for any conceptual or flow diagram** (system architecture, dispatch patterns, sequence diagrams, ER diagrams, state machines). **Keep folder trees as fenced code blocks** using the standard `├──` / `└──` characters — mermaid has no clean file-tree type and tree characters in monospace read fine. The architecture doc's marketplace diagram is the canonical example of the good shape (a `flowchart TB` with subgraphs for marketplace/plugins/consumer, plus `classDef` color coding).

**How to apply:**
- For new diagrams in any markdown doc, reach for `mermaid` first.
- Pick the diagram type that fits the content (`flowchart`, `sequenceDiagram`, `erDiagram`, `classDiagram`, `stateDiagram-v2`) instead of defaulting to `flowchart`.
- For file/folder trees, keep using fenced code blocks — don't try to coerce them into mermaid.
- See [`docs/best-practices/diagrams-in-docs.md`](../best-practices/diagrams-in-docs.md) for the full rule, including the "when to deviate" exceptions (e.g. agent prompt files read by Claude itself rather than viewed on GitHub).

**Trace:** Driven by Matt's directive ("I want the mermaid diagram") on 2026-05-11 during the lessons-loop scaffolding work. Codified in `docs/best-practices/diagrams-in-docs.md` and in personal memory under `feedback_diagrams.md`.

---

## 2026-05-07 — PSM discipline = quarterly QBR + per-partner success plan + visible health score (with EdTech overlay)

**Context:** Designed a `partner-success-manager` agent for an EdTech Partner Success Manager (communication / translation / rostering) who is also her team's AI champion.

**What we tried first:** A generic Partner Success Manager agent design with the standard PSM artifacts (profile, success plan, QBR, health, onboarding, touchpoints).

**Why it would have fallen short:** The generic version missed three context dimensions that turned out to dominate the role's reality: (1) **EdTech school-year cadence** — rostering crunch, EOY data, renewal cycles all map to the academic calendar, not Q1/Q2/Q3/Q4; (2) the user's **high-touch support background** — her instinct to invest time in upfront enablement to prevent downstream tickets is well-supported in PSM literature and should be reinforced, not flattened into a generic onboarding checklist; (3) her unique team responsibility as **AI champion** — every useful interaction with the agent is a candidate for a team-shared workflow library, not a one-off win.

**What works:** The PSM discipline rule is parallel to the PMP version: **quarterly QBR cadence + per-partner success plan + visible health scoring**. Plus three context overlays:
- **EdTech school-year awareness** baked into the onboarding checklist, success-plan milestones, and QBR prompts.
- **High-touch DNA reinforcement** in the onboarding flow (proactive demos, district IT alignment, integration validation up front).
- An **AI workflow library** that grows organically as useful patterns surface, with the agent prompting *"should this become a library entry?"* when it produces something reusable.

**How to apply:**
- For any role-design ask, hunt for the **discipline rule** first — the cadence + ownership + format triad that separates real practice from theater. PMP and PSM both have it; other roles likely do too.
- When the role lives in a specific industry (EdTech, healthcare, financial services), bake the industry's **calendar / cadence** into the templates, not just the agent description.
- When the user is the **AI champion** for their team, make the agent transparent about *how* it does things, so the user can replicate and teach the move. Treat agent interactions as training data for the team.
- A high-touch / proactive-setup philosophy is a real strength in PSM work — design for it explicitly, don't flatten it.

**Trace:** Researched 2026-05-07 against SaasPedia, Impartner, PartnerStack, PARTNERNOMICS, TSIA, and Gainsight QBR resources. Driven by Matt's request for an agent for his wife (new EdTech PSM, AI champion). Implemented in `.claude/agents/partner-success-manager.md` and 7 templates under `templates/partner-success/`.

---

## 2026-05-07 — PMP discipline = weekly cadence + single ownership + same format

**Context:** Building a PMP-grade `project-manager` agent for cross-domain consulting work.

**What we tried first:** An initial draft of a generic *"Tracker"* agent that maintained activity log, task list, and project tracker — useful but vague. No specific cadence, no ownership rules, no format constraints.

**Why it failed (would have failed in practice):** Without specific operational rules, *"tracking"* tools accumulate dust. A tool that's optional gets skipped; a tool that's vague gets gamed. The reason most consultants are *"not good at PM"* isn't laziness — it's that they have tracking artifacts but no enforcement around them.

**What works:** PMI's PMBOK 7 + the leading PM literature converges on three operational rules that make PM real:

1. **Weekly review cadence**, never skipped — when missed, the agent prompts.
2. **Single owner per item** — every RAID entry, every task, exactly one named person. No *"the team,"* no *"TBD."*
3. **Same format every time** — consistency is what makes status reports trusted.

Plus PMI's 7-element status report (overall status / timeline / achievements / upcoming milestones / active risks / budget / decisions needed) capped at ≤1 page.

**How to apply:**
- When building any tracking tool, agent, or skill: bake in the cadence + ownership + format rules. Don't make them optional.
- For consulting status reports: PMI's 7-element format, ≤1 page, every week.
- For RAID logs: weekly minimum review, immediate logging for critical items.
- For task lists: stale items (>7 days no update) flagged automatically; single owner enforced.

**Trace:** Researched 2026-05-07 against PMI's PMBOK 7 standard plus ProjectManagement.com / Asana / MPUG sources. Driven by Matt's request for a PMP-grade PM agent. Implemented in `.claude/agents/project-manager.md` and 5 templates under `templates/` (raid-log, task-list, status-report, activity-log, stakeholder-register).
