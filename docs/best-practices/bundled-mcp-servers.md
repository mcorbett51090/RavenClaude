# Bundling (or recommending) an MCP server in a plugin

**Status:** Pattern — strong default; deviate only with a written reason. The two **Don't**s under [Security](#how-to-apply) (literal secrets; silent write-capable servers) are **Absolute rules**.

**Domain:** Marketplace mechanics, plugin authoring, MCP integration.

**Applies to:** Any plugin under `plugins/<name>/` that wants to give its agents a real tool (MCP server) rather than only describing how to call an external system. Generalized from the `power-platform` plugin's CLAUDE.md §9 / §9a / §9a.1 doctrine (the first and, at time of writing, only bundled-MCP precedent in the marketplace).

---

## Why this exists

A plugin's agents can _describe_ how to call Dataverse, a Power BI file, or an API — but until the plugin ships a tool, the agent can't _act_. Bundling an MCP server closes that gap. But an MCP server is a **subprocess**: it runs outside every model-layer guard (`guard-destructive.sh`, the Thing tribunal, the permission deny-list see only the agent's own tool calls — not what a server process does), it **auto-starts when the plugin is enabled** at user scope, its **tool results are untrusted input** that flow straight into agent context, and a community server is a **supply-chain dependency** that ships to every consumer on `/plugin marketplace update`. Get the bundling decision or the wiring wrong and you've added an un-contained, un-pinned, possibly credential-holding process to every consumer's machine — silently. This rule makes the decision deliberate and the wiring safe, and it captures the doctrine so the next plugin doesn't re-derive it (or diverge from it).

## How to apply

### Step 1 — Decide: bundle, recommend, or evaluate-first

Pick the row that matches the server. **Default to the least-coupled row that works.**

| Situation | Disposition | What you ship |
|---|---|---|
| Server is **zero-config / no per-consumer state** (operates on local files, no auth, no tenant URL) AND is **first-party or a well-maintained MIT/Apache community package** | **BUNDLE** | An `mcpServers` entry in `plugin.json` (referencing a pinned published artifact), a `NOTICE.md` attribution, and a CLAUDE.md doctrine block (Step 4). Power BI's `pbix-mcp` is the canonical example. |
| Server is **per-tenant / authenticated / billed** (org-specific URL, OAuth/SPN, metered) OR is **first-party from the vendor** | **RECOMMEND, don't bundle** | No `mcpServers` entry (you can't hardcode a consumer-specific URL/secret). A CLAUDE.md section with the exact `claude mcp add …` command, prerequisites, **billing/cost callout**, and the owning agent. The official Dataverse MCP is the canonical example. |
| Server is **community, write-capable, secret-handling**, and **no first-party equivalent exists** | **EVALUATE-FIRST, never default** | A CLAUDE.md note documenting the option, a **mandatory `ravenclaude-core/security-reviewer` gate** before any consumer adopts it, and a pointer to the lower-blast-radius path (CLI/REST) to prefer when an MCP isn't required. |

> **First-party vs. third-party is the trust seam, not "in-repo vs. external":** a **third-party** server → _reference the published artifact_ (pinned + attributed), never vendor its source into the tree. A **first-party** server (our own stdlib scripts) → bundle the code, versioned with the plugin's semver.

### Step 2 — Pin the dependency (supply chain)

Never ship an unpinned install. Pin the published artifact and **record the tested version** so a breaking or compromised upstream release can't reach consumers silently.

```jsonc
// plugin.json — reference a pinned published package, don't vendor source
{
  "mcpServers": {
    "powerbi-editor": { "command": "pbix-mcp-server" }
  }
}
```

```bash
# Consumer prerequisite — PIN it, and state the version this plugin was tested against:
pip install 'pbix-mcp==<tested-version>'   # not: pip install pbix-mcp
```

If the runtime supports it, prefer an invocation that carries the pin inline (`npx -y pkg@1.2.3`, `uvx pkg==1.2.3`). Re-confirm the tested version at each plugin version bump (`[verify-at-use]`).

### Step 3 — Handle the auto-start reality (no silent side effects)

A bundled MCP server **auto-starts when the plugin is enabled** (user scope). You cannot make a bundled server "dormant" — and `defaultEnabled: false` is the wrong tool for an optional capability, because it disables the **whole plugin**, not just the server.

- **If the server is one optional capability among agents/skills** (e.g. `power-platform`): accept **loud-but-non-fatal degradation**. If the prerequisite isn't installed, the server shows as `failed` in `/mcp` and the binary error surfaces in the `/plugin` Errors tab; Claude Code and every other tool still work. Document this failure path explicitly (Step 4) — it's the #1 support question.
- **If the plugin's _primary_ value IS a backend-reaching server** that shouldn't auto-connect on install: use `"defaultEnabled": false` in `plugin.json` (requires Claude Code ≥ 2.1.154) so the plugin installs **disabled** and enabling is the consumer's explicit opt-in. State this in a Migration note — flipping an existing plugin to `defaultEnabled:false` disables it for current consumers on update.

### Step 4 — Write the CLAUDE.md doctrine block (this is what makes agents _use_ the tool)

Declaring the server in `plugin.json` makes the tool _exist_; it does not make agents _reach for it_. Agents default to their own reasoning unless the plugin's constitution tells them the capability exists and when to prefer it. Copy this template into the plugin's `CLAUDE.md`:

```markdown
## N. Bundled MCP server — `<server-name>` (<upstream>)

The plugin declares `<server-name>` in `plugin.json`, backed by <upstream link> (<license>).
It exposes <N tools> for <what it does>. **Read-only / read-write:** <state which verbs>.

**Consumer prerequisite** — run once: `<pinned install command>`.
Until then the server is **loud-but-non-fatal**: it shows `failed` in `/mcp` and the error
surfaces in the `/plugin` Errors tab; Claude Code and all other tools still work. **If the
tools aren't responding, check `/mcp` and the `/plugin` Errors tab first.** (MCP subprocesses
get a minimal shell env — a binary visible in your terminal may be missing to the child
process; use an absolute path or the documented `python -m …` fallback.)

**Which agent owns it?** Primarily `<agent>` (<why>). Others call it situationally: <list>.
**Trigger:** when the user asks to <do X>, call the tool instead of explaining the API.

**Boundary** — `<server-name>` is for <scope>. It is **NOT** <the thing it's confused with>.
For <the other thing>, use <the correct path> instead.

See `NOTICE.md` for attribution and the PATH-fallback configuration.
```

The **boundary** ("what it is NOT") and the **trigger** ("reach for it when X instead of describing") are the load-bearing lines — omit them and the agent treats the tool as optional trivia.

### Step 5 — Attribution + security gates

- **`x-mcpAttribution` (CI-enforced)** — declare every server in a top-level `x-mcpAttribution` map in `plugin.json`, keyed by server name. This is what `scripts/check-mcp-attribution.py` checks on every PR (teeth audited in `audit-gates.sh` Gate 98). Top-level placement is deliberate: Claude Code ignores unrecognized top-level `plugin.json` fields (they load fine and are at most a non-blocking `claude plugin validate` warning), so the field never affects plugin loading or server launch — verified against the plugins-reference "Unrecognized fields" section.

  ```jsonc
  {
    "mcpServers": { "powerbi-editor": { "command": "pbix-mcp-server" } },
    "x-mcpAttribution": {
      "powerbi-editor": {
        "party": "third-party",      // "first-party" | "third-party"
        "source": "https://github.com/d0nk3yhm/pbix-mcp",
        "license": "MIT",
        "notice": "NOTICE.md"         // file must exist AND mention the server name
      }
    }
  }
  ```

  The gate makes "is this third-party?" **author-declared, not heuristically guessed** from the command string. A `first-party` entry needs only `party`; a `third-party` entry additionally needs `source`, `license`, and a `notice` file that exists and names the server.

- **`NOTICE.md`** — every third-party server gets a prose attribution entry: source repo, package, license, what it does, the pinned prerequisite, and a PATH fallback. (The `x-mcpAttribution.notice` field points at it; the gate checks it exists and names the server.) Keep the fallback command **identical** to the one in CLAUDE.md (a mismatch is a real, shipped bug — see Provenance).
- **Least privilege** — declare the server's verbs. **Default bundled servers to read-only.** A **write-capable** server is an Absolute-rule `security-reviewer` gate before it ships, and interacts with **Gate 25** (the deterministic `mcp.allowed_servers` allowlist): a write verb from a server not in the consumer's allowlist is a pre-LLM DENY. A bundled server is **not** exempt from that allowlist — design for it; don't quietly defeat it.
- **Secrets** — if the server needs credentials, bundle a **reference** (Key Vault URI, `op://` ref, or an env-var _name_) that the server dereferences at runtime — **never the literal**. Note: `userConfig`'s `sensitive: true` only masks the enable-prompt input and stores at rest in the OS keychain; it does **not** keep the value out of the `CLAUDE_PLUGIN_OPTION_<KEY>` env exported to every plugin subprocess. So the reference-not-literal rule is the real boundary, not the `sensitive` flag.

**Do:**
- Pin the dependency and record the tested version.
- Default to read-only; gate write-capable servers through `security-reviewer`.
- Write the CLAUDE.md doctrine block (owner agent + trigger + boundary + failure path).
- Keep the PATH-fallback command identical across `CLAUDE.md` and `NOTICE.md`.
- Bump the plugin version in both mirrors (`plugin.json` + `marketplace.json`) — adding/removing a bundled server is a user-visible change.

**Don't:**
- Ship a literal secret in `plugin.json`, `NOTICE.md`, or any bundled file. _(Absolute.)_
- Bundle a write-capable server without a `security-reviewer` gate. _(Absolute.)_
- Vendor a third-party server's source into the tree — reference the published artifact.
- Use `defaultEnabled:false` to "fix" a missing prerequisite — that disables the whole plugin.

## Edge cases / when the rule does NOT apply

- **First-party server code** (our own scripts exposed as MCP tools): the "reference don't vendor" guidance inverts — you _do_ bundle the code, versioned with the plugin. Still default it read-only; a tool that mutates posture or invokes the tribunal (`thing-decide`) is deferred until the self-disable interaction is designed.
- **Per-server attribution placement.** The convention puts `x-mcpAttribution` at the **top level** of `plugin.json` (a map keyed by server name), not inside each `mcpServers` entry. Both load fine — Claude Code ignores unrecognized keys in either spot — but top-level is the explicitly-blessed location for ecosystem-agnostic metadata and keeps the `mcpServers` entries clean for the loader. The CI gate (`check-mcp-attribution.py`) reads the top-level map.
- **Project-scope `@skills-dir` plugins** get per-server approval and don't auto-start monitors; the auto-start concerns in Step 3 are about the default **user-scope** marketplace install.

## See also

- [`plugin-versioning.md`](./plugin-versioning.md) — the version-mirror bump that any bundled-server change triggers
- [`cross-plugin-references.md`](./cross-plugin-references.md) — keep MCP-owning-agent references soft so they degrade gracefully
- [`ci-gate-audit.md`](./ci-gate-audit.md) — if you add a CI gate enforcing any clause here, it needs a fail-on-bad + pass-on-good fixture pair
- [`../../plugins/power-platform/CLAUDE.md`](../../plugins/power-platform/CLAUDE.md) §9 / §9a / §9a.1 — the source doctrine this rule generalizes
- [`../../plugins/power-platform/NOTICE.md`](../../plugins/power-platform/NOTICE.md) — the attribution + PATH-fallback format
- [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference) — `mcpServers`, `userConfig`, `defaultEnabled` (verify volatile fields at use)
- [Claude Code MCP](https://code.claude.com/docs/en/mcp) — env-var expansion in MCP configs

## Provenance

Generalized 2026-06-05 from `power-platform/CLAUDE.md` §9/§9a/§9a.1 during the plugin-bundling-options planning work (`docs/plan/plugin-bundling-options.md` + two-panel review). The analysis that produced it found two concrete bugs in the source pattern — a contradictory PATH-fallback command (`python -m pbix_mcp.server` in CLAUDE.md vs. `python -m pbix_mcp.cli` in NOTICE.md) and an unpinned `pip install` — which is why "keep the fallback identical" and "pin the dependency" are explicit clauses, not generic advice. The auto-start / `defaultEnabled` and `sensitive`-isn't-secret-safe points were verified against the Claude Code plugins reference during that review.

---

_Last reviewed: 2026-06-05 by `mcorbett51090`_
