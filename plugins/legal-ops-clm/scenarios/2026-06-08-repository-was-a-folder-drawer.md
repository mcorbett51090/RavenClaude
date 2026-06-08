---
scenario_id: 2026-06-08-repository-was-a-folder-drawer
contributed_at: 2026-06-08
plugin: legal-ops-clm
product: generic
product_version: "unknown"
scope: likely-general
tags: [repository, metadata, schema, reporting, findability, due-diligence]
confidence: high
reviewed: false
---

> Not legal advice — an operational field note. A qualified lawyer owned the legal judgement throughout.

## Problem

A mid-size company kept every executed contract as a PDF in nested SharePoint folders organized by department, then year, then "vendor name as whoever-uploaded-it spelled it." When the CFO asked a basic diligence question ahead of a financing — "what's our total committed annual spend across vendor contracts, and which ones have change-of-control clauses?" — nobody could answer without a person opening files one by one. The folders held the documents but answered no question; finding a contract meant already knowing where someone had filed it, and reporting across the set was impossible.

## Constraints context

- ~600 executed contracts; three different folder-naming conventions across departments after two reorgs.
- Same counterparty appeared as "Acme", "Acme Inc.", and "ACME Corp" in three folders.
- The diligence ask had a two-week clock; "open every PDF" was not a plan.

## Attempts

- Tried: a stricter folder-naming convention + a "please file correctly" memo. Failed — conventions drift the moment they meet a busy uploader, and the question was still un-answerable because a folder path is not a queryable field; you cannot SUM a directory tree.
- Tried: full-text search across the PDFs. Failed — search found documents containing a phrase but could not aggregate (total annual value, count of auto-renews next quarter), normalize counterparty names, or tell a signed contract from a draft; it surfaced hits, not answers.
- Tried: a metadata SCHEMA — named fields per contract (counterparty [normalized], type, annual value, effective/expiry dates, auto-renew flag, notice-window deadline, governing law, owner, change-of-control flag, obligation links) in a structured store, with the PDF attached. This worked.

## Resolution

Once contracts were rows with named fields instead of files in folders, the diligence questions became one-line filters/sums: total committed annual spend, contracts with change-of-control clauses, auto-renews due next quarter and their notice deadlines. Normalizing the counterparty field collapsed the "Acme ×3" duplication. The same schema then powered standing reports (expiring-soon, by-value, by-counterparty, obligation-due) that hadn't been possible against the folder tree. Back-filling the schema for 600 contracts was real work, but it was done once and the repository became answerable.

## Lesson

The repository is a schema, not a drawer — contract metadata is named, queryable fields (counterparty, value, dates, auto-renew, notice deadline, owner, governing law, obligation links), not a folder convention. Folders and full-text search find a document you can already describe; a schema answers questions across the whole set and powers reporting and alerts. Normalize the fields that get aggregated (counterparty, value) at entry. Not legal advice — a lawyer owned any read of what a clause (e.g. change-of-control) actually meant.
