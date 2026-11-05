# Run the portal review before polish

**Status:** Absolute rule — a portal or signed-in review that has not placed each major block is not done. Visual, accessibility, and form polish do not substitute for that table.

**Domain:** Web design / information architecture

**Applies to:** `web-design`, and any `ux-research` pass that is reviewing an existing portal or public site rather than studying users.

---

## Why this exists

Reviews of the signed-in product kept reporting nav chrome, contrast, and form styling while a tool sat on the wrong route. The motivating miss, `[user-reported 2026-11-05]`, is a card editor left on `/account/site` after `/account/cards/site` already existed. Chrome and accessibility passes do not see that, because the editor can be usable and still be in the wrong product area. Placement has to happen first or it does not happen.

## How to apply

On every portal, signed-in, or mixed public-plus-portal review, open [`../knowledge/portal-and-site-review-checklist-2026-11.md`](../knowledge/portal-and-site-review-checklist-2026-11.md) and fill it in section order.

1. Declare `public` or `signed-in`, and the routes.
2. Report one line per class in the Collab playbook `#review` ([PR #3](https://github.com/mcorbett51090/RavenPower-Collab/pull/3)), or `N/A — reason`. `#placement` is Keep, Move (route and product area), or Remove/redirect, and it is not optional on a portal pass. `#review-out` is `N/A — review-out`.
3. On the Website product, placement ships only when `check-content-placement.mjs` passes for `account/**` and shell/nav files (Website #953). Do not rename that check.
4. A **Block** row stops ship until it passes or the PR waives it with an owner and a reason. A **Record** row is written down and does not by itself stop the merge.

**Do:**

- Name the route and the product area when the verdict is Move.
- Treat a rendered route as the evidence. A component mounted in a unit test is not a pass.
- Hand auth, sessions, deletion, and connectors to `security-reviewer`. This rule does not re-audit them.

**Don't:**

- Call the pass done because focus rings and copy look fine.
- Treat a content-audit KKCR score as a placement verdict.
- Promote a checklist miss into a finding about users.

## Edge cases / when the rule does NOT apply

- A single-discipline task with no page to place: "what is the contrast ratio of these two hexes", "rename this token". Say so in one line. Do not pretend PLACE was run.
- A user study. `ux-research` frames and synthesizes research. If the ask is also a review of the existing UI, run this checklist and keep the two write-ups separate.
- Public marketing with no signed-in surface. Run the public rows (SEO-PUBLIC, RESP-PUBLIC, PERF-CWV, COPY-LEVEL). PLACE still applies to each major section of the page: Keep, Move, or Remove.

## See also

- [Portal and public-site review checklist](../knowledge/portal-and-site-review-checklist-2026-11.md)
- [Information architecture skill](../skills/information-architecture/SKILL.md)
- [UI pattern standing bar](../../ux-research/knowledge/ui-pattern-standing-bar-2026-11.md) — grades from 2026-11-04; this rule does not re-grade them
- [Portal chrome and coding-agent accessibility](../../accessibility-engineering/knowledge/portal-and-agent-accessibility-2026-11.md)

## Provenance

Written 2026-11-05 from the portal-review ask (placement, focus census, form controls, connectors, lag and prefetch, login-bundle ratchet, beta and locked states, org versus user chrome, analytics home, purge). The `/account/site` versus `/account/cards/site` miss is user-reported. Website issue 953 could not be fetched in that session; the public `RavenPowerWebsite` repository did not contain it.

---

_Last reviewed: 2026-11-05_
