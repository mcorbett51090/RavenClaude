# Build-loop log — recurring-defect hardening BUILD plan

**What this is.** The per-pass log for the iterate-to-3-consecutive-clean critic loop over
`build-plan.md` (the BUILD translation of the converged 20-pass `hardening-plan.md`). Distinct from
`loop-log.md`, which is the DESIGN loop's log — do not append to that file from this loop.

---

## Pass B1 (sonnet)

Critiqued `build-plan.md` (17 PRs + 1 docs commit) against BOTH substantive and deterministic axes in
one pass, in the worktree `.claude/worktrees/forge-recurring-defects`, verifying every cited fact against
the real repo (not the design plan's prior verification — re-derived independently this pass).

**Deterministic sweep (clean).** Re-verified, this session, against the real tree:
- `scripts/audit-gates.sh` = 6454 lines exact; highest `── Gate N:` header = 194 → next-free = 195;
  150 distinct gate numbers; `Supported:` at `:877`; dispatcher close `esac :880`/`fi :881`; exit-2
  assertion template at `:1047` (`rc_is_2=0; [ "$rc" -eq 2 ] || rc_is_2=1`); `_skip_or_fail()` at `:945`;
  Gate 132 dual-region echo at `:406`/`:5192` — all match the plan's §0 contract table exactly.
- Gate headers cited across the plan: Gate 51 `:4282`, Gate 144 `:5377`, Gate 154 `:5514`, Gate 167
  `:5820`, Gate 179 `:6092`, Gate 190 `:801`(dispatcher)/`:6259`(full-suite), Gate 34 (claim-grounding,
  confirming PR 9's "extends the existing gate" claim) — all confirmed at the cited line.
- New gate numbers 195–210: each appears in exactly its own PR section (197 legitimately 3× — all
  within PR 2's own text), no cross-PR collision, no collision with any existing gate number (max 194).
- Every file the plan calls "new" (`check-gate-registration.py`, `check-regex-catalog-compiles.py`,
  `enforce-portability.sh`, `check-hook-failclosed.sh`, `check-verdict-default-nonpermissive.py`,
  `check-surface-parity.py`, `check-trigger-scoping-consistency.py`,
  `subagent-safe-guard-checklist.md`, `check-host-capability-citations.py`,
  `check-selfheal-push-safety.py`, `check-self-certifying-change.py`) is confirmed genuinely absent;
  every file it cites as existing (`_portable.sh`, `guard-premise.sh`, `hooks.json`,
  `route-decision-review.sh`, `thing-orchestrator.sh`, `runaway-brake.sh`, `claim-grounding-lint.sh`,
  `check-frontmatter.py`, `check-dashboard-server-parity.py`, `check-host-support.py`,
  `check-marketplace-claims.py`, `check-plugin-detail-render.mjs`, both `ci-gate-audit.md` /
  `validating-a-measuring-instrument.md` docs) is confirmed present. `.repo-layout.json` globs, both
  `serve-dashboards.py` twins, `RC_BASELINE` at `check-plugin-detail-render.mjs:54`, `host-support.json`
  (no `activation_gate` field yet — correctly unbuilt), `ravenclaude-core` version 0.253.0 in both
  mirrors, `validate-macos.yml` `runs-on: macos-latest`/paths-filtered/non-required, and
  `validate-marketplace.yml`'s prettier step at exactly `:305` — all confirmed.
- Phase/PR/P-class cross-references: every `Ph N`/`Phase N` in build-plan.md resolves to a real
  hardening-plan.md phase (0–16, incl. Half A/B on 11); every `P#` (P0–P21 incl. tier labels) resolves;
  the coverage table lists all 21 classes with prevention + remediation PRs.

**Substantive issues found + fixed (2):**

1. **[Buildability / P8-shaped self-repro, PR 2]** The plan's nested-worktree exemption fix for
   `guard-premise.sh` named "the exemption" as a single location. Read (not sed, per the anti-tunnel
   note — `xc.tribunal-self-disable` denied two direct `sed`/`grep` reads of `guard-premise.sh` this
   pass, reproducing the plan's own incident (d)) confirmed the fragile `path.replace(proj,
   "").lstrip("/")` idiom that causes the bug exists at **two independent call sites**: T-PROSE's
   durable-artifact exemption (`rel_p` at `:280`, gating `:283`) and T-SHAPE's prefix-exemption list
   (`rel` at `:405`, gating `:407`). Patching only one would leave the guard half-fixed — exactly the
   "fix-one-instance-and-stop" class (P8) this same design elsewhere warns against, reproduced inside
   its own remedy. **Fix applied:** PR 2's Files bullet now names both call sites explicitly and states
   why both must be patched; Gate 197's must-fail→must-PASS (nested-worktree) acceptance test now
   asserts through **both** trigger paths (a T-PROSE-shaped diagnosis write and a T-SHAPE-shaped
   new-module write, both under `.ravenclaude/runs/**` in a nested worktree) so a fix applied to only
   one call site is caught, not silently accepted.

2. **[Remediation concreteness, PR 3]** PR 3's packaging-move remediation item (c) cited a "6-call-site
   move" for relocating `premise-gate.py`/`classify_claim.py`/`check-design-schema.py`. Traced the
   figure to `hardening-plan.md:315`, where "6 call sites" was derived for the **first two** scripts
   only — `check-design-schema.py` is a v0.253.0 addition folded into the same PR without re-deriving
   the count. Grepping the real tree found additional shipped, operational-surface citations beyond the
   originally-counted forge-pipeline/SKILL.md pair: `forge-pipeline/reference/premise-gate.md:40`
   (`classify_claim.py`), `design-clone/SKILL.md:22` and `brand-extraction/SKILL.md:67`
   (`check-design-schema.py`) — so "6" undercounts the three-script scope. Separately found that
   `scripts/check-shipped-references-resolve.py` (**Gate 187**, header confirmed at `:748`) **already**
   carries a `_DEFERRED_PACKAGING` ignore-list holding exactly these three basenames, with its own
   in-file comment ("REMOVE these two [now three] entries when that move lands — the gate then keeps
   them honest") — i.e. a concrete, existing, fail-closed enumeration mechanism was sitting unused by
   the plan. **Fix applied:** PR 3's remediation item (c) now specifies the move as (1) relocate the
   three files, (2) remove all three basenames from `_DEFERRED_PACKAGING`, (3) run Gate 187 — which
   itself enumerates every remaining bare-reference citation and fails loudly on any miss — replacing
   the stale hand-counted "6" with a self-verifying mechanism instead of a completion criterion nobody
   would re-derive. Mirrored the correction into the coverage table's P1 remediation cell.

**Anti-tunnel discipline observed this pass:** two direct `sed -n`/`grep` read commands against
`plugins/ravenclaude-core/hooks/guard-premise.sh` were DENIED by `xc.tribunal-self-disable` — a live,
this-pass reproduction of the plan's own documented incident (c)/(d). Handled per the sanctioned path:
switched to the `Read` tool for both, recorded here, no tool-switch-to-tunnel and no reworded command
retry attempted against the same guard.

**Substantive axes reviewed, no further issues found this pass:** buildability of all 17 PRs (each names
exact files, a gate spec, must-fail fixtures, acceptance tests); the six-part teeth block present and
honestly scoped (structurally-satisfied SNR vs genuine-RISK correctly distinguished) on every proposed
gate; macOS-portability of every proposed script (Python 3.9 stdlib + `from __future__ import
annotations`, or bash 3.2-safe reuse of `_portable.sh`); owner-gating (4 hard-gated PRs — 3/10/12/17 —
correctly scoped to only the judgment-call half of their PR, none over-gates the mechanism build itself;
PR 16/seed#6 and PR 8-9-14/decision#7 correctly soft-flagged rather than hard-blocked, matching the P2
"residual tail / owner-optional" tier); sequencing/DAG (PR 1 correctly first; PR 4's hard dependency on
{PR 1, PR 3} and PR 11's on {PR 9, PR 10} both stated and consistent with the DAG diagram; PR 3/PR 4
correctly target the already-required whole-tree `validate-marketplace.yml` as a **step**, never a new
`paths:`-filtered required workflow — the hang trap named in AGENTS.md is avoided).

**Issues count: 2 substantive (both fixed). 0 deterministic-sweep failures.**

**Verdict: NOT CLEAN (2 of 3 needed) — issues found and fixed this pass.**

---

## Pass B2 (opus)

Critiqued the post-B1 `build-plan.md` HARD on the seven SUBSTANTIVE axes (deterministic tail treated as
already-clean per the loop hand-off), verifying every load-bearing citation against the REAL repo in the
worktree — not against the plan's own prior verification.

**B1's two fixes — VERIFIED SOUND + COMPLETE (both re-derived independently this pass):**

1. **Guard-premise two-call-site fix (PR 2).** Read (not grep — anti-tunnel) `guard-premise.sh` directly:
   `:280` `rel_p = path.replace(proj, "").lstrip("/")` gates the `.ravenclaude/` durable-artifact check at
   `:283` (T-PROSE); `:405` `rel = path.replace(proj, "").lstrip("/")` gates the
   `.ravenclaude/`/`docs/`/`.claude/` prefix-exempt check at `:407` (T-SHAPE). **Two genuinely independent
   call sites, identical fragile idiom** — B1's "fix both, catch a one-site fix in Gate 197" is correct and
   complete. `:111 if d.get("tool_name") != "Write":` confirms the Write-only matcher scope B1 resolved.
2. **Packaging figure → Gate 187 mechanism (PR 3).** `check-shipped-references-resolve.py:91-101`
   `_DEFERRED_PACKAGING` holds all THREE basenames (`premise-gate.py` `:92`, `classify_claim.py` `:93`,
   `check-design-schema.py` `:100`) with the in-file "REMOVE these … when that move lands" comment; Gate 187
   is dual-region (`:749` dispatcher / `:6153` full-suite). B1's three additional citations are REAL:
   `classify_claim.py` @ `forge-pipeline/reference/premise-gate.md:40`; `check-design-schema.py` @
   `design-clone/SKILL.md:22` (cited `../../../../scripts/…` — non-resolving in a consumer, confirming the
   defect) and `brand-extraction/SKILL.md:67` (bare `scripts/…`). B1's "stale-6 → Gate-187-clean-exit DoD"
   replacement is sound. Max gate = 194 → next-free 195 confirmed.

**Substantive issues found + fixed this pass (3, one conceptual defect fixed in two places for PR 2):**

1. **[Meta-risk R4 / axis 7, PR 4] PR 4 depended on an artifact PR 1 does not produce.** PR 4 read
   "Depends on PR 1 (imports the `hooks.json` machine-read / hook enumeration)" — but PR 1's deliverables
   (`check-gate-registration.py` + `check-regex-catalog-compiles.py`) parse `audit-gates.sh` + regex
   catalogs, **never `hooks.json`**. PR 1 (its own text, `:113`) names its shared export as the
   "`audit-gates.sh`-parse," and PR 1's Gate 195 exit-2 sub-check (`:145`) has hook-detection flowing
   **PR 4 → PR 1** ("Import PR 4's hook-detection when it lands"), the reverse of the claimed import. A
   builder following PR 4 literally would hunt for a nonexistent `hooks.json` reader in PR 1 → the exact
   build-to-guessed-contract (R4/P15) class this initiative exists to kill, reproduced in the plan's own
   DAG. **Fix:** rewrote PR 4's dependency clause — imports PR 1's `audit-gates.sh` parse; the `hooks.json`
   enumeration that drives every hook is PR 4's OWN read, not a PR 1 export — with a design-note that
   `hardening-plan.md` Phase 3's mirror phrasing ("reuses Phase 1's machine-read of `hooks.json`") is the
   same root imprecision (Phase 1 reads no `hooks.json`).

2. **[Design-fidelity + owner-gating, axes 3 & 4, PR 2] PR 2 claimed PR 17's owner-gated SNR-exempt-door
   role.** (a) PR 2's SNR line (`:244`) read "this IS the self-non-recursion fix Phases 2/7/8/9/12/13 depend
   on for their residual" — a **direct internal contradiction** with PR 17 (`:848-849`), which claims the
   identical role, and with the design (hardening-plan §2), which assigns the SNR-residual retirement of the
   source-scan family (Phase 2/7/8/9/12/13 → PR 3/13/11/6/9/8) to **Phase 11 Half B = PR 17** (owner-gated,
   Fork 2, red-team) — NOT to Phase 11 Half A (PR 2). (b) PR 2's Files bullet (`:217`) "give it a reachable
   sanctioned escape" was owner-gating-dangerous: a builder could read it as "build the widened
   exempt-path/sentinel door now," which is exactly PR 17's red-team-gated deliverable. Read
   `guard-premise.sh:296-397` and confirmed the T-PROSE screen **already** carries a narrow sanctioned
   escape (`_CTRL` in-block `premise-ok:`/`control:` marker `:338`, `RC_PREMISE_CONTROL`, and the
   `control.md` file `rc_load_control` `:390`, v0.245.0). **Fix (two edits):** SNR line now states PR 2 is a
   deny-hook edit covered by that *existing* escape and is explicitly **not** the door PR 17 owns; the Files
   bullet now says "honor the *existing* escape on the Edit/MultiEdit path — NOT the widened door, which is
   PR 17's owner-gated deliverable." This closes the risk of a non-gated PR pre-empting Fork 2's red-team.

**Noted, NOT edited (lower-severity bookkeeping, owner-gating envelope preserved):** the DAG (`:912`) and
PR 17 (`:878`) enumerate the source-scan PRs retiring their SNR residual as "(2/6/8/9/13)", which diverges
from the design's phase-derived set {PR3, PR6, PR8, PR9, PR11, PR13} (it drops PR 3-portability and
PR 11-host-capability and adds PR 2). Each source-scan PR's OWN text correctly points to PR 17's exempt
path (PR 3 `:309`, PR 6 `:471` verified), so no build defect results; left for a bookkeeping reconcile to
the design's phase list rather than editing the fuzzy membership myself and risking a new error.

**Axes reviewed, no further substantive issues:** buildability (each PR names exact files + a six-part-teeth
gate spec); the six-part teeth honestly scoped per gate (genuine-deny vs structurally-satisfied-SNR vs
advisory-N/A-by-design correctly distinguished; no advisory gate mislabeled as exit-2-bearing and vice
versa); owner-gating (4 hard/soft gates — PR 3/10/12/17 — correctly scoped to the judgment-call half; after
the PR-2 fix, no non-gated PR pre-empts an owner call, and no over-gating); sequencing/DAG (keystone PR 1
first; gate numbers 195-210 provisional + re-derived-per-PR + keystone-catches-collision — the correct P3
handling; required-check `paths:`-hang trap avoided — new gates go into `audit-gates.sh`/`validate-macos.yml`
as STEPS, no new required workflow); remediation completeness (every problem-inventory live-open maps to a
concrete PR; the two honest-partials P4/P15 + two named-not-built residuals stated as scope limits, not
dropped); meta-risk (PR 12 forbids the scan_repo tautology; PR 13 is honestly a proxy-scan paired-with-the-
ruleset; no PR recreates fail-open / proxy-key / non-portable / self-referential / guessed-contract).

**Issues count: 3 substantive (all fixed). 1 noted-not-edited. B1's 2 fixes verified sound.**

**Verdict: NOT CLEAN (resets the consecutive-clean counter) — real substantive issues found + fixed this pass.**

---

## Pass B3 (sonnet)

Closed the internal-consistency class B2 noted-but-did-not-edit, EXHAUSTIVELY (grepped every
`(N/N/.../N)`-shaped and `PR N/N/.../N`-shaped enumeration in `build-plan.md`, not just B2's flagged
instance), re-verified B2's 3 fixes against the real `guard-premise.sh` in the worktree, and swept for
residual substantive issues.

**Task 1 — internal-consistency sweep (4 divergences found + fixed, all in `build-plan.md`):**

1. **[B2's noted divergence, now closed]** PR 17's DoD (`:892`, was) and the DAG (`:926`, was) both
   enumerated the source-scan PRs retiring their SNR residual via PR 17 as `(2/6/8/9/13)` — wrong on
   two counts: it dropped **PR 3** (portability, Phase 2) and **PR 11** (host-capability, Phase 8), and
   it wrongly included **PR 2**, which PR 2's own SNR line (fixed in B2) explicitly says is NOT that
   door. The authoritative set, per the design's §2 reconciled note (`hardening-plan.md` Phase set
   {2,7,8,9,12,13}) translated via the coverage table (Ph2→PR3, Ph7→PR13, Ph8→PR11, Ph9→PR6, Ph12→PR9,
   Ph13→PR8) = **{3,6,8,9,11,13}** — already stated correctly at `:251` (B2's own fix) but never
   propagated to these two other occurrences. Fixed both to `(3/6/8/9/11/13)` and added an explicit
   "NOT PR 2" callout at each site pointing back to PR 2's SNR line, so the three occurrences (`:251`,
   `:893`, `:928`) now agree.
2. **[New] Checklist item 7's "pure CI reader" SNR list was itself wrong, and self-contradicted PR13's
   own section.** Read `PR 1/4/5/7/13/14/15/16 satisfies SNR structurally … needs only step-3's N/A
   note" — but PR13 (Phase 7, self-heal push-safety) carries an explicit `**SNR — small RISK M1**` in
   its own Gate build spec (`the clean fix is PR 17`), directly contradicting "needs only step-3's N/A
   note." Meanwhile PR10 (Phase 6, behavioral canary), which IS genuinely tagged `structurally
   satisfied` in its own section, was missing from the list. Cross-checked every PR's own `**SNR:**`
   line (2-17) against the design's per-phase Teeth tags: true structurally-satisfied set =
   {1,4,5,7,10,14}; RISK-carrying (needs PR 17) = {3,6,8,9,11,13} — matching fix #1's set exactly, which
   is the cross-check that this fix is right. Rewrote item 7 to split the two categories explicitly and
   warn against the "no PreToolUse deny surface" ≠ "no SNR risk" confusion the design's §2 note names.
3. **[New] Ambiguous "(P8 dep)" notation in the §1 PR-sequence table (row 9, Tier column).** Read as
   "class P8" (every other cell in the same row uses that exact `P#` notation for a problem-inventory
   class) but actually meant "PR 11 / Phase 8 depends on this" (per PR 9's own header text: "built early
   because PR 11 composes it"). P8 the class (fix-one-instance/unscoped-regex) has nothing to do with
   PR 9 (contract-provenance, P15). Fixed to `(PR 11/Ph 8 dep)`.

**Verified NO divergence (checked, left alone):** the top-level Coverage table (both build-plan.md's
PR-numbered version and hardening-plan.md's Phase-numbered version) — every P1-P21 row's
prevention/remediation cross-refs resolve and match design phase→PR translation; every PR-header
`(Phase N)` tag matches its own `**Delivers:**` P#-set against the design's per-phase closes-list;
gate numbers 195-210 — each appears only within its own PR's line range (grepped, zero cross-PR
collisions); the Tier (P0/P1/P2) column matches design §8's Prioritization table for all 17 rows +
docs commit; the 4 owner-gated PRs (3/10/12/17) are named identically across the §1 table, each PR's
own header, the DAG, and the "Owner-gated PRs" table; version-bump enumeration (`:1057-1058`) — PR15's
absence from both the bump and no-bump lists is NOT a bug, it's covered by the same sentence's trailing
"docs (Ph 0/15) commit straight to main" carve-out.

**Task 2 — B2's 3 fixes re-verified against the real repo (all sound, all still current):**

- **Guard-premise two-call-site fix (PR 2).** Read (not grep — anti-tunnel; a `sed -n`/`grep` read of
  this exact file was DENIED by `xc.tribunal-self-disable` mid-pass, a fresh 5th reproduction of the
  plan's own incident (c)/(d) — handled via the `Read` tool, no tunnel, recorded here) confirmed both
  citations exactly: `:280` `rel_p = path.replace(proj, "").lstrip("/")` gates the `.ravenclaude/`
  durable-artifact check at `:283` (T-PROSE); `:405` `rel = path.replace(proj, "").lstrip("/")` gates
  the `.ravenclaude/`/`docs/`/`.claude/` prefix-exempt check at `:407` (T-SHAPE); `:111`
  `if d.get("tool_name") != "Write":` confirmed. Also confirmed the `_CTRL` escape (`:338`) and
  `rc_load_control`/`control.md` (`:390`) B2 cited for PR 2's "honor the existing escape" fix are real.
  **One important disambiguation found while verifying:** the shipped v0.245.0 CLAUDE.md milestone
  ("A guardrail whose only exit is unreachable gets tunnelled") already scoped a DIFFERENT ledger (the
  premise-probe control ledger keyed by `(CLAUDE_PROJECT_DIR, session_id)`) to the worktree — that is a
  separate bug in the same file, already fixed. It does NOT touch the `path.replace(proj, "")` idiom at
  `:280`/`:405` that PR 2 targets — confirmed by direct read that idiom is still live, unfixed, in the
  current tree. B1/B2/PR 2's target bug is real and current, not superseded.
- **Packaging figure → Gate 187 mechanism (PR 3).** Not re-derived this pass (B2 already re-derived it
  independently from B1; no new information surfaced that would change it); no contradiction found
  during the broader sweep.

**Task 3 — substantive residual sweep (light-touch, given B1+B2's depth):** no new six-part-teeth
failure, dropped mechanism, or owner-gating defect found. The only residuals are the ones already named
honestly in-plan (P4/P15 partials, the two named-not-built residuals, PR15's docs-straight-to-main
carve-out) — none silently dropped.

**Issues count: 4 (all internal-consistency divergences, all fixed). 0 substantive-residual issues.
B2's 3 fixes verified sound + current against the real repo (0 drift, 1 disambiguation from unrelated
shipped work noted).**

**Verdict: NOT CLEAN (resets the consecutive-clean counter) — real issues found + fixed this pass.**

---

## Pass B4 (opus) — CLEAN (1 of 3)

Independent confirmation, opus lens — did NOT trust prior passes; re-derived every load-bearing fact
against the REAL repo in the worktree. Anti-tunnel honored: read `guard-premise.sh` via the `Read`
tool (not grep/sed), which `xc.tribunal-self-disable` denies for that file.

**B3's 4 consistency fixes — VERIFIED HELD + correct against the design:**
- **Fix #1 (SNR-set uniform).** `(3/6/8/9/11/13)` at `:892` (PR 17 DoD) and `:927` (DAG), each with
  its "**not** PR 2" callout (`:893`, `:928`); PR 2's own SNR line `:251-253` states the same set in
  the phase-list form (Phase 2/7/8/9/12/13 → PR 3/13/11/6/9/8 = {3,6,8,9,11,13}). Zero stray
  `(2/6/8/9/13)` remaining (grep clean). The three notations agree.
- **Fix #2 (checklist item 7).** Structurally-satisfied `{1,4,5,7,10,14}` (`:999-1001`) vs RISK-carrying
  `{3,6,8,9,11,13}` (deny hook PR 3 + prose/source-scan lints PR 6/8/9/11/13). Cross-checks fix #1's
  set exactly — the internal-consistency proof B3 cited — and all 17 PRs partition cleanly
  (RISK 6 + structural 6 + n/a {12,15,16} + PR 2 special-case + PR 17 = the fix itself).
- **Fix #3 (row-9 notation).** `(PR 11/Ph 8 dep)` at `:72` — no longer readable as the P8 class.

**3 independent re-derivations (against the real tree):**
1. **Gate numbers (P3 keystone contract).** `audit-gates.sh` = 6454 lines; highest `── Gate N:` = **194**
   → next-free **195** ✓; **150** distinct numbers ✓; `Supported:` `:877` ends `…193, 194.` ✓; dispatcher
   close `esac :880`/`fi :881` ✓. Provisional 195-210 collide with nothing (max is 194). **90** numbers
   echo their header ≥2× — corroborates the design's ~87-dual-region calibration, so PR 1's
   key-on-region (not on description-difference) anti-flood rationale is sound.
2. **PR 2 guard-premise target — real + current, NOT superseded.** `:111` `if d.get("tool_name") !=
   "Write":` (Write-only matcher) ✓; the fragile `path.replace(proj, "").lstrip("/")` idiom exists at
   BOTH `:280` (feeds the `.ravenclaude/` durable-artifact check `:283`, T-PROSE) and `:405` (feeds the
   `.ravenclaude/`/`docs/`/`.claude/` prefix-exempt check `:407`, T-SHAPE) — the two-call-site fix is
   genuine. Distinct from the v0.245.0 worktree-scoping fix (that scoped the LEDGER key at
   `guard-premise.sh:246`/`log-probe.sh:162`); the `:280`/`:405` exemption idiom is still live/unfixed.
3. **PR 3 packaging move — mechanism real, move genuinely unbuilt.** Gate 187 dual-region (`:748`
   dispatcher `187)` arm — the plan's cited "`:748` header" is the case-label, echo on `:749`, a
   defensible pointer; `:6153` full-suite); `check-shipped-references-resolve.py:87-101` `_DEFERRED_PACKAGING`
   holds all three basenames (`premise-gate.py:92`, `classify_claim.py:93`, `check-design-schema.py:100`)
   with the "REMOVE … when that packaging move lands" comment. All three scripts confirmed at
   marketplace-root `scripts/`, absent from `plugins/ravenclaude-core/scripts/` — the move is real and
   pending, and the DoD (Gate 187 clean exit after the ignore-list edit) is a genuine mechanism.

**Bonus contract checks:** PR 10 precondition holds — `host-support.json` present with **no**
`activation_gate` field yet (Gate 154 pins it, `:5514`). PR 5 contract holds — Gate 51 IS the portal
derive-and-compare at `:4282`; Gate 144 IS the unrelated Prompt Builder XSS floor at `:5377` (the plan's
"verify the number, Gate 144 is now unrelated" caveat is correct).

**Holistic build-readiness — PASS.** Every PR carries files (all under already-allowed globs) + gate
spec + must-fail fixture(s) + acceptance test(s) + DoD. Keystone-first sequencing sound (PR 1 first; its
`audit-gates.sh` parse imported not re-derived by PR 4/6/14 — avoids recreating R2 inside the plan). The
4 owner-gated PRs (3/10/12/17) each gate only the judgment-call half (Fork 3 → config default only, PR 3
mechanism builds regardless; seed #5 → mandatory-vs-advisory, PR 10 mechanism builds; Fork 1 → the DROP
build; Fork 2 → the whole of PR 17 behind a red-team). Every P1-P21 has prevention + remediation; the two
honest partials (P4/P15) + two named-not-built residuals are stated as scope limits, not dropped. DAG
deps consistent (PR 4→{1,3}; PR 11→{9,10}; PR 12→Fork 1; PR 17→Fork 2). New gates land as STEPS in
`audit-gates.sh`/`validate-macos.yml`, never a new `paths:`-filtered required workflow — the AGENTS.md
hang trap avoided.

**Meta-risk — no PR recreates a root cause.** Fail-open: PR 4 audits for it, PR 13 honestly bounded as a
proxy-scan paired-with-the-ruleset (not a replacement). Non-portable: every script bash-3.2 / Py-3.9-stdlib
+ `from __future__ import annotations`; PR 3's own lint must not open a door. Self-ref: PR 1's parse
imported not duplicated; source-scan PRs carry `# noport`/exempt-path mitigation + PR 17's durable door.
Guessed-contract: every spec built to a this-session `file:line`; B2 already fixed the one PR-4→PR-1
artifact-dependency inversion; PR 12 forbids the `scan_repo` tautology. Proxy-key: N/A.

**One benign observation (NOT an issue, counter not reset):** build-plan cites Gate 187 at `:748` (the
`187)` dispatcher case-label) while the header echo is `:749` — within case-label-vs-echo ambiguity, and
the load-bearing reference (`_DEFERRED_PACKAGING` at `:91-101`, all three basenames) is exactly correct.
No material defect; the packaging-move DoD does not rest on the header line number.

**Issues count: 0. B3's 4 fixes held + correct. 3 independent re-derivations + 4 bonus contract checks
all green. The plan is executable PR-by-PR.**

**Verdict: CLEAN (1 of 3) — genuine clean confirmed independently, no fabricated issue, no rubber-stamp.**

---

## Pass B5 (sonnet) — CLEAN (2 of 3)

Independent confirmation, sonnet lens, did NOT trust B4 — re-derived every load-bearing fact against the
REAL repo in this worktree (not against B1-B4's citations). Anti-tunnel honored: read `guard-premise.sh`
via the `Read` tool only (no grep/sed attempted against it this pass).

**Deterministic greps re-run (2+, against the live tree):**
1. **Gate-number collision check.** `wc -l scripts/audit-gates.sh` = 6454; highest `── Gate N:` = **194**;
   150 distinct numbers; `Supported:` `:877` ends `…193, 194.`; dispatcher close `esac :880`/`fi :881` —
   all match build-plan §0 exactly. New gates 195-210 each grepped: every one appears **only within its
   own PR's line range** in build-plan.md (zero cross-PR bleed, zero collision with the existing max-194
   set) — re-verified independently, not copied from B1's table.
2. **SNR-set uniformity.** `(3/6/8/9/11/13)` appears at both PR 17's DoD and the DAG, each with its "not
   PR 2" callout; grep for the old wrong `(2/6/8/9/13)` returns zero hits (B3's fix holds). PR 2's own SNR
   line states the same set in phase-list form. Checklist item 7's structurally-satisfied set
   `{1,4,5,7,10,14}` also re-confirmed present.

**Design-fidelity checks (5 PRs against their hardening-plan.md phase, not the requested 2-3 — went
wider given the size of the plan):** PR 1/Phase 1 (keystone meta-gate — reachability/uniqueness/exit-2/
regex-compile/UNWIRED-partial all present in both, same honest P4 scoping), PR 5/Phase 4 (surface-parity
— the P17 host-scope-sentence forward-reference correctly named-not-built in both, pointing at Phase 8/
PR 11), PR 11/Phase 8 (host-capability lint — the oracle-backed-exit-2-vs-advisory-docs-prose split is
identical in both), PR 12/Phase 5 (count-SSOT DROP — Fork 1 gate, negative-assertion design, RC_BASELINE
de-hardcode all match), PR 2+17/Phase 11 (Half A/Half B split, the two exemption bugs, the `xc.tribunal-
self-disable` read/mutate discriminator, the owner-gated Fork 2 red-team requirement — all match). No
phase→PR fidelity drift found in any of the five.

**Independent re-derivations against the real repo (beyond B1-B4's citations):**
- Gate headers: 51 `:4282` ✓, 144 dispatcher `:615`/full-suite `:5377` ✓, 154 full-suite `:5514` ✓, 167
  dispatcher `:600`/full-suite `:5820` ✓, 187 dispatcher `748)`-label/echo `:749` ✓ (B4's benign-observation
  characterization re-confirmed — `748` is the case label, `749` the echo, exactly as B4 described), 179
  dispatcher `:722`/full-suite `:6092` ✓, 190 dispatcher `:801`/full-suite `:6259` ✓, 32 `:3449` ✓, 16
  `:1820` ✓ — 9 gate citations checked, all exact.
- `guard-premise.sh` (Read tool only): `:111` `if d.get("tool_name") != "Write":` ✓; the fragile
  `path.replace(proj, "").lstrip("/")` idiom independently confirmed at BOTH `:280` (feeds the
  `.ravenclaude/` durable check `:283`) and `:405` (feeds the prefix-exempt check `:407`) — genuinely two
  call sites, PR 2's two-site fix is not overclaiming. `_CTRL` escape `:338`, `rc_load_control()` call
  `:390` — both confirmed real and exactly where PR 2 cites them, even though this file has grown to 624
  lines (v0.245.0's file-based-control mechanism) since the design was authored — the two target lines are
  untouched by that later work, so PR 2's target bug is current, not superseded (re-confirming B3's own
  disambiguation finding, independently).
- `check-marketplace-claims.py` (git-modified 2026-08-12, before build-plan.md's 2026-08-13 mtime): read
  the full function list and `collect_counts()`/`check_count_drift_family()` bodies. Confirmed the "2 of 6"
  claim is STILL accurate on the current tree: the per-plugin description-claim check
  (`first_skill_claim`/`first_agent_claim`) covers only skills + agents; `actual_core_hook_count`/
  `actual_core_rule_count` feed a DIFFERENT check (`ravenclaude-core`'s own README table, not a per-plugin
  templates/commands/hooks/rules claim) — so templates/commands/hooks/rules are genuinely unchecked
  per-plugin, exactly as PR 12 states. This function-list looked, at first read, like it might already
  cover 5 of 6 (five `actual_*_count` functions exist) — worth flagging as a place a less careful pass
  could mis-conclude the plan's "2/6" claim is stale; it is not.
- `regenerate-artifacts.yml` (last touched 2026-08-12, before build-plan.md's mtime): PR 13's citations
  `:367-369` (direct-push-rejected comment), `:372`/`:386` (create-pull-request + branch name), `:416-424`
  (the merge-once-checks-pass step) — all exact against the current 459-line file.
- `host-support.json`: no `activation_gate` field (grep clean) — PR 10's "correctly unbuilt" claim holds.
  `RC_BASELINE` at `check-plugin-detail-render.mjs:54` ✓. `claim-grounding-lint.sh` referenced in
  `audit-gates.sh:3594` — PR 9's "extends the existing gate" claim has a real target to extend.

**New cross-check this pass (not explicitly re-run by B1-B4 as stated): version-bump enumeration vs. each
PR's own DoD line.** Read every one of the 17 PRs' own "Version bump" / "No version bump" DoD sentence and
partitioned them: bump = {2,3,7,8,9,10,12,16,17} (9), no-bump = {1,4,5,6,13,14} (6), conditional =
{11} (1), docs-carve-out = {15} (1) — 9+6+1+1 = 17, and this partition matches the Whole-initiative DoD's
own summary list (`:1057-1058`) exactly, PR-by-PR. No mismatch.

**Implementation-lens (sonnet-favored angle) — no findings:** every proposed script's macOS-portability
claim (bash-3.2-safe / Python-3.9-stdlib / `env -i PATH=/usr/bin:/bin` / no PyYAML-dependent parsing) is
consistent with this repo's own established idioms for the same problem shape (verified against the
shipped `_portable.sh` precedent and the git-protocol hook's "minimal scalar sed idiom, no PyYAML" note).
No fixture description found that would fail to actually trigger its stated must-fail condition. No
"appears in suite by name" claim found unsupported — PR 9's "extends the existing gate" and PR 11's
"extend Gate 154" both have real, grep-confirmed targets to extend.

**One benign observation (NOT an issue, counter not reset — same class as B4's Gate-187 line-pointer
note):** Checklist item 7 (`:1000`) groups PR 15 with PR 12/16 as "differently-`n/a`-tagged," but PR 15's
own section (`:816-833`) carries no literal `**SNR:**` line anywhere (grep-confirmed zero hits), unlike
PR 12 (`**SNR:** n/a` at `:727`) and PR 16 (`**SNR:** n/a.` at `:852`) which do. The underlying substance
is correct — PR 15 adds no new gate at all ("Gate build spec: none new"), so there is no source-scan
surface for an SNR tag to apply to, and its prose ("honestly not machine-gated beyond the cross-link")
conveys the same conclusion the missing tag would. A builder following checklist item 7's instruction to
"confirm... present up front" for PR 15 would find no formal tag but would immediately see why (no gate to
tag) upon reading PR 15's own two-paragraph section. No build-behavior consequence, no wrong SNR
classification, nothing an engineer would build differently. Left un-edited per the B4 precedent for a
citation-level nit with no material defect, rather than manufacturing a counter-reset over a non-issue.

**Coverage / owner-gated / DAG / DoD — confirmed:** all 21 classes (P1-P21) have both a prevention PR and
a remediation-of-live-open PR in the Coverage table, cross-checked against the §1 PR-sequence table's own
Classes column (P5's PR1-contribution is documented inside PR1's Gate 195 spec body — "Exit-2 specificity
(P5 shared clause)" — even though PR1's top "Delivers:" line and the §1 table's Classes column omit it,
mirroring hardening-plan.md Phase 1's own header-parenthetical-vs-closes-list asymmetry; not a build
defect, just an unsurfaced-in-the-summary-line completeness gap identical in shape to the source design).
4 owner-gated PRs (3/10/12/17) named identically across the §1 table, the Owner-gated-PRs table, and each
PR's own header. DAG's stated hard dependencies (PR4→{1,3}; PR11→{9,10}; PR12→Fork1; PR17→Fork2) match
each PR's own "Depends on" prose. Whole-initiative DoD's 4 items are all satisfiable by the PR set as
specified.

**Issues count: 0. Genuinely re-derived independently — no B1-B4 finding taken on faith, several citations
re-checked against a real tree that had continued to evolve (guard-premise.sh grew to 624 lines,
check-marketplace-claims.py and regenerate-artifacts.yml were both touched 2026-08-12) without drifting
any of the plan's load-bearing claims.**

**Verdict: CLEAN (2 of 3) — genuine clean confirmed independently, no fabricated issue, no rubber-stamp.**

---

## Pass B6 (opus) — CLEAN (3 of 3 — BUILD PLAN CONVERGED)

Final independent check, opus lens — did NOT trust B1-B5; re-derived every load-bearing fact against the
REAL repo in this worktree. Anti-tunnel honored: read `guard-premise.sh` via the `Read` tool only; this
B6 entry itself is appended via the `Edit` tool to the pre-existing log (Edit on an existing file is the
correct tool, not a Write-placeholder tunnel).

**My own 3 highest-risk re-derivations (chosen independently, verified this session):**

1. **Gate-number keystone contract (P3).** `wc -l scripts/audit-gates.sh` = **6454**; highest `── Gate N:`
   = **194** → next-free **195** ✓; **150** distinct numbers ✓; `Supported:` `:877` ends `…193, 194.` ✓;
   dispatcher close `esac :880`/`fi :881` ✓; exit-2 template `rc_is_2=0; [ "$rc" -eq 2 ] || rc_is_2=1` at
   `:1047`/`gate "… exit 2 (not 1)"` at `:1048` ✓. Grepped the live tree for `── Gate (195..210):` →
   **zero** (no collision with the existing max-194 set). In `build-plan.md`, the 16 new numbers 195-210
   map 1:1 to 16 gates (PR 1 makes 195+196; PR 9 extends the claim-grounding gate + PR 15 uses Gate 29 →
   no new number). Each new number appears only inside its own PR's line range — the **one** apparent
   exception, `Gate 195` at `:367` inside PR 4, is a deliberate **cross-reference** to PR 1's gate (B2's
   PR-4→PR-1 dependency fix: "its Gate 195 exit-2 sub-check imports PR 4's hook-detection"), NOT a
   re-assignment. Zero cross-PR gate collision.

2. **PR 2 guard-premise two-call-site target — real + current, and the owner-gate boundary it sets.**
   Read (not grep): `:111 if d.get("tool_name") != "Write":` (Write-only matcher — Edit/MultiEdit evade,
   the gap PR 2 closes) ✓; the fragile `path.replace(proj, "").lstrip("/")` idiom exists at BOTH `:280`
   (feeds the `.ravenclaude/` durable-artifact check `:283`, T-PROSE) and `:405` (feeds the
   `.ravenclaude/`/`docs/`/`.claude/` prefix-exempt check `:407`, T-SHAPE) — two genuinely independent
   call sites; PR 2's two-site fix is not overclaiming. The EXISTING escape PR 2 relies on is present:
   `_CTRL` `:338`, `rc_load_control()` def `:190`/called-in-block `:390`, `premise-ok:` marker,
   `RC_PREMISE_CONTROL`. This anchors the owner-gate boundary: **Half A (PR 2, un-gated) uses this
   existing escape; PR 17 (Fork 2, red-team, owner-gated) is the widened door** — PR 2's SNR line
   explicitly disclaims PR 17's role, so no un-gated PR pre-empts the owner call. (The v0.245.0 milestone
   scoped the LEDGER key — a different bug; the `:280`/`:405` exemption idiom is still live/unfixed,
   re-confirming B3-B5's disambiguation.)

3. **PR 3 packaging-move remediation — mechanism real, move genuinely unbuilt.** Gate 187 dual-region
   (`:748` dispatcher `187)` / `:6153` full-suite); `check-shipped-references-resolve.py:91-101`
   `_DEFERRED_PACKAGING` holds all THREE basenames (`premise-gate.py:92`, `classify_claim.py:93`,
   `check-design-schema.py:100`) with the "REMOVE … when that packaging move lands" comment. All three
   scripts confirmed at marketplace-root `scripts/`, absent from `plugins/ravenclaude-core/scripts/` — the
   move is real and pending; the DoD (relocate → remove basenames → Gate 187 clean exit) is a
   self-verifying mechanism replacing the stale "6" count.

**Bonus contract checks (all green):** PR 9 has a real target — `claim-grounding-lint.sh` @
`audit-gates.sh:3594`; PR 5's Gate 51 @ `:4282` (portal shell router) vs the now-unrelated Gate 144 XSS
floor @ `:5377` — the plan's "verify the number, Gate 144 is now unrelated" caveat is accurate; PR 10/11
`host-support.json` present with **0** `activation_gate` fields (correctly unbuilt); Gate 154 dual-region
(`:470`/`:5514`) is a real extend target; `RC_BASELINE` literal @ `check-plugin-detail-render.mjs:54`;
version **0.253.0** in both mirrors.

**Whole-plan verdict — SOUND + COMPLETE + EXECUTABLE:**
- **(a) teeth-bearing prevention for all 21 classes** — coverage table maps every P1-P21 to a prevention
  PR (grep-confirmed all 21 rows present); the six-part teeth reminder is applied per gate, honestly
  scoped (structurally-satisfied SNR vs RISK-carrying vs advisory-N/A-by-design correctly distinguished).
  The two honest partials (P4 doc-convention-only; P15 durable-artifact-subset) are named, not dropped.
- **(b) remediates every live-open** — each P-class carries a remediation cell; the two named-not-built
  residuals (~194-gate UNWIRED retrofit; twin-server shared-import) are stated as scope limits.
- **(c) keystone-first** — PR 1 first; its `audit-gates.sh` parse imported (not re-derived) by PR 4/6/14,
  avoiding recreating R2 inside the plan. Hard deps: PR 4→{1,3}; PR 11→{9,10}; PR 12→Fork 1; PR 17→Fork 2.
- **(d) gates exactly the owner-judgment halves** — 4 owner-gated PRs (3/10/12/17). PR 3 (Fork 3) + PR 10
  (seed #5) soft-gate only a config/mandatory knob (mechanism builds regardless); PR 12 (Fork 1) + PR 17
  (Fork 2) hard-gate the judgment-heavy DROP build / red-teamed widened door. No over-gating; no non-gated
  PR pre-empts an owner call.
- **(e) no PR recreates a root cause** — fail-open audited (PR 4) not recreated; every script bash-3.2 /
  Py-3.9-stdlib + `from __future__ import annotations`; PR 1's parse imported not duplicated; source-scan
  PRs carry `# noport`/exempt-path + PR 17's durable door; B2's PR-4→PR-1 contract inversion already
  fixed; PR 12 forbids the `scan_repo` tautology; new gates land as STEPS in `audit-gates.sh`/
  `validate-macos.yml`, never a new `paths:`-filtered required workflow (the AGENTS.md hang trap avoided).

**DoD complete + decision-ready:** version-bump partition {2,3,7,8,9,10,12,16,17} bump / {1,4,5,6,13,14}
no-bump / {11} conditional / {15} docs-carve-out = 17, matching the whole-initiative DoD list; prettier
`--write`+`--check`, ruff via `python3 -m pip`, audit-gates green per PR; migration notes on the two
consumer-visible PRs (PR 3 in-loop deny, PR 12 DROP); docs (Ph 0/15) straight to main; no new
`.repo-layout.json` globs needed (re-verified — all new files under already-allowed globs). The
owner-decision surface (Fork 1/2/3, seeds #5/#6, decision #7) is enumerated in one table with recommended
leans — ready to hand to the owner.

**Two benign observations (NOT issues, counter NOT reset — same class as B4's Gate-187 line-pointer note
and B5's PR-15 SNR-tag note):** (1) the plan cites `rc_load_control` "at `:390`" (its call inside the
T-PROSE block) while the function *definition* is `:190` — a line-pointer nuance; the load-bearing
reference (the existing escape) is exactly correct. (2) `Gate 195` at `:367` inside PR 4 is a deliberate
dependency cross-reference, correctly handled, not a collision. Neither is a material defect.

**Issues count: 0. B1-B3's 9 fixes held through B4/B5 and hold now; B4/B5's re-derivations re-confirmed
independently against a still-evolving tree (guard-premise.sh 624 lines; the three packaging scripts
still marketplace-root). No fabricated issue, no rubber-stamp.**

**Verdict: CLEAN (3 of 3 — BUILD PLAN CONVERGED). The loop converges; the build plan is a sound, complete,
executable, decision-ready plan.**
