# G6 — Synthesis · The authoritative plan · `dashboard-redesign`

**Date:** 2026-07-15 · **Gate:** G6 (synthesis pass 2) · **Depth:** deep · **Owner:** Matt Corbett
**Repo:** RavenClaude @ `fix/ravenclaude-core-stale-macos-claims`, plugin `ravenclaude-core` v0.199.1
**Supersedes for build purposes:** `plan-A.md`, `plan-B.md`. Those remain the record of how we got here.
**Inputs merged:** `scope.md` · `claims-table.md` · `plan-A.md` · `plan-B.md` · `gap-delta.md` ·
`critic-brief.md` · `tiebreaks-learn.md` · `tiebreaks-security.md` · `red-team.md` · **`red-team-2.md`**

This is the last gate that reasons over the whole record. G7 routes; G8 checks.

**Pass-2 note:** a second red team attacked *this document* (pass 1 attacked the candidate plans, so
post-merge modes were structurally invisible to it). It returned **two HIGH** and **three MEDIUM** findings,
all folded below. **Both HIGHs visibly changed the plan** — P1 rewrote §0 and §12, P2 re-targeted Phase 6
from a build into a delta. Every pass-2 number below was **independently re-measured at G6** and the
deltas are recorded, not papered over.

---

## 0. What this build actually is — **and what it buys**

**Not** a top-to-bottom redesign. The record narrowed it three times, on measurement.

### 0.1 🔴 Read this before funding the long pole — the DOM pillar does **not** clear the threshold

**The single most decision-relevant fact in this plan, and it was absent from pass 1.**

| | `dashboard.html` | `index.html` |
|---|---:|---:|
| **Today** | 57,330 = **41.0×** the threshold | 50,945 = **36.4×** |
| **After the ENTIRE critical path** (Phase 0→2→3, the largest engineering here) | **≈24,900 = ~17.8×** | **≈25,600 = ~18.3×** |
| **Reduction** | **~57%** | **~50%** |
| **Of the remainder: the two exempt panels** | **97.2%** | 94.5% |
| **Of the remainder: `panel-learn` ALONE** | **79.1%** | 76.9% |

*Measured at G6 under `html.parser`, script/style excluded, islanded panels costed at 2 elements each
(`<section>` + `<script type="application/json">`). `red-team-2.md` independently derived 24,489 / 17.5× and
25,195 / 18.0× — **the two measurements agree within ~1.8% and agree exactly on every ratio.** The residue is
a **floor**: it assumes all 181 non-exempt panels island, and Phase 0's sweep can only **exempt more**, which
only raises it. **Phase 0 emits the authoritative figure (§7 Phase 0, item 4a) — neither number above is
adopted as a budget.***

**State it plainly: this build does not bring the DOM under Lighthouse's 1,400-node error threshold. It
removes ~57% of it and lands at ~17.8×. The work that would close the rest is §11.2 — currently scoped
OUT.**

**Why this was invisible until pass 2, stated honestly:** §12 correctly struck all three inherited node
targets (`≤12,000`, `<2,000`, `no panel > 8,000`) as underived — **and replaced them with nothing**. §12.2
then ratchets Gate 132 against *its own re-derived budget*, and F1's `count−1` must-fail half proves the
**meter** has teeth, not that the **build** has a target. **A ratchet whose budget is set from what was
achieved cannot fail on achieving little.** All ten stop conditions pass at 17.8×. §5's F3 row said only
"CLOSED BY SCOPE" — pass 1 had **priced** the exemption (≈24,646 / ≈25,902) and synthesis carried the
mitigation while dropping its decision-relevant half. §12 now carries a **derived target**, not just a
derived budget (§12.2a).

### 0.2 🔴 THE DECISION THIS PLAN OWES THE TEAM LEAD — make it in Phase 0, before the long pole is funded

> **Fund the critical path for ~57%, or fund the Learn conversion (§11.2) that is 79% of what remains?**

**These compete for the same engineering effort and the plan must not fund the first by default.**

- **Phase 2/3 as scoped** — 181 panels islanded, zero risk to any live-DOM binding, lands at ~17.8×.
- **§11.2 (convert Learn)** — Fork 1 declined it as *"open-ended engineering risk in a harness that has
  already regressed once"*, priced against the **baseline** at *"~19,702 nodes (34%)"*, where it reads
  optional. **Against the residue it actually competes with, Learn is 79%.** §11.2 is re-priced accordingly.
- **Phase 0's flip check (item 6) already exists to inform exactly this call** — Fork 1's own stated flip
  condition is that Gate 93's JSON-escaping fix might be a one-line regex loosening. The plan simply never
  said what that check was a decision *about*. It is this.

**And the honest third option — a waiver, which must be written down if taken:** *"~17.8× is acceptable for a
private, local-first tool; Lighthouse's 1,400 is a web-vitals threshold, not this tool's SLO."* **If that is
the answer, §0.3 must stop justifying a Large pillar with a threshold the build won't meet.** Per
`red-team-2.md` §9: **you may keep the threshold or keep the framing — not both.** Waiving it *silently* is
not acceptable.

### 0.3 The pillars

| Pillar | Honest verdict | Weight |
|---|---|---|
| **Visual / brand** | **A reskin.** A complete dark theme already ships (`shared-tokens.css:150-190`); the commerce gold is Δ6/255 from the existing dark gold. Work = flip the default, swap 6/255, self-host 2 woff2, apply the type scale. | Small |
| **Payload** | **Not a crisis.** 1.05 MB gzip (dashboard) / 1.73 MB gzip (portal). Real, not urgent. **No wire budget in v1** — §11.4. | None (v1) |
| **DOM** | **The one genuine engineering defect — and the build only gets ~57% of it (§0.1).** Weight is Large *for the effort*, not for the outcome. **Read §0.1/§0.2 before accepting this row.** | Large |
| **IA / search** | **Real gap, but only where the record proves it** — `trees` and `commands` have no search and no list-level grouping. Learn already has both (G4a §7.4). | Medium |
| **Guardrail control** | **Ruled out as posed** (Fork 2, binding). And **the aggregated view already ships** (`panel-pipeline`, P2) — so this is a **delta**, not a build. | **Small — shrunk at pass 2** |
| **Live bugs found en route** | **Four**, all independent of the redesign: the `/__save` header guard; `emitYaml`'s silent key drop; a **mislabelled shipped guardrail control** (P5); **a hook missing from the shipped pipeline map entirely** (P2). | Medium |

**The honest scope: reskin + a ~57% DOM fix + a targeted IA/search fix + four live-bug remediations + a
pipeline-panel delta.** Materially smaller than the G0 framing, and that is a finding, not a shortfall.

---

## 1. Binding rulings carried (not re-litigated)

1. **Astro rejected — fix the generator in place.** Settled at G4a after a hostile steelman including a
   hybrid neither panel considered. **The reasoning is corrected:** Astro's node-count benefit is **not
   falsified** — it is **not unique to Astro**. The rejection rests on the **cost** comparison, never on a
   falsified benefit, so it cannot be reopened on a bad basis: no node toolchain in a python-served plugin,
   no CI bump off the pinned `node-version: "20"`, no custom Content Layer loader for 924 non-file-backed
   markdown sections, 1 gate touched vs 12, no rewrite of 11,614 working lines. **Strike plan-A §7's
   "0 for 4."**
2. **The "12 gates bind JS only" premise is FALSE.** Gate 93 (`check-stepper-render.mjs`) binds generated
   **markup** and says so in its own header; Gate 51 (`check-shell-router.mjs`) binds markup **and** a
   literal, whitespace-sensitive CSS rule. G4a executed both plans' DOM mechanism against the real gate:
   **both return `exit=1`.**
3. **Gold-as-body-text is AAA (8.24:1) in dark mode**, not the 3.6:1 in `shared-tokens.css`'s comment (real
   light-mode value: **3.12:1**). An **aesthetic** call, not an a11y floor. **Panel B carried the false
   constraint into a binding ship-gate — DROPPED.** B's teal remedy measures **6.12:1**: the rule would have
   replaced an 8.24:1 color with a 6.12:1 one and called it safer.
4. **No master off-switch.** A switch spanning all 20 hooks IS the single catastrophic point of failure by
   construction — the defect is the topology, not the wiring. **The safety floor is never switchable:**
   `guard-destructive.sh` **entire**, `thing-orchestrator.sh`'s self-disable (`:159`) + hard-rule (`:210`)
   floors, `enforce-layout.sh`'s path-traversal scrub, the `security_deny` family (permission engine —
   genuinely not a hook), and the container/worktree boundary.
   *P2 re-targets Phase 6's **scope**; it does not reopen this ruling.*
5. **The `/__save` header guard is a confirmed live bug.** Absent `Origin` **and** absent `Sec-Fetch-Site`
   ⇒ `_local_request_ok()` returns `True` ⇒ `GET /__csrf` returns **200 + a CSRF token** (executed T1–T4).
   **Severity: medium** — loopback-bound (`:2004` binds `127.0.0.1`; `Host` fails closed). A real bypass
   **for the agent**, not for a remote attacker. **The `/__save` POST itself was never executed** — the probe
   was guard-denied and the gate stopped rather than reshape it. Both gates were observed open; a 200 on
   `/__save` was not. **Independent of the redesign; owns Phase 5a.**

---

## 2. Reconciliations — where the record contradicted itself

Later executed measurement supersedes earlier asserted numbers. Resolved, not averaged.

### 2.1 🔴 F1 — the counter, and the **precise** scope of what is retired *(narrowed at pass 2)*

`tiebreaks-learn.md` instructed `re.findall(r'<([a-zA-Z][a-zA-Z0-9-]*)[\s/>]', html)`. **JSON escapes `"`
but not `<`**, so:
- The `<script type="application/json">` wrapper **adds** a tag and every `<` in the payload survives
  encoding → **a regex Gate 132 reports ~zero reduction, slightly negative, for the adopted mechanism.**
  Reproduced: live markup 3 tag-tokens / island 4; `html.parser` live 3 / island 1.
- **Baseline is 57,330, not 57,419** (verified at G6 — my counter reproduces it exactly).
- **Plan A's must-fail half is broken under the correct parser:** 57,330 ≤ 57,418 **passes**. Derive the
  must-fail budget as **`count − 1`**, never a literal.

**⚠️ Pass-2 correction — my own §2.1 was OVER-STATED, and Phase 0 must not treat a confirmation as a
contradiction.** It declared *"429 / 19,702 / 20,131 / ≤20,500 are all regex-derived and incommensurable."*
**Measured at G6 under `html.parser`: `learn` 19,702 · `settings` 4,515 · `trees` 20,612 · `commands` 6,308
— identical to the regex slices, to the digit.** The divergence is **created by islanding; it does not exist
in the pre-islanding measurements.** Precise disposition:

| Figure | Status |
|---|---|
| **Per-panel slices** (19,702 / 4,515 / 20,612 / 6,308; index `trees` 13,521) | **CONFIRMED, not retired.** Both methods agree exactly. §11.2's use of 19,702 is **correct**. |
| **Whole-document total** (57,419 vs **57,330**) | Diverges by exactly the 89 script/style tokens. **Use 57,330.** |
| **Shell figures** (359 / 1,615) | **RETIRED — they genuinely diverge.** G6 measures **271** (dashboard) / **977** (index). Re-derive. |
| **Composed figures** (429 floor, 20,131, ≤20,500, F2's ≤21,800) | **RETIRED** — built on the retired shells, and falsified by the exemptions (§2.6). |
| **Any post-islanding count** | **The regex is blind. `html.parser` only.** |

**Rulings:** (1) **Specify `html.parser` inside Gate 132's own header** — the regex is load-bearing folklore
in four artifacts and will be reached for again. (2) Write §2.1's *reason* into that header too: G4a measured
only **89** tag-like tokens inside script/style — true **today**; post-islanding the divergence goes **89 →
~46,000**. **The plan invalidates its own justification.** (3) **Phase 0 re-derives every composed figure.**

### 2.2 🔴 F3 — `settings` is exempt; Fork 2's own test was never applied to it

Fork 1 exempted Learn *because* of load-time DOM binding. Fork 2 of the same artifact then pulled `settings`
into scope asserting *"no bespoke JS-binding contract … a plain content panel."* **False — verified at G6:**

- All **144** posture radios (`input[type="radio"][data-category][data-layer]`) live in `panel-settings`.
- `dashboard.html:13261` — **load-time, module-scope, document-wide** read, with the generator's own comment:
  `/* Read actual checked radios from DOM to pick up any rendered defaults */`.
- `:13906` / `:13941` — load-time `addEventListener` binds over the same document-wide selectors.

**Effect chain, all silent:** island `settings` → `:13261` reads an **empty NodeList** → `state.categories`
never picks up rendered defaults → **the in-memory posture silently diverges from what was rendered**;
`:13906`/`:13941` bind **zero** listeners → clicking a posture control does nothing; `forEach` over an empty
NodeList **throws nothing**. A subsequent Save writes `emitYaml(state)` **wholesale**
(`serve-dashboards.py:1520-1560` — no merge) → **a corrupted load persisted as a silently rewritten guardrail
posture.**

**Every gate stays green:** Gate 35 is **DOM-free by its own header** (`check-dashboard-roundtrip.mjs:11` —
verified) → **structurally blind**; the 12 render gates bind JS text (unchanged); Gate 13 regen matches; Gate
132 goes *greener*; Gates 93/51 untouched.

**Ruling — exempt `settings`**, for exactly the reason Learn was exempted. **The exemption test, mechanical
(Phase 0):** for each candidate panel, grep for module-scope `document.querySelectorAll` / `getElementById`
whose targets live in that panel. Fails ⇒ exempt. **Sweep all 184 panels** — *the assertion that got
`settings` wrong was made about all 180 at once, and there are **184** (§2.8).*

### 2.3 🟡 F5 — it is FOUR knobs, not six

Verified at G6: `claim-grounding-lint.sh:52-62` and `delegation-nudge.sh:56-65` are **byte-for-byte the same
bounded walk-up for the mere *presence* of `.ravenclaude/comfort-posture.yaml`** — `if [[ -f
"$dir/.ravenclaude/comfort-posture.yaml" ]]; then posture_found=1; break; fi` … `[[ "$posture_found" -eq 0 ]]
&& exit 0`. **Neither reads a key** (`grep -c 'command_review\|thing' claim-grounding-lint.sh` → **0**). So
`tiebreaks-security.md` §1's "own posture read" row is false, and its own table classifies that shape
(file-presence) as *"not a posture key"* — internally inconsistent; the miscount produced "6".

**Ruling — the 4 real knobs:** `guard-web-access` (`.ravenclaude/web-access.yaml`), `runaway-brake`
(`runaway:`), `dod-gate` (`definition_of_done`), `route-decision-review` (`decision_review`). Render
`claim-grounding-lint` + `delegation-nudge` as **"no knob — fires whenever a comfort-posture exists."**
**Do NOT introduce new top-level keys** — that reopens the V3 gap Fork 2 cited to reject the design (a new
top-level key is covered by **neither** `concerns-catalog.md:187` **nor** `:192`). Building over 4 existing
keys **preserves the ruling's load-bearing property: there is no single key to write.** Medium, not high —
both hooks are advisory (`exit 0` always).

### 2.4 🟡 F2 — per-surface budgets; the gate binds two surfaces, the tiebreak measured one

Fork 2 derived its floor from `dashboard.html` only; Gate 132 binds **both**. The portal's shell is far
larger, and Fork 2's whole margin cannot absorb the delta. `index.html`'s `trees` is **13,521**, not 20,612
(`include_trees=False`, `generate-dashboards.py:248` — G6-verified), so **the per-panel savings differ per
surface too — a single ratchet table is wrong on both ends.**

**Ruling — Gate 132 carries two budgets and two ratchet tables, both re-derived under §2.1's parser.** *(Both
surfaces have **184** panels and identical `learn`/`settings` — the exempt mass is the same 24,217; only the
shell and `trees` differ.)*

### 2.5 🟡 F4 — `emitYaml` silently drops `stream_classify` / `stream_threshold` on every Save

Verified at G6: `dashboard.html` contains **0** occurrences of either key. They are real posture keys, parsed
at **`plugins/ravenclaude-core/scripts/stream-session-start.py:55`** (`_MODE_RE`) and **`:57`**. *(Path
correction: G5 cited `hooks/`; the file is under `scripts/`.)* `/__save` writes wholesale; `emitYaml()`
rebuilds the file from `state`. **Gate 35's state model has no stream keys** → the gate that exists to catch
this is green.

**The v0.61.0 data-loss bug recurring** — that milestone fixed the identical defect for
`runaway`/`decision_review`/`definition_of_done` and added Gate 35. The stream keys shipped later (v0.164.0)
and were added to neither. **The gate did not generalize; it enumerates.**

**In scope because the plan raises its fire rate:** Phase 6 lives on this save path and gives the user a new
reason to Save. **Remediate in Phase 5b (Phase 6's hard pre-build gate).**

### 2.6 🔴 P1 — the residue, and the floor definition the exemptions falsified

**Two corrections, both structural:**

1. **§8 routed Fork 2's floor verbatim — *"measured floor = shell + active tab"* — to Phase 0. Under the
   adopted exemptions that floor is unreachable by ~24,200 nodes, permanently.** Phase 0 would emit a floor
   no later phase can approach, for a ratchet no later phase can satisfy. **The exemption (§2.2, adopted
   *after* that tiebreak) invalidates the floor §8 still routed.**
   **Ruling — Phase 0 emits the *exempted* floor:** `floor = shell + active tab + Σ(exempt panels)`.
   §8's row is amended.
2. **The residue is now stated in §0.1 and gated in §12.2a.** §11.2 is re-priced against it (§11.2).

### 2.7 🔴 P2 — **the aggregated guardrail view already ships.** Phase 6 is a delta, not a build

**The plan diagnoses this exact failure mode (R7) and then commits it one phase later.** §7 Phase 4 is
emphatic — *"three artifacts in this run grepped one generator and wrongly concluded it was absent"*;
*"B's proposed left rail is a description of the current Learn tab"* ⇒ *"do not rebuild Learn."*
**R7 was scoped to IA only. The same check was never run against Phase 6.**

**Verified at G6 — the shipped artifact:**

| Phase 6 proposed | Already ships |
|---|---|
| *"A dedicated 'Guardrail Pipeline' panel in Configure"* | `generate-dashboards.py:11406` → `<section class="tab-panel" id="panel-pipeline" … aria-label="**Guardrail pipeline**">`; tab at `:11379` (`data-cat="setup"`, *"Pipeline — the safety checks every command passes through"*). **Both surfaces, 388 elements each** (G6-measured). |
| *"A generated, always-visible disclosure line"* | `:472-476` — *"A visual map of **EVERY guardrail** … Each stage carries a **live ON/OFF badge**"*. 15 stages / 4 lanes; `badge ∈ {always, dynamic, advisory}`. |
| *"Four live knobs"* | **Seven** already have live inline editors (`syncPipelineTab()` `:8886`, dispatched `:8594`). **3 of Phase 6's 4** are among them. |
| *"The scope text goes ON the control (R10)"* | Already shipped for the floor: `guard-destructive` → *"Built-in safety floor — always on, can't be turned off."* |
| *"`PostureToggle`, not a row in a list"* | `:476` — knobs *"round-trip the **SAME** comfort-posture.yaml the Settings tab uses (shared `state` + emitYaml + /__save)"*. The seam already exists. |

**Blast if built as written — why HIGH, not a wasted phase:** it ships **two competing guardrail views on the
same surface**, each claiming to enumerate which hooks are active, each drifting independently, with Phase
6's drift gate on **only the new one** — and the new one **strictly narrower** (4 knobs vs 7) while claiming
to be the aggregated one. **By the plan's own R10 standard — *"a control that overclaims is worse than no
control, because the user will trust it"* — two guardrail views that can disagree about which floors are live
is that defect, doubled.**

**Ruling — re-target Phase 6 as a delta on `panel-pipeline`. The measured, real gaps (all G6-verified):**

1. **`guard-web-access` is missing from the lanes** — it appears in the generator only in the separate
   `panel-web-access`'s copy (`:11320`, `:11327`), **never in `_PIPELINE_LANES`**.
2. **`delegation-nudge` does not appear in the generator at all** — `grep -c
   'delegation-nudge\|delegation_nudge' scripts/generate-dashboards.py` → **0**. **The shipped map is already
   missing a hook. This is live drift today** — and the empirical proof Phase 6's drift gate is needed, **on
   the existing tab**.
3. **No pipeline render gate exists.** `ls scripts/check-*render*.mjs` → bifrost, concern-stats, heimdall,
   mimir, nidhoggr, norns, sleipnir, stepper, streams, vidarr. **No pipeline.** The drift gate is real, new,
   and valuable — it belongs on `panel-pipeline`.
4. **The lanes are hand-maintained, not generated.** `_PIPELINE_LANES` is a Python literal; the **only**
   `hooks.json` mention in the entire generator is **the comment at `:473` claiming it is grounded there.
   It is not** — #2 is the proof. Phase 6's *"sourced from the same config the hooks read, never a
   hand-maintained sentence that can drift"* is exactly right, aimed one panel to the left.

**Open product call — Matt's, not an agent's:** `panel-pipeline` is 388 elements and hand-maintained. If he
wants it **replaced** rather than extended, Phase 6 must say *"replace `panel-pipeline`"* and own the
removal, the `#/pipeline` route, and the fixture. **Either way, "build a new panel" as written is wrong.**

### 2.8 🟡 Pass-2 corrections to counts and claims *(lower-tier, folded)*

- **"180 panels" is 184.** G6-measured: **184** `.tab-panel` sections on **each** surface (`grep -c` → 184
  both). Phase 0's sweep is enumerative, so the count is not load-bearing — **but the sweep must enumerate
  from the artifact, never from a literal**, or four panels get no verdict and island unswept.
- **§3's "Phase 5 ∥ Phases 1-4 — disjoint from the generator's render path" is FALSE** (P4). G6-verified:
  `emitYaml` is emitted **by** the generator (`generate-dashboards.py:7226`), as is `applyGuardrailConfig`
  (`:7168`), into the same `dashboard.html` Phases 1-2 regenerate; Gate 35 then extracts it back out of that
  file. **The *generator source* regions are disjoint (`_page_kwargs` / `_JS` / `_CSS`); the *generated
  artifact* is shared — and that is what both gates read.** Corrected in §3.

---

## 3. Dependency DAG + critical path

```
  [SETTLED AT G4b — the ordering constraint, satisfied before any DOM work]
   Learn / Gate-93 stepper contract ──► (a) EXEMPT LEARN ─────────────────┐
                                                                          │
Phase 4a — ROUTES (day 0, no pre-build gate) ──────────┐                  │
  · enumerate every committed #/… → fixture            │                  │
  · extend Gate 51 by destination                      │ (Phase 2's       │
                                                       │  acceptance      │
Phase 0 ── instrument, re-derive, sweep ──┬────────────┤  consumes this)  │
  · Gate 132 (html.parser, per-surface)   │            │                  │
  · emit the EXEMPTED floor + residue     │            ▼                  │
  · exemption sweep (all 184 panels)      ├── Phase 2 (DOM fix) ──┬───────┤
  · R8 gate sweep · design tokens         │        │              │       │
  · §0.2 DECISION → Team Lead             │        ▼              │       │
                                          │   [Phase 3]           │       │
                                          ├── Phase 1 (brand)     │       │
                                          │   virtualization      │       │
                                          │   (conditional)       │       │
                                          │        │              │       │
                                          │        └──► Phase 4b (IA + search) ──┐
                                          │                                      │
                                          └── Phase 5 (posture-write integrity   │
                                               + /__save remediation)            │
                                                     │                           │
                                                     ▼                           │
                                               Phase 6 (pipeline delta) ─────────┤
                                                                                 ▼
                                                                         Phase 7 (ship)
```

**Ordering constraint honored:** the Learn/Gate-93 stepper contract was **decided at G4b — (a) exempt Learn —
before any DOM phase exists.** Phase 2 inherits it as a satisfied pre-build gate. Fork 1's own flip condition
is a bounded Phase 0 check (finding-only); a flip is a **Team Lead scope decision** (§0.2).

**Phase 4 is split (pass-2 fix, `red-team-2.md` §6.1).** Phase 2's per-commit acceptance requires *"every
committed `#/…` resolves (Gate 51 extended by destination)"* — but Phase 4 owned building that extension and
was gated on *"Phase 2 merged."* **A builder following the old DAG hits a circular dependency at Phase 2's
first commit**, and §8 assigned the Gate 51 extension to no phase at all. **Phase 4a (routes) is day-0 work**
— pure analysis of the current tree, depends on nothing — and **feeds Phase 2**. **Phase 4b (IA + search)**
runs after Phase 2/3. Both now have §8 rows.

**Parallel:**
- **Phase 1 ∥ Phase 2** — CSS vs body-emission: **disjoint generator-source regions** (`_page_kwargs` / `_JS`
  / `_CSS`). Expect a conflict only in `_page_kwargs`.
- **Phase 5 ∥ Phases 1-4** — **on the generator source only.** ⚠️ **Correcting this plan's own pass-1 claim
  (P4):** they are **not** disjoint on the *artifact* — `emitYaml` (`:7226`) and `applyGuardrailConfig`
  (`:7168`) are emitted **by** the generator into the same `dashboard.html`. **Three phases (1 ∥ 2 ∥ 5) each
  end by regenerating the same 7.8 MB file.** That is fine — see §7's regen precedence — but it is not
  disjointness and the plan must not claim it.

**Critical path:** `Phase 0 → 2 → [3] → 4b → 7`, with `4a` day-0 feeding Phase 2. Phase 2 is the long pole.
**Read §0.1/§0.2 before funding it.**

**The scheduling risk is Phase 5, not Phase 2.** It carries the only external dependency (a
`security-reviewer` verdict) and hard-gates Phase 6. **Dispatch the reviewer on day 0, in Phase 0.**

**Phase 3 is conditional-but-expected, not droppable** (R13) — see §7 Phase 3.

---

## 4. Alternatives + trade-offs

### 4.1 Stack

| Option | Trade-off, one line |
|---|---|
| **Fix the Python generator in place** | **ADOPT.** Attacks the measured bottleneck with zero node, zero CI bump, zero new dependency, 1 gate touched — and the brand work is already ~97.6% present as a color delta. |
| Astro `is:inline` | Reject — keeps all 12 gates (repro-confirmed) and delivers nothing: Astro touches none of the JS, so you rewrite 11,614 lines of Python into JS for zero payload, node-count, or beauty win. |
| Astro bundled + rewrite the 12 gates | Reject — a real component model + code-splitting, paid for with the repo's deepest harness, for a wire win that is real but not urgent. |
| **Astro hybrid (components for markup, inline directive for JS)** | Reject — the steelman neither panel considered, and it fails *worse*: the custom loader is still unavoidable, `scope_css`/`iife_wrap` still don't retire (they exist for the JS the directive keeps Astro away from), **and Astro normalizes markup → it breaks Gates 93 and 51 by construction. The option that looked like it kept the gates keeps 10 of 12.** |
| Style Dictionary token pipeline, no Astro | Reject — solves the one thing Astro was honestly for, but the bound design system is already the token source of truth. |

### 4.2 DOM-fix mechanism

| Option | Trade-off, one line |
|---|---|
| **Inline JSON islands, render-on-activate** | **ADOPT.** Script contents are never parsed into the DOM → zero new network requests, zero build step, zero static/served divergence, no cache-busting, no new gate surface, no `data/` dir needing an allow-list entry. **Honest ceiling: ~17.8% of the baseline remains (§0.1) — the mechanism is sound; the *scope* is what caps it.** |
| Sidecar JSON files | Reject as the content mechanism — shrinks the document (a real edge forgone), but adds cache-busting, a Gate 13 extension, a new allow-listed dir, a fetch beat per first tab open, and a JS-off hole. **Its Gate-13-extension discipline is adopted anyway; its data-side search matcher is adopted in Phase 4b.** |
| Server-side pagination via `/__read` | Reject outright — breaks on static GitHub Pages, one of the two required surfaces. |
| True multi-page SSG | Reject for v1 — high risk to "every `#/…` resolves" for a crawlability payoff this private tool does not need. |

**Correction carried:** plan-A justified islands partly via Constraint 4 (*"NO RUNTIME LOAD"*) read as a
general no-runtime-fetch rule. **G1 5a already narrowed that** — the claim is scoped to the token CSS; the
generalization *"every HTML artifact stays self-contained"* is **false** (the file's own Google Fonts `<link>`
proves it). **Right mechanism, one wrong reason.** The other three reasons stand alone.

### 4.3 The guardrail control

| Option | Trade-off, one line |
|---|---|
| **A delta on the shipped `panel-pipeline`** | **ADOPT (P2).** The aggregated view already exists with 15 stages, live badges, 7 knobs and R10 scope text. The delta is 4 real gaps (§2.7) — smaller, real, better-aimed, and it fixes drift that exists **today**. |
| A new aggregated panel (pass-1 Phase 6) | **Reject — it is a duplicate.** Ships two competing guardrail views, drift-gated on only the new one, and strictly narrower (4 knobs vs 7). |
| **Replace `panel-pipeline` outright** | **Open — Matt's call (§2.7).** Legitimate (it is 388 elements, hand-maintained) but must own the removal, the route, and the fixture. |
| A new top-level master key spanning 20 hooks | Reject (binding, Fork 2) — the switch *is* the catastrophic point; and a new key is covered by neither self-disable trigger (V3). |
| Retrofit a uniform gate into all 20 hooks | Reject — six hooks cannot be turned off at all, and the shapes are not commensurable. A **new cross-cutting control plane whose failure mode is total**. |

### 4.4 The DOM meter

| Option | Trade-off, one line |
|---|---|
| **Static `html.parser` counter: per-surface load budget + per-panel *payload* budget (JSON-decode the island, count its elements)** | **ADOPT.** Deterministic, browser-free, CI-safe, ratcheted from a green baseline with a `count−1` must-fail half — **and it closes D5's "no CI-safe post-activation check" for islanded panels**, because the island payload *is* the markup `activate()` renders. |
| Headless / JSDOM rendered-DOM meter | Defer — resolves F1 and F3(b) together and is the only meter that sees *arbitrary* JS-rendered DOM, but a materially larger build, and unnecessary once panels with load-time binds are exempted rather than converted. **§11.2.** |
| Regex tag-token counter | **Reject — this is F1.** Blind to the exact mechanism it exists to measure. |

**Stated assumption:** the meter assumes `activate()` renders the payload verbatim — the adopted mechanism.
If Phase 3 virtualizes, the rendered subset is **smaller**, so the budget stays sound as a ceiling. **Write
this into Gate 132's header.**

---

## 5. Risk matrix — merged G4a (R*) + G5 pass 1 (F*) + G5 pass 2 (P*)

Score = P × I. **Status is this gate's disposition**, not a restatement.

| # | Risk | P | I | Score | Disposition at G6 |
|---|---|:-:|:-:|:-:|---|
| **P1** | **The plan passes every gate while the DOM pillar lands at ~17.8× — and no acceptance test can fail on it** | **5** | **4** | **20** | **OPEN BY DESIGN, now VISIBLE.** §0.1 states the residue up front; §0.2 puts the fund-this-or-§11.2 decision to the Team Lead **before** the long pole; §12.2a adds a **derived target**, not just a derived budget; §11.2 re-priced at 79%. **A waiver is acceptable and must be written down (§0.2).** |
| **F3** | **Islanding `settings` kills the posture editor + corrupts posture state, all gates green** | **5** | **5** | **25** | **CLOSED BY SCOPE — `settings` exempt (§2.2).** **Its price is now carried, not dropped: the exemption is 97.2% of the residue (§0.1) — that omission was P1's root cause.** |
| **P2** | **Phase 6 rebuilds `panel-pipeline`, which already ships → two competing guardrail views, drift-gated on only the new one** | **5** | **4** | **20** | **CLOSED BY RE-TARGET (§2.7).** Phase 6 is now a delta on the shipped panel. **The plan's own R7 diagnostic, never run against Phase 6 until pass 2.** |
| **F1** | **Gate 132's regex counter is blind to the adopted mechanism** | **5** | **4** | **20** | **CLOSED BY DESIGN — `html.parser` in the gate; Phase 0 re-derives; must-fail = `count−1`.** **Scope narrowed at pass 2: per-panel slices are CONFIRMED, not retired (§2.1).** |
| **R1** | DOM fix breaks Gate 93 (steppers, node-links, Learn search dead) | 5 | 4 | 20 | **CLOSED BY SCOPE — Fork 1 exempts Learn.** Gate 93, `initConceptSteppers()`, node_links and `#learn-search` untouched. |
| **R2** | `/__save` reachable by a local process | 4 | 4 | **16** | **OPEN — Phase 5a.** Loopback-bound, `Host` fails closed. Real for exactly one adversary — the agent. |
| **P3** | **Phase 6's acceptance is unsatisfiable for 1 of 4 knobs — and satisfying it needs the key §2.3 forbids** | 4 | 3 | **12** | **CLOSED BY SCOPE — Phase 5b covers BOTH serializers (§7 Phase 5b).** F5 checked the view could *save* and closed it; **it can save, it cannot be gated.** |
| **R8** | The other render gates carry undiscovered markup/CSS bindings | 3 | 4 | **12** | **OPEN — Phase 0 sweep.** 2 of 5 checked bind markup/CSS; the prior is not good. |
| **F4** | `emitYaml` drops `stream_classify`/`stream_threshold` on every Save | 4 | 3 | **12** | **OPEN — Phase 5b.** Live today; G6-verified. Phase 6 raises its fire rate. |
| **F2** | Single-surface budget vs a two-surface gate | 4 | 3 | **12** | **CLOSED BY DESIGN — per-surface budgets + tables (§2.4).** |
| **P4** | **R14 ("regen is the LAST commit") and Phase 2's per-commit ratchet are mutually exclusive** | 4 | 3 | **12** | **CLOSED BY PRECEDENCE — R14 rescoped to the generator *source*; Phase 2 regens per commit (§7 preamble).** Also falsifies this plan's own §3 disjointness claim (§2.8). |
| **P5** | **A shipped guardrail control is already mislabelled; the plan corrected it only on the panel it should not build** | 4 | 3 | **12** | **CLOSED BY RE-TARGET — folded into Phase 6's delta (§7 Phase 6).** Post-merge would have shipped **two contradicting labels for the same hook**. |
| **R9** | Visual redesign breaks Gate 51's chrome-hide CSS rule | 3 | 3 | **9** | **OPEN — Phase 1.** CONFIRMED by G4a execution; the acceptance test is rewritten. |
| **F5** | The view's "six hooks" is four | 4 | 2 | 8 | **CLOSED BY DESIGN — 4 knobs, 2 labelled "no knob" (§2.3).** |
| **R10** | The control overclaims | 2 | 4 | 8 | **OPEN — Phase 6.** *Note P2/P5: the shipped panel already gets this right for `guard-destructive` and already gets it **wrong** for `claim-grounding-lint`.* |
| **F6** | The `.ravenclaude/runs/**` widening | 2 | 3 | 6 | **MITIGATED — `forbidden_globs` (§6).** Pass 2 swept every write this plan schedules: **no interaction** (`red-team-2.md` §7.3). Residual: the *class* is unfixed (§11.1). |
| **R11** | The portal's wire cost is never addressed | 4 | 2 | 8 | **ACCEPTED, RECORDED (§11.4).** |
| **R13** | Virtualization treated as droppable | 4 | 2 | 8 | **CLOSED BY LABEL — Phase 3 conditional-but-expected.** |
| **R14** | Gate 13 byte-exactness → merge churn | 3 | 2 | 6 | **RESCOPED (P4).** Regen is mechanical; a regen conflict is resolved by **re-running the generator**, never by merging hunks. |
| **R15** | `render_fragment()` sole-caller assumed | 2 | 3 | 6 | **OPEN — Phase 0, one command.** |
| **R7** | IA rebuilt on a falsified premise | 2 | 3 | 6 | **CLOSED BY SCOPE — IA re-targeted at `trees` + `commands`.** **P2 is R7's exact recurrence one phase later — the diagnostic was written and not re-run.** |
| **R5** | A switch check above the floors removes them | 1 | 5 | 5 | **CLOSED BY DESIGN — no new switch key.** Standing constraint: any check sits at `:229`, never `:100`. `thing-orchestrator.sh:95-99` says so and **neither plan cited it.** |
| **R16** | Astro reopened on contaminated reasoning | 2 | 2 | 4 | **CLOSED — reasoning corrected (§1.1).** |
| **R3 / R4 / R6 / R12** | B's <2,000; B's gold gate; switch-without-trigger; cwd=`$HOME` | — | — | — | **All closed** (§2.1 / §1.3 / §2.3 / §6). |

### 5.1 ⚠️ The standing signal — surfaced, not buried

**Five consecutive FORGE gates were blocked by `guard-destructive.sh` false positives on demonstrably
non-destructive, read-only work — in a repo where the tribunal is OFF, by the one hook with no knob.**
G1 (a `curl` font measurement) · G2 (a `python3` regex test and a `sed -n` read — **both reads**) · G4a
(three read-only `grep`/`sed`) · G4b-security (three, incl. a literal that was **an argument to a read-only
classifier**) · G5 (a cleanup **inside the session scratchpad**).

**The off-switch under design would have prevented none of them.** The tribunal is inert here; every deny
came from `guard-destructive.sh` — no posture read, no env bypass, no knob; only exits `:74` (empty) and
`:494` (no match). The deny fires at `:491` — **one code path that is simultaneously the false positive and
the real floor. There is no seam to cut between them.**

**Two things follow, and both bind:**
1. **This falsifies plan-A §4.1** (*"the annoyance and the protection are not the same layer"*) — the central
   input to A's floor decision. For the floor hook, they are one code path.
2. **It relocates the real friction.** **The highest-value guardrail work in this repo is not a switch — it
   is reducing `guard-destructive.sh`'s false-positive rate.** §11.3. **The one change that would have
   unblocked all five gates.**

**⚠️ Pass-2 datum that sharpens this, recorded honestly:** **G5-pass-2 ran a dozen `grep`/`sed`/`python3`
reads from the repo root and drew ZERO false positives — breaking the streak.** G6 (this gate) likewise drew
zero across ~10 reads. **That is consistent with §11.3's narrow defect statement** (*"only a read whose **own
search pattern** carries the `key:` write-shape trips it"*) — neither gate's patterns did. **The streak was
real; so is the narrowness.** It cuts the same direction: if the FP rate is this pattern-specific, the fix is
cheap and targeted, and the ergonomic case for **any** switch weakens further — it does not strengthen.

---

## 6. Already DONE this session — completed, not pending

**F6 is fixed and verified.** `.repo-layout.json` gained `.ravenclaude/runs/**` to `allowed_globs`
(**human-approved**) because `enforce-layout.sh` was denying FORGE's own **mandated** run-dir writes from the
repo root. Every earlier artifact existed only because session 1 ran from `$HOME`, where the hook is inert
(`enforce-layout.sh:62`). The red team then found that glob **too broad** — it exposed `runs/thing/**` (the
runaway brake's counter: `runaway-brake.sh:48`, `:161-163`; a one-line `Write` of `0 - 0` **resets the
brake**) and `runs/*/hook-events.jsonl` (**forgeable, erasable deny history**, read by Heimdall, Víðarr, and
the SessionStart banner). So `forbidden_globs` now carries both.

**Driven live against the real hook** (`enforce-layout.sh:172-182` checks `forbidden_globs` **before**
`allowed_globs`; forbidden wins): FORGE run dir → **ALLOW(0)** · notifications → **ALLOW(0)** ·
`runs/thing/decisions/` → **DENY(2)** · `runs/thing/runaway/` → **DENY(2)** · `runs/*/hook-events.jsonl` →
**DENY(2)** · traversal → **DENY(2)**.

**Verified at G6:** `allowed_globs` contains `.ravenclaude/runs/**`; `forbidden_globs` is exactly
`[".ravenclaude/runs/thing/**", ".ravenclaude/runs/*/hook-events.jsonl"]`; `git status` → `M
.repo-layout.json` (uncommitted). **Pass 2 swept every write this plan schedules against those forbids —
Phase 0's token delta + Gate 132, Phase 6's disclosure source, Phase 5's fixtures, all gate outputs: no
interaction** (`red-team-2.md` §7.3). *Phase 6 enables `route-decision-review`, whose tribunal logs land under
the now-forbidden `runs/thing/decisions/` — but the hook writes those via shell redirect/`jq`, which the
tool-shaped `enforce-layout.sh` never sees. **§6's "costs nothing operationally" holds against the full write
set.***

**Two things this plan records:**

1. **This is an engineering pre-commitment** — a `.repo-layout.json` `allowed_globs` edit, a boundary file.
   **It forces `landing=pr` at G7.** The PR body needs this rationale verbatim: *the hook was denying the
   run-artifact convention the plugin's own CLAUDE.md mandates (`.ravenclaude/runs/<task-or-epic-id>/`); the
   allow is scoped by a forbid-list that keeps the tribunal substrate and the hook-event audit log out of the
   `Write` tool's reach; both were driven live against the real hook.* Alternative considered and rejected:
   narrowing to `.ravenclaude/runs/forge/**` — that denies the general convention. **The forbid-list is the
   better instrument.**
2. **The underlying class is unfixed.** `enforce-layout.sh` has **no gitignore exemption**, so it is
   **strictly stricter than the CI backstop it mirrors** — `validate-layout.yml` only inspects **added
   tracked files**, and `.ravenclaude/runs/` is gitignored (`.gitignore:4`, verified) with **0 tracked files.
   CI never sees this path at all.** **This edit fixes the instance, not the class.** → **§11.1**, not
   in-scope.

**Honest caveat travelling with the waiver:** the run substrate is **not integrity-protected against the
agent by any layer** — `enforce-layout.sh` is tool-shaped (`Write|Edit|MultiEdit`) and a `>` shell redirect
writes unpoliced. The forbid-list makes the *sanctioned tool path* no more permissive than the hole that
already exists; it does not close the hole. **Heimdall and Víðarr present that log to the user as an audit
trail. An audit log the audited party can rewrite should not be labelled an audit log without a caveat** —
the same "label the control" discipline this plan applies elsewhere.

---

## 7. Phases — pre-build gates · acceptance · DoD

**Every phase leaves the tree green and ends with a version bump + `scripts/audit-gates.sh`.**

**⚠️ REGEN PRECEDENCE (P4) — this replaces pass-1's "regen is the LAST commit of a phase."** That rule and
Phase 2's per-commit ratchet are **mutually exclusive**, and pass 1 gave no precedence:
- **Honor "regen last"** ⇒ every non-final Phase-2 commit ships a stale artifact ⇒ **Gate 13 red on every
  one** (`generate-dashboards.py:11598-11605` → `if existing != new_html: STALE`, exit 1 — G6-verified; run
  by `audit-gates.sh:922`), **and** Gate 132 counts pre-phase bytes, so the ratchet measures the artifact the
  commit didn't change and goes red against a ratcheted-down budget. **The phase cannot proceed.**
- **Honor the per-commit acceptance** ⇒ regen every commit ⇒ **R14 violated by construction.**

**Ruling — R14 is about the *generator source*, not the artifact:** *no hand-edits to a generated file; regen
is mechanical, so **a regen conflict is resolved by re-running the generator, never by merging hunks**.* That
dissolves the conflict for parallel phases at zero cost. **Therefore: every commit regenerates**, and the
per-commit ratchet is real. The churn R14 feared is not *merge* churn but *review* churn — a smaller,
different cost that §9's claim 4d already books as a tooling cost.

---

### Phase 4a — Routes · **day 0, no pre-build gate** · owner: `frontend-coder`

*Split out at pass 2 (`red-team-2.md` §6.1): Phase 2's acceptance consumes this, and the old DAG gated it
behind Phase 2 — a circular dependency at Phase 2's first commit.*

- Enumerate the **exact current** `#/…` grammar (shell router / `SECTION_ALIAS` / `DASH_OWNER` / every
  `href="#/…"`) and **snapshot it as a fixture**.
- **Extend Gate 51 to assert by destination.**

**Acceptance:** the fixture enumerates every committed `#/…`; Gate 51 green by destination against today's
tree; a must-fail half (delete one route) goes red.
**DoD:** no version bump. The whole-tree bar.

---

### Phase 0 — Instrument, re-derive, sweep, **and put §0.2 to the Team Lead** · owner: `backend-coder` + `tester-qa`

**Pre-build gate:** none — the entry. **Dispatch `security-reviewer` for Phase 5 on day 0, here.**

1. **Build Gate 132** (next free slot; used slots G6-verified: 1-38, 40-54, 60, 70, 80, 90-93, 97-106,
   110-129, 131 → **132+ free**). Stdlib Python, **`html.parser` element count, script/style contents
   excluded — the method written into the gate's own header**, with §2.1's reason (89 → ~46,000 post-islanding).
2. **Two budgets, two ratchet tables** — `dashboard.html` and `index.html` (F2).
3. **Per-panel payload budget:** JSON-decode each island, count *its* elements — the CI-safe post-activation
   check for islanded panels (§4.4). Write the stated assumption into the header. *(Its teeth-proof is
   **deferred to Phase 2's first island** — at Phase 0 no island exists to decode. `red-team-2.md` §7.5.)*
4. **Re-derive under the correct parser.** Baseline **57,330**. **No composed figure from any prior artifact
   is adopted** (§2.1's table says exactly what is retired and what is confirmed — **do not re-litigate the
   per-panel slices; they reproduce to the digit**).
   - **4a. 🔴 Emit the EXEMPTED floor, not Fork 2's shell+active-tab floor (P1):**
     `floor = shell + active tab + Σ(exempt panels)`. **Fork 2's ~429 is unreachable by ~24,200 under the
     adopted exemptions and must not be routed here.** Emit the **residue** and the **× vs 1,400** for both
     surfaces. **This number is §0.1's authority.**
5. **Exemption sweep — enumerate from the artifact.** **There are 184 panels, not 180** (G6-verified, both
   surfaces). For each, grep for module-scope `document.querySelectorAll` / `getElementById` whose targets
   live in that panel. Fails ⇒ **exempt**. `learn` and `settings` are known failures.
6. **Fork 1 flip check (bounded, ≤30 min, finding-only).** Fork 1's stated flip condition: *"if the
   JSON-escaping fix in Gate 93 is a one-line regex loosening rather than a re-architecture, (b)'s cost
   collapses."* **Untested. Test it; report the finding. Do not act on it.** *(Second, unchecked flip
   condition: whether a cheaper mechanism could lazy-load only Learn's ~7,519 SVG nodes while keeping the
   stepper/search markup live. Also finding-only.)*
7. **R8 sweep — read all 12 render gates in full.** Output: a per-gate binding table, zero `[unverified]`.
8. **R15** — `grep -rn "render_fragment" . --include='*.py'` with **quoted** globs.
9. **Design tokens** — read project `76e5ef74-a8c4-4cf7-9423-86ca92eddbdc` (tokens, variants, both ui_kits)
   → `design-token-delta.md` reconciling against `shared-tokens.css`. **Where they differ, the design project
   wins for values; `shared-tokens.css` stays the generate-time mechanism.** *(If the design tool is
   unavailable in the build session, this becomes a `[blocked]` row with the named route — not a silent skip.)*
10. **🔴 PUT §0.2 TO THE TEAM LEAD.** Deliver: the residue, the ×, the 97.2% / 79.1% split, the flip-check
    finding, and the §11.2-vs-Phase-2/3 comparison. **Phase 2 does not start until this is answered.**

**Acceptance:**
- Gate 132 green at the re-derived baseline on **both** surfaces; **must-fail half at `count − 1`** (derived,
  never literal) red on each. **This is the teeth-proof — plan A's literal 57,418 would have passed.**
- **The exempted floor + residue + × are emitted for both surfaces** (P1). *This is the phase's most
  important output.*
- Self-consistency over live markup: **Σ panels + shell = whole-document count**, both surfaces.
- Exemption sweep emits a verdict for **all 184**. **A panel with no verdict is not islandable.**
- Per-gate binding table: 12 of 12, zero `[unverified]`.
- `design-token-delta.md` names every disagreeing token (or a `[blocked]` row).
- Flip-check finding written (either direction).
- **§0.2 answered, in writing, by the Team Lead.**

**DoD:** no version bump. Layout allow-list verified to cover the new script before push. The whole-tree bar.

---

### Phase 1 — Visual system + brand · owner: `frontend-coder` — **∥ Phase 2**

**Pre-build gate:** Phase 0's `design-token-delta.md`.

1. **Make dark the default** — it exists; it simply is not default. Retain light as `[data-theme="light"]`.
2. **Reconcile the gold** → commerce `#C9A249` (Δ ≤ 6/255). Measured **7.84:1 on `#14110d` — AAA**.
3. **Correct the token file's a11y comment** — it claims ~3.6:1; the real light-mode value is **3.12:1**
   (*worse*). Fix the number **and scope the rule to light mode, where it is real**.
4. **Re-derive "no gold body text" as an aesthetic rule** — in dark it clears AAA at 8.24:1. Record restraint
   as design judgment; **do not launder it as a contrast constraint it is not.**
5. **Self-host the fonts** — 2 woff2, ~69 KB (latin). Kills the `shared-tokens.css:10-13` ↔
   `dashboard.html:9-11` contradiction **and** the offline failure on the exact surface the redesign is for.
   **Independent of everything — ship it first.**
6. **Consume the bound design system** per Phase 0's delta.

**Acceptance:**
- **A contrast gate (the V5 method) covering BOTH themes** — dark pairs ≥ 4.5:1 text / ≥ 3:1 UI, **and the
  light-mode rule the plan affirms as real**. *Pass-2 fix (`red-team-2.md` §6.2): pass 1 asserted **dark
  only**, and B's gold ship-gate was dropped (correctly) — so **the one contrast rule this plan calls real —
  light-mode gold at 3.12:1 — was enforced by nothing**, while light remained a supported opt-out. The
  correction over-corrected. **If light mode is instead left unenforced, say so on the page and why.***
- **R9 — the Gate 51 acceptance is rewritten.** Plan A's *"all 12 green with zero fixture edits, the
  empirical proof of G1 6f"* is **struck**: G1 6f is false and Gate 51 binds a literal, whitespace-sensitive
  CSS rule. **Correct test: if Phase 1 touches the chrome-hide classes or reformats that rule, Gate 51 goes
  red and the fixture is updated in the same commit — that is the gate working, not a defect.** Any *other*
  gate red **is** a defect.
- Gate 13 regen-clean. Both surfaces render dark. Zero runtime third-party requests, asserted against the
  generated HTML.

**DoD:** minor bump in **both** manifests (CI fails on drift). Gates 13/35/51/132 + the 12. Font asset dir
added to `.repo-layout.json` **in this PR**. The whole-tree bar.

---

### Phase 2 — DOM fix · inline JSON islands · owner: `backend-coder` — **∥ Phase 1**

**Pre-build gates:**
- ✅ **The Learn/Gate-93 stepper contract — DECIDED AT G4b: (a) exempt Learn.** Satisfied *before* this phase
  exists, per the ordering constraint.
- 🔴 **§0.2 answered by the Team Lead** (Phase 0, item 10). **This phase is the long pole and it buys ~57%.
  Do not start it by default.**
- Phase 0's Gate 132 green at the re-derived baseline, both surfaces, must-fail red.
- Phase 0's exemption sweep: a verdict for **all 184**.
- Phase 0's R8 binding table: 12 of 12.
- **Phase 4a's route fixture + Gate 51-by-destination** (this phase's acceptance consumes them).

**Scope:**
- **Exempt (resident, full markup, `display:none` while inactive):** `learn` (Fork 1), `settings` (F3),
  **plus any panel Phase 0's sweep failed.**
- **Island:** `trees`, `commands`, and every panel that **passed** the sweep.

**Order: largest first, one commit each, ratchet both surfaces each time. Every commit regenerates** (the
regen precedence above).

**Acceptance, per commit:**
- Gate 132 ≤ the new per-surface budgets (**both** — F2); the per-panel payload budget holds. *(The payload
  half's teeth-proof lands here, at the first island — deferred from Phase 0.)*
- **Content counts asserted against the generator's own inventories, never prose:** `_decision_trees_inventory()`
  (**924**), `_best_practices_inventory()` (**2,216**), the commands glob (**525**).
- **Every committed `#/…` resolves** — Phase 4a's fixture, 100%.
- `__openPlugin` + `#dt-store` still render trees on plugin pages.
- **The exempt panels are provably untouched:** Gate 93 green with **zero** fixture edits; `#learn-search`
  filters live DOM exactly as today; the 144 posture radios bind at load and a round-trip Save is
  byte-identical for an unchanged posture. **This is F3's regression test and it is mandatory** — Gate 35 is
  structurally blind to it.
- The 12 render gates + Gates 13/35 green.

**DoD:** minor bump per commit (both manifests); `<noscript>` pointer to the source markdown; **Gate 13
extended to cover any generated JSON the islands introduce**; the whole-tree bar.

---

### Phase 3 — Virtualization · **conditional, expected** · owner: `backend-coder`

**Pre-build gate:** Phase 2 merged.
**Entry condition (derived):** any islanded panel's **payload budget** exceeds the per-panel bar the Team
Lead sets from Phase 0. **Expect `trees` to trigger.**

**Correcting plan A:** it labelled this *"droppable"* and wrote *"if Phase 2 hits budget, do not build this"*
— but Phase 2's budget is a **load** budget and says nothing about the **open-panel** budget that triggers
this phase. **A's own projection guaranteed the entry condition fired** (R13). **Expected work, on the
critical path.**

**Build:** render only expanded `<details>` cards.
**Acceptance:** the per-panel payload budget holds for every islanded panel; deep links into a non-rendered
card still resolve and scroll; the 12 gates + 13/35/51/132 green.
**DoD:** minor bump (both manifests); the whole-tree bar.

---

### Phase 4b — IA + search · owner: `frontend-coder`

**Pre-build gate:** Phase 2 merged (and Phase 3 if triggered). *Phase 4a already landed on day 0.*

**Scope — re-targeted where the gap is real (R7).** G4a falsified B's flagship justification: *"No search"*
is **false** (`learn-search` exists with 49 `data-search` blobs; the portal ships a **⌘K palette**,
hand-maintained in the shell — which is why three artifacts grepped one generator and wrongly concluded it
was absent). *"No faceting"* is **false for Learn** (10 collapsed `concept-cat` groups with count badges;
deliberate per CLAUDE.md v0.136.0). **B's proposed left rail is a description of the current Learn tab.**

**So: do not rebuild Learn.** The genuine gap: **nothing searches the 924 trees / 2,216 best-practices / 525
commands** — the exact content whose density is the problem, and the content Phase 2 just islanded.

1. **A data-side search matcher over the island payloads** — `JSON.parse` the island and query it as data
   (~150 lines vanilla JS, no npm dependency, no new file). **B's mechanism meeting A's own requirement**
   (A's test named ⌘K search into an unopened panel and A's phases never built it). **No `search-index.json`
   sidecar** — the payload is already in the document, so the zero-new-request property survives.
2. **List-level grouping + count badges (`Stat`) for `trees` and `commands` only.** Search resolves into the
   existing deep-link scheme — a shortcut into the IA, never a parallel one.
3. **New capability is additive only** (`#/learn/<id>?q=…`) — never a rename. `SECTION_ALIAS` / `DASH_OWNER`
   / `SECTION_TABS` **extended, never renamed.**
4. **Fail states, designed:** unknown `#/…`; live `/__*` 404 on static Pages; zero search results. Each
   explains **why** (static export, no backend) and **what still works**.

**Acceptance:** ranked results over trees/commands/best-practices with **no network round trip**; selecting a
result deep-links + scrolls, rendering the item if needed · **100% of Phase 4a's fixture resolves; zero
`#/…` 404s** · **`#learn-search` still works, untouched** · static-Pages smoke test (no `/__*` calls; the
**designed** empty state) · Gate 51 green by destination; the 12 + 13/35/132 green.
**DoD:** minor bump (both manifests); the whole-tree bar.

---

### Phase 5 — Posture-write integrity + `/__save` remediation · owner: `security-reviewer` (verdict) → `backend-coder` (build) — **∥ Phases 1-4**

**PRE-BUILD GATE — HARD:** a **binding `ravenclaude-core/security-reviewer` verdict on the `/__save`
remediation shape. Dispatch on day 0, in Phase 0.** Brief with: `serve-dashboards.py:19` (*"no auth, no rate
limiting, no audit"*), `:250-255` (*"a malicious **web page** the user is viewing"* + DNS-rebinding),
**`:1359-1371`** (absent `Origin` / `Sec-Fetch-Site` **PASS**; only `Host` fails closed), `:1482`/`:1505`
(the token endpoint sits behind the **same** `_local_request_ok()`), `:260-264` (the token rationale), and
the executed T1–T4 results.

**5a — The `/__save` header guard (R2).**
- **The defect of record is the comment at `:260-264`** — *"a scripted HTTP client that omits Origin (so the
  Origin guard passes) still has to present this token"* — **mechanically true and securely vacuous.**
  `_handle_csrf` gates the token endpoint on the **same** `_local_request_ok()` that `do_POST` uses, so the
  client that "omits Origin (so the Origin guard passes)" **passes the token endpoint for exactly the same
  reason and is handed the token.** The token is a real barrier to a cross-origin browser page (CORS blocks
  reading the response); **no barrier at all to a local scripted client.**
- **Minimum:** correct the comment to state the real, browser-only threat model.
- **If a stronger property is wanted:** require `Sec-Fetch-Site` to be **present** (fail-closed on absence)
  on state-changing POSTs — one line, with a real compatibility cost. **The reviewer owns that call.**
- **State honestly in the comment and the PR:** the POST was **never executed** — guard-denied, and the gate
  stopped rather than reshape it. Both gates observed open; a 200 on `/__save` was not observed.
  `network_write` panel-routing is a real but **unquantified** residual defense (LLM seat judgment, not a
  deterministic floor).
- **What this kills permanently:** plan-A §4.4's human/agent asymmetry. **"The human in the browser can
  always flip the switch; the agent in the shell can never write it" is not a property this architecture
  provides.** A read the CSRF machinery as an agent boundary; it is a **browser** boundary. **Dashboard-only
  is ergonomic, not a security control — do not write it down as a boundary.**
- **The design that cannot be reached (say it plainly, so nobody looks again):** a control both reachable by
  the human and unreachable by the agent **does not exist in this architecture**. The human's write path *is*
  `/__save`; the agent *is* a local process; the only discriminator is **client-asserted headers**, and
  omission is the passing case. Closing it needs an out-of-band channel the architecture lacks — **each a
  bigger build than the entire redesign.** A cost judgment, not an impossibility proof.

**5b — Posture-write integrity (F4 + 🔴 P3).**
- Add `stream_classify` + `stream_threshold` to `state` + `emitYaml` (**emit-when-non-default**, matching the
  existing convention so "absent ⇒ default" holds) + `applyGuardrailConfig`. Extend Gate 35's fixture.
- **🔴 SCOPE EXPANSION (P3) — Gate 35 must cover BOTH serializers.** Phase 6's acceptance requires all 4
  knobs round-trip, but **`guard-web-access`'s knob is not a comfort-posture key**: it lives in
  `.ravenclaude/web-access.yaml` (schema `allow:` / `deny:` only — `guard-web-access.sh:9-10`) and
  round-trips through a **separate serializer**, `emitWebAccessYaml()` (`:8782`) + `applyWebAccess()`
  (`:8789`), hydrated at `:8596`. **`emitYaml()` never touches it.** **Gate 35 structurally cannot see it** —
  G6-verified: its extract list (`:50-68`) is `CR_DEFAULT`/`TIER_DEFAULT`/`RUNAWAY_DEFAULT`/
  `PARALLELISM_DEFAULT`/`DOD_DEFAULT`/`freshTiers()`/`quoteYamlKey()`/`applyGuardrailConfig()`/`emitYaml()`,
  and its state model (`:83-95`) has **no web-access, and no path to it.** Its own header scopes it to *"the
  **comfort-posture** serializer."*
  **Without this expansion the test resolves three ways and two are bad:** (a) add a web-access key to
  `comfort-posture.yaml` → **the new top-level key §2.3 forbids** → Phase 6 breaches the ruling it exists to
  honor; (b) extend Gate 35 but leave it unscoped → **it lands nowhere**; (c) **ship "3 of 4 round-trip" and
  call it green** — the likely, vacuous path, and **§2.5's own diagnosis (*"the gate did not generalize; it
  enumerates"*) recurring inside the phase built to honor it.**
  ⇒ **"Make Gate 35 enumerate the posture keys the hooks actually read" explicitly includes
  `guard-web-access.sh` reading `web-access.yaml`. Gate 35 covers both serializers.** Then Phase 6's
  acceptance is true as written.
  *(Checked and falsified, recorded so it is not re-raised: `emitWebAccessYaml()` rebuilds wholesale from the
  DOM — F4's exact shape — **but `allow`/`deny` are the only keys in the schema and both are modelled. No
  data loss.** `red-team-2.md` §7.2.)*
- **Better, and the real fix:** generalize Gate 35 to enumerate hook-read keys rather than a hand-maintained
  list — **key #15 repeated key #4's bug; otherwise key #16 repeats it again.**

**Acceptance:** Gate 35 round-trips `stream_classify`/`stream_threshold` (emit-when-non-default +
hydrate-back), must-fail half strips one key → red · a posture carrying both survives a Save
**byte-identically** for untouched keys · **Gate 35 reaches `emitWebAccessYaml()`/`applyWebAccess()` and
round-trips `allow`/`deny`** (P3) · if generalized: adding a key to a hook's parser **without** adding it to
the dashboard fails the gate · the `/__save` change ships with a test that does **not** require executing a
disabling write.
**DoD:** minor bump (both manifests); **migration note required if the `/__save` guard tightens** (a
consumer's existing client could start getting 403s); Gates 13/35 + the 12; the whole-tree bar.

---

### Phase 6 — **`panel-pipeline` delta** *(re-targeted at pass 2 — NOT a new panel)* · owner: `frontend-coder`

**PRE-BUILD GATES — HARD:**
1. **Phase 5 merged.** This phase puts controls on the save path and **gives the user a new reason to Save.**
   Shipping over an `emitYaml` that silently destroys posture keys is exactly the failure this plan exists to
   prevent. **P3's Gate-35 expansion is included in that gate** — without it, this phase's own acceptance is
   unsatisfiable for `guard-web-access`.
2. **🔴 Matt answers §2.7's open product call: extend `panel-pipeline`, or replace it?** *(Default: extend.
   Replace must own the removal, the `#/pipeline` route, and the fixture.)*

**🔴 DO NOT BUILD A NEW PANEL.** `generate-dashboards.py:11406` already ships
`<section id="panel-pipeline" … aria-label="Guardrail pipeline">` on both surfaces (388 elements): a 15-stage
map across 4 lanes with **live ON/OFF badges**, **7** inline knob editors, and R10 scope text already correct
for `guard-destructive`. **A second view would ship two competing guardrail surfaces, drift-gated on only the
new one, the new one strictly narrower (4 knobs vs 7)** — R10's own defect, doubled, on a guardrail surface.

**The delta — four measured gaps (all G6-verified):**

1. **🔴 Fix the false label (P5).** `_PIPELINE_LANES:687-700` says `claim-grounding-lint` → `"set": "Active
   once command review is turned on."` **This is false** — `grep -c 'command_review\|thing'
   plugins/ravenclaude-core/hooks/claim-grounding-lint.sh` → **0**. Its real gate (`:47-62`) is (a) the file
   is under `knowledge/`/`docs/` and (b) a **bare file-presence** walk-up for `comfort-posture.yaml`.
   **A user reaches this today:** they turn command review **off**, read the label, and conclude the
   fact-check hook is off. **It still fires** — on every `knowledge/`/`docs/` write, whenever a posture file
   exists up-tree. **Replace with §2.3's wording: *"no knob — fires whenever a comfort-posture exists."***
   Apply the same to `delegation-nudge`.
2. **Add the two missing hooks to the lanes.** **`guard-web-access` is absent** (it appears only in
   `panel-web-access`'s copy at `:11320`/`:11327`). **`delegation-nudge` is absent from the generator
   entirely** (0 grep hits) — **the shipped map is already missing a hook. This is live drift today.**
3. **Build the drift gate — on `panel-pipeline`.** **No pipeline render gate exists** (verified: the 10
   `check-*render*.mjs` are bifrost, concern-stats, heimdall, mimir, nidhoggr, norns, sleipnir, stepper,
   streams, vidarr). Assert **`_PIPELINE_LANES` vs `hooks/hooks.json`**: adding a hook to `hooks.json`
   without adding a lane stage **fails**. **This gate would have caught both #1's label and #2's missing
   hook.** It is the right gate, aimed one panel to the left.
4. **Ground the lanes, or stop claiming they are grounded.** `_PIPELINE_LANES` is a hand-maintained Python
   literal; the **only** `hooks.json` mention in the entire generator is **the comment at `:473` claiming it
   is grounded there. It is not** (#2 is the proof). Either generate the lanes from `hooks.json` or **correct
   the comment** — the drift gate (#3) makes the first option safe.

**Surface the 4 knobs coherently (§2.3):** `guard-web-access`, `runaway-brake`, `dod-gate`,
`route-decision-review`. **3 of the 4 already have inline editors** — the delta is `guard-web-access`, whose
knob lives in a second file (P3; `ALLOWED_TARGETS` at `serve-dashboards.py:67-75` contains **both** files, so
it can save — and after Phase 5b it can also be **gated**). **NO new top-level posture key** (§2.3).

**Standing design constraint (R5), even with no new key:** any switch check in any hook sits **below** that
hook's own floor — at `thing-orchestrator.sh:229`, where the enabled gate already is, **never at `:100` or
"the top."** `:95-99` says so and **neither plan cited it.** *(It also forces a correction: plan-A §4.3 cited
`:100` as its **model** — precisely the placement that removes the floors — while §4.5 Option B promised to
keep them. **A's mechanism contradicted A's own semantics.**)*

**Acceptance:**
- **The drift gate is green on `panel-pipeline`**, and its **must-fail half** (add a hook to `hooks.json`
  without a lane stage) is **red**. *This is the phase's reason to exist.*
- **`claim-grounding-lint`'s and `delegation-nudge`'s labels match their code** — asserted against the hooks,
  not hand-checked. **Exactly one label per hook exists in the product** (no second view — the P2 regression
  test).
- `guard-web-access` + `delegation-nudge` appear in the lanes.
- Each of the **4 knobs** round-trips (Gate 35 extended, **both serializers** — P3).
- Static Pages renders the panel **read-only with an explanation**, not a broken control.
- **A posture with all 4 knobs non-default survives a Save byte-identically for every unmodelled key** (the
  F4 regression, enforced upstream by Phase 5b).
- The 12 gates + Gates 13/35/132 green.

**DoD:** minor bump (both manifests); **migration note** if any consumer-visible posture behavior changes;
the whole-tree bar. **If this phase adds/removes any skill/agent/artifact whose count is encoded in
marketplace prose, regenerate the counts/artifacts in this phase** — skipping this caused the 2026-06-03
three-PR hotfix chain (PRs #244–#247). **This phase is the live risk for that rule.**

---

### Phase 7 — Ship · owner: `team-lead`

**Pre-build gate:** Phases 1, 2, 4a, 4b, 5, 6 merged (3 if triggered).

`scripts/audit-gates.sh` → 0 · `npx --yes prettier@3.9.4 --check .` → 0 · `ruff check .` → 0 · the layout
verification snippet · `scripts/check-checkout-fresh.sh`. **`landing=pr`** → the `forge/dashboard-redesign`
PR, carrying §6's `.repo-layout.json` rationale **and §0.1's residue statement**.

---

## 8. Tiebreak verdicts + red-team mitigations → owning phase

| Ruling / mitigation | Source | Owning phase |
|---|---|---|
| **Fork 1 — exempt Learn** (forfeit 19,702; zero code risk vs an open-ended rewrite of an already-`exit=1` mechanism in a harness with a documented prior regression, v0.118/0.119) | `tiebreaks-learn.md` | **Decided at G4b (pre-Phase-2).** Enforced in **Phase 2**; flip condition checked finding-only in **Phase 0** |
| **Fork 1 — log (b) as an explicitly-scoped follow-on** | `tiebreaks-learn.md` | **§11.2 — now re-priced at 79% of the residue (P1)** |
| **Fork 1 — if (b) is adopted:** Gate 93 asserts **both** representations; the must-fail half must exercise the **payload-parsing path**; the contract must assert `#learn-search` resolves against the **rendered** subset | `tiebreaks-learn.md` | **§11.2 (follow-up contract)** |
| **Fork 2 — ~~measured floor = shell + active tab~~** | `tiebreaks-learn.md` | **🔴 AMENDED (P1) — Phase 0 emits the *exempted* floor: `shell + active tab + Σ(exempt)`. Fork 2's ~429 is unreachable by ~24,200 under §2.2's exemptions, which were adopted *after* that tiebreak.** |
| **Fork 2 — do not split A's and B's numbers** | `tiebreaks-learn.md` | **Phase 0** — the budget is a measurement, never a compromise |
| **Fork 2 (security) — no master switch; largest safe subset as a *view*** | `tiebreaks-security.md` | **Phase 6 — as a delta on the view that already ships (P2)** |
| **Fork 2 — the safety floor, never switchable** | `tiebreaks-security.md` | **Phase 6** (standing constraint) + **§1.4** |
| **Fork 2 — placement at `:229`, never `:100`** | `tiebreaks-security.md` | **Phase 6** (standing constraint) |
| **Fork 2 — "dashboard-only" is ergonomic, not a boundary** | `tiebreaks-security.md` | **Phase 5a** |
| **Fork 2 — the `/__save` guard as a live bug, medium** | `tiebreaks-security.md` §6 | **Phase 5a** |
| **Fork 2 — A's V3 confirmed** (a new top-level key is covered by neither trigger) | `tiebreaks-security.md` §3 | **Honored by shipping no new key (Phase 6)** |
| **Fork 2 — correction to G4a:** *"neither trigger matches an HTTP post"* is **wrong** — `/__save`'s `ALLOWED_TARGETS` contract **forces the literal filename into the POST body**, so a `curl` POST matches `:187`. G4a's conclusion survives via a **pre-written script**, which never puts the filename in the command string | `tiebreaks-security.md` §3 | **Phase 5a** (brief the reviewer with the correct mechanism) |
| **Fork 2 — correction to G4a:** *"a plain READ is over-blocked"* **overshoots** — only a read whose **own pattern** carries the `key:` write-shape trips it | `tiebreaks-security.md` §3.1 | **§11.3** |
| **Fork 2 — correction to A's V4:** `command_review.enabled` **does exist**, is engine-honored, is *"a top-level circuit-breaker only"*, and **is set in this repo's own posture**. A observed one posture file (home, where absent ⇒ default `True`) and generalized to the architecture; the critic endorsed it. **A's Option B semantics are correct AND already built** | `tiebreaks-security.md` §4, §8.3 | **Recorded — it is why Phase 6 builds no new tribunal key** |
| **F1 — `html.parser` in the gate; re-derive; must-fail `count−1`; baseline 57,330** | `red-team.md` | **Phase 0** — *scope narrowed by pass 2 (§2.1)* |
| **F2 — per-surface budgets + tables** | `red-team.md` | **Phase 0** (built) / **Phase 2** (enforced) |
| **F3(a) — exempt `settings`; sweep the rest** | `red-team.md` | **Phase 0** (sweep) / **Phase 2** (exempt) — **its price now in §0.1** |
| **F4 — stream keys into `emitYaml`; generalize Gate 35** | `red-team.md` | **Phase 5b** |
| **F5 — 4 knobs; label 2 "no knob"; no new keys** | `red-team.md` | **Phase 6** |
| **F6 — `forbidden_globs`** | `red-team.md` | **DONE (§6)** |
| **🔴 P1 — residue in §0/§12; exempted floor; re-price §11.2; derived target** | `red-team-2.md` | **§0.1/§0.2, Phase 0 item 4a, §11.2, §12.2a** |
| **🔴 P2 — re-target Phase 6 as a delta on `panel-pipeline`** | `red-team-2.md` | **§2.7, Phase 6** |
| **P3 — Gate 35 covers both serializers** | `red-team-2.md` | **Phase 5b** |
| **P4 — regen precedence; R14 rescoped; §3's disjointness corrected** | `red-team-2.md` | **§7 preamble, §3, §2.8** |
| **P5 — fix `claim-grounding-lint`'s shipped label** | `red-team-2.md` | **Phase 6, item 1** |
| **§6.1 — split Phase 4a (routes, day 0) from 4b** | `red-team-2.md` | **§3 DAG, Phase 4a — and this row is the one §8 previously lacked** |
| **§6.2 — the light-mode contrast rule has no gate** | `red-team-2.md` | **Phase 1 acceptance** |
| **§6.3 — 184 panels, not 180; enumerate from the artifact** | `red-team-2.md` | **Phase 0, item 5** |
| **§7.5 — the payload teeth-proof is deferred to Phase 2's first island** | `red-team-2.md` | **Phase 0, item 3** |
| **R8 — sweep the render gates** | `critic-brief.md` | **Phase 0** |
| **R9 — Gate 51's CSS binding; rewrite "zero fixture edits"** | `critic-brief.md` | **Phase 1** |
| **R10 — scope text on the control** | `critic-brief.md` | **Phase 6** |
| **R13 — virtualization is not droppable** | `critic-brief.md` / `gap-delta.md` | **Phase 3** |
| **R15 — `render_fragment()`'s sole-caller** | `critic-brief.md` | **Phase 0** |
| **Gate 51 extension by destination** | `red-team-2.md` §6.1 | **Phase 4a** *(previously unassigned)* |

---

## 9. Unverified claims → the concrete step that settles each

**No dangling `[unverified — training knowledge]`.**

| Claim | Marker | Settling step |
|---|---|---|
| **1b** — Astro's bundled output dir is `_astro/` | `[unverified — training knowledge]` | **RETIRED** — Astro rejected (§1.1) on the cost comparison, not on this. **Moot regardless:** `.nojekyll` already exists at the repo root (0 bytes) — the gotcha is pre-solved. *If ever needed:* `npm create astro@latest` + `npm run build`, `ls dist/`. |
| **3b** — per-`client:*` hydration costs | `[unverified — training knowledge]` | **RETIRED** — Astro-only. |
| **4d** — "line length is irrelevant to HTML parsing" | `[unverified — training knowledge]` | **NOT LOAD-BEARING — no work scheduled either way.** Phase 2 dissolves the 2.3 MB line as a side effect. **Gate:** if any future phase proposes minification *for performance*, settle it first — WHATWG HTML §13.2, or an A/B parse benchmark. Until then the long line is a **tooling** cost, which is real and must not be counted as a performance claim. |
| **5c** — the Google-Fonts egress / GDPR angle | `[unverified — training knowledge]` | **MOOT BY CONSTRUCTION** — Phase 1 self-hosts regardless, justified by the *verified* halves (the `shared-tokens.css:10-13` contradiction + the offline failure). *If it becomes load-bearing:* `security-reviewer`. |
| **6g** — minifier identifier-renaming | `[unverified — training knowledge]` | **RETIRED** — Astro-only. |
| **6h** — `is:inline` emits a bare `<script>` | Was the highest-leverage gap | **SETTLED — the repro was run**; G4a re-verified the ruling against it. **Its thumb-on-the-scale sentence is struck** (§1.1). |
| **8e** — the self-disable regex misses a bare `thing:` key | Was Speculation | **SETTLED — falsified.** A's V2 found the second regex at `:187`; Fork 2 §3 confirmed by executed regex evaluation. |
| **10c** — the gold delta is "visually near-indistinguishable" | Speculation (no ΔE) | **Phase 1 — the designer rules.** The *contrast* half is settled (7.84:1 AAA); only the aesthetic judgment is open. |
| **11b** — `render_fragment()` has one caller | Medium (zsh-mangled globs) | **Phase 0, item 8** — quoted globs. **B kept it open and B is right.** |
| **12 render gates' binding shapes** (7 unread) | `[unverified]` | **Phase 0, item 7** — read all 12; zero `[unverified]` rows. **2 of 5 checked bind markup/CSS.** |
| **Counts 924 / 2,216 / 525** | Both plans gate on them | **Phase 2 acceptance** — assert against the generator's own inventories, never prose. |
| **Fonts: 2 woff2, ~69 KB latin** | Not checked by G4a | **Phase 1** — measured at self-host time; not load-bearing. |
| **Design-system token values** | Neither panel read them | **Phase 0, item 9** — or a `[blocked]` row with the named route, never a silent skip. |
| **Live hosted `content-length`** | `[unverified]` | **NOT LOAD-BEARING** — order confirmed; no wire budget in v1 (§11.4). |
| **`/__save` POST executed end-to-end (T5)** | **Inferred, not executed** | **Phase 5a — say so in the comment and the PR.** Both gates driven open (T1–T4, executed); a 200 on `/__save` never observed. `_local_request_ok()` is **one function** shared by both endpoints; `do_POST:1505-1510` calls exactly it and `_csrf_ok()`, and nothing else. **Control flow unambiguous; "confirmed in code" ≠ "executed."** |
| **F3's binds are non-idempotent under a later `activate()`** | Read, not browser-driven | **Moot — `settings` is exempt**, so the mode never fires. The `:13261` **state-divergence half survives regardless** (that read runs once at load). Exempting is cheaper than settling. |
| **The other panels have no load-time DOM binds** | **The assertion that got `settings` wrong covered all 180 — and there are 184** | **Phase 0, item 5** — a verdict for all 184, enumerated **from the artifact**. |
| **`.ravenclaude/web-access.yaml` does not exist** though the G1 brief said to honor it | **Open since G1, thrice-flagged, never answered** | **🔴 STILL ESCALATED — the Team Lead answers. Do NOT create the file.** It is `guard-web-access`'s knob and Phase 6 surfaces it. **Either the brief was stale or its absence is a finding.** An agent must not create a guardrail config file to make its own view render. **P3 sharpens the consequence:** the knob is not a comfort-posture key but a separate file with a separate serializer, so Phase 5b must gate it and Phase 6 must render its real state — **including "no file present"** — honestly. **Absent ⇒ render the true state; never fabricate one.** |

---

## 10. Content preservation, per phase

| Phase | 525 commands | 924 trees | 2,216 best-practices | 48 Learn concepts | 144 posture radios |
|---|---|---|---|---|---|
| 0 / 4a | untouched | untouched | untouched | untouched | untouched |
| 1 | restyled only — **no markup change** | same | same | same | same |
| 2 | **JSON island** — same bytes, same `activate()`, same deep link | **island**, plus `#dt-store` + `__openPlugin` asserted | **island** | **EXEMPT — untouched** (Fork 1) | **EXEMPT — untouched** (F3) |
| 3 | virtualized render; payload unchanged | same | same | untouched | untouched |
| 4b | re-homed by group; every legacy route preserved | same | same | **untouched — do not rebuild Learn** (R7) | untouched |
| 5 | untouched | untouched | untouched | untouched | **integrity restored** (F4/P3) |
| 6 | untouched | untouched | untouched | untouched | untouched — **labels corrected** (P5) |

**Nothing is dropped. No content is "demonstrably irrelevant."**

**The reachability argument, corrected.** Plan A's §5.2 claimed islands *"preserve that exact reachability
contract byte-for-byte"* because inactive panels are already `display:none`. **That holds for *humans*
(Ctrl-F, the a11y tree) and fails for the *DOM query* — and it was wrong three times over**: the stepper
init, node_links, and `#learn-search` all query live DOM. A hidden panel keeps nodes **queryable**; a JSON
island does not. **This plan does not rely on that argument. It exempts every panel with a load-time DOM bind
instead** — which is why Learn and `settings` are exempt, why the sweep is mandatory, and **why the residue
is 97.2% exempt mass (§0.1). The exemption is not a footnote; it is the outcome.**

---

## 11. Named follow-up candidates — **out of scope, with their trade-offs**

### 11.1 `enforce-layout.sh` has no gitignore exemption (the class behind F6)
The hook is **strictly stricter than the CI backstop it mirrors**, permanently, for every gitignored path.
§6's edit fixes the **instance**, not the **class** — the next gitignored convention hits it identically.
**Trade-off:** **consumer-facing hook behavior** — it changes what every installed plugin denies. Needs its
own design pass and its own `audit-gates.sh` fixtures (a gitignored-path must-allow **and** a tracked-path
must-deny). **Not in scope.** *If it lands, F6 and the asymmetry die together — that is the class fix.*

### 11.2 🔴 The Gate-93 (b) path — convert Learn · **re-priced at pass 2; this is §0.2's other half**
Fork 1's declined option, logged **explicitly** rather than silently dropped: rewrite Gate 93 against the
island payload **and** re-point `initConceptSteppers()`, node_links, and `#learn-search` to on-activate.

**🔴 THE PRICE, RE-FRAMED (P1) — this is the correction that matters:** pass 1 priced it as *"~19,702 nodes
(**34% of the baseline**)"*, framed against 57,330, **where it reads optional**. **Framed against the residue
it actually competes with, Learn is 79.1% of what remains after the entire critical path** (§0.1). **The work
scoped OUT is the work that resolves the defect the plan exists to fix.** *(The 19,702 figure itself is
**confirmed**, not retired — both counters agree to the digit, §2.1.)*

**Trade-off, honestly:** buys the single largest remaining block at the cost of an open-ended rewrite in the
repo's deepest harness — the same cost class both plans cited as decisive against Astro-bundled, imported
back deliberately for one panel, in a region with a **documented prior regression** (v0.118/0.119 broke
node_links by changing exactly this render shape). **Its own PR, its own Gate-93-v2 fixture with a must-fail
half that exercises the payload-parsing path, its own risk review.** Contract in §8.
**Its cost may collapse if Phase 0's flip check finds the JSON-escaping fix is a one-line regex loosening.**
**→ §0.2. A Team Lead call, not an agent's.**
*Would also need:* the headless/JSDOM rendered-DOM meter (§4.4) — which would resolve F1 and F3(b) together.
**A coherent synthesis and worth costing, but materially larger than this build.**

### 11.3 `guard-destructive.sh`'s false-positive rate — **the highest-value guardrail work in this repo**
Five consecutive gates blocked on read-only work (§5.1). The narrow, sharp defect: **the hook cannot
distinguish a command from a command *passed as an argument to a read-only tool*.** Pair with the accurate
concerns-catalog defect: `concerns-catalog.md:189-191` claims *"a plain READ of the file (grep/cat) is not
over-blocked"* — **true for most reads, false for the subset whose own search pattern carries the `key:`
write-shape** (`grep -n "command_review:"` blocked; `grep -n "command_review"` passes). *G4a's blanket
falsification overshot; this is the accurate defect — and G5-pass-2 and G6 both drew zero false positives,
which corroborates the narrowness rather than the breadth (§5.1).*
**Trade-off:** every loosening of a floor hook is a security change and `guard-destructive.sh` is **floor
end-to-end** — its false positives are the price of having no seam, and **that trade is currently correct**.
Needs a binding `security-reviewer` verdict and `audit-gates.sh` fixtures. **The irony worth recording:** this
trigger **over-blocks reads of the posture file while missing writes to it via HTTP** (Phase 5a).

### 11.4 The portal's wire cost (R11)
`index.html` is **10.28 MB raw / 1.73 MB gzip** — **65% heavier on the wire** than the surface both plans
reasoned about, and it is the actual front door and the surface `audit-gates.sh` tests. **Accepted for v1
with the reason stated:** the adopted mechanism keeps the bytes in the document **by design** (that is what
buys zero new requests, zero cache-busting, zero static/served divergence), so an island-based plan **cannot
express a wire budget**. Gate 132 binds both surfaces for **nodes**, the measured bottleneck. **Trade-off if
reopened:** sidecar files retire this, at the cost of §4.2's whole column.

### 11.5 The run substrate is not integrity-protected against the agent
Per §6's waiver. **Heimdall and Víðarr present the hook-event log to the user as an audit trail.** The
`forbidden_globs` entry closes the *sanctioned tool path*; a `>` shell redirect still writes unpoliced.
**An audit log the audited party can rewrite should not be labelled an audit log without a caveat.**

---

## 12. Stop condition — replaces scope §7

scope §7 is unusable as written: *"materially under 7.8 MB"* measures **the wrong thing** (the wire cost is
~1.05 MB gzip and no adopted decision moves it), and *"a single documented control"* presumes exposing a
control that **does not exist**, **should not be built** (§1.4), and **whose aggregated view already ships**
(§2.7).

**Ship when all eleven hold, checked in one run. Every line is a command that exits 0/1.**

1. `scripts/audit-gates.sh` → exit 0 — **all gates**, incl. the 12 render + 13 + 35 + 51 + 93 + 132 + the new
   pipeline drift gate.
2. **Gate 132 green on BOTH surfaces** against their **own** re-derived budgets (F2), under **`html.parser`**
   (F1), with a **`count−1`** must-fail half red on each.
   - **2a. 🔴 THE DERIVED TARGET (P1) — a budget is not a goal.** The load residue on each surface is
     **≤ that surface's exempted floor × (1 + margin)**, where the exempted floor is
     `shell + active tab + Σ(exempt panels)` **as Phase 0 emits it** (§7 Phase 0, item 4a), and the margin is
     set by the Team Lead in Phase 0. **Without this, §12.2 is a ratchet against a self-set bar and cannot
     fail on achieving little.** **And the plan must state, in §0.1 and in the PR, what the residue *is* in
     multiples of 1,400 — the target is "we hit the floor our exemptions allow," NOT "we cleared Lighthouse."**
3. **Per-panel payload budget** holds for every islanded panel (§4.4).
4. **Contrast gate — both themes** (§6.2): dark pairs ≥ 4.5:1 text / ≥ 3:1 UI, **and the light-mode rule the
   plan affirms as real** — or a written statement that light is unenforced and why.
5. **Zero `#/…` 404s** — Phase 4a's fixture, 100%.
6. **Counts intact — 525 / 924 / 2,216** — asserted against the generator's own inventories.
7. **Zero runtime third-party requests** (fonts self-hosted) — asserted against the generated HTML.
8. **The exempt panels are provably intact:** Gate 93 green with zero fixture edits; `#learn-search` filters
   live DOM as today; the 144 posture radios bind at load and round-trip a Save byte-identically.
9. **Posture-write integrity:** a posture carrying `stream_classify` / `stream_threshold` survives a Save
   byte-identically for every unmodelled key (F4), **and Gate 35 reaches both serializers** (P3).
10. **Exactly one guardrail view exists** (P2), its labels match the hooks (P5), and the drift gate's
    must-fail half is red.
11. `prettier --check .` + `ruff check .` → exit 0.

**Explicitly NOT ship conditions, and why — so nobody re-adds them:**
- ~~"initial DOM ≤ 12,000 nodes"~~ — **scope-derived, not a floor**, and derived by a **broken parser**.
- ~~"< 2,000 nodes"~~ — **unreachable by any mechanism that does not delete content**; misses by 8,367+ even
  before the exemptions.
- ~~"no single panel > 8,000 nodes when active"~~ — replaced by item 3, which is **CI-safe and measurable**;
  the 8,000 literal was never derived.
- ~~"gold never appears as body text in either theme"~~ — **forbids an AAA (8.24:1) color and routes to a
  6.12:1 one** (§1.3).
- ~~"a wire/payload budget"~~ — **§11.4**, recorded with its reason.
- ~~"the DOM is under Lighthouse's 1,400-node threshold"~~ — **🔴 NOT ACHIEVED AND NOT ACHIEVABLE IN THIS
  SCOPE.** The build lands at **~17.8×** (§0.1). **This is the plan's most important honest statement and it
  must appear in the PR.** Closing the rest is §11.2 → §0.2.

**The bound on "iterate until perfect":** *perfect* is 1–11. **Aesthetic iteration is capped at three rounds
against the design project, and a round counts only if it produces a named token/component delta.** A fourth
round is a **scope decision for the Team Lead, not more iteration.** Anything 1–11 does not cover is **v2**.

---

## 13. Definition of Done — repo conventions (`AGENTS.md`), every phase

1. **Per-phase acceptance tests** — that phase's block in §7, **all green, re-run explicitly**, never
   inferred from a prior phase's pass.
2. **Semver bumped in BOTH** `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and**
   `.claude-plugin/marketplace.json` — **CI fails on drift.** Currently **0.199.1** in both (G6-verified).
3. **Layout allow-list discipline** — any new directory's glob lands in `.repo-layout.json` **in the same PR
   as its first file**, never deferred (per PR #32: the local hook fires on Write/Edit, but `mkdir -p` + a
   batch write surfaces the failure in CI, not locally). Run the verification snippet before every push.
4. **`npx --yes prettier@3.9.4 --write .`** before commit; `--check .` → exit 0. **Whole-tree** — a single
   mis-formatted file in `main` blocks every subsequent PR, including markdown-only ones.
5. **`ruff check .`** → exit 0. Same whole-tree discipline.
6. **`scripts/audit-gates.sh`** → exit 0. Required reading before adding/changing any CI step:
   `docs/best-practices/ci-gate-audit.md`. **A Gate 10 skip is not a pass.**
7. **`scripts/check-checkout-fresh.sh`** — never trust a test run against a stale checkout.
8. **🔴 If any phase adds or removes a skill, agent, or other artifact whose count is encoded in marketplace
   prose, that phase's DoD MUST include regenerating the counts/artifacts.** Skipping this caused the
   2026-06-03 three-PR hotfix chain (PRs #244–#247). **Phase 6 is the live risk.**
9. **Migration note required** for anything that could break a consumer on `/plugin marketplace update` —
   **Phase 5** if the `/__save` guard tightens, **Phase 6** if any consumer-visible posture behavior changes.
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
    is the highest slot currently in the harness `[G8-verified]`.**
11. **Landing:** `landing=pr` — forced by §6's `.repo-layout.json` `allowed_globs` edit (an engineering
    pre-commitment on a boundary file). **The PR body carries §6's rationale AND §0.1's residue statement.**

---

## 14. Conduct record for this gate

No guard denied any operation during G6 (either pass). **No content was obfuscated, split, or encoded to pass
a classifier at any point.** `.repo-layout.json`, the comfort-posture, and every guard config were left
exactly as this gate found them — the one edit in this run (`.ravenclaude/runs/**` + its `forbidden_globs`)
was **human-approved before G5 pass 1** and is recorded as completed work in §6, not as this gate's doing.
This gate's writes land inside the FORGE run dir, which that pre-existing glob permits.

**Pass-2 verification note:** every pass-2 finding was **independently re-measured at G6** rather than
accepted on report — the residue arithmetic (§0.1, agreeing within ~1.8% and exactly on every ratio), the
184-panel count, `panel-pipeline`'s existence and size, `claim-grounding-lint`'s false label and the hook's
zero `command_review` hits, `delegation-nudge`'s total absence from the generator, Gate 35's extract list and
state model, Gate 13's `--check` branch, and `emitYaml`/`applyGuardrailConfig`'s generator line numbers —
**the last of which falsified a disjointness claim in this plan's own §3** (§2.8). Where G6's measurement and
`red-team-2.md`'s differ, **both are cited and Phase 0 arbitrates** — no number is adopted as a budget here.
