# COPPA 2026 adds four new stop-needs-counsel leaves for K-5 products

**Status:** Absolute rule
**Domain:** EdTech FERPA and data privacy
**Applies to:** `edtech-partner-success`

---

## Why this exists

The COPPA 2025 amendment's full compliance deadline passed on April 22, 2026. Four new categories of data handling now require counsel review before a PSM or CS team can represent the product as compliant to a K-5 district partner: (1) biometric collection from users under 13, (2) government-ID collection from users under 13, (3) K-5 products without a written cybersecurity program, and (4) third-party data flows without a separate VPC (virtual private environment or equivalent isolation). A PSM who tells a district "you're fine on COPPA" without checking these four leaves is making a compliance representation outside their authority and potentially the product's current compliance posture.

## How to apply

For any K-5 product evaluation, renewal, or data-privacy conversation, screen for these four leaves before making any compliance statement. Any "yes" routes to counsel — not to the PSM.

```
COPPA 2026 four-leaf screen (K-5 products):

  Leaf 1: Biometric data from <13
    — Does the product collect voice, face, fingerprint, or behavioral biometric data from K-5 students?
    — YES → STOP. Route to counsel. This is a new compliance surface post-April 2026.

  Leaf 2: Government-ID data from <13
    — Does the product collect or process SSN, state ID, passport, or equivalent from K-5 students?
    — YES → STOP. Route to counsel.

  Leaf 3: No written cybersecurity program
    — Does the vendor have a written cybersecurity program (not just a policy page)?
    — NO → STOP. Route to vendor legal + your security-reviewer before district evaluation proceeds.

  Leaf 4: Third-party data flows without separate VPC
    — Does the product pass any K-5 student data to third-party analytics, AI, or advertising services
      without a separately documented VPC-equivalent data isolation?
    — YES → STOP. Route to counsel.

If all four leaves are clear:
    PSM may continue the data-privacy conversation at the appropriate level.
    Document the screen result in the partner profile.
```

**Do:**
- Run this four-leaf screen before any K-5 data-privacy conversation with a district.
- Document the screen result in the partner profile with a date (screen becomes stale after 6 months or on any product update).
- Route any "yes" leaf to the security-reviewer, then to counsel — do not try to interpret the leaf independently.

**Don't:**
- Make COPPA compliance representations for K-5 products without running this screen.
- Assume a product that was COPPA-compliant pre-April 2026 is automatically compliant post-amendment.
- Confuse a vendor's privacy policy page with a written cybersecurity program (Leaf 3).

## Edge cases / when the rule does NOT apply

This rule applies specifically to K-5 products (users under 13). Products designed exclusively for adults or for grades 9–12 are not COPPA-regulated for the student user; they may have other privacy obligations under FERPA or state law. Higher-ed and corporate L&D segments do not fall under COPPA.

## See also

- [`../agents/ferpa-comms-translator.md`](../agents/ferpa-comms-translator.md) — handles FERPA and privacy-adjacent communications where the screen result affects messaging.
- [`./ferpa-classify-the-data-bucket-before-you-share-or-de-identify.md`](./ferpa-classify-the-data-bucket-before-you-share-or-de-identify.md) — the companion FERPA screening rule that applies to all K-12 student data, not just K-5.

## Provenance

Grounded in the plugin's knowledge file `coppa-2025-amendment-edtech-implications.md` (last reviewed 2026-06-04). The four-leaf structure maps directly to the four new compliance surfaces created by the 2025 COPPA amendment with full enforcement effective April 22, 2026. **Field guidance, not legal advice — route any yes-leaf to counsel.**

---

_Last reviewed: 2026-06-05 by `claude`_
