# Settings controls: markup, keyboard and screen-reader contract (retrieved 2026-11-05)

> **Last reviewed:** 2026-11-05. **Confidence:** high for rows marked `[docs-verified 2026-11-05]` (the named
> primary page was read this session); medium for `[inference]`; none for `[unverified]`. This file is rule text
> for audits and builds. It is **not** a conformance claim and it is **not** a screen-reader result: no
> assistive-technology session produced it ([`test-assistive-tech`](../skills/test-assistive-tech/SKILL.md) does that).
>
> The *choice* of control (tiles, segments, sliders, switches, short copy, sheets, usage cards) is
> [`web-design`'s `settings-and-choice-controls-2026.md`](../../web-design/knowledge/settings-and-choice-controls-2026.md).
> This file is the markup and keyboard contract those choices must meet. It is separate from the 2026-11-04
> capture ([`portal-and-agent-accessibility-2026-11.md`](portal-and-agent-accessibility-2026-11.md)) and re-grades
> nothing in it.

Apply §3 #3 and #4 first: keyboard and screen-reader parity is the floor, native before ARIA.

## Per-control contract

| Control | Build with | Keys `[docs-verified]` | Name / state | Must not |
|---|---|---|---|---|
| **Switch** | `<input type="checkbox">` with a visible label. Adding `role="switch"` to a checkbox is the common route `[unverified this session — confirm against ARIA in HTML]`; the native `switch` attribute is **experimental with limited support** (MDN) so do not rely on it | Space toggles; Enter optional (APG Switch) | Name from the visible label. State is the native `checked`. **The label never changes with state** (APG: "critical") | Flip the label text ("Enable/Disable…"); omit a visible state cue other than color |
| **Segmented control / radio tiles (single choice)** | `fieldset` + `legend` + native `input type="radio"`; the segment/tile is the `<label>`. Keep the input in the accessibility tree: hide it with a visually-hidden clip, **not** `display:none` or `visibility:hidden` `[inference]` | Tab enters on the checked radio (first if none); arrows move **and** select; Space checks (APG Radio Group). One tab stop for the group | Group has a visible label; each option has a name; extra text via `aria-describedby` | `role="tablist"` for a choice that does not switch panels; a clickable `div`; a link or button inside a tile |
| **Multi-choice tiles / chips** | Native `input type="checkbox"` per tile in a `fieldset` | Space toggles each | As switch, label visible | `aria-pressed` buttons when a checkbox fits `[inference]` |
| **Slider** | Native `input type="range"` + `<label>`; implicit role `slider` (MDN) | Arrows ±step, Home/End, optional PageUp/PageDown (APG Slider). Native range implements these in browsers `[unverified this session — test in AT]` | `aria-valuetext` when the number is not friendly ("Large, 18 px") (APG). Show the value in `<output>` | Rely on drag only (WCAG 2.5.7 AA); a slider as the only way to enter an exact number |
| **Tooltip** | Trigger references the tooltip with `aria-describedby`; container `role="tooltip"` (APG Tooltip) | Esc dismisses (APG) | Describes; does not name | Hold essential information; use `title=`; rely on hover (touch) |
| **Toggletip ("more info")** | `<button type="button">` named "More about <label>" + an adjacent `role="status"` region that receives the message `[docs-verified 2026-11-05, secondary source: Inclusive Components]` | Enter/Space on the button; Esc/outside click/blur clears | The button keeps its role; the message is announced via the live region | `aria-describedby` on the toggletip button (the source reports it can disable the button for screen-reader users) |
| **Sheet / overlay** | Native `<dialog>.showModal()` where the repo's [`semantic-html` rule](../../web-design/best-practices/reach-for-semantic-html-before-aria.md) allows; otherwise `role="dialog"` + `aria-modal="true"` | Tab/Shift+Tab contained; Esc closes; focus lands inside on open and returns to the opener on close (APG Dialog Modal) | Visible title is the name (`aria-labelledby`) | Close only by swipe/drag; stack a second sheet; mark `aria-modal` unless outside content is actually blocked |
| **Usage meter** | `<meter min max value low high optimum>` inside a `<label>`-associated block; implicit role `meter` (MDN) | None (not interactive) | Visible text states the figure ("6.2 of 10 GB") | Color as the only threshold signal; a bar with no text equivalent |
| **Save status** | `role="status"` (polite) | — | "Saved" once per commit | Announce every slider tick or keystroke `[inference]` |
| **Connector row** | A row in the Connect-apps list: provider name as text, account count as text, status as text when present | Tab reaches **Authorize**; the row is not the only control | Button name "Authorize \<Provider\>". Count is text ("2 accounts" or "Not connected") | A row that is only a clickable `div`; a count that is a badge with no text |
| **Brand icon** | `<img alt="">` when the provider name is visible text beside it `[inference]` | None | The name is the text, so the connector is still named with images off | The icon as the only name; a generic plug or another brand's asset standing in for it |
| **Base-scope tiles** | `fieldset` + `legend` "Access" + four native radios. Visible labels are exactly **Minimal**, **Read only**, **Full**, **Requested** | Same as radio tiles: one tab stop, arrows move and select | Each tile's name is its visible label. Changing the selection updates the pills | A `<select>`; a fifth tile; checkbox semantics for a single-choice preset |
| **Scope pills** | `<ul>` of the scopes in the current request; if removable, each pill carries a real `<button>` named "Remove \<scope\>" | Enter/Space on the button; Tab through the removes | A `role="status"` region says "Removed \<scope\>" once, and "Access set to \<tile\>" once when the base tile changes `[inference — wording not tested with a screen reader]` | Remove by pointer only; an unnamed ×; a pill list that differs from the scopes on screen |
| **"Advanced" disclosure** | `<button>` with `aria-expanded` and `aria-controls` (the solid disclosure rule in [`portal-and-agent-accessibility-2026-11.md`](portal-and-agent-accessibility-2026-11.md)) | Enter/Space | Name is "Advanced"; show a count when the set differs from the preset ("Advanced (2)") | `role="menu"`; opening on hover; a second sheet |
| **"Required" tile** | A static list item with the title and the visible word "Required". It is **not** an input `[inference]` | None (not interactive) | Read as normal text. "Already granted" is text when this account already holds it | A disabled, pre-checked checkbox (often skipped or announced as unavailable) |
| **Additional Access group** | One `fieldset` + `legend` per area; legend says the area and that it is optional. Native checkboxes, unchecked at the start | Space toggles each; Tab follows visual order | Group name from the legend; each tile's name is its visible title | Pre-ticked optional scopes; one unlabeled checkbox list for every area |
| **Account label field** | A text input with a visible `<label>` ("Account label"). Shown on Add account only | Tab to the field; ordinary text editing | The label is the name. Placeholder is not the label | Placeholder-only; asking for the label again on an account that already has one |
| **Multi-step authorize flow** | One modal dialog (above); steps replace the content inside it | Esc closes on every step and returns focus to the opener. Back moves to the previous step's heading and keeps the choices `[inference]` | "Step 1 of 2: Choose access" and "Step 2 of 2: Authorize" as visible text; focus moves to the new step heading `[inference]` | A second sheet; moving the sheet to a new URL without restoring focus; losing choices on Back |
| **Accounts list (inside the sheet)** | `<ul>` of accounts. Each row's **Authorize** is a `<button>` named "Authorize \<label\>". **Add account** is a `<button>` last. "Make default", if present, is a separate radio group | Tab through each Authorize, then Add account, then Close. Arrows apply only inside the Make-default radios | Each row exposes the label plus the provider identifier as text, and status as text | One radio that authorizes every account; naming rows "Account 1/2"; status by color only |

## WCAG 2.2 criteria that these controls trigger

| Criterion | Level | Applies to | Source |
|---|---|---|---|
| **2.5.7 Dragging Movements** | AA | Slider thumbs, sheet drag handles, any reorder by drag. A single-pointer alternative must exist (click/tap on the track is the page's example). The page does not say whether a *native* range is exempt as a user-agent control, so give text-size and similar sliders −/+ step buttons | `[docs-verified 2026-11-05]` |
| **1.4.13 Content on Hover or Focus** | AA | Tooltips and any hover/focus popover: dismissible without moving pointer or focus, hoverable, persistent. User-agent `title` tooltips are excepted, which is also why `title` is not an accessible "more info" | `[docs-verified 2026-11-05]` |
| **2.5.8 Target Size (Minimum)** | AA | Switch thumbs, segment hit areas, slider thumbs, ⓘ buttons — 24×24 CSS px floor, owned by [`a11y-visible-focus-and-target-size`](../../web-design/best-practices/a11y-visible-focus-and-target-size.md) | existing house rule |
| **4.1.2 Name, Role, Value** | A | Every control above. GOV.UK cites it for revealed content that is not announced | `[docs-verified 2026-11-05, GOV.UK Radios]`; criterion text not re-fetched |
| **1.4.1 Use of Color** | A | Selected segment/tile, switch state, meter threshold | existing house rule: [`color-not-the-only-signifier`](../../web-design/best-practices/color-not-the-only-signifier.md) |
| **1.4.4 Resize Text / 1.4.10 Reflow** | AA | Text-size preview and segment rows at 320 px / 200 % | `[unverified this session]` |

## What an audit records

| Finding | Result |
|---|---|
| Choice control is a `div`/`span` with a click handler and no role, name or keys | Pattern fail (§3 #4) |
| Switch label changes with state | Pattern fail (APG) |
| Segmented control not operable with arrows as one tab stop | Pattern fail |
| Slider thumb cannot be moved without dragging, custom-drawn | Fail 2.5.7 (AA) |
| Native slider with no step alternative | Note: the Understanding page is silent on the exception. Record it and recommend step buttons; do not fail 2.5.7 on this alone `[inference]` |
| "More info" only available on hover or only in `title=` | Fail 1.4.13 / pattern fail |
| Sheet closes only by swipe, or focus is not returned | Pattern fail (APG) |
| `aria-describedby` present on a toggletip button | Not a WCAG failure; flag for AT testing `[secondary source]` |
| Usage state conveyed by bar color only | Fail 1.4.1 |
| Required scope rendered as a disabled pre-checked checkbox | Pattern note: recommend a static "Required" tile `[inference]`; fail only if it breaks 1.4.1 or 4.1.2 |
| Pills removable only by pointer, or the scope list on screen differs from the request | Pattern fail (keyboard parity, §3 #3); the mismatch routes to `security-reviewer` |
| Base-scope choice is a `<select>` or a set of buttons with no radio group semantics | Pattern fail (one tab stop, arrows select) |
| Connect-apps Authorize is one button for every account, or the account row has no keyboard Authorize | Pattern fail (§3 #3) |
| Connector identifiable only by its icon | Pattern fail: the provider name is text beside a decorative image |

## Test script (keyboard first, then one screen reader)

1. Tab through the page: every control reachable, in visual order, focus visible and not obscured.
2. Segmented/tiles: Tab lands once; arrows move and select; Shift+Tab leaves.
3. Switch: Space toggles; the label stays the same; the new state is announced.
4. Slider: arrows, Home, End; the announced value is the `aria-valuetext`; the −/+ step buttons work from the keyboard as well as the pointer.
5. Toggletip: Enter shows the text and it is announced; Esc clears it.
6. Sheet: focus moves in, is contained, Esc closes, focus returns to the exact opener; the close button works without a pointer.
7. Usage card: the figure is read as text, not only a percentage.
8. Connect-apps list: each row's name is text, the count is text, and Tab lands on "Authorize \<Provider\>". Activate it. Focus moves to the sheet title.
9. Accounts sheet, with two accounts on a provider that allows two: Tab reaches "Authorize \<label\>" for each, then "Add account", then Close. Status is text. Activate one Authorize and confirm focus lands on "Step 1 of 2: Choose access". Activating Add account asks for the label once, then the same step.
10. Base tiles: Tab lands once. Arrows move across Minimal, Read only, Full and Requested and select. The pills match the selected preset. Remove one pill with Enter; the status region announces the removal; the matching Advanced checkbox is unchecked.
11. Advanced: Enter opens and closes it. It is not a second dialog. Continue stays disabled, with visible text, until a base tile is selected. After Continue, focus is on "Step 2 of 2: Authorize". Back returns to step 1 with the same tile and the same edits.
12. Required items are not in the tab order and read as text. Each Additional Access group is a fieldset, and every box in it starts unchecked. The pill summary matches the scopes that will be sent.
13. Esc from either step closes the sheet and returns focus to the same Authorize button on the list.
14. Run once with NVDA or VoiceOver and write down which one. Do not generalise to other AT.

## Markup sketch (Connect apps)

House markup for the contract above. Not a screenshot of any product `[inference]`.

```html
<li>
  <img src="/icons/notion.svg" alt="">
  <span>Notion</span>
  <span>2 accounts</span>
  <button type="button">Authorize <span class="visually-hidden">Notion</span></button>
</li>
```

```html
<dialog aria-labelledby="sheet-title">
  <h2 id="sheet-title">Notion</h2>
  <button type="button">Close</button>
  <h3>Accounts</h3>
  <ul>
    <li>
      <span>work</span>
      <span>ada@example.com</span>
      <span>Connected</span>
      <button type="button">Authorize work</button>
    </li>
  </ul>
  <button type="button">Add account</button>
</dialog>
```

```html
<h2>Step 1 of 2: Choose access</h2>
<label for="account-label">Account label</label>
<input id="account-label" type="text" autocomplete="off">
<fieldset>
  <legend>Access</legend>
  <label><input type="radio" name="access" value="minimal"> Minimal</label>
  <label><input type="radio" name="access" value="read-only"> Read only</label>
  <label><input type="radio" name="access" value="full"> Full</label>
  <label><input type="radio" name="access" value="requested"> Requested</label>
</fieldset>
<ul>
  <li>Read pages <button type="button">Remove Read pages</button></li>
</ul>
<div role="status"></div>
<button type="button" aria-expanded="false" aria-controls="advanced-scopes">Advanced</button>
<div id="advanced-scopes" hidden>
  <fieldset>
    <legend>Pages</legend>
    <label><input type="checkbox"> Read pages</label>
  </fieldset>
</div>
<p>Choose an access level to continue.</p>
<button type="button">Continue</button>
```

```html
<h2>Step 2 of 2: Authorize</h2>
<p>Authorize as work</p>
<ul>
  <li>Read pages <span>Required</span></li>
</ul>
<fieldset>
  <legend>Comments, optional</legend>
  <label><input type="checkbox"> Write comments</label>
</fieldset>
<button type="button">Authorize</button>
```

The label field is omitted when the person authorized an account that already has a label. "Make default" is a separate `fieldset` of radios and is left out when the product has no default.

## Limits

- No assistive-technology session produced this file, and no study shows these controls are easier for disabled users.
- `role="switch"` on a checkbox, tab-panel segmented controls, 1.4.4 and 1.4.10 were not fetched; they are labeled.
- Legal and conformance determinations route to counsel (§2). Security of any connector or sign-in surface routes to `ravenclaude-core` `security-reviewer`.

## Sources (retrieved 2026-11-05)

[APG Switch](https://www.w3.org/WAI/ARIA/apg/patterns/switch/) · [APG Radio Group](https://www.w3.org/WAI/ARIA/apg/patterns/radio/) · [APG Slider](https://www.w3.org/WAI/ARIA/apg/patterns/slider/) · [APG Tooltip](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/) (marked work in progress, no task-force consensus) · [APG Dialog (Modal)](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) · [WCAG 2.2 Understanding 2.5.7](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html) · [Understanding 1.4.13](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html) · [MDN checkbox `switch`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/checkbox) · [MDN range](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/range) · [MDN meter](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/meter) · [GOV.UK Radios](https://design-system.service.gov.uk/components/radios/) · [Inclusive Components: Tooltips & Toggletips](https://inclusive-components.design/tooltips-toggletips/)
