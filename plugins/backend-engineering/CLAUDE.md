# Backend Engineering Plugin — Team Constitution

> Team constitution for the `backend-engineering` Claude Code plugin — **4** specialist agents for the application/service craft behind an API — domain modeling and service boundaries, business logic, caching, background jobs and messaging, the data-access layer, and backend reliability — distinct from the API contract and the database schema. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`backend-architect`](agents/backend-architect.md) | Service/application architecture: domain modeling, service boundaries (monolith vs microservices, where to split), inter-service communication (sync vs async), and the overall backend shape | "monolith or microservices?", "where should we split this service?", "design our backend architecture", "sync call or event?" |
| [`service-implementation-engineer`](agents/service-implementation-engineer.md) | Business-logic implementation: clean service/use-case layering, error handling and result modeling, validation, idempotency keys, and structuring code so logic is testable and the framework stays at the edges | "implement this business logic", "how should I structure this service?", "handle errors properly", "make this idempotent" |
| [`backend-data-access-engineer`](agents/backend-data-access-engineer.md) | The data-access layer: repository/data-mapper pattern, transaction boundaries, ORM use without N+1, the outbox pattern, caching (cache-aside, invalidation, stampede protection), and read/write separation in app code | "our ORM generates N+1 queries", "add caching to this", "where should the transaction boundary be?", "implement the outbox pattern" |
| [`backend-reliability-engineer`](agents/backend-reliability-engineer.md) | Backend resilience and async work: timeouts, retries with exponential backoff + jitter (idempotent only), circuit breakers, bulkheads, graceful degradation, and background-job/worker design (queues, DLQs, idempotent consumers) | "add retries and timeouts", "a slow dependency takes us down", "design our background jobs", "add a circuit breaker" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **A monolith until proven otherwise.** Start with a well-modularized monolith; split into services only when a real scaling, team-autonomy, or deploy-isolation need appears. Premature microservices buy distributed-systems pain for free.
2. **Model the domain, then the code.** Boundaries follow the business, not the database tables. A service/module that owns a coherent capability beats one that wraps a table.
3. **The data-access layer is owned, not sprinkled.** Queries live behind a repository/data layer with explicit transaction boundaries — not raw ORM calls scattered through controllers. This is where N+1 and accidental long transactions breed.
4. **Idempotency is mandatory for anything retried.** Every async worker, webhook handler, and retried call has a dedup key. Retries are guaranteed by the network; non-idempotent retries corrupt.
5. **Cache deliberately; invalidation is the hard part.** Decide what's cacheable, the TTL, the invalidation trigger, and the stampede protection up front. A cache without an invalidation story serves stale data as a feature.
6. **Fail fast and degrade gracefully.** Timeouts on every outbound call, retries with backoff+jitter (idempotent only), circuit breakers, and a defined degraded mode. A backend with no timeouts cascades one slow dependency into total failure.

## 3. Seams (the bridges to neighbouring plugins)

- **The API contract (paradigm, OpenAPI/AsyncAPI, versioning, pagination semantics)** → `api-engineering`; this team implements the service *behind* the contract.
- **The database schema, indexes, query plans, and migrations** → `database-engineering`; we own the data-access *code* and transaction boundaries, they own the schema and tuning (we flag ORM-generated N+1 to them).
- **Where the service runs, builds, and deploys** → `devops-cicd` + the cloud plugin + `cloud-native-kubernetes`.
- **Timeouts/retries/SLOs as an operational concern** → `observability-sre` (we implement the resilience patterns; they set the SLOs they protect).
- **Authentication of the caller and end-user identity** → `auth-identity`; authorization-in-the-service logic is ours, the identity is theirs.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer): [`knowledge/backend-engineering-decision-trees.md`](knowledge/backend-engineering-decision-trees.md) (monolith-vs-service, caching, sync-vs-async, extract-now-vs-later) and [`knowledge/data-store-and-api-paradigm-decision-trees.md`](knowledge/data-store-and-api-paradigm-decision-trees.md) (SQL-vs-NoSQL store selection, REST-vs-GraphQL-vs-gRPC). **Traverse the relevant Mermaid tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (idempotent payments, N+1 + pool exhaustion, zero-downtime migration, poison-message queues). Secondary source; never replaces the knowledge bank.

## 6. Technical-runtime tier — LSP code intelligence (bundled config, binary installed separately)

Backend engineering is a **code** domain, so the plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) giving agents real-time code intelligence — go-to-definition, find-references, diagnostics — instead of grep-and-guess. Verified against the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference) (LSP servers section, 2026-06-05); LSP support landed in Claude Code 2.0.74 `[verify-at-use]`.

It configures three language servers covering this plugin's example languages (Node/Python/Go):

| Language | Server | `command` | Install (consumer, separate) |
|---|---|---|---|
| Python | Pyright | `pyright-langserver --stdio` | `pip install pyright` **or** `npm install -g pyright` |
| TypeScript/JS | typescript-language-server | `typescript-language-server --stdio` | `npm install -g typescript-language-server typescript` |
| Go | gopls | `gopls serve` | `go install golang.org/x/tools/gopls@latest` `[verify-at-use]` |

**The plugin ships the *config*, not the *binary*.** Per the plugins reference: "LSP plugins configure how Claude Code connects to a language server, but they don't include the server itself." If a server's binary isn't on `PATH`, it shows `Executable not found in $PATH` in the `/plugin` Errors tab and that one language degrades — Claude Code and all other tools keep working (the same **loud-but-non-fatal** posture as a missing MCP prerequisite). LSP servers start only after the workspace is trusted, and `/reload-plugins` is needed to pick up a config change mid-session.

> Package names and the `--stdio` / `serve` invocations are verified against the official LSP-plugin table in the plugins reference (`pyright-lsp`, `typescript-lsp`) and the `gopls` example in the same doc (2026-06-05). Re-confirm the `gopls` install path and the 2.0.74 LSP-support version at use — both are version-volatile.

## 7. Recommended (not bundled) MCP servers — code/git/db context

This plugin **bundles no MCP server**, on purpose. Per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**; a write-capable or per-consumer-configured server is **recommend-not-bundle**. Every backend-useful server fails the zero-config-read-only bar — so we document the recommended `claude mcp add …` paths instead of shipping an `mcpServers` entry.

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **Filesystem** ([`@modelcontextprotocol/server-filesystem`](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem), MIT, first-party reference) | Needs a **consumer-specific allowed-directory path** (can't hardcode), and is **write-capable** (it can create/move/delete files) → both disqualify bundling. | `claude mcp add fs -- npx -y @modelcontextprotocol/server-filesystem /path/to/allowed/dir` — pass **only** the dirs the agent may touch; the path arg is the access boundary. |
| **Git** ([`mcp-server-git`](https://github.com/modelcontextprotocol/servers/tree/main/src/git), MIT, first-party reference) | Needs a **consumer-specific repo path**, and exposes **write** verbs (commit, etc.) → recommend-not-bundle; prefer the read/search subset. | `claude mcp add git -- uvx mcp-server-git --repository /path/to/repo` |
| **PostgreSQL (read-only)** | A backend engineer wants live schema/row context, but it is **per-tenant + authenticated** (a DB connection string = a secret) → never bundle; secrets stay a **reference**, never a literal. The Anthropic reference `@modelcontextprotocol/server-postgres` is **archived/deprecated** (May 2025; SQL-injection fix never shipped) — **do not recommend it.** Point consumers at a maintained read-only community fork (vet license/activity at adoption) or Google's MCP Toolbox for Databases, gated through `ravenclaude-core/security-reviewer`. | Consumer-configured, secret as a reference (env-var name / vault URI), **read-only transaction mode**, `security-reviewer` sign-off before adoption. |

**Why none are bundled (the load-bearing reasoning):** the filesystem and git reference servers are MIT and first-party, but both need a consumer-specific path *and* carry write verbs — the rule's decision table sends "per-consumer config OR write-capable" to **recommend, don't bundle**. The Postgres path additionally handles a secret (a connection string), which is an Absolute-rule "reference-not-literal" + `security-reviewer` situation. If a genuinely zero-config, read-only, broadly-useful backend server appears, revisit this with the doctrine block in [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) Step 4.

> Verified 2026-06-05: official MCP reference-server set (filesystem, git, fetch, memory, sequential-thinking, time) and the archival of the postgres/sqlite/redis reference servers per the [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) repo; the `@modelcontextprotocol/server-postgres` deprecation per its npm/Docker listings. Package names, archival status, and the MCP Toolbox version are volatile — re-confirm at use.

## Value-add completeness (pilot build-out 2026-06-05)

Disposition of every value-add menu item (built vs. recorded N-A with reason):

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 scenarios (idempotent payments, N+1 + pool exhaustion, zero-downtime migration, poison-message queue) matching the existing `scenarios/README.md` index + 9-field schema. |
| 2 | **Decision-tree knowledge** | **BUILT** — `knowledge/data-store-and-api-paradigm-decision-trees.md`: SQL-vs-NoSQL store selection + REST-vs-GraphQL-vs-gRPC. Chosen because the existing tree file already covers monolith/cache/sync-async/extract — these two were the gaps. |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §7. No server clears the zero-config + read-only bar (filesystem/git need a path + are write-capable; Postgres is per-tenant + secret-handling; the Anthropic postgres reference is deprecated). Documented the recommended `claude mcp add` paths instead. No invented servers. |
| 4 | **LSP server** | **BUILT** — `.lsp.json` (pyright / typescript-language-server / gopls), wired via `plugin.json` `lspServers`. Genuinely useful for a code domain; binaries install separately (§6). |
| 5 | **bin/ executables** | **N-A** — no `rc-*` script clears the rule's "namespace + prefer Bash-tool skills" bar better than the existing advisory hook (`hooks/check-backend-engineering-anti-patterns.sh`) + skills already do. A contract/migration linter would duplicate `api-engineering` / `database-engineering` lanes. |
| 6 | **userConfig / output-styles / monitors / settings defaults / themes** | **N-A** — no groundable, broadly-valuable instance. An API-review output-style would overlap the agents' Output Contract; the plugin is config-light by design. |
| 7 | **skills/hooks/commands/templates** | **Coverage sufficient** — 4 skills, 4 commands, 4 templates, 1 advisory hook already cover boundary design, implementation, data-access/caching, and resilience. Idempotency is covered across a template + best-practice + the `backend-implementation` skill; a 5th skill would gold-plate. |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top entry for this build-out. No `NOTICE.md` (nothing third-party is bundled). |
