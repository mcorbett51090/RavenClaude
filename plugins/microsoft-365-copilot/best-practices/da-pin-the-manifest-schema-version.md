# Pin the declarative-agent manifest `$schema` and `version` — never "latest"

**Status:** Absolute rule — an unpinned manifest version is a time bomb; the schema ships ~monthly and a silent version drift changes validation and capability behavior under you.

**Domain:** Agent design / declarative-agent manifest

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

The declarative-agent manifest schema is versioned and advances roughly monthly — v1.0 through **v1.7** is the visible run as of 2026-05-30, each minor version *adding* capabilities (graphic art + code interpreter in 1.2; Dataverse / Teams messages / Email / unscoped People in 1.3; `behavior_overrides` + connector-scoping in 1.4; Meetings in 1.5; embedded knowledge + `sensitivity_label` + `worker_agents` + `user_overrides` in 1.6). If you author against "latest" or omit the version, the manifest the toolkit validates today is not the one it validates next month: a capability you relied on may shift shape, a new required field may appear, and your RAI/schema validation can flip from pass to fail with no code change on your side. Pinning makes the version a deliberate, reviewed dependency — you bump it on purpose, re-verify, and re-run the golden-prompt set. This is house opinion #2, and the plugin hook flags an unpinned manifest.

## How to apply

Set both the `$schema` URL and the `version` string to a concrete version. Bump them together, deliberately, when you adopt a new schema's features — never as an incidental edit.

```jsonc
{
  // Pin BOTH — the $schema URL carries the version, and `version` must agree with it.
  "$schema": "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.7/schema.json",
  "version": "v1.7",
  "name": "Contoso Policy Assistant",
  "description": "Answers HR-policy questions from the indexed policy library.",
  "instructions": "You are an HR-policy assistant...",
  "capabilities": [
    { "name": "GraphConnectors", "connections": [{ "connection_id": "contosoPolicies" }] }
  ]
}
```

**Do:**
- Pin `$schema` and `version` to a known version (currently **v1.7**, `[verify-at-build]`).
- Bump the version as a reviewed change: read that version's "Changes from previous version" page, re-validate, re-run the golden-prompt set.
- Keep the API **plugin** manifest version pinned too — it is a *separate* schema (currently **v2.4**, which added MCP `RemoteMCPServer` runtime support) — see [`./apiplugin-pin-plugin-manifest-and-map-operationid-both-ways.md`](./apiplugin-pin-plugin-manifest-and-map-operationid-both-ways.md).

**Don't:**
- Use a version-less `$schema` URL or omit `version`.
- Bump the version just to silence a "newer version available" prompt without re-validating.
- Assume a capability available in v1.7 exists in the version you actually pinned — match the capability to the pinned version.

## Edge cases / when the rule does NOT apply

`worker_agents`, `sensitivity_label` (only when the agent embeds files), and `user_overrides` exist only at v1.6+; if you genuinely need one, pin to the version that introduced it and document why. Microsoft recommends the latest schema for new agents — "pin" does not mean "stay old", it means "choose explicitly". The exact current version is `[verify-at-build]`: re-confirm the v-number against Microsoft Learn before relying on it.

## See also

- [`./design-to-66-percent-of-the-declarative-agent-wall.md`](./design-to-66-percent-of-the-declarative-agent-wall.md) — the budget wall the pinned manifest sits inside
- [`./da-pass-rai-validation-design-the-prompt-for-it.md`](./da-pass-rai-validation-design-the-prompt-for-it.md) — what schema-valid does NOT buy you
- [`../knowledge/declarative-agent-manifest-2026.md`](../knowledge/declarative-agent-manifest-2026.md) · [`../agents/declarative-agent-engineer.md`](../agents/declarative-agent-engineer.md)
- [Declarative agent schema 1.7](https://learn.microsoft.com/microsoft-365/copilot/extensibility/declarative-agent-manifest-1.7) — the current schema and its change log

## Provenance

Codifies house opinion #2 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in the Microsoft Learn declarative-agent schema version pages (v1.0–v1.7, with the per-version "Changes from previous version" change logs) and the plugin-manifest v2.4 page, retrieved 2026-05-30. The version run is fast-moving and tagged `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
