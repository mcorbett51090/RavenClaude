# Section 508 conformance is the law — not a nice-to-have

**Status:** Absolute rule
**Domain:** Accessibility / ICT compliance
**Applies to:** `public-sector-govtech`

---

## Why this exists

Section 508 of the Rehabilitation Act (29 U.S.C. § 794d) requires that federal agencies and the
contractors providing them with Information and Communications Technology (ICT) ensure that the
ICT is accessible to employees and members of the public with disabilities. This is not a
guideline or a best-practice recommendation — it is a federal civil-rights law with enforcement
authority. An inaccessible government website, software application, or document can expose the
agency to complaints filed with the Access Board, OCR, or through litigation. Contractors who
deliver non-conformant ICT may face contract disputes or corrective action.

The most common posture that leads to violations is deferral: "we'll fix accessibility after
launch." Post-launch remediation is dramatically more expensive than building accessibility in from
the start (accessibility debt compounds exactly like technical debt), and it leaves real people —
federal employees and members of the public with disabilities — unable to use the system for the
entire remediation period. That gap is the legal harm the statute was written to prevent.

## How to apply

1. **Include 508 testing in Sprint 0 and in the definition of done.** Every sprint that ships
   user-facing functionality should have 508 testing as an acceptance criterion.
2. **Automated tools first; manual testing required.** Automated tools (axe, ANDI, WAVE) catch
   30–40% of WCAG issues. Manual testing with a screen reader (NVDA+Firefox, JAWS+Chrome,
   VoiceOver+Safari) is required before a VPAT can be marked "Supports."
3. **Author a VPAT/ACR for every product delivered to a government buyer.** The Voluntary Product
   Accessibility Template (VPAT) / Accessibility Conformance Report (ACR) is the standard evidence
   artifact. "We comply" without documentation is not a conformance claim — it is an assertion.
4. **Remediate blockers before release.** A blocker is a WCAG failure that prevents a user of
   assistive technology from completing a core task. It does not ship.

**Do:**

- Integrate 508 testing into CI/CD and the sprint definition of done.
- Test with actual assistive technology (NVDA, JAWS, VoiceOver) — not just automated tools.
- Maintain a current VPAT/ACR for every product; update it on every major release.
- Train developers on WCAG 2.1 AA success criteria — not just ARIA attributes.

**Don't:**

- Defer 508 testing to a "pre-launch accessibility review."
- Mark VPAT criteria "Supports" without documented evidence from AT testing.
- Treat 508 as a checkbox for the contracting office, separate from the engineering team.
- Assume internal tools are exempt — employees with disabilities have the same rights.

## Edge cases / when the rule does NOT apply

- **Products with a specific statutory exemption:** some narrow categories of ICT have documented
  exemptions (national security systems under E.O. 12958; ICT purchased or maintained before
  January 18, 2018, if updating would require a substantial redesign). The exemption must be
  formally documented by the agency — "it would be hard" is not an exemption.
- **Undue burden:** an agency may claim fundamental alteration or undue burden, but must document
  the determination and provide an alternative means of access. Contractors cannot invoke this
  on the agency's behalf.

## See also

- [`./plain-language-serves-the-citizen-and-is-required.md`](./plain-language-serves-the-citizen-and-is-required.md)
- [`../skills/accessibility-508-and-records/SKILL.md`](../skills/accessibility-508-and-records/SKILL.md)
- [`../knowledge/govtech-decision-trees.md`](../knowledge/govtech-decision-trees.md) — 508 conformance path tree

## Provenance

29 U.S.C. § 794d (Rehabilitation Act § 508), as amended by the Workforce Innovation and
Opportunity Act (2014). Implemented by the Access Board's ICT Accessibility Standards (January 2017
refresh, 36 CFR Part 1194). WCAG 2.1 AA is incorporated by reference.

---

_Last reviewed: 2026-06-08 by `claude`._
