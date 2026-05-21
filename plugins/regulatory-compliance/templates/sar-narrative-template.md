# SAR / STR narrative — [Case ID]

> **Confidentiality: regulator-only.** Do not share with the subject. Do not commit to general-purpose repositories. The plugin's PreToolUse hook flags PII; for SAR / STR drafting, flip the hook to BLOCK (`exit 2`) per [`../CLAUDE.md`](../CLAUDE.md) §7.

**Case ID:** [internal case reference]
**Filing regulator:** [FinCEN / FIU / BMA FIA / other]
**Filing entity (filer):** [your firm]
**Filer name (MLRO / AMLCO):** [named individual]
**Subject(s):** [primary subject — name in structured fields; the narrative references them]
**Date of detection:** [YYYY-MM-DD]
**Activity date range:** [from YYYY-MM-DD to YYYY-MM-DD]
**Total amount:** [currency + amount, with FX rate + date if cross-currency]
**Typology shorthand:** [structuring / layering / TBML / funnel account / mirror trading / pass-through / cash-business inconsistency / PEP atypical / other]
**Prior SAR/STR (if continuing activity):** [prior ID + date]

---

## Narrative

### Opening

This [SAR / STR] is being filed by [filing entity] to report [typology shorthand] activity by [subject], involving [amount] across [period] in [account(s) / instrument(s)].

### Subject background

[Brief: customer relationship since [date], declared business / occupation, declared source of funds / source of wealth, original risk rating at onboarding.]

### Chronology

- **YYYY-MM-DD** — [event 1, dated bullet, fact-only, no editorializing]
- **YYYY-MM-DD** — [event 2]
- **YYYY-MM-DD** — [...]

### Why suspicious — the typology

[2-5 sentences. Name the typology explicitly. Explain why the observed pattern matches the typology. Reference specific amounts / counterparties / geographies / mechanics. Tie back to inconsistency with customer's declared profile.]

### Internal investigation steps taken

- [Step 1 — what we reviewed, sources consulted]
- [Step 2 — parties interviewed (internal only — never the subject), questions asked, answers]
- [Step 3 — additional context obtained from monitoring / screening / negative-news searches]
- [Step 4 — internal escalation: who reviewed, who approved filing]

### Status of relationship

- Maintained | Restricted | Exited (pending) | Exited (completed) — as of [YYYY-MM-DD]
- [If restricted or exited: brief rationale.]

### Closing

This filing is intended to alert [regulator / FIU] to the above and is not a determination that any illegality has occurred.

---

## Filing audit trail

| Item | Date | Person | Notes |
|---|---|---|---|
| Activity first detected | YYYY-MM-DD | [name + system] | |
| First-pass disposition | YYYY-MM-DD | [name] | [alert workflow ID] |
| Escalated to MLRO | YYYY-MM-DD | [name] | |
| Filing decision (file / no-file) | YYYY-MM-DD | MLRO [name] | |
| Filing submitted | YYYY-MM-DD | MLRO [name] | [filing system ID] |
| Filing acknowledgment received | YYYY-MM-DD | [system] | [ack ID] |

---

## Continuing-activity check

- **Days since prior SAR (if any):** [#]
- **Continuing-activity report due:** [YYYY-MM-DD or "n/a (initial filing)"]

---

## Internal disclosure controls

- **Tipping-off:** confirmed compliance with tipping-off rules (no disclosure to subject or related parties).
- **Internal access:** restricted to [named roles only].
- **Storage:** [secure repository name].

---

**Quality-check sign-off:**

- [ ] Typology named explicitly
- [ ] Chronology dated and complete
- [ ] Subject identifying details accurate (cross-check with KYC file)
- [ ] No speculation about criminal-law violations
- [ ] No tipping content
- [ ] Maker-checker sign-off recorded
- [ ] Filing within statutory deadline
