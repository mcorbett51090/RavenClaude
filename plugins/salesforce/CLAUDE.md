# salesforce — plugin constitution

This plugin ships a roster of Salesforce engineering specialists. It inherits the marketplace constitution at the repository root (`../../CLAUDE.md`) and the cross-tool conventions in `../../AGENTS.md`. Anything here is **salesforce-specific** and refines — never overrides — the root rules.

## What this plugin is

A focused set of agents for building on the Salesforce platform: bulk-safe Apex (triggers, async, SOQL/DML), declarative-automation triage (Flow vs Apex, automation density), Agentforce design under determinism and Trust Layer constraints, and cross-cutting platform architecture (data model, sharing, LDV, packaging, DevOps, integration). A forked reviewer enforces the house opinions as a pass/fail rubric.

## Agent roster

| Agent | Scope | Model |
| --- | --- | --- |
| `apex-engineer` | Apex / server-side: triggers, async, SOQL/SOSL, tests | sonnet |
| `flow-automation-architect` | Declarative automation, Flow-vs-Apex, automation density | sonnet |
| `agentforce-architect` | Agentforce topics/actions, determinism, Trust Layer | sonnet |
| `salesforce-platform-architect` | Data model, sharing, LDV, packaging, DevOps, integration | opus |
| `salesforce-reviewer` | The 15 house opinions as a pass/fail review rubric (forked) | opus |

## The 15 house opinions

These are baked into every agent and are the `salesforce-reviewer`'s rubric:

1. Bulkify everything — no SOQL or DML in a loop, ever.
2. One trigger per object; logic lives in a handler class.
3. Logic-less triggers — the trigger is a dispatch shell.
4. Recursion control is mandatory on every handler.
5. No hard-coded IDs (records, RecordTypes, profiles) — query or use custom metadata.
6. `with sharing` by default; justify every `without sharing`.
7. Enforce CRUD/FLS for user-context access (`WITH SECURITY_ENFORCED` / `Security.stripInaccessible`).
8. Bind every SOQL variable — no string concatenation in dynamic SOQL.
9. Test for bulk (200 records); assert outcomes, not coverage.
10. No `@isTest(SeeAllData=true)` — use a TestDataFactory.
11. Flow over Apex for simple automation; Apex past the declarative ceiling. Document the call.
12. One automation entry point per object.
13. Design for LDV from day one — selective, indexed queries.
14. Agentforce is non-deterministic — never where a deterministic automation belongs; gate with the Trust Layer.
15. Bundle metadata in 2GP packages; deploy in dependency order; never click-deploy to prod.

## Escalating out — cross-plugin seams

- **Security verdicts** — SOQL injection, secret handling, and FLS-as-a-security-control escalate to `ravenclaude-core/security-reviewer`. This plugin supplies the domain rubric; core owns the verdict. There is deliberately **no** security agent here.
- **Generic test authoring** escalates to `ravenclaude-core/tester-qa`; `apex-engineer` owns the Salesforce-specific bulk/assert discipline.
- **Azure-native integration** (middleware, Event Grid, queues crossing into Azure) coordinates with `azure-cloud/*`.
- **The accuracy / grounding / Structured Output protocols** are inherited from the root constitution.

## House conventions

- Every agent inherits the team constitution and references plugin-internal files only.
- Knowledge docs are citation-grounded and dated. Fast-moving Agentforce facts are tagged `[verify-at-build]`.
- Skills are deterministic, parameterized, and safe to run unattended.
- The advisory hook `hooks/flag-salesforce-anti-patterns.sh` greps written Apex for the grep-able anti-patterns (SOQL/DML in loop, hard-coded IDs, `SeeAllData=true`, missing `with sharing`) and prints non-blocking notes.

## Knowledge & scenario banks (the dual-bank model)

Two banks back the agents (see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer): [`knowledge/`](knowledge/) — ~20 Mermaid decision trees across Apex (async/security/trigger/SOQL-selectivity/bulk/test-isolation/Experience-Cloud-auth), Flow/LWC, integration/data/LDV, platform/ALM/Agentforce, and the new **automation-density + order-of-execution** trees ([`knowledge/automation-density-decision-trees.md`](knowledge/automation-density-decision-trees.md)). **Traverse the relevant tree top-to-bottom before choosing.** Plus ~70 `best-practices/` one-rule docs.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (SOQL-in-loop 101, trigger-recursion runaway, guest-user data exposure, Agentforce non-deterministic misfire). Secondary source; never replaces the knowledge bank. Security verdicts still escalate to `ravenclaude-core/security-reviewer`.

## Technical-runtime tier — LSP code intelligence (bundled config, binary installed separately)

Salesforce is a **code** domain, so the plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) giving agents real-time code intelligence instead of grep-and-guess. **The plugin ships the *config*, not the *binary*** — a missing server is loud-but-non-fatal (shows `Executable not found in $PATH` in the `/plugin` Errors tab; that one language degrades, everything else keeps working).

| Language | Server | `command` | Consumer install (separate) `[verify-at-use]` |
|---|---|---|---|
| Apex | Apex Language Server (`apex-jorje-lsp.jar`) | `java -cp ${APEX_JORJE_LSP_JAR} … apex.jorje.lsp.ApexLanguageServerLauncher` | **Has a hard Java + jar dependency.** Needs JDK ≥ 11 (JDK 21 recommended). The jar ships *inside* the Salesforce Apex VS Code extension — there is no standalone published binary; extract `apex-jorje-lsp.jar` from the extension and set `APEX_JORJE_LSP_JAR` to its absolute path. The launch class + classpath form are the documented integration path. |
| LWC (JS/TS) | typescript-language-server | `typescript-language-server --stdio` | `npm install -g typescript-language-server typescript` |
| LWC (HTML templates) | vscode-html-language-server | `vscode-html-language-server --stdio` | ships with `vscode-langservers-extracted` (`npm install -g vscode-langservers-extracted`) |

> The Apex entry is **honest about its dependency**: it cannot run from a bare `PATH` like pyright/gopls — it needs Java *and* a consumer-supplied jar path (`${APEX_JORJE_LSP_JAR}`), so it is shipped as a real-but-prerequisite-gated config, not a broken or fabricated one. There is no separate maintained SOQL-server worth shipping; SOQL lives inside `.cls`/`.trigger` files covered by the Apex server. Verified 2026-06-05 against the Salesforce Extensions for VS Code "Apex Language Server" docs (launch class `apex.jorje.lsp.ApexLanguageServerLauncher`, `apex-jorje-lsp.jar`, Java ≥ 11 / JDK 21) and the nvim-lspconfig `apex_ls` reference. Re-confirm the jar name and Java floor at use — both are version-volatile.

## Recommended (not bundled) MCP server — the Salesforce DX MCP Server

This plugin **bundles no MCP server**, on purpose. Per [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**; every Salesforce MCP path is **org-credentialed**, which is recommend-not-bundle.

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **Salesforce DX MCP Server** ([`@salesforce/mcp`](https://www.npmjs.com/package/@salesforce/mcp), first-party, pilot/beta) | Requires an **authorized org** — you must pass `--orgs` and the org must already be authed (`sf org login web` / an External Client App for OAuth). It is **credentialed + per-tenant** → fails the zero-config bar. Toolsets cover SOQL, metadata deploy, tests, admin — read **and** write. | `npx -y @salesforce/mcp@<tested-version> --orgs <alias>` after `sf org login web`. The org auth is a **reference** (the authed-org alias / env), **never a literal secret in `plugin.json`**. Gate adoption through `ravenclaude-core/security-reviewer`; a write verb from a non-allowlisted server is a pre-LLM deny (Gate 25). |
| **Salesforce Hosted MCP Servers** (first-party, e.g. `sobject-reads` / `sobject-mutations`) | Per-user **OAuth 2.0 + PKCE** via an External Client App; admin must enable the server in-org. Even the read-only `sobject-reads` enforces per-user auth → not zero-config. | Consumer-configured via the Hosted MCP setup (ECA + activate server); secret as a reference, `security-reviewer` sign-off. |

**Why none are bundled (the load-bearing reasoning):** there is **no zero-config, no-auth Salesforce server** to bundle — `@salesforce/mcp` and the hosted servers all dereference org credentials and most are write-capable, which the doctrine's decision table sends straight to **recommend, don't bundle** (with the secret kept a reference and a `security-reviewer` gate). No server was invented to fill the slot. Verified 2026-06-05 against the `@salesforce/mcp` npm/GitHub listings and the Salesforce *Hosted MCP Servers* developer docs; package name, version (0.26.9, pilot/beta), and the OAuth/ECA flow are volatile — re-confirm at use.

## Value-add completeness (build-out 2026-06-05)

This plugin was **missed** in the earlier marketplace-wide enrichment and had no scenarios bank. Disposition of every value-add menu item (built vs. recorded N-A with reason):

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 scenarios + `scenarios/README.md` index (SOQL-in-loop 101, trigger-recursion runaway, guest-user data exposure, Agentforce non-deterministic misfire), 9-field schema, volatile facts `[verify-at-build]`-tagged. Each maps to an existing canonical rule + tree. |
| 2 | **Decision-tree knowledge** | **BUILT (1 new file, 2 trees)** — `knowledge/automation-density-decision-trees.md` (where-does-this-automation-go on a busy object + order-of-execution). Chosen because the plugin's ~20 existing trees already cover async/security/trigger/SOQL/bulk/integration/LDV/packaging/Agentforce; *automation density + order-of-execution* (house opinion #12) was the clear gap. |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — see § above. `@salesforce/mcp` + Hosted MCP are all org-credentialed (OAuth/ECA, mostly write-capable); no zero-config no-auth Salesforce server exists. Documented the `npx … --orgs` / Hosted-MCP paths with secret-as-reference + `security-reviewer` gate. No invented servers. |
| 4 | **LSP server** | **BUILT** — `.lsp.json` (Apex Language Server + LWC JS/TS + LWC HTML), wired via `plugin.json` `lspServers`. The Apex entry honestly carries its Java + consumer-supplied-jar dependency (`${APEX_JORJE_LSP_JAR}`); it is prerequisite-gated, not broken. |
| 5 | **Runnable script** | **BUILT** — `scripts/apex_governor_smell.py` (stdlib-only, ruff-clean): heuristic SOQL/DML-in-loop scanner over a tree of `.cls`/`.trigger` files (the plugin's #1 house opinion). Complements the single-file advisory hook by scanning a whole directory; decision-support, not a guarantee. |
| 6 | **bin/ · monitors · output-styles · settings defaults · themes** | **N-A** — none clears the "groundable + broadly valuable, doesn't duplicate the advisory hook / new script / skills" bar; the plugin is config-light by design. |
| 7 | **skills/hooks/commands/templates** | **Coverage sufficient** — 5 skills, 8 commands, 5 templates, 1 advisory hook already cover SOQL authoring, LWC scaffold, data-load, release pipeline, bulk REST. The new scenarios + density trees + script extend reach without a new agent (team-growth-as-knowledge house rule). |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top `0.6.0` entry. No `NOTICE.md` (nothing third-party is bundled; the script is original stdlib-only, LSP/MCP packages are referenced not vendored). |

## Milestones

- **v0.1.0** — initial roster (5 agents), 9 knowledge docs, 5 skills, 5 templates, anti-pattern hook.
- **v0.4.1** — fixed a dead cross-plugin seam: `apex-engineer` escalated generic test authoring to `ravenclaude-core/test-author`, which does not exist (the core test agent is `tester-qa`). Renamed all 5 references — incl. the machine-read `works_with` frontmatter that drives routing — to `ravenclaude-core/tester-qa` (two-panel audit 2026-05-31).
- **v0.6.0** — value-add build-out (the plugin was missed in the earlier pass): scenarios bank (4 scenarios + README), automation-density + order-of-execution decision trees, `.lsp.json` (Apex + LWC LSP), `scripts/apex_governor_smell.py`, CHANGELOG. MCP dispositioned recommend-not-bundle (every Salesforce server is org-credentialed). See § "Value-add completeness (build-out 2026-06-05)".
