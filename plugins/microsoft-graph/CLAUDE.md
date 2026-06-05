# Microsoft Graph Plugin — Team Constitution

> Team constitution for the `microsoft-graph` Claude Code plugin — specialist agents for the Microsoft Graph API: the **API** craft (querying, paging, batching, delta, throttling, SDKs), the **identity** craft (Entra app registration, permissions/scopes/consent, auth flows, least-privilege), and the **workloads** craft (users/groups, mail/calendar, Teams, files, change notifications).
>
> **Orientation:** domain-specific to Microsoft Graph development. For the domain-neutral team inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`graph-api-engineer`](agents/graph-api-engineer.md) | OData query shaping (`$select`/`$filter`/`$expand`/`$search`/`$count`), paging (`@odata.nextLink`), `$batch`, change tracking (delta queries), throttling/429 + `Retry-After` discipline, the Graph SDKs (.NET/JS/Python/Java), `advanced query` (ConsistencyLevel + `$count`). | "build this Graph query/call"; "this is throttling (429)"; "page through all results"; "track changes with delta"; "batch these requests" |
| [`graph-identity-engineer`](agents/graph-identity-engineer.md) | Entra app registration, **delegated vs application** permissions, scopes + admin consent, least-privilege permission selection, auth flows (auth-code + PKCE, client-credentials, on-behalf-of, device-code), certificate vs secret creds, token caching. | "which permission do I need (and is it delegated or app)?"; "set up app-only auth"; "consent is failing"; "least-privilege this scope list" |
| [`graph-workloads-engineer`](agents/graph-workloads-engineer.md) | The workload surfaces — users/groups & directory, mail/calendar (Outlook), Teams (chat/channel/lifecycle), SharePoint/OneDrive files (drive items, large-file upload sessions), and **change notifications** (subscriptions, lifecycle notifications, rich notifications + encryption, renewal). | "read/send mail"; "create a Teams message"; "upload a large file"; "subscribe to changes / webhook"; "list group members at scale" |

Three coherent personas (API / identity / workloads). Per the marketplace house rule, this plugin ships specialist *doing*-agents and forks **no** core *review* role — **all auth/permission/security verdicts escalate to `ravenclaude-core/security-reviewer`** (over-privileged scopes, secret handling, consent posture, notification-payload decryption keys). **Sub-agents do not spawn other sub-agents** — only the Team Lead delegates.

---

## 2. Routing rules (Team Lead)

- **"Build/shape this Graph query, page it, batch it, delta it, it's throttling"** → `graph-api-engineer`.
- **"Which permission / delegated vs app / consent / auth flow / least-privilege"** → `graph-identity-engineer` (escalate the permission-scope verdict to security-reviewer).
- **"Mail/calendar/Teams/files/users-groups/webhook-subscription"** → `graph-workloads-engineer`.
- **Copilot (Graph) *connectors* / external-item ingestion for Copilot** → seam to **`microsoft-365-copilot/graph-connector-engineer`** (that plugin owns the Copilot connector surface; this plugin owns the Graph API broadly — cross-link, don't duplicate).
- **Entra *tenant/identity infrastructure* (Conditional Access, PIM, B2B/B2C tenant design)** → escalate to **`azure-cloud/entra-identity`**. This plugin owns the *app-on-Graph* identity surface, not tenant identity governance.

---

## 3. Cross-cutting house opinions (the agents enforce)

1. **Least-privilege permissions, always.** Pick the narrowest scope that works; prefer delegated over application unless the scenario is daemon/no-user; never request `.ReadWrite.All` when `.Read` or a resource-scoped permission suffices. This is a security control and escalates to review.
2. **Delegated vs application is a design decision, not a default.** State which one, and why (user-context vs daemon), before writing auth code.
3. **Select what you need; never `GET /users` bare.** Always `$select` explicit fields; `$filter`/`$search` server-side; never page the whole tenant to filter client-side.
4. **Page everything; assume more than one page.** Follow `@odata.nextLink` to exhaustion — a first-page result is not "all results."
5. **Respect throttling as a contract.** Honor `429` + `Retry-After` with backoff + jitter; batch with `$batch` to cut round-trips; don't hammer.
6. **Track changes with delta, don't re-pull.** For "what changed," use delta queries / change notifications, not periodic full reads.
7. **Subscriptions are stateful and expire.** Every change-notification subscription needs validation handling, a renewal strategy before expiry, lifecycle-notification handling, and (for rich payloads) decryption-key management — the last escalates to security review.
8. **Secrets are certificates, not strings, in production.** Prefer certificate credentials / managed identity over client secrets; never embed a secret in code or a notification URL.
9. **Volatile claims carry a retrieval date** (beta-vs-v1.0 endpoints, permission names, throttling limits, metered/PAYG APIs) and are re-verified before quoting — and **never ship `/beta` to production** without flagging it.

---

## 4. Anti-patterns the agents flag

- An application permission where a delegated one (user context) was correct — or vice-versa.
- A `.ReadWrite.All`/`.All` scope where a narrower or resource-scoped permission would do (over-privilege).
- `GET` a collection with no `$select` (over-fetch) or client-side filtering of a server-filterable query.
- Code that reads only the first page (missing `@odata.nextLink`).
- No `429`/`Retry-After` handling; no backoff; N serial calls where `$batch` fits.
- Periodic full re-reads where a delta query / change notification was the right tool.
- A subscription with no renewal/lifecycle handling (silently dies) or rich notifications with mishandled decryption keys.
- A client secret in source / config / a notification URL; a long-lived secret where a certificate/managed identity belongs.
- A `/beta` endpoint shipped to production with no flag; a permission/limit quoted with no retrieval date.

---

## 4a. Automated checks (hook)

The `hooks/` directory ships [`check-graph-anti-patterns.sh`](hooks/check-graph-anti-patterns.sh) — a **PreToolUse** Edit/Write/MultiEdit hook on Graph code/request files (`.cs`/`.ts`/`.tsx`/`.js`/`.jsx`/`.py`/`.ps1`/`.http`) that flags four mechanically-detectable violations of §3/§4:

| Check | What it catches | Rule |
|---|---|---|
| `/beta` endpoint | `graph.microsoft.com/beta` referenced in code | §3 #9 — never ship `/beta` to production without flagging it |
| Hardcoded client secret | `client_secret`/`ClientSecret = "<literal>"` (not an env/Key-Vault reference) | §3 #8 — secrets are certificates/managed identity, never strings; escalates to `security-reviewer` |
| Broad write-`.All` scope | `Directory.*.All` / a `*.ReadWrite*.All` permission string | §3 #1 — confirm least-privilege; prefer delegated + narrowest/resource-scoped |
| Advanced query w/o `ConsistencyLevel` | `$search=`/`$count=true` with no `ConsistencyLevel: eventual` | §3 #3/#4 — the classic Graph `400`; advanced queries need the eventual header + `$count` |

**Advisory by default** (prints to stderr, exits 0). Set `MSGRAPH_STRICT=1` to make violations blocking (exit 2). The hook is conservative — it only fires on Graph-relevant code/request file extensions, so unrelated edits aren't flagged. The plugin's [`hooks/hooks.json`](hooks/hooks.json) wires it in automatically when the plugin is installed.

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

Inherits the CGP from `ravenclaude-core`. Before an agent says "I can't" or asserts a Graph fact (a permission name, an endpoint, a throttling limit, delegated-vs-app applicability), it must: (1) check the knowledge bank + decision trees; (2) **traverse the relevant `## Decision Tree:` section** before choosing (permission type, auth flow, query vs delta vs subscription, paging/batching) — don't keyword-match; (3) try the next-easiest defensible path before declaring blocked; (4) escalate with the mandatory phrasing. Permission names, endpoint availability (v1.0 vs beta), and throttling numbers are **volatile** and carry inline `[verify-at-build]` / `[unverified — training knowledge]` markers per the Claim-Grounding discipline. See [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).

---

## 6. Output Contract

```
Goal: <the Graph operation, in resource terms>
Resource & version: <endpoint; v1.0 vs beta + why; the resource type>
Permission: <exact permission(s); DELEGATED or APPLICATION + why; least-privilege justification — escalate to security-reviewer>
Auth flow: <auth-code+PKCE / client-credentials / OBO / device-code + why; cert vs secret>
Call: <method + URL + $query params; paging plan; $batch if applicable; SDK snippet>
Resilience: <429/Retry-After handling; backoff; delta/subscription if "what changed">
Verdict: <plain-language outcome + the security/consent notes>
```

Plus the cross-plugin **Structured Output Protocol** JSON block ([`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)).

---

## 7. Knowledge bank & best practices

- [`knowledge/`](knowledge/) — reference docs with `Last verified:` dates + Mermaid **decision trees** (permission type, auth flow, query vs delta vs subscription, paging/batching, throttling response, large-file upload, **and runtime error-disposition** — which HTTP status → which non-interchangeable fix). The agents traverse these before choosing a method.
- [`best-practices/`](best-practices/) — named, citable rules (one per file), grounded in the knowledge bank and surfaced in the marketplace repo-guide + dashboard Guidance tab.
- [`scenarios/`](scenarios/) — dated, scope-tagged, **unverified** engagement narratives (the marketplace scenarios pattern; see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)). Surface a matching scenario only as a *secondary* source, behind the mandatory unverified-scenario preamble, never overriding the cited knowledge bank. Scenarios carry no secrets, tenant IDs, app/client IDs, or credentials (§3 #8).
- [`scripts/graph_scope_analyzer.py`](scripts/graph_scope_analyzer.py) — a stdlib-only (no network, no tenant contact) **scope analyzer/linter**: feed it a permission list or a JWT access token (claims-only, no signature verification) and it flags the over-privilege anti-patterns from §3 #1 / §4 and suggests narrower alternatives, exiting `1` when a scope must escalate to `security-reviewer` (so it's pipeline-usable). It is **decision-support, not a security sign-off**; owned by `graph-identity-engineer`.

## 7a. Bundled MCP server — `microsoft-learn` (Microsoft Learn MCP)

The plugin declares one MCP server in `plugin.json`: **`microsoft-learn`**, the Microsoft Learn MCP Server — a remote HTTP endpoint at `https://learn.microsoft.com/api/mcp` (open-source tooling repo [`MicrosoftDocs/mcp`](https://github.com/MicrosoftDocs/mcp), MIT). It exposes **three read-only tools**: `microsoft_docs_search`, `microsoft_code_sample_search`, and `microsoft_docs_fetch`. **Read-only:** it searches/fetches *public* Microsoft documentation only — it does **not** touch the consumer's tenant, mailboxes, files, directory, code, or any user data, and it writes nothing.

**Why it's the right bundle for *this* plugin.** A Microsoft Graph plugin's #1 accuracy risk is a **volatile fact recalled from training** — a permission name, a v1.0-vs-beta endpoint, a throttle limit, a subscription max-expiry. The Learn MCP lets every agent **verify a volatile fact against current first-party docs** rather than asserting it from memory — the tool form of the §3 #9 / §5 `[verify-at-build]` discipline. It clears the zero-config-read-only bundling bar in [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md): zero per-consumer state (fixed public endpoint), no auth (no secret to bundle/leak), read-only, first-party documentation. (Same server, same shape as `microsoft-365-copilot` §11 — each plugin declares its own.)

**Consumer prerequisite — none.** Remote HTTP, no auth, nothing to install. If the network can't reach `learn.microsoft.com`, the server shows `failed` in `/mcp` and the error surfaces in the `/plugin` Errors tab; Claude Code and every other tool still work (**loud-but-non-fatal**). **If the Learn tools aren't responding, check `/mcp` and the `/plugin` Errors tab first** — the usual cause is no network egress, not a broken server. No local subprocess, so no PATH/`python -m` fallback.

**Which agent owns it?** **All three** call it situationally — a shared grounding tool, not one specialist's. **Trigger:** when about to state a version-, endpoint-, permission-, or limit-volatile Graph fact, **search/fetch Learn first** instead of recalling it.

**Boundary** — `microsoft-learn` is for **public Microsoft documentation only**. It is **NOT** a connection to the consumer's tenant or the Microsoft Graph; it cannot read tenant data, send mail, or create a subscription.

**NOT bundled — credentialed Graph MCPs (recommend, evaluate-first).** A tenant-acting Graph MCP (e.g. **Lokka**, `@merill/lokka`, MIT, `0.1.7` `[verify-at-use]`) is **per-tenant + Entra-authenticated + write-capable** (`POST`/`PUT`/`PATCH`/`DELETE`), so it is "recommend, don't bundle," and any write scope is an **Absolute-rule `security-reviewer` gate** before it ships (Gate 25 `mcp.allowed_servers`). Setup + the secret-as-a-reference rule are documented in [`NOTICE.md`](NOTICE.md); never bundle a per-tenant credentialed server.

See [`NOTICE.md`](NOTICE.md) for attribution + the consumer-side `claude mcp add` override.

---

## 8. Escalating out of the Microsoft Graph team

- **`ravenclaude-core/security-reviewer`** — permission scope, consent posture, secret/credential handling, notification-payload decryption keys.
- **`microsoft-365-copilot/graph-connector-engineer`** — Copilot (Graph) connectors / external-item ingestion for Copilot.
- **`azure-cloud/entra-identity`** — Entra tenant identity governance (Conditional Access, PIM, B2B/B2C).
- **`power-platform`** — Dataverse data when the source/target is Power Platform.
- **`ravenclaude-core/documentarian`** / **`project-manager`** — deliverables / engagement RAID.

---

## Value-add completeness (build-out 2026-06-05)

PR #315 added the consolidated knowledge decision-trees, `best-practices/`, the skills, and the templates (and the `scenarios/README.md` index). This build-out fills the net-new gaps. Every menu item is dispositioned honestly below.

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — the 4 scenarios the `scenarios/README.md` index already referenced but that were never created: [`throttling-429-retry-after-cascade`](scenarios/2026-06-05-throttling-429-retry-after-cascade.md), [`app-only-consent-failure`](scenarios/2026-06-05-app-only-consent-failure.md), [`delta-query-410-resync`](scenarios/2026-06-05-delta-query-410-resync.md), [`subscription-silent-expiry`](scenarios/2026-06-05-subscription-silent-expiry.md). 9-field schema, Learn-cited, dated, no secrets/tenant IDs. |
| 2 | **knowledge/ decision-trees** | **BUILT (complementing #315)** — [`knowledge/api-error-disposition-decision-trees.md`](knowledge/api-error-disposition-decision-trees.md): two new **runtime-tier dispositioning** trees (HTTP-status → non-interchangeable fix; silent-vs-hard failure / "is green actually healthy?"). #315's trees are all *design-time* (choose the call); these are the *recovery-time* complement and directly disposition all 4 new scenarios. The brief's other suggestions (delegated-vs-application, delta-vs-poll-vs-webhook) were **already covered** by #315 — adding them would duplicate. |
| 3 | **skill / template (the flagged gap)** | **BUILT (template)** — [`templates/graph-permission-matrix.md`](templates/graph-permission-matrix.md): a fillable capability→permission decision matrix (type/consent/narrower-alternative/runtime-disposition) that feeds the existing app-registration worksheet. Distinct from the `permission-least-privilege-review` *skill* (an audit playbook) and the `graph-app-registration` *template* (a registration record) — it's the *decision artifact* between them, and it wires in the new error-disposition tree. (The brief noted "missing skills/ and templates/" — that was pre-#315; both dirs now exist with strong coverage, so a 5th skill would gold-plate.) |
| 4 | **Bundled MCP** | **BUILT (one read-only server) + recommend-not-bundle (credentialed)** — bundled **`microsoft-learn`** (remote HTTP, no auth, read-only, MIT; verified real 2026-06-05) with `x-mcpAttribution` + [`NOTICE.md`](NOTICE.md), mirroring the `microsoft-365-copilot` precedent. **Lokka** (`@merill/lokka`, MIT, write-capable, per-tenant Entra auth) is documented **recommend-not-bundle** + `security-reviewer` gate. No invented servers. |
| 5 | **LSP server** | **N-A** — this plugin's value is Graph *design/API* guidance, not editing a single source language; agents emit snippets across .NET/JS/Python/PowerShell/HTTP, so no one language server fits. (Contrast `backend-engineering`, which ships `.lsp.json` because it *is* a code-authoring domain.) |
| 6 | **Runnable script (`scripts/`)** | **BUILT** — [`scripts/graph_scope_analyzer.py`](scripts/graph_scope_analyzer.py): stdlib-only scope/JWT-claims analyzer flagging over-privilege + suggesting narrower alternatives, exit `1` on mandatory escalation (CI-usable). Ruff-clean. Real value: turns the §4 anti-pattern list into a deterministic check. |
| 7 | **bin/ · monitors · output-styles · settings · themes** | **N-A** — no groundable broadly-valuable instance. `bin/` would duplicate the advisory hook + the new script; there's nothing to monitor (no build/long-running process); output-styles/themes overlap the §6 Output Contract; no tool-permission surface beyond `ravenclaude-core`'s. |
| 8 | **CHANGELOG.md / NOTICE.md** | **BUILT** — `CHANGELOG.md` added with a top entry; `NOTICE.md` added because a third-party MCP server is now bundled (required by the attribution gate). |

## Milestones

- **v0.3.2** — pre-build-out: 3 agents, 5 skills, 4 templates, 5 commands, 1 advisory hook, 3-file decision-tree knowledge bank, best-practices library, scenarios README + index (#315).
- **v0.4.0** — value-add build-out: 4 scenarios (filling the #315 index), the runtime error-disposition decision-tree knowledge file (2 trees), the permission-matrix template, the stdlib scope-analyzer script, the bundled `microsoft-learn` read-only MCP (+ NOTICE.md + recommend-not-bundle doctrine for Lokka), and CHANGELOG.
