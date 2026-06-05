# Govern subscriptions and data-driven alerts as managed content

**Status:** Pattern
**Domain:** Governance / server administration
**Applies to:** `tableau`

---

## Why this exists

Tableau Server and Cloud allow any viewer to subscribe themselves (and others) to
scheduled PDF/image deliveries of any view they can access, and any user to set
data-driven alerts on numeric marks. In large deployments, unmanaged
subscriptions accumulate quickly: hundreds of outdated, redundant, or broken
subscriptions that fire every morning and consume server rendering capacity even
when the underlying workbook has changed or been archived. Alerts on stale data
or retired views generate noise. Without governance, the subscription and alert
catalogue becomes unmaintainable.

## How to apply

**Audit quarterly:** use the REST API to list all subscriptions and alerts on the
site. Flag any that reference a deprecated or archived view, or that have not
been opened in 90 days.

```python
# List all subscriptions via REST API (paginate — use the pagination rule)
def list_all_subscriptions(server_url, auth_token, site_id):
    # ... paginated GET /api/3.21/sites/{site_id}/subscriptions
    pass

# Flag stale subscriptions: last_sent older than 90 days or view is archived
def audit_subscriptions(subscriptions: list) -> list:
    stale = []
    for sub in subscriptions:
        view = get_view(sub["content"]["id"])
        if view is None or view.archived:
            stale.append(sub)
        # Additional: check sub["lastSent"] against 90-day threshold
    return stale
```

**Permissions:** restrict who can send subscriptions to others (prevent users
from adding colleagues to high-frequency deliveries without consent). Configure
this in Server settings `[verify-at-build]`.

**Broken view alert:** implement a webhook or job that deletes subscriptions
pointing to views that have been deleted or moved.

**Do:**
- Run a quarterly subscription and alert audit; report stale items to their owners.
- Restrict "subscribe others" permissions to prevent unsolicited delivery subscriptions.
- Delete subscriptions pointing to archived or deleted content automatically.

**Don't:**
- Let subscriptions accumulate indefinitely — each scheduled subscription
  consumes a background job slot on Server.
- Leave alerts on views that have been certified with a different data source
  — the alert thresholds may no longer be meaningful.
- Block all subscriptions site-wide — they provide genuine value for operational
  monitoring.

## Edge cases / when the rule does NOT apply

- Small deployments (< 50 users, < 100 views): subscription governance overhead
  is not yet worth automating; a manual quarterly review is sufficient.

## See also

- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — owns site governance including subscriptions
- [`./gov-sites-and-projects-as-the-governance-skeleton.md`](./gov-sites-and-projects-as-the-governance-skeleton.md) — subscriptions inherit the project permission model
- [`./server-rest-api-paginate-all-resources.md`](./server-rest-api-paginate-all-resources.md) — paginate the subscription list call

## Provenance

Standard Tableau Server/Cloud administration practice. The subscription and
alert management REST API endpoints are documented in Tableau REST API reference
`[verify-at-build]`. Site-level subscription governance is a standard
recommendation in Tableau server administration guides.

---

_Last reviewed: 2026-06-05 by `claude`_
