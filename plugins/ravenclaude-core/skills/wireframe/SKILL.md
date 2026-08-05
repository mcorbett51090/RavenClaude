---
name: wireframe
description: "Invoked by /wireframe. Turn a plain-language description of anything — a web page, an app/software screen, a dashboard, or a flow/diagram — into a validated wireframe MODEL, then a high-fidelity self-contained HTML Artifact (authored via artifact-design) and, for flows, a Mermaid flowchart. One model, many surfaces; iterate by editing the model. NOT a full design spec or accessibility audit (that is the designer agent) and NOT production code."
---

# Skill: wireframe (`/wireframe`)

> **Main-session skill.** It publishes an HTML **Artifact**, so it must run in the main session — a
> subagent (including `designer`) has no Artifact tool and cannot publish. If a subagent produced the
> model, hand the publish **up** to the main session.

Turn any description into a wireframe by producing **one JSON model** and rendering it. The model is the
contract; every surface is derived from it, so "make the header blue" or "turn this into a dashboard"
edits **one** source of truth.

## When to use this vs. the `designer` agent (reciprocal — keep them delimited, not parallel)

| Use `/wireframe` (this skill, main session) | Use the `designer` agent |
|---|---|
| Fast: description → validated model → **high-fi HTML Artifact** + **Mermaid-for-flows** | Full **design spec**, accessibility audit, and handoff to `frontend-coder` |
| You want a shareable layout mockup to react to now | You want a documented, reviewed design decision + rationale |

`designer` may produce the model/spec and hand the Artifact publish up to the main session. Don't run
both for the same ask — pick the surface that matches the depth needed.

## The method (description → model → render)

1. **Frame the task.** If the ask is ambiguous on *what kind of thing* or *which viewport*, ask **≤2**
   crisp questions; otherwise proceed. Pick `meta.type` ∈ `page | app-screen | dashboard | flow` and
   start from the matching skeleton in [`skeletons/`](skeletons/).
2. **Rank hierarchy.** Set `emphasis` (`primary | secondary | tertiary`) on regions/sections — this is
   `designer`'s information-hierarchy method, made machine-readable so the renderer keys off it
   ("primary = largest + highest-contrast") instead of re-deriving from order.
3. **Fill realistic content.** Populate `content_slots` with *representative* copy — never `lorem`, and
   never a real brand's claims, logos, or numbers (see out-of-scope). Placeholder ≠ fabricated fact.
4. **Emit + self-validate.** Write the model to `.ravenclaude/runs/wireframe/<slug>/model.json` (slug
   rule below) and validate it: `python3 plugins/ravenclaude-core/skills/wireframe/wireframe_lint.py
   --validate <path>`. If `python3` is unavailable, self-check the model against
   [`schemas/wireframe-model.schema.json`](../../../../schemas/wireframe-model.schema.json) by reading it
   — state that you are doing the behavioral check.
5. **Render the surface(s) asked for:**
   - **HTML Artifact (primary, high-fi):** first load the **`artifact-design`** skill, then author the
     Artifact **free-hand** from the model. A script cannot produce a high-fi comp — you do. Follow the
     Artifact contract in §"HTML rules" below.
   - **Mermaid (flow type):** run `wireframe_lint.py --emit-mermaid <model.json>` for a deterministic,
     sanitized `flowchart`. Do not hand-write Mermaid — the emitter escapes labels safely.
   - **ASCII wireframe (structural, deterministic):** `python3 render_ascii.py --emit <model.json>` —
     a byte-deterministic box-drawing frame. Good for a plaintext/terminal or diff-friendly sketch.
   - **SVG wireframe (structural, deterministic, embeddable/CI-diffable):** `python3 render_svg.py
     --emit <model.json>` — output clears `svg-report-lint` (Gate 103) **by construction** (closed
     `<svg>/<g>/<rect>/<text>` vocab, no script/handlers/remote refs, viewBox aspect padded into
     0.05..20). Both renderers share the deterministic `_layout.py` box-packer.
   - **Named archetype:** start from a library model under `archetypes/<category>/<slug>.json`
     (`marketing` / `app` / `data`) and adapt it; check structural completeness with
     `archetype_score.py --score <model.json>` (≥ 80 = well-formed, **not** a taste judgement).
   - **Multi-screen app (v2):** set `meta.model_version: "2"` and use `screens[]` (each `{id, regions}`)
     plus optional `flow_edges[]` (`{from, to, label?}`) — **mutually exclusive** with top-level
     `regions`. ASCII/SVG render every screen; the screen-to-screen nav map comes from
     `wireframe_lint.py --emit-screen-flow <model.json>` (a Mermaid `flowchart LR`).

## Safety — route every runtime value through the gated sanitizers (binding)

The model carries **customer/description-derived text** that lands in a **published, shareable** Artifact.
When you author the HTML, you **must** route values through the sanitizers in `wireframe_lint.py`
(importable, or mirror their logic):

- **brand colors / any value entering `<style>` or a `style=` attr → `css_value`** (allowlist: `#hex`,
  `rgb()/hsl()`, or a keyword only). This blocks `url()` external-fetch and CSP breaks. Reject, don't pass.
- **any URL (`href`, `src`) → `uri_scheme`** (allowlist `http/https/mailto/tel`; blocks `javascript:` /
  `data:`).
- **any user/description text in HTML → `html_text`** (entity-escape).
- **flow node/edge labels → the Mermaid emitter** (which calls `mermaid_label`).
- **any text in an ASCII render → `ascii_text`** (strips C0 controls + newlines; the renderer then
  **clips** every label to its cell interior, so a `-`/`|`/`+` in content can't forge a frame border —
  which is why `ascii_text` does NOT strip those glyphs and a KPI `-12%` survives intact).
- **any text in an SVG render → `html_text`, any color → `css_value`** (the SVG renderer routes these,
  and its output is held to `svg-report-lint`/Gate 103).

**Honest scope (say this plainly if asked what's guaranteed):** the validator, the four sanitizers, and
the Mermaid emitter are **mechanically gated** on committed fixtures (audit-gates.sh **Gate 145**). The
final HTML Artifact is authored free-hand at runtime and lives under gitignored `.ravenclaude/runs/`, so
its safety/fidelity is a **required behavior you perform**, not something CI can diff — it is **refereed**
(optionally via the `visual-feedback-loop` skill), never claimed as mechanically gated.

## HTML rules (the Artifact contract)

- **Self-contained / strict-CSP:** inline all CSS/JS; no external CDN, script, font, or remote image
  (data-URIs only if unavoidable).
- **Theme-aware both ways:** `@media (prefers-color-scheme: dark)` **plus** `:root[data-theme=…]`
  overrides.
- **No horizontal page scroll:** relative units, flex/grid, `max-width:100%`; wide tables/diagrams in an
  `overflow-x:auto` container.
- **Body content only.** The `<title>` and `favicon` are **Artifact tool parameters**, not authored into
  the page. Keep the favicon **stable** across an iteration's redeploys.

## Slug & iteration

- **`<slug>`:** lowercase, `[a-z0-9-]` only; reject `/` and `..`; cap length; **append a short run
  id/hash for uniqueness**. Rationale: a bare human slug silently overwrites a prior iteration (data
  loss), and an unsanitized slug written via `Bash` redirection can escape the tree. Confine writes to
  `.ravenclaude/runs/wireframe/<slug>/`.
- **Iterate:** on an edit, mutate `model.json` and **re-render only the surface currently in view** — not
  all of them.

## Scope

**Shipped (v1 + v1.1):** the model + `schemas/wireframe-model.schema.json`; the high-fi **HTML
Artifact** + **Mermaid-for-flows**; the `wireframe_lint.py` primitives (validator + four sanitizers +
`ascii_text` + Mermaid emitter + the `emit_screen_flow` nav-map emitter); the deterministic
**`_layout.py`** box-packer; the **ASCII** (`render_ascii.py`) and **SVG** (`render_svg.py`) renderers
(SVG held to `svg-report-lint`/Gate 103); the two-level **named-archetype library** (`archetypes/`) +
`archetype_score.py`; and the **multi-screen (v2)** `screens[]`/`flow_edges[]` extension. Every
deterministic surface is byte-stable (`cross-platform-determinism`) and gated by `audit-gates.sh`
**145–150**. Full trail: [`docs/wireframe-studio-plan.md`](../../../../docs/wireframe-studio-plan.md).

**Honest gate scope (mandatory to state if asked):** the validator, the sanitizers, the Mermaid +
screen-flow emitters, the box-packer self-check, and the ASCII/SVG determinism goldens are
**mechanically gated** on committed fixtures. `archetype_score` measures **structural completeness**,
not aesthetic quality — a committed archetype scoring ≥ 80 means it is well-formed, not that it is good
design (the discriminating teeth is the degraded must-fail fixture, not the ≥ 80 self-check). The final
HTML Artifact remains free-hand at runtime (behavioral, refereed — never claimed as mechanically gated).

**Out of scope:** real design-tool export (Figma/Sketch), turning a wireframe into production code, and
any fabricated brand asset, logo, or real-sounding metric.
