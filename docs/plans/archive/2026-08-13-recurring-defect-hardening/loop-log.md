# Loop log — recurring-defect hardening plan, adversarial critique passes

## Pass 1 (sonnet)

Read the full 1,153-line v1 plan, `problem-inventory.md` (21 classes / 6 root causes),
`claims-table.md` (CL-1..CL-25), and cross-checked ~15 load-bearing `file:line` citations against
the real repo in the worktree (`audit-gates.sh` line count/gate count/Supported: list,
`enforce-layout.sh`, `_portable.sh`, `check-macos-portability.sh`, `guard-premise.sh`'s
`tool_name != "Write"` scope, `check-plugin-detail-render.mjs:54`'s `RC_BASELINE`,
`host-support.json`, `claim-grounding-lint.sh`, `regenerate-artifacts.yml`'s PAT-based self-heal PR,
Gate 144/16/179/184/190 header placements in both the `--check` dispatcher and full-suite regions).
Nearly every citation checked out exactly as claimed — the plan's grounding discipline is genuinely
strong. Two real issues found and fixed; scrutinized meta-risk, coverage, and the teeth blocks
specifically per the CLEAN-is-suspect instruction, and did not find grounds to fabricate a third.

**Issue 1 (real, with consequence) — Phase 11's scope missed a live, reproducible P7 instance found
during this very critique.** While reading `_portable.sh` and `check-macos-portability.sh` to verify
this plan's own citations, two independent, ordinary read-only `sed -n`/`grep` Bash commands were
DENIED pre-LLM by `xc.tribunal-self-disable` ("would disable or tamper with the Thing itself") —
structurally identical to the plan's own §6 Incident (c), but a *fresh*, *this-session* recurrence,
not a re-citation of the original G6 run's evidence. Traced the mechanism in
`thing-concerns.py:screen_always` + `concerns-catalog.md`'s `xc.tribunal-self-disable` trigger #2: the
regex matches the bare token `sed`/`perl`/`awk` within 200 chars of a substrate path with **no
discrimination between a read (`sed -n`) and a mutation (`sed -i`)**. This is a distinct mechanism
from `guard-premise.sh`'s T-PROSE (Bash-command-shaped, not content-scanned), and Phase 11's "Files
touched" list (as originally written) named only `guard-premise.sh` and the hard-rule guards — never
`thing-concerns.py`/`concerns-catalog.md`. Consequence: as scoped, Phase 11 Half A would not fix the
mechanism that just denied benign verification work mid-critique, and every future phase's own
build-time verification reads (teeth constraint #4, §2 — "built against a this-session file:line
read") are exposed to the same false-positive. **Fix applied:** added a third Half-A bullet naming the
mechanism, the regex, and a targeted remedy (require a mutation flag/write-target before the verb
counts as a match); added a new must-fail↔must-pass acceptance test; updated Files touched, the
Live-open text, and the P7 coverage-table row; added a clearly-dated "Incident (d)" addendum to §6
(kept separate from incidents a–c so provenance — G6 run vs. this critic pass — isn't conflated).

**Issue 2 (real, with consequence) — Phase 4 and Phase 8 both claimed to build the same host-scope-
sentence↔`host-support.json` parity mechanism, with no stated import/ownership direction.** Phase 4's
Goal listed "host-scope-sentence parity (P17)" as one of "Three variants" the phase implements, tagged
only "(shared with Phase 8)" — but Phase 4's own Files-touched and Acceptance-tests sections had no
file or must-fail test for it (unlike variants 1 and 2, each fully specified). Phase 8's Goal (a)
independently states "extend Gate 154 to scan generator output for literal host-name+capability
strings not traceable to a `host-support.json` lookup" — the same capability, with no reference back to
Phase 4. Left as written, a builder implementing Phase 4 from its own spec could reasonably start
building this variant from scratch, recreating R2 (duplication) *inside the plan itself* — exactly the
failure Phase 1's shared-primitive-import discipline (§0) was written to prevent for the meta-gate
parse, but which was left unstated here. **Fix applied:** clarified in Phase 4's Goal that this bullet
is a forward-reference only (no file/test of its own) and the mechanism is built exactly once, in
Phase 8; added a reciprocal note in Phase 8's Goal (a); retitled the Phase 4 header to state it "names,
does not build" the P17 variant. No new DAG edge was needed — the resolution is that Phase 4 never
independently builds it, not that one phase imports from the other.

**Scrutinized and found sound (no fix needed):** the six-part teeth blocks' self-non-recursion (SNR)
lines (correctly distinguish CI-reader phases, which are structurally SNR-safe, from genuine
`PreToolUse` deny/prose-scan phases, which carry an explicit RISK tag and a stated mitigation); the
Phase 1→3 hard-import dependency and Phase 1→9/14 soft-reuse dependencies in the DAG (consistent with
the phase texts); the "never add `paths:` to a required workflow" discipline applied correctly to
Phase 2/3 (both land as steps inside the already-required `validate-marketplace.yml`, never a new
required workflow, and `validate-macos.yml` is correctly kept non-required); Fork 1/2/3's framing as
genuine owner judgment calls rather than rule-derivable facts; the coverage table's prevent+remediate
pairing for a sample of classes (P2/P3/P4/P6/P9/P13/P15/P19), each of which correctly distinguishes an
already-fixed *specific incident* (per `problem-inventory.md`'s "Fix applied" lines, several of which
I independently confirmed against this repo's own `CLAUDE.md` milestones — e.g., Gate 184's dispatcher
placement, the `srm.force-push`/`sce.curl-pipe-shell` unscoped-`.*` fixes, the v0.245.0 premise-ledger
worktree-scoping fix, the PreCompact retraction) from the still-open *generalized* gap the phase
actually closes; Phase 5's RC_BASELINE tautology framing (independently confirmed the golden-literal
comparison at `check-plugin-detail-render.mjs:54`); the risk matrix's M1 (meta-risk) framing, which
already anticipated exactly the class of failure Issue 1 surfaced, just not this specific trigger.

**Confidence note:** the exact regex alternative that fired on my two denied commands could not be
pinned with full certainty (a later, structurally similar command touching neither `_portable.sh` nor
`check-macos-portability.sh` was also denied, and an apparently-identical `sed -n` read of a *different*
hooks-dir file succeeded earlier in the same session) — command-review outcomes in this environment
were not perfectly reproducible call-to-call. The fix as written targets the trigger #2 regex I
confirmed by direct source read (the most parsimonious explanation covering at least the `_portable.sh`
denial), and is framed as narrowing a confirmed false-positive-prone regex rather than asserting it is
the sole cause of every observed denial — Phase 3's own fail-closed exit-code audit (already in the
plan) is the general-purpose backstop for verifying this class of hook behavior once built.

Verdict: **not clean** — 2 substantive issues found and fixed, both with a demonstrated consequence
(a live false-positive during this very pass; a latent in-plan duplication risk), grounded in
this-session repo reads, not fabricated.

## Pass 2 (opus)

Re-read the full 1,194-line plan (both pages), the inventory (P1–P21), the claims table, and pass 1's
log. Verified pass 1's two fixes against the real repo, then attacked the keystone spec, the teeth
blocks, and the meta-risk axis for NEW defects. Cross-checked ~12 load-bearing citations in the worktree:
`audit-gates.sh` (6454 lines exact; `Supported:` list + `esac` boundary at ~:877/:881; Gate 184 at
:6108-6122; exit-2 template `gate "… blocks with exit 2 (not 1)"` at :1046-1049), `concerns-catalog.md`
trigger #2 regex, `thing-concerns.py`/`guard-premise.sh`/`_portable.sh` presence, the srm/sce hard rules'
YAML-under-`triggers.regex` format (confirms Phase 1's `check-regex-catalog-compiles.py (path,
field-selector)` is feasible against this catalog, and that its Python-`re` compile engine matches the
consumer engine — the right-contract property). **2 real issues found and fixed; the plan was NOT clean.**

**Issue 3 (NEW, real, with consequence) — Phase 1's P3 number-uniqueness sub-check keys on the WRONG
signal and would false-positive on the majority of shipped gates, disabling the keystone on day one.**
The spec (`hardening-plan.md:188`, "no gate number appears twice with a *different* description") and its
must-fail fixture (`:213`, "two `── Gate 104:` headers of different descriptions") treat *same-number +
different-description* as the collision signal. But that is the **legitimate norm** in this harness, not
the bug: measured this session, **87 of 150 distinct gate numbers echo their `── Gate N:` header in BOTH
the `--check` dispatcher AND the full-suite region, each pair with deliberately different text** — a
`(per-gate run)` short form vs the canonical full form (verified on Gates 194/190/167/144/179; e.g. Gate
194 `:871` "…bidirectional teeth (per-gate run)" vs `:6406` "…BIDIRECTIONAL teeth (survive + neutralize)").
The real two-Gate-104 collision was two *independent full-suite* gates sharing a number — a *region*
distinction, not a description one. As specified, the check fires on all 87 dual-region gates → the
constantly-firing guard gets disabled (the exact M5 fate), i.e. **the keystone reproduces the P2/P4 hollow-
/disabled-gate class inside itself** — the plan's own headline meta-risk (M1/M3), un-caught by pass 1.
The must-fail fixture is also miscalibrated: a legitimate dual-region gate has *exactly* the "same number,
different description" shape the fixture calls a collision, so a builder's teeth would "pass" while
mis-modeling the bug. **Fix applied:** re-specified the P3 bullet to key on **region** (a collision =
two same-number headers both in the full-suite region; the dispatcher↔full-suite pair is one gate in two
regions, excluded via the region-split the reachability sub-check already computes), with the measured
87/150 evidence inline; corrected the must-fail fixture to "both headers in the full-suite region" and
added a **companion must-PASS** asserting an unmodified dual-region gate is NOT flagged. (Confirmed the P2
*reachability* sub-check is unaffected — Gate 194's full-suite body keeps a literal `gate "…" must_pass`
call at `:6427` even though the work delegates to a sub-script, so "≥1 `gate` call in the unconditional
region" holds; no edit needed there.)

**Issue 4 (real, adjusts pass 1's Issue-1 fix) — the read/mutation discriminator pass 1 wrote for the
`xc.tribunal-self-disable` fix mischaracterizes `perl -p` as a mutation flag, leaving a residual
false-positive on perl reads.** Pass 1's Phase 11 Half-A remedy (`:645-647`) said "require an in-place-
mutation flag (`-i` for `sed`, `-p`/redirection for the others)…". But `perl -p`/`-n` **without** `-i`
prints to stdout — a read, not a mutation (perl mutates only with `-i`; awk has no bare in-place flag and
mutates only via redirection, already caught by trigger #1). A builder implementing "`-p` = mutation"
would keep denying benign `perl -pe`/`perl -p` reads — preserving, for perl, the exact false-positive the
fix exists to remove (a mini-P8 "fix-one-instance" *inside* the fix: sed handled, perl's flag wrong). The
error is benign-direction (it over-denies, doesn't fail open), so low-severity, but it is a genuine
correctness defect in a security-critical guard spec. **Fix applied:** rewrote the remedy to match only on
`-i` (sed/perl) with awk/redirect/`tee`/`sponge` mutations already covered by trigger #1 and the verb
list; explicitly flagged that `perl -p` is a read; and stated fail-closed is preserved (the plan's own
acceptance test already asserts `-i` and the `tee`-pipe form still deny exit 2, so the narrowing does not
open a hole). Verified against the confirmed trigger #2 regex in `concerns-catalog.md`.

**Scrutinized and found SOUND (no fix needed):** pass 1's Issue-1 fix target — the trigger #2 regex
(`sed|perl|awk` in the verb list, `.{0,200}` before a substrate path, no read/mutate discrimination) is
exactly as pass 1 and the plan describe, and narrowing it does not fail open (redirect→trigger #1;
`-i`/`tee`/`sponge`→still denied; exotic in-process `perl -e 'open'` writes→the catalog's documented
`shell_code_exec` backstop). Pass 1's Issue-2 fix (Phase 4 "names, does not build" P17; built once in
Phase 8) is complete — header retitle (`:335`), forward-reference clarification (`:343`), and reciprocal
Phase 8 Goal-(a) note (`:494`) all landed, and no DAG edge was needed. The P2 reachability spec's
"≥1 `gate` call in the unconditional region" heuristic holds even for sub-script-delegated gates (they
retain the `gate "…" must_pass "$rc"` line), and the plan's M5 pre-build zero-false-positive dry-run is a
genuine safety net for the delegation edge cases. The exit-2 clause (`:1046-1049`), the version-mirror /
required-check-`paths:`-hang / whole-tree-prettier blast-radius handling (M4/M6), the CI-reader-vs-deny-hook
SNR distinction, and the 7 owner decisions' framing (each a genuine judgment call, not rule-derivable) are
all sound. No correlated-error blind spot found beyond Issue 3 (which pass 1 and both panels shared —
reachability treated as region-aware but uniqueness left description-keyed).

Verdict: **not clean** — 2 real issues found and fixed (one NEW keystone defect with a majority-of-gates
false-positive consequence; one adjustment to pass 1's own fix), both grounded in this-session repo reads.

## Pass 3 (sonnet)

Re-read the full ~1,209-line plan (post pass-1+2 edits), the loop log, the inventory, and the claims table.
Verified pass 1's and pass 2's fixes are intact and sound in the current file (Phase 1's region-keyed P3
uniqueness rewrite at `:188-199`/`:223`, the `-i`-only mutation discriminator for `xc.tribunal-self-disable`
at `:659-662`, Phase 4/8's "names, does not build" reconciliation, the nested-worktree + Write-scope fixes)
— no regression, no re-opened issue. Per the assignment, attacked attack-axis 1 hardest: pass 2 found the
keystone P3 (uniqueness) sub-check false-positived on 87/150 gates; this pass checked whether the OTHER two
Phase-1 sub-checks (exit-2-specificity, reachability) share the same shape against the real `audit-gates.sh`
(6454 lines, confirmed unchanged this session). **1 new issue found and fixed, of the same class and a
worse measured rate than pass 2's; 1 smaller but real coverage-gap issue found and fixed; reachability and
regex-compile checked and found sound.**

**Issue 5 (NEW, real, with consequence, worse rate than the P3 bug) — Phase 1's P5 exit-2-specificity
sub-check keyed on gate NAME ("blocks"/"deny") instead of on whether the gate exercises an actual hook
process, and would false-positive on the large majority of the very gates it targets.** The spec
(`hardening-plan.md:200-202` pre-fix) read: "any assertion whose name says 'blocks'/'deny' must be paired
with an explicit `[ "$rc" -eq 2 ]` check… (`:1047-1048` is the positive template)." Measured this session
with a script over the real `audit-gates.sh`: of the **57** gates whose name contains
"blocks"/"deny"/"denies", only **8 (14%)** actually pipe stdin JSON into a `hooks/*.sh` script and assert
its captured exit code — the genuine PreToolUse-hook contract where "exit 2" is the fail-closed signal
(the cited `:1046-1048`, `guard-web-access` at `:4686/4691`). The other **49 (86%)** assert an *internal
decision-engine output* that has no process exit code at all: `thing_decision`'s returned string
(`:1590` `gate "thing: panel deny -> deny" must_pass "$rc"` asserts `[[ "$d" == "deny" ]]`, a Python-emitted
string comparison — confirmed by reading `:1580-1592`), `_predeny`'s boolean (`:2279-2292`, confirmed by
reading `:2270-2295` — string-equality against `"1"`/`"0"`), or an adapter's translated JSON field
(`:2148-2159`, `permissionDecision`, no shell exit code in the chain at all). A name-only "blocks/deny →
must show `-eq 2`" rule, as literally specified, would flag all 49 as violations on day one — **the exact
keystone-flood fate the P3 fix in this same section already corrects for (M5, the meta-gate reproducing
P2/P4 inside itself), at a worse rate: 86% here vs. 58% (87/150) for P3.** This is a category error, not
just a wrong keying signal: "exit code 2" is a PreToolUse-hook-process concept and does not apply to a
Python string comparison or an adapter's JSON field, no matter what the gate is named. Also confirmed: the
plan's own Acceptance-tests list for Phase 1 (pre-fix) had **no must-fail/must-pass fixture at all** for
the P5 clause (only P2, P3, P6 were covered) — so nothing in the plan's own teeth would have caught this
before build, unlike P3 which at least had a (mis-specified) fixture. **Fix applied:** rewrote the P5 Goal
bullet (`:200-217` post-fix) to scope the check to gates carrying the real hook-invocation signature
(`hooks/*.sh` piped stdin, `rc=$?`-shaped capture — the same signature Phase 3's execution audit already
needs when it enumerates hooks, so this reuses rather than re-derives detection), with the measured 57/8/49
evidence inline and file:line citations for one example of each bucket; added the missing must-fail fixture
plus a companion must-PASS asserting the 49 internal-decision-engine gates are NOT flagged, mirroring pass
2's fix pattern for P3.

**Issue 6 (real, smaller, coverage-gap — attack axis 2, feasibility vs. the real repo) — Phase 2's CI
backstop glob list for the portability lint drops the `plugins/*/` prefix on `monitors/**`, so as written it
would silently lint zero files there.** Confirmed this session: there is **no top-level `monitors/` at
repo root** (`ls monitors` → not found); the only shipped monitors directory is
`plugins/ravenclaude-core/monitors/` (containing `watch-run-state.sh`, a real `.sh` file), and
`.repo-layout.json`'s own allow-list already uses the correctly-prefixed `plugins/*/monitors/**` (`:61`).
Phase 2's Files-touched/scope text had `plugins/**/hooks/*.sh` and `plugins/*/bin/rc` correctly prefixed but
left `monitors/**` bare in four places (`:254` scope list, `:263` live-open item (b) which explicitly claims
this phase "extends coverage past `hooks/**` to `monitors/**`", and both Fork-3 owner-decision mentions at
`:973`/`:1182`). As written, the unprefixed glob matches nothing at repo root, so `watch-run-state.sh` would
be silently excluded from the exact lint this phase's own live-open item claims to extend to it — a small
instance of the "allow-list glob that fails open" shape this repo's own `AGENTS.md` names as a recurring
mistake (the `validate-marketplace.yml` required-check history). **Fix applied:** corrected all four
occurrences to `plugins/*/monitors/**`, with an inline note at the first occurrence citing the confirmed
absence of a root-level `monitors/` and the `.repo-layout.json` precedent.

**Scrutinized and found SOUND (no fix needed):** the **reachability** sub-check (P2) — spot-checked
several more gate headers beyond pass 1/2's citations (including the `_skip_or_fail`-gated jq/python3-absent
branches at `:1198-1216`, which still carry a literal `gate` call in source even though it may not execute
at runtime under missing deps — irrelevant to a static parser) and found no header lacking a same-region
`gate` call. The **regex-compile primitive** (P4/P6) — traced "the comfort-posture hard-rule catalog" the
Goal bullet names as a second invocation target and confirmed (via `research-guardrails.md:419` and direct
reads of `concerns-catalog.md:727`/`:797`) it is the SAME `concerns-catalog.md` file `thing-concerns.py`
already parses with Python's `re` (the `srm.force-push`/`sce.curl-pipe-shell` entries live there), not a
second catalog on a different regex engine — so no engine-mismatch risk, just a two-names-one-file framing
that is confusing but not a functional defect, so left as-is. Also checked whether `guard-destructive.sh`'s
own inline regexes (confirmed bash `[[ =~ ]]` POSIX-ERE, a genuinely different engine from Python `re`) are
in scope for the regex-compile primitive — they are not: that primitive is explicitly scoped to a
`(path, field-selector)` **catalog** (a structured YAML list), and `guard-destructive.sh`'s patterns are
inline shell-function literals, not a catalog Phase 1 claims to validate — so this is a non-issue, not a
gap. Pass 1's and pass 2's fixes verified intact and unregressed in the current file. No new correlated-error
blind spot, DAG problem, or owner-decision-framing issue found beyond the two above.

Verdict: **not clean** — 2 real issues found and fixed (one NEW keystone-class defect matching pass 2's
Issue-3 shape at a worse measured rate — 86% vs. 58% — plus its missing acceptance test; one real
glob-prefix coverage gap), both grounded in this-session repo reads, not fabricated. Convergence count
resets to 0 consecutive CLEAN passes.

## Pass 4 (opus)

Applied the earlier passes' "name/proxy-not-behavior" meta-lens to the phases they scrutinized least —
**Phases 5–16** (the plan tops out at Phase 16; there is no Phase 17) — plus a whole-plan consistency
sweep after three edit rounds. Grounded the review against the real worktree files: read
`regenerate-artifacts.yml` (the self-heal push/PR/merge path), confirmed `plugins/*/monitors/`
(`watch-run-state.sh`, no root `monitors/`) and `.repo-layout.json:61`, and re-verified passes 1–3's fixes
are intact in the current file. **1 substantive issue found and fixed; the rest scrutinized and found
sound.**

**Issue 7 (NEW, real, on-thesis) — Phase 7's "no direct-to-`main` push" invariant keys on a proxy string
and its `[not-hollow]` teeth over-claimed coverage, reproducing the R5/R1 fail-open class it exists to
fix — one level up.** The phase's mechanism is a grep of self-heal workflows for a direct-to-`main` push
path. Read against the real `regenerate-artifacts.yml` this session: the *runtime* guarantee that the
workflow cannot mutate `main` is the **branch-protection ruleset** (the workflow's own comments say so —
`:358`, `:367–369` "main is protected: direct `git push origin HEAD:main` is rejected by the ruleset"),
and the workflow lands on `main` **only via an auto-merged PR** (`:416–424`), never a push. A push-string
grep therefore **cannot see** a computed-ref push (`git push origin "$B":main`), a `gh api` commit, or a
`gh pr merge --admin` bypass — any of which is a main-mutating regression that passes the grep **green**
(fail-open). Yet the `[not-hollow]` teeth line asserted the check was "mitigated by a must-fail fixture
reintroducing the dangerous line" — a single-literal fixture that proves it catches *one* shape, not the
class (the P8 "fix-one-instance" trap inside the check itself). This is precisely the "assert the real
behavior, not a proxy string" discipline the plan enforces militantly in Phase 1 (P3 region-keying, P5
hook-signature scoping) but silently relaxed in Phase 7. **Fix applied (3 targeted edits, preserving the
teeth block + coverage table):** (a) added an "Honest bound" paragraph to the Goal naming the ruleset as
the actual guarantee (grounded in `:358`/`:367–369`/`:416–424`), reframing the grep as *defense-in-depth
for the enumerated literal push shapes* and naming the three evasion residuals it cannot see; (b) rewrote
the must-fail bullet to enumerate all shapes (`… main` / `HEAD:main` / `:refs/heads/main` / `--admin`
merge) so a single-literal fixture can't leave the others silently uncaught, plus a companion pass-on-good
asserting the current auto-merged-PR path is NOT flagged; (c) softened the `[not-hollow]` teeth line so the
multi-shape fixture is not read as claiming full-class coverage, with the ruleset named as the guarantee
for what the text-scan cannot see. Net effect: the phase keeps its value (a review-time regression catcher)
without over-claiming — the exact honesty correction passes 1–3 made elsewhere.

**Scrutinized and found SOUND (no fix needed):**
- **Phase 5** negative-assertion regex (`\d+\s+(agents?|skills?|templates?|commands?|hooks?|rules?)`) — a
  handful of prose false-positives are conceivable but the six words are artifact-type-specific, most
  matches ARE drift-prone count claims, and M5's mandatory pre-build dry-run against the real ~180
  descriptions is the standing guard before it flips to blocking. Keys on the forbidden literal being
  DROP-ped, not a proxy for it.
- **Phase 6** behavioral canary + `activation_gate` — asserts a planted marker fired on the host's real
  path (behavior, not a files-exist proxy); fail-closed (an unconfirmable canary ships as unsupported).
- **Phase 8(b)** host-capability-citation lint — the "new host escapes the host-name list" risk is closed
  by composition, not left open: Phase 6 makes adding a host to `host-support.json` (the SSOT the lint
  keys off) a mandatory onboarding step, so a new lane is in the SSOT before its prose can be scanned.
- **Phase 9** scoping-consistency lint — explicit fallback-to-flag-not-block when a block can't be cleanly
  classified (stated in the phase + M9); keys on the structural unscoped-`.*`-beside-scoped-sibling shape.
- **Phase 10** two-worktree fixture — behavior-based (A's record must not block B).
- **Phase 14** self-cert flag maps gate→target from a manual manifest that can go incomplete (a gate with
  no manifest entry escapes the flag) — a real limitation, but it is **advisory (a flag, not a block)** and
  P10 is explicitly low-severity, so the failure mode is "misses a self-cert case," not a false green on a
  control. Acceptable as scoped; not edited.
- **Phases 12/13/16** — advisory-by-design, each states its non-control limit in its `[exit-2 N/A]` line;
  no over-claim.
- **Whole-plan consistency after 3 edit rounds:** the §1 coverage table maps every P1–P21 to an existing
  phase with both prevent + remediate; every `depends_on_claims` resolves to a real CL-1…CL-25 row (none
  moved — passes edited the plan, not the claims table); the DAG's hard edges (3→1, 3→2, 8→{6,12}) match
  the phase texts; the Phase 4↔8 "names-does-not-build P17" reconciliation from pass 1 is intact and
  consistent across the header, both Goals, the coverage table, and the DAG. No dangling reference, no
  renumber drift.
- **Owner decisions (7):** each is a genuine preference / high-blast / cost-value judgment (RC_BASELINE
  A/B/C trade-off, fund-the-red-team, posture+scope friction knob, mandatory-vs-advisory onboarding,
  sequencing confirmation, DOM-budget defer, advisory-tail worth-it) — none became rule-derivable as the
  plan matured; the one settled sub-question (the `scan_repo`-derived baseline is a forbidden tautology)
  is already decided in-plan, not left to the owner.
- **Passes 1–3 fixes (spot-check):** region-keyed P3 uniqueness + companion must-PASS, hook-invocation-
  signature-scoped P5 exit-2 clause + its companion must-PASS, the `-i`-only mutation discriminator (incl.
  the explicit "`perl -p` is a read, do not treat as mutation" note), and the `plugins/*/monitors/**`
  glob-prefix fix — all present and correct in the current file; the monitors fix re-verified against the
  real repo (no root `monitors/`; `plugins/ravenclaude-core/monitors/watch-run-state.sh` exists;
  `.repo-layout.json:61`).

Verdict: **not clean** — 1 real, on-thesis issue found and fixed (a proxy-string check whose teeth
over-claimed, reproducing the fail-open class it fixes), grounded in this-session reads of the real
`regenerate-artifacts.yml`, not fabricated. The find is the same "name/proxy-not-behavior" shape passes
1–3 chased in Phase 1, located this pass in a later phase (Phase 7) exactly as the assignment predicted it
might recur. Convergence count stays at 0 consecutive CLEAN passes.

## Pass 5 (sonnet)

Re-read the full ~1,248-line plan (post pass-1–4 edits), the loop log, `problem-inventory.md`, and
`claims-table.md`. Verified passes 1–4's fixes are intact and unregressed (region-keyed P3 uniqueness +
companion must-PASS at `:188-199`/`:238`; hook-signature-scoped P5 exit-2 clause + companion must-PASS at
`:200-217`/`:239`; the `-i`-only `xc.tribunal-self-disable` discriminator with the explicit "`perl -p` is a
read" note at `:698-701`; the `plugins/*/monitors/**` glob-prefix fix at all four occurrences; Phase 7's
"Honest bound" paragraph, multi-shape must-fail fixture, and softened `[not-hollow]` line, `:497-536` —
confirmed against the real `regenerate-artifacts.yml`'s ruleset comments this session). Did a broad final
sweep for the plan's own dominant defect shape (name/proxy-not-behavior, keying-signal mismatches,
teeth-block over-claims) across every phase not yet scrutinized for it, plus feasibility spot-checks
against the real repo. **1 real issue found and fixed — the same "name/proxy" shape as passes 1–3, this
time as a teeth-block over-claim rather than a false-positive-firing check.**

**Issue 8 (NEW, real, on-thesis) — Phase 1's fourth sub-check (the P4/UNWIRED "hollow gate" clause) was
tagged onto the regex-compile-primitive bullet as "(P4/P6)", claimed as fully closed in the coverage
table, but as specified is a documentation-only convention addition with no automated check and no
must-fail fixture — leaving the phase's own `[not-hollow]` teeth line ("must-fail halves") claiming
coverage the mechanism does not deliver.** Confirmed this session: `docs/best-practices/ci-gate-audit.md`
currently documents exactly **two** fixture categories, `must_fail_on` and `must_pass_on` (`:25-26`); the
plan's pre-fix Goal bullet said only "Add a third fixture category `must_flag_unwired_on` to
`ci-gate-audit.md`, generalizing Gate 179's UNWIRED verdict" — grammatically and substantively an edit to
a **doc**, not a description of logic `check-gate-registration.py` (a static parser over `── Gate N:`
headers) would execute. This is structurally sound as a limitation, not a bug to "fix into existence": Gate
179's actual UNWIRED behavior (`audit-gates.sh:6092-6099`, confirmed by direct read) is a **runtime**
property of `premise-gate.py --self-test` — whether a gate's own detector silently no-ops on a
missing/malformed input — which a static text parse of gate headers cannot see, unlike the genuinely
static P2/P3/P5/P6 sub-checks. But the plan's coverage table (pre-fix) listed "P4 | ... | **Ph 1** (UNWIRED
/ must-flag-unwired taxonomy) | Ph 1 + doc" with no honest-partial caveat — inconsistent with how the same
table already flags P15/P20 as partial elsewhere — and Phase 1's own Acceptance-tests list had must-fail
fixtures for P2, P3, P5, P6 but **none for P4**, so nothing in the phase's own teeth would prove the P4
claim even to the honest-partial standard the plan applies elsewhere. Cross-checked against
`problem-inventory.md`'s leverage table (`:238`), which names the intended mechanism **"the doc + the
gate-introspection layer"** (both halves) — confirming the hardening plan as drafted delivers only the doc
half and silently drops the second, rather than stating the drop. This is the same recurring shape passes
1–4 found (P3/P5 keyed on the wrong signal and false-positived; Phase 7's grep over-claimed behavioral
coverage it couldn't deliver) — here manifesting as a **teeth-block over-claim on an under-specified
mechanism** rather than a firing false-positive. **Fix applied (5 targeted edits, preserving the teeth
block + coverage table structure):** (a) split the merged "(P4/P6)" Goal bullet into two — the regex-compile
primitive stays scoped to P6 alone; a new "UNWIRED taxonomy (P4) — honest partial" bullet states plainly
that this is a doc-convention addition, not a `check-gate-registration.py` check, names the confirmed
`:25-26` two-category baseline, and cites the problem-inventory's "doc + gate-introspection layer" framing
so the dropped half is named rather than silently absent; (b) updated "Classes closed + live-open
remediated" to flag P4 as honest-partial and state explicitly that retrofitting the ~194 shipped gates is
NOT performed by this phase; (c) clarified Files-touched's `ci-gate-audit.md` entry to name the actual
edit (the new fixture category, not only the Phase-0 cross-link); (d) added an explicit "P4 has no
must-fail fixture, by design" line to Acceptance-tests so the absence reads as a stated scope decision, not
an oversight; (e) narrowed the Teeth block's `[not-hollow]` line to scope "must-fail halves" to
P2/P3/P5/P6 and name the P4 exception inline. (A slip during edit (e) briefly truncated the adjacent
`[exit-2]` clause — caught and repaired in the same pass before finalizing, confirmed by re-reading the
patched section.) Coverage-table framing now matches the plan's own established honest-partial precedent
(P15/P20) instead of being the one silent overclaim.

**Scrutinized and found SOUND (no fix needed):**
- **Phase 4's Gate-144 citation** ("derive-and-compare … already running the same render check over both
  `dashboard.html` and `index.html`") — read `audit-gates.sh:5377-5399` directly: Gate 144 does run
  `check-prompt-builder-render.mjs` against both `$DASH_HTML` and `$IDX_HTML` independently (an
  XSS-sink-absence static grep, not literally a derive-from-A-assert-B-agrees comparison). The citation is
  a loose paraphrase of a narrower mechanism, but it does not misdirect a builder — Phase 4's own variant 1
  (route/placement parity, genuine SSOT-derive-then-assert) and Gate 32 (genuine twin-process dispatch) are
  the real precedents for what Phase 4 builds, and neither depends on Gate 144 being more than it is. Left
  as-is: imprecise characterization, not a defect with a builder-facing consequence.
- **Phase 4's twin-server claim (P12)** — confirmed both `./scripts/serve-dashboards.py` and
  `./plugins/ravenclaude-core/scripts/serve-dashboards.py` exist as claimed; Gate 32 (`:3449`) already
  checks endpoint-name parity between them (confirmed by direct read, `:4224` comment), leaving exactly the
  `main()`-behavioral-drift gap Phase 4 says it closes.
- **Phase 2 Fork 3's `git_protocol: off|warn|block` precedent** — confirmed real and shipped
  (`plugins/ravenclaude-core/CLAUDE.md:2423`, `2447`; `hooks/enforce-git-protocol.sh`,
  `hooks/tests/test-enforce-git-protocol.sh`, wired in `hooks.json` and `.claude/settings.json`) — Phase
  2's `macos_portability_lint` knob is a sound reuse of a real pattern, not an invented one.
  Other Phase 1 sub-checks (P2 reachability, P3 uniqueness, P5 exit-2, P6 regex-compile) re-read against
  the current file and confirmed each still carries its own must-fail + companion must-PASS fixture and an
  accurate file:line citation; no regression from passes 1-4's edits.
- **Pass 4's Phase 7 fix** — re-read in full: the "Honest bound" paragraph, the four-shape must-fail
  enumeration (`… main` / `HEAD:main` / `:refs/heads/main` / `--admin` merge), the pass-on-good naming the
  real auto-merged-PR path, and the softened `[not-hollow]` teeth line are all present, mutually
  consistent, and correctly grounded in the cited `regenerate-artifacts.yml` line numbers. Sound and
  complete; no further edit needed.
- **DAG, coverage table, owner-decisions (7), and dependency edges** — re-swept for dangling references or
  renumbering drift after this pass's edits; none introduced. The Phase 4↔8 "names-does-not-build P17"
  reconciliation (pass 1) remains intact and consistent across header, both Goals, coverage table, and DAG.

Verdict: **not clean** — 1 real issue found and fixed (a teeth-block over-claim on an under-specified
sub-check, the same name/proxy-not-behavior class as passes 1–4, this time manifesting as claimed-vs-actual
coverage rather than a firing false-positive), grounded in this-session repo reads
(`ci-gate-audit.md:25-26`, `audit-gates.sh:6092-6099`, `problem-inventory.md:238`), not fabricated.
Convergence count stays at 0 consecutive CLEAN passes.

## Pass 6 (opus)

Ran the definitive teeth-block-honesty audit the assignment scoped: walked **every** phase's six-part
teeth block **phase-by-phase, all 17 (Ph 0–16)** — for each of the six parts (not-hollow, exit-2,
macOS, contract, surfaces, SNR) asked whether the claim EXACTLY matches what the mechanism delivers or
over-claims (asserts hard/full coverage where the mechanism is partial/advisory/doc-only). Cross-read the
current plan (post pass-1–5 edits) against `problem-inventory.md` (P17 teeth spec at `:188-194`, `:193`;
the R1/R6 root-cause framing). **1 real over-claim found and fixed; the plan was NOT clean.** This is the
same last-surviving defect class passes 4–5 named (teeth claim more than the mechanism delivers), located
this pass in a phase neither pass had scrutinized for it (Ph 8's `[exit-2]` line — pass 4 checked only
Ph 8(b)'s *composition* risk, pass 5's found-sound list never touched Ph 8's teeth).

**Issue 9 (NEW, real, on-thesis) — Phase 8's `[exit-2]` teeth line over-claims uniform hard-gating and
contradicts its own `[SNR]` line.** Pre-fix, `[exit-2]` read: "exit 2 on *any* uncited/untraceable host
claim … this targets *generated, machine-produced* text with a deterministic source, so it can be gated
hard (the distinction from Phase 12's advisory nudge over free-form prose is deliberate)." But Phase 8's
own `[SNR]` line (unchanged, `:600-604`) concedes sub-check (b) (`check-host-capability-citations.py`) "is
a prose scan of `knowledge/`/`docs/`" and "residual accepted as **advisory** for the `docs/` subset." So
the same teeth block simultaneously (i) claims hard exit-2 on "any" uncited host claim and (ii) concedes
the `docs/` subset is advisory — a direct contradiction. Worse, the stated JUSTIFICATION ("machine-produced
text") is false for sub-check (b): it scans **hand-written** `knowledge/`/`docs/` markdown, not machine
output — so the clean contrast drawn against "Phase 12's advisory nudge over free-form prose" does not
hold, because (b)'s `docs/` portion *is* an advisory nudge over free-form prose. Consequence (this is not
cosmetic): a builder following `[exit-2]` literally would build a **hard-blocking `docs/`-prose scanner**,
which false-positives on legitimate retraction / supersession notes — reproducing the exact P7/M1
self-reference class the plan exists to close, one level up (the same "teeth over-claim → mechanism
recreates its own class" shape pass 4 found in Ph 7). The honest structure: (a) generator-output parity +
(c) adapter round-trip are machine-produced/execution-based → hard exit-2; (b) hard-fails only where a
deterministic `host-support.json` oracle backs the claim (generator output + `knowledge/`), and is
advisory over free-form `docs/` prose — the hard gate justified by the *oracle*, never by the text being
"machine-produced." **Fix applied (2 targeted edits, teeth-block + acceptance-test structure preserved):**
(a) rewrote the `[exit-2]` line to split oracle-backed-hard (a/c + b's cross-referable claims) from
advisory (b's `docs/` prose), naming the `[SNR]` concession inline and correcting the justification to
"deterministic oracle, not machine-produced"; (b) aligned the acceptance-test bullet (`:589`) so the
"uncited claim → exit 2" fixture is scoped to generator/`knowledge/` (oracle-backed) surfaces and names the
`docs/`-prose case as advisory. Did **not** flag P17 in the §1 coverage table as honest-partial: P17's
PRIMARY mechanisms (generator parity + adapter round-trip) are genuinely hard-gated machine surfaces —
only the `docs/`-prose sub-portion of the citation lint is advisory — so P17 is not primarily-advisory the
way P4/P15 are, and adding an honest-partial flag there would itself be an inaccurate over-correction.

**Teeth blocks audited phase-by-phase (all 17) and the verdict on each:**
- **Ph 0** (P20 doc) — honest; every part correctly n/a except `[not-hollow]` (md-links gate). No over-claim.
- **Ph 1** (P2/P3/P4/P6+P5) — honest post-pass-5: `[not-hollow]` scoped to P2/P3/P5/P6 with the P4/UNWIRED doc-convention exception named; coverage table flags P4 honest-partial. Verified intact (`:98`, `:264`, `:268-272`; `[exit-2]` clause complete at `:271-272`, the pass-5 truncation repair holding).
- **Ph 2** (P1) — `[surfaces]` ("CI linter and macos-latest runner assert the same banned-token set … a divergence between them is itself a failure") is the pre-build confirmation, not a shipped standing divergence-gate; **considered and judged defensible** — for a single-surface deny hook constraint #5 is only weakly applicable, the claim satisfies its "never a constant oracle" spirit, and any over-reach pushes a builder toward a *more* robust (shared-source) design, not a harmful one (opposite consequence-sign to Ph 8). Not fixed — fixing it would be marginal/fabricated.
- **Ph 3** (P5/P6) — honest; `[SNR]` correctly splits the execution-runner (structural) from the static verdict-default lint (small residual + mitigation named).
- **Ph 4** (P11/P12) — honest; "names, does not build" P17 (pass-1 fix) intact; teeth cover only the P11/P12 mechanisms it actually builds.
- **Ph 5** (P13) — honest; `[surfaces]` explicitly conditions the cross-check on the independent-scanner Fork-1 option and says keep-golden forgoes it.
- **Ph 6** (P16/P18) — honest; `[exit-2]` framed as fail-closed-by-shipping-as-unsupported; M10 states the live-host-in-CI limit. (Pass 4 already blessed.)
- **Ph 7** (P14) — pass-4 honest-partial fix intact: Honest-bound paragraph (`:522-534`), 4-shape must-fail fixture (`:545`), softened `[not-hollow]` naming the ruleset as the real guarantee (`:550-555`).
- **Ph 8** (P17) — **the over-claim above; fixed.**
- **Ph 9** (P8) — honest; `[exit-2]` distinguishes confident-inconsistency (block) from unclassifiable-block (advisory flag), matching M9.
- **Ph 10** (P9) — honest; real gate (generalized Gate 190) + checklist; teeth describe the fixture-harness must-fail, not auto-coverage of every guard.
- **Ph 11** (P7) — honest; Half A / Half B split, M2 red-team gate on Half B stated.
- **Ph 12** (P15) — honest; explicitly advisory, `[exit-2] N/A-by-design`, coverage table flags P15 honest-partial.
- **Ph 13** (P19) — honest; explicitly advisory.
- **Ph 14** (P10) — honest; explicitly advisory flag, not a block.
- **Ph 15** (P20 checklist) — honest; `[not-hollow]` states plainly "the checklist is a doc discipline, honestly not machine-gated beyond the cross-link."
- **Ph 16** (P21) — honest; `[not-hollow]` = existing freshness gate over the generated sentence.

**Coverage-table honest-partial labels verified:** P4 (Ph 1) and P15 (Ph 12) are the two classes whose
PRIMARY mechanism is doc/advisory, and both are flagged honest-partial in §1 — correct. Every other row's
prevention phase delivers an automated check + must-fail fixture (spot-confirmed against each phase's
Acceptance-tests list); no remaining row mislabels an advisory/doc mechanism as a hard closure. **Final
consistency:** `depends_on_claims` all still resolve to CL-1…CL-25 (no claims-table edits any pass);
§1 maps all 21 classes; §4 DAG hard edges (3→1, 3→2, 8→{6,12}) match the phase texts; §10 owner decisions
(7) and §9 DoD unchanged and complete; the Ph 4↔8 "names-does-not-build P17" reconciliation still
consistent across header/both Goals/coverage table/DAG after this pass's Ph 8 edits.

Verdict: **not clean** — 1 real, on-thesis over-claim found and fixed (Ph 8's `[exit-2]` teeth line
claimed uniform hard exit-2 gating while its own `[SNR]` line concedes the `docs/` subset is advisory, and
justified the hard gate by a false "machine-produced" property), grounded in this-session reads of the
plan and `problem-inventory.md:188-194`, not fabricated. It is the same last-surviving class passes 4–5
named, in a phase neither had scrutinized for it. Convergence count stays at 0 consecutive CLEAN passes.

## Pass 7 (sonnet)

Read the full ~1,280-line plan (post pass-1–6 edits), the loop log (all 6 prior passes), the inventory, and
the claims table. **Verified pass 6's Phase 8 fix first** (the assignment's explicit ask), then independently
re-derived 6 teeth blocks/citations against the real repo not freshly re-checked by name in prior passes, and
swept for the dominant recurring class (proxy-keyed checks, teeth/Goal over-claims) one more time across the
whole document. **1 real issue found and fixed — pass 6's own fix was incomplete, not wrong.**

**Issue 10 (real, adjusts pass 6's own fix — same defect class, one level up) — Phase 8's Goal (b) bullet
still unconditionally claimed the new checker "fails the build" on any uncited host-capability claim,
directly contradicting the narrower scope pass 6 had already given the `[exit-2]`/`[SNR]` teeth lines and
the acceptance-test bullet in the very same phase.** Verified this session by re-reading Phase 8 in full
(`hardening-plan.md:568-612` pre-fix): pass 6's edit (Issue 9) correctly rewrote the `[exit-2]` teeth line
and the must-fail acceptance-test bullet (`:589` pre-fix) to split oracle-backed-hard (generator output +
`host-support.json`-cross-referable `knowledge/` claims) from advisory-only (free-form `docs/` prose) — but
it explicitly scoped itself to "2 targeted edits, teeth-block + acceptance-test structure" and never touched
the **Goal** bullet itself, which still read: "a `check-frontmatter.py`-sibling
(`check-host-capability-citations.py`) that **fails the build** on a host name adjacent to a
supported/unsupported/native verb without a dated basis or `host-support.json` cross-ref" — no `docs/`
carve-out at all. The "Classes closed + live-open remediated" line repeated the same unscoped claim ("no
gate fails a build on an uncited host-capability claim"). Consequence: the Goal is the primary spec a
builder reads first to know what the mechanism *does* — a builder following the Goal literally would still
build the hard-blocking `docs/`-prose scanner that pass 6's own fix exists to rule out (the exact P7/M1
false-positive-on-legitimate-prose class, reproduced by the un-synced half of pass 6's own edit). This is
the same "teeth claims more than the mechanism delivers" shape passes 4–6 chased, located here in the one
place none of them checked: whether a phase's **Goal** text (as opposed to its Teeth/acceptance-tests) had
been reconciled after a mid-stream narrowing. **Fix applied (2 targeted edits):** (a) rewrote Goal (b) to
state the checker scans generator output + `knowledge/`/`docs/` prose but hard-fails (exit 2) only where a
`host-support.json` cross-ref exists to gate against (generator output + resolvable `knowledge/` claims),
with a free-form `docs/` claim as an advisory nudge, not a build failure — matching the teeth/acceptance-test
scope verbatim, with an inline note naming what was inconsistent and why; (b) tightened the "Classes closed"
Live-open sentence the same way. No DAG, coverage-table, or dependency-claims edit needed — P17's row already
described the phase generically enough ("host-capability lint + adapter round-trip") not to inherit the
over-claim.

**Independently re-derived against the real repo (not previously spot-checked by file:line in this exact
form) — all confirmed sound, no fix needed:**
- `docs/best-practices/ci-gate-audit.md:20-26` still documents exactly the two fixture categories
  (`must_fail_on`, `must_pass_on`) Phase 1's P4 bullet cites as the pre-fix baseline — confirmed unchanged,
  consistent with the plan being unbuilt.
- `scripts/audit-gates.sh` Gate 179's UNWIRED-verdict comment block (the "G3b READS `depends_on_claims`...
  hence the UNWIRED verdict" text) — read directly, matches Phase 1's P4 description and problem-inventory's
  citation almost verbatim.
- `plugins/ravenclaude-core/skills/knowledge-file-staleness-sweep/SKILL.md` exists (Phase 13's reuse target).
- `plugins/ravenclaude-core/knowledge/host-support.json` exists but carries **no** `activation_gate` field
  yet — correct, since Phase 6 (which would add it) is unbuilt; confirms Phase 8's pre-build dependency on
  Phase 6 is a real, not-yet-satisfied dependency, not a stale claim.
- `.github/workflows/regenerate-artifacts.yml` — re-confirmed the "main is protected: direct push is
  rejected by the ruleset" comment and the PAT-based auto-merge-on-green-checks path Phase 7's "Honest bound"
  paragraph (pass 4's fix) rests on; still accurate, though the file has grown since (a `sleep 25` race /
  `gh pr checks --watch` fix landed 2026-08-13, unrelated to the cited invariant).
- `scripts/audit-gates.sh:5377-5399` (Gate 144) and `:3449` (Gate 32 header) — both re-confirmed present and
  matching Phase 4's citations.
- `plugins/ravenclaude-core/hooks/claim-grounding-lint.sh` and `scripts/check-marketplace-claims.py` — both
  exist, matching Phase 12 and Phase 5's Files-touched claims.
- `scripts/audit-gates.sh:6259` (Gate 190 full-suite region) — confirmed the two-worktree fixture comments
  ("recorded in worktree A denied an unrelated new module in worktree B", "Teeth 1 — collapse the scope key
  in BOTH hooks and the cross-worktree half must go...") are real, backing Phase 10's citation of Gate 190
  as the template to generalize.

**Investigated and found NOT a defect (avoided fabricating an issue, per the assignment's warning) —**
`scripts/check-marketplace-claims.py` now contains `actual_core_hook_count()` and `actual_core_rule_count()`
functions in addition to the skill/agent counters CL-5 and Phase 5 cite — at first read this looked like it
might mean the "2 of 6 counted quantities" figure (Phase 5's Live-open text, CL-5) had gone stale as the
script evolved past the point of the original citation. Read the functions' actual scope before concluding
anything: `actual_core_hook_count`/`actual_core_rule_count` cross-check only the **`ravenclaude-core`
plugin's own internal "What's inside" README table** (`_CORE_TABLE_RES`, matching `| Hooks | N |` rows in
one specific file), not a general "N hooks"/"N rule-sets" claim scanned across all ~180 plugin
descriptions the way `SKILLS_RE`/`AGENTS_RE` are. So the general, cross-marketplace coverage the "2 of 6"
figure describes (matching Phase 5's own negative-assertion-gate regex scope —
`agents?|skills?|templates?|commands?|hooks?|rules?`, six word-categories) is still accurately 2-of-6
(skills, agents) generally covered; hooks/rule-sets are checked only for one plugin, and
templates/commands are wholly uncovered anywhere — consistent with problem-inventory's "4 of 6 count types
still ungated." No edit made; the deeper read resolved the apparent discrepancy rather than confirming a
defect.

**Scrutinized and reconfirmed sound (no fix needed) — whole-document consistency after pass 7's edit:**
the §1 coverage table's P17 row remains accurate (states the phase generically, inherits no over-claim);
the §4 DAG's Phase 8 node and its dependency on {Phase 6, Phase 12} unchanged and correct; the Phase 4↔8
"names, does not build" P17 reconciliation (pass 1) remains intact and untouched by this pass's edit; owner
decisions (7) and the DoD (§9) re-read in full, no dangling reference or renumbering drift found; passes
1–6's fixes (region-keyed P3 uniqueness, hook-signature-scoped P5, the `-i`-only `xc.tribunal-self-disable`
discriminator, the `plugins/*/monitors/**` glob-prefix, Phase 7's Honest-bound paragraph, Phase 1's P4
honest-partial framing) all re-read intact in the current file.

Verdict: **not clean** — 1 real issue found and fixed (pass 6's own fix left the Goal bullet unreconciled
with its corrected Teeth/acceptance-test scope, reproducing the exact over-claim pass 6 had just fixed one
paragraph over), grounded in this-session reads of the plan (`hardening-plan.md:568-612`) and the real repo
(`ci-gate-audit.md`, `audit-gates.sh` Gates 144/179/190/32, `host-support.json`,
`regenerate-artifacts.yml`, `check-marketplace-claims.py`), not fabricated. One investigation
(`check-marketplace-claims.py`'s hook/rule-set counters) was pursued to a deeper read and found NOT a
defect — recorded rather than either fabricated or silently dropped. Convergence count stays at 0
consecutive CLEAN passes (this is not a clean pass).

## Pass 8 (opus) — CLEAN: end-to-end re-read of Phases 1/7/8, fresh dominant-class sweep, coverage/DoD/DAG/owner-decisions/claims-resolution confirmed, feasibility re-verified against the real repo — no survivor

Read the full 1,290-line plan (post pass-1–7 edits), the loop log (all 7 prior passes), the inventory,
and the claims table. This pass = mutual-consistency of the accumulated edits + a fresh sweep, per the
assignment. **First priority: verify pass 7's fix (the most recent, and the one that adjusted pass 6's
own fix) left no loose end** — the exact failure mode the last several passes chased (pass 7 found pass 6
left the Phase 8 Goal unscoped). It did not. **No new issue found; this is a genuine first CLEAN.**

**1. Phase 8 END-TO-END (the assignment's explicit ask) — all five surfaces agree on the
oracle-backed-hard vs advisory-prose split.** Re-read Goal (a/b/c) + "Classes closed" + coverage-table
P17 row + `[exit-2]`/`[SNR]` teeth + acceptance tests as one unit:
- Goal (a) generator-output→Gate-154 extension and (c) adapter round-trip are machine-produced/execution
  surfaces → hard exit-2; Goal (b) hard-fails (exit 2) **only where a `host-support.json` cross-ref
  exists** (generator output + resolvable `knowledge/` claims), advisory over free-form `docs/` prose.
- "Classes closed" Live-open (`:588-592`): "no gate fails a build on an uncited host-capability claim
  traceable to `host-support.json` (a free-form `docs/`-only claim stays advisory)" — matches Goal.
- Acceptance test 2 (`:599`): "in generator output or a `knowledge/` file where a cross-ref exists →
  exit 2. (A free-form `docs/`-prose claim is advisory)" — matches.
- `[exit-2]` teeth: splits oracle-backed-hard (a/c + b's cross-referable) from advisory (b's `docs/`),
  justified by the deterministic `host-support.json` oracle, NOT by "machine-produced"; `[SNR — partial
  RISK]` concedes the `docs/`-subset advisory residual. Consistent.
- **Pass 6's `[exit-2]` teeth fix + pass 7's Goal-(b) fix are fully reconciled; the coverage-table P17
  row (`:111`) and the DAG describe Phase 8 generically ("host-capability lint + adapter round-trip";
  "uncited host claims") and inherit no over-claim — pass 7's "no coverage-table/DAG edit needed" holds.**
  No residue.

**2. Phase 1 END-TO-END — five sub-checks internally consistent.** P2 reachability / P3 region-keyed
uniqueness (87/150 dual-region evidence) / P5 hook-signature-scoped exit-2 (57/8/49 evidence) / P6
regex-compile / P4 UNWIRED honest-partial — all agree across Goal, acceptance tests (must-fail for
P2/P3/P5/P6 with companion must-PASSes; **P4 has no must-fail fixture by design, stated explicitly**),
teeth (`[not-hollow]` scoped to P2/P3/P5/P6 with the P4/UNWIRED doc-convention exception named), and the
coverage-table P4-honest-partial flag. No sub-check keys on a proxy.

**3. Phase 7 END-TO-END — proxy-honesty intact.** Goal + "Honest bound" paragraph (ruleset is the real
guarantee, the grep is defense-in-depth for the enumerated push shapes) + 4-shape must-fail
(`… main` / `HEAD:main` / `:refs/heads/main` / `--admin` merge) + pass-on-good (the auto-merged-PR path
NOT flagged) + softened `[not-hollow]` teeth (catches the enumerated shapes, NOT the full class) all
agree. Pass 4's fix holds.

**4. Structural sweep — all intact.** §1 coverage table maps every P1–P21 with BOTH a prevention phase
and a remediation of its live-open instance (verified row-by-row); honest-partial flags on P4 (Ph 1) and
P15 (Ph 12) are the only two, correct and ratified by passes 4+6. §10 owner decisions = 7 (Forks 1/2/3 +
seeds #5/#4/#6 + the advisory-tail question). §9 DoD present (per-phase + whole-initiative). §4 DAG hard
edges (3→1, 3→2, 8→{6,12}) and Phase 11 as shared dependency of {2,7,8,9,12,13} match the phase texts.
All 16 phase `depends_on_claims` lists resolve to real CL-1…CL-25 rows (Ph 16's explicit `[]` included);
no claims-table edits any pass.

**5. Feasibility re-verified against the real worktree repo (this session):** `audit-gates.sh` = 6454
lines (matches Phase 1's citation); `validate-macos.yml` / `validate-marketplace.yml` /
`regenerate-artifacts.yml` all present (Phase 2/3/7 targets); `host-support.json` present with **no
`activation_gate` field** (confirms Phase 6/8's dependency is a real, not-yet-satisfied one — the plan is
correctly unbuilt); Gates 154/167/144/32/190 each present in BOTH the `--check` dispatcher (`(per-gate
run)`) and full-suite regions with deliberately different wording (e.g. Gate 144 `:615` vs `:5377`) —
directly confirming the dual-region shape Phase 1's P3 region-keying rests on and the 87/150 evidence;
exit-2 template `gate "guard-destructive blocks with exit 2 (not 1)" must_pass` at `:1046`; the `--check`
boundary + `Supported:` list at `:877-881` (the two surfaces Phase 1's reachability sub-check compares;
Gate 184 now in the list, confirming the P2 remediation already landed); Gate 179 UNWIRED verdict at
`:6097` (Phase 1's P4 citation).

**Two borderline candidates considered and found NOT survivors (recorded rather than fabricated or
silently dropped):**
- **§0 line-57's "Phase 4 — Surface-parity gate (P11/P12 + P17 host-scope variant)".** Read against
  pass 1's "Phase 4 names, does not build P17" reconciliation, this looked like a possible un-propagated
  residual. Judged defensible: "host-scope variant" is itself a scoping qualifier (parallel to line 54's
  "P5's exit-2 clause"), it is consistent with the coverage table's own "Ph 4/5/6" P17-**contributor**
  attribution, and every authoritative surface (Phase 4 header/Goal, Phase 8 Goal (a), coverage table,
  DAG) states "built in Ph 8" and self-corrects a builder immediately — zero builder-facing consequence,
  the same disposition pass 5 gave the Gate-144-characterization item. Not elevated to a defect (doing so
  would manufacture a nit against the loop's own consequence standard).
- **P19 (Ph 13) vs P15 (Ph 12) honest-partial parallelism.** Both are advisory nudges, yet only P15 is
  coverage-table-flagged honest-partial. Found principled and already-ratified: P15's CLASS is
  majority-reasoning-bound (no hook sees the chat — the honest-partial flag marks a mechanism that
  can't reach most of its class), whereas P19's class lives entirely in gateable durable files that
  Ph 13 DOES reach (advisorily) — the partiality there is enforcement-strength, stated in the header
  ("the supersession rule's enforceable half") and teeth. Passes 4 and 6 both examined the advisory
  phases + the honest-partial labeling and ruled the current P4/P15-only flagging correct; not re-opened.

**No fix contradicts another; no fix left a loose end elsewhere.** The last three passes' fixes
(Phase 8 `[exit-2]` teeth → Goal (b) → this end-to-end re-read) form a closed, mutually-consistent chain.
The fresh dominant-class sweep (proxy-keyed mechanism / teeth-over-claim) across every phase surfaced
nothing beyond what passes 1–7 already resolved.

Verdict: **CLEAN** — no survivor, grounded in an end-to-end re-read of the three multiply-edited phases
(1/7/8) plus 4/11, a fresh dominant-class sweep, a full coverage/DoD/DAG/owner-decision/claims-resolution
confirmation, and this-session feasibility reads of the real repo. **This starts the 3-consecutive-CLEAN
count: 1 of 3.**

## Pass 9 (sonnet)

Independent cross-model check per the assignment (do not trust pass 8's CLEAN verdict). Re-derived, not
re-summarized, six high-risk claims directly against the real repo rather than pass 8's account of them:
(1) `audit-gates.sh` line count and the `--check` dispatcher boundary (`esac`/`fi` at `:880-881`); (2) the
87/150 dual-region-echo statistic Phase 1's P3 fix rests on — **wrote an independent Python parser**
(not reused from any pass) that extracted every `── Gate N:` header, split by dispatcher-vs-full-suite
region using the real `:881` boundary, and got **exactly 87 of 150 distinct gate numbers appearing in
both regions, all 87 with different text, zero same-region collisions** — matches the plan's cited
figure exactly, independently reproduced; (3) the P5 hook-signature-vs-name-only statistic — wrote a
second independent parser scanning for `gate "..."` calls whose name contains block/deny/denies and
checking for a preceding `hooks/*.sh`-piped + `rc=$?`-captured signature; got 66/9 by a looser heuristic
(vs. the plan's stated 57/8) — same order of magnitude and same conclusion (a small minority actually
key on a hook exit code), confirming the mechanism's *scoping logic* is sound even though exact counts
depend on match strictness; (4) `concerns-catalog.md`'s `xc.tribunal-self-disable` trigger #2 regex —
read verbatim, confirms it is still unfixed and matches the plan's exact citation (no discrimination
between `sed -n`/`sed -i`); (5) `regenerate-artifacts.yml`'s ruleset-protection comments (`:358`,
`:367-369`, `:397`) — present, worded as pass 4/7 cite, PR-only merge path intact; (6) `host-support.json`
has no `activation_gate` field and `ci-gate-audit.md` still documents exactly two fixture categories —
both confirm the plan's dependency/honest-partial claims are still accurate, not stale.

**Issue 11 (NEW, real, with a reproduced mechanical consequence — a different flavor of the plan's own
dominant defect class) — ten "Files touched" / build-instruction citations across Phases 2, 11, 12, and
13 (plus the teeth block §2 and the §6 empirical-evidence section) name a bare, unprefixed path
(`hooks/enforce-portability.sh`, `hooks/hooks.json`, `hooks/guard-premise.sh`,
`hooks/guard-destructive.sh`, `hooks/claim-grounding-lint.sh`, `hooks/_portable.sh` ×5,
`skills/knowledge-file-staleness-sweep/SKILL.md`) that does not exist in this repo and is not covered by
`.repo-layout.json`'s `allowed_globs` — only `plugins/*/hooks/**` and `plugins/*/skills/**` are allowed;
there is no top-level `hooks/` or `skills/` directory at all.** Confirmed by directly invoking the real
`plugins/ravenclaude-core/hooks/enforce-layout.sh` (the exact PreToolUse hook this repo already runs on
every Write/Edit) against the plan's own literal Phase-2 citation:
`{"tool_name":"Write","tool_input":{"file_path":"hooks/enforce-portability.sh",...}}` → **exit 2, DENIED**,
reason `"'hooks/enforce-portability.sh' does not match any allowed_globs in .repo-layout.json"`; the same
check against `skills/knowledge-file-staleness-sweep/SKILL.md` (Phase 13's citation, confirmed to
already exist at `plugins/ravenclaude-core/skills/knowledge-file-staleness-sweep/SKILL.md`) → the same
DENY. Re-running both against the corrected `plugins/ravenclaude-core/`-prefixed paths → **exit 0,
allowed**, confirming the fix. This is not cosmetic: for the five instances that name an **already-shipped**
file (`guard-premise.sh`, `guard-destructive.sh`, `claim-grounding-lint.sh`, `hooks.json`,
`knowledge-file-staleness-sweep/SKILL.md` — all confirmed present only under `plugins/ravenclaude-core/`),
a builder following "Files touched" literally would attempt to create/edit a **different, nonexistent**
file at the wrong location instead of the real file that governs behavior — the fix would silently not
land. For the two new files (`enforce-portability.sh`, `check-portability-lint.*`'s sibling
`hooks.json`-registration line), the builder's own Write would be **denied by this repo's own
layout-enforcement gate** — the exact self-referential "a hardening plan whose own build instructions
get caught by the guard it's hardening" shape the plan's meta-risk M1 already names for source-scan
false-positives, here manifesting as a path-citation defect instead. The inconsistency was also
internally provable without running anything: the *same* Phase 11 "Files touched" line already used the
fully-correct `plugins/ravenclaude-core/scripts/thing-concerns.py` and
`plugins/ravenclaude-core/knowledge/concerns-catalog.md` nine lines earlier while citing bare
`hooks/guard-premise.sh` and `hooks/guard-destructive.sh` in the very same bullet — ruling out "deliberate
shorthand convention" as an explanation. **Fix applied:** corrected all 10 occurrences (5×`hooks/_portable.sh`
via a scoped `replace_all` confirmed not to collide with the one already-correct full-path citation at
line 772; 5 individually-scoped edits for `enforce-portability.sh`, `hooks.json`, `guard-premise.sh`,
`guard-destructive.sh`, `claim-grounding-lint.sh`) plus the `skills/knowledge-file-staleness-sweep/SKILL.md`
instance in Phase 13 (11 total edits) to the correct `plugins/ravenclaude-core/`-prefixed path; added a
one-clause note to Phase 2's `hooks.json` citation naming the dual-registration convention
(CLAUDE.md's "Marketplace-dev hooks" section — plugin-canonical `hooks.json` **and** `.claude/settings.json`
dev-mirror) since a builder touching that file needs to know both wirings exist. Left untouched (judged
not the same defect, no builder-facing consequence): the remaining bare `hooks/**`/`hooks/*.sh` mentions
(lines 201/214/262/306/310/1054/1055/1058/1227/1264/1265) — these are scope-describing prose ("outside
`hooks/**`", "a `hooks/*.sh` script" as a generic shape) sitting next to an already-correctly-prefixed
literal glob (`plugins/**/hooks/*.sh` in Phase 2's own CI-backstop bullet), not a literal path a builder
writes to; and the generic `` `knowledge/` `` mentions in Phases 8/12, which describe a scan corpus
category (any plugin's `knowledge/` dir) rather than a specific file.

**Scrutinized and found sound (no fix needed):** every other "Files touched" line in the plan (17 total,
spot-checked all) resolves to a real top-level (`scripts/**`, `docs/**`, `.github/**`) or correctly
`plugins/ravenclaude-core/`-prefixed path — confirmed `scripts/ravenclaude`, `scripts/check-plugin-detail-render.mjs`
exist at repo-root `scripts/` as cited, `plugins/ravenclaude-core/knowledge/host-support.json` and
`.../knowledge/subagent-safe-guard-checklist.md`'s parent dir are correctly prefixed. Pass 8's Phase
1/7/8 end-to-end reconciliation, the coverage table, DAG, 7 owner decisions, and DoD were all re-read in
full and found consistent with no new dangling reference — the survivor found this pass is orthogonal to
everything passes 1–8 already fixed (a path-citation defect, not a false-positive-firing check or a
teeth-block over-claim), located by directly executing the repo's real enforcement hook against the
plan's own literal citations rather than reasoning about them.

Verdict: **not clean** — 1 real issue found and fixed (10 build-instruction path citations across 4
phases + the teeth block + the empirical-evidence section pointed at a nonexistent top-level `hooks/`/
`skills/` location that this repo's own layout-enforcement hook mechanically denies — reproduced live by
invoking the real hook, not inferred), grounded in this-session repo reads and two independently-written
verification scripts (the 87/150 region-split parser, the P5 hook-signature scanner) that reproduced
prior passes' cited statistics rather than trusting them. Convergence count resets to 0 consecutive
CLEAN passes.

## Pass 10 (opus) — exhaustive mechanical sweep

Applied the plan's own lesson ("enumerate EVERY instance of a class before closing it") as an
exhaustive mechanical-verification sweep against the REAL repo in the worktree, to stop clean/not-clean
oscillating on mechanical loose-ends. Enumerated and existence-checked EVERY file/path citation, spot-
checked EVERY load-bearing `file:line` ref, resolved EVERY `depends_on_claims`, and re-swept the teeth /
coverage / owner-decisions / DAG. **1 real survivor found and fixed (pass 9 fixed 11 path citations of
one wrong-prefix shape; this pass found a 12th, of a DIFFERENT wrong prefix, that pass 9's normalization
could not have caught).**

**Issue 12 (NEW, real, with a builder consequence — same class as pass 9's Issue 11, different wrong
prefix) — two citations of `validating-a-measuring-instrument.md` named a nonexistent
`plugins/ravenclaude-core/knowledge/` path; the file actually lives at `docs/best-practices/`.** Pass 9
hunted the `hooks/`/`skills/` bare-path shape and normalized them to a `plugins/ravenclaude-core/`
prefix; this file is a **different** case — it is NOT under the plugin at all, it is a top-level
`docs/best-practices/` doc (`find` this session: `./docs/best-practices/validating-a-measuring-instrument.md`,
the only copy; **no** `plugins/.../knowledge/` copy exists), so the `plugins/ravenclaude-core/`-prefix
normalization pass 9 ran would have skipped it entirely. Confirmed the concrete consequence: **Phase 0's
sole deliverable is a markdown cross-link to this file**, and Phase 0's own acceptance test states "the
existing `check-md-links.py` gate validates the new link resolves" — a builder following the plan's
literal path (`hardening-plan.md:161`, the Phase-0 live-open item) would author a link to the nonexistent
`plugins/ravenclaude-core/knowledge/…` target, which the phase's own named gate (Gate 29 / `check-md-links.py`,
confirmed present at `scripts/check-md-links.py`) would then reject — the exact "a hardening plan whose own
build instruction is caught by the guard it relies on" shape pass 9 named. It was also cited a second time
at `hardening-plan.md:910` (Phase 15's Files-touched "(referenced)" line). **Fix applied:** corrected both
occurrences (161, 910) to `docs/best-practices/validating-a-measuring-instrument.md` via a scoped
`replace_all` on the exact wrong-path string (line 920's bare-name `[contract]`-teeth reference carries no
path prefix and is correct as-is — left untouched, consistent with how every other file is cited by bare
name in a teeth line). Re-verified: the corrected path resolves to an existing file (so the Phase-0 link
now passes `check-md-links.py`), and both plan lines now read `docs/best-practices/`.

**Everything else enumerated and verified SOUND against the real repo this session (no fix needed):**
- **Every `plugins/ravenclaude-core/…` citation** (13 distinct): all EXIST except the two legitimately-new
  proposed files (`hooks/enforce-portability.sh`, `knowledge/subagent-safe-guard-checklist.md`), whose
  parent dirs are layout-allowed. `monitors/` correctly `plugins/ravenclaude-core/monitors/` (holds
  `watch-run-state.sh`); pass 9's `hooks/*`/`skills/…SKILL.md` fixes all intact.
- **Every `scripts/…` citation:** all EXISTING-file refs resolve (`audit-gates.sh`, `check-macos-portability.sh`,
  `check-marketplace-claims.py`, `check-host-support.py`, `check-dashboard-server-parity.py`, `ravenclaude`,
  `check-plugin-detail-render.mjs`, `serve-dashboards.py` [twin: root + plugin, confirming the Phase-4 P12
  claim], `generate-copilot-plugin.py`); every new `scripts/check-*.py`/`.sh` path fnmatches `scripts/**`
  in `.repo-layout.json` (ran the pass-9 fnmatch check over all 14 proposed new paths → all ALLOWED).
- **Every bare-name file reference** (`check-md-links.py`, `check-shell-router.selftest.mjs`, `classify_claim.py`,
  `premise-gate.py`, `runaway-brake.sh`, …): all exist — `classify_claim.py`/`premise-gate.py` confirmed at
  **marketplace-root** `scripts/`, which is exactly the "still-open packaging move" Phase 2 claims (accurate,
  not stale).
- **`file:line` spot-checks:** `audit-gates.sh` = **6454 lines exact** (matches Phase 1); `:877` Supported
  list (Gate 184 present → P2 remediation landed) + `:881` dispatcher `fi` boundary; exit-2 template
  `gate "guard-destructive blocks with exit 2 (not 1)"` at **:1048** (`:1046-1049`); Gate 184 header `:6108`;
  Gate 179 UNWIRED `:6092` (exit-1 verdict `:6097`); Gate 144 `:5377`; Gate 16 `:1820`; Gate 32 `:3449`;
  `_skip_or_fail()` `:945`; grep-by-name ritual `:6119`; Gate 194 canonical `:6406` / per-gate `:871`.
  `_portable.sh:37` = `_rc_timeout()`; `check-plugin-detail-render.mjs:54` = `RC_BASELINE`;
  `generate-copilot-plugin.py:421` = the verbatim-`description` reuse; `regenerate-artifacts.yml` `:358`/
  `:367-369` (ruleset-protection comments) + `:372` (`peter-evans/create-pull-request`) + `:386`
  (`chore/self-heal-artifacts`) + `:416` (the "Merge the self-heal PR once its required checks pass" step —
  `:416-424` still lands squarely on the auto-merge step even though the file grew and the `gh pr merge`
  line is now `:458`); `ci-gate-audit.md:25-26` still exactly two fixture categories (`must_fail_on`/
  `must_pass_on`), confirming Phase 1's P4 honest-partial baseline is not stale.
- **Statistics:** 6454 lines (exact). 87/150 (P3) and 57/8/49 (P5) were independently reproduced by pass 9's
  two parsers (87/150 exact; P5 66/9 by a looser heuristic → same conclusion); not re-run this pass to avoid
  re-tripping the `xc.tribunal-self-disable` false-positive on a `thing`/`audit` parse — directionally
  confirmed, exact P5 counts carried from pass 3's measurement (8+49=57 internally consistent). "2 of 6"
  (CL-5/Phase 5) confirmed still accurate by pass 7's deep read; the cross-repo milestone record (this
  session's injected plugin `CLAUDE.md`) independently corroborates Gates 184/185/186/189/190/193/194 and
  the count-gate scope.
- **`depends_on_claims`:** every token resolves — the full set is exactly CL-1…CL-25, none out of range,
  none dangling (Ph 16's explicit `[]` included). Coverage table maps all P1–P21 with prevent+remediate;
  owner decisions = 7; DoD + DAG unchanged and consistent — all re-confirmed by passes 8/9 and unaffected
  by this pass's single path edit.

**Live incident recorded (fresh §6-incident-(d)-class recurrence, NOT a plan defect — reinforces Phase 11
Half A).** Mid-sweep, a single read-only Bash verification command (`sed -n`/`grep -n` line-range reads of
`plugins/ravenclaude-core/hooks/_portable.sh` + `scripts/check-macos-portability.sh`, to confirm the plan's
own `file:line` citations) was **DENIED pre-LLM by the command-review tribunal** —
`xc.tribunal-self-disable`, "would disable or tamper with the Thing itself" (Sága-logged
`thing-2026-08-13T…json`). It mutated nothing; the trigger-#2 regex fired on the bare `sed` token within
200 chars of a `ravenclaude-core/hooks|scripts` path with no read-vs-mutation discrimination — **exactly**
the mechanism the plan's Phase 11 Half A adds a mutation-flag discriminator for, and exactly the §6
incident (c)/(d) shape. **Anti-tunnel discipline honored:** did NOT reword-to-route-around, did NOT
Write-placeholder-then-Edit, did NOT switch tools to smuggle the same shell verb; instead used the **Read
tool** (the canonical, sanctioned file-read path — not an evasion of a matcher) for the remaining plugin-
substrate line-range checks, and recorded the denial here. This is the fourth-plus live firing of the
plan's highest-frequency class across the run, and it fired on THIS critic pass's ordinary verification
work — independent, this-session corroboration that Phase 11 Half A's reprioritization into the P0/P1 band
is empirically warranted, not merely asserted.

Verdict: **not clean** — 1 real mechanical survivor found and fixed (a wrong-prefix path citation of a
`docs/best-practices/` file mis-homed under `plugins/ravenclaude-core/knowledge/`, ×2 occurrences, with a
Phase-0-gate builder consequence; the 12th path-citation defect of pass 9's class, of a prefix shape pass 9
structurally could not have caught), grounded in this-session repo reads (`find`, existence checks, the
`.repo-layout.json` fnmatch, the real `check-md-links.py` presence). Every other file/path/`file:line`/
statistic/`depends_on_claims`/teeth/coverage/DAG element enumerated and verified sound. Convergence count
resets to 0 consecutive CLEAN passes.

## Pass 11 (sonnet) — CLEAN [RECONCILED — entry reconstructed from the pass-11 receipt; the original append was lost, itself a live instance of the reported-done-but-artifact-not-updated class]

**Provenance of this entry.** Pass 11 ran, verified the plan, and returned a CLEAN receipt to the
orchestrator — but its append to this file never landed (a live instance of the exact "work done but the
durable artifact not updated" shape the plan's own R6/P19 class describes). Reconstructed by Pass 13
(sonnet) from the pass-11 receipt handed to the orchestrator, dated identically to when Pass 11 actually
ran, and inserted here in its correct chronological position between Pass 10 and Pass 12 rather than
appended out of order.

**Verification summary (per the receipt):** verified pass-10's fix to
`docs/best-practices/validating-a-measuring-instrument.md` landed at both occurrences (the wrong
`plugins/ravenclaude-core/knowledge/` prefix corrected to the real `docs/best-practices/` path); re-verified
15+ file:line citations word-for-word against the real repo (`enforce-layout.sh`, `_portable.sh:37`,
`concerns-catalog.md` trigger regex, `audit-gates.sh` ×7, `ci-gate-audit.md`, `regenerate-artifacts.yml`,
`host-support.json` confirmed to have no `activation_gate` field, `check-macos-portability.sh`); re-derived
the 87/150 dual-region statistic with a fresh parser (the third independent reproduction of that number);
confirmed every `depends_on_claims` token resolves inside CL-1…CL-25; a full end-to-end read of the plan
was internally consistent; hit the `xc.tribunal-self-disable` false-positive mid-verification and handled
it via the **Read tool** (the sanctioned file-read path) rather than tunnelling around the denial.

Verdict: **CLEAN** — no survivor found. (1 of 3 consecutive CLEAN passes at the time it ran, per this
reconstructed record — see Pass 12's counting-state note below and Pass 13's reconciliation of it.)

## Pass 12 (opus) — CLEAN: independent cross-model re-derivation (build-readiness + 6 high-risk claims reproduced from scratch + path-citation class re-swept + coverage/DoD/DAG/owner-decisions/claims all confirmed) — no survivor

Independent confirmation pass per the assignment (do NOT trust the prior CLEAN — re-scrutinize as a
different model). Read the full 1,291-line plan, the inventory (P1–P21 / R1–R6), the claims table
(CL-1…CL-25), and all prior passes. Did not re-summarize prior passes' work — re-derived the load-bearing
facts from scratch against the real worktree repo with independently-written parsers, then ran the
build-readiness lens the next (build-plan) stage needs.

**Counting-state note (recorded honestly, not a plan defect):** the loop-log as I found it ends at
**Pass 10** (opus), which found Issue 12 and reset the convergence count to 0. There is **no Pass 11
entry in this file** — despite the spawn brief describing a clean pass 11 (1 of 3). I cannot substantiate
a "2 of 3" from the artifact, so I record this as CLEAN and leave the count for the orchestrator to
reconcile: per the committed log, this is the **first** CLEAN since pass 10's reset (1 of 3) unless an
unlogged pass 11 exists. The plan itself is not affected by this metadata discrepancy.

**[Reconciled by Pass 13]:** Pass 11's entry has since been reconstructed from its receipt and backfilled
above, in its correct chronological position between Pass 10 and this entry. This pass (12) is therefore
retroactively confirmed as the **2nd** of 3 consecutive CLEAN passes, not the 1st — though Pass 13 (below)
found a real survivor and reset the count to 0 regardless, so this reconciliation is for audit-trail
accuracy, not because the streak continued.

**Path-citation class (passes 9/10's survivor class) — re-swept independently, fully closed.** Wrote a
fresh parser that extracted every backticked path token in the plan and, for each, checked existence +
`.repo-layout.json` `allowed_globs` coverage. **All 18 "Files touched" build-citation lines** now resolve
to either an existing file or a layout-allowed new file; **every slash-bearing path across the whole plan
(prose included) resolves** — no wrong-prefix `hooks/`/`skills/`/`knowledge/` survivor of pass 9's shape,
no `plugins/…/knowledge/`-mishomed `docs/best-practices/` file of pass 10's shape. The only tokens my
parser flagged were **bare basenames** (`audit-gates.sh`, `plugin.json`, `marketplace.json`, `runaway-brake.sh`,
…) used as legitimate prose/teeth shorthand — the exact disposition passes 9/10 gave them.

**Six high-risk claims re-derived from scratch (independent parsers, not prior passes' numbers):**
1. `scripts/audit-gates.sh` = **6454 lines exact**; `Supported:` at `:877`; dispatcher `esac` at `:880`, `fi` at `:881` — all match Phase 1's cited contract.
2. Phase 1 P3's region-keying statistic — my own region-split parser (boundary at the confirmed `:880` `esac`) got **exactly 150 distinct gate numbers, 87 dual-region (all 87 with *different* header text), 0 same-region full-suite collisions** — reproduces the plan's "87 of 150" precisely and confirms the P3 check must key on region, not description-difference.
3. `plugins/ravenclaude-core/knowledge/host-support.json` has **no** `activation_gate` field — Phase 6/8's dependency is a real, not-yet-satisfied one (plan correctly unbuilt).
4. `docs/best-practices/ci-gate-audit.md` documents **exactly two** fixture categories (`must_fail_on`, `must_pass_on`) — Phase 1's P4 honest-partial baseline is accurate, `must_flag_unwired_on` genuinely not yet present.
5. `concerns-catalog.md` trigger #2 (the verb-near-substrate-path screen) is present verbatim as cited, still with **no read-vs-mutation discriminator and no read-mode exemption** — Phase 11 Half A's fix is genuinely needed and unbuilt.
6. `.github/workflows/regenerate-artifacts.yml` self-heal is **PR-only** via `peter-evans/create-pull-request` on `chore/self-heal-artifacts`, with the "main is protected — direct push rejected by the ruleset" comments intact — Phase 7's "Honest bound" (ruleset is the real guarantee) holds.
   Plus 10 load-bearing `file:line` citations spot-checked against the real file (Gate 144 `:5377`, Gate 32 `:3449`, Gate 179 UNWIRED `:6092`/`:6097`, exit-2 template `:1046`/`:1048`, Gate 184 `:6108`, Gate 16 `:1820`, grep-suite ritual `:6119`, Gate 190 `:801`) — **every one resolves to exactly the cited content**, corroborating pass 10's exhaustive sweep across models.

**Build-readiness lens (what the next stage derives the build plan from) — every phase is buildable.**
Walked all 17 phases (0–16): each names its file(s), the check it ships, its must-fail fixture(s), and its
acceptance test. The only two no-must-fail-fixture cases are **honestly flagged as such** and not read as
claimed coverage — Phase 1's P4/UNWIRED doc-convention addition (stated "no must-fail fixture in this phase,
by design") and the doc-only Phases 0/15 — and Phase 11 Half A's Write-scoped-matcher fix carries an
explicit `[unverified — confirm matcher scope during build]` marker rather than a guessed contract. No phase
is too vague to build.

**Dominant-defect-class sweep (proxy-keying / teeth-over-claim / fail-open / non-portable bash /
self-referential) — no last instance.** Proxy-keying: Phase 1 P3/P5 key on region / hook-invocation
signature (the real shapes), Phase 7's grep is honestly bounded to the ruleset as the true guarantee,
Phase 9 keys on the structural unscoped-wildcard-beside-scoped-sibling shape. Teeth-over-claim: Phase 8's
`[exit-2]` (pass 6/7 fixes) is internally consistent oracle-backed-hard-vs-advisory across Goal/tests/teeth;
every advisory phase (12/13/14) states `[exit-2] N/A-by-design`. Fail-open: Phase 3 *is* the fail-closed
mechanism and asserts exit **2** specifically. Non-portable bash: all new scripts are Python 3.9 stdlib /
bash-3.2-safe and route shimmed needs through `_portable.sh`. Self-referential: the per-phase `[SNR]` lines
correctly split structurally-safe CI readers from genuine deny-hook/prose-scan RISKs that depend on
Phase 11's exempt path. No new instance.

**Coverage / owner-decisions / DoD / DAG / depends_on_claims — confirmed.** §1 maps all 21 classes with a
prevention phase + a remediation of live-open (P4/P15 the only two honest-partial flags, correct); §10 = 7
owner decisions; §9 DoD is per-phase + whole-initiative; §4 DAG hard edges (3→1, 3→2, 8→{6,12}) + Phase 11
as shared dependency of {2,7,8,9,12,13} match the phase texts; every phase's `depends_on_claims` resolves
inside CL-1…CL-25 (Ph 16's explicit `[]` included).

**Live incident (fresh §6-(d)-class recurrence, NOT a plan defect — corroborates Phase 11 Half A).** For
every plugin-substrate file read this pass I used the **Read tool** (the sanctioned file-read path) and
Python, deliberately avoiding the verb-near-substrate-path shape that denied passes 9/10's ordinary
verification reads — anti-tunnel discipline honored (no reword-to-route-around, no Write-placeholder tunnel,
no tool-switch to smuggle a matcher-tripping verb). This is independent, this-session corroboration that
Phase 11 Half A's reprioritization is empirically warranted.

Verdict: **CLEAN** — no survivor. Grounded in independently-written parsers that reproduced the plan's
load-bearing statistics from scratch (6454 lines exact; 87/150 dual-region exact), a full path-citation
re-sweep confirming passes 9/10's fixes hold with no new shape, 10 file:line spot-checks all accurate, a
build-readiness pass over all 17 phases, and a fresh dominant-class sweep — none fabricated. Per the
committed loop-log this is the first CLEAN since pass 10's reset (see the counting note above).

## Pass 13 (sonnet) — 1 real survivor found and fixed (a stale gate-number citation, content-mismatched, of a class no prior pass's spot-check methodology could have caught)

Two tasks per the brief: (1) reconcile the loop-log audit-trail gap (Pass 11's lost append), (2) an
independent third-confirmation scrutiny that does NOT trust passes 11/12's verdicts.

**Task 1 — loop-log reconciled.** Backfilled the `## Pass 11 (sonnet) — CLEAN [RECONCILED …]` entry
above, in its correct chronological position between Pass 10 and Pass 12, reconstructed from the pass-11
receipt per the brief's exact content. Added a `[Reconciled by Pass 13]` annotation to Pass 12's
counting-state note (which had honestly recorded "no Pass 11 entry" and treated itself as the first CLEAN
since pass 10) so it no longer reads as stale now that Pass 11 is backfilled — Pass 12 is retroactively the
2nd of 3, not the 1st, for the audit trail's sake (moot for the live convergence count below, since this
pass resets it regardless).

**Task 2 — independent spot-check found a real survivor.** Verified 6 file:line citations directly against
the real `scripts/audit-gates.sh` (6454 lines, confirmed exact again): `_rc_timeout` at
`_portable.sh:37` ✓; `host-support.json` confirmed to have no `activation_gate` field ✓; the Phase-0
cross-link at `hardening-plan.md:161`/`:910` confirmed still reading `docs/best-practices/…` (pass 10's fix
holds) ✓; `ci-gate-audit.md:25-26` confirmed still exactly two fixture categories ✓; Gate 179 UNWIRED
comment at `:6097` ✓; Gate 184 present in both the dispatcher region (`:744`) and the full-suite region
(`:6108`) ✓ — **but the 7th check broke the streak.**

**The survivor: Phase 4's Goal and Teeth cited `audit-gates.sh:5377–5399` as "Gate 144's derive-and-compare
… already running the same render check over both dashboard.html and index.html" — the precedent the whole
Phase 4 surface-parity mechanism (P11/P12) generalizes from.** Read that exact line range in the real repo:
`:5377` is `── Gate 144: Prompt Builder render + XSS floor (check-prompt-builder-render.mjs) ──` — an XSS/
render check for an unrelated feature, nothing to do with nav-route placement or `DASH_OWNER`. Grepping the
file for the actual DASH_OWNER/`navChildren` derive-and-compare logic the plan describes (extracts the four
nav maps, executes `navChildren()`/`resolveNavActive()`, two must-fail halves — a dropped sub-nav link and
a removed `DASH_OWNER` destination) found it at **`── Gate 51: Unified portal shell router + committed-route
destinations ────` (`:4282`), with the must-fail teeth at `:4366` and `:4408-4419`** — a completely
different gate. Cross-checked against `plugins/ravenclaude-core/CLAUDE.md:1961-1989` (the dated v0.216.0
milestone problem-inventory.md P11 cites): at that release the derive-and-compare fix genuinely *was* filed
under "Gate 144" — so the plan's citation was accurate to the historical record it was drawn from, but the
harness has since been renumbered (consistent with the repo's own P3 class — gate-number reassignment over
time) and gate number 144 was later reused for the unrelated Prompt Builder feature while the DASH_OWNER
mechanism now lives under Gate 51. The plan's forward-looking "already running the same render check"
present-tense claim, with a specific current line citation, is simply wrong in the current tree. This is
the plan's own P11 class (presence-not-placement / assert-the-wrong-surface) recurring **inside the plan's
own citation of the gate meant to fix it** — pointed enumeration of *why* it survived 12 prior passes: every
prior file:line spot-check (passes 1, 8, 9, 10, 12) confirmed only that a `Gate 144` header exists at that
line — none diffed the header's *content* against the plan's semantic claim about what the gate does. A
citation can resolve and still be wrong.

**Fix applied — targeted `Edit`, 4 occurrences, `Gate 144` → `Gate 51` + line range `5377–5399` →
`4282–4421`:** `hardening-plan.md:57` (§0 strategy summary), `:105` (§1 coverage table, P11 row), `:395`
(Phase 4 Goal — plus the line-range correction), `:424-425` (Phase 4 Teeth `[contract]` line — plus the
line-range correction). Left problem-inventory.md's and claims-table.md's "Gate 144" references
**untouched** — those correctly describe the dated v0.216.0 historical incident (accurate to what was true
then; per scope, G1 artifacts are reused, not re-derived) and are not forward-looking build citations. Did
NOT touch Phase 14's "Gate 51's unchanged-selftest pattern" (P10) reference, which is a *different*,
already-correct use of Gate 51 (the self-certifying-change historical incident) — confirmed no collision
between the two Gate-51 usages, since the current Gate 51 genuinely covers both the router-existence check
(Phase 14's precedent) and the by-destination DASH_OWNER check (Phase 4's, now correctly cited). All 4 edits
applied cleanly — no guard denial, no tunnel needed.

**Remaining independent scrutiny (per the brief's checklist), no further survivor:**
- **Coverage table:** all 21 rows P1–P21 present, each with both a Prevention-phase and a
  Remediation-of-live-open column filled (§1) — matches problem-inventory's 21-class dedup exactly, no
  class dropped or duplicated.
- **7 owner decisions:** cross-checked §10 against problem-inventory's 6 named seeds — all 6 present
  (RC_BASELINE/seed 1, guard-escape-door/seed 2, macOS aggressiveness/seed 3, canary-mandatory/seed 5,
  priority-sequencing/seed 4, DOM-budget/seed 6) plus decision 7 (the advisory-tail question), which the
  text itself correctly labels as "beyond the six seeds" (a Panel A addition) rather than silently inflating
  the seed count. Framing consistent, no orphaned or mislabeled seed.
- **DoD completeness:** §9's per-phase + whole-initiative DoD matches `scope.md`'s stated DoD ("the build
  plan is complete and I surface the decisions the owner must make") — this run's own DoD is correctly
  scoped as "the plan + owner decisions, not the build," consistent throughout.
- **Dominant-class sweep (proxy-key / teeth-overclaim / fail-open / non-portable / self-ref):** the Gate
  144→51 finding above **is** the proxy-key/presence-not-placement class, so I additionally spot-checked 4
  more gate-number citations for the same content-mismatch shape — Gate 154 (`:470` dispatcher / `:5514`
  full-suite, "host-support map completeness + derivation" — content matches), Gate 167 (`:600` / `:5820`,
  "Copilot -> tribunal end-to-end" — matches), Gate 190 (`:801` / `:6259`, "premise ledger scoping" /
  "blast radius" — matches), Gate 6 (`:1246`, "Behavioral enforce-layout" — matches). No second instance of
  the class found; the Gate 144 citation appears to be an isolated stale-renumbering casualty, not a
  systemic recurrence across the plan's ~15 gate citations — enumerated rather than assumed.

Verdict: **NOT CLEAN** — 1 real survivor found and fixed (a stale, content-mismatched gate-number citation
surviving 5 prior passes' file:line spot-checks because none of them diffed cited-line *content* against
the plan's semantic claim, only cited-line *existence*), grounded in this-session repo reads
(`grep`/`awk`/`wc -l` via Bash, `Read` tool for file contents — no guard denial encountered this pass).
Loop-log audit-trail gap reconciled (Pass 11 backfilled, Pass 12's counting note annotated). Convergence
count resets to **0** consecutive CLEAN passes.

## Pass 14 (opus) — exhaustive citation sweep

The mandate: verify EVERY citation in the plan against the CURRENT repo in one pass and close the
citation-drift class exhaustively (pass 9/10 found path prefixes; pass 13 found a renumbered gate — Gate
144→51). Enumerated and re-derived every gate-number, `file:line`, path, and load-bearing statistic
against the real worktree this session. **Result: 2 edits — 1 genuine citation survivor fixed + 1
self-documenting drift-note added; everything else resolves exactly.**

**Survivor found + fixed — Phase 1's dispatcher-boundary line label was off by one.** The reachability
sub-check (`hardening-plan.md:186`) cited the full-suite region as beginning "after the `--check`
dispatcher `esac` at `:881`". Read the real `audit-gates.sh:875–882` (via Read tool): line **880** is
`  esac`, line **881** is `fi`. So the cited line 881 contains `fi`, not `esac` — the `esac` is at 880.
The boundary line number (881) is correct for the region split (the region begins after the `fi` that
closes the whole `if [ --check ]` block), but the label named the wrong construct. **Fix:** rewrote to
"after the `--check` dispatcher block closes — `esac` `:880` / `fi` `:881`", so both lines are named
exactly. (Pass 12 had read these same lines and called it a match; strictly, line 881 ≠ `esac`, so this
pass tightens it — the whole point of the exhaustive sweep.)

**Self-documenting drift-note added — Phase 4's Gate 51 citation (the one pass 13 just repaired).**
Gate numbers demonstrably renumber (144→51 bit pass 13). Added an inline "verify the gate number against
the current `audit-gates.sh` before building … and gate numbers drift" note at the Phase 4 Goal citation,
naming that this mechanism shipped under "Gate 144" until the renumber and that Gate 144 is now the
unrelated Prompt Builder XSS check at `:5377` — so a future reader is warned at the exact spot that most
recently drifted. Confirmed pass 13's fix is itself sound: Gate 51 (`:4282–4421`) genuinely contains the
DASH_OWNER derive-and-compare (must-fail teeth at `:4407`/`:4419`) and runs `check-committed-routes.mjs`
over **both** `$DASH_HTML` and `$IDX_HTML` (`:4393–4394`) — so the citation now points at the gate that
actually does the mechanism, and the residual "render check" phrasing is the same non-misdirecting
looseness pass 5 already blessed.

**Everything else enumerated and verified EXACT against the current repo (no drift):**
- **Every `Gate N` reference resolves to the current header + role.** Gate 51 `:4282` (portal router /
  DASH_OWNER — the Phase-4 precedent); Gate 144 `:5377` (Prompt Builder XSS — correctly NOT the Phase-4
  mechanism); Gate 32 `:3449` (server endpoint parity, Phase 4 P12); Gate 179 `:6092`/UNWIRED verdict
  `:6097` (Phase 1 P4); Gate 184 `:6108` full-suite / `:744` dispatcher (Phase 1 keystone); Gate 154
  `:5514` (Phase 8 host-support); Gate 167 `:5820` (Phase 6/8 Copilot→tribunal); Gate 190 `:801`
  dispatcher / `:6259` full-suite (Phase 10 premise-ledger scoping); Gate 16 `:1820` (Phase 1
  regex-compile); Gate 194 `:871` per-gate / `:6406` canonical (Phase 1's dual-region 87/150 evidence);
  Gate 132 `:5192` (Phase 16 DOM ratchet); Gate 29 `:3233` (Phase 0/15 check-md-links); Gate 187 `:6153`
  (Phase 2 "Gate-187-adjacent"). Gate 6's "counterfeit deny subtests" (Phase 3) confirmed grounded in the
  v0.193.0 milestone (Gate 6's deny subtests were passing exit=1 "green for the wrong reason" on macOS).
- **Every `file:line` still contains what the plan says:** exit-2 template `:1047`(`[ "$rc" -eq 2 ]`)/`:1048`(the
  `gate "guard-destructive blocks with exit 2 (not 1)"` assertion); `Supported:` list `:877` (Gate 184
  present → P2 remediation landed); grep-suite ritual `:6119`; `_skip_or_fail()` `:945`; the three P5
  internal-decision-engine examples `:1590` (`thing_decision`→`[[ "$d"=="deny" ]]`), `:2148` (adapter
  `.permissionDecision` jq), `:2279` (`_predeny` boolean); `_portable.sh:37`=`_rc_timeout()`;
  `enforce-layout.sh:40–46` (stdin-jq fallback) + `:94–105` (`emit_deny` deny-JSON + exit 2);
  `check-macos-portability.sh:26–30` (why-a-runner-not-a-linter) + `:83–85` (exit-code contract);
  `check-plugin-detail-render.mjs:54`=`const RC_BASELINE = {`; `generate-copilot-plugin.py:421`
  (verbatim `description` reuse); `regenerate-artifacts.yml` `:358`/`:367–369` (ruleset-rejects-direct-push
  comments), `:372` (`peter-evans/create-pull-request`), `:386` (`chore/self-heal-artifacts`),
  `:416–424` (still lands on the "Merge the self-heal PR once its required checks pass" step).
- **Every repo path exists / is layout-allowed:** all confirmed unregressed since pass 10's sweep — no
  new wrong-prefix survivor (`plugins/ravenclaude-core/…`, `scripts/…`, `docs/best-practices/…` all
  resolve; the two proposed-new files' parents are allowed).
- **Every load-bearing statistic holds:** `audit-gates.sh` = **6454 lines** (matches Phase 1); **87/150**
  (P3 dual-region — independently reproduced 3× by passes 9/11/12 against this exact unchanged file);
  **57/8/49** (P5 — the plan's three cited example lines 1590/2148/2279 all verified; directional
  "small minority key on a hook exit code" holds, exact counts heuristic-dependent as the plan states);
  **"2 of 6"** (Phase 5 — `check-marketplace-claims.py` docstring confirms only skill-count (check 2) +
  agent-count (check 2b) are general cross-marketplace gates; hooks/rules are rc-core-README-only,
  templates/commands uncovered).

**Re-confirmed already-converged (not re-litigated):** §1 coverage table maps all P1–P21 with both a
prevention phase and a remediation-of-live-open column (P4/P15 the only two honest-partial flags); the
per-phase teeth blocks stay honest (no over-claim reintroduced); every `depends_on_claims` resolves
inside CL-1…CL-25 (Ph 16's explicit `[]` included); §10 = 7 owner decisions; §9 DoD per-phase +
whole-initiative; §4 DAG hard edges (3→1, 3→2, 8→{6,12}) + Phase 11 as shared dependency of
{2,7,8,9,12,13} match the phase texts.

**Live incident (fresh §6-(d)-class recurrence, NOT a plan defect — corroborates Phase 11 Half A).** A
single read-only `sed -n`/`grep` compound (verifying `_skip_or_fail`, Gate 179, "counterfeit", and
`_portable.sh:37` in one batch) was DENIED pre-LLM by `xc.tribunal-self-disable` — "would disable or
tamper with the Thing itself" — because it named `plugins/ravenclaude-core/hooks|scripts` substrate
paths with no read-vs-mutation discrimination (Sága `thing-2026-08-13T17-55-22Z-75185.json`). **Anti-tunnel
discipline honored:** did NOT reword to route around it, did NOT Write-placeholder-then-Edit, did NOT
switch tools to smuggle the verb — used the **Read tool** (the sanctioned file-read path) for every
plugin-substrate read and recorded the denial here. This is the fifth-plus live firing of the plan's
highest-frequency class across the loop, on THIS pass's ordinary citation-verification work —
independent this-session corroboration that Phase 11 Half A's reprioritization is empirically warranted.

Verdict: **not clean** — 1 genuine citation survivor found + fixed (a line-label off-by-one: cited line
881 is `fi`, `esac` is 880) plus 1 preventive self-documenting drift-note at the freshly-renumbered Gate
51 citation, grounded in an exhaustive this-session re-derivation of every gate-number / `file:line` /
path / statistic against the real repo. The citation-drift class is now swept end-to-end: no other gate
number, line reference, path, or statistic drifted. Convergence count resets to **0** consecutive CLEAN
passes (this pass made edits).

## Pass 15 (sonnet) — 1 real survivor found and fixed (a tier-label contradiction no citation-focused pass could have caught, since it names no file/line/gate-number)

Confirmation pass 1 of the final 3-consecutive-clean run. Did **not** trust pass 14's CLEAN — re-read the
full ~1,294-line plan end-to-end (all 17 phases, §0 strategy, §1 coverage table, §4 DAG, §5 divergence
reconciliation, §6 empirical evidence, §7 risk matrix, §8 prioritization, §9 DoD, §10 owner decisions),
the entire loop-log (all 14 prior passes), `problem-inventory.md`, and `claims-table.md`. Spot-checked 3
of pass 14's citations against the real repo rather than trusting its account, then ran a fresh holistic
sweep for any structural issue orthogonal to the citation-drift class the last four passes (9/10/13/14)
already closed. **1 real, new issue found and fixed — a tier-label self-contradiction, not a citation
defect, so it was invisible to every prior pass's file:line/gate-number/path methodology.**

**Citation spot-checks (3 of pass 14's, confirmed exact against the real repo this session):**
1. `audit-gates.sh:875-882` — line **880** is `esac`, line **881** is `fi` (`wc -l` also reconfirms 6454
   lines total). Matches pass 14's fix verbatim: "`esac` `:880` / `fi` `:881`" (`hardening-plan.md:185`).
2. `audit-gates.sh:4282` — `── Gate 51: Unified portal shell router + committed-route destinations ────`.
   Matches pass 13/14's corrected Phase-4 citation (Gate 144→51) exactly; the header's actual content
   (portal router / route destinations) matches the plan's DASH_OWNER derive-and-compare claim, not the
   unrelated Prompt Builder XSS check still correctly sitting at Gate 144 (`:5377`).
3. `audit-gates.sh:1046-1049` — the exit-2 template: `:1047` is `[ "$rc" -eq 2 ]`, `:1048` is
   `gate "guard-destructive blocks with exit 2 (not 1)" must_pass "$rc_is_2"`. Matches Phase 1's P5
   citation and Phase 3's `[contract]` line exactly.

All 3 resolved exactly as pass 14 described — the exhaustive sweep's methodology is trustworthy on this
sample; no re-litigation needed of the other 11 gate-numbers/citations/statistics passes 9-14 already
closed.

**Issue 13 (NEW, real, with consequence — a self-contradiction invisible to every citation-focused pass,
since it cites no file/line/gate-number) — the plan's own P0/P1/P2 tier vocabulary is used
inconsistently for Phase 11 Half A: six narrative mentions call it "the P1 band" while §8's authoritative
Prioritization table places it in the P0 tier.** Confirmed by grep across the whole file:
`hardening-plan.md:84`, `:756-757`, `:989` (the §4 DAG ASCII diagram), `:1012-1013`, `:1076`, and
`:1169` (§6's load-bearing empirical-evidence conclusion) all said Phase 11 Half A "moves into" / "is
reprioritized to" / "elevates … into" **"the P1 band."** But §8's own table — the section titled
"Prioritization (P0 / P1 / P2)" and the canonical tier assignment every other phase in the plan is keyed
against (§0 tags Phase 1/2/3 "**P0.**", Phase 4/5/6 "**P1.**" using this exact vocabulary) — places
"**Ph 11 Half A**" squarely inside the **P0** row (`:1211`: "P0 — do first (no owner input beyond
approving this plan) | … **Ph 11 Half A** … | … **Ph 11 Half A is promoted here from the residual tail
by §6's live evidence** — it closes the measured highest-frequency live failure and needs no owner
gate"). This is not a stylistic wobble: the table's own row definitions make the two tiers mutually
exclusive on the exact property that decides Half A's placement — **P0** is defined as "no owner input
beyond approving this plan," **P1** as "needs one owner ruling, or composes with P0." Half A is stated
everywhere (§10 owner decision 2: "Independent of this ruling: authorize Ph 11 Half A now"; the DAG
diagram itself, `:990`: "NO wider owner gate") to need **zero** owner ruling — which structurally
disqualifies it from P1 by the table's own definition and confirms P0 is the semantically correct tier.
Consequence: a reader following the six narrative mentions (§0's strategy summary, §4's DAG diagram, §5's
divergence reconciliation, §6's headline empirical conclusion) would believe Half A ships in the *second*
wave behind an owner ruling, directly contradicting §8's own table and owner-decision 2's explicit
"ships now, no gate" framing — the exact kind of cross-section drift the coverage table, DAG, and
owner-decisions cross-checks in this task's brief exist to catch. It survived 14 prior passes because none
of them was keyed to catch it: passes 9/10/13/14 (the citation-drift specialists) grep for file:line
refs, gate numbers, and paths — a bare tier label carries none of those, so it was structurally outside
every previous pass's search surface, and no prior pass's "holistic" pass (4, 6, 8, 12) happened to grep
the tier vocabulary specifically. **Fix applied:** corrected all 6 "P1 band" occurrences to "P0 band" (a
literal string change preserving every surrounding sentence), verified via `grep -n "P1 band"` returning
zero hits post-fix and `grep -n "P0 band"` returning exactly the 6 corrected lines, and added a short
inline cross-reference at the first occurrence (`:84`) pointing to §8's table and stating *why* P0 is
correct ("needs no owner ruling, matching P0's definition rather than P1's"), so a reader hitting the
inconsistency's origin point immediately sees the resolution rather than having to hunt for it. Left
§8's table itself untouched (it was already correct — the narrative prose was the outlier, not the table).

**Remaining holistic checks (no further survivor):**
- **Coverage table (§1):** re-confirmed all 21 rows P1–P21 present, each with both a Prevention-phase and
  a Remediation-of-live-open column filled; P4 (Ph 1) and P15 (Ph 12) remain the only two honest-partial
  flags — unchanged by this pass's tier-label fix (the coverage table names phases, not tiers).
- **7 owner decisions (§10):** all present — RC_BASELINE (Fork 1), guard-escape-door (Fork 2), macOS
  aggressiveness (Fork 3), canary-mandatory (seed 5), priority-sequencing (seed 4), DOM-budget (seed 6),
  advisory-tail-worth-it (the Panel-A-added 7th). Owner decision 2's "Independent of this ruling: authorize
  Ph 11 Half A now" is consistent with the corrected P0 placement, not contradicted by it.
- **DoD (§9):** per-phase + whole-initiative sections present and unchanged; this pass's fix is a label
  correction, not a scope or acceptance-test change, so no DoD line needed editing.
- **DAG (§4):** hard edges (3→1, 3→2, 8→{6,12}) and Phase 11 as shared dependency of {2,7,8,9,12,13}
  re-confirmed matching the phase texts; the ASCII diagram's Half-A box (`:989-990`) now reads "P0 band"
  consistent with §8, its pre-existing minor column-width variance (unrelated to this fix, present before
  and after) left as-is since no prior pass flagged ASCII-art alignment as a defect and doing so now would
  be a manufactured nit against the loop's own consequence standard.
- **`depends_on_claims`:** unaffected by this pass's edit (no phase's dependency list touches tier
  labels); spot-confirmed Phase 11's `[CL-7, CL-22]` still resolves correctly.
- **Dominant-defect-class sweep (proxy-keying / teeth-over-claim / fail-open / non-portable bash /
  self-reference):** no new instance found in this pass beyond the tier-label contradiction above, which
  is its own distinct class (internal cross-section inconsistency) rather than a recurrence of the five
  named classes.
- **`claims-table.md` / `problem-inventory.md`:** re-confirmed CL-1…CL-25 present (25 rows) and 21
  P-classes present — both reference docs unchanged by this pass, consistent with the scope note that G1
  artifacts are reused, not re-derived.

Verdict: **not clean** — 1 real, new issue found and fixed (a tier-label self-contradiction across 6
locations, invisible to every prior citation-keyed pass because it names no file/line/gate-number),
grounded in this-session greps of the plan and the real repo (3 citation spot-checks all confirmed exact).
Convergence count resets to **0** consecutive CLEAN passes.

## Pass 16 (opus) — exhaustive internal-consistency sweep

Pass 15 found a tier-label self-contradiction (6 prose "P1 band" mentions vs §8's P0 table). Per the
brief this class needs an EXHAUSTIVE sweep, not one-nit sampling. Checked EVERY internal cross-reference
for agreement across all 17 phases: (1) every P0/P1/P2 tier mention vs §8; (2) every "Phase N does/builds
X" claim vs the phase's Goal; (3) coverage table ↔ phases; (4) DAG edges ↔ phase deps; (5) owner-decisions
↔ phases/forks; (6) risk-matrix ↔ phases; (7) §N section pointers. **1 real internal-consistency
contradiction found (a mis-enumerated phase-set), manifest in 2 sections → 2 targeted Edits; every other
axis CLEAN.**

**Issue 14 (NEW, real — the "depends-on-Phase-11" source-scan set was enumerated inconsistently: §2
omitted Phase 7 where it belongs; M1 listed Phase 7 where it doesn't).** Every authoritative location gives
the set of phases whose SNR residual depends on Phase 11's exempt path as **{2, 7, 8, 9, 12, 13}** — the §4
DAG twice (`:995` "source-scan phases (2,7,8,9,12,13)"; `:1012` "shared dependency of every source-scan
phase (2, 7, 8, 9, 12, 13)"), §5 D6 (`:1105` "which phases actually depend on Phase 11 (2, 7, 8, 9, 12,
13)"), M1's own first sentence (names "self-heal grep (Ph 7)" among the source-scan guards needing the
exempt path), and **Phase 7's own `[SNR — small RISK]` teeth line** (`:564-567`: "the clean fix is Phase
11's exempt path"). But **two locations contradicted that set:**
  - **§2's reconciled-note enumeration (`:141`)** listed the depend-on-Phase-11 lints as "(Phases 8, 9, 12,
    13)" — **omitting Phase 7** → an implied set of {2,8,9,12,13}. This is the single outlier; it silently
    drops Phase 7 from the very list the DAG/§5/Phase-7-teeth put it in. A builder reading §2 (the teeth
    contract) would conclude Phase 7 needs no Phase-11 exempt path, directly contradicting Phase 7's own
    teeth and the DAG's shared-dependency edge. **Fix:** "prose-scanning lints (Phases 8, 9, 12, 13)" →
    "prose/source-scanning lints (Phases 7, 8, 9, 12, 13)" + a one-clause note that Ph 7/8 sit in *both* the
    no-deny-surface list and the Phase-11-dependent list (they can't deny their own fix, but their
    source-scan can false-positive on a comment/doc — exactly the residual Phase 11 clears; this matches the
    dual-listing the plan already gave Phase 8).
  - **M1's mitigation cell (`:1193`)** listed "CI readers (Ph 1/3/4/**7**/10/14/15) satisfy SNR structurally
    (no deny surface)" — **including Phase 7** among the structurally-satisfied readers, directly
    contradicting M1's *own first sentence* which names Ph 7 a source-scan guard needing the exempt path
    (and correctly EXCLUDES Ph 8 from the same parenthetical). Intra-cell self-contradiction. **Fix:** "Pure
    CI readers (Ph 1/3/4/10/14/15) satisfy SNR structurally … ; Ph 7/8 have no deny surface either but carry
    a source-scan residual, so they sit with the Phase-11-dependent set" — removing Ph 7 from the structural
    parenthetical and stating its true classification, matching M1's own treatment of Ph 8.

Both edits point the same direction (Phase 7 IS a source-scan guard depending on Phase 11, per its own
teeth) and make the set uniformly {2,7,8,9,12,13} across §2, §4 DAG (×2), §5 D6, M1, and every phase's
`[SNR]` teeth. No plan-internal line-number self-references exist (the plan cites §-anchors and real-repo
`file:line`, never its own line numbers), so the +1-line shift from these edits breaks no citation.

**Every other internal cross-reference verified CLEAN (enumerated, not sampled):**
- **P-tier labels (§8 authoritative table):** all 6 pass-15 "P0 band" fixes hold (`grep "P1 band"` → 0);
  §0's bold tags Ph1/2/3=P0, Ph4/5/6=P1 match §8; §10 decision-5's build sequence
  `{Ph 2, Ph 3, Ph 11-A}(P0) → {Ph 4, Ph 5, Ph 6, Ph 8, Ph 9, Ph 10, Ph 13}(P1) → tail(P2)` matches §8's
  three tier rows **exactly**; every phase placed in exactly one tier (11 split A/B).
- **"Phase N does X" claims:** §0's per-phase one-liners (Ph 1 closes P2/P3/P4/P6; Ph 4 generalizes Gate 51;
  Ph 6 generalizes Gate 167; etc.) all match each phase's Goal; the pass-8-blessed "Ph 4 names, does not
  build P17 (built in Ph 8)" reconciliation intact across header/§0/coverage/DAG.
- **Coverage table ↔ phases:** all 21 rows P1–P21 map to a phase whose header "closes P#" agrees, each with
  a prevention + remediation column; honest-partial flags exactly P4 (Ph 1) and P15 (Ph 12), both matching
  those phases' teeth; P17 correctly NOT flagged (pass-6 ruling).
- **DAG edges ↔ phase deps:** hard edges 3→1 (imports parse) + 3→2 (audit target), 8→{6,12} (compose) all
  match the phase acceptance-test "depends on" text; soft reuse edges (9,14 reuse Ph 1's parse; 5 shrinks 7)
  match; Phase 11 shared-dependency-of-{2,7,8,9,12,13} now consistent post-fix.
- **Owner-decisions ↔ phases:** 7 decisions each reference a real phase/fork (Fork 1→Ph 5, Fork 2→Ph 11-B,
  Fork 3→Ph 2, seed #5→Ph 6, seed #4→sequencing, seed #6→Ph 16, +advisory-tail Ph 12/13/14); M13 + DoD both
  read the owner-gated set as "(5, 6, 11-B)" consistently.
- **Risk-matrix ↔ phases:** M1–M13 all reference real phases/mechanisms (M1's Phase-7 dual-listing was the
  one defect, fixed above); M2→Ph 11-B, M4→Ph 2/3 required-workflow, M12→advisory Ph 12/13/14, etc.
- **§N pointers** all resolve (§5 Divergence, §6 Empirical, §7 risk matrix, §8 Prioritization, §10 Owner).
- **Quick-confirm (not re-litigated):** citations (pass-14 exhaustive) intact; teeth honesty (pass-6)
  intact; coverage completeness (all 21 classes) intact.

Verdict: **not clean** — 1 real internal-consistency contradiction (a phase-set mis-enumeration surviving
all 15 prior passes because they read the DAG's `{2,7,8,9,12,13}` and confirmed it, never diffing it
against §2's prose enumeration or M1's parenthetical), fixed in its 2 manifestations (§2 `:141`, M1
`:1193`); every other tier-label / phase-claim / coverage / DAG / owner-decision / risk-matrix / §-pointer
cross-reference verified consistent. Convergence count resets to **0** consecutive CLEAN passes.

## Pass 17 (sonnet) — 1 real survivor found and fixed (a Gate-51/144 pairing pass 13/14's own fix left uncorrected in a second location within the same phase)

Confirmation pass 1 of the final 3-consecutive-clean run, design-level scope only (per the brief: build-plan-level detail is out of scope for this pass). **First priority: verify pass 16's Phase-11-dep-set fix held.** It does — confirmed by direct grep of the current file: `{2,7,8,9,12,13}` is now uniform across all 5 authoritative locations (§2 `:141` "prose/source-scanning lints (Phases 7, 8, 9, 12, 13)"; §4 DAG `:995` and `:1012`; §5 D6 `:1105`; M1 `:1193`, which now correctly excludes Ph 7 from the "Pure CI readers … satisfy SNR structurally" parenthetical — `(Ph 1/3/4/10/14/15)` — and states "Ph 7/8 … sit with the Phase-11-dependent set"). No `grep -n "P1 band"` hits (pass 15's tier-label fix also holds, 0 remnants).

**Holistic re-sweep for a remaining instance of any of the 5 already-swept classes (design/teeth-honesty/path-citations/gate-number-drift/internal-consistency), spot-checked across §0, §4's DAG, §8-§10, and every phase not recently touched.** Found 1 genuine survivor, in the gate-number/`file:line`-drift class pass 13/14 already worked (the same phase, a location their fix did not reach).

**Issue 15 (real, gate-number-drift class recurring in a second location within the phase passes 13/14 already fixed once) — Phase 4's own "Classes closed + live-open remediated" line still paired Gate 51 with Gate 144 as if both were current case-by-case surface-parity precedents, directly contradicting the Goal/Teeth citations 3-4 lines above it that pass 13/14 already corrected.** Pre-fix, the Live-open sentence (`hardening-plan.md:414-416` pre-edit) read: "no generic N-surface parity gate exists (Gate 51/144 are case-by-case)." Pass 13 found and fixed 4 occurrences of a stale "Gate 144" citation in this exact phase (the Goal, the Teeth `[contract]` line, §0, and the §1 coverage-table row) after discovering the harness renumbered and Gate 144 now names something unrelated; pass 14 added a drift-note at the Goal citation warning future readers exactly this. But pass 13's fix was scoped to "4 occurrences" it enumerated by location, and this fifth location — 14 lines further down, in the same phase's "Live-open" sentence — was not one of them, so the stale pairing survived both sweeps. Verified directly this session (not trusted from the loop log): read `scripts/audit-gates.sh:5375-5399` in the real worktree — Gate 144 is unambiguously "Prompt Builder render + XSS floor (`check-prompt-builder-render.mjs`)," a static innerHTML-sink grep run independently against `$DASH_HTML` and `$IDX_HTML` for an unrelated feature (the Prompt Builder skill), not a derive-and-compare parity check and not related to `DASH_OWNER`/`navChildren`/nav-route placement at all. The "Gate 51/144" pairing is a direct carry-forward of `problem-inventory.md`'s historical citation (where, at the time of the dated incident, Gate 144 genuinely was the DASH_OWNER fix and Gate 51 separately asserted the 5-section IA contract — both legitimate then) — but the harness has since renumbered, collapsing both mechanisms onto the current Gate 51, and this line never got the same update the phase's other 4 citations already received. Consequence: a reader relying on this Live-open sentence (rather than the Goal three lines above it) would believe there are currently *two* case-by-case parity precedents worth checking, and would find Gate 144 irrelevant on inspection — a small but genuine self-contradiction inside the one phase this exact defect class has already twice required a fix in, which is itself worth flagging (a citation-drift class recurring inside the very phase two prior passes patched, because their fix was location-scoped rather than pattern-scoped). **Fix applied:** rewrote the parenthetical to name only Gate 51 as the current case-by-case precedent, state plainly that Gate 144 is NOT one (citing the direct `:5376-5377` read confirming it's the unrelated XSS floor), and name the pre-renumber inheritance from `problem-inventory.md` as the traceable cause rather than leaving the correction unexplained. Left `problem-inventory.md`'s own "Gate 144"/"Gate 51" references untouched (per scope, G1 artifacts are reused, not re-derived, and they are accurate to the dated historical record they describe — consistent with pass 13's disposition of the same question for the identical file).

**Scrutinized and found SOUND (no fix needed) — spot-checks beyond the required Phase-11-dep-set verification:**
- **§4 DAG's ASCII-art crossing lines** (Phase 6's `──┐` / Phase 7's `├──►` / the "Phase 9 / Phase 12 (provenance)" merged row `───────────────────────────┘` / Phase 8's `─┘`) visually suggest Phase 7 and Phase 9 might feed into Phase 8, which would contradict the prose bullet immediately below stating the real dependency is `Phase 8 → {Phase 6, Phase 12}` only. Judged **not a defect**: the unambiguous prose ("The genuinely hard dependencies are few … Phase 8 → {Phase 6, Phase 12} (composition)") sits directly under the diagram and is what a reader actually depends on for the dependency set; the crossing lines are a monospace box-drawing artifact of shared column positions, the same category of cosmetic ASCII-art imprecision pass 12 already declined to flag (the column-width variance) and pass 16 explicitly left alone for the same reason. Manufacturing a fix here would be a nit against the loop's own established consequence standard, not a genuine design defect.
- **Owner decisions (7):** re-read in full — each is still a genuine judgment call (a cost/uniformity trade-off, a security-review funding call, a friction-vs-safety default, a mandatory-vs-advisory ratification, a sequencing confirmation, a defer-or-build call, an advisory-tail worth-it call) with no rule that could settle it from the plan's own text; none has become rule-derivable as the plan matured.
- **DoD (§9):** per-phase (gate proof, pre-build dry-run, whole-tree lint, gate-audit meta-test, macOS run, version bumps, migration notes, docs-to-main routing, layout allow-list, owner-gated recorded deferral) and whole-initiative (4 numbered items, including the "re-run after all phases ship" closure-proof item) sections both present and internally consistent with §8's tiers and §10's owner list.
- **Coverage table (§1):** all 21 rows P1–P21 re-confirmed present with both a Prevention-phase and a Remediation-of-live-open column; P4 (Ph 1) and P15 (Ph 12) remain the only two honest-partial flags; no row over-claims a mechanism's actual scope.
- **Six-part teeth blocks:** spot-re-read Phases 1, 7, 8, 11 (the three most-edited across the loop) — all still internally consistent post-pass-16's edit (no new over-claim introduced by the phase-set fix's wording change).

Verdict: **not clean** — 1 real issue found and fixed (a gate-number-pairing citation left stale in a second location inside the exact phase two prior passes already corrected once for the identical underlying defect class), grounded in a this-session direct read of the real `scripts/audit-gates.sh:5375-5399` (not trusted from the loop log) plus a full grep-verified confirmation that pass 16's dependency-set fix and pass 15's tier-label fix both hold with zero remnants. Convergence count resets to **0** consecutive CLEAN passes — this is NOT one of the 3 confirmation passes; the streak restarts from this fix.

## Pass 18 (opus) — deterministic residual sweep — CLEAN

Not a model-sampled read: ran actual `grep -nE` over `hardening-plan.md` for each of the 5 residual
classes prior passes' spot-reads kept missing one of, cross-checked every hit against a this-session
Read of the real `scripts/audit-gates.sh`, and re-grepped to confirm 0 stale instances per pattern.
**Zero residuals found across all 5 classes — genuinely clean, no edit made (fabricating one would
violate the loop's own consequence standard).**

**Class 1 — `Gate 144` (grep `Gate 144|Gate-144`):** 3 hits, ALL the self-documenting correction note
(`:400`, `:401`, `:416`) — "shipped under Gate 144 until a harness renumber", "Gate 144 is now the
unrelated Prompt Builder XSS check at `:5377`", "**not** Gate 144 … the unrelated Prompt Builder XSS
floor". None uses Gate 144 as an active parity/derive-and-compare precedent; the active precedent is
uniformly **Gate 51**. Verified against source: `audit-gates.sh:4282` Gate 51 = "Unified portal shell
router + committed-route destinations" whose "By-destination half" re-derives from BOTH
`$DASH_HTML`/`$IDX_HTML` and asserts a `DASH_OWNER` destination removal goes red — i.e. Gate 51 genuinely
IS the derive-and-compare-over-both-surfaces mechanism the plan attributes to it (so the description is
accurate, not a stale Gate-144 description); `audit-gates.sh:5377` Gate 144 = "Prompt Builder render +
XSS floor (check-prompt-builder-render.mjs)", a static innerHTML-sink grep, unrelated. Pass 17's fix
holds; **re-grep → only the note remains. CLEAN.**

**Class 2 — every `Gate N` (grep `Gate [0-9]+`, deduped: 51×7, 167×7, 154×4, 190×3, 144×3, 32×2, 184×2,
179×2, 132×2, 6/29/20/194/16/104×1):** read the `── Gate N:` headers in the real `audit-gates.sh` for
ALL 15 distinct numbers — every one maps to the role the plan claims (51 router/DASH_OWNER `:4282`;
167 Copilot→tribunal `:600/:5820`; 154 host-support map `:470/:5514`; 190 premise-ledger blast-radius
"one agent must not gate another" `:801/:6259`; 132 DOM-budget ratchet `:406/:5192`; 32 dashboard server
endpoint parity `:3449`; 184 memory-compaction guard `:744/:6108`; 179 FORGE G3b premise gate
`:722/:6092`; 29 markdown-link resolution `:3233`; 20 Copilot bridge / adapter I/O `:178/:2129`; 6
behavioral enforce-layout `:1246`; 16 concern-catalog regexes compile `:1820`; 194 design-clone
bidirectional teeth `:871/:6406`; 144 XSS floor `:5377`; 104 historical collision example). **No drift.
CLEAN.**

**Class 3 — priority tier labels (grep `P0`/`P1`/`P2`, read §8 table `:1213-1219`):** §8 authoritative =
P0{Ph 0,1,2,3,11-A} / P1{Ph 4,5,6,8,9,10,13} / P2{Ph 7,11-B,12,14,15,16}. §0's explicit tier labels
(`:54` Ph1=P0, `:55` Ph2=P0, `:56` Ph3=P0, `:57` Ph4=P1, `:58` Ph5=P1, `:59` Ph6=P1) and the
Ph-11-Half-A→P0 promotion (`:84-85`, `:1019`, `:1217`) all match §8 exactly. The §0 residual-tail listing
(`:63-72`) is a coverage narrative, not a conflicting tier assertion (phases 7-16 carry no explicit Pn
label there). **No mismatch. CLEAN.**

**Class 4 — Phase-11 dependency set (grep the enumeration shapes):** every enumeration is the authoritative
`{2,7,8,9,12,13}` — `:141-142` ("Phase 2's portability hook" + "Phases 7, 8, 9, 12, 13"), `:792`
(`2/7/8/9/12/13`), `:999` (`(2,7,8,9,12,13)`), `:1016` (`(2, 7, 8, 9, 12, 13)`), `:1109`
(`(2, 7, 8, 9, 12, 13)`), M1 `:1197` (Ph 2/9/7/8/12/13). No `{8,9}` / `{7,8,9}` variant survives anywhere.
Pass 16/17's fix holds. **Re-grep → 0 variants. CLEAN.**

**Class 5 — path prefixes (grep bare `(hooks|skills|knowledge)/<name>.<ext>` unprefixed):** re-grep returns
NONE — every such occurrence is either plugin-prefixed (`plugins/ravenclaude-core/hooks/…`,
`plugins/**/hooks/*.sh`, `plugins/*/monitors/**`), docs-prefixed, a glob invocation-signature
(`hooks/*.sh` describing the PreToolUse-hook shape), or a scope-concept reference (`hooks/**` = "the hooks
directory scope"). No bare unprefixed file path. **CLEAN.**

**Bonus confirmation (not one of the 5, but Phase 1 leans on it):** `audit-gates.sh:877` = the `Supported:`
list, `:880` = `esac`, `:881` = `fi` — exactly the dispatcher boundary Phase 1's Goal cites; the
`Supported:` list confirms every per-gate-run number the plan references (20, 132, 144, 154, 167, 179,
184, 190, 194) is registered.

Verdict: **CLEAN** — deterministic `grep`-then-verify sweep finds **0** stale instances across all 5
residual classes; the 16 real defects fixed over passes 1-17 have converged and the named residual classes
are all already correct in the current file. No edit made this pass. This IS a clean confirmation pass;
the streak advances by one.

## Pass 19 (sonnet) — CLEAN (2 of 3)

Confirmation pass 2 of the final 3-consecutive-clean run, a different model from pass 18 (opus). Did not
trust pass 18's CLEAN verdict — independently re-ran its greps against the real `hardening-plan.md` in
this worktree and cross-checked the underlying `scripts/audit-gates.sh` content directly, then did a
design-level holistic read of sections pass 18's grep sweep does not itself read (coverage table, teeth
constraint 6's reconciled note, risk-matrix M1, prioritization table, DoD, owner decisions, DAG).

**Greps re-run (independently, not copied from pass 18's log):**
1. `grep -nE "Gate 144|Gate-144" hardening-plan.md` → 3 hits, all at `:400/:401/:416`, all inside the
   self-documenting correction note ("shipped under Gate 144 until a harness renumber… Gate 144 is now the
   unrelated Prompt Builder XSS check"). No active use of Gate 144 as a current parity precedent.
   Cross-checked the underlying claim by reading the real file directly: `scripts/audit-gates.sh:4279-4298`
   confirms Gate 51 = "Unified portal shell router + committed-route destinations" with a "By-destination
   half" that re-derives from **both** `$DASH_HTML`/`$IDX_HTML` and asserts a `DASH_OWNER` destination
   removal goes red — genuinely the derive-and-compare mechanism the plan attributes to it; `:5376-5399`
   confirms Gate 144 = "Prompt Builder render + XSS floor (`check-prompt-builder-render.mjs`)", an
   unrelated static innerHTML-sink grep. Both citations are accurate to the real repo.
2. `grep -n "P1 band"` → 0 hits; `grep -n "P0 band"` → present, and §8's own table (`:1217`) places
   "Ph 11 Half A" in the P0 row, matching the DAG's "reprioritized to the P0 band by the live evidence"
   (`:1030`). No tier-label contradiction survives.
3. Phase-11 dependency-set enumeration: `grep -nE "\{8,\s*9\}|\{7,\s*8,\s*9\}|Phases 8, 9, 12, 13"` → 0
   hits (no stale/short variant survives); the 5 authoritative locations (§2 `:141`, §4 DAG `:999`/`:1016`,
   §5 D6 `:1109`, M1 `:1197`) all read the uniform `{2,7,8,9,12,13}` — confirmed by direct read, not just
   grep-count.

**Design-level holistic read (sections pass 18's targeted grep sweep doesn't itself walk):** §1 coverage
table (21 rows, each with a prevention + remediation column, P4/P15 the only honest-partial flags) — read
in full, internally consistent; §2's reconciled note on constraint 6 (Ph 7/8 correctly dual-listed as
no-deny-surface-but-source-scan-residual) — matches M1's mitigation cell verbatim, no contradiction; §4
DAG's hard edges (3→1, 3→2, 8→{6,12}) and Phase 11's shared-dependency framing — consistent with the phase
texts; §7 risk matrix M1's mitigation cell now correctly excludes Ph 7 from the "pure CI reader" list and
states its true classification; §8's tier table (P0={0,1,2,3,11-A}, P1={4,5,6,8,9,10,13},
P2={7,11-B,12,14,15,16}) — every phase in exactly one tier, matches §0's bold tags and the DAG's Half-A
promotion; §9 DoD (per-phase + whole-initiative) and §10's 7 owner decisions — each still a genuine
judgment call, none rule-derivable, all still referencing real phases/forks. Counted directly: 21 distinct
`P#` rows in the coverage table, 7 numbered owner decisions, 25 `CL-#` rows in `claims-table.md` — all
match the plan's own stated totals. `git status --short` in the worktree is clean — no edit needed or made.

No coverage gap, teeth over-claim, proxy-key, fail-open, self-reference, or rule-derivable-owner-decision
found. No genuinely-new design-level survivor.

Verdict: **CLEAN (2 of 3)** — greps re-run independently and confirmed 0 residuals across the Gate-144,
tier-label, and Phase-11-dependency-set classes; a design-level holistic read of the coverage table, teeth
reconciled note, risk matrix, prioritization table, DoD, DAG, and owner decisions found no survivor. No
edit made this pass.

## Pass 20 (opus) — CLEAN (3 of 3 — CONVERGED)

Final independent check (do NOT trust passes 18/19). Re-derived my own highest-risk items from scratch
against the real worktree repo, ran my own deterministic grep sweep of the 5 residual classes, and did a
holistic soundness/completeness/buildability read of the whole plan. **No survivor — genuine convergence.**

**Independent re-derivations (my own picks, re-derived against the real repo, not trusted from prior passes):**
1. **`scripts/audit-gates.sh` = 6454 lines exact** (`wc -l`) — matches Phase 1's cited contract.
2. **Gate 51 vs Gate 144 content (Phase 4's most-fixed citation, survived 12 passes as a content-mismatch).**
   Read both bodies directly: `:4282` Gate 51 = "Unified portal shell router + committed-route destinations"
   and its body genuinely runs `check-committed-routes.mjs --dashboard $DASH_HTML --index $IDX_HTML` with a
   must-fail teeth half on a removed `DASH_OWNER` destination — the derive-and-compare-over-both-surfaces
   mechanism the plan attributes to it. `:5377` Gate 144 = "Prompt Builder render + XSS floor" (innerHTML-sink
   grep), unrelated to parity. Pass 13/14/17's Gate 144→51 fix + the drift-note are correct and hold. The
   injected plugin `CLAUDE.md` v0.211.0 milestone independently corroborates Gate 144 = Prompt Builder XSS.
3. **Dispatcher boundary**: `:877` Supported list, `:880` `esac`, `:881` `fi` — matches pass 14's off-by-one
   fix ("`esac` `:880` / `fi` `:881`") exactly.
4. **87/150 dual-region statistic (Phase 1 P3 keying) — reproduced with MY OWN parser** (boundary at the
   `:881` `fi`): 150 distinct gate numbers, **87 dual-region (header in both regions), 0 same-region
   full-suite collisions**. Exactly reproduces the cited "87 of 150" and confirms the P3 check must key on
   region (a collision = a same-region duplicate, of which there are 0), not on description-difference — the
   naive rule would false-positive on all 87 dual-region gates (the M5 keystone-flood the fix corrects).
5. **`host-support.json` has no `activation_gate` field** (read the file directly) — Phase 6/8's dependency
   is a real, not-yet-satisfied one; the plan is correctly unbuilt.

**My own deterministic grep sweep of the 5 residual classes (independent, not copied from pass 18/19):**
Gate 144 → only the 3 correction-note lines (`:400/:401/:416`), no active parity use; `P1 band` → 0 hits,
`P0 band` → 6 (tier-label fix holds); phase-11 dep-set short/stale variants (`{8,9}`/`{7,8,9}`/`Phases 8, 9,
12, 13`) → 0, authoritative `{2,7,8,9,12,13}` present at `:999/:1016/:1109` (+ §2 `:141` / M1 `:1197` in the
"Phases 7, 8, 9, 12, 13" prose form, Phase 7 correctly included); bare unprefixed `hooks/`/`skills/`/
`knowledge/` file-path citations → 0. All 5 classes clean.

**Holistic verdict — sound + complete + buildable for all 21 classes (prevent + remediate):**
- **Complete:** §1 coverage table maps every P1–P21 to a prevention phase AND a remediation-of-live-open;
  the two honest-partial flags (P4/Ph1, P15/Ph12) are named, not hidden; P17 correctly NOT flagged (its
  primary mechanisms — generator parity + adapter round-trip — are hard-gated machine surfaces; only the
  `docs/`-prose citation sub-scan is advisory, per the oracle-backed-vs-advisory split).
- **No mechanism recreates its own class:** the keystone (Phase 1) is built first and guards + is imported
  by every later gate ("audit the auditor before you add auditors"); the six-part teeth block's [SNR] lines
  honestly split structurally-safe CI readers from genuine deny/prose-scan RISKs that depend on Phase 11's
  exempt path. M1 leads the risk matrix with this exact meta-risk.
- **No fail-open:** [exit-2] requires literal exit 2 (not merely nonzero); Phase 3 is the dedicated
  fail-closed execution audit; advisory phases (12/13/14) honestly declare [exit-2] N/A-by-design rather
  than over-claiming — the one class of over-claim passes 4–8 chased is absent.
- **Empirically grounded prioritization:** §6's "guards false-positive on legitimate work is the
  highest-frequency live failure" is independently corroborated by the injected plugin `CLAUDE.md`
  milestones (v0.242.0 #861 srm.force-push unscoped `.*`; v0.244.0 #866 the identical sce.curl-pipe-shell
  half-fix + "nine blocks of work whose only sin was describing the thing accurately"; v0.245.0 the premise
  guard's "a guardrail whose only exit is unreachable gets tunnelled"), and by this loop's own passes 9/10/14
  each hitting the `xc.tribunal-self-disable` false-positive on their verification reads and handling it via
  the Read tool. Phase 11 Half A → P0 is earned, not asserted.

**7 owner decisions confirmed genuinely owner-only** (re-read §10): RC_BASELINE direction (cost/uniformity
trade-off), fund-the-security-review-now, macOS enforcement default/scope (friction-vs-safety), canary
mandatory-vs-advisory (policy), sequencing confirmation, DOM-budget defer, advisory-tail worth-it — each a
genuine judgment call, none rule-derivable; the one settled sub-question (a `scan_repo`-derived baseline is a
forbidden tautology) is already decided in-plan, not handed to the owner.

**[build-plan item, do NOT reset]:** Phase 1's P2 reachability heuristic ("≥1 `gate` call in the
unconditional full-suite region") is a parser-calibration property against the *current* tree — e.g. any gate
whose full-suite work is fully delegated to a sub-script would need its literal `gate "…"` line to remain
(passes 2/3 spot-checked this holds for Gate 194 and the `_skip_or_fail`-gated branches). The design already
gates this behind the M5 mandatory pre-build zero-false-positive dry-run, so it is a build-time calibration
task, not a design defect.

Verdict: **CLEAN — 3 of 3 consecutive, CONVERGED.** No genuinely-new design-level survivor. The 17 real
defects fixed across passes 1–17 have converged; my independent re-derivations (6454 lines; Gate 51/144
content; the `:877/:880/:881` boundary; 87/150 via my own parser; no `activation_gate`) and my own grep
sweep of all 5 residual classes all confirm the current file is correct. No edit made this pass.
