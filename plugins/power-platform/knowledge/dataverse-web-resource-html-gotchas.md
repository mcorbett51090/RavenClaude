# HTML web resources in model-driven apps — the four gotchas that silently break a page

> **Last reviewed:** 2026-06-11. Sources: production debugging lesson (a GitHub Copilot session
> building Tesla-style HTML "workflow" web resources for a real customer model-driven app — BTCSI
> Insight), reconciled against learn.microsoft.com on 2026-06-11 (URLs inline). Refresh when the
> Dataverse web-resource URL contract, the `Xrm.WebApi` signature, or the `EntityDefinitions`
> metadata API change. Companion to the [`dataverse-web-resources`](../skills/dataverse-web-resources/SKILL.md)
> skill (the build-time playbook) and to [`model-driven-app-update-paths.md`](model-driven-app-update-paths.md)
> (the deploy-time playbook). Owned by `model-driven-engineer`.

An HTML web resource embedded in a model-driven app fails in ways that produce **no error** — a page
stuck on a loading spinner, every KPI reading `0`, or a `404` the portal swallows. Each of the four
gotchas below cost a real debugging session. None is obvious from the happy-path docs; three of them
are *silent*. Read this before building or reviewing another HTML/JS web resource page.

---

## Gotcha 1 — `%2F`-encoded slashes collapse the virtual folder, so relative `../` paths can break

**Symptom.** Page loads, shows `Loading…` forever, no error. The real cause: the page's `<script
src="../shared/utils.js">` never loaded, so the global it defined was `undefined`, so the page's
init/`route()` threw, so the loading `<div>` never cleared.

**Mechanism.** A web resource named `prefix_/flows/onsite_flow` is **served with its slashes
URL-encoded as `%2F`** — i.e. the browser sees the page at
`/WebResources/prefix_%2Fflows%2Fonsite_flow`. That whole encoded name is **one flat path segment**,
so a relative `../shared/utils.js` climbs from the wrong base and resolves to
`/WebResources/shared/utils.js` (which doesn't exist) instead of
`/WebResources/prefix_%2Fshared%2Futils.js`. The virtual "folder structure" the `/` characters
simulate only survives when the host serves the resource with **literal** slashes; once a sitemap or
host link carries the `%2F`-encoded form, `../` traversal is unreliable.

**This nuance matters — don't blindly "always use absolute paths."** Microsoft's official guidance is
the near-opposite of a naive absolute-path rule, so pick the fix deliberately:

- Microsoft **recommends relative URLs** between web resources (`../styles/styles.css`) and
  **explicitly warns against** root-anchored `/WebResources/<name>` paths: on a multi-org server a
  root-anchored path resolves against the user's **default** org, yielding "File Not Found" even when
  the resource exists in the org they're actually in. (Rare with today's per-environment URLs, but
  documented — don't treat hardcoded `/WebResources/...` as universally safe.)
  — <https://learn.microsoft.com/power-apps/developer/model-driven-apps/web-resources#reference-web-resources>

**The robust fix (preferred) — let the platform build the URL.** Use
`Xrm.Utility.getGlobalContext().getWebResourceUrl("prefix_/shared/utils.js")`, which returns the
correct relative URL *with the cache-busting version token* and sidesteps both the `%2F` trap and the
multi-org trap. (`getClientUrl()` gives you the environment root if you must compose a URL yourself.)
— <https://learn.microsoft.com/power-apps/developer/model-driven-apps/clientapi/reference/xrm-utility/getglobalcontext/getwebresourceurl>

**The pragmatic fix (what unblocked the live session) — a hardcoded absolute path** like
`/WebResources/prefix_%2Fshared%2Futils.js` works in a single-environment tenant. Note the explicit
`%2F`. Accept the documented multi-org caveat above; in a modern per-environment tenant it does not
bite, but record that you chose it.

**Decision rule.** Prefer `getWebResourceUrl()`. If you hardcode, encode the slashes (`%2F`) and only
do so when you control the environment URL. Never assume bare `../` works for a slash-named resource
loaded via the sitemap.

---

## Gotcha 2 — `Xrm.WebApi.retrieveMultipleRecords` wants the *logical* name (singular), not the entity-set name (plural)

**Symptom.** `The entity "prefix_onsites" cannot be found. Specify a valid query, and try again.`

**Mechanism.** `Xrm.WebApi.retrieveMultipleRecords(entityLogicalName, options)` takes the **table
logical name** — singular, e.g. `prefix_onsite` (the doc's own example is `account`, not `accounts`).
The plural entity-set name (`prefix_onsites`) is only for **raw `fetch`** calls against
`/api/data/v9.2/<entitySetName>`. Passing the set name to `Xrm.WebApi` is the entity-not-found above.
— <https://learn.microsoft.com/power-apps/developer/model-driven-apps/clientapi/reference/xrm-webapi/retrievemultiplerecords>

**Surface trap — the rule flips on Power Pages.** `Xrm.WebApi` (model-driven forms + HTML web
resources) → **logical** name. **Power Pages** `$pages.webAPI.retrieveMultipleRecords` →
**entity-set** name (`accounts`). Same-looking call, opposite argument. Don't copy a Power Pages
snippet into a model-driven web resource (or vice-versa) without flipping it.

**Helper pattern.** Have your data helper take the logical name and *derive* the plural for any raw
`fetch` fallback, only overriding when the plural isn't `logical + "s"`:

```javascript
ns.fetchMany = function (logicalName, select, filter, orderby, top, entitySetName) {
  var setName = entitySetName || logicalName + "s"; // override when pluralization is irregular
  var qs = buildQueryString(select, filter, orderby, top);
  // Xrm.WebApi path → LOGICAL name (singular)
  if (parent.Xrm) return parent.Xrm.WebApi.retrieveMultipleRecords(logicalName, qs);
  // raw fetch fallback → ENTITY SET name (plural)
  return fetch("/api/data/v9.2/" + setName + qs, { headers: { "OData-Version": "4.0" } });
};
```

---

## Gotcha 3 — verify field names against the live metadata API before writing `$select`; never trust a spec doc

**Symptom.** `Could not find a property named 'prefix_openingmeetingdate' on type
'Microsoft.Dynamics.CRM.prefix_onsite'.`

**Mechanism.** The page was built from a *design spec* describing an **intended future** schema, not
the **live** schema in the environment. Several assumed columns simply don't exist. Spec docs,
design docs, and an LLM's memory of "what fields this table probably has" are all untrustworthy for
**exact** column names — and a wrong name in `$select` fails the whole query.

**The discipline — query `EntityDefinitions` first, paginating `@odata.nextLink`:**

```
GET /api/data/v9.2/EntityDefinitions(LogicalName='prefix_onsite')/Attributes?$select=LogicalName,AttributeType
```

Attribute lists are paged: follow the `@odata.nextLink` in the response until it's absent, or you'll
silently miss columns past the first page. Only after confirming the real column set do you write
`$select`, the record-detail select, stage logic, checklists, and key-field references.

This is the Power Platform instance of the repo-wide **verify-the-load-bearing-assumption-before-a-
high-impact-activity** discipline — the same root lesson as
[`dataverse-solution-layering-active-dependency.md`](dataverse-solution-layering-active-dependency.md).
A field name written from a spec is an unverified premise; the metadata API is the one-call check that
costs seconds and saves a deploy-debug-redeploy loop.

---

## Gotcha 4 — `pac solution import` is slow; for sitemap-only changes, PATCH the sitemap over the Web API

**Symptom.** A `pac solution import` of an app solution containing BPFs, canvas apps, and web
resources runs **25+ minutes** [field-observed, not a documented SLA] and can *look* hung when it
isn't — tempting a fatal mid-import cancel.

**The lever — don't re-import a whole solution to change one navigation item.** For a **sitemap-only**
change, patch the sitemap directly:

1. `GET /api/data/v9.2/sitemaps({id})?$select=sitemapxml`
2. Inject the new `<Area>`/`<Group>`/`<SubArea>` block into the XML (before `</SiteMap>`).
3. `PATCH /api/data/v9.2/sitemaps({id})` with the updated `sitemapxml`.
4. `POST /api/data/v9.2/PublishAllXml` to publish.

**Sitemap `%2F` encoding (ties back to Gotcha 1).** A SubArea pointing at a slash-named web resource
must carry the **encoded** slashes in the XML:

```xml
<!-- web resource named:  prefix_/flows/onsite_flow  -->
<SubArea Id="onsiteFlow" Title="Onsite Flow"
         Url="/WebResources/prefix_%2Fflows%2Fonsite_flow" />
```

Literal slashes in the SubArea `Url` for a slash-named resource will not resolve. (For new work,
prefer the `$webresource:` directive where the XML supports it — it establishes a solution dependency
and avoids hand-encoding; the `/WebResources/...%2F...` form is the fallback when you're patching XML
directly. See the [`dataverse-web-resources`](../skills/dataverse-web-resources/SKILL.md) skill rule 9.)

**Two adjacent deploy tips from the same session.**

- **Publish:** a targeted `PublishXml` with a GUID-format `ParameterXml` returned `400`; `PublishAllXml`
  was the reliable fallback (already a house rule in the skill's `deployment.md`).
- **OData filter encoding:** build `$filter` query strings with a real URL-encoder
  (`urllib.parse.urlencode` / `encodeURIComponent`), never string concatenation — an unencoded space
  in a filter throws `InvalidURL` in Python `http.client` and equivalent failures elsewhere.

---

## One-line recall

> Slash-named web resources are served `%2F`-flattened (Gotcha 1 — prefer `getWebResourceUrl()`);
> `Xrm.WebApi` wants the **logical** name, Power Pages wants the **set** name (Gotcha 2); confirm every
> column against `EntityDefinitions/Attributes` before `$select`, paging `@odata.nextLink` (Gotcha 3);
> patch the sitemap over the Web API instead of a 25-minute solution import (Gotcha 4).
