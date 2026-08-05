# FORGE G6 — Authoritative plan: `/wireframe` (wireframe-studio)

> This is the single synthesized plan the orchestrator reads in full. It merges G0 scope, the G1
> claims table, panels A/B, the gap-delta, the correlated-error critic, the **binding** tiebreaks
> (including the owner ruling + the G5 BLOCKER-1 resolution), and the red-team. Where any input
> conflicts with `tiebreaks.md`, **`tiebreaks.md` wins** — its rulings are reflected below with no
> dangling conflict. This-session repo facts were re-verified at synthesis (see inline groundings).

---

## 1. Executive summary

**What v1 is.** A **main-session `/wireframe` skill** in `ravenclaude-core` (no new agent) that turns a
plain-language description of *anything* — a web page, an app/software screen, a dashboard, or a simple
flow/diagram — into:

1. a **schema-validated wireframe MODEL** (one JSON document; the contract every surface consumes),
2. a **high-fidelity, self-contained HTML Artifact** that the **executing Claude authors free-hand**
   from that model, applying the `artifact-design` skill (CE-1: *never* a deterministic Python script),
3. a **Mermaid flowchart** for the `flow` artifact type (the one place Mermaid is the right output), and
4. a **minimal, stdlib-only skill-scoped helper `wireframe_lint.py`** — a hand-rolled structural
   **validator** + **context-aware sanitizers** + a **deterministic Mermaid emitter** — which a new
   **must-fail audit-gate** exercises against **committed fixtures**.

The model persists to `.ravenclaude/runs/wireframe/<slug>/model.json` so iteration ("make the header
blue", "turn this into a dashboard") edits one source of truth and re-renders only the surface in view.

**The explicit v1 / v1.1 line (owner-ruled).**

| In v1 (this build) | Deferred to v1.1 |
|---|---|
| Wireframe MODEL + top-level JSON Schema | **ASCII / box-drawing renderer** |
| Claude-authored high-fi HTML Artifact (via `artifact-design`) | **SVG renderer** (+ the shared box-packer / `_layout.py` coordinate engine + AABB self-checks) |
| **Mermaid** flowchart for `flow` type (deterministic emitter in `wireframe_lint.py`) | **Full two-level named-archetype library** + golden-set scoring |
| `wireframe_lint.py` (validator + sanitizers + Mermaid emitter) | **Multi-screen flow extension** (B's `screens[] + flow_edges[]` app-nav map) |
| Lean starter-skeleton set (one per artifact type) | Python-rendered deterministic surfaces + `cross-platform-determinism` for ASCII/SVG snapshots |

v1.1 is **not** promised as a fixed follow-on; it is the honest destination of the owner's four-format
intent (scope decision 2), sequenced behind demonstrated demand. Nothing in the v1 architecture blocks
it — the schema, sanitizers, and Mermaid emitter are the reusable substrate.

---

## 2. Home placement — **owner's G8 ratification point**

**Ship:** `plugins/ravenclaude-core/skills/wireframe/SKILL.md` as a **main-session skill** in
`ravenclaude-core`, **no new agent**. Both panels converged on this independently (gap-delta §"strong
convergence"), the critic kept it ("well-grounded and safe — keep it"), and the owner already leaned
this way at G0 (scope decision 3 tagged home as a genuine-preference call). **This is the owner's G8
ratification point** — the one call surfaced for explicit sign-off at exit.

**Why skill-in-core beats the alternatives** (full trade-off table in §7):
- **Domain-neutral → core** (house rule 1): "wireframe anything" serves any consumer; direct precedent
  is `brand-extraction`, a domain-neutral schema+stdlib-engine capability that shipped as a **core
  skill**, not a plugin. A RavenPower creative-suite plugin would hide a neutral tool behind one
  company's brand.
- **Zero agent-description-budget cost:** skills load on invocation; only agent `name`+`description`
  count against the ~15K orchestrator budget (claims #6/#12). A new agent would spend permanent budget
  for a capability `designer` + a skill already covers.
- **No catalog weight:** no 169th `marketplace.json` entry (168 verified this session).
- **No layout/migration risk:** every path already matches `.repo-layout.json` (verified — §8).

**Main-session, not a subagent pointer (RT-4, binding).** `designer`'s frontmatter `tools:` is
`Read, Edit, Write, Grep, Glob, Bash, WebFetch, WebSearch` — **no Artifact tool** (verified this
session). A `designer` *subagent* therefore **cannot publish an HTML Artifact**; only the main-session
Claude can. So `/wireframe` is invoked **from the main session**, and the reconciliation with `designer`
is **reciprocal**, not a one-way subagent pointer:

- **`designer.md` gains a reciprocal "when to use which" note** (RT-4): *`designer` = full design spec +
  accessibility audit + handoff to `frontend-coder`; `/wireframe` (main session) = fast description →
  validated model → high-fi HTML Artifact + Mermaid-for-flows.* `designer` may produce the model/spec
  and hand the publish **up** to the main session.
- **`SKILL.md` carries the mirror note**, so the two surfaces are **delimited, not parallel** — closing
  the house-rule-4 drift risk (R9) the marketplace warns against. This is a `designer.md` prose edit
  only: **no** `description`/`tools`/scenario change, so `check-frontmatter.py` is untouched.

---

## 3. Architecture

### 3.1 The wireframe MODEL (the contract — one shape, authored once)

One JSON document is the artifact of the single genuinely-judged step (description → model, claims
#6/#9). Every surface consumes exactly this shape. It lives at top-level
**`schemas/wireframe-model.schema.json`** (mirroring the existing `schemas/brand-kit.schema.json`
sibling precedent — gap-delta #9 ruling, tiebreak #9). Schema shape (adopting A's superset per tiebreaks
#2/#3):

```
Wireframe
├─ meta        { title,
│                type: page | app-screen | dashboard | flow,      // selects the starter skeleton
│                viewport: desktop | mobile | tablet | responsive, // renderers genuinely need this
│                theme: auto | light | dark,
│                fidelity: high | structural,
│                model_version: "1",                              // RT-6 seam: enables v1.1 migrate
│                brand?: { palette[], type_scale, radius } }       // forward-hook: brand-extraction compose
└─ regions[]                                                       // top-level layout areas
   Region { role: header|nav|sidebar|main|aside|footer|hero|toolbar|filter-bar|canvas|card-grid|modal,
            layout: stack | row | columns:N | grid:RxC | split,
            emphasis: primary | secondary | tertiary,             // designer info-hierarchy, machine-readable
            sections[] }
      Section { kind, heading?, emphasis, content_slots[], components[] }
         Slot      { text | image-box | data-shape }              // realistic placeholder content
         Component { type: button|input|form|card|table|chart|kpi-stat|list|tabs|breadcrumb|search|
                           avatar|badge|toggle|stepper|nav-item|node|edge,
                     props: { label, placeholder_text, variant, state, size, icon } }
```

**Flow / diagram is canonically A's node/edge-on-one-canvas** (tiebreak gap #1, A-canonical for v1):
a `flow` is a single `canvas` region whose sections carry `node` + `edge` components — the literal
process/decision flowchart that maps directly to a Mermaid `flowchart`. **B's multi-screen
`screens[] + flow_edges[]` app-navigation map is recorded as a v1.1 optional extension** of the
app-screen type — not canonical v1, not merged by omission.

`meta.emphasis` on regions/sections wires `designer`'s primary/secondary/tertiary information-hierarchy
method into the model so the HTML author (and, in v1.1, the coordinate renderers) can key off it
mechanically instead of re-deriving from component order (tiebreak #2). `meta.model_version` is seeded
now so v1.1 can add a one-time validate-and-migrate pass over persisted models (RT-6 mitigation).

### 3.2 WHO renders WHAT — the split that resolves CE-1

| Surface | Rendered by | Fidelity | Determinism |
|---|---|---|---|
| **HTML Artifact** (primary) | **The executing Claude, free-hand**, applying `artifact-design` | **High** (near a comp) | Non-deterministic by design; **refereed** (not gated) |
| **Mermaid flowchart** (`flow` type) | **`wireframe_lint.py`** deterministic emitter | Structural | Deterministic; **gated** on a golden `.mmd` |
| **Model validation** | **`wireframe_lint.py`** hand-rolled structural validator | — | Deterministic; **gated** on committed fixtures |
| **Text/CSS/URI/Mermaid-label sanitizing** | **`wireframe_lint.py`** context-aware sanitizers | — | Deterministic; **gated** on malicious-input fixtures |

**Why the split.** CE-1 established that a deterministic Python script *cannot* produce a high-fi comp
(the design judgment lives in Claude reading `artifact-design`, not in a fixed renderer walking a closed
vocabulary) and *cannot* "load a skill." So high-fi HTML is **Claude-authored**. But CE-2/CE-5's "v1
needs no interpreter at all" was too aggressive (G5 BLOCKER-1): it removed the only code path that could
mechanically enforce the **schema-validation** claim and the **CE-4 context-aware escaping safety floor**
on a *published, shareable* Artifact. The G5 resolution **re-admits a minimal stdlib helper**
`wireframe_lint.py` (NOT an HTML renderer — the high-fi HTML stays Claude-authored). It provides:

- **(a) a hand-rolled structural validator** of the model against `schemas/wireframe-model.schema.json`
  — **no `jsonschema` dependency** (verified absent this session: `python3 -c "import jsonschema"` →
  `ModuleNotFoundError`; CI installs it for `validate-schemas.yml` but the consumer path must not
  assume it). Mirrors the `extract_brand.py` stdlib-only precedent.
- **(b) context-aware sanitizers** (CE-4, binding): `html_text` (HTML-entity escape); `css_value`
  (allowlist → validated `#hex` / `rgb()` / `hsl()` / named keyword only, reject everything else —
  blocks `url()` external-fetch / CSP break); `uri_scheme` (allowlist `http` / `https` / `mailto` /
  `tel` — blocks `javascript:` and `data:`); `mermaid_label` (quote + entity-escape `"`/`#`, strip
  `[](){};`+newlines, refuse bare reserved words `end`/`graph`/`subgraph`/`class` — RT-3).
- **(c) a deterministic Mermaid emitter** from the model (settles claim #10's Mermaid half via a
  headless golden-`.mmd` parse in the gate).

The skill **REQUIRES** the executing Claude to route every brand-color / URI / user-text value through
these gated sanitizers when it free-hands the HTML — this is how CE-1 (Claude authors) and CE-4
(context-aware safety floor) coexist: the *primitives* are real, gated code; the *application* of them
to the final HTML is behavioral.

### 3.3 HONEST GATE-SCOPE STATEMENT (verbatim from `tiebreaks.md` G5 BLOCKER-1 resolution — mandatory)

> **HONEST SCOPE STATEMENT (mandatory in plan.md):** *mechanically gated* = validator + sanitizer
> primitives + Mermaid golden; *behavioral (NOT gateable — Artifact runtime output is never committed
> to CI)* = Claude's final free-hand HTML composition, which the skill REQUIRES to route every
> brand-color / URI / user-text value through the gated sanitizers. This keeps CE-1 while giving CE-4 +
> schema-validation real enforced code paths. Do NOT claim the final HTML is mechanically gated.

Corollaries the plan states plainly (RT-1/RT-2 honest split):
- **Gateable (real code paths):** the schema file is well-formed JSON; a committed golden `model.json`
  validates and known-bad models fail with a named reason; the sanitizers turn malicious input into
  safe output on committed fixtures; a golden `.mmd` parses headless and a raw-bracket-label fixture
  fails. All exercised by the audit-gate against fixtures in `tests/fixtures/wireframe/`.
- **NOT gateable (behavioral, refereed):** that any given *runtime* model a consumer produces is
  schema-valid, and that Claude's final published HTML actually routed every value through the
  sanitizers. `.ravenclaude/runs/` is **gitignored** (verified this session), so runtime output never
  reaches CI. `SKILL.md` states this honestly: runtime validation/escaping is a *required behavior*
  Claude performs with the gated primitives; fidelity/safety of the published Artifact is **refereed**
  (optionally via `visual-feedback-loop`), never claimed as mechanically gated.

### 3.4 The HTML Artifact contract (claims #7/#8)

Claude authors the HTML per the in-prompt Artifact contract: **self-contained / strict-CSP** (no
external CDN / script / font / image — inline CSS/JS, data-URIs only if unavoidable); **theme-aware**
both directions (`@media (prefers-color-scheme: dark)` + `:root[data-theme=...]` overrides);
**no horizontal page scroll** (relative units, flex/grid, `max-width:100%`, wide content in
`overflow-x:auto`); **body-only content** — `<title>`/`favicon` are **tool parameters**, not authored
into the HTML (CE-6 / RT-11: A's correct handling; B's full-document-with-own-`<title>` shape is
rejected). Favicon stays **stable across an iteration's redeploys**. Content is realistic but never a
real brand's claims or logo (scope out-of-scope line).

### 3.5 Iteration & slug safety

- **Persist** the model at `.ravenclaude/runs/wireframe/<slug>/model.json` (tiebreak #6, B's Run
  Artifacts convention). On an edit, mutate that one file and **re-render only the surface(s) in view**.
- **`<slug>` derivation (RT-5, binding):** lowercase, `[a-z0-9-]` only, replace/reject `..` and `/`,
  cap length, and **append a short hash / run UUID for uniqueness**. Rationale: a human slug with no
  uniqueness rule silently overwrites a prior iteration's model (data loss), and an unsanitized slug
  written via `Bash` redirection bypasses `enforce-layout.sh`'s `..`-scrub → out-of-tree write. Writes
  are confined to the run dir.

---

## 4. Reconciled dependency DAG (v1 scope)

```
P0  Pre-build gates (confirm; don't build)
      │
      ▼
P1  schemas/wireframe-model.schema.json  ── THE CONTRACT, blocks everything ──┐
      │                                                                        │
      ├──────────────► P2  wireframe_lint.py  (validator + sanitizers + Mermaid emitter)
      │                        │
      │                        ├──────────► P3  tests/fixtures/wireframe/  (valid/invalid models,
      │                        │                 malicious-input cases, golden .mmd)
      │                        │                        │
      │                        ▼                        ▼
      │                 P5  Gate 145 in scripts/audit-gates.sh (+ --check dispatcher)  ◄── needs P2 code + P3 fixtures
      │                        │
      └──────────► P4  SKILL.md (authoring method, artifact-design load, sanitizer-routing mandate,
                         slug rule, iterate/persist, reciprocal designer note)  ── needs P1 schema + P2 sanitizer signatures
                         │
                         ▼
      P6  Integration & wiring: designer.md reciprocal note · plugin.json + marketplace.json semver bump ·
          CLAUDE.md skills-list + count 49→50 · prettier/ruff/audit-gates · PR on forge/wireframe-studio
          (depends on P1..P5)
```

- **Blocks:** P1 (schema) blocks P2, P3, P4. P5 (gate) blocks on P2 (real code to exercise) **and** P3
  (fixtures to diff). P6 blocks on P1–P5.
- **Parallelizes:** P3 (fixtures) and P4 (SKILL.md) can proceed alongside each other once P2's function
  signatures are fixed; P4 needs only the schema + sanitizer signatures, not the finished gate.
- **Critical path:** `P0 → P1 → P2 → P5 → P6` (schema → helper code → must-fail gate → wiring). The
  primary *value* path — `P0 → P1 → P4 → (Claude authors HTML Artifact)` — is shorter and independent of
  the gate, so a demoable high-fi HTML wireframe exists before the gate machinery finishes (de-risks
  early, mirrors A's "primary value path is shorter" observation).
- **No shared box-packer / `_layout.py` on the v1 path** — it is v1.1 work for ASCII/SVG (tiebreak #4).

---

## 5. Per-phase acceptance tests + pre-build gates

### P0 — Pre-build gates (confirm, don't build)
- **PB-0a — layout:** re-confirm `.repo-layout.json` covers `schemas/**`, `tests/fixtures/**`,
  `plugins/*/skills/**`, `.ravenclaude/runs/**` (all verified present this session → **no glob edit**).
- **PB-0b — no agent:** confirm no agent is added → `check-frontmatter.py` stays out of scope and the
  ~15K description budget is untouched. (If the owner instead chose an agent at G8, the frontmatter
  schema + `tools:` + ≤300-char `description` would gate — flagged at the fork; not the ruled path.)
- **PB-0c — version targets:** ravenclaude-core is at **0.211.0** (verified) → v1 lands **0.212.0**
  (additive minor). Reserve **Gate 145** (highest registered gate is **144**, verified).
- **Acceptance:** a one-line decision note in the run dir; the AGENTS.md layout-verification snippet
  returns "Layout OK".

### P1 — Model schema (the contract; blocks everything)
- Author `schemas/wireframe-model.schema.json` (Draft-07 vocabulary) for §3.1.
- **Pre-build gate:** schema authored **before** any consumer (contract-first).
- **Acceptance:** `python3 -m json.tool` clean; the 4 artifact-type starter skeletons
  (page / app-screen / dashboard / flow) each validate; 3 malformed models each fail with a named
  reason (missing `meta.type`; unknown `component.type`; empty `regions`).

### P2 — `wireframe_lint.py` (stdlib-only helper)
- Implement (a) validator, (b) `html_text` / `css_value` / `uri_scheme` / `mermaid_label` sanitizers,
  (c) deterministic Mermaid emitter. Stdlib-only (no `jsonschema`). A `--self-test` mode against bundled
  fixtures (matches `forge-route.py --self-test` precedent).
- **Acceptance:** valid golden model → exit 0; each malformed model → nonzero + named reason; each
  sanitizer turns a documented malicious input into safe output (`css_value` rejects
  `red;}body{background:url(https://evil/x)}`; `uri_scheme` rejects `javascript:`/`data:`;
  `mermaid_label` neutralizes nested `[]`, `-->`, `"`, `;`/newline, and refuses bare `end`); Mermaid
  emitter is **byte-deterministic** on re-run (`cross-platform-determinism` checklist — tiebreak #7).

### P3 — Fixtures (`tests/fixtures/wireframe/`)
- Commit: valid model(s); ≥3 invalid models (one per named failure); malicious-input→expected-safe-output
  cases per sanitizer; one **golden `.mmd`**; one **known-bad `.mmd`** (raw-bracket / arrow-in-label).
- **Acceptance:** fixtures are the exact inputs P2's `--self-test` and P5's gate consume; committed
  goldens follow `cross-platform-determinism` (no OS path seps, no locale formatting, stable ordering,
  no timestamps).

### P4 — `SKILL.md` (authoring discipline)
- Body carries: the description→model method (frame task → pick `type`+skeleton → rank `emphasis` →
  fill realistic slots → emit + self-validate against the schema); the **`artifact-design` load step**
  before authoring HTML; the **mandate to route every brand-color/URI/user-text value through
  `wireframe_lint.py`'s sanitizers**; the **body-only / title+favicon-as-params** rule; the `<slug>`
  sanitization rule; the persist-and-selective-re-render iterate loop; the **reciprocal "when to use
  which" note** vs `designer`; the honest statement that runtime validation/escaping is behavioral. May
  ask ≤2 refining questions. Frontmatter = `name` + a trigger-led `description` (skills are exempt from
  `check-frontmatter.py`'s agent-only gates — claim #12).
- **Acceptance:** 3 sample briefs (a landing page, an app settings screen, an analytics dashboard) walk
  the documented method to models that validate against P1's schema and carry non-lorem realistic
  content; a `flow` brief produces node/edge sections that the emitter turns into a parsing `.mmd`.

### P5 — Gate 145 in `scripts/audit-gates.sh` (+ `--check 145`)
- Register a numbered gate (per the ci-gate-audit discipline) that runs `wireframe_lint.py` over the P3
  fixtures with a **must-fail half**: known-good model validates (exit 0) **and** a known-bad model
  fails (nonzero); each sanitizer's malicious fixture yields safe output; the golden `.mmd` parses
  headless while the known-bad `.mmd` fails the parse. Add `145` to the `--check` dispatcher list.
- **Pre-build gate:** the gate must **fail on known-bad AND pass on known-good** — proven by
  `scripts/audit-gates.sh` itself (the meta-test). A skipped/always-green gate is rejected.
- **Acceptance:** `bash scripts/audit-gates.sh --check 145` passes; full `scripts/audit-gates.sh` green.

### P6 — Integration, marketplace mechanics, landing (§8 Definition of Done)

---

## 6. Risk matrix (critic R1–R12 ⊕ red-team RT-1–RT-6; BLOCKER-1 shown resolved)

Probabilities/impacts are **relative to the owner-ruled v1 shape** unless marked "(as drafted)".

| # | Risk | Prob | Impact | Status & mitigation / waiver |
|---|------|------|--------|------------------------------|
| **BLOCKER-1** (RT-1+RT-2, one root) | v1 asserts a "schema-validated model" + a "must-fail gate enforcing context-aware escaping" while CE-2/CE-5's "no interpreter" removed every code path that could enforce either | — | High | **RESOLVED (G5 → G6):** re-admit the minimal stdlib `wireframe_lint.py` (validator + sanitizers + Mermaid emitter); gate it against **committed fixtures**; state the **honest gate-scope split** (§3.3) — *mechanically gated* = primitives + goldens; *behavioral* = the free-hand runtime HTML. No claim that runtime output is mechanically gated. |
| R1 (as drafted) | High-fi HTML disappoints — a deterministic renderer emits a skeleton, not a comp | — | — | **DISSOLVED:** HTML is Claude-authored via `artifact-design` (CE-1); no deterministic HTML renderer exists in v1. |
| R2 (as drafted) | `render_html.py` "loads artifact-design" category error | — | — | **DISSOLVED:** no `render_html.py` in v1. |
| R3 / CE-4 → **RT-2** | Context-blind escaping lets CSS-`url()` / `javascript:` / Mermaid-label injection reach a **published** Artifact | Med | High | **Mitigated:** four context-aware sanitizers in `wireframe_lint.py` (CSS-value allowlist, URI-scheme allowlist, HTML-text, Mermaid-label), gated on malicious-input fixtures; skill **requires** routing all runtime values through them. Residual: runtime application is behavioral, not gated (stated honestly). Owner: security-reviewer. |
| **RT-1** | "Schema-validated" unenforced at consumer runtime (`.ravenclaude/runs/` gitignored; no jsonschema) | Med | High | **Mitigated:** stdlib validator ships and is gated on committed goldens; `SKILL.md` states runtime validation is Claude self-checking against the reference schema (behavioral), CI validates only committed fixtures. |
| **RT-3** | Mermaid label/syntax breakage → silent blank/broken flow diagram | Med | Med | **Mitigated (genuinely gateable):** `mermaid_label` sanitizer (quote + entity-escape + strip metachars + refuse reserved words); golden `.mmd` headless-parse gate with a must-fail known-bad `.mmd`. This is where the gate budget is best spent. Settles claim #10's Mermaid half. |
| **RT-4** / R9 | Drift vs `designer`; and a subagent pointer is non-functional (`designer` has no Artifact tool) | Med | Med | **Mitigated:** `/wireframe` is a **main-session** skill; **reciprocal** "when to use which" note in both `SKILL.md` and `designer.md`; `designer` may build the model and hand publish up. |
| **RT-5** | `<slug>` unspecified → silent collision (data loss) + path traversal (out-of-tree Bash write) | Med | Med | **Mitigated:** slug rule — lowercase `[a-z0-9-]`, reject `..`/`/`, cap length, append hash/UUID; writes confined to the run dir. |
| R5 | Low-value renderers (ASCII/SVG) + priciest `_layout.py` node on the critical path | — | — | **DISSOLVED for v1:** ASCII/SVG + box-packer deferred to v1.1; v1 critical path is `schema → helper → gate`, not the coordinate engine. |
| R6 / CE-5 | python3 not present at consumer → render `command not found` | Low | Med | **Mostly dissolved:** v1's HTML + Mermaid need **no interpreter at runtime** (Claude-authored / emitter-optional). `wireframe_lint.py` is a *dev/CI + optional local* helper; the skill degrades gracefully to behavioral self-check where python3 is absent. Residual accepted + stated. |
| R7 | flow-type schema fork (node/edge vs screens+flow_edges) | — | Low | **RESOLVED:** A's node/edge-on-canvas is canonical v1 (maps to Mermaid `flowchart`); B's multi-screen map is a v1.1 optional extension (tiebreak #1). |
| R8 / CE-2 | Model carries dead-weight fields for unshipped renderers | Low | Low | **Reduced:** v1 ships only HTML + Mermaid, both of which use `emphasis`/`viewport`/`brand`/`theme`; the fields are not dead in v1. `model_version` seeds the v1.1 seam. |
| **RT-6** | v1→v1.1 seam: free-hand-authored, runtime-unvalidated models won't cleanly feed v1.1 ASCII/SVG | Low-Med | Low-Med | **Mitigated:** `meta.model_version` now + a v1.1 validate-and-migrate pass; `SKILL.md` documents v1 persisted models are HTML/Mermaid-oriented. Accepted-risk waiver otherwise. |
| R10 | Determinism/validation oversold | Low | Low | **Mitigated:** §3.3 states precisely what is deterministic/gated (validator, sanitizers, Mermaid emitter on fixtures) vs behavioral (runtime model + HTML). |
| R11 / CE-6 | Artifact-wrapper boundary error (own `<head>`/`<title>`/favicon) | Low | Low | **Mitigated:** body-only content; title/favicon as tool params (§3.4). |
| R12 | Convergence mistaken for corroboration | — | Med | **Addressed:** the critic's CEs were treated as the agenda convergence hid; the wireframe-vs-comp fidelity fork (CE-3) was escalated to and ruled by the owner (tiered hybrid), not resolved by assertion. |

**No unmitigated high-severity blocker remains.** BLOCKER-1 is resolved; every other row carries a
mitigation or an explicit accepted-risk waiver.

---

## 7. Alternatives considered (carried from the panels + critic)

| Alternative | Source | Why rejected (for v1) |
|---|---|---|
| **New dedicated `wireframe-studio` plugin** (agent + skill) | A-alt3 / B §"why not (b)" | Adds a 169th catalog entry + (if it ships an agent) permanent ~15K budget cost for a **domain-neutral** capability that fits core; `brand-extraction` is the precedent for neutral schema+engine → **core skill**. Promotion path stays open if scope later grows to a prototyping *suite* (multi-screen prototypes, Figma export — both out of scope). |
| **Deterministic Python `render_html.py` as the high-fi engine** | both panels' original plan | **The critic's CE-1 category error.** A script cannot "load `artifact-design`" or exercise design judgment; a fixed renderer's virtue (same skeleton every time) is the *definition* of low-fi. Owner ruled: **Claude authors the HTML free-hand**; Python earns its determinism only on structural output (Mermaid now; ASCII/SVG in v1.1). |
| **Four independent free-text→format generators (no shared model)** | A-alt1 / B-altC | The scope's named anti-pattern: guarantees cross-format drift and makes "iterate" impossible (no single source of truth). |
| **HTML-only, derive other formats by parsing the HTML** | A-alt2 | Couples every surface to brittle DOM parsing; loses the "model is the contract" gate. |
| **One monolithic super-renderer (all formats, one pass)** | B-altB | Couples formats (one layout bug breaks all); blocks independent dev/test; pays layout cost even when unused. |
| **LLM free-hand rendering for *every* format, no helper code** | B-altA | Leaves schema-validation + CE-4 escaping instruction-only with nothing to gate — exactly the green-gate-over-open-door RT-1/RT-2 warn of. v1 keeps free-hand **only** for HTML and re-admits `wireframe_lint.py` for the gateable primitives. |
| **All four formats co-equal in v1** | scope decision 2, as read by both panels | Front-loads low-value ASCII/SVG (thin demand; SVG's `_layout.py` is the priciest, most bug-prone critical-path node) ahead of value. Owner ruled a **value-tiered** cut: v1 = HTML + Mermaid-for-flows; ASCII/SVG → v1.1, still inside the owner's four-format destination. |

---

## 8. Definition of Done

**Skill files**
- `plugins/ravenclaude-core/skills/wireframe/SKILL.md` — `name` + trigger-led `description`; the §5-P4
  body (method, `artifact-design` load step, sanitizer-routing mandate, body-only/title+favicon rule,
  slug rule, iterate/persist, reciprocal designer note, honest behavioral-vs-gated statement).
- `plugins/ravenclaude-core/skills/wireframe/wireframe_lint.py` — stdlib-only validator +
  `html_text`/`css_value`/`uri_scheme`/`mermaid_label` sanitizers + deterministic Mermaid emitter +
  `--self-test`.
- (Lean v1 starter skeletons — one per artifact type — bundled under the skill dir; full named-archetype
  library is v1.1.)

**Schema + fixtures**
- `schemas/wireframe-model.schema.json` — top-level, mirrors `brand-kit.schema.json` precedent.
- `tests/fixtures/wireframe/` — valid + ≥3 invalid models; per-sanitizer malicious-input→safe-output
  cases; a golden `.mmd` + a known-bad `.mmd`. Committed goldens follow `cross-platform-determinism`.

**The gate (must-fail, real teeth)**
- **Gate 145** wired into `scripts/audit-gates.sh` main sequence **and** its `--check` dispatcher list
  (currently ends at 144, verified). Exercises `wireframe_lint.py` over the fixtures with a **known-bad
  half** (invalid model fails; malicious inputs are neutralized; known-bad `.mmd` fails the parse) and a
  known-good half (valid model + golden `.mmd` pass). Proven by the `audit-gates.sh` meta-test.

**Marketplace mechanics (modified plugin — not a new plugin)**
- Bump `ravenclaude-core` semver in **both** `plugins/ravenclaude-core/.claude-plugin/plugin.json`
  **and** the mirrored `.claude-plugin/marketplace.json` entry: **0.211.0 → 0.212.0** (verified current;
  CI fails on drift).
- Update `plugins/ravenclaude-core/CLAUDE.md`: add `/wireframe` to the skills list + the "New skills"
  narrative, and bump the **skill-count prose 49 → 50** (verified 49 today). If a Learn-tab concept card
  / repo-guide surface is added, regenerate the dashboards and honor the freshness gates (the 2026-06-03
  three-PR hotfix trap).
- **`designer.md`** — reciprocal "when to use which" note (prose only; no `description`/`tools`/scenario
  change → `check-frontmatter.py` untouched).
- **`.repo-layout.json` — NO edit needed** (verified this session: `schemas/**`, `tests/fixtures/**`,
  `plugins/*/skills/**`, `.ravenclaude/runs/**` all present in `allowed_globs`). Stated explicitly to
  avoid the PR #32 layout-allow-list pitfall.
- **`check-frontmatter.py` — N/A** (no agent added) — a direct consequence of the skill-not-agent ruling.

**Whole-tree hygiene (AGENTS.md discipline)**
- `npx prettier@3.9.4 --write .` then `--check .` exit 0 (touches the JSON schema + fixtures + any YAML).
- `ruff check .` exit 0 (the stdlib-only `wireframe_lint.py`).
- `scripts/audit-gates.sh` green (meta-test proves Gate 145 has teeth); `python3 -m json.tool` on the
  schema + all fixture models + both manifests after the bump.
- AGENTS.md layout-verification snippet returns "Layout OK" before push.

**Landing**
- PR on branch **`forge/wireframe-studio`** (ships inside `plugins/` → PR required, not straight to
  main). Post-PR: run the decision-review retrospective over the PR's decisions and log the verdict as a
  PR comment (repo convention).
- **Migration note: none** — additive skill; nothing in a consumer's installed plugin changes on
  `/plugin marketplace update` until they invoke `/wireframe`.

**`[unverified]` claim from claims-table.md — settling step.** Claim #10 (`[unverified — training
knowledge]`: SVG 1.1 + Mermaid syntax are the emit targets). v1 settles the **Mermaid** half: the
`wireframe_lint.py` emitter's golden `.mmd` is **parsed headless in Gate 145** (a raw-bracket-label
known-bad `.mmd` must fail) — moving Mermaid syntax from `[unverified]` to gate-verified. The **SVG 1.1**
half is deferred with the SVG renderer to **v1.1**, where the `svg-report-lint` (Gate 103) security floor
+ a sample render settle it; until then it carries no v1 claim. (All other claims #1–#9, #11–#12 were
`WARN→OK` / `OK` and re-verified at synthesis: 168 plugins, 49 skills, version 0.211.0, `jsonschema`
absent, `schemas/brand-kit.schema.json` sibling present, globs present, `.ravenclaude/runs/` gitignored,
`designer` has no Artifact tool.)

**Success signal (scope §41-44):** from a one-sentence brief, `/wireframe` produces a high-fi HTML
Artifact for a **page**, an **app screen**, and a **dashboard** (proving "anything"), plus a **Mermaid
flowchart** for a **flow** brief — all from the same validated model, with every runtime value routed
through the gated context-aware sanitizers. ASCII + SVG follow in v1.1.
