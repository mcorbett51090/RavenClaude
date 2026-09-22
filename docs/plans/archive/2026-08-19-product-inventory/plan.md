# G6 — plan.md: RavenClaude product inventory + efficacy harness

**Status:** authoritative synthesis. Supersedes `plan-A.md` and `plan-B.md`. Where this document
conflicts with either panel plan, this document wins. Adjudicated rulings R1–R12 are encoded below
and are **not open for re-litigation** — each is tagged at the point where it lands.

Inputs read in full: `scope.md`, `claims-table.md` (incl. settled rows 14/15), `plan-A.md`,
`plan-B.md`, `gap-delta.md`, `critic-brief.md`, `red-team.md`.

Every `depends_on_claims:` line is machine-read and contains **clean numeric row ids only**
(⛔ R11 — prose in that field tripped the premise gate twice and made it cite non-existent rows).

---

## 0. The one-paragraph position

The most important result of this run is not a plan for an inventory. It is the critic's
correlated-error finding: **the motivating failure is a TEST-ASSERTION gap, not a documentation
gap, and it is still open in this repo today.** Both panels reasoned about documenting features
while the defect class that started the project remained live — 8 hooks still write advisories no
consumer receives, and of 56 hook tests, 5 assert `additionalContext` and **zero** assert
`updatedToolOutput`. Nothing in the existing suite asserts that a hook's output reaches the model.
So Phase 0 closes that, before one inventory entry is authored (⛔ R1).

After that, the build is sequenced by value density, not by coverage arithmetic. **The harness
carries nearly all the value and needs zero entries to run** — a 10-line reference resolver already
found two real dangling `SKILL.md` references with a negative control, and in both panel plans that
same check sat behind authoring 54 skill entries first. So the harness is keyed by **artifact path**,
not by concept id, and ships first. Then the **inception ratchet** — an added artifact not named in
any `covers[]` fails the build — which is what actually delivers the owner's "inventory all the
features" goal: coverage grows monotonically and cannot regress, so completeness becomes a forcing
function instead of a 90–110-hour authoring sprint that has a ~20% chance of finishing (⛔ R2).
Then ~20 mechanism entries at the owner's bar. The long tail accretes behind the ratchet.

The owner's goal is **not dropped**. It is reached by a different mechanism, on a longer clock, with
value landing in week 1 instead of month 6. §12 states the honest total and the coverage curve.

---

## 1. Ground-truth ledger — every load-bearing fact, with its anchor

Re-verified in this worktree during synthesis. A fact without an anchor is not in this table.

| # | Fact | Anchor |
|---|---|---|
| GT1 | Staleness gate has a **double exemption**: `if c["kind"] != "platform-fact" or not c["last_verified"]: continue` — a concept escapes if it is not a platform-fact **OR** simply lacks the field | `scripts/concepts.py:276` (⛔ R3) |
| GT2 | Corpus is **41 `ravenclaude-built` vs 17 `platform-fact`** — the gate covers the MINORITY kind | claims-table row 2 + kind census |
| GT3 | `--check` **short-circuits**: `_staleness_violations` returns 1 before the registry-freshness comparison is ever reached | `scripts/concepts.py:301-305` (⛔ R4b) |
| GT4 | Post-merge self-heal greps the **literal string** `staleness gate FAILED`; on no match it runs `exit "$_crc"` and kills every later self-heal step | `.github/workflows/regenerate-artifacts.yml:198`, `:203` (⛔ R4a) |
| GT5 | The workflow's own comment records the incident this re-arms: *"left main UN-HEALED across many merges"* | `regenerate-artifacts.yml:183-191` |
| GT6 | **T-PROSE fires only on file CREATE** — `if os.path.exists(path): sys.exit(0)` runs immediately after the T-PROSE scan | `plugins/ravenclaude-core/hooks/guard-premise.sh:459` (⛔ R10) |
| GT7 | **56 hook test files**; **5** assert `additionalContext`; **0** assert `updatedToolOutput` | `plugins/ravenclaude-core/hooks/tests/*.sh` |
| GT8 | **8 genuinely exposed advisory hooks** — write stderr, never exit 2, no delivered channel. All 8 confirmed present on disk | see §2.1 |
| GT9 | `panel-learn` is **already DOM-islanded**; islanded panels cost a flat 2 elements; the 23,861-element payload is `--report`-only and gated by nothing in `check()` | `scripts/check-dom-budget.py:104,128,793,805` (⛔ R5) |
| GT10 | 58 concept files; registry at `plugins/ravenclaude-core/concepts.json` | `scripts/concepts.py:34`, `knowledge/concepts/` census |
| GT11 | `concepts.py --check` runs on every PR under `set -e` | `.github/workflows/validate-marketplace.yml:418` |
| GT12 | `.repo-layout.json` already allows `plugins/*/knowledge/**`, `plugins/*/scripts/**`, `plugins/*/bin/**`, `tests/fixtures/**` — **no layout edit is needed anywhere in this plan** | `.repo-layout.json:14,68,79,80` |
| GT13 | A 10-line reference resolver over 54 `SKILL.md` files found 2 real dangling refs (`webfetch-hardening` → a knowledge file that does not exist; `cross-platform-determinism` → `scripts/generate-repo-guide.py`, absent), with a negative control that correctly false-positived on a repo-root-relative form | critic V10 |
| GT14 | PR #991 precedent: two branches each raised a shared baseline correctly in isolation and wrongly after the other merged | `scripts/check-plugin-detail-render.mjs` `RC_BASELINE` comment (⛔ R6) |
| GT15 | No byte-size gate exists anywhere — 336 gate headers in `audit-gates.sh`, zero size gates; `dashboard.html` 10.27 MB, `index.html` 9.26 MB, 220 SVGs / 4.4 MB for 58 concepts | critic V11 |
| GT16 | Claim 5 counting discrepancy: the table says 48 hooks; two independent in-session measures returned **47** `*.sh`. Unresolved — a counting-rule difference, not a defect | claims row 5 vs plan-A P4, plan-B §0 |

---

## 2. Phase 0 — Close the live defect. Before any inventory work. ⛔ R1

`depends_on_claims: [7, 9, 12]`

This phase authors **zero** concept files and touches **zero** inventory machinery. It exists because
the correlated-error finding is the most important result of this run: both panels planned to
document a defect class that is still shipping.

### 2.1 P0-a — Triage the 8 exposed advisory hooks

The critic's raw count was inflated: it counted fail-closed guards whose `exit 2` channel works
correctly. The orchestrator's precise re-measure yields **8** hooks that write stderr, never
`exit 2`, and have no delivered channel:

| Hook | Likely disposition (⛔ decide per hook — do NOT blanket-convert) |
|---|---|
| `guard-recursive-spawn.sh` | Candidate genuine advisory — a spawn warning the model should see |
| `regen-on-manifest-change.sh` | Candidate genuine advisory — "you changed a manifest, regenerate" is model-actionable |
| `reapply-posture.sh` | Likely **internal logging** — posture reapplication is a side effect, not advice |
| `ensure-default-mode.sh` | Likely **internal logging** |
| `dashboard-autostart.sh` | Likely **internal logging** — a launcher, its consumer is the terminal |
| `_host-canary.sh` | Likely **internal logging** / diagnostic |
| `_model-fallback.sh` | Candidate genuine advisory — a silent model downgrade is exactly what the model should be told |
| `codex-hook-env.sh` | **Adapter** — its consumer is another host's env, not the model |

⛔ **Per-hook decision is mandatory.** A blanket conversion to `additionalContext` would inject
terminal noise into every turn's context and would be the mirror-image defect: a channel that
reaches the model with content nobody wanted there. The deliverable is a written disposition table
with, per hook, one of: `advisory → convert`, `internal-logging → keep stderr, document why`,
`adapter → out of scope`.

**Guardrail from claim 9:** two `additionalContext` emitters on one event **concatenate**; they do
not last-write-wins. Converting several hooks on the same event compounds. `updatedToolOutput`, by
contrast, **replaces** — so two emitters of that on one event is a silent data-loss shape. Any
conversion must state which event it lands on and what else already emits there.

### 2.2 P0-b — The reusable delivered-channel assertion. This is the durable half.

Nothing in 56 tests asserts a hook's output reaches the model. Ship one shared helper —
`plugins/ravenclaude-core/hooks/tests/lib/assert-delivered-channel.sh` — exposing:

- `assert_delivers_additional_context <hook> <event> <payload-fixture> <sentinel>` — runs the hook,
  parses stdout as JSON, asserts `hookSpecificOutput.additionalContext` contains the sentinel.
- `assert_delivers_updated_tool_output <hook> …` — the assertion that **zero** tests currently make.
- `assert_denies <hook> …` — asserts the `permissionDecision: deny` envelope (the fail-closed tier
  whose `exit 2` channel already works).
- `assert_terminal_only <hook> …` — the **positive statement of the internal-logging tier**: asserts
  stderr carries the text AND that stdout carries no delivered channel. An internal-logging hook is
  then *tested as such*, not merely untested.

⛔ **Every helper carries a neutered-copy canary**, the pattern already proven by
`test-advisory-delivery.sh`: strip the emitting line from a copy of the hook under test and assert
the helper **fails** on it. Without this, "the hook delivers" and "the helper never ran the check"
are indistinguishable — the exact defect this project exists to catch, reproduced in the fixer.

### 2.3 P0-c — The convention rule, enforced not stated

Add to `scripts/audit-gates.sh` (⛔ register in **both** the `--check <N>` dispatcher **and** the
main sequence — Gate 184 shipped unreachable for a whole release by being added to only one):

> **Gate INV-CHANNEL.** Every hook whose disposition table entry is `advisory` must have at least
> one test invoking `assert_delivers_additional_context` or `assert_delivers_updated_tool_output`.
> Must-fail fixture: a hook marked `advisory` with only a stderr assertion. Must-pass: the pristine
> tree post-P0-a.

⛔ Grep the suite output for the **literal gate name**, never `Gate N` — a batched header has
already made a by-number grep report 7 false unruns in this repo.

### 2.4 Acceptance

1. Disposition table written for all 8, with a per-hook reason.
2. Every hook dispositioned `advisory` has a delivered-channel assertion; every hook dispositioned
   `internal-logging` has an `assert_terminal_only` assertion. **No hook is left untested in either
   direction** — that symmetry is what stops the triage from becoming a silent exemption list.
3. The helper's neutered-copy canary demonstrably fails on the neutered copy.
4. `assert_delivers_updated_tool_output` has at least one real caller — the count goes 0 → ≥1.
5. Gate INV-CHANNEL registered in dispatcher **and** main sequence; suite output greps by name.
6. ⛔ Claim 10: the fix is not live for any consumer until `plugin.json` bumps, then
   `scripts/sync-plugin-versions.py` **and** `scripts/generate-copilot-plugin.py` run.

**Cost: hours, not weeks.** This is the whole fix for the whole motivating class.

---

## 3. Phase 1 — Empirical spikes. The literal first executable step of the inventory track. ⛔ R10

`depends_on_claims: [13, 15, 16]`

Plan A asserted T-PROSE compatibility with certainty and never tested it — which is precisely the
shape T-PROSE exists to catch. This phase runs four cheap experiments and records literal verdicts.
It authors no production content.

### 3.1 S1 — T-PROSE canary (adopted verbatim from plan-B Phase 0)

Author **one** canary concept file — `hook-message-channels.md`, the owner's own worked example —
carrying a dated, certainty-stamped mechanism claim, and **write it through the real hook**.

Known from GT6: T-PROSE fires only on **CREATE**, so the blast radius is narrower than feared —
re-stamps and `last_verified` bumps on existing files are structurally exempt. The open questions
the spike must answer with a literal yes/no:

- Does a **frontmatter-only** `sources:` block satisfy `_CTRL` for a claim in body paragraph 3+?
  (Prior: no — `_CTRL` is a ±6-line window regex, not document-level.)
- Does an inline `control: <text>` line placed **immediately above** the claim clear it? (Prior:
  yes — `control:` matches `_CTRL`. Placing it **above** rather than below is deliberate: a
  5-sentence / 600-char nuance is ≈6–7 wrapped lines, so a `control:` line *below* it can fall
  outside the ±6-line window from a claim in line 1.)
- Does a **second** dated claim later in `body_md`, with no adjacent control, deny? If yes, the
  authoring rule is one control per **claim**, not one per file — which is more overhead than
  either panel budgeted.
- Does the YAML `last_verified:` date in frontmatter itself trip `_STAMP` against a nearby body line?

**Deliverable:** a written line-offset rule, and the exact template shape, recorded in
`docs/best-practices/inventory-authoring.md`. Every later phase inherits it.

### 3.2 S2 — `claude -p` availability in scheduled CI (settles claim 15's residual)

A throwaway `workflow_dispatch`-only job running `command -v claude; claude -p 'reply OK'` under
scheduled-CI conditions. Record a literal yes/no. **No phase is cancelled either way** — §7.4
specifies the substitute ladder — but the answer selects which lane does the work.

### 3.3 S3 — Self-heal contract probe (feeds P2)

On a scratch branch, make `concepts.py --check` fail with a **new** failure class and observe
whether `regenerate-artifacts.yml` continues or detonates. This converts R4 from a read-derived
inference into a measured fact before the fix is designed.

### 3.4 S4 — Apostrophe / rendering-path audit (red-team #8)

Trace, by reading rather than assuming, every consumer of authored prose (`nuance`, `body_md`,
`refresh_when`) from concept file → `concepts.py` → `generate-dashboards.py` → CI annotation. Confirm
each is a **Python string operation**, not a shell interpolation. Two same-repo precedents exist for
this class; "plausibly safe, unverified" is the standard this repo's own discipline rejects.

⛔ Separately and unconditionally: **no apostrophes anywhere inside a single-quoted bash block,
including prose comments.** One apostrophe closes the string and the hook dies with a non-blocking
error — the gate fails **open** and silently stops gating.

### 3.5 Acceptance

A four-row verdict table with the command run and the literal output class for each. **A spike with
no recorded verdict is not done.** ⛔ An empty result needs a positive control — S1 must include a
file that *should* deny and does, or "it did not deny" is unfalsifiable.

---

## 4. Phase 2 — Fix the self-heal contract and the masking short-circuit. ⛔ R4

`depends_on_claims: [1, 13]`

**This is a CRITICAL INTEGRATION FAILURE in plan A and it must be closed before any new
`concepts.py --check` failure class ships.**

### 4.1 The defect

`regenerate-artifacts.yml:198` greps `concepts.py --check` output for the literal string
`staleness gate FAILED`. On match → `::warning::` and continue. On **no match** → `exit "$_crc"` at
`:203`, fatal, and every subsequent self-heal step stops: concept SVGs, decision-tree SVGs,
`dashboard.html`, `index.html`, BI reports, the Copilot package, the feedback report. A's
`covers_digest is STALE` message matches nothing, so a covers-digest mismatch reaching `main`
reproduces exactly the incident the workflow's own comment records at `:183-191` — *"left main
UN-HEALED across many merges."*

### 4.2 The fix — a stable machine marker, not a prose string

Do **not** reword the new failure to match the old prose. A prose string a future edit can silently
reword is the wrong contract shape — that is how this fuse was armed in the first place.

1. `concepts.py --check` emits, on any **content-freshness** failure class (platform-fact staleness,
   inventory staleness, covers-digest drift), a stable machine-readable marker line:
   `RC-CONCEPTS-CLASS: human-reverify-required`. Generator failures emit
   `RC-CONCEPTS-CLASS: generator-failure`.
2. `regenerate-artifacts.yml` greps the **marker**, not the sentence. Keep the old
   `staleness gate FAILED` grep as an OR-term for one release so a version-skew rollout cannot
   detonate mid-migration.
3. ⛔ **New test, required:** a fixture that makes the new check fail and asserts the self-heal
   workflow still completes every downstream step. Without it, "the contract holds" and "nobody
   checked" are indistinguishable.

### 4.3 Collect-all, never short-circuit (R4b)

`concepts.py:301-305` evaluates staleness first and `return 1` before comparing `concepts.json` to
the serialized registry. Adding two more early-exit classes into the same funnel means one stale
entry blinds registry-freshness for the whole corpus — the **masking-gate** defect already in this
repo's record (a red gate hiding later ones in the same step).

**Requirement:** `--check` collects every violation class and reports them together, with a single
exit at the end. Acceptance: a tree with BOTH a stale entry AND a stale `concepts.json` reports
**both**, not the first.

### 4.4 Acceptance

1. S3's measured verdict reproduced, then shown fixed.
2. Self-heal completes all steps when the new check fails (the required test above).
3. Collect-all proven with a dual-violation fixture.
4. Gate registered in dispatcher **and** main sequence; greped by literal name.

---

## 5. Phase 3 — Close the staleness double-exemption. Both escapes. ⛔ R3

`depends_on_claims: [3, 13]`

### 5.1 The defect, stated precisely

`scripts/concepts.py:276`:

```python
if c["kind"] != "platform-fact" or not c["last_verified"]: continue
```

A concept escapes staleness if it is **EITHER** not a platform-fact **OR** simply lacks the field.
Both escapes matter, and the corpus makes the first one dominant: **41 `ravenclaude-built` vs 17
`platform-fact`** — the gate covers the minority kind. Every inventory entry would be
`ravenclaude-built` and inherit zero staleness pressure.

⛔ **A fix that only flips the kind check leaves the second escape wide open**: an entry with no
`last_verified` at all is still skipped, and "unverified" then looks identical to "verified
recently." That is the silent-green shape.

### 5.2 The fix

1. **Kind escape:** the gate applies to any concept with `entry_class: inventory` regardless of
   `kind`, and continues to apply to `kind: platform-fact`.
2. **Missing-field escape:** for a gated concept, an **absent or empty `last_verified` is a
   violation**, not a skip. Message: `last_verified is ABSENT — unverified is not fresh`.
3. Both classes emit the `RC-CONCEPTS-CLASS: human-reverify-required` marker from §4.2.

### 5.3 ⛔ Content-drift is the PRIMARY axis; calendar age is secondary and non-blocking on PRs

The critic's arithmetic is decisive and both panels got this wrong in opposite directions. At 162
entries on a 180-day clock (plan A) steady state needs **~0.9 re-verifications every day, forever**;
at 30 days (plan B) it is **~5.4/day** and the gate is red essentially always, so it gets disabled
within a month. Worse, entries authored in waves **expire in waves on the same day**, turning every
open PR in the repo red — including PRs touching nothing related. That is not a deadline; it is a
periodic repo-wide outage with a documentation task as the only exit.

**Resolution:**

| Axis | Trigger | PR CI | Scheduled sweep |
|---|---|---|---|
| **Content drift** (primary) | `covers_digest` mismatch — a covered artifact changed after the entry was stamped | **BLOCKING** | blocking |
| **Calendar age** (secondary) | `last_verified` older than the window | **WARNING** | **BLOCKING** |
| **Absent `last_verified`** | field missing/empty on a gated entry | **BLOCKING** | blocking |
| `kind: platform-fact`, 90 days | unchanged from today | **BLOCKING** | blocking |

Content drift is strictly the better instrument: it fires when the fact **can actually have become
false**, not when a calendar rolls. It is also the same computation as `covers_digest` — the
mechanism already exists and both panels gated it on the wrong axis. The blocking calendar gate is
retained only where the population is small enough to service: the ~17 `platform-fact` entries.

⛔ **Digest false-positive management.** The digest is over the whole file including comments —
deliberately, because in this repo the comments **are** where the mechanism nuance lives. That means
a comment typo fix trips the same tripwire as a mechanism change. Mitigation: the failure message
prints the entry's own `refresh_when` text and offers `--restamp-cosmetic`, which re-stamps
`covers_digest` **without** advancing `last_verified` — so a cosmetic edit does not buy 180 days of
false freshness. Substantive re-verification advances both.

### 5.4 Anti-rubber-stamp (gap-delta Q1.1)

`restamp` enforces that *something ran*, not that anyone *re-read*. Left alone this becomes the new
"advisory hook writing to stderr": passes every check, nobody re-read the claim.

**Mechanism, not exhortation:** `restamp` (the substantive form) requires `--reason <text>` of ≥ 30
chars, appended to a committed `restamp-log` line carrying `{entry_id, date, reason, digest_before,
digest_after}`. `coverage --report` surfaces the **ratio of restamps whose `nuance` text was
unchanged** — a high ratio is the tell for a rubber-stamp loop. It is a reported signal, not a gate:
a legitimately-unchanged nuance after a real re-read is normal, and gating it would manufacture
false edits.

### 5.5 `covers[]` completeness (gap-delta Q1.2 / Q4.1) — an honest partial

A `covers_digest` is only as complete as the author-declared `covers[]`. An under-scoped list, or a
host-dependent claim left as `entry_class: inventory` instead of split into a `platform-fact`,
yields an entry whose tripwire silently never fires.

**Partial check, shipped:** `check-covers-completeness.py` — every repo-relative path appearing in
the entry's `nuance` or `nuance_source` must also appear in `covers[]`, or carry an explicit
`platform-fact` exemption. **Stated limit:** this catches under-declaration that is *textually
visible*. It cannot catch a nuance that depends on host behaviour never named as a path. That
residual is waived in §21-W3 with its reason.

### 5.6 `refresh_when` (critic §3.4)

Neither panel made the field the schema actually reserved for this machine-actionable. Collapse the
three ideas into **one** trigger mechanism rather than shipping two new fields beside a decorative
third:

- `covers[]` + `covers_digest` = the mechanism (content drift).
- `refresh_when` = the **structured** form: an optional list of extra path globs or a version
  predicate, evaluated by the same drift check. Free-text remains accepted and renders in the failure
  message.
- Plan B's `verified_against` is **not** shipped as a separate field — its idea (content drift)
  is adopted; its implementation (`git log -1 --format=%cI` timestamps) is rejected as fragile to
  squash, rebase, and shallow clones, where a content hash is not.

### 5.7 Acceptance

1. A fixture `ravenclaude-built` inventory entry past the window **warns** on PR and **fails** the
   sweep.
2. A fixture entry with `last_verified` absent **fails** on PR.
3. A mutated covered artifact **fails** on PR; `--restamp-cosmetic` clears the digest without moving
   `last_verified`; a dated fixture proves the date did not move.
4. The 58 existing concepts still validate and `concepts.json` is **byte-identical to HEAD** — the
   positive control proving the change is additive.

---

## 6. Phase 4 — The harness, keyed by ARTIFACT PATH. Zero entries required. ⛔ R2, R8

`depends_on_claims: [5, 12, 14]`

Runs **in parallel with P2/P3** — it depends on nothing they produce. This is the phase that
delivers value in week 1.

### 6.1 The decoupling, and why it is the central design change

Plan A stated *"the registry IS `concepts.json`"* — probes driven off inventory entries. That
coupling is a choice, not a necessity, and it is what put a 10-line check that finds real defects
today behind 54 authored entries. **The probe registry is keyed by artifact path.** It runs across
all hooks, skills, agents and scripts on day 1 with zero entries authored. When an inventory entry
exists, it *inherits* the probe verdict for its `covers[]` paths; it never gates the probe running.

**GT13 is the decisive datum:** a 10-line resolver found 2 real dangling `SKILL.md` references, with
a negative control that correctly flagged its own false-positive mode (repo-root-relative forms).
That check should run tomorrow, not in month 4.

### 6.2 Probe classes, populations, observables, and controls

⛔ **Claim 14 is capped here, not assumed.** There is no universal probe shape. Each class names its
own observable, its own control, and where there is no cheap observable, says so.

| Class | Population | Observable | ⛔ Control (mandatory) | Tier |
|---|---|---|---|---|
| `hook-decision` | ~15 hooks | synthetic payload on stdin → assert `deny` envelope | **Two-sided:** same payload, trigger removed, must **not** deny. A prober that denies everything is indistinguishable from a working guard | effect |
| `hook-advisory` | ~10 hooks | assert `hookSpecificOutput.additionalContext` + self-identifying banner on stdout | neutered-copy canary (P0-b's helper, reused) | effect |
| `hook-sideeffect` | ~10 hooks | run against `mktemp -d` root; assert the ledger/event line appears | **planted-secret negative:** fixture payload carries a fake token; the written record must **not** contain it | effect |
| `hook-adapter` | ~10 hooks | fixture input → assert translated envelope shape | a fixture the adapter must pass through **unchanged**, so a pass-everything adapter is caught | effect |
| `hook-registration` | all 47 | file exists **and** is named in `hooks.json` for the event it claims **and** in `.claude/settings.json` (dev lane) | a deliberately unregistered fixture hook must be reported | reachability |
| `script-selftest` | ~18 scripts | run `--check`/`--self-test`/`--must-fail`; assert the declared pass exit | the tool's **own declared** teeth-bit exit — ⛔ divergent per claim 11 | effect |
| `script-callgraph` | ~27 scripts | static call-graph: named by any workflow, `bin/rc` verb, hook, `SKILL.md`, or other script? | a planted orphan script must be reported unreachable | **reachability only** |
| `skill-static` | 54 skills | frontmatter parses; `name`+`description` present; **every referenced path resolves** | a fixture skill with a dangling reference must be reported | **reachability only** |
| `agent-static` | 15 agents | `check-frontmatter.py` + referenced-path resolution + non-empty `tools:` | fixture agent with empty `tools:` must be reported | **reachability only** |
| `skill-invocation` / `agent-dispatch` | 69 | `claude -p` with a scenario `trigger_phrase`; assert load/route | a **sentinel known to load, in the same batch** — otherwise "not loaded" and "blind harness" are identical | effect, **T2, sampled** |
| `static-resolution` | remainder | every referenced path resolves | planted dangling reference | reachability |

⛔ **Class-A probes must not assume an exit code from a Bash `tool_response` — claim 8: a failing
Bash `tool_response` carries NO exit-code field.** Assert on the emitted JSON envelope only.

### 6.3 ⛔ `--must-fail` conventions differ per tool. Read the declaration; never hard-code. (claim 11)

Measured divergence: `premise-gate.py` uses **exit 0** as its teeth bit; `sync-plugin-versions.py`
uses **exit 2**. A shared assumption is wrong by construction.

Every new detector implements `--must-fail-convention`, printing exactly
`must-fail-teeth-exit: <n>`, and `--must-fail`, which runs its planted canary and exits with that
declared code. `audit-gates.sh` calls the convention first, then `--must-fail`, and **compares** — so
a tool that declares one number and returns another fails the audit, which also catches a future
convention change silently breaking the auditor.

### 6.4 ⛔ The harness must not count itself. R8 — the sweep-of-the-sweep, shipped in this phase.

Neither panel derived its registered-vs-executed count from a source independent of `concepts.json`.
**A sweep that counts itself cannot detect its own blindness:** if a concept file fails validation
and silently drops out of the registry, both the registered and executed counts shrink together and
the check stays green. That is the `2>/dev/null` manufactured-clean shape, one layer up.

**The independent source, named:** `git ls-files` over the four artifact roots
(`plugins/ravenclaude-core/{hooks,skills,agents,scripts}/`), filtered by the counting rule the phase
states in writing. This is **not** `concepts.json`, **not** `concepts.py`'s registry, and **not** any
file the sweep also writes.

Three assertions after every sweep run:

1. `census(git ls-files) == artifacts_enumerated_by_sweep` — a divergence by even one is the harness
   going blind.
2. `probes_registered == probes_executed` — catches a class typo or a class with no runner file.
3. **Every registered probe is invoked by** (a) a workflow step, (b) `audit-gates.sh`'s numbered
   sequence, or (c) the sweep script itself. A probe file on disk invoked by none of the three is
   flagged exactly like an unwired hook — same detector class, same severity. (This repo has already
   paid for the general form: 39 of 49 gates invoked by no workflow.)

**⛔ The TELL when the sweep goes blind:** any of the three numbers moving **down** without a
corresponding artifact deletion in the same diff. The sweep reports all three every run;
`coverage --report` renders them; a downward move with no deletion fails the sweep's own gate.

**The permanently-red canary.** A fixture artifact whose probe is **wrong on purpose** — it asserts
a sentinel arrives via a channel measured to be undelivered, mirroring the `_advise.sh` incident —
lives in `tests/fixtures/` forever. If a sweep run ever reports it **passing**, the sweep is broken
and its own gate fails loud. Every "trust the harness" argument routes through this one fixture
staying red until deliberately made to pass by a change nobody made.

### 6.5 Security overlay — the probe is the risk surface

- Probes run against a **temp project root** (`mktemp -d`), never the live repo.
- Run records store **derived labels only**: entry id, class, verdict, duration. Never stdout,
  stderr, command text, or payloads.
- Where a probe must inspect output, it asserts **by pattern against an in-memory buffer** and
  discards it.
- Records land in `.ravenclaude/runs/inventory-sweep/` — **gitignored**, per the storage contract.
  ⛔ Do not "helpfully" commit them; that reverses a deliberate decision about other people's data.
- ⛔ The planted-secret canary (§6.2 class `hook-sideeffect`) has a `--must-fail` mode asserting the
  sweep record does **not** contain the fixture token. Without it, "the scrubber works" and "the
  scrubber was never invoked" are indistinguishable.

### 6.6 Acceptance

1. The skill-reference resolver reproduces GT13's two real findings **and** its negative control.
2. Every class runner ships its control and the control **demonstrably fires**.
3. Neutering one runner's assertion makes the sweep fail (gate INV-PROBE-TEETH).
4. All three §6.4 counts computed from the independent census; a deliberately-dropped concept file
   does **not** move both numbers together (the positive control for the independence claim).
5. The permanently-red canary is red.
6. Planted-secret `--must-fail` proves the scrubber bites.
7. Runners are apostrophe-clean inside single-quoted blocks — mechanically greped in the same PR.

---

## 7. Phase 5 — Schema delta. ⛔ R12 fields land here.

`depends_on_claims: [1, 3, 13, 14]`

All changes in `scripts/concepts.py` (root `scripts/`, not the write-guarded plugin `scripts/`).
Additive; every existing concept keeps validating unchanged.

### 7.1 Fields

```yaml
entry_class: inventory          # absent -> today's behaviour exactly
covers:                         # non-empty list of repo-relative paths
  - plugins/ravenclaude-core/hooks/_advise.sh
covers_digest: "sha256:…"       # generated over sorted concat of covers[] contents
nuance: >                       # <=4 RENDERED LINES (see R10 window), the mechanism fact
nuance_evidence:
  measured: 2026-08-19
  control: "…"                  # rendered ABOVE the nuance as a literal `control:` line
  falsifier: "…"
  probe: <path> | "unprobed: <>=30 chars of reason>"
nuance_source: <file>:<line-range>     # a POINTER, never a payload (R9)
verify:
  tier: effect | reachability | none
  strength: executed | static | observational   # ⛔ R12 — renders distinctly
  class: <one of §6.2>
  probe: <path>                 # required unless tier == none
  teeth_exit: <n>               # THIS probe's declared convention (claim 11)
  rationale: "…"                # required IFF tier == none
last_verified: YYYY-MM-DD       # required on inventory entries, gated per §5
refresh_when: …                 # free text OR structured globs (§5.6)
```

⛔ **`nuance` is capped at 4 rendered lines, not 5 sentences / 600 chars.** Plan A's cap was
~6–7 wrapped lines, which can push a `control:` line outside T-PROSE's ±6-line window from a claim
in line 1. The cap and the above-placement together are what make the mitigation structural. S1's
measured verdict may tighten this further; S1 wins over this number.

### 7.2 ⛔ R9 — No raw bytes in committed fields

Concept files are committed and **permanently retained**, unlike `.ravenclaude/runs/` which is
gitignored. `log-probe.sh`'s header states why it stores derived labels only: raw command text and
output *carry tokens, keys and payloads*. Both panels extended that discipline to the sweep's
gitignored records and **neither extended it to the committed authoring surface.**

**Rule, stated negatively and enforced:**

> `nuance`, `nuance_evidence.control`, `nuance_evidence.falsifier`, and `nuance_source` **may**
> summarize a mechanism, name a label, or cite a `file:line` location. They **may never** contain
> verbatim command text, verbatim stdout/stderr, or payload text.

Enforcement (`check-inventory-evidence.py`, deterministic): reject a value that contains a shell
prompt marker, a `$ `-prefixed line, a multi-line block that looks like captured output, a
high-entropy token ≥ 20 chars, or an absolute filesystem path outside the repo. **Stated limit:**
this is a shape heuristic, not a secret scanner. It catches paste-of-output; it cannot certify that
a paraphrase contains nothing sensitive. Waived in §21-W4.

### 7.3 ⛔ R12 — The weak-check tier must render distinctly. This is NOT optional.

Per settled claim 14, ~60% of the inventory — 54 skills, 15 agents, 27 uncalled scripts, **96 of
162** — gets findability + reference-integrity only. Their consumer is a model deciding to read a
file; there is no deterministic signal that it happened.

Both panels recorded that honestly *in the plan* and then left the distinction invisible on the one
surface the project exists to make legible. Plan A gated it behind an explicitly **optional** P9.
**A weak check and a strong one that look identical is the inert-gate defect wearing a badge.**

**Requirement:** `verify.strength` renders as a distinct, non-decorative badge on every concept card:

| `strength` | Badge | What it means to a reader |
|---|---|---|
| `executed` | **Probed** | A real payload was run and a real observable asserted |
| `static` | **Findable** | Its frontmatter parses and its references resolve. **Nothing executed it.** |
| `observational` | **Observed** | Seen after the fact (post-spawn), not gate-capable before it |
| `tier: none` | **Unverified** | With the written rationale shown inline |

The badge text must state the limit, not a reassuring synonym. "Findable" is honest; "Verified
(static)" is not, because a reader skims the first word. `effect-status: unverified — <reason>`
(adopted from plan B) is a **counted, surfaced** figure, not a silent absence.

### 7.4 Claim-15 substitute ladder (adopted from plan A, the best-engineered part of either plan)

| Tier | What runs | Needs | Where |
|---|---|---|---|
| T0 | every deterministic probe class | `bash` + `python3` | PR CI **and** nightly |
| T1 | side-effect/adapter probes vs temp roots; planted-secret canary | `bash` + `python3` | nightly |
| T2 | skill-invocation, agent-dispatch, re-measurement of the delivery **platform fact** | a live `claude -p` | per S2's verdict |

1. **Probe first** (S2). Until it runs, T2's CI availability is **UNKNOWN**, never absent.
2. **If unavailable → the attestation-age substitute.** T2 runs **locally**; its only committed
   output is a `last_verified` re-stamp. CI then gates on attestation **age**, not on running the
   model. An owner who stops running T2 gets a red **sweep**. This converts an unavailable capability
   into an enforceable deadline.
3. **Proxy assertion, always on regardless.** The per-hook static shape check runs in T0; the
   *delivery* fact it depends on is modelled as its own `kind: platform-fact` concept under the
   existing 90-day gate — so a stale delivery fact fails CI **with no model call at all**. This is
   the cleverest single idea in either panel plan and it is adopted verbatim.
4. **If a model call IS available → budget it.** Sample k=8 per nightly run on a rotating cursor in
   `.ravenclaude/runs/inventory-sweep/cursor.json` (gitignored), covering all 69 in ~9 days.
   ⛔ **The positive control runs in EVERY batch, not once.**
5. ⛔ **A silent skip when T2 cannot run is the exact defect class.** The sweep reports **UNKNOWN**,
   never green. Age-based staleness is the **primary** enforcement (it degrades correctly even if the
   sweep's own write path breaks); `effect-status: unverified` is the **secondary**, informative
   layer — not the other way around.

### 7.5 Acceptance

1. 58 existing concepts validate; `concepts.json` byte-identical to HEAD.
2. A fixture inventory entry missing `nuance` fails with a specific message.
3. A fixture with a pasted output block fails `check-inventory-evidence.py`.
4. Badge rendering asserted by a DOM/string test on the generated dashboard, not by inspection.

---

## 8. Phase 6 — Surfacing and budgets. ⛔ R5.

`depends_on_claims: [4, 16]`

### 8.1 ⛔ R5 — B's Gate-132 premise is FALSE; the underlying risk is REAL

`panel-learn` is **already DOM-islanded** (`check-dom-budget.py:104,128`): its markup lives in a
`<script type="application/json">` payload the parser reads as CDATA, and islanded panels cost a flat
`ISLANDED_PANEL_COST = 2` elements. `check()` compares only the **live** element total against the
ratchet. **Plan B's entire per-batch ratchet-raise process is built for a gate that cannot fire.**
Delete it.

**The real, measured risk:** 23,861 elements for 58 concepts ≈ 411 elements/concept. 162 more entries
is **~90,000 elements injected into the DOM on one tab click**, against a Lighthouse threshold of
1,400 — and the payload figure is printed by `--report` and **gated by nothing**.

**Ship an ENFORCED payload budget.** The number is already computed; only the gate is missing:

1. `check-dom-budget.py check()` gains a **per-panel payload ceiling**, monotonic ratchet, seeded at
   the current measured value.
2. **Byte ratchet** on `dashboard.html` and `index.html` — currently 10.27 MB and 9.26 MB with
   **no byte-size gate anywhere in 336 gate headers**. 58 concepts already carry 220 SVGs / 4.4 MB;
   2.8× the count plausibly adds 8–12 MB to **each** surface, and nothing warns.
3. Both ratchets are seeded **before** any bulk authoring, so the first batch measures against a real
   baseline rather than establishing one retroactively.

### 8.2 ⛔ R2 corollary — diagrams are opt-in, never auto-generated

Plan A's skeleton prefilled a mermaid diagram per draft. `regenerate-artifacts.yml:226-234` reverts a
failed render with a `::warning::` and **continues green**, and `render-concepts.py --check` is
deliberately off the PR path — so 162 diagrams rendered one-`npx`-process-each through mermaid-cli +
Chromium is an all-or-nothing revert that leaves SVGs permanently stale while CI reads green. **That
is the single most dangerous line in either panel plan.**

Rules: diagrams are **opt-in per entry**; rendering happens in batches of ≤ 20; and
`render-concepts.py --check` becomes a PR gate **for changed concepts only**.

### 8.3 Acceptance

1. A synthetic +200-concept payload **fails** the new ceiling; the pristine tree passes.
2. A synthetic +5 MB dashboard **fails** the byte ratchet.
3. A deliberately-broken diagram render **fails** the changed-concepts PR gate instead of warning.
4. Badges from §7.3 render for all four strengths in a fixture set.

---

## 9. Phase 7 — The nuance gate: deterministic floor + BLOCKING sampled review. ⛔ R7

`depends_on_claims: [11, 14]`

### 9.1 The ruling, stated plainly

**The nuance bar is not fully automatable, and a fake metric that passes while entries teach nothing
is worse than an admitted human step.** Plan A's `G-N2` is constructively gameable — a worked
4-token example defeats it — and its only backstop, the LLM judge, is advisory **by plan A's own
admission**. Plan B's honesty about its own prefilter ("catches the laziest failure mode, nothing
more") is correct, but its sample review was a process step with no mechanism, and **this repo's
record is that process steps decay and mechanisms do not.**

Resolution: keep A's deterministic gate as a **cheap floor**, adopt B's **blocking** sample review,
and give it a mechanism.

### 9.2 The deterministic floor (necessary, never sufficient)

Four mechanical checks. They certify a nuance is *shaped like one and falsifiable*. They cannot
certify it is **true** or **non-obvious**, and the gate's own output must say so.

- **F1 — negation-of-expectation marker.** Closed vocabulary applied to a named alternative
  (`not … but`, `never`, `instead of`, `rather than`, `two ways`, `only one`). Coarse filter.
- **F2 — non-derivability from the reader's baseline.** `|M \ B| >= 2` where `M` is mechanism tokens
  (backticked spans, hook event names, `exit <n>`, dotted/slashed identifiers, quoted JSON fields)
  and `B` is the reader's baseline.
  ⛔ **The measured flaw, fixed here:** plan A's `B` deliberately excluded the covered artifact's own
  header, on the reasoning that the dashboard reader has the summary and not the file. That exclusion
  is exactly what makes the exploit free — **every mechanism token needed to pass is sitting in the
  file the author has open.** Fix: compute **two** counts against **two** baselines.
  `B1 = summary ∪ title ∪ covers-basenames` (the reader's baseline, gates at ≥2) and
  `B2 = B1 ∪ the covered artifacts' own header text`. An entry passing B1 but not B2 is **reported
  separately as `derived-from-header`** and ratcheted **down** over time. It still passes — a nuance
  restated from a header is genuinely useful to a dashboard reader — but it is counted honestly
  rather than laundered into the same number as an original finding. **Two token sets, two counts,
  one honest number.**
- **F3 — anti-goodhart.** Each novel mechanism token must sit in a sentence containing a verb from a
  closed claim-verb list (*reaches, arrives, fires, returns, exits, replaces, concatenates, denies,
  is keyed by, is read by, blocks, no-ops*). A token in a bare noun phrase does not count. Stuffing
  then requires writing false claims — a different and much more visible offence.
- **F4 — evidence triple wired.** `measured`, `control`, `falsifier` non-empty; `control` ≥ 20 chars
  and ≠ `falsifier`; `probe` names an existing registered path **or** starts with `unprobed: ` plus
  ≥ 30 chars of reason. An unprobed nuance is allowed — it is *honest* — and the unprobed fraction is
  counted and ratcheted down.

⛔ The floor's own output must print: *"These checks test shape and falsifiability. They do not test
whether the nuance is true, and they do not test whether it is non-obvious. The sampled review does
the second; only a probe does the first."*

### 9.3 The blocking sampled review, with a mechanism

- **Cadence:** every authoring batch. **Sample:** 25% stratified across artifact classes, minimum 3.
- **Reviewer:** a **fresh-context** reviewer with no memory of the authoring session. A reviewer that
  authored the batch rubber-stamps its own summary.
- **Rubric:** one yes/no — *"would a competent RavenClaude user learn something they could not have
  guessed from the title plus the 200-char summary?"*
- ⛔ **The mechanism (this is what plan B lacked):** verdicts are written to a **committed**
  `tests/fixtures/inventory-review-ledger.json` — `{batch_id, entry_ids_sampled, verdicts, reviewer,
  date}`. `coverage --check` **reads the ledger and blocks batch N+1 if batch N has no recorded
  sample, or scored below 80%.** It is a gate, not an intention. A ledger the CI does not read is a
  process step, and process steps decay.

### 9.4 The calibrated judge — adopted verbatim, still non-blocking

Plan A's calibration bar is **the strongest single control in either document** and is adopted with
no change: a frozen golden set of ~12 measured positives (the two-channel fact; `additionalContext`
concatenates while `updatedToolOutput` replaces, claim 9; version-keyed cache so merged ≠ live,
claim 10; divergent `--must-fail` exits, claim 11; a failing Bash `tool_response` has no exit-code
field, claim 8) plus ~12 deliberately authored restatements. **The judge must score ≥ 22/24 on the
golden set in the same run before any of its verdicts are reported.** Below that it emits
`judge-uncalibrated` and no per-entry verdicts. Without this, "judge says all entries are fine" and
"judge is broken" are indistinguishable.

The judge stays **non-blocking**: a non-deterministic merge gate is a defect class this repo already
treats as unacceptable. The blocking human step is §9.3, which is deterministic in its *mechanism*
(a ledger entry exists or does not) even though its *content* is judgment.

⛔ **Named weakness of the golden set:** plan A wrote both the check and the fixtures meant to defeat
it — a closed loop. **Requirement:** at least 4 of the 12 negatives must be authored by someone
instructed *"make this pass the nuance gate while teaching nothing"*, i.e. adversarially, not
illustratively. The critic's own worked example (`PostToolUse` fires before
`hookSpecificOutput.additionalContext` is read, and the hook exits 0) is negative #1.

### 9.5 Acceptance

1. Floor runs clean over the 12 golden positives; rejects all 12 negatives, each naming which of
   F1–F4 it failed.
2. The 4 adversarial negatives are rejected by the **B2/derived-from-header** count or by the
   sampled review — and the plan records which, honestly, per negative.
3. `--must-fail-convention` prints its declared exit; `--must-fail` returns it; `audit-gates.sh`
   compares them.
4. `coverage --check` **blocks** on a fixture batch with a missing ledger entry, and on one scoring
   70%.

---

## 10. Phase 8 — The inception ratchet. This is what delivers complete coverage. ⛔ R2, R6

`depends_on_claims: [5, 10]`

### 10.1 The forcing function

> **Any file added under `plugins/ravenclaude-core/{hooks,skills,agents,scripts,commands}/` in this
> diff, that is not named in any inventory entry's `covers[]`, fails the build.**

Implementation: `git diff --name-only --diff-filter=A origin/main` ∩ the artifact roots, minus the
union of all `covers[]`. Deterministic, no model, ~15 lines.

Paired invariants, enforced by `coverage --check`:

- `published_entries` may never decrease;
- `covered_artifacts / total_artifacts` may never decrease, where the denominator comes from the
  **independent census of §6.4**, not from `concepts.json`;
- reported and ratcheted **down**: `unprobed_fraction`, `tier: none` fraction, `derived-from-header`
  fraction.

**This is the mechanism by which the owner's "inventory all the features" goal is actually reached.**
Coverage grows monotonically and cannot regress; new features never widen the gap. A hard
"162 by date X" target is explicitly rejected — it creates exactly the pressure that produces
restatements, which is the failure the whole project exists to prevent.

⛔ **Sequencing correction over plan A.** Plan A armed this only after wave 1 authoring
(*"there must be real entries before the gate is armed"*), which means every artifact shipped during
a 90–110-hour authoring effort is **ungated** — A's own promise that "new features never widen it"
does not hold during the window it matters most. The ratchet is armed **before** bulk authoring, on
the strength of the ~8 seed entries P0 and P4 naturally produce.

### 10.2 ⛔ R6 — Merge-time re-measure. Red-team blocker.

**Precedent, in this repo, this session's lineage:** PR #991. Two branches each raised a shared
baseline correctly in isolation and wrongly after the other merged; the wrong value still passes on
its own branch and surfaces later as unexplained drift. Any multi-batch rollout reproduces this per
batch, and it applies to **every** ratchet this plan adds: coverage, payload ceiling, byte size,
unprobed fraction, `derived-from-header` fraction.

**Rule — required on every ratchet, every batch, no exceptions:**

> The last step before merge is **recompute the ratchet value on rebased HEAD**, not trust the value
> computed when the branch was cut. A ratchet number in a diff whose base is not `origin/main` at
> merge time is invalid.

Enforcement, so this is not exhortation: `check-ratchet-freshness.py` records, alongside each ratchet
value, the `origin/main` SHA it was measured against. CI fails if that SHA is not the PR's actual
merge base. ⛔ An absent behind-count means **UNKNOWN**, never up-to-date.

### 10.3 ⛔ Half-finished incentive — the rationale-mill risk (red-team #7)

Once the gate is armed and the dedicated authoring push ends, the path of least resistance for any
unrelated PR adding a script is a `tier: none` entry with a one-line rationale. The gate cannot
distinguish "this team stopped caring" from "genuinely no cheap observable exists" — it just demands
that *some* entry exist. That silently reproduces the 162-stale-summaries failure, spread out
post-hoc instead of front-loaded.

**Mitigation:** track the **rate of growth** of `tier: none` entries, not just the raw fraction. A
growth rate exceeding the rate observed during the dedicated authoring phase fires a signal — the
gate has become a rationale mill. Reported, not blocking: blocking it would push authors toward a
false `tier: reachability`, which is worse.

### 10.4 ⛔ Substrate constraints (both panels partly missed these)

- **`plugins/ravenclaude-core/{hooks,scripts}/` deny Bash writes**, even read-only operations in some
  shapes. Every edit there uses **Write/Edit tools**. `chmod` and `git update-index --chmod` are both
  denied on that path.
- **This plan adds no `plugins/*/hooks/*.sh`.** New executables live in root `scripts/` and are
  invoked as `bash scripts/x.sh` / `python3 scripts/x.py` — no mode bit needed, matching how
  `audit-gates.sh` already invokes its helpers. If a future follow-on does need a hook, the shipped
  precedent is `ask-on-ambiguity.sh`: author in `plugins/ravenclaude-core/scripts/`, register in
  `hooks.json` with a `bash ` prefix, and skip the `hooks/`-directory fight entirely. Adding a real
  `hooks/*.sh` also stales `index.html`'s hook count and forces
  `check-plugin-detail-render.mjs`'s wired-hook ratchet up **with a cause comment**.
- ⛔ **Parallel authoring agents are DENIED by `guard-premise.sh` fail-closed** (beacon absent +
  Bash ran → DENY). The only escape that reaches a **dispatched subagent** is the **file-based
  control** — env vars do not cross into the hook's process. **Pre-stage the file-based control
  before dispatching any authoring wave.** Neither panel mentioned this and plan A's P8 was
  explicitly "parallelisable across agents."
- ⛔ Do not put a literal blocked command in a commit message — the tribunal matches a *description*
  of a command as the command itself.
- ⛔ No `paths:` filter may be added to any required workflow. A skipped *job* reports Success; a
  skipped *workflow* reports nothing and hangs the PR forever.

### 10.5 Acceptance

1. A PR adding a fixture file under `hooks/` with no entry **fails**; adding the entry makes it pass.
2. The ratchet fails on a deliberately deleted entry.
3. `check-ratchet-freshness.py` fails a PR whose ratchet SHA is not its merge base — proven by
   constructing the #991 shape deliberately.
4. No `paths:` filter on `validate-marketplace.yml`, mechanically asserted by a grep in the audit.
5. Suite output greped by **literal gate name**.

---

## 11. Phase 9 — Wave 1: ~20 mechanism entries at the owner's bar

`depends_on_claims: [6, 7, 8, 9, 10, 11]`

### 11.1 The unit is the MECHANISM, not the file

The owner's example — *"hooks can send a message two ways and only one reaches the model"* — is a
mechanism fact **true of all 47 hooks at once**. Writing it into 47 entries writes the same fact 47
times. The honest shape of the corpus is ~15–25 genuine mechanism facts that generalise across many
artifacts, plus ~140 artifacts whose only honest per-file statement is a summary. Per-artifact
`covers` binding survives intact: **a mechanism entry can list 47 paths in `covers[]` and coverage
still computes per artifact.**

### 11.2 The bar, restated as three named parts

Every qualifying entry names all three, or it is a restatement:

| | Name | The `_advise.sh` example |
|---|---|---|
| N1 | **Counterfactual** — what a competent reader would have assumed instead | "stderr at exit 0 reaches the model" |
| N2 | **Discriminator** — the observation separating the two readings | "a SessionStart `additionalContext` sentinel came back in every trial; the stderr token never did" |
| N3 | **Consequence** — what is different because of it | "advisory hooks advised the terminal, never the model, for their entire service life" |

Author-facing test: *delete your nuance paragraph. Could a competent engineer reconstruct it from the
feature's name plus its 200-char summary? If yes, it is a restatement.*

### 11.3 The wave-1 set

The seven zero-coverage names from claim 6 — `premise-gate`, `probe-validity`, `triage-outcome`,
`cause-taxonomy`, `ledger`, `set-conservation`, `_advise` — plus the rewrite of `claim-grounding`
(written before the channel defect, so now **incomplete rather than absent**), plus the measured
mechanism facts already sitting in `claims-table.md` and hook headers: the two-channel fact; the
`additionalContext` **concatenates** vs `updatedToolOutput` **replaces** asymmetry (claim 9); the
version-keyed plugin cache so merged ≠ live (claim 10); divergent `--must-fail` exit conventions
(claim 11); a failing Bash `tool_response` carrying no exit-code field (claim 8); T-PROSE firing on
the **certainty stamp**, so the confident version of a claim is the one that gets denied; T-PROSE
firing only on file **CREATE** (GT6); the staleness double-exemption (GT1); the self-heal grep
contract (GT4).

### 11.4 ⛔ Test the bar's transferability in week 1, not month 3

The owner's example is drawn from the **one artifact class where the bar is achievable** — hooks have
a machine-readable contract with a host process. It was generalised to four classes without test.
**Author 3 real entries for 3 skills before authoring 54.** If a competent author cannot produce a
genuine counterfactual for 3 skills, the standard does not transfer, and the plan should know that in
week 1. If it does not transfer, skills get honest summary entries with `verify.strength: static`
and the plan says so — which is a legitimate outcome, not a failure.

### 11.5 Drafts lane

Skeletons live in `plugins/ravenclaude-core/knowledge/inventory-drafts/` — **outside** the concepts
glob, so a skeleton with `nuance: TODO` is invisible to the dashboard and to CI, and **promotion is
the gate**. Verified allowed by `.repo-layout.json:68`; `check-lineup-citations.py` is opt-in via an
explicit marker, and `generate-document-map.py` globs non-recursively, so drafts escape both.
⛔ **Add what plan A omitted:** a draft older than 90 days is either promoted or removed, reported by
`coverage --report`. Otherwise the drafts lane becomes the 162 stale summaries, relocated.

### 11.6 Regen chain, wrapped (adopted from plan B)

Every batch regenerates in order: `concepts.py` → `render-concepts.py` → `generate-dashboards.py` →
`generate-index-dashboard.py`. Ship **one** wrapper, `scripts/regen-inventory.sh`, so a batch author
runs one command. 12 batches × 4 manual steps is 48 chances to regenerate out of order, and a stale
generated artifact reddens CI for the **right** reason in a way that looks like the **wrong** reason
to an unfamiliar reader.

### 11.7 Acceptance

1. All ~20 pass `concepts.py --check` and the nuance floor.
2. All ~20 have `verify.tier != none`, or a written rationale.
3. The judge, calibrated at ≥ 22/24, labels ≥ 18/20 as `nuance`. Any `restatement` verdict is
   reviewed, not auto-failed.
4. The sampled review scores ≥ 80% and its verdicts are in the committed ledger.
5. They render with **no edit** to `dashboard.html` or `concepts.json` — verified by regenerating and
   diffing. ⛔ `dashboard.html` is generated and ~10 MB: regenerate, never hand-edit.
6. The 3-skill transferability test is recorded with a literal verdict.

---

## 12. Phase 10 — Scheduled sweep + operator health card

`depends_on_claims: [10, 15]`

New `.github/workflows/inventory-sweep.yml`: `schedule` (off the hour — scheduler spikes are real)
plus `workflow_dispatch`. Runs T0+T1, `coverage --report`, and the non-blocking calibrated judge on a
sample.

⛔ **This workflow must NOT become a required status check** and must not be added to the branch
ruleset. A scheduled workflow reports nothing on a PR, and a required check that reports nothing
hangs the PR forever.
⛔ Notification lines carry **derived labels only** — counts and entry ids, never probe output.

**The operator health card** (adopted from plan B, absent from plan A): the Learn tab is where a
reader browses; it is not where an operator looks. A read-only dashboard card surfaces the harness's
own state: probes registered · probes executed · independent census · `effect-status: unverified`
count · entries failing content drift · `tier: none` count and its growth rate ·
`derived-from-header` count · unprobed fraction. These are **operational state**, not knowledge, and
they belong on an operator surface rather than inside a collapsed concept card.

**Acceptance:** a dispatch run completes T0+T1 and writes a derived-label-only report; a deliberately
broken probe makes the run **red**; the sweep is **not** in the branch ruleset (asserted by `gh api`);
an entry aged past its window fails the **sweep** (proven with a dated fixture) while only **warning**
on PR.

---

## 13. Phase 11 — Long-tail coverage, by ratchet

`depends_on_claims: [5, 6, 14]`

The owner's "inventory all the features" goal completes here, on a longer clock, driven by the
mechanism rather than by a sprint:

- Every **new** artifact is covered at inception (§10.1) — the gap can only shrink.
- The remaining backlog is authored opportunistically: when an artifact is touched for any reason,
  its entry is authored or updated in the same PR. Cost lands on work already happening.
- Optional dedicated waves of ~20, each with the §9.3 ledger gate, whenever capacity exists.
- ⛔ **Re-measure claim 5 in this phase and state the counting rule used.** The table says 48 hooks;
  two independent in-session measures returned 47 (GT16). Inherit the number from nothing —
  measure it and write down what was counted.

⛔ **Family entries** are permitted where per-file nuance genuinely does not exist (adapters, shims):
one entry listing all members in `covers[]`, so coverage still computes per artifact. This is a
quality decision, not a coverage shortcut.

---

## 14. Reconciled dependency DAG

```
                    P0  Live defect (R1)              <- BEFORE any inventory work
                     │
                    P1  Empirical spikes (R10, cl.15) <- literal first step of the inventory track
                     │
        ┌────────────┴────────────┐
        │                         │
   P2 Self-heal contract     P4 Path-keyed harness      <- P4 needs nothing from P2/P3.
      + collect-all (R4)        + sweep-of-sweep (R8)      Value lands HERE, week 1.
        │                         │
   P3 Staleness, both            │
      escapes (R3)               │
        │                         │
        └────────────┬────────────┘
                     │
              P5  Schema delta (R12 fields, R9)
                     │
              P6  Surfacing + budgets (R5, R12 render)
                     │
              P7  Nuance gate: floor + blocking ledger (R7)
                     │
              P8  Inception ratchet + merge-time re-measure (R2, R6)
                     │
              P9  Wave 1 — ~20 mechanism entries
                     │
              P10 Scheduled sweep + operator health card
                     │
              P11 Long-tail coverage, by ratchet
```

- **Critical path:** P0 → P1 → P2 → P3 → P5 → P6 → P7 → P8 → P9 → P10 → P11.
- **Off the critical path, starts immediately after P1:** **P4**. This is deliberate — the harness is
  where the value density is, and it must not wait on the schema.
- **Blocking risk is P1**, not volume. If S1 shows the ±6-line window cannot accommodate a
  multi-claim body, the authoring rule becomes one control per **claim** and §12's effort estimate
  rises; no phase is cancelled. If S2 says no `claude -p` in CI, §7.4 step 2 activates; no phase is
  cancelled.
- **Parallelism after P8:** long-tail waves are disjoint by artifact set and touch no shared file
  except `concepts.json`, which is generated — conflicts are regenerated, never hand-merged.
  ⛔ Pre-stage the file-based premise control before dispatching any parallel wave (§10.4).

---

## 15. Combined risk matrix

Severity is P×I, capped at the higher when one is Critical. **Owner** = which panel's design the risk
came from. Every row names the phase that closes it — a risk with no owning phase is a waiver in §21.

| # | Risk | From | P | I | Sev | Closed by |
|---|---|---|---|---|---|---|
| X1 | New `--check` failure class aborts post-merge self-heal; `main` carries stale dashboard/index/SVGs across many merges behind a `::warning::` | A | 0.8 | Crit | 🔴 | **P2** — stable `RC-CONCEPTS-CLASS` marker + required "self-heal still completes" test |
| X2 | 162 auto-generated mermaid diagrams: render fails, output reverted, `::warning::` only, self-heal continues green, SVGs permanently stale | A | 0.75 | High | 🔴 | **P6.2** — diagrams opt-in; batches ≤ 20; `render-concepts.py --check` a PR gate for changed concepts |
| X3 | Blocking calendar staleness across a large corpus turns every PR red in waves (~0.9/day at 180d; ~5.4/day at 30d) | A + B | 0.85 | High | 🔴 | **P3.3** — content drift is primary and blocking; calendar warns on PR, blocks on sweep; calendar-blocking retained only for the ~17 platform-facts |
| X4 | The live channel defect stays open while an inventory is authored around it | neither | 0.9 | High | 🟠 | **P0** — the whole phase |
| X5 | Harness silently no-ops / counts itself and cannot see its own blindness | both | 0.7 | High | 🟠 | **P4.4** — independent `git ls-files` census, three counts, downward-move TELL, permanently-red canary |
| X6 | Nuance gate passes trivially-true mechanism-vocabulary restatements at scale | A (B concedes) | 0.8 | Med | 🟠 | **P7.2 F2 dual-baseline** + **P7.3 blocking sampled review with a committed ledger** |
| X7 | ~162 entries never finish; corpus stalls at 30–60% and partial reads as full | both | 0.8 | Med | 🟠 | **P8** ratchet makes a stall a stable honest fraction; **re-scoped to ~20 + ratchet** so the stall is planned, not hoped |
| X8 | Learn payload grows ~24k → ~90k elements injected on one click; gated by nothing | both | 0.7 | High | 🟠 | **P6.1** — enforced per-panel payload ceiling |
| X9 | `dashboard.html` + `index.html` grow ~8–12 MB each; no byte gate exists anywhere | both | 0.7 | Med | 🟠 | **P6.1** — byte ratchet on both surfaces, seeded before authoring |
| X10 | Ratchet-race: parallel batches compute against the same stale baseline, each correct alone, wrong after the other merges | both | 0.6 | High | 🟠 | **P8.2** — merge-time re-measure + `check-ratchet-freshness.py` SHA binding |
| X11 | Weak-check tier renders identically to a strong one — 96 of 162 show a check that looks like verification | both (A deferred it to an optional phase) | 0.9 if P6 slips | High | 🟠 | **P5.3 + P6** — `verify.strength` badge, non-optional |
| X12 | Restamp is an edit, not a review — becomes the new stderr-advisory | A | 0.6 | Med | 🟡 | **P3.4** — `--reason` ≥30 chars, committed restamp log, unchanged-nuance ratio reported |
| X13 | Parallel authoring agents denied fail-closed by `guard-premise.sh`; env-var escape does not cross into a subagent | A | 0.65 | Med | 🟡 | **P8/§10.4** — pre-stage the **file-based** control before dispatch |
| X14 | Secret/PII egress into committed concept fields (`nuance_evidence`, `nuance_source`) | both | 0.5 | High | 🟠 | **P5.2 R9** — negative rule + `check-inventory-evidence.py` shape gate |
| X15 | T-PROSE denies the authoring write; discovered at file #40 not #1 | A asserted, never tested | 0.4 | Med | 🟡 | **P1 S1** — empirical canary first; 4-line nuance cap; `control:` **above** the claim |
| X16 | `--check` short-circuits, masking every later violation class | A | 0.7 | Med | 🟠 | **P2.3** — collect-all with a dual-violation fixture |
| X17 | `covers[]` under-declared, so the tripwire silently never fires for a real drift | A | 0.5 | Med | 🟡 | **P3.5** — partial textual completeness check; residual waived §18 |
| X18 | Inception gate degrades into a `tier: none` rationale mill after the push ends | both | 0.6 | Med | 🟡 | **P10.3** — growth-**rate** signal, not just raw fraction |
| X19 | B's Gate-132 per-batch ratchet-raise process is built for a gate that cannot fire | B | 1.0 if executed | Low | 🟡 | **P6.1 (R5)** — process deleted; replaced by the enforced payload budget |
| X20 | New gates registered in only one of the dispatcher / main sequence, or greped by number | both | 0.4 | Med | 🟡 | Every phase's acceptance: register in **both**, grep by **literal name** |
| X21 | Apostrophe class recurs — in a bash block (fails **open**, silently stops gating) or in a prose-rendering path | both | 0.4 | Med | 🟡 | **P1 S4** audit + per-phase apostrophe grep |
| X22 | Scheduled sweep unavailable and skips silently | both | 0.3 | High | 🟡 | **P5.4** — age-based gate is PRIMARY (degrades correctly even if the sweep's own write path breaks); `effect-status: unverified` is secondary; sweep reports UNKNOWN, never green |
| X23 | LLM judge reports verdicts while broken | — | 0.15 | High | 🟢 | **P7.4** — A's ≥22/24 same-run calibration bar, adopted verbatim. Strongest single control in either document |
| X24 | Merged ≠ live: the fix ships but no consumer sees it | claim 10 | 0.5 | Med | 🟡 | Every phase's acceptance: bump `plugin.json`, run `sync-plugin-versions.py` **and** `generate-copilot-plugin.py` |

---

## 16. Red-team mitigations — every one, mapped

| Red-team # | Failure mode | Sev | Mitigation in this plan |
|---|---|---|---|
| 1 | Harness silently no-ops; registered-vs-executed can shrink together | HIGH | **P4.4** — independent `git ls-files` census (never `concepts.json`); three counts; invoked-by-one-of-three cross-check; downward-move TELL; permanently-red canary. ⛔ R8 satisfied |
| 2 | Self-blocking on T-PROSE | MED-HIGH | **P1 S1** as the literal first executable step of the inventory track (⛔ R10). Narrowed by GT6 (CREATE-only), but tested rather than asserted. 4-line nuance cap; `control:` above the claim; one control per **claim** if S1 says so |
| 3 | **BLOCKER** — ratchet race, wrong baseline passes on its own branch | HIGH | **P8.2** (⛔ R6) — merge-time re-measure mandatory on every ratchet; `check-ratchet-freshness.py` binds each value to the merge-base SHA; PR #991 shape reproduced as the must-fail fixture |
| 4 | Scheduled sweep cannot run; marker-write itself fails | MEDIUM | **P5.4** — age-based staleness PRIMARY (survives a broken sweep write path), `effect-status: unverified` secondary. UNKNOWN, never green |
| 5 | Secret/PII egress into committed concept files | MEDIUM | **P5.2** (⛔ R9) — negative rule stated explicitly, plus a deterministic shape gate. `log-probe.sh`'s derived-label discipline extended from the gitignored tier to the committed authoring surface |
| 6 | **BLOCKER** — gameable deterministic nuance gate; advisory-only judge | HIGH | **P7** (⛔ R7) — floor kept as a cheap floor; dual-baseline F2 closes the measured "tokens are in the open file" flaw; B's sample review adopted and made **blocking via a committed ledger `coverage --check` reads**; 4 adversarially-authored negatives added to the golden set |
| 7 | Half-finished → inception gate becomes a rationale mill | MEDIUM | **P10.3** — growth-rate signal for `tier: none`, reported not blocking (blocking would push authors to a false `reachability`) |
| 8 | Apostrophe class beyond the bash scripts | LOW-MED | **P1 S4** — trace every authored-prose consumer and confirm Python-string, not shell-interpolation; per-phase apostrophe grep on single-quoted blocks |

**Both red-team blockers (#3 and #6) are closed as adjudicated (R6, R7).**

---

## 17. Unsettled claims — the concrete settling step for each

| Row | Status | Concrete settling step | Phase | If it settles the other way |
|---|---|---|---|---|
| **14** — every core feature has a cheap reachability observable | **owner-gated / CAPPED 2026-08-19.** Not assumed; capped | Hand-run one probe **and its control** per class in §6.2 against one representative artifact, and record a 11-row table of {observable found? control fired?}. ⛔ **Exit condition: any class whose control does not fire is demoted to `tier: none` with a written rationale. A probe with no working control does not ship.** | **P4** | Already absorbed — three classes are named as reachability-only up front, and `verify.strength` renders the cap to the reader (⛔ R12) |
| **15** — a scheduled sweep can run in CI without credentials or a live model call | **partially settled (cheapest-partial exit).** T0 ≈80% needs only bash+python3 | **S2:** a `workflow_dispatch`-only job running `command -v claude; claude -p 'reply OK'` under scheduled-CI conditions; record the literal yes/no | **P1** | §7.4 step 2 activates: T2 moves LOCAL, CI gates on attestation **age**. No phase is cancelled. ⛔ Residual: the sweep must report **UNKNOWN**, never green, on a T2 skip |
| **5** — 48 hooks / 54 skills / 15 agents / 45 scripts | settled as a WARN observation, but two measures returned **47** hooks | Re-measure and **state the counting rule used** (`_`-prefixed sourced helpers included or not); write the rule into the census script so it cannot drift | **P11** | Cosmetic — the ratchet's denominator comes from the independent census, which carries its own stated rule |
| **claims-table footer** — the QUALITY standard (nuance, not coverage) | asserted, never tested for transferability beyond hooks | **Author 3 real entries for 3 skills before authoring 54** and record a literal verdict on whether a genuine counterfactual exists | **P9.4** | Skills get honest summary entries at `verify.strength: static`, and the plan says so. A legitimate outcome, not a failure |
| **Rows 1–4, 6–13, 16** | settled | no action; they are the ground the plan stands on | — | — |

---

## 18. Alternatives considered

| # | Alternative | Trade-off | Verdict |
|---|---|---|---|
| 1 | Parallel `inventory.json` registry beside `concepts.json` | Avoids concept-schema churn, but forks the SSOT and needs dashboard plumbing scope.md explicitly does not want | **Rejected** |
| 2 | Big-bang authoring of ~162 entries (both panels) | Reaches the stated goal directly, but costs 90–110 person-hours with ~15–25% completion probability, and puts a 10-line check that finds real defects today behind month 4 | **Rejected** — replaced by harness-first + ratchet (⛔ R2). The goal is **not** dropped; §19 states the curve |
| 3 | One entry per artifact (~162) vs per mechanism (~20 + families) | Per-artifact answers "does feature X have an entry"; per-mechanism matches the owner's actual bar and avoids writing one fact 47 times | **Per-mechanism adopted** — `covers[]` can list 47 paths, so coverage still computes per artifact. A's own schema refutes A's own volume |
| 4 | Probes keyed by concept id (plan A: "the registry IS concepts.json") | One SSOT, no second list — but couples every check to authored entries | **Rejected** — probes are keyed by **artifact path**; entries inherit verdicts. Decoupling is what lets the harness run in week 1 |
| 5 | Runtime-only harness: a real `claude -p` bake-off per feature | The only thing proving end-to-end delivery; ~162 model calls per sweep, unbounded cost, blocked on claim 15 | **Rejected as the default lane**; retained as T2, sampled, with a positive control in every batch |
| 6 | `verified_against` + `git log -1 --format=%cI` (plan B) as the drift axis | Simpler, but a git-log timestamp is fragile to squash, rebase and shallow clones | **Idea adopted, implementation rejected** — content drift via `covers_digest` is the same idea with a robust instrument |
| 7 | 30-day calendar staleness for `ravenclaude-built` (plan B) | Honest about a weekly-shipping repo, but ~5.4 re-verifications/day at scale; the gate gets disabled within a month | **Rejected** |
| 8 | 180-day **PR-blocking** calendar staleness (plan A) | An enforceable deadline, but ~0.9/day forever and wave-synchronised expiry turns every open PR red | **Rejected as PR-blocking**; retained as a **sweep**-blocking warning |
| 9 | Auto-derive `nuance` from each artifact's `⛔ WHY THIS EXISTS` header | Cheap and high-yield for ~25 artifacts, but a derived nuance is definitionally derivable | **Adopted as a SEED only** — the header lands in `nuance_evidence`; the entry is counted in the separately-reported `derived-from-header` class and ratcheted down |
| 10 | Make the LLM judge a blocking merge gate | Higher precision, but a non-deterministic merge gate and an uncalibrated judge fails toward green | **Rejected** — judge stays calibrated + advisory; the blocking human step is the sampled review, whose *mechanism* (ledger entry present) is deterministic |
| 11 | B's per-batch Gate-132 ratchet-raise process | Built for a gate that cannot fire — `panel-learn` is islanded at a flat cost of 2 | **Deleted** (⛔ R5); replaced by an enforced payload/byte budget |
| 12 | Skip the dashboard `verify.strength` badge (plan A's optional P9) | Saves a phase; leaves 96 of 162 entries rendering a weak check identically to a strong one | **Rejected** (⛔ R12) — non-optional |
| 13 | A `PostToolUse` inventory nudge at write time | Catches a missing entry earlier than PR time; needs a new `hooks/*.sh` with a mode bit this environment cannot set, plus `index.html` + render-ratchet reconciliation | **Deferred**, named as a follow-on, not silently dropped |

---

## 19. Honest effort estimate and the coverage curve ⛔ R2

### 19.1 What the panels estimated, and what it actually costs

Plan A budgeted **~50 person-hours** for ~162 entries at 10–25 min each. That estimate omits three
measured costs:

1. **The regeneration chain per batch** — `concepts.py` → `render-concepts.py` →
   `generate-dashboards.py` → `generate-index-dashboard.py`, four steps, every batch. Plan A does
   not name the chain at all.
2. **162 mermaid renders** — one `npx` process per diagram, requiring Chromium and its system libs
   fetched on demand, with an all-or-nothing revert on failure that continues green.
3. **8–12 MB of inlined SVG per surface**, on top of 10.27 MB and 9.26 MB, with **no byte gate
   anywhere** in 336 gate headers.

**Corrected figure for the big-bang shape: ~90–110 person-hours** — the largest single authoring
effort in this repo's recorded history by a wide margin, with a realistic completion probability of
**~15–25%**.

### 19.2 What this plan costs

| Block | Effort | Value delivered |
|---|---|---|
| **P0** — live defect | **hours** (≈ 1 day) | Closes the class that started the project. Highest value/hour in the entire plan |
| **P1** — spikes | ≈ 0.5 day | Converts three asserted facts into measured ones before anything is built on them |
| **P2–P3** — self-heal + staleness | ≈ 1–2 days | Removes a critical integration failure and a masking short-circuit that would otherwise ship with the first new check |
| **P4** — path-keyed harness | ≈ 3–5 days | **Finds real defects on day 1** with zero entries authored. GT13 is the proof |
| **P5–P7** — schema, surfacing, budgets, nuance gate | ≈ 4–6 days | Makes the corpus gateable and honest; caps unbounded artifact growth before it starts |
| **P8** — inception ratchet | ≈ 1–2 days | The forcing function. From here, coverage cannot regress |
| **P9** — ~20 mechanism entries | ≈ 10–15 person-hours | The part a reader actually reads |
| **P10** — sweep + health card | ≈ 1–2 days | The operator surface and the cadence half of R3 |
| **P11** — long tail | **amortized, not scheduled** | Completion, driven by the ratchet |

**Total to a fully-enforced harness plus 20 high-value entries: ≈ 3 working weeks.**
**Total to ~162 entries: still ~90–110 person-hours of authoring** — that number does not shrink; it
is *sequenced* so it is no longer on the critical path and no longer a precondition for any value.

### 19.3 The coverage curve

| Milestone | Covered artifacts | Entries | What a reader/operator has |
|---|---|---|---|
| End of P0 | 0 | 0 | The motivating defect **closed**, and a reusable assertion that catches the class |
| End of P4 | **all ~162 probed or statically checked** | 0 | Every artifact has a **verdict** — a probe ran or a static check ran — with zero entries authored |
| End of P8 | ~8 | ~8 | Coverage is now **monotonic**. The gap can only shrink |
| End of P9 | ~50–90 (mechanism entries list many `covers[]` paths each) | ~20 | The mechanism nuances a reader would not have guessed |
| +6 months | ~60–75% | ~40–60 | Growth from the inception gate plus opportunistic authoring |
| +12–18 months | → 100% | ~60–100 | Completion, guaranteed by the ratchet, not by a sprint |

⛔ **The distinction that matters:** *verification* coverage reaches ~100% at the end of **P4**;
*entry* coverage reaches ~100% asymptotically via the ratchet. Both panels conflated the two and
consequently put the cheap, high-value one behind the expensive, low-probability one.

⛔ **What half-finished looks like, and why it is safe:** a stall at 50/162 entries leaves a stable,
honestly-reported fraction that cannot rot backwards, with the highest-value entries done first by
design, and **no** empty shells in the dashboard (the drafts lane is outside the concepts glob). A
stall **without** a ratchet is worse than none, because partial coverage reads as full coverage to
anyone who does not check the denominator. **The ratchet is what makes an unfinishable target safe to
aim at** — and it is equally what makes a ~20-entry corpus a legitimate stopping point rather than an
abandonment.

---

## 20. What this plan does NOT deliver

Stated plainly, because an admitted gap beats a false claim of coverage.

1. **It does not verify that any nuance is TRUE.** The floor checks shape and falsifiability; the
   sampled review checks non-obviousness; only a probe checks truth, and only for probed entries.
   Entries carry `unprobed:` with a reason, counted and surfaced.
2. **It does not prove any skill or agent is ever LOADED by a model.** 96 of 162 artifacts have no
   cheap runtime observable; their consumer is a model deciding to read a file. What ships is
   **findability and reference integrity** — real (GT13 found two live defects) but narrower than
   reachability. `verify.strength: static` renders that limit to the reader (⛔ R12).
3. **It does not deliver ~162 authored entries in this project.** It delivers ~20 plus a mechanism
   that reaches the rest. The owner's goal is met on a longer clock, not abandoned (§19.3).
4. **It does not make the nuance bar machine-checkable end to end.** ⛔ R7 is explicit: the bar is not
   fully automatable, and a fake metric that passes while entries teach nothing is worse than an
   admitted human step. There is a required human/fresh-model step and it is the real gate.
5. **It does not gate agent dispatch before it happens.** Agent reachability is **observational** —
   `SubagentStart` fires post-spawn and a pre-dispatch DENY has never been verified live. The schema
   says `strength: observational` rather than implying stronger coverage than exists.
6. **It does not detect a mis-declared `covers[]` that omits a dependency never named as a path.**
   §5.5's check is textual. §21-W3 waives the rest.
7. **It does not certify that authored evidence text contains nothing sensitive.** §7.2's gate is a
   shape heuristic, not a secret scanner. §21-W4 waives the rest.
8. **It does not add a write-time inventory nudge.** That needs a new `hooks/*.sh` with a mode bit
   this environment cannot set. Deferred, named (§18 alt 13), not silently dropped.
9. **It does not touch the other 181 plugins.** Core only, per scope R1.
10. **It does not re-litigate the advisory-channel fix merged at v0.283.0.** P0 addresses the
    *remaining* 8 exposed hooks and the missing test assertion, which are a different, still-open
    half of the same class.

---

## 21. Residual risks and accepted-risk waivers

Each waiver names what is accepted, why the cheapest mitigation was not taken, and the TELL that
would show the risk has materialised.

**W1 — A plausible-sounding false nuance merges.**
*Accepted because:* the only real truth check is a probe, and 96 of 162 artifacts have none. The
floor, the dual-baseline count, the calibrated judge, the sampled review and the covers-digest
re-read are five independent partial filters; adding a sixth partial filter has sharply diminishing
returns against the cost.
*TELL:* a sampled-review pass rate that stays high while `derived-from-header` count rises — entries
are getting more mechanically plausible and less original.

**W2 — Findability is not reachability for 96 of 162 artifacts (claim 14's cap).**
*Accepted because:* the alternative is ~69 `claude -p` calls per sweep with unbounded cost, blocked
on claim 15. The cap is owner-gated as of 2026-08-19.
*Mitigated by:* T2 sampling at k=8/night with a positive control **in every batch**, covering all 69
in ~9 days when a model call is available; and by rendering the limit (⛔ R12).
*TELL:* a `static`-strength check-class reporting 0 findings for many consecutive sweeps is
**expected** in steady state and is **not** by itself evidence of blindness — the permanently-red
canary (§6.4) is what separates "nothing broke" from "the sweep went blind." ⛔ This is the one place
where a long green streak is legitimate, and the canary is the only thing that makes it readable.

**W3 — `covers[]` completeness is only textually checked.**
*Accepted because:* a complete check would require inferring which facts a prose paragraph depends
on, which is the same unsolved problem as W1.
*TELL:* an entry whose nuance is later found false while its digest never tripped. Log these; three
occurrences should reopen the design.

**W4 — Committed evidence fields are shape-gated, not secret-scanned.**
*Accepted because:* a real secret scanner over free prose has a false-positive rate that would make
authoring unworkable, and the fields are meant to hold **pointers and labels**, not payloads (⛔ R9).
*TELL:* any `nuance_evidence` value exceeding ~300 chars, or containing a newline-separated block —
both are reported by `coverage --report`.

**W5 — Calendar staleness does not block a PR.**
*Accepted because:* the arithmetic (§5.3) makes a blocking calendar gate at corpus scale a periodic
repo-wide outage, and a gate that gets disabled protects nothing.
*Mitigated by:* content drift blocking on PRs — the axis that fires when a fact can actually have
become false — plus calendar blocking on the sweep and for the ~17 platform-facts.
*TELL:* median `last_verified` age across inventory entries trending upward across sweeps.

**W6 — The inception gate can degrade into a rationale mill.**
*Accepted because:* the alternative (blocking `tier: none`) pushes authors toward a false
`reachability` claim, which is strictly worse — a wrong strong label beats no label only for
appearances.
*TELL:* §10.3's growth-rate signal.

**W7 — ~162-entry completion is not guaranteed on any date.**
*Accepted deliberately.* A hard "162 by date X" target creates exactly the pressure that produces
restatements — the failure the project exists to prevent. The ratchet guarantees the **direction**,
not the date.
*TELL:* `covered_artifacts / total_artifacts` flat across two consecutive quarters with new artifacts
still landing means the gate is being satisfied minimally; pair it with W6's signal.

**W8 — S1 may find that T-PROSE needs one control per claim, not one per file.**
*Not yet accepted — it is measured in P1.* If it lands that way, per-entry authoring cost rises
materially and §19.2's P9 figure grows. Named here so it is a known variance, not a surprise at
file #40.

---

## 22. Phase index — `depends_on_claims` in one place

⛔ R11: these lines are literal and machine-read. **Numeric row ids only. No prose in this field** —
prose here silently breaks the premise gate and has already made it cite non-existent rows.

```
P0   Close the live defect (R1)                       depends_on_claims: [7, 9, 12]
P1   Empirical spikes (R10, claim 15)                 depends_on_claims: [13, 15, 16]
P2   Self-heal contract + collect-all (R4)            depends_on_claims: [1, 13]
P3   Staleness, both escapes (R3)                     depends_on_claims: [3, 13]
P4   Path-keyed harness + sweep-of-sweep (R2, R8)     depends_on_claims: [5, 12, 14]
P5   Schema delta (R9, R12 fields)                    depends_on_claims: [1, 3, 13, 14]
P6   Surfacing + budgets (R5, R12 render)             depends_on_claims: [4, 16]
P7   Nuance gate: floor + blocking ledger (R7)        depends_on_claims: [11, 14]
P8   Inception ratchet + merge-time re-measure (R6)   depends_on_claims: [5, 10]
P9   Wave 1 — ~20 mechanism entries                   depends_on_claims: [6, 7, 8, 9, 10, 11]
P10  Scheduled sweep + operator health card           depends_on_claims: [10, 15]
P11  Long-tail coverage by ratchet                    depends_on_claims: [5, 6, 14]
```

---

## 23. Adjudicated-ruling index — where each lands

| Ruling | Landed in |
|---|---|
| **R1** live defect first | §2 (P0) — all of it; X4; §16 |
| **R2** coverage by ratchet, not big-bang | §6 (P4 decoupling), §10 (P8), §19 (effort + curve), §18 alt 2 |
| **R3** staleness double-exemption, BOTH escapes | §5 (P3), GT1, GT2 |
| **R4** covers_digest aborts self-heal; short-circuit masks | §4 (P2), GT3, GT4, GT5, X1, X16 |
| **R5** Gate-132 premise false; enforce a payload budget | §8.1 (P6), GT9, X8, X9, X19, §18 alt 11 |
| **R6** merge-time re-measure | §10.2 (P8.2), GT14, X10, §16 row 3 |
| **R7** nuance gate deterministic AND blocking-human | §9 (P7), X6, §16 row 6, §20-4 |
| **R8** the harness must not count itself | §6.4 (P4.4), X5, §16 row 1 |
| **R9** no raw bytes in committed fields | §7.2 (P5.2), X14, §16 row 5, W4 |
| **R10** T-PROSE CREATE-only; spike is the first step | §3.1 (P1 S1), GT6, X15, §16 row 2, W8 |
| **R11** clean numeric `depends_on_claims` | every phase heading; §22 |
| **R12** weak checks must render distinctly | §7.3 (P5.3), §8 (P6), X11, §20-2, §18 alt 12 |
