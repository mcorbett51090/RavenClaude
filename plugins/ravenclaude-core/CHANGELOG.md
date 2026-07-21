# Changelog — ravenclaude-core

All notable changes to the `ravenclaude-core` plugin. Versioning is semver; the `version` field in `.claude-plugin/plugin.json` (mirrored in the marketplace catalog) is the authoritative source of truth, and this file tracks the user-visible arc. Larger architectural narratives live in [`CLAUDE.md`](CLAUDE.md) milestones; this file is the scannable per-version log.

## 0.207.0 — 2026-07-21

### Added

- **New best-practice — "Build a capability as CLI + Skill first; reach for MCP only when the state lives in someone else's running system"** ([`best-practices/build-cli-plus-skill-first-reach-for-mcp-for-live-external-state.md`](best-practices/build-cli-plus-skill-first-reach-for-mcp-for-live-external-state.md), rule 35). The design-time selection heuristic — a Skill answers "how do we do X _here_?", an MCP server answers "what is true right now _over there_?" — so build CLI + Skill by default and reach for MCP only when the agent needs a live view of state inside another running system. This is the **upstream** complement to the runtime [`mcp-tool-context-is-a-budget`](best-practices/mcp-tool-context-is-a-budget-enable-only-what-you-need.md) rule (that one prunes the servers you already enabled; this one decides whether to add one at all). Sourced from the recurring Claude-community scan ([2026-07-21](../../docs/research/2026-07-21-claude-subreddit-scan/README.md)); token figures marked `verify-at-use`, the discriminator is the durable part.

**Cost:** none to any always-loaded surface — one additive best-practice file + a README index row (34 → 35 rules). **Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

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
