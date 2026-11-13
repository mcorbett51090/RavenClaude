# Place page content before polishing chrome

**Status:** Absolute rule — on a signed-in portal UX pass, every major block has a verdict before chrome changes. "The nav looks fine" without that inventory is not a pass.

**Domain:** Web Design — information architecture, signed-in product UI

**Applies to:** `web-design`. Portal-review checklists in other plugins link here; they do not restate the pass.

---

## Why this exists

A signed-in portal can grow a second home for a tool. Navigation is updated to a dedicated route, and the old page keeps the editor. The next UX pass then restyles the leftover and reports the rail as healthy.

The reported miss `[user-described 2026-11-05]`: a card editor was still on `/account/site` after navigation already pointed card editing at `/account/cards/site`. This rule did not open that product. The routes are an example of the shape, not a URL scheme to copy. No user study measured the miss. The procedure is the point.

## How to apply

On every signed-in portal UX pass, before type, color, spacing, or motion, inventory each major block from the rendered page:

| Verdict | Required name |
|---|---|
| **Keep** | The job this page owns, in a few words. |
| **Move** | Route and product area. The old page keeps a link, not a second editor. |
| **Remove/redirect** | Where the person lands. Remove the block if the page stays. Redirect the URL if the URL itself is the duplicate. |

Walk signed in, and open every route the rail, account menu, and in-page tabs can reach. The full pass, the five process steps, and the copy-paste checklist are in [`../knowledge/content-placement-page-ia-2026-11.md`](../knowledge/content-placement-page-ia-2026-11.md).

**Do:**
- Write the table into the pass notes before the diff.
- Move an editor to the route the nav already names, and delete it from the old page.
- Record `N/A — no signed-in routes` on a marketing-only site, or `N/A — not a portal UX pass` on a one-line copy fix.

**Don't:**
- Polish an editor that the nav has already given its own route.
- Sign off a portal UX pass from the rail alone.
- Score account-page blocks with the marketing KKCR matrix (Keep / Consolidate / Rewrite / Retire).

## Edge cases / when the rule does NOT apply

- A hub may **Keep** a summary or a status line. It may not **Keep** the editor those rows link to.
- Greenfield with no routes yet: design the sitemap first ([`../skills/information-architecture/SKILL.md`](../skills/information-architecture/SKILL.md)). Run this pass once the signed-in routes exist, including the first implementation.
- A written reason can **Keep** a duplicate control that is not an editor (a compact status that deep-links). An editor or builder needs the owner route. "We might need it here too" is not a reason.

## See also

- [`../knowledge/content-placement-page-ia-2026-11.md`](../knowledge/content-placement-page-ia-2026-11.md) — the pass, the worked row, the checklist
- [`../templates/site-architecture.md`](../templates/site-architecture.md), [`../templates/launch-checklist.md`](../templates/launch-checklist.md) — where a portal review records the table
- [`../../ux-research/knowledge/ui-pattern-standing-bar-2026-11.md`](../../ux-research/knowledge/ui-pattern-standing-bar-2026-11.md) — portal-walk QA rows; not a study
- [`../skills/content-audit/SKILL.md`](../skills/content-audit/SKILL.md) — KKCR is a different matrix
