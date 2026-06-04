# regulatory-compliance — Claude Code plugin

> Financial-regulatory & compliance specialist team for the RavenClaude marketplace.

Ships **twelve specialist agents** — six function agents (AML/KYC analyst, regulatory-reporting analyst, risk-and-controls specialist, policy & procedure writer, examination-prep specialist, Bermuda-insurance specialist) and **six jurisdiction/regulator specialists** (BMA financial-institutions — banking/trust/corporate-services/fund-admin/investment-business, the primary build-out; CIMA/Cayman; Bahamas; Channel Islands — Jersey JFSC + Guernsey GFSC; UK PRA; US federal+state) — backed by **nineteen primary-source-cited regulator knowledge files**, ten playbook skills, eleven working templates, twenty-seven best-practice rules, and one **defensive PreToolUse** hook that scans pending writes for PII (SSN, IBAN, credit-card, Bermuda TIN, wire instructions) before they land on disk.

The plugin's positioning reflects field experience inside a Tier-1 financial regulator (Bermuda Monetary Authority). It produces analysis and documentation; **it does not give legal advice** — legal opinions stay with counsel.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ravenclaude-core@ravenclaude         # prerequisite
/plugin install regulatory-compliance@ravenclaude
/reload-plugins
```

Requires `ravenclaude-core@>=0.5.0`.

## What's inside

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 12 (6 function + 6 jurisdiction) | [`agents/`](agents/) |
| Regulator knowledge files | 19 (13 BMA + 6 jurisdiction/directory) | [`knowledge/bma/`](knowledge/bma/), [`knowledge/jurisdictions/`](knowledge/jurisdictions/) |
| Best-practice rules | 27 | [`best-practices/`](best-practices/) |
| Skills | 10 | [`skills/`](skills/) |
| Hooks | 1 (PreToolUse, defensive) | [`hooks/`](hooks/) |
| Templates | 11 | [`templates/`](templates/) |

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution.

## When to dispatch

```text
"Review this customer's KYC file"          → aml-kyc-analyst
"FATCA filing is due in 6 weeks"           → regulatory-reporting-analyst
"Build our risk register"                  → risk-and-controls-specialist
"Draft an AML policy refresh"              → policy-and-procedure-writer
"BMA exam scheduled for Q3"                → examination-prep-specialist
"BMA-domiciled captive — capital math"     → bermuda-insurance-specialist
"Classify this Bermuda bank/trust/CSP/fund" → bma-financial-institutions-specialist
"Mutual Funds Act or Private Funds Act?"   → cima-cayman-specialist
"Who licenses this Bahamian entity?"       → bahamas-financial-services-specialist
"Jersey JPF or Guernsey PIF?"              → channel-islands-specialist
"Is this firm PRA- or FCA-regulated?"      → uk-pra-specialist
"Which US regulator / BSA-AML / BOI?"      → us-financial-regulation-specialist
```

## Regulator knowledge base

The jurisdiction specialists read **19 primary-source-cited knowledge files** before answering — **thirteen BMA files** under [`knowledge/bma/`](knowledge/bma/) (banking, trust, corporate-services, fund-administration, investment-business, overview, **msb-and-digital-assets**, **aml-atf**, **supervision-and-filings**, a **decision-trees** classification file, a **filing-calendar**, an **economic-substance-and-tax** edge file, and an **edge-cases** catalogue) and six under [`knowledge/jurisdictions/`](knowledge/jurisdictions/) (CIMA/Cayman, Bahamas, Jersey-Guernsey, UK PRA, US federal+state, and a global standard-setter directory). Each cites the actual Act + section and Code + date; values that could not be pinned to the primary text (many regulator sites 403 automated fetch) carry an explicit `[unverified]` marker — the instruction to confirm against the primary PDF before relying.

## House opinions (short list)

1. Cite the regulation (regulator's primary source, with section + paragraph).
2. Privilege is a design constraint.
3. Three lines of defense are not a slogan.
4. Risk appetite drives controls.
5. Remediation has a date and an owner.
6. Default to written.
7. Materiality definitions in writing.
8. Sanctions screening is binary.
9. Privacy by default in examples.
10. Don't give legal advice.
11. Provenance on every regulatory claim.
12. Jurisdiction matters.
13. Risk is quantified where possible (inherent + residual).

Full list (plus 14 anti-patterns) in [`CLAUDE.md`](CLAUDE.md) §3 / §4.

## Hooks — important

[`hooks/scrub-confidential-pre-write.sh`](hooks/scrub-confidential-pre-write.sh) is a **PreToolUse** hook (runs *before* the write completes), scanning the pending content for confidentiality-violating patterns. Catches SSNs, EINs, IBANs, credit-card numbers, Bermuda TIN patterns, passport / driver's-licence shapes, and free-form wire instructions.

**Advisory by default.** For sensitive engagements — and **always for SAR / STR drafting** — flip `exit 0` to `exit 1` at the bottom of the script so the hook blocks the write entirely. Real client PII should never land on disk in a shared repo.

The hook is conservative; tune the Bermuda-specific patterns to match your actual TIN / passport / DL formats. See [`CLAUDE.md`](CLAUDE.md) §7.

## License

MIT — same as the rest of the marketplace.
