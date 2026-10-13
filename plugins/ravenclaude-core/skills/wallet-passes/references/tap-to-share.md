# Tap-to-share & tap-to-lead-form — what is possible, gated, or impossible

For the two product goals behind a RavenPass-style card: **(1) tap a phone to
share/receive a card or pass**, and **(2) a tap opens a lead/contact form in minimal
steps**. Sourced from the 2026-10-12 Wallet capability KB (primary Apple/Google/Android
docs). Use with [`apple.md`](apple.md), [`google.md`](google.md), and the
[`verify.md`](verify.md) ledger — several load-bearing claims here are `Unverified` and
flagged inline.

## The two-sentence answer

- **Goal 1 is partially achievable with zero approvals, but not the way it is usually
  imagined.** Phone-to-phone NFC "beaming" of a card is **not** available to third
  parties on either platform. What *is* available: Apple's native **proximity pass
  share** (iPhone→iPhone, Wallet→Wallet, controlled only by *not* setting
  `sharingProhibited`), **NameDrop** (system-owned, no API), and an **NFC tag/sticker/card
  + QR** that any phone reads.
- **Goal 2 is fully achievable today with zero approvals** via one stable HTTPS URL
  carried by an NFC tag + a printed QR + the QR inside a Wallet pass — at a cost of
  exactly one extra tap (the system "open link" step) on both platforms.

## The architecture that satisfies both — "one URL, three carriers"

One stable, short, **universal-link / App-Link-ready** HTTPS URL per card, carried by:

1. **NFC tag** in the physical card/sticker/keyfob — a single NDEF well-known URI (`type "U"`) record, HTTP**S**.
2. **Printed QR** on the same card — the fallback for pre-iPhone-XS, Android with NFC off, iPads.
3. **QR inside the Wallet pass** — Apple `barcodes[0]` (`PKBarcodeFormatQR`), Google `barcode` — pointing at the *same* URL.

The URL lands on a page that (a) shows the card, (b) offers the lead form (**Goal 2**,
2 taps), (c) offers "Save my contact" (vCard) + Add-to-Apple-Wallet / Add-to-Google-Wallet
buttons. Make it universal-link/App-Link-ready from day one so a future native app is a
config change (`apple-app-site-association` + `assetlinks.json`), **not a reprint of a
single card**. This is the single most important decision: one stable URL, everywhere.

## Apple / iOS — possible / gated / impossible

### Possible today (Apple Developer membership + Pass Type ID cert only)

- Signed `.pkpass` `generic` business card; iOS 27 `posterGeneric` variant (⚠️ P1 unverified (#3) — see [`apple.md`](apple.md) §3.2); QR via `barcodes[]`.
- Full contact block on `backFields` (unlimited count/length; Apple *requires* issuer contact on the back).
- Lock-screen surfacing via `locations[]` (≤10) + `relevantDates[]` (iOS 18+).
- Live updates after handout via `webServiceURL` + `authenticationToken` + APNs (production only).
- **Native phone-to-phone pass share** (Wallet→Wallet proximity): "hold your iPhone a few centimetres from the top of the other person's iPhone… then tap Share." Gated only by the issuer — leave `sharingProhibited` false/omitted. ⚠️ P1 unverified (#10 in [`verify.md`](verify.md)) which exact Share-sheet channels (AirDrop/Messages/Mail) are offered.
- **NFC tag → HTTPS URL → web form** — iPhone XS+, no app, no entitlement. Tag carries a well-known URI record; HTTP/HTTPS, `mailto:`, `sms:`, `tel:`, Maps schemes supported; **custom URL schemes are not** — use universal links.
- Web distribution via the "Add to Apple Wallet" badge (Apple SVG/EPS, 45 locales, 0.1X clear space, Wallet Marketing Agreement). ⚠️ P1 unverified (#2) — whether a `.pkpass` download works in **non-Safari iOS browsers and Android browsers** is undocumented; expect a plain file download with no handler there.

### Needs an Apple entitlement / approval

| Capability | Who grants | Timeline |
|---|---|---|
| `nfc` key on a pass (VAS) — tap pass to a **terminal** | Apple, via `developer.apple.com/contact/passkit/` (sign-in gated). Also requires a VAS-certified Apple-Pay terminal + POS "VAS Only"/"Payment and VAS" modes | ⚠️ P1 unverified (#7) — no published SLA |
| `NFCVASReaderSession` — iPhone **reads** another device's pass | Apple. Doc: "requires an entitlement… Updates will include… a link to the entitlement request form" — i.e. the form is not public as of 2026-10-12 | Unknown / effectively blocked |
| App Clip (NFC-integrated App Clip Code, no-install) | App Store Review; requires a **published full App Store app** carrying the App Clip in every version | App Review |
| NFC & SE Platform / HCE (EEA) | Apple; agreements, lab review, EEA establishment, fees (#27) | Unknown |

### Not possible on iOS

- **Phone-to-phone NFC sharing of a pass by a third-party app.** Wallet pass NFC is the VAS pass→terminal protocol only; `nfc.message` is capped at **64 bytes** and goes to an Apple Pay terminal. ⚠️ P1 unverified (#6) — that a Wallet pass is therefore invisible to ordinary NDEF readers is inferred, not stated.
- **Hooking NameDrop.** ⚠️ P1 unverified (#5) — no public NameDrop API. NameDrop shares only "your name, the phone number or email address you choose, and Contact Poster information" — nothing else from the card — and it **cannot update an existing contact** (needs iOS 17.1 on both devices). RavenPass's only lever is coaching users' Contacts *My Card*; the proximity handshake is system-owned.
- **Tapping the front of a pass to open an arbitrary web URL** (pre-iOS 27). `appLaunchURL` only works with `associatedStoreIdentifiers` and launches **your own** App Store app. The poster-event-ticket URL keys (`contactVenueWebsite`, …) are "(Poster event tickets only)." iOS 27 **Featured Actions** (`call`, `place`, `shop`, `bookAppointment`, `viewOffersRewards`) are the first general answer — but ⚠️ P2 unverified (#11): Apple documents the action *identifiers* without a documented JSON schema. See [`apple.md`](apple.md) § Featured Actions.
- **A poster event ticket with a QR** — "poster event tickets aren't compatible with tickets that require a QR code or barcode for entry." Another reason a card uses `posterGeneric`/`generic`, not the poster event ticket.
- **NFC background tag reading while Wallet is open** — documented exclusion (also camera-in-use, airplane mode, never-unlocked, active Core NFC session). You cannot have the user open the pass *and* tap a tag at once.
- **An App Clip that is just a web form** — HIG: "Don't use App Clips solely for marketing… Avoid using web views… offer a quick link to your website instead."

## Google / Android — possible / gated / impossible

### Possible today (self-serve, once out of Demo Mode)

- Generic pass business card (`GenericObject` + `cardTitle`/`header`/`subheader`/`logo`/`heroImage`/`hexBackgroundColor`). Class review is automatic (`reviewStatus: underReview` → platform sets `approved`).
- QR via `barcode` / `rotatingBarcode`; rich `textModulesData[]` + `linksModuleData[]`.
- Save links anywhere a hyperlink works (`https://pay.google.com/gp/v/save/<jwt>`); works in web, email, SMS, chat. ⚠️ mind the **~1800-char JWT ceiling** — pre-create the object server-side and ship a skinny JWT (see [`google.md`](google.md)).
- Geo notifications via `merchantLocations[]` (≤10); updates via `patch`/`addmessage`.
- NFC tag → HTTPS URL → web form (Android tag dispatch).

### Needs Google approval

- **Leaving Demo Mode** (issue to non-test users; drop the `[TEST ONLY]` title prefix): Business Profile + payments profile + ≥1 class → "Request publishing access." (#25 — unknown turnaround.)
- **`appLinkData`** — the front-of-pass button opening a website (`webAppLinkInfo`, `displayText` ≤30 chars). ⚠️ P1 unverified (#8) — the FAQ says "Applinking requires allowlisting"; **no criteria/timeline published.** This is the single highest-value unknown for an Android pass CTA. See [`google.md`](google.md) §7.1.
- **Smart Tap** (phone→terminal NFC redemption): certified terminal provider + Collector ID + `enableSmartTap`/`redemptionIssuers` on the class + ASCII `smartTapRedemptionValue` on the object (#26 — unknown turnaround).
- **Generic Private Pass** (whole pass in a JWT): scoped to sensitive data (health/government ID) — **wrong vertical for a business card**.

### Not possible on Android / Google Wallet

- **A personal photo (headshot) on the pass** — "Google Wallet does not support personal images on passes." Direct collision with a business-card design: use brand art for `logo`/`heroImage`, keep the headshot behind the URL. (Apple publishes no equivalent ban — #29.)
- **Developer-authored push notifications** — only the fixed system reminders (Generic: upcoming 24 h before `validTimeInterval` start, expiry 48 h before end).
- **Deleting a class or object** — users can only de-link.
- **Save URLs beyond ~1800 chars** — browser truncation; use the skinny JWT.
- **Opening an iOS app from a Google pass** — `iosAppLinkInfo` is deprecated.
- **Google Play Instant / Instant Apps** — removed December 2025. There is no Android equivalent of App Clips; Google's advice is to deep-link to a regular app.
- **Phone-to-phone pass sharing** — not documented on Android. ⚠️ P2 unverified (#16) — Android Beam's removal is inferred from its absence in the current NFC guide.
- Whether a Google Wallet pass even works **on iOS** is ⚠️ P1 unverified (#4) — plan Android-only and ship `.pkpass` for iOS.

### Android NFC behavior change to design against

- **Android 16**: scanning a `http(s)` NFC tag triggers `ACTION_VIEW` (not `ACTION_NDEF_DISCOVERED`).
- **Android 17**: surfaces an **"open link" notification requiring explicit user interaction** — so the URL-tag flow is now the **same 2 taps as iOS** (tap tag → tap notification), not 1. Budget for it in copy.
- API limits to design against: Google Wallet API is **20 req/s**, no official SLA, recommended **10 s timeout** (p99 ~5 s); callbacks arrive with `Googlebot` / `Google-Valuables` user agents — allowlist them.

## Friction ranking — "a tap opens a lead/contact form"

| Route | iOS taps | Android taps | Install? | Approval? |
|---|---|---|---|---|
| **NFC tag → HTTPS URL** | tag → notification → form | ≤15: tag → form; **16: `ACTION_VIEW`; 17+: tag → "open link" → form** | none | none |
| **QR → HTTPS URL** | Camera → banner → form | Camera/Lens → tap → form | none | none |
| Wallet pass QR (screen → camera) | owner 2–3 taps to surface pass; scanner points + taps | — | pass saved | pass cert only |
| Proximity Wallet pass share | open pass → hold phones → Share | n/a (iOS↔iOS) | pass saved | pass cert only |
| vCard download | download → open → Add | Contacts → Organize → Import from file | none | none |
| App Clip Code (NFC/scan) | tap/scan → App Clip card → Open | n/a | needs a published app | App Store review |
| Wallet pass NFC (VAS / Smart Tap) | terminal only | terminal only | — | Apple/Google cert + certified terminal |

## Lowest-friction workaround (both platforms)

**NFC tag or printed QR → one stable HTTPS universal-link/App-Link-ready URL → web lead
form (+ "save my contact" vCard).** Recipient cost: 2 taps on both platforms. No app, no
entitlement, no review. It degrades perfectly and upgrades to a native app later without
reprinting a card. Add a skinny-JWT "Add to Google Wallet" + "Add to Apple Wallet" button
on that same page.

### vCard notes

- vCard is good for *giving* your details, mediocre as a *one-tap* experience, and
  one-directional. iOS documents only the email/message-**attachment** import path;
  ⚠️ P2 unverified (#15) what a Safari `.vcf` **download** does. Android import is a manual
  Contacts → Organize → Import-from-file flow — **not** one tap.
- Prefer a web **form** (captures *their* details — the clean 2-tap lead flow) as the
  primary CTA, with a vCard download as the secondary "here are mine."

## App Clip constraints (if a native iOS app is ever on the roadmap)

- Invocable by NFC tag, QR, App Clip Code, Safari, Messages, Maps, Siri Suggestions.
- Size tiers **10 MB (pre-iOS 16) / 15 MB (iOS 16+) / 100 MB (iOS 17+)** — the 100 MB tier
  is **digital-invocation-only** (no App Clip Codes / QR / NFC). (The old "10/15/50 MB"
  progression is wrong; there is no 50 MB tier.)
- Requires a **published full App Store app** carrying the App Clip in every version.
- HIG prohibits marketing-only App Clips and discourages web-view wrappers — a thin web-form
  App Clip is review risk. NFC-integrated App Clip Codes use **Type 5** tags ≥35 mm.
- Ephemeral: the system removes an App Clip after inactivity (#21 — period unknown).
