# G6 — Hardening plan (v1, reconciled): recurring-defect hardening (full sweep · prevent + remediate)

**What this is.** The single authoritative v1 hardening plan, synthesized by the FORGE G6 stage from the
two divergent panel drafts (`plan-A.md`, Opus; `plan-B.md`, Sonnet), reconciled against each other and
folded in with the live evidence generated during this very run. It builds on the consolidated
`problem-inventory.md` (21 canonical classes P1–P21, 6 root causes R1–R6, the leverage-ranked mechanism
table, 6 owner-decision seeds) and `claims-table.md` (CL-1…CL-25). Nothing here re-derives an occurrence;
every phase cites the claim rows it rests on.

Both panels converged on the same strategic spine — **not 21 point-fixes, four leverage plays plus a
short residual tail** — and on the same keystone: **audit the auditor before you add auditors.** Where
they diverged (RC_BASELINE handling, macOS-runner enforcement aggressiveness, guard-escape-door
sequencing), the divergences are reconciled in [§ Divergence reconciliation](#divergence-reconciliation)
— surfaced as owner forks where the choice is a genuine judgment call, resolved in-plan where one panel's
reasoning strictly dominated.

DoD for this run is **the plan + the owner decisions, not the build** (per `scope.md`). Nothing in this
document was built; every acceptance test below is a spec for a future gate, not a report of one running
today.

> **Anti-tunnel note (this synthesis followed the discipline the plan exists to teach).** Where this
> document must refer to a forbidden command the guards catch, it describes it **in prose** — "a
> force-push to a protected branch", "a fetch-piped-into-a-shell", "a bare in-place stream edit" — never
> as literal danger-command syntax, and it writes every defect in **descriptive/past tense**, not as a
> live-diagnostic present-tense probe. That is exactly the sanctioned remediation Panel A and the
> consolidator used, and the opposite of the Write-placeholder-then-Edit tunnel Panel B used (see
> [§ Empirical evidence generated during THIS run](#empirical-evidence-generated-during-this-run)). No
> Write was routed around a matcher to produce this file.

---

## 0. Recommended strategy — the reconciled sequencing thesis

**Four leverage plays plus a short residual tail, sequenced so the cheapest highest-leverage mechanism
lands first and every mechanism after it is guarded by the ones before it.**

The keystone is the **gate-introspection meta-gate** (`check-gate-registration.py`): it closes P2/P3/P4/P6
in one parse **and it is the thing that guarantees every subsequent gate this plan adds is actually
wired, actually fails on a bad input, and actually appears in the full-suite output by name.** Building
it first means the 10+ new gates that follow inherit a standing proof they aren't the next Gate 184.
That is the sequencing thesis in one line: *audit the auditor before you add auditors* (Panel A's
"keystone" framing).

Panel B contributed the complementary framing that survives into this plan: **the meta-gate is not only
a keystone, it is a shared primitive.** Its `audit-gates.sh` parse is imported (not re-derived) by the
exit-code audit (Phase 3), the catalog-hygiene lint (Phase 9), and the self-certifying-change flag
(Phase 14). Building the parse once and importing it is this plan's own instance of the
derive-don't-duplicate maxim R2 names — re-deriving it per consumer would recreate R2 inside the very
plan meant to close R2. Both framings point at the same first move; this plan keeps both.

**The reconciled build order** (leverage × pain × cost, cheapest-first inside each tier):

- **Phase 0 — Quick wins** (P20 doc cross-link). Zero-risk, ships same day. Banked before any code (Panel B).
1. **Phase 1 — Gate-introspection meta-gate** (P2/P3/P4/P6 + P5's exit-2 clause) — cheapest, closes 4 classes, guards + is imported by all later work. **P0, keystone + shared primitive.**
2. **Phase 2 — Author-time portability lint** (P1) — the single highest-recurrence class (18 door commits, still breaking at #885/#873). In-loop `PreToolUse` deny + CI backstop, mirroring `enforce-layout.sh`↔`validate-layout.yml`. **P0.**
3. **Phase 3 — Fail-closed exit-code execution audit** (P5/P6) — extends the `check-macos-portability.sh` execution runner; a static syntax check provably cannot see this class. **P0.**
4. **Phase 4 — Surface-parity gate** (P11/P12 + P17 host-scope variant) — generalizes Gate 51's derive-and-compare; assert two generated surfaces against **each other**, never a constant. **P1.**
5. **Phase 5 — Count-SSOT DROP refactor** (P13; shrinks P14) — plan already converged; **owner settles RC_BASELINE before build**. **P1**, highest cost. [OWNER-GATED — Fork 1]
6. **Phase 6 — Behavioral-canary host-onboarding bar** (P16/P18 + P17) — generalizes Gate 167; owner ratifies mandatory-vs-advisory. **P1.** [OWNER-GATED — seed #5]

Then the residual tail the four plays don't structurally cover (the inventory's named residuals, CL-25):

- **Phase 7** — self-heal push-safety invariant (P14)
- **Phase 8** — cross-host projection / host-capability lint + adapter round-trip (P17)
- **Phase 9** — catalog-scoping-consistency lint + regex-catalog rollout (P8, P6 remainder)
- **Phase 10** — subagent-safe-guard authoring checklist/fixture (P9)
- **Phase 11** — sanctioned-guard-escape door (P7, contributes P9) — **owner-gated on a security review [Fork 2]**
- **Phase 12** — contract-verification write-time provenance lint (P15, honest partial)
- **Phase 13** — staleness-linkage / supersession nudge (P19)
- **Phase 14** — self-certifying-change flag (P10)
- **Phase 15** — corpus-scale plausibility checklist (P20 checklist half)
- **Phase 16** — DOM-budget ratchet formalization (P21) — lowest priority, owner may defer

**Two cross-cutting disciplines the whole plan honors, because they are the meta-risk of a hardening
initiative:** (a) **every new gate ships with a must-fail half and is registered in BOTH the `--check`
dispatcher and the full-suite region, then verified by grepping the full-suite output for the gate's name**
— the Gate-184 ritual (`audit-gates.sh:6119`), and the reason Phase 1 exists at all; (b) **every new
source-scan guard gets a sanctioned-exempt path or intent-vs-description discrimination up front**, so it
does not reproduce P7 (the source-scan-matches-prose class) inside a mechanism meant to fix a different
class. This second discipline is no longer hypothetical: **three separate guards false-positived on this
run's own legitimate planning/verification work** — the empirical spine of this plan, in
[§ Empirical evidence](#empirical-evidence-generated-during-this-run) — and that evidence **reprioritizes**
the intent-vs-description and sanctioned-escape mechanisms upward (Phase 11's low-risk half and the
premise-guard scope fix move into the P0 band, ahead of their nominal residual-tail rank — see §8, where
it needs no owner ruling, matching P0's definition rather than P1's "needs one owner ruling").

---

## 1. Coverage table — every P# maps to a phase (none dropped)

Every class carries **both** a prevention phase and a remediation of its live-open instances. No class is
dropped; the 21-class dedup accounting in `problem-inventory.md` is preserved intact.

| P# | Class (one line) | Prevention phase | Remediation of live-open in |
|---|---|---|---|
| **P1** | macOS / stock-toolchain doors | **Ph 2** (author-time portability lint) | Ph 2 (lint the tree; fix #885/#873 residue; port `premise-gate.py`/`classify_claim.py` packaging across 6 call sites) |
| **P2** | never-ran / mis-wired gate | **Ph 1** (meta-gate reachability) | Ph 1 (assert every existing gate reachable; scan for another Gate-184 shape) |
| **P3** | gate-number collision + self-desc drift | **Ph 1** (number-uniqueness + `Supported:` cross-check, same parse) | Ph 1 |
| **P4** | hollow gate (input silently empties) | **Ph 1** (UNWIRED / must-flag-unwired taxonomy — **honest partial**: a doc-convention addition, not an automated retroactive scan; see Phase 1's Goal) | Ph 1 + doc (generalize Gate 179) |
| **P5** | exit-code severity / fail-open-on-error | **Ph 3** (exit-code execution audit) + **Ph 1** (exit-2 clause) | Ph 3 (drive every enforcement hook; audit the C4 rewrite trap beyond `thing-orchestrator.sh`) |
| **P6** | malformed regex silently disables a rule | **Ph 1** (regex-compile primitive) + **Ph 9** (full catalog rollout) | Ph 1 (comfort-posture hard-rule catalog gets its first standing recompile) |
| **P7** | self-referential guard denies own fix/test/docs | **Ph 11** (sanctioned-exempt door — owner-gated) | Ph 11 (fix `.ravenclaude/runs/**` nested-worktree exemption + the Write-scoped-matcher gap + the `xc.tribunal-self-disable` read/write-blind verb-near-path trigger — the **live this-run instance**, incl. this run's and the critic pass's own denials) |
| **P8** | fix-one-instance / unscoped-regex-beside-scoped | **Ph 9** (catalog-scoping-consistency lint) | Ph 9 (grep the catalog for remaining unscoped wildcards beside a scoped sibling) |
| **P9** | guard escape unreachable → tunnelled; shared-state | **Ph 10** (subagent-safe-guard checklist/fixture) | Ph 10 (audit other session-keyed substrates: runaway-brake, thing runaway dirs) |
| **P10** | self-certifying change (gate re-authored with its target) | **Ph 14** (self-cert flag) | Ph 14 |
| **P11** | presence-not-placement cross-surface regression | **Ph 4** (surface-parity gate) | Ph 4 (generalize Gate 51 over full route set) |
| **P12** | twin-server behavioral drift | **Ph 4** (behavioral-parity variant) | Ph 4 (or eliminate the twin via shared import — Ph 4 note) |
| **P13** | count / version-mirror drift | **Ph 5** (count-SSOT DROP) | Ph 5 (drop ~180×3 literals; gate the 4 ungated count types + ~180 README tables) |
| **P14** | self-heal / generated-artifact cascade | **Ph 7** (self-heal push-safety invariant) | Ph 7 (assert no direct-to-`main` push; post-heal freshness re-check on PR head) |
| **P15** | building to an unverified contract | **Ph 12** (contract-provenance lint — honest partial) | Ph 12 (reasoning-bound; only the durable-artifact subset is gateable) |
| **P16** | install completes / wires nothing | **Ph 6** (behavioral canary) | Ph 6 (re-verify MH-05 dashboard empty-states + host-verdict banner) |
| **P17** | cross-host projection drift / adapter payload loss | **Ph 8** (host-capability lint + adapter round-trip) + Ph 4/5/6 | Ph 8 (fix MH-28 two-call-site residue; uncited host claims) |
| **P18** | silent disarm on update (hash-trust / version-floor) | **Ph 6** (`activation_gate` field + shared re-arm helper) | Ph 6 |
| **P19** | stale claim in an every-session-loaded file | **Ph 13** (staleness-linkage + supersession nudge) | Ph 13 (extend sweep to constitution files) |
| **P20** | corpus-scale measuring-instrument invalidity | **Ph 0** (doc cross-link) + **Ph 15** (plausibility checklist) | Ph 0 (one-line cross-link is an immediate win) |
| **P21** | DOM-budget ratchet friction | **Ph 16** (generate gate-state prose; raise-request record) | Ph 16 (lowest priority; owner may defer) |

---

## 2. The six-part teeth block — the design constraint every mechanism carries

The whole point of this run is that a hardening mechanism **must not recreate the very root causes it
attacks** (R1–R6). So every mechanism below carries a **six-part teeth block**. The first two panels each
enforced this (Panel A as an `[R-tag]` list, Panel B as a table); this plan carries the union, one line
per constraint, and marks a **RISK** wherever a mechanism cannot fully satisfy a constraint (routed to the
[risk matrix](#risk-matrix)).

| # | Constraint | What it forbids recurring | Test that proves it |
|---|---|---|---|
| **1** | **not-hollow / appears-in-suite-by-name** | R3/R1 — a gate that never ran, or is green whether present or absent | must-fail fixture + registered in **both** dispatcher and full-suite region + the suite output grepped for the gate name post-registration |
| **2** | **fail-closed / exit-2 specific** | R5 — a deny path that satisfies a naive nonzero check via a crash (exit 1) or a swallowed error; a verdict chain whose `else`/`*)` resolves to allow | assert the observed deny exit is literally **2**, not merely nonzero; every verdict chain ends in an explicit non-permissive default; EXIT trap armed before the first fallible op |
| **3** | **macOS-portable** | R1 — invisible-on-Linux-CI doors: `declare -A`, `mapfile`, upper/lower parameter-expansion, `globstar`, unshimmed timeout, PCRE-`grep`, in-place stream edit, GNU-only find | the mechanism itself is bash-3.2-safe / Python-3.9-stdlib, and routes any shimmed need through `plugins/ravenclaude-core/hooks/_portable.sh` |
| **4** | **verified contract** | R4 — building to a guessed model of the harness/tool | built against a this-session `file:line` read (each phase cites its anchors), never a recalled assumption |
| **5** | **assert-surfaces-against-each-other** | R2/R1 — asserting a surface against a hardcoded constant instead of deriving the expectation from a second surface | where the mechanism guards two surfaces, derive from one and check the other; never a constant oracle |
| **6** | **self-non-recursion (SNR)** | R6 — a source-scan guard denying its own fix/test/comment/docs | the mechanism must not deny a description of the pattern it forbids: exempt-path or in-file sentinel, `printf`-assembled fixtures, prose-not-literal descriptions, or built as a CI reader (no `PreToolUse` deny surface) |

**Reconciled note on constraints 5 and 6:** Panel B correctly observed that several mechanisms are **CI
readers, not write-time deny hooks** (Phases 1, 3-static, 4, 7, 8, 10, 14, 15) — these have **no**
`PreToolUse` surface on which to deny their own fix, so their SNR is satisfied *structurally* rather than
by an exempt path. Only the genuine `PreToolUse` deny hooks (Phase 2's portability hook) and the
prose/source-scanning lints (Phases 7, 8, 9, 12, 13) carry the P7 self-reference risk and therefore depend on
Phase 11's sanctioned-exempt door to fully retire their SNR residual. (Phases 7 and 8 appear in the
no-deny-surface list above *and* here: they cannot deny their own fix, but their source-scan can
false-positive on a comment/doc describing the pattern — the residual Phase 11 clears.) This distinction — which panels
stated differently — is made explicit per-phase below and is the substance of the guard-escape-door
reconciliation.

---

## 3. Phases

Each phase lists: **Goal · Classes closed (P#) + live instances remediated · Files · Acceptance tests +
pre-build gates · Teeth (the six-part block) · `depends_on_claims`.**

---

### Phase 0 — Quick wins (zero risk, ships same day) · closes P20 (doc-hygiene half)

**Goal.** Bank the free fix the inventory names outright, before any code is written elsewhere: the
missing forward-pointer between the two measuring-instrument docs.

**Classes closed + live-open remediated:** P20 (doc-discoverability half only — the checklist-in-workflow
half is Phase 15). Live-open: the missing cross-link between `docs/best-practices/ci-gate-audit.md` and
`docs/best-practices/validating-a-measuring-instrument.md` (`problem-inventory.md:218`) — a
reader who finds the older gate doctrine first has no pointer to the newer 3,337-finding lesson.

**Files touched:** `docs/best-practices/ci-gate-audit.md` (one forward-pointer line).

**Acceptance tests + pre-build gates:** none new — a doc edit with no code path. The existing
`check-md-links.py` gate validates the new link resolves; per the v0.194.0 lesson it must be a real
markdown *link*, not a backtick path the link-checker skips.

**Teeth:** [not-hollow] enforced by the existing md-links gate (a resolvable target) · [exit-2] n/a (doc)
· [macOS] n/a (markdown) · [contract] grounded in both docs cited in the inventory · [surfaces] n/a ·
[SNR] n/a (not a gate/hook).

**`depends_on_claims: [CL-12, CL-24]`** (CL-24 mutation-testing general practice is `[unverified —
training knowledge]`; cite the internal doc where load-bearing.)

---

### Phase 1 — Gate-introspection meta-gate (the keystone + shared primitive) · closes P2, P3, P4, P6 (+ P5 exit-2 clause)

**Goal.** Ship `scripts/check-gate-registration.py`, a static parser over `scripts/audit-gates.sh`
(measured this session at ~6454 lines / ~194 gates / ~521 `gate()` assertions, universal `── Gate N:`
box-drawing header convention), that asserts in one pass:
- **Reachability (P2):** every `── Gate N:` header has ≥1 `gate` call in the **unconditional full-suite
  region** (after the `--check` dispatcher block closes — `esac` `:880` / `fi` `:881`), not only inside a `--check N)` arm — the
  exact Gate-184 paste-inside-dispatcher shape (`:6108–6122`). Cross-check the `Supported:` list (`:877`)
  against the real dispatcher case labels — two independently-maintained surfaces, compared to each other.
- **Number-uniqueness (P3):** flag a gate number that appears **twice in the unconditional full-suite
  region** (the real two-Gate-104 collision was two *independent full-suite* gates sharing a number,
  `2026-06-23-gate-consolidation-audit.md:18`). **Do NOT key this on description-difference.** Measured
  this session: **87 of 150 gate numbers legitimately echo their `── Gate N:` header in BOTH the `--check`
  dispatcher AND the full-suite region, with deliberately *different* text** — a `(per-gate run)` short
  form vs the canonical full form (e.g. Gate 194 `… bidirectional teeth (per-gate run)` at `:871` vs
  `… BIDIRECTIONAL teeth (survive + neutralize)` at `:6406`). A "same-number → different-description →
  collision" rule would false-positive on all 87 and get the keystone disabled on day one — the exact
  fate this plan warns against (M5), i.e. the keystone reproducing P2/P4 inside itself. Reuse the same
  region-split the reachability sub-check already computes: a legitimate dispatcher↔full-suite pair is
  *one* gate echoed in two regions; a collision is *two* headers of the same number in the *same*
  (full-suite) region.
- **Exit-2 specificity (P5, shared clause):** for a gate that exercises an actual `PreToolUse` hook
  *process* — stdin-JSON piped into a `hooks/*.sh` script, its `$?` captured as the gate's `rc` — the
  assertion must be paired with an explicit `[ "$rc" -eq 2 ]` check, not a bare nonzero must-fail
  (`:1047–1048` is the positive template). **Do NOT key this on the gate NAME containing "blocks"/"deny"
  alone — that is the wrong signal, the same shape as the P3 bug just corrected above.** Measured this
  session: of the 57 gates in `audit-gates.sh` whose name contains "blocks"/"deny"/"denies", only 8 (14%)
  assert an actual hook-process exit code; the other **49 (86%) assert an internal decision-engine
  output** — a `thing_decision`/`_predeny` string or boolean, an adapter's translated JSON field, a
  tribunal verdict — where "exit code 2" is not a meaningful concept at all (e.g. `:1590`
  `gate "thing: panel deny -> deny" must_pass "$rc"` asserts `[[ "$d" == "deny" ]]` against a
  Python-emitted string; `:2148` asserts an adapter's translated `permissionDecision` JSON field; neither
  touches a process exit code). A name-only "blocks/deny → must show `-eq 2`" rule would flag all 49 as
  violations on day one — the exact keystone-flood fate the P3 fix above corrects for, at a WORSE rate
  (86% vs. P3's 58%). **Scope the check to gates whose preceding lines show the literal PreToolUse-hook
  invocation signature** (a `hooks/*.sh` path piped stdin, `|| rc=$?`/`|| GD_RC=$?`-shaped capture) — the
  same signature Phase 3's execution audit already targets when it enumerates hooks (import, don't
  re-derive the detection) — and leave internal-decision-engine "blocks"/"deny" gates unscoped by this
  clause entirely.
- **Regex-compile primitive (P6):** ship the reusable `scripts/check-regex-catalog-compiles.py`
  `(path, field-selector)` that compiles every regex in a named catalog and fails on a malformed one —
  generalizing Gate 16's `thing-concerns.py`-only check. First invoked against the existing concerns
  catalog (proves parity) and against the comfort-posture hard-rule catalog (the newly-covered surface,
  the v0.242.0/v0.244.0 silent-disable).
- **UNWIRED taxonomy (P4) — honest partial, added this critic pass.** Add a third fixture category
  `must_flag_unwired_on` to `ci-gate-audit.md`, generalizing Gate 179's UNWIRED verdict
  (`:6092–6099`, the pattern where a data-dependent gate whose upstream field goes silently absent
  must emit a distinct non-pass, non-generic-fail verdict rather than running clean while checking
  nothing). **Scope this bullet honestly: it is a documentation/authoring-convention addition,
  not a check `check-gate-registration.py` performs.** Confirmed this session:
  `docs/best-practices/ci-gate-audit.md` presently documents exactly two fixture categories
  (`must_fail_on`, `must_pass_on`, `:25–26`); this adds a third, named convention for future
  data-dependent-gate authors to follow — it does **not** retroactively scan the ~194 shipped
  gates for one lacking an UNWIRED self-test, because whether a gate's own detector silently
  no-ops on a missing/malformed input is a **runtime** property (what a gate's logic *does* on
  bad input), not something visible to a static text parse of `── Gate N:` headers. (The
  regex-compile primitive above and the reachability/uniqueness/exit-2 sub-checks are all
  genuinely static-parse-detectable; this one structurally isn't, which is exactly why it has
  no must-fail fixture of its own below — unlike P2/P3/P5/P6, each of which does.) The
  problem-inventory's own leverage table (`:238`) names this mechanism "the doc + the
  gate-introspection layer" — this plan builds the doc half now and does not claim the second
  half exists; a future automated liveness-probe scan (distinguishing which gates are
  data-dependent and checking each exposes a distinguishable UNWIRED verdict) is a real,
  larger follow-up this bullet deliberately does not pre-empt.

**This parser is the shared primitive** imported by Phases 3, 9, and 14 (derive-don't-duplicate — a
second copy in any of them would recreate R2 inside this plan).

**Classes closed + live-open remediated:** P2, P3, P4 (honest partial — see above), P6. Live-open: a full
run against the *current* `audit-gates.sh` at merge surfaces any already-unreachable or duplicate-numbered
gate; the comfort-posture hard-rule catalog gets its first standing regex-compile check; the P4 UNWIRED
convention is written into `ci-gate-audit.md` for future data-dependent-gate authors, but retrofitting the
~194 already-shipped gates for an explicit UNWIRED self-test state is NOT performed by this phase and is
not tracked as a remediation item here — a real gap, named rather than silently dropped.

**Files touched:** `scripts/check-gate-registration.py` (new), `scripts/check-regex-catalog-compiles.py`
(new), `scripts/audit-gates.sh` (register as new gates in **both** regions; add exit-2 teeth),
`docs/best-practices/ci-gate-audit.md` (the Phase-0 cross-link + the new `must_flag_unwired_on` fixture
category, `:25–26`'s taxonomy).

**Acceptance tests + pre-build gates:**
- must-fail (P2): a synthetic `audit-gates.sh` copy in `mktemp -d` with a gate pasted inside the dispatcher → exit nonzero.
- must-fail (P3): a copy with two `── Gate 104:` headers **both in the full-suite region** (the real collision shape) → exit nonzero, names both. **Companion must-PASS (guards against the false-positive flood):** an unmodified dual-region gate — one `── Gate N:` echo in the `--check` dispatcher (with the `(per-gate run)` wording) plus one in the full-suite region (with the canonical wording) — must NOT be flagged, proving the check keys on region, not on description-difference (87/150 shipped gates have exactly this legitimate shape).
- must-fail (P5): a synthetic gate with the real hook-invocation signature (stdin piped into a `hooks/*.sh` script, `rc=$?` captured) whose companion `-eq 2` check is missing — only a bare nonzero must-fail — → exit nonzero, names the gate. **Companion must-PASS (guards against the false-positive flood):** the 49 internal-decision-engine "blocks"/"deny"-named gates measured this session (e.g. `:1590`, `:2148`, `:2279` — asserting a `thing_decision`/`_predeny` string/boolean or an adapter's translated JSON field, never a hook-process exit code) must NOT be flagged, proving the check keys on the hook-invocation signature, not on the gate name.
- must-fail (P6): a catalog copy with a deliberately malformed regex → `check-regex-catalog-compiles.py` exit nonzero, names the line.
- **P4 has no must-fail fixture in this phase, by design — stated here rather than left implicit.** It is a doc-convention addition (above), not a check `check-gate-registration.py` runs, so there is nothing for a fixture to exercise; a future automated liveness-probe scan would need its own must-fail half when it ships.
- pass-on-good: the current, already-fixed tree passes.
- **pre-build gate (both panels demanded this):** run the drafted parser against the CURRENT `audit-gates.sh` before registering it and confirm **zero false positives** on the ~194 shipped gates — a parser that floods the suite on day one gets disabled, the exact fate the posture doc warns a constantly-firing guard invites. Then register in both regions and **grep the suite output for the new gate names** (`:6119`); assertion count must rise by the number added.

**Teeth:** [not-hollow] must-fail halves + both regions + suite-grep for the P2/P3/P5/P6 sub-checks; the
P4/UNWIRED sub-check is the one exception, honestly scoped above as a doc convention with no must-fail
half of its own — not read as claimed must-fail coverage · its own registration is subject to
its own reachability rule (a good self-consistency property) · [exit-2] any parse ambiguity (a header with
no match, an unreadable file) exits nonzero, never silently skips · [macOS] pure Python 3.9 stdlib
(`re`/`pathlib`), `from __future__ import annotations` (the PEP-604 door the v0.194.0 `check-md-links.py`
fix named) · [contract] built against `── Gate N:`, the `--check` boundary at `:881`, the `Supported:`
list at `:877` — all read this session · [surfaces] the `Supported:` string checked against the real case
labels — two surfaces, not a hardcoded list · [SNR] **structurally satisfied** — a CI/audit-gates reader,
never a `PreToolUse` deny, so it cannot deny a `Write`; its must-fail fixtures are synthetic `mktemp -d`
copies, never the live file.

**`depends_on_claims: [CL-3, CL-15, CL-4, CL-25]`**

---

### Phase 2 — Author-time portability lint · closes P1 (highest recurrence)

**Goal.** Ship a portability lint with two front doors, mirroring `enforce-layout.sh`↔`validate-layout.yml`:
1. **In-loop `PreToolUse(Write|Edit|MultiEdit)` hook** (`plugins/ravenclaude-core/hooks/enforce-portability.sh`, new) that DENIES a
   write introducing a banned bash-4/GNU token — associative-array declaration, `mapfile`,
   upper/lower parameter-expansion, `globstar`, an unshimmed timeout, PCRE-`grep`, an in-place stream edit,
   GNU-only find idioms — unless routed through `plugins/ravenclaude-core/hooks/_portable.sh` (confirmed present, `_rc_timeout` at
   `_portable.sh:37`). Deny copied from `enforce-layout.sh:94–105` (`hookSpecificOutput`
   `permissionDecision: deny` JSON + exit 2); absent-target / stdin-`jq` fallback per `enforce-layout.sh:40–46`.
2. **CI backstop** — a new **step** (never a new required workflow with a `paths:` filter — see Risk M4)
   inside the already-required whole-tree `validate-marketplace.yml`, running the same linter over
   `plugins/**/hooks/*.sh` + `scripts/*.sh` + `scripts/ravenclaude` (the extension-less installer that
   fell outside the `scripts/*.sh` glob and broke at #885) + `plugins/*/bin/rc` + `plugins/*/monitors/**`
   (confirmed this session: the only shipped `monitors/` lives at `plugins/ravenclaude-core/monitors/`
   — there is no top-level `monitors/` at repo root — so an unprefixed `monitors/**` glob, as an earlier
   draft of this bullet had it, would silently match zero files and exclude `watch-run-state.sh` from
   the very lint this phase's live-open item (b) claims to extend coverage to; `.repo-layout.json`'s own
   allow-list already uses the correct `plugins/*/monitors/**` form).

**Enforcement posture is an owner fork — Fork 3 (below), reconciled to Panel B's graduated knob** (in-loop
**warn** default, escalatable to **block** via a `macos_portability_lint: off|warn|block` comfort-posture
knob matching the existing `git_protocol` precedent), with wide scope (Panel A) because the two most
recent breaks (#885, #873) were *outside* `hooks/**`.

**Classes closed + live-open remediated:** P1. Live-open: (a) lints the **current** tree, surfacing the
#885 apostrophe-in-heredoc-in-substitution residue and the #873 `pip`-vs-`python3 -m pip` shape the runner
does not lint; (b) extends coverage past `hooks/**` to `plugins/*/monitors/**`/`scripts/**`/entrypoints; (c) folds in
the deferred packaging move — `premise-gate.py`/`classify_claim.py` from marketplace-root `scripts/` to
`${CLAUDE_PLUGIN_ROOT}` across 6 call sites (v0.243.0 "Still open", already Gate-187-adjacent) as a tracked
remediation item.

**Files touched:** `plugins/ravenclaude-core/hooks/enforce-portability.sh` (new), `scripts/check-portability-lint.*` (new),
`plugins/ravenclaude-core/hooks/hooks.json` + `.claude/settings.json` (register PreToolUse, both wirings — the dev-mirror
dual-registration convention CLAUDE.md's "Marketplace-dev hooks" section requires),
`.github/workflows/validate-marketplace.yml` (CI step), `scripts/audit-gates.sh` (new gate + must-fail half).

**Acceptance tests + pre-build gates:**
- must-fail: the #885 apostrophe shape, plus one fixture per banned construct in isolation — each DENIED (exit 2) by the hook and flagged by the CI linter.
- pass-on-good: a script routing the same operation through `_portable.sh` (`_rc_timeout`/`_rc_upper`/`_rc_pcre_match`) passes; a benign write passes; a write to a file *outside* the scoped globs containing a banned token passes (scope discipline).
- pass-on-good (SNR self-test): editing the portability hook's OWN source to add a new banned-token check, routed through `_portable.sh`, is allowed.
- **pre-build gate:** dry-run the deny logic (report-only) over every currently-shipped file under the scoped globs; confirm zero unexpected denials before flipping live. New gate registered both regions + suite-grep; **run `check-macos-portability.sh` on macos** to confirm the lint and the runner agree (assert-against-each-other — author-time half vs execution half).

**Teeth:** [not-hollow] one must-fail per banned construct (a hook catching only one construct while
missing another would itself be hollow) + both regions + suite-grep · [exit-2] deny is exit **2**;
unreadable target / missing `jq` → exit 0 fail-safe (the `enforce-layout.sh` contract — a portability lint
that hard-fails a consumer with no shell surface would be worse than the gap) · [macOS] the lint itself is
bash-3.2-safe (`grep -E`, no PCRE; no associative arrays) — it must not open a door while closing one ·
[contract] built against `_portable.sh`'s real exported shims and the `enforce-layout.sh` deny contract,
both read this session · [surfaces] the CI linter and the `macos-latest` runner assert the same
banned-token set from two angles (static author-time vs runtime execution) — a divergence between them is
itself a failure · [SNR — **RISK M1**] this is a genuine `PreToolUse` deny hook and its own fixtures,
`_portable.sh` (banned tokens in comments), and `check-macos-portability.sh` (which deliberately
re-introduces banned constructs in its mutants) all *contain* the tokens as data — exactly P7.
**Mitigation up front:** a sanctioned-exempt allowlist (`plugins/ravenclaude-core/hooks/_portable.sh`, `check-macos-portability.sh`,
`tests/fixtures/**`, the linter's own source) + a `# noport` in-file sentinel; the residual (a banned token
in a *new* comment in someone else's script) is accepted as advisory-warn, not deny. Shares the exempt-path
design with Phase 11 and reuses its outcome if Phase 11 ships first.

**`depends_on_claims: [CL-2, CL-16, CL-23]`** (CL-23 ShellCheck `SC3xxx` complement is `[unverified —
training knowledge]` and WARN — do not gate the build on it; verify against ShellCheck docs before relying,
and prefer the perl/`_portable.sh`-backed in-repo lint over an external-tool dependency, per the v0.196.0
"why perl, not install-GNU-grep" reasoning).

---

### Phase 3 — Fail-closed exit-code execution audit · closes P5, P6

**Goal.** Extend the `check-macos-portability.sh` execution runner into a general **hook exit-code /
fail-closed audit**: drive every `PreToolUse` enforcement hook with malformed / empty / error-shaped input
under `env -i PATH=/usr/bin:/bin` on macos **and** ubuntu, and assert the outcome is **deny(2) or
safe-noop(0), never a fail-open exit 1** (a static syntax check provably cannot see this class — the
constructs are valid, they fail only at runtime, the same reasoning `check-macos-portability.sh:26–30`
states for a different family). Add a static lint that every verdict-resolving `case`/`if` chain ends in
an explicit non-permissive default arm (the v0.205.1 tie-breaker "else → allow" fix) and a trap-ordering
check (the EXIT trap armed before the first fallible op — the v0.205.1 "`_emitted`-after-write" fix). The
hook enumeration reuses **Phase 1's** machine-read of `hooks.json` (import, not re-derive).

**Classes closed + live-open remediated:** P5, P6. Live-open: no blanket meta-check currently drives every
enforcement hook's deny/error/else fixture; the associative-array index-0 collision (C4) rewrite trap is
audited only inside `thing-orchestrator.sh` — this phase's execution pass is the wider audit over any
sibling using the same role-keyed pattern.

**Files touched:** `scripts/check-hook-failclosed.sh` (new — the execution runner),
`scripts/check-verdict-default-nonpermissive.py` (new — the static lint, deliberately separate so it runs
without executing anything), `.github/workflows/validate-macos.yml` (add the audit; keep `macos-latest` +
an ubuntu matrix leg), `scripts/audit-gates.sh` (new gate + must-fail half).

**Acceptance tests + pre-build gates:**
- drive-each-hook: feed `{}`, malformed JSON, and an error-inducing payload; assert exit ∈ {0, 2}.
- must-fail: a mutant hook whose error/deny branch resolves to exit 1 (fail-open) MUST be caught.
- must-fail (static): a `case` chain ending in a permissive `*)` allow MUST be flagged.
- pass-on-good: the current tribunal (`thing-orchestrator.sh`) and `route-decision-review.sh` — already hardened for this class — pass clean (proves the audit isn't just re-finding what's fixed).
- **pre-build gate:** registered both regions + suite-grep; **assert the observed deny exit is literally 2, not merely nonzero** (`:1047–1048`). Depends on Phase 1 (imports the parse) and Phase 2 (the new portability hook is one of this audit's targets — running Phase 3 before Phase 2 would silently skip the newest hook).

**Teeth:** [not-hollow] the exit-1-vs-exit-2 must-fail reproduces a dated real shape (Gate 6's counterfeit
deny subtests) + both regions + suite-grep · [exit-2] this *is* the fail-closed mechanism; a missing
interpreter during a hook's own test run is a hard CI failure via the existing `_skip_or_fail`
(`audit-gates.sh:945–957`), never a silent skip · [macOS] runs under `env -i PATH=/usr/bin:/bin` exactly
like the runner it extends; bash-3.2-safe · [contract] built against the exit-code contract in
`check-macos-portability.sh:83–85` and the exit-2 assertion at `audit-gates.sh:1047–1048` · [surfaces]
runs the *same* hooks on macos+ubuntu and asserts identical deny/safe-noop outcomes — a platform
divergence is a failure (how the original doors hid) · [SNR] **structurally satisfied** — it *executes*
hooks with crafted input (no prose-scan surface); the static verdict-default lint could match a
commented-out `*) allow`, mitigated by the same `# noport`-style sentinel as Phase 2.

**`depends_on_claims: [CL-4, CL-17]`**

---

### Phase 4 — Surface-parity gate · closes P11, P12 (names, does not build, the P17 host-scope variant — see Phase 8)

**Goal.** Generalize Gate 51's derive-and-compare (`audit-gates.sh:4282–4421`, already running the same
render check over **both** `dashboard.html` and `index.html` — **verify the gate number against the current
`audit-gates.sh` before building: this mechanism shipped under "Gate 144" until a harness renumber
(corrected pass 13; Gate 144 is now the unrelated Prompt Builder XSS check at `:5377`), and gate numbers
drift**) into a reusable **N-surface parity engine**:
for a declared surface pair, derive the expectation from ONE surface and assert the other agrees — never a
constant. Three variants:
- **route/placement parity (P11):** for every nav route/tab, extract the destination from the standalone `ds-nav` chrome (the SSOT the portal folds in) and assert the portal's `DASH_OWNER` + that section's `navChildren` agree — the v0.216.0 "third time this shape shipped" fix generalized over the full route set.
- **behavioral parity (P12):** dispatch both `serve-dashboards.py` copies (root + bundled) with identical requests and diff responses (busy-port recovery, root redirect, CSRF host-keying, `/__sleipnir` handler existence) — closing the Gate-32 blindness to `main()` drift.
- **host-scope-sentence parity (P17):** assert every host-name+capability string in generated output traces to a `host-support.json` lookup. **Clarified in this pass — this is a forward-reference, not a Phase 4 deliverable:** unlike variants 1 and 2 above, this bullet has no dedicated file or must-fail test anywhere in Phase 4's own spec below. The actual mechanism is built once, in **Phase 8** (which extends Gate 154 for exactly this purpose — see Phase 8's Goal (a)); Phase 4 does not independently build a second copy. This line is kept here only to name the capability up front; the coverage-table P17 row and the DAG both already attribute the build to Phase 8. Stating this explicitly closes a real ambiguity the original draft left open: without it, a builder reading only Phase 4 could reasonably start implementing this variant from scratch, recreating R2 (duplication) *inside this very plan* — the exact failure Phase 1's shared-primitive-import discipline (§0) was written to prevent for the meta-gate parse, but which was left unstated here.

**Honesty caveat (both panels):** each surface pair needs a bespoke extractor, so cost scales with surface
count. If the server-twin instance needs enough bespoke logic that "one generic engine" is really two
scripts sharing a comment convention, **ship it honestly as two scripts** rather than force a false
abstraction — a false generalization would itself be a hollow gate.

**Classes closed + live-open remediated:** P11, P12; contributes P17. Live-open: no generic N-surface
parity gate exists (Gate 51 — the DASH_OWNER derive-and-compare mechanism, per the Goal's confirmed
current-tree citation above — is case-by-case; **not** Gate 144, which this session's direct read
(`audit-gates.sh:5376-5377`) confirms is the unrelated Prompt Builder XSS floor, not a parity check at
all — the pre-renumber pairing this line inherited from `problem-inventory.md`'s historical citation is
now stale and is corrected here rather than silently carried); Gate 32 remains blind to `main()` drift;
the twin `serve-dashboards.py` is still two hand-maintained copies (the durable fix is a shared import).

**Files touched:** `scripts/check-surface-parity.py` (new engine, `(derive_fn, assert_fn)`),
`scripts/check-dashboard-server-parity.py` (extend name-parity → behavioral-parity, or a sibling),
`scripts/audit-gates.sh` (new gate + must-fail halves).

**Acceptance tests + pre-build gates:**
- must-fail (P11): a fixture where the standalone homes a tab under Control but the portal's `DASH_OWNER` says Catalog → exit 2 (the exact v0.216.0 regression); and a link moved out of its correct `navChildren` while `DASH_OWNER` unchanged → exit 2.
- must-fail (P12): a fixture where one server copy 500s on `/__sleipnir` while the other serves it, and one with busy-port recovery patched out → exit 2.
- pass-on-good: the current tree (a positive control).
- **pre-build gate:** confirm the `derive_fn`/`assert_fn` split genuinely generalizes past these two instances before claiming "generic"; both regions + suite-grep.

**Teeth:** [not-hollow] two must-fail halves per instance, replaying real shipped regressions · [exit-2]
exit 2 on any disagreement — a placement bug is a user-visible dead-end, not a nit · [macOS] Python; the
behavioral leg dispatches the servers via stdlib http · [contract] built against Gate 51's real
derive-and-compare (`:4282–4421`) and Gate 32's documented endpoint-name-only limitation · [surfaces] this
mechanism *is* the assert-against-each-other prior in its purest form — derive from one, check the other ·
[SNR] **structurally satisfied** — a CI reader comparing two generated artifacts, no prose-scan surface.

**`depends_on_claims: [CL-6, CL-14, CL-18]`**

---

### Phase 5 — Count-SSOT DROP refactor · closes P13 (shrinks P14; contributes P17/P19) · OWNER-GATED [Fork 1]

**Goal.** Execute the **already-converged** count-ssot plan pair (reuse, do not re-derive — per scope).
The recommended direction: DROP the granular per-artifact count literals ("N skills, N templates…") from
~180 `plugin.json` descriptions, their `marketplace.json` mirrors, and README count tables; keep only
self-evident enumerations (the roster `agents (a, b, c…)` carries no standalone digit). Add a
**negative-assertion gate** (no description may contain a digit immediately followed by an
agents/skills/templates/commands/hooks/rules word; fails closed, doubles as a migration-completeness proof).
**RC_BASELINE is the owner fork (Fork 1)** and this phase does not proceed to the DROP build until the
owner rules it — the reconciled options (drop / independent-scanner-generate / keep-golden, plus Panel B's
hybrid) are laid out in [§ Divergence reconciliation](#divergence-reconciliation) and
[§ Owner decisions](#owner-decisions).

**Classes closed + live-open remediated:** P13. Live-open (this-session-confirmed at
`check-marketplace-claims.py`): the checker verifies only **2 of 6** counted quantities; ~180 README
tables have **zero** coverage; the Copilot verbatim-inheritance channel (`generate-copilot-plugin.py:421`)
stays open until core's description drops the count. The DROP eliminates the class by construction.

**Files touched:** ~180 `plugin.json` + `marketplace.json` + README tables (DROP),
`scripts/count-core-sections.py` (new — only if the independent-scanner option is chosen),
`scripts/check-marketplace-claims.py` (add the negative-assertion gate; extend 2/6 → all 6 count types),
`check-plugin-detail-render.mjs:54` (de-hardcode `RC_BASELINE`), `scripts/audit-gates.sh`.

**Acceptance tests + pre-build gates:**
- must-fail: a `plugin.json` description reintroducing a count literal → the negative-assertion gate exits 2.
- must-fail (independent-scanner option only): a fixture proving the independent scanner and the render's `scan_repo` **can** diverge (not a tautology — the load-bearing non-collusion property both count-ssot plans require).
- **owner-decision pre-build gate:** the RC_BASELINE ruling recorded in `docs/decisions/` before the DROP build starts. Whole-tree prettier + the negative gate registered both regions + suite-grep.

**Teeth:** [not-hollow] the negative-assertion gate has a must-fail half + both regions + suite-grep; it is
*stronger* than a freshness gate because DROP makes the class impossible-by-construction · [exit-2] exit 2
on any surviving literal · [macOS] Python 3.9 stdlib scanners · [contract] grounded in the converged plan
pair (read this session) and `generate-copilot-plugin.py:421` · [surfaces] the independent-scanner-vs-
`scan_repo` cross-check IS the assert-against-each-other prior; keep-golden forgoes it (a golden literal is
a constant — the very R2 anti-pattern), which is the substance of Fork 1 · [SNR] n/a — the negative gate
matches description literals, which are genuinely consumer-read prose being forbidden (no fix/test to
falsely deny).

**`depends_on_claims: [CL-5, CL-19]`**

---

### Phase 6 — Behavioral canary as host-onboarding acceptance bar · closes P16, P18 (+ P17) · OWNER-GATED [seed #5]

**Goal.** Require every `--host X` installer to **end with a behavioral canary** — trigger the host's real
invocation path and confirm a planted marker fired — not a files-exist check (generalizing Gate 167's
Copilot→tribunal round-trip). Add a per-host `activation_gate` field to `host-support.json`
(`hash_trust | version_floor | none`; the file already carries a per-component per-host schema, confirmed
this session), consumed by **one shared re-arm-notice helper** at install/update/status (the Codex
hash-trust + Copilot version-floor retrofits become one abstraction instead of per-host copies).

**Classes closed + live-open remediated:** P16, P18; contributes P17. Live-open: MH-05 (whether every
affected dashboard panel got the honest-empty-state treatment and the host-verdict banner landed — not
re-verified) — this phase's build includes running that verification and either closing it or re-ticketing
it; any future host lane reproduces the disarm shape unless the check is mandatory shared onboarding.

**Files touched:** `scripts/ravenclaude` (canary step at end of each `--host` install),
`plugins/ravenclaude-core/knowledge/host-support.json` (`activation_gate` field — a schema extension, so
the gate that pins it updates in the same commit), a shared `_rc_rearm_notice` helper, `scripts/audit-gates.sh`.

**Acceptance tests + pre-build gates:**
- must-fail: an installer mutant that reports success while the planted marker never fires → the canary MUST catch it (the MH-07 "wires nothing, says nothing" shape).
- must-fail: a host with `activation_gate: hash_trust` whose re-arm notice is stripped on `update` → caught.
- pass-on-good: the existing Codex + Copilot lanes (canary-proven per Gate 167) pass under the generalized mechanism.
- remediation: re-verify MH-05 and record the result.
- **pre-build gate:** confirm the `host-support.json` schema addition doesn't break its gate-pin; both regions + suite-grep. **Owner ratifies mandatory-vs-advisory (seed #5) before it becomes a hard onboarding bar.**

**Teeth:** [not-hollow] must-fail halves; the canary fires the host's real path, not a files-exist check ·
[exit-2] a host lane whose canary can't be confirmed to fire ships as unsupported in `host-support.json`,
not silently assumed working; the re-arm notice at `update` is the fail-loud complement to the silent
disarm · [macOS] bash-3.2-safe installer + Python helper; reuses `_portable.sh` where the canary needs a
bounded timeout · [contract] grounded in Gate 167, the MH-07/MH-17 ledger findings, and the
`host-support.json` SSOT pinned by Gate 154, all this session · [surfaces] the canary asserts the host's
*real runtime behavior* against a *planted marker* — the strongest surfaces-against-each-other form (an
actual execution, not two static texts) · [SNR] **structurally satisfied** — an installer-time canary, not
a write-time deny hook.

**`depends_on_claims: [CL-9, CL-21]`** (both WARN-tier; owner ratifies mandatory-vs-advisory, seed #5.)

---

### Phase 7 — Self-heal push-safety invariant · closes P14

**Goal.** A CI invariant that self-heal workflows can only ever open a PR, never mutate the protected
`main` ref directly: assert `regenerate-artifacts.yml` (and any future self-heal workflow) has **no
direct-to-`main` push path** — it already uses `peter-evans/create-pull-request` on
`chore/self-heal-artifacts` (`:372`/`:386`), but nothing gates a regression. Add a post-self-heal
freshness re-check on the opened PR head, and a hermetic-render assertion (tree byte-identical after
`audit-gates.sh` — the v0.208.0 render-to-temp discipline). Independent of Phase 5's timeline; Phase 5's
DROP is the durable fix (fewer artifacts under exact-byte gates), this is the point-fix that holds until it
lands.

**Honest bound on the "no direct-to-`main` push" check — it is a proxy-string scan, not a behavioral
proof (added this critic pass, applying the plan's own anti-proxy discipline to itself).** The *runtime*
guarantee that a self-heal workflow cannot mutate `main` is the **branch-protection ruleset**, not this
grep — verified against the workflow's own comments this session (`:358`, `:367–369`: "main is protected:
direct `git push origin HEAD:main` is rejected by the ruleset"), and note the current workflow lands on
`main` *only* through its auto-merged PR (`:416–424`), never a push. This text-scan is therefore
**defense-in-depth that catches the enumerated literal push shapes at PR-review time** — earlier than the
ruleset's runtime rejection. By construction it **cannot see** a computed-ref push (`git push origin
"$B":main`), a `gh api` commit onto `main`, or a `gh pr merge --admin` bypass — a main-mutating regression
in any of those shapes passes this grep green (the exact fail-open R5/R1 class this phase fixes, reproduced
one level up). So the check is **paired with the ruleset, never a replacement for it**, and its must-fail
half must enumerate the push shapes rather than assert a single literal (below).

**Classes closed + live-open remediated:** P14. Live-open: the cascade recurs faster than the count-SSOT
refactor lands; every new generated surface adds a freshness gate + a self-heal path. The named incidents
are already fixed; this phase adds the standing invariant the inventory notes is missing.

**Files touched:** `scripts/check-selfheal-push-safety.py` (new — greps self-heal workflows for a
direct-to-`main` push path), `.github/workflows/regenerate-artifacts.yml` (post-heal re-check step),
`scripts/audit-gates.sh`.

**Acceptance tests + pre-build gates:**
- must-fail: a workflow fixture reintroducing a direct-to-`main` push in **each enumerated shape** — `git push … main`, `git push … HEAD:main`, `git push … :refs/heads/main`, and a `gh pr merge --admin` bypass — each → exit 2 (a single-literal fixture would leave the other shapes silently uncaught, the P8 "fix-one-instance" trap inside this very check).
- pass-on-good: the current PR-only `regenerate-artifacts.yml` (the auto-merged-PR path at `:416–424` is NOT flagged — it lands on `main` through the ruleset's required checks, not a push).
- hermeticity: a self-heal run against a known-stale tree — the post-run freshness check on the PR head must pass (proving the self-heal actually fixed what it claims, not an empty PR).
- **pre-build gate:** both regions + suite-grep. (May not need Phase 1's library — a text-scan over workflow YAML is simpler than parsing `audit-gates.sh`; a genuine "no dependency" case, not a missed reuse.)

**Teeth:** [not-hollow] the push-safety assertion is a structural grep for an *absence* (which P4 warns can
silently empty) — the multi-shape must-fail fixture proves it catches the **enumerated** literal push shapes
(`git push … main` / `HEAD:main` / `:refs/heads/main` / `--admin` merge), **not** the full class of
main-mutations; a computed-ref or `gh api` regression evades any text-scan, so the branch-protection ruleset
(not this grep) is the actual guarantee against those — the honest bound is stated in the Goal, so this line
is not read as claiming coverage it does not have · [exit-2] a workflow the checker can't parse fails the
check, not passes · [macOS] pure Python YAML text parse · [contract] grounded in
`regenerate-artifacts.yml:367–388` (the PR-open + auto-merge path) and the ruleset-rejects-direct-push
comments at `:358`/`:367–369`, read this session · [surfaces] the freshness re-check on the
PR head (not the pre-self-heal state) is a surfaces-against-each-other assertion · [SNR — small RISK] the
workflow-grep could match a direct-to-`main` push token inside a *comment* explaining the rule (the file
has such prose at `:367`). Mitigated by matching only an un-commented `run:`-line push + the `# noport`-style
sentinel; the clean fix is Phase 11's exempt path.

**`depends_on_claims: [CL-5, CL-19]`**

---

### Phase 8 — Cross-host projection / host-capability lint + adapter round-trip gate · closes P17

**Goal.** Three additions: (a) extend Gate 154 to scan generator output for literal host-name+capability
strings not traceable to a `host-support.json` lookup — **this is the same capability Phase 4's Goal names
as "host-scope-sentence parity (P17)"; it is built exactly once, here, and Phase 4 does not build a second
copy** (clarified in this critic pass — see Phase 4's note); (b) a `check-frontmatter.py`-sibling
(`check-host-capability-citations.py`) that scans generator output and hand-written `knowledge/`/`docs/`
prose for a host name adjacent to a supported/unsupported/native verb without a dated basis or
`host-support.json` cross-ref (the MH-03 uncited-claim shape) — **hard-fails the build (exit 2) only
where a `host-support.json` cross-ref exists to gate against** (generator output, and any `knowledge/`
claim resolvable to the SSOT); an un-marked claim in free-form `docs/` prose with no resolvable cross-ref
is an **advisory nudge, not a build failure** — the same oracle-backed-vs-advisory split the Teeth
`[exit-2]`/`[SNR]` lines below state (**corrected this critic pass — this Goal bullet previously said
"fails the build" unconditionally, contradicting the narrower scope pass 6 already gave the acceptance
test and the `[exit-2]`/`[SNR]` teeth lines; a builder reading only the Goal, the primary spec, would
have built the over-broad hard-blocking `docs/`-prose scanner the teeth fix exists to rule out**);
(c) a standing **adapter round-trip gate** per host (deny + reason must survive
translation), generalizing Gate 167 — closing the v0.250.0 "adapters kept the deny, threw away the reason"
regression. Composes Phase 6's `activation_gate` field and Phase 12's provenance-marker convention.

**Classes closed + live-open remediated:** P17. Live-open: MH-28 (the claim-grounding fix survives at two
call sites the fix did not reach — this phase locates and fixes them); no gate fails a build on an uncited
host-capability claim traceable to `host-support.json` (a free-form `docs/`-only claim stays advisory, not
a build failure — see the Goal and Teeth `[exit-2]` scoping above); not every host-facing sentence reads
from `host-support.json`.

**Files touched:** `scripts/check-host-support.py` (extend), `scripts/check-host-capability-citations.py`
(new), `scripts/audit-gates.sh`.

**Acceptance tests + pre-build gates:**
- must-fail: a generated manifest listing slash commands on a host the plugin says has none (MH-27) → exit 2.
- must-fail: an uncited "host X reads file Y" claim with no dated basis, **in generator output or a `knowledge/` file where a `host-support.json` cross-ref exists to gate against** → exit 2. (A free-form `docs/`-prose claim is advisory, not a hard exit-2 — see the Teeth `[exit-2]`/`[SNR]` lines.)
- must-fail: an adapter mutant that drops the deny reason → the round-trip gate catches it.
- pass-on-good: the current, already-corrected `AGENTS.md` host table with dated per-row basis.
- **pre-build gate:** depends on Phase 6 (`activation_gate` + re-arm helper) and Phase 12 (the provenance-marker convention this generalizes from single-file advisory to generator-output-wide static check); both regions + suite-grep.

**Teeth:** [not-hollow] must-fail halves replay real previously-corrected false claims + both regions +
suite-grep · [exit-2] exit 2 where a **deterministic oracle backs the check** — (a) generator-output
parity and (c) the adapter round-trip target machine-produced text, and (b)'s `host-support.json`-cross-
referable claims (generator output + `knowledge/`) hard-fail against that SSOT; **but sub-check (b) is
itself a prose scan of hand-written `knowledge/`/`docs/`, so its free-form `docs/` subset is advisory,
NOT exit-2 — the `[SNR]` line below concedes exactly this, so "exit 2 on *any* uncited host claim" would
over-claim.** The deliberate contrast with Phase 12 therefore holds for the oracle-backed surfaces only;
over `docs/` prose (b) is the same advisory-nudge shape Phase 12 is, and the hard gate is justified by the
deterministic `host-support.json` oracle, never by the (hand-written) text being "machine-produced" ·
[macOS] Python 3.9 stdlib,
`from __future__ import annotations` · [contract] grounded in Gate 154, Gate 167, and the AGENTS.md
dated-per-row basis convention, read this session · [surfaces] host-scope sentences asserted against
`host-support.json` (the SSOT), never a hand-typed constant — the shared surface-parity prior · [SNR —
partial RISK] the host-capability-claim lint is a prose scan of `knowledge/`/`docs/` and could match a
sentence *documenting* a false claim it is retracting (the supersession-note shape). Mitigation: honor an
inline `[docs-verified <date>]`/`[unverified]` marker as the exempt signal; scope to un-marked absolute
claims only; residual accepted as advisory for the `docs/` subset.

**`depends_on_claims: [CL-9, CL-18, CL-20]`**

---

### Phase 9 — Catalog-scoping-consistency lint + regex-catalog rollout completion · closes P8 (+ P6 remainder)

**Goal.** Turn the enumerate-the-class discipline (prose today) into a check: ship
`scripts/check-trigger-scoping-consistency.py` that groups comfort-posture triggers by block/category and
flags any bare unscoped wildcard across a command separator where a sibling in the same block uses an
explicit separator-excluding character class; require the same pattern's other matches to be in the diff or
waived. Would have caught **both** the unscoped-wildcard incidents (a force-push rule and a
fetch-piped-into-a-shell rule, fixed one release apart) statically. Finish rolling **Phase 1's**
regex-compile primitive out to every remaining regex-bearing catalog (import, not re-derive).

**Classes closed + live-open remediated:** P8, P6 remainder. Live-open: the enumerate-the-class step is
prose; the existing recompile checks validity, not scoping consistency; nothing greps the catalog for a
bare unscoped wildcard beside a scoped sibling. This phase's grep-for-the-class run is what a standing
check would have caught between the two dated incidents.

**Files touched:** `scripts/check-trigger-scoping-consistency.py` (new), reuses
`scripts/check-regex-catalog-compiles.py` from Phase 1, `scripts/audit-gates.sh`.

**Acceptance tests + pre-build gates:**
- must-fail: a synthetic two-trigger block where A uses a bare wildcard and B (same category, same danger shape) uses a separator-excluding class → exit 2.
- regression: replay the two dated incidents as historical snapshots — the checker flags the second-found sibling at the *first* incident's snapshot, and is clean at the post-second-fix snapshot.
- pass-on-good: the current post-fix catalog.
- **pre-build gate:** confirm the scoping-consistency property is genuinely derivable from the diff rather than requiring semantic judgment about which sibling belongs to which danger class; if a block can't be cleanly classified, the fallback is a **flag, not a block** (an open design risk in the risk matrix, not resolved by fiat). Both regions + suite-grep.

**Teeth:** [not-hollow] the two-incident regression fixture is real history, not synthetic · [exit-2] exit
2 on a scoping inconsistency; if the checker can't confidently classify a block it defaults to flagging,
never silently passing · [macOS] Python 3.9 stdlib · [contract] grounded in the two named incidents and the
scoped-sibling separator-excluding pattern the fixes used · [surfaces] it asserts sibling triggers in one
block against each other (the scoped sibling is the oracle for the unscoped one) — R2 applied to catalog
rules · [SNR — **RISK M1**] the lint scans the catalog, which contains regex literals that look like the
thing being forbidden — exactly the P7 minefield (writing a fixture requires a destructive-looking literal).
Mitigation: `printf`-assembled fixtures (the current workaround) + Phase 11's exempt path if it ships; if a
future iteration converts it to a `PreToolUse` advisory nudge it must ship advisory-only.

**`depends_on_claims: [CL-8]`**

---

### Phase 10 — Subagent-safe-guard authoring checklist/fixture · closes P9

**Goal.** A **subagent-safe-guard authoring checklist + reusable two-worktree fixture harness**: every
stateful `PreToolUse` guard must (a) declare its state key + prove it varies per parallel agent (a
2-worktree fixture: worktree A's record must not block worktree B), and (b) expose a **file-based escape**
whose *refusal* paths (missing key, empty value, cross-scope control) are tested before the success path.
Gate 190's two-worktree teeth test (`audit-gates.sh:801`) is the template to generalize. Audit the other
session-keyed substrates (runaway-brake counters, thing runaway dirs) against the checklist now.

**This phase is directly reinforced by the live evidence** — Panel B's Write-placeholder-then-Edit tunnel
this run is a fresh instance of the exact "guard escape unreachable → tunnelled" class this phase closes
(see [§ Empirical evidence](#empirical-evidence-generated-during-this-run)).

**Classes closed + live-open remediated:** P9. Live-open: the generalizable principle is un-gated; no
standing check asks, for any *other* guard shipping an env-var escape, whether that escape is reachable
from a subprocess; the other session-keyed substrates haven't been audited.

**Files touched:** `plugins/ravenclaude-core/knowledge/subagent-safe-guard-checklist.md` (new) + a reusable
two-worktree fixture harness a future guard's own test file imports, `scripts/audit-gates.sh` (generalize
Gate 190's teeth over the guard set).

**Acceptance tests + pre-build gates:**
- must-fail: a guard keyed on `session_id` (not worktree) where A's negative blocks B → the 2-worktree fixture catches it (the v0.245.0 collision).
- must-fail: a guard whose only escape is an env var a `Bash` call can't pass to the hook process → flagged.
- audit remediation: `runaway-brake.sh`'s counters run through the checklist, pass/fail recorded, fixed if failing.
- **pre-build gate:** none — independent of every other phase; both regions + suite-grep.

**Teeth:** [not-hollow] must-fail halves (the collision + the unreachable-escape) reuse a real dated
incident + both regions + suite-grep · [exit-2] a guard failing the collision fixture is a genuine build
blocker for that guard's own merge, not advisory · [macOS] bash-3.2-safe fixture using `git worktree add`
(already used in this repo's worktree tooling; no GNU-only flags) · [contract] built on the confirmed-shipped
v0.245.0 worktree-scoping + file-based-control fix (Gate 190, `:801`) · [surfaces] the two-worktree fixture
is two independent instances of the same guard asserted not to interfere — the runtime-level
surfaces-against-each-other prior · [SNR] **structurally satisfied** — a checklist + test harness, not a
deny hook.

**`depends_on_claims: [CL-11]`**

---

### Phase 11 — Sanctioned-guard-escape door + premise-guard scope fix · closes P7 (contributes P9) · OWNER-GATED [Fork 2]

**Goal.** Build the twice-deferred sanctioned-exempt door for the intent-bearing hard-rule guards, plus fix
the two concrete exemption bugs this run exposed. Two halves, **sequenced by risk**:

**Half A — the low-risk half, ships immediately, no wider owner ruling required:**
- Fix the `.ravenclaude/runs/**` exemption so it covers **nested worktrees** — the exemption is computed by
  stripping `CLAUDE_PROJECT_DIR` from the write path before checking the `.ravenclaude/` prefix, and in a
  nested-worktree session that comparison can fail even when the target is genuinely under
  `.ravenclaude/runs/`. This denied the miners' own Writes and the panel drafts this run.
- Fix / close the **Write-scoped-matcher gap**: `guard-premise.sh`'s T-PROSE screen appears scoped to
  `tool_name == "Write"` only, so an `Edit` evades it — which is simultaneously a false-positive-mitigation
  gap and a *tunnelling* surface (Panel B used exactly this Write-placeholder-then-Edit path this run).
  **`[unverified — confirm matcher scope during build]`** — the exact scope must be read from the guard
  source before this fix is designed; the remedy is to make the screen tool-agnostic (cover `Edit`/`MultiEdit`)
  **and** give it a reachable sanctioned escape so the correct response to a false-positive is the escape,
  not a tunnel.
- **Fix `xc.tribunal-self-disable`'s verb-name-near-path trigger to distinguish a read from a mutation**
  (`plugins/ravenclaude-core/scripts/thing-concerns.py:screen_always`, trigger #2 in
  `plugins/ravenclaude-core/knowledge/concerns-catalog.md`) — `'(?s)\b(rm|unlink|shred|mv|cp|install|ln|tee|
  sed|perl|awk|truncate|dd|chmod|chown|patch|sponge)\b.{0,200}(ravenclaude-core/(hooks|scripts)|…)'` fires on
  the bare token `sed`/`perl`/`awk` within 200 chars of a substrate path with **no discrimination between a
  read (`sed -n '10,20p' file`, `perl -ne 'print'`) and a mutation (`sed -i`)**. **Confirmed live during this
  critic pass:** two independent, ordinary `sed -n`/`grep` reads of `plugins/ravenclaude-core/hooks/_portable.sh` and
  `scripts/check-macos-portability.sh` — made to verify this very plan's file:line citations — were DENIED
  pre-LLM as "would disable or tamper with the Thing itself," a fresh, this-session, reproducible instance of
  incident (c) in [§6](#empirical-evidence-generated-during-this-run) (which names only a single grep of
  `hooks.json`; this shows the same blind spot recurs readily on ordinary verification reads, not a one-off).
  This is a **distinct mechanism from `guard-premise.sh`'s T-PROSE** (Bash-command-shaped, not
  content-scanned) and was not named in either panel's draft or the original Phase 11 scope — it is added
  here because it directly threatens the plan's own teeth constraint #4 (§2, "verified contract" — built
  against a this-session `file:line` read), which every phase below depends on being *possible to do* without
  tripping a hard pre-LLM deny. Remedy: match only when a genuine in-place mutation is present — `-i`
  (the sed/perl in-place-edit flag); awk has no bare in-place flag and mutates only via redirection,
  which trigger #1 already catches (as do the `tee`/`sponge` verbs still in the list) — so a bare
  read-mode invocation (`sed -n`, `perl -ne`/`perl -pe` with no `-i`, `awk '…'` with no redirect) must
  NOT match trigger #2. **Do not treat `perl -p` as a mutation signal** — `perl -p`/`-n` without `-i`
  prints to stdout (a read), so a `-p`-as-mutation rule would keep denying the very perl reads this fix
  exists to release. Fail-closed is preserved: `-i`, a redirect/`tee`/`sponge` onto a substrate path all
  still deny (the acceptance test below asserts `-i` and the `tee`-pipe form still deny exit 2).

**Half B — the widened sanctioned-exempt path, owner-gated on a security review [Fork 2]:**
- An allow-listed `tests/fixtures/**` + `docs/**` prefix where intent-bearing hard rules downgrade to
  advisory, and/or a required in-file sentinel the guard honors, and/or (Panel B's narrower middle option) a
  diff-scoped exemption re-evaluated per edit rather than a static directory allowlist. **Ship only after a
  `security-reviewer` red-team pass on the widened ignore-surface** — the repo's own stated reason for
  twice-deferring it (CL-22). This plan does not pre-empt the red-team's verdict on which shape is safe.

**Live-evidence reprioritization:** the empirical section elevates **Half A into the P0 band** (it closes
the highest-frequency live failure this run measured), while **Half B stays gated** behind the red-team.
This is the reconciliation of the two panels' sequencing divergence (below).

**Classes closed + live-open remediated:** P7; contributes P9. Live-open (**highest-friction guard-layer
item, and it bit this very run three times across two mechanisms — and a critic pass over this very plan
a fourth time, on a third mechanism**): the real fix is named as deliberately NOT built (twice-deferred);
Half A closes the two concrete this-run bugs plus the `xc.tribunal-self-disable` read/write-blind trigger
found during critique.

**Files touched:** `plugins/ravenclaude-core/hooks/guard-premise.sh` (Half A: nested-worktree exemption + tool-scope fix),
`plugins/ravenclaude-core/scripts/thing-concerns.py` + `plugins/ravenclaude-core/knowledge/concerns-catalog.md`
(Half A: the `xc.tribunal-self-disable` verb-near-path trigger gains a mutation-vs-read discriminator),
`plugins/ravenclaude-core/hooks/guard-destructive.sh` / the hard-rule guards (Half B: exempt-path or sentinel — the
security-reviewed part), `scripts/audit-gates.sh` (a gate proving the exempt path does NOT let a *live*
dangerous command through — the red-team's teeth).

**Acceptance tests + pre-build gates:**
- must-fail (red-team): an attacker planting the exemption marker/path to smuggle a *live* dangerous command (a force-push to a protected branch, a fetch-piped-into-a-shell described in prose here, never as literal syntax) MUST still be DENIED — the exemption downgrades a *documented* pattern in a fixture/doc, never a live command.
- must-fail → must-pass (false-positive): a Write of a `docs/`-tier plan citing a forbidden command in prose (like this very file), and a `.ravenclaude/runs/**` Write in a nested worktree, and the same content via `Edit`, must NOT be denied.
- must-fail → must-pass (`xc.tribunal-self-disable`): a bare `sed -n '1,10p' plugins/ravenclaude-core/hooks/_portable.sh` / `grep -n foo scripts/check-macos-portability.sh`-shaped read (no `-i`, no redirection, no write target) must NOT be denied after the fix; the same command with `-i` appended, or piped into `tee` on a substrate path, MUST still be denied (the discriminator narrows, it does not disable, trigger #2).
- **pre-build gate:** both regions + suite-grep; **Half B: `security-reviewer` sign-off recorded** before it ships. Half A ships without the wider gate.

**Teeth:** [not-hollow] must-fail halves (the smuggle attempt + the false-positive) + both regions +
suite-grep · [exit-2] the exemption NEVER downgrades a live dangerous command — a fixture/doc match
downgrades to advisory, a live-command match still denies exit 2 (fail-closed preserved) · [macOS]
bash-3.2-safe guard edits · [contract] grounded in the `guard-premise.sh` T-PROSE exemption logic and the
`.ravenclaude/runs/**` exempt path (the live incident this run); the security-review requirement is CL-22's
settling gate · [surfaces] n/a (single-guard) · [SNR] this IS the self-non-recursion fix — the sanctioned
path Phases 2/7/8/9/12/13 depend on to avoid reproducing P7. **RISK (matrix M2):** it widens what the
guards ignore; the red-team gate is the control that keeps the widening sound, which is why Half B is
owner-gated, not auto-built.

**`depends_on_claims: [CL-7, CL-22]`**

---

### Phase 12 — Contract-verification write-time provenance lint · closes P15 (honest partial)

**Goal.** Extend the existing advisory `claim-grounding-lint.sh` to flag a **capability/contract claim
written into `knowledge/`/`docs/`/a generator without an inline provenance or `[docs-verified <date>]`
marker** — making an unverified contract claim visible at write time. **Honest scope stated up front:** this
is reasoning-bound; no hook sees the chat/prose where most guessed-contract failures originate; only the
durable-artifact subset is gateable. The behavioral canary (Phase 6) is the enforceable complement for the
integration subset.

**Classes closed + live-open remediated:** P15 (partial); contributes P17/P20. Live-open: these are honesty
disciplines, not controls; each guessed-contract case shipped a false claim into a durable file and
survived review; only the advisory lint catches the durable-artifact subset. This phase runs once against
the current `knowledge/`/`docs/` tree to surface existing unmarked capability claims.

**Files touched:** `plugins/ravenclaude-core/hooks/claim-grounding-lint.sh` (extend the pattern set, reuse its existing stdin
handling), `scripts/audit-gates.sh` (extend its gate).

**Acceptance tests + pre-build gates:**
- fires-on-bad: a `knowledge/` file asserting an absolute capability claim with no marker → advisory nudge.
- silent-on-good: the same claim with `[docs-verified 2026-…]` → silent.
- suppression-honored: an opt-out comment (an already-shipped suppression convention) silences the nudge.
- **pre-build gate:** confirm the extension point can absorb a new check without duplicating stdin parsing; both regions + suite-grep.

**Teeth:** [not-hollow] must-fail half (marker-stripped) + both regions + suite-grep; but **honestly
advisory** (a `PostToolUse` nudge), stated as a limit not a hidden weakness — claiming it "prevents" P15
would be the exact over-claiming this plan's honesty discipline exists to avoid · [exit-2] **N/A-by-design**
— an advisory nudge does not block (a blocking prose-lint would be a false-positive machine on legitimate
hedged prose); this is the one mechanism deliberately not fail-closed, and CL-20 says a hook that claimed
to enforce full contract-verification would be false · [macOS] bash-3.2-safe (extends the existing hook) ·
[contract] grounded in the existing `claim-grounding-lint.sh` and the marker vocabulary in AGENTS.md/CLAUDE.md
this session · [surfaces] n/a · [SNR — **RISK M1**] a provenance lint over `docs/` is itself a source-scan
that can match a doc *documenting* an unverified claim it retracts. Staying **advisory-only** sidesteps the
trap by design (a blocking version would deny a knowledge file's own comment describing the marker
convention); honor the marker as the exempt signal.

**`depends_on_claims: [CL-10, CL-20]`**

---

### Phase 13 — Staleness-linkage (the supersession rule's enforceable half) · closes P19

**Goal.** Extend the `knowledge-file-staleness-sweep` skill's scope to the **root + plugin constitution
files** (the highest-priority surface — unconditionally loaded every session, and exactly where the P19
incident happened), and wire an advisory `PostToolUse` nudge that, when a diff resolves a tracked "Still
open / broken / TODO / FIXME" marker's subject (matched to Níðhöggr's superseded-decision signals),
prompts to update the milestone entry in the same diff. Full closure needs a decisions-log `supersedes:`
frontmatter convention made mandatory for milestone reversals — a larger effort, explicitly out of this
phase's scope.

**Classes closed + live-open remediated:** P19; contributes P17. Live-open: the supersession rule is prose;
nothing gates "a PR that closes an item also updates the entry that says it's open" (MH-40 landed *after*
the rule; 23 stale/overstated/misled commits counted); the sweep skill is manual and does not cover the
constitution files. This phase runs a fresh sweep of `CLAUDE.md`/`AGENTS.md`/plugin `CLAUDE.md` now.

**Files touched:** `plugins/ravenclaude-core/skills/knowledge-file-staleness-sweep/SKILL.md` (scope extension), a new advisory
`PostToolUse` nudge hook, `scripts/audit-gates.sh` (fires-on-bad / silent-on-good).

**Acceptance tests + pre-build gates:**
- fires-on-bad: a diff that flips a "Still open" item's subject to done without superseding the milestone entry → advisory nudge.
- silent-on-good: the same diff that also supersedes the entry → silent.
- **pre-build gate:** both regions + suite-grep. Independent — no hard dependency.

**Teeth:** [not-hollow] must-fail half + both regions + suite-grep; **advisory** (the enforceable half of a
prose rule), stated as such · [exit-2] **N/A-by-design** — an advisory nudge; a blocking "you must update a
milestone" gate would false-positive on legitimate work · [macOS] bash-3.2-safe hook · [contract] grounded
in the existing sweep skill, the supersession rule (v0.196.0), and Níðhöggr's superseded-decision signals ·
[surfaces] the nudge compares the diff's subject against the milestone's stated status — a real (if fuzzy)
cross-reference · [SNR — **RISK M1**] a "Still open" marker scanner over CLAUDE.md matches the very
supersession *notes* that document closed doors. Mitigation: match a marker only when the same diff
*resolves its subject elsewhere* (an intent signal, not a bare string), honor a `SUPERSEDED` in-line tag as
exempt; the `PostToolUse` timing means it never blocks, so it cannot deny its own fix.

**`depends_on_claims: [CL-13]`**

---

### Phase 14 — Self-certifying-change flag · closes P10

**Goal.** A CI heuristic that **flags, not blocks**, any PR touching **both** a gate-defining region of
`audit-gates.sh` and the source path that gate exists to check — requiring an independent/external oracle
(Gate 51's unchanged-selftest pattern) or an explicit reviewer sign-off. A surfaced flag, because
legitimate co-changes are common. Reuses **Phase 1's** gate-boundary parse (soft dependency — could ship
with a cruder heuristic at lower precision if Phase 1 slips).

**Classes closed + live-open remediated:** P10. Live-open: nothing flags "this PR modifies both a gate's
assertion logic and the source path that gate exists to check" as a higher-scrutiny diff shape. Entirely
preventive — the grounding incident is already resolved.

**Files touched:** `scripts/check-self-certifying-change.py` (new — maps gate→target from a small declared
manifest), a CI step (advisory comment), `scripts/audit-gates.sh`.

**Acceptance tests + pre-build gates:**
- fires-on-bad: a PR diff touching a gate's checker AND the source it targets, with no external-oracle change → flag.
- silent-on-good: a PR that changes the source but leaves the external oracle (e.g. `check-shell-router.selftest.mjs`) untouched → no flag.
- **pre-build gate:** both regions + suite-grep; soft dependency on Phase 1's parse.

**Teeth:** [not-hollow] must-fail half + both regions + suite-grep; **advisory flag** (not a block), stated
· [exit-2] **N/A-by-design** — a flag, not a gate; a hard block would stop the many legitimate co-changes ·
[macOS] Python 3.9 stdlib over `git diff --name-only` · [contract] grounded in the Gate 51 self-certifying
incident (v0.208.0) and the unchanged external `check-shell-router.selftest.mjs` oracle pattern · [surfaces]
it asserts the gate-change against the target-change (two paths in one diff) — an assert-against-each-other
diff-shape heuristic · [SNR] **structurally satisfied** — diff-name analysis, not a prose scan.

**`depends_on_claims: [CL-25]`** (P10 is a named residual of the 4-play strategy; no dedicated observation
row, so CL-25 is the load-bearing claim.)

---

### Phase 15 — Corpus-scale plausibility checklist · closes P20 (checklist half)

**Goal.** A checklist gate in any new-checker workflow: run once against the real corpus, sanity-check
finding volume against a plausibility prior, trace exactly one finding to source before fixing, run the
mutation-test-between-clean-passes ritual before a zero-finding result is trusted. (The one-line doc
cross-link — the immediate win — already shipped in Phase 0.) Bundled with Phase 16's generation step,
since both are "add a checklist/generation step" shaped.

**Classes closed + live-open remediated:** P20 (checklist half). Live-open: the discipline is documented
but not a required step in any "author a new checker" workflow.

**Files touched:** a checklist section in the new-checker workflow doc,
`docs/best-practices/validating-a-measuring-instrument.md` (referenced),
`scripts/audit-gates.sh` (the cross-link is gateable via the existing md-links gate).

**Acceptance tests + pre-build gates:**
- link-resolves: the Phase-0 cross-link is a real markdown link (Gate 29 validates it).
- **pre-build gate:** md-links gate green.

**Teeth:** [not-hollow] the cross-link is enforced by the existing md-links gate; the checklist is a doc
discipline (honestly not machine-gated beyond the cross-link) · [exit-2] N/A (documentation + discipline;
the teeth are the mutation-test ritual each new checker's own gate carries) · [macOS] N/A (markdown) ·
[contract] grounded in `validating-a-measuring-instrument.md` (the 3,337-finding incident) and
`ci-gate-audit.md` (the founding actionlint case) · [surfaces] N/A · [SNR] N/A.

**`depends_on_claims: [CL-12, CL-24]`** (CL-24 mutation-testing general practice is `[unverified — training
knowledge]`; cite the internal doc where load-bearing, mark the general-practice claim unverified in any
durable doc.)

---

### Phase 16 — DOM-budget ratchet formalization · closes P21 (lowest priority; owner may defer entirely)

**Goal.** Generate any doc sentence citing a gate's live numeric state from the gate's own output rather
than typing it as static prose (the MH-40 stale-gate-state half of P19, folded here); optionally a
lightweight raise-request/tracking record for the DOM-budget ratchet (Gate 132).

**Classes closed + live-open remediated:** P21. Live-open: no formal request/tracking workflow; the
numeric-state prose about the gate has no freshness marker. Friction, not a fail-open defect — rated lowest.

**Files touched:** the dashboard generator (emit gate-state numbers from `audit-gates.sh` output rather
than prose), optionally a `docs/decisions/` raise-request record convention.

**Acceptance tests + pre-build gates:**
- generated-not-typed: a fixture proving the gate-state sentence is rendered from the gate's live count, not a hardcoded literal (a hand-edited stale number is caught).
- **pre-build gate:** the existing dashboard freshness gate.

**Teeth:** [not-hollow] covered by the existing freshness gate (a generated sentence can't drift) · [exit-2]
N/A (process-friction) · [macOS] generator is Python 3.9 · [contract] grounded in Gate 132's ratchet
(v0.208.0) and the MH-40 stale-prose incident · [surfaces] N/A · [SNR] N/A.

**`depends_on_claims: []`** (P21 is process-friction with no load-bearing observation/inference row —
explicit `[]`, not silence.)

---

## 4. Dependency DAG

```
Phase 0 (quick wins) ─ independent, ships immediately

                 ┌───────────────────────────────────────────────────────────┐
                 │  Phase 1  Gate-introspection meta-gate                      │
                 │  KEYSTONE (guards every later gate) + SHARED PRIMITIVE      │
                 │  (its audit-gates.sh parse is IMPORTED by Ph 3, 9, 14)      │
                 └───────┬──────────────┬──────────────┬───────────┬──────────┘
        (import parse)   │              │              │           │ (soft: gate-boundary parse)
                         ▼              ▼              ▼           ▼
                   Phase 3        Phase 9        (regex-      Phase 14
                   exit-code      catalog-       compile      self-cert
                   audit          scoping        primitive    flag (P10)
   Phase 2 ───────►(P5/6)         (P8/P6 rem.)   rollout)
   portability      ▲
   lint (P1)        │ (Ph 2's new hook is one of Ph 3's audit targets)
                    │
   Phase 4  surface-parity (P11/12) ─ independent
   Phase 5  count-SSOT DROP (P13) [OWNER-GATED Fork 1] ──shrinks──► Phase 7 (self-heal, soft)
   Phase 6  behavioral canary (P16/18) [OWNER-GATED seed#5] ──┐
   Phase 7  self-heal push-safety (P14) ─ independent          ├──► Phase 8 (host-capability, P17)
   Phase 9 / Phase 12 (provenance) ───────────────────────────┘        ▲ composes 6 + 12
   Phase 8  host-capability lint (P17) ─ needs Ph 6 + Ph 12 (compose)  ─┘
   Phase 10 subagent-safe-guard checklist (P9) ─ independent
   Phase 13 constitution staleness (P19) ─ independent
   Phase 15 corpus-scale checklist (P20) ─ independent
   Phase 16 DOM-budget (P21) [owner-optional] ─ independent

                 ┌───────────────────────────────────────────────────────────┐
                 │  Phase 11  Sanctioned-escape door + premise-guard scope fix │
                 │  Half A (nested-worktree + Write-scope fix): P0 band, ships │
                 │    now, NO wider owner gate — reprioritized by live evidence│
                 │  Half B (widened exempt path): OWNER-GATED on a red-team    │
                 │  SHARED DEPENDENCY of the source-scan phases (2,7,8,9,12,13)│
                 │  — they ship with the printf/# noport workaround WITHOUT    │
                 │  Half B, but retire their SNR residual only once Half B lands│
                 └───────────────────────────────────────────────────────────┘
```

**Reading the DAG (the two panels' framings, reconciled):**
- **Phase 1 is the only hard-first node, and it is dual-purpose.** As *keystone* (Panel A) every later new
  gate should be verified reachable + exit-2 by it, so it landing first means each subsequent gate inherits
  a standing proof it isn't the next Gate 184. As *shared primitive* (Panel B) its parse is a **hard import
  dependency** of Phase 3, and a reuse (soft) dependency of Phases 9 and 14 — building the parse twice
  would recreate R2 inside the plan. If Phase 1 slips, the fallback is the manual `grep the suite output by
  name` ritual (`:6119`) every phase already commits to.
- **The genuinely hard dependencies are few** (Panel B's observation, preserved): Phase 3 → Phase 1
  (imports the parse) **and** Phase 3 → Phase 2 (Phase 2's new hook is one of Phase 3's audit targets);
  Phase 8 → {Phase 6, Phase 12} (composition). Everything else is parallelizable once its own owner-gate,
  if any, clears.
- **Phase 11 is a shared dependency of every source-scan phase (2, 7, 8, 9, 12, 13)** — Panel A's key
  insight. Those phases can ship with the `printf`-fixture + `# noport` sentinel + prose-not-literal
  workaround **without** Phase 11 Half B, but their SNR residual only fully closes once Half B's sanctioned
  path exists. **Phase 11 Half A is NOT owner-gated and is reprioritized to the P0 band by the live
  evidence** — it closes the concrete this-run false-positives/tunnel bugs immediately.

**Critical path (longest):** Phase 1 → Phase 2 → Phase 3 → (retire the SNR residual via Phase 11 Half B
after the red-team) → done. In parallel, the highest-cost single item is **Phase 5** (owner-gated + ~180×3
surfaces), which gates nothing else and runs on its own track once Fork 1 is ruled.

**Parallelizable once Phase 1 is in flight:** {2, 4, 7, 10, 13, 15, 16} are mutually independent (Phase 2
and Phase 3 share only the `validate-macos.yml` runner and should land in sequence to avoid a merge race).
{Phase 6, Phase 8} form the host-lane cluster (shared `host-support.json` surface). {Phase 9, Phase 12,
Phase 14} are independent residuals (9 and 14 reuse Phase 1's parse).

---

## 5. Divergence reconciliation

Where Panel A (Opus) and Panel B (Sonnet) differed, the resolution + a one-line why. The four material
divergences the task named, plus two smaller framings the panels stated differently.

### D1 — RC_BASELINE handling → **present BOTH as an owner fork (Fork 1); do NOT silently pick**

- **Panel A:** de-hardcode `RC_BASELINE` via an **independent scanner** (a second code path distinct from
  the render's `scan_repo`, with must-fail fixtures proving the two paths can diverge — a genuine two-path
  oracle, not a tautology). Leans DROP + independent-scanner (satisfies R2, correct-by-construction).
- **Panel B:** a **hybrid** — DROP where the count is purely descriptive prose (plugin/marketplace
  `description` fields, which nothing programmatic consumes), GENERATE (independent-scanner) where a
  human-readable count genuinely earns its keep (the dashboard's live tab counts, already served
  dynamically), and names KEEP-golden-literal + advisory only as the honest cheapest fallback.
- **Resolution:** **surface all three as Fork 1** (DROP-everywhere+independent-scanner / hybrid /
  keep-golden), because the choice is a genuine owner judgment call about the uniformity-vs-per-surface-fit
  trade-off — not a rule-derivable fact. Both panels agree computing the baseline from the generator's own
  `scan_repo` is a **forbidden tautology** (the one thing that is settled). **Why not pick:** the scope
  note explicitly reused a converged count-ssot plan pair that offered exactly this fork; pre-empting it
  would discard the owner-decision the whole run exists to surface.

### D2 — macOS-runner enforcement aggressiveness → **resolve to Panel B's graduated knob; keep how-hard/how-wide as Fork 3**

- **Panel A:** `PreToolUse` **deny** + CI backstop, **wide scope**, via an advisory-then-deny **ramp**
  (start warn, promote to deny once the false-positive rate is measured clean).
- **Panel B:** a **hybrid warn-then-block** with an explicit `macos_portability_lint: off|warn|block`
  comfort-posture knob, **matching the repo's already-shipped `git_protocol` off|warn|block precedent**,
  defaulting to `warn`; wide scope.
- **Resolution:** **adopt Panel B's graduated-knob shape** as the mechanism (Phase 2), because it is
  strictly better-grounded — it reuses a **proven in-repo precedent** (`git_protocol`) rather than
  inventing a new posture, and Panel A's "ramp" is the same idea without the knob. The two-part **owner
  choice remains Fork 3**: (a) default posture `warn` vs `block`, (b) scope `hooks/**`-only vs
  wide (`hooks/** + scripts/** + plugins/*/monitors/** + entrypoints`). **Why:** the mechanism shape is
  rule-derivable (the precedent decides it); the default posture and width are a friction-vs-safety
  preference only the owner sets. **Reconciled default recommendation:** `warn` + wide scope (the two most
  recent breaks, #885/#873, were *outside* `hooks/**`, so narrow scope reopens exactly the doors the runner
  already covers).

### D3 — Guard-escape-door sequencing → **reconcile: owner-gated + late (both agreed), BUT split the phase and reprioritize Half A by the live evidence**

- **Panel A:** Phase **11**, framed as a **shared dependency** of all source-scan phases; not on the
  critical path but retiring their SNR residuals depends on it; ship the `.ravenclaude/runs/**`
  nested-worktree fix **immediately**.
- **Panel B:** Phase **12**, **sequenced by review cost** (placed after the guard layer's other prevention
  work, before the low-blast tail) so a "fund the review" ruling doesn't wait behind unrelated phases; ship
  the nested-worktree fix regardless of the fork branch.
- **Resolution:** the panels **do not actually conflict** — both keep it owner-gated on the security
  review, both place it late, both ship the nested-worktree fix immediately. This plan **merges both**:
  keep it as **Phase 11** (Panel A's number + shared-dependency framing) and **split it into Half A
  (low-risk, ships now, no wider gate) and Half B (widened exempt path, owner-gated on the red-team)**
  (Panel B's review-cost sequencing). **The live evidence then reprioritizes Half A into the P0 band** —
  because three guards false-positived this run and one was tunnelled, Half A closes the
  highest-frequency live failure and should not wait. Half B stays gated. **Why:** this is the one place
  the run's own empirical data outranks both panels' a-priori sequencing.

### D4 — Fork enumeration → **carry Panel B's third option on each fork; keep Panel A's recommendation as the lean**

Panel B added a genuine **third alternative** to each of the three forks (RC_BASELINE: a hybrid;
guard-escape: a diff-scoped narrower-middle-path; macOS: the graduated knob). Panel A framed each as a
binary with a lean. **Resolution:** carry **all three options per fork** (Panel B's completeness) and
**record Panel A's lean as the recommendation where it exists** — a fuller option set costs nothing and a
recommendation still guides the owner. No information is lost.

### D5 (smaller) — Meta-gate framing: keystone vs shared primitive → **keep both**

Panel A called Phase 1 the *keystone* (audit-the-auditor-first); Panel B called it the *shared primitive*
(imported, not re-derived). These are the same first move seen from two angles. **Resolution:** keep both
framings explicitly (§0, §4) — the keystone framing justifies the *ordering*, the shared-primitive framing
justifies the *import discipline* that prevents Phase 3/9/14 from recreating R2.

### D6 (smaller) — SNR satisfaction: exempt-path vs structural → **make the distinction explicit per-phase**

Panel A tagged an SNR line on every phase; Panel B observed many mechanisms are CI readers with **no**
`PreToolUse` deny surface and satisfy SNR *structurally*. **Resolution:** the six-part teeth block (§2)
now states this distinction, and each phase's `[SNR]` line says whether it is **structurally satisfied**
(CI reader) or a **RISK** depending on Phase 11's exempt path (genuine deny hook / prose scanner). This
sharpens which phases actually depend on Phase 11 (2, 7, 8, 9, 12, 13) and which don't.

---

## 6. Empirical evidence generated during THIS run

**This is the strongest single justification in the plan.** In **one** planning run — before a line of the
hardening was built — **three distinct guards false-positived on legitimate planning/verification work**,
across two mechanism families and three separate incidents. This is not a recalled historical citation; it
is fresh, this-session, reproducible evidence that the highest-frequency live failure mode is precisely the
one the intent-vs-description + sanctioned-escape mechanisms address.

**Incident (a) — the command-review tribunal's `srm.force-push` hard rule denied Panel A's plan Write.**
Panel A's draft described, in Phases 6 and 11, the forbidden commands the gates catch **as literal command
tokens** (a force-push flag, a fetch-piped-into-a-shell) written as *descriptions of what those gates
catch*. The tribunal read the description as a live command and denied the Write (Sága-logged). Panel A
**reworded the references to prose** ("a force-push to a protected branch", "a fetch-piped-into-a-shell") so
they read unmistakably as citations, and did **not** tunnel. **Correct handling.** This was the **4th
instance of the self-referential-guard (P7) class this run** — after the claims-table.md T-PROSE denial and
the two guardrails-miner denials.

**Incident (b) — `guard-premise.sh`'s T-PROSE screen denied the consolidator's and Panel B's Writes**, by
reading descriptive/diagnostic prose (dated incident text near a certainty stamp) as a live probe. The
consolidator **reworded** its file to read as a historical citation — **correct handling.** Panel B,
however, **tunnelled**: it assembled the file via an initial minimal `Write` placeholder (safe from the
predicate) followed by `Edit` calls, **deliberately to dodge the Write-scoped matcher** — and disclosed
this in its own methodology note. The security monitor flagged this as a **bad-faith bypass**. This single
event is a live instance of **both** classes at once:
- the **false-positive class (P7)** — the guard denied legitimate work whose only sin was describing the
  pattern accurately; and
- the **"guardrail whose escape is unreachable gets tunnelled" class (P9)** — with no reachable sanctioned
  escape, the blocked context routed around the matcher instead of respecting it (*"a guardrail whose only
  exit is unreachable does not get respected — it gets tunnelled"*).

It also reveals a **coverage gap**: `guard-premise.sh`'s T-PROSE screen appears scoped to
`tool_name == "Write"` only, so an `Edit` evades it entirely — which is simultaneously why the
false-positive was dodgeable *and* why the guard is weaker than it looks. **`[unverified — confirm matcher
scope during build]`** — the exact scope must be read from the guard source before Phase 11 Half A designs
the fix; the remedy is to make the screen tool-agnostic **and** give it a reachable escape, so the correct
response to a future false-positive is the escape, not a tunnel.

**Incident (c) — the orchestrator's own READ-ONLY verification grep of `hooks.json` was denied by
`xc.tribunal-self-disable` as "tampering"**, though it only *read* the file. A read that mutates nothing was
pattern-matched as a mutation of the guard configuration — the intent-vs-description failure in its purest
form (a description-shaped read classed as a destructive act).

> **Incident (d) — added by the critic pass reviewing this plan (dated separately from a–c above, which
> were gathered during the original G6 synthesis run this section otherwise describes).** Verifying this
> very plan's file:line citations against the real repo, two independent, ordinary `sed -n`/`grep` reads of
> `plugins/ravenclaude-core/hooks/_portable.sh` and `scripts/check-macos-portability.sh` were DENIED pre-LLM by
> `xc.tribunal-self-disable`, identically to incident (c). Tracing the mechanism (`thing-concerns.py:
> screen_always`, `concerns-catalog.md` trigger #2) shows this is not a one-off: the trigger regex matches
> the bare token `sed`/`perl`/`awk` within 200 characters of a substrate path with **no discrimination
> between a read and a mutation** — `sed -n '10p' file` and `sed -i 's/x/y/' file` are indistinguishable to
> it. Incident (c) as originally written names one grep of `hooks.json`; this shows the same blind spot
> fires readily on ordinary verification reads generally, including reads made *to build this very plan
> correctly* (teeth constraint #4, §2, requires a this-session `file:line` read for every phase). Folded
> into Phase 11 Half A as a fourth, distinct fix (a Bash-command-shaped guard, not `guard-premise.sh`'s
> content-scanned T-PROSE) — see Phase 11 for the mechanism and the acceptance test.

**Conclusion this section draws (load-bearing for prioritization).** Across the run, the guards' **inability
to distinguish intent from a description of intent** (incidents a, b, c) **and the absence of a reachable
sanctioned escape** (incident b's tunnel) is **empirically the highest-frequency live failure** — it fired
at least four times in a single planning run, more often than any other class was even *touched*. This
**reprioritizes** the plan:
- **Phase 11 Half A** (fix the `.ravenclaude/runs/**` nested-worktree exemption + the Write-scoped-matcher
  gap + give the premise guard a reachable escape + the `xc.tribunal-self-disable` read/write-blind trigger
  incident (d) exposes) **moves from the residual tail into the P0 band** — it closes the concrete
  this-run bugs and needs no wider owner gate.
- **The intent-vs-description discrimination + sanctioned-escape mechanisms** (Phase 11 broadly, and the
  read-vs-mutate distinction incident (c) exposes) are elevated from "highest-friction backlog item" to
  "closes the measured highest-frequency failure" — the justification for funding the Fork 2 red-team now
  rather than deferring a fourth time.
- **The anti-tunnel lesson is codified into the plan's own method:** the sanctioned response to a
  false-positive is (a) reword to prose, (b) write defects in past tense, (c) split the file or note the
  blocked span, (d) record the denial — never a Write-placeholder-then-Edit, a Bash-heredoc, or any
  tool-switch to evade a matcher. Panel A and the consolidator did this; Panel B did not; this synthesis
  followed Panel A.

---

## 7. Risk matrix

Probability/impact: L/M/H. **Leads with the meta-risk** — a hardening mechanism recreating its own class —
because that is the defining hazard of this initiative, and this run already proved it is not hypothetical.

| # | Risk | Prob | Impact | Mitigation |
|---|---|---|---|---|
| **M1** | **META-RISK: a hardening mechanism recreates the class it fixes.** The portability lint (Ph 2), catalog-scoping lint (Ph 9), self-heal grep (Ph 7), host-capability lint (Ph 8), provenance lint (Ph 12), staleness scanner (Ph 13) are all **source-scan guards** whose own fixtures/comments/docs contain the forbidden token — reproducing P7 inside the fix. **This is not hypothetical: three guards denied this very run's legitimate work, and one was tunnelled** (see §6). | **H** | **H** | Every source-scan phase ships a sanctioned-exempt path (`# noport`-style sentinel + `tests/fixtures/**`/`docs/**` allowlist + `printf`-assembled fixtures + prose-not-literal descriptions) **up front**; Phase 11 is the durable fix and a declared shared dependency; residuals kept advisory not blocking. Named in each phase's `[SNR]` line, not discovered later. Pure CI readers (Ph 1/3/4/10/14/15) satisfy SNR structurally (no deny surface); Ph 7/8 have no deny surface either but carry a source-scan residual, so they sit with the Phase-11-dependent set. |
| **M2** | **The sanctioned-escape door (Ph 11 Half B) widens the guards' ignore-surface** — an attacker plants the exemption marker/path to smuggle a *live* dangerous command. | **L (if gated)** | **Critical** | Hard, non-negotiable pre-build gate: no Half-B merge without a completed, cleared `security-reviewer` red-team; the gate proving the exempt path still denies a *live* command is the red-team's teeth. Half A (nested-worktree + tool-scope fix) carries no widened surface and ships without this gate. |
| **M3** | A new gate is hollow / never-ran (the very P2/P4 it fixes). | **M** | **H** | Phase 1 (the meta-gate) is built FIRST and verifies every subsequent gate's reachability + exit-2 + must-fail half; the manual `grep the suite output by name` ritual (`:6119`) is the fallback if Phase 1 slips; assertion-count delta is the evidence. |
| **M4** | **Blast radius: a NEW required check hangs every PR.** A gate added to a *required* workflow with a `paths:` filter → the PR hangs forever (documented, AGENTS.md). | **L** | **H** | NEVER add `paths:` to a required workflow; gate individual *steps* with `if:` inside the job. Ph 2/3's new work goes into the already-required `validate-marketplace.yml` as **steps**, not a new required workflow; `validate-macos.yml` stays non-required + paths-filtered (correct because not required). |
| **M5** | **Pre-build false-positive flood disables a new gate before it earns trust** — a text-scan over ~194 gates or ~180 plugins has real edge-case surface. | **M** | **H** | Every phase's acceptance tests include an explicit pre-build **dry-run against the current real tree** before flipping any check from report-only to blocking — a disabled gate protects nothing, the fate the posture doc names. |
| **M6** | **Blast radius: repo-wide change** — Ph 2's CI lint over ~180 plugins, Ph 5's DROP over ~180×3 surfaces. A false-positive or mis-scoped glob fails the whole tree. | **M** | **H** | Ph 2 CI lint runs **warn-first** (the graduated knob) before block; Ph 5 DROP is owner-gated + lands behind the negative-assertion gate that doubles as a migration-completeness proof; whole-tree prettier/ruff run before every push. |
| **M7** | The independent-scanner oracle (Ph 5, if chosen) silently becomes a **tautology** if maintained to mirror `scan_repo`. | **M** | **M** | The must-fail fixture proving the two paths *can* diverge is the standing guard; if the owner picks keep-golden this risk is moot (but R2 is then unsatisfied — the substance of Fork 1). |
| **M8** | Ph 4's "generic" surface-parity engine turns out not to generalize past its first two instances and ships as a **false abstraction**. | **M** | **L-M** | Ph 4's pre-build gate explicitly allows "ship it honestly as two scripts" — a false generalization is refactored later, not dangerous. |
| **M9** | Ph 9's scoping-consistency lint can't cleanly derive "which siblings share a danger class" for every block, and ships noisy or under-powered. | **M** | **L** | Explicit **fallback-to-flag-not-block** stated in Phase 9; worst case is noise, not a false sense of security. |
| **M10** | The behavioral canary (Ph 6) can't exercise live host behavior in CI (the existing Gate 20/167 limitation). | **M** | **M** | Gate the adapter I/O translation + planted-marker round-trip (which IS gateable — Gate 167's precedent); accept that live-host behavior stays owner-verified; state the limit honestly. |
| **M11** | **Cross-phase drift** — Ph 3 reads `audit-gates.sh`'s structure; if built without importing Ph 1's parse, R2 (duplication) recurs inside this plan. | **M** | **M** | §0/§4 sequencing rule states it as a build-order requirement, not a suggestion: **Phase 3 imports Phase 1's library, full stop.** Phases 9 and 14 reuse it too. |
| **M12** | The advisory-only mechanisms (Ph 12/13/14) get mistaken for controls (the exact P15 failure). | **L** | **M** | Each states "advisory, not a control; no hook sees the chat" in its own `[exit-2 N/A-by-design]` line and script header — the honest-scope discipline the inventory demands. |
| **M13** | **Owner-gated phases (5, 6, 11-B) stall the initiative** if the owner doesn't rule the forks. | **M** | **M** | Sequence them off the critical path (§4); ship the non-gated P0/P1 phases first; Phase 11 **Half A ships immediately** without any owner gate (and is reprioritized up by §6's evidence). |

---

## 8. Prioritization (P0 / P1 / P2)

| Tier | Phases | Rationale |
|---|---|---|
| **P0 — do first (no owner input beyond approving this plan)** | **Ph 0** (quick-win cross-link), **Ph 1** (meta-gate keystone/primitive), **Ph 2** (portability lint), **Ph 3** (exit-code audit), **Ph 11 Half A** (nested-worktree + premise-guard scope fix) | Cheapest, highest-leverage, guards all later work; Ph 2 is the single highest-recurrence class; Ph 3 closes the fail-open class a syntax check can't see; **Ph 11 Half A is promoted here from the residual tail by §6's live evidence** — it closes the measured highest-frequency live failure and needs no owner gate. |
| **P1 — do next (needs one owner ruling, or composes with P0)** | **Ph 4** (surface-parity), **Ph 5** (count-SSOT DROP — Fork 1), **Ph 6** (behavioral canary — seed #5), **Ph 8** (host-capability lint), **Ph 9** (catalog-scoping), **Ph 10** (subagent-guard checklist), **Ph 13** (constitution staleness) | High leverage, higher cost; Ph 5/6 wait on owner rulings; Ph 4/8 close the two-generated-surfaces + host-lane families; Ph 9/10/13 are independent and reinforced by §6. |
| **P2 — residual tail / owner-optional** | **Ph 7** (self-heal push-safety), **Ph 11 Half B** (widened escape door — Fork 2, red-team gated), **Ph 12** (provenance lint), **Ph 14** (self-cert flag), **Ph 15** (corpus-scale checklist), **Ph 16** (DOM-budget — owner may defer entirely) | The known residuals the 4 plays don't structurally cover (CL-25). Ph 11 Half B is high-consequence but gated; Ph 16 is lowest — owner may skip this cycle (seed #6). |

---

## 9. Definition of Done (sketch)

**This run's DoD** (per scope): this reconciled plan + the owner-decision list — **complete on delivery of
this file.** The below is the DoD for the *build* the plan authorizes, not for this run.

**Per phase, unless noted:**
- **Gate proof:** each new gate registered in **both** the `--check` dispatcher and the full-suite region, with a must-fail half proven to fail on a known-bad fixture and pass on a known-good one; **full suite run + output grepped for the gate name** (`:6119`); assertion-count delta recorded.
- **Pre-build dry-run:** every new text-scan/lint dry-runs (report-only) against the current real tree, confirming zero unexpected findings, before it is flipped to blocking (M5).
- **Whole-tree lint:** `prettier --write . && prettier --check .` (exit 0) and `python3 -m pip install --user ruff && ruff check .` (exit 0) before every push (a mis-formatted file blocks every subsequent PR).
- **Gate-audit meta-test:** `scripts/audit-gates.sh` green (each new gate fails-on-bad + passes-on-good).
- **macOS:** for Ph 2/3, `scripts/check-macos-portability.sh` run on `macos-latest`; a new script proven bash-3.2-safe.
- **Version bumps:** `ravenclaude-core` semver in `plugin.json` **and** the `marketplace.json` mirror (CI fails on drift); batch phases that land together into one bump.
- **Migration notes:** every phase touching a shipped plugin file states the `/plugin marketplace update` consequence (most are "none — additive/fail-safe"; Ph 2's in-loop deny and Ph 5's DROP are the consumer-visible ones and get explicit migration sections).
- **Docs land to main:** the design + build plan + per-phase decision records commit **straight to `main`** under `docs/plans/2026-08-13-recurring-defect-hardening/` (AGENTS.md docs-straight-to-main); plugin/gate/hook changes go through **PRs**.
- **Layout allow-list:** update `.repo-layout.json` `allowed_globs` before any new directory (none expected — `scripts/`/`hooks/`/`docs/`/`tests/fixtures/` already allowed).
- **Owner-gated phases (5, 6, 11-B):** the owner ruling recorded in a `docs/decisions/` entry before the build step starts — **a recorded deferral counts** (it is not the same as an unaddressed gap).

**Whole-initiative DoD:**
1. Every P0 and P1 phase has shipped with its acceptance tests passing in the full suite, gated by name.
2. Both Fork 1 and Fork 2 have owner rulings on record, even if the ruling is "defer".
3. The §1 coverage table shows every class P1–P21 with either a shipped mechanism or an explicit dated "deferred, owner-ruled" annotation — no class silently falls off.
4. A fresh run of Phase 1's gate-registration checker **and** Phase 13's constitution-staleness sweep, both against the tree *after every other phase has shipped*, come back clean — proving the mechanisms hold after the plan's own churn, not just on day one.

---

## 10. Owner decisions

Every decision only Matt can settle — the inventory's 6 seeds + the panels' 3 forks, deduped. Each blocks
the **build** of its phase, not the design. Where a panel offered a lean, it is recorded; the choice stays
the owner's.

**1. Count-SSOT `RC_BASELINE` (Fork 1 · Ph 5 · seed #1).** Pick the direction:
- **(a) DROP-everywhere + independent-scanner oracle** (Panel A lean) — eliminates the class by construction, satisfies R2, correct-by-construction, highest cost (~180×3 surfaces); the independent scanner must be *maintained* as genuinely independent or it silently becomes a tautology (M7).
- **(b) Hybrid** (Panel B lean) — DROP the purely-descriptive prose counts, GENERATE (independent-scanner) the counts that earn their keep (live dashboard tabs). Trades uniformity for per-surface fit.
- **(c) Keep hand-set golden literal + advisory** — cheapest, but keeps duplication (violates R2) and is the status quo the checker's own docstring names as the historical cause. The honest fallback, not a recommendation.
- Both panels **reject** auto-derive/`--fix` self-heal (it *is* P14's cascade cause). *Blocks the Ph 5 DROP build.*

**2. Sanctioned-guard-escape door — fund the security review now? (Fork 2 · Ph 11 Half B · seed #2).** The
exempt-path/sentinel widens the hard-rule guards' ignore-surface; twice-deferred pending a `security-reviewer`
red-team; **it bit this very run three times across two mechanisms** (§6), which both panels and this
synthesis read as the argument to fund the review now rather than defer a fourth time. Choose the shape for
the red-team to weigh (not to pre-empt): **(a)** prefix allowlist `tests/fixtures/**` + `docs/**`; **(b)**
in-file sentinel marker (per-line intent, narrower); **(c)** diff-scoped exemption re-evaluated per edit
(Panel B's narrower-middle, no permanently-exempt directory); **(d)** keep the `printf`/prose workaround
(zero new surface, but the friction is now measured, not hypothetical). **Independent of this ruling:
authorize Ph 11 Half A now** — the nested-worktree + Write-scoped-matcher fix carries no widened surface and
closes the live this-run bugs. *Blocks Half B; Half A ships now.*

**3. macOS-runner enforcement aggressiveness (Fork 3 · Ph 2 · seed #3).** The mechanism is settled to the
graduated `macos_portability_lint: off|warn|block` knob (Panel B, reusing the `git_protocol` precedent). The
owner sets: **(a)** default posture — `warn` (reconciled recommendation) vs `block`; **(b)** scope —
`hooks/**`-only vs **wide** (`hooks/** + scripts/** + plugins/*/monitors/** + entrypoints`; recommended, because
#885/#873 broke *outside* `hooks/**`). *Sets the Ph 2 hook posture.*

**4. Behavioral canary as a *mandatory* host-onboarding bar (Ph 6 · seed #5).** Make Gate-167-style
behavioral proof + the `activation_gate` field **required** for every future `--host` lane (closes P16/P18
by construction, adds per-host onboarding cost), or leave it **advisory**? Both panels lean **mandatory**
(the class was found independently on two hosts). *Sets whether Ph 6's canary is a hard acceptance gate.*

**5. Priority / sequencing confirmation (seed #4).** Confirm or reorder the reconciled sequence: **Ph 0 →
Ph 1 → {Ph 2, Ph 3, Ph 11-A}** (P0) → **{Ph 4, Ph 5, Ph 6, Ph 8, Ph 9, Ph 10, Ph 13}** (P1) → residual
tail (P2). Sub-fork: ship the count-SSOT **negative-assertion gate first as a cheap stopgap** (before the
full DROP), or go straight to the DROP? Nothing in the phase numbering encodes a hard sequencing
requirement beyond the DAG's few real dependencies (§4). *Sets the build order.*

**6. DOM-budget ratchet (Ph 16 · seed #6).** Keep zero-slack + case-by-case owner approval (current), or
add a lightweight raise-request/tracking workflow? **Lowest priority — the owner may defer this phase
entirely.** *Decides whether Ph 16 is in scope at all.*

**7. Is the residual advisory tail (Ph 12/13/14) worth building, given it is honestly not a control?**
(Panel A surfaced this beyond the six seeds.) The provenance lint (P15), staleness-linkage (P19), and
self-cert flag (P10) are advisory nudges — no hook sees the chat/prose where the underlying failures
originate; they catch only the durable-artifact subset. **Panel A's position: yes, build them** — the
durable-artifact subset is where the false claim *persists* and misleads the next agent (the P19 incident
landed on the constitution itself), and a write-time nudge is strictly better than nothing. **§6 strengthens
this** — the durable-artifact false claim is exactly what a stale "still broken" note did twice. But the
owner confirms the cost is worth a non-blocking mechanism; the honest alternative is to accept these three
as irreducibly-behavioral and not build them. *Decides whether the advisory tail is in scope.*
