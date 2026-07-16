# G6 — Synthesis · The authoritative plan · `dashboard-redesign`

> ⚠️ **PATH DEVIATION — read §BLOCKER first.** This artifact is **not** at the mandated
> `.ravenclaude/runs/forge/dashboard-redesign/plan.md`. **`enforce-layout.sh` DENIED that write**, and the
> deny is legitimate. I did **not** edit `.repo-layout.json` to permit my own write, and did **not** use a
> shell redirect to bypass the hook — either would be the exact pattern this run exists to judge.
> **`plan.md` on disk is UNCHANGED (the pass-2 version, 93,991 B). This file is the pass-3 revision.**
> Recovery is one `mv` once a human restores the glob (§BLOCKER).

**Date:** 2026-07-15 · **Gate:** G6 (synthesis pass 3) · **Depth:** deep · **Owner:** Matt Corbett
**Repo:** RavenClaude @ **`fix/ravenclaude-core-save-header-guard`** (⚠️ branch changed mid-run — §BLOCKER)
**Inputs merged:** `scope.md` · `claims-table.md` · `plan-A.md` · `plan-B.md` · `gap-delta.md` ·
`critic-brief.md` · `tiebreaks-learn.md` · `tiebreaks-security.md` · `red-team.md` · `red-team-2.md` ·
**the Team Lead's §0.2 ruling + three resolutions (pass 3)**

---

## ✅ BLOCKER RESOLVED — the F6 edit was committed all along, on a branch this section never checked

> **Status: CLEARED 2026-07-16. The blocker below was real as a *deny*, but its *root cause was wrong*, and
> its remedy is now merged to `main` (PR #684, `610f35fa`). Do not act on the stricken text — it is retained
> only because the reasoning error is instructive.**
>
> **What was actually true:** the edit **was committed**, as `283f18f8` on branch **`forge/dashboard-redesign`**.
> The table below checked `fix/ravenclaude-core-stale-macos-claims` and `fix/ravenclaude-core-save-header-guard`
> — neither of which carried it — and concluded *"never committed."* It never checked the third branch, which
> was the one holding it. Nothing evaporated; the session had simply moved to a branch cut from `main`.
>
> **Verified on `main` after #684 merged** — driven against the real hook, `CLAUDE_PROJECT_DIR` = repo root:
>
> | Path | Verdict |
> |---|---|
> | `.ravenclaude/runs/forge/<slug>/plan.md` | **ALLOW(0)** |
> | `.ravenclaude/runs/thing/decisions/…` | **DENY(2)** |
> | `.ravenclaude/runs/*/hook-events.jsonl` | **DENY(2)** |
> | traversal (`runs/../../etc/passwd`) | **DENY(2)** |
>
> `main:.repo-layout.json` carries `allowed_globs:35 → ".ravenclaude/runs/**"` and
> `forbidden_globs:80 → [".ravenclaude/runs/thing/**", ".ravenclaude/runs/*/hook-events.jsonl"]`.
> **No human action is outstanding. `landing=pr` was re-derived by G7 independently and still holds — on four
> signals, now including `version-bump-target`.**
>
> **What survives, and is the reason this stays on the page:** consequence 3 was right, and is *reinforced*
> rather than weakened. §11.1's class is real — `enforce-layout.sh` polices a gitignored path CI never sees.
> The agent that raised this was **correct to stop and correct to refuse to widen the config to unblock its own
> write**; it was wrong only about *why*. A deny is evidence about one route, not proof of a missing capability
> — and "absent from the two branches I checked" is not "never committed."

**The deny, verbatim** (driven read-only against the real hook, `CLAUDE_PROJECT_DIR` = repo root) — **real at the
time, now cleared**:

```
[enforce-layout] BLOCKED: Layout policy:
'.ravenclaude/runs/forge/dashboard-redesign/plan.tmp' does not match any allowed_globs
in .repo-layout.json. Add the glob to .repo-layout.json allowed_globs first, with
rationale in the PR description.
EXIT=2
```

**Root cause — verified, and it falsifies my own §6:**

| Check | Result |
|---|---|
| `allowed_globs` contains `.ravenclaude/runs/**` | **False** |
| `forbidden_globs` | **`[]` — empty** |
| `git status --porcelain` | **clean** — the working-tree edit is gone |
| `git stash list` | **0 stashes** |
| `git show fix/ravenclaude-core-stale-macos-claims:.repo-layout.json` | **also False** — *it was never committed on the old branch either* |
| Current branch | **`fix/ravenclaude-core-save-header-guard`** (was `fix/ravenclaude-core-stale-macos-claims`) |

**The edit was purely a working-tree change and was never committed. The branch moved to land PR #685, and
the edit evaporated. It exists nowhere: not in the tree, not on either branch, not in a stash.**

**Three consequences, all binding:**

1. **§6's "F6 is fixed and verified … DONE this session" is FALSE as of now.** The `forbidden_globs`
   protecting the tribunal substrate and the hook-event audit log are **gone too** — so the mitigation *and*
   its scoping both vanished together. Pass-2's §6 must not be trusted; it is corrected below.
2. **🔴 The `landing=pr` forcing function is GONE.** §6/§13.11 asserted *"landing=pr is FORCED by the
   `.repo-layout.json` `allowed_globs` edit (an engineering pre-commitment on a boundary file)."* **There is
   no such edit in the tree.** G7 must re-derive its routing: `landing=pr` may still be right on other
   grounds (this plan commits to generator + hook + gate + manifest changes), but **the specific input that
   forced it no longer exists.** Do not carry the old justification.
3. **This is exactly the class §11.1 named.** `enforce-layout.sh` has no gitignore exemption, so it polices a
   gitignored path CI never sees — and the *only* thing that made FORGE's mandated run-dir writes work was an
   **uncommitted** edit. **An uncommitted mitigation is not a mitigation.** The instance regressed the moment
   a branch moved.

**~~Required of a human~~ — DONE. Merged to `main` in PR #684 (`610f35fa`); verified live on `main` (see the
status block at the top of this section). No action outstanding.** The original text follows:
```json
"allowed_globs":   [ …, ".ravenclaude/runs/**" ],
"forbidden_globs": [ ".ravenclaude/runs/thing/**", ".ravenclaude/runs/*/hook-events.jsonl" ]
```
Both patterns were previously driven live against the real hook (FORGE run dir → ALLOW(0); `runs/thing/**`,
`runs/*/hook-events.jsonl`, traversal → DENY(2)). **The forbid-list is not optional** — without it the allow
exposes the runaway brake's counter (`runaway-brake.sh:48`, `:161-163`; a one-line `Write` of `0 - 0` resets
it) and makes deny history forgeable. **Then:** `mv` this file to
`.ravenclaude/runs/forge/dashboard-redesign/plan.md`.

*I did **not** write to the run dir by shell redirect, which `tiebreaks-security.md` §5.2 showed would bypass
the tool-shaped hook entirely — available, and forbidden. This file sits in the session scratchpad, which
`enforce-layout.sh:90-91` explicitly declines to police (*"File is outside the project root — not our policy
to enforce"*) — the hook's documented scope, not a bypass, and the same disposition `tiebreaks-security.md`
§7.1 recorded for the identical situation.*

---

## 0. What this build actually is — **and what it buys**

### 0.1 🔴 The DOM pillar — RE-MEASURED under the Team Lead's ruling

**The §0.2 ruling lifts Learn's exemption, and it transforms the build.** Every pass-2 figure assumed that
exemption and is **retired**. Re-measured at G6 pass 3 (`html.parser`, script/style excluded, islanded panels
costed at 2 elements each — `<section>` + `<script type="application/json">`):

| | `dashboard.html` | `index.html` |
|---|---:|---:|
| **Today** | 57,330 = **41.0×** the threshold | 50,945 = **36.4×** |
| ~~Pass-2 (Learn exempt)~~ | ~~≈24,920 = 17.8×~~ **RETIRED** | ~~≈25,626 = 18.3×~~ **RETIRED** |
| **NOW (Learn converted; `settings` exempt)** | **≈5,220 = ~3.7×** | **≈5,926 = ~4.2×** |
| **Reduction** | **~91%** (was ~57%) | **~88%** (was ~50%) |
| **Of the remainder: `settings` alone** | **86.5%** | 76.2% |

**The ruling is worth ~19,700 nodes on each surface and takes the build from ~57% to ~91%.** It is the
difference between a plan that leaves the defect largely intact and one that nearly closes it.

**Still honest: ~3.7× does not clear Lighthouse's 1,400-node error threshold.** But it is now within one
decision of doing so — see §0.2b. **Phase 0 emits the authoritative figures (item 4a); no number here is
adopted as a budget.**

### 0.2 ✅ ANSWERED BY THE TEAM LEAD — a RECORD, not a gate

> *"go with the recommendation. I'm fine with breaking live functionality temporarily if the dashboard gets
> updated and fixed."*

**Ruling: fund the Learn conversion. Learn's exemption is LIFTED. This supersedes Fork 1's tiebreak.**

**Why this reading and not another** (the clarifier disambiguates it): only the Learn-conversion option
*breaks live functionality at all*. The other two do not — one exempts the panels precisely **to avoid**
breaking them; the other is a waiver that changes no code. *"I'm fine with breaking live functionality
temporarily if the dashboard gets updated and fixed"* coheres with exactly one option.

**Fork 1 exempted Learn on risk** — *"open-ended engineering risk in a harness that has already regressed
once."* **The human who owns that risk has now accepted it.** §0.2 existed to route this decision to him;
it did. **Not re-litigated — implemented.**

**Consequences:**
- **§11.2 is promoted from a follow-up to IN SCOPE.** It is the point of the build. → **Phase 2L.**
- **Phase 2 is UNBLOCKED.** §0.2 is no longer a pre-build gate; it is a record.
- **Phase 0's flip check (item 6) is now LOAD-BEARING, not informational** — it sizes the *funded* work.
  **Sequence it first.**
- **The ordering constraint survives:** the Learn/Gate-93 stepper contract must still be decided **before**
  the DOM phase. **It is decided — "convert."** Its *shape* (Gate 93-v2's assertions) is specified in
  Phase 2L and settled before Phase 2L builds.

### 0.2b ⚠️ The NEXT §0.2-shaped decision — `settings`. **NOT authorized; do not assume it.**

**`settings` is explicitly NOT covered by the §0.2 authorization. The risk shape is different, and the
difference is the whole point:**

| | Learn | `settings` |
|---|---|---|
| How it breaks | **Visibly** — the stepper renders wrong; you see it, you fix it | **Silently** — the posture editor dies with **every gate green** |
| Detection | Immediate, by eye | **None.** Gate 35 is DOM-free by its own header (`check-dashboard-roundtrip.mjs:11`) → structurally blind |
| Consequence | Temporary breakage, then fixed | **The next Save writes corrupted posture wholesale** (`serve-dashboards.py:1520-1560`, no merge) |

*"Temporarily broken, then fixed"* **describes Learn exactly and describes `settings` not at all.
Data loss you don't find out about is not temporary breakage.** **Keep the `settings` exemption.**

**What would make it a normal, decidable trade — and it is a real one:**
- **Prerequisite: the post-`activate()` DOM check must exist first** (headless/JSDOM). `tiebreaks-learn.md`
  §D5 records that **no plan has one**. That gate is what makes `settings`' breakage *visible* — it converts
  the silent failure into a Learn-shaped one. **Build the gate, then the decision is normal.**
- **The price, so it can be decided rather than deferred by inertia:** `settings` is **86.5%** of the new
  dashboard residue. **Converting it lands the build at ~707 nodes (0.5×) on `dashboard.html` and ~1,413
  (1.0×) on `index.html` — i.e. it CLEARS Lighthouse's 1,400-node error threshold outright.**
  **That is the decision: one panel stands between this build and the threshold.**
- **Route it as the next §0.2**, priced against the residue, once the rendered-DOM meter exists (§11.2b).

### 0.3 The pillars

| Pillar | Honest verdict | Weight |
|---|---|---|
| **Visual / brand** | **A reskin.** A complete dark theme already ships; the commerce gold is Δ6/255. Flip the default, swap 6/255, self-host 2 woff2, apply the type scale. | Small |
| **Payload** | **Not a crisis.** ~1.05 MB gzip (dashboard) / 1.73 MB (portal). **No wire budget in v1** — §11.4. | None (v1) |
| **DOM** | **The genuine defect — and the ruling now gets ~91% of it** (§0.1), landing at ~3.7×. One further decision (§0.2b) clears the threshold. | **Large — now the point of the build** |
| **IA / search** | Real gap only where proven — `trees` and `commands`. Learn already has search + grouping. | Medium |
| **Guardrail control** | Ruled out as posed (Fork 2). **The aggregated view already ships** (`panel-pipeline`, P2) → a **delta**. | Small |
| **Live bugs found en route** | **Three open** (was four): `emitYaml`'s silent key drop (F4); a **mislabelled shipped control** (P5); **a hook missing from the pipeline map** (P2). **`/__save` is FIXED — §1.5.** | Medium |

**The honest scope: reskin + a ~91% DOM fix (incl. the Learn conversion) + a targeted IA/search fix + three
live-bug remediations + a pipeline-panel delta.**

---

## 1. Binding rulings carried (not re-litigated)

1. **Astro rejected — fix the generator in place.** Reasoning corrected: Astro's node-count benefit is **not
   falsified** — it is **not unique to Astro**. The rejection rests on the **cost** comparison: no node
   toolchain in a python-served plugin, no CI bump off `node-version: "20"`, no custom Content Layer loader
   for 924 non-file-backed markdown sections, 1 gate touched vs 12, no rewrite of 11,614 working lines.
2. **The "12 gates bind JS only" premise is FALSE.** Gate 93 binds generated **markup**; Gate 51 binds markup
   **and** a literal, whitespace-sensitive CSS rule. G4a executed both plans' mechanism: **both `exit=1`.**
3. **Gold-as-body-text is AAA (8.24:1)** in dark mode, not 3.6:1 (real light-mode value: **3.12:1**). An
   **aesthetic** call, not an a11y floor. B's ship-gate **DROPPED** — its teal remedy measures **6.12:1**.
4. **No master off-switch.** A switch spanning all 20 hooks IS the catastrophic point by construction. **The
   safety floor is never switchable:** `guard-destructive.sh` **entire**, `thing-orchestrator.sh`'s
   self-disable (`:159`) + hard-rule (`:210`), `enforce-layout.sh`'s traversal scrub, the `security_deny`
   family, the container/worktree boundary. *P2 re-targets Phase 6's scope; it does not reopen this.*
5. **✅ The `/__save` header guard is FIXED AND SHIPPED — PR #685, `18109b18` (verified in the tree this
   session).** `_state_change_origin_ok()` (`plugins/ravenclaude-core/scripts/serve-dashboards.py:1381`,
   called at `:1561`) now requires a **present, allow-listed `Origin`** on `do_POST`. Proven by driving a
   real server: header-absent POST **200 → 403**; browser-shaped POST **200 → 200** (the dashboard still
   saves); hostile Origin 403; zero ACAO headers (invariant held). Both server copies; Gate 32 parity green.
   **Dropped from Phase 5.**
   **🔴 Record honestly what the fix does NOT do:** it closes the **browser / DNS-rebinding** threat. **It
   does not stop a local scripted process**, which can send any header it likes — and which can simply write
   `.ravenclaude/comfort-posture.yaml` directly, needing no HTTP at all. **Fork 2 §5.3's "unreachable design"
   ruling stands and is now confirmed in shipped code:** a control both reachable by the human and
   unreachable by the agent does not exist in this architecture. **"Dashboard-only" remains ergonomic, not a
   security boundary. Do not write it down as one.**

---

## 2. Reconciliations

### 2.1 F1 — the counter, and the precise scope of what is retired

`tiebreaks-learn.md` instructed a regex tag-token count. **JSON escapes `"` but not `<`**, so the
`<script type="application/json">` wrapper **adds** a tag and every `<` in the payload survives → **a regex
Gate 132 reports ~zero reduction for the adopted mechanism.** Baseline is **57,330**, not 57,419. Plan A's
must-fail half is broken under the correct parser (57,330 ≤ 57,418 **passes**) → derive it as **`count − 1`**.

**Pass-2 narrowing (kept):** my earlier "all regex figures are incommensurable" was **over-stated**.
Per-panel slices are **CONFIRMED, not retired** — `learn` 19,702 · `settings` 4,515 · `trees` 20,612 ·
`commands` 6,308 (index `trees` 13,521) reproduce **to the digit** under both counters. The divergence is
**created by islanding**; it does not exist pre-islanding. **Retired:** the whole-document total (57,419 →
**57,330**), the shell figures (359/1,615 → G6 measures **271**/**977**), and every composed figure (429,
20,131, ≤20,500, ≤21,800). **Phase 0 must not treat that confirmation as a contradiction.**

**Rulings:** specify **`html.parser` inside Gate 132's own header**, with the reason (G4a measured 89
script/style tokens — true *today*; post-islanding the divergence goes **89 → ~46,000**; **the plan
invalidates its own justification**). Phase 0 re-derives every composed figure.

### 2.2 F3 / §0.2b — **Learn's exemption LIFTED; `settings`' exemption RETAINED**

**Learn — converted (§0.2).** Fork 1's risk ruling is superseded by the risk owner. Phase 2L owns it.

**`settings` — exempt, and the reasoning is the risk *shape*, not the node count.** Verified this session:
- All **144** posture radios (`input[type="radio"][data-category][data-layer]`) live in `panel-settings`.
- `dashboard.html:13261` — **load-time, module-scope, document-wide** read, with the generator's own comment:
  `/* Read actual checked radios from DOM to pick up any rendered defaults */`.
- `:13906` / `:13941` — load-time `addEventListener` binds over the same document-wide selectors.

**Effect chain, all silent:** empty NodeList → `state.categories` never picks up rendered defaults → **the
in-memory posture silently diverges from what was rendered**; zero listeners bind; `forEach` over an empty
NodeList **throws nothing**; the next Save persists the corruption wholesale. **Every gate stays green** —
Gate 35 DOM-free (`:11`, verified); the 12 bind JS text; Gate 13 regen matches; Gate 132 goes *greener*.

**The exemption test, mechanical (Phase 0):** for each candidate panel, grep for module-scope
`document.querySelectorAll` / `getElementById` whose targets live in that panel. Fails ⇒ exempt.
**Sweep all 184 panels** — *the assertion that got `settings` wrong covered all 180 at once, and there are
**184** (both surfaces, verified).* **Learn fails this test too — it is converted anyway, under §0.2, with
the conversion work explicitly funded (Phase 2L). A panel that fails the test is either exempt or funded;
it is never silently islanded.**

### 2.3 F5 — four knobs, not six

Verified: `claim-grounding-lint.sh:52-62` and `delegation-nudge.sh:56-65` are byte-for-byte the same bounded
walk-up for the mere **presence** of `comfort-posture.yaml`. **Neither reads a key**
(`grep -c 'command_review\|thing' claim-grounding-lint.sh` → **0**).

**The 4 real knobs:** `guard-web-access` (`.ravenclaude/web-access.yaml`), `runaway-brake` (`runaway:`),
`dod-gate` (`definition_of_done`), `route-decision-review` (`decision_review`). Render `claim-grounding-lint`
+ `delegation-nudge` as **"no knob — fires whenever a comfort-posture exists."** **No new top-level keys** —
that reopens the V3 gap (a new key is covered by **neither** `concerns-catalog.md:187` **nor** `:192`).
4 existing keys **preserves the load-bearing property: there is no single key to write.**

### 2.4 F2 — per-surface budgets

Gate 132 binds both surfaces; the tiebreak measured one. `index.html`'s `trees` is **13,521**, not 20,612
(`include_trees=False`, `:248`) → **the per-panel savings differ per surface; a single ratchet table is wrong
on both ends.** **Two budgets, two ratchet tables, both re-derived under §2.1's parser.**

### 2.5 F4 — `emitYaml` silently drops `stream_classify` / `stream_threshold` on every Save

Verified: `dashboard.html` contains **0** occurrences of either key. Both are real posture keys, parsed at
**`plugins/ravenclaude-core/scripts/stream-session-start.py:55`** (`_MODE_RE`) and **`:57`** *(path
correction: G5 cited `hooks/`; the file is under `scripts/` — re-verified this session)*. `/__save` writes
wholesale; `emitYaml()` rebuilds from `state`. **Gate 35's state model has no stream keys** → the gate that
exists to catch this is green.

**The v0.61.0 data-loss bug recurring** — that milestone fixed the identical defect for
`runaway`/`decision_review`/`definition_of_done` and added Gate 35. The stream keys shipped later (v0.164.0)
and were added to neither. **The gate did not generalize; it enumerates.** **Still open. Phase 5 owns it.**

### 2.6 P1 — the residue and the exempted floor

Fork 2's floor (*"shell + active tab"*) predates the exemptions and is falsified by them. **Phase 0 emits the
*exempted* floor:** `floor = shell + active tab + Σ(exempt panels)` — now `settings` only. §8's row amended.
The residue is stated in §0.1 and gated by §12.2a's **derived target**.

### 2.7 P2 — the aggregated guardrail view already ships. Phase 6 is a delta

**The plan diagnoses this exact mode (R7) and committed it one phase later.** Verified this session:

| Phase 6 proposed | Already ships |
|---|---|
| *"A dedicated 'Guardrail Pipeline' panel"* | `generate-dashboards.py:11406` → `<section id="panel-pipeline" … aria-label="**Guardrail pipeline**">`; tab at `:11379`. **Both surfaces, 388 elements each.** |
| *"A generated, always-visible disclosure line"* | `:472-476` — *"A visual map of **EVERY guardrail** … a **live ON/OFF badge**"*. 15 stages / 4 lanes. |
| *"Four live knobs"* | **Seven** already have inline editors (`syncPipelineTab()` `:8886`, dispatched `:8594`). **3 of Phase 6's 4** among them. |
| *"Scope text ON the control (R10)"* | Already shipped for the floor: `guard-destructive` → *"Built-in safety floor — always on, can't be turned off."* |

**Blast if built as written:** **two competing guardrail views**, each claiming to enumerate active hooks,
drift-gated on **only the new one**, the new one **strictly narrower** (4 knobs vs 7). **By R10's own
standard — *"a control that overclaims is worse than no control"* — that defect, doubled.**

**The delta — four measured gaps:** `guard-web-access` absent from the lanes (only in `panel-web-access`'s
copy, `:11320`/`:11327`) · **`delegation-nudge` absent from the generator entirely** (0 grep hits — **the
shipped map is already missing a hook; live drift today**) · **no pipeline render gate exists** (the 10
`check-*render*.mjs` are bifrost, concern-stats, heimdall, mimir, nidhoggr, norns, sleipnir, stepper,
streams, vidarr) · **the lanes are hand-maintained** — the **only** `hooks.json` mention in the generator is
**the `:473` comment claiming they are grounded there. They are not.**

**Open product call — Matt's:** extend `panel-pipeline`, or replace it (388 elements, hand-maintained)?
**Either way, "build a new panel" as written is wrong.**

### 2.8 Corrections to counts and claims

- **184 panels, not 180** (both surfaces, verified). Phase 0's sweep is enumerative — **enumerate from the
  artifact, never from a literal**, or four panels get no verdict and island unswept.
- **§3's "Phase 5 ∥ Phases 1-4 — disjoint from the generator's render path" is FALSE** (P4). Verified:
  `emitYaml` is emitted **by** the generator (`:7226`), as is `applyGuardrailConfig` (`:7168`), into the same
  `dashboard.html` the render phases regenerate; Gate 35 extracts it back out. **The *generator source*
  regions are disjoint; the *generated artifact* is shared — and that is what both gates read.**

### 2.9 ✅ `.ravenclaude/web-access.yaml` — RESOLVED. The premise was FALSE; closed.

**Open since G1, thrice-flagged by me as "either a stale brief or a finding." It is neither — verified at
source this session:**

- **It is optional by design, and its absence is the documented fail-safe, not a defect.**
  `guard-web-access.sh:14` (verified verbatim): *"Fail-safe: absent config / missing jq / unparseable file ->
  exit 0 (ask as normal); the hook never breaks web access."* Unknown domain → the agent's normal per-domain
  prompt.
- **A template ships** at `plugins/ravenclaude-core/templates/web-access.yaml` (verified, 1,015 B); the
  dashboard editor writes the live copy on demand (`serve-dashboards.py:65` → `WEB_ACCESS_TARGET`); the
  per-repo copy deliberately stays local.

⇒ **The G1 brief's "honor it" mandate was satisfied all along. Nothing to add, nothing to remove. Removed
from the open/unreconciled list.** *(My repeated escalation was itself the error — I treated an absence as a
gap without reading the hook's own fail-safe comment. The same read-only-part-of-the-system class this run
has now committed five times.)*

**The one real requirement it leaves:** **Phase 6's view must render the "not configured yet" state** rather
than assuming the file exists. Folded into Phase 6's acceptance.

---

## 3. Dependency DAG + critical path

```
  [SETTLED — the ordering constraint, satisfied before any DOM work]
   Learn / Gate-93 stepper contract ──► §0.2 RULING: **CONVERT** (Fork 1 superseded) ──┐
                                                                                       │
Phase 4a — ROUTES (day 0, no pre-build gate) ──────────┐                               │
  · enumerate every committed #/… → fixture            │                               │
  · extend Gate 51 by destination                      │ (Phase 2's acceptance)        │
                                                       │                               │
Phase 0 ── instrument, re-derive, sweep ──┬────────────┤                               │
  · [ITEM 6 FIRST] flip check — sizes 2L  │            ▼                               │
  · Gate 132 (html.parser, per-surface)   ├── Phase 2 (islands: trees, commands, ──┬───┤
  · emit the EXEMPTED floor + residue     │            179 swept small panels)     │   │
  · exemption sweep (all 184)             │                    │                   │   │
  · R8 gate sweep · design tokens         ├── Phase 1 (brand)  ▼                   │   │
                                          │            Phase 2L (CONVERT LEARN)    │   │
                                          │             · Gate 93-v2               │   │
                                          │             · re-point 3 subsystems    │   │
                                          │                    │                   │   │
                                          │                    ▼                   │   │
                                          │              [Phase 3] virtualization  │   │
                                          │              (conditional)             │   │
                                          │                    │                   │   │
                                          │                    └──► Phase 4b (IA + search) ──┐
                                          │                                                  │
                                          └── Phase 5 (posture-write integrity: F4 + P3)     │
                                                     │                                       │
                                                     ▼                                       │
                                               Phase 6 (pipeline delta) ─────────────────────┤
                                                                                             ▼
                                                                                     Phase 7 (ship)
```

**Ordering constraint honored:** the stepper contract was decided **before** any DOM phase — the §0.2 ruling
*is* that decision ("convert"). Its *shape* is specified in Phase 2L and settled before 2L builds.

**Critical path:** `Phase 0 → 2 → 2L → [3] → 4b → 7`, with `4a` day-0 feeding Phase 2. **Phase 2L is now the
highest-value phase in the plan** (~19,700 nodes) and the riskiest — it is sequenced after Phase 2 because 2
establishes the island mechanism 2L applies to a harder target.

**Parallel:** Phase 1 ∥ Phase 2 (disjoint generator-source regions; conflict only in `_page_kwargs`).
Phase 5 ∥ Phases 1-4 **on the generator source only** — ⚠️ **not on the artifact** (§2.8/P4): three phases
each end by regenerating the same 7.8 MB file. Fine under §7's regen precedence, but it is not disjointness.

---

## 4. Alternatives + trade-offs

### 4.1 Stack
| Option | Trade-off |
|---|---|
| **Fix the Python generator in place** | **ADOPT.** Zero node, zero CI bump, zero new dependency, 1 gate touched; brand work ~97.6% present. |
| Astro `is:inline` | Reject — keeps the 12 gates and delivers nothing; Astro touches none of the JS. |
| Astro bundled + rewrite 12 gates | Reject — a real component model, paid for with the repo's deepest harness, for a wire win that is not urgent. |
| **Astro hybrid** | Reject — the steelman neither panel considered; fails *worse*: the custom loader is unavoidable, `scope_css`/`iife_wrap` don't retire, **and Astro normalizes markup → breaks Gates 93 and 51 by construction. Keeps 10 of 12.** |
| Style Dictionary | Reject — the bound design system is already the token source of truth. |

### 4.2 DOM-fix mechanism
| Option | Trade-off |
|---|---|
| **Inline JSON islands, render-on-activate** | **ADOPT.** Script contents are never parsed into the DOM → zero new requests, zero build step, zero static/served divergence, no cache-busting, no new gate surface. **With Learn converted the mechanism now reaches ~91%** (§0.1). |
| Sidecar JSON files | Reject as the content mechanism (adds cache-busting, a Gate 13 extension, a new allow-listed dir, a fetch beat, a JS-off hole). **Its Gate-13-extension discipline and its data-side search matcher are adopted anyway.** |
| Server-side pagination via `/__read` | Reject outright — breaks on static Pages, one of the two required surfaces. |
| True multi-page SSG | Reject for v1 — high risk to "every `#/…` resolves" for a crawlability payoff this private tool does not need. |

*Correction carried:* plan-A justified islands partly via *"NO RUNTIME LOAD"* read as a general
no-runtime-fetch rule. G1 5a narrowed it: the claim is scoped to the token CSS; the generalization is
**false** (the file's own Google Fonts `<link>` proves it). **Right mechanism, one wrong reason.**

### 4.3 The guardrail control
| Option | Trade-off |
|---|---|
| **A delta on the shipped `panel-pipeline`** | **ADOPT (P2).** Smaller, real, better-aimed; fixes drift that exists **today**. |
| A new aggregated panel | **Reject — a duplicate.** Two competing views; drift-gated on only the new one; strictly narrower. |
| **Replace `panel-pipeline`** | **Open — Matt's call.** Must own the removal, the route, the fixture. |
| A new master key over 20 hooks | Reject (binding, Fork 2). |
| Retrofit a uniform gate into 20 hooks | Reject — six hooks can't be turned off at all; a **new cross-cutting control plane whose failure mode is total**. |

### 4.4 The DOM meter
| Option | Trade-off |
|---|---|
| **Static `html.parser`: per-surface load budget + per-panel *payload* budget (JSON-decode the island)** | **ADOPT.** Deterministic, browser-free, CI-safe, ratcheted with a `count−1` must-fail half — **and it closes D5's gap for islanded panels**, because the island payload *is* the markup `activate()` renders. |
| **Headless / JSDOM rendered-DOM meter** | **Defer — but it is now the gate that unlocks §0.2b.** The only meter that sees *arbitrary* JS-rendered DOM. **→ §11.2b.** |
| Regex tag-token counter | **Reject — this is F1.** |

*Stated assumption:* the meter assumes `activate()` renders the payload verbatim. If Phase 3 virtualizes, the
rendered subset is **smaller** → the budget stays sound as a ceiling. **Write this into Gate 132's header.**

---

## 5. Risk matrix

| # | Risk | P | I | Score | Disposition |
|---|---|:-:|:-:|:-:|---|
| **🔴 BLOCKER** | **The F6 `.repo-layout.json` edit is gone (uncommitted, lost on branch change) → the mandated write is DENIED; §6's "DONE" is false; the `landing=pr` forcing function is gone** | **5** | **4** | **20** | **OPEN — needs a human (§BLOCKER).** An uncommitted mitigation is not a mitigation. |
| **F3/§0.2b** | Islanding `settings` kills the posture editor silently, all gates green | 5 | 5 | 25 | **CLOSED BY SCOPE — `settings` exempt (§2.2).** Now priced (86.5% of residue) and routed as the next §0.2 (§0.2b), gated on the rendered-DOM meter. |
| **P1** | The plan passes every gate while achieving little | 5 | 4 | 20 | **LARGELY RESOLVED BY THE §0.2 RULING** — the build now takes 41.0× → **~3.7×** (~91%). §0.1 states it; §12.2a gates it with a **derived target**. |
| **R1/2L** | Converting Learn breaks Gate 93 + steppers + node_links + `#learn-search` | **5** | **3** | **15** | **ACCEPTED BY THE RISK OWNER (§0.2) and FUNDED (Phase 2L).** I↓ 4→3: the human authorized temporary breakage *conditional on it being fixed*. **Phase 2L's acceptance is that condition.** |
| **F1** | Gate 132's regex counter is blind to the mechanism | 5 | 4 | 20 | **CLOSED BY DESIGN.** Scope narrowed (§2.1). |
| **P2** | Phase 6 rebuilds `panel-pipeline` → two competing guardrail views | 5 | 4 | 20 | **CLOSED BY RE-TARGET (§2.7).** |
| **R8** | Other render gates carry undiscovered markup/CSS bindings | 3 | 4 | 12 | **OPEN — Phase 0 sweep.** 2 of 5 checked bind markup/CSS. **Now higher-stakes: Phase 2L touches Gate 93 deliberately.** |
| **F4** | `emitYaml` drops the stream keys on every Save | 4 | 3 | 12 | **OPEN — Phase 5.** Live today. Phase 6 raises its fire rate. |
| **P3** | Phase 6's acceptance unsatisfiable for 1 of 4 knobs | 4 | 3 | 12 | **CLOSED BY SCOPE — Phase 5 covers BOTH serializers.** |
| **F2** | Single-surface budget vs a two-surface gate | 4 | 3 | 12 | **CLOSED BY DESIGN (§2.4).** |
| **P4** | R14 vs the per-commit ratchet are mutually exclusive | 4 | 3 | 12 | **CLOSED BY PRECEDENCE (§7 preamble).** |
| **P5** | A shipped guardrail control is already mislabelled | 4 | 3 | 12 | **CLOSED BY RE-TARGET — Phase 6 item 1.** |
| **R9** | The visual redesign breaks Gate 51's CSS rule | 3 | 3 | 9 | **OPEN — Phase 1.** CONFIRMED by execution; acceptance rewritten. |
| **~~R2~~** | ~~`/__save` reachable by a local process~~ | — | — | — | **✅ CLOSED — FIXED AND SHIPPED (PR #685, §1.5).** Residual (a local process needs no HTTP at all) is **structural, not a defect** — Fork 2 §5.3. |
| **R10** | The control overclaims | 2 | 4 | 8 | **OPEN — Phase 6.** *The shipped panel already gets this right for `guard-destructive` and **wrong** for `claim-grounding-lint`.* |
| **F6** | The `.ravenclaude/runs/**` widening | — | — | — | **⚠️ REGRESSED — see BLOCKER.** The mitigation *and* its forbid-list scoping are both gone. |
| **R11** | The portal's wire cost | 4 | 2 | 8 | **ACCEPTED, RECORDED (§11.4).** |
| **R13** | Virtualization treated as droppable | 4 | 2 | 8 | **CLOSED BY LABEL — Phase 3 conditional-but-expected.** |
| **R14** | Gate 13 byte-exactness → churn | 3 | 2 | 6 | **RESCOPED (P4).** |
| **R15** | `render_fragment()` sole-caller assumed | 2 | 3 | 6 | **OPEN — Phase 0, one command.** |
| **R7** | IA rebuilt on a falsified premise | 2 | 3 | 6 | **CLOSED BY SCOPE.** **P2 is R7's exact recurrence — the diagnostic was written and not re-run.** |
| **R5** | A switch check above the floors removes them | 1 | 5 | 5 | **CLOSED — no new key.** Standing constraint: any check sits at `:229`, never `:100`. |
| **~~R3/R4/R6/R12~~** | B's <2,000; B's gold gate; switch-without-trigger; cwd=`$HOME` | — | — | — | **All closed.** |

### 5.1 The standing signal — with an honest update

**Five consecutive FORGE gates were blocked by `guard-destructive.sh` false positives on read-only work** —
in a repo where the tribunal is OFF, by the one hook with **no knob** (no posture read, no bypass; only exits
`:74` empty and `:494` no-match; the deny fires at `:491` — **one code path that is simultaneously the false
positive and the real floor**).

**Two things follow:** (1) **this falsifies plan-A §4.1** (*"the annoyance and the protection are not the
same layer"*) — for the floor hook they are one code path; (2) **the highest-value guardrail work in this
repo is not a switch — it is reducing that FP rate** (§11.3).

**⚠️ The streak is broken, and the update cuts the same way.** G5-pass-2, G6-pass-2 and G6-pass-3 (this gate)
each ran ~10+ `grep`/`sed`/`python3` reads from the repo root and drew **zero** `guard-destructive.sh` false
positives. **Consistent with §11.3's narrow defect statement** (*"only a read whose **own search pattern**
carries the `key:` write-shape trips it"*) — none of these gates' patterns did. **The streak was real; so is
the narrowness.** The fix is cheap and targeted, and the ergonomic case for **any** switch weakens further.

**But note what blocked *this* gate instead: `enforce-layout.sh`** — and unlike the FP streak, **that deny
was correct.** The layout hook did its job; the *mitigation* had evaporated (§BLOCKER).

---

## 6. ✅ F6 — fixed, committed, merged, and verified on `main`

> **The retraction that stood here is itself withdrawn (2026-07-16).** It claimed the edit was *"never
> committed … evaporated … absent from both branches."* **False** — it was committed as `283f18f8` on
> `forge/dashboard-redesign`, a branch the retraction never checked, and it is now on `main` via PR #684
> (`610f35fa`). Pass-2's §6 was **right**; the retraction was the error. Both are recorded because the
> failure mode — *"absent from the two branches I looked at"* generalised into *"never committed"* — is
> exactly the over-generalisation this repo's accuracy discipline exists to catch, and it happened inside a
> gate built to catch it.

**Current state, verified by driving the real hook on `main`:**

| Path | Verdict |
|---|---|
| `.ravenclaude/runs/forge/<slug>/plan.md` · `runs/notifications/` | **ALLOW(0)** |
| `.ravenclaude/runs/thing/decisions/` · `runs/thing/runaway/` | **DENY(2)** |
| `.ravenclaude/runs/*/hook-events.jsonl` | **DENY(2)** |
| traversal (`runs/../../etc/passwd`) | **DENY(2)** |

`main:.repo-layout.json` — `allowed_globs:35` carries `".ravenclaude/runs/**"`; `forbidden_globs:80` carries
`[".ravenclaude/runs/thing/**", ".ravenclaude/runs/*/hook-events.jsonl"]`. **FORGE can write its own run
artifacts from any branch, and the audit substrate is closed to tool-shaped writes.**

**What remains true (the design, not the state):** the mitigation's *shape* was verified by execution when it
existed — `enforce-layout.sh:172-182` checks `forbidden_globs` **before** `allowed_globs`, forbidden wins;
FORGE run dir → ALLOW(0); `runs/thing/**`, `runs/*/hook-events.jsonl`, traversal → DENY(2). **It costs
nothing operationally** — the hooks that write those files use shell redirect/`jq`, not the `Write` tool, so
the tool-shaped hook never fires on them. Pass 2 swept every write this plan schedules: **no interaction.**

**~~What must be redone by a human~~ — nothing.** Both the allow and the forbid-list are committed and on
`main`. The forbid-list shipped **with** the allow, not after it, so the window in which the allow alone
exposed the runaway brake's counter never reached `main`.

**The lesson, which is §11.1's class in one sentence:** `enforce-layout.sh` polices a **gitignored** path
that **CI never sees** (`validate-layout.yml` inspects added **tracked** files; `.ravenclaude/runs/` is
gitignored at `.gitignore:4` with **0 tracked files**), and the only thing making FORGE's mandated writes
work was an **uncommitted** edit. **An uncommitted mitigation is not a mitigation — it is a session-scoped
illusion.** → **§11.1**, now with a live regression as its evidence.

**Honest caveat that still travels:** the run substrate is **not integrity-protected against the agent by any
layer** — the hook is tool-shaped and a `>` redirect writes unpoliced. **Heimdall and Víðarr present that log
to the user as an audit trail. An audit log the audited party can rewrite should not be labelled an audit log
without a caveat.**

---

## 7. Phases

**Every phase leaves the tree green and ends with a version bump + `scripts/audit-gates.sh`.**

**⚠️ REGEN PRECEDENCE (P4):** "regen is the LAST commit" and the per-commit ratchet are **mutually
exclusive** — honor the first and Gate 13 is red on every non-final commit (`:11598-11605` → `if existing !=
new_html: STALE`, exit 1; run by `audit-gates.sh:922`) while Gate 132 counts pre-phase bytes; honor the
second and R14 is violated by construction. **Ruling — R14 is about the *generator source*:** *no hand-edits
to a generated file; a regen conflict is resolved by **re-running the generator**, never by merging hunks.*
**Therefore every commit regenerates**, and the per-commit ratchet is real. The churn R14 feared is *review*
churn, not merge churn — a smaller cost §9's claim 4d already books as tooling.

---

### Phase 4a — Routes · **day 0, no pre-build gate**
Enumerate the exact current `#/…` grammar (shell router / `SECTION_ALIAS` / `DASH_OWNER` / every
`href="#/…"`) → **fixture**. **Extend Gate 51 to assert by destination.**
**Acceptance:** the fixture enumerates every committed `#/…`; Gate 51 green by destination against today's
tree; a must-fail half (delete one route) red. **DoD:** no version bump; the whole-tree bar.

---

### Phase 0 — Instrument, re-derive, sweep

**Pre-build gate:** none — the entry.

1. **🔴 ITEM 6 FIRST — the Fork 1 flip check. NOW LOAD-BEARING (§0.2), not informational.** Fork 1's stated
   condition: *"if the JSON-escaping fix in Gate 93 is a one-line regex loosening rather than a
   re-architecture, (b)'s cost collapses."* **Untested.** **It now sizes the funded Phase 2L. Run it before
   anything else in this phase** — the answer determines whether 2L is a one-line gate change or a
   re-architecture. *(Second, unchecked condition: whether a cheaper mechanism could lazy-load only Learn's
   ~7,519 SVG nodes while keeping the stepper/search markup live. **Also now load-bearing — it could deliver
   most of 2L's win at a fraction of its risk.** Check it here.)*
2. **Build Gate 132** — **slot 132 is free (Gate 131 is the highest live slot, `[G8-verified]`)**. Stdlib
   Python, **`html.parser`, script/style excluded — the method in the gate's own header**, with §2.1's reason.
3. **Two budgets, two ratchet tables** (F2).
4. **Per-panel payload budget** — JSON-decode each island, count its elements (§4.4). *(Its teeth-proof is
   **deferred to Phase 2's first island** — at Phase 0 no island exists to decode.)*
   - **4a. Emit the EXEMPTED floor** — `shell + active tab + Σ(exempt)`, now **`settings` only**. Emit the
     **residue** and the **× vs 1,400** for both surfaces. **This is §0.1's authority.** *(Fork 2's ~429
     predates the exemptions and is not routed here.)*
5. **Exemption sweep — enumerate from the artifact. 184 panels, not 180.** For each, grep for module-scope
   `document.querySelectorAll` / `getElementById` targeting that panel. Fails ⇒ **exempt or funded, never
   silently islanded.** Known failures: `settings` (exempt), `learn` (**funded — Phase 2L**).
6. **R8 sweep — read all 12 render gates in full.** Zero `[unverified]` rows. **Higher stakes now: 2L touches
   Gate 93 deliberately.**
7. **R15** — `grep -rn "render_fragment" . --include='*.py'` with **quoted** globs.
8. **Design tokens** → `design-token-delta.md`; the design project wins for values, `shared-tokens.css` stays
   the generate-time mechanism. *(If the design tool is unavailable, a `[blocked]` row with the named route —
   never a silent skip.)*

**Acceptance:** Gate 132 green at the re-derived baseline both surfaces, **must-fail at `count − 1`** red on
each *(plan A's literal 57,418 would have passed)* · **the exempted floor + residue + × emitted for both
surfaces** · Σ panels + shell = whole-document count · a verdict for **all 184** · the binding table 12/12 ·
`design-token-delta.md` (or `[blocked]`) · **the flip check answered in writing — it sizes Phase 2L.**
**DoD:** no version bump; the whole-tree bar.

---

### Phase 1 — Visual system + brand — **∥ Phase 2**

**Pre-build gate:** Phase 0's `design-token-delta.md`.

Dark default (light retained as `[data-theme="light"]`) · gold → `#C9A249` (**7.84:1 on `#14110d` — AAA**) ·
**correct the token comment** (claims ~3.6:1; real light value **3.12:1** — *worse*) **and scope the rule to
light mode, where it is real** · **re-derive "no gold body text" as aesthetic**, not an a11y floor ·
**self-host the fonts** (2 woff2, ~69 KB — kills the `:10-13` ↔ `:9-11` contradiction **and** the offline
failure; **independent — ship first**) · consume the design system.

**Acceptance:**
- **A contrast gate covering BOTH themes** — dark pairs ≥ 4.5:1 text / ≥ 3:1 UI **and the light-mode rule the
  plan affirms as real**. *Pass-2 fix: the gate asserted **dark only**, and B's gold ship-gate was dropped
  (correctly) — so **the one contrast rule this plan calls real was enforced by nothing** while light stayed
  a supported opt-out. **The correction over-corrected.** If light is instead left unenforced, say so and why.*
- **R9 — rewritten.** Plan A's *"all 12 green with zero fixture edits, the empirical proof of G1 6f"* is
  **struck**: G1 6f is false and Gate 51 binds a literal, whitespace-sensitive CSS rule. **Correct test: if
  Phase 1 touches the chrome-hide classes or reformats that rule, Gate 51 goes red and the fixture is updated
  in the same commit — that is the gate working.** Any *other* gate red **is** a defect.
- Gate 13 regen-clean; both surfaces dark; zero runtime third-party requests, asserted against the HTML.

**DoD:** minor bump in **both** manifests (**bump from `main` — §13.2**); Gates 13/35/51/132 + the 12; the
font asset dir added to `.repo-layout.json` **in this PR**; the whole-tree bar.

---

### Phase 2 — DOM fix · islands · **∥ Phase 1**

**Pre-build gates:** ✅ the stepper contract (decided — "convert", §0.2) · Phase 0's Gate 132 green + must-fail
red · a verdict for **all 184** · the R8 binding table · **Phase 4a's route fixture + Gate 51-by-destination.**
*(§0.2 is no longer a gate — it is answered.)*

**Scope:** **Island** `trees`, `commands`, and every small panel that **passed** the sweep.
**Exempt:** `settings` (§2.2) **+ any panel the sweep failed.** *(Learn is Phase 2L, not here.)*

**Order: largest first, one commit each, ratchet both surfaces each time. Every commit regenerates.**

**Acceptance, per commit:** Gate 132 ≤ the new per-surface budgets (**both**) and the per-panel payload
budget holds *(the payload teeth-proof lands here, at the first island)* · **counts asserted against the
generator's own inventories, never prose** — `_decision_trees_inventory()` (**924**),
`_best_practices_inventory()` (**2,216**), the commands glob (**525**) · **every committed `#/…` resolves**
(Phase 4a's fixture, 100%) · `__openPlugin` + `#dt-store` still render trees on plugin pages · **the exempt
panels are provably untouched — the 144 posture radios bind at load and a round-trip Save is byte-identical
for an unchanged posture** (F3's regression test, **mandatory** — Gate 35 is structurally blind to it) · the
12 + Gates 13/35 green.

**DoD:** minor bump per commit (both manifests, **from `main`**); `<noscript>` pointer to the source markdown;
**Gate 13 extended to cover any generated JSON the islands introduce**; the whole-tree bar.

---

### Phase 2L — 🔴 **CONVERT LEARN** *(promoted from §11.2 — now the point of the build)*

**Pre-build gates — HARD:**
1. **Phase 0's flip check answered** (it sizes this phase).
2. **Phase 2 merged** — it establishes the island mechanism this phase applies to a harder target.
3. **The Gate 93-v2 contract settled** (below) — the ordering constraint, at the phase boundary.

**Authorization — recorded verbatim, because it is the whole basis for this phase:**
> *"go with the recommendation. I'm fine with breaking live functionality temporarily if the dashboard gets
> updated and fixed."*

**This is an accepted risk, not an absent one. The authorization is conditional — *"if the dashboard gets
updated and fixed."* This phase's acceptance IS that condition. It does not ship broken.**

**Build:**
1. **Island the Learn panel** (~19,702 nodes — **79% of the pre-ruling residue; the single largest block**).
2. **Gate 93-v2** — rewrite from asserting on live HTML text (its own header: *"Pure text-based
   assertions… We assert against the generated HTML/JS text directly"*) to **parsing + unescaping the JSON
   payload** and re-running the same frame/dot/caption/hidden-controls invariants against it.
   **The must-fail half MUST exercise the payload-parsing path** (a payload with an unescaped quote or a
   missing frame key). **Today's must-fail half (stripped reduced-motion guard + forced second active frame,
   `check-stepper-render.mjs:81-92`) does not touch that path and would pass even if it silently no-ops.**
3. **Re-point three live-DOM-coupled subsystems to on-activate:**
   - **`initConceptSteppers()`** — currently an **immediately-invoked IIFE** (`generate-dashboards.py:10861-10864`)
     that queries the document at load and binds once.
   - **node_links** — the diagram deep-link JS targeting `.concept-diagram-well svg` live in the DOM.
   - **`#learn-search`** — filters via `panel.querySelector("#learn-search")` / `card.dataset.search` against
     **live DOM nodes** (`:10753`). **The only working search anywhere in the dashboard.**
4. **Heed the generator's own warning** — `:1198-1205` exists *because of a prior regression*: *"everything
   else… lives in the body and is **present in the DOM even while closed** — so `initConceptSteppers()` /
   node-link binding still find their targets."* **CLAUDE.md:828** records v0.118/0.119 breaking node_links by
   changing exactly this render shape. **This phase touches that coupling deliberately, with three consumers.**

**Acceptance — this IS the "gets updated and fixed" condition:**
- **Gate 93-v2 green**, and its must-fail half — **exercising the payload-parsing path** — red.
- **The steppers render and animate** after `activate('learn')`; the reduced-motion guard still holds.
- **node_links resolve** into the diagram after activation.
- **`#learn-search` filters the rendered subset** after `activate()` — **not just the raw payload.**
  *(A Gate-93-v2 that doesn't check this ships the exact regression `gap-delta.md` §7.1 and `critic-brief.md`
  §8.1 both already found.)*
- Gate 132 ≤ the new per-surface budgets; the Learn payload budget holds.
- Every `#/learn/<id>` deep link resolves and scrolls (Phase 4a's fixture).
- The 12 + Gates 13/35/51/132 green.

**DoD:** **its own PR** (Fork 1's requirement, honored), **its own risk review**, minor bump (both manifests,
**from `main`**); regen; the whole-tree bar.

**⚠️ Honest limit:** Gate 93-v2 asserts the **payload**, which is CI-safe and achievable now. Fork 1's
contract also named a **post-`activate()` DOM snapshot** — that is the rendered-DOM meter this plan defers
(§11.2b). **Its absence is exactly why Learn's breakage must be caught by eye and fixed, rather than by a
gate — which is the risk the human accepted, and it is why `settings` (which breaks silently) is NOT covered
by the same authorization (§0.2b).**

---

### Phase 3 — Virtualization · **conditional, expected**

**Pre-build gate:** Phase 2L merged.
**Entry condition (derived):** any islanded panel's **payload budget** exceeds the per-panel bar the Team Lead
sets from Phase 0. **Expect `trees` to trigger** (and possibly `learn`, now islanded).

*Correcting plan A:* it labelled this *"droppable"* and wrote *"if Phase 2 hits budget, do not build this"* —
but Phase 2's budget is a **load** budget and says nothing about the **open-panel** budget that triggers this
phase. **A's own projection guaranteed the entry condition fired** (R13). **Expected work, on the critical path.**

**Build:** render only expanded `<details>` cards.
**Acceptance:** the per-panel payload budget holds for every islanded panel; deep links into a non-rendered
card still resolve and scroll; the 12 + 13/35/51/132 green. **DoD:** minor bump; the whole-tree bar.

---

### Phase 4b — IA + search

**Pre-build gate:** Phase 2L merged (and Phase 3 if triggered). *Phase 4a landed on day 0.*

**Re-targeted where the gap is real (R7).** G4a falsified B's flagship justification: *"No search"* is
**false** (`learn-search` + 49 `data-search` blobs; the portal ships a **⌘K palette**, hand-maintained in the
shell — which is why three artifacts grepped one generator and wrongly concluded it was absent);
*"No faceting"* is **false for Learn** (10 collapsed `concept-cat` groups with count badges, deliberate per
CLAUDE.md v0.136.0). **B's proposed left rail is a description of the current Learn tab. Do not rebuild Learn.**

**The genuine gap:** **nothing searches the 924 trees / 2,216 best-practices / 525 commands.**

1. **A data-side search matcher over the island payloads** — `JSON.parse` the island and query it as data
   (~150 lines vanilla JS, no npm dependency, no new file). **B's mechanism meeting A's own requirement.**
   **No `search-index.json` sidecar** — the payload is already in the document; the zero-new-request property
   survives. **Note the new coupling: Phase 2L re-points `#learn-search` to the same data-side shape, so 2L
   and 4b share a mechanism — build it once, in 2L, and extend it here.**
2. **List-level grouping + count badges (`Stat`) for `trees` and `commands` only.**
3. **Additive only** (`#/learn/<id>?q=…`); `SECTION_ALIAS`/`DASH_OWNER`/`SECTION_TABS` **extended, never renamed.**
4. **Fail states designed:** unknown `#/…`; live `/__*` 404 on static Pages; zero search results — each
   explaining **why** and **what still works**.

**Acceptance:** ranked results with **no network round trip**; selecting a result deep-links + scrolls,
rendering the item if needed · **100% of Phase 4a's fixture; zero `#/…` 404s** · **`#learn-search` works
against the rendered subset** (2L's contract, re-asserted) · static-Pages smoke test (no `/__*` calls; the
**designed** empty state) · Gate 51 by destination; the 12 + 13/35/132 green. **DoD:** minor bump; whole-tree bar.

---

### Phase 5 — Posture-write integrity · **∥ Phases 1-4** · *(the `/__save` half is DONE — §1.5)*

**Pre-build gate:** none. *(Pass-2's hard `security-reviewer` gate was for the `/__save` remediation, which
**shipped in PR #685**. Dropped. **Phase 5 no longer blocks on an external verdict — it is now purely
data-integrity work.**)*

**5a — F4: the stream keys.** Add `stream_classify` + `stream_threshold` to `state` + `emitYaml`
(**emit-when-non-default**, matching the existing convention so "absent ⇒ default" holds) +
`applyGuardrailConfig`. Extend Gate 35's fixture.

**5b — 🔴 P3: Gate 35 must cover BOTH serializers.** Phase 6's acceptance requires all 4 knobs round-trip,
but **`guard-web-access`'s knob is not a comfort-posture key**: it lives in `.ravenclaude/web-access.yaml`
(schema `allow:` / `deny:` only — `guard-web-access.sh:9-10`) and round-trips through a **separate
serializer**, `emitWebAccessYaml()` (`:8782`) + `applyWebAccess()` (`:8789`), hydrated at `:8596`.
**`emitYaml()` never touches it.** **Gate 35 structurally cannot see it** — verified: its extract list
(`:50-68`) is `CR_DEFAULT`/`TIER_DEFAULT`/`RUNAWAY_DEFAULT`/`PARALLELISM_DEFAULT`/`DOD_DEFAULT`/`freshTiers()`/
`quoteYamlKey()`/`applyGuardrailConfig()`/`emitYaml()`, and its state model (`:83-95`) has **no web-access and
no path to it.** Its own header scopes it to *"the **comfort-posture** serializer."*

**Without this, the test resolves three ways and two are bad:** (a) add a web-access key to
`comfort-posture.yaml` → **the new top-level key §2.3 forbids** → Phase 6 breaches the ruling it exists to
honor; (b) extend Gate 35 but leave it unscoped → **it lands nowhere**; (c) **ship "3 of 4 round-trip" and
call it green** — the likely, vacuous path, and **§2.5's own diagnosis (*"the gate did not generalize; it
enumerates"*) recurring inside the phase built to honor it.**
⇒ **"Generalize Gate 35 to enumerate the posture keys the hooks actually read" explicitly includes
`guard-web-access.sh` reading `web-access.yaml`. Gate 35 covers both serializers.**

*(Checked and falsified, recorded so it is not re-raised: `emitWebAccessYaml()` rebuilds wholesale from the
DOM — F4's exact shape — **but `allow`/`deny` are the only keys in the schema and both are modelled. No data
loss.**)*

**Better, and the real fix:** generalize rather than enumerate — **key #15 repeated key #4's bug; otherwise
key #16 repeats it again.**

**Acceptance:** Gate 35 round-trips the stream keys (emit-when-non-default + hydrate-back), must-fail strips
one key → red · a posture carrying both survives a Save **byte-identically** for untouched keys · **Gate 35
reaches `emitWebAccessYaml()`/`applyWebAccess()` and round-trips `allow`/`deny`** · if generalized: adding a
key to a hook's parser **without** adding it to the dashboard fails the gate.
**DoD:** minor bump (both manifests, **from `main`**); Gates 13/35 + the 12; the whole-tree bar.

---

### Phase 6 — **`panel-pipeline` delta** *(NOT a new panel)*

**Pre-build gates — HARD:** **Phase 5 merged** *(it puts controls on the save path and gives the user a new
reason to Save; shipping over an `emitYaml` that silently destroys posture keys is exactly the failure this
plan exists to prevent — and **P3's Gate-35 expansion is inside that gate**, without which this phase's own
acceptance is unsatisfiable for `guard-web-access`)* · **Matt answers §2.7: extend or replace?**

**🔴 DO NOT BUILD A NEW PANEL.** `:11406` already ships the aggregated view (388 elements, 15 stages, live
badges, 7 knobs, R10 scope text correct for `guard-destructive`). A second view ships **two competing
guardrail surfaces** — R10's own defect, doubled.

**The delta:**
1. **🔴 Fix the false label (P5).** `_PIPELINE_LANES:687-700` → `claim-grounding-lint`: `"set": "Active once
   command review is turned on."` **False** — `grep -c 'command_review\|thing' claim-grounding-lint.sh` →
   **0**. Its real gate (`:47-62`) is (a) the file is under `knowledge/`/`docs/` and (b) a **bare
   file-presence** walk-up. **A user reaches this today:** turns command review off, reads the label,
   concludes the hook is off — **it still fires.** Replace with §2.3's wording: **"no knob — fires whenever a
   comfort-posture exists."** Same for `delegation-nudge`.
2. **Add the two missing hooks to the lanes** — `guard-web-access` (only in `panel-web-access`'s copy) and
   **`delegation-nudge`, absent from the generator entirely** (0 hits — **live drift today**).
3. **Build the drift gate — on `panel-pipeline`.** **No pipeline render gate exists.** Assert
   **`_PIPELINE_LANES` vs `hooks/hooks.json`**. **It would have caught both #1's label and #2's missing hook.**
4. **Ground the lanes, or stop claiming they are grounded.** The **only** `hooks.json` mention in the
   generator is **the `:473` comment claiming it. It is not.** Either generate the lanes from `hooks.json` or
   **correct the comment** — the drift gate makes the first safe.
5. **Surface the 4 knobs coherently** (§2.3). 3 already have inline editors; the delta is `guard-web-access`
   (P3). **NO new top-level posture key.**

**Standing constraint (R5):** any switch check sits **below** its hook's floor — at
`thing-orchestrator.sh:229`, **never `:100`** (`:95-99` says so; **neither plan cited it**). *(It also forces
a correction: plan-A §4.3 cited `:100` as its **model** — precisely the placement that removes the floors —
while §4.5 Option B promised to keep them. **A's mechanism contradicted A's own semantics.**)*

**Acceptance:** **the drift gate green, its must-fail half red** *(this is the phase's reason to exist)* ·
**labels match the hooks, asserted against them** · **exactly one guardrail view exists** (the P2 regression
test) · `guard-web-access` + `delegation-nudge` in the lanes · each of the **4 knobs** round-trips (Gate 35,
**both serializers**) · **✅ the view renders the "not configured yet" state for `web-access.yaml` rather than
assuming the file exists** (§2.9 — its absence is the documented fail-safe, not an error) · static Pages
read-only with an explanation · **a posture with all 4 knobs non-default survives a Save byte-identically for
every unmodelled key** · the 12 + 13/35/132 green.

**DoD:** minor bump (both manifests, **from `main`**); **migration note** if consumer-visible posture behavior
changes; the whole-tree bar. **If this phase adds/removes any skill/agent/artifact whose count is encoded in
marketplace prose, regenerate the counts/artifacts here** — skipping this caused the 2026-06-03 three-PR
hotfix chain (PRs #244–#247). **This phase is the live risk.**

---

### Phase 7 — Ship

**Pre-build gate:** Phases 1, 2, 2L, 4a, 4b, 5, 6 merged (3 if triggered).
`scripts/audit-gates.sh` → 0 · `prettier --check .` → 0 · `ruff check .` → 0 · the layout snippet ·
`scripts/check-checkout-fresh.sh` · **§13.2's version re-verification against `main`.**
**`landing=pr`** — **re-derive the justification (§BLOCKER item 2); the `.repo-layout.json` forcing function
is gone.** The PR body carries **§0.1's residue statement** and §0.2's ruling.

---

## 8. Tiebreak verdicts + mitigations → owning phase

| Ruling / mitigation | Source | Owning phase |
|---|---|---|
| ~~**Fork 1 — exempt Learn**~~ | `tiebreaks-learn.md` | **🔴 SUPERSEDED by the §0.2 human ruling.** The risk owner accepted the risk Fork 1 declined. → **Phase 2L (funded).** |
| **Fork 1 — (b)'s contract:** Gate 93 asserts the payload; the must-fail half exercises the **payload-parsing path**; `#learn-search` resolves against the **rendered** subset | `tiebreaks-learn.md` | **Phase 2L — now the live contract, not a hypothetical.** *(Its post-`activate()` snapshot half → §11.2b.)* |
| **Fork 1 — (b) gets its own PR + fixture + risk review** | `tiebreaks-learn.md` | **Phase 2L DoD — honored.** |
| ~~**Fork 2 — floor = shell + active tab**~~ | `tiebreaks-learn.md` | **AMENDED (P1) — Phase 0 emits the *exempted* floor** (`settings` only now). |
| **Fork 2 — do not split A's and B's numbers** | `tiebreaks-learn.md` | **Phase 0** — a measurement, never a compromise |
| **Fork 2 (security) — no master switch; the largest safe subset as a *view*** | `tiebreaks-security.md` | **Phase 6 — as a delta on the view that already ships (P2)** |
| **Fork 2 — the safety floor, never switchable** | `tiebreaks-security.md` | **Phase 6** + **§1.4** |
| **Fork 2 — placement at `:229`, never `:100`** | `tiebreaks-security.md` | **Phase 6** |
| **Fork 2 — "dashboard-only" is ergonomic, not a boundary** | `tiebreaks-security.md` | **§1.5 — now CONFIRMED in shipped code.** #685 closes the browser threat and explicitly does not stop a local process. |
| ~~**Fork 2 — the `/__save` guard as a live bug**~~ | `tiebreaks-security.md` §6 | **✅ FIXED — PR #685 (§1.5). Dropped from Phase 5.** |
| **Fork 2 — A's V3 confirmed** | `tiebreaks-security.md` §3 | **Honored by shipping no new key (Phase 6)** |
| **Fork 2 — correction to G4a:** *"neither trigger matches an HTTP post"* is **wrong** — `ALLOWED_TARGETS` forces the filename into the body; the conclusion survives via a **pre-written script** | `tiebreaks-security.md` §3 | **Recorded** *(the `/__save` path is now closed anyway)* |
| **Fork 2 — correction to G4a:** *"a plain READ is over-blocked"* **overshoots** — only a read whose **own pattern** carries the `key:` write-shape | `tiebreaks-security.md` §3.1 | **§11.3** |
| **Fork 2 — correction to A's V4:** `command_review.enabled` **does exist**, is engine-honored, and **is set in this repo's own posture**. A observed one posture file and generalized to the architecture; the critic endorsed it | `tiebreaks-security.md` §4/§8.3 | **Why Phase 6 builds no new tribunal key** |
| **F1 / F2 / F3 / F4 / F5** | `red-team.md` | **Phase 0 / 0+2 / 0+2 / Phase 5 / Phase 6** |
| ~~**F6 — `forbidden_globs`**~~ | `red-team.md` | **🔴 REGRESSED — the edit is gone (§BLOCKER). Needs a human.** |
| **P1 — residue; exempted floor; §11.2 promoted; derived target** | `red-team-2.md` | **§0.1, Phase 0 item 4a, Phase 2L, §12.2a** |
| **P2 / P3 / P4 / P5** | `red-team-2.md` | **Phase 6 / Phase 5 / §7 preamble+§3 / Phase 6 item 1** |
| **§6.1 — Phase 4a split (day 0)** | `red-team-2.md` | **§3 DAG + Phase 4a** *(the row §8 previously lacked)* |
| **§6.2 — the light-mode contrast rule has no gate** | `red-team-2.md` | **Phase 1 acceptance** |
| **§6.3 — 184 panels; enumerate from the artifact** | `red-team-2.md` | **Phase 0 item 5** |
| **R8 / R9 / R10 / R13 / R15** | `critic-brief.md` | **Phase 0 / 1 / 6 / 3 / 0** |
| **Gate 51 extension by destination** | `red-team-2.md` §6.1 | **Phase 4a** |

---

## 9. Unverified claims → the concrete step that settles each

| Claim | Marker | Settling step |
|---|---|---|
| **1b** — Astro's output dir is `_astro/` | `[unverified — training knowledge]` | **RETIRED** — Astro rejected on cost, not on this. **Moot regardless:** `.nojekyll` exists at the repo root — the gotcha is pre-solved. |
| **3b** — per-`client:*` hydration costs | `[unverified — training knowledge]` | **RETIRED** — Astro-only. |
| **4d** — "line length is irrelevant to HTML parsing" | `[unverified — training knowledge]` | **NOT LOAD-BEARING.** Phase 2 dissolves the 2.3 MB line as a side effect. **Gate:** if any phase proposes minification *for performance*, settle it first (WHATWG HTML §13.2, or an A/B parse benchmark). The long line is a **tooling** cost — real, and not a performance claim. |
| **5c** — the Google-Fonts egress / GDPR angle | `[unverified — training knowledge]` | **MOOT BY CONSTRUCTION** — Phase 1 self-hosts regardless, justified by the *verified* halves. |
| **6g** — minifier identifier-renaming | `[unverified — training knowledge]` | **RETIRED** — Astro-only. |
| **6h** — `is:inline` emits a bare `<script>` | Was the highest-leverage gap | **SETTLED — the repro was run.** Its thumb-on-the-scale sentence is struck. |
| **8e** — the self-disable regex misses a bare `thing:` key | Was Speculation | **SETTLED — falsified** (V2 found `:187`; Fork 2 §3 confirmed by executed regex evaluation). |
| **10c** — the gold delta is "visually near-indistinguishable" | Speculation (no ΔE) | **Phase 1 — the designer rules.** The *contrast* half is settled (7.84:1 AAA). |
| **11b** — `render_fragment()` has one caller | Medium | **Phase 0 item 7** — quoted globs. **B kept it open and B is right.** |
| **12 render gates' bindings** (7 unread) | `[unverified]` | **Phase 0 item 6** — read all 12. **2 of 5 checked bind markup/CSS. Now higher-stakes: Phase 2L touches Gate 93 deliberately.** |
| **Counts 924 / 2,216 / 525** | Both plans gate on them | **Phase 2 acceptance** — the generator's own inventories. |
| **Fonts: 2 woff2, ~69 KB** | Not checked | **Phase 1** — measured at self-host time; not load-bearing. |
| **Design-system token values** | Neither panel read them | **Phase 0 item 8** — or a `[blocked]` row, never a silent skip. |
| **Live hosted `content-length`** | `[unverified]` | **NOT LOAD-BEARING** — no wire budget in v1. |
| ~~**`/__save` POST executed end-to-end (T5)**~~ | Was inferred, not executed | **✅ SETTLED BY THE FIX — PR #685 drove a real server: header-absent POST 200 → 403; browser-shaped POST still 200.** The inference was correct and is now moot. |
| **F3's binds are non-idempotent under a later `activate()`** | Read, not browser-driven | **Moot — `settings` is exempt.** The `:13261` **state-divergence half survives regardless** (it runs once at load). Exempting is cheaper than settling. **Re-opens only under §0.2b**, and the rendered-DOM meter (§11.2b) settles it then. |
| **The other panels have no load-time DOM binds** | **The assertion that got `settings` wrong covered all 180 — and there are 184** | **Phase 0 item 5** — a verdict for all 184, **from the artifact**. |
| ~~**`.ravenclaude/web-access.yaml`**~~ | Was thrice-escalated by me | **✅ RESOLVED — §2.9. Optional by design; absence is the documented fail-safe (`guard-web-access.sh:14`); a template ships; the editor writes it on demand. Nothing to add or remove. My escalation was the error.** |

---

## 10. Content preservation, per phase

| Phase | 525 commands | 924 trees | 2,216 best-practices | 48 Learn concepts | 144 posture radios |
|---|---|---|---|---|---|
| 0 / 4a | untouched | untouched | untouched | untouched | untouched |
| 1 | restyled only | same | same | same | same |
| 2 | **island** | **island** + `#dt-store`/`__openPlugin` asserted | **island** | untouched | **EXEMPT** |
| **2L** | untouched | untouched | untouched | **🔴 ISLANDED — steppers/node_links/search re-pointed; Gate 93-v2. Temporary breakage authorized; acceptance is the "fixed" condition** | **EXEMPT** |
| 3 | virtualized render; payload unchanged | same | same | same | untouched |
| 4b | re-homed by group; legacy routes preserved | same | same | **search extended, not rebuilt** (R7) | untouched |
| 5 | untouched | untouched | untouched | untouched | **integrity restored** (F4/P3) |
| 6 | untouched | untouched | untouched | untouched | untouched — **labels corrected** (P5) |

**Nothing is dropped.**

**The reachability argument, corrected.** Plan A claimed islands *"preserve that exact reachability contract
byte-for-byte"* because inactive panels are already `display:none`. **That holds for *humans* and fails for
the *DOM query* — wrong three times over** (stepper init, node_links, `#learn-search`). A hidden panel keeps
nodes **queryable**; a JSON island does not. **This plan does not rely on that argument.** It exempts or
**funds** every panel with a load-time DOM bind — `settings` exempt, **Learn funded (Phase 2L)**. **Phase 2L
is precisely the cost of that argument being false.**

---

## 11. Named follow-ups — out of scope, with trade-offs

### 11.1 🔴 `enforce-layout.sh` has no gitignore exemption — **now with a live regression as evidence**
The hook is **strictly stricter than the CI backstop it mirrors**, permanently, for every gitignored path.
**§BLOCKER is this class firing:** the only thing making FORGE's mandated writes work was an **uncommitted**
edit, which evaporated on a branch change. **An uncommitted mitigation is not a mitigation.**
**Trade-off:** **consumer-facing hook behavior** — it changes what every installed plugin denies. Needs its
own design pass and `audit-gates.sh` fixtures (a gitignored-path must-allow **and** a tracked-path must-deny).
**Not in scope.** *If it lands, F6 and the asymmetry die together — the class fix.*

### 11.2b 🔴 The rendered-DOM meter (headless/JSDOM) — **the gate that unlocks §0.2b**
`tiebreaks-learn.md` §D5: **no plan has a CI-safe post-activation DOM check.** It is the missing half of Fork
1's Gate-93 contract **and** the prerequisite for converting `settings`.
**Why it now matters more than it did:** with Learn converted, **`settings` is 86.5% of the remaining
residue, and converting it clears Lighthouse's threshold outright (~0.5×)**. The only thing making that
decision unsafe is that `settings` breaks **silently** — and this meter is what makes it break **loudly**.
**Trade-off:** a materially larger build (headless browser or JSDOM in CI, a new gate class, new flake
surface). **Cost it explicitly — it converts §0.2b from "don't touch it" into a normal decision.**

### 11.3 `guard-destructive.sh`'s false-positive rate
The narrow, sharp defect: **the hook cannot distinguish a command from a command *passed as an argument to a
read-only tool*.** Pair with the accurate catalog defect: `concerns-catalog.md:189-191`'s *"a plain READ is
not over-blocked"* is **true for most reads, false for the subset whose own search pattern carries the `key:`
write-shape**. *G4a's blanket falsification overshot. Three consecutive gates have now drawn zero FPs, which
corroborates the narrowness (§5.1).*
**Trade-off:** every loosening of a floor hook is a security change, and `guard-destructive.sh` is **floor
end-to-end** — its FPs are the price of having no seam, and **that trade is currently correct**. Needs a
binding `security-reviewer` verdict + fixtures.

### 11.4 The portal's wire cost (R11)
`index.html` is **10.28 MB raw / 1.73 MB gzip** — **65% heavier** than the surface both plans reasoned about,
and it is the actual front door. **Accepted for v1:** the adopted mechanism keeps the bytes in the document
**by design** (that is what buys zero new requests), so an island-based plan **cannot express a wire budget**.
Gate 132 binds both surfaces for **nodes**, the measured bottleneck.

### 11.5 The run substrate is not integrity-protected against the agent
The hook is tool-shaped; a `>` redirect writes unpoliced. **An audit log the audited party can rewrite should
not be labelled an audit log without a caveat.** **§BLOCKER makes this worse, not better** — right now there
is not even a forbid-list.

---

## 12. Stop condition

**Ship when all eleven hold. Every line exits 0/1.**

1. `scripts/audit-gates.sh` → 0 — all gates, incl. the 12 + 13 + 35 + 51 + **93-v2** + 97 + 132 + the
   pipeline drift gate.
2. **Gate 132 green on BOTH surfaces** against their **own** re-derived budgets, under **`html.parser`**, with
   a **`count−1`** must-fail half red on each.
   - **2a. THE DERIVED TARGET — a budget is not a goal.** The load residue on each surface is **≤ that
     surface's exempted floor × (1 + margin)**, the floor being `shell + active tab + Σ(exempt)` **as Phase 0
     emits it**, margin set by the Team Lead. **Without this, §12.2 is a ratchet against a self-set bar.**
     **And state the residue in multiples of 1,400 in §0.1 and the PR** — the target is "we hit the floor our
     exemptions allow," **not** "we cleared Lighthouse."
3. **Per-panel payload budget** holds for every islanded panel.
4. **Contrast gate — both themes**, or a written statement that light is unenforced and why.
5. **Zero `#/…` 404s** — Phase 4a's fixture, 100%.
6. **Counts intact — 525 / 924 / 2,216** — the generator's own inventories.
7. **Zero runtime third-party requests** (fonts self-hosted).
8. **🔴 Learn is converted AND WORKING (§0.2's condition):** Gate 93-v2 green with a must-fail half that
   **exercises the payload-parsing path**; steppers render + animate after `activate()`; node_links resolve;
   **`#learn-search` filters the rendered subset**. **The exempt `settings` panel is provably intact** — the
   144 radios bind at load and round-trip a Save byte-identically.
9. **Posture-write integrity:** a posture carrying `stream_classify`/`stream_threshold` survives a Save
   byte-identically for every unmodelled key, **and Gate 35 reaches both serializers**.
10. **Exactly one guardrail view exists**, its labels match the hooks, the drift gate's must-fail half is red,
    **and the "not configured yet" web-access state renders**.
11. `prettier --check .` + `ruff check .` → 0.

**Explicitly NOT ship conditions:**
- ~~"≤ 12,000"~~ / ~~"< 2,000"~~ / ~~"no panel > 8,000"~~ — scope-derived or undderived; replaced by 2/2a/3.
- ~~"gold never as body text in either theme"~~ — forbids an AAA color and routes to a 6.12:1 one.
- ~~"a wire/payload budget"~~ — §11.4.
- ~~"the DOM is under Lighthouse's 1,400 threshold"~~ — **NOT achieved in this scope. The build lands at
  ~3.7× (was ~17.8× before the §0.2 ruling).** **One decision stands between this and the threshold:
  `settings` (§0.2b), gated on the rendered-DOM meter (§11.2b). Say this in the PR.**

**The bound on "iterate until perfect":** *perfect* is 1–11. **Aesthetic iteration is capped at three rounds
against the design project; a round counts only if it produces a named token/component delta.** A fourth
round is a **scope decision for the Team Lead.** Anything 1–11 does not cover is **v2**.

---

## 13. Definition of Done — repo conventions (`AGENTS.md`)

1. **Per-phase acceptance tests** — that phase's block in §7, all green, **re-run explicitly**.
2. **🔴 Semver — CORRECTED, and my pass-2 statement needs a precise correction, not a concession.**
   Pass-2 §13.2 said *"Currently **0.199.1** in both (G6-verified)."* **That was TRUE on the branch it was
   measured on** — `git show fix/ravenclaude-core-stale-macos-claims:…/plugin.json` → **0.199.1**, and my
   pass-1 tool output recorded exactly that. It was **not** 0.199.0 there. **But the statement was
   *unstable*, and the reason is a real defect worth more than the correction:**

   | Commit | Branch | Version |
   |---|---|---|
   | `51be23e3` (shared parent) | — | **0.199.0** |
   | `eb364c54` | `fix/ravenclaude-core-stale-macos-claims` | **0.199.1** |
   | `18109b18` (**PR #685**) | `fix/ravenclaude-core-save-header-guard` | **0.199.1** |

   **`eb364c54` and `18109b18` are SIBLINGS of `51be23e3` — neither is an ancestor of the other (verified:
   `git merge-base --is-ancestor eb364c54 HEAD` → NO). Both independently bumped 0.199.0 → 0.199.1. Two
   different plugin contents claim the same version.**

   **🔴 The CI drift gate cannot catch this.** It compares `plugin.json` **vs** `marketplace.json` — and on
   **each** branch they agree at 0.199.1. **Drift is green on both.** The gate checks *internal* consistency,
   never consistency *with history*. **So whichever PR merges second either conflicts on the version line
   or — if the line is byte-identical and git auto-resolves it — lands with NO EFFECTIVE BUMP, silently
   violating "bump on every user-visible change."**

   ⇒ **The rule is not "bump from the working branch." It is: bump from the version in `main` at merge time,
   and re-verify against `main` immediately before landing (Phase 7).** **This plan's first phase to land must
   bump to at least 0.199.2 — 0.199.1 is already occupied by #685.** Bump in **BOTH** manifests.
3. **Layout allow-list discipline** — any new directory's glob lands in `.repo-layout.json` **in the same PR
   as its first file** (per PR #32). **And per §BLOCKER: COMMIT it — an uncommitted glob is not a glob.**
4. **`npx --yes prettier@3.9.4 --write .`** before commit; `--check .` → 0. **Whole-tree.**
5. **`ruff check .`** → 0. Same discipline.
6. **`scripts/audit-gates.sh`** → 0. **A Gate 10 skip is not a pass.**
7. **`scripts/check-checkout-fresh.sh`** — never trust a run against a stale checkout.
8. **🔴 If any phase adds/removes a skill, agent, or artifact whose count is encoded in marketplace prose,
   regenerate the counts/artifacts in that phase.** Caused the 2026-06-03 three-PR hotfix chain (#244–#247).
   **Phase 6 is the live risk.**
9. **Migration note** for anything that could break a consumer on `/plugin marketplace update` — **Phase 6**
   if consumer-visible posture behavior changes. *(Phase 5's `/__save` migration note is moot — #685 shipped
   it.)*
10. **Regen precedence (P4):** **every commit regenerates.** R14 is about the *generator source*: no
    hand-edits to a generated file; a regen conflict is resolved by **re-running the generator**, never by
    merging hunks.

    **10a. The regen command set — BOTH surfaces, named explicitly (added at G8).** The plan binds two
    surfaces (§2.4, Phase 2's two ratchet tables), and each has its **own** freshness gate. Regenerating
    only the dashboard leaves the portal stale and **Gate 97 red**:

    | Surface | Regen command | Freshness gate |
    |---|---|---|
    | `dashboard.html` | `python3 scripts/generate-dashboards.py` | **Gate 13** (`audit-gates.sh:922`) |
    | `index.html` (portal) | `python3 scripts/generate-index-dashboard.py` | **Gate 97** (`--check`, `audit-gates.sh:153`, `:3629-3634`) |

    `scripts/generate-copilot-plugin.py` (copilot-package freshness, `:1500`/`:1527`) reads `agents/` —
    **out of scope unless a phase touches an agent/skill**; if Phase 6 ever does, it re-enters via item 8.

    **Re-derive this set from `scripts/audit-gates.sh` before trusting it** — the gate harness is the
    source of truth. FORGE's own `reference/regen-discipline.md` is a *cached copy* and was verified
    stale at G8: it omits `generate-concepts-doc.py`, `generate-bi-report.py`, and
    `generate-feedback-report.py` (all live in the harness), and its item 4 previously named
    `generate-repo-guide.py`, which v0.124.0 deleted `[G8-verified this session: file absent; Gate 97 +
    generate-index-dashboard.py present at audit-gates.sh:153 and :3629]`. **Gate 132 is free — Gate 131
    is the highest slot currently in the harness `[G8-verified; re-confirmed at G6 pass 3]`.**
11. **Landing:** `landing=pr`. **🔴 Re-derive the justification — §6's `.repo-layout.json` forcing function is
    GONE (§BLOCKER).** It is still almost certainly right (this plan commits to generator + hook + gate +
    manifest changes), but **do not cite the old reason.** The PR body carries **§0.1's residue statement** and
    **§0.2's ruling**.

---

## 14. Conduct record

**One guard denial this gate, reported verbatim and not routed around** (§BLOCKER): `enforce-layout.sh`
DENIED the mandated `plan.tmp` write. **I did not widen `.repo-layout.json`** — an agent widening a guardrail
config so its **own** write succeeds is the exact pattern this run exists to judge, and the deny's own text
routes it to a human PR. **I did not use a `>` redirect**, which `tiebreaks-security.md` §5.2 showed bypasses
the tool-shaped hook entirely — available, and forbidden. **No content was obfuscated, split, or encoded.**
This artifact sits in the session scratchpad, which `enforce-layout.sh:90-91` explicitly declines to police
(*"File is outside the project root — not our policy to enforce"*) — the hook's documented scope, and the same
disposition `tiebreaks-security.md` §7.1 recorded. **`plan.md` on disk is UNCHANGED and is not silently
half-updated.**

**Pass-3 verification note:** every input was independently re-verified rather than accepted on report — the
residue recomputation (§0.1), `guard-web-access.sh:14`'s fail-safe and the shipped template (§2.9),
`_state_change_origin_ok()` at `:1381`/`:1561` (§1.5), the stream keys' real path under `scripts/` (§2.5),
Gate 35's extract list and state model (P3), `panel-pipeline` and `claim-grounding-lint`'s false label (P2/P5),
and the version topology (§13.2) — **the last of which contradicted the correction I was handed.** Pass-2's
"0.199.1" was **true on its branch**; the real defect is a **sibling-branch version collision the drift gate
is structurally blind to**, which is a larger finding than the one reported. **Per this repo's accuracy
discipline — never falsely concede when corrected; verify first.**
