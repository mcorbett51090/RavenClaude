# No breach does not mean no FERPA exposure after Naviance

**Status:** Absolute rule
**Domain:** EdTech FERPA and data privacy
**Applies to:** `edtech-partner-success`

---

## Why this exists

Before February 2026, the common working assumption in EdTech CS was: "if we haven't had a breach, we don't have a FERPA enforcement problem." The PowerSchool Naviance $17.25M wiretapping settlement (February 2026 preliminary; June 10, 2026 final) changed that assumption. The Naviance theory: vendor collection of student behavioral data through session-replay tools (in the Naviance case, FullStory) without adequate consent or disclosure was treated as an unauthorized interception of education-record-adjacent information — not a breach, but still a violation. PSMs can no longer represent "no breach" as equivalent to "no FERPA exposure" to a district partner, especially for products that use session-replay, behavioral analytics, or third-party tag managers on student-facing pages.

## How to apply

Before making any data-privacy representation to a K-12 district, screen for the Naviance exposure pattern — third-party behavioral-data collection on student-facing surfaces without explicit consent or disclosure.

```
Naviance-pattern screen for PSMs:

  Question 1: Does the product have any student-facing pages (login, assessment, learning activity)?
    — NO: lower risk on this theory; standard FERPA screening still applies
    — YES: proceed to Question 2

  Question 2: Are session-replay, behavioral analytics, or third-party tag managers
    active on those pages? (FullStory, Hotjar, Amplitude, Mixpanel embedded on student pages)
    — NO: document and represent accordingly
    — YES → STOP. Route to counsel before making any data-privacy representation.

  Question 3: Is there a specific disclosure in the DPA or privacy policy covering these tools?
    — YES AND reviewed by counsel: may proceed; document the disclosure
    — NO or unclear → STOP. Route to counsel.

PSM representation rule:
  You may say: "We have not had a data breach."
  You may NOT say: "We have no FERPA compliance risk."
  When in doubt: "Our data-privacy posture is [X]; I'll loop in our legal team to confirm
    the specific question you're asking about our analytics stack."
```

**Do:**
- Run the Naviance-pattern screen before any district data-privacy conversation involving student-facing surfaces.
- Document the screen result in the partner profile.
- Escalate any positive screen to the security-reviewer and then to counsel.

**Don't:**
- Represent "no breach = no FERPA exposure" to a district partner.
- Assume that a vendor's privacy-policy page covers session-replay tools — check the DPA specifically.
- Answer "do you have any session-replay tools on student-facing pages?" with a guess.

## Edge cases / when the rule does NOT apply

This rule applies to products with student-facing interfaces. Admin-only tools (products accessed only by district administrators, not by students or families) have a different FERPA exposure profile. Higher-ed and corporate L&D segments may have different legal frameworks; this rule is specific to K-12 FERPA.

## See also

- [`../agents/ferpa-comms-translator.md`](../agents/ferpa-comms-translator.md) — handles the partner-facing communication when a privacy concern has been identified.
- [`./ferpa-classify-the-data-bucket-before-you-share-or-de-identify.md`](./ferpa-classify-the-data-bucket-before-you-share-or-de-identify.md) — the companion FERPA data-classification rule.

## Provenance

Grounded in the plugin's knowledge file `edtech-enforcement-precedents-2025-2026.md` (last reviewed 2026-06-04). The Naviance pattern — wiretapping theory on session-replay tools — is the specific new exposure this rule addresses. **Field guidance, not legal advice — route any positive screen to counsel.**

---

_Last reviewed: 2026-06-05 by `claude`_
