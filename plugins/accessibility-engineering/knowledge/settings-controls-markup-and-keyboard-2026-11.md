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
| **Scope tiles (connect flow)** | Native `input type="checkbox"` per tile in a `fieldset`/`legend` (one group per provider area) | Space toggles each; Tab order follows the visual order | Visible title is the name; caption via `aria-describedby` | A clickable `div`; a pre-ticked optional scope |
| **Scope pills** | `<ul>` of chosen scopes; if removable, each pill carries a real `<button>` named "Remove <scope>" | Enter/Space on the button | A `role="status"` region says "Removed <scope>" once `[inference]` | Remove by pointer only; an unnamed × |
| **"Advanced" disclosure** | `<button>` with `aria-expanded` and `aria-controls` (the solid disclosure rule in [`portal-and-agent-accessibility-2026-11.md`](portal-and-agent-accessibility-2026-11.md)) | Enter/Space | Name says what opens; show a count when something inside is chosen | `role="menu"`; opening on hover |
| **"Required" tile** | A static list item with the title and the visible word "Required". It is **not** an input `[inference]` | None (not interactive) | Read as normal text | A disabled, pre-checked checkbox (often skipped or announced as unavailable) |
| **Multi-step authorize flow** | One modal dialog (above); steps replace the content inside it | Esc closes on every step | "Step 2 of 2: Authorize" as visible text; focus moves to the new step heading `[inference]` | Moving the sheet to a new URL without restoring focus; losing choices on Back |
| **Account list** | `<ul>` of accounts under a disclosure; "Make default" is a native radio group in a `fieldset`; "Add another account" is a `<button>` | Arrows within the radio group; Tab to row actions | Each row's name is the account identifier plus the connector, status as text | Naming rows "Account 1/2"; status by color only |

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

## Test script (keyboard first, then one screen reader)

1. Tab through the page: every control reachable, in visual order, focus visible and not obscured.
2. Segmented/tiles: Tab lands once; arrows move and select; Shift+Tab leaves.
3. Switch: Space toggles; the label stays the same; the new state is announced.
4. Slider: arrows, Home, End; the announced value is the `aria-valuetext`; step buttons work with the pointer only.
5. Toggletip: Enter shows the text and it is announced; Esc clears it.
6. Sheet: focus moves in, is contained, Esc closes, focus returns to the exact opener; the close button works without a pointer.
7. Usage card: the figure is read as text, not only a percentage.
8. Connect flow: tick scope tiles, confirm the pills match exactly, remove one pill with the keyboard, open and close Advanced, press Continue and check focus lands on the "Step 2 of 2" heading; Back keeps the choices. Required items read as text, not as controls. With two accounts, pick one and confirm the announced identifier is the account, not a number.
9. Run once with NVDA or VoiceOver and write down which one. Do not generalise to other AT.

## Limits

- No assistive-technology session produced this file, and no study shows these controls are easier for disabled users.
- `role="switch"` on a checkbox, tab-panel segmented controls, 1.4.4 and 1.4.10 were not fetched; they are labeled.
- Legal and conformance determinations route to counsel (§2). Security of any connector or sign-in surface routes to `ravenclaude-core` `security-reviewer`.

## Sources (retrieved 2026-11-05)

[APG Switch](https://www.w3.org/WAI/ARIA/apg/patterns/switch/) · [APG Radio Group](https://www.w3.org/WAI/ARIA/apg/patterns/radio/) · [APG Slider](https://www.w3.org/WAI/ARIA/apg/patterns/slider/) · [APG Tooltip](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/) (marked work in progress, no task-force consensus) · [APG Dialog (Modal)](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) · [WCAG 2.2 Understanding 2.5.7](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html) · [Understanding 1.4.13](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html) · [MDN checkbox `switch`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/checkbox) · [MDN range](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/range) · [MDN meter](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/meter) · [GOV.UK Radios](https://design-system.service.gov.uk/components/radios/) · [Inclusive Components: Tooltips & Toggletips](https://inclusive-components.design/tooltips-toggletips/)
