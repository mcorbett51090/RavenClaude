# Return structured adaptive card responses from API plugins for complex data — not prose summaries

**Status:** Pattern
**Domain:** API plugins
**Applies to:** `microsoft-365-copilot`

---

## Why this exists

When a Copilot API plugin returns complex structured data (a list of orders, a ticket status, a pricing table), the default rendering is a prose paragraph synthesized by the Copilot model. Prose rendering loses structure, can misrepresent numeric values through hallucinated reformatting, and is harder for a user to scan than a formatted table or card. Adaptive card response templates, wired via the plugin manifest's `staticTemplate` or `previewCardTemplate`, render the data in a structured visual container that is native to Teams and Copilot — preserving numbers, dates, and labels exactly as returned.

## How to apply

Register an adaptive card template in the plugin manifest:

```json
{
  "functions": [{
    "name": "GetOrderStatus",
    "capabilities": {
      "response_semantics": {
        "data_path": "$.orders",
        "properties": {
          "title": "$.orderId",
          "subtitle": "$.status",
          "url": "$.detailUrl"
        },
        "static_template": {
          "type": "AdaptiveCard",
          "version": "1.5",
          "body": [
            { "type": "TextBlock", "text": "${orderId}", "weight": "Bolder" },
            { "type": "TextBlock", "text": "Status: ${status}" },
            { "type": "TextBlock", "text": "Amount: ${amount}" }
          ],
          "actions": [
            { "type": "Action.OpenUrl", "title": "View Order", "url": "${detailUrl}" }
          ]
        }
      }
    }
  }]
}
```

Design rules for plugin adaptive cards:
- Use `data_path` to target the array or object in the response that the card iterates over — avoid flattening the response in the API just for the card.
- Always include a `url` property in `properties` so Copilot can generate a citation link.
- Keep the card body to the 3–5 most important fields — Copilot may show multiple results and a dense card degrades the interface.

**Do:**
- Test adaptive card rendering in the Agents Toolkit Playground — card schemas that are valid JSON can still fail to render in Copilot due to version constraints `[verify-at-build]`.
- Provide a `previewCardTemplate` (smaller, thumbnail-like) in addition to the `static_template` for list results.
- Match the card version to Teams' supported adaptive card version — using v1.6 features in a v1.5 declared card causes silent truncation.

**Don't:**
- Return HTML inside a card TextBlock — HTML is not rendered in adaptive cards in Copilot; use markdown-lite formatting (bold via `**`, line breaks via `\n`).
- Depend on adaptive card `Input.*` elements for user interaction inside a Copilot conversation — Copilot does not process card inputs as conversational turns.
- Omit the `data_path` — without it, Copilot maps the entire response body to the card template, which rarely produces the correct layout.

## Edge cases / when the rule does NOT apply

For simple single-value responses (a yes/no confirmation, a single sentence) where there is no structured data to render, a prose response is appropriate and an adaptive card adds overhead without value.

## See also

- [`../agents/api-plugin-engineer.md`](../agents/api-plugin-engineer.md) — owns API plugin design and plugin manifest authoring
- [`./apiplugin-pin-plugin-manifest-and-map-operationid-both-ways.md`](./apiplugin-pin-plugin-manifest-and-map-operationid-both-ways.md) — the manifest binding rule that the adaptive card template depends on

## Provenance

Codifies the `api-plugin-openapi-hygiene` skill from CLAUDE.md §9 on response semantics and adaptive cards; Microsoft Learn Copilot API plugin adaptive card template documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
