---
name: publish-digital-collections-and-access
description: Publish a collection online, rights- and cultural-sensitivity-cleared — run the copyright/rights gate and the source-community consultation, decide open-access vs restricted (CC0/CC-BY vs a rights-restricted license, with rights statements), and stand up the IIIF image/presentation stack + DAMS + online catalog + virtual exhibitions, defaulting toward openness where rights allow while cultural sensitivity gates the publish button. Reach for this when the user asks "publish our collection online", "open access or not?", "set up IIIF for our images", or "can we put this culturally sensitive material online?". Used by `collections-and-engagement-specialist` (primary).
---

# Skill: publish-digital-collections-and-access

> **Invoked by:** `collections-and-engagement-specialist` (primary). Also consulted by `museum-operations-lead` where digital access carries an image-licensing or membership-benefit angle.
>
> **When to invoke:** "Publish our collection online"; "open access or rights-restricted?"; "set up IIIF"; "can we put this sensitive material online?"; any move from a catalogued object to a public digital presence.
>
> **Output:** a rights- and sensitivity-cleared publish plan — the open-access/CC decision, the IIIF + DAMS + online-catalog + virtual-exhibition stack, and the access-vs-rights trade-off — with the seams stated.

## Procedure

1. **Run the rights gate first.** Traverse [`../../knowledge/museum-operations-decision-tree.md`](../../knowledge/museum-operations-decision-tree.md) Tree D. Copyright status: **public domain** (openness is on the table), **in copyright but museum holds/clears the rights** (publish under a license), or **in copyright and NOT cleared** (thumbnail/metadata only — clear rights or wait). Never publish a full image you haven't cleared.
2. **Run the cultural-sensitivity gate.** Is the material NAGPRA/culturally sensitive or community-restricted? If yes → **consult the source community**, apply traditional-knowledge (TK) labels, and restrict or contextualize per their guidance. Consent precedes publication — this gate can override "it's public domain".
3. **Decide open access vs restricted.** Where rights and sensitivity allow, **default toward openness** — CC0 / CC-BY for public-domain and rights-cleared works expands mission reach; locking up public-domain works leaves reach on the table. Where display is rights-restricted, publish under a clear license with access terms. Apply standardized **rights statements** (rightsstatements.org / Creative Commons) so users know what they can do.
4. **Stand up the technical stack.** **DAMS** as the source of truth for media; **IIIF** (Image API for deep-zoom + Presentation API/manifests for interoperability) served through a viewer (Mirador / Universal Viewer); the **online catalog** fed from the CMS/DAMS. Name what's already in place vs new.
5. **Extend with virtual exhibitions where they earn their keep** — a reach/audience multiplier for a physical show or a research resource, not a replacement for the object.
6. **State the seams and flip conditions.** Image-licensing revenue or a membership-benefit angle → `museum-operations-lead`; marketing the release → `marketing-operations`. Name the 1-2 facts that would change the plan (e.g., "if the artist's estate declines a license, drop to metadata-only").

## Worked example

> User: "We want to put our whole collection online. Half is pre-1900, some is 20th-century work still in copyright, and a few pieces are Native American ceremonial objects. Open access?"

- **Pre-1900 (public domain):** default to **open access** — CC0 or CC-BY, full IIIF images, rights statement "No Copyright — United States". This is the mission-reach win.
- **20th-century in-copyright:** gate — does the museum hold/can it clear the rights? If cleared → publish under a defined license with access terms; if not → **metadata + thumbnail only** until cleared. Don't publish full images on hope.
- **Native American ceremonial objects:** the **cultural-sensitivity gate overrides** the copyright analysis — consult the affiliated community, apply TK labels, and restrict/contextualize per their guidance; some material should not be displayed at all. Consent before publish.
- **Stack:** DAMS as source of truth → IIIF Image + Presentation APIs → Mirador viewer → online catalog fed from TMS. A virtual exhibition for the pre-1900 highlights.
- **Seam:** image-licensing revenue on the open images → `museum-operations-lead`.

## Guardrails

- The rights gate and the cultural-sensitivity gate run **before** publication — never publish an uncleared full image, never publish sensitive material without source-community consent.
- Default toward **openness where rights and sensitivity allow** — but openness never overrides a community restriction.
- Use standardized **rights statements** (rightsstatements.org / Creative Commons) — don't invent bespoke terms.
- **IIIF + a DAMS source of truth**, not a pile of JPEGs on a web server — interoperability and provenance of the digital asset matter.
- A virtual exhibition extends reach; it does not replace the object or the physical experience.
- Volatile specs (IIIF versions, rights-statement vocabularies, DAMS/viewer features) carry a **retrieval date** and are re-verified before a commitment. See [`../../knowledge/museum-operations-patterns-2026.md`](../../knowledge/museum-operations-patterns-2026.md).
