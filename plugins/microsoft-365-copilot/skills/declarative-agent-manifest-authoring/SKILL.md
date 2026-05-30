---
name: declarative-agent-manifest-authoring
description: "Author and review a Microsoft 365 Copilot declarative-agent manifest — pin the schema version (v1.7), keep instructions within the ~8,000-char budget, declare only the needed capabilities, write scope-demonstrating conversation starters, wire API actions, and pass manifest + Responsible-AI validation against the 50/25/4096/45s hard-limit wall. Use when building or reviewing a declarative agent."
---

# Declarative-agent manifest authoring

Playbook for `declarative-agent-engineer`. Source of truth: [`../../knowledge/declarative-agent-manifest-2026.md`](../../knowledge/declarative-agent-manifest-2026.md). Skeleton: [`../../templates/declarative-agent-manifest.md`](../../templates/declarative-agent-manifest.md).

## 1. Pin the schema
Set `$schema` / `schema_version` to a concrete version (currently **v1.7** `[verify-at-build]`), never "latest". Record the version you pinned and why in the manifest comment / PR.

## 2. Budget before you write
- Instructions ≤ **~8,000 chars**.
- Grounding designed to **~66%** of: 50 grounding items / 25 plugin-response items / ~4,096 tokens / 45 s.
- **No loops** — if the agent needs to iterate, it's a custom-engine agent; route to `copilot-extensibility-architect` → `agents-sdk-engineer`.

## 3. Write the instructions
Role + scope + tone + refusal rules + how to use each grounding source. Push reference facts into grounding (connectors / knowledge / actions), not the prompt. Be explicit about what the agent must *decline*.

## 4. Declare capabilities (only what's needed)
`WebSearch`, `GraphConnectors`, `OneDriveAndSharePoint`, code interpreter, image generator, people/email/meetings. Each org-data capability is license-gated → state the **`Licensing impact:`** line.

## 5. Conversation starters
3–6 that demonstrate the scope; they are discovery, not behavioral coverage.

## 6. Wire actions
Reference API plugins (four-file plugin via `api-plugin-engineer`); verify `operationId` mapping.

## 7. Validate
- Manifest schema validation.
- **Responsible-AI validation** (runs on sideload/publish).
- **Golden-prompt regression set** (the [`copilot-agent-eval-harness`](../copilot-agent-eval-harness/SKILL.md) skill) — schema-valid ≠ behaviorally correct.

## Anti-patterns
- Unpinned schema; instructions over budget; designing to the ceiling; assuming the agent can loop; declaring capabilities you don't use; calling it "done" on schema validity alone.
