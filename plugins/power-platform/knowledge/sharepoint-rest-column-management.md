# SharePoint REST API — browser-console column management (when programmatic auth is blocked)

> **Last reviewed:** 2026-07-08. Source: live iterative testing across 4 SharePoint document
> libraries in a real engagement, reconciled against Microsoft Learn on 2026-07-08 (URLs
> inline). Refresh when the SharePoint Online `_api/web/lists/.../fields` contract, the
> `FieldType` / `DateTimeFieldFormatType` enums, or the form-digest / MERGE-tunnel semantics change.
> Companion to [`data-store-dataverse-vs-sharepoint-vs-teams`](../best-practices/data-store-dataverse-vs-sharepoint-vs-teams.md)
> (when SharePoint is the right store) and [`datastore-and-integration-decision-trees`](datastore-and-integration-decision-trees.md)
> (routing). The [`flow-engineer`](../agents/flow-engineer.md) agent owns the Power-Automate side of
> the InternalName contract this doc is about.

## When this applies

Some organizations block **all programmatic auth** to SharePoint by policy — Graph API, MSAL,
service principals, app-only tokens. When bulk column work is needed anyway, the authorized fallback
is **JavaScript run from the browser console** on the SharePoint site, executing as the signed-in
user against the SharePoint REST endpoint (`_api/`). Reach for this pattern when:

- You must **create, rename, or delete columns** in SharePoint document libraries in bulk.
- Programmatic auth is unavailable (policy, or bootstrapping *before* any flow/app exists).
- A Power Automate flow can't do it yet — e.g. you're fixing a wrong column `InternalName` that a
  flow now depends on.

> ⚠️ **`InternalName` is permanent after creation.** The only fix for a wrong `InternalName` is
> **delete + recreate**. Get it right the first time — see the two-step pattern below.

> **This is a fallback, not the default.** Where programmatic auth *is* allowed, prefer Microsoft
> Graph (`/sites/{id}/lists/{id}/columns`) or PnP. This doc exists for the policy-blocked case.

---

## Environment setup

**Run from the site home page, never a library URL.** Relative `_api/` paths resolve incorrectly
from a library/Forms page, so use absolute URLs throughout and load the console on:

```
✅ https://tenant.sharepoint.com/sites/SITE_NAME
❌ https://tenant.sharepoint.com/sites/SITE_NAME/Shared%20Documents/Forms/AllItems.aspx
```

**Use a prefixed variable name.** `window.SITE` may already exist in the SharePoint page context, so
don't shadow it:

```js
const _SP_SITE = "https://tenant.sharepoint.com/sites/SITE_NAME"; // ← change per environment
```

**`GetByTitle` takes the display name, NOT the URL slug.**

```js
GetByTitle("Filing Intake"); // ✅ matches the list Title property
GetByTitle("filingintake"); // ❌ URL path, not Title → 404
```

Verify the display name before scripting — list every library's Title + server-relative URL:

```js
const r = await fetch(
  `${_SP_SITE}/_api/web/lists?$select=Title,RootFolder/ServerRelativeUrl&$expand=RootFolder`,
  { headers: { Accept: "application/json;odata=verbose" } },
);
(await r.json()).d.results.forEach((l) => console.log(l.Title, l.RootFolder.ServerRelativeUrl));
```

---

## Digest token (required for every write)

Fetch once at script start. Valid ~30 minutes on SharePoint Online — enough for all column
operations in a single run.

```js
const dR = await fetch(`${_SP_SITE}/_api/contextinfo`, {
  method: "POST",
  headers: { Accept: "application/json;odata=verbose" },
});
const digest = (await dR.json()).d.GetContextWebInformation.FormDigestValue;
```

---

## Creating a column with a controlled `InternalName` (two-step pattern)

SharePoint derives `InternalName` from `Title` **at creation time**, and it is **permanent**. To
control the `InternalName`:

1. **Create** with `Title = InternalName` (no spaces, PascalCase) — SP preserves it exactly.
2. **MERGE-update** the display `Title` to the spaced human-readable name immediately after (a
   MERGE, _not_ an HTTP `PATCH` — see [PATCH (MERGE)](#patch-merge--the-correct-method) below).

```js
// Step 1 — Create: Title = InternalName (e.g. "EntityName", no spaces)
const cr = await fetch(`${listUrl}/fields`, {
  method: "POST",
  headers: {
    Accept: "application/json;odata=verbose",
    "Content-Type": "application/json;odata=verbose",
    "X-RequestDigest": digest,
  },
  body: JSON.stringify({
    __metadata: { type: "SP.FieldText" },
    Title: "EntityName", // ← becomes the permanent InternalName
    FieldTypeKind: 2,
    MaxLength: 255,
  }),
});
const field = (await cr.json()).d;
const fieldId = field.Id;
const internalName = field.InternalName; // verify === 'EntityName'

// Step 2 — Update the display Title (MERGE)
await fetch(`${listUrl}/fields/getById('${fieldId}')`, {
  method: "POST",
  headers: {
    Accept: "application/json;odata=verbose",
    "Content-Type": "application/json;odata=verbose",
    "X-RequestDigest": digest,
    "X-HTTP-Method": "MERGE",
    "If-Match": "*",
  },
  body: JSON.stringify({
    __metadata: { type: "SP.FieldText" },
    Title: "Entity Name", // ← human display name with spaces
  }),
});
```

> If `internalName !== requested name`, SP appended a suffix (usually `0`) because a hidden system
> field already owns that name — see [the InternalName suffix gotcha](#internalname-suffix-gotcha).

---

## PATCH (MERGE) — the correct method

| ❌ Wrong                                     | ✅ Correct                                     |
| -------------------------------------------- | --------------------------------------------- |
| `method: 'PATCH'` + `X-HTTP-Method: MERGE`   | `method: 'POST'` + `X-HTTP-Method: MERGE`     |
| `/fields('guid')`                            | `/fields/getById('guid')`                     |
| `'IF-MATCH': '*'`                            | `'If-Match': '*'` (RFC 7230 canonical casing) |

`X-HTTP-Method: MERGE` is an HTTP tunnel designed for **`POST`** only. Pairing it with a real
`PATCH` verb is self-contradictory and returns `400` on strict SharePoint configurations.

---

## Field-type reference

Every value in the two `FieldTypeKind` / enum tables below is corroborated by the Microsoft Learn
[`FieldType` enum](https://learn.microsoft.com/dotnet/api/microsoft.sharepoint.client.fieldtype) and
the [`DateTimeFieldFormatType` enum](https://learn.microsoft.com/dotnet/api/microsoft.sharepoint.client.datetimefieldformattype).

| Type             | `__metadata.type`      | `FieldTypeKind` | Notes                                                            |
| ---------------- | ---------------------- | --------------- | ---------------------------------------------------------------- |
| Single line text | `SP.FieldText`         | `2`             | Add `MaxLength: 255`.                                            |
| Multi-line text  | `SP.FieldMultiLineText`| `3`             |                                                                  |
| Date/Time        | `SP.FieldDateTime`     | `4`             | Use `DisplayFormat` for DateOnly vs DateTime (see below).        |
| Choice           | `SP.FieldChoice`       | `6`             | Add `Choices: { results: ['A','B','C'] }`.                       |
| Yes/No           | `SP.FieldBoolean`      | `8`             |                                                                  |
| Number           | `SP.FieldNumber`       | `9`             | Use `DisplayFormat` for decimals — there is **no** `Decimals`.   |

### `SP.FieldDateTime` — `DisplayFormat` enum

```
0 = DateOnly   (date picker, no time)   ← use for period-end, due-date, date-of-birth
1 = DateTime   (date + time picker)
```

> ⚠️ **Common mistake:** `col.dateOnly ? 1 : 0` is **inverted**. Correct: `col.dateOnly ? 0 : 1`
> (DateOnly is `0`, per the Learn `DateTimeFieldFormatType` enum).

```js
fieldBody = {
  __metadata: { type: "SP.FieldDateTime" },
  Title: col.name,
  FieldTypeKind: 4,
  DisplayFormat: col.dateOnly ? 0 : 1, // 0 = DateOnly, 1 = DateTime
};
```

### `SP.FieldNumber` — `DisplayFormat` (decimal places)

`SP.FieldNumber.DisplayFormat` is an **Int32** property
([Microsoft Learn](https://learn.microsoft.com/dotnet/api/microsoft.sharepoint.client.fieldnumber.displayformat)).
The integer → decimal-places mapping below is **live-validated (2026-07-08)** — Learn documents the
property type but does not publish the integer mapping:

```
-1 = Automatic (SP default — shows all significant digits)
 0 = Auto
 1 = 0 decimal places
 2 = 1 decimal place
 3 = 2 decimal places   ← e.g. a confidence score
 4 = 3 decimal places
 5 = 4 decimal places
```

> ⚠️ **`SP.FieldNumber` has no `Decimals` property in the REST API.** Passing it returns
> `400 The property 'Decimals' does not exist on type 'SP.FieldNumber'`. Use `DisplayFormat`.
>
> **SP REST vs Graph — don't cross the wires:** the Microsoft **Graph**
> [`numberColumn`](https://learn.microsoft.com/graph/api/resources/numbercolumn) resource uses a
> string `decimalPlaces` (`automatic | none | one | two | … | five`). That is the *Graph* shape, not
> the SharePoint REST `_api/` shape this doc uses — the SP REST field is the integer `DisplayFormat`
> above. Mixing the two is a common source of `400`s.

```js
// For 2 decimal places:
fieldBody = {
  __metadata: { type: "SP.FieldNumber" },
  Title: col.name,
  FieldTypeKind: 9,
  DisplayFormat: 3, // 2 decimal places
};
```

---

## `InternalName` suffix gotcha

SP silently appends `0` (or higher) to `InternalName` if a hidden system field already owns that
name. The create call still returns `200`, but `field.InternalName` comes back as e.g.
`ReviewStatus0` instead of `ReviewStatus`.

**Detection — always check the returned `InternalName`:**

```js
const internalName = (await cr.json()).d.InternalName;
if (internalName !== col.name) {
  console.warn(`⚠️  Expected ${col.name} but got ${internalName} — SP appended a suffix`);
  // The field IS created — just under a different InternalName.
  // Any Power Automate flow that writes to this column MUST use the suffixed name.
}
```

**Known system conflicts in SP Online document libraries:**

- `ReviewStatus` → becomes `ReviewStatus0` (hidden approval field present in all libraries).
- A field name starting with a **lowercase** letter gets hex-encoded (e.g. `mrz1` →
  `_x006d_rz1`). **Always use PascalCase** to avoid this.

**When a suffix occurs:**

- The field is still created and usable.
- Update the display Title using the returned `fieldId`.
- Update **all** Power Automate flow references from `ReviewStatus` → `ReviewStatus0`.
- Record the suffix in your column inventory.

---

## Data-safe delete pattern

Before deleting any column, confirm both:

1. `AllowDeletion` is not `false` (a sealed field is part of a content type — skip it silently).
2. The column is **empty across all list items**.

```js
// Fetch fields with the AllowDeletion flag
const fieldsResp = await fetch(
  `${listUrl}/fields?$select=InternalName,Title,TypeAsString,AllowDeletion&$filter=Hidden eq false and ReadOnlyField eq false`,
  { headers: { Accept: "application/json;odata=verbose" } },
);
const fields = (await fieldsResp.json()).d.results;

// Deletable candidates: not on your keep-list, not sealed, not a system field
const candidates = fields.filter(
  (f) => !KEEP.has(f.InternalName) && f.AllowDeletion !== false && !f.InternalName.startsWith("_"),
);
const candidateNames = candidates.map((f) => f.InternalName);

// Data check — page via __next (odata=verbose), $top=5000 per page
let allItems = [],
  url = `${listUrl}/items?$select=${candidateNames.join(",")}&$top=5000`;
while (url) {
  const r = await fetch(url, { headers: { Accept: "application/json;odata=verbose" } });
  const body = await r.json();
  allItems = allItems.concat(body.d?.results ?? []);
  url = body.d?.__next ?? null;
}

// Only delete truly empty columns
const safeToDelete = candidates.filter(
  (f) => !allItems.some((item) => item[f.InternalName] !== null && item[f.InternalName] !== ""),
);

for (const f of safeToDelete) {
  await fetch(`${listUrl}/fields/getByInternalNameOrTitle('${f.InternalName}')`, {
    method: "POST",
    headers: { "X-RequestDigest": digest, "X-HTTP-Method": "DELETE", "If-Match": "*" },
  });
  await _delay(600); // rate-limit
}
```

---

## Full script template

Change `_SP_SITE` and `LIBRARY` at the top; everything else is reusable. The `columns` array is an
illustrative worked example — replace it with your own.

```js
(async () => {
  const _SP_SITE = "https://tenant.sharepoint.com/sites/SITE_NAME"; // ← change per env
  const LIBRARY = "Filing Intake"; // ← display name, NOT the URL slug
  const _delay = (ms) => new Promise((r) => setTimeout(r, ms));

  // 1. Digest
  const dR = await fetch(`${_SP_SITE}/_api/contextinfo`, {
    method: "POST",
    headers: { Accept: "application/json;odata=verbose" },
  });
  const digest = (await dR.json()).d.GetContextWebInformation.FormDigestValue;
  console.log("✅ Got digest");

  const listUrl = `${_SP_SITE}/_api/web/lists/GetByTitle('${encodeURIComponent(LIBRARY)}')`;

  // 2. Existing fields (skip already-present)
  const eR = await fetch(`${listUrl}/fields?$select=InternalName&$filter=Hidden eq false`, {
    headers: { Accept: "application/json;odata=verbose" },
  });
  if (!eR.ok) {
    console.error(`❌ Library not found (${eR.status}) — check the display name`);
    return;
  }
  const existing = new Set((await eR.json()).d.results.map((f) => f.InternalName));

  // Worked example — replace with your own columns.
  const columns = [
    { name: "EntityName", title: "Entity Name", type: "Text" },
    { name: "PeriodEnd", title: "Period End", type: "DateTime", dateOnly: true },
    { name: "DueDate", title: "Due Date", type: "DateTime", dateOnly: true },
    { name: "DaysOverdue", title: "Days Overdue", type: "Number" },
    { name: "ConfidenceScore", title: "Confidence Score", type: "Number", decimals: 2 },
  ];

  let created = 0,
    skipped = 0,
    failed = 0;

  for (const col of columns) {
    if (existing.has(col.name)) {
      console.log(`  ⏭️  ${col.name}`);
      skipped++;
      continue;
    }

    // Build the field body
    let fieldBody;
    if (col.type === "DateTime") {
      fieldBody = {
        __metadata: { type: "SP.FieldDateTime" },
        Title: col.name,
        FieldTypeKind: 4,
        DisplayFormat: col.dateOnly ? 0 : 1, // 0 = DateOnly, 1 = DateTime
      };
    } else if (col.type === "Number") {
      fieldBody = { __metadata: { type: "SP.FieldNumber" }, Title: col.name, FieldTypeKind: 9 };
      if (col.decimals != null) fieldBody.DisplayFormat = col.decimals + 1; // 3 = 2dp
    } else {
      fieldBody = {
        __metadata: { type: "SP.FieldText" },
        Title: col.name,
        FieldTypeKind: 2,
        MaxLength: 255,
      };
    }

    // Create (Title = InternalName)
    const cr = await fetch(`${listUrl}/fields`, {
      method: "POST",
      headers: {
        Accept: "application/json;odata=verbose",
        "Content-Type": "application/json;odata=verbose",
        "X-RequestDigest": digest,
      },
      body: JSON.stringify(fieldBody),
    });
    if (!cr.ok) {
      console.error(`  ❌ ${col.name} ${cr.status}: ${(await cr.text()).substring(0, 200)}`);
      failed++;
      await _delay(500);
      continue;
    }
    const cd = (await cr.json()).d;
    const internalName = cd.InternalName;
    const fieldId = cd.Id;

    // Suffix / mismatch handling — the field IS created regardless of the returned
    // InternalName (suffix `0` or higher, or a hex-encoded lowercase/system conflict),
    // so warn but still proceed to set the display Title. Matches the "suffix gotcha" section.
    if (internalName !== col.name) {
      console.warn(
        `  ⚠️  ${col.name} → created as "${internalName}" (SP appended a suffix or hex-encoded a conflict) — update PA flow refs to this exact name`,
      );
    }

    // Update the display Title (concrete SP type required for MERGE)
    if (col.title !== col.name) {
      const spType =
        col.type === "DateTime"
          ? "SP.FieldDateTime"
          : col.type === "Number"
            ? "SP.FieldNumber"
            : "SP.FieldText";
      await fetch(`${listUrl}/fields/getById('${fieldId}')`, {
        method: "POST",
        headers: {
          Accept: "application/json;odata=verbose",
          "Content-Type": "application/json;odata=verbose",
          "X-RequestDigest": digest,
          "X-HTTP-Method": "MERGE",
          "If-Match": "*",
        },
        body: JSON.stringify({ __metadata: { type: spType }, Title: col.title }),
      });
    }

    console.log(`  ✅ ${internalName} → "${col.title}"`);
    created++;
    await _delay(600); // rate-limit: SP Online throttles ~100 ops/min
  }

  console.log(`\n✅ Done — Created: ${created}, Skipped: ${skipped}, Failed: ${failed}`);
})();
```

---

## Multi-environment pattern

Change only `_SP_SITE` at the top of the script per environment — no other edits needed. Gate the
production run behind an approval step.

```
DEV:  https://tenant.sharepoint.com/sites/SITE_NAME_DEV
TEST: https://tenant.sharepoint.com/sites/SITE_NAME_TEST
PROD: https://tenant.sharepoint.com/sites/SITE_NAME       (requires an approval gate)
```

---

## Verification script

Run before any create/delete to discover display names and the current column state:

```js
(async () => {
  const _SP_SITE = "https://tenant.sharepoint.com/sites/SITE_NAME";
  const LIBS = ["Filing Intake", "Balance Sheet", "Income Statement"]; // your libraries
  for (const lib of LIBS) {
    const r = await fetch(
      `${_SP_SITE}/_api/web/lists/GetByTitle('${encodeURIComponent(lib)}')/fields?$select=InternalName,Title,TypeAsString&$filter=Hidden eq false and ReadOnlyField eq false`,
      { headers: { Accept: "application/json;odata=verbose" } },
    );
    if (!r.ok) {
      console.log(`${lib}: ${r.status}`);
      continue;
    }
    const fields = (await r.json()).d.results.filter((f) => !f.InternalName.startsWith("_"));
    console.log(`\n${lib} (${fields.length} custom):`);
    fields.forEach((f) => console.log(`  ${f.InternalName} (${f.TypeAsString}) → "${f.Title}"`));
  }
})();
```

---

## Common errors and fixes

| Error                                                    | Cause                                                            | Fix                                                                       |
| -------------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `404 on GetByTitle`                                      | Used the URL slug instead of the display name                   | Use the display name (`Filing Intake`, not `filingintake`)                |
| `500 Cannot add a field without a Display Name`          | Passed `SchemaXml` in the JSON body (SP ignores it)             | Use the `{ __metadata, Title, FieldTypeKind }` pattern                    |
| `404 Cannot find resource addfieldasxml`                 | `/fields/addfieldasxml` exists only at web level, not list level | Use `POST /fields` with a JSON body                                       |
| `400 The property 'Decimals' does not exist`             | `Decimals` is not a valid `SP.FieldNumber` property             | Use `DisplayFormat` (3 = 2dp) instead                                     |
| `InternalName` `ReviewStatus0` when requesting `ReviewStatus` | Hidden SP system field conflict — suffix appended          | Accept the suffix; update PA flow refs to `ReviewStatus0`                 |
| `method: PATCH` + `X-HTTP-Method: MERGE` → `400`         | The MERGE tunnel works only on `POST`                           | Use `method: POST` + `X-HTTP-Method: MERGE`                               |
| Flow PATCH returns `200` but the SP column stays null    | The `InternalName` in the flow body doesn't match the real one  | Verify `InternalName`s with the verification script; SP silently discards unknown keys |
| Script run from a library URL → wrong `_api` base        | Relative paths resolve incorrectly off the home page            | Run the console on the **site home page** only                            |
