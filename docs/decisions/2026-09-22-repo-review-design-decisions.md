# Repo review — design decisions needing your input (2026-09-22)

A scheduled full-repo review ran the three-panel process again (6 parallel dimension finders on a lighter
model → one heavier validation/dedup pass → per-item tie-break on the ambiguous priorities), then **every
surviving finding was re-verified against source in the main session — not taken on a subagent's word**, per
this repo's Claim-Grounding discipline.

**The mechanical baseline is still spotless.** Re-confirmed this session: `marketplace.json` + all 182
`plugin.json` valid, `.repo-layout.json` valid, all shell hooks/scripts pass `bash -n` and are executable,
`check-frontmatter.py` green, `prettier --check .` and `ruff check .` both clean on the whole tree,
`sync-plugin-versions.py --check` in sync. The genuine findings below are subtle logic/architecture matters
that no gate catches.

- **Three code/precision fixes with no design input were implemented directly** and ship in the
  accompanying PR (see "Implemented" at the bottom) — each low-blast, clearly-correct, and validated locally
  (self-tests re-run, prettier/ruff clean). Three further no-design fixes surfaced but did **not** ship:
  one (`plugin.schema.json` `requires.plugins` validation) had **already landed independently on `main`**
  via a parallel review by the time this branch merged `main`, and two (the root-README per-plugin skill
  counts and the `marketplace.json` self-count) are **derivable counts** that were re-rotting in real time as
  parallel plugin PRs merged (`main` moved from 182 to 184 plugins mid-run) — exactly the cross-PR count
  contagion this repo's self-healing gate design avoids, so they are folded into the self-heal follow-up
  below rather than hand-patched here.
- **Two new findings are routed here for your decision** (D6, D7) — each either changes a data-integrity
  guard's matching or is a product-direction call.
- **One confirmed P2 doc fix was deferred** (D8) because landing it correctly forces a `ravenclaude-core`
  version release; the exact remediation is written out so it lands in seconds when watched.
- **The five findings from the 2026-08-04 review (D1–D5) are all still open**, verified unchanged this
  session — status refresh at the bottom.

Run record: `.ravenclaude/runs/repo-review-2026-08-25/` (this checkout's HEAD is commit #1020).

---

## D6 — Correctness (P2): `guard-memory-compaction.sh` never inspects MultiEdit's `edits[]`, so a MultiEdit shrink of MEMORY.md skips the deny

**File:** `plugins/ravenclaude-core/hooks/guard-memory-compaction.sh` (~lines 158–171)

Verified against source this session. The guard's header advertises `Write|Edit|MultiEdit` coverage, but the
MEASURE branch reads the size delta with `_field '.tool_input.old_string'` / `'.tool_input.new_string'` — the
**Edit** payload shape. A **MultiEdit** call carries its changes under `.tool_input.edits[]` (an array of
`{old_string,new_string}`), so for `tool_name=MultiEdit` both fields come back empty, the
`if [ -n "$_old_s" ]` block never runs, `new_bytes` stays empty, and line 171 unconditionally `exit 0`
(allow). A **>15% shrink of MEMORY.md performed via MultiEdit** — the natural tool for a section-by-section
markdown rewrite, which is exactly the compaction shape the guard exists to catch — is never denied or warned.

**Why it is P2, not P1 (the load-bearing mitigation):** the SNAPSHOT (~lines 133–140) runs on **every**
guarded Write/Edit/MultiEdit, before and independent of the MEASURE branch, and is tool-shape-independent. So
the incident this guard was actually built to prevent — silent **unrecoverable** loss — is still averted on
the MultiEdit path: the prior bytes are on disk. The residual gap is (a) the missing deny/warn friction and
(b) that a silent allow never emits the "a snapshot was saved under `.ravenclaude/runs/*/memory-snapshots/`"
pointer, so recoverability is real but undiscoverable until someone knows to look.

**Recommended fix:** in the MEASURE branch, when `tool_name` is `MultiEdit`, reconstruct the size delta from
`.tool_input.edits[]` (sum the `old_string`/`new_string` lengths across the array, or measure the resulting
file) instead of the scalar Edit fields.

**Why it's here, not in the PR:** the fix **broadens what a data-integrity guard denies** — a legitimate
MultiEdit MEMORY.md rewrite would newly be subject to the shrink deny. That is a guard-matching behavior
change and deserves the same must-fail-half fixture discipline (Gate 184) the guard originally shipped with:
add a bidirectional fixture (deny a >15% MultiEdit shrink; allow a normal MultiEdit edit) with the change.
Small effort; a guard-matching change, so reviewed rather than landed autonomously in an unwatched run.

---

## D7 — Correctness / product-direction (P2): the context-usage meter is Grok-session-only, so two documented features are dead on Claude Code (the default host)

**File:** `plugins/ravenclaude-core/scripts/context-usage-meter.py` (session-dir + `measure()`), consumed by
`conserve-tokens.py` and `handoff-nudge.py`

Verified by reading the module this session. `session_dir_from_env()` builds the session path from
`GROK_SESSION_ID` / `GROK_HOME` / `~/.grok`, and `measure()` reads a Grok `updates.jsonl` artifact. There is
**no `~/.claude` transcript reader anywhere in the file.** On Claude Code, `measure()` returns
`status:'unknown'`; `conserve-tokens.py` and `handoff-nudge.py` both gate on `status == 'ok'`, so:

- the CLAUDE.md context-pressure **conserve-tokens** trigger, and
- the **handoff-nudge** "context-hot" Stop-hook nag

both **never engage on the primary/default host.** `handoff-nudge.py`'s "the hook fires on every host" comment
is provably false for the gated behavior — which matters under this repo's Claim-Grounding discipline.

**Why it is P2, not P1:** both features are **opt-in** (they engage only when a consumer authors
`context_handoff` / conserve config in `.ravenclaude/comfort-posture.yaml`), and both **fail safe** (silent
no-op, no crash, no wrong data). conserve-tokens still works via its phrase and posture-switch triggers; only
the automatic context-pressure trigger is dead. Nothing breaks — but two documented features are inert exactly
where most consumers run, behind a false "every host" claim.

**The decision I need from you — which direction?**

- **(a) Honest-scope the docs (the floor, trivial).** Correct the "every host" claim to say the meter-driven
  triggers are Grok-only today, so the docs stop over-promising. Correct regardless of (b).
- **(b) Add a `~/.claude` transcript reader (the substantive fix).** Teach the shared meter module to read
  Claude Code's transcript so both triggers light up on the default host. Higher value, but it touches a
  shared module consumed by two hooks + their gates and needs real design (which transcript, how to size it,
  how to test it without a live session).

**Recommendation:** ship **(a)** now as the floor (kills the false claim), then scope **(b)** as its own change.
Not landed autonomously because (a) alone is a knowledge/claim edit best made with your read on the wording,
and (b) is a product-direction call with a shared-module blast radius.

---

## D8 — Doc bug (P2), CONFIRMED and fix-ready, deferred only for the release cascade: `AGENTS.md` gives bare `bin/rc` commands that fail from the repo root

**File:** `AGENTS.md` (storage-contract section, ~lines 108 and 125)

Verified this session: `AGENTS.md` §"Opening the dashboard" (~line 52) explicitly says to invoke the launcher
by **full path** (`plugins/ravenclaude-core/bin/rc`) because a bare invocation is unreliable — yet the
storage-contract section two sections later hands readers bare `bin/rc artifacts new <task-id>` and
`bin/rc artifacts list`. There is no repo-root `bin/` (`ls bin` → No such file or directory), so a reader
copy-pasting from the repo root hits exactly the failure the same file warned about. This is a canonical,
cross-tool doc (read by Copilot CLI, Codex, and Claude Code by import), and I hit this failure myself at the
start of this run (`bin/rc artifacts new` → not found; fell back to `python3 scripts/rc-artifacts.py`).

**The fix itself is two lines** (bare `bin/rc` → `plugins/ravenclaude-core/bin/rc` in both places).

**Why it's deferred, not in the PR:** the storage-contract section is projected into
`plugins/ravenclaude-core/copilot/AGENTS.md` by `generate-copilot-plugin.py`, which has a freshness gate. I
confirmed the edit makes that projection STALE, so a correct landing is: edit root `AGENTS.md` →
`python3 scripts/generate-copilot-plugin.py` (regenerates the projection cleanly — I verified the only
resulting diff is `copilot/AGENTS.md`) → bump `ravenclaude-core` patch version →
`python3 scripts/sync-plugin-versions.py`. That turns a doc typo into a shipped-plugin **version release**;
shipping the projection change **without** a bump would create exactly the silent shipped-content drift this
repo dislikes, and no gate forces the bump either way. That release cascade is disproportionate blast radius
for an unwatched scheduled run — but it is a clean, mechanical, ~2-minute change when watched. **Recommend
landing it as its own tiny PR with the steps above.**

---

## Status refresh — the 2026-08-04 findings (D1–D5) are all still open

Each re-verified against current source this session; none has been addressed since 2026-08-04 (the only
commits touching the relevant files were #982 — which scoped **git-push** delete detection only — and #961,
the forms plugin). They remain routed to you for the reasons the prior doc gives; carrying them forward:

| ID | File | What | Still open? |
| -- | ---- | ---- | ----------- |
| **D1** | `guard-destructive.sh` (~446) | Security (P1): misses download-then-execute RCE (download to file with `-o`/`-O`/redirect, then run the saved file). No `download-then-execute`/`urlretrieve`/`--output-document` detection present. | **Yes** — unchanged |
| **D2** | `guard-destructive.sh` (~351/396/411) | Bug (P2): `_is_dangerous_rm`/`_find`/`_truncate` false-DENY safe compound commands (dangerous-target check not scoped to the matched command's own segment). Sequence **after** D1 (D1 tightens, D2 loosens). | **Yes** — unchanged |
| **D3** | `thing-decide.py` `_tally` (~601) | Security/correctness (P1): only Heimdall's abstention forces a Thor tie-break; the safety seat **Forseti** abstaining does not. Line 601 still reads `if heimdall_abstained or …`. Protected tribunal substrate (`xc.tribunal-self-disable`, Gate 225/162) — gate on the golden eval. | **Yes** — unchanged |
| **D4** | `thing-decide.py` `_tally` (~616–619) | Correctness (P2): Thor tie-breaker's own confidence is never checked against `threshold`. No such check present. Same protected substrate as D3; pairs with it. | **Yes** — unchanged |
| **D5** | 43× `flag-*antipatterns.sh` | Product direction (P2): 43 byte-identical stubs whose comment/`note()` claim PII/PHI/baseline/sourcing checks but only grep `TODO`/`FIXME`/`lorem ipsum`. Re-counted this session: **43 stubs**, unchanged. Recommendation stands: ship honest-minimal note text for all 43 (floor), then real detectors for the ~6 high-sensitivity domains. | **Yes** — unchanged |

None of D1–D5 was auto-implemented, for the same reasons as before: D1/D2 change a **default-active security
guard's matching**; D3/D4 mutate **protected tribunal substrate** that `xc.tribunal-self-disable` hard-denies
and that must be re-run against the golden eval (Gate 33); D5 is a **product-direction call** with a 43-plugin
/ 9 MB `index.html` regen blast radius. All are exactly the "review, don't land autonomously in an unwatched
run" class.

---

## Implemented in the accompanying PR (no design input required — each verified against source + validated locally)

Grouped by final (tie-broken) priority. None touches shipped plugin content, so no version bump is required;
all three live under `scripts/` (with the review write-up under `docs/decisions/`).

### P2

| # | Fix | File | Validation |
| - | --- | ---- | ---------- |
| F1 | **Posture mislabel.** `derive_posture_label` returned `'unknown'` when a posture file is present but omits `global_default`, while the engine (`apply-comfort-posture.py`) treats an absent key as `'ask'` → `'balanced'`. The seeded balanced template and real posture files omit the key, so `/wrap` run-context stamped `posture_label: unknown` for the common case. Aligned the deriver with the engine default; **added the missing self-test case** (the old fixture wrote the key, masking the bug). | `scripts/capture-run-context.py` | `--check` green incl. new keyless-file case |
| F2 | **Ledger branch collision.** `branch_slug()` maps `/`→`-` but leaves an existing `-` untouched, so `feat/x` and `feat-x` slug to one ledger; `load_ledger` never verified the stored branch, so the second branch silently read/appended the first's closed-finding memory (false reopened verdicts). Added a loud branch-mismatch guard (back-compatible with pre-`branch` ledgers). | `scripts/review-ledger.py` | `--self-test` 40/40; collision now raises; same-branch load intact |

### P3

| # | Fix | File | Validation |
| - | --- | ---- | ---------- |
| F3 | **Meta-gate precision.** `DEFAULT_ARM` matched any case-arm starting with `*` (e.g. `*_denied)`), so a verdict `case` lacking a true bare `*)` catch-all could go undetected — the fail-open this gate exists to catch. Tightened the regex to require a real catch-all (`*` followed by `)` or `|`) and added an M4 self-test fixture. Latent today (no live trigger). | `scripts/check-verdict-default-nonpermissive.py` | `--self-test` teeth verified (M4 now caught); real-tree run still green |

### Surfaced but not shipped in this PR

| # | Fix | Why not shipped |
| - | --- | --------------- |
| F4 | **Schema coverage gap** — validate the universally-used `requires.plugins` array (was unvalidated via `additionalProperties`). | **Already landed on `main` independently** via a parallel review (`schemas/plugin.schema.json` now carries a `requires.plugins` items pattern). This branch's identical fix was dropped when merging `main` in — the merge took `main`'s version. No action needed. |
| F5 | **README per-plugin skill counts** (finance 9→23, power-platform 21→23, web-design 11→13, ravenclaude-core 52→54). | **Derivable count, re-rotting.** `main` restructured the README during this run and deprecated the hand-maintained bullet list ("prefer the portal over any hand-maintained essay list"). Rather than fight the restructure with a P3 cosmetic edit, folded into the self-heal follow-up below. |
| F6 | **Marketplace self-count** ("plus N domain plugins"). | **Derivable count, re-rotting.** `main` moved from 182 → 184 plugins mid-run, so the value churned (was 181, now 183) before this PR could land. Left to the self-heal follow-up rather than shipping a value already stale on arrival. |

> **Durable follow-up for F5/F6 (P3):** these root-README/marketplace self-counts are derivable but sit
> **outside** the self-healing `check-marketplace-claims.py --fix` scope, so they rot on the next
> plugin/skill addition (as this run demonstrated live). The durable fix is to bring them under that gate's
> self-heal coverage (the same pattern already used for the `plugin.json`/`marketplace.json` entries), so a
> post-merge job rewrites them rather than a human/agent hand-patching a moving target on every PR. Filed here
> as its own gate-infra change rather than expanded into this PR.
