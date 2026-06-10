# Security questionnaires, RFP compliance & the trust library

> _Last reviewed: 2026-06-10._ How to answer security/vendor-risk questionnaires and stay RFP-compliant — honestly and reusably. Framework **names** (SIG, CAIQ, SOC 2, ISO 27001) are durable; any specific control number, report date, or audit-period claim is **engagement-specific and must be verified against the current report**, never quoted from memory.

---

## The frameworks you'll meet

| Questionnaire / standard | What it is | How to use it |
|---|---|---|
| **SIG** (Shared Assessments) | A large, standardized vendor-risk questionnaire (Core / Lite tiers) | Map answers to your control set once; reuse across buyers who send SIG |
| **CAIQ** (CSA, on the Cloud Controls Matrix) | Cloud-specific yes/no control questionnaire | Maintain a master CAIQ; many buyers accept it in lieu of a bespoke one |
| **VSA / bespoke spreadsheets** | A buyer's own security team spreadsheet | Map each row to your control taxonomy; don't answer cold |
| **SOC 2 (Type II)** | An independent attestation over the Trust Services Criteria across a period | Your primary evidence package — point buyers to it to deflect re-answering |
| **ISO 27001** | A certified ISMS with a Statement of Applicability | The SoA item is the evidence behind an "implemented" claim |

**The leverage move:** most buyers will accept your **SOC 2 Type II report + a trust center** in place of a 300-cell questionnaire. Offer that first; it deflects the repetitive work and is faster for everyone.

---

## The answering discipline (non-negotiable)

A security questionnaire is a **legal artifact**, not marketing copy. Every claim must survive an audit and a contract clause.

1. **Map every "yes" to a control + evidence.** Name the control and what backs it: a SOC 2 report section, an ISO SoA item, a written policy, a system config. A "yes" with no evidence is not a "yes".
2. **State the truth boundary plainly** for each answer:
   - **Implemented** — shipped and evidenced.
   - **Roadmap (dated)** — planned; say so, never inflate to implemented.
   - **Not applicable (with why)** — e.g., "no on-prem component, so N/A."
   - **Compensating control** — we don't do X exactly, but Y covers the same risk.
3. **Flag every unverifiable claim** for `ravenclaude-core/security-reviewer` *before* it ships. If you can't tie it to evidence yourself, it goes in the verification queue, not the answer box. On a security questionnaire, a confident wrong answer is a contractual liability (and a clawback / fraud risk).
4. **Never inflate roadmap → implemented.** This is the cardinal sin of questionnaire response — it converts a sales shortcut into a legal exposure.

---

## RFP compliance checklist (disqualification guard)

RFPs are routinely thrown out on technicalities *before* the prose is read. Before submitting, confirm:

- [ ] **Deadline** — submitted before the exact cutoff (timezone checked).
- [ ] **Format** — file type, naming, portal vs email as specified.
- [ ] **Page / length limits** — per section, not just overall.
- [ ] **Section order + numbering** — matches the RFP's structure exactly; evaluators score against it.
- [ ] **Mandatory forms / attachments** — signed, completed, included (insurance certs, references, pricing sheets).
- [ ] **Every requirement answered** — one matrix row each (comply / partial / roadmap / no-bid); no requirement left blank.
- [ ] **Pricing format** — matches the requested structure exactly.

A brilliant response that misses a mandatory form scores zero.

---

## The reusable trust-answer library (the compounding asset)

The repetitive questionnaire is a tax; the library is how you stop paying it twice.

- **Answer once, curate, reuse.** Every answered question goes into the library (the RFP response matrix template has a library section).
- **Owner + freshness date on every answer.** Security posture changes; a stale "yes" is a liability. Date each answer and assign an owner who keeps it current.
- **Promote the library to a trust center.** A self-serve trust center (controls, SOC 2 on request, sub-processors, status, data-handling) deflects the repetitive questionnaires entirely — the highest-leverage end state.
- **Version with the security program.** When `cybersecurity-grc` / `security-engineering` change a control, the library answer changes with it. The library mirrors the program of record; it is not a separate source of truth.

---

## Seams

- **`ravenclaude-core/security-reviewer`** — mandatory verification of any security claim before it ships to a prospect.
- **`cybersecurity-grc` / `security-engineering`** — own the SOC 2 / ISO program, the controls, and the evidence the answers map to. This plugin *responds*; those plugins *own the program*.
- **`ravenclaude-core/documentarian`** — turns the curated library into a customer-facing trust center.
