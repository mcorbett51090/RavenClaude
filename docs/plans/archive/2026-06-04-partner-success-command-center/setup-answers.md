# Setup answers — fill these in (5 minutes, unblocks real data + hosting)

None of these block the **synthetic** build (Prompts 1–2 work today). They decide
the scope of the later **real-data** swap and where the dashboard lives. Fill in
the right-hand column and the connector/hosting work becomes unambiguous.

## The six data questions

| # | Question | Why it matters | Your answer |
|---|---|---|---|
| Q1 | Which **support tool**? (Zendesk / Freshdesk / Intercom / SFDC Service Cloud / other) | Decides whether a new connector knowledge file is needed for the tickets block. | _…_ |
| Q2 | **Contract** system of record? (Salesforce CPQ / Ironclad / DocuSign CLM / file share) | Decides the contracts-block connector scope. | _…_ |
| Q3 | **Calendar** tool? (Google / Outlook / none — derived countdowns only) | Decides whether calendar events sync for real or stay derived from contract dates. | _…_ |
| Q4 | Where does the **Top 15 list** live today? (Salesforce list view / spreadsheet / in your head) | Drives the source of the `top15_status` field. | _…_ |
| Q5 | Scope: **just you**, or your **team**? | Decides whether `owner_psm` is a real filter or a constant. | _…_ |
| Q6 | **Sentiment** Green/Yellow/Red — Planhat-native field, or you set it? | Drives where the sentiment widget reads from. | _…_ |

## Hosting decision

| Option | What it means | Pick |
|---|---|---|
| **Local-only** | Open the file (or `python3 -m http.server`) on your own machine. Simplest, zero infra, data never leaves your laptop. | _…_ |
| **GitHub Pages (private)** | A private link you can pull up on any device. Slightly more setup; the repo must allow Pages. **Only if the data is synthetic or you're comfortable with the access model** — never publish real partner data. | _…_ |

> Default if unsure: **local-only** with synthetic data while the layout is
> proven; revisit hosting once real data is in play and the privacy model is
> settled.

When these are answered, the real-data connector work (the "Tier 0.5" effort in
[`plan.md`](./plan.md)) can be scoped precisely.
