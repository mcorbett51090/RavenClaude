# Curate the vector, don't regenerate it

**Status:** Absolute rule
**Domain:** Generation / deliverable integrity
**Applies to:** `brand-identity-studio`

> The deliverable-integrity principle is durable; provider/indemnity specifics are `generative-web-media`'s
> per-asset call and `[verify-at-use]`.

---

## Why this exists

The whole value promise of this engagement is the **human curation**: a person selected a concept, modified it
substantially, and that curated artifact is the brand. Re-generating that logo in Firefly for a "final,
indemnified" pass produces a **different asset** — it throws away the curation and the documented human
authorship that made the deliverable copyrightable and ownable. Firefly's IP-indemnity value is real, but it
applies to **fill/photographic imagery** where concept == final in one pass, not to a logo the client already
chose. Regeneration is not a finishing step; it is a new, un-curated asset.

## How to apply

- Treat the **curated Recraft/Ideogram-class vector as the deliverable**. It ships as-is (SVG), refined by the
  human, logged in the authorship record.
- **Never** re-send a curated logo/wordmark to Firefly (or any generator) for a "final" pass.
- Reserve Firefly-default (and the per-asset indemnity decision, made by `generative-web-media`) for
  **fill/photographic imagery** — not logos.
- If indemnity is needed on the mark itself, that is a **legal/licensing** question for `security-reviewer` and
  the vector provider's terms — not a reason to regenerate.

**Do:** ship the curated vector; keep the authorship log with it.
**Don't:** regenerate the chosen logo in Firefly to "make it indemnified" — that's a new asset.

## Edge cases / when the rule does NOT apply

Producing **new** fill/photographic imagery (a hero photo, a texture) is a fresh generation where Firefly's
one-pass concept==final + indemnity is appropriate — because there is no prior human-curated artifact to
destroy. That is generation, not regeneration of a curated mark.

## See also

- Skill: [`../skills/logo-and-visual-system-direction/SKILL.md`](../skills/logo-and-visual-system-direction/SKILL.md)
- Template: [`../templates/creative-brief-for-generative-media.md`](../templates/creative-brief-for-generative-media.md),
  [`../templates/curation-and-authorship-log.md`](../templates/curation-and-authorship-log.md)
- Best-practice: [`./ai-logo-copyright-is-not-trademark-document-human-authorship.md`](./ai-logo-copyright-is-not-trademark-document-human-authorship.md)

## Provenance

Codifies the RT2/R3 red-team resolution and B16 (Firefly indemnity for imagery). Retrieval 2026-07-13.

---

_Last reviewed: 2026-07-13 by `claude`_
