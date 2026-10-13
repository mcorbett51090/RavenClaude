# VERIFY ledger — claims with weak, indirect, or absent primary evidence

Compiled from the 2026-10-12 Wallet capability KB. Every line below is either (a)
unverified from a primary source, (b) an argument from absence of documentation, or
(c) a documented value whose underlying number Apple/Google do not publish.
**Treat each as a hypothesis, not a fact.** Re-check before any of these drives a
build decision or a customer promise.

Severity: **P1** = would change a RavenPass architecture or a customer promise · **P2**
= would change an implementation detail · **P3** = an undocumented number recorded as
"unknown". The **8 P1 items (#1–#8)** also carry an inline `⚠️ P1 unverified (#n)` note
at their claim site in the relevant reference — do not treat the claim as settled there.

> **How to read a claim that cites one of these.** Anywhere a reference says a thing
> "see verify.md #N" or carries a `P1 unverified (#N)` note, the surrounding text is the
> **working belief**, not a contract. If you are about to promise it to a customer or
> wire an irreversible build decision to it, run the "How to verify" step first.

## P1 — architecture / promise level

- Unverified: **#1 (P1)** — the single-pass MIME type is `application/vnd.apple.pkpass` and serving it over HTTPS triggers Safari's inline Add-to-Wallet sheet. The current Wallet Passes pages only document the **bundle** type `application/vnd.apple.pkpasses`; the single-pass type was on no page fetched. Long-standing in practice. How to verify: serve a real `.pkpass` with that `Content-Type` from a test HTTPS endpoint and open in Safari on a current iPhone; cross-check the archived PassKit Package Format Reference.
- Unverified: **#2 (P1)** — a `.pkpass` download works in non-Safari iOS browsers and in Android browsers. Not documented; Apple only says "provide a download on a web page." How to verify: test Chrome/Firefox/Edge on current iOS and Chrome on Android (expect a plain file download with no Wallet handler).
- Unverified: **#3 (P1)** — `posterGeneric` is a real, supported top-level `pass.json` key. Documented in the **guide** ("Creating a Poster Generic Pass") with a full code sample, but **absent from the `Pass` reference property table** as of 2026-10-12 (zero occurrences of "posterGeneric" in the Pass DocC JSON). Could be doc-sync lag, a beta-gated key, or a rename. How to verify: build a pass with `posterGeneric` + a `generic` fallback and install on an iOS 27 device; re-check the `Pass` reference in ~30 days.
- Unverified: **#4 (P1)** — Google Wallet passes are usable on iOS. Not stated on any page fetched. `AppLinkData.iosAppLinkInfo` is deprecated ("Links to open iOS apps are not supported"), which hints Android-first but is not a statement about pass availability on iOS. How to verify: open a `https://pay.google.com/gp/v/save/<jwt>` link on an iPhone and record the result; find the primary supported-platforms page.
- Unverified: **#5 (P1)** — no public NameDrop API exists for third-party apps (so RavenPass cannot originate, intercept, populate, or receive a NameDrop exchange). Argument from absence: a developer.apple.com search surfaced only forum threads. How to verify: grep the PassKit / Contacts / `UIActivityItemsConfiguration` references for any NameDrop surface; check WWDC 2023–2026 session indexes for "NameDrop."
- Unverified: **#6 (P1)** — Apple Wallet NFC passes are invisible to ordinary NDEF readers (iPhone background tag reading, Android `ACTION_NDEF_DISCOVERED`). Inferred from two facts (pass `nfc` = VAS protocol; reading VAS needs `NFCVASReaderSession` + a `GET VAS DATA` command). Apple never says "a pass does not emit NDEF." How to verify: hold an iPhone with an NFC-enabled pass against an Android NDEF-reader app and against an iPhone doing background tag reading; record that nothing is detected.
- Unverified: **#7 (P1)** — Apple's NFC pass (VAS) certificate request has no published SLA. Verified only that `/contact/passkit/` is sign-in gated (302 → idmsa.apple.com), so the form wording and any SLA are not publicly inspectable. The cited "1–2 weeks" is forum anecdote only. How to verify: sign in with the RavenPass Apple Developer account, read the form, record what it asks and any stated timeline.
- Unverified: **#8 (P1)** — Google `appLinkData` (the front-of-pass button) requires allowlisting. Stated once, in the FAQ ("Applinking requires allowlisting which can be requested here"), with no criteria, eligibility, form content, or timeline; the linked form was not fetched. **This gates whether RavenPass can put a tappable "Share your details" button on the front of a Google pass.** How to verify: open the FAQ's "requested here" link while signed into the Google Pay & Wallet Console; capture the form fields and any stated review time.

## P2 — implementation detail

- Unverified: **#9 (P2)** — `backFields` values containing a URL, phone number, or email are auto-linked (data detectors) by Wallet. Universally observed in practice; **not stated** on any page fetched. How to verify: build a test pass with a bare `https://`, `tel:`, and `mailto:` in `backFields` and inspect on current iOS.
- Unverified: **#10 (P2)** — Wallet's Share sheet offers AirDrop, Messages, Mail, and third-party apps. `support.apple.com/en-us/111112` only says "Tap the Share button"; the channel list came from a search snippet of the iPhone User Guide, not fetched page text. How to verify: fetch the full iPhone User Guide page body, or test on device.
- Unverified: **#11 (P2)** — the exact `pass.json` schema for declaring iOS 27 Featured Actions. Apple documents the action **identifiers** (`call`, `place`, `shop`, `bookAppointment`, `viewOffersRewards`, …) and says each has "an icon, string, and action," but no JSON key, nesting, or URL field is documented. How to verify: look for a `featuredActions`/`passActions` key in the DocC JSON for `Pass`/`SemanticTags`/Pass Designer; else inspect a shipped iOS 27 poster pass or file a DTS question.
- Unverified: **#12 (P2)** — `com.apple.developer.nfc.readersession.formats` still accepts the value `NDEF`. The current reference lists only `TAG`. Historically both `NDEF` and `TAG` were valid. How to verify: check the Xcode capability UI and a current entitlements file; cross-check `NFCNDEFReaderSession`'s own entitlement requirement.
- Unverified: **#13 (P2)** — the required/recommended NFC tag type for a plain URL business-card tag. Apple documents Type 5 only for NFC-integrated App Clip Codes; Core NFC reads types 1–5. Nothing says which type to buy for a plain URL tag. How to verify: test NTAG213/215/216 (Type 2) tags against current iPhones and Android 17 devices; confirm capacity for the chosen URL.
- Unverified: **#14 (P2)** — Android QR scanning via Camera / Google Lens works as assumed. No Google primary-source page was retrieved for this. How to verify: find the support.google.com page for "Scan a QR code with your Android phone" and quote it.
- Unverified: **#15 (P2)** — iOS behavior when Safari *downloads* a `.vcf` from a web page. Apple documents only "tap a `.vcf` attachment in an email or message"; the browser-download path is undocumented and has changed across iOS versions. How to verify: test `Content-Type: text/vcard` download, `Content-Disposition: inline` vs `attachment`, and a `data:`/blob URL on current iOS.
- Unverified: **#16 (P2)** — Android Beam / phone-to-phone NDEF push is gone. Argument from absence: the current Android NFC guide never mentions Beam. How to verify: find an Android release-notes/behavior-changes page that names Beam's removal and the API level.

## P3 — undocumented numbers (recorded as "unknown")

- Unverified: **#17 (P3)** — the maximum size of a single `.pkpass`. Apple documents only the bundle limit (10 passes / 150 MB). Single-pass limit unknown.
- Unverified: **#18 (P3)** — the maximum number of passes a user may store in Wallet. Not documented.
- Unverified: **#19 (P3)** — Apple's default lock-screen relevance distance (the default that `maxDistance` is compared against). Not documented.
- Unverified: **#20 (P3)** — rate limits on Apple pass-update APNs pushes / web-service calls. Not documented.
- Unverified: **#21 (P3)** — how long iOS keeps an App Clip before removing it ("a period of inactivity"). Not documented.
- Unverified: **#22 (P3)** — Google's geofence radius for `merchantLocations` ("a Google-set radius"). Not documented.
- Unverified: **#23 (P3)** — Google's limit on `linkedObjectIds` per object ("there is a limit… new linked objects are ignored silently"). Value not documented.
- Unverified: **#24 (P3)** — which fields are on Google's `notifyPreference` notification allowlist. Not documented.
- Unverified: **#25 (P3)** — Google Wallet publishing-access review turnaround. Not documented.
- Unverified: **#26 (P3)** — Smart Tap enablement / terminal-certification turnaround. Not documented.
- Unverified: **#27 (P3)** — Apple NFC & SE Platform fee schedule ("applicable fees"). Amounts not published.
- Unverified: **#28 (P3)** — Generic Private Pass approval turnaround. Not documented.
- Unverified: **#29 (P3)** — whether Apple publishes a policy on personal photos on passes (Google explicitly prohibits them). No Apple equivalent found. Worth checking App Review Guidelines / Wallet acceptable-use before putting a headshot on a `.pkpass`.

## Cross-platform asymmetries worth a second look

- **Headshots.** Google states flatly that "personal images" are **not supported** on passes (documented, not a VERIFY item). Apple has no equivalent statement in the docs reviewed (#29). If RavenPass wants a photo on the card, the design may differ per platform — or the photo lives only behind the URL.
- **Front-of-pass tappable link.** Google has `appLinkData` (allowlist-gated, #8). Apple has nothing equivalent before iOS 27 Featured Actions (#11), and `appLaunchURL` only launches an associated App Store app. #8 and #11 together decide whether "tap the pass → lead form" is achievable at all without a native app.
- **Doc freshness.** Google Wallet pages said "Last updated 2026-10-08"; Android pages "2026-10-01." Apple's Wallet guides describe iOS 27 features, but the `Pass` reference lags the guides (#3). Re-run this sweep after the next Apple release.
