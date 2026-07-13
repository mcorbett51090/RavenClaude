# Human curation is not optional

**Status:** Absolute rule
**Domain:** Quality / human-in-the-loop
**Applies to:** `generative-web-media`

> Engineering rule. The gate is a hard blocker in the flow, not a doc suggestion (red-team RT6).

---

## Why this exists

Generative models fail in predictable, sometimes subtle ways — garbled text, wrong anatomy, impossible reflections, off-brand drift — that a metric won't catch but a person will in a glance. An asset that flows straight from generation to production un-reviewed will eventually ship a defect onto a client's live site. A mandatory human selection/approval gate is the cheapest insurance against that, and it is what turns "the model made something" into "we chose to ship this."

## How to apply

- Every asset passes a **human curation sign-off** before production: a person selects which asset(s) ship and records the decision (who / what / when / alt text approved) — the **curation artifact**.
- [`/generate-web-asset`](../commands/generate-web-asset.md) **cannot reach "done"** without the artifact — the gate is a hard blocker in the command flow, not a suggestion.
- Pair curation with anti-slop QA and the WCAG alt-text review in the same gate ([`../skills/curation-and-accessibility-gate/SKILL.md`](../skills/curation-and-accessibility-gate/SKILL.md)).

**Do:** require and record a human sign-off before any asset ships.
**Don't:** auto-publish generated assets, or treat the gate as advisory.

## Edge cases / when the rule does NOT apply

Internal drafts and throwaway exploration don't need a formal sign-off — but the moment an asset is bound for production (especially a client site), the gate is mandatory.

## See also

- [`../skills/curation-and-accessibility-gate/SKILL.md`](../skills/curation-and-accessibility-gate/SKILL.md)
- [`../commands/generate-web-asset.md`](../commands/generate-web-asset.md)

## Provenance

Codifies `brand-and-accessibility-reviewer` house opinion + red-team RT6; grounded in the anti-slop sources (retrieved 2026-07-13).

---

_Last reviewed: 2026-07-13 by `claude`_
