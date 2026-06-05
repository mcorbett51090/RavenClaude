# Changelog — fintech-payments-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.0] — 2026-06-05

Value-add build-out against the full menu, completing the net-new gaps left after PR #315 (which added the consolidated decision-tree knowledge, `best-practices/`, and `templates/`). Every menu item is dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes).** `idempotency-key-double-charge` (DB unique-index dedup AND a PSP-passthrough idempotency key — teams miss the second), `webhook-replay-and-reconciliation` (verify-signature-first + dedupe-by-event-id + order-independent handlers; reconciliation surfaced both bugs), `decline-retry-storm-and-dunning` (branch on the reason code: never retry a hard decline, smart-retry soft ones), `pci-scope-creep-tokenization` (homegrown JS touching card fields + unmanaged payment-page scripts broke a self-attested SAQ-A). Matches the existing `scenarios/README.md` index + 9-field schema; surfaced behind the mandatory unverified-scenario preamble.
- **Decision-tree knowledge (NEW, complementing #315).** `knowledge/payment-ledger-and-psp-topology-decision-trees.md` — two Mermaid trees the #315 file left open: **ledger model** (single-entry table vs. mutable-balance anti-pattern vs. append-only double-entry) and **PSP topology + settlement timing** (single PSP vs. orchestration layer; fulfill-on-authorized vs. gate-on-settled; the ACH/SEPA delayed-settlement rule), with a dated, cited ISO 20022 cross-border note.
- **Runnable script.** `scripts/recon_diff.py` — a stdlib-only, zero-dependency ledger-vs-PSP reconciliation differ that mechanizes the Reconciliation-discrepancy-triage tree (PSP_ONLY / LEDGER_ONLY / AMOUNT_MISMATCH / CURRENCY_MISMATCH buckets). Money is integer minor units end-to-end (a float amount is rejected loudly); exits non-zero on any discrepancy so a CI recon gate can use it. `ruff check`-clean. Referenced from the idempotency + webhook scenarios.
- **CLAUDE.md** §5 (knowledge & scenario banks + runnable tooling) and the value-add completeness disposition table.

### Decisions (recorded, not built)

- **No bundled MCP server.** The official **Stripe MCP server** (`@stripe/mcp` local, or the remote `https://mcp.stripe.com` via OAuth) is **credentialed and write-capable** (its permissions are scoped by a Restricted API Key — a secret) and per-consumer — so per `docs/best-practices/bundled-mcp-servers.md` it is **RECOMMEND, don't bundle**, with a mandatory `ravenclaude-core/security-reviewer` gate (payments = high blast radius) and the secret carried as a reference (env-var name / RAK), never a literal. No payments MCP clears the zero-config + read-only-by-default bar, so no `mcpServers` entry ships and no `x-mcpAttribution` / `NOTICE.md` is needed. No invented servers.
- **No LSP server.** The plugin is method/design guidance, not tied to one source language (examples span ledger SQL, webhook handlers in any backend language); an `.lsp.json` belongs to the code plugin actually editing that source (`backend-engineering`). N-A.
- **No `bin/`, monitors, output-styles, settings defaults, or themes** — none cleared the "groundable + broadly valuable, doesn't duplicate an existing surface or a neighbouring plugin" bar. The one runtime artifact with real value (`recon_diff.py`) ships under `scripts/`.
- **Skills/commands/templates/hooks coverage held sufficient** — 5 skills, 4 commands, 4 templates, 1 advisory hook already cover payment-flow architecture, integration, reconciliation, PCI-scope, and subscription billing; the scenarios + the new topology trees + the recon script extend reach without a new agent or skill.

### Verify-at-use

- **PCI-DSS v4.0.1** future-dated requirements mandatory after **31 March 2025**; requirements **6.4.3 / 11.6.1** were removed from SAQ-A and replaced with a modified SAQ-A eligibility statement (merchant-confirms-not-susceptible to script attack OR TPSP-provides-protection). SAQ-A eligibility wording is volatile — consult a QSA for authoritative scope.
- **ISO 20022 / Swift** — the MT message family was retired in favour of ISO 20022 (MX/CBPR+) at the end of the coexistence period, **22 November 2025**; relevant to bank-rail cross-border integrations, not card PSPs.
- **Stripe MCP** — package `@stripe/mcp` / remote endpoint `https://mcp.stripe.com`, RAK-scoped, human-confirmation recommended. All version/standard facts are volatile — re-confirm against the vendor / standards body before quoting.

## [0.2.0] — earlier

4-agent fintech-payments-engineering team (payments-architect, payments-integration-engineer, billing-subscriptions-engineer, payments-pci-compliance-advisor): 6 skills, a decision-tree knowledge bank, best-practices, 4 templates, 4 commands, 1 advisory hook. Seams to finance, regulatory-compliance, ravenclaude-core/security-reviewer, api-engineering, backend-engineering, auth-identity.
