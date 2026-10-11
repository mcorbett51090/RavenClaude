# Apple Wallet / PassKit reference

Sourced from Apple Developer documentation. Prefer the live Wallet Passes pages; the archived Wallet Developer Guide still holds the layout, image-point, relevance, and signing rules that the live pages summarize.

| Topic | Official source |
|---|---|
| Pass bundle, styles, fields, images, relevance, colors, barcodes, signing | [Wallet Developer Guide — Pass Design and Creation](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html) |
| Top-level Pass object | [Pass](https://developer.apple.com/documentation/walletpasses/pass) · [Defining the metadata of your Wallet Pass](https://developer.apple.com/documentation/walletpasses/defining-the-metadata-of-your-wallet-pass) |
| Field dictionary (`changeMessage`, `attributedValue`, `dataDetectorTypes`) | [PassFieldContent](https://developer.apple.com/documentation/walletpasses/passfieldcontent) |
| Semantic tags / poster event tickets | [Supporting semantic tags](https://developer.apple.com/documentation/walletpasses/supporting-semantic-tags-in-wallet-passes) · [Creating a poster event pass](https://developer.apple.com/documentation/walletpasses/creating-an-event-pass-using-semantic-tags) · [SemanticTags](https://developer.apple.com/documentation/walletpasses/semantictags) |
| Poster generic (newer layout) | [Creating a Poster Generic Pass](https://developer.apple.com/documentation/walletpasses/creating-a-poster-generic-pass) |
| Upcoming events on a poster ticket | [WWDC25 — What's new in Wallet](https://developer.apple.com/videos/play/wwdc2025/202/) |
| Web service + APNs | [Adding a Web Service to Update Passes](https://developer.apple.com/documentation/WalletPasses/adding-a-web-service-to-update-passes) · [Updating a Pass](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Updating.html) |
| Distribution | [Distributing and updating a pass](https://developer.apple.com/documentation/walletpasses/distributing-and-updating-a-pass) |
| HIG | [Human Interface Guidelines — Wallet](https://developer.apple.com/design/human-interface-guidelines/wallet) |
| Getting started / NFC overview | [Getting Started with Apple Wallet](https://developer.apple.com/wallet/get-started/) |
| NFC dictionary | [Pass.NFC](https://developer.apple.com/documentation/walletpasses/pass/nfc-data.dictionary) |
| Beacons | [Pass.Beacons](https://developer.apple.com/documentation/walletpasses/pass/beacons-data.dictionary) |
| Sharing UX | [Add, use, and share tickets and passes](https://support.apple.com/en-us/111112) · [Wallet & Privacy](https://www.apple.com/legal/privacy/data/en/wallet/) |

## 1. The `.pkpass` bundle

A pass is a ZIP of a directory ([Pass Design and Creation](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)):

| File | Role |
|---|---|
| `pass.json` | Identity, style dictionary, colors, relevance, barcodes, NFC, web service |
| `icon.png` (+ `@2x` / `@3x`) | Lock screen + Mail / Messages attachment preview |
| `logo.png` (+ `@2x` / `@3x`) | Top-left of the pass face |
| style images | `strip.png`, `thumbnail.png`, `background.png`, `footer.png` — see §5 |
| `en.lproj/pass.strings` (and other `.lproj`) | Localized strings / localized images |
| `manifest.json` | SHA-1 (hex) of **every file except** `manifest.json` and `signature` |
| `signature` | PKCS#7 detached signature of the manifest, signed with the Pass Type ID certificate, **including the WWDR intermediate**, with S/MIME `signing-time` |

Omit Finder metadata (`.DS_Store`). After signing, do not edit any file — a hash mismatch is the usual "pass will not add" failure ([TN2302 Passbook FAQ](https://developer.apple.com/library/archive/technotes/tn2302/_index.html)).

Identity of a pass is `passTypeIdentifier` + `serialNumber`. A replacement with those two keys equal **is** an update; a new serial is a second pass.

## 2. Required top-level keys

From [Pass Design and Creation](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html) and [Pass](https://developer.apple.com/documentation/walletpasses/pass):

| Key | Notes |
|---|---|
| `formatVersion` | Number `1` |
| `passTypeIdentifier` | `pass.` + reverse-DNS; must match the signing certificate |
| `serialNumber` | Unique within the pass type; opaque to PassKit |
| `teamIdentifier` | Team ID; must match the signing certificate OU |
| `organizationName` | Lock-screen / Mail attribution |
| `description` | VoiceOver. Start with a type noun ("Membership card", "Weekly coupon") plus one or two distinguishers — not a dump of every field |

Also typically set: `logoText`, `foregroundColor`, `backgroundColor`, `labelColor` as `rgb(r, g, b)`. If a `background.png` is present, `backgroundColor` is ignored.

Store non-visible app data in `userInfo`, not extra front fields.

## 3. Pass styles

Specify **one** style key whose value is the field dictionary. You cannot invent a style ([Pass Design and Creation](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)).

| Style key | Use | Distinctive chrome |
|---|---|---|
| `boardingPass` | One trip (air / train / bus / boat). Requires `transitType`: `PKTransitTypeAir` / `Boat` / `Bus` / `Train` / `Generic` | Transit cut; origin→destination primary pair |
| `coupon` | Offer / discount | Perforated top edge |
| `eventTicket` | One event or a season book | Small cutout; strip **or** background+thumbnail |
| `storeCard` | Loyalty, gift, points, stored value | Strip behind primary |
| `generic` | Anything else — gym, coat check, metro balance, **business card** | Thumbnail beside fields |

### 3.1 Poster event ticket (iOS 18+)

Poster event tickets reuse the `eventTicket` bundle plus semantic tags. If required tags are missing, Wallet shows the **legacy** event layout ([Creating a poster event pass](https://developer.apple.com/documentation/walletpasses/creating-an-event-pass-using-semantic-tags)).

Required for the poster face (omit any → fallback):

- `preferredStyleSchemes`: `["posterEventTicket"]`
- `semantics.eventName`
- `semantics.venueName`
- `semantics.venueRegionName`
- `semantics.venueRoom`
- `semantics.eventStartDate` / `eventEndDate` (ISO 8601)
- `semantics.eventType` (e.g. `livePerformance`)

Keep `eventTicket.primaryFields` / `secondaryFields` / `auxiliaryFields` so older OS versions still render. Semantic tags may live on the top-level `semantics` object **or** on a field; placement does not change behavior ([Supporting semantic tags](https://developer.apple.com/documentation/walletpasses/supporting-semantic-tags-in-wallet-passes)).

WWDC25 adds `upcomingPassInformation[]` on a poster ticket so one pass can list later events ([WWDC25 What's new in Wallet](https://developer.apple.com/videos/play/wwdc2025/202/)). Each entry follows the same semantic structure; add / update / remove entries via the web-service update path.

### 3.2 Poster generic (newer devices)

`posterGeneric` is a separate top-level style. Wallet prefers it when present; include a **second** legacy style (`generic`, `storeCard`, `eventTicket`, or `coupon`) on the same `pass.json` for older iOS / watchOS ([Creating a Poster Generic Pass](https://developer.apple.com/documentation/walletpasses/creating-a-poster-generic-pass)). Poster generic slots: `headerFields`, `primaryFields`, `footerFields`, `backFields`, `additionalInfoFields`, plus a square QR when supplied.

A business card that must run on current **and** older phones should ship `generic` as the fallback (or as the only style). Do not require `posterGeneric` for a card.

## 4. Field slots, counts, truncation

Each field is `{ "key", "label", "value" }` plus optional formatters (`dateStyle`, `timeStyle`, `isRelative`, `numberStyle`, `currencyCode`, `textAlignment`) and `changeMessage` ([PassFieldContent](https://developer.apple.com/documentation/walletpasses/passfieldcontent)).

Order **inside** a slot array is significant. Order **between** slot arrays is not — Wallet places primary / secondary / auxiliary by slot, not by JSON key order.

### 4.1 Official slot counts

From [Pass Design and Creation](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html):

| Slot | Typical max | Notes |
|---|---|---|
| `headerFields` | 3 | Only slot visible when passes are **stacked**. Use sparingly. |
| `primaryFields` | 1 (2 on `boardingPass`) | Most prominent |
| `secondaryFields` | 4 | Less prominent |
| `auxiliaryFields` | 4 (5 on `boardingPass`) | Least prominent on the face |
| `backFields` | unbounded | Scrolls; font shrinks as a field grows |
| Combined secondary+auxiliary | 4 on coupon / store / generic **with a square barcode** | Official combined cap |

Do **not** ship extra front fields "just in case." Hidden extras can appear if a future layout shows more slots. Non-visible data belongs in `userInfo`.

Apple Watch (legacy guide): no strip, no thumbnail, **no back** on older watchOS; header fields become one-line strips; primary then secondary then auxiliary, two fields per line only when they share a slot type. `logo` always wins over `logoText` when both do not fit; if there is no logo, `logoText` shows even when truncated. Rectangular barcodes rotate to portrait. ([Pass Design and Creation — Designing Passes for Apple Watch](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html))

### 4.2 Truncation — what Apple actually says

Apple does **not** publish per-slot character maxima. Official rules:

- Front contents "must be brief."
- "If there is too much text, some fields may not be displayed."
- Front does not wrap; overflow is dropped or ellipsized.
- Back may be long; users scroll; per-field type size decreases as that field grows.
- `description` is for VoiceOver, not a second front.

Working envelope (not a contract — measure on device + Dynamic Type):

| Slot | Keep labels near | Keep values near |
|---|---|---|
| Header | 8–12 | 6–12 |
| Primary | 10–16 | 18–28 |
| Secondary / auxiliary | 8–14 | 12–20 |
| Back | unconstrained | unconstrained (split huge legal into several keys) |

Always re-check with two header fields filled, a long Dynamic Type setting, and Apple Watch.

### 4.3 `changeMessage` and `%@`

When a field `value` changes on update **and** the field has `changeMessage`, Wallet shows that string as the update notification ([Updating a Pass — Devices Display Change Messages](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Updating.html), [PassFieldContent](https://developer.apple.com/documentation/walletpasses/passfieldcontent)).

- Include `%@` — Wallet substitutes the **new** value.
- Example: `"changeMessage": "Gate changed to %@"`.
- Omit `changeMessage` for silent updates (season-ticket refresh, new support phone).
- Change messages interrupt; reserve them for time-sensitive facts (gate, delay, venue move).
- You cannot send an arbitrary APNs alert on a pass. Visible text = `changeMessage`, not an `alert` key on the push.

### 4.4 Link tappability (back only)

From [Pass Design and Creation](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html) and [PassFieldContent](https://developer.apple.com/documentation/walletpasses/passfieldcontent):

- Back-field text is run through **data detectors** (URLs, phone numbers). Tap opens Safari or Phone.
- `dataDetectorTypes` is **back-only**. Default = all detectors. `[]` disables them. Not used on watchOS.
- `attributedValue` may contain an `<a href="…">` tag (the only supported HTML). It **overrides** `value` on iPhone. **watchOS ignores `attributedValue`** — always ship `value` as well.
- Front fields are **not** tappable links. A URL on `primaryFields` is just text (and will truncate).

`associatedStoreIdentifiers` (top-level array of iTunes item IDs) is the official "install our app from the pass" hook.

Contact info for the **signing organization** is required on the back ([App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), cited from the Wallet guide).

## 5. Images and @1x / @2x / @3x

All official sizes are in **points**. Ship the base PNG and the Retina twins Apple names with an `@2x` / `@3x` suffix before `.png` (for example `logo.png` and its 2x / 3x companions). Images scale to fill the slot and **crop** if the aspect ratio differs ([Pass Design and Creation — Images Fill Their Allotted Space](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)). Do not pad with whitespace to "nudge" layout — that breaks when the slot changes.

| Asset | Points | @1x px | @2x px | @3x px | Used on |
|---|---|---|---|---|---|
| `icon.png` | 29×29 | 29×29 | 58×58 | 87×87 | Lock screen, Mail, **iMessage / attachment preview** |
| `logo.png` | 160×50 allotted; usually narrower | 160×50 | 320×100 | 480×150 | Top-left, next to `logoText` |
| `footer.png` | 286×15 | 286×15 | 572×30 | 858×45 | Near barcode (`boardingPass`) |
| `thumbnail.png` | 90×90; keep aspect 2:3–3:2 | 90×90 | 180×180 | 270×270 | `generic` / `eventTicket` (no strip) |
| `background.png` | 180×220; cropped + **blurred** | 180×220 | 360×440 | 540×660 | `eventTicket` without strip |
| `strip.png` (modern iPhone widths) | event 375×98; gift/coupon 375×144; other 375×123 | same | ×2 | ×3 | `coupon`, `storeCard`, `eventTicket` |
| `strip.png` (older 320-pt width) | event 320×84; square-barcode 3.5" 320×110; other 320×123 | same | ×2 | ×3 | same |

Style → allowed images ([Table 4-1](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)):

| Style | logo | icon | strip | background | thumbnail | footer |
|---|---|---|---|---|---|---|
| `boardingPass` | ✓ | ✓ | | | | ✓ |
| `coupon` | ✓ | ✓ | ✓ | | | |
| `eventTicket` | ✓ | ✓ | ✓ | ✓ | ✓ | |
| `generic` | ✓ | ✓ | | | ✓ | |
| `storeCard` | ✓ | ✓ | ✓ | | | |

On `eventTicket`, **strip excludes background and thumbnail**. Watch does not show strip, thumbnail, or (on older watchOS) the back.

**HIG / design:** keep the face uncluttered; the system owns chrome (barcode well, rounded card, share). See [HIG — Wallet](https://developer.apple.com/design/human-interface-guidelines/wallet) and [Getting Started](https://developer.apple.com/wallet/get-started/).

`logo` vs `logoText`: `logo` is the mark; `logoText` is a short wordmark Wallet sets in the remaining header width. Do not bake the same wordmark into `logo.png` **and** set `logoText` — Watch will drop `logoText` when the logo is present and the text does not fit.

## 6. Barcodes

Prefer the `barcodes` **array** (iOS 9+ / watchOS 3+). Keep legacy `barcode` (singular) only if you still support iOS 8 ([Pass Design and Creation](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)). Wallet shows the first format the device supports.

Documented formats in the Wallet guide: `PKBarcodeFormatQR`, `PKBarcodeFormatPDF417`, `PKBarcodeFormatAztec`, `PKBarcodeFormatCode128`. watchOS **does not** render Code 128 — supply a 2D fallback or Watch shows no code. [Creating a Poster Generic Pass](https://developer.apple.com/documentation/walletpasses/creating-a-poster-generic-pass) also lists QR, PDF417, Aztec, Code 128, Code 39, Codabar, EAN-13, ITF.

Each entry: `message`, `format`, `messageEncoding` (typically `iso-8859-1`; Unicode is poorly supported by scanners), optional `altText`.

Use an **optical** scanner, not a laser, on LCD. Test on iPhone **and** Watch; QR is the most Watch-friendly (square). Wallet locks portrait and boosts backlight while the code is up ([Getting Started](https://developer.apple.com/wallet/get-started/)).

## 7. NFC

Passes can redeem at a contactless reader with **no barcode** ([Getting Started](https://developer.apple.com/wallet/get-started/), [Pass.NFC](https://developer.apple.com/documentation/walletpasses/pass/nfc-data.dictionary), [Creating a Poster Generic Pass](https://developer.apple.com/documentation/walletpasses/creating-a-poster-generic-pass)).

The pass.json key is `nfc` (dictionary). Apple's Value Added Services (VAS) path — used with Apple Pay terminals / certified readers — requires an NFC-enabled Pass Type ID certificate.

| Key | Rule |
|---|---|
| `message` | Payload presented to the reader. Keep ≤ 64 bytes; longer values are truncated. |
| `encryptionPublicKey` | Base64 X.509 SubjectPublicKeyInfo containing an ECDH P-256 public key |
| `requiresAuthentication` | Optional; Face ID / passcode before the NFC payload is released (newer iOS) |

NFC-enabled loyalty / membership on Apple Pay terminals: see Apple's "supporting loyalty and membership passes" note on [Getting Started](https://developer.apple.com/wallet/get-started/). Without the NFC entitlement on the certificate, the `nfc` block is ignored and the pass still adds.

## 8. Relevance — lock-screen presentation

Relevance is **passive** (no alert). Update notifications are a different channel ([Pass Design and Creation — Relevance Information](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)).

| Key | Limit | Format |
|---|---|---|
| `relevantDate` | 0 or 1 | W3C / ISO 8601 complete date + hours and minutes (seconds optional) |
| `locations` | ≤ 10 | `{latitude, longitude, altitude?, relevantText?}` |
| `beacons` | ≤ 10 UUIDs | `{proximityUUID, major?, minor?, relevantText?, name?}` ([Pass.Beacons](https://developer.apple.com/documentation/walletpasses/pass/beacons-data.dictionary)) |

When you have more than ten stores, pick the user's favorites and **update** the pass; or use one beacon UUID across many stores (that is how you exceed ten GPS points).

`relevantText` for a location: why the pass is relevant *here* ("Store nearby on 3rd and Main"). Do **not** put the organization name in it, and do not write "Redeem this pass at…". Time-based relevant text is supplied by the system.

### Style × relevance (official Table 4-2)

| Style | `relevantDate` | `locations` | Match rule |
|---|---|---|---|
| `boardingPass` | Recommended unless the pass is long-lived | Optional, **large** radius (~km) | Date **and** any location (iOS 6.1+). Date only if no location. |
| `coupon` | **Not supported** | Required if any relevance is set; **small** radius (~100 m) | Any location |
| `eventTicket` | Recommended (required with relevance before iOS 7.1) | Optional, large radius | Date and any location; date-only if no location |
| `generic` | Optional | Required if any relevance is set; small radius | Date and location; location-only if no date |
| `storeCard` | **Not supported** | Required if any relevance is set; small radius | Any location |

Exact radii are an implementation detail and may change. Do not lie about coordinates to force lock-screen presence. Simulator does **not** evaluate relevance — test on a device.

## 9. `voided` and `expirationDate`

A pass is treated as expired when **either** is true ([Pass](https://developer.apple.com/documentation/walletpasses/pass) expiration keys, widely restated in the package-format reference):

| Key | Meaning |
|---|---|
| `expirationDate` | Complete date with hours and minutes (seconds optional). After this instant the pass is expired. |
| `voided` | Boolean, default `false`. Set `true` after redemption / cancel (one-time coupon, used ticket). |

Expired / voided passes move out of the active stack (system UI). To **un-void**, push an update with `voided: false` and a future (or omitted) expiration — same `passTypeIdentifier` + `serialNumber`.

## 10. Web service and APNs

Create an updatable pass by setting `webServiceURL` (HTTPS, optional port) and `authenticationToken` ([Adding a Web Service to Update Passes](https://developer.apple.com/documentation/WalletPasses/adding-a-web-service-to-update-passes), [Updating a Pass](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Updating.html)).

You may change any field **except** `serialNumber` (and do not rotate `authenticationToken` — devices still holding the old pass will fail auth). Simulator does not register for pushes.

### Endpoints (relative to `webServiceURL`)

Documented flow in the two sources above; path shape is the long-standing PassKit web-service contract:

| Method | Path | Auth | Job |
|---|---|---|---|
| `POST` | `/v1/devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}/{serialNumber}` | `Authorization: ApplePass {authenticationToken}` | Register; body has `pushToken`. Persist device ↔ pass. `401` if token wrong. |
| `DELETE` | same | same | Unregister; drop the row; drop the device when it has no passes left |
| `GET` | `/v1/devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}?passesUpdatedSince={tag}` | device library id | Return `{ "serialNumbers": […], "lastUpdated": "<opaque tag>" }` for passes that device registered **and** that changed since the tag. No tag → all registered serials. |
| `GET` | `/v1/passes/{passTypeIdentifier}/{serialNumber}` | `ApplePass {authenticationToken}` | Latest `.pkpass`. Honor `If-Modified-Since` → `304`. |
| `POST` | `/v1/log` | — | Device-side error log; persist for support |

Push: for each registered device, send APNs to its `pushToken` with **empty JSON `{}`**, using the **same certificate + key that signed the pass**. Extra alert keys are the wrong tool and are lost when APNs coalesces. If APNs reports the token dead, delete that device and its registrations.

Update tag is opaque but totally ordered — later than every earlier tag (a timestamp string is fine).

**Caching:** Wallet keeps the last `.pkpass`. A "new" pass with a new serial sits beside the old one. A byte-identical body should 304. Users who never registered (no `webServiceURL`, or they blocked updates) keep whatever they first saved.

## 11. Sharing, AirDrop, NameDrop

Wallet can share a pass via the Share sheet (AirDrop, iMessage, Mail, third-party apps) and, on current iOS, by holding two iPhones near each other ([Apple Support 111112](https://support.apple.com/en-us/111112), [Wallet & Privacy](https://www.apple.com/legal/privacy/data/en/wallet/)). If Share is missing, the **issuer disabled sharing**.

Pass-level control: `sharingProhibited` (boolean, default `false`) on the Pass object ([Pass](https://developer.apple.com/documentation/walletpasses/pass)). `true` removes the Share control. A business card you *want* people to hand off should leave this false. A single-use ticket should set `true` and enforce server-side (a shared `.pkpass` is just a file).

Privacy note: when a managed pass is shared, the device may tell the pass provider that a share happened (e.g. guest-limit counting). Family Sharing may auto-accept a pass shared by a parent to a child account.

NameDrop-style nearby share is an OS feature on eligible devices; there is no separate pass.json "NameDrop" key. Disabling Share (`sharingProhibited: true`, or issuer-side disable) is what turns it off.

## 12. Signing checklist

1. Register a Pass Type ID; create a Pass Type ID certificate.
2. Download the current [Apple WWDR intermediate](https://www.apple.com/certificateauthority/).
3. `manifest.json` = `{ "relative/path": "<sha1 hex>", … }` for every file except manifest + signature.
4. Detached PKCS#7 of the manifest, WWDR **in the bag**, `signing-time` set.
5. Zip the directory contents (not the wrapper folder) as `something.pkpass`.
6. On failure: device / Simulator console. Usual causes: JSON typos, Team ID / pass type mismatch, missing WWDR, leftover `.DS_Store`, edited files after signing ([TN2302](https://developer.apple.com/library/archive/technotes/tn2302/_index.html)).

WWDC26 ships a Swift-on-Server **Pass Builder** (`buildpass`) that writes the manifest, signs with your cert + WWDR, and zips ([WWDC26 What's new in Wallet](https://developer.apple.com/videos/play/wwdc2026/209/)). Use it if you want the package mechanics off your plate; the `pass.json` contract above does not change.

## 13. HIG notes that affect layout

From [HIG — Wallet](https://developer.apple.com/design/human-interface-guidelines/wallet) and the Wallet guide:

- The system draws the card chrome, barcode well, and stacked-header strip. Do not mimic Wallet chrome in the artwork.
- Make the **next action** obvious (code or NFC) and keep the face to the facts the holder needs at the door / desk.
- Prefer system date / currency formatters so locale is correct.
- Test Dark / increased contrast / larger text — front slots will shed fields before they wrap.
- Mail and Messages preview the **icon**, not the strip or thumbnail. A 29-pt mark that is only a cropped photo will look like noise in iMessage.
