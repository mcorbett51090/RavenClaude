# Integration Patterns

**Dated:** 2026-05-30 · **Status:** current

Salesforce integration reduces to **six canonical patterns**. The choice turns on synchronous vs asynchronous, who initiates, and the API/limit budget. Azure-native middleware coordinates with `azure-cloud/*`.

## Decision Tree: which integration pattern?

```mermaid
graph TD
  A[Integration requirement] --> B{Who initiates?}
  B -->|Salesforce calls out| C{Need the response now?}
  B -->|External calls Salesforce| D[Remote Call-In - REST/SOAP/Bulk API]
  C -->|Yes, synchronous| E[Request and Reply]
  C -->|No, can be async| F{Bulk dataset on a schedule?}
  F -->|Yes| G[Batch Data Synchronization]
  F -->|No| H[Fire and Forget - Platform Events / @future callout]
  B -->|Display external data without storing| I[Data Virtualization - Salesforce Connect / OData]
  B -->|External event updates the UI| J[UI Update Based on Data Changes - streaming/CDC]
```

## The six patterns

| Pattern | Sync/Async | Use when |
| --- | --- | --- |
| **Request and Reply** | Sync | Salesforce needs an immediate response from an external system |
| **Fire and Forget** | Async | Salesforce notifies; no response needed (Platform Events, async callout) |
| **Batch Data Synchronization** | Async | Bulk import/export on a schedule (Bulk API 2.0) |
| **Remote Call-In** | Sync/Async | External system creates/reads/updates Salesforce data via API |
| **UI Update Based on Data Changes** | Async (push) | External change pushes to the Salesforce UI (Streaming/CDC) |
| **Data Virtualization** | Sync (no copy) | Display external data live without storing it (Salesforce Connect/OData) |

## Limit budget

Every outbound callout and inbound API call consumes the **daily API request limit**; synchronous callouts hold a long-running concurrent request slot and have a per-transaction time cap. Prefer Platform Events / Bulk API for high-volume async, and push middleware (incl. Azure Event Grid / Service Bus via `azure-cloud/*`) for fan-out. Verify current API/limit numbers `[verify-at-build]`.

## Sources

- https://sfdcdevelopers.com/2025/10/29/salesforce-integration-patterns-types-use-cases-and-best-practices/
