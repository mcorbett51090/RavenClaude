# Designing a visual pass builder

> **Retrieved 2026-10-26.** Tool behaviour from Apple's "Creating a pass with Pass Designer", WWDC26-209,
> `apple/pass-builder` (default branch), Google's Pay & Wallet Console and pass-builder docs; Passcreator and
> PassKit.com help centres are third-party `[3p]`. The pass rules a builder enforces are in
> [`pass-types.md`](pass-types.md); general editor craft (drag and drop, undo, draft/publish, simple/advanced
> modes) is in the `web-design` plugin's `knowledge/visual-builder-ux-2026.md`, when that plugin is installed.

## What existing designers do

| Tool | Notable behaviour |
|---|---|
| **Apple Pass Designer** (macOS 27 app, 2026) | Template picker that preloads fields and image placements for six styles; a component sidebar (identity and signing, style, images, barcode and NFC, header/primary/footer fields, semantics); a live preview that can "visualize the appearance of each pass in each version of the software"; a canvas-colour toggle; "tells you which images are needed for each pass"; saves `.pkpasstemplate` `[doc]` |
| **Apple Pass Builder** | `PassPackage`, `PassSigner`, `PassValidator` with event, seat, boarding, field-format and required-image plugins; Swift 6.3 on macOS 14+ or Linux; "early preview… APIs may change" `[code]`. It does not run on an edge runtime — read its validators as the reference constraint set instead |
| **Google pass builder / Pay & Wallet Console** | A visual form that generates the JSON; the Console edits **classes only** and changes apply to every holder on save `[doc]` |
| **Passcreator** | Live preview; draft vs **Publish changes** with an "Unpublished changes" badge; publishing "rolls the changes out to your template and to passes already saved on phones"; conditional fields; passes from a demo certificate "cannot be updated later" `[3p]` |
| **PassKit.com** | Crops to the slot's ratio on upload; says plainly that the browser image is "not an actual pass" but "a visual approximation" `[3p]` |

## Copy these

1. **Kind-first template picker.** Choosing *loyalty*, *membership*, *coupon*, *event ticket* or *business card*
   preloads role-based fields and image slots (Pass Designer's model).
2. **A multi-target preview strip:** iPhone iOS 27 (poster), iPhone iOS 26 and earlier (legacy fallback), Apple
   Watch, Android, Google web. Each render carries a **"not shown here" badge** per field — dropped for space,
   back only, hidden on Watch, not allowed in Google card rows — computed from the `PlacementPlan` in
   [`pass-types.md`](pass-types.md) §5.
3. **A slot-aware cropper.** One master upload, cropped per slot with safe-area overlays: Apple's material strip
   at the bottom of poster artwork and the text zone over a strip; Google's 15 % circle-mask margin and the hero's
   20 dp padding. Generate Apple @2x and @3x automatically.
4. **Contrast checking against the real background.** Apple: check foreground and label colours against the
   background colour and, where text sits on a strip or artwork, against the image region under the text box.
   Google has no text-colour control, so warn on colours outside Google's recommended palette and on neon.
5. **A barcode preview that tells the truth** — render the real symbology and show each platform's fallback
   ("iOS 26: QR shown instead of Codabar"); offer `TEXT_ONLY` or `altText` for promo codes.
6. **Draft → publish with the blast radius.** Google: "Publishing updates class X — N saved passes change at the
   next sync; classes cannot be deleted." Apple: "N passes will be re-signed and pushed to M devices."
7. **Test-issue to my own phone** before publish: a QR that opens the `.pkpass` and the Google save link on the
   editor's device, using a reserved test serial/object that stays updatable (avoid the demo-certificate trap).
8. **Inline validation that mirrors Apple's validator** (missing icon @2x/@3x, currency + number style together,
   poster requirements) plus Google's length and count limits — shown while typing.
9. **A notification composer with budgets:** Google's 3 notifying messages and 3 field-update notifications per
   pass per 24 h, Apple's "time-critical only" change-message rule, and a preview of the lock-screen text.

## Avoid these

- **Claiming pixel accuracy.** Both platforms own fonts, truncation and chrome, and Google redesigned passes in
  2026 ("Expressive Passes", release notes 2026-09-15). Label the preview an approximation and push real-device
  tests.
- **Hard-coded image sizes.** Google changed its hero guidance in 2026; keep slot specs in a versioned data table.
- **Positional editing as the source of truth.** It cannot express Google's class/object split or Apple's
  drop-on-overflow; edit roles and let placement be computed.
- **Editing a live Google class without versioning** — classes are shared, undeletable and propagate at once.
- **Offering poster event tickets, NFC or Smart Tap to tenants without the entitlement or certified terminals.**

## A sensible editor layout `[inference]`

Left: the kind picker, then grouped controls in plain language — *Brand* (logo, colours, artwork), *What the pass
shows* (role fields with sample values), *Barcode*, *When it appears* (locations, dates), *Messages*. Right: the
preview strip with platform tabs and a front/back flip. Simple mode shows only the fields the chosen kind needs;
advanced mode exposes every slot, back fields, relevance, featured actions and placement overrides. Save and
publish live in a header that always shows "Saved · Unpublished changes · Affects N passes".
