# G1 — Problem inventory (consolidated): recurring-defect hardening

**What this is.** The one authoritative, deduplicated master list, merged from the three G1 miners
(`research-engineering.md` 11 classes, `research-guardrails.md` 14 classes, `research-product.md` 8
classes). The miners overlap heavily (macOS doors, fail-open, self-referential guards, presence-vs-
placement, twin drift, projection drift each appear in ≥2 files); this document collapses them to one
canonical class per real problem, citing every surface it spans. Every dated occurrence is carried
forward verbatim from a miner — **no occurrence was invented here**; where two miners cited the same
incident, the more precise citation was kept.

Reused, not re-derived (per scope): the count-drift structural fix already has a converged cross-model
plan pair at `../../../../forge-count-ssot/.ravenclaude/runs/forge/count-ssot/{plan-A.md,plan-B.md}`.

---

## Root causes

The three miners each derived a meta-pattern set independently (engineering: 4 root causes;
guardrails: a 5-mechanism "systemic gap" ranking; product: 6 shapes). They converge on **six** root
causes. Each is stated once; the class inventory tags every class to its primary + secondary cause.

| id | Root cause (one line) | Classes it spawns |
|---|---|---|
| **R1** | **Verification surface is blind to the failure surface** — the gate/linter is structurally incapable of seeing the real defect, so a passing suite is byte-identical whether the gate is present or absent. | P2, P4, P5, P10, P11, P12, P20 (and R1 is a co-cause of P1) |
| **R2** | **Duplication instead of derivation** — the same value is *stored* in many surfaces instead of *derived* in one, and every sync mechanism (`--fix`, self-heal, twin copy, hand-typed projection) becomes a cascade source. | P3, P13, P14, P17, P18 |
| **R3** | **Prose rule with no gate** ("a prose rule is a wish") — a discipline is written down but not machine-enforced, and each one recurred *after* being written. | P1, P2, P8, P19, P21 (and R3 is the meta-cause the whole run attacks) |
| **R4** | **Building to an unverified / guessed contract** — a plausible mental model of a tool/workflow/problem is treated as fact and drives expensive build; one primary-source read would have falsified it. | P15, P16, P20 |
| **R5** | **Fail-open where fail-closed was intended** — an error/else/edge path resolves to *allow* (or a crash's exit-1 reads as a pass), because Claude Code's contract makes only exit 2 blocking and the ergonomic default is permissive. The loud failure is the safe one; the silent one is dangerous. | P5, P6, P18 (co-cause of P1) |
| **R6** | **Tooling can't tell intent from description, or truth from a stale prior** — self-reference failures: a source-scan guard denies its own fix/test/docs; a stale "still-open" claim in a session-loaded file misleads the next agent; an adapter/escape-hatch loses the reason or is unreachable from the context that needs it. | P7, P9, P17, P19 |

**The strategy the root causes imply** (all three miners converge on this): not 21 point-fixes, but
**(a) an "audit the auditor" gate-introspection layer** (R1+R3, closes the P2/P3/P4/P5/P6 cluster at
once), **(b) finish the count-SSOT derive-don't-duplicate refactor** (R2, plan already converged —
owner settles the RC_BASELINE A/B fork), **(c) a small family of author-time lints** that convert the
highest-recurrence prose rules into gates (R3+R5+R6), and **(d) a generalized surface-parity gate**
(R1+R2, closes the two-generated-surfaces family P11/P12/P17).

---

## Class inventory

21 canonical classes after dedup. `RC` = root-cause tag(s). Occurrences are dated and ≥2 except where a
single deeply-measured incident is carried forward because the miners flagged its fix pattern as
directly generalizable (P9, P20 — noted inline). "Leverage" marks classes closed by a **shared**
mechanism (see the ranked table below).

### P1 — macOS / stock-toolchain portability doors
- **Surfaces:** `plugins/**/hooks/*.sh`, `scripts/*.sh`, the tribunal (`thing-orchestrator.sh`), `monitors/**`, the `ravenclaude` installer, Python 3.9-vs-3.10 helpers.
- **Occurrences:** bash-3.2 layout gate silently bypassed on every macOS session, PR #660 (`e7c769e2`, v0.193.0); `timeout` absent (exit 127) disarmed decision-review + tribunal, #664 (`8f361d32`, v0.195.0); BSD `grep` no `-P` → 12 anti-pattern hooks never fired, #666 (`add8bfaf`, v0.196.0); BSD `sed -i` killed `audit-gates.sh` at gate 7/87, #669 (`dae3d2a8`); tribunal `declare -A`×7 + C4 collision trap, #672 (`2ac5abd3`, v0.197.0); a **new** macOS parse break (`scripts/ravenclaude` apostrophe) landed **after all doors "closed"**, #885 (`8d54af2d`); the ruff step told you to run `pip` (absent on stock macOS), #873 (`400ec948`); GNU-only `find` in `newest_log()` → no push notification ever reached a macOS session, v0.222.2 (`CHANGELOG.md:1481-1493`).
- **RC:** R1 (invisible to Linux CI) + R5 (fails open on macOS only) + R3 (portability rule is prose).
- **Fix applied:** `hooks/_portable.sh` shim (`_rc_timeout`/`_rc_upper`/`_rc_pcre_match`, perl-backed); a portability discipline in the plugin CLAUDE.md; the load-bearing `validate-macos.yml` `runs-on: macos-latest` executing hooks under `env -i PATH=/usr/bin:/bin` (Gate 131), #679 (`5b0613d2`).
- **STILL LIVE / OPEN:** the portability rule is **prose, not gated at author time** — #885 broke macOS *after* every door was closed; the `macos-latest` runner executes hooks but does **not lint new scripts** for banned constructs before merge; `check-macos-portability.sh` coverage may not extend past `hooks/**` to `monitors/**` / launch entrypoints (product miner flagged, unconfirmed); `premise-gate.py` + `classify_claim.py` cited repo-relative but live at marketplace-root `scripts/` — a deferred **packaging move across 6 call sites** (v0.243.0).
- **Prevention (teeth):** a `PreToolUse(Write|Edit)` **author-time portability linter** (bash-3.2-safe itself) that DENIES a write introducing `declare -A`/`mapfile`/`${x^^}`/`shopt -s globstar`/unshimmed `timeout`/`grep -P`/`sed -i`/GNU-`find` unless routed through `_portable.sh`. Complements `validate-macos.yml` exactly as `enforce-layout.sh` complements `validate-layout.yml`.
- **Leverage:** single class but **highest recurrence in the repo** (18 door commits). Shares the *execution-based* backstop with P5/P6.

### P2 — Never-ran / mis-wired gate (green ≠ ran)
- **Surfaces:** `scripts/audit-gates.sh`, scaffolded `.github/` workflows.
- **Occurrences:** Gate 184 pasted inside the `--check` dispatcher → ran 0× in the full suite while the milestone claimed "registered in both"; full-suite grep for "184" = 0 matches; fix proved by assertion count 701→703, PR #864 (`890c45c3`, v0.243.0, `audit-gates.sh:6108-6122`). Gates 60 + 80 existed only in `--check`, no full-suite block — same shape 7 weeks earlier (`2026-06-23-gate-consolidation-audit.md:20`). Gate 179 self-documents the shape; Gate 192/CE-1 names it at scaffold scale (a missing companion `check-workflow-hygiene.py`).
- **RC:** R1 (green is not evidence) + R3 ("wired in both" is a prose claim, not a call site).
- **Fix applied:** a standing ritual comment on Gates 186-192 ("run the full suite and GREP ITS OUTPUT FOR THE GATE BY NAME"); 60/80 wired into the full suite in the 2026-06-23 audit.
- **STILL LIVE / OPEN:** the ritual is a **comment, not a gate** — nothing parses `audit-gates.sh` and asserts every "Gate N" header is reachable from an unconditional code path (not nested under a `--check N)` arm).
- **Prevention (teeth):** `check-gate-registration.py` — statically extract every `echo "-- Gate N:"` header + every `gate "..."` call site with enclosing scope; assert each header has a `gate` call in the unconditional region; cross-check the `Supported:` list. Must-fail fixture = the v0.243.0 paste-inside-dispatcher shape.
- **Leverage:** ★ closed by the **gate-introspection meta-gate** together with P3, P4, P5, P6.

### P3 — Gate-number collision + harness self-description drift
- **Surfaces:** `scripts/audit-gates.sh` gate headers + `--check` case labels + `Supported:` line + dispatcher count comment.
- **Occurrences:** two unrelated full-suite gates both numbered **104** (a grep-PCRE check and a Pipeline stats render) → addressing "104" could reach only one (`2026-06-23-gate-consolidation-audit.md:18`); the same audit found a stale dispatcher gate-count comment drifted from the real count.
- **RC:** R2 (harness self-description duplicated, drifts) + R1.
- **Fix applied:** manual renumber + count-sync in the one-off 2026-06-23 audit.
- **STILL LIVE / OPEN:** prevention is still a human eyeballing the next free number; the harness grew 68→~194 gates with no registry enforcing uniqueness; the 2026-06-23 sweep was one-off, not a standing check.
- **Prevention (teeth):** number-uniqueness check folded into `check-gate-registration.py` (reuses the same parse P2 needs) — assert no gate number appears twice with a different description.
- **Leverage:** ★ same gate-introspection meta-gate as P2/P4/P5/P6 — near-zero marginal cost.

### P4 — Hollow gate (input silently empties; "0 findings" == "0 opportunities to find one")
- **Surfaces:** any data-dependent gate in `audit-gates.sh`; zero-exit-code linters (actionlint/semgrep/SAST); container-probe gates.
- **Occurrences:** Gate 179 (FORGE G3b premise gate) self-documents: if the G2/G3 contract stops emitting `depends_on_claims`, it runs, finds no edges, passes green while checking nothing — now emits an explicit `UNWIRED` verdict (`audit-gates.sh:6092-6099`). `ci-gate-audit.md:15` founding case: actionlint 1.7.7 as a Docker action scored 10/10 for "verification depth" while structurally unable to fail a build (exit 0 regardless of findings), `lessons-learned.md:113-143`, PRs 9-13. Container-probe sub-case: checking only that a binary is on PATH, never that it can run (`ci-gate-audit.md:45`).
- **RC:** R1 (assertion is blind to whether its own data pipeline is alive).
- **Fix applied:** Gate 179's `UNWIRED` verdict class; the actionlint shell-wrap converting nonzero-output → `exit 1`; the container-usability-probe rule.
- **STILL LIVE / OPEN:** per-gate discipline only — no general **liveness-probe / canary** convention (a synthetic known-bad input every data-dependent gate must flag, distinct from its must-fail fixture, to prove the pipeline is connected). Gate 179 built it ad hoc; it isn't a documented pattern others copy.
- **Prevention (teeth):** add a third fixture category `must_flag_unwired_on` to the `ci-gate-audit.md` taxonomy (upstream field silently absent → gate must emit a distinct non-pass, non-generic-fail verdict). Generalize Gate 179 into the doc + the gate-introspection layer.
- **Leverage:** ★ gate-introspection meta-gate family.

### P5 — Exit-code severity: green-for-wrong-reason & fail-open-on-error (loud = safe, silent = dangerous)
- **Surfaces:** every `PreToolUse` enforcement hook; the tribunal tie-breaker/salvage; `audit-gates.sh` must-fail assertions.
- **Occurrences:** Gate 6 went 4/8→8/8 on macOS because deny subtests had been passing with **exit 1 (crash), not exit 2 (deny)** — half its teeth were counterfeit (`CLAUDE.md:1337-1339`, v0.193.0). The exit-code table: `declare -A`→2 (blocks, *loud+safe*); `shopt globstar`→1, `mapfile`→127, `${v^^}`→1 (silent fail-opens nobody reported) (`CLAUDE.md:1346-1355`). Tribunal tie-breaker `else → allow` resolved any out-of-protocol verdict to ALLOW, v0.205.1 #713 (`19494fdb`, Gate 14); same PR, `_emitted=1` set *before* the `jq` write (serialization failure → fail-open). Lenient JSON salvage could recover a garbage verdict into a *voted allow*, v0.205.0 (fixed with monotonic-tighten-only). `network_access` shipped as a quoted `"false"` (string, not bool) in the security-tighten direction while the gate was green (v0.216.0). Cursor silently allows on a malformed hook response where every other host fails closed, Gate 159/MH-13 (`audit-gates.sh:5660-5668`). `guard-memory-compaction.sh` explicitly re-names the class in v0.241.0.
- **RC:** R5 (permissive default / exit-code contract) + R1 (a bare nonzero must-fail can't tell crash from deny).
- **Fix applied:** `audit-gates.sh:1046-1051` asserts exit **2 specifically** (not merely nonzero); tie-breaker `else → posture` (deny for high-stakes); monotonic salvage; trap armed first + `_emitted` after the write; the exit-code contract in every new guard's header; the `security_deny` floor.
- **STILL LIVE / OPEN:** the exit-2 assertion and the fail-closed error branch are applied **per-hook by hand** — no blanket meta-check drives every enforcement hook's deny/error/else fixture and asserts the outcome is deny(2) or safe-noop(0), never a fail-open exit 1; no static check that hooks arm their EXIT trap before the first fallible op; the `declare -A → index-0 collision` (C4) rewrite trap is unaudited outside `thing-orchestrator.sh`.
- **Prevention (teeth):** a **hook exit-code / fail-closed execution audit** (drive each hook with malformed/empty/error input under a minimal PATH on macos+ubuntu; assert exit 2 or safe-noop) + a static lint that every verdict-resolving `case`/`if` chain ends in an explicit non-permissive default arm + a trap-ordering check.
- **Leverage:** ★★ shares the execution runner with P1; shares the "must-fail asserts exit 2" clause with the gate-introspection meta-gate; the verdict-default lint also covers P6.

### P6 — Malformed regex silently disables a catalog rule (swallowed compile error)
- **Surfaces:** `thing-concerns.py` trigger catalog; the comfort-posture `srm`/`sce` hard-rule table.
- **Occurrences:** `thing-concerns.py`'s matcher swallows a regex compile error so one bad pattern doesn't crash the whole scan — side effect: the broken rule matches nothing, silently, permanently (`audit-gates.sh:1820-1823`, Gate 16 comment). The same hazard is flagged live for the comfort-posture hard-rule catalog: "a typo in a hard rule does not fail loudly — it silently disables the rule" (`CLAUDE.md:2333-2335`, v0.244.0).
- **RC:** R5 (a swallowed error is a silent fail-open) — closely coupled to P7/P8 (all three are the trigger-catalog cluster).
- **Fix applied:** Gate 16 compiles every trigger regex in the `thing-concerns.py` catalog (must-fail fixture = a deliberately malformed regex) — **for that one catalog only**.
- **STILL LIVE / OPEN:** the comfort-posture hard-rule catalog (the one implicated in the v0.242.0/v0.244.0 incidents) is verified by a **manual one-time recompile**, not a Gate-16-shaped standing check.
- **Prevention (teeth):** generalize Gate 16 into a reusable `check-regex-catalog-compiles.py` (path + field selector) invoked once per regex-bearing catalog.
- **Leverage:** the regex-compile pass is part of the gate-introspection meta-gate; the catalog-lint is shared with P8.

### P7 — Self-referential guard denies its own fix / test / docs (source-scan matches prose)
- **Surfaces:** `guard-*.sh` hard-rule guards (`srm.force-push`, `sce.curl-pipe-shell`), `guard-premise.sh` T-PROSE.
- **Occurrences:** while fixing `srm.force-push` the guard denied a test harness, a JSON fixtures file, the bug report **twice**, and two source comments — each because it contained the pattern it documented (`CLAUDE.md:2223-2235`, v0.242.0 #861). The same day, `sce.curl-pipe-shell` denied the Edit that fixes the rule, a comment, and the self-matching test — **nine blocks of legitimate work in one session** whose only sin was describing the pattern accurately (`CLAUDE.md:2337-2343`, v0.244.0 #866). *This session's own miner hit it a third time:* `guard-premise.sh` T-PROSE denied two Write attempts of `research-guardrails.md` (dated incident text near a certainty stamp), and the `.ravenclaude/runs/**` exemption didn't classify the nested-worktree path — a **live, this-run instance**.
- **RC:** R6 (the guard has no representation for "this text is inside a fixture/comment/diff" vs "a live command").
- **Fix applied:** a **workaround only** — new fixtures assembled with `printf` instead of literals (keeps the literal out of a scannable file but doesn't generalize past newly-authored fixtures; a pre-existing comment or the guard's own source still trips it).
- **STILL LIVE / OPEN:** the repo names the real fix as **deliberately NOT built** (twice-deferred): a sanctioned exempt path or an honoured in-file marker, held pending a security review of the widened ignore-surface. This is **the highest-friction live remediation item in the guard layer** — and the nested-worktree exemption gap surfaced again this very run.
- **Prevention (teeth):** the sanctioned-exempt door — (a) an allow-listed `tests/fixtures/**` + `docs/**` prefix where intent-bearing hard rules downgrade to advisory, and/or (b) a required in-file sentinel the guard honours; **plus fix the `.ravenclaude/runs/**` exemption to cover nested worktrees.** Ship only after a red-team pass on the widened surface.
- **Leverage:** owner-gated (security review) — see decision seed #2.

### P8 — Fix-one-instance-and-stop / unscoped-regex-beside-a-scoped-sibling
- **Surfaces:** the comfort-posture trigger catalog (`pre_llm_deny`/`always_screen` rules); any batch-fixable pattern (advisory-hook stdin fallback).
- **Occurrences:** `srm.force-push`'s unscoped `.*` fixed (v0.242.0 #861 `5ec08426`) → **"#861 was half-done — `sce.curl-pipe-shell` had the same unscoped `.*`"** (v0.244.0 #866 `bcef661d`); the v0.242.0 milestone even *states the general rule* while leaving two more unscoped rules one screen away (`CLAUDE.md:2199-2211`, `:2310-2322`). The measuring-instrument corollary "a found defect is a sample of a class — grep for the class" (the `--border`-as-text-colour case). The stdin-path fallback shipped in waves: 66 hooks (#580 `8cfa9e30`) then 45 more (#605 `6eea7e18`).
- **RC:** R3 (enumerate-the-class is prose) + R6 (the fix targets the reported site, not the class).
- **Fix applied:** the codified rule "when you fix a pattern, enumerate every instance before you close it"; the force-push fix recompiled all 131 catalog triggers (syntactic validity only).
- **STILL LIVE / OPEN:** the enumerate-the-class step is **prose** — the recompile checks validity, not **scoping consistency**; nothing greps the catalog for a bare unscoped `.*` sitting in a block where a sibling uses an explicit excluded-character class.
- **Prevention (teeth):** `check-trigger-scoping-consistency.py` — group triggers by block/category; flag any bare wildcard across a command separator where a sibling uses an explicit `[|&;]`-excluding class; require the same pattern's other matches to be in the diff or waived. Would have caught both incidents statically.
- **Leverage:** shares the catalog-lint substrate with P6.

### P9 — Guard escape unreachable → tunnelled + shared-state collision across parallel agents
- **Surfaces:** `guard-premise.sh` / `log-probe.sh` ledger; any stateful `PreToolUse` guard with an env-var escape; session-keyed substrates (runaway-brake, thing runaway dirs — unaudited).
- **Occurrences (one deeply-measured incident; carried forward because the miners flag the fix pattern as directly generalizable):** the premise ledger keyed on `(CLAUDE_PROJECT_DIR, session_id)` — neither varies per agent — so a 6-agent run collapsed 49 `cwd` values onto one ledger (**14,322 events under one session_id**, 2,825 entries, 50 unresolved negatives); a negative in worktree A denied an unrelated module in worktree B; the escape `RC_PREMISE_OVERRIDE` was an **env var a `Bash` tool call can't pass to the hook process**, so a subagent that *ran* the control couldn't say so; one agent **routed around the hook via Bash heredocs**, one stranded a finished harness in a scratchpad, PR #870 (`4b6544e1`, v0.245.0, Gate 190). *"A guardrail whose only exit is unreachable does not get respected — it gets tunnelled."*
- **RC:** R6 (state keyed to the wrong boundary; escape in a channel the blocked context can't reach).
- **Fix applied:** scope the ledger key to the **git worktree** (derived from `cwd`, the one per-agent-varying field), recorder + gate sharing the derivation; a **file-based control** (`…/scopes/<scope>/control.md`, writable by the `Write` tool, four required keys) whose refusals are tested first. Gate 190 ships both halves with must-fail teeth.
- **STILL LIVE / OPEN:** the **generalizable principle is un-gated** — no standing check asks, for any *other* guard shipping an env-var escape, whether that escape is reachable from a subprocess; the other session-keyed substrates haven't been audited for the same parallel-agent collision.
- **Prevention (teeth):** a **subagent-safe-guard authoring checklist/fixture** — every stateful `PreToolUse` guard must (a) declare its state key + prove it varies per parallel agent (a 2-worktree fixture: A's record must not block B), and (b) expose a **file-based escape** whose *refusal* paths are tested. Gate 190's two-worktree teeth test is the template to copy.

### P10 — Self-certifying change (a gate re-authored in the same commit it guards)
- **Surfaces:** `audit-gates.sh` gates, checker scripts, hook test files re-authored alongside the code they check.
- **Occurrences (one incident; fix pattern generalizable):** Gate 51 was re-authored in the same commit that deleted a nav element it checks — the pass proves nothing unless an external oracle is untouched; proven not-weaker by an unchanged self-test file that still tripped all three of its own mutation tests (`CLAUDE.md:1729-1732`, v0.208.0).
- **RC:** R1 (a test changed in the same diff as the behavior it asserts is circular).
- **Fix applied:** an external, unmodified oracle left untouched by the re-authoring commit.
- **STILL LIVE / OPEN:** one-off manual arrangement — nothing flags "this PR modifies both a gate's assertion logic and the source path that gate exists to check" as a higher-scrutiny diff shape.
- **Prevention (teeth):** a CI heuristic that flags any PR touching both a gate-defining file and the source it targets, requiring an independent/external oracle (Gate 51's pattern) or an explicit reviewer sign-off — a surfaced flag, not a hard block (legitimate co-changes are common).

### P11 — Presence-not-placement / cross-surface parity regression (portal ↔ standalone dashboard)
- **Surfaces:** the marketplace portal `index.html` and the shipped standalone `dashboard.html` (which the portal folds in); their routing/ownership tables (`DASH_OWNER`, `navChildren`, `ds-nav`).
- **Occurrences (self-named "the third time this shape has shipped"):** portal shell nav dead-ended on Overview, `window.__dashApp` exposed after the dashboard's own `})();`, v0.125.1 (`CLAUDE.md:662-664`). Prompt Builder worked standalone but the portal router didn't own the route (`DASH_OWNER` had no `prompt-builder`), v0.211.1 #755 (`820f6d9a`, `CHANGELOG.md:2095-2111`). The route was owned but the two surfaces disagreed where — standalone moved the tab to Control, portal still pointed to Catalog, and **Gate 144 stayed green across two releases because it asserted presence, not placement**, v0.216.0 (`fc026c0e`, `CLAUDE.md:1961-1989`).
- **RC:** R1 (existence assertion topologically weaker than the placement property) + R2 (two hand-maintained ownership tables).
- **Fix applied:** Gate 144 re-authored to **derive** the home from the folded standalone chrome (single source of truth) and assert the portal agrees, two must-fail halves; Gate 51 asserts the 5-section IA contract by destination.
- **STILL LIVE / OPEN:** the rule is applied **case-by-case** (Gate 51, Gate 144) — **no generic N-surface parity gate**; a *new* two-surface feature can still be asserted independently against a constant; the "third time" framing implies a fourth is plausible.
- **Prevention (teeth):** a **portal↔standalone parity gate** that, for every nav route/tab, extracts the destination from the standalone `ds-nav` chrome and asserts the portal's `DASH_OWNER` + that section's `navChildren` agree — generalizing Gate 144's derive-and-compare over the full route set automatically.
- **Leverage:** ★★ the **surface-parity gate** — same mechanism closes P12 and contributes to P17.

### P12 — Twin-server behavioral drift (endpoint-name gate blind to `main()`)
- **Surfaces:** the two `serve-dashboards.py` copies (root dev + bundled plugin), required byte-identical for reader bodies only.
- **Occurrences:** the bundled server bound port 8000 raw while `commands/dashboard.md` advertised fallback/`--no-open`/auto-open behavior that existed only in the root server; CSRF `_ALLOWED_HOSTS` keyed on `args.port` would have broken every `/__save` on a fallback bind — Gate 32 "checks `/__` endpoint names… structurally cannot see `main()` drift," v0.205.3 #716 (`b903f32f`, `CLAUDE.md:1663-1707`). `GET /__sleipnir` 500'd on the root server because the handler existed only in the bundled copy despite its docstring calling itself a mirror; Gate 32 passed throughout (it regexes the dispatch-line string, never asks whether a handler exists), v0.222.3 (`b2443e0a`, `CHANGELOG.md:1450-1461`).
- **RC:** R2 (two hand-maintained copies) + R1 (name-parity gate blind to behavior).
- **Fix applied:** fallback/redirect logic ported + CSRF re-keyed to the bound port (v0.205.3); Sleipnir handler restored (v0.222.3).
- **STILL LIVE / OPEN:** Gate 32 remains unable to see `main()`-level drift by construction; no test exercises both dispatch tables behaviorally; the real fix (a shared module the two servers import) is unbuilt.
- **Prevention (teeth):** eliminate the twin (shared import), or extend Gate 32 from **endpoint-name parity to behavioral parity** — dispatch both copies with identical requests and diff responses (busy-port recovery, root redirect, CSRF host-keying).
- **Leverage:** ★ surface-parity gate family (behavioral variant).

### P13 — Count / version-mirror drift (the count-SSOT class)
- **Surfaces:** ~180 hand-authored `plugin.json` descriptions, their `marketplace.json` mirrors, ~180 README tables, `copilot/plugin.json` (inherits core's count **verbatim** at `generate-copilot-plugin.py:421`), `dashboard.html`/`index.html`, `AGENTS.md`.
- **Occurrences:** PR #750 (`aaf6e7d3`, Prompt Builder) is the scope-named cascade seed; "correct stale skill/plugin/hook counts (P1 — CI red on main)" #2489806 (`2489a806`); "heal stale dashboard.html + index.html + README counts" #764 (`49158059`); "fix AGENTS.md stale counts (P2)" #827 (`d662e5d5`) + the claims gate never opened AGENTS.md #883 (`9a0e5d35`); the README component table stale **again** in the 2026-08-05 triage. plan-B §0 measured: `check-marketplace-claims.py` verifies only **2 of 6** counted quantities; per-plugin READMEs have **zero** gate coverage.
- **RC:** R2 (same count stored in ~180×3 places instead of derived once; `--fix` sync is a many-file write that cascades into freshness gates).
- **Fix applied:** version-mirror parity CI (`validate-marketplace.yml:484`); `regen-on-manifest-change.sh`; the self-heal `regenerate-artifacts.yml`; **a converged cross-model FORGE plan pair** for the structural fix — **not yet built**.
- **STILL LIVE / OPEN:** the whole DROP/GENERATE refactor is **unbuilt** — counts still duplicated across ~180×3 surfaces; 4 of 6 count types still ungated; ~180 README tables ungated; the Copilot verbatim-inheritance channel open until core's description drops the count.
- **Prevention (teeth):** build plan-A/B — **DROP the prose count literals** (eliminates the class, the `--fix` machinery, and the cascade) + a **negative-assertion gate** (no description may contain `\d+\s+(agents?|skills?|templates?|commands?|hooks?|rules?)`, fails closed, doubles as a migration-completeness proof) + an **independent-scanner oracle** for `RC_BASELINE`.
- **Leverage:** its DROP direction shrinks P14's cascade surface. **Owner must settle the RC_BASELINE A/B fork** (seed #1).

### P14 — Self-heal / generated-artifact regeneration cascade
- **Surfaces:** `dashboard.html`/`index.html`/`copilot/` freshness gates + the `regenerate-artifacts.yml` self-heal pipeline + `audit-gates.sh` hermeticity.
- **Occurrences:** "self-heal gave up 26s in and left main shipping stale dashboards" #884 (`4e133414`); "self-heal opens PR with a PAT so required checks run" #765 (`821b84d2`); "install Chrome + deps so mermaid SVGs render" #766 (`d420a55e`); "self-heal opens a PR instead of pushing to protected main" #610 (`24f8edc1`, reland #759); "restore `--fix`'s repo-wide tree residue in the meta-test" #758 (`19fffdb5`); "make audit-gates hermetic — render to temp, never regenerate in place" #581 (`b4ca8119`); "quote 6 mermaid labels so the SVG render succeeds" #772 (`aca49aba`).
- **RC:** R2 (exact-byte freshness gate over an artifact whose inputs vary by clone depth / render env / `--fix` timing) + R1.
- **Fix applied:** hermetic render-to-temp; self-heal-via-PR-with-PAT (never push-to-main); the Norns/Níðhöggr/Mímir readers inline nothing git-derived (read live via `/__*`) to dodge the exact-byte trap. Standing record: `docs/research/2026-06-22-self-heal-ci-breakage/`.
- **STILL LIVE / OPEN:** the cascade recurs **faster than the count-SSOT refactor lands** — every new generated surface adds a freshness gate + a self-heal path.
- **Prevention (teeth):** a CI invariant that **self-heal can only ever open a PR, never push `main`** (assert the workflow has no `git push origin main` path) + a post-self-heal freshness re-check on the opened PR head + a hermetic-render assertion (tree byte-identical after audit-gates). Structurally, P13's DROP direction is the durable fix (fewer artifacts under exact-byte gates).

### P15 — Building to an unverified / guessed contract
- **Surfaces:** integration generators (Codex adapter), best-practice docs (PreCompact), FORGE/two-panel constants, dispatched sub-agent premises.
- **Occurrences:** the Codex "adapter" — the repo modelled Codex as "another Copilot"; Codex speaks the Claude Code hook contract **natively**, so a 456-line generator + envelope translation were **not needed** (fix was a ~100-line env shim); two audit "open pieces" **dissolved on contact with the primary source**, v0.216.0 #783 (`fc026c0e`) — *"Verify the contract before you build to it."* The **PreCompact hook for a non-problem**: a BP prescribed it to "flush plan state before compaction destroys it"; measured on real transcripts, **compaction APPENDS, destroys nothing** (44 boundaries, 1,942 turns retained), the hook *can* block (doc said it can't), the remedy was unmechanizable — retracted after **13 months as prose**, #869 (`11e0bdb5`). F7's "shared rubric via a common constants module" was false — the module didn't exist, #662 (`3839686d`). The Contoso "golden reference" flow rebuilt around a pipeline with **0 successful runs ever**.
- **RC:** R4 (a plausible mental model treated as fact drives expensive build).
- **Fix applied:** the CGP "Verify the load-bearing assumption / a reference before you mirror it" clauses; the `[unverified — training knowledge]` marker discipline; the `xc.unverified-capability-assertion` ASK concern.
- **STILL LIVE / OPEN:** these are **honesty disciplines, not controls** — no hook sees the chat/prose; each case shipped a false claim into a durable file and survived review; only the advisory `claim-grounding-lint.sh` catches the durable-artifact subset.
- **Prevention (teeth):** partial only (it's about reasoning) — extend `claim-grounding-lint.sh` to flag a **capability/contract claim written into `knowledge/`/`docs/`/a generator without an inline provenance or `[docs-verified <date>]` marker**, making an unverified contract claim visible at write time. The behavioral-canary (P16) is the enforceable complement for the integration subset.

### P16 — Install completes and wires nothing (host activation contract unverified; no behavioral canary)
- **Surfaces:** `ravenclaude` per-host installer (Codex, Copilot); generated `copilot/AGENTS.md` load path; host env-var vocabulary.
- **Occurrences:** MH-07 — pre-fix `ravenclaude setup` had **no Codex awareness**, wrote to Copilot's paths (none of which Codex reads): "a Codex operator's setup completes 'successfully' and wires zero skills, zero hooks, zero MCP… Nothing tells them so" (`ledger.md:330-401`). MH-04/MH-08 — Codex's env-var vocabulary never populated → every guardrail able to fail open, dashboard rendering identical to a clean state; the fix shipped with **zero callers for a full release** (`ledger.md:214-239,404-433`). MH-01 — a case-sensitive tool-name compare meant every Copilot tool call fell through **before the tribunal or web-access guard ran** — "the marketplace's single most heavily-engineered safety mechanism… completely dark on this host"; only one fixture used a Copilot-shaped name pre-fix (`ledger.md:112-156`, closed by Gate 167). MH-09 — generated `copilot/AGENTS.md` had no default load path (`ledger.md:454-483`).
- **RC:** R4 (host contract modeled on the nearest host, not read from its own docs) + R1 (installer reports success without verifying anything downstream consumed what it wrote) + R2 (env vocab).
- **Fix applied:** `ravenclaude install --host codex`; the `_rc_host_env()` shim; Copilot tool-name normalization; `.github/copilot-instructions.md` auto-write; Gate 167 (behavioral teeth).
- **STILL LIVE / OPEN:** MH-05 — whether every affected dashboard panel (not just Heimdall/Víðarr) got the honest-empty-state treatment, and whether the host-verdict-banner remedy landed, was not re-verified.
- **Prevention (teeth):** require every `--host X` installer to **end with a behavioral canary** — trigger the host's real invocation path, confirm a planted marker fired — not a files-exist check. Make Gate 167's retrofit the **default acceptance bar** for every future host lane (seed #5).
- **Leverage:** the canary is shared with P17/P18 (host-lane onboarding).

### P17 — Cross-host projection drift / host-support map self-contradiction / adapter payload loss
- **Surfaces:** the Copilot/Codex/Gemini manifest + agent projectors; `knowledge/host-support.json`; host-scoped sentences in generated output; the adapter I/O envelope translation.
- **Occurrences:** MH-27 — the generated Copilot manifest listed seven slash commands on a host the plugin says has none, copied verbatim from Claude-Code-only text (`CHANGELOG.md:1473-1479`). The Pipeline tab's hardcoded "nowhere else" list sat beside a derived supported-hosts list → the sentence self-contradicted when only half updated (`ledger.md:2106-2107`). MH-10 — the Copilot agent projector dropped the `tools:` allowlist entirely, so `security-reviewer` projected with **unrestricted tool access**; the first fix draft nearly re-drifted by reusing the wrong vocabulary table (`ledger.md:486-546`). MH-03 — root `AGENTS.md` claimed five-tool support with no citation; Aider's docs never mention `AGENTS.md` (`ledger.md:188-211`). The "Two Geminis" conflation (host vs model), MH-30 (lane named 17×, supported 0×). **Adapter payload loss:** "adapters kept the deny, threw away the reason," re-opening "Blocked by RavenClaude guard" diagnostic-blindness, v0.250.0 #882 (`ab468353`); the whole v0.110-v0.112 Copilot-adapter trilogy (`2>/dev/null`-ed the real stderr, landed JSONL in `runs/unknown/`); Gate 167 (payload-survives-to-tribunal).
- **RC:** R2 (each projector re-derives/copies by hand, nothing asserts consistency) + R6 (a lossy adapter drops the reason in translation).
- **Fix applied:** `host-support.json` (MH-21) as the intended SSOT, pinned by Gate 154; Gate 166 for the `tools:` projection (class-subset floor); Gate 167 (round-trip payload); the AGENTS.md host table with dated per-row basis; the Gemini host/model split.
- **STILL LIVE / OPEN:** MH-28 — the claim-grounding fix "survives at two call sites the fix did not reach"; no gate fails a build on an **uncited host-capability claim**; not every host-facing sentence reads from `host-support.json`; Gate 32-style structural checks still miss behavioral/round-trip drift on new hosts.
- **Prevention (teeth):** extend Gate 154 to scan generator output for literal host-name+capability strings not traceable to a `host-support.json` lookup; a `check-frontmatter.py`-sibling that fails on a host name near a supported/unsupported/native verb without a dated basis or `host-support.json` cross-ref; a standing **adapter round-trip gate** per host (deny + reason must survive), generalizing Gate 167.
- **Leverage:** ★ surface-parity gate (host-scope sentences vs host-support.json) + the host-canary.

### P18 — Silent disarm on update (hook-trust-by-hash / version-floor gaps)
- **Surfaces:** the Codex hook-trust model; the Copilot CLI version floor; the `git pull` update path; the SessionStart banner (itself a hook).
- **Occurrences (independent on two hosts, same shape):** MH-17 — Codex tracks hook trust **by hash**, this repo updates via plain `git pull`, so every pull changing a hook byte invalidates trust and **nothing announces it** (the banner is itself a hook) (`CLAUDE.md:2045-2056`, `ledger.md:814-856`). MH-23 — sub-agent tool calls did **not fire below Copilot CLI 1.0.52** and nothing in the installer checked the running version — "the same silent-disarm shape as Codex hash-trust… nothing anywhere checked it"; the documenting skill sourced its version table from a `/tmp` path that didn't exist, several rows wrong (`ledger.md:1100-1169`).
- **RC:** R5 (enforcement silently disarms — fails open — on update) + R2 (per-host retrofits, no shared abstraction).
- **Fix applied:** Codex — a re-trust notice at install/update/status + inside the generated config (`--dangerously-bypass-hook-trust` named only to be refused). Copilot — a version-floor check (Gate 157) + two guard-script fixes found the same pass.
- **STILL LIVE / OPEN:** **structural** — any future host lane with its own trust/version gate reproduces the shape unless the check becomes a mandatory shared part of host onboarding rather than a per-host retrofit.
- **Prevention (teeth):** a per-host `activation_gate` field in `host-support.json` (`hash_trust | version_floor | none`), consumed by **one shared re-arm-notice helper** at install/update/status.
- **Leverage:** shares the host-onboarding-contract substrate with P16/P17.

### P19 — Stale claim in an every-session-loaded file (the supersession discipline)
- **Surfaces:** the plugin + root `CLAUDE.md` (loaded into **every** session), milestone lists, dashboard audit lenses, gate-state prose (DOM-budget).
- **Occurrences:** "the constitution said the macOS tribunal was broken — it fixed itself 3 PRs ago"; an agent read the stale "Still open" list and told the maintainer **twice** the tribunal was broken on macOS (working since v0.197.0), #683 (`c73fabc2`, `CLAUDE.md:1563-1589`). MH-40 — a `dashboard_autostart` DOM control reported "not shipping" after it shipped in the same release; an audit lens read the un-updated sentence and reported closed work as open (`CLAUDE.md:2000-2007`). "four surfaces that misled a reader" #797 (`e4a8018b`); "four surfaces that overstated their own scope" #787 (`8ea4c186`); "three false claims about recently shipped work" on the dashboard #812 (`7039f78e`). The v0.244.1/v0.245.0 PreCompact retraction re-invoked the supersession convention by name.
- **RC:** R6 (a durable, trusted-looking prior outlives its truth and misleads the next agent) + R3 (the supersession rule is prose).
- **Fix applied:** the **supersession rule** (v0.196.0): "when you close a door, supersede the entry that says it's open **in the same PR**"; dated milestones kept but marked SUPERSEDED in-place.
- **STILL LIVE / OPEN:** the rule is **prose** — nothing gates "a PR that closes an item also updates the entry that says it's open" (MH-40 landed *after* the rule; 23 stale/overstated/misled commits counted); the `knowledge-file-staleness-sweep` skill exists but is **manual and does not cover the constitution files** — exactly where the incident happened and the highest-priority surface (unconditionally loaded).
- **Prevention (teeth):** extend the staleness-sweep skill's scope to the root + plugin constitution files; wire an advisory `PostToolUse` that, when a diff resolves a tracked "Still open / broken / TODO / FIXME" marker's subject (matched to Níðhöggr's superseded-decision signals), nudges to update the milestone entry in the same diff. Full closure needs a decisions-log `supersedes:` frontmatter convention made mandatory for milestone reversals.

### P20 — Corpus-scale measuring-instrument invalidity (a new checker lies fluently, at scale)
- **Surfaces:** any newly-authored audit/checker tool (the UI/UX audit harness is the worked case).
- **Occurrences (one deeply-analyzed incident; the doc names the general shape, not a one-off):** a headless-browser UI/UX audit harness opened at 94 findings, peaked at **3,337, ~99% not real**, across **six independent checker bugs** (DOM-ancestor backdrop walk, point-based lookup misuse, unresolved `<label for>`, wrong focus-visible model, bounding-box without the criterion's exceptions, hand-rolled visibility test) — **nothing crashed, exit 0 throughout, every number the right type and wrong value** (`validating-a-measuring-instrument.md`, `lessons-learned.md:27-43`, 2026-07-29). Framed as the silent-green defect moved up one level into the tool meant to find defects — worse there, "a wrong gate corrupts every conclusion drawn from it."
- **RC:** R1 (the assertion doesn't measure what it claims) + R4 (a new tool trusted on its first run against an assumed-correct model).
- **Fix applied:** a three-step triage (treat implausible finding-volume as a bug report about the checker → caught ~half; trace exactly one finding to source before fixing → caught all six; ask the platform for the authoritative answer vs. hand-modeling) + a **mutation-test-between-clean-passes** ritual; the resulting gate ships both must-fail directions.
- **STILL LIVE / OPEN:** the discipline is **documented but not a required step** in any "author a new checker" workflow; the older `ci-gate-audit.md` doesn't cross-link the newer `validating-a-measuring-instrument.md` (a reader who finds the gate doctrine first has no forward pointer).
- **Prevention (teeth):** (1) the one-line cross-link between the two docs; (2) a checklist gate in any new-checker workflow — run once against the real corpus, sanity-check finding volume against a plausibility prior, trace one finding to source, run the mutation-test-between-clean-passes ritual before a zero-finding result is trusted.

### P21 — DOM-budget zero-slack ratchet friction (process-friction, lower severity)
- **Surfaces:** Gate 132 (DOM-element budget) + its monotonic ratchet + the prose describing its live count.
- **Occurrences:** Gate 132 introduced at zero slack with a monotonic ratchet, v0.208.0 (`CLAUDE.md:1709-1754`); six changelog entries each record "no ratchet raise needed," achieved via an islanding trick (a JSON payload island costs +0 counted elements) or pure CSS/token changes (`CHANGELOG.md:736,832,1145,1441,1771,1836`); the one owner-approved raise (Prompt Builder, +6, `CHANGELOG.md:2151`). MH-40's stale-gate-state prose (folded into P19).
- **RC:** R3 (a hard zero-slack ratchet with no formal request/tracking workflow beyond ad-hoc owner approval).
- **Fix applied:** the islanding-trick precedent as the default pattern; the one legitimate raise documents the sanctioned path.
- **STILL LIVE / OPEN:** no formal request/tracking workflow; the numeric-state prose about the gate has no freshness marker (the MH-40 half is P19's concern).
- **Prevention (teeth):** generate any doc sentence citing a gate's live numeric state from the gate's own output rather than typing it as static prose; optionally a lightweight raise-request record. **Lowest priority** — this is friction, not a fail-open defect.

---

## Leverage-ranked mechanisms

Ranked by (classes closed × mechanizability), with build cost and any owner gate noted. "★" mechanisms
close multiple classes.

| Rank | Mechanism | Classes it closes / touches | Mechanizability | Build cost | Notes |
|---|---|---|---|---|---|
| **1** | ★ **Gate-introspection meta-gate** (`check-gate-registration.py` over `audit-gates.sh`): reachability + exit-2-specificity + regex-compile over every catalog + gate-number uniqueness | **P2, P3, P4, P6**; the must-fail-exit-2 clause serves **P5** | **High** — flat bash script, regular `-- Gate N:` header convention already universal; parse is mechanical | Low | Guardrails miner's #1. One parse serves reachability + uniqueness + compile. Must-fail fixture = the Gate-184 paste-inside-dispatcher shape |
| **2** | ★ **Author-time portability lint** (`PreToolUse(Write\|Edit)` on `hooks/**` + `scripts/**` + `monitors/**`) denying banned bash-4/GNU tokens unless routed through `_portable.sh` | **P1** | **High** — token grep, bash-3.2-safe itself | Low | Closes one class but **the single highest-recurrence class** (18 doors, still breaking at #885). In-loop complement to `validate-macos.yml` |
| **3** | ★ **Fail-closed exit-code execution audit** (drive every enforcement hook's deny/error/empty fixture under minimal PATH on macos+ubuntu → assert exit 2 or safe-noop, never fail-open exit 1) + verdict-chain-ends-in-non-permissive-default lint + trap-ordering check | **P5, P6**; the runner is shared with **P1** | **High** — extends `validate-macos.yml` | Low-Med | "Execute, don't lint" — `bash -n` provably can't see this class |
| **4** | ★ **Surface-parity gate** (derive the expectation from one generated surface, assert the other; never assert both against a constant) | **P11, P12**; host-scope-sentence variant serves **P17**; behavioral-parity variant serves **P12** | **Med-High** — generic over a route table, but each surface pair needs a bespoke extractor | Med | Generalizes Gate 144/Gate 32; product+guardrails+engineering all name it |
| **5** | ★ **Count-SSOT derive-don't-duplicate refactor** (DROP prose count literals + negative-assertion gate + independent-scanner `RC_BASELINE` oracle) | **P13**; shrinks **P14**'s cascade surface; contributes to **P17/P19** | Med (gate) / Low (concept) | **High** (touches ~180×3 surfaces) but **plan already converged** | **Owner gate:** RC_BASELINE A/B fork (seed #1) |
| **6** | ★ **Behavioral canary as host-onboarding acceptance bar** (`activation_gate` field + one shared re-arm helper; every `--host X` installer ends by firing the host's real path + confirming a planted marker) | **P16, P18**; contributes to **P17** | Med — generalizes Gate 167 | Med | **Owner gate:** make it mandatory for future host lanes (seed #5) |
| **7** | **Contract-verification write-time provenance lint** (extend `claim-grounding-lint.sh` to flag capability/contract claims in `knowledge/`/`docs/`/generators without a provenance / `[docs-verified]` marker) | **P15**; contributes to **P17, P20** | **Low-Med** — reasoning-bound; only the durable-artifact subset is gateable | Low | Honest partial: no hook sees the chat/prose |
| **8** | **Catalog-scoping-consistency lint** (`check-trigger-scoping-consistency.py`: flag a bare unscoped `.*` across a separator beside a scoped sibling; require class-siblings in the diff or waived) | **P8**; shares substrate with **P6** | High | Low | Turns "grep for the class" into a gate |
| **9** | **Subagent-safe-guard authoring checklist/fixture** (state keyed to worktree; file-based escape reachable by `Write`; 2-worktree fixture proving A doesn't block B, refusal paths tested) | **P9** | Med — generalizes Gate 190 | Med | Highest *blast radius* remaining gap (tunnelled/lost work, not just red CI) |
| **10** | **Sanctioned-guard-escape door** (exempt `tests/fixtures/**` + `docs/**` prefix and/or honoured in-file sentinel; fix the `.ravenclaude/runs/**` nested-worktree exemption) | **P7**; contributes to **P9** | Med | Med | **Owner gate:** worth its security-review cost? (seed #2). Twice-deferred; surfaced again this run |
| **11** | **Staleness-linkage** (extend the staleness-sweep skill to constitution files + advisory `PostToolUse` nudge on resolving a tracked "Still open" marker; `supersedes:` frontmatter) | **P19**; contributes to **P17** | Low-Med — partial/advisory | Low | The enforceable half of the supersession rule |
| **12** | **Self-heal push-safety invariant** (assert self-heal workflows have no `git push origin main` path + post-self-heal freshness re-check on the PR head + hermetic-render assertion) | **P14** | High | Low | Point-fix until P13's DROP lands |
| **13** | **Self-certifying-change flag** (surface a PR touching both a gate and the source it guards → require an independent oracle or sign-off) | **P10** | Med | Low | A flag, not a block |
| **14** | **Corpus-scale plausibility checklist** (new checker's first real-corpus run: implausible-volume sanity + trace-one-to-source + mutation-test-between-clean-passes) + the two-doc cross-link | **P20** | Low-Med — discipline + one doc edit | Low | The doc cross-link is a one-line immediate win |

**Structural observation (all three miners):** ranks 1, 3, and the regex-compile in rank 1 reduce to
one shared capability — a script that can introspect the gate harness + the hooks it tests (is a gate
wired? does its deny path exit 2? does its catalog compile?). Build that introspection **once as a
shared library** the checks import — itself an instance of the repo's own derive-don't-duplicate maxim.

---

## Owner-decision seeds

These feed the run's DoD (a build plan + the decisions only the owner can make). Each is a genuine
fork the analysis surfaces but cannot settle from rules alone.

1. **Count-SSOT `RC_BASELINE` A/B fork** (from the converged count-ssot plan pair). **plan-A** de-hardcodes `RC_BASELINE` via an *independent scanner* (a second code path, must-fail fixtures proving the two paths can diverge — not a tautology); **plan-B** keeps it a *hand-set golden literal + advisory*. Both agree computing it from the generator's own `scan_repo` is a forbidden tautology. Pick one before the count-SSOT build starts.
2. **Sanctioned-guard-escape door — worth its security-review cost?** The exempt fixtures/docs path or in-file sentinel (P7) widens what the hard-rule guards ignore; it's been **twice-deferred on purpose** pending a red-team pass on the widened surface — and it bit this very run (the miner's own writes were denied). Decide whether to fund that security review now (it's the highest-friction live guard-layer item) or keep the `printf` workaround.
3. **macOS-runner enforcement aggressiveness.** For the P1 author-time portability lint: (a) how hard — a `PreToolUse` **deny** (in-loop, blocks the write) vs a CI-only lint (backstop) vs both; and (b) how wide — `hooks/**` only, or `hooks/** + scripts/** + monitors/** + the installer`. The wider + harder, the fewer escapes but the more author friction.
4. **Priority / sequencing.** The analysis's implied order is: **(1) gate-introspection meta-gate** (cheapest, closes 4-5 classes) → **(2) author-time portability lint** (highest recurrence) → **(3) fail-closed exit-code audit** → **(4) surface-parity gate** → **(5) count-SSOT build**. And a sub-fork: ship the count-SSOT **negative-assertion gate first as a cheap stopgap**, or go straight to the full **DROP refactor** (eliminates the class + cascade but touches ~180×3 surfaces)? Owner confirms or reorders.
5. **Behavioral canary as a *mandatory* host-onboarding bar.** Make Gate-167-style behavioral proof + the `activation_gate` field required for every future `--host` lane (closes P16/P18 by construction but adds per-host onboarding cost). Ratify or leave advisory.
6. **DOM-budget ratchet (P21) — formalize or leave ad-hoc?** Keep zero-slack + case-by-case owner approval (current), or add a lightweight raise-request/tracking workflow. Lowest priority; owner may defer.

---

## Coverage note (dedup accounting)

Every miner class maps into a canonical P-class: **engineering** C1→P1, C2→P2/P5, C3→P13, C3b→P14,
C4→P11, C5→P8, C6→P15, C7→P19, C8→P7, C9→P5, C10→P9, C11→P12/P17. **guardrails** C1→P2, C2→P4, C3→P5,
C4→P5, C5→P7, C6→P8, C7→P6, C8→P9, C9→P10, C10→P11, C11→P5, C12→P3, C13→P20, C14→P19. **product**
C1→P11, C2→P12, C3→P21(+P19), C4→P1(+P16), C5→P16, C6→P17, C7→P18, C8→P17. No miner class was dropped;
21 canonical classes, 6 root causes.
