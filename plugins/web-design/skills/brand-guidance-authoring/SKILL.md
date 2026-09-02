---
name: brand-guidance-authoring
description: Author a project's generation-time brand-voice contract (brand-guidance.md) — a named aesthetic, a two-typeface max, a tiny palette, a 4px spacing scale, a motion philosophy, and a project-scoped anti-pattern catalogue that bans the recurring "AI slop" patterns (generic-sans brand faces, indigo gradients, 3-card grids, card-in-card, stock-photo 100vh heroes) by default. Loaded into context before every page-generation call — the tokens answer "what are the values," this answers "how does an agent reliably apply them." Reach for this skill when a project's design-tokens.json exists (or is being produced alongside) and no brand-voice contract exists yet. Used by `visual-designer` (primary); `frontend-implementer` and `content-strategist` co-consume it (voice rules straddle visual and copy).
---

# Skill: brand-guidance-authoring

**Purpose:** produce a project's `brand-guidance.md` — a short, checkable brand-voice contract loaded
into context on every page-generation call, distinct from the token JSON `design-tokens-scaffolding`
produces once per brand cycle. Closes the gap
[`knowledge/design-sources/vercel-design-md.md`](../../knowledge/design-sources/vercel-design-md.md)
named: a Vercel-style generation-time brand-guidance file, with a named anti-pattern catalogue, had no
owning skill in this plugin.

## 1. Tokens vs. guidance — the boundary this skill sits on

| | Values (`design-tokens-scaffolding`) | Application (this skill) |
|---|---|---|
| Answers | "What are the values?" | "How does an agent reliably apply them?" |
| Artifact | `design-tokens.json` | `brand-guidance.md` |
| Read cadence | Once per brand cycle | Loaded into context on **every page-generation call** |
| Format | W3C DTCG token JSON | Prose contract + a resolved anti-pattern catalogue |

This is the same distinction
[`knowledge/design-md-token-interop.md`](../../knowledge/design-md-token-interop.md)'s disambiguation
table already draws (see that file rather than re-deriving it here) — and it is why this artifact is
named `brand-guidance.md`, never `DESIGN.md` or `design.md`: the Google-Labs `DESIGN.md` format already
shipped in this repo as a **token-export** house default
([`ravenclaude-core/templates/DESIGN.md`](../../../ravenclaude-core/templates/DESIGN.md)), and Vercel's
own `design.md` post uses the same filename for this skill's *different* job. Same filename, different
job, twice over — hence a third, unambiguous name here.

## 2. When to use / when NOT to use

**Use when:** a project has (or is producing alongside) a `design-tokens.json` and will generate more
than one page agentically — a marketing site, a multi-page app shell, any build where "make it look
consistent across pages" matters.

**Do NOT use for:**
- Authoring the token JSON itself — that's [`design-tokens-scaffolding`](../design-tokens-scaffolding/SKILL.md).
- A pure component-library refactor with no new page generation.
- A build with no agentic page generation at all (a hand-authored single static page). Record
  `N/A — no agentic page generation` at the pipeline's G3 gate per
  [`gold-standard-website-pipeline/SKILL.md`](../gold-standard-website-pipeline/SKILL.md) §1's binding
  N/A discipline — this is the pipeline's existing sanctioned way to not-run a criterion without a
  silent skip.

## 3. The authoring procedure

1. **Read the closed G1/G2 outputs** — the discovery brief's audience/archetype and the IA's content
   model. The aesthetic must serve the audience named there, not be picked in a vacuum.
2. **Read the G3 token JSON.** Palette, spacing, and radius in `brand-guidance.md` are *derived from*
   the existing tokens — never re-decided here. If a value this skill needs doesn't exist in the token
   set yet, that's a `design-tokens-scaffolding` gap, not something to invent inline.
3. **Name the aesthetic against ≥2 concrete references** from
   [`knowledge/design-references.md`](../../knowledge/design-references.md) — real sites/products, not
   adjectives. "Editorial technical, like Stripe docs" is a named aesthetic; "modern and clean" is not
   and is explicitly banned as brand-voice prose by this skill's own discipline (§4).
4. **Write every rule as an observable statement** — the single highest-leverage idea in this skill.
   Four worked before/after pairs:

   | Adjectival (banned) | Observable (required) |
   |---|---|
   | "Keep it clean." | "Use exactly two typefaces; no more than three type sizes visible in any single viewport." |
   | "Feel modern." | "Radius is `none` everywhere except form inputs (`sm`); elevation is a 1px hairline, never a shadow." |
   | "Make the hero pop." | "The hero's only color accent is `color.accent.default`; every other element in the hero uses `color.text.default` or `color.background.default`." |
   | "Keep the copy friendly." | "Sentences average under 20 words; the CTA verb is always an action a user performs (\"Start,\" \"Send\"), never a description (\"Get started today\")." |

5. **Resolve every anti-pattern catalogue row's `override`** for this project — copy the 10 IDs from
   [`reference/anti-pattern-catalogue.md`](reference/anti-pattern-catalogue.md) into the project's
   `brand-guidance.md` §7 (using the [`templates/brand-guidance.md`](templates/brand-guidance.md)
   scaffold), setting each `override.status`. Every row defaults `enforced`; relaxing one requires a
   non-empty, project-specific `rationale` — "we like it" is not a rationale.
6. **Emit `brand-guidance.md`** beside `design-tokens.json` in the gate ledger, so both artifacts land
   together at the same pipeline stage.

## 4. The observable-statement rule

Every sentence in a project's `brand-guidance.md` must describe something a reader (human or agent)
could check by looking at the rendered output — never an adjective standing in for a decision that was
never actually made. Banned words in this file's own rules (not the aesthetic's *name*, which may be a
proper noun): `clean`, `modern`, `sleek`, `polished`, `beautiful`, `elegant`, and close synonyms. If a
rule can't be rewritten to pass this bar, it isn't a rule yet — it's a wish.

## 5. Overriding the catalogue

The 10 rows in [`reference/anti-pattern-catalogue.md`](reference/anti-pattern-catalogue.md) are
**recommendations, not doctrine.** Every row ships `enforced` by default; a project relaxes or replaces
one via the `override` block, with a required rationale.

**The live example this skill deliberately does not resolve for you:** `AP-01` bans a generic-sans face
(Inter, Roboto, Open Sans, Arial, `system-ui`) as a project's brand-voice/display face, but
[`knowledge/design-references.md`](../../knowledge/design-references.md) still recommends Inter as one
of three acceptable display faces in its own Synthesis section — for the general case, not this
catalogue's stricter default. Both are correct in their own scope: `AP-01`'s ban is specifically about
the *identity-carrying* face; Inter/Roboto/etc. remain fine as a UI, data, tabular, or system-fallback
face. If a project's brand voice genuinely is Inter, that's exactly what `override.status: relaxed`
with a stated rationale is for — this skill surfaces the tension, it does not adjudicate it. See
`design-references.md`'s own "Live tension — Inter as a display face" note for the fuller cross-link.

## 6. Hygiene checklist

- [ ] `brand-guidance.md` exists beside `design-tokens.json` in the gate ledger.
- [ ] All 7 required sections present, in order (named aesthetic, typography, palette, spacing,
      radius & elevation, motion philosophy, anti-pattern catalogue).
- [ ] Typeface count ≤ 2, machine-readable in §2.
- [ ] Every catalogue row (§7) has a resolved `override.status`; every non-`enforced` row has a
      non-empty `rationale`.
- [ ] Zero adjectival rules anywhere in the file's own prose (§4's banned-word list).
- [ ] Palette references DTCG semantic tokens, never raw hex.

## 7. Verifying the structural bar mechanically (optional)

G3's five structural facts (§6 above) are checkable by a stdlib script rather than only by an
agent's own read: [`scripts/brand_guidance_lint.py`](scripts/brand_guidance_lint.py) checks a
project's `brand-guidance.md` against exactly the same five facts — file exists and is non-empty,
all 7 sections present in order, typeface count ≤ 2 (read from the `typeface_count:` marker), every
catalogue row's `override` resolved with a rationale where relaxed, and zero adjectival rules in the
project's own authored prose. It is a structural checker only — it says nothing about whether the
result looks good; that judgment stays with [`brand-polish-checklist.md`](reference/brand-polish-checklist.md).

```shell
python3 scripts/brand_guidance_lint.py check <path-to-brand-guidance.md> \
  --catalogue reference/anti-pattern-catalogue.md
```

A project may wire this into CI to make G3's structural bar mechanically enforced rather than
agent-attested; the pipeline does not run it automatically today.

## See also

- [`reference/anti-pattern-catalogue.md`](reference/anti-pattern-catalogue.md) — the 10 banned patterns, ID'd and overridable
- [`reference/brand-polish-checklist.md`](reference/brand-polish-checklist.md) — the fresh-context self-check, advisory only
- [`templates/brand-guidance.md`](templates/brand-guidance.md) — the emitted artifact's scaffold
- [`scripts/brand_guidance_lint.py`](scripts/brand_guidance_lint.py) — the runnable structural checker for G3's 5 facts (`--self-test` proves each check independently)
- [`../design-tokens-scaffolding/SKILL.md`](../design-tokens-scaffolding/SKILL.md) — the values half of this boundary
- [`../design-system-audit/SKILL.md`](../design-system-audit/SKILL.md) — auditing the resulting system for consistency
- [`../gold-standard-website-pipeline/SKILL.md`](../gold-standard-website-pipeline/SKILL.md) — G3, where this skill is dispatched
- [`../../knowledge/design-sources/vercel-design-md.md`](../../knowledge/design-sources/vercel-design-md.md) — the pattern this skill is modeled on
- [`../../knowledge/design-md-token-interop.md`](../../knowledge/design-md-token-interop.md) — the disambiguation from the Google-Labs `DESIGN.md` token-export format
- [`../../../ravenclaude-core/knowledge/visual-feedback-loop.md`](../../../ravenclaude-core/knowledge/visual-feedback-loop.md) — the render→see→critique→iterate canon this skill's checklist plugs into
