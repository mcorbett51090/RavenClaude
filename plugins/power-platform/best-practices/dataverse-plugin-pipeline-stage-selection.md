# Register a Dataverse plug-in step on the stage + mode the work actually needs

**Status:** Pattern — strong default; deviate only with a written reason on the registration step.

**Domain:** Dataverse / Plug-ins

**Applies to:** `power-platform`

---

## Why this exists

The plug-in pipeline stage (PreValidation 10 / PreOperation 20 / PostOperation 40) and the execution mode (synchronous vs asynchronous) together decide whether your logic is transactional, whether it can block the user, and how much latency it adds to every write. Picking the wrong combination is the single most common cause of plug-in pain: validation registered on PostOperation can't cleanly reject the operation; data-mutation registered on PostOperation costs an extra `Update` round-trip (and can recurse); a synchronous external HTTP call on a high-volume table is a transaction-timeout factory. The stage is not a stylistic choice — it changes correctness and performance.

## How to apply

Match the stage and mode to what the code does:

| Intent | Stage | Mode | Why |
|---|---|---|---|
| Reject bad input early, no DB state needed | **PreValidation (10)** | Sync | Runs **outside** the transaction → cheapest rollback, fires before security checks for some messages |
| Set defaults / transform / auto-number the Target before save | **PreOperation (20)** | Sync | Mutate `Target` in place, no extra `Update` call, all inside the transaction |
| Create/update related records that must commit atomically with the main op | **PostOperation (40)** | Sync | Row exists; `PostEntityImages` available; rolls back together |
| Email, notification, external API call, logging | **PostOperation (40)** | **Async** | 24h budget instead of 2 min; failure doesn't roll back the user's save |

```csharp
// PreOperation (20), Sync — mutate the Target directly, no second round-trip.
// Register: Create of cnt_invoice, stage 20, sync. Filtering attrs irrelevant for Create.
public void Execute(IServiceProvider serviceProvider)
{
    var context = (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));
    if (context.Stage != 20) return;                       // defensive: refuse to run off-stage
    var target = (Entity)context.InputParameters["Target"];
    if (target.GetAttributeValue<DateTime?>("cnt_invoicedate") == null)
        target["cnt_invoicedate"] = DateTime.UtcNow;       // in-place; persisted by MainOperation
}
```

**Do:**
- Validate-and-reject on **PreValidation (10)** with `InvalidPluginExecutionException` — it's outside the transaction, so the rollback is cheapest.
- Mutate the `Target` on **PreOperation (20)** in place. Don't call `service.Update` on the same row from a PreOp plug-in — set the attribute on `Target` and let MainOperation persist it.
- Push slow / external / non-critical work to **PostOperation (40) async**. The user's save shouldn't wait on an email send.
- Register **filtering attributes** on Update steps so the plug-in fires only when a relevant column changes.

**Don't:**
- Register validation on PostOperation — the write already happened; "rejecting" now means an awkward compensating delete.
- Make a synchronous external HTTP call inside the transaction (PreOp/PostOp sync) on a high-volume table — you risk the 2-minute sync timeout and you hold a DB lock the whole time.
- Use static fields for state — plug-in instances are cached and reused; use `context.SharedVariables` for pipeline-scoped state.

## Edge cases / when the rule does NOT apply

- **PreEntityImages are not available on Create** (the row doesn't exist yet); **PostEntityImages are not available on Delete** (the row is gone). If your PostOp logic needs old values, register a Pre-Image; if it needs new values on Create, register a Post-Image — and that forces the PostOperation stage.
- A genuinely **transactional** related-record write (e.g. an inventory decrement that must commit-or-fail with the order) belongs on PostOperation **sync**, not async — async runs outside the transaction and can't roll the order back.
- **Pre-validation runs before the database transaction begins**, so a `service.Create` you issue there is **not** rolled back if the main operation later fails. Don't write durable side effects from stage 10.

## See also

- [`../skills/dataverse-plugins/resources/execution-pipeline.md`](../skills/dataverse-plugins/resources/execution-pipeline.md) — stage table, message-type matrix, entity-image availability, filtering attributes
- [`../skills/dataverse-plugins/resources/common-patterns.md`](../skills/dataverse-plugins/resources/common-patterns.md) — auto-number (PreOp), validation (PreValidation), cascade-aggregate (PostOp) reference implementations
- [`./dataverse-rollup-vs-calculated-vs-plugin.md`](./dataverse-rollup-vs-calculated-vs-plugin.md) — when a plug-in is the wrong mechanism entirely
- [`../knowledge/dataverse-decision-trees.md`](../knowledge/dataverse-decision-trees.md) — `## Decision Tree: Plug-ins — pipeline stage + execution mode`
- [`../agents/dataverse-architect.md`](../agents/dataverse-architect.md) — owner; carries the "plug-in only when transactional + synchronous" prior

## Provenance

Grounded in the plugin's own `skills/dataverse-plugins/resources/execution-pipeline.md` (stage/mode/image tables) and the `dataverse-architect` agent's stated opinions (§ "Opinions specific to this agent": "Plug-ins only when the logic must be transactional and synchronous"; "Sync plug-ins on high-volume tables doing slow work … are a transaction-timeout factory"). Stage numbers (10/20/40) and the 2-min sync / 24-hour async budgets are from the same skill's CRITICAL RULES.

---

_Last reviewed: 2026-05-30 by `claude`_
