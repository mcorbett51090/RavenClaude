# A honeypot must be invisible to assistive tech and to autofill

**Status:** Absolute rule — a honeypot that a screen reader or a password manager can fill is not a spam filter, it is a silent rejection mechanism aimed at the users least able to work around it.
**Domain:** Forms engineering — anti-abuse
**Applies to:** `forms-engineering`

---

## Why this exists

A honeypot works on one assumption: a human never fills this field, because a human never perceives it. Two populations break that assumption, and both are human.

**Assistive technology.** `display: none` removes an element from the accessibility tree; almost every other way of hiding a field does not. A field pushed off-screen, sized to zero, or given `opacity: 0` is still announced. A screen-reader user hears a plausible label, fills it in, submits, and is rejected — with no error, because the whole design of a honeypot is to not tell the submitter. The rejection is invisible in analytics too: it looks exactly like an abandonment.

**Password managers and browser autofill.** Autofill matches on name, `autocomplete` value, label text and heuristics. A honeypot called `email2`, `phone`, `address`, `company` or `url` is a magnet. The user sees nothing happen and is rejected for something their browser did.

Both failures share a property that makes them expensive: **you will not find out.** There is no error page, no support ticket that says "your honeypot rejected me", and no metric that separates a honeypot rejection from someone changing their mind.

## How to apply

Four properties, all four required:

1. **Out of the accessibility tree.** `display: none` on the wrapper, or `hidden`, plus `aria-hidden="true"`. Not `opacity`, not off-screen positioning, not zero height.
2. **Out of the tab order.** `tabindex="-1"` on the input, so keyboard traversal never lands on it.
3. **Opted out of autofill.** `autocomplete="off"` on the field, and a `name` with no autofill heuristic behind it. Avoid every real field name; prefer something specific to your application and meaningless outside it.
4. **Labelled for the machine, not for a person.** If a label is present for markup validity, it must be inside the same hidden wrapper.

Then, the fifth requirement, which is about operations rather than markup:

5. **Count every rejection and alert on the count.** A honeypot is a filter in front of your own front door. If it is not observable, you cannot tell "spam stopped" from "customers stopped".

## The test that actually catches this

Not a visual check — a visual check passes trivially, which is the whole problem.

- Read the form with a screen reader and confirm the field is never announced.
- Load the form in a browser signed into a password manager, trigger autofill on the real fields, and confirm the honeypot stays empty.
- Submit a legitimate form and confirm it is accepted; submit with the honeypot filled and confirm it is rejected **and counted**.

## The anti-pattern

Adding a honeypot and never looking at it again. The second-worst variant is adding one alongside a time-trap and treating both as free: the time-trap's false-positive rate against autofilling users is `[unverified — premise not disconfirmed; no false-positive-rate study located, open-web search 2026-08-17]`, so it should log rather than reject until you have measured it.

## Source

Failure mechanism derived from the accessibility-tree and autofill behaviours described in this marketplace's own accessibility rules — see [`../../web-design/best-practices/reach-for-semantic-html-before-aria.md`](../../web-design/best-practices/reach-for-semantic-html-before-aria.md) and [`../knowledge/form-anti-abuse.md`](../knowledge/form-anti-abuse.md) §2 (2026-08-17). The ladder that says when to reach for a honeypot at all is in the same knowledge file, §1.
