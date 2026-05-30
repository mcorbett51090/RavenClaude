# Template — declarative-agent manifest (pinned schema)

Copy + fill. Source of truth: [`../knowledge/declarative-agent-manifest-2026.md`](../knowledge/declarative-agent-manifest-2026.md). Pin the version; design to ~66% of the wall.

```jsonc
{
  // PIN THE SCHEMA — never "latest". Currently v1.7 [verify-at-build].
  "$schema": "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.7/schema.json",
  "version": "v1.7",
  "name": "<agent display name>",
  "description": "<one-line scope; what it does, for whom>",

  // ≤ ~8,000 chars. Role + scope + tone + refusal rules + how to use grounding.
  // Push reference facts into grounding, NOT this string.
  "instructions": "You are <role>. Scope: <...>. Always <...>. Never <...>. Use <grounding> for <...>. Decline <out-of-scope>.",

  // Declare ONLY what's needed — each org-data capability is license-gated.
  "capabilities": [
    { "name": "WebSearch" },
    { "name": "GraphConnectors", "connections": [{ "connection_id": "<connectionId>" }] },
    { "name": "OneDriveAndSharePoint", "items_by_url": [{ "url": "<site/library URL>" }] }
  ],

  // 3–6 starters that demonstrate scope (discovery, not coverage).
  "conversation_starters": [
    { "title": "<short>", "text": "<example prompt>" }
  ],

  // API actions — reference the four-file plugin (see api-plugin-pair.md).
  "actions": [
    { "id": "<actionId>", "file": "ai-plugin.json" }
  ]
}
```

## Budget annotations (fill before sign-off)

| Limit | Budget (~66%) | This agent | OK? |
|---|---|---|---|
| Grounding items (50) | ~33 | | |
| Plugin response items (25) | ~16 | | |
| Tokens (~4,096) | ~2,700 | | |
| Timeout (45 s) | ~30 s | | |
| Loops? | **none allowed** | | |
| Instructions chars (~8,000) | ~5,300 | | |

## Pre-ship checklist
- [ ] Schema **pinned** to a concrete version (recorded the version + date).
- [ ] Instructions within budget; reference facts in grounding, not the prompt.
- [ ] Only-needed capabilities; **`Licensing impact:`** stated for each org-data source.
- [ ] Manifest schema validation passes.
- [ ] **Responsible-AI validation** passes (sideload/publish).
- [ ] **Golden-prompt regression set** passes (`copilot-agent-eval-harness`).
- [ ] No loop/iteration required (else → custom-engine agent).

**Licensing impact:** <Copilot seats; connector quota; SharePoint-knowledge gating; or "none">
