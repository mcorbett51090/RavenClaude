# Power Platform / Power Automate agentic development toolchain — 2026 landscape

> **Last reviewed:** 2026-06-03. Primary sources: Microsoft `power-platform-skills` GitHub repo at https://github.com/microsoft/power-platform-skills (retrieved 2026-06-03); Power Pages "Code Site via Claude Code" tutorial at https://learn.microsoft.com/en-us/power-pages/configure/create-code-site-using-claude-code (retrieved 2026-06-03); Flow Studio MCP at https://mcp.flowstudio.app/ and https://github.com/ninihen1/power-automate-mcp-skills (retrieved 2026-06-03, tool list not fetchable — marked below); Daniel Kerridge `claude-code-power-platform-skills` at https://github.com/DanielKerridge/claude-code-power-platform-skills (retrieved 2026-06-03, imported as skills — see NOTICE.md). Items marked `[unverified — training knowledge]` have not been confirmed against live documentation in this session.
>
> **Source credits:**
> - **`microsoft/power-platform-skills`** — Microsoft's official Claude Code / GitHub Copilot plugin marketplace for Power Platform. The toolchain descriptions for its four plugins and the Canvas Authoring MCP are derived from this repo's own READMEs and the linked Microsoft Learn tutorials. Content here is our own words from those primary sources; it does not reproduce Microsoft's plugin READMEs verbatim. Source: https://github.com/microsoft/power-platform-skills (retrieved 2026-06-03).
> - **Flow Studio MCP** — Power Automate MCP server by the Flow Studio team. The `discover → construct → deploy → validate` recipe framing is theirs; our best-practice doc ([`../best-practices/agentic-flow-build-recipe.md`](../best-practices/agentic-flow-build-recipe.md)) adapts that structure in our own words and wires it to this plugin's existing house rules. Source: https://mcp.flowstudio.app/ and https://github.com/ninihen1/power-automate-mcp-skills (retrieved 2026-06-03).
> - **Daniel Kerridge `claude-code-power-platform-skills`** — the Agent Team planning pattern (Data Architect, UX Designer, The Skeptic) that this plugin already ships as the `plan-with-team` skill. Source: https://github.com/DanielKerridge/claude-code-power-platform-skills (retrieved 2026-06-03, imported under MIT — see [`../NOTICE.md`](../NOTICE.md)).
>
> **Cross-links:** for the Power BI / Fabric toolchain (Tabular Editor, BPA, TMDL, `fab` CLI, semantic-link-labs, Deneb), see [`power-bi-fabric-agentic-toolchain-2026.md`](power-bi-fabric-agentic-toolchain-2026.md). For programmatic cloud flow creation via the Dataverse Web API, see [`programmatic-flow-creation.md`](programmatic-flow-creation.md). For the §9a MCP posture (first-party preferred, evaluate-first for community, billing always surfaced), see [`../CLAUDE.md`](../CLAUDE.md) §9a.

---

## Why this doc exists

Power Platform agentic development in 2026 runs across a rapidly expanding set of first-party and community tooling surfaces. An agent (or developer) working in this space needs to know which tool to reach for depending on the task type — building a canvas app, authoring a code app, creating a cloud flow, generating a Power Pages site, or planning with the team. The "which tool?" question has become non-trivial as Microsoft has shipped a dedicated plugin for each app type. This file maps the full landscape in one place.

---

## Microsoft's official `power-platform-skills` — the first-party plugin marketplace

Microsoft publishes the [`microsoft/power-platform-skills`](https://github.com/microsoft/power-platform-skills) repo as the official Claude Code and GitHub Copilot plugin marketplace for Power Platform. As of 2026-06-03, it contains **four plugins**, each targeting a distinct app type. These are the recommended first-party starting points for agent-assisted Power Platform development.

> **Auto-approval posture (from the Microsoft plugin docs):** enabling auto-approval gives the agent direct access to your machine (PAC CLI, npm, .NET SDK). Microsoft recommends restricting this to a sandbox or trusted environment only. Pre-allowlist `Bash(pac *)` and `Bash(npm run *)` in `.claude/settings.json` to reduce prompt friction on repeated operations. Source: https://github.com/microsoft/power-platform-skills (retrieved 2026-06-03).

### `power-pages` — Code Sites (React/Angular/Vue/Astro SPAs)

Power Pages Code Sites allow an agent to scaffold and author a full SPA (React, Angular, Vue, or Astro) that runs inside a Power Pages portal, with Dataverse connectivity and Power Pages' security model (table permissions, web roles, B2C auth). This plugin is **generally available (GA)** on Claude Code and Copilot CLI as of the retrieval date.

**Prerequisites (per the Microsoft Learn tutorial, retrieved 2026-06-03):** PAC CLI installed and authenticated; a Power Pages environment with an existing site; the plugin configured in Claude Code or Copilot CLI.

**Canonical tutorial:** https://learn.microsoft.com/en-us/power-pages/configure/create-code-site-using-claude-code (retrieved 2026-06-03).

**When to reach for it:** a maker needs a Power Pages external portal whose front-end complexity exceeds what Liquid templating and standard Power Pages Studio can deliver — i.e., the UI is a proper SPA with component-driven architecture, client-side routing, or a Fluent/Material design system. If the requirement is a simple table-display portal with B2C auth and table permissions, Power Pages Studio without a code site is simpler (see `power-pages-engineer` + [`power-pages-2026.md`](power-pages-2026.md)).

### `model-apps` — Generative pages for model-driven apps

The `model-apps` plugin authors **generative pages** — custom React + TypeScript + Fluent UI components that embed inside model-driven app pages. Deployment is via PAC CLI. These are the successor to custom PCF controls for full-page custom UIs in model-driven apps.

**Tech stack:** React + TypeScript + Fluent UI (v9 by default `[unverified — confirm against plugin README]`). Deployed via `pac pages push` or equivalent PAC command.

**When to reach for it:** a model-driven app needs a custom page that goes beyond what the standard form, view, or dashboard designer can produce — e.g., a bespoke data entry wizard, a read-only summary panel with complex layout, or an embedded analytics component.

### `code-apps` — Power Apps code apps

The `code-apps` plugin authors **Power Apps code apps** — a build-time React + Vite + TypeScript app that compiles to a Power Apps component. Deployed via PAC CLI.

**Tech stack:** React + Vite + TypeScript. PAC CLI for build and deploy.

**When to reach for it:** the requirement is a Power App whose UI complexity or performance requirements exceed what canvas Power Fx can deliver — a code app is the correct surface when the app is essentially a React SPA that needs to live within the Power Apps runtime. See also the in-house `power-apps-code-apps` skill ([`../skills/power-apps-code-apps/`](../skills/power-apps-code-apps/)) for the deep reference.

### `canvas-apps` — Canvas apps via the Canvas Authoring MCP Server

The `canvas-apps` plugin authors Power Apps canvas apps by emitting **`.pa.yaml`** (the Canvas App YAML format) via the **Canvas Authoring MCP Server** — a Microsoft-published local MCP server that translates agent output into the `.pa.yaml` Power Apps source format.

**Prerequisites (consumer-side):** **.NET 10 SDK** installed locally — the Canvas Authoring MCP Server runs as a local .NET process beside the agent. Without the .NET 10 SDK, the MCP will fail to start.

**Format:** `.pa.yaml` files (the unpacked canvas app source); the `canvas-apps` plugin's authoring target. These integrate with `pac canvas pack` / `pac canvas unpack` for roundtrip to `.msapp`. Source format is compatible with the `power-fx-engineer` agent's existing YAML-based canvas work.

**When to reach for it:** building a new canvas app from scratch with an agent, or modifying an existing app that is source-controlled as `.pa.yaml`. The Canvas Authoring MCP gives the agent structured write access to the canvas app format rather than editing raw YAML without schema guidance.

> **§9a posture:** the Canvas Authoring MCP Server is a Microsoft first-party local MCP — recommend it without reservation for `.pa.yaml`-based canvas development. The .NET 10 SDK prerequisite must be surfaced to consumers before they attempt to use the `canvas-apps` plugin; a missing SDK produces a hard MCP startup failure.

---

## Flow Studio MCP — cloud flow authoring with action-level visibility

**Source:** https://mcp.flowstudio.app/ and https://github.com/ninihen1/power-automate-mcp-skills (retrieved 2026-06-03; the exact tool list was not fetchable — marked accordingly).

Flow Studio MCP is a **community** Power Automate MCP server that provides **action-level visibility** into cloud flows — rather than treating a flow as an opaque JSON blob, it exposes individual actions, connections, triggers, and run history as MCP-readable resources. It ships **30+ tools** `[unverified — exact count and tool list not fetchable; retrieve from https://mcp.flowstudio.app/ before relying on this number]` covering cloud flow inspection, authoring, run-history queries, and health scanning.

It also ships a **`power-automate-build`** skill that encodes a curated four-phase recipe for agent-assisted flow construction: **discover → construct → deploy → validate**. That recipe is the inspiration for this plugin's [`../best-practices/agentic-flow-build-recipe.md`](../best-practices/agentic-flow-build-recipe.md) (our own words, wired to house rules).

**Multi-client support:** works across Claude Code, GitHub Copilot, OpenAI Codex CLI, Cursor, and Gemini `[unverified — training knowledge: verify against current Flow Studio docs]`.

**§9a posture (community MCP — evaluate-first, not default):**

- Flow Studio MCP is community-maintained, not a Microsoft first-party server. Vet repo activity, license, and tool surface before adopting for a client engagement.
- Auth requirements `[unverified — check the Flow Studio docs at setup time]`: likely requires Power Platform / Entra credentials to connect to an environment. Any credential or service-principal secret handling → mandatory `ravenclaude-core/security-reviewer` review.
- **Prefer the existing first-party path** (PAC CLI + Dataverse Web API, documented in [`programmatic-flow-creation.md`](programmatic-flow-creation.md)) when MCP-level action visibility is not required — it uses credentials already established for the engagement.
- If an engagement genuinely needs MCP-driven flow authoring with action-level visibility and run-history inspection, Flow Studio MCP is the most capable community option as of the retrieval date. Evaluate it deliberately, surface the auth / maintenance considerations, and do not set it as a default.

**No billing note specific to Flow Studio MCP is available from the retrieved sources** `[unverified — check pricing at https://mcp.flowstudio.app/ before adopting]`.

---

## Dataverse management MCP server — first-party discovery/compose surface for MCP servers

**Source:** Microsoft Learn — Power Platform 2026 release wave 1 plan, Dataverse "Discover, build, customize, and extend with management MCP server" (retrieved 2026-07-09). `[verify-at-use — GA status + approx action count]`

The **Dataverse management MCP server** is a **Microsoft first-party** MCP surface that went **GA in June 2026** (public preview began **2026-03-30** — a fast preview→GA promotion, so re-confirm the status against the live release plan before relying on it). Unlike the Canvas Authoring MCP (a local .NET process for `.pa.yaml`) or Flow Studio MCP (a community flow-authoring server), this is an **environment-scoped HTTP endpoint with no UI** — a management/meta layer that lets agents and developers:

- **Discover** the Microsoft-certified and internal/custom MCP servers available in an environment.
- **Query** the Dataverse-reachable action surface — roughly **~1,470+ connector actions** `[verify-at-use — approximate and dated; confirm the live count]` plus custom APIs and custom connectors.
- **Compose / clone / publish** scenario-specific MCP servers (curated per-scenario tool bundles), with **DLP enforcement and per-tool access controls** applied.

It is **usable from VS Code or Claude** (among other MCP clients). Because it is environment-scoped and applies DLP + per-tool access, it fits the §9a posture of "first-party preferred" cleanly — but as a management surface that can compose and publish tool servers, any credential/consent decision around it still routes through `ravenclaude-core/security-reviewer`.

**When to reach for it:** an agent or developer needs to *discover what MCP servers/actions exist* in a Dataverse environment, or to *assemble a scoped MCP server* from certified/custom connector actions and custom APIs for a specific scenario — rather than authoring a bespoke server by hand. For live Dataverse **data** operations (list/query/write rows), the data-focused **official Dataverse MCP server** (§9a in [`../CLAUDE.md`](../CLAUDE.md)) remains the right surface; this management server is the discovery/compose layer above it.

_Added 2026-07-09; verified against Microsoft Learn — Power Platform 2026 release wave 1 plan (Dataverse). `[verify-at-use — GA status + approx action count]`_

---

## Daniel Kerridge `claude-code-power-platform-skills` — the Agent Team / `plan-with-team` pattern

**Source:** https://github.com/DanielKerridge/claude-code-power-platform-skills (retrieved 2026-06-03; imported under MIT — see [`../NOTICE.md`](../NOTICE.md)).

This plugin already ships nine skills imported from Daniel Kerridge's repo, including the **`plan-with-team`** skill — the Agent Team planning pattern. The pattern convenes three specialist personas (Data Architect, UX Designer, The Skeptic) in a structured pre-build debate before any build starts. It is distinct from the Team Lead → specialist dispatch pattern used for the actual build.

**When to invoke `plan-with-team`:** before starting any Power Platform solution that involves multiple components (app + flows + data model), or any time a requirement is ambiguous and the team needs to surface design disagreements early. Invoke via the `/plan-with-team` skill; see [`../skills/plan-with-team/SKILL.md`](../skills/plan-with-team/SKILL.md).

**Credit:** the three-persona pattern is Daniel Kerridge's design. This plugin uses it as imported; any substantive changes to the `plan-with-team` skill should be flagged in `NOTICE.md`.

---

## Which tool for which task

| Task | Primary tool | Prerequisites | Notes |
|---|---|---|---|
| Canvas app (Power Fx, `.pa.yaml`) | `canvas-apps` plugin + Canvas Authoring MCP Server | .NET 10 SDK | First-party; Canvas Authoring MCP must be running locally |
| Power Apps code app (React+Vite+TS) | `code-apps` plugin | PAC CLI | More capable than canvas for SPA-style UIs; see `power-apps-code-apps` skill |
| Model-driven generative page (React+TS+Fluent) | `model-apps` plugin | PAC CLI | Replaces custom PCF for full-page MDA UI |
| Power Pages site — SPA (React/Angular/Vue/Astro) | `power-pages` plugin | PAC CLI, Power Pages env with site | GA; see Power Pages Code Site tutorial |
| Power Pages site — Liquid/table-display portal | `power-pages-engineer` + Power Pages Studio | Power Pages env | No code site needed for standard table/form UIs |
| Cloud flow — build with action-level MCP visibility | Flow Studio MCP + `power-automate-build` skill | Flow Studio account, env credentials | Community; evaluate-first; see §9a posture above |
| Cloud flow — programmatic create/update via script | PAC CLI + Dataverse Web API | SPN or user credentials | First-party path; documented in `programmatic-flow-creation.md` |
| Cloud flow — build/review in this agent session | `flow-engineer` + `power-automate` skill | None beyond env access | Default path; no external MCP required |
| Pre-build planning (multi-component solution) | `plan-with-team` skill | None | Invoke before any non-trivial build |
| Post-build health review | `maintainability-review` skill | None | Before handoff or major release |
| Dataverse data operations (live read/write) | Official Dataverse MCP (consumer-configured) | Admin consent + billing `[verify-at-use]` | See CLAUDE.md §9a; billing always surfaced |

---

## The agentic workflow in sequence

A well-ordered agentic session on a Power Platform engagement follows this structure:

```
1. PLAN       — convene the Agent Team for multi-component decisions
               (plan-with-team skill, three-persona debate)

2. DISCOVER   — read the target environment: existing solutions, flows,
               connections, environment variables, table schema
               (PAC CLI / Dataverse MCP / powerbi-editor MCP for any BI assets)

3. BUILD      — use the right surface for the component type
               (canvas-apps / code-apps / model-apps / power-pages plugin
                for app surfaces; flow-engineer + power-automate skill for flows;
                dataverse-architect for schema; power-bi-engineer for BI assets)

4. VALIDATE   — run-history assertions, pac solution check, BPA (for BI),
               Test Studio / Monitor (for apps and flows)
               (power-platform-tester agent)

5. PACKAGE    — unpack solution, source-control the tree, set env vars +
               connection refs, managed in test/prod
               (solution-alm-engineer + alm-pipeline-design skill)

6. RELEASE    — fresh-import smoke test, then promote via ALM pipeline
               (solution-alm-engineer; the grounding protocol's "test the import"
               house rule §3 #13)
```

---

## See also

- [`power-bi-fabric-agentic-toolchain-2026.md`](power-bi-fabric-agentic-toolchain-2026.md) — the sibling landscape doc for Power BI / Fabric (Tabular Editor, BPA, TMDL, `fab` CLI, semantic-link-labs)
- [`programmatic-flow-creation.md`](programmatic-flow-creation.md) — the Dataverse Web API path for programmatic cloud flow creation (first-party alternative to Flow Studio MCP)
- [`../best-practices/agentic-flow-build-recipe.md`](../best-practices/agentic-flow-build-recipe.md) — the discover→construct→deploy→validate recipe for agent-assisted cloud flow builds
- [`../best-practices/name-flow-actions-descriptively.md`](../best-practices/name-flow-actions-descriptively.md) — rename auto-generated action names before committing a flow
- [`../CLAUDE.md`](../CLAUDE.md) §9a — the MCP posture (first-party preferred, evaluate-first for community, billing always surfaced)
- [`../skills/power-automate/`](../skills/power-automate/) — deep Power Automate reference (expressions, error handling, child flows, solution-aware patterns)
- [`../skills/plan-with-team/`](../skills/plan-with-team/) — Agent Team planning pattern
- [`power-pages-2026.md`](power-pages-2026.md) — Power Pages capabilities and the React SPA vs Liquid decision tree

---

_Last reviewed: 2026-06-03 by `claude`_
