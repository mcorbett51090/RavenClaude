# Paginate all Tableau Server REST API list calls

**Status:** Absolute rule
**Domain:** Server / automation
**Applies to:** `tableau`

---

## Why this exists

The Tableau Server REST API returns paginated results for list endpoints (list
workbooks, list views, list users). The default page size is 100 items and the
API caps it at 1000 per call `[verify-at-build]`. A script that calls
`GET /workbooks` once and processes the first page silently misses every
workbook after the 100th. In a site with 500 workbooks this is a 80% data loss
— and the script will succeed with no error, making the gap invisible until
someone notices a workbook is missing from the report.

## How to apply

Always implement pagination using the `pageNumber` and `pageSize` parameters
and the `pagination` block in the response:

```python
import requests

def get_all_workbooks(server_url: str, auth_token: str, site_id: str) -> list:
    headers = {"x-tableau-auth": auth_token}
    page_size = 100
    page_number = 1
    all_workbooks = []

    while True:
        resp = requests.get(
            f"{server_url}/api/3.21/sites/{site_id}/workbooks",
            headers=headers,
            params={"pageSize": page_size, "pageNumber": page_number},
        )
        resp.raise_for_status()
        data = resp.json()

        workbooks = data["workbooks"]["workbook"]
        all_workbooks.extend(workbooks)

        pagination = data["pagination"]
        total = int(pagination["totalAvailable"])
        page_number += 1

        if page_size * (page_number - 1) >= total:
            break

    return all_workbooks
```

**Do:**
- Always read `pagination.totalAvailable` and loop until all pages are retrieved.
- Use `pageSize=100` (or the maximum supported) to minimise round trips
  `[verify-at-build]`.
- Log the total retrieved vs total available as a sanity check in automation scripts.

**Don't:**
- Make a single REST call and assume the result is complete.
- Use a hardcoded iteration count instead of the `totalAvailable` check.
- Ignore `resp.raise_for_status()` — a 403 or 404 mid-pagination must abort, not
  silently return a partial result.

## Edge cases / when the rule does NOT apply

- Calls to singleton endpoints (get a specific workbook by id, get the current
  user): no pagination needed.

## See also

- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — owns REST API automation and content management
- [`./server-automate-with-connected-apps-and-pats-not-passwords.md`](./server-automate-with-connected-apps-and-pats-not-passwords.md) — the auth token in this example uses a PAT or Connected App

## Provenance

Codifies the pagination requirement from the Tableau Server REST API reference
documentation `[verify-at-build]`. The default page-size truncation is a
documented behaviour; scripts that miss it silently lose data.

---

_Last reviewed: 2026-06-05 by `claude`_
