# Ideal business-card pass layout

A Wallet pass is a **live, field-driven card**, not a JPEG of a paper business card. Both platforms crop, mask, localize, and restyle artwork. Type that lives in pixels will clip, stay English, and vanish from VoiceOver / TalkBack.

Use this with [`apple.md`](apple.md) and [`google.md`](google.md). Official rules are cited; placement recommendations are the working default for a person-to-person card.

## 1. What a card is (and is not)

| Do | Don't |
|---|---|
| Apple style `generic` | `storeCard` / `coupon` / `eventTicket` (wrong chrome + relevance) |
| Google `genericType: GENERIC_OTHER` | Dedicated Loyalty / Event verticals unless it really is those |
| Name, role, company in **fields** | Name/role/URL painted onto `logo`, `strip`, `heroImage`, `background` |
| One QR (vCard URL or profile) | A second decorative barcode |
| Tappable `tel:` / `mailto:` / `https:` on the **back / details** | A URL on an Apple **front** field (not tappable) |
| Share on (Apple `sharingProhibited` omitted/false) | `sharingProhibited: true` on a card you want people to hand off |
| `icon.png` as a simple 29-pt mark | Using the strip art as the iMessage preview (Mail/Messages use **icon**) |

Apple generic is the documented home for "any pass that doesn't fit into one of the other more specific styles" ([Pass Design and Creation](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)). Google generic is the documented home for non-specialized cards ([GenericObject](https://developers.google.com/wallet/reference/rest/v1/genericobject)).

`posterGeneric` can look more poster-like on newest OS versions, but a card that must work on current **and** older phones should ship legacy `generic` as the fallback (or as the only style) ([Creating a Poster Generic Pass](https://developer.apple.com/documentation/walletpasses/creating-a-poster-generic-pass)).

## 2. Apple — what goes where

```text
┌─────────────────────────────────────────┐
│ [logo]  logoText (company)    header(s) │  ← stacked-pass strip: header only
│─────────────────────────────────────────│
│  PRIMARY          [thumbnail]           │  ← person name
│  (name)           90×90 pt photo/mark   │
│─────────────────────────────────────────│
│  SECONDARY          SECONDARY           │  ← role | company (if not in logoText)
│─────────────────────────────────────────│
│  AUX                AUX                 │  ← city | short phone  OR omit and
│                                         │     put contact on the back
│─────────────────────────────────────────│
│              [ QR  ]                    │  ← profile or vCard URL
│              altText                    │
└─────────────────────────────────────────┘
  BACK (scroll): email, phone, web, LinkedIn, address, vCard link, org contact
```

| Slot | Content | Why |
|---|---|---|
| `logo` | Mark only, no type | 160×50 pt slot, cropped; Watch drops `logoText` if both do not fit |
| `logoText` | Short company wordmark | System type, localizable |
| `headerFields` (0–1) | Tiny status ("CARD") or office code | Visible when stacked; 3 max, use 0–1 |
| `primaryFields` | Person name | The one thing the holder reads at arm's length |
| `secondaryFields` | Role, then company if not in `logoText` | Combined secondary+auxiliary ≤ 4 with a square QR |
| `auxiliaryFields` | City **or** one phone, not both plus extras | Overflow hides fields ([Pass Design and Creation](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)) |
| `thumbnail` | Headshot or secondary mark, 2:3–3:2 | Optional; Watch will not show it |
| `barcodes[0]` | `PKBarcodeFormatQR` of `https://…/alex.vcf` or profile | Square = Watch-safe |
| `backFields` | `tel`, `mailto`, https, address, pronouns, org contact | **Only** place Apple makes URLs and phones live |

**Safe zones**

- `logo`: keep the mark inside ~80% of the 160×50 pt box; do not run type to the edge.
- `thumbnail`: stay inside 2:3–3:2 or Wallet crops.
- `icon` (29 pt): solid recognizable mark — this is the **iMessage / Mail preview**.
- No strip / background on `generic`. Do not add them "for brand"; they are ignored or illegal for the style.

**Relevance (optional):** office GPS in `locations` (≤10, small radius). `relevantDate` is optional on generic; skip it for an evergreen card. `storeCard`-style "no date" rules do not apply — this is `generic`.

**NFC:** only with an NFC Pass Type ID. `nfc.message` ≤ 64 bytes (vCard URL or id). Otherwise the QR is the tap/scan story.

**Share:** leave `sharingProhibited` false so AirDrop / iMessage / nearby-iPhone share work ([Apple Support](https://support.apple.com/en-us/111112)). Enforce uniqueness server-side if needed; a `.pkpass` is a file.

**Void / expire:** omit `expirationDate` on a living card. Set `voided: true` when the person leaves, then push an update.

## 3. Google — what goes where

```text
┌─────────────────────────────────────────┐
│ (wideLogo or circular logo)  cardTitle  │  ← company
│─────────────────────────────────────────│
│  subheader                              │  ← role
│  header                                 │  ← person name
│  row1:  label/value    label/value      │  ← from classTemplateInfo (≤3 rows)
│  row2:  label/value    label/value      │
│─────────────────────────────────────────│
│              heroImage  1032×812        │  ← photo/texture, NO type
│─────────────────────────────────────────│
│              [ QR ]                     │
└─────────────────────────────────────────┘
  DETAILS: textModules (address/blurb) + linksModule (tel, mailto, https)
```

| Field | Content | Official constraint |
|---|---|---|
| `cardTitle` | Company | < 47 chars EN ([Brand guidelines](https://developers.google.com/wallet/generic/resources/brand-guidelines)) |
| `header` | Person name | Required; treat as the title |
| `subheader` | Role | < 88 chars EN |
| `logo` | Square mark, **15% pad**, not pre-masked | ≥ 660×660, 1:1 |
| `wideLogo` | Optional 16:5 wordmark | Replaces logo on card view; transparent PNG 1280×400 |
| `hexBackgroundColor` | Brand hex, not neon | Recommended palette in the brand guide |
| `heroImage` | Portrait or texture | 1032×812, ~5:4, **no embedded text**, 20 dp pad |
| `barcode` | QR of the same URL as Apple | `QR_CODE` |
| Card rows | Role already in subheader — use rows for city / dept if needed | ≤ 3 rows, prefer 2 items/row |
| `textModulesData` | Address, one-line bio | Brand guide: ≤ 2 class+object combined |
| `linksModuleData` | `tel:`, `mailto:`, `https://`, LinkedIn | Brand guide: ≤ 4 URIs total |
| `appLinkData` | Optional "Open profile" button | Object overrides class |

**Safe zones**

- Logo: 15% margin; Google circles it. A horizontal wordmark will lose its first and last letters — use `wideLogo` for that, keep `logo` as the mark.
- Hero: 20 dp breathing room; nothing important on the top/bottom edge; **no typography**.
- Notification strings (if you ever notify): title < 29, collapsed < 40, expanded < 80.

**NFC:** Smart Tap is partner-only (`enableSmartTap` + `redemptionIssuers` + ASCII `smartTapRedemptionValue`). Default card = QR only.

**Notify:** a business card almost never needs `TEXT_AND_NOTIFY`. Cap is 3/pass/24h. Nearby `merchantLocations` (≤10+10) is optional for a reception desk.

## 4. Artwork rules (both)

1. **Never overlay text on images.** Apple crops and (for background) blurs; Google hero is not localized and explicitly bans embedded text ([Brand guidelines — Hero](https://developers.google.com/wallet/generic/resources/brand-guidelines); [Pass Design and Creation — Images](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)).
2. **Do not simulate Wallet chrome** (fake barcode wells, fake rounded-rect cards, fake "Add" buttons).
3. **One QR, one destination.** Same HTTPS URL on both platforms (a hosted `.vcf` or a profile page that serves `text/vcard` to scanners).
4. **Icon ≠ hero.** Apple `icon` is 29 pt and is what iMessage shows. A cropped hero as icon is unreadable.
5. **`logoText` vs wordmark.** Pick one. System `logoText` **or** a `wideLogo` / typeset logo asset — not both saying the same word.

## 5. Complete Apple `pass.json` (business card)

Replace identifiers, URLs, and RGB with the issuer's values. Images listed in comments must exist in the bundle at 1x / 2x / 3x.

```json
{
  "formatVersion": 1,
  "passTypeIdentifier": "pass.com.example.people.card",
  "serialNumber": "person-alex-rivera-2026",
  "teamIdentifier": "A1B2C3D4E5",
  "organizationName": "Northwind Studio",
  "description": "Business card, Alex Rivera, Northwind Studio",
  "logoText": "Northwind",
  "foregroundColor": "rgb(255, 255, 255)",
  "backgroundColor": "rgb(26, 26, 26)",
  "labelColor": "rgb(200, 200, 200)",
  "sharingProhibited": false,
  "generic": {
    "headerFields": [
      {
        "key": "kind",
        "label": "Card",
        "value": "Staff"
      }
    ],
    "primaryFields": [
      {
        "key": "name",
        "label": "Name",
        "value": "Alex Rivera"
      }
    ],
    "secondaryFields": [
      {
        "key": "role",
        "label": "Role",
        "value": "Design Director"
      },
      {
        "key": "company",
        "label": "Company",
        "value": "Northwind"
      }
    ],
    "auxiliaryFields": [
      {
        "key": "city",
        "label": "Based",
        "value": "Austin"
      }
    ],
    "backFields": [
      {
        "key": "email",
        "label": "Email",
        "value": "alex@northwind.example",
        "dataDetectorTypes": ["PKDataDetectorTypeLink"]
      },
      {
        "key": "phone",
        "label": "Phone",
        "value": "+1-512-555-0142",
        "dataDetectorTypes": ["PKDataDetectorTypePhoneNumber"]
      },
      {
        "key": "web",
        "label": "Website",
        "attributedValue": "<a href='https://northwind.example/alex'>northwind.example/alex</a>",
        "value": "https://northwind.example/alex"
      },
      {
        "key": "linkedin",
        "label": "LinkedIn",
        "value": "https://www.linkedin.com/in/example-alex"
      },
      {
        "key": "address",
        "label": "Office",
        "value": "100 Congress Ave, Austin, TX"
      },
      {
        "key": "vcard",
        "label": "Add to Contacts",
        "value": "https://northwind.example/alex.vcf"
      },
      {
        "key": "org-contact",
        "label": "Issuer",
        "value": "Northwind Studio — hello@northwind.example — https://northwind.example"
      }
    ]
  },
  "barcodes": [
    {
      "format": "PKBarcodeFormatQR",
      "message": "https://northwind.example/alex.vcf",
      "messageEncoding": "iso-8859-1",
      "altText": "Scan to save contact"
    }
  ],
  "locations": [
    {
      "latitude": 30.2642,
      "longitude": -97.7431,
      "relevantText": "Northwind office nearby"
    }
  ],
  "webServiceURL": "https://passes.northwind.example/",
  "authenticationToken": "replace-with-32+char-secret"
}
```

Bundle next to this file: `icon.png` (+ 2x / 3x), `logo.png` (+ 2x / 3x), optional `thumbnail.png` (+ 2x / 3x). Then `manifest.json` + WWDR-inclusive `signature` ([Pass Design and Creation — signed and compressed](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)).

Optional `nfc` (NFC cert only):

```json
"nfc": {
  "message": "https://northwind.example/alex.vcf",
  "encryptionPublicKey": "<base64-X509-P256-SPKI>"
}
```

## 6. Complete Google `GenericClass` + `GenericObject`

Class (template — create once):

```json
{
  "id": "3388000000022111111.northwind_people_card",
  "classTemplateInfo": {
    "cardTemplateOverride": {
      "cardRowTemplateInfos": [
        {
          "twoItems": {
            "startItem": {
              "firstValue": {
                "fields": [{ "fieldPath": "object.textModulesData['DEPT']" }]
              }
            },
            "endItem": {
              "firstValue": {
                "fields": [{ "fieldPath": "object.textModulesData['CITY']" }]
              }
            }
          }
        }
      ]
    }
  },
  "textModulesData": [
    {
      "id": "ABOUT",
      "header": "About",
      "body": "Northwind Studio designs products for civic and commercial clients."
    }
  ],
  "linksModuleData": {
    "uris": [
      {
        "uri": "https://northwind.example",
        "description": "Website",
        "id": "WEB"
      }
    ]
  }
}
```

Object (one person):

```json
{
  "id": "3388000000022111111.person_alex_rivera_2026",
  "classId": "3388000000022111111.northwind_people_card",
  "state": "ACTIVE",
  "genericType": "GENERIC_OTHER",
  "cardTitle": {
    "defaultValue": { "language": "en-US", "value": "Northwind Studio" }
  },
  "subheader": {
    "defaultValue": { "language": "en-US", "value": "Design Director" }
  },
  "header": {
    "defaultValue": { "language": "en-US", "value": "Alex Rivera" }
  },
  "hexBackgroundColor": "#1a1a1a",
  "logo": {
    "sourceUri": { "uri": "https://northwind.example/wallet/logo-660.png" },
    "contentDescription": {
      "defaultValue": { "language": "en-US", "value": "Northwind mark" }
    }
  },
  "heroImage": {
    "sourceUri": { "uri": "https://northwind.example/wallet/alex-hero-1032x812.png" },
    "contentDescription": {
      "defaultValue": { "language": "en-US", "value": "Portrait of Alex Rivera" }
    }
  },
  "barcode": {
    "type": "QR_CODE",
    "value": "https://northwind.example/alex.vcf",
    "alternateText": "Scan to save contact"
  },
  "textModulesData": [
    {
      "id": "DEPT",
      "header": "Dept",
      "body": "Design"
    },
    {
      "id": "CITY",
      "header": "Based",
      "body": "Austin"
    }
  ],
  "linksModuleData": {
    "uris": [
      {
        "uri": "tel:+15125550142",
        "description": "Phone",
        "id": "TEL"
      },
      {
        "uri": "mailto:alex@northwind.example",
        "description": "Email",
        "id": "MAIL"
      },
      {
        "uri": "https://www.linkedin.com/in/example-alex",
        "description": "LinkedIn",
        "id": "LI"
      }
    ]
  }
}
```

JWT save link ([Working with JWTs](https://developers.google.com/wallet/generic/use-cases/jwt), [Issuing for web](https://developers.google.com/wallet/generic/web)):

```json
{
  "iss": "wallet-issuer@project.iam.gserviceaccount.com",
  "aud": "google",
  "typ": "savetowallet",
  "iat": 1710000000,
  "origins": ["https://northwind.example"],
  "payload": {
    "genericObjects": [
      {
        "id": "3388000000022111111.person_alex_rivera_2026",
        "classId": "3388000000022111111.northwind_people_card"
      }
    ]
  }
}
```

Sign RS256 with the issuer service-account key, then:

```text
https://pay.google.com/gp/v/save/<signed_jwt>
```

Render that URL with Google's official **Add to Google Wallet** button asset — do not draw your own ([Brand guidelines](https://developers.google.com/wallet/generic/resources/brand-guidelines)).

## 7. Common-mistakes checklist

Use before review or ship. Each item names the official constraint.

### Truncation and hidden fields

- [ ] Apple front copy is brief; extra secondary/auxiliary fields were **deleted**, not left "for later" ([Pass Design and Creation](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)).
- [ ] Square QR + generic: secondary+auxiliary **combined ≤ 4**.
- [ ] Google English strings sit under the brand-guide caps (title < 47, field label < 20, field data < 15, etc.) ([Brand guidelines](https://developers.google.com/wallet/generic/resources/brand-guidelines)).
- [ ] Tested at large Dynamic Type / font scale. Front slots drop fields; they do not wrap.

### `logoText` vs wordmark

- [ ] Company name appears **once** in the header: Apple `logoText` **or** a typeset `logo.png`, not both.
- [ ] Google: mark in `logo` (circled); wordmark only as `wideLogo` if needed.
- [ ] Watch path checked: with a logo present, long `logoText` is omitted ([Apple Watch layout](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)).

### Artwork

- [ ] No name, role, phone, or URL in `logo` / `thumbnail` / `heroImage` / `background` / `strip`.
- [ ] Google hero is ~5:4 (1032×812), 20 dp pad, no type.
- [ ] Google logo is a **square** with 15% safe margin, not a pre-made circle.
- [ ] `hexBackgroundColor` is not neon.
- [ ] Apple images exist at 1x, 2x, and 3x for every slot the style allows.

### iMessage / Mail / list preview

- [ ] `icon.png` is a legible 29-pt mark. That is what Mail and Messages show ([Pass Design and Creation](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)).
- [ ] Google list thumbnail is the circular `logo`, not the hero.

### Links

- [ ] Apple tappable URLs and phones live in `backFields` (`dataDetectorTypes` and/or `attributedValue` + a plain `value` for watchOS) ([PassFieldContent](https://developer.apple.com/documentation/walletpasses/passfieldcontent)).
- [ ] Google contacts are `tel:` / `mailto:` / `http(s):` in `linksModuleData`, ≤ 4 URIs.
- [ ] No "tap the URL on the front" expectation on Apple.

### Updates, cache, void

- [ ] Apple updates keep `passTypeIdentifier` + `serialNumber`. `authenticationToken` is unchanged ([Updating a Pass](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Updating.html)).
- [ ] APNs payload is `{}`. Visible text is `changeMessage` with `%@`, and only for time-sensitive fields (a card rarely needs one).
- [ ] Web service honors `If-Modified-Since` / `304`. Users who never registered still hold the first `.pkpass`.
- [ ] Google already-saved objects ignore later `saveRestrictions` edits.
- [ ] Google `TEXT_AND_NOTIFY` ≤ 3 per pass per 24h.

### Signing / save buttons

- [ ] Apple signature includes the **WWDR intermediate**; Team ID matches; no post-sign edits ([TN2302](https://developer.apple.com/library/archive/technotes/tn2302/_index.html)).
- [ ] Google button is the official asset; JWT `aud=google`, `typ=savetowallet`, signed with the issuer service account; URL is `https://pay.google.com/gp/v/save/<jwt>`.

### Sharing

- [ ] Card is shareable (`sharingProhibited` false / omitted) unless it is a one-seat credential.
- [ ] Nearby iPhone / AirDrop / iMessage share is accepted as a copy of whatever is on the face + back ([Wallet & Privacy](https://www.apple.com/legal/privacy/data/en/wallet/)). Do not put secrets in fields.
- [ ] If Share is missing in Wallet, the issuer disabled it — not an iOS bug ([Apple Support](https://support.apple.com/en-us/111112)).

### NFC

- [ ] Apple `nfc` only with an NFC-enabled Pass Type ID; `message` ≤ 64 bytes.
- [ ] Google Smart Tap only after partner enablement; otherwise QR only.
