# Configure the web-access allow/deny list before the first WebFetch

**Status:** Pattern
**Domain:** Agent design / Security / Web access
**Applies to:** `ravenclaude-core`

---

## Why this exists

An agent that fetches URLs on demand without a configured allow/deny list prompts the user for every new domain — one by one, as they are encountered. In a multi-step research session, this produces a stream of one-off approval dialogs that interrupt the work flow and that the user typically approves reflexively, which defeats the purpose of having an approval mechanism. A committed allow/deny list — populated before the session begins — gives the agent deterministic guidance (known-good domains auto-fetch, known-bad domains are blocked without prompting) and surfaces only genuinely novel domains for user decision, once, with the four-option choice.

## How to apply

Populate `.ravenclaude/web-access.yaml` before the session begins:

```yaml
# .ravenclaude/web-access.yaml
allow:
  # Documentation and official sources the project routinely fetches
  - docs.anthropic.com
  - learn.microsoft.com
  - developer.github.com
  - docs.python.org
  # Project-specific sources
  - api.your-service.com

deny:
  # Known-bad or out-of-scope domains
  - pastebin.com        # often used for exfiltration
  - discord.com         # no programmatic data the agent needs
```

Match rules: a rule matches the domain **and** its subdomains. `docs.anthropic.com` matches `docs.anthropic.com/path/to/page`; it does not match `www.anthropic.com`.

**Four-option choice (agent behavior for unlisted domains):**

When the agent encounters a domain not in either list, it surfaces this choice:
1. **Just once** — fetch now; write nothing.
2. **This session** — allow for the rest of this session; cleared when the session ends.
3. **Permanently** — add to the `allow` list; committed to `web-access.yaml`.
4. **Deny** — add to the `deny` list; blocked in future sessions.

**Do:**
- Populate the allow list with sources the project's agents will routinely need — official documentation, API references, your own services.
- Review and extend the allow list when a new plugin or domain is added to the project's scope.
- Use the dashboard's "Web access" panel (`#/configure → Web access`) to edit the list with a UI if available.

**Don't:**
- Add broad domains like `*.com` or `github.com` to the allow list — scope the allowed domains to the specific subdomains the agents actually need.
- Commit credentials or API keys in URL patterns in the allow list — the list governs domain-level routing, not authenticated access.
- Treat the allow list as a security boundary — it determines when to prompt, not whether the destination is safe. Security review is still needed for any external data the agent acts on.

## Edge cases / when the rule does NOT apply

- Offline development environments with no internet access — the allow/deny list is still useful for documenting expected external dependencies, but no fetches will succeed regardless.
- Projects where all external fetches are researcher-agent tasks with user oversight — the four-option choice on each domain is the right interaction pattern and no pre-configuration is needed.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — "Website access — allow/deny lists + the four-option prompt (added 2026-06-01)" section.
- [`./check-runtime-state.md`](./check-runtime-state.md) — the same "configure before you act" discipline applied to the broader event substrate.

## Provenance

Distilled from `plugins/ravenclaude-core/CLAUDE.md` §"Website access — allow/deny lists + the four-option prompt (added 2026-06-01)". The `guard-web-access.sh` hook is the deterministic enforcement layer.

---

_Last reviewed: 2026-06-05 by `claude`_
