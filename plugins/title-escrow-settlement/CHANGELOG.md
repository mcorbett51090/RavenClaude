# Changelog — title-escrow-settlement

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-02

Initial release.

### Added

- **3 agents** — `title-escrow-lead` (order-to-policy workflow, production sequencing, ALTA/CFPB/TRID compliance coordination, wire-fraud control program), `title-examiner` (title search & examination, chain of title, liens/encumbrances, the commitment's B-I requirements / B-II exceptions, curative), `closing-settlement-coordinator` (escrow/settlement, CD/statement coordination, closing/signing, good-funds discipline, disbursement, recording, funding).
- **4 skills** — `title-search-and-examination`, `commitment-and-curative`, `escrow-closing-and-disbursement`, `wire-fraud-and-trust-account-controls`.
- **Knowledge bank** — `title-escrow-decision-trees.md` (4 Mermaid trees: clear-a-title-exception cure-vs-insure-over-vs-except, escrow disbursement authorization, wire verification before disbursement, order-to-policy production workflow) and `title-escrow-reference-2026.md` (dated reference: ALTA best-practice pillars, CFPB/TRID/good-funds concepts, common exceptions & requirements, recording basics — each with source placeholder + retrieval date + verify-at-use).
- **5 best-practices** — verify the wire before you send a dollar, clear the commitment requirements before you close, never disburse against uncollected funds, chain of title is examined not assumed, protect the escrow trust account absolutely.
- **2 templates** — title-commitment-worksheet, closing-checklist.
- **2 commands** — `/clear-title-exceptions`, `/run-closing-checklist`.

### Scope & verify-at-use

- **Advisory domain operations knowledge, not legal, title-underwriting, or financial advice.** The agents make no binding insurability determination (the underwriter's) and give no legal opinion (counsel's). They are wire-fraud sensitive and store no PII.
- All underwriter guidelines, ALTA best-practice pillars, CFPB/TRID specifics, good-funds rules, curative sufficiency standards, and recording requirements in `title-escrow-reference-2026.md` are volatile and jurisdiction-/underwriter-specific — each carries a retrieval date + `[verify-at-use]`; re-confirm against the underwriter, counsel, or the recording jurisdiction before quoting or acting. Never source a wire destination from a file — verify wires by out-of-band callback only.
- Seams to `mortgage-lending` (the CD/loan side), `legal-small-firm` (binding legal / contested title), and `commercial-real-estate` (transaction context).
