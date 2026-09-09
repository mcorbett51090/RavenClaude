# Build plan (v1): recurring-defect hardening — PR-by-PR implementation

**What this is.** The buildable, sequenced translation of the CONVERGED design (`hardening-plan.md`,
17 phases, P0/P1/P2, 6 owner decisions + 1 fork, six-part teeth per mechanism) into **shippable PR
units** an engineer or future agent executes one at a time. It groups the 17 design phases into
**17 PRs + 1 docs-straight-to-main commit**, ordered keystone-first then by leverage (§8 of the design),
with every build step verified this session against the **real** `audit-gates.sh` / hooks / manifests in
this worktree — not a guessed contract (that is one of the 21 classes this initiative fixes: R4/P15).

> **Anti-tunnel note (this plan followed the discipline it teaches).** Where a step must name a
> guard-caught command, it is described in **prose / past tense** ("a force-push to a protected branch",
> "a fetch-piped-into-a-shell"), never as literal danger syntax. **Two live proofs, this session:** (1) a
> read-only grep of `concerns-catalog.md` carrying the verb-list literals was DENIED pre-LLM by
> `xc.tribunal-self-disable` (a fresh, reproducible **incident (d)**); (2) the first Write of this very
> file was DENIED by `guard-premise.sh` T-PROSE, which read a section heading as a diagnosis-stated-as-fact
> (a live **P7** instance — the class PR 2 fixes). Both were handled the sanctioned way — a safe-token
> re-grep + the `Read` tool for (1), and a **reword to procedural prose** for (2) — **not** by tunnelling
> around the matcher (the Write-placeholder-then-Edit path the run's Panel B was flagged for).

---

## 0. Verified build contract (this session, in `.claude/worktrees/forge-recurring-defects`)

Every subsequent PR is specified against these reads. Re-verify the volatile ones (gate max, version) at
each PR's build time — they drift as earlier PRs merge.

| Fact | Value (verified) | Where |
|---|---|---|
| `audit-gates.sh` size | 6454 lines | `wc -l` |
| Highest `── Gate N:` header | **194** → **next free = 195** | `grep -oE '── Gate [0-9]+'` |
| Distinct gate numbers | **150** (many echoed in both regions) | same |
| `Supported:` list | `:877`, ends `…193, 194.` | `grep -n 'Supported:'` |
| `--check` dispatcher close | `esac` `:880` / `fi` `:881` | `sed -n '876,882p'` |
| Exit-2 assertion template | `:1046–1048` (`rc_is_2=0; [ "$rc" -eq 2 ] || rc_is_2=1; gate "… exit 2 (not 1)"`) | `sed -n '1045,1050p'` |
| `_skip_or_fail()` | `:945` | grep |
| Dual-region echo proof | Gate 132 `:406` (dispatcher, "per-gate run") + `:5192` (full-suite) | grep |
| `_portable.sh` shims | `_rc_timeout :37`, `_rc_upper :55`, `_rc_pcre_match :83`, `_rc_host_env :129`, `_rc_host :148` | grep |
| `guard-premise.sh` tool scope | **`:111` `if d.get("tool_name") != "Write":`** — T-PROSE/T-SHAPE is Write-only; Edit/MultiEdit evade | Read |
| `xc.tribunal-self-disable` trigger #2 | `concerns-catalog.md:184` — verb list within `{0,200}` of a substrate path, **no read/mutate discriminator** | Read |
| `.repo-layout.json` globs | `scripts/**`, `plugins/*/hooks/**`, `plugins/*/knowledge/**`, `plugins/*/skills/**`, `plugins/*/monitors/**`, `docs/**`, `tests/fixtures/**`, `.github/**`, `.claude/settings.json` — **all present** | Read |
| Twin servers | `scripts/serve-dashboards.py` + `plugins/ravenclaude-core/scripts/serve-dashboards.py` | find |
| `RC_BASELINE` | `scripts/check-plugin-detail-render.mjs:54` `const RC_BASELINE = {` | grep |
| Packaging-move outliers | `scripts/premise-gate.py`, `scripts/classify_claim.py`, `scripts/check-design-schema.py` at **marketplace-root**; cited repo-relative in `forge-pipeline/SKILL.md:132,163` | find/grep |
| `ravenclaude-core` version | **0.253.0** (plugin.json + marketplace.json mirror) | json |
| macOS runner | `validate-macos.yml` `runs-on: macos-latest` `:49`, paths-filtered, **not** required | grep |
| Required whole-tree workflow | `validate-marketplace.yml` (prettier `:305`, ruff, audit-gates, frontmatter) — Phase 2's CI lint lands here as a **step** | grep |

**Layout verdict: NO new `.repo-layout.json` globs are required by any PR** — every new file lands under
an already-allowed glob (verified above). This matches the design DoD ("none expected").

**Gate-number discipline (this IS class P3 — do not hand-assign blindly).** The gate numbers below
(**195–210**) are **provisional**, assigned assuming strictly sequential merge. **Every PR re-derives its
next-free number against the then-current `audit-gates.sh` max + the `Supported:` list at its own build
time.** Once **PR 1** lands, `check-gate-registration.py` (the keystone) *catches* a collision or an
unreachable paste automatically — which is why PR 1 is first.

---

## 1. PR sequence at a glance

| # | PR | Design phase(s) | Classes (prevent + remediate) | Tier | Gate(s) | Owner-gated? | Effort |
|---|---|---|---|---|---|---|---|
| — | **Docs commit** (straight to `main`) | Ph 0 (+ Ph 15 doc half) | P20 | P0 | (existing Gate 29 md-links) | no | S |
| 1 | **Keystone: gate-introspection meta-gate** | Ph 1 | P2, P3, P4(partial), P6 | P0 | 195, 196 | no | M |
| 2 | **Premise-guard scope + read/mutate fix** | Ph 11 Half A | P7 (+P9) | P0 | 197 | no | S–M |
| 3 | **Author-time portability lint** | Ph 2 | P1 | P0 | 198 | **Fork 3** (posture default) | M |
| 4 | **Fail-closed exit-code execution audit** | Ph 3 | P5, P6 | P0 | 199 | no | M |
| 5 | **Surface-parity gate** | Ph 4 | P11, P12 | P1 | 200 | no | M–L |
| 6 | **Catalog-scoping-consistency lint** | Ph 9 | P8 (+P6 remainder) | P1 | 201 | no | M |
| 7 | **Subagent-safe-guard checklist/fixture** | Ph 10 | P9 | P1 | 202 | no | M |
| 8 | **Constitution staleness linkage** | Ph 13 | P19 | P1 | 203 | no | S–M |
| 9 | **Contract-provenance lint (advisory)** | Ph 12 | P15 (partial) | P2→built early (PR 11/Ph 8 dep) | (extends existing) | no | S |
| 10 | **Behavioral canary host-onboarding** | Ph 6 | P16, P18 (+P17) | P1 | 204 | **seed #5** | M–L |
| 11 | **Host-capability lint + adapter round-trip** | Ph 8 | P17 | P1 | 205 | no (needs PR 9 + PR 10) | M |
| 12 | **Count-SSOT DROP refactor** | Ph 5 | P13 (shrinks P14) | P1 | 206 | **Fork 1** | L |
| 13 | **Self-heal push-safety invariant** | Ph 7 | P14 | P2 | 207 | no | S–M |
| 14 | **Self-certifying-change flag** | Ph 14 | P10 | P2 | 208 | no | S |
| 15 | **Corpus-scale plausibility checklist** | Ph 15 | P20 (checklist half) | P2 | (existing Gate 29) | no | S |
| 16 | **DOM-budget ratchet formalization** | Ph 16 | P21 | P2 | 209 | seed #6 (may defer) | S |
| 17 | **Widened sanctioned-escape door** | Ph 11 Half B | P7 (durable) | P2 | 210 | **Fork 2 (red-team)** | M |

**Six-part teeth reminder (every new gate passes all six, checked in each PR's DoD):** (1)
not-hollow/appears-in-suite-by-name; (2) fail-closed/exit-2-specific; (3) macOS-portable (bash-3.2 /
Python-3.9-stdlib, no `declare -A`/`mapfile`/`${x^^}`/`shopt globstar`/GNU-`timeout`/PCRE-`grep`/in-place
`sed`/GNU-`find`); (4) verified contract (built to a this-session `file:line`); (5)
assert-surfaces-against-each-other (never a constant oracle); (6) self-non-recursion (SNR — a CI reader
has no deny surface; a real deny hook / prose scanner needs the `# noport`-style sentinel + `printf`
fixtures + prose-not-literal + PR 17's exempt path).

---

## Docs commit (Phase 0 + Phase 15 doc half) — straight to `main`, no PR

Per AGENTS.md, pure `docs/` changes commit straight to `main` (they cannot break a consumer's
`/plugin marketplace update`).

- **Files:** `docs/best-practices/ci-gate-audit.md` — add a forward-pointer **markdown link** (not a
  backtick path — Gate 29 skips code spans; the v0.194.0 `strip_code()` lesson) to
  `docs/best-practices/validating-a-measuring-instrument.md`. Optionally add the reciprocal back-pointer.
- **Also here (Phase 15 doc half):** add the corpus-scale plausibility checklist section to the
  "author a new checker" workflow doc, referencing `validating-a-measuring-instrument.md` (the
  3,337-finding incident) and `ci-gate-audit.md` (the founding actionlint case).
- **Verify:** `python3 scripts/check-md-links.py` green (Gate 29); the new link resolves and is a real
  link. **DoD:** no version bump (docs-only), no gate added.
- **Effort S · risk none · rollback: revert the doc lines.**

---

## PR 1 — Keystone: gate-introspection meta-gate (Phase 1)

**Delivers:** P2 (reachability), P3 (number-uniqueness), P4 (UNWIRED doc convention — honest partial),
P6 (regex-compile primitive). **This PR is FIRST because its two gates guard every later PR's gate** and
its `audit-gates.sh`-parse is imported (not re-derived) by PR 4/6/14 (shared primitive; re-deriving it
would recreate R2 inside the plan).

**Files (all under allowed globs; no plugin change → no version bump):**
- `scripts/check-gate-registration.py` (new).
- `scripts/check-regex-catalog-compiles.py` (new — reusable `(path, field-selector)`).
- `scripts/audit-gates.sh` (register the two new gates in **both** regions; add exit-2 teeth halves).
- `docs/best-practices/ci-gate-audit.md` (add the third fixture category `must_flag_unwired_on` next to
  the existing `must_fail_on`/`must_pass_on` at `:25–26` — a **doc convention for future authors**, not a
  retroactive scan).

**Gate build spec:**
- **Gate 195 — `check-gate-registration.py`** (next-free; re-verify). Static parser over `audit-gates.sh`:
  - **Reachability (P2):** every `── Gate N:` header must have ≥1 `gate` call in the **unconditional
    full-suite region** (after the dispatcher closes — `esac :880`/`fi :881`), not only in a `--check N)`
    arm (the Gate-184 paste-inside-dispatcher shape, `:6108–6122` before its fix). **Build-plan
    calibration item (from loop-log `:1441`):** the "≥1 `gate` call in the full-suite region" heuristic is
    a *parser-calibration* property against the current tree — a gate whose full-suite work is delegated
    to a sub-script still keeps its literal `gate "…"` line (spot-checked true for Gate 194 and the
    `_skip_or_fail`-gated branches). This calibration rides the **M5 mandatory pre-build zero-false-positive
    dry-run** below, so it is a build-time tuning step, not a design defect.
  - **Number-uniqueness (P3):** flag a number appearing **twice in the same (full-suite) region** (the
    real two-Gate-104 collision). **Key on region, NOT description-difference** — measured: 87/150 numbers
    legitimately echo their header in BOTH the dispatcher (`(per-gate run)` wording) AND the full-suite
    region (canonical wording); a "same-number→different-text→collision" rule floods the suite day-one and
    gets the keystone disabled (the M5 fate). Reuse the same region-split the reachability sub-check
    computes.
  - **Exit-2 specificity (P5 shared clause):** for a gate whose preceding lines show the **PreToolUse-hook
    invocation signature** (a `hooks/*.sh` path piped stdin, `|| rc=$?`/`|| GD_RC=$?` capture), require a
    paired `[ "$rc" -eq 2 ]` check. **Scope to that signature — do NOT key on the gate NAME containing
    "blocks"/"deny"** (measured: only 8/57 name-matching gates assert a hook exit; 49 assert an internal
    decision-engine string/JSON — e.g. `:1590` `thing_decision`, `:2148` adapter field — where "exit 2" is
    meaningless). Import PR 4's hook-detection when it lands; until then compute the signature locally.
  - Exit **2** (fail-closed) on any parse ambiguity (a header with no match, an unreadable file); never a
    silent skip.
- **Gate 196 — `check-regex-catalog-compiles.py`** (next-free). Compiles every regex in a named catalog,
  fails on a malformed one. First invoked against the `thing-concerns.py` concerns catalog (parity with
  Gate 16) **and** the comfort-posture hard-rule catalog (the newly-covered surface — the v0.242.0/v0.244.0
  silent-disable).
- **UNWIRED (P4) — honest partial:** a **doc-convention addition only** (`must_flag_unwired_on` in
  `ci-gate-audit.md`), generalizing Gate 179's UNWIRED verdict (`:6092`). **No must-fail fixture in this
  PR by design** — whether a gate's own detector silently no-ops on a missing input is a *runtime*
  property, not visible to a static header parse. State this scope explicitly; do NOT claim a retroactive
  scan of the ~194 gates.
- **Appears-in-suite-by-name:** register both gates in the `--check` dispatcher case + the `Supported:`
  string + the full-suite region; after registering, **grep the full-suite output for the two gate names**
  (`:6119` ritual) and confirm the assertion count rose by the number added.
- **macOS-portability:** pure Python 3.9 stdlib (`re`/`pathlib`), `from __future__ import annotations`
  (the PEP-604 door the v0.194.0 `check-md-links.py` TypeError named — CI runs 3.10+, so this fails only
  on a stock-macOS local run and is easy to miss).
- **Contract verified:** `── Gate N:`, dispatcher close `:881`, `Supported:` `:877`, exit-2 template
  `:1046–1048` — all read this session.

**Acceptance tests + fixtures (`mktemp -d` synthetic copies of `audit-gates.sh`, never the live file):**
- must-fail (P2): a copy with a gate pasted inside the dispatcher → nonzero.
- must-fail (P3): a copy with two `── Gate 104:` headers **both in the full-suite region** → nonzero,
  names both. **Companion must-PASS (anti-flood):** an unmodified dual-region gate (dispatcher `(per-gate
  run)` echo + full-suite canonical echo) is NOT flagged.
- must-fail (P5): a synthetic gate with the hook-invocation signature but no companion `-eq 2` check →
  nonzero, names the gate. **Companion must-PASS (anti-flood):** the 49 internal-decision-engine
  "blocks"/"deny" gates (e.g. `:1590`, `:2148`) are NOT flagged.
- must-fail (P6): a catalog copy with a deliberately malformed regex → `check-regex-catalog-compiles.py`
  nonzero, names the line.
- pass-on-good: the current already-fixed tree passes both gates.

**Remediation of live-open:** running Gate 195 against the current `audit-gates.sh` at merge surfaces any
already-unreachable/duplicate gate; Gate 196 gives the comfort-posture hard-rule catalog its first
standing recompile. The ~194-gate UNWIRED retrofit is **explicitly NOT performed** (named gap).

**DoD:** M5 **pre-build dry-run** — run the drafted parser against the CURRENT tree, confirm **zero false
positives** across all 150 numbers BEFORE registering (a day-one flood disables the keystone). Then both
regions + suite-grep + assertion-count delta. prettier (`.py` is ignored; ruff `check .` must pass).
`scripts/audit-gates.sh` green incl. the two new gates' own audit. No version bump (no `plugins/` change).
Migration: none.

**Effort M · risk M (false-positive flood — M5 mitigates) · rollback: revert both scripts + the two gate
registrations; nothing downstream has imported the parse yet.**

---

## PR 2 — Premise-guard scope + read/mutate discriminator (Phase 11 Half A)

**Delivers:** P7 (self-referential-guard false-positives), contributes P9. **Reprioritized into the P0
band by the run's live evidence — and this session added two more reproductions: incident (d) above, and
the first Write of this very build-plan being T-PROSE-denied.** Ships **now, no owner gate** (Half B's
widened surface is the only owner-gated part → PR 17). Placed right after the keystone so **every
subsequent source-scan PR suffers fewer guard false-positives while being built.**

**Files (touches `plugins/` → version bump required):**
- `plugins/ravenclaude-core/hooks/guard-premise.sh` — (a) fix the `.ravenclaude/runs/**` exemption to
  cover **nested worktrees** (the exemption strips `CLAUDE_PROJECT_DIR` before the `.ravenclaude/` prefix
  check; in a nested-worktree session that comparison can fail on a genuinely-under-`runs/` path — it
  denied the miners' and panel Writes this run). **VERIFIED this session — the fragile
  `path.replace(proj, "").lstrip("/")` idiom exists at TWO separate call sites in this file, not one:**
  T-PROSE's own durable-artifact exemption (`rel_p` at `:280`, gating the `.ravenclaude/` check at `:283`)
  **and** T-SHAPE's prefix-exemption list (`rel` at `:405`, gating the `.ravenclaude/`/`docs/`/`.claude/`
  check at `:407`). Both are independently vulnerable to the identical nested-worktree failure (a `proj`
  that is not a literal substring of `path` leaves `rel`/`rel_p` as the full absolute path, which never
  matches a bare `startswith(".ravenclaude/")`). **Fix both call sites** — patching only one (the
  P8-shaped "fix-one-instance-and-stop" trap this very design names elsewhere) would leave the other
  half of the guard still denying legitimate nested-worktree writes; (b) **make the T-PROSE/T-SHAPE screen tool-agnostic** —
  **VERIFIED this session at `:111` `if d.get("tool_name") != "Write":`** (the design's `[unverified —
  confirm matcher scope]` marker is now **resolved**): an `Edit`/`MultiEdit` evades the screen entirely,
  which is both a false-positive-mitigation gap and the exact tunnelling surface Panel B used. Extend the
  guard to cover `Edit`/`MultiEdit` **and** ensure the guard's **existing** sanctioned escape — the
  in-block `premise-ok:`/`control:` marker (`_CTRL` at `:338`), `RC_PREMISE_CONTROL`, and the durable
  `control.md` file (`rc_load_control` at `:390`, v0.245.0) — is honored on the `Edit`/`MultiEdit` path
  too, so the correct response to a false-positive is that existing escape, not a tool-switch. **This is
  NOT the widened exempt-path/sentinel door** (the `tests/fixtures/**`+`docs/**` allowlist) — that is
  PR 17's owner-gated (Fork 2, red-team) deliverable and is deliberately NOT built here.
- `plugins/ravenclaude-core/scripts/thing-concerns.py` + `plugins/ravenclaude-core/knowledge/concerns-catalog.md`
  — fix `xc.tribunal-self-disable` trigger #2 (`concerns-catalog.md:184`, `screen_always`) to
  **discriminate a read from a mutation**: match only on a genuine in-place mutation — the in-place-edit
  flag on the stream editors, a redirect/`tee`/`sponge` onto a substrate path (trigger #1 already covers
  redirection). A bare read invocation of the stream editors / a bare pattern-print must NOT match trigger
  #2. **Do NOT treat print-mode as a mutation signal** — print-mode without the in-place flag writes to
  stdout (a read), so a print-as-mutation rule would keep denying the very reads this fix releases.
  Fail-closed preserved: the in-place-edit flag + a `tee`-pipe onto a substrate path still deny exit 2.
- `scripts/audit-gates.sh` — new Gate 197 + must-fail half.

**Gate build spec — Gate 197** (next-free): exercises the three fixes end-to-end.
- must-fail → must-PASS (nested-worktree): a `.ravenclaude/runs/**` Write **in a nested worktree** must
  NOT be denied after the fix — asserted through **both** call sites (a T-PROSE-triggering diagnosis
  sentence written under `.ravenclaude/runs/**` in a nested worktree, AND a new-source-module Write under
  `.ravenclaude/runs/**` in a nested worktree, so a fix applied to only one of `guard-premise.sh:280`/`:405`
  is caught).
- must-fail → must-PASS (tool-scope): the same descriptive prose via `Edit` is screened the same as via
  `Write` (the screen no longer evades on `Edit`); and a legitimate docs-tier prose citation (like this
  file) is NOT denied.
- must-fail → must-PASS (read/mutate): a bare pattern-print read of a plugin hook / a bare
  line-range-print read of a script (no in-place flag, no redirect) must NOT be denied after the fix; the
  **same command with the in-place flag appended, or piped into `tee` onto a substrate path, MUST still
  deny exit 2** (the discriminator narrows, it does not disable — trigger #2).
- **exit-2:** the exemption/discriminator NEVER downgrades a live dangerous command; fail-closed preserved.
- **macOS:** bash-3.2-safe guard edits; `thing-concerns.py` stays Python-3.9-stdlib.
- **SNR:** PR 2 is a genuine `PreToolUse` deny-hook edit whose own residual is covered by the guard's
  existing `premise-ok:`/`control:` escape (above); here it clears the two concrete this-run guard-premise
  false-positives. It is **NOT** the sanctioned-exempt door the *other* source-scan hooks (Phase
  2/7/8/9/12/13 → PR 3/13/11/6/9/8) depend on to retire *their* SNR residual — per the design
  (hardening-plan §2) that door is **Phase 11 Half B = PR 17** (owner-gated, Fork 2), which those PRs adopt
  once it lands (until then, the `printf`/`# noport` workaround). PR 17, not PR 2, carries that role.

**Remediation of live-open:** closes the two named this-run false-positive bugs + the
`xc.tribunal-self-disable` read/write-blind trigger (incidents (c) and (d), the latter reproduced this
very session while verifying this plan's citations; and the guard-premise T-PROSE denial of this file's
own first Write).

**DoD:** both regions + suite-grep for Gate 197. **Version bump** ravenclaude-core 0.253.0 → next (both
`plugin.json` + `marketplace.json` mirror). prettier (JSON) + ruff green. audit-gates green. **Migration
note:** consumer-visible in the permissive direction only — ordinary verification reads of substrate files
stop being denied; every genuine substrate mutation still denies. bash-3.2-safe (no reopened macOS door).

**Effort S–M · risk L (narrows what the guard denies — fail-closed preserved) · rollback: revert the
three files; the guard reverts to its prior Write-only + read-blind behavior.**

---

## PR 3 — Author-time portability lint (Phase 2)

**Delivers:** P1 — the single highest-recurrence class (18 door commits, still breaking at #885/#873).
**Fork 3 sets the default posture + scope** (the *mechanism* is settled to a graduated knob); the build
starts with the recommended default and the owner flips the config value — Fork 3 gates only the default,
not the build. Depends on PR 2 landing first (fewer guard false-positives while authoring the token
fixtures).

**Files (touches `plugins/` → bump):**
- `plugins/ravenclaude-core/hooks/enforce-portability.sh` (new) — `PreToolUse(Write|Edit|MultiEdit)`.
  Deny/warn a write introducing a banned bash-4/GNU token (associative-array declaration, `mapfile`,
  upper/lower parameter-expansion, `globstar`, an unshimmed timeout, PCRE-`grep`, an in-place stream edit,
  GNU-only `find` idiom) unless routed through `_portable.sh` (confirmed shims: `_rc_timeout`/`_rc_upper`/
  `_rc_pcre_match`). Copy the deny contract from `enforce-layout.sh:94–105` (`hookSpecificOutput`
  `permissionDecision` + exit 2); copy the absent-target / stdin-`jq` fail-safe from `enforce-layout.sh:40–46`
  (unreadable target / missing `jq` → exit 0 — a portability lint that hard-fails a consumer with no shell
  surface is worse than the gap).
- `plugins/ravenclaude-core/hooks/hooks.json` + `.claude/settings.json` — register `PreToolUse` in **both**
  wirings (the dev-mirror dual-registration CLAUDE.md's "Marketplace-dev hooks" requires).
- `scripts/check-portability-lint.*` (new) — the CI-backstop linter (same banned-token set).
- `.github/workflows/validate-marketplace.yml` — add a new **step** (NOT a new required workflow, NOT a
  `paths:` filter — Risk M4) running the linter over `plugins/**/hooks/*.sh` + `scripts/*.sh` +
  `scripts/ravenclaude` (the extension-less installer that fell outside `scripts/*.sh` and broke at #885)
  + `plugins/*/bin/rc` + `plugins/*/monitors/**` (**use the `plugins/*/monitors/**` prefix form** — an
  unprefixed `monitors/**` matches zero files, verified: the only shipped `monitors/` is under
  `plugins/ravenclaude-core/`).
- `scripts/audit-gates.sh` — Gate 198 + must-fail half.

**Enforcement posture — Fork 3 (owner sets the config default):** graduated knob
`macos_portability_lint: off | warn | block` (mirroring the shipped `git_protocol` precedent).
**Recommended default: `warn` + wide scope** (the two most recent breaks #885/#873 were *outside*
`hooks/**`, so narrow scope reopens exactly the doors the runner already covers). Owner may set `block` or
narrow scope; the mechanism is unchanged either way.

**Gate build spec — Gate 198** (next-free):
- must-fail: the #885 apostrophe-in-heredoc shape + one fixture per banned construct in isolation — each
  DENIED (exit 2) by the hook at `block` and flagged by the CI linter.
- pass-on-good: a script routing the same op through `_portable.sh` passes; a benign write passes; a write
  to a file **outside** the scoped globs containing a banned token passes (scope discipline).
- pass-on-good (SNR self-test): editing the portability hook's OWN source to add a new banned-token check,
  routed through `_portable.sh`, is allowed.
- **exit-2:** deny is exit **2**; unreadable target / missing `jq` → exit 0 fail-safe.
- **macOS:** the lint itself is bash-3.2-safe (`grep -E`, no PCRE, no associative arrays) — it must not
  open a door while closing one.
- **surfaces:** the CI linter and the `macos-latest` runner (`check-macos-portability.sh`) assert the same
  banned-token set from two angles (static author-time vs runtime execution) — a divergence is itself a
  failure. **Run `check-macos-portability.sh` on macos** in the DoD to confirm they agree.
- **SNR — RISK M1:** this is a genuine deny hook whose own fixtures/`_portable.sh`/`check-macos-portability.sh`
  *contain* the banned tokens as data. **Mitigation up front:** a sanctioned-exempt allowlist
  (`_portable.sh`, `check-macos-portability.sh`, `tests/fixtures/**`, the linter's own source) + a
  `# noport` in-file sentinel; residual (a banned token in a new comment elsewhere) accepted as
  advisory-warn. Shares the exempt-path design with PR 17 and reuses its outcome if PR 17 ships first.

**Remediation of live-open:** (a) lint the current tree — surface the #885 apostrophe residue + the
`pip`-vs-`python3 -m pip` (#873) shape; (b) extend coverage past `hooks/**` to
`plugins/*/monitors/**`/`scripts/**`/entrypoints. **(c) Packaging move (tracked here, folded from Ph 2
live-open (c) + the v0.253.0 sibling):** relocate `scripts/premise-gate.py`, `scripts/classify_claim.py`,
**and** `scripts/check-design-schema.py` from marketplace-root `scripts/` to
`plugins/ravenclaude-core/scripts/` (`${CLAUDE_PLUGIN_ROOT}`) and update all citations — verified:
`forge-pipeline/SKILL.md:132,163` cite the first two **repo-relative**, so they resolve here but NOT in a
consumer repo; the third is the v0.253.0 deferred sibling with the identical defect. **The move already has
a concrete, existing acceptance mechanism — use it instead of a hand-counted citation figure.**
`scripts/check-shipped-references-resolve.py` (**Gate 187**, `:748` header) carries a `_DEFERRED_PACKAGING`
set (`check-shipped-references-resolve.py:91-101`) that **already lists all three basenames**
(`premise-gate.py`, `classify_claim.py`, `check-design-schema.py`) as an intentional ignore-list, with its
own comment stating "REMOVE these two [now three] entries when that move lands — the gate then keeps them
honest." **Do the move by (1) relocating the three files, (2) removing all three basenames from
`_DEFERRED_PACKAGING`, (3) running Gate 187** — it then enumerates every remaining bare marketplace-root
reference in an operational surface (`rules/skills/commands/agents/templates`, `.md`/`.sh`/`.json`/`.yaml`/
`.yml`) and fails loudly on any citation the move missed. **The design's "6-call-site" figure
(`hardening-plan.md:315`) predates the third script and was derived for only the first two** — this session
found at least one additional citation of `classify_claim.py` (`forge-pipeline/reference/premise-gate.md:40`)
and at least two of `check-design-schema.py` (`design-clone/SKILL.md:22`, `brand-extraction/SKILL.md:67`)
beyond the originally-counted pair, so **treat "6" as a stale estimate, not a completion criterion** — Gate
187's clean exit after the ignore-list edit is the actual DoD, not a fixed count. This is a **6+-call-site
move** and **may split into its own small PR** if it bloats the portability diff — it touches `plugins/`
(files move INTO the plugin) so it carries its own migration reasoning. Note: moving a `.py` into the
plugin means it ships to consumers — confirm no marketplace-root-only assumption breaks.

**DoD:** M5 dry-run (report-only over every scoped file, zero unexpected denials) before flipping the knob
past `warn`. Both regions + suite-grep. **Version bump** (both mirrors). prettier (YAML/JSON) + ruff.
audit-gates green. **Migration note (consumer-visible — one of two in the whole plan):** the in-loop deny
is new; document that `macos_portability_lint` defaults to `warn` (no block on update) and how to set
`block`. If the packaging move rides here, add a migration line for the relocated scripts.

**Effort M · risk M (repo-wide CI lint over ~180 plugins — warn-first + M5 dry-run mitigate) · rollback:
set the knob `off` + revert the CI step; the hook no-ops.**

---

## PR 4 — Fail-closed exit-code execution audit (Phase 3)

**Delivers:** P5 (fail-open-on-error), P6. A static syntax check provably cannot see this class (the
constructs are valid, they fail only at runtime). **Depends on PR 1** (imports PR 1's shared
**`audit-gates.sh` parse** — PR 1's actual export per PR 1 above, used here to locate each gate's region +
the hook-invocation signature; the **`hooks.json` enumeration that drives every enforcement hook is PR 4's
OWN read**, NOT a PR 1 deliverable — PR 1 parses `audit-gates.sh`/regex-catalogs, never `hooks.json`, and
its Gate 195 exit-2 sub-check *imports PR 4's* hook-detection, not the reverse) **and PR 3** (the new
portability hook is one of this audit's targets — running before PR 3 silently skips the newest hook).
*(Design note: `hardening-plan.md`'s Phase 3 phrasing "reuses Phase 1's machine-read of `hooks.json`" is
the same imprecision corrected here — Phase 1 reads no `hooks.json`; the reused primitive is the
`audit-gates.sh` parse.)*

**Files (no `plugins/` change → no bump):**
- `scripts/check-hook-failclosed.sh` (new — the execution runner). Drive every `PreToolUse` enforcement
  hook with malformed / empty / error-shaped input under `env -i PATH=/usr/bin:/bin` on macos **and**
  ubuntu; assert the outcome is **deny(2) or safe-noop(0), never a fail-open exit 1**.
- `scripts/check-verdict-default-nonpermissive.py` (new — the static lint, deliberately separate so it
  runs without executing anything). Assert every verdict-resolving `case`/`if` chain ends in an explicit
  non-permissive default (the v0.205.1 "else → allow" fix) + a trap-ordering check (EXIT trap armed before
  the first fallible op — the v0.205.1 `_emitted`-after-write fix).
- `.github/workflows/validate-macos.yml` — add the audit; keep `macos-latest` + **add an ubuntu matrix
  leg** (currently macos-only). This workflow is paths-filtered + **not required**, which is correct
  (M4) — a paths filter here does not hang a PR.
- `scripts/audit-gates.sh` — Gate 199 + must-fail half.

**Gate build spec — Gate 199** (next-free):
- drive-each-hook: feed empty JSON, malformed JSON, and an error-inducing payload; assert exit ∈ {0, 2}.
- must-fail: a mutant hook whose error/deny branch resolves to exit 1 (fail-open) MUST be caught.
- must-fail (static): a `case` chain ending in a permissive `*)` allow MUST be flagged.
- pass-on-good: the current tribunal (`thing-orchestrator.sh`) + `route-decision-review.sh` — already
  hardened — pass clean (proves the audit isn't just re-finding fixed shapes).
- **exit-2:** assert the observed deny exit is literally **2**, not merely nonzero (`:1046–1048`
  template). A missing interpreter during a hook's own test run is a hard CI failure via the existing
  `_skip_or_fail` (`:945`), never a silent skip.
- **macOS:** runs under `env -i PATH=/usr/bin:/bin` exactly like the runner it extends; bash-3.2-safe.
- **surfaces:** runs the *same* hooks on macos+ubuntu and asserts identical deny/safe-noop outcomes — a
  platform divergence is a failure (how the original doors hid).
- **contract:** the exit-code contract in `check-macos-portability.sh:83–85` + the exit-2 assertion at
  `:1046–1048`, read this session.
- **SNR:** structurally satisfied (it *executes* hooks — no prose-scan surface); the static
  verdict-default lint could match a commented-out `*) allow`, mitigated by the `# noport`-style sentinel.

**Remediation of live-open:** no blanket meta-check currently drives every enforcement hook's
deny/error/else fixture; the associative-array index-0 collision (C4) rewrite trap is audited only inside
`thing-orchestrator.sh` — this pass is the wider audit over any sibling using the role-keyed pattern.

**DoD:** both regions + suite-grep. `check-macos-portability.sh` on `macos-latest`. audit-gates green. No
version bump. Migration: none.

**Effort M · risk M (cross-phase drift M11 — import PR 1's parse, do not re-derive) · rollback: revert
the two scripts + the workflow leg.**

---

## PR 5 — Surface-parity gate (Phase 4)

**Delivers:** P11 (presence-not-placement), P12 (twin-server behavioral drift). Names but does NOT build
the P17 host-scope variant (that is built once, in PR 11 — see the design's explicit Phase-4→Phase-8
clarification; building a second copy here would recreate R2).

**Files (no `plugins/` change → no bump, unless the twin is eliminated — see note):**
- `scripts/check-surface-parity.py` (new engine, `(derive_fn, assert_fn)`).
- `scripts/check-dashboard-server-parity.py` (extend name-parity → behavioral-parity, or a sibling).
- `scripts/audit-gates.sh` — Gate 200 + must-fail halves.

**Gate build spec — Gate 200** (next-free). Generalize Gate 51's derive-and-compare (`:4282–4421`).
**Verify the gate number against the current tree before building** — the design flags that Gate 51's
mechanism shipped under "Gate 144" pre-renumber (Gate 144 is now the unrelated Prompt Builder XSS floor
at `:5377` — confirmed this session Gate 51's header is at `:4282`). Two variants built here:
- **route/placement parity (P11):** for every nav route/tab, extract the destination from the standalone
  `ds-nav` chrome (the SSOT the portal folds in) and assert the portal's `DASH_OWNER` + that section's
  `navChildren` agree (the v0.216.0 "third time this shape shipped" fix, generalized).
- **behavioral parity (P12):** dispatch both `serve-dashboards.py` copies (root + bundled, both confirmed
  present) with identical requests and diff responses (busy-port recovery, root redirect, CSRF host-keying,
  `/__sleipnir` handler existence) — closing Gate 32's blindness to `main()` drift.
- **Honesty caveat (design):** if the server-twin instance needs enough bespoke logic that "one generic
  engine" is really two scripts sharing a comment, **ship it honestly as two scripts** — a false
  generalization is itself a hollow gate.
- **exit-2** on any disagreement (a placement bug is a user-visible dead-end). **macOS:** Python; the
  behavioral leg dispatches via stdlib http. **surfaces:** this mechanism IS the assert-against-each-other
  prior in its purest form. **SNR:** structurally satisfied (CI reader comparing two generated artifacts).

**Acceptance tests:** must-fail (P11) — standalone homes a tab under Control but portal `DASH_OWNER` says
Catalog → exit 2 (the exact v0.216.0 regression); a link moved out of its `navChildren` while `DASH_OWNER`
unchanged → exit 2. must-fail (P12) — one server copy 500s on `/__sleipnir` while the other serves it;
busy-port recovery patched out → exit 2. pass-on-good: current tree.

**Remediation of live-open:** no generic N-surface parity gate exists (Gate 51 is case-by-case); Gate 32
remains blind to `main()` drift; the twin `serve-dashboards.py` is still two hand-maintained copies (the
durable fix — a shared import — is a **note**, not built here; **if built, it touches `plugins/` → bump**).

**DoD:** pre-build — confirm the `derive_fn`/`assert_fn` split genuinely generalizes past these two
instances before claiming "generic" (M8). Both regions + suite-grep. audit-gates green. No bump (unless
twin eliminated). Migration: none.

**Effort M–L · risk M (false-abstraction M8 — "ship as two scripts" is the sanctioned fallback) ·
rollback: revert the scripts + gate.**

---

## PR 6 — Catalog-scoping-consistency lint (Phase 9)

**Delivers:** P8 (fix-one-instance / unscoped-regex-beside-scoped), P6 remainder (regex-catalog rollout).
**Reuses PR 1's `check-regex-catalog-compiles.py`** (import, not re-derive).

**Files (no `plugins/` change → no bump):**
- `scripts/check-trigger-scoping-consistency.py` (new).
- `scripts/audit-gates.sh` — Gate 201 + must-fail half.

**Gate build spec — Gate 201** (next-free). Group comfort-posture triggers by block/category; flag a bare
unscoped wildcard across a command separator where a sibling in the same block uses an explicit
separator-excluding character class; require the same pattern's other matches in the diff or waived. Would
have caught **both** unscoped-wildcard incidents (a force-push rule and a fetch-piped-into-a-shell rule,
fixed one release apart) statically. Finish rolling PR 1's regex-compile primitive out to every remaining
regex-bearing catalog.
- must-fail: a synthetic two-trigger block where A uses a bare wildcard and B (same category, same danger
  shape) uses a separator-excluding class → exit 2.
- regression: replay the two dated incidents as historical snapshots — flags the second-found sibling at
  the *first* incident's snapshot, clean at the post-second-fix snapshot.
- pass-on-good: the current post-fix catalog.
- **exit-2:** on a scoping inconsistency; if the checker can't confidently classify a block, default to
  **flag, not block** (M9 — worst case is noise, not false security). **macOS:** Python 3.9 stdlib.
  **surfaces:** asserts sibling triggers against each other (the scoped sibling is the oracle for the
  unscoped one). **SNR — RISK M1:** the lint scans the catalog (regex literals that look like the thing
  forbidden); mitigate with `printf`-assembled fixtures + PR 17's exempt path; if ever converted to a
  `PreToolUse` nudge, ship advisory-only.

**Remediation of live-open:** the enumerate-the-class step is prose today; nothing greps the catalog for a
bare unscoped wildcard beside a scoped sibling. This PR's run is what a standing check would have caught
between the two dated incidents.

**DoD:** pre-build — confirm the property is derivable from the diff, not semantic judgment; fallback is
flag-not-block. Both regions + suite-grep. audit-gates green. No bump. Migration: none.

**Effort M · risk M (M9 classification ambiguity → flag-not-block) · rollback: revert the script + gate.**

---

## PR 7 — Subagent-safe-guard authoring checklist/fixture (Phase 10)

**Delivers:** P9 (guard-escape-unreachable → tunnelled; shared-state collision). **Directly reinforced by
the live evidence** (Panel B's Write-placeholder-then-Edit tunnel this run). Independent — no dependency.

**Files (touches `plugins/knowledge/` → bump):**
- `plugins/ravenclaude-core/knowledge/subagent-safe-guard-checklist.md` (new) + a reusable **two-worktree
  fixture harness** a future guard's test file imports.
- `scripts/audit-gates.sh` — Gate 202 (generalize Gate 190's teeth over the guard set; Gate 190 header
  confirmed `:6259`).

**Gate build spec — Gate 202** (next-free). Every stateful `PreToolUse` guard must (a) declare its state
key + prove it varies per parallel agent (a 2-worktree fixture: worktree A's record must not block B),
(b) expose a **file-based escape** whose *refusal* paths (missing key, empty value, cross-scope control)
are tested before the success path. Gate 190's two-worktree teeth test (`:801` dispatcher / `:6259`
full-suite) is the template.
- must-fail: a guard keyed on `session_id` (not worktree) where A's negative blocks B → the 2-worktree
  fixture catches it (the v0.245.0 collision).
- must-fail: a guard whose only escape is an env var a `Bash` call can't pass to the hook process →
  flagged.
- audit remediation: run `runaway-brake.sh` counters + the thing runaway dirs through the checklist,
  pass/fail recorded, fixed if failing.
- **exit-2:** a guard failing the collision fixture is a genuine build blocker for its own merge, not
  advisory. **macOS:** bash-3.2-safe fixture using `git worktree add` (no GNU-only flags). **surfaces:**
  two independent instances asserted not to interfere. **SNR:** structurally satisfied (checklist + test
  harness, not a deny hook).

**Remediation of live-open:** no standing check asks whether any *other* guard's env-var escape is
reachable from a subprocess; the other session-keyed substrates haven't been audited.

**DoD:** both regions + suite-grep. **Version bump** (both mirrors). audit-gates green. Migration: none
(additive knowledge + a gate over existing guards).

**Effort M · risk L · rollback: revert the checklist + fixture harness + gate.**

---

## PR 8 — Constitution staleness linkage (Phase 13)

**Delivers:** P19 (stale claim in an every-session-loaded file). Independent.

**Files (touches `plugins/skills/` + `plugins/hooks/` → bump):**
- `plugins/ravenclaude-core/skills/knowledge-file-staleness-sweep/SKILL.md` — extend scope to the **root +
  plugin constitution files** (the highest-priority surface — loaded every session, exactly where the P19
  incident happened).
- a new advisory `PostToolUse` nudge hook (`plugins/ravenclaude-core/hooks/…`) — when a diff resolves a
  tracked "Still open / broken / TODO / FIXME" marker's subject (matched to Níðhöggr's superseded-decision
  signals), prompt to update the milestone entry in the same diff.
- `scripts/audit-gates.sh` — Gate 203 (fires-on-bad / silent-on-good).

**Gate build spec — Gate 203** (next-free), **advisory**:
- fires-on-bad: a diff flipping a "Still open" item's subject to done without superseding the milestone
  entry → advisory nudge.
- silent-on-good: the same diff that also supersedes → silent.
- **exit-2: N/A-by-design** — an advisory `PostToolUse` nudge; a blocking "you must update a milestone"
  gate would false-positive on legitimate work (M12 — state "advisory, not a control" in the header).
  **macOS:** bash-3.2-safe hook. **surfaces:** compares the diff's subject against the milestone's stated
  status. **SNR — RISK M1:** a "Still open" scanner over CLAUDE.md matches the very supersession notes;
  mitigate by matching a marker only when the same diff *resolves its subject elsewhere* + honor a
  `SUPERSEDED` in-line tag; `PostToolUse` timing means it never blocks, so it can't deny its own fix.

**Remediation of live-open:** run a fresh sweep of `CLAUDE.md`/`AGENTS.md`/plugin `CLAUDE.md` now
(MH-40 landed *after* the rule; 23 stale/overstated commits counted). Full closure needs a mandatory
decisions-log `supersedes:` frontmatter convention — **out of this PR's scope** (named, not silently
dropped).

**DoD:** both regions + suite-grep. **Version bump.** audit-gates green. Migration: none (advisory).

**Effort S–M · risk L · rollback: revert the SKILL scope + nudge hook + gate.**

---

## PR 9 — Contract-provenance lint (Phase 12) — advisory; built early because PR 11 composes it

**Delivers:** P15 (building-to-unverified-contract — honest partial). **Sequenced before PR 11 even though
it is P2-tier**, because PR 11 (host-capability lint) composes Phase 12's provenance-marker convention
(DAG: Phase 8 → Phase 12).

**Files (touches `plugins/hooks/` → bump):**
- `plugins/ravenclaude-core/hooks/claim-grounding-lint.sh` — extend the pattern set (reuse its existing
  stdin handling) to flag a capability/contract claim written into `knowledge/`/`docs/`/a generator without
  an inline provenance or `[docs-verified <date>]` marker.
- `scripts/audit-gates.sh` — **extend the existing claim-grounding gate** (no new number — it extends the
  gate that already covers `claim-grounding-lint.sh`).

**Gate build spec (extends existing gate), advisory:**
- fires-on-bad: a `knowledge/` file asserting an absolute capability claim with no marker → advisory nudge.
- silent-on-good: the same claim with `[docs-verified 2026-…]` → silent.
- suppression-honored: the already-shipped opt-out comment silences the nudge.
- **exit-2: N/A-by-design** — a `PostToolUse` nudge; a blocking prose-lint would false-positive on hedged
  prose (CL-20: a hook claiming full contract-verification would be false). **macOS:** bash-3.2-safe
  (extends the existing hook). **SNR — RISK M1:** a provenance lint over `docs/` can match a doc
  *documenting* an unverified claim; staying **advisory-only** sidesteps the trap; honor the marker as the
  exempt signal.

**Remediation of live-open:** run once against the current `knowledge/`/`docs/` tree to surface existing
unmarked capability claims (advisory list, not a build failure).

**DoD:** confirm the extension point absorbs a new check without duplicating stdin parsing; both regions +
suite-grep on the extended gate. **Version bump.** audit-gates green. Migration: none (advisory).

**Effort S · risk L (advisory — M12: state it's not a control) · rollback: revert the pattern-set
extension.**

---

## PR 10 — Behavioral canary as host-onboarding acceptance bar (Phase 6)

**Delivers:** P16 (install-wires-nothing), P18 (silent-disarm-on-update), contributes P17.
**OWNER-GATED — seed #5** (mandatory-vs-advisory). The mechanism builds regardless; the owner ratifies
whether the canary is a *hard* onboarding bar before it becomes mandatory.

**Files (touches `plugins/knowledge/` + `scripts/ravenclaude` + a `plugins/` helper → bump):**
- `scripts/ravenclaude` — add a **behavioral canary step at the end of each `--host` install** (trigger
  the host's real invocation path, confirm a planted marker fired — not a files-exist check; generalizing
  Gate 167's Copilot→tribunal round-trip).
- `plugins/ravenclaude-core/knowledge/host-support.json` — add a per-host `activation_gate` field
  (`hash_trust | version_floor | none`; the file already carries a per-component per-host schema —
  confirmed this session). **The gate that pins `host-support.json` (Gate 154, `:5514`) updates in the
  same commit** so the schema addition doesn't break its pin.
- a shared `_rc_rearm_notice` helper (`plugins/ravenclaude-core/hooks/` or `scripts/`) consumed at
  install/update/status (the Codex hash-trust + Copilot version-floor retrofits become one abstraction).
- `scripts/audit-gates.sh` — Gate 204 + must-fail halves.

**Gate build spec — Gate 204** (next-free):
- must-fail: an installer mutant that reports success while the planted marker never fires → the canary
  MUST catch it (the MH-07 "wires nothing, says nothing" shape).
- must-fail: a host with `activation_gate: hash_trust` whose re-arm notice is stripped on `update` →
  caught.
- pass-on-good: the existing Codex + Copilot lanes (canary-proven per Gate 167, `:5820`) pass under the
  generalized mechanism.
- remediation: re-verify **MH-05** (whether every affected dashboard panel got the honest-empty-state +
  the host-verdict banner landed — not re-verified) and record the result (close or re-ticket).
- **exit-2:** a host lane whose canary can't be confirmed to fire ships as unsupported in
  `host-support.json`, not silently assumed working. **macOS:** bash-3.2-safe installer + Python helper;
  reuse `_portable.sh` where the canary needs a bounded timeout (`_rc_timeout`). **surfaces:** the canary
  asserts the host's *real runtime behavior* against a *planted marker* — the strongest
  surfaces-against-each-other form. **SNR:** structurally satisfied (installer-time canary).
- **M10 honest limit:** live-host behavior may not be exercisable in CI (Gate 20/167 limitation) — gate the
  adapter I/O + planted-marker round-trip (which IS gateable), accept that live-host behavior stays
  owner-verified, state the limit.

**DoD:** confirm the `host-support.json` schema addition doesn't break Gate 154's pin. Both regions +
suite-grep. **Owner ratifies mandatory-vs-advisory (seed #5) before it becomes a hard bar** — record the
ruling in `docs/decisions/`. **Version bump.** audit-gates green. Migration: none unless the owner makes it
mandatory (then note the per-host onboarding cost).

**Effort M–L · risk M (M10 live-host un-exercisable in CI) · rollback: revert the canary step + the
`activation_gate` field + the helper + gate.**

---

## PR 11 — Host-capability lint + adapter round-trip gate (Phase 8)

**Delivers:** P17 (cross-host projection drift / adapter payload loss). **Depends on PR 10** (composes the
`activation_gate` field) **and PR 9** (composes the provenance-marker convention). Builds the P17
host-scope-sentence parity that Phase 4 *named* — **built exactly once, here.**

**Files (no `plugins/` change unless the MH-28 fix lands in `plugins/` — see remediation → conditional bump):**
- `scripts/check-host-support.py` (extend Gate 154 to scan generator output for literal host-name+capability
  strings not traceable to a `host-support.json` lookup).
- `scripts/check-host-capability-citations.py` (new — a `check-frontmatter.py` sibling) — scans generator
  output + hand-written `knowledge/`/`docs/` prose for a host name adjacent to a supported/unsupported/native
  verb without a dated basis or `host-support.json` cross-ref (the MH-03 uncited-claim shape). **Hard-fail
  (exit 2) ONLY where a `host-support.json` cross-ref exists to gate against** (generator output + any
  `knowledge/` claim resolvable to the SSOT); an un-marked claim in free-form `docs/` prose with no
  resolvable cross-ref is an **advisory nudge, NOT a build failure** (the design corrected an
  over-broad-Goal ambiguity here — do NOT build the hard-blocking `docs/`-prose scanner).
- a standing **adapter round-trip gate** per host (deny + reason must survive translation), generalizing
  Gate 167 — closing the v0.250.0 "adapters kept the deny, threw away the reason" regression.
- `scripts/audit-gates.sh` — Gate 205 + must-fail halves.

**Gate build spec — Gate 205** (next-free):
- must-fail: a generated manifest listing slash commands on a host the plugin says has none (MH-27) →
  exit 2.
- must-fail: an uncited "host X reads file Y" claim with no dated basis, **in generator output or a
  `knowledge/` file where a cross-ref exists** → exit 2. (A free-form `docs/`-prose claim is advisory.)
- must-fail: an adapter mutant that drops the deny reason → the round-trip gate catches it.
- pass-on-good: the current already-corrected `AGENTS.md` host table with dated per-row basis.
- **exit-2** where a deterministic `host-support.json` oracle backs the check; **advisory** over free-form
  `docs/` prose (the `[SNR]` line concedes this — "exit 2 on *any* uncited host claim" would over-claim).
  **macOS:** Python 3.9 stdlib, `from __future__ import annotations`. **surfaces:** host-scope sentences
  asserted against `host-support.json` (the SSOT), never a hand-typed constant. **SNR — partial RISK:** the
  citation lint could match a sentence *documenting* a false claim it retracts; honor an inline
  `[docs-verified <date>]`/`[unverified]` marker as exempt; scope to un-marked absolute claims; residual
  advisory for the `docs/` subset.

**Remediation of live-open:** fix **MH-28** (the claim-grounding fix survives at two call sites the fix did
not reach — locate + fix them; **if these are in `plugins/`, this PR requires a version bump**); no gate
fails a build on an uncited host-capability claim traceable to the SSOT (a free-form `docs/`-only claim
stays advisory).

**DoD:** depends on PR 9 + PR 10 landing. Both regions + suite-grep. audit-gates green. Version bump **iff**
the MH-28 fix touches `plugins/`. Migration: none.

**Effort M · risk M · rollback: revert the two scripts + gate; the MH-28 call-site fixes revert
independently.**

---

## PR 12 — Count-SSOT DROP refactor (Phase 5)

**Delivers:** P13 (count/version-mirror drift), shrinks P14, contributes P17/P19. **OWNER-GATED — Fork 1
(RC_BASELINE).** The plan pair has converged; this PR **holds its DROP build** until the owner rules
Fork 1 (the direction determines whether an independent-scanner is built at all).

**Files (massive `plugins/` change → version bump every touched plugin + marketplace mirror):**
- ~180 `plugin.json` descriptions + their `marketplace.json` mirrors + ~180 README count tables (DROP the
  granular per-artifact count literals; keep self-evident enumerations — the roster `agents (a, b, c…)`
  carries no standalone digit).
- `scripts/count-core-sections.py` (new — **only if** the independent-scanner option is chosen in Fork 1).
- `scripts/check-marketplace-claims.py` (add the negative-assertion gate; extend the **2/6 → all 6** count
  types — measured this session at the checker).
- `scripts/check-plugin-detail-render.mjs:54` (de-hardcode `RC_BASELINE` — confirmed the literal is there).
- `scripts/audit-gates.sh` — Gate 206.

**Gate build spec — Gate 206** (next-free), **negative-assertion**: no description may contain a digit
immediately followed by an agents/skills/templates/commands/hooks/rules word; fails **closed**; doubles as
a migration-completeness proof (stronger than a freshness gate — DROP makes the class impossible by
construction).
- must-fail: a `plugin.json` description reintroducing a count literal → exit 2.
- must-fail (independent-scanner option only): a fixture proving the independent scanner and the render's
  `scan_repo` **can** diverge (not a tautology — the load-bearing non-collusion property; M7). Computing
  the baseline from the generator's own `scan_repo` is a **forbidden tautology** (the one settled point).
- **owner-decision pre-build gate:** the RC_BASELINE ruling recorded in `docs/decisions/` **before** the
  DROP build begins. **exit-2** on any surviving literal. **macOS:** Python 3.9 stdlib scanners.
  **surfaces:** the independent-scanner-vs-`scan_repo` cross-check IS the assert-against-each-other prior;
  keep-golden forgoes it (a golden literal is a constant — the R2 anti-pattern, the substance of Fork 1).
  **SNR:** n/a — the negative gate matches consumer-read description prose being forbidden (no fix/test to
  falsely deny).

**Remediation of live-open:** the checker verifies only 2/6 counted quantities; ~180 README tables have
zero coverage; the Copilot verbatim-inheritance channel (`generate-copilot-plugin.py:421`) stays open
until core's description drops the count. The DROP eliminates the class by construction.

**DoD:** Fork 1 ruled + recorded first. Whole-tree prettier (JSON) + ruff. The negative gate both regions +
suite-grep. **Version bump every touched plugin + marketplace mirror** (CI fails on drift). audit-gates
green. **Migration note (consumer-visible — the second of two):** the DROP changes ~180 descriptions; add
an explicit migration section.

**Effort L (highest cost — ~180×3 surfaces) · risk M6 (repo-wide change — the negative gate + owner gate +
whole-tree prettier mitigate) + M7 (tautology if independent-scanner mis-maintained — the divergence
fixture guards it) · rollback: revert the DROP (large diff — do it as one squash so revert is clean).**

---

## PR 13 — Self-heal push-safety invariant (Phase 7)

**Delivers:** P14 (self-heal / generated-artifact cascade). Independent of PR 12's timeline (PR 12's DROP
is the durable fix; this is the point-fix that holds until it lands).

**Files (no `plugins/` change → no bump):**
- `scripts/check-selfheal-push-safety.py` (new — greps self-heal workflows for a direct-to-`main` push
  path).
- `.github/workflows/regenerate-artifacts.yml` (post-heal freshness re-check step on the opened PR head).
- `scripts/audit-gates.sh` — Gate 207.

**Gate build spec — Gate 207** (next-free). Assert a self-heal workflow has **no direct-to-`main` push
path** — it already uses the create-pull-request action on `chore/self-heal-artifacts` (`:372`/`:386`),
but nothing gates a regression. **Honest bound (state in the script header):** this is a **proxy-string
scan, not a behavioral proof** — the runtime guarantee is the branch-protection ruleset (`:358`,
`:367–369`: direct push to `main` rejected by the ruleset; the workflow lands on `main` *only* via its
auto-merged PR at `:416–424`). The scan is defense-in-depth catching the enumerated literal push shapes at
PR-review time; it **cannot** see a computed-ref push, a `gh api` commit, or an admin-merge bypass — so it
is **paired with the ruleset, never a replacement.**
- must-fail: a workflow fixture reintroducing a direct-to-`main` push in **each enumerated shape** (the
  plain push-to-main, the `HEAD:main` form, the `:refs/heads/main` form, and an admin-merge bypass) — each
  → exit 2 (a single-literal fixture would leave the other shapes uncaught — the P8 trap inside this very
  check).
- pass-on-good: the current PR-only workflow (the auto-merged-PR path at `:416–424` is NOT flagged — it
  lands via the ruleset's required checks, not a push).
- hermeticity: a self-heal run against a known-stale tree — the post-run freshness check on the PR head
  must pass (proving the self-heal fixed what it claims, not an empty PR).
- **exit-2:** a workflow the checker can't parse fails the check, not passes. **macOS:** pure Python YAML
  text parse. **surfaces:** the freshness re-check on the PR head (not the pre-self-heal state) is a
  surfaces-against-each-other assertion. **SNR — small RISK M1:** the workflow-grep could match a
  push-to-main token inside a *comment* explaining the rule (the file has such prose at `:367`); mitigate
  by matching only an un-commented `run:`-line push + the `# noport`-style sentinel; the clean fix is PR 17.

**Remediation of live-open:** the cascade recurs faster than the count-SSOT refactor lands; this adds the
standing invariant the inventory notes is missing.

**DoD:** both regions + suite-grep. (May not need PR 1's parse — a text-scan over workflow YAML is simpler;
a genuine "no dependency" case.) audit-gates green. No bump. Migration: none.

**Effort S–M · risk L · rollback: revert the script + workflow step + gate.**

---

## PR 14 — Self-certifying-change flag (Phase 14)

**Delivers:** P10 (gate re-authored with its target). Entirely preventive. **Soft dependency on PR 1's
gate-boundary parse** (could ship with a cruder heuristic at lower precision if PR 1 slipped — it won't,
PR 1 is first).

**Files (no `plugins/` change → no bump):**
- `scripts/check-self-certifying-change.py` (new — maps gate→target from a small declared manifest).
- a CI step (advisory comment) in an existing workflow.
- `scripts/audit-gates.sh` — Gate 208.

**Gate build spec — Gate 208** (next-free), **advisory flag, not a block**: flag any PR touching **both**
a gate-defining region of `audit-gates.sh` and the source path that gate exists to check — requiring an
independent/external oracle (Gate 51's unchanged-selftest pattern) or an explicit reviewer sign-off.
- fires-on-bad: a PR diff touching a gate's checker AND the source it targets, with no external-oracle
  change → flag.
- silent-on-good: a PR that changes the source but leaves the external oracle (e.g.
  `check-shell-router.selftest.mjs`) untouched → no flag.
- **exit-2: N/A-by-design** — a flag, not a gate; a hard block would stop the many legitimate co-changes
  (M12). **macOS:** Python 3.9 stdlib over `git diff --name-only`. **surfaces:** asserts the gate-change
  against the target-change (two paths in one diff). **SNR:** structurally satisfied (diff-name analysis).

**DoD:** both regions + suite-grep; soft dep on PR 1's parse. audit-gates green. No bump. Migration: none.

**Effort S · risk L · rollback: revert the script + CI step + gate.**

---

## PR 15 — Corpus-scale plausibility checklist (Phase 15)

**Delivers:** P20 (checklist half). Mostly folded with the Phase-0 docs commit (the cross-link shipped
there); this PR is the checklist-as-required-step in the new-checker workflow doc, if not already banked.

**Files (docs → straight to `main` unless it edits `audit-gates.sh`):**
- a checklist section in the new-checker workflow doc + reference to
  `docs/best-practices/validating-a-measuring-instrument.md`.
- (the cross-link is gateable via existing Gate 29 md-links — no new gate).

**Gate build spec:** none new — the cross-link is enforced by Gate 29 (a resolvable markdown link, not a
backtick path). The checklist is a doc discipline (honestly not machine-gated beyond the cross-link); its
teeth are the mutation-test-between-clean-passes ritual each new checker's own gate carries.

**DoD:** md-links gate green. No bump (docs). Migration: none.

**Effort S · risk none · rollback: revert the doc section.**

---

## PR 16 — DOM-budget ratchet formalization (Phase 16)

**Delivers:** P21 (DOM-budget ratchet friction). **Lowest priority — seed #6, owner may defer this PR
entirely.**

**Files (touches the dashboard generator → generates `plugins/ravenclaude-core/dashboard.html` → bump):**
- the dashboard generator (`scripts/generate-dashboards.py`) — emit any doc sentence citing a gate's live
  numeric state from the gate's own output rather than typing it as static prose (the MH-40
  stale-gate-state half of P19, folded here).
- optionally a `docs/decisions/` raise-request/tracking record convention for the Gate 132 ratchet.
- `scripts/audit-gates.sh` — Gate 209.

**Gate build spec — Gate 209** (next-free):
- generated-not-typed: a fixture proving the gate-state sentence is rendered from the gate's live count,
  not a hardcoded literal (a hand-edited stale number is caught).
- **exit-2: N/A** (process-friction). **macOS:** generator is Python 3.9. **contract:** Gate 132's ratchet
  (`:406`/`:5192`) + the MH-40 stale-prose incident. **SNR:** n/a.

**DoD:** the existing dashboard freshness gate + the new gate. **Version bump** (`dashboard.html`
regenerates). audit-gates green. Migration: none.

**Effort S · risk L · rollback: revert the generator change + gate. Owner may skip this PR entirely.**

---

## PR 17 — Widened sanctioned-escape door (Phase 11 Half B)

**Delivers:** P7 (durable fix — the sanctioned path Phases 2/7/8/9/12/13 depend on to fully retire their
SNR residual). **OWNER-GATED — Fork 2 (fund the security review).** Ships **only after a `security-reviewer`
red-team pass on the widened ignore-surface** — the repo's own stated reason for twice-deferring it (CL-22).
This PR **waits on the Fork 2 ruling AND a cleared red-team** before its build step begins.

**Files (touches `plugins/hooks/` → bump):**
- `plugins/ravenclaude-core/hooks/guard-destructive.sh` / the hard-rule guards — the exempt-path or
  in-file sentinel (the security-reviewed part). The chosen shape is Fork 2's owner decision among: (a)
  prefix allowlist `tests/fixtures/**` + `docs/**`; (b) in-file sentinel marker (per-line intent,
  narrower); (c) diff-scoped exemption re-evaluated per edit; (d) keep the `printf`/prose workaround
  (zero new surface). This plan does NOT pre-empt the red-team's verdict on which shape is safe.
- `scripts/audit-gates.sh` — Gate 210 (proves the exempt path does NOT let a *live* dangerous command
  through — the red-team's teeth).

**Gate build spec — Gate 210** (next-free):
- must-fail (red-team): an attacker planting the exemption marker/path to smuggle a *live* dangerous
  command (a force-push to a protected branch, a fetch-piped-into-a-shell — described here in prose, never
  literal syntax) MUST still be DENIED — the exemption downgrades a *documented* pattern in a fixture/doc,
  never a live command.
- must-fail → must-pass (false-positive): a Write of a `docs/`-tier plan citing a forbidden command in
  prose (like this very file), and a `.ravenclaude/runs/**` Write in a nested worktree, and the same
  content via `Edit`, must NOT be denied.
- **exit-2:** the exemption NEVER downgrades a live dangerous command — a fixture/doc match → advisory, a
  live-command match still denies exit 2 (fail-closed preserved). **macOS:** bash-3.2-safe guard edits.
  **SNR:** this IS the self-non-recursion fix. **RISK M2:** it widens what the guards ignore; the red-team
  gate is the control that keeps the widening sound — the non-negotiable pre-build gate.

**DoD:** **Fork 2 ruled + `security-reviewer` sign-off recorded** before it ships. Both regions +
suite-grep. **Version bump.** audit-gates green. Migration: none (the exempt path only *narrows* denials of
documented patterns; live commands still deny). Once landed, the source-scan PRs (3/6/8/9/11/13 — the
Phase 2/7/8/9/12/13 translation, per PR 2's SNR line above; **not** PR 2 itself) can retire their
`# noport`/`printf` SNR workaround.

**Effort M · risk Critical-if-ungated (M2 — the red-team gate is the control; Half A in PR 2 already
carries no widened surface and shipped without this gate) · rollback: revert the exempt path + gate; the
guards revert to the printf/prose workaround.**

---

## Sequencing / DAG

```
Docs commit (Ph 0 + Ph 15 doc) ── straight to main, ships same day (independent)

PR 1  Keystone meta-gate (Ph 1)  ── MUST BE FIRST
  │   its 2 gates guard every later gate; its audit-gates parse is IMPORTED by PR 4/6/14
  ├─────────────► PR 4  exit-code audit (Ph 3)   [also needs PR 3]
  ├─────────────► PR 6  catalog-scoping (Ph 9)   [reuses regex-compile primitive]
  └─────────────► PR 14 self-cert flag (Ph 14, P10) [soft: gate-boundary parse]

PR 2  Premise-guard scope fix (Ph 11-A)  ── P0, no owner gate, ships right after keystone
  │   reprioritized by live evidence; reduces guard false-positives for ALL later source-scan PRs
PR 3  Portability lint (Ph 2)  ── P0 [Fork 3 sets posture default] ──► PR 4 (its hook is an audit target)

PR 5  Surface-parity (Ph 4, P11/P12) ── independent
PR 7  Subagent-guard checklist (Ph 10, P9) ── independent
PR 8  Constitution staleness (Ph 13, P19) ── independent
PR 9  Provenance lint (Ph 12, P15) ──┐ (composed by PR 11)
PR 10 Behavioral canary (Ph 6) [seed#5] ──┤──► PR 11 host-capability lint (Ph 8, P17)
PR 12 Count-SSOT DROP (Ph 5) [Fork 1] ── shrinks ──► PR 13 (self-heal, soft)
PR 13 Self-heal push-safety (Ph 7, P14) ── independent
PR 15 Corpus-scale checklist (Ph 15, P20) ── independent (mostly in the docs commit)
PR 16 DOM-budget (Ph 16, P21) [owner-optional] ── independent

PR 17 Widened escape door (Ph 11-B) [Fork 2 red-team] ── SHARED dep of the source-scan PRs (3/6/8/9/11/13)
      NOT PR 2 (PR 2 uses guard-premise.sh's EXISTING escape, not this widened door — see PR 2's SNR line)
      they ship with the printf/# noport workaround WITHOUT PR 17, and retire their SNR residual once it lands
```

**Keystone-first rationale (both panel framings, kept):** PR 1 is the only hard-first node and it is
dual-purpose. As **keystone** (Panel A), every later gate should be verified reachable + exit-2-specific by
it, so it landing first means each subsequent gate inherits a standing proof it isn't the next Gate 184. As
**shared primitive** (Panel B), its parse is a hard import dependency of PR 4 and a reuse dependency of
PR 6/PR 14 — building the parse twice recreates R2 *inside the plan*. If PR 1 ever slipped, the fallback is
the manual "grep the suite output by name" ritual (`:6119`) every PR already commits to.

**The genuinely hard dependencies are few:** PR 4 → {PR 1, PR 3}; PR 11 → {PR 9, PR 10}; PR 12 → Fork 1;
PR 17 → Fork 2. Everything else parallelizes once PR 1 is in flight (PR 3 and PR 4 share only the
`validate-macos.yml`/`validate-marketplace.yml` runners and should land in sequence to avoid a merge race).

**Critical path (longest):** PR 1 → PR 3 → PR 4 → (retire the SNR residual via PR 17 after the red-team) →
done. The highest single-cost item, **PR 12**, gates nothing else and runs on its own track once Fork 1 is
ruled.

---

## Owner-gated PRs (each waits on an owner ruling before its build step begins)

Record the ruling — even "defer" — in a `docs/decisions/` entry before the gated build step begins, so the
build never stalls silently.

| PR | Design fork/seed | What the owner settles | Recommended lean (from the plan) | What the ruling gates |
|---|---|---|---|---|
| **PR 3** | **Fork 3** (seed #3) | (a) default posture `warn` vs `block`; (b) scope `hooks/**`-only vs **wide** | `warn` + **wide** (#885/#873 broke *outside* `hooks/**`) | Only the **config default**; the mechanism builds regardless — a *soft* gate. |
| **PR 10** | **seed #5** | Is the canary a **mandatory** host-onboarding bar or advisory? | mandatory (class found on two hosts) | Whether the canary is a *hard* acceptance gate for future host lanes. |
| **PR 12** | **Fork 1** (seed #1) | RC_BASELINE direction: (a) DROP+independent-scanner / (b) hybrid / (c) keep-golden | (a) DROP+independent-scanner (Panel A) or (b) hybrid (Panel B) — owner call | The **DROP build itself** — a hard gate; hold the ~180-surface edit until ruled. |
| **PR 17** | **Fork 2** (seed #2) | Fund the `security-reviewer` red-team now? + which exempt shape (a/b/c/d) | fund it now (bit the run ≥4×); shape is the red-team's call | The **entire PR** — a hard gate; no Half-B merge without a cleared red-team. |
| — (defer) | **seed #6** | DOM-budget ratchet — formalize or leave ad-hoc? | lowest priority; may defer PR 16 entirely | Whether **PR 16** is in scope this cycle. |
| — (scope) | **decision #7** | Is the advisory tail (PR 9/PR 8/PR 14) worth building though not a control? | yes — the durable-artifact false claim is exactly what a stale note did twice | Whether PR 8/9/14 are in scope. |

**PR 2 (Half A) is explicitly NOT owner-gated** and ships now — it carries no widened surface.

---

## Build-time verification checklist (this initiative's own lessons, applied to the build itself)

Run this per PR that adds a gate — it is the six-part teeth test made operational:

1. **Grep the full-suite output for the new gate BY NAME** after registering it (`:6119` ritual). A gate
   absent from the suite output was never wired — the Gate-184 class this whole initiative exists to catch.
   Confirm the **assertion-count delta** equals the number of gates added.
2. **Register in BOTH regions:** the `--check` dispatcher case + the `Supported:` string (`:877`) + the
   unconditional full-suite region (after `:881`). Once PR 1 lands, `check-gate-registration.py` enforces
   this automatically — but check it by hand on PR 1 itself (it can't self-check before it exists).
3. **Confirm the deny path is exit 2, not merely nonzero** (`:1046–1048` template) — a crash (exit 1) or a
   swallowed error is a counterfeit deny (Gate 6 lesson). For an advisory gate, confirm exit-2 is
   **N/A-by-design** and say so in the script header (M12).
4. **macOS-portability check:** the new script is bash-3.2-safe / Python-3.9-stdlib — no `declare -A`,
   `mapfile`, `${x^^}`, `shopt -s globstar`, GNU-`timeout`, PCRE-`grep`, in-place `sed`, GNU-`find`; route
   any shimmed need through `_portable.sh`; Python carries `from __future__ import annotations` (the
   PEP-604 door — CI is 3.10+, so this fails only on a stock-macOS local run). Run PR 3/PR 4 on
   `macos-latest`.
5. **M5 pre-build dry-run:** run every new text-scan/lint report-only against the CURRENT real tree; confirm
   **zero unexpected findings** before flipping it to blocking. A gate that floods the suite day-one gets
   disabled — the fate the posture doc names (this bit PR 1's keystone hardest, hence its explicit dry-run).
6. **Deterministic-grep any citation/count the PR touches:** if a PR asserts a `file:line` or a gate number,
   re-derive it against the then-current tree (gate numbers drift — this IS P3; the Gate-51-was-"Gate-144"
   drift is the worked example).
7. **SNR check for a real deny hook / prose scanner:** confirm the exempt-path (`# noport` sentinel +
   `tests/fixtures/**`/`docs/**` allowlist) + `printf`-assembled fixtures + prose-not-literal descriptions
   are present up front (M1), not discovered later — this applies to the genuine `PreToolUse` deny hook
   (PR 3) and the prose/source-scanning lints that carry SNR **RISK** per their own Gate build spec (PR
   6/8/9/11/13 — the Phase 9/13/12/8/7 translation), all of which depend on PR 17 for the durable fix (the
   corrected source-scan set from PR 17's DoD above). **Do NOT read "no `PreToolUse` deny surface" as "no
   SNR risk"** — PR 6/8/9/11/13 are CI readers (no Write/Edit they can deny) yet still source-scan text and
   so still carry the RISK, exactly the confusion the design's §2 reconciled note warns against. A pure CI
   reader with no source-scan surface at all (PR 1/4/5/7/10/14 — each individually tagged "structurally
   satisfied" in its own Gate build spec — plus the differently-`n/a`-tagged PR 12/15/16) satisfies SNR
   structurally and needs only step-3's N/A note.
8. **Anti-tunnel discipline while building:** if a guard denies a legitimate build Write (as
   `xc.tribunal-self-disable` denied a citation-verifying read of `concerns-catalog.md` **this session**,
   and as `guard-premise.sh` denied the first Write of this very file), reword to prose / past tense, split
   the file, or record the denial — **never** a Write-placeholder-then-Edit, a Bash-heredoc, or any
   tool-switch to evade the matcher.

---

## Coverage — every P1–P21 → the PR(s) that build its prevention + remediation

| P# | Class | Prevention PR | Remediation-of-live-open PR |
|---|---|---|---|
| **P1** | macOS / stock-toolchain doors | **PR 3** (author-time portability lint) | PR 3 (lint the tree; #885/#873 residue; packaging move of `premise-gate.py`/`classify_claim.py`/`check-design-schema.py`, scoped + verified by Gate 187's `_DEFERRED_PACKAGING` removal, not a fixed count) |
| **P2** | never-ran / mis-wired gate | **PR 1** (reachability sub-check) | PR 1 (run against current `audit-gates.sh` at merge) |
| **P3** | gate-number collision + self-desc drift | **PR 1** (number-uniqueness + `Supported:` cross-check) | PR 1 |
| **P4** | hollow gate (input silently empties) | **PR 1** (UNWIRED doc convention — honest partial) | PR 1 + doc (generalize Gate 179; ~194-gate retrofit explicitly NOT done) |
| **P5** | exit-code severity / fail-open-on-error | **PR 4** (exit-code execution audit) + **PR 1** (exit-2 clause) | PR 4 (drive every enforcement hook; audit the C4 rewrite trap beyond `thing-orchestrator.sh`) |
| **P6** | malformed regex silently disables a rule | **PR 1** (regex-compile primitive) + **PR 6** (catalog rollout) | PR 1 (comfort-posture hard-rule catalog's first standing recompile) |
| **P7** | self-referential guard denies own fix/test/docs | **PR 17** (widened exempt door — Fork 2) | **PR 2** (nested-worktree exemption + Write-scoped-matcher fix + `xc.tribunal-self-disable` read/mutate discriminator — the live this-run instance, incl. incidents (c)/(d) and this file's own denial) |
| **P8** | fix-one-instance / unscoped-regex-beside-scoped | **PR 6** (catalog-scoping-consistency lint) | PR 6 (grep the catalog for remaining unscoped wildcards) |
| **P9** | guard escape unreachable → tunnelled; shared-state | **PR 7** (subagent-safe-guard checklist/fixture) | PR 7 (audit runaway-brake, thing runaway dirs) + PR 2 (contributes) |
| **P10** | self-certifying change | **PR 14** (self-cert flag) | PR 14 |
| **P11** | presence-not-placement cross-surface regression | **PR 5** (surface-parity gate) | PR 5 (generalize Gate 51 over full route set) |
| **P12** | twin-server behavioral drift | **PR 5** (behavioral-parity variant) | PR 5 (or eliminate the twin via shared import — PR 5 note, bumps if built) |
| **P13** | count / version-mirror drift | **PR 12** (count-SSOT DROP) | PR 12 (drop ~180×3 literals; gate 4 ungated count types + ~180 README tables) |
| **P14** | self-heal / generated-artifact cascade | **PR 13** (self-heal push-safety invariant) | PR 13 (assert no direct-to-`main` push; post-heal freshness re-check on PR head) |
| **P15** | building to an unverified contract | **PR 9** (contract-provenance lint — honest partial) | PR 9 (durable-artifact subset only; reasoning-bound) |
| **P16** | install completes / wires nothing | **PR 10** (behavioral canary) | PR 10 (re-verify MH-05 dashboard empty-states + host-verdict banner) |
| **P17** | cross-host projection drift / adapter payload loss | **PR 11** (host-capability lint + adapter round-trip) + PR 5/10/12 | PR 11 (fix MH-28 two-call-site residue; uncited host claims) |
| **P18** | silent disarm on update (hash-trust / version-floor) | **PR 10** (`activation_gate` field + shared re-arm helper) | PR 10 |
| **P19** | stale claim in an every-session-loaded file | **PR 8** (staleness-linkage + supersession nudge) | PR 8 (sweep constitution files) |
| **P20** | corpus-scale measuring-instrument invalidity | **Docs commit** (cross-link) + **PR 15** (plausibility checklist) | Docs commit (one-line cross-link — immediate win) |
| **P21** | DOM-budget ratchet friction | **PR 16** (generate gate-state prose; raise-request record) | PR 16 (lowest priority; owner may defer) |

**Every class P1–P21 has both a prevention PR and a remediation PR. None dropped.** The two honest partials
(P4 doc-convention-only; P15 durable-artifact-subset-only) and the two named-but-not-built residuals (the
~194-gate UNWIRED retrofit; the twin-server shared-import elimination) are stated as scope limits inside
their PRs, not silently omitted.

---

## Whole-initiative DoD (from the design, restated as PR-completion gates)

1. Every P0/P1 PR shipped with its acceptance tests passing in the full suite, gated by name (checklist §1).
2. Fork 1 (PR 12) and Fork 2 (PR 17) have owner rulings on record — even if the ruling is "defer".
3. The Coverage table above shows every class P1–P21 with a shipped mechanism or an explicit dated
   "deferred, owner-ruled" annotation — no class silently falls off.
4. A fresh run of PR 1's `check-gate-registration.py` **and** PR 8's constitution-staleness sweep, both
   against the tree *after every other PR has shipped*, come back clean — proving the mechanisms hold after
   the plan's own churn, not just on day one.

**Per-PR DoD (unless noted):** each new gate registered in **both** regions with a proven must-fail half +
suite-grep + assertion-count delta; M5 pre-build dry-run for every text-scan; `prettier --write . &&
prettier --check .` (exit 0) + `python3 -m pip install --user ruff && ruff check .` (exit 0) before every
push; `scripts/audit-gates.sh` green incl. the new gate's own audit; **version bump** (both `plugin.json`
+ `marketplace.json` mirror) **iff** a `plugins/**` file changed — PR 2/3/7/8/9/10/12/16/17 bump, PR
1/4/5/6/13/14 do not (PR 11 bumps only if the MH-28 fix lands in `plugins/`); a migration note where a
shipped plugin file changes (most are "none — additive/fail-safe"; **PR 3's in-loop deny and PR 12's DROP
are the two consumer-visible ones** and get explicit migration sections); docs (Ph 0/15) commit straight to
`main`; no new `.repo-layout.json` globs needed (verified).
