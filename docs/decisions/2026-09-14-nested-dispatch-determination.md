# Determination — may a called agent call agents? (2026-09-14)

**Question asked:** *Is allowing the called agents to call agents possible, and is it desirable?*

**Short answer:** **Possible — yes, on the platform, three layers deep by default. Enabled in this roster — no, and now by declaration rather than by accident. Desirable — not as a default; one bounded shape is sanctioned, per agent, by name, with a reason.** What shipped to make that verdict hold and stay visible is listed at the end.

Every platform claim below is `[docs-verified 2026-09-14]` against the Claude Code [sub-agents](https://code.claude.com/docs/en/sub-agents) and [hooks](https://code.claude.com/docs/en/hooks) references and the `anthropics/claude-code` changelog, retrieved this session. Roster claims are measurements run this session, with the command. **Later the same day the core platform claims were also `[observed live]` on Claude Code 2.1.271** with the maintainer's signed-in account — five real runs of `main → coordinator(s) → leaf`; § 7 has the runs, the ledgers, and the four things the live runs taught that the docs did not.

---

## 1. Is it possible? — Yes. The platform nests by default.

| Fact | Source |
| --- | --- |
| A subagent **can spawn subagents of its own, up to three layers below the main conversation**, by default. | sub-agents § "Let subagents spawn their own subagents"; **`[observed live 2.1.271]`** — `main → coord1 → coord2 → leaf` completed with the leaf's ledger line carrying `caller_agent_id` = coord2's real `agentId` (§ 7) |
| The cap is `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`; `1` turns nesting off; at the limit Claude Code withholds `Agent` from every subagent except a fork (whose `Agent` call then errors). | same; **`[observed live]`** — with a 4th layer requested, the 3rd-layer subagent reported *"no dispatch tool … only a Read tool is provided"* although its definition lists `Agent`; the ceiling is a **silent tool removal**, not an error on the call (§ 7) |
| History: v2.1.172–2.1.216 nested up to five deep, uncapped; v2.1.217–2.1.218 defaulted to one (off); **v2.1.219 raised the default to three**. | same, the version note |
| The thing that keeps one subagent from spawning while nesting is on is its **`tools:` allow-list** — *"omit `Agent` from its `tools` list or add it to `disallowedTools`"*. | same |
| In a **subagent definition**, `Agent(type)` scoping is **ignored**: listing `Agent` lets it spawn *anything*; the parenthesised type list does nothing. The `Agent(agent_type)` syntax applies only to an agent running as the main thread with `claude --agent`. | sub-agents § "Restrict which subagents can be spawned" |
| The built-in **`general-purpose`** and **`claude`** types hold **"every tool available to subagents"** — `Agent` included. `Explore` / `Plan` are read-only. | sub-agents § "Built-in subagents" |
| Hooks from settings files and plugins **run inside subagents**; `PreToolUse` / `PostToolUse` fire there and the input carries the caller's **`agent_id`** and **`agent_type`** as top-level fields. `agent_id` is *"present only when the hook fires inside a subagent call"*; `agent_type` alone also appears on a `claude --agent` session, so nesting keys on `agent_id`. | hooks § "Where hooks are configured", § "Common input fields" |
| Only the **top-level subagent's summary** returns to the main conversation; intermediate output never does. The UI shows nested subagents as a tree. | sub-agents § "Let subagents spawn…" |

So the platform not only permits it, it defaults to it. "Sub-agents do not spawn other sub-agents" — the line in [`rules/agent-collaboration.md`](../../plugins/ravenclaude-core/rules/agent-collaboration.md) and in 180+ plugin constitutions — is a **house rule, not a platform limit**, and until this pass the repo's own prose in places said the opposite (`subagent-isolation-and-tooling.md` stated subagents *cannot* spawn; corrected).

## 2. Is it enabled in this roster? — No, and it was only true by coincidence.

Measurement (`python3 scripts/check-nested-dispatch.py --check`, this session):

```
agents with tools: 623   granting dispatch: 0 (exempt 0)   exemptions on file: 0
✓ no shipped agent can call agents: every `tools:` allow-list omits `Agent` / `Task` / `*`
```

All 623 shipped agents omit `Agent`, `Task` (the pre-rename alias) and the `"*"` wildcard from `tools:`. That is what actually held the rule — **not** the prose, and not [`guard-recursive-spawn.sh`](../../plugins/ravenclaude-core/hooks/guard-recursive-spawn.sh), which is a `PostToolUse` grep over an agent's *text* that warns and cannot block. Nothing would have noticed one file adding `Agent`, and `Agent(scout)` would have read as "may dispatch scout only" while meaning "may dispatch anything, at any tier".

**What the roster cannot control** — named so nobody reads "0 granting" as "0 nesting":

1. The built-in `general-purpose` / `claude` subagents carry `Agent`. A Team Lead that dispatches `general-purpose` has dispatched something that can nest, on every host with the default depth.
2. A project-local `.claude/agents/*.md` in a consumer repo can list `Agent`. Gate 289 reads this marketplace's `plugins/*/agents/`, not the consumer's tree.
3. A fork inherits the conversation's tool list, `Agent` included.

Those three are why the **meter**, not the gate, is the second half of the answer (§ 5).

## 3. Is it desirable? — Not as a default. Here is the cost model.

The tier doctrine ([`model-tier-delegation.md`](../../plugins/ravenclaude-core/knowledge/model-tier-delegation.md)) says delegation saves money only when (a) the volume moves to a cheaper tier and (b) the boundary crossings stay small. Nesting works against both, and against a third thing the doctrine relies on:

| Cost | Why nesting incurs it |
| --- | --- |
| **The handoff tax is paid where the Team Lead cannot see it.** | Each nested hop is a brief written + a report re-read, at the *caller's* tier. Only the top summary reaches the main thread; the intermediate reports — the very thing `handoff-tax-meter` exists to flag as `report_over_cap` — are consumed by a subagent that receives no advisory and has no `Max output` contract of its own. |
| **The tier of the whole subtree is whatever the caller chose.** | A `general-purpose` worker on an Opus session inherits Opus. Its children resolve by the same order (per-invocation → frontmatter → env → main model); an un-pinned `Explore` it spawns is an Opus `Explore`. `explore-tier-pin` does fire inside subagents (hooks run there), so *that* sink is closed — but nothing pins the caller's other choices, and the caller is a cheap-or-mid model making tier decisions the doctrine reserves for the frontier orchestrator. `[unverified — whether a nested child's "main conversation's model" fallback means the top session or the immediate parent is not stated in the reference]` |
| **Recovery runs sideways instead of up.** | The escalation ladder says a botched worker re-dispatches *one tier up*, decided by the Team Lead. A subagent that can re-dispatch does the classic pay-twice thing — the same tier, a longer brief — with no one above it to notice. |
| **The single-orchestrator invariant is what makes the ledger a denominator.** | "Cost per completed task" needs every dispatch attributable to one decision-maker. With nesting, `dispatch-ledger.jsonl` still records every hop (hooks fire inside subagents), but the *reasoning* behind a hop lives in a subagent transcript the Team Lead never reads. |
| **Blast radius compounds.** | A subagent inherits its parent's permission mode and cannot be restricted below it; `tools:` is the only cap. `Agent` in `tools:` is an *unscoped* grant (the type list is ignored), so an agent with `Agent` can dispatch a `general-purpose` with every tool, whatever else its own allow-list omits. |

Against that, the platform's own stated use case is real: *"a reviewer subagent that dispatches a verifier per finding, so the intermediate output never reaches your main conversation."* That is precisely the shape where the intermediate output is *supposed* to be discarded — and where the tax is small because the verifiers are read-only and cheap.

### The verdict

| Shape | Verdict | Why |
| --- | --- | --- |
| **Any shipped agent listing `Agent` / `Task` / `"*"` in `tools:`** | **Denied by default** — Gate 289 fails the build | unscoped grant; the type list is ignored; the costs above |
| **A frontier-tier parent that fans out to fast-tier, read-only leaves** (the reviewer → verifiers shape) whose leaves cannot themselves dispatch | **Sanctionable, per agent, by name** — an entry in [`tests/fixtures/nested-dispatch-exemptions.json`](../../tests/fixtures/nested-dispatch-exemptions.json) whose reason says why the observability and tier costs are acceptable *for this agent* | the one shape where the tax is bounded (leaves return little) and the tier decision is made by a frontier model, which is what the doctrine requires of an orchestrator |
| **A mid/fast-tier agent that dispatches** | **Denied** — do not exempt | a cheap model making tier decisions is the failure the doctrine's "planning quality is the floor" row names |
| **Nesting deeper than two layers below main** | **Denied** — do not exempt | the summary of a summary of a summary; nothing in the ledger can price it |
| **Nesting via the built-in `general-purpose` / `claude` / a fork** | **Cannot be gated here; is metered** — `nested_dispatch` advisory + `nesting` row in `dispatch-summary`; consumer off-switch is `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` | the roster does not own those definitions |

No exemption is on file today. The first one to be added must pass the shape test above and its reason must name the leaf type(s) and tier — an exemption that says "orchestrator persona" and nothing else is the reasonless row Gate 289 rejects.

**Why not simply recommend `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` everywhere?** It is a consumer-side env knob, not something a plugin can set, and it also disables the sanctioned shape. The doctrine's "Knobs" table lists it as the consumer's off-switch; the marketplace's own control is the `tools:` line, which is what it ships.

## 4. What is *not* decided here

- **Whether to build the hook that could scope nested dispatch.** The declaration cannot scope it (type list ignored), but a `PreToolUse(Agent)` hook *can*: the input carries `agent_id` / `agent_type` for the caller and `tool_input.subagent_type` / `tool_input.model` for the child, so a hook could deny any nested dispatch whose child is not read-only-fast, or whose caller is not frontier. That would turn the "sanctionable shape" row from a reviewed exemption into an enforced envelope. Not built this pass: no agent needs it yet, and the tribunal's high-blast rule says a *blocking* hook on the dispatch path is a design check-in, not a pass-3 addition. Recorded as the follow-up.
- **Agent teams** (`TeamCreate`, teammates as peer processes) are a different mechanism from nested subagents and are covered by [`dynamic-workflows.md`](../../plugins/ravenclaude-core/knowledge/dynamic-workflows.md) and [`cross-session-messaging.md`](../../plugins/ravenclaude-core/knowledge/cross-session-messaging.md); nothing here changes them.

## 5. What shipped for this determination

| Layer | Artifact | Binds? |
| --- | --- | --- |
| **Gate 289** — the declaration | [`scripts/check-nested-dispatch.py`](../../scripts/check-nested-dispatch.py) in `scripts/audit-gates.sh`: fails any `agents/*.md` whose `tools:` grants `Agent` / `Agent(...)` / `Task` / `"*"` without a reasoned exemption; fails a stale or reasonless exemption; an empty roster is not a pass; `--must-fail` proves all six grant forms fail and a clean list (incl. `Bash(a, b)`, `TaskOutput`, `disallowedTools: Agent`) passes | **yes** — CI |
| **Meter** — the observation | [`handoff-tax-meter.py`](../../plugins/ravenclaude-core/scripts/handoff-tax-meter.py) schema v2: records `caller_agent_id`, `caller_agent_type`, `nested`, `depth` (reconstructed from the caller's own ledger line; a stated lower bound when the caller was never seen spawned), the `nested_dispatch` flag + advisory naming the caller, layer, off-switch and this document; `dispatch-summary` gains a `nesting` row. Gate 285's hook test drives the nested path through the real bash contract (legs H1–H6) | no — advisory, by design |
| **Prose** | `subagent-isolation-and-tooling.md` (the stale "cannot spawn"), `rules/agent-collaboration.md` (hard layer = `tools:`, gated), `model-tier-delegation.md` § "Multi-hop delegation", `AGENTS.md` rule 11, the agent template, the `agent-quality-rubric` skill | no |
| **Prose, written under maintainer override** | `plugins/ravenclaude-core/CLAUDE.md` core-rule paragraph and `CHANGELOG.md` 0.323.0 entry — the tribunal's whole-file screen blocked every tool-mediated attempt (§ 6); applied 2026-09-14 from the shell after the maintainer overrode the rule for this task | no |

The existing `guard-recursive-spawn.sh` stays as the prose-level nudge it always was; it is no longer the only thing standing between the rule and a one-line edit.

## 6. A gap found while shipping: two files this host cannot edit

Every attempt to write `plugins/ravenclaude-core/CLAUDE.md` and `plugins/ravenclaude-core/CHANGELOG.md` this pass was hard-denied by the tribunal (`phase: hard-rule-deny`, seats `[]`, Sága records `thing-2026-09-14T22-11-14Z…`, `…T22-16-08Z…`, `…T22-16-44Z…`, `…T22-19-04Z…`; the same two files were denied at 15:57, 16:09, 17:12 and 17:39 in the earlier passes). The cause was isolated this session by running the screen itself — `thing-concerns.screen_always(catalog, "<path>\n<file content>")` on the *unmodified, committed* file — rather than inferred from the verdict:

| Observation | Source |
| --- | --- |
| The Sága record shows `tool_name: "Write"` with `bytes: 386594` for what this host presented as a find-and-replace edit. **Cursor surfaces every edit to the hook as a whole-file `Write`**; Claude Code's `Edit` sends only `old_string` / `new_string`. | Sága `tool_input` |
| The §B.9.3 hard rules (`srm.force-push`, `sce.curl-pipe-shell`, `xc.ragnarok-non-user-invocation`) are `always_screen` + `pre_llm_deny` and — deliberately, per the comment at the narrowing in `thing-decision.py` ("the §B.9.3 hard rules … still screen the FULL text") — run over the **entire write payload**, not the delta. | `thing-decision.py` § classify-payload |
| `screen_always` on the committed `CHANGELOG.md` returns `hard_rule_deny: True, hard_rule_concern: 'srm.force-push'`. The match is on the **wrapper-normalised variant**: two historical entries *document* the `-p` / `-P` git-global fix with a literal force-push example, and `_normalize_for_match` strips the global option, producing the exact string the trigger looks for. `CLAUDE.md` matches Ragnarök the same way — § "High-blast-radius commands" (v0.77.0) quotes the guarded invocation it is describing. | this-session run, output above |

**Consequence:** on a host whose edit tool is a whole-file write, any file that *documents* a hard-rule command becomes un-editable by an agent, permanently, regardless of what the edit adds. On this branch that is the constitution and the changelog — the two files a version bump is supposed to touch. This is an **observation about the hook's host contract**, not a defect in the rule: the rule is doing exactly what its comment says.

**Not done here, on purpose:** the file is tribunal substrate and the repo's own rule is that an agent does not loosen a hard rule to let its own write through. The two candidate fixes, for the design check-in:

1. **Screen the delta, not the document, for file shapes.** For `Write`, diff the payload against the on-disk file and run the §B.9.3 regexes over *added* lines only. Unchanged bytes were not introduced by this write, so this removes no coverage of anything the write *does* — a script that newly contains a force-push is still caught — while ending the freeze. `Edit`/`MultiEdit` already screen only the strings, so this makes `Write` consistent with them.
2. **Rephrase the two documented examples** in `CHANGELOG.md` and `CLAUDE.md` so the normalised text no longer matches (the way this document and the 0.323.0 release note below describe the triggers in prose). Cheaper, but it re-freezes the moment anyone documents a hard-rule command verbatim again, and it edits history to satisfy a screen.

Option 1 is the durable one and stays open as the design check-in (ledger `rc-6c598f5546e8`). **For this task the maintainer overrode the rule** (2026-09-14, 23:10 UTC): both edits were applied from the shell by a patch that read the on-disk files and inserted the new text, so the documented hard-rule examples never passed through an agent tool payload and the hard rules themselves were not touched. The release note below is retained as the record of what was applied.

### 0.323.0 release note (applied to `plugins/ravenclaude-core/CHANGELOG.md` under maintainer override, 2026-09-14)

**Added**

- **Determination: may a called agent call agents?** Possible — yes, the platform nests three layers deep by default (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`). Enabled in this roster — no, and now by declaration: all 623 agents omit `Agent` from `tools:`, which is the layer that actually binds (`Agent(type)` scoping is ignored in a subagent definition, so `Agent` in any form is an unscoped grant). Desirable — not as a default; the one sanctionable shape is a frontier-tier parent fanning out to fast-tier read-only leaves, exempted per agent by name with a reason. This document is the full record; the operating summary is `knowledge/model-tier-delegation.md` § "Multi-hop delegation".
- **Gate 289 — `scripts/check-nested-dispatch.py`** (marketplace CI): fails any `agents/*.md` whose `tools:` grants `Agent` / `Agent(...)` / `Task` / `"*"` without a reasoned entry in `tests/fixtures/nested-dispatch-exemptions.json`; a stale or reasonless exemption fails; an empty roster is not a pass. `--must-fail` proves all six grant forms fail and that `Bash(git a, b)`, `TaskOutput` / `TaskStop` and a `disallowedTools: Agent` pass clean. Until now the only guard was `guard-recursive-spawn.sh`, a grep over prose that warns and cannot block.
- **`handoff-tax-meter` sees nesting** (ledger schema v2). Hooks fire inside subagents and the input then carries the caller's `agent_id` / `agent_type`, so each ledger line records `caller_agent_id`, `caller_agent_type`, `nested`, and a reconstructed `depth` (1 = main thread; the caller's own depth + 1 when the caller was spawned in this session's ledger; else `2` marked `depth_is_lower_bound`). New advisory flag **`nested_dispatch`** names the caller, the layer, the off-switch and this decision; `rc dispatch-summary` gains a `nesting` row. This is how the three vectors Gate 289 cannot reach — the built-in `general-purpose` / `claude` types, a fork, a consumer's project-local agent — become visible. Gate 285's hook test drives the nested path through the real bash contract (legs H1–H6).

**Changed**

- **`knowledge/subagent-isolation-and-tooling.md`** — (1) "subagents cannot spawn subagents" was a platform claim and was false; it now states the house rule, the `tools:` layer that enforces it, and Gate 289. (2) The `CLAUDE_CODE_SUBAGENT_MODEL` section had the env var as step 1 of the resolution order; stale since v2.1.251 (it is step 3, a fleet default that per-invocation and frontmatter override); v2.1.257's `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` is the only thing that flattens a roster pin. Consequence stated: a consumer's plain env var no longer overrides the `opus` pin on the three merge gates.
- **`rules/agent-collaboration.md`** — the single-orchestrator sentence names the layer that binds (`tools:`, gated) and the sanctioned exemption shape.
- `AGENTS.md` step 11, the agent-definition template and the `agent-quality-rubric` skill state the `tools:` dispatch rule and Gate 289.

**Known**

- The host-contract finding in § 6 (whole-file `Write` screening freezes any file that documents a hard-rule command) is open as a design check-in; the two blocked edits were applied under a per-task maintainer override, not by loosening the rule.

## 7. What "tested" means here — first the boundary, then the live runs that moved it

The maintainer asked whether nesting was tested and worked. When this section was first written the honest answer was *no, not live*: this host had no Claude Code runtime, so the platform half was a sourced claim and only the meter and the gate had been executed. The maintainer then installed Claude Code 2.1.271 here and signed in, and **five live runs** were made the same day. The table is what stands now.

| Claim | Status | Evidence |
| --- | --- | --- |
| The **platform** lets a subagent spawn a subagent, three layers deep by default | **`[observed live 2.1.271]`** | `main → parent → leaf` (2 layers) and `main → coord1 → coord2 → leaf` (3 layers, three separate runs) all completed; each nested ledger line carries the caller's real `agentId` (e.g. leaf: `caller_agent_id: a463b346e67c5359b` = coord2's id, `caller_agent_type: coord2`). Runs cost US$0.10–0.15 each. |
| The **ceiling** is three subagent layers, and at the ceiling `Agent` is withheld | **`[observed live]`** | `main → coord1 → coord2 → coord3 → leaf` requested: coord3 (3rd layer) replied *"DISPATCH REFUSED: no dispatch tool … only a Read tool is provided"* — its definition lists `tools: Agent, Read`, its transcript shows zero tool calls, the leaf was never spawned. The cap manifests as a **silent tool removal**, not an error on the call. |
| The **meter** observes a nested dispatch | **executed, passed — live and synthetic** | The real `handoff-tax-meter.sh` fired inside each subagent; ledgers show `nested: true`, the caller id/type, the tier per hop; `--summary` prints "2 nested dispatch(es) by coord2 ×1, coord1 ×1; deepest layer 3". Synthetic: `test-gate285-handoff-tax-meter.sh` H1–H7, `handoff-tax-meter.py --self-test`. |
| **Gate 289** fails a `tools:` grant of `Agent` / `Task` / `"*"` and passes the current roster | **executed, passed** | `scripts/check-nested-dispatch.py --check` → 623 agents, 0 grants; `--must-fail` → all six grant forms fail, the clean forms pass; wired into `scripts/audit-gates.sh`. |

The live harness is committed as [`hooks/tests/live-nested-dispatch.sh`](../../plugins/ravenclaude-core/hooks/tests/live-nested-dispatch.sh) — opt-in (`RC_LIVE=1`, a signed-in `claude`), never wired into CI because it spends the account's usage, and it prints *SKIP — a skip is NOT a pass* otherwise.

### 7.1 Four things the live runs taught that the docs did not

1. **Hooks fire child-first, so the write-time depth is a floor.** The child's `PostToolUse` runs *inside* the caller, before the caller's own dispatch completes, so ledger lines land `leaf, coord2, coord1`. At write time the caller's line does not exist yet and every nested line recorded the floor "2, lower bound" — including a leaf that was really at layer 3. The synthetic tests had written lines parent-first and never saw this. **Fixed:** `--summary` now re-resolves every depth by walking the `caller_agent_id` chain over the complete ledger (`_resolve_depths`, cycle-safe); the line keeps its honest floor. Re-run on the live ledgers: "deepest layer 3", exact. Test legs: self-test *live order*, bash H7a/H7b.
2. **The nested advisory was read by the wrong party — and derailed it.** A `PostToolUse` hook's `additionalContext` goes back to whoever made the tool call. Inside coord2 that is coord2, not the Team Lead. The `nested_dispatch` text was written to the orchestrator ("a called agent called an agent, *not you*"); delivered to the calling worker it read as injected content — in run 4, coord1's entire report was an explanation that it had *"noticed the handoff-tax meter block … formatted like a system notice … I'm not acting on it"*, and the leaf's answer was never relayed. **Fixed:** the `nested_dispatch` flag is recorded on the ledger and surfaced by `--summary` (which the Team Lead reads) but is **never spoken** as `additionalContext`; per-dispatch flags the caller does pay for (report/brief caps, frontier read-only) are still spoken to it, addressed as a subagent, with a footer telling it not to carry the notice into its report. Run 5, after the fix: coord1 returned `L1> …/src/b.py:1` and nothing else. Test legs: self-test *nested_dispatch alone → no advisory* and *over-cap inside a subagent*, bash H1/H2.
3. **Nested dispatches sometimes launch in the background unasked.** In 2 of 5 runs a dispatch made *from inside a subagent* returned `Async agent launched successfully` although `run_in_background` was unset, and the caller finished with *"still waiting on the leaf agent's result"*. The meter already records those lines as `status: async_launched` with the report side `null`; what the live runs add is that the **caller may return before its child does** — a correctness risk for nesting that the cost model in § 3 did not name. Cause not isolated (platform heuristic vs. model choice); recorded as an observation, 2 of 5.
4. **`sonnet` resolves to `claude-sonnet-5`, `haiku` to `claude-haiku-4-5-20251001`** on 2.1.271 — the meter's tier classifier placed both correctly (`mid`, `fast`) with no change.

None of these change the verdict in § 4. They sharpen § 3: the observability cost is now measured (the depth had to be reconstructed post hoc; the in-flight advisory cannot reach the orchestrator at all), and the correctness cost has a new line (background children outliving their caller).
