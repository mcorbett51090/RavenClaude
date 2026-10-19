# Tap-to-share & tap-to-lead-form — what is possible, gated, or impossible

For the two product goals behind a RavenPass-style card: **(1) tap a phone to
share/receive a card or pass**, and **(2) a tap opens a lead/contact form in minimal
steps**. Sourced from the 2026-10-12 Wallet capability KB (primary Apple/Google/Android
docs), extended 2026-10-14 with **[Pushing a card to another person](#pushing-a-card-to-another-person--the-senders-playbook-2026-10-14)**
(every hand-off path ranked, and the receiving-page traps). Use with [`apple.md`](apple.md),
[`google.md`](google.md), and the [`verify.md`](verify.md) ledger — several load-bearing
claims here are `Unverified` and flagged inline.

## The two-sentence answer

- **Goal 1 is partially achievable with zero approvals, but not the way it is usually
  imagined.** Phone-to-phone NFC "beaming" of a card is **not** available to an ordinary
  third-party card issuer on either platform (the two exceptions — Apple's iOS 27 *Tap to
  Share* and EEA device-to-device HCE — are gated on entitlements a business-card app will
  not get; see the playbook below). What *is* available: Apple's native **proximity pass
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
- **Native phone-to-phone pass share** (Wallet→Wallet proximity): "hold your iPhone a few centimetres from the top of the other person's iPhone… then tap Share." Gated by the issuer — leave `sharingProhibited` false/omitted — and by Apple's undefined "eligible passes" (#30). The Share-sheet channels are now DOC (Wallet & Privacy: "AirDrop, iMessage, Mail, or with third-party mail, messaging, or other communication apps" — #10 resolved 2026-10-14).
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

- **Phone-to-phone NFC sharing of a pass by a third-party app** — for an ordinary issuer. (iOS 27 *Tap to Share* can add a pass to a customer's Wallet when two iPhones touch, but only inside an active **Tap to Pay on iPhone** session, entitlement-reviewed, not in the EEA — see the playbook § Out of reach.) Wallet pass NFC is the VAS pass→terminal protocol only; `nfc.message` is capped at **64 bytes** and goes to an Apple Pay terminal. ⚠️ P1 unverified (#6) — that a Wallet pass is therefore invisible to ordinary NDEF readers is inferred, not stated.
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
- **Phone-to-phone NFC beaming of a pass** — not documented on Android. ⚠️ P2 unverified (#16) — Android Beam's removal is inferred from its absence in the current NFC guide. Two things that **are** documented (2026-10-14): Google Wallet's holder-side **Share** "if it has Share above it" (some passes; Generic unverified — #33), and Android 17 **Tap to share** (NFC-started Quick Share, Pixel 6+) carrying links and contact cards — which forwards the card **URL**, not a pass.
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
| Proximity Wallet pass share | open pass → hold phones → Share ("eligible passes" undefined — #30) | n/a (iOS↔iOS) | pass saved | pass cert only |
| OS share sheet / prefilled text with the card URL | owner: 1 tap; recipient: link → Add | same | none | none |
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

## Pushing a card to another person — the sender's playbook (2026-10-14)

Research for "make handing a Wallet business card to someone as frictionless as possible."
Tags: **DOC** = a primary source says it (quoted) · **MEAS** = a credible hands-on report ·
**UNVER** = claimed or inferred, not proven. New ledger items are #30–#37 in [`verify.md`](verify.md)
(#38 added 2026-10-18 with § Straight to Wallet).

### The shape of the answer

There is no third-party "beam a pass to the phone next to you." Every frictionless hand-off is
**one stable https URL per card** carried by whatever is nearest — the pass's own QR, an NFC
sticker, the OS share sheet, a prefilled text — **plus one native exception**: Apple Wallet's
own *Share* of the pass file, iPhone → iPhone. So the work is (a) make the link one tap to send,
and (b) make the page it lands on impossible to get stuck on (§ Receiving-page traps). The
surveyed competitors (Blinq, Popl, HiHello, OVOU, Mobilo, Wave, V1CE, Haystack — help centres,
2026) all treat the pass as "a QR the owner shows"; none documents a share link on the pass
itself, and only one (QRPlanet) documents the recipient adding the **owner's** card to their own
wallet from the link — the gap a card product can own.

### Every path, ranked by total friction (sender + receiver)

| # | Path | Sender | Receiver | Reach | Evidence / gate |
|---|---|---|---|---|---|
| 1 | **Pass QR → camera** | double-click side button, show the pass (or the **Apple Watch** — "When you add a ticket or pass to the Wallet app on your iPhone, you automatically add it to the Wallet app on your paired Apple Watch", DOC [111112](https://support.apple.com/en-us/111112)) | point camera, tap banner, tap Add / Save | any phone | DOC: Camera — "Tap the link that appears at the bottom of the screen." Put the **card URL**, not a vCard, in the pass barcode. |
| 2 | **NFC sticker → https URL** | nothing (sticker on case) | tap, (A17: tap notification) | iPhone XS+, Android | DOC: "iPhone XS and later support background tag reading"; https/mailto/sms/tel only, no custom schemes. Owner writes it from **Chrome on Android with Web NFC** (no app; § Writing the sticker) or any NFC app; an iOS app can write with the standard *NFC Tag Reading* capability (DOC: `writeNDEF`, iOS 13+, "iPhone 7 and later"). |
| 3 | **Wallet → Share (the pass file)** | open pass, Share | tap, Add | iPhone ↔ iPhone / Watch | DOC 111112: "You can share some tickets and passes in the Wallet app with other iPhone or Apple Watch users"; iOS 17 guide: "The shared pass is added to the recipient's Wallet." Channels, DOC [Wallet & Privacy](https://www.apple.com/legal/privacy/data/en/wallet/): "Wallet allows you to share passes by AirDrop, iMessage, Mail, or with third-party mail, messaging, or other communication apps." Gate: `sharingProhibited` unset. |
| 4 | **OS share sheet with the card URL** (`navigator.share({url})` / native share) | one tap | tap link, tap Add | any | DOC MDN: needs "transient activation". Share the **URL alone** — Messages draws the rich preview only when the message is the link. Carries into AirDrop, Messages, WhatsApp, Android Quick Share / Tap to share. |
| 5 | **Prefilled text / email / WhatsApp** | one tap, pick the person in their own app | tap link, tap Add | any | `mailto:?subject=&body=` is valid (DOC RFC 6068). `sms:` body: **#31**. `https://wa.me/?text=` (MEAS). No recipient data ever reaches you. |
| 6 | **Hold two iPhones together** | open pass, hold phones | Accept the AirDrop offer | iPhone ↔ iPhone, "eligible passes", iOS 17.2+ | DOC 111112: "hold your iPhone a few centimeters from the top of the other person's iPhone. A glow will appear…". Apple never defines **eligible** (#30); proximity AirDrop is DOC'd for "someone **in your contacts**". Do **not** promise it — see § Hold-to-share, in detail. |
| 7 | **Android Tap to share** (NFC-started Quick Share) | overlap phone tops | accept | Android 17, Pixel 6+; Samsung Fold8/Flip8 "coming soon" | DOC [support.google.com/android/answer/17161144](https://support.google.com/android/answer/17161144): shares "contact information, photos, videos, links, location"; "Tap to share is available for Pixel 6 and newer phones running Android 17 and higher." Free if you offer #4. |
| 8 | **Quick Share → iPhone (AirDrop interop)** | share sheet | iPhone must set *Everyone for 10 Minutes* | Pixel 8a+ / Galaxy S24+ → iPhone | DOC (Pixel help): files; links **UNVER**. |
| 9 | **NameDrop** | hold iPhones | accept | iPhone ↔ iPhone | Swaps contact details, never the pass or the card link (no API — #5). DOC ([Apple Personal Safety guide](https://support.apple.com/guide/personal-safety/secure-namedrop-ips97e16d3b1/web)): "NameDrop shares only your name, the phone number or email address you choose, and Contact Poster information" — a URL in *My Card* does **not** travel, so coaching owners to add the card URL there does nothing (corrected 2026-10-18). |

### Hold-to-share, in detail (research 2026-10-14)

What is now known about Apple's "bring two iPhones together" pass share, and what is not:

- **It is an AirDrop transfer.** MEAS ([Tom's Guide, 2023-12](https://www.tomsguide.com/how-to/how-to-airdrop-share-tickets-on-iphone), screenshots): the sender sees "*Name* – Waiting to receive… 1 Pass", the receiver sees a "*Name* – Connected" banner, then "AirDrop – *Name* would like to share a Wallet pass – Decline / Accept". AirDrop itself is DOC'd as BLE + Apple peer-to-peer Wi-Fi over TLS (Platform Security Guide); NameDrop is "part of AirDrop".
- **Which radio detects the phones is not documented.** Consumer sites say NFC (others NFC + UWB, contradicting each other). Inference: not UWB — NameDrop is DOC'd on iPhone SE / Apple Watch SE models that list NFC but no UWB.
- **No issuer switch exists.** Apple's full `pass.json` key reference (~70 keys incl. 26.x) has exactly one sharing key, `sharingProhibited`; no `sharing` dictionary, entitlement or semantic tag gates proximity sharing (checked 2026-10-14). Pass vendors (PassKit, Passcreator, Airship, PassSource) document only the Share-button flag. `PKShareablePassMetadata` is Secure-Element credential provisioning, not `.pkpass`. The only "nearby" in the Wallet Passes docs is boarding-pass **flight status** sharing, not the pass.
- **Contacts appear to gate it.** DOC: proximity AirDrop is for "someone in your contacts" (iOS 17–27 guides). DOC (Apple Staff, [developer forum 738469](https://developer.apple.com/forums/thread/738469)): an app's `activityItemsConfiguration` proximity share "only works if both devices are 'known' contacts. If you see the NameDrop UI, it means they are not." MEAS (Tom's Guide): "You may end up using the NameDrop contact sharing feature if you're not already a contact… share your details and then bring the iPhones together again." So for strangers: **first touch swaps contacts (NameDrop), second touch can hand over the pass** — reported once, untested on a generic pass. Conflicting: MacRumors (2023) says proximity worked for non-contacts; that predates iOS 26.2 AirDrop codes (#36).
- **Same Apple Account (owner testing with their own two phones):** MEAS (Apple Community 255157985): the phones show only a "connected" banner, no NameDrop. Wallet passes sync across one account (DOC), so the receiving phone may already hold the pass — a likely reason nothing is offered (UNVER).
- **Reported working:** an expired UK rail ticket (boarding-pass style), person to person (MEAS). **Not found either way:** any generic, store-card, coupon or membership pass.
- **"Nothing at all" vs NameDrop:** with a pass open, the gesture still shows NameDrop or a Connected banner when the phones' proximity path works; **no glow at all points at the phones** (settings, lock state, iOS < 17.2), not the pass (inference).

**Test protocol** (record iOS versions; both phones: *Bringing Devices Together* on, Wi-Fi + Bluetooth on, Personal Hotspot off, unlocked):
1. Device control — share a **photo** by holding the phones together. Fails → the phones, not the pass.
2. Pass control — a boarding pass / rail / movie ticket with a Share button.
3. Two **different** Apple Accounts, people **in each other's Contacts**; run a same-account pair as a separate arm with the pass removed from the receiver (and iCloud Wallet sync off).
4. Strangers: let NameDrop complete, then bring the phones together again.
5. Decisive style control — sign the same payload as `eventTicket`, `generic` and `posterGeneric` with your own certificate (`sharingProhibited` unset) and repeat. Record per attempt: nothing / NameDrop / Connected only / pass offered.

**Android's equivalent is Android-only.** DOC (Help 17161144): Tap to share sends "contact information, photos, videos, links, location, and more with **nearby Android devices**" (Pixel 6+ on Android 17; Samsung Fold8/Flip8 "coming soon"); started from the share sheet, so a card **URL** rides it; no developer API documented. No tap gesture crosses iPhone ↔ Android; Quick Share ↔ AirDrop is a device list, with the iPhone on "Everyone for 10 Minutes".

**iOS 26.2 changed AirDrop for strangers (DOC, iPhone User Guide):** "if someone tries to send you
an item with AirDrop and they're not in your contacts, they must use an AirDrop code." So for
someone just met, #1 (QR) or Messages beats AirDrop; say so in owner copy. Whether the
hold-together gesture is exempt from the code: **not found** (#36).

### What the recipient of a shared pass actually gets

- **The same pass.** DOC ([Poster Generic](https://developer.apple.com/documentation/walletpasses/creating-a-poster-generic-pass)): "Two passes of the same type with the same serial number represent the same pass." MEAS (PassKit, 2024): sharing "simply sends the exact same pass."
- **Your updates.** DOC (archived Updating guide): "a single pass can be registered by multiple devices." Each recipient's phone registers with your `webServiceURL`, so an edit reaches every copy and the registration count is a rough share counter (**UNVER** as analytics).
- **Consequence for design:** never put owner-only data in a shareable pass (the owner-edit link must be login-gated), and expect the barcode to be seen by everyone in a Messages thread (`apple.md` §11a).

### Receiving-page traps — where "frictionless" actually breaks

| Trap | Evidence | Fix |
|---|---|---|
| **`.pkpass` on Android** | DOC [Google Wallet help](https://support.google.com/wallet/answer/12060038): Google Wallet can import a downloaded pass ("Select Google Wallet", Continue) but "A downloaded pass that you convert may be limited in functionality and you may not get updates." | Android: show **Google** when you issue one and hide Apple; with no Google pass, keep the `.pkpass` as the fallback. |
| **Google save link on iPhone** | DOC: saving "can only be initiated in the context of a logged-in Google identity"; MEAS (2023): iOS gets a web UI. | iPhone: hide the Google button. |
| **In-app browsers** (Instagram, Facebook, Messenger, TikTok, Snapchat, LinkedIn…) | DOC ([archived Distributing Passes](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/DistributingPasses.html)): "Both the Safari app and the Safari view controller can import the pass files directly… If you want to load a file using a web view, you must detect the request, download the pass, and programmatically add the pass yourself." MEAS ([forum 844595](https://developer.apple.com/forums/thread/844595), 2026-09): valid passes "blocked inside Instagram and Messenger." MEAS (Krause 2022): Instagram/Facebook/Messenger/TikTok/Snapchat use their own WKWebView; X/Reddit use Safari View Controller; WhatsApp/Slack/Gmail open the default browser. | UA-detect on iOS and show "open in Safari" under Add to Apple Wallet, with a one-tap `x-safari-https://…` link (#32 — undocumented) **and** the by-hand route beside it. Do not flag Chrome iOS (below) or Safari View Controller apps. |
| **Chrome / Firefox on iOS** | DOC (Chromium source): `PassKitTabHelper` handles `application/vnd.apple.pkpass` and presents `PKAddPassesViewController`. Firefox iOS: bug 1250209 FIXED (v5.0). | No action; serve the pass over **GET** with the right MIME (a POST was a reported failure, MEAS). |
| **Hidden buttons that show anyway** | A component library's `.btn { display:inline-flex }` beats the UA `[hidden]` rule. Measured on a production card page (2026-10-14): `hidden` set, `display:flex`, 53 px tall — a dead Share button on every desktop. | `[hidden]{display:none!important}` wherever script un-hides controls. |
| **Strict CSP on the card host** | A `script-src` without `'self'`/inline blocks the page's own share script; `form-action 'none'` refuses a share-back form submit (CSP semantics). | Ship the card script as a **same-origin file**; allow exactly the form's target origin. |
| **Desktop visitor** | DOC ([Add to Apple Wallet guidelines](https://developer.apple.com/wallet/add-to-apple-wallet-guidelines/)): pages opened elsewhere should say "To add this [pass] to Wallet, open this [email, web page] on your iPhone". | Keep the QR on the page; a share button degrades to **Copy link**. |

### Straight to Wallet from the QR and the tag (built 2026-10-18)

Built in RavenPower (RavenPower-Website PR #685, ravenpower-app #18, RavenPower-website-factory
#102). It drops the receiver's steps from *camera → page → Add to Apple Wallet → Add* to
*camera → Add*.

**The pattern.**

- **Only the scan carriers are marked.** The Apple pass's QR and the NFC tag carry the card URL
  plus a marker **fragment**, `#add-to-wallet` (the Google pass's QR does not — Save-JWT row
  below). Shared links, printed links and the holder's own links to
  the card stay plain — otherwise opening your own card re-offers its pass.
- **When the card page's script sees exactly that fragment**, it (1) removes it with
  `history.replaceState`, then (2) about 150 ms after paint navigates to *this phone's* Wallet
  link: the `.pkpass` on iPhone/iPad; on Android the Google save link **only when a native Google
  pass exists** — never the `.pkpass` import on Android (it loses updates, § Receiving-page traps).
  The card page stays underneath, so **Cancel** lands on the card.
- **It does nothing** in an in-app browser, on a computer, or when the card has no Wallet button.
  After an auto-open the two-step "Save contact + Wallet" button is not set up.

**Why a fragment, not a query parameter.**

- The server never sees a fragment, so static hosts and edge caches serve the same object and no
  server change is needed.
- A page without the script ignores it.
- It survives a redirect: when a 3xx `Location` has no fragment, the user agent keeps the
  original one (RFC 9110 §10.2.2 — DOC, not re-read 2026-10-18).

**Fail closed** (from a security review). No auto-open unless `replaceState` succeeded — otherwise
Back returns to the marked URL and runs it again. Navigate only to a same-site path
(`/^\/(?!\/)/`) or an `https://` URL — never `javascript:`, `data:`, `http:` or protocol-relative
`//host` — because the same script ships to hand-built pages whose markup is authored elsewhere.

| Constraint | Evidence | Rule |
|---|---|---|
| **Google Save-JWT budget** | MEAS (2026-10-18): a rich card's compact-tier Save JWT measured 1,791 of Google's 1,800-character safe limit ([`google.md`](google.md), DOC). Adding the 14-character fragment to the Google object's barcode pushed it over, and the add-time pass shed to the bare tier (title and colour lost). | The **Google** pass's QR does **not** carry the marker. Anything added to a Google object costs about 4/3 of its length in the Save JWT. Revisit when the Save link carries only a REST-created object id. |
| **Apple: a barcode change is a Wallet push** | MEAS (2026-10-18): changing the barcode `message` changes `pass.json`, so the update-service version moves and every holder gets an update push on the pass's next build — silent, since there is no `changeMessage`. A key-by-key diff of 8 builds showed exactly one changed key (`barcodes[0].message`); images and `rev` unchanged. | Treat it as a Wallet push that needs the owner's GO before the production deploy. |
| **NFC tag capacity (NTAG213)** | 144 bytes of user memory − 3 (Type-2 TLV: type, length, terminator) − 4 (NDEF short-record header: flags, type length, payload length, type `U`) = a **137-byte URI payload** (the identifier code plus the URL after the abbreviated prefix). DOC (NXP datasheet; NFC Forum Type 2 / NDEF formats), not re-read 2026-10-18. Which tag type to buy is still #13. | Keep the marker only while the marked record still fits; otherwise write the plain URL. The marker must never be what makes a tag unwritable. |

**Measured (#38, partly resolved):** MEAS (owner device test on a real iPhone, 2026-10-18): a card
URL ending `#add-to-wallet`, opened directly in Safari on RavenPower's preview
(`preview.ravenpower-sites.pages.dev/connect`) and on production (`www.ravenpower.net/connect`),
showed Wallet's pass sheet (Add / review) with **no tap**. So iOS Safari does present the
Add-to-Wallet sheet for the script-initiated `location.assign()` to the `.pkpass`, about 150 ms
after page load, without user activation. **Not yet recorded:** the iOS version, the Camera QR
banner and NFC-tag notification entry points themselves (the test opened the URL directly in
Safari), and a non-Safari default browser. If it does not fire on one of those, the person simply
lands on the card.

### Google: the second person to save the card

- DOC ([MultipleDevicesAndHoldersAllowedStatus](https://developers.google.com/wallet/reference/rest/v1/MultipleDevicesAndHoldersAllowedStatus)): `MULTIPLE_HOLDERS` — "The Pass object is shareable by a user and can be saved by any number of different users, and on any number of devices." `ONE_USER_ALL_DEVICES` — "Once the first user saves the object, no other user will be allowed to view or save it."
- DOC: the field is on the **class** (GenericClass: "Identifies whether multiple users and devices will save the same object referencing this class"), not the object. The unset default is **not documented** (#34).
- **Rule for a business card issued as one object per card:** set `MULTIPLE_HOLDERS` on the class explicitly, or the owner (first saver) locks every recipient out. The alternative — one object per saver minted at save time — buys per-saver analytics and revocation at the cost of N patches per edit (put changing content on the class).
- DOC ([help](https://support.google.com/wallet/answer/12060038)): Google Wallet has a holder-side **Share** — "You can share a pass if it has Share above it… Some pass issuers don't allow sharing." Whether it appears on **Generic** passes: **#33**.

### Writing the sticker without an app — Web NFC

DOC ([Chrome](https://developer.chrome.com/docs/capabilities/nfc)): "Web NFC … launched in Chrome 89 for Android"; "only available to top-level frames and secure browsing contexts (HTTPS only)"; needs a user gesture; "Host-based Card Emulation are not supported." DOC (MDN): `write()` "triggers a permission prompt". DOC (caniuse): Chrome for Android only. DOC (WebKit): "We oppose this feature and will not implement it." So: feature-detect `'NDEFReader' in window`, write one `url` record, and hide the button everywhere else.

### Web Share with a file (not recommended for a card)

DOC (Chromium `ShareServiceImpl` / FILE_TYPES): Chrome's permitted share types are images, audio, video, pdf, txt, csv, html — **no `.pkpass`, no `.vcf`**. DOC (WebKit `Navigator.cpp`): Safari's `canShare` has no MIME allow-list; what the iOS sheet then does with a `.pkpass` File is **#37**. Share the URL instead.

### Quick-open for the owner (the "show my QR" moment)

- Double-click side button → Wallet (DOC, iOS 18 settings). Whether it works with no payment card in Wallet: **not found**.
- Lock-screen suggestion via `relevantDates` / `locations` (DOC, iOS 27 guide: "Suggest on Lock Screen").
- MEAS: iOS 18 Shortcuts **Open [Pass or Card]** action → bind to the **Action Button** or **Back Tap** (both DOC'd as able to run a shortcut). No documented URL scheme opens a specific pass (`shoebox://` opens Wallet only, MEAS 2016).

### Out of reach for a business-card issuer (and why)

| Mechanism | Why not |
|---|---|
| Apple **Tap to Share** (iOS 27, ProximityReader) | DOC: lets an app add a pass to a customer's Wallet when two iPhones touch, but "requires an active Tap to Pay on iPhone session", is "not currently available in the European Economic Area", and Tap to Pay is entitlement-reviewed ("Apple reviews each application using predefined criteria"). |
| iOS **NFC & SE Platform / HCE** | DOC: use cases are "in-store payments, car keys, closed loop transit, corporate badges, student ID, home keys, hotel keys, merchant loyalty and rewards, and event tickets" (+ government ID, iOS 26.4) — **no contact exchange**. EEA-only HCE has a "Device-to-Device" case needing "the legal right and the necessary regulatory permissions". |
| `PKShareablePassMetadata` / `PKAddShareablePassConfiguration` | DOC: Secure Element credential provisioning (keys, access), not barcode `.pkpass`. |
| Android app as an NFC tag (HCE) | Possible in an **Android app** (DOC HostApduService; ISO-DEP, not NDEF, is what the docs describe). MEAS (PocketTag, one developer): an iPhone 16 on iOS 26.6.1 read a URL from an Android HCE Type-4 tag; an iPhone 11 did not; a contact-card payload got "no response". Needs an Android app. |

### Ranked build list (what to ship, cheapest friction cut first)

1. **Card URL in the pass barcode** (not a vCard) — every camera becomes a receiver.
2. **`sharingProhibited` unset + a web service** — Wallet Share works and every copy updates.
3. **Platform-aware receiving page** — one Wallet button per phone, Save Contact, in-app-browser escape.
4. **Share button with the URL alone** on every card page (share sheet → else Copy link → else hidden).
5. **Owner "send" panel** — Share / Text / Email / WhatsApp / Copy, recipient chosen in the owner's own app.
6. **Web NFC sticker writer** (Android Chrome) and a native writer in the app.
7. **Google class `MULTIPLE_HOLDERS`** before Google goes live.
8. Later: an offline vCard/MeCard QR (DOC: iPhone Camera "supports the vCard format… options to save to your contacts"; MeCard too — Apple Tech Talk 2017), widgets / Live Activity / Controls in an app, an App Clip receive path.

## App Clip constraints (if a native iOS app is ever on the roadmap)

- Invocable by NFC tag, QR, App Clip Code, Safari, Messages, Maps, Siri Suggestions.
- Size tiers **10 MB (pre-iOS 16) / 15 MB (iOS 16+) / 100 MB (iOS 17+)** — the 100 MB tier
  is **digital-invocation-only** (no App Clip Codes / QR / NFC). (The old "10/15/50 MB"
  progression is wrong; there is no 50 MB tier.)
- Requires a **published full App Store app** carrying the App Clip in every version.
- HIG prohibits marketing-only App Clips and discourages web-view wrappers — a thin web-form
  App Clip is review risk. NFC-integrated App Clip Codes use **Type 5** tags ≥35 mm.
- Ephemeral: the system removes an App Clip after inactivity (#21 — period unknown).
