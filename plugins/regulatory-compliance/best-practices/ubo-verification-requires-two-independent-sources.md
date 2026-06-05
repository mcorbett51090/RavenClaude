# UBO Verification Requires Two Independent Sources

**Status:** Absolute rule
**Domain:** AML / KYC / beneficial ownership
**Applies to:** `regulatory-compliance`

---

## Why this exists

Ultimate beneficial ownership (UBO) verification is one of the highest-risk elements of KYC onboarding, and the most common failure mode is relying on a single source — typically a client-provided UBO declaration — without corroboration. A client-provided declaration tells you what a customer claims; a second independent source tests whether the claim is consistent with external evidence. FATF Recommendation 24 and most national implementing rules require that UBO information be "verified from reliable, independent sources" (plural is deliberate). Single-source UBO verification is a textbook finding at examination, because it leaves the firm unable to demonstrate it tested the declaration rather than just received it.

## How to apply

Every UBO verification package must include at least two independent sources, with the independence criterion explicitly documented.

```
UBO Verification Checklist — Minimum Standard
──────────────────────────────────────────────────
Step 1 — IDENTIFY UBOs
  Threshold: 25% direct or indirect beneficial ownership (check
  jurisdiction — some regimes use 10% or lower for higher-risk sectors).
  Walk the ownership chain to every natural person who qualifies.

Step 2 — SOURCE ONE (Primary document)
  Document type: passport / national ID / other government-issued photo ID
  Date: within the last 5 years (or per jurisdiction requirement)
  Condition: original or certified copy; liveness / document authentication if remote

Step 3 — SOURCE TWO (Independent corroboration — must be independent of the UBO and of Source 1)
  Acceptable: official corporate registry (confirm the UBO is listed at the
              relevant threshold); certified financial statements showing ownership
              structure; regulatory filing (e.g., a statutory BO register submission);
              corroborating government database (where available and accessible).
  Not acceptable as Source 2: a second declaration from the same client, or
  another document provided by the UBO themselves.

Step 4 — DOCUMENT INDEPENDENCE
  State explicitly why Source 2 is independent of Source 1 and independent of the client:
  e.g., "Source 2 is the Companies House registration extract, pulled directly
  from the registry by the compliance analyst on 2026-05-15 — not provided by the client."

Step 5 — RECONCILE DISCREPANCIES
  If Source 1 and Source 2 conflict → EDD trigger → escalate to MLRO.
  If Source 2 is unavailable → document the reason, the alternatives attempted, and
  the compensating measures applied; do not proceed without MLRO sign-off.
```

**Do:**
- Pull Source 2 directly yourself (from the registry, the database, the public record) — don't ask the client to provide it.
- Document the date and URL/access point of any digital source so the pull can be reproduced.
- Re-verify UBO on every material change of control, not only at onboarding.

**Don't:**
- Accept a client-provided shareholder register as Source 2 — it is controlled by the same party as Source 1.
- Treat a second ID document from the same UBO as a second independent source — independence is about the *origin* of the information, not the count of documents.
- Mark UBO verification "complete" when a discrepancy between sources is open.

## Edge cases / when the rule does NOT apply

- **Listed companies** (securities traded on a regulated, transparent exchange) — the exchange's regulatory filing disclosure substitutes for full UBO verification on the listed entity itself; still verify any individual UBO above threshold in the listed company's controlling shareholder chain.
- **Government entities or their wholly-owned subsidiaries** — typically exempt from UBO verification in most FATF-implementing regimes; document the exemption basis.

## See also

- [`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md) — owns the KYC file review and UBO verification discipline.
- [`./edd-is-depth-not-document-count.md`](./edd-is-depth-not-document-count.md) — the two-source rule is the minimum; EDD requires corroboration on source-of-wealth and source-of-funds beyond the ownership chain.

## Provenance

Codifies the AML/KYC-analyst's UBO verification standard from CLAUDE.md §4 anti-pattern ("KYC EDD packages relying on a single source for verification of a higher-risk customer") and the `kyc-edd-review` skill. The two-independent-sources requirement reflects FATF Recommendation 24 and standard BSA/AML examination expectations across the BMA, CIMA, JFSC, GFSC, and FinCEN frameworks.

---

_Last reviewed: 2026-06-05 by `claude`_
