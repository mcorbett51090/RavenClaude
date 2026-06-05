---
scenario_id: 2026-06-05-pci-scope-creep-tokenization
contributed_at: 2026-06-05
plugin: fintech-payments-engineering
product: generic
product_version: "unknown"
scope: likely-general
tags: [pci-dss, saq-a, tokenization, scope-reduction, hosted-fields, client-side-script]
confidence: medium
reviewed: false
---

## Problem

A team believed they were "SAQ-A, card data never touches our servers" because they used a PSP's JS SDK. But over time the checkout page had accumulated a homegrown card-input form whose values were read by the site's own JavaScript before being handed to the PSP tokenizer — so card field values **did** transit the merchant's own client-side code, and a pile of third-party marketing/analytics scripts ran on the same payment page with no inventory or integrity control. Two scope problems: the JS touching card fields pushed them toward SAQ-A-EP / SAQ-D territory, and the unmanaged scripts on the payment page collided with the PCI-DSS v4.x client-side-script expectations. This surfaced during an acquirer's annual attestation, not a breach — but it meant their self-attested SAQ-A was not actually defensible.

## Constraints context

- **PCI scope is an engineering-design consequence, then a compliance verdict.** This team's job (and this plugin's lane) is to *minimize* scope by architecture; the SAQ determination and any QSA assessment are a regulatory clearance that routes to `regulatory-compliance` / a QSA, and the security verdict to `ravenclaude-core/security-reviewer` (CLAUDE.md §3). This scenario is the engineering half only.
- PCI-DSS v4.0.1 future-dated requirements became **mandatory after 31 March 2025** `[verify-at-use]`. Two of them — **6.4.3** (manage and integrity-check every script on the payment page) and **11.6.1** (detect tampering/unexpected changes to the payment page) — were subsequently **removed from SAQ-A and replaced with a modified SAQ-A eligibility statement**: the merchant must confirm their referring payment page is not susceptible to script-based attacks, OR confirm the TPSP's embedded payment element provides that protection on the merchant's behalf `[verify-at-use — SAQ-A eligibility wording is volatile; confirm the current SAQ-A criteria and consult a QSA for authoritative scope]`.
- The cheapest PCI compliance is the card data you never receive — re-architecting toward a fully PSP-hosted field is a smaller lift than carrying SAQ-D controls.

## Attempts

- Tried: arguing they were already SAQ-A because "we use the PSP SDK." Failed — using the SDK is necessary but not sufficient; if *your* JS can read the card field values, the field values transited your code and scope grows.
- Tried: adding a Content-Security-Policy and a script inventory to satisfy the script-management intent while keeping the homegrown form. Partially helped the script-control gap, but didn't fix the core problem that their JS still handled card values.
- Tried (the move that worked): **replace the homegrown card inputs with the PSP's hosted fields / iframe elements** so card values live in the PSP's origin and the merchant JS never sees them, **and** establish a managed inventory + integrity check (or rely on the TPSP's attestation) for the remaining scripts on the payment page. That restored a defensible SAQ-A posture and shrank the script-management surface.

## Resolution

**Tokenize so the raw PAN never touches your servers *or your client-side code*, and control the scripts on the payment page.** Engineering moves:

1. **Use the PSP's hosted fields / iframe elements** — card values stay in the PSP's origin; your JS never reads them. This is the SAQ-A-eligible architecture.
2. **Never let your own JS read card field values** — the moment it does, scope grows (SAQ-A-EP / SAQ-D). A homegrown card form wired to a tokenizer is the common trap.
3. **Inventory and integrity-check every script on the payment page** (PCI-DSS v4 6.4.3 / 11.6.1 intent), or confirm the TPSP provides that protection per the current SAQ-A eligibility statement `[verify-at-use]`.
4. **Log money operations, never card data** — never the PAN/CVV/track data, anywhere.
5. **Route the verdict out.** This plugin minimizes scope and recommends the architecture; the SAQ determination + attestation go to `regulatory-compliance` / a QSA, and the security clearance to `ravenclaude-core/security-reviewer`. See the two PCI-scope trees in `../knowledge/fintech-payments-engineering-decision-trees.md`.

**Action for the next engineer:** "we use the PSP SDK" is not proof of SAQ-A. Check whether your own JavaScript can ever read a card field value (if yes, scope grows) and whether the scripts on the payment page are inventoried + integrity-checked (v4 6.4.3/11.6.1). Confirm the *current* SAQ-A eligibility wording and route the attestation to a QSA — this is engineering decision-support, not a compliance verdict.

**Sources (retrieved 2026-06-05):**
- PCI DSS v4.0.1 publication + future-dated requirements effective 31 March 2025 — https://blog.pcisecuritystandards.org/just-published-pci-dss-v4-0-1 and https://blog.pcisecuritystandards.org/now-is-the-time-for-organizations-to-adopt-the-future-dated-requirements-of-pci-dss-v4-x
- Requirements 6.4.3 / 11.6.1 removed from SAQ-A, replaced with a modified eligibility statement (merchant-confirms-not-susceptible OR TPSP-provides-protection) — https://hyperproof.io/resource/pci-dss-4-0-update-new-saq-a-eligibility-criteria/ and https://trustedsec.com/blog/the-hidden-trap-in-the-pci-dss-saq-a-changes

PCI-DSS requirement details and SAQ-A eligibility are volatile — `[verify-at-use]` against the current standard and a QSA before any deliverable.

Cross-reference: canonical guidance is `../best-practices/minimize-pci-scope-with-tokenization.md` and `../best-practices/never-log-pan-or-cvv.md`; the two PCI-scope trees in `../knowledge/fintech-payments-engineering-decision-trees.md`; template `../templates/pci-scope-checklist.md`.
