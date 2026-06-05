# Refresh the QuickBooks OAuth token before the 100-day window closes

**Status:** Absolute rule
**Domain:** Connector / QuickBooks Online
**Applies to:** `data-platform`

---

## Why this exists

QuickBooks Online OAuth 2.0 refresh tokens expire after 100 days of disuse. A connector that calls QBO on a daily schedule can silently approach the 100-day ceiling during a holiday period, a client pause, or a pipeline outage. When the token expires, QBO returns a `401 invalid_grant` and the pipeline goes dark — silently, unless you instrument the expiry. A QBO integration without a documented refresh discipline will fail for at least one engagement per year.

## How to apply

Store the token issuance timestamp alongside the refresh token. On every pipeline run, check the age. If the token is older than 85 days, force a refresh before issuing the API call — don't wait for QBO to reject it.

```python
import datetime, os

def get_valid_qbo_token(token_store) -> str:
    issued_at = token_store.get("issued_at")  # ISO timestamp
    age_days = (datetime.datetime.utcnow() - datetime.datetime.fromisoformat(issued_at)).days
    if age_days >= 85:
        # Force refresh before the 100-day hard expiry
        new_tokens = qbo_client.refresh_access_token(token_store["refresh_token"])
        token_store.update(new_tokens)
        token_store["issued_at"] = datetime.datetime.utcnow().isoformat()
    return token_store["access_token"]
```

**Checklist:**
- [ ] Token issuance timestamp persisted with the refresh token (not just the access token)
- [ ] Pre-emptive refresh at 85 days (15-day buffer before hard expiry)
- [ ] Pipeline alert on `401 invalid_grant` with human escalation path
- [ ] Documented re-auth flow if the refresh token itself expires (requires manual re-authorization)
- [ ] Rate-limit-aware retry: 10 req/s per realm-ID burst limit enforced separately

**Do:**
- Persist the `issued_at` timestamp to durable storage (not memory).
- Set up a monitoring alert for `qbo_token_age_days > 80`.
- Document which human must re-authorize if the token fully lapses.

**Don't:**
- Assume daily pipeline runs keep the token fresh — a multi-week pause will expire it.
- Rely on QBO returning a helpful error message; instrument expiry proactively.
- Use a single QBO OAuth app for multiple clients (each realm-ID is a separate token).

## Edge cases / when the rule does NOT apply

- If a QBO integration runs via a managed connector (Fivetran, Airbyte Cloud) that handles OAuth renewal internally, verify the platform's behavior but do not implement manual refresh on top of it — check vendor docs.
- Sandbox/test realm tokens follow the same rules unless Intuit changes them — verify at build time.

## See also

- [`../agents/etl-pipeline-engineer.md`](../agents/etl-pipeline-engineer.md) — owns QBO connector configuration
- [`./connector-rate-limit-aware-retry.md`](./connector-rate-limit-aware-retry.md) — the companion rule for QBO's 10 req/s per realm limit

## Provenance

Codifies knowledge from `knowledge/quickbooks-online-integration.md` (QBO OAuth + 100-day refresh discipline) and data-platform CLAUDE.md §4 anti-patterns ("A QuickBooks integration written without rate-limit-aware retry logic").

---

_Last reviewed: 2026-06-05 by `claude`_
