---
name: wallet-passes
description: Use when designing, reviewing, or implementing Apple Wallet (.pkpass / PassKit) or Google Wallet passes — business cards, tickets, save links — or handing a card to another person (share sheet, AirDrop, NFC tag, QR, in-app browsers) and lead capture. Covers pass.json layout, images, NFC/VAS/Smart Tap, updates, JWT save URLs, branding.
---

# wallet-passes

Official-docs reference for Apple Wallet (PassKit) and Google Wallet generic passes. Read this file first; open a reference only for the platform you are building.

| Need | Open |
|---|---|
| Apple `pass.json`, styles, images, relevance, signing, web service, NFC, Featured Actions | [`references/apple.md`](references/apple.md) |
| Google Generic class/object, templates, images, JWT save, Smart Tap, notifications, publishing | [`references/google.md`](references/google.md) |
| Digital business-card layout, worked examples, common-mistakes checklist | [`references/business-card-layout.md`](references/business-card-layout.md) |
| Tap-to-share / tap-to-lead-form: what's possible / entitlement-gated / impossible; NFC-tag/QR → HTTPS; workarounds; **pushing a card to another person** (every path ranked, receiving-page traps, Google multi-holder) | [`references/tap-to-share.md`](references/tap-to-share.md) |
| Weak / unverified / absent-evidence claims (the 38-item ledger; P1 = #1–#8) | [`references/verify.md`](references/verify.md) |

## When to use

- Authoring or reviewing a `.pkpass` / `pass.json` or a Google Wallet `GenericClass` / `GenericObject`.
- Choosing field slots, image assets, barcodes, NFC / Smart Tap, or save-link issuance.
- Designing a **digital business card** that must survive both wallets without baked-in text.
- Diagnosing truncation, dead links, silent updates, cached stale passes, or rejected artwork.

**Not for:** payment cards / Apple Pay / Google Pay checkout, boarding-pass airline integrations beyond PassKit field rules, or native Wallet UI apps (that is PassKit / Wallet API app code, not pass design).

> ## ⚠️ P1 unverified — architecture / promise level (read before you promise)
>
> Eight claims the research could not confirm from a primary source would each change an architecture decision or a customer promise. **Do not treat any of these as settled**; the full ledger with how-to-verify steps is [`references/verify.md`](references/verify.md).
>
> 1. **`.pkpass` single-pass MIME / Safari Add-to-Wallet sheet** (#1) — `application/vnd.apple.pkpass` was on no current page.
> 2. **`.pkpass` download in non-Safari/Android browsers** (#2) — partly resolved: Chrome iOS shows the Add sheet, Google Wallet on Android imports a `.pkpass` (no updates); **in-app browsers (Instagram, Messenger…) fail**.
> 3. **`posterGeneric` is a real supported key** (#3) — absent from the `Pass` reference table; ship a `generic` fallback.
> 4. **Google Wallet passes work on iOS** (#4) — not stated; plan Android-only + `.pkpass` for iOS.
> 5. **No public NameDrop API** (#5) — argument from absence; you cannot drive NameDrop from an app.
> 6. **Apple NFC passes invisible to ordinary NDEF readers** (#6) — inferred, not stated.
> 7. **Apple NFC (VAS) cert has no published SLA** (#7) — the request form is sign-in gated.
> 8. **Google `appLinkData` needs allowlisting** (#8) — one FAQ sentence, no criteria/timeline; it gates any front-of-pass button.
>
> The other 30 items (#9–#38: P2 implementation details and P3 undocumented numbers; #10 resolved, #38 partly resolved) are in the same ledger.

## Hard rules (both platforms)

1. **Text lives in fields, never in artwork.** Do not overlay name, title, phone, or URL on `logo` / `strip` / `heroImage` / `background`. Artwork is cropped, masked, localized, and blurred; baked text will clip or stay English. Apple: [Pass Design and Creation](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html). Google: [Brand guidelines — hero images](https://developers.google.com/wallet/generic/resources/brand-guidelines).
2. **Front of pass is scarce; back/details is cheap.** Apple front slots have hard *counts* and soft *width*; overflow hides fields, it does not wrap ([Pass Design and Creation](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)). Google recommends ≤2 fields/row and ≤3 rows, with published English character limits ([Brand guidelines — Content](https://developers.google.com/wallet/generic/resources/brand-guidelines)).
3. **Links are tappable only where the platform says so.** Apple: data detectors and `<a href>` `attributedValue` apply to **back fields**, not the front ([PassFieldContent](https://developer.apple.com/documentation/walletpasses/passfieldcontent)). Google: use `linksModuleData` (`http:`, `tel:`, `mailto:`) and optional `appLinkData` ([Brand guidelines — Modules](https://developers.google.com/wallet/generic/resources/brand-guidelines)).
4. **Identity of a pass is (issuer type + serial/id), not the artwork.** Apple update = same `passTypeIdentifier` + `serialNumber` ([Updating a Pass](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Updating.html)). Google object id is `issuerId.identifier` ([GenericObject](https://developers.google.com/wallet/reference/rest/v1/genericobject)).
5. **Do not invent hard Apple character maxima.** Apple publishes field *counts* and "too much text → some fields are not displayed." Any per-slot character table that is not from Apple is working guidance, not a contract. Google *does* publish English limits — use those.

## Apple — 30-second map

Style key at the top of `pass.json` (exactly one legacy style; newer poster styles may sit beside a fallback):

| Style | Typical use | Images | Front field budget |
|---|---|---|---|
| `generic` | membership, claim ticket, **business card** | logo, icon, thumbnail | ≤3 header, 1 primary, ≤4 secondary, ≤4 auxiliary; square barcode combines secondary+auxiliary to ≤4 |
| `storeCard` | loyalty / gift | logo, icon, strip | same combined-4 rule with square barcode |
| `coupon` | offer | logo, icon, strip | same |
| `eventTicket` | event entry | logo, icon, strip **or** background+thumbnail (not both) | standard counts |
| `boardingPass` | transit | logo, icon, footer | ≤2 primary, ≤5 auxiliary; needs `transitType` |
| `posterEventTicket` via `preferredStyleSchemes` | iOS 18+ poster event | semantic tags required or it falls back | keep legacy `eventTicket` fields |
| `posterGeneric` | newer poster generic | poster + fallback style | include a legacy style dictionary for older OS |

Required top-level keys: `formatVersion` (1), `passTypeIdentifier`, `serialNumber`, `teamIdentifier`, `organizationName`, `description`. Package = `pass.json` + images + `manifest.json` (SHA-1 of every file except itself and `signature`) + PKCS#7 detached `signature` that **includes the WWDR intermediate**. Zip → `.pkpass`.

**Updates:** `webServiceURL` + `authenticationToken`. Push an **empty JSON dictionary** via APNs using the pass-signing cert; device then GETs changed serials and the new `.pkpass`. `changeMessage` with `%@` is the only user-visible update alert.

**Relevance:** ≤10 `locations`, ≤10 `beacons`, one `relevantDate`. Style changes how date AND/OR location match. Coupons and store cards **do not** support `relevantDate`.

**Void / expire:** `voided: true` **or** past `expirationDate` marks the pass expired.

**Share:** omit `sharingProhibited` (or `false`) to allow Wallet share / AirDrop / nearby iPhone (NameDrop-style). `true` hides Share. Issuer can disable sharing entirely ([Apple Support](https://support.apple.com/en-us/111112)).

Full field/image/NFC/web-service tables: [`references/apple.md`](references/apple.md).

## Google — 30-second map

Two resources: **class** (template / program) + **object** (one person's pass).

| Surface | What goes there |
|---|---|
| `cardTitle` | Business / program name (required on object) |
| `header` | Pass title — person name on a business card (required) |
| `subheader` | Title / location label |
| `logo` / `wideLogo` | Circular-masked 1:1 logo (660×660 min, **15% safe margin**, do not pre-mask) or 16:5 wide logo |
| `heroImage` | Official generic hero: **1032×812 px (~5:4), no embedded text, 20dp top/bottom pad** |
| `hexBackgroundColor` | `#RRGGBB`; avoid neon; Google picks dominant logo color if omitted |
| `textModulesData` | Detail-view text (class + object both render; brand guide: ≤2 between class and object; API: up to 10+10 displayed) |
| `linksModuleData` | `http:` / `tel:` / `mailto:` URIs (brand guide: ≤4 total; API: up to 10+10 displayed) |
| `barcode` | QR / PDF417 / Aztec / Code128 etc. |
| `smartTapRedemptionValue` | ASCII NFC payload; class must set `enableSmartTap` + `redemptionIssuers` (Smart Tap partners only) |

**Save link:** sign a JWT (`aud: google`, `typ: savetowallet`) with the issuer service-account key; issue `https://pay.google.com/gp/v/save/<signed_jwt>`. Use Google's **Add to Google Wallet** button assets — do not redraw the button ([Brand guidelines](https://developers.google.com/wallet/generic/resources/brand-guidelines), [JWT](https://developers.google.com/wallet/generic/use-cases/jwt)).

**Notifications:** max **3** `TEXT_AND_NOTIFY` messages per pass per 24h (`QuotaExceededException` after that). Expiry notice = 2 days before; upcoming = 1 day before; only one of those two. Nearby: ≤10 `merchantLocations` on class and ≤10 on object.

Full schema/templates/branding: [`references/google.md`](references/google.md).

## Tap to share / lead capture — 30-second map

For "tap a phone to share a card" and "a tap opens a lead form." Full detail + friction tables + workarounds: [`references/tap-to-share.md`](references/tap-to-share.md).

- **Phone-to-phone NFC "beaming" of a card is NOT available to third parties** on either platform. A pass's `nfc` key (Apple VAS / Google Smart Tap) talks to a **terminal**, not another phone, and both need an entitlement + certified hardware.
- **What IS available for "tap phones":** Apple **Wallet→Wallet proximity share** (leave `sharingProhibited` false — the one real third-party-controlled primitive), **NameDrop** (system-owned, no API — #5), and an **NFC tag/sticker + QR** any phone reads.
- **"A tap opens a lead form" is fully doable today, zero approvals:** one stable **HTTPS universal-link/App-Link-ready URL** carried by (a) an NFC tag (NDEF well-known URI, HTTPS, single record), (b) a printed QR, (c) the QR inside the pass. Cost: **2 taps** on both platforms (Android 17 added an "open link" notification step, matching iOS).
- **Front-of-pass CTA button:** Apple has none before iOS 27 **Featured Actions** (schema unverified — #11); `appLaunchURL` only launches *your* App Store app. Google has **`appLinkData`** but it is **allowlist-gated** (#8). Until both are confirmed, the QR + back/detail links are the CTA.
- **Keep off the build list:** phone-to-phone card beaming (not available), a NameDrop integration (no API), a headshot on a Google pass (banned), reliance on developer-authored Google push (unsupported), a `.vcf`-download-only primary flow (multi-step on both platforms).

### Pushing a card to another person — 30 seconds

Full ranked table + evidence: [`references/tap-to-share.md`](references/tap-to-share.md) § Pushing a card to another person.

- **One URL, many carriers.** Pass QR (any camera; the pass is on the paired Apple Watch automatically), NFC sticker, the OS share sheet with the **URL alone**, prefilled text/email/WhatsApp. The one native file hand-off is Wallet **Share** (iPhone → iPhone; same serial, so every copy registers for your updates).
- **Strangers:** iOS 26.2+ AirDrop to a non-contact needs an **AirDrop code** — the QR or Messages is faster. The hold-two-iPhones gesture is for undefined "eligible passes" (#30): never promise it.
- **The receiving page is where it breaks:** one Wallet button per phone (Android hides Apple only when a Google pass exists — Google Wallet imports `.pkpass` without updates; iPhone hides Google); an **in-app-browser** escape on iOS (Instagram/Messenger block passes — Apple: only Safari and Safari View Controller import directly); `[hidden]{display:none!important}` so script-hidden buttons stay hidden; a strict CSP needs the script as a same-origin file.
- **Google:** one object saved by many people needs `multipleDevicesAndHoldersAllowedStatus: MULTIPLE_HOLDERS` **on the class** — under `ONE_USER_ALL_DEVICES` the first saver locks everyone else out.
- **Straight to Wallet:** mark only the pass QR and the NFC tag with `#add-to-wallet` (not the Google pass's QR — Save-JWT budget); the card script strips it and opens this phone's Wallet link, fail-closed. iOS Safari shows the sheet with no tap (MEAS 2026-10-18, URL opened in Safari); the Camera and NFC entry points and other default browsers are still #38 — [`references/tap-to-share.md`](references/tap-to-share.md) § Straight to Wallet.
- **Owner without an app:** Web NFC writes a sticker from Chrome on Android (Safari will not implement it). `sms:` body forms are undocumented (#31) — use per-phone forms and device-test.

## Business-card default

Use Apple **`generic`** + Google **`GENERIC_OTHER`** (or a membership `genericType` if it is honestly a membership). Front: person name + role + one QR (vCard or profile URL). Back/details: `tel:`, `mailto:`, website, LinkedIn, address, terms. **Never** put the name in `logo` / `heroImage`. Worked `pass.json` + `GenericObject`: [`references/business-card-layout.md`](references/business-card-layout.md).

### Product decisions (Matthew)

- **Headshot is optional and Apple-only.** Apple `thumbnail` may carry a headshot; never put a photo of a person on a Google pass — Google Wallet policy bans personal images (see [`references/google.md`](references/google.md)).
- **Card first, info capture second.** Ship the wallet card itself first; the lead-form / info-capture flow ([`references/tap-to-share.md`](references/tap-to-share.md)) comes after.
- **The iPhone app is owned by Product & Delivery.** App Clip / native-app work is their call, not this skill's.

### Issuer and footer — planned, not shipped

- **RavenPass is the default issuer** (IM-2).
- **Planned:** per-pass certificate routing (IM-3..IM-7) with encrypted bring-your-own signing keys. Not shipped — do not describe as available.
- **Pass footer convention:** `Business Name · description`.

## Common mistakes (read the checklist before shipping)

- Front-field truncation / hidden fields because copy is too long or too many slots filled.
- `logoText` **and** a wordmark inside `logo.png` (Watch drops `logoText` when it does not fit; you get a double brand or a clipped one).
- Baking text into strip / hero / background (not localized; cropped). Messages draws the **pass face** for a shared `.pkpass` (Mail uses `icon.png`) — see [`references/apple.md`](references/apple.md) §11a; when the iMessage preview matters, share a **link** whose page follows Apple TN3156.
- Putting a URL on an Apple **front** field and expecting it to be tappable.
- Changing Apple `serialNumber` or `authenticationToken` on "update" (that is a new pass; old devices keep the cached one).
- APNs payload that is not `{}` — Wallet coalesces pushes; extra keys are lost.
- Google neon `hexBackgroundColor`; pre-masked circular logo; hero with typography.
- More than 3 Google notify-messages / 24h.
- Skipping WWDR in the Apple PKCS#7 signature (pass will not add; console says signature error).

Full checklist: [`references/business-card-layout.md`](references/business-card-layout.md) § Common mistakes.
