---
name: design-clone
description: Capture a reference website's full design schema (spacing/type/grid/elevation/component recipes) and apply it to a target — cloning the craft while swapping in the target's own brand and structurally blocking the reference's identity from leaking. Fidelity is browser-gated; trade dress is not cleared here.
---

# design-clone — clone the craft, swap the identity

**Clone the craft, swap the identity.** This skill reproduces a reference site's *functional
craft* — its spacing scale, type scale, grid/breakpoints, elevation ramp, and component
recipes — and re-skins it with the **target's own** brand (logo, colors, fonts). The
reference's **identity** (logo, signature color, mascot) is structurally unable to reach the
output. Reproducing re-skinned functional craft is the lower-risk path; faithfully cloning a
distinctive *whole composition* is not, and this skill cannot detect the difference (see
[Trade-dress limit](#trade-dress-limit-not-legal-clearance)).

This is the **capture + apply** half of the design-schema-mimicry capability. It sits beside:

- **Capture** — `brand-extraction`'s [`extract_brand.py`](../brand-extraction/extract_brand.py)
  emits the reference's `design-schema.json` (declared-CSS only, every value stamped
  `capture_method:"static"`) and its `brand.json` brand kit.
- **Contract** — [`schemas/design-schema.schema.json`](../../../../schemas/design-schema.schema.json),
  conformance-checked by [`scripts/check-design-schema.py`](../../scripts/check-design-schema.py)
  (the single stdlib conformance point — no `jsonschema`, no cross-skill import).
- **Apply** — this skill's [`apply_schema.py`](apply_schema.py) + [`sanitizers.py`](sanitizers.py).

## What "apply" does

```
apply_schema.py <ref-design-schema.json> --target-brand <target-brand-kit.json> --out <dir>
```

It emits, into `<dir>`:

- `design-schema.css` — `--space-*` / `--font-size-*` / `--shadow-*` / `--grid-*` custom
  properties, geometry cloned from the reference but **colors and fonts from the target**.
- `component-<archetype>.html` — one **fixed-structure** scaffold per recognized component
  (button / card / nav / input), value-only, wired to `design-schema.css`.
- `apply-report.json` — what was emitted, what was dropped, and the advisory identity flags.

Every reference-derived value is routed through an **allowlist sanitizer** before it can reach
a stylesheet; anything that is not on the allowlist is dropped, not salvaged.

## The two-layer identity defence

1. **Hard structural no-read invariant (the real defence).** `apply()` reads only the
   reference's structural geometry and the **target** brand kit's colors/fonts. Its body does
   not read the reference's `logos[]` or `colors.palette` — even when handed a reference bundle
   that carries those keys — so a reference logo or primary color has no structural route to
   the output regardless of whether the advisory flag fired.
2. **Identity-color re-entry neutralization.** A signature color can still try to ride in
   through an elevation/border color. Shadow emission is **geometry only**: a chromatic
   (identity-bearing) color is replaced with a target-owned token (`var(--brand-shadow-color)`);
   a neutral elevation tint (achromatic black/gray) survives verbatim. So
   `0 0 12px #e10098` → `0 0 12px var(--brand-shadow-color)`, while
   `0 2px 8px rgba(0,0,0,0.1)` survives byte-for-byte.
3. **Advisory flag (`flag_identity_risks`).** A second, never-authoritative layer that flags
   every logo, **every** high-frequency saturated reference color (not just `role=="primary"` —
   the role guess mislabels signature colors), mascot/illustration keyword hits, and any color
   embedded in elevation/components. `action` is always `"human-decision"`; it never
   auto-approves; distinctiveness / trade-dress / legal calls route to
   `ravenclaude-core/security-reviewer` (mirroring the
   [`asset-provenance-guardian`](../../../generative-web-media/agents/asset-provenance-guardian.md)
   flag-and-route posture). **Not legal advice.**

## The sanitizers ([`sanitizers.py`](sanitizers.py))

- `html_text`, `uri_scheme`, `css_value` are **ported from
  [`wireframe_lint.py`](../wireframe/wireframe_lint.py) — keep in sync.** `css_value` is
  **color-only**: it validates a safe CSS color and nothing else, which is exactly why the
  structural payload needs the strict allowlists below (routing `8px` / a shadow / `1200px`
  through a color-only check returns `None` and would ship an empty stylesheet).
- `css_length` — `^-?num(px|rem|em|%|vw|vh|ch|ex)$` or literal `0`.
- `css_number` — `^\d+(\.\d+)?$`.
- `css_shadow` — a **bounded compound**: every token must be a `css_length`, a matched color,
  or literal `inset`; ≤4 length tokens per layer, ≤8 layers. **Any unknown token drops the
  ENTIRE value** — never the clean remainder (no partial salvage).
- All widened sanitizers unconditionally reject `(`/`)` (except inside a matched color), `;`
  `{` `}` `/*` `\` `<` `>`, `@import`, `expression(`, `var(`, and whitespace-injection. Regexes
  are linear (no nested quantifiers — no ReDoS over a large `css_text`).

## Browser-gated fidelity

This apply path is an **offline, declared-CSS** transform — a structural clone of the design
*system*, never a pixel-fidelity claim. Verifying that the re-skinned output actually *looks*
like the reference is the **browser layer's** job (the render→compare loop's `ssim_score`
gate), present only when a browser tool is. With no browser tool the loop reports fidelity
**unverified** — it does not, and cannot, compare pixels in stdlib. Every captured value
self-declares `capture_method`, and v1 ships only the `static` producer.

## Stateless-loop boundary (read this loudly)

**One pass is not convergence.** `apply()` is a single, stateless transform — it holds no
iteration history and cannot decide it is "done." The determinate gate (structural + `ssim`
when present) is the **only** stopping proof. **Patience across iterations is the agent's
cross-iteration job**, never state held in this skill: re-run, compare against the reference,
adjust, and re-run — stop when the gate passes, not after the first render.

## Trade-dress limit (not legal clearance)

The identity discipline is conservative by construction — the tool cannot ship the reference's
logo or brand color even if the heuristic misses. But **trade dress protects overall
look-and-feel / distinctive arrangement, which is exactly what a faithful whole-composition
clone reproduces, and this tool cannot detect that.** A clean `identity_flags[]` is **not**
legal clearance. "Is this reference's look distinctive enough to be protected?" routes to
`ravenclaude-core/security-reviewer` / counsel. Not legal advice.

## Gate

**Gate 194** (`scripts/audit-gates.sh --check 194`) drives `apply_schema.py --self-test` and is
**bidirectional**: hostile `url(javascript:…)` / `;background` / `expression()` / partial-salvage
shadows must be **absent** from `design-schema.css`; legit `8px` / `1.5rem` /
`0 2px 8px rgba(0,0,0,0.1)` / `1200px` must **survive verbatim**; the reference signature color
must be **absent** and the output tree must carry **zero** logo/image files; and the advisory
flag must fire without ever auto-approving. Its must-fail mutants prove the teeth (neuter a
sanitizer → hostile appears → red; drop-everything sanitizer → survive fails → red; let
`apply()` read `colors.palette` → reference color appears → red).
