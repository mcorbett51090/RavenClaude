# GitHub MCP tool surface — scope it least-privilege before you drive GitHub through it

> **Last verified:** 2026-08-12. **Refresh trigger:** re-verify the toolset / read-only / scope facts if `github/github-mcp-server`'s README changes its allow-list, read-only, or auth model; the gold-standard evidence was captured via `gh api` + WebFetch on 2026-08-12.

This file is the **least-privilege authoring reference** for the GitHub API surface an agent drives through the official GitHub MCP server: what it is, how remote and local differ, the two levers that bound its blast radius, which surface to **request or be granted** for a given task, and where the command-review layer *enforces* the scope this file only *advises*. It exists because the marketplace previously shipped no consumer-facing GitHub-MCP tool-surface / least-privilege reference — only the runtime PR-landing route ladder **[obs] claim #34**.

**Who consumes it:** an autonomous agentic CLI (Claude Code, GitHub Copilot CLI, …) that will operate a GitHub repo as the actor — opening PRs, filing issues, reviewing, reading commits. Each point below carries its provenance.

**Provenance legend:** **[obs] claim #N** = grounded in a verified claim from the `claude-github-primary` gold-standard research (source-stamped there, checked 2026-08-12) · **[obs] — CLAUDE.md §…** = grounded in an in-repo file read this session · **[inf]** = a conclusion drawn from the named evidence · **[unverified — training knowledge]** = recalled, not checked this session.

---

## 1. What this is — the map, and why you scope it

- **`github/github-mcp-server` is GitHub's official MCP server** (MIT, active) — the first-party primitive that gives an agent *structured* GitHub tools (issues, pull requests, commits, code scanning, …) instead of raw shell or hand-rolled API calls **[obs] claim #14**.
- The server exposes a **large** tool surface. An agent does not need all of it for any one task, and the docs make **scoping the headline, not a footnote**: *grant only necessary permissions* **[obs] claim #15**.
- The least-privilege pattern this file teaches — a **toolset allow-list + read-only mode + minimum token scopes**, and OIDC / short-lived credentials over long-lived secrets — is the transferable practice extracted from the gold-standard set **[inf] / [obs] claim #45**.

---

## 2. Remote vs local — two deployments, one precedence rule

| | **Remote** (GitHub-hosted) | **Local** (self-hosted) |
|---|---|---|
| How it runs | GitHub-hosted MCP endpoint | Docker container or binary you run |
| Auth | OAuth (browser flow); the token is held **in memory only** | a token you supply to the process |
| Best for | quick start, no infra to run | air-gapped / policy-controlled environments, pinned versions |

**[obs] claim #16**

- **A Personal Access Token takes precedence over OAuth.** When a PAT is present, the server uses it *instead of* the OAuth token — so if you set a PAT, **its scopes are the effective blast radius**, and an over-scoped PAT silently overrides a carefully-scoped OAuth grant **[obs] claim #16 / [inf]**.
- Practical consequence: decide the token *first*, scope it to the task, and don't leave a broad PAT set "for convenience" next to an OAuth flow **[inf]**.

---

## 3. The two blast-radius levers — both are also context-size levers

The server ships two independent knobs. **Set both as tight as the task allows.**

| Lever | What it does | Blast-radius effect | Context-size effect |
|---|---|---|---|
| **Toolset allow-list** (`--toolsets`) | exposes only the named toolsets | fewer tools an injected instruction can reach | fewer tool schemas in the prompt |
| **Read-only mode** | drops every write verb | the agent structurally *cannot* mutate | smaller, read-only surface |

**[obs] claim #15**

- The README states enabling only the toolsets you need **"can help the LLM with tool choice and reduce the context size"** — so the allow-list is *simultaneously* a routing/clarity lever and a least-privilege lever; you are not trading one for the other **[obs] claim #15**.
- Go finer than a toolset when you can: expose the **specific tools** a task needs. The gold-standard daily-report example grants exactly two read tools — `mcp__github__list_commits` and `mcp__github__list_issues` — via an `--allowedTools` list, nothing else **[obs] claim #15**.
- **Prefer read-only wherever the task is read-only.** A summarize / triage / report task never needs a write verb; granting one anyway is pure downside **[inf] / [obs] claim #45**.

---

## 4. Decision table — MCP server vs `gh` CLI vs raw API (which surface to *request*)

**This table answers a provisioning question: which surface should the agent be *granted / request* for a task.** It is a *different question* from "which route *works* this session," which the runtime probe-first route ladder answers — see [remote-mcp-pr-landing.md](remote-mcp-pr-landing.md). Keep them separate: you might *grant* the MCP server as the least-privilege surface (this file) yet find at runtime that this session's working PR-open route is the CLI or the API (the ladder). One is an authoring/least-privilege decision; the other is a live-capability probe.

| Surface | Scoping granularity | Least-privilege posture | Request/grant it when |
|---|---|---|---|
| **GitHub MCP server** | **per-toolset and per-tool** allow-list + a read-only mode | **strongest** — structural, name-level | default for an agent operating GitHub; the only surface with a built-in read-only mode and a tool allow-list **[obs] claim #15** |
| **`gh` CLI** | inherits the ambient login's scopes; no per-tool cap from the CLI itself | **coarse** — as broad as the logged-in credential | a human-shaped, already-authed session where the MCP surface isn't wired **[inf]** |
| **Raw GitHub API** | bounded only by the token's scopes | **coarsest** — whatever the token carries | a gap the higher surfaces don't cover; scope the token hard **[inf]** |

- **Default recommendation:** request the **MCP server with a toolset/tool allow-list and read-only where possible** — it is the only one of the three that lets you cap the surface *below* the token's scopes **[obs] claim #45 / [inf]**.
- Whichever surface you request, **grant the PAT/OAuth minimum scopes** — the token is the floor under all three **[obs] claim #15**.

---

## 5. Where this is *enforced* — the command-review allowlist (authoring vs enforcement)

This file is **authoring-time guidance**: it tells the agent which tools to *request*. That is advice, not a control. The **enforcement** layer is separate and deterministic — the command-review tribunal ("the Thing") ships an **`mcp.allowed_servers`** allowlist, documented in the plugin's [CLAUDE.md](../CLAUDE.md) under **"MCP server allowlist — engine feature-complete."**

- The two layers compose and are **distinct**: this file says *which tools to request*; the allowlist **denies a write verb from a non-listed server at command-review time** **[obs] claim #45 / [obs] — CLAUDE.md §"MCP server allowlist"**.
- As documented there: when an allowlist is configured, a **write** verb (anything outside the read-verb prefixes `get_` / `list_` / `read_` / `search_` / `describe_` / `fetch_`) from a server *not* on the list is denied pre-LLM, citing `mcp.unverified-server`; reads and listed-server writes fall through to the panel **[obs] — CLAUDE.md §"MCP server allowlist"**.
- It is **opt-in and fail-open**: an absent/empty allowlist denies nothing **[obs] — CLAUDE.md §"MCP server allowlist"**. So the authoring discipline in this file is what keeps the surface small when the allowlist is off — the allowlist is the belt to this file's suspenders **[inf]**.

**Takeaway:** never cite *this knowledge file* as the thing that blocks an over-scoped MCP call — it is context, not a gate. The `mcp.allowed_servers` allowlist (a hook-layer deny) is the enforcement **[inf] / [obs] — CLAUDE.md §"MCP server allowlist"**.

---

## 6. Minimum scopes for a custom GitHub App

If you provision a **custom** GitHub App to give the agent its own identity, scope it to the minimum the work needs:

- **A custom minimal GitHub App needs only Contents, Issues, and Pull requests** to open PRs, file/triage issues, and read/write repo content; **the official app grants a broader set** **[obs] claim #13**.
- So a purpose-built App is a *least-privilege* win over adopting the broad official grant, when you control the App **[inf]**.
- Add a scope only when a concrete task requires it (e.g. a workflow-touching task needs the corresponding scope); default to the Contents/Issues/Pull-requests floor **[inf]**.

---

## 7. Least-privilege checklist — apply before granting the surface

1. **Pick the surface deliberately.** Prefer the MCP server for its toolset/tool allow-list and read-only mode; drop to `gh` / raw API only for a gap they leave **[obs] claim #45 / [inf]**.
2. **Decide the token first.** Remember a PAT overrides OAuth — scope the *effective* credential, and don't leave a broad PAT set beside a scoped OAuth flow **[obs] claim #16 / [inf]**.
3. **Allow-list the toolsets, then the tools.** Expose only what the task uses (the two-read-tool daily-report shape is the model) **[obs] claim #15**.
4. **Choose read-only when the task is read-only.** No write verb for a summarize/triage/report job **[inf] / [obs] claim #45**.
5. **Grant minimum token scopes** — and for a custom App, the Contents/Issues/Pull-requests floor, widened only on demonstrated need **[obs] claim #15 / #13**.
6. **Prefer short-lived credentials** (OIDC / workload-identity) over a long-lived secret where the environment supports it **[obs] claim #45**.
7. **Back it with the allowlist.** Configure the Thing's `mcp.allowed_servers` so a non-listed server's write is denied at command-review time — this file's advice is not a control on its own **[obs] — CLAUDE.md §"MCP server allowlist" / [inf]**.
8. **Separate "granted" from "works."** If a granted MCP route doesn't respond this session, that's a runtime-capability question — probe the route ladder in [remote-mcp-pr-landing.md](remote-mcp-pr-landing.md), don't widen the grant to "fix" it **[inf]**.
