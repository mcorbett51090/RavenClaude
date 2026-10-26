# Pass types beyond generic: loyalty, membership, coupons, event tickets

> **Retrieved 2026-10-26** from Apple's Wallet Passes documentation (DocC JSON), the HIG, WWDC24-10108,
> WWDC26-209, Apple's open-source `apple/pass-builder` (default branch), Google Wallet developer docs, brand
> guidelines and REST reference. Tags: `[doc]` primary page, `[code]` Apple pass-builder source, `[3p]` vendor or
> blog only, `[unverified]`, `[inference]`. **Basics** (`pass.json` structure, signing, the web service, NFC basics,
> JWT save links) are in [`apple.md`](apple.md) and [`google.md`](google.md) and are not repeated here.

## 0. What changes a builder's design

| # | Rule | Why |
|---|---|---|
| 1 | **Model fields by semantic role, not screen slot** (`balance`, `tier`, `memberId`, `eventName`, `seat`, `offerTitle`, `expiry`); compute placement per platform | The same fact lives in different places: Google's `rewardsTier` is a **class** field; Google `loyaltyPoints.balance` is about 7 characters; Apple `storeCard` fits 4 secondary + auxiliary fields **combined** `[doc]` |
| 2 | **Ship loyalty/membership, then coupons, then classic event tickets.** Skip Apple *poster* event tickets unless the tenant holds an Apple NFC certificate | "Poster event tickets aren't compatible with tickets that require a QR code or barcode for entry" `[doc]`; Apple's validator errors on a poster ticket without `nfc` + `requiresAuthentication` `[code]` |
| 3 | **Apple: two layouts per template** — `posterGeneric` (iOS 27+) plus a legacy fallback (`storeCard`, `generic` or `coupon`) generated from the same roles | "Wallet's style resolution prioritizes `posterGeneric` when present"; older iOS needs the legacy dictionary on the same pass `[doc]` |
| 4 | **A Google class is live, shared and undeletable** — show the blast radius before publish | Class edits reach every object at next sync; classes and objects cannot be deleted; a PATCH replaces whole arrays `[doc]`. Apple has no class, so a template change means re-signing and pushing every pass `[inference]` |
| 5 | **Keep master artwork; derive per-slot crops server-side** | Google's hero guidance moved to **1032×812 (≈5:4)** in 2026 (from the long-cited 3:1) `[doc]`, `[3p for the date]`; Apple slots are points at @2x/@3x; Google logos are circle-masked |
| 6 | **A notification composer with per-platform budgets**, not a raw send box | Google: **3** notifying messages and **3** field-update notifications per pass per 24 h (`QuotaExceededException` past that) `[doc]`. Apple notifies only through a changed field's `changeMessage`, and the HIG says "Never use a change message for marketing" `[doc]` |
| 7 | **Barcode picker = intersection with an automatic QR fallback** | iOS 27 added Code 39, Codabar, EAN-13, ITF, but "if you provide only a new barcode type, the pass will not render a barcode on iOS 26 and earlier" `[doc: WWDC26]`; Google rotating barcodes are QR or PDF417 only `[doc]` |
| 8 | **Escalate Apple multi-tenant signing to the owner before shipping new types** | App Store Review Guideline 1.5 (updated 2026-10-16): passes should be "signed with a dedicated certificate assigned to the brand or trademark owner of the pass" `[doc]`. Enforcement for web-distributed passes is `[unverified]`. Google's terms explicitly allow authorised aggregators `[doc]` |

## 1. Loyalty and membership

### Apple `storeCard` and `posterGeneric`

- **storeCard face:** logo + `logoText`, up to 3 header fields (archived guide), **one primary field over the strip**,
  secondary + auxiliary **≤ 4 combined on one row**, then the barcode `[doc]`. Fields that don't fit are **dropped
  whole, not truncated** ("If you include more fields than the pass can display, the additional fields don't
  appear on the pass face") `[doc]`.
- **No points field.** Use a field with `currencyCode` or `numberStyle` — not both (the validator warns)
  `[code]`. `semantics.balance` (`{amount, currencyCode}`) is "only for a store card pass" `[doc]`. Tier and
  secondary points are ordinary fields.
- **Images:** `icon` (required), `logo`, `strip` 375×144 pt. Watch hides the strip, thumbnail and back `[doc]`.
- **Relevance:** ≤ 10 `locations`, ≤ 10 beacons; legacy rule for store cards and coupons — no relevant date,
  location required, radius "on the order of a hundred meters" `[doc: archived guide]`. Whether iOS 18
  `relevantDates` applies to store cards is `[unverified]`.
- **Enrolment:** `personalization.json` with `requiredPersonalizationFields` (Name, PostalCode, EmailAddress,
  PhoneNumber); in practice tied to NFC/VAS programmes `[unverified that it is NFC-only]`.
- **NFC / VAS** needs Apple's entitlement and VAS-certified terminals (Apple lists Square, Adyen, Verifone Flex
  among certified providers) `[doc]` — out of reach for most small-business tenants.
- **`posterGeneric` (iOS 27 / watchOS 27):** "membership, loyalty, coupon, rewards, gift card, and other pass
  types in a poster-style format". Face: background artwork (358×448 pt, "a material strip covers the bottom
  edge"), primary logo, header field, primary fields (an unlabelled first primary displays as a bold title), a
  footer field, optional barcode `[doc]`. **Counts conflict:** the doc says up to four primary and two footer
  fields; WWDC26 says only the first footer field is displayed — design for one `[doc vs doc]`.

### Google `LoyaltyClass` / `LoyaltyObject`

| Field | Level | Limit |
|---|---|---|
| `loyaltyPoints {label, balance}` | object | label ≤ 9, balance ≤ 7 characters |
| `secondaryLoyaltyPoints` | object | same shape |
| `accountName`, `accountId` | object | ≤ 20 each; `accountId` is also the barcode fallback |
| `rewardsTier`, `secondaryRewardsTier` (+ labels) | **class** | `rewardsTier` ≤ 7 |
| `programName`, `programLogo`, `wideProgramLogo`, `heroImage`, `hexBackgroundColor` | class (`heroImage` also per object) | — |
| `linkedOfferIds[]` | object | offers must already exist |

- **Tier strategy is a builder decision:** Google suggests one class per tier; the alternative is one class with
  the tier in object `textModulesData` `[doc]`, `[inference]`.
- **Notifications:** `addMessage` with `TEXT_AND_NOTIFY` (≤ 3 per pass per 24 h; links must relate to the pass);
  field-update notifications with `notifyPreference: NOTIFY_ON_UPDATE`, sent on every request, only for tier,
  program name and the two balances, also ≤ 3 per 24 h; ≤ 10 `messages` per pass `[doc]`.
- **Nearby:** `merchantLocations` ≤ 10 per class + 10 per object; Google decides distance and text; needs precise
  always-on location `[doc]`.
- **Linking:** `linkedOfferIds`, or Auto Linked Passes (`linkedObjectIds`, same issuer, ≤ 50, best effort, users
  can opt out) `[doc]`. Since 2026-06-30, saved coupons upgrade to linked loyalty accounts when users connect a
  merchant account `[doc: release notes]`.
- **App button:** `appLinkData` (display text ≤ 30) **requires allowlisting** `[doc: FAQ]`.
- **Generic used as membership:** most content is object-level; `genericType` includes
  `GENERIC_GYM_MEMBERSHIP`, `GENERIC_LIBRARY_MEMBERSHIP`, `GENERIC_SEASON_PASS`; default rows use reserved
  text-module ids `row2left`, `row2right`, `row3left`, `row3right`; automatic reminders 24 h before the valid
  interval starts and 48 h before it ends `[doc]`. Use Generic for memberships without points, Loyalty when
  there is a balance `[inference]`.

## 2. Event tickets

### Apple `eventTicket`, classic

- Header, one primary, secondary, auxiliary, plus an optional second auxiliary row (`row: 1`, event tickets
  only) `[doc]`.
- Images: `icon`, `logo`, and **either** `strip` **or** `background` + `thumbnail` — never both; non-poster
  backgrounds are blurred `[doc]`.
- `groupingIdentifier` groups tickets with the same pass type ID and style; a `.pkpasses` bundle (MIME
  `application/vnd.apple.pkpasses`) carries **up to 10 passes or 150 MB** per download `[doc]`.
- `relevantDates[]` (iOS 18+) replaces `relevantDate`; multi-day events use several intervals `[doc]`.
- Season tickets (iOS 26+): `upcomingPassInformation[]` entries; an entry without a date shows as TBD `[doc]`.

### Apple poster ("enhanced") event ticket — read before offering it

- Opt in with `"preferredStyleSchemes": ["posterEventTicket", "eventTicket"]` while keeping `eventTicket`; failed
  validation falls back to legacy `[doc]`. Legacy fields that are present but invalid make "ingestion fail on all
  devices" `[doc]`.
- Required tags: the doc lists `eventName`, `venueName`, `venueRegionName`, `venueRoom` (+ team abbreviations for
  sports, `performerNames` for live performance); Apple's validator requires `eventName`, `venueName` **and NFC**
  `[doc vs code]`. Which iOS introduced it (18 per WWDC24; "iOS 26 and later" in the current article) is a
  documented conflict.
- Poster-only extras: event-guide URLs (parking, food, merchandise, transit, accessibility…), 1–4 quick actions,
  `useAutomaticColors`, `footerBackgroundColor`, `eventLogoText`, `primaryLogo` (30 pt tall), `secondaryLogo`
  (12 pt tall), `artwork` 358×448 pt `[doc]`.

### Google `EventTicketClass` / `EventTicketObject`

- Class: `eventName` (required), `eventId` (≤ 64; groups a user's tickets for one event — "if you use only one
  class per event, you can simply set this to the classId"), `venue`, `dateTime{doorsOpen, start, end}`, custom
  labels for seat/row/section/gate `[doc]`.
- Object: `seatInfo`, `reservationInfo.confirmationCode` (shared by one order), `ticketHolderName`,
  `ticketNumber`, `ticketType`, `faceValue`, `groupingInfo` `[doc]`.
- **Rotating barcode:** TOTP `valuePattern`, QR or PDF417 only; insert the object server-side and reference it by
  id so the key is not in the save link; a static fallback "negates most of the security benefits" `[doc]`.
- Automatic reminder 3 h before the event; update-and-notify only within 3 h of the start, ≤ 3 per 24 h `[doc]`.
- One JWT may carry many objects; past ~1800 characters, pre-insert and reference by id `[doc]`.

## 3. Coupons and offers

- **Apple `coupon`:** ≤ 3 header, one primary over a 375×144 pt strip, ≤ 4 secondary + auxiliary combined;
  `expirationDate` plus a relative-date field for the visible expiry; `voided: true` after a single-use
  redemption; no promo-code field (use a field plus the barcode `message`/`altText`); location-only relevance
  (~100 m); no expiry-reminder concept `[doc]`. iOS 27 coupon image changes are self-contradictory in Apple's own
  Pass Designer page `[unverified]`.
- **Google `OfferClass` / `OfferObject`:** class `title` (≤ 60), `provider` (≤ 12), `redemptionChannel`
  (`INSTORE | ONLINE | BOTH | TEMPORARY_PRICE_REDUCTION`), `finePrint`, `shortTitle` (≤ 20), `titleImage`; object
  `validTimeInterval`, `state`; automatic expiry reminder 48 h before expiry (`disableExpirationNotification`
  exists for offers only); single use = PATCH `state: COMPLETED` `[inference: no single-use flag]`; promo codes
  can use barcode type `TEXT_ONLY` (no rotation, no alternate text) `[doc]`.

## 4. Layout constraints to generate a builder from

### Apple — front-of-pass maxima (extra fields are dropped, not truncated)

| Style | header | primary | secondary | auxiliary | footer | Images | Min OS |
|---|---|---|---|---|---|---|---|
| `storeCard` | ≤ 3 | 1 over strip | ≤ 4 **combined with aux** | (combined) | – | icon, logo, strip | iOS 6 |
| `coupon` | ≤ 3 | 1 over strip | ≤ 4 **combined with aux** | (combined) | – | icon, logo, strip | iOS 6 |
| `generic` | ≤ 3 | 1 beside thumbnail | ≤ 4 | ≤ 4 (8 total; 4 combined with a square barcode) | – | icon, logo, thumbnail | iOS 6 |
| `eventTicket` classic | ≤ 3 | 1 | ≤ 4 | ≤ 4 + a second row of ≤ 4 | – | icon, logo, strip **or** background + thumbnail | iOS 6 |
| poster event ticket | semantic | semantic | semantic | semantic | seat footer ≤ 4 elements | primaryLogo, secondaryLogo, artwork/background | iOS 18 (doc conflict) |
| `posterGeneric` | 1 | ≤ 4; unlabelled first = title | – | – | design for 1 | icon, primaryLogo, artwork | iOS 27 |

**Image slots** (points; supply @2x and @3x): `icon` 38×38 (required, all styles) · `logo` 50 tall, 50–160 wide ·
`primaryLogo` 30 tall, 30–126 wide · `secondaryLogo` 12 tall, 12–135 wide · `strip` 375×144 · `thumbnail` 90 tall,
60–90 wide · `artwork` 358×448 · `background` 343×503 per the HIG vs 345×505 per Apple's pass-builder `[conflict]`.

**Field attributes worth exposing:** `label`, `changeMessage` (must contain `%@`), `currencyCode` *or*
`numberStyle`, `dateStyle`/`timeStyle`, `isRelative`, `ignoresTimeZone`, `textAlignment` (invalid on primary and
back fields), `attributedValue` (an `<a href>` only; not on watchOS) `[doc]`.

**Featured actions (iOS 27, all styles):** `featuredActions: [{identifier, type, url}]`, **max 2**, `type` from a
fixed list (`call`, `place`, `order`, `shop`, `addToBalance`, `membershipBenefits`, `bookAppointment`,
`viewOffersRewards`, `viewSchedule`, …) `[doc]`. Whether the issuer controls the icon and label is
`[unverified]` — the doc prose says so, the JSON shape does not.

### Google — the template skeleton every vertical shares (set on the class)

| Section | Control | Rules |
|---|---|---|
| Card title | fixed per vertical (logo + issuer + title) | "Neither the field references … nor their position can be changed"; a wide logo replaces logo + issuer on Android |
| Card rows | `cardTemplateOverride.cardRowTemplateInfos[]` of one/two/three items | ≥ 1 row, recommend ≤ 2; text fields or text modules only — links and image modules are not rendered here |
| Barcode section | top/bottom details | text or image modules; images 80 px tall |
| Hero | `object.heroImage` → `class.heroImage` | full width; fallback category art when none |
| Details | `detailsTemplateOverride` | any field, module or messages |
| List view | first/second row options | logo, colour, 3 rows |

**Limits (sources conflict; enforce the strictest):** `textModulesData` 10 per class + 10 per object (template
docs say 20; brand guidelines say "up to two"), header ≤ 35, body ≤ 500; `imageModulesData` 1 + 1;
`linksModuleData` "up to four" (brand guidelines); `messages` ≤ 10. Text guidance: title < 47, subtitle < 88,
label < 20, value < 15, two fields per row, up to three rows; notification title < 29, body < 80 `[doc]`.

**Images:** logo PNG ≥ 660×660, 1:1, **circle-masked, 15 % margin, don't pre-mask** · wide logo 1280×400 (16:5),
transparent · hero 1032×812 (≈ 5:4), no embedded text · image module ≥ 1860 px wide. Images must be public HTTPS
URLs (redirects can 404); content-hash the URL so a change is picked up `[inference]`. A personal photo is allowed
only as a **secure private image** (API upload → `privateImageId`, object-only, image modules only) `[doc]`.

**Colour:** `hexBackgroundColor` only — no text or label colour; unset, Google takes the dominant colour of the
hero, else the logo. Google publishes a recommended palette and says to avoid neon `[doc]`. How Wallet picks text
colour is `[unverified]`.

**Barcodes, cross-platform:** QR, PDF417, Aztec, Code 128 work everywhere. Code 39, Codabar and EAN-13 need iOS
27+ and a QR fallback for older iOS. Data Matrix, EAN-8 and UPC-A are Google-only. Apple `I2of5` and Google
`ITF_14` are not the same symbology name — verify with a scanner `[inference]`.

## 5. One neutral model for both platforms

| Concept | Apple | Google | Mapping |
|---|---|---|---|
| Template vs instance | none — each `.pkpass` is self-contained | class (shared, live) vs object | **lossy** — the builder owns the template layer for Apple |
| Points / balance | field + `currencyCode`/`numberStyle`; `semantics.balance` | `loyaltyPoints` (balance ≤ 7) | clean; Google is tighter |
| Tier | any field | class `rewardsTier`, class per tier, or object module | **lossy** — pick a strategy |
| Primary visual | strip, thumbnail or poster artwork | hero (≈ 5:4, below the data) | **lossy** — separate crops |
| Logo | rectangle ≤ 160×50 pt | 660 px circle + optional 16:5 wide | **lossy** — two assets |
| Text colours | foreground + label | none | Apple-only |
| Seat / row / section / gate | `semantics.seats[]` + fields | `seatInfo` | clean |
| Order grouping | `groupingIdentifier`; `.pkpasses` ≤ 10 | `eventId`, `groupingInfo`, confirmation code | clean semantics, different mechanics |
| Expiry | `expirationDate` | `validTimeInterval.end` + 48 h reminder | clean; reminder Google-only |
| Single-use redeem | `voided: true` | `state: COMPLETED` | clean |
| Rotating code | — | TOTP rotating barcode | Google-only |
| Issuer messages | only `changeMessage` on a changed field | `messages[]` + notify (3/24 h) | Google-only |
| Links | back fields, poster URLs, ≤ 2 featured actions | links module, one app button, value-added modules | **lossy** |

Proposed shape `[inference]`:

```ts
type PassKind = 'businessCard' | 'membership' | 'loyalty' | 'coupon' | 'eventTicket';

interface PassTemplate {                       // the builder's unit of design (≈ a Google class)
  id: string; tenantId: string; kind: PassKind;
  version: number; status: 'draft' | 'published' | 'retired';
  brand: { organizationName: string; programName?: string; logo: AssetRef; wideLogo?: AssetRef; icon: AssetRef;
           colors: { background: Rgb; foreground?: Rgb; label?: Rgb; autoFromArtwork?: boolean } };
  art: { hero?: AssetRef; posterArtwork?: AssetRef; thumbnail?: AssetRef; crops?: Record<SlotId, SlotCrop> };
  fields: FieldDef[];                          // roles, not positions
  barcode?: { formats: BarcodeFormat[]; valueFrom: Binding; rotating?: { periodMillis: number } };
  links: { kind: 'web' | 'tel' | 'mailto' | 'map' | 'app'; label: string; uri: string }[];
  featuredActions?: { type: AppleFeaturedActionType; url: string }[];   // ≤ 2
  relevance: { locations?: { lat: number; lng: number; text?: string }[]; dates?: { start: string; end?: string }[] };
  platforms: {
    apple?:  { passTypeId: string; layout: 'poster+legacy' | 'legacyOnly';
               legacyStyle: 'storeCard' | 'coupon' | 'generic' | 'eventTicket'; posterEventTicket?: boolean };
    google?: { vertical: 'loyalty' | 'offer' | 'eventTicket' | 'generic';
               classStrategy: 'perTemplateVersion' | 'perTier' | 'perEvent'; genericType?: string };
  };
}
interface FieldDef {
  key: string;                                  // Apple field key and Google text-module id ([A-Za-z0-9_-])
  role: 'balance' | 'secondaryBalance' | 'tier' | 'memberId' | 'memberName' | 'offerTitle' | 'expiry'
      | 'eventName' | 'venue' | 'startsAt' | 'seat' | 'row' | 'section' | 'gate' | 'holderName' | 'custom';
  label?: string; value: Binding | Literal; priority: number;   // priority decides what drops first
  scope: 'template' | 'instance';               // Google class vs object; Apple re-sign blast radius
  notify?: { onChange: boolean; message?: string };
  backOnly?: boolean;
}
interface PlacementPlan {                       // computed, never stored; drives the preview's "not shown" badges
  platform: 'ios27' | 'iosLegacy' | 'watch' | 'android' | 'googleWeb';
  slots: { slot: string; fieldKeys: string[]; overflow: string[]; warnings: string[] }[];
}
```

**Compiler examples** `[inference]`: loyalty → `storeCard` puts `balance` in the primary field and fills secondary +
auxiliary (≤ 4) by priority, the rest to the back; loyalty → `posterGeneric` puts `memberId` in the header and
`memberName` as the unlabelled title; loyalty → Google maps `balance` → `loyaltyPoints`, `memberId` →
`accountId`, `tier` → class `rewardsTier` under the per-tier strategy, other instance fields → object text
modules and ≤ 2 card rows. Event → one Google class per event, one object per ticket; Apple one pass per ticket
with `groupingIdentifier` = event id.

## 6. Policy and go-live gates

- **Apple:** the pass type ID must match the signing certificate — one certificate per pass type ID; Apple's
  examples use a separate pass type ID per kind of pass; creating them needs the Account Holder or Admin role;
  an expired certificate stops new signing and updates, a revoked one breaks installed passes `[doc]`. Validity
  is reportedly one year `[3p, unverified]`. Guideline 3.2.1(iv) limits passes to payments, offers and
  identification; 1.5 asks for a dedicated certificate per brand owner (see §0 rule 8). On the back, include
  contact details for the signing organisation and, if different, the redeeming one `[doc]`.
- **Google:** new issuers start in **Demo Mode** ("[TEST ONLY]", test accounts only); publishing access is
  reviewed and needs a business profile and at least one class; "only trusted aggregators can create issuer
  accounts programmatically"; a `draft` class cannot create objects and you cannot return to draft; classes and
  objects cannot be deleted; 20 requests/second; callbacks arrive from `Googlebot` / `Google-Valuables` user
  agents, so allowlist them at the CDN `[doc]`. Whether a new vertical re-triggers review is `[unverified]`.

## 7. Could not verify

Google publishing access per vertical · Apple certificate validity and pass-type-id limits · whether one Apple
pass type id may carry several styles, and whether a style may change on update of the same serial · enforcement
of guideline 1.5 for multi-tenant signers · iOS 27 coupon and store-card changes · `posterGeneric` header/footer
counts · the poster event ticket's iOS version and required tags · Apple image-size conflicts (background,
footer) · Google text-colour logic, image re-fetch caching, "Expressive Passes" (2026-09-15) API changes, module
and message display limits · removal of Google's 10-location cap at I/O 2026 `[3p]` · Apple push rate limits ·
Apple ITF vs Google ITF-14 equivalence · issuer control of featured-action icons.
