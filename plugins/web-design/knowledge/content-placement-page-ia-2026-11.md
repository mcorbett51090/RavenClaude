# Content placement — page-content IA for a signed-in portal (2026-11-05)

> **Last reviewed:** 2026-11-05. **Confidence:** high that the pass below is the house procedure; the worked miss is `[user-described]`, not a page this file opened. This is a process addendum for coding agents. It is not a user study, and it does not re-grade the 2026-11-04 capture.

Read this before a signed-in portal UX pass, and before polishing chrome on an account page. The citable rule is [`../best-practices/place-page-content-before-polishing-chrome.md`](../best-practices/place-page-content-before-polishing-chrome.md). A portal-review checklist that is only an example, not research, lives in [`../../ux-research/knowledge/ui-pattern-standing-bar-2026-11.md`](../../ux-research/knowledge/ui-pattern-standing-bar-2026-11.md) § "Portal walk".

## When the pass runs

Run it on **every signed-in portal UX pass**: layout, information architecture, navigation, "clean this account page up", a visual review, or any change that adds, moves, or restyles a major block.

A one-line copy fix or a bugfix that does not change what the page is for records `N/A — not a portal UX pass`. That note does not excuse the next pass.

A change to a single account page that is not framed as a full pass still inventories **that page** and **any route the nav already dedicates to the same block**, before type, color, spacing, or motion.

## Verdicts

One row per major block, taken from the **rendered** page (a block that is mounted and visible counts, even if the task did not mention it).

| Verdict | Use it when | What you must name |
|---|---|---|
| **Keep** | This block's job is this page's job. | Nothing. Say what job it serves, in a few words. |
| **Move** | The job already has a route, or it belongs in a named product area. | The route **and** the product area (`/account/cards/site` — Cards). This page does not keep a second copy of the block. |
| **Remove/redirect** | The block should not be on this page. | Where the person lands. **Remove** if the page stays and only the block goes (leave a link when the job still exists elsewhere). **Redirect** if the URL itself is the duplicate (301 or an in-app replace, one hop). |

Do not use the content-audit KKCR matrix here (Keep / Consolidate / Rewrite / Retire). That matrix scores whole marketing URLs. This one scores blocks on a signed-in page. Do not paste either matrix onto the other job. See [`../skills/content-audit/SKILL.md`](../skills/content-audit/SKILL.md).

A row with no verdict, or a Move / Remove/redirect that does not name a route or product area, is an unfinished pass.

## Anti-pattern — the editor left behind

Navigation already points at a dedicated route for an editor or builder. The editor is still on another page. Agents then polish the leftover (spacing, type, empty states) and report that the nav looks fine.

**Reported miss** `[user-described 2026-11-05]`. This file did not open the product. Matthew described a card editor still on `/account/site` after navigation already pointed card editing at `/account/cards/site`.

| Block | Verdict | Destination | What `/account/site` keeps |
|---|---|---|---|
| Card editor (fields, preview, save) | **Move** | `/account/cards/site` — Cards | A link to that route, such as "Edit cards". Not a second editor. |

Other blocks on `/account/site` still need their own rows. This file does not inventory a product it did not open. Site settings that are about the site, not about cards, are **Keep** only after someone looks at the rendered page and says so.

The same test applies wherever the product's nav already chose an owner route. `/account/...` is the shape of the report, not a URL scheme every product must copy.

**Fail:** the editor is still rendered on the old page. Restyling it is not a Move.

## Checklist (copy into a portal review)

Walk **signed in**. Open every route the signed-in nav can reach: the rail, the account menu, and in-page tabs. The 2026-11-04 example walk found Cards opened from the account menu and highlighted nothing in the rail — menu destinations are in scope. A product whose account area is `/account` walks every `/account` page, not a sample.

For each route:

- [ ] Major blocks listed from the rendered page, one row each.
- [ ] Each row is **Keep**, **Move** (route + product area), or **Remove/redirect** (landing route named).
- [ ] No editor or builder remains on this page when the rail, account menu, or a tab already has a dedicated route for it.
- [ ] A Move leaves a link on the old page when the job still exists. It does not leave the tool.
- [ ] The table is written **before** chrome diffs (type, color, spacing, motion, empty-state polish).
- [ ] "The nav looks fine" is not the review. The table is the review.

```
| Route | Block | Verdict | Destination (route — product area) | Old page keeps |
|---|---|---|---|---|
| /account/site | Card editor | Move | /account/cards/site — Cards | Link only |
```

## Process optimizations agents follow

These five are house procedure `[inference]`, drawn from the miss above: a correct nav and a wrong page body can ship in the same pass. They are not measured findings.

1. **Placement before chrome polish.** Write the verdict table before changing type, color, spacing, or motion. A polished editor on the wrong route is still the wrong page.
2. **Signed-in walk of every account page.** On a portal UX pass, open every signed-in route the nav can reach, signed in, including account-menu destinations. Do not review only the URL named in the task.
3. **No "nav looks fine" without a content inventory.** A labeled rail, a current-location mark, and an aligned icon do not show that the body belongs on that URL.
4. **One editor, one route.** If navigation already names a dedicated route for a builder, remove that builder from every other page. Leave a link to the owner route.
5. **Name the destination before the diff.** Move and Remove/redirect rows name the route and the product area in the pass notes before code changes. "Move this somewhere" is not a verdict.

## What this file is not

- Not the sitemap skill ([`../skills/information-architecture/SKILL.md`](../skills/information-architecture/SKILL.md)). That designs URLs and nav. This checks that each URL's body matches the nav you already shipped.
- Not a research grade. Do not file the table as a usability finding. [`ux-research`](../../ux-research/knowledge/ui-pattern-standing-bar-2026-11.md) may cite the checklist as QA. It must not promote the miss to solid, provisional, or a study result.
- Not a patch for a product repository. Apply the pass on the next portal UX change. Do not invent blocks that were not on the rendered page.
