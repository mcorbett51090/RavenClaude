# Declarative-agent manifest + the hard limits (2026)

**Last reviewed:** 2026-05-30
**Confidence:** High on the limit values + version-pin discipline (first-party). `[verify-at-build]` on the exact current schema version — it ships ~monthly (latest verified **v1.7**).
**Read when:** authoring or reviewing a declarative-agent manifest, or sizing a design against the wall.

---

## The hard limits (the load-bearing wall)

| Limit | Value | Note |
|---|---|---|
| Grounding items | **50** | inclusive of overhead |
| Plugin response items | **25** | inclusive of overhead |
| Tokens | **~4,096** | inclusive of overhead |
| Timeout | **45 s** | end-to-end |
| Orchestration | **single grounding op + single tool call, sequential** | **NO loops / no iteration** |

**Design to ~66% of every limit** — they're inclusive of system overhead, so the usable budget is well under the headline number. The moment a task needs iteration, a loop, or multi-step tool chaining, it is **not** a declarative agent — escalate to a custom-engine agent (`agents-sdk-engineer`). Grounding: [declarative agent architecture](https://learn.microsoft.com/microsoft-365/copilot/extensibility/declarative-agent-architecture).

## The manifest (pinned schema)

Pin the schema — never "latest". The manifest ships ~monthly; latest verified **v1.7** `[verify-at-build]`. Grounding: [declarative agent manifest v1.7](https://learn.microsoft.com/microsoft-365/copilot/extensibility/declarative-agent-manifest-1.7).

Capability map (high level):
- **`name` / `description`** — discovery surface.
- **`instructions`** — the system prompt; **~8,000-char budget**. Role + scope + tone + refusal rules; push reference detail into grounding, not the prompt.
- **`capabilities`** — web search (`WebSearch`), Graph connectors (`GraphConnectors`), SharePoint/OneDrive knowledge (`OneDriveAndSharePoint`), code interpreter, image generator, people, email, meetings — declare only what's needed.
- **`conversation_starters`** — demonstrate scope; not behavioral coverage.
- **`actions`** — reference API plugins (the four-file plugin; see [`api-plugins-and-auth-2026.md`](api-plugins-and-auth-2026.md)).

## Validation (two gates + the regression set)

1. **Manifest schema validation** — structural; runs in the Agents Toolkit / on sideload.
2. **Responsible-AI (RAI) validation** — runs on **sideload and publish**; an agent can be schema-valid and fail RAI.
3. **Golden-prompt regression set** — house opinion: **no DA is "done" on schema validity alone.** Schema valid ≠ behaviorally correct. See the [`copilot-agent-eval-harness`](../skills/copilot-agent-eval-harness/SKILL.md) skill.

## Licensing impact

Declarative agents run on the user's Copilot license; capabilities that ground on org data (connectors, SharePoint/OneDrive knowledge) are license-gated and may meter quotas — state the impact.

## Refresh triggers
- A new manifest version ships → re-verify v-number, capability names, and limit values.
- Limit values change in the architecture doc.
