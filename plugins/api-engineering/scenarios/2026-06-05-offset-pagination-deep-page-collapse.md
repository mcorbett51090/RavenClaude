---
scenario_id: 2026-06-05-offset-pagination-deep-page-collapse
contributed_at: 2026-06-05
plugin: api-engineering
product: rest-openapi
product_version: "unknown"
scope: likely-general
tags: [pagination, cursor, offset, keyset, rate-limit, n-plus-1, performance]
confidence: high
reviewed: false
---

## Problem

A `GET /transactions` list endpoint used `?page=N&page_size=50` offset pagination. It was fine in testing and for the first few months in production, then degraded badly: a partner's nightly export walked the full history page by page, and by page ~4,000 each request took 8+ seconds and the database CPU pegged. Worse, the export **double-counted and skipped rows** — new transactions inserted during the multi-hour walk shifted every subsequent page's offset, so rows slid across page boundaries.

## Constraints context

- A large, append-heavy table (tens of millions of rows, ordered newest-first by `created_at`), backing a partner-facing export use case that legitimately needs the *whole* dataset.
- `OFFSET N` makes the database scan and discard N rows before returning the page — cost grows linearly with depth, so deep pages are pathologically slow even with an index.
- The data set is **mutating during the walk** (new inserts at the head), which is exactly the condition under which offset pagination loses its correctness guarantee.
- A per-partner rate limit existed but was generous; the slow deep-page queries were inside the limit, so rate limiting didn't protect the database.

## Attempts

- Tried: adding an index on `created_at`. Helped the shallow pages but did nothing for the offset-scan cost on deep pages — `OFFSET 200000` still has to walk past 200k index entries.
- Tried: capping `page` to a maximum (e.g. reject `page > 1000`). Stopped the worst queries but **broke the legitimate full-export use case** — the partner genuinely needed everything, so a hard cap just moved the problem to "how do I export beyond page 1000?"
- Tried (the resolution): switching the list contract to **cursor (keyset) pagination** and giving the bulk-export use case its own answer.

## Resolution

**Offset pagination drifts under writes and degrades on deep pages; cursor (keyset) pagination is O(1) per page and stable across inserts.** The fix:

1. **Cursor pagination as the default contract.** Replace `?page&page_size` with `?limit&cursor`. The cursor encodes the sort key of the last row seen (e.g. `created_at` + a tiebreaker `id` to make the sort **total** — without the tiebreaker, rows sharing a `created_at` can be skipped or repeated at the boundary). Each page query is `WHERE (created_at, id) < (:cursor_ts, :cursor_id) ORDER BY created_at DESC, id DESC LIMIT :limit` — an index range scan that costs the same on page 1 and page 4,000.
2. **Opaque, signed cursor.** Return the cursor as an opaque base64 token, not raw column values — so the internal sort key isn't part of the public contract and can't be tampered with to scan arbitrary ranges.
3. **The cursor is stable under inserts.** New rows at the head don't shift the keyset window, so the walk no longer double-counts or skips. (Rows *deleted* between pages simply don't appear — acceptable for an export; document it.)
4. **For the genuine bulk-export use case, offer the right tool.** A full-history dump is not a paginated-list problem — point the partner at an async export job (`202 + polling` → a downloadable file) or a change-data-feed (`?since=<cursor>` incremental sync), so the interactive list endpoint isn't carrying a batch workload.
5. **Page-size ceiling + cost-based limits.** Cap `limit` (e.g. ≤100) and treat list traversal as a consumption vector (API4) — the protection is a bounded page size and a sane cursor, not just a request-rate limit.

The mental model: `OFFSET` is "skip N then read" (linear, drift-prone); keyset is "read where key < last_seen" (constant, stable). Page numbers are a UI affordance, not a data-access primitive — don't let a page-number contract leak into a programmatic consumer's bulk walk.

**Action for the next engineer:** if a list endpoint is slow only on deep pages, or an export double-counts/skips under load, suspect offset pagination first. The migration is a new `cursor`/`limit` contract (keep `page` working on the old version for a deprecation window), a **total** sort order (sort key + unique tiebreaker), and a separate async/CDC path for true bulk export.

Cross-reference: complements [`../knowledge/api-design-decision-trees.md`](../knowledge/api-design-decision-trees.md) (the pagination tree), [`../best-practices/build-cursor-pagination-over-offset.md`](../best-practices/build-cursor-pagination-over-offset.md), [`../best-practices/build-long-running-ops-with-202-and-polling.md`](../best-practices/build-long-running-ops-with-202-and-polling.md), and the `cursor-pagination-design` skill. The query-plan/index specifics belong to `database-engineering`; this team owns the **pagination contract and the cursor encoding**.
