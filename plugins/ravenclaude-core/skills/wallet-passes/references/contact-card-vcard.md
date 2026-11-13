# Contact cards: vCard fidelity, QR, NFC and the card builder

> **Retrieved 2026-10-26.** Standards: RFC 2426 (vCard 3.0), RFC 6350 (vCard 4.0), RFC 9554 (2024 extensions).
> Platform pages: Apple Core NFC background tag reading, NameDrop (Personal Safety guide), Contacts on Mac;
> Microsoft "Import vCards to Outlook contacts"; Google Contacts help; Open Graph; Facebook and LinkedIn image
> requirements; Denso Wave QR pages. Vendor help centres (Popl, Blinq, HiHello, Linq, Wave) are `[V]`;
> measurements made this session are `[M]`. **Biggest caveat:** Apple, Google and Microsoft do not publish how
> their contact apps import each vCard property; per-platform behaviour below is mostly `[unverified]` until a
> device test confirms it. Tap-to-share mechanics are in [`tap-to-share.md`](tap-to-share.md).

## 1. vCard: what to emit

- **Version: emit 3.0.** Apple's own exports carry `VERSION:3.0` `[3p sample]`; Android's open-source vCard library
  defaults to 2.1 and marks 4.0 "not published yet" `[AOSP code comment, age unknown]`; several importers reject
  4.0. Do not send two versions.
- **Required:** `FN` and `N` (3.0). For a business-only card, `N:;;;;` plus `X-ABShowAs:COMPANY` `[3p]`.
- **Lines:** CRLF; fold at **75 octets** (not characters — folding CJK by character produced a 215-octet line
  `[M]`); continuation lines hold 74 because the leading space counts; never split a UTF-8 sequence.
- **Escaping:** backslash-escape `\`, `,`, `;` and newlines (`\n`) in text values, **per component** of structured
  values (`N`, `ORG`, `ADR`) — escaping the joined string shifts every later component.
- **URLs:** percent-encode `,` and `;` (`%2C`, `%3B`) rather than backslash-escaping. One parser truncated an
  unescaped map URL at its first comma `[M: vobject 0.9.9]`; RFC 2426 types `URL` as a URI but says commas "in a
  value" must be escaped, and does not reconcile the two. Percent-encoding is safe under both readings.
- **Several phones and emails:** `TEL;TYPE=CELL,VOICE`, `TEL;TYPE=WORK,VOICE`, `EMAIL;TYPE=INTERNET,WORK` (RFC 2426
  §3.3). One of each is the common gap.
- **Structured address:** `ADR;TYPE=WORK:;;street;city;region;postcode;country` (seven components, empty ones keep
  their `;`), not the whole line in the street slot.
- **Labelled links for every social:** `itemN.URL` + `itemN.X-ABLabel`. Do not rely on `X-SOCIALPROFILE` alone —
  one unanswered Apple forum report (April 2026) says iOS did not restore it on re-import `[3p]`.
- **Add `UID`, `REV`, `PRODID`.** Whether iOS or Google use them to merge an existing contact is `[unverified]`;
  assume a re-saved card may create a duplicate and say so.
- **Photo:** inline `PHOTO;ENCODING=b;TYPE=JPEG:` (folded), square JPEG, EXIF stripped, a few hundred pixels.
  Never rely on `PHOTO;VALUE=uri` (reported ignored by several importers `[3p]`). Size claims in the wild (256 px,
  224 KB, 50 KB, 600 px) conflict and none is primary.
- **`NOTE`:** off by default; no RFC limit, keep it short.
- **Serve** as `text/vcard; charset=utf-8` with `Content-Disposition: attachment; filename="…"` (RFC 6350 §10.1;
  `text/x-vcard` is legacy).
- **Newer properties:** RFC 9554 adds `PRONOUNS` and `SOCIALPROFILE` to 4.0 only. On a 3.0 card, pronouns go in the
  display name or title and a social profile is a labelled URL.

**Prove it with a harness** `[recommendation]`: a golden fixture exercising commas, semicolons, backslashes and
newlines in name, org and note; CJK and emoji; three phones; two emails; a structured address; seven labelled
URLs; a photo; a long note — parsed in CI by two independent parsers, asserting ≤ 75-octet lines and CRLF only.
Then a manual matrix once per release: iPhone (Safari link, Mail attachment, Files, camera QR), Pixel and Samsung
(Chrome, then Google Contacts), Google Contacts web import, Outlook classic, new and web, macOS Contacts.

## 2. QR codes

- **Encode the short card URL, never the vCard.** A URL needed a 29-module symbol (version 3, ECC M); a minimal
  201-byte vCard needed 57 modules; one with a small photo did not fit in any version `[M]`.
- **Centre logo:** switch to ECC **H** and keep the logo ≤ 20 % of the symbol width, never over finder patterns.
  In one decoder under synthetic degradation, H survived 25 % width, Q 20 %, M about 15 %, and L failed from 15 %
  `[M, one desktop decoder — not a phone]`.
- **Dark on light only** — every inverted code failed to decode `[M]`; most reader SDKs don't decode inverted
  codes by default `[3p]`.
- **Quiet zone:** keep four modules (secondary sources; ISO/IEC 18004 is paywalled); zero failed over a busy
  background `[M]`.
- **Add a scan check in the builder:** decode the styled QR in the browser before allowing a download.

## 3. NFC and NameDrop

- **NFC tags:** write one short `https` URI record. iOS background tag reading takes the **first** URI record,
  accepts `http(s)`, `mailto:`, `tel:`, `sms:` and others but **not custom schemes**, works on iPhone XS and later
  only while the phone is in use, shows a notification the user must tap, and is unavailable during camera, Wallet
  payment or Core NFC sessions and in airplane mode `[Apple]`. Use a stable URL and change what it serves, never
  the tag. Don't write a vCard to a tag.
- **NameDrop cannot be driven from a web card.** It exchanges the user's own Contacts card (name, a chosen phone
  or email, Contact Poster), needs iOS 17.1 on both phones, and either side can choose receive-only `[Apple]`.

## 4. The card builder

**Content blocks the leading products offer** `[V]`: profile photo, logo, cover; name (Blinq adds prefix, suffix,
preferred name, pronouns); headline/bio; contact rows; social links (incl. payment handles); custom links and
buttons; booking; video; files (Wave); gallery and team directory (Wave); a lead-capture "exchange" form; vCard
download; QR; NFC.

**Default order** `[inference]`: identity header → a row of primary actions (Save contact or Exchange, Call, Text,
Email, Directions or Book) → featured links → social row → rich blocks → exchange form → QR and share footer.

**Editor patterns to copy** `[V]`: Blinq's onboarding order (name → work email and phone → company, title,
website → logo auto-detected from the company name → photo → colour and layout); a live phone preview with
"preview as a visitor" (Popl, HiHello); a six-dot drag handle on desktop and press-and-hold on mobile (Popl,
Blinq); a searchable field picker with popular fields pinned (HiHello); tile-level Save/Discard (Linq).
**Avoid:** paywalling basics; a double save (Blinq's app saves per field, then again); copies that drift from the
card (Blinq's signature card); gating the exchange form first by default; a recipient account upsell.

**Colour from the logo:** none of the products researched documents suggesting a brand colour from the uploaded
logo `[absence not proven]` — with a contrast-guarded palette behind it, it is a cheap differentiator.

**Team templates — four field states, not one** `[V: HiHello, Wave, Blinq]`: *locked* (admin value), *required*
(member must fill), *optional*, *hidden*. Add a lock on shared company socials, a per-template invite link, bulk
creation, and an **impact preview** ("this change updates 42 cards") because HiHello and Wave propagate template
edits to every card.

**Exchange (lead capture)** `[V]`: make the order a per-card setting — Linq's "Contact Exchange Preference", Popl's
"Lead Capture Mode", HiHello's saved-first vs collect-first — and default to **save first, exchange second**. Copy
Popl's hidden fields as a **source tag** (`?src=…` stored on the lead). If a follow-up goes by SMS, collect SMS
consent as its own checkbox (US rules were in flux after a 2025 appeals ruling `[3p, ask counsel]`). Under GDPR,
consent is provable, unbundled, never pre-ticked, and withdrawable as easily as given (Art. 7, Recital 32), with
the controller, purpose, retention and rights stated at collection (Art. 13).

**Analytics:** per-link click counts and a view-source split (QR / NFC / link — append a short `?s=` marker to each
entry point). Popl documents only aggregate link taps; HiHello points to UTM + GA4 `[V]`. Counts only — no
per-viewer identity.

**Sharing extras:** an OG image ≥ 1200×630 (Facebook; LinkedIn ≥ 1200×627) with width, height and alt tags and a
content-addressed URL so a change gets a new preview; keep it ≤ 300 KB (the stricter of two conflicting WhatsApp
claims `[3p]`). Offer a plain-text email signature too, because the Gmail and Outlook mobile apps support only
plain-text signatures (Blinq's docs) `[V]`.
