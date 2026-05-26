---
id: copilot-bridge
title: "GitHub Copilot CLI bridge"
category: "Marketplace engineering"
kind: ravenclaude-built
order: 54
summary: "RavenClaude runs under GitHub Copilot CLI too — via a generated package + a hook adapter — and updating is just `git pull`, never a re-install."
see_also: [layout-hook, hook-lifecycle]
last_verified: 2026-05-26
refresh_when: "The Copilot package generator, the hook adapter's envelope mapping, or Copilot's plugin-hook bug status changes."
sources:
  - label: "ravenclaude-core constitution"
    url: "plugins/ravenclaude-core/CLAUDE.md"
  - label: "generate-copilot-plugin.py"
    url: "scripts/generate-copilot-plugin.py"
---

Copilot CLI is itself a plugin host with the same lifecycle events (SessionStart / PreToolUse / …), Agent Skills, AGENTS.md, and MCP — so most of the plugin ports. Three pieces make it work: `generate-copilot-plugin.py` **projects** the canonical plugin into a Copilot package (generated, never hand-maintained, `--check`-gated like the dashboard); a **hook adapter** translates the I/O envelopes so the *unmodified* hook scripts run under Copilot (mapping its `toolName`/`toolArgs` ⇄ Claude's `tool_name`/`tool_input`, and the verdict shapes); and **enforcement hooks ship repo-level** in `.github/hooks/` because a Copilot bug stops plugin-level `preToolUse` hooks from firing.

The design pillar is **frictionless updates**: instead of Copilot's re-install-to-update flow, the plugin loads **live** via `copilot --plugin-dir copilot/`, so an update is just **`git pull`** (`ravenclaude update`). No re-install, ever.

```mermaid
flowchart TD
  CANON[Canonical plugin] --> GEN[generate-copilot-plugin.py]
  GEN --> PKG[copilot/ package · --check gated]
  CO[Copilot PreToolUse envelope] --> AD[hook adapter]
  AD --> CL[unmodified hook scripts]
  CL --> AD
  UP[Update] --> PULL[git pull · loads live]
  class CANON,GEN,PKG,AD,CL,UP,PULL built
  class CO fact
```

<!-- mini -->
```mermaid-mini
flowchart LR
  C[Canonical plugin] --> A[adapter] --> CO[Copilot CLI]
  C --> U[update = git pull]
  class C,A,U built
```
