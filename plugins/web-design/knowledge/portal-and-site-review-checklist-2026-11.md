# Portal and public-site review checklist

> **Last reviewed:** 2026-11-05. **Confidence:** high that the rows below are the review this plugin now requires; low that any row is a finding about users. This is a QA and engineering checklist. It is not a study.
>
> **Read this before** a portal UX pass, a signed-in product review, or a public-site launch review that sits next to a signed-in app. Placement is section PLACE. Do that section before SHELL, A11Y, FORM, or visual polish. A pass that reports contrast and copy and has no placement table is not done.
>
> **Not this file:** the graded UI-pattern capture ([`../../ux-research/knowledge/ui-pattern-standing-bar-2026-11.md`](../../ux-research/knowledge/ui-pattern-standing-bar-2026-11.md)) and the chrome markup bar ([`../../accessibility-engineering/knowledge/portal-and-agent-accessibility-2026-11.md`](../../accessibility-engineering/knowledge/portal-and-agent-accessibility-2026-11.md)). Do not re-grade them. Do not reconstruct the missing 109-claim extract. A row here is a design or engineering check. It is not evidence about users.

Fail cells are examples of a miss. They are criteria for the review, not a report that a live product currently behaves that way.

## How to run a pass

The class list is the Collab playbook heading `#review` ([RavenPower-Collab PR #3](https://github.com/mcorbett51090/RavenPower-Collab/pull/3)): one line per class, `pass`, `fail`, or `N/A — reason`. A blank line is a miss. This file does not publish a second list of class titles. This session could not open that repository (not-found from the token in use), so the titles stay in the playbook. Do not invent an extra class to fill a count.

`#placement` is the hard IA gate. On a portal or signed-in pass it is not `N/A`. Each major block is **Keep**, **Move** (route and product area), or **Remove/redirect** (the route that remains). Write that table before any other class.

`#review-out` is the list of deliberate non-goals. Each of those is `N/A — review-out`, with the playbook's reason. Do not add a check for them, and do not let a section below override that.

1. **Name the surface** in the first line: `public` or `signed-in`, plus the routes this change touches.
2. **Walk `#review` in the playbook's order.** Placement first. The sections below are the expansion for classes this marketplace already had a concrete miss for. If the playbook marks one of them `#review-out`, stop at `N/A — review-out`.
3. **One line per class.** Evidence is a route, a width, or a test name.
4. **Ship** means:
   - **Block** — the product change does not ship until the row passes, or the PR waives it with an owner and a reason.
   - **Record** — write the verdict. A fail is a finding. It does not by itself stop the merge.
5. **Rendered, not mocked.** A check counts only when something loads the route (or the built HTML) and asserts the condition. A unit test that mounts the component alone does not count. This marketplace has no symbol named `real_test` (repository search on the review date). Use that name in the product repo if it already means "rendered route"; do not invent the helper here.

The product repository owns the CI. This marketplace states the assertion. It does not ship Website product code.

## Evidence

| Label | What it means here |
|---|---|
| House rule already in this plugin | Cited inline. Follow it. |
| User-reported on the review date | Stated in the ask that commissioned this file. Not a crawl of a live product. |
| Inference | A house default with no user study behind it. |
| Capture grade | Solid or provisional rows from the UI-pattern files. The grade stays on the row. |

**Website #953.** The ask calls content placement a hard merge gate on Website #953. This session could not open that issue: the public repository `mcorbett51090/RavenPowerWebsite` has a README and no issue 953. Treat "hard gate" as user-reported, not as a fetched issue body.

**In-flight siblings, not dependencies.** Draft PR #1411 (settings controls) and PR #1412 (placement-only rule) were open while this file was written and are not merged into this text. If they land, they are the longer write-ups. They do not replace this list. If they disagree with a row here, re-read both and do not silently pick one.

## PLACE — content placement (first)

Every major block on each touched route gets one verdict. Blocks include forms, builders, editors, tables, share kits, analytics panels, and settings groups. Chrome, contrast, and control styling do not answer this section.

| Verdict | When |
|---|---|
| **Keep** | The block does this page's job, and this route is where that job is done. |
| **Move** | The block is the real tool. Name the product area and the route. |
| **Remove / redirect** | Duplicate or leftover. Name the route that remains. |

| ID | Check | Look for | Fail | Pass | Ship |
|---|---|---|---|---|---|
| PLACE-BLOCK | One verdict per major block | The page's job, the nav parent, breadcrumbs, and the URL agree | Fails when the card editor is still mounted on `/account/site` while the Site card editor route is `/account/cards/site`. The nav parent is account-site; the tool belongs to Cards | Editor imports exist only under `/account/cards/site`. `/account/site` keeps account-level site settings, or redirects | **Block** |
| PLACE-DUP | One home per tool | The same editor, share kit, or analytics panel is not mounted on two routes | Fails when the editor renders on both routes, so one of them is the wrong parent | The surviving route is named; the other redirects or is gone | **Block** |
| PLACE-CRUMB | Parents match | Rail, breadcrumb, and URL name the same parent | Fails when the breadcrumb says Account, then Site, while the page is the card editor | Breadcrumb, rail highlight, and URL share one product area | **Block** when they name different objects. **Record** when they are the same object with different wording (see COPY-SAME) |

**Ship gate (placement).** On the Website product the check is `check-content-placement.mjs` (Website #953). It covers `account/**` and shell/nav files. A diff that touches those paths does not ship while that check fails. Prose review uses the same Keep / Move / Remove table. Do not invent a second script name for this gate. This plugin does not add the script to a product repo.

KKCR in [`content-audit`](../skills/content-audit/SKILL.md) scores a URL. It does not place a block. Do not treat a content-audit verdict as a placement verdict.

## SHELL — chrome, context, navigation

Solid chrome rules (labeled persistent rail, disclosure buttons, current location) stay in the accessibility-engineering file. Apply them. The rows here are the ones that file does not already decide.

| ID | Check | Look for | Fail | Pass | Ship |
|---|---|---|---|---|---|
| SHELL-IN | A visible destination lands in the shell | Every rail or account-menu item the persona can see | Fails when a visible item paints a bare "Not found" with no rail and no way back. The UI-pattern walk's example was a Forms item visible to every persona unless the account owned an org | The item is hidden, or the shell explains the missing role or prerequisite | **Block** |
| SHELL-CURRENT | Current location off the rail | Pages opened from the account menu or a deep link | Fails when Cards, opened from the account menu, highlights nothing, or Profile, security, connectors, and sessions have no current-item cue | The current item is visible and exposed to assistive tech. More than one `aria-current` is not itself a fail (discarded claim) | **Block** |
| SHELL-ORG | Org context and user context are different controls | The header says which org and which person, and switching one does not pretend to switch the other | Fails when one menu changes the org name and the signed-in person, or the org name changes while the list is still the previous org's rows | Org switch reloads org-scoped data. A user-scoped page (profile) stays on that person. The URL drops the previous org's record id | **Block** |
| SHELL-PAINT | The shell paints before the page data | Navigation updates the rail and the heading without waiting for the destination payload | Fails when the click waits on the editor bundle and the data before the heading changes, and the old page stays interactive | Heading and current-item update immediately. The content region shows a skeleton the size of the block it replaces (solid skeleton rule) | **Block** for a full-screen spinner that removes the shell on an in-app navigation. **Record** for the first load after login |
| SHELL-SKELETON | Skeleton matches the content | Width and height of the loaded block, including media | Fails when a short bar stands in for a tall card | The reserved box matches the loaded block. Do not invent a generic timing number; Primer's milliseconds were not in the UI-pattern notes | **Block** |
| SHELL-PALETTE | Command palette or in-app search, if one exists | Results and navigation stay in the current org | Fails when the palette lists another org's records, or activating a result drops the shell | `N/A` when there is no palette. Otherwise results are scoped and land in the shell | **Block** when a palette exists |

## A11Y — accessibility

Floor is WCAG 2.2 AA unless the product named another target. Procedure: [`accessibility-review`](../skills/accessibility-review/SKILL.md). Contrast math: `scripts/contrast_ratio.py`. Text on a photo: [`text-over-photo-contrast-2026.md`](text-over-photo-contrast-2026.md). Do not mark AA failed solely on an AAA criterion (2.4.13 Focus Appearance, 2.3.3 Animation from Interactions, 2.5.5 Target Size Enhanced).

| ID | Check | Look for | Fail | Pass | Ship |
|---|---|---|---|---|---|
| A11Y-CENSUS | Focus census | At the width under test, tab order versus what is visible | Fails when the desktop rail and the closed mobile drawer are both in the tab order, a visible control is skipped, or a control can be focused while its container is hidden | The census lists each visible control once. Hidden navigation is `inert` or out of the tab order. A positive `tabindex` is not the fix | **Block** |
| A11Y-RING | Visible focus | A ring on the control, against the actual background, in each theme the product ships | Fails when the outline is removed and nothing replaces it, or the ring matches the card color | Focus is visible (2.4.7). Where the ring is the component boundary, it meets 3:1 against adjacent colors (1.4.11) | **Block** |
| A11Y-OBSCURED | Focus not covered | Sticky bars, the rail, and a save footer | Fails when the focused field sits under the sticky save bar | The focused item is not entirely hidden (2.4.11) | **Block** |
| A11Y-KEYS | Keyboard operation | Disclosures, sheets, and dialogs | Fails when a mouse opens the connector sheet and the keyboard cannot activate it, closing the sheet leaves focus on the document body, or Escape leaves the sheet open | Native button, focus trapped in the dialog, focus restored on close, no trap | **Block** |
| A11Y-NAME | Names | Accessible name on every control; visible text is not replaced by a different `aria-label` | Fails when the placeholder is the only label, or primary nav is icon-only | Persistent label (1.3.1). Primary rail items have visible text | **Block** |
| A11Y-CONTRAST | Contrast | Token pairs and text on photos | Fails when body text is under 4.5:1, or UI is under 3:1, measured on the wrong background. Photo text reported as a pass because a token pair passed | `contrast_ratio.py` on the displayed colors. Photo text measured, or reported as not measured | **Block** |
| A11Y-TARGET | Target size and field text | The 400px signed-in width | Fails when a target is under 24 by 24 CSS px (2.5.8) with no spacing exception, or an input is under 16px so a phone zooms on focus | Targets meet 2.5.8. Form text is at least 16px. 44px is AAA or a platform stretch, not the AA floor | **Block** for 24px and 16px text. **Record** for 44px |
| A11Y-LIVE | Status messages | Save, error, and org-switch announcements | Fails when "Saved" is only a visual string and a screen reader hears nothing (4.1.3) | The status is a live region, or the control's name changes to the new state | **Block** |
| A11Y-MOTION | Reduced motion | Interaction-triggered motion, including view transitions and skeleton shimmer | Fails when motion has no `prefers-reduced-motion` fallback | Motion is gated. 2.3.3 stays AAA and is not an AA fail by itself | **Block** for the fallback. **Record** for 2.3.3 |
| A11Y-PURPOSE | Input purpose | Login and profile fields that collect the person's own data | Fails when email and password inputs have no `autocomplete` token (1.3.5) | Tokens match the field (`email`, `current-password`, `new-password`, `name`) | **Block** on those fields |

**Focus-census gate.** Load the route signed in. Collect elements in the tab order (not `inert`, not `disabled`, not `hidden`, not `display: none`, not `visibility: hidden`, tabindex at least 0). Fail on a duplicate, a visible control left out of the list, or a control whose ancestor is closed. `layout-probe.js` already checks focus-ring contrast on a rendered page; it does not replace this census.

## FORM — forms and controls

House form rules: [`ux-form-design-and-error-handling.md`](../best-practices/ux-form-design-and-error-handling.md) (validate on blur, inline error, a dead submit control is not the pattern). The Baymard trio in the UI-pattern file is **provisional**: once an error is showing, re-check on input so a fix clears it, and show positive validation. That does not repeal "do not validate on every keystroke before the field has been blurred or submitted." Both can be true. Do not fail a form that only validates on blur.

Builders that publish use the header in [`visual-builder`](../skills/visual-builder/SKILL.md): "Saved · Unpublished changes". Settings that commit in place use FORM-SAVED below. Do not collapse those two strings.

| ID | Check | Look for | Fail | Pass | Ship |
|---|---|---|---|---|---|
| FORM-CHOICE | Small, known choice sets | A closed list of about five or fewer options | Fails when a theme control is a dropdown of three options, each option a sentence, with a help paragraph under the closed control | Tiles, a segmented control, a switch, or a slider that shows the live value. Extra explanation is a toggletip, not a paragraph | **Record**. Inference: no study in this repo shows tiles beat dropdowns. Do not block a merge on this row alone |
| FORM-TIP | Where the meaning lives | Label, caption, and any hover text | Fails when the only explanation is a hover tooltip that disappears, and it fails 1.4.13 (not dismissible, hoverable, and persistent) | Visible label plus a short caption. A tooltip that carries meaning meets 1.4.13, or the meaning is in the caption | **Block** for 1.4.13. **Record** for "prefer a toggletip" |
| FORM-SAVED | Save state | The commit control on a settings or editor form | Fails when the button still says Save after the server accepts, or it says Saved before the server accepts and then reverts. A toast vanishes and the control looks idle | The control says Save while dirty. After the server accepts, it reads `Saved · HH:MM` in the viewer's clock and stays until the next edit. The clock convention (12- or 24-hour) is the product's, stated once | **Block** |
| FORM-DIRTY | Leave with unsaved edits | Navigation, org switch, and tab close on an editor | Fails when edits vanish with no prompt | The product asks, or it has already saved and FORM-SAVED shows the time | **Block** on editors and builders. **Record** on a single settings switch that commits on change |
| FORM-DOUBLE | In-flight create | The primary create action | Fails when two clicks create two records | Further clicks during the request do not create a second record, or the write is idempotent | **Block** on creates |
| FORM-ERROR | Error text | Association and the fix | Fails when the only signal is a red border, or a modal that drops the field | The message names the fix, sits on the field, and is referenced by `aria-describedby` | **Block** |
| FORM-CONFLICT | Two writers | A builder that can overwrite | Fails when the last write wins silently | The conflict is shown. **Record** on a settings page with no shared draft | **Block** only when the surface is a shared builder |

Draft #1411 is the longer control-ladder note if it merges. Until then, FORM-CHOICE and FORM-TIP are the review rows.

## CONNECT — multi-account connectors and OAuth

Pattern the ask named: a connect-apps sheet that can hold more than one account, in the manner of a bot's connect sheet. This session did not capture that product's UI. Do not block a review for failing to match an unseen layout. Block the behaviors below.

Handoff, do not re-derive: [`auth-identity`](../../auth-identity/skills/oauth-oidc-flow-design/SKILL.md) for the flow, and `ravenclaude-core` `security-reviewer` when the diff touches tokens. Authorization code with PKCE for a public client. No implicit flow. Redirect URIs match exactly.

| ID | Check | Look for | Fail | Pass | Ship |
|---|---|---|---|---|---|
| CONNECT-LIST | More than one account | The sheet lists linked accounts for the provider | Fails when one "Connected" boolean is the whole UI, and connecting again replaces the previous account with no list | Each account is a row: who, which product area it feeds, and a disconnect that names that account | **Block** |
| CONNECT-SCOPES | What is granted | Human words for the scopes, on the sheet, before the provider window | Fails when "Connect" states no read or write access | The sheet names the access in product language. The provider's own consent screen still appears | **Block** |
| CONNECT-RETURN | Coming back | Allow-listed return path inside the shell | Fails when a deny or a provider error paints a bare page with no shell, a return parameter can leave the origin, or a token or authorization code remains in the portal query string | Deny and error return to the sheet and say what happened. The return path is allow-listed. Secrets stay out of the URL | **Block** |
| CONNECT-REVOKE | Disconnect | The provider grant and the local row | Fails when disconnect hides the row and leaves a usable token | The review names the revocation call. A later read with the old token is refused | **Block** when the diff touches disconnect |
| CONNECT-DIALOG | The sheet is a dialog | Role and focus | Fails when the account list uses `role="menu"`, or focus is not restored | A dialog, labeled, dismissed with Escape, focus restored | **Block** |

## PERF — performance

Field budgets this plugin already uses (LCP 2.5s, INP 200ms, CLS 0.1 at the 75th percentile) live in [`core-web-vitals-tuning`](../skills/core-web-vitals-tuning/SKILL.md) and [`web-platform-capabilities-2026.md`](web-platform-capabilities-2026.md). The UI-pattern capture does not newly verify them. Cite those files, not the capture, when a document needs a source.

| ID | Check | Look for | Fail | Pass | Ship |
|---|---|---|---|---|---|
| PERF-LOGIN | Login entry ratchet | The JS and CSS of the login route only | Fails when the login chunk imports the signed-in shell, an editor, or a chart library, or the gzip size grew and the PR does not say why | Login is its own entry. A committed baseline exists. A growth names the reason in the PR. If no baseline exists yet, this row stays fail until the PR that touches login adds one | **Block** when the diff touches the login route or shared root. **N/A** otherwise, with that sentence |
| PERF-LAG | Transition lag | Shell versus data, as in SHELL-PAINT | Fails when the rail click stays idle until the destination's JavaScript finishes | The shell updates first. Long tasks on the click are an INP finding for `performance-engineer` | **Block** when the shell does not update first |
| PERF-PREFETCH | Prefetch of the likely next view | Hover or speculation rules on rail destinations | Fails when a logout, delete, OAuth start, or other mutating URL is prefetched, or a safe rail link stays cold until the click | Safe GET navigations may prefetch ([`web-platform-capabilities-2026.md`](web-platform-capabilities-2026.md) Speculation Rules, or the framework's link prefetch). Mutating URLs do not | **Block** for prefetch of a mutating URL. **Record** for a cold safe link |
| PERF-CWV | Public field budget | Marketing and other public templates that declared a budget | Fails when a public launch is over the declared LCP, INP, or CLS budget with no written justification | The budget is the one written at discovery, measured in the field when field data exists | **Block** on a public launch. **Record** on a signed-in route unless that route has its own written budget |
| PERF-SW | Service worker and back-forward cache | Authenticated HTML and logout | Fails when a service worker serves account HTML from cache after logout, or the back button shows the previous person's data | Authenticated HTML is not stored as a static asset. Logout clears the view; back does not show the previous account | **Block** |

## SEC — security, sessions, purge

This section records the handoff. It is not a second security review. `security-reviewer` is mandatory when the diff touches auth, sessions, user data, connectors, payments, upload, or deletion. `auth-identity` owns cookie flags, PKCE, redirect URIs, localStorage token bans, and CSRF for cookie sessions. Do not paste exploit steps into the review.

| ID | Check | Look for | Fail | Pass | Ship |
|---|---|---|---|---|---|
| SEC-HANDOFF | The right reviewer saw it | A named handoff when the diff is in scope | Fails when the UX pass approves a connector or a delete with no security review | The review names `security-reviewer` and, for the flow, `auth-identity`, or it says `N/A` because the diff touches none of the in-scope kinds | **Block** when in scope |
| SEC-URL | Secrets out of the URL | Query and hash | Fails when an access token, refresh token, email, or session id is in the query string | Resumable UI state (tab, filter, open record id that is not a secret) may be in the URL | **Block** |
| SEC-ORG | Old org id is not a read | After an org switch, replay of the previous id | Fails when the URL or a cached request still returns the previous org's record | The server refuses the id for the new context. The client drops it | **Block** when the diff touches org-scoped reads |
| SEC-PURGE | Every copy | The PR lists stores when it deletes, exports, disconnects, or closes an account | Fails when account removal clears the user row and the next login still shows a cached org list, a search hit, or an analytics profile | The PR names primary store, cache, search, analytics, exports, sessions, and provider tokens. A test reads each after the delete and finds no row | **Block** when the diff deletes or exports. **N/A** with that sentence otherwise |
| SEC-LEAK | Errors and traces | The rendered error | Fails when a stack trace, a SQL string, or another person's row appears on an error or locked state | The shell shows a recovery action. Details stay in the server log | **Block** |
| SEC-EXPORT | Export scope | A download or share kit | Fails when an export includes another org, or a public share image is built from private card content | Export and any public preview are limited to what this context may show. Private content is not a share card | **Block** when the diff touches export or share |

## RESP — responsive

| ID | Check | Look for | Fail | Pass | Ship |
|---|---|---|---|---|---|
| RESP-PORTAL | Signed-in widths | 400px and 1280px on each touched portal route, while signed in | Fails when, at 400px, the rail covers the editor and the control cannot be reached, or at 1280px the rail's current item and the page disagree | Both widths exercised. What was clicked is in the note | **Block** on touched portal routes |
| RESP-PUBLIC | Public matrix | The device matrix in [`adaptive-layout`](../skills/adaptive-layout/SKILL.md), including 320px reflow (1.4.10) | Fails when a public launch was checked only in a desktop window | The matrix ran, or the waiver names the viewports skipped | **Block** on a public launch. Do not demand the full viewport matrix on a portal settings tweak; RESP-PORTAL is the portal bar |
| RESP-ZOOM | Zoom | 200 percent text (1.4.4) and no zoom lock | Fails when the viewport sets `user-scalable=no` or a `maximum-scale` below 2 | The viewport tag does not lock zoom | **Block** |

400px is the signed-in walk width from the ask. It is not a WCAG number. 320px remains the reflow width for public pages.

## STATE — empty, error, locked, beta

The UI-pattern walk's note that flag-off routes answer with a not-found page by design is an observation about that fixture. Read the flag before filing a not-found as a bug.

| ID | Check | Look for | Fail | Pass | Ship |
|---|---|---|---|---|---|
| STATE-EMPTY | Nothing here yet | A first-run or zero-row page | Fails when the page is a blank card, or it says "No items" with no action | One next step, inside the shell | **Block** |
| STATE-ERROR | The request failed | Retry, inside the shell | Fails when the response is a bare status page, or another context's rows stay on screen | The shell stays. The message names a retry. Partial data is not the previous org | **Block** |
| STATE-LOCK | Why it is locked | Role, plan, and missing prerequisite are different sentences | Fails when a visible rail item has no shell, or a plan lock says "forbidden" with no upgrade or request path | Hidden, or explained in the shell with the specific lock (role, plan, or missing site) | **Block** |
| STATE-BETA | Flag off | Direct URL and the nav | Fails when the nav shows a beta item whose URL has no shell, or the review calls a designed flag-off not-found a bug without reading the flag | The PR states the contract: hidden, locked-in-shell, or not-found. The nav matches that contract | **Block** when the diff touches the flag or the nav item. **Record** the contract otherwise |
| STATE-LOADING | Waiting | Skeleton, not a second shell | Fails when the shell unmounts while data loads | SHELL-PAINT and SHELL-SKELETON pass | **Block** |

## ANALYTICS — instrumentation lives in the product area

House pair: GA4 (consent mode, denied by default) plus Cloudflare Web Analytics, as one inventory line. GA4 does not auto-fire on an authenticated surface without sign-off and URL redaction. See [`third-party-script-hygiene`](../skills/third-party-script-hygiene/SKILL.md).

| ID | Check | Look for | Fail | Pass | Ship |
|---|---|---|---|---|---|
| ANALYTICS-HOME | The event's home | Event name, product area, and the route that emits it | Fails when `card_edited` fires from `/account/site`, so the cards area has no record of the edit | The emitting route is in the placement map's area for that event | **Block** when the diff adds or moves an event |
| ANALYTICS-AUTH | Authed traffic | Whether GA4 is on the signed-in layout | Fails when GA4 loads on account routes with no sign-off | The authed layout does not inject GA4 unless the exception is written. Cloudflare may remain the pageview baseline | **Block** |
| ANALYTICS-PII | Payload | Query, titles, and properties | Fails when an email, a token, or a document body is on the event | Identifiers are the product's own ids, documented. No secrets | **Block** |
| ANALYTICS-PUBLIC | Public consent | Marketing pages | Fails when a non-essential tag fires before consent in the EU | The launch-checklist consent rows pass | **Block** on a public launch that adds a tag. **N/A** on a portal pass that did not change public tags |

## COPY — naming and wayfinding

| ID | Check | Look for | Fail | Pass | Ship |
|---|---|---|---|---|---|
| COPY-SAME | One name | Rail, `h1`, document title, and empty state | Fails when the rail says "Members", the heading says "Members area", and the document title is "App" on every route | The same words for the same object. The document title includes the page | **Block** when the names refer to different objects, or every route shares one title. **Record** for a wording drift that is still the same object |
| COPY-ACTION | The verb | Buttons | Fails when a settings write says "Submit" or "Click here" | The verb is the action ("Save", "Connect Google") | **Block** for "click here" (2.4.4). **Record** for "Submit" where FORM-SAVED already applies |
| COPY-LEVEL | Reading level | Public marketing copy | Fails when a public launch has no stated grade ceiling | `scripts/flesch_kincaid.py` against the discovery ceiling | **Block** on public primary-flow copy. **N/A** as a portal ship gate. Invite dropping this row from portal reviews |

## SEO — public pages and the portal are different checks

| ID | Check | Look for | Fail | Pass | Ship |
|---|---|---|---|---|---|
| SEO-PUBLIC | Indexable pages | Title, description, canonical, one `h1`, sitemap, OG on pages meant to be shared | Fails when a marketing page is marked noindex, or a share has no card | [`seo-technical-audit`](../skills/seo-technical-audit/SKILL.md) passes. `llms.txt` is not a launch gate | **Block** on a public launch |
| SEO-PORTAL | Signed-in routes stay out of the index | Sitemap, robots, and the response | Fails when an account route is in the sitemap, or the HTML is indexable and includes user content | Portal prefixes are kept out of the sitemap and send noindex, or the document is not publicly reachable. The title still exists for the browser tab | **Block** |
| SEO-STATUS | Status codes | Public missing page and a retired URL | Fails when a missing public page answers success, or a moved URL has no permanent redirect | A missing public page answers not-found. A retired URL redirects in one hop | **Block** on a public launch or a redirect change |
| SEO-AEO | Answer-engine extras on the portal | `llms.txt`, JSON-LD of user records | Fails when a portal review treats a missing `llms.txt` as a ship block, or private records are published as public JSON-LD | Public marketing may add `llms.txt` as insurance. The portal does not | Do not block. Invite discarding SEO-AEO as a portal row |

## Gates — what CI should enforce

| Row | Already in this plugin | What the product repo adds |
|---|---|---|
| PLACE-BLOCK, PLACE-DUP | This checklist | `check-content-placement.mjs` on `account/**` and shell/nav files (Website #953). No other script name |
| A11Y-CENSUS | Procedure above. Not a script in this repo | Rendered-route tab census |
| A11Y-RING, A11Y-CONTRAST | `layout-probe.js`, `contrast_ratio.py`, device matrix | Run them on the touched routes |
| A11Y-KEYS, CONNECT-DIALOG | `accessibility-review` Pass 3 | Rendered-route keyboard script for the sheet |
| FORM-SAVED, FORM-DIRTY | This checklist | Rendered-route test: dirty, save, assert the `Saved ·` text, then navigate away |
| PERF-LOGIN | None | Gzip ratchet on the login entry, plus a forbidden-import list |
| PERF-PREFETCH | None | Mutating URLs have no prefetch |
| PERF-SW | None | After logout, back does not show the previous account |
| SEC-PURGE | None | After delete, each named store reads empty |
| SEO-PORTAL, SEO-PUBLIC | `seo-technical-audit` is a manual skill | Sitemap and robots test: portal prefixes out; public URLs answer success |
| ANALYTICS-AUTH, ANALYTICS-HOME | Prose in `third-party-script-hygiene` | Authed layout does not inject GA4; the event emitter's route is in the event's area |
| STATE-LOCK, STATE-BETA, STATE-EMPTY | None | Fixture personas: empty, role-locked, plan-locked, flag-off |
| RESP-PORTAL | Device matrix is built for public pages | Signed-in walk at 400px and 1280px on touched routes |

A green unit test of a presentational component does not satisfy a row whose gate says rendered-route.

## Do not fail a review for these

| Claim | What to do |
|---|---|
| Exactly one `aria-current` | Discarded in the UI-pattern capture. Check that the current place is announced |
| Icon-only primary nav justified as an NN/g rule | Not a justification. Ask for visible text. A missing icon beside labeled items is a visual alignment note, not an accessibility fail |
| Tiles convert better than dropdowns | Not shown here. FORM-CHOICE stays Record |
| An unmet 2.3.3 or 2.4.13 called an AA fail | Record the level. Do not fail AA on that alone |
| `llms.txt` required to launch | Not a gate |
| Print stylesheet on the portal | Public content sites only ([`print-stylesheet-for-content-sites.md`](../best-practices/print-stylesheet-for-content-sites.md)) |
| The full public viewport matrix on a one-route portal settings change | RESP-PORTAL is the bar |
| A card-sort of 8 to 12 people before moving a misplaced editor | That is a research study. Placement of a known tool is PLACE-BLOCK |
| Matching an unseen connect-apps screenshot | CONNECT rows are the bar |

## Invite to discard

These rows are the weak ones. Drop them if they are not earning their keep:

- FORM-CHOICE as anything stronger than Record
- COPY-LEVEL on portal screens
- SEO-AEO
- PERF-PREFETCH's Record half (keep the Block half for mutating URLs)
- A11Y-TARGET's 44px Record half
- SHELL-PALETTE when the product has no palette (it is already `N/A`)

## What a finished pass contains

One line per `#review` class: verdict and evidence, or `N/A — reason`. `#placement` is filled with Keep / Move / Remove before any later class is marked done. A `#review-out` class is `N/A — review-out`. Public and signed-in rows are not mixed under one silent scope.

This file does not authorize a change in a product repository. Those changes are opened separately.
