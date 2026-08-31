# Clear the error the moment it is fixed

**Status:** Pattern — an error message that outlives the error teaches the user that their fix did not work.
**Domain:** Forms engineering — validation feedback
**Applies to:** `forms-engineering`

---

## ⛔ What this rule does not restate

**When** to validate — on blur, not on keystroke; inline, not in a modal; name the fix, not the problem — is already ruled on in [`../../web-design/best-practices/ux-form-design-and-error-handling.md`](../../web-design/best-practices/ux-form-design-and-error-handling.md). This rule is the one thing that rule does not cover: what happens on the way **out** of the error state.

## Why this exists

Validate-on-blur is the right default for showing an error. It is the wrong default for **removing** one.

Once a field is in an error state, the user's next keystroke is an attempt to fix it. If the error only re-evaluates on blur, the message stays on screen through the entire correction — and the user, who is reading the message while typing, has no confirmation that they are heading in the right direction. Two things follow, and both are commonly observed as "the form is broken":

- The user re-edits a field that is already correct, because the message is still there.
- The user abandons a nearly-complete form because it appears to be rejecting a value they can see is right.

The asymmetry is the whole rule: **be slow to accuse, quick to forgive.** Showing an error early is a false accusation; clearing one late is a false accusation you are refusing to withdraw.

## How to apply

1. **Show on blur. Clear on input.** Once a field is in error, re-evaluate on every input event and clear the moment it passes. Do not wait for the next blur.
2. **Do not switch to keystroke validation generally.** The asymmetric rule applies only to fields already in error; a field that has never errored still validates on blur.
3. **Clear the summary entry too.** If there is an error summary at the top of the form, its entry for the field must disappear with the inline message — a summary that lags is worse than no summary, because it is the thing screen-reader users are steered to.
4. **Announce the clear, don't just remove it.** Removing the message from a live region silently leaves an assistive-technology user with no confirmation. Update the field's status, and keep the error's programmatic association correct in both directions.
5. **Do not move focus on clear.** Focus movement mid-correction is disorienting and costs more than the message did.
6. **Re-validate on submit regardless.** A cleared client-side message is a UI state, not an acceptance; the server decides.

## The anti-pattern

An error styled with a persistent red border that is only recomputed when the form is submitted again. The user fixes the field, sees no change, assumes the fix was rejected, and starts trying alternatives.

## Source

Complements the blur/inline/name-the-fix rule linked above (read 2026-08-17). The clearing half is absent from it, which is the only reason this file exists; the error-association and focus mechanics belong to [`../../web-design/agents/accessibility-auditor.md`](../../web-design/agents/accessibility-auditor.md).
