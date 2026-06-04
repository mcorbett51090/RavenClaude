---
title: COPPA 2025 Amendment — EdTech Implications
audience: psm, ferpa-comms-translator, security-reviewer
status: stable
last_reviewed: 2026-06-04
refresh_triggers:
  - "DOE FERPA rulemaking publication"
  - "FTC EdTech-specific guidance addendum"
  - "Edmodo / IXL precedent update"
  - "First COPPA enforcement under amended Rule against an EdTech vendor"
sources_verified_at: 2026-06-04
field_guidance_not_legal_advice: true
---

# COPPA 2025 Amendment — EdTech Implications

> The COPPA Rule final amendments (published Apr 22, 2025; effective Jun 23, 2025; **full compliance deadline Apr 22, 2026**) materially change the K-5 EdTech vendor evaluation. The compliance deadline has now passed (today is 2026-06-04). Any unrevised vendor practice is exposed under the amended Rule. **Field guidance — not legal advice.**

---

## 1. What changed in the Apr 22 2025 final rule

- **Separate verifiable parental consent (VPC) required for third-party disclosure** for targeted-advertising-or-other purposes. The existing combined-consent model no longer covers downstream sharing. [[FTC press](https://www.ftc.gov/news-events/news/press-releases/2025/01/ftc-finalizes-changes-childrens-privacy-rule-limiting-companies-ability-monetize-kids-data), [Federal Register](https://www.federalregister.gov/documents/2025/04/22/2025-05904/childrens-online-privacy-protection-rule)]
- **Expanded PI definition** — biometric identifiers (face / fingerprint / voice) **and** government-issued identifiers are now PI for under-13. [[K12 Dive](https://www.k12dive.com/news/ftc-finalizes-coppa-rule-children-data-privacy/738077/), [Davis Wright Tremaine](https://www.dwt.com/blogs/privacy--security-law-blog/2025/05/coppa-rule-ftc-amended-childrens-privacy)]
- **Data-retention limit** — only as long as necessary for the original collection purpose; **no indefinite retention.**
- **Cybersecurity program required** — written plan, designated staff, annual assessment. [[Latham](https://www.lw.com/admin/upload/SiteAttachments/FTC-Publishes-Updates-to-COPPA-Rule.pdf)]

`[verify-at-use — 2026-06-04 — FTC final rule + Federal Register publication]`

---

## 2. What didn't change (deliberately)

- **FTC declined EdTech-specific carveouts**, citing pending FERPA rulemaking by DOE. [[FTC press release](https://www.ftc.gov/news-events/news/press-releases/2025/01/ftc-finalizes-changes-childrens-privacy-rule-limiting-companies-ability-monetize-kids-data)]
- **Edmodo + IXL precedents continue to control the school-authorization line** — schools can authorize only for *educational purpose*; any non-educational use kicks back to direct parental consent. [[PIPC](https://publicinterestprivacy.org/ftc-amicus-briefs-ixl-learning/)]
- **PTAC small-cell guidance unchanged** — n ≥ 10 with complementary suppression on n ≤ 5 remains the conservative industry default.

---

## 3. Four new STOP-needs-counsel leaves

Each leaf triggers the **counsel + security-reviewer dual-review** before any contract / renewal / product expansion can proceed.

### 3.1 Biometric collection from under-13 without VPC
- Face / fingerprint / voice is now COPPA-PI.
- **School authorization is insufficient.** Direct VPC required for K-5 proctoring, voice-input assessment, face-recognition login, etc.
- **PSM signal:** K-5 product mentions "voice assessment," "face authentication," "biometric login," "AI tutor with voice."

### 3.2 Government-ID collection from under-13 without VPC
- E.g., immigration status fields, Medicaid linkage, SSN-suffix verification.
- **School authorization is insufficient.** Direct VPC required.
- **PSM signal:** Form / intake collects any government-issued ID number from K-5 users.

### 3.3 Any K-5 product without a written cybersecurity program
- Written plan + designated staff + annual assessment is now a Rule requirement, not best-practice.
- **PSM signal:** Vendor responds to security-review request with informal "we use cloud providers" instead of a documented program.

### 3.4 Third-party data flow for non-educational purpose without separate VPC
- E.g., parent-engagement analytics shared with marketing partner; usage telemetry sold to research firm.
- **School authorization is insufficient** — separate VPC required for the downstream flow.
- **PSM signal:** Vendor DPA carves out "to improve services" or "for research" without naming specific downstream parties and binding them to the same restriction.

---

## 4. Operational checklist for PSMs evaluating K-5 vendors

Run this checklist on any new K-5 vendor and on annual renewal of existing vendors.

| # | Check | Pass condition | Source |
|---|---|---|---|
| 1 | DPA lists every downstream subprocessor by name | Subprocessor exhibit present + current | NDPA v2.2 Exhibit H |
| 2 | DPA prohibits AI training on student PII | Five-clause model present (see [`ai-training-prohibition-clauses.md`](./ai-training-prohibition-clauses.md)) | NDPA v2.2 + practitioner consensus |
| 3 | No biometric collection OR VPC flow documented | If biometric, vendor demonstrates VPC capture + retention | COPPA amended Rule |
| 4 | No government-ID collection OR VPC flow documented | If government-ID, VPC capture | COPPA amended Rule |
| 5 | Written cybersecurity program available on request | Plan exists + designated staff + annual assessment | COPPA amended Rule |
| 6 | Retention limits stated for each data category | Retention not indefinite; deletion certification on contract end | COPPA amended Rule |
| 7 | Third-party data flow inventory provided | Each downstream flow named, purpose stated, VPC status documented | COPPA amended Rule |
| 8 | Click-through TOS does NOT bundle commercial uses | Educational uses separated; LEA binds parents (not vendor TOS) | Edmodo + IXL precedents |
| 9 | NY + CA + CT cluster exposure disclosed | If vendor operates in 2-of-3, multistate insurance status disclosed | Illuminate $5.1M precedent (see [`edtech-enforcement-precedents-2025-2026.md`](./edtech-enforcement-precedents-2025-2026.md)) |
| 10 | DPA renewal cadence aligns with vendor product changes | Annual DPA refresh tied to product release notes | NDPA v2.2 practice |

Any **fail** → counsel + security-reviewer dual-review before contract.

---

## 5. Enforcement window — why 2026-Q2 onward is the highest-risk period

- COPPA full compliance deadline passed Apr 22, 2026.
- Federal AI Executive Order (Dec 2025) — establishes federal posture aligned with the amended COPPA Rule.
- FTC's two IXL amicus briefs reaffirm the school-authorization narrowness.
- **Net:** any 2026-Q2-or-later breach by an EdTech vendor of an unrevised practice is exposed under the amended Rule, with the Edmodo $6M precedent + IXL pending appeal as the litigation backdrop.

Practitioner consensus 2026: **AI-feature subprocessor disclosure is the most common 2026 audit finding.** PSMs should default-treat any AI feature added since Apr 22, 2026 as needing fresh DPA addendum + subprocessor flow-down review.

---

## 6. What the FTC's deferral to DOE FERPA rulemaking means in practice

The FTC declined EdTech-specific COPPA carveouts in 2025 specifically because the DOE has FERPA rulemaking pending. Practical consequence:

- The **post-2025 EdTech school-authorization line is still controlled by 2014 FTC guidance + Edmodo 2023 order + IXL amicus briefs.**
- The DOE rulemaking, *when published*, will likely reset this line.
- Until then, treat the school-authorization line as **maximally narrow** — only educational purposes, directly tied to the LEA's instructional mission, with downstream flows requiring separate VPC.

---

## See also

- [`ai-training-prohibition-clauses.md`](./ai-training-prohibition-clauses.md) — five-clause DPA model; biometric overlay.
- [`ferpa-dashboard-boundaries.md`](./ferpa-dashboard-boundaries.md) — what a PSM dashboard can/can't surface.
- [`edtech-enforcement-precedents-2025-2026.md`](./edtech-enforcement-precedents-2025-2026.md) — Illuminate / PowerSchool / Naviance / CDE precedents.
- [`parent-comms-jurisdictional-bear-traps.md`](./parent-comms-jurisdictional-bear-traps.md) — state overlay.
- [`state-privacy-law-matrix.md`](./state-privacy-law-matrix.md) — 2026 enforcement scoreboard.
