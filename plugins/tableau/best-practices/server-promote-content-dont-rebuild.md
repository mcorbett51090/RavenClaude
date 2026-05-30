# Promote content dev→test→prod through a repeatable path; never hand-republish

**Status:** Absolute rule — hand-republishing into a governed prod environment breaks the audit chain and drifts connections. Content moves through a repeatable migration path.

**Domain:** Server / ALM

**Applies to:** `tableau`

---

## Why this exists

When you open prod, download the dev workbook, tweak the data connection, and re-publish by hand, three things silently break: the connection string drifts (you typed the prod server name, or didn't), the permissions don't come along (you re-grant from memory), and there's no record of *what* moved *when* — the audit chain is gone. The fix is to treat promotion like any other deployment: a repeatable path that carries the content and its connection remapping from dev→test→prod the same way every time. The **Content Migration Tool** runs a saved plan that remaps connections and paths; the **REST API** scripts it for CI; `tabcmd` handles simpler scripted publishes. Which one you pick is a decision-tree call — but "I'll just re-publish it" is never a leaf on that tree for the prod path.

## How to apply

Pick the repeatable method from the promotion tree and run it the same way every release. Example: a scripted REST promotion that publishes and remaps the connection per environment.

```bash
# Scripted promotion (REST API) — publish a workbook to PROD with a prod connection.
# Auth via a Connected App / PAT, NOT an interactive login.
TOKEN=$(curl -s -X POST "$PROD/api/3.x/auth/signin" \
  -d '{"credentials":{"personalAccessTokenName":"ci","personalAccessTokenSecret":"'"$PAT"'","site":{"contentUrl":"prod"}}}' \
  -H 'Content-Type: application/json' -H 'Accept: application/json' | jq -r .credentials.token)

# Publish workbook, OVERWRITE in place, point at the prod published data source:
curl -X POST "$PROD/api/3.x/sites/$SITE/workbooks?overwrite=true" \
  -H "X-Tableau-Auth: $TOKEN" \
  -F 'request_payload={"workbook":{"name":"FinanceKPI","project":{"id":"'"$PROD_PROJECT"'"}}};type=application/json' \
  -F 'tableau_workbook=@FinanceKPI.twbx;type=application/octet-stream'
# Connections are remapped to the prod published data source — not the dev one baked into the file.
```

**Do:**
- Use **Content Migration Tool** (saved plan) when promotion must remap connections/paths/field values.
- Use the **REST API** for headless CI/CD promotion; authenticate with a Connected App or PAT, not a person.
- Remap the connection to the **target environment's published data source** as part of the move.
- Version the migration plan / promotion script in source control so the path is reviewable.

**Don't:**
- Download-from-dev / re-publish-to-prod by hand for governed content — that drifts connections and drops permissions.
- Hard-code one environment's server name in the promotion script — parameterize per env.
- Assume permissions travel with a manual republish — they don't.

## Edge cases / when the rule does NOT apply

- **One-time, non-prod moves** — a manual download/publish is acceptable for a low-stakes move that never touches the governed prod path.
- **`tabcmd` availability differs Cloud vs Server** `[verify-at-build]` — confirm the target platform before scripting with `tabcmd`.
- **CMT is an add-on** — Content Migration Tool requires Advanced Management / Server Management `[verify-at-build]`; without it, the REST API is the repeatable path.

## See also

- [`./server-publish-with-separated-data-sources.md`](./server-publish-with-separated-data-sources.md) — separated data sources are what let connections remap cleanly on promotion
- [`./embed-connected-apps-jwt-not-trusted-tickets.md`](./embed-connected-apps-jwt-not-trusted-tickets.md) — the same Connected App auth used for headless promotion
- [`../knowledge/governance-embedding-decision-trees.md`](../knowledge/governance-embedding-decision-trees.md) — `## Decision Tree: Content promotion`
- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — owns this rule
- Tableau Help, "Tableau Content Migration Tool" + "REST API publish workbook" `[verify-at-build]`

## Provenance

Codifies constitution house opinion #7 ("Promote, don't rebuild") and the `tableau-admin` discipline #3. Grounded in the CMT / REST API / `tabcmd` promotion paths — re-verify add-on requirements and `tabcmd` Cloud-vs-Server availability before quoting.

---

_Last reviewed: 2026-05-30 by `claude`_
