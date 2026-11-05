# A content block stays on the page whose job it is

**Status:** Absolute rule — on every portal or signed-in product UX review, each major content block gets a placement verdict. A pass that only checks chrome, accessibility, and form controls is not finished.

**Domain:** UX / Information architecture

**Applies to:** `web-design` (owns the verdict). `ux-research` records it on an evaluative review of an existing UI and does not treat it as a finding about users.

---

## Why this exists

A page can be navigable, accessible, and well-formed and still hold the wrong work. Chrome, accessibility, and form review all look at what is already on the page. They do not ask whether that block belongs there. The miss that made this a required step was reported on 2026-11-05 `[user-reported]`: the full card editor still lived on `/account/site` after the Site card already had its own route, `/account/cards/site`. Earlier UX passes did not flag it. They had been looking at the nav, the accessibility of the controls, and the forms.

This is a placement rule, not a visual-redesign rule and not a re-grade of the 2026-11-04 UI-pattern capture.

## How to apply

Run this on every portal or signed-in product UX review pass, in the same loop as refreshing the UX and accessibility research those passes already do. Do it before the pass is called done.

1. List the major content blocks on the page. Include forms, builders, editors, tables, share kits, analytics panels, and settings. Shared chrome (the rail, the account menu, the page heading) is not a block for this gate.
2. For each block, ask: **does this block belong on this page, or elsewhere?**
3. Record one verdict. A block with no verdict means the pass is incomplete.

| Verdict | Use it when | What you must name |
|---|---|---|
| **Keep** | The block does this page's job, and this route is the place that job is done. | The page's job, in one line. |
| **Move** | The block is the real tool, and another product area already owns that job. | The product area and the route it moves to. |
| **Remove / redirect** | The block duplicates a tool that already has a route, or it is a leftover from before that route existed. | The route that remains, and that the old one redirects or is deleted. |

**The signature anti-pattern:** a builder or editor on a page whose nav parent is a different product entity. `/account/site` is a site page. A full card editor is the card's tool. Once `/account/cards/site` exists, the editor on the site page is Move or Remove / redirect, not Keep. A summary, a status line, or a link that opens the editor on the card's own route can stay.

```text
Route: /account/site
Page job: settings for this site

| Block                         | Verdict            | Destination                          |
| Full card editor              | Remove / redirect  | /account/cards/site                  |
| Site name and domain settings | Keep               | —                                    |
| Link: Edit site card          | Keep               | opens /account/cards/site            |
```

The routes in that table are the 2026-11-05 example `[user-reported]`. They are not a URL scheme this plugin requires of every product.

**Do:**

- Write the verdict down. "Looks fine" is not a verdict.
- Name the destination route on every Move and every Remove / redirect.
- Re-run the gate when a new route is added for an entity that an older page still edits.

**Don't:**

- Close a UX pass on chrome, accessibility, and form controls alone.
- Keep a second full editor because the page "already has it" and the controls work.
- Collapse placement into a content-quality score. Keep / Consolidate / Rewrite / Retire (the content audit) scores a URL. It does not answer "does this editor belong on this route?"

## Edge cases / when the rule does NOT apply

- **A marketing, legal, or other single-purpose page.** Record `N/A — single-purpose page`. The page has one job; this gate is for a shell that can collect another entity's tool.
- **A pointer, not the tool.** A card, a count, or a link that opens the editor on the owning route is Keep.
- **Settings for this page's own entity.** The site name on the site page stays. The rule moves the other entity's editor, not every field.
- **Greenfield, before any route exists.** Pick the owning route in the IA (see the content-placement decision tree) and do not leave the editor on a parent you already know is the wrong entity.

## See also

- [`../skills/information-architecture/SKILL.md`](../skills/information-architecture/SKILL.md) §8 — the placement procedure inside the IA skill
- [`../knowledge/web-design-decision-trees.md`](../knowledge/web-design-decision-trees.md) — "Content placement — keep, move, or remove a block"
- [`../skills/content-audit/SKILL.md`](../skills/content-audit/SKILL.md) — KKCR scores the URL; it does not place a block
- [`../../ux-research/knowledge/ui-pattern-standing-bar-2026-11.md`](../../ux-research/knowledge/ui-pattern-standing-bar-2026-11.md) — the portal-walk checklist cross-reference (a placement row is QA, not a user finding)

## Provenance

House rule added 2026-11-05 from an owner-reported portal miss `[user-reported]`: the full card editor remained on `/account/site` after `/account/cards/site` already existed. Prior UX passes missed it because they reviewed nav chrome, accessibility, and forms. This file is the checklist item those passes now run every loop. It does not re-grade the 2026-11-04 UI-pattern capture, and it does not claim a user study.

---

_Last reviewed: 2026-11-05 by `cursor`_
