# Protect PHI and 42 CFR Part 2 records

**Status:** Absolute rule
**Domain:** Privacy, security, and regulatory compliance
**Applies to:** `behavioral-mental-health-practice`

---

## Why this exists

Behavioral health records are among the most sensitive categories of protected health information.
They carry stigma risk (mental health diagnoses, SUD records), legal risk (records that could affect
custody, employment, licensure, or criminal proceedings), and, for SUD records, a federal protection
layer (42 CFR Part 2) that is stricter than HIPAA. A disclosure error in behavioral health can cause
direct patient harm — not just a compliance citation.

The minimum-necessary principle (a HIPAA requirement, and the spirit of Part 2) means: disclose only
what is required for the stated purpose, to the stated recipient, with the stated authorization. Every
step in any disclosure workflow should ask "is this the minimum necessary?"

## How to apply

**Do:**

- Apply HIPAA minimum-necessary standards to every disclosure, access request, and internal sharing
  of PHI.
- For any records involving SUD diagnosis, treatment, or referral from a federally assisted program:
  apply 42 CFR Part 2 first (see `42-cfr-part-2-is-stricter-than-hipaa.md`).
- Train all staff — clinical, billing, administrative — on what constitutes PHI and Part 2-protected
  records, and on the disclosure rules that apply to each.
- Implement EHR access controls: staff should only access patient records they are actively involved
  in treating (minimum-necessary access, not practice-wide open access).
- Conduct a HIPAA Security Risk Assessment on a regular basis (annually is the standard) and
  remediate identified gaps.
- Use secure messaging and HIPAA-compliant communication channels for any PHI — no unencrypted email,
  no personal texting, no consumer file-sharing services.
- Store physical records securely; shred before disposal.
- Log disclosures and maintain a disclosure accounting record as required by HIPAA.

**Don't:**

- Share PHI in clear text (unencrypted) email, text, or messaging platforms without a BAA.
- Allow staff to access records of patients they are not treating.
- Rely on HIPAA's TPO carve-out for SUD records (it doesn't apply under Part 2).
- Discuss PHI in common areas where other patients can hear.
- Commit identifying patient data to a shared, non-secured repository (e.g., a GitHub repo, a shared
  Google Sheet without access controls).
- Assume a verbal disclosure authorization is sufficient — get it in writing for all disclosures.

## Edge cases / when the rule does NOT apply

- Internal treatment communications (a clinician's note shared with a supervising clinician within
  the same practice) are typically within HIPAA's treatment exception, but still subject to minimum-
  necessary access controls.
- Research disclosures may be subject to IRB oversight and specific HIPAA research exceptions;
  consult the practice's compliance officer and IRB.
- There is no "exception" to Part 2 based on convenience or routine practice — the narrow Part 2
  exceptions (medical emergency, audit, court order) are the only pathways that do not require
  specific written patient consent.

## See also

- [`./42-cfr-part-2-is-stricter-than-hipaa.md`](./42-cfr-part-2-is-stricter-than-hipaa.md)
- [`../templates/intake-packet.md`](../templates/intake-packet.md) — Part 2 consent form structure
- [`../knowledge/bh-practice-decision-trees.md`](../knowledge/bh-practice-decision-trees.md) — disclosure routing decision tree
- For HIPAA Security Rule technical safeguard gap assessments → `regulatory-compliance` plugin

## Provenance

Codifies HIPAA Privacy Rule (45 CFR §§164.502–164.514) minimum-necessary and disclosure requirements,
and 42 CFR Part 2 confidentiality requirements, as interpreted for outpatient behavioral health
practice operations. SAMHSA is the primary guidance authority for Part 2; OCR (HHS Office for Civil
Rights) for HIPAA. Final determinations on disclosure legality require qualified legal counsel.

---

_Last reviewed: 2026-06-08 by `claude`._
