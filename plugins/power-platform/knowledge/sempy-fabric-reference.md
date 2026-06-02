# sempy.fabric — Semantic Link in Fabric notebooks (reference)

> **Last reviewed:** 2026-06-02. Source: [Microsoft Learn — `sempy.fabric` Package reference](https://learn.microsoft.com/en-us/python/api/semantic-link-sempy/sempy.fabric?view=semantic-link-python), full page distilled 2026-06-02 (the page is ~1,800 lines — the inventory in §3–§5 mirrors every function and class section listed there). Refresh when (a) Microsoft publishes a new `semantic-link-python` view (the URL's `view=` parameter changes), (b) a function in §3 is deprecated or removed from the docs, or (c) `sempy.fabric.set_service_principal()` semantics for out-of-notebook use change.
>
> **Claim-grounding note.** Every function / class / submodule name in this file was lifted verbatim from the Microsoft Learn API reference at the date above — quote verbatim, do not paraphrase. Parameter defaults and exception types were taken from the same source. Where this file calls out a behavior (Direct Lake handling, refresh policy semantics, ReadWrite permission requirement), the source language is Microsoft's; rephrasings are flagged. If an item is **not** in `sempy.fabric` and you need it, check the companion submodules in §5 *before* concluding it doesn't exist — many semantic-model and lakehouse ops live in `sempy.fabric.semantic_model` and `sempy.fabric.lakehouse`.

---

## 1. When to read this file

Read this file when an engagement requires Python-based interaction with a Power BI / Fabric semantic model or workspace, especially **inside a Fabric notebook** where Semantic Link is already authenticated as the notebook identity.

Use sempy.fabric for:

- **Inspecting a semantic model from a notebook** — list tables / columns / measures / relationships; run DAX; export results to a DataFrame.
- **Authoring or modifying a semantic model programmatically** — TOM (Tabular Object Model) editing via `connect_semantic_model()`; TMSL via `execute_tmsl()`.
- **Orchestrating dataset refresh** — kick off async refresh, poll for completion, target specific tables / partitions.
- **Workspace / item enumeration** — `list_workspaces()`, `list_items()`, lakehouse / report / dataflow inventories.
- **Performance + health checks** — `model_memory_analyzer()` (Vertipaq), `run_model_bpa()` (Best Practice Analyzer), `create_trace_connection()` for ad-hoc tracing.
- **Direct Lake / OneLake workflows** — `read_table(mode='onelake')` for spark / pandas ingestion of lakehouse-backed delta tables.

Do **not** use sempy.fabric for:

- **Authoring report files** (`visual.json`, `page.json`, `report.json`). For that, see the companion [`pbir-enhanced-reference.md`](pbir-enhanced-reference.md) (build) and [`pbir-enhanced-report-loading.md`](pbir-enhanced-report-loading.md) (debug). sempy's `sempy.fabric.report` submodule lets you list / clone / rebind reports but is not a PBIR file editor.
- **Tenant administration** that requires Power BI admin REST APIs (Portal / Capacity admin). sempy.fabric exposes user-scoped operations; `sempy.fabric.admin` is partial. Tenant-scope work routes to `power-platform-admin` via the Power BI REST API directly.
- **Out-of-notebook scripting that needs a real `.pbix` file open.** For that, prefer the bundled `powerbi-editor` (pbix-mcp) MCP — see [`../CLAUDE.md`](../CLAUDE.md) §9.

**Decision priors:**

- Inside a Fabric notebook → reach for `sempy.fabric` first; auth is implicit.
- Outside a Fabric notebook (a regular Python script / CI job) → still works, but you must `pip install semantic-link-sempy` and supply credentials via `set_service_principal()` or an Azure `TokenCredential`. The function surface is the same.
- Need to edit the actual `.pbix` / `.pbit` binary → `powerbi-editor` MCP, not sempy.
- Need to author Enhanced report JSON files → write the files directly, guided by [`pbir-enhanced-reference.md`](pbir-enhanced-reference.md).

---

## 2. Authentication

**Inside a Fabric notebook (the happy path):** sempy.fabric uses the notebook's built-in identity automatically. Every function takes an optional `credential: TokenCredential | None = None` — leaving it as `None` (the default) picks up the notebook execution context. No MSAL, no token shuffling.

**Outside a notebook — service principal:**

```python
from sempy.fabric import set_service_principal, list_workspaces

with set_service_principal(
    tenant_id="<tenant-id>",
    client_id="<sp-app-id>",
    client_secret="<sp-secret>",
):
    ws = list_workspaces()
```

`set_service_principal()` is a context manager — credentials apply only inside the `with` block.

**Outside a notebook — Azure `TokenCredential`:** pass an explicit credential (e.g. `azure.identity.DefaultAzureCredential`) to any function that accepts the `credential=` kwarg.

**ReadWrite vs read-only.** Many functions default to read-only (XMLA mode). To edit models with TOM or run write XMLA, set `readonly=False` (where the parameter exists) and ensure your principal has **ReadWrite** access on the semantic model. Functions that *require* ReadWrite are explicitly flagged in the Microsoft docs — see §7.

**Out-of-notebook caveat (security review trigger).** A script outside Fabric handling service-principal secrets is exactly the surface that escalates to `ravenclaude-core/security-reviewer` per the team constitution. Don't commit the secret; resolve from a secret manager or Azure Key Vault at runtime.

---

## 3. Top-level functions, by purpose

Every function below is exposed directly at `sempy.fabric.<name>` and takes a `credential: TokenCredential | None = None` kwarg unless noted. Workspace-targeting functions also take `workspace: str | UUID | None = None` (when `None`, uses the notebook's attached workspace).

### 3.1 Workspace operations

| Function | Returns | When |
|---|---|---|
| `create_workspace(display_name, capacity_id=None, description=None)` | workspace ID (`str`) | Provisioning a new Fabric workspace |
| `list_workspaces(filter=None, top=None, skip=None, roles=None, endpoint=None)` | `DataFrame` | Inventory; supports `endpoint=Literal['powerbi','fabric']` |
| `delete_workspace(workspace)` | — | Tear-down |
| `resolve_workspace_id(workspace=None)` | `str` (UUID) | Name → ID lookup |
| `resolve_workspace_name(workspace=None)` | `str` | ID → name lookup |
| `resolve_workspace_name_and_id(workspace=None)` | `Tuple[str, str]` | Both at once |
| `get_sku_size(workspace=None)` | `str` | Fetch SKU / capacity size |
| `get_notebook_workspace_id()` | `str` | Current notebook's parent workspace ID |
| `get_workspace_id()` | `str` | Current notebook OR attached lakehouse workspace ID |

### 3.2 Semantic-model (dataset) — metadata + query

| Function | Returns | When |
|---|---|---|
| `evaluate_dax(dataset, dax_string, workspace=None, verbose=0, num_rows=None, role=None, effective_user_name=None, use_readwrite_connection=False)` | `FabricDataFrame` | Ad-hoc DAX query with results as DataFrame |
| `evaluate_measure(dataset, measure, groupby_columns=None, filters=None, fully_qualified_columns=None, num_rows=None, use_xmla=False, workspace=None, verbose=0, use_readwrite_connection=False)` | `FabricDataFrame` | Compute a measure with optional `groupby_columns` and `filters` |
| `read_table(dataset, table, fully_qualified_columns=False, num_rows=None, multiindex_hierarchies=False, mode='xmla', onelake_import_method=None, workspace=None, verbose=0)` | `FabricDataFrame` | Read a table into a DataFrame. `mode` is `'xmla'`, `'rest'`, or `'onelake'`. `onelake_import_method` is `'spark'` or `'pandas'` when `mode='onelake'`. |
| `list_datasets(workspace=None, mode='xmla', additional_xmla_properties=None, endpoint=None)` | `DataFrame` | Inventory; `mode='rest'` is read-only and doesn't need ReadWrite |
| `resolve_dataset_id(dataset_name, workspace=None)` | `str` | Name → ID |
| `resolve_dataset_name(dataset_id, workspace=None)` | `str` | ID → name |
| `resolve_dataset_name_and_id(dataset, workspace=None)` | `Tuple[str, str]` | Both |
| `list_tables(dataset, include_columns=False, include_partitions=False, extended=False, advanced=False, additional_xmla_properties=None, workspace=None, include_internal=False)` | `DataFrame` | `advanced=True` returns Vertipaq stats |
| `list_columns(dataset, table=None, extended=False, additional_xmla_properties=None, workspace=None)` | `DataFrame` | Column audit |
| `list_measures(dataset, additional_xmla_properties=None, workspace=None)` | `DataFrame` | All measures |
| `list_relationships(dataset, extended=False, additional_xmla_properties=None, calculate_missing_rows=False, workspace=None)` | `DataFrame` | `calculate_missing_rows=True` detects cardinality violations |
| `list_hierarchies(dataset, extended=False, additional_xmla_properties=None, workspace=None)` | `DataFrame` | Hierarchies + levels |
| `list_partitions(dataset, table=None, extended=False, additional_xmla_properties=None, workspace=None)` | `DataFrame` | For incremental refresh / aggregations |
| `list_datasources(dataset, additional_xmla_properties=None, workspace=None)` | `DataFrame` | Data-source connections |
| `list_expressions(dataset, additional_xmla_properties=None, workspace=None)` | `DataFrame` | M queries + named DAX expressions |
| `list_annotations(dataset, additional_xmla_properties=None, workspace=None)` | `DataFrame` | Model annotations |
| `list_perspectives(dataset, additional_xmla_properties=None, workspace=None)` | `DataFrame` | Custom views |
| `list_calculation_items(dataset, additional_xmla_properties=None, workspace=None)` | `DataFrame` | Calculation-group items |
| `list_translations(dataset, additional_xmla_properties=None, workspace=None)` | `DataFrame` | Multilingual models |
| `get_tmsl(dataset, workspace=None)` | `str` (TMSL JSON) | Retrieve TMSL definition |
| `list_roles(dataset, include_members=False, additional_xmla_properties=None, workspace=None)` | `DataFrame` | Security roles, optionally with members |
| `get_row_level_security_permissions(dataset, additional_xmla_properties=None, workspace=None)` | `DataFrame` | RLS filter expressions per table per role |

### 3.3 Refresh / async

| Function | Returns | When |
|---|---|---|
| `refresh_dataset(dataset, workspace=None, refresh_type='automatic', max_parallelism=10, commit_mode='transactional', retry_count=0, objects=None, apply_refresh_policy=True, effective_date=<today>, verbose=0)` | refresh request ID (`str`) | Kick off async refresh, optionally scoped to specific tables / partitions |
| `list_refresh_requests(dataset, workspace=None, top_n=None)` | `DataFrame` | Refresh history + status |
| `get_refresh_execution_details(dataset, refresh_request_id, workspace=None)` | `RefreshExecutionDetails` | Poll a single refresh's status, start / end / errors |

### 3.4 TOM (Tabular Object Model)

| Function | Returns | When |
|---|---|---|
| `connect_semantic_model(dataset, readonly=True, workspace=None, verbose=0)` | `Iterator[TOMWrapper]` (context manager) | Read or write model edits via TOM. `with` block recommended. |
| `create_tom_server(dataset=None, readonly=True, workspace=None)` | `Microsoft.AnalysisServices.Tabular.Server` (.NET object) | Lower-level — talk to multiple datasets on one server connection |
| `execute_tmsl(script, refresh_tom_cache=True, workspace=None)` | — | Execute TMSL script for model modifications |
| `execute_xmla(dataset, xmla_command, workspace=None, use_readwrite_connection=False)` | `int` (rows affected) | Execute XMLA commands (cache clear, `ProcessAdd`, etc.) |
| `refresh_tom_cache(workspace=None)` | — | Refresh sempy's TOM cache after external changes |
| `get_model_calc_dependencies(dataset, workspace=None)` | `Iterator[ModelCalcDependencies]` | Calculated-object dependency graph |

### 3.5 Analysis + diagnostics

| Function | Returns | When |
|---|---|---|
| `model_memory_analyzer(dataset, workspace=None, export='html', return_dataframe=False)` | `Dict[str, DataFrame]` or `None` | Vertipaq compression + memory analysis. `export` is `'html'`, `'table'`, `'zip'`, or `None`. |
| `run_model_bpa(dataset, workspace=None, export='html', return_dataframe=False, language=None)` | `DataFrame` or `None` | Best Practice Analyzer scan; `language` translates findings |
| `create_trace_connection(dataset, workspace=None)` | `TraceConnection` | Open an Analysis Services trace for perf debugging |

### 3.6 Data validation + relationships

| Function | Returns | When |
|---|---|---|
| `list_relationship_violations(tables, missing_key_errors='raise', coverage_threshold=1.0, n_keys=10)` | `DataFrame` | Validate cardinality in data; report missing keys |
| `plot_relationships(tables, include_columns='keys', missing_key_errors='raise', *, graph_attributes=None)` | `graphviz.Digraph` | Visual relationship graph |

### 3.7 Reports, dataflows, gateways, capacities, apps

| Function | Returns | When |
|---|---|---|
| `list_reports(workspace=None, endpoint=None)` | `DataFrame` | Reports in workspace |
| `list_dataflows(workspace=None, endpoint=None)` | `DataFrame` | Dataflows |
| `list_dataflow_storage_accounts()` | `DataFrame` | Dataflow storage |
| `list_gateways()` | `DataFrame` | On-premises gateways |
| `list_capacities()` | `DataFrame` | Fabric capacities |
| `list_apps()` | `DataFrame` | Power BI apps |

### 3.8 Lakehouse, notebook, folder, item — Fabric workspace items

| Function | Returns | When |
|---|---|---|
| `create_lakehouse(display_name, description=None, workspace=None, folder=None, enable_schema=False, lro_config=None, **kwargs)` | lakehouse ID | Create a Fabric lakehouse |
| `get_lakehouse_id()` | `str` | Lakehouse attached to current notebook |
| `create_notebook(display_name, description=None, content=None, default_lakehouse=None, default_lakehouse_workspace=None, workspace=None, folder=None, lro_config=None, **kwargs)` | notebook ID | Create a notebook |
| `run_notebook_job(notebook_id, workspace=None, lro_config=None, **kwargs)` | job ID | Async notebook execution |
| `get_artifact_id()` | `str` | Current notebook / artifact ID |
| `create_folder(folder, workspace=None, recursive=False)` | folder ID | **Experimental.** Folder hierarchy |
| `list_folders(workspace=None, root_folder=None, recursive=True, extend_folder_path=False)` | `DataFrame` | **Experimental.** |
| `delete_folder(folder, workspace=None)` | — | **Experimental.** |
| `move_folder(folder, target_folder=None, workspace=None)` | — | **Experimental.** |
| `rename_folder(folder, new_folder_name, workspace=None)` | — | **Experimental.** |
| `resolve_folder_id(folder, workspace=None)` | `str` | **Experimental.** |
| `resolve_folder_path(folder, workspace=None)` | `str` | **Experimental.** |
| `list_items(item_type=None, workspace=None, root_folder=None, recursive=True, **kwargs)` | `DataFrame` | All items (reports, datasets, lakehouses, …) |
| `get_item(item, item_type=None, workspace=None, return_dataframe=True)` | `DataFrame` or `Dict` | Single-item metadata |
| `get_item_definition(item, item_type, workspace=None, return_dataframe=False, decode=True, format=None, lro_config=None)` | `Dict` or `DataFrame` | Item JSON / code definition; auto-decodes base64 |
| `delete_item(item_id, workspace=None)` | — | Delete |
| `resolve_item_id(item=None, item_type=None, workspace=None, **kwargs)` | `str` | |
| `resolve_item_name(item=None, item_type=None, workspace=None, **kwargs)` | `str` | |

### 3.9 Data import / export + translation

| Function | Returns | When |
|---|---|---|
| `read_parquet(path)` | `FabricDataFrame` | Read parquet with metadata (Arrow) |
| `translate_semantic_model(dataset, languages, exclude_characters=None, workspace=None, model_readonly=False, verbose=0)` | `DataFrame` | Auto-translate model metadata via Cognitive Services |

### 3.10 Authentication helper

| Function | Returns | When |
|---|---|---|
| `set_service_principal(tenant_id, client_id, *, client_secret=None, client_certificate=None)` | context manager | Use SP credentials outside a Fabric notebook (§2) |

---

## 4. Classes

| Class | Full path | What it represents | Key methods / properties |
|---|---|---|---|
| `FabricDataFrame` | `sempy.fabric.FabricDataFrame` | pandas-compatible DataFrame with embedded Power BI column metadata (table, dataset, workspace, data_type, data_category) | inherits pandas surface; `column_metadata` dict |
| `FabricSeries` | `sempy.fabric.FabricSeries` | Series with Power BI metadata propagation | metadata preservation through operations |
| `TOMWrapper` | `sempy.fabric.TOMWrapper` | Context-manager wrapper around the Tabular Object Model | exposes `.Model`, `.Database`, `.Refresh()` on the underlying `Microsoft.AnalysisServices.Tabular.Server` |
| `FabricRestClient` | `sempy.fabric.FabricRestClient` | REST client for Fabric REST APIs (workspaces, items, capacities, operations, folders) — auto-acquires auth tokens | `.get()`, `.post()`, `.delete()`, `.patch()`, `lro_wait` param |
| `PowerBIRestClient` | `sempy.fabric.PowerBIRestClient` | REST client for Power BI REST APIs (datasets, reports, gateways, groups, apps, dataflows) | `.get()`, `.post()`, `.delete()`, `.patch()` |
| `DataCategory` | `sempy.fabric.DataCategory` | Enum-like class for Power BI data categories | static constants (e.g. `DataCategory.Geography.City`) |
| `TraceConnection` | `sempy.fabric.TraceConnection` | Connection for starting / stopping AS Trace events | `.start_trace()`, `.stop_trace()`, `.get_events()` |
| `Trace` | `sempy.fabric.Trace` | Wrapper around an AS Trace event stream | event capture, timings, DAX-query analysis |
| `RefreshExecutionDetails` | `sempy.fabric.RefreshExecutionDetails` | Status wrapper for an async refresh | `.Status`, `.StartTime`, `.EndTime`, `.Errors` |
| `ModelCalcDependencies` | `sempy.fabric.ModelCalcDependencies` | Calculated-object dependencies in a model — always instantiate via `get_model_calc_dependencies()` | dependency-graph navigation |
| `MetadataKeys` | `sempy.fabric.MetadataKeys` | String constants for `column_metadata` dictionary keys | `TABLE`, `COLUMN`, `DATASET`, `WORKSPACE_ID`, `DATA_TYPE`, `DATA_CATEGORY`, … |
| `LroConfig` | `sempy.fabric.LroConfig` | TypedDict for Long-Running Operation polling | `timeout`, `max_retries`, `backoff` — pass via `lro_config=` |
| `CognitiveServiceRestClient` | `sempy.fabric.CognitiveServiceRestClient` | REST client for Cognitive Services (Language) — used internally for translation | no auth token required |

---

## 5. Submodules

These are the namespaces directly under `sempy.fabric.*`. Many semantic-model and lakehouse functions live here, **not** on the top-level `sempy.fabric` namespace — check these before concluding sempy "doesn't" expose something:

| Submodule | Contains |
|---|---|
| `sempy.fabric.admin` | Admin API — workspace / user / domain administration |
| `sempy.fabric.exceptions` | Exception classes — `WorkspaceNotFoundException`, `DatasetNotFoundException`, `ItemNotFoundException`, `DomainNotFoundException`, `CapacityNotFoundException`, plus HTTP errors from REST |
| `sempy.fabric.lakehouse` | Lakehouse creation / listing / resolution + Delta ops (`OPTIMIZE`, `VACUUM`) |
| `sempy.fabric.matcher` | Built-in matchers for type inference — geographic (cities, countries, lat / lon), identifiers (barcodes, postal codes) |
| `sempy.fabric.report` | Report listing, cloning, rebinding; JSON definition inspection / editing |
| `sempy.fabric.semantic_model` | Semantic-model listing, deployment, refresh — **including Direct Lake connection management** |
| `sempy.fabric.spark` | Spark runtime + pool / session settings in Fabric |
| `sempy.fabric.sql_endpoint` | SQL-endpoint discovery, connection strings, metadata refresh |

---

## 6. Common workflows

### 6.1 Evaluate DAX → DataFrame

```python
import sempy.fabric as fabric

df = fabric.evaluate_dax(
    dataset="MyDataset",
    dax_string='EVALUATE ROW("Sales", [Total Sales], "Count", COUNTA(Orders[OrderID]))',
)
```

### 6.2 Refresh a dataset and poll

```python
request_id = fabric.refresh_dataset(
    dataset="MyDataset",
    refresh_type="automatic",
    apply_refresh_policy=True,
)

details = fabric.get_refresh_execution_details(
    dataset="MyDataset",
    refresh_request_id=request_id,
)
print(details.Status, details.StartTime, details.EndTime)
```

### 6.3 List workspaces, datasets, resolve IDs

```python
ws = fabric.list_workspaces()
ds = fabric.list_datasets(workspace="MyWorkspace")
ds_id = fabric.resolve_dataset_id("MyDataset", workspace="MyWorkspace")
```

### 6.4 Read semantic-model metadata

```python
tables = fabric.list_tables(dataset="MyDataset", include_columns=True)
rels   = fabric.list_relationships(dataset="MyDataset")
meas   = fabric.list_measures(dataset="MyDataset")
roles  = fabric.list_roles(dataset="MyDataset", include_members=True)
rls    = fabric.get_row_level_security_permissions(dataset="MyDataset")
```

### 6.5 TOM editing — add a measure

```python
with fabric.connect_semantic_model("MyDataset", readonly=False) as tom:
    model = tom.model
    table = model.Tables["Sales"]
    m = table.AddMeasure()
    m.Name = "Revenue +10%"
    m.Expression = "[Revenue] * 1.1"
    model.SaveChanges()

fabric.refresh_tom_cache()
```

### 6.6 Direct Lake — read a table from OneLake

```python
df = fabric.read_table(
    dataset="MyDirectLakeDataset",
    table="FactSales",
    mode="onelake",
    onelake_import_method="spark",
)
```

### 6.7 Vertipaq + BPA health scan

```python
fabric.model_memory_analyzer(dataset="MyDataset", export="html")
fabric.run_model_bpa(dataset="MyDataset", export="html")
```

---

## 7. Permission model — which functions need ReadWrite

The Microsoft docs flag several functions with `⚠️` indicating they require **ReadWrite** permissions on the semantic model. These typically use the XMLA endpoint and need the dataset's XMLA endpoint to be enabled at the **tenant capacity** level (Power BI Premium / Premium Per User / Fabric capacities — see [Power BI Premium XMLA endpoint setup](https://learn.microsoft.com/en-us/power-bi/enterprise/service-premium-connect-tools)).

ReadWrite-requiring (non-exhaustive):

- `connect_semantic_model(readonly=False, …)` — obvious.
- TMSL / XMLA execution: `execute_tmsl()`, `execute_xmla(use_readwrite_connection=True, …)`.
- Most `list_*` functions on a semantic model when using their default XMLA path — `list_tables()`, `list_columns()`, `list_measures()`, `list_relationships()`, `evaluate_measure()`, etc.
- `list_datasets(mode='xmla', …)` — default mode. Use `mode='rest'` for read-only inventory.

When permission is the blocker, the next-easiest path is usually `mode='rest'` on `list_datasets()` (and analogous REST modes where exposed) to confirm the dataset exists, then escalate the ReadWrite ask. Don't conclude "sempy can't do X" until you've checked whether the same call exists with a REST alternative — that's the alternate-methods grounding protocol applied to this library.

---

## 8. Direct Lake, DirectQuery, TOM — touchpoints

**Direct Lake.** Semantic models in Direct Lake mode query Fabric lakehouse delta tables directly without a separate semantic model import. When reading from a Direct Lake model with `read_table()`, use `mode='onelake'` (and pick `onelake_import_method='spark'` for large tables or `'pandas'` for small) to bypass XMLA and pull from OneLake directly. This is the performance-friendly path for large fact tables — XMLA mode round-trips through the semantic-model engine.

**DirectQuery.** DirectQuery models behave like import models to sempy's query surface — `evaluate_dax()` and `evaluate_measure()` work the same. The cost shape is different (the query is executed live at the source), but the function surface is identical.

**TOM / .NET interop.** `connect_semantic_model()` returns a `TOMWrapper` whose underlying server is a `Microsoft.AnalysisServices.Tabular.Server` .NET object, accessed via pythonnet. Full TOM is available: tables, columns, measures, relationships, roles, partitions, TMSL / XMLA execution, calculation groups. Changes via TOM require `model.SaveChanges()` followed by `refresh_tom_cache()` to sync sempy's local cache.

---

## 9. Gotchas + caveats

- **`**kwargs` parameters are deprecated** on functions like `create_lakehouse()`, `refresh_dataset()`. Use `lro_config` for Long-Running Operation polling control going forward.
- **ReadWrite gating** — see §7. The `⚠️` markers in the Microsoft docs are load-bearing; don't ignore them when an SP-driven script is the consumer.
- **XMLA vs REST mode**: `list_datasets(mode='xmla')` requires ReadWrite, `mode='rest'` is read-only and doesn't need it. `list_dataflows()` and `list_reports()` support both PowerBI and Fabric endpoints and auto-fallback on `HTTP 403`.
- **Refresh commit modes**: `commit_mode='transactional'` commits all objects atomically (safe, slower). `commit_mode='partialBatch'` commits per partition (faster, less safe). When `commit_mode='partialBatch'`, `apply_refresh_policy` must be `False`.
- **`Trace`** is "only intended for exploratory use" per Microsoft — events are best-effort and timings depend on server load. **Not** for production monitoring.
- **Experimental APIs** (`create_folder()` and the rest of the folder family) may change between releases. Don't pin a workflow to them in customer code without a fallback.
- **Exception types** (in `sempy.fabric.exceptions`): `WorkspaceNotFoundException`, `DatasetNotFoundException`, `ItemNotFoundException`, `DomainNotFoundException`, `CapacityNotFoundException`. HTTP errors wrap REST failures. Catch these specifically rather than blanket `except Exception` — they carry the resource name in the message.
- **`additional_xmla_properties`** parameter (on many `list_*` functions) lets you pull extra TMSL-side metadata at query time without a second round-trip. Use it when you know the property name and the default surface doesn't include it.
- **Notebook vs script auth boundary**: a function that works in a Fabric notebook (`credential=None` → notebook identity) will fail or behave differently in a local script without `set_service_principal()` or an explicit credential. This is a permission-model boundary, not a sempy bug — surface it explicitly when an engagement's "it worked in the notebook" pattern fails in CI.
- **Concurrent TOM writes** — TOM is not designed for concurrent multi-writer edits to the same model. If you're orchestrating model edits from multiple notebooks, serialize them.

---

## 10. Related Microsoft Learn cross-references

When this reference doesn't cover the depth you need, the following Microsoft Learn pages are the primary downstream sources:

- [Tabular Object Model (TOM) — .NET API](https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server) — low-level interop for TOM editing.
- [XMLA / XML for Analysis Reference](https://learn.microsoft.com/en-us/analysis-services/xmla/) — XMLA command spec.
- [TMSL — Tabular Model Scripting Language](https://learn.microsoft.com/en-us/analysis-services/tmsl/) — TMSL script reference.
- [Power BI Data Categorization](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-data-categorization) — `DataCategory` reference.
- [DAX Function Reference](https://learn.microsoft.com/en-us/dax/) — for `evaluate_dax()` queries.
- [Power BI REST APIs](https://learn.microsoft.com/en-us/rest/api/power-bi/) — when `PowerBIRestClient` calls don't expose what you need at the sempy surface.
- [Fabric REST APIs](https://learn.microsoft.com/en-us/rest/api/fabric/) — workspaces, items, capacities — same logic for `FabricRestClient`.
- [Enhanced Refresh with Power BI REST API](https://learn.microsoft.com/en-us/power-bi/connect-data/asynchronous-refresh) — when `refresh_dataset()` semantics need a deeper read.
- [Power BI Premium XMLA endpoint setup](https://learn.microsoft.com/en-us/power-bi/enterprise/service-premium-connect-tools) — capacity-level enablement for ReadWrite XMLA.

---

## 11. Routing notes for the Team Lead

- **`power-bi-engineer`** is the primary owner of this reference. Carries the inline knowledge prior pointing at this file.
- **`flow-engineer`** consults it when a cloud flow needs to fetch / refresh / read a semantic model **without** going through Power Automate's higher-cost Power BI connector — e.g. a flow that calls an Azure Function which calls sempy.
- **`solution-alm-engineer`** consults it when an ALM pipeline includes a notebook step that programmatically validates a deployed semantic model (BPA, Vertipaq, refresh + DAX smoke test).
- **`dataverse-architect`** consults the §3.2 metadata surface when an engagement bridges Dataverse → Power BI and the question is "what shape did the semantic model on top of this Dataverse data end up with?" Read-only via `mode='rest'` first.
- **`power-platform-admin`** consults §3.1 and §3.8 (workspaces / items / capacities) for tenant audits where sempy is the easier path than direct REST.
- **`ravenclaude-core/security-reviewer`** is invoked when sempy is used **outside** a Fabric notebook with `set_service_principal()` — service-principal-secret handling is the mandatory-review surface (§2).
- **Companion files** in this knowledge bank:
  - [`pbir-enhanced-reference.md`](pbir-enhanced-reference.md) — Enhanced report file shape (`visual.json` / `page.json` / `report.json`).
  - [`pbir-enhanced-report-loading.md`](pbir-enhanced-report-loading.md) — debug runbook for Enhanced reports that won't load.
  - [`dataverse-token-acquisition.md`](dataverse-token-acquisition.md) — the auth-acquisition counterpart for Dataverse-side scripting (sempy is the Power-BI-side counterpart).

The boundary the Team Lead should respect: sempy is the *Python-from-a-Fabric-notebook* path. When the work fits a notebook context, prefer sempy. When the work belongs in a cloud flow, a Logic App, or an Azure Function, the right primary is `flow-engineer` or `azure-cloud/integration-engineer` calling the Power BI / Fabric REST APIs directly.
