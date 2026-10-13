# Google Wallet — Generic pass reference

Sourced from Google Wallet API documentation. Generic is the vertical for anything that is not a dedicated ticket / loyalty / offer / gift / transit type — including a digital business card.

| Topic | Official source |
|---|---|
| Generic flow | [Add to Google Wallet flow](https://developers.google.com/wallet/generic/overview/add-to-google-wallet-flow) |
| Create class + object | [Create Passes Classes and Passes Objects](https://developers.google.com/wallet/generic/use-cases/create) |
| `GenericObject` schema | [REST Resource: genericobject](https://developers.google.com/wallet/reference/rest/v1/genericobject) |
| `GenericClass` schema | [REST Resource: genericclass](https://developers.google.com/wallet/reference/rest/v1/genericclass) |
| Card / details / list templates | [ClassTemplateInfo](https://developers.google.com/wallet/reference/rest/v1/ClassTemplateInfo) |
| Brand, images, character limits, button | [Brand guidelines — Generic](https://developers.google.com/wallet/generic/resources/brand-guidelines) |
| JWT save links | [Working with JSON Web Tokens](https://developers.google.com/wallet/generic/use-cases/jwt) · [Issuing passes for web, email, SMS](https://developers.google.com/wallet/generic/web) |
| Push + nearby notifications | [Trigger Push Notifications](https://developers.google.com/wallet/generic/use-cases/trigger-push-notifications) |
| Save many objects in one tap | [Add multiple pass types](https://developers.google.com/wallet/generic/use-cases/save-multiple-pass-types) |

## 1. Class vs object

| Resource | Meaning | REST |
|---|---|---|
| `GenericClass` | Program / template (layout, shared modules, Smart Tap issuers) | `POST https://walletobjects.googleapis.com/walletobjects/v1/genericClass` |
| `GenericObject` | One person's pass | `POST …/genericobject` |

An object **must** reference an existing, approved class of the same type (`classId`). IDs are `issuerId.identifier` — alphanumeric plus `.` `_` `-` ([GenericObject](https://developers.google.com/wallet/reference/rest/v1/genericobject)).

Just-in-time: you may embed `genericClasses` and `genericObjects` arrays in the JWT payload so Google creates them when the user saves ([Add to Google Wallet flow](https://developers.google.com/wallet/generic/overview/add-to-google-wallet-flow)).

`state` on the object (`ACTIVE` default, `INACTIVE`, `EXPIRED`, `COMPLETED`) controls which Wallet pile the card sits in. `validTimeInterval` also expires the object when the window ends.

## 2. Object fields (card face)

From [GenericObject](https://developers.google.com/wallet/reference/rest/v1/genericobject):

| Field | Required | Where it renders |
|---|---|---|
| `id` | yes | `issuerId.objectSuffix` |
| `classId` | yes | `issuerId.classSuffix` |
| `cardTitle` | yes | Header row — business / program name ("Northwind Studio") |
| `header` | yes | Title row — the pass title ("Alex Rivera" on a card, "Library card" on a membership) |
| `subheader` | no | Label above the title ("Director of Design", venue, …) |
| `logo` | no | Upper-left + list thumbnail. If omitted, first letter of `cardTitle` |
| `wideLogo` | no | Replaces `logo` on the card view when set |
| `hexBackgroundColor` | no | `#RRGGBB`. Else: hero dominant → logo dominant → Google-chosen |
| `heroImage` | no | Full-width banner on the card (100% width) |
| `barcode` | no | Code + optional `alternateText` (alt-only is allowed) |
| `rotatingBarcode` | no | Rotating code (transit-style) |
| `textModulesData[]` | no | Detail text. Class + object **both** show. API display cap: 10 class + 10 object |
| `linksModuleData` | no | URI list. Class + object both show. API display cap: 10 + 10 |
| `imageModulesData[]` | no | Full-width image under the hero. Only **one** class image and **one** object image render |
| `appLinkData` | no | Front-of-pass button. Object wins if both class and object set it |
| `genericType` | no | See §2.1 |
| `notifications` | no | Expiry **or** upcoming — not both; expiry wins |
| `smartTapRedemptionValue` | no | ASCII NFC payload; class must enable Smart Tap |
| `merchantLocations[]` | no | ≤ 10; nearby notification. Extra points rejected |
| `messages[]` | no | ≤ 10; detail-template messages |
| `groupingInfo` | no | Stack related objects |
| `passConstraints` | no | NFC / screenshot limits |
| `saveRestrictions` | no | Checked **only at save**; later edits do not evict an already-saved pass |
| `valueAddedModuleData[]` | no | ≤ 10 |
| `linkedObjectIds[]` | no | Auto-push other objects to holders; cannot unlink; other-issuer IDs rejected |

### 2.1 `genericType`

| Enum | Use |
|---|---|
| `GENERIC_OTHER` | Default catch-all — **business card** |
| `GENERIC_GYM_MEMBERSHIP` / `GENERIC_LIBRARY_MEMBERSHIP` | Memberships |
| `GENERIC_LOYALTY_CARD` | Possible, but Google tells you to use the dedicated Loyalty vertical instead |
| `GENERIC_ENTRY_TICKET` / `GENERIC_SEASON_PASS` / `GENERIC_PARKING_PASS` / `GENERIC_RESERVATIONS` | Admission-shaped |
| `GENERIC_VOUCHER` / `GENERIC_RECEIPT` | Offer / proof |
| `GENERIC_AUTO_INSURANCE` / `GENERIC_HOME_INSURANCE` / `GENERIC_UTILITY_BILLS` | Document-shaped |

## 3. Class fields that matter for layout

From [GenericClass](https://developers.google.com/wallet/reference/rest/v1/genericclass):

| Field | Role |
|---|---|
| `id` | `issuerId.classSuffix` |
| `classTemplateInfo` | Overrides default card / details / list rows. Unset → Google's default field set |
| `enableSmartTap` | Partner-only. Contact support. |
| `redemptionIssuers[]` | Issuer IDs allowed to redeem over Smart Tap; each needs a Smart Tap key |
| `textModulesData` / `linksModuleData` / `imageModulesData` | Shared program copy / links / image |
| `callbackOptions` | Server callbacks on save / delete |
| `multipleDevicesAndHoldersAllowedStatus` | One holder vs many |
| `viewUnlockRequirement` | Screen-lock to view |
| `merchantLocations[]` | ≤ 10 class-level nearby points |
| `securityAnimation` | Official animation overlay |

## 4. Card templates (`classTemplateInfo`)

[ClassTemplateInfo](https://developers.google.com/wallet/reference/rest/v1/ClassTemplateInfo):

- `cardTemplateOverride.cardRowTemplateInfos[]` — **at most three rows** on the card view.
- Each row is exactly one of `oneItem` / `twoItems` / `threeItems`.
- Field refs look like `object.header`, `object.textModulesData['ROLE']`, `class.textModulesData['HOURS']`.
- List-view override: `firstRowOption` + `secondRowOption` (second row is suppressed when the object is in a group).
- Details template controls the expanded back-of-pass sections.

Brand guide adds a usability cap on top of the API: **≤ two fields per row, and up to three rows if possible** ([Brand guidelines — Content](https://developers.google.com/wallet/generic/resources/brand-guidelines)). Prefer `twoItems` rows for a business card (role | company, phone | email).

## 5. Official character limits (English)

From [Brand guidelines — Content / Notifications](https://developers.google.com/wallet/generic/resources/brand-guidelines). These are English; translations run longer, so stay under.

| Surface | Limit |
|---|---|
| Title label (`cardTitle`) | < 47 characters |
| Subtitle label (`subheader`) | < 88 characters |
| Field / title label | < 20 characters |
| Field data | < 15 characters |
| Notification title | < 29 characters |
| Notification collapsed body | < 40 characters |
| Notification expanded body | < 80 characters |

Headings, labels, and names: **title case**.

The brand-guide **module counts** are tighter than the REST display caps — design to the guide, and do not depend on the extra API slots remaining visible forever:

| Module | Brand-guide count |
|---|---|
| `imageModulesData` | One, on class **or** object |
| `infoModuleData` | Up to two (class + object combined). One-column list |
| `linksModuleData` | Up to **four URIs total** (class + object) |
| `textModulesData` | Up to **two** between class and object |

REST `textModulesData` / `linksModuleData` advertise 10+10 displayed. Ship to the brand-guide numbers unless you have a reason and have screenshotted the extra modules on current Android.

## 6. Images

All figures from [Brand guidelines](https://developers.google.com/wallet/generic/resources/brand-guidelines). Prefer PNG.

### 6.1 Logo (circular mask)

| Rule | Value |
|---|---|
| Min size | 660×660 px |
| Aspect | 1:1 |
| Mask | Google applies a **circle**. Do **not** pre-mask |
| Safe area | **15% margin** on all sides so the mark survives the circle |
| Background | Full-bleed square; the corners will be cropped away |

If `logo` is missing, Wallet shows the first letter of `cardTitle`.

### 6.2 Wide logo

Supported on generic (and tickets, boarding, loyalty, offer, gift, transit).

| Rule | Value |
|---|---|
| File | Transparent PNG |
| Recommended | 1280×400 px |
| Min height | 400 px, width proportional |
| Aspect | 16:5 |
| Contrast | Light mark on dark `hexBackgroundColor`, dark mark on light |

When `wideLogo` is set it **replaces** `logo` on the card view.

### 6.3 Hero image

`heroImage` is a full-width banner. If omitted, Google shows a **category fallback**.

| Rule | Value |
|---|---|
| Recommended | **1032×812 px** |
| Aspect | 1032:812 (~5:4) |
| File | PNG; transparent PNG if the card color should show through |
| Do | Photography / illustration; **20 dp padding** top and bottom |
| Don't | **Embed text** (not localized); square-ish crop that is not ~5:4; thin ribbons; content touching the top/bottom edge |

### 6.4 Additional / barcode images

| Asset | Rule |
|---|---|
| `imageModulesData.mainImage` | Full width under the hero. Min 1860 px wide, variable height, colored background |
| Image above barcode | Max 20 dp tall. One image: 1600×80. Two: 80×80 + 780×80 |
| Image below barcode | Max 20 dp tall. Square 80×80 or full-width 1600×80 |

### 6.5 Background color

`hexBackgroundColor`. Google warns off high-saturation neon (`#00FF00`, `#00FFFF`) — text bleeds. Recommended swatches in the brand guide include `#1a1a1a`, `#677088`, `#e8eaed`, `#f8f9fa`, `#ffffff`, `#d6322d`, `#f78f48`, `#f9bb2d`, `#1e7e3b`, `#216acf`, `#9147df`, plus light tints `#fce8e6` / `#e6fffa` / `#e8f0fe`.

## 7. Links and Smart Tap

### 7.1 `linksModuleData`

URI prefixes from [Brand guidelines — Modules](https://developers.google.com/wallet/generic/resources/brand-guidelines):

| Prefix | Result |
|---|---|
| `http:` / `https:` | Opens the site or a Maps query; link / map icon |
| `tel:` | Dials; phone icon |
| `mailto:` | Compose mail; mail icon |

Put the vendor app / site in `linksModuleData` so the holder can leave Wallet for the rich profile. Deep links should land in Play Store if the app is missing; deferred deep link after install is preferred.

`appLinkData` is the **front-of-pass** button (`webAppLinkInfo` for a website; `displayText` ≤ 30 chars; object overrides class; `iosAppLinkInfo` is deprecated — "Links to open iOS apps are not supported"). It is the only documented way to put a tappable "Share your details" CTA on the *front* of a Google pass.

> ⚠️ **P1 unverified (#8) — see [`verify.md`](verify.md).** The FAQ says "Applinking requires allowlisting which can be requested here," with **no criteria, eligibility, form content, or timeline** published, and the linked form was not fetched. This gates whether a front-of-pass button is available to RavenPass at all — do not promise it before opening the allowlist form signed into the Google Pay & Wallet Console. Until then, ship the QR + `linksModuleData` (detail-view links) as the CTA.

### 7.2 Smart Tap (NFC)

Partner program — `enableSmartTap` is "available only to Smart Tap enabled partners. Contact support" ([GenericClass](https://developers.google.com/wallet/reference/rest/v1/genericclass)).

To transmit over NFC:

1. Class: `enableSmartTap: true` and `redemptionIssuers` listing issuer IDs that have a Smart Tap key.
2. Object: `smartTapRedemptionValue` — **ASCII only**.
3. Terminal must be Smart Tap certified.

`passConstraints` can further limit NFC / screenshots. Without the partner enablement, set a QR `barcode` instead — do not ship a dead `smartTapRedemptionValue`.

## 8. "Add to Google Wallet" JWT save links

From [JWT](https://developers.google.com/wallet/generic/use-cases/jwt) and [Issuing passes for web, email, SMS](https://developers.google.com/wallet/generic/web):

1. Encode claims:

```json
{
  "iss": "service-account@…",
  "aud": "google",
  "typ": "savetowallet",
  "iat": 1710000000,
  "origins": ["https://example.com"],
  "payload": {
    "genericObjects": [
      { "id": "ISSUER.OBJECT", "classId": "ISSUER.CLASS" }
    ]
  }
}
```

2. Sign **RS256** with the Google Cloud service-account key that is authorized on the Wallet Business Console (Android SDK path signs with the app SHA-1 instead).
3. Issue the URL:

```text
https://pay.google.com/gp/v/save/<signed_jwt>
```

That URL is valid in web, email, SMS, chat, and **can only be initiated in the context of a logged-in Google identity**. Present it as Google's official **Add to Google Wallet** button (primary or condensed, black only, min height 48 dp, 8 dp clear space, equal-or-larger than sibling buttons). Do not recolor, relocalize, or rebuild the button. Localized assets are listed in the brand guide. RU-only surfaces still use the older "Save to phone" assets.

> **⚠️ The 1800-character ceiling is the key practical constraint.** "The safe length of an encoded JWT is 1800 characters… If the length is over 1800 characters, the save may not work due to truncation by web browsers" ([Issuing passes for web](https://developers.google.com/wallet/generic/web)). A card with a photo URL, several text modules, links, and a barcode blows past it. **Remedy (the skinny JWT):** pre-create the class and object server-side via REST, then hand out a JWT whose `payload.genericObjects[]` carries only `{ "id": "ISSUER_ID.OBJECT_SUFFIX" }` — the full object already exists at Google, so the link stays short ([FAQ](https://developers.google.com/wallet/generic/resources/faq)). Just-in-time (embedding the whole class/object in the JWT) is fine only when the result stays under 1800 chars.

`origins` should list the HTTPS origins that embed the button.

To save many already-inserted objects (mixed verticals) in one tap, put each type's array in `payload` ([Add multiple pass types](https://developers.google.com/wallet/generic/use-cases/save-multiple-pass-types)).

**View in Google Wallet** is a different official button — use it only to open a pass the user already saved.

## 9. Updates and notification limits

### 9.1 Mutating a live pass

`PATCH` / `UPDATE` on the class or object REST resource. Holders see the new values on the next Wallet sync. `saveRestrictions` changes do **not** apply to already-saved objects.

### 9.2 Message + push

[Trigger Push Notifications](https://developers.google.com/wallet/generic/use-cases/trigger-push-notifications):

- `addmessage` with `message_type: TEXT_AND_NOTIFY` adds a detail-template message **and** a lock-screen notification.
- User must have Wallet notifications enabled.
- Tap → card view with a "View Message" callout → details, unread highlighted.
- Hyperlinks in the body must be **about this pass** (Acceptable Use).
- Lock-screen copy is **owned by Google**, not your `header`/`body` verbatim.
- **Maximum 3 notification-triggering messages per pass per 24 hours.** A fourth `TEXT_AND_NOTIFY` returns `QuotaExceededException`. Further updates must use `TEXT` (silent message) or a regular PATCH.
- Google may throttle if they judge the traffic as spam.
- `UPDATE` / `PATCH` can edit or remove messages.

**Developer-authored arbitrary push is not supported** ("Developer authored push notifications are not currently supported by Google Wallet," [FAQ](https://developers.google.com/wallet/generic/resources/faq)). The only notification surfaces are: the fixed Generic **system reminders** (§9.3), `addmessage` messages (≤10/object), and **field-update notifications** via `notifyPreference: NOTIFY`. The latter "will only be sent to users if the field is part of an **allowlist**" and the setting "is ephemeral and needs to be set with each PATCH or UPDATE." ⚠️ P3 unverified (#24) — the allowlisted field set is not documented. A business card almost never needs any of these.

### 9.3 Expiry / upcoming

`notifications` supports **one** of ([GenericObject](https://developers.google.com/wallet/reference/rest/v1/genericobject)):

| Key | When Google fires |
|---|---|
| `expiryNotification.enableNotification` | **2 days before** `validTimeInterval.end` |
| `upcomingNotification.enableNotification` | **1 day before** `validTimeInterval.start` |

If both are set, expiry wins and upcoming is ignored.

### 9.4 Nearby

Add `merchantLocations` (≤ 10 class + ≤ 10 object; extra points are rejected). Google chooses radius and dwell; Google writes the notification text. Requires notifications **and** precise, always-on location for Wallet. Sticky while the user is at the point; swipe to dismiss; disappears on leave ([Trigger Push Notifications — Nearby](https://developers.google.com/wallet/generic/use-cases/trigger-push-notifications)). `merchantLocations` replaces the deprecated `LatLongPoints` / `LoyaltyClass.locations`. ⚠️ P3 unverified (#22) — the "Google-set radius" value is not documented.

## 10. Branding and naming

From [Brand guidelines](https://developers.google.com/wallet/generic/resources/brand-guidelines):

- Write **Google Wallet** (capital G, capital W). Do not abbreviate. Do not mimic Google's typeface. Use the localized product name in the markets they list (e.g. US Spanish → "Billetera de Google").
- Buttons: official SVG / PNG / Android XML only. Primary on light backgrounds; condensed when width is tight.
- Pass content must follow Google Payments content policies, including linked websites.
- Partner platform placement: always include an app or site URI in `linksModuleData` so the holder can reach the rich profile.

## 11. Business-card field map (Google)

| Intent | Field |
|---|---|
| Company | `cardTitle` |
| Person | `header` |
| Role | `subheader` |
| Mark | `logo` (square, 15% pad) — **not** a typeset wordmark |
| Texture / portrait | `heroImage` with **no** name/title baked in |
| QR to vCard or profile | `barcode.type = QR_CODE`, `barcode.value` = URL |
| Phone / mail / web / LinkedIn | `linksModuleData.uris[]` |
| Address / blurb | `textModulesData[]` (one or two) |
| Brand color | `hexBackgroundColor` from the recommended list or a non-neon brand hex |
| NFC (if enrolled) | class Smart Tap + object `smartTapRedemptionValue` |

Worked JSON: [`business-card-layout.md`](business-card-layout.md).

## 12. Operational limits, Demo Mode → publishing, and hard prohibitions

From [FAQ](https://developers.google.com/wallet/generic/resources/faq), [Requesting publishing access](https://developers.google.com/wallet/generic/test-and-go-live/request-publishing-access), and [GenericObject](https://developers.google.com/wallet/reference/rest/v1/genericobject).

### Operational limits to design against

- API is **rate-limited to 20 requests/second**. No official SLA; recommended **10 s timeout** (p99 latency ~5 s).
- Server **callbacks arrive with `Googlebot` and `Google-Valuables` user agents** — allowlist them in your CDN/WAF or they get blocked.
- Class review is **automatic** — set `reviewStatus: underReview` and the platform sets it to `approved`; it cannot be set back to `draft`.

### Demo Mode → publishing access (required before real users)

- A new Issuer account starts in **Demo Mode**: you can only issue to accounts with the **Admin/Developer role** on the issuer or added as **test accounts**, and every pass title carries a **`[TEST ONLY]`** prefix.
- To leave it: complete your **Business Profile** (business info + a payments profile) **and** create **≥1 Passes Class**, then click **"Request publishing access."** Screenshots are **no longer** required. Once granted, the `[TEST ONLY]` prefix disappears on reopen. ⚠️ P3 unverified (#25) — no review turnaround is published. **Start this early; it blocks serving any non-test user.**
- Multi-tenant note: "If the Issuer account for pass development contains classes for other merchants, you must set up a new account on behalf of the merchant," and an issuer gets exactly **one** Collector ID — an architecture decision with no easy reversal.

### Hard prohibitions (not configurable)

- **No personal images on passes** — "Google Wallet does not support personal images on passes… personal images are not allowed." Use brand art for `logo`/`heroImage`; keep a headshot behind the URL. (Apple publishes no equivalent ban — see [`verify.md`](verify.md) #29.)
- **Cannot delete a class or object** — users can only de-link. Short, stable, never-reused suffixes are mandatory.
- `linkedObjectIds[]` cannot be unlinked and cannot cross issuers; ⚠️ P3 unverified (#23) — there is a per-object limit beyond which new links are "ignored silently," value not documented.
- **Generic Private Pass is the wrong vertical for a business card** — it is scoped to sensitive data (health/government ID) and invites a regulatory-grade review; it is the only path where the whole pass lives in the JWT (no stored object), but the 1800-char ceiling still applies.

### iOS coverage

⚠️ P1 unverified (#4) — whether a Google Wallet pass can be saved/viewed **on iOS** is not stated on any page fetched. Plan Android-first and ship a `.pkpass` for iOS users.
