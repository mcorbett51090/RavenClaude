---
name: wallet-passes
description: Use when designing, reviewing, or implementing Apple Wallet (.pkpass / PassKit) or Google Wallet (GenericClass / GenericObject) passes — especially digital business cards, membership cards, tickets, coupons, or "Add to Wallet" save links. Reach for this on pass.json field layout, image sizes, truncation, NFC/Smart Tap, web-service updates, JWT save URLs, or branding rules.
---

# wallet-passes

Official-docs reference for Apple Wallet (PassKit) and Google Wallet generic passes. Read this file first; open a reference only for the platform you are building.

| Need | Open |
|---|---|
| Apple `pass.json`, styles, images, relevance, signing, web service, NFC | [`references/apple.md`](references/apple.md) |
| Google Generic class/object, templates, images, JWT save, Smart Tap, notifications | [`references/google.md`](references/google.md) |
| Digital business-card layout, worked examples, common-mistakes checklist | [`references/business-card-layout.md`](references/business-card-layout.md) |

## When to use

- Authoring or reviewing a `.pkpass` / `pass.json` or a Google Wallet `GenericClass` / `GenericObject`.
- Choosing field slots, image assets, barcodes, NFC / Smart Tap, or save-link issuance.
- Designing a **digital business card** that must survive both wallets without baked-in text.
- Diagnosing truncation, dead links, silent updates, cached stale passes, or rejected artwork.

**Not for:** payment cards / Apple Pay / Google Pay checkout, boarding-pass airline integrations beyond PassKit field rules, or native Wallet UI apps (that is PassKit / Wallet API app code, not pass design).

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

## Business-card default

Use Apple **`generic`** + Google **`GENERIC_OTHER`** (or a membership `genericType` if it is honestly a membership). Front: person name + role + one QR (vCard or profile URL). Back/details: `tel:`, `mailto:`, website, LinkedIn, address, terms. **Never** put the name in `logo` / `heroImage`. Worked `pass.json` + `GenericObject`: [`references/business-card-layout.md`](references/business-card-layout.md).

## Common mistakes (read the checklist before shipping)

- Front-field truncation / hidden fields because copy is too long or too many slots filled.
- `logoText` **and** a wordmark inside `logo.png` (Watch drops `logoText` when it does not fit; you get a double brand or a clipped one).
- Baking text into strip / hero / background (not localized; cropped; Mail/iMessage preview uses **`icon.png`**, not the strip).
- Putting a URL on an Apple **front** field and expecting it to be tappable.
- Changing Apple `serialNumber` or `authenticationToken` on "update" (that is a new pass; old devices keep the cached one).
- APNs payload that is not `{}` — Wallet coalesces pushes; extra keys are lost.
- Google neon `hexBackgroundColor`; pre-masked circular logo; hero with typography.
- More than 3 Google notify-messages / 24h.
- Skipping WWDR in the Apple PKCS#7 signature (pass will not add; console says signature error).

Full checklist: [`references/business-card-layout.md`](references/business-card-layout.md) § Common mistakes.
