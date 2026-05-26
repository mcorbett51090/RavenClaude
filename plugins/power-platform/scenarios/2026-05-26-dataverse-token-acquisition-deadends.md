---
scenario_id: 2026-05-26-dataverse-token-acquisition-deadends
contributed_at: 2026-05-26
plugin: power-platform
product: dataverse-web-api
product_version: "v9.2 (2026.04); pac 2.7.x"
scope: environment-specific
tags: [dataverse-web-api, auth, msal, access-token, pac-cli, codespace, client-credentials]
confidence: high
reviewed: false
---

## Problem

An agent needed to update a Power Automate cloud flow via the Dataverse Web API from a
**GitHub Codespace**. `pac` was already authenticated and working, but the agent had no
obvious way to turn that into a bearer token for `requests`/`curl`, and burned many turns
exploring auth paths before finding one that worked. The flow update itself was simple; the
**token acquisition** was where the time went.

## Permissions context

- GitHub Codespace dev environment; `pac` interactively authenticated to the target org.
- `AZURE_CLIENT_SECRET` was **absent** from the Codespace env (the existing repo scripts —
  `import-rename-flows.py`, `activate-flows-post-import.py` — all use client-credentials, so
  the agent assumed that was the only path).
- `az` CLI not installed / not logged in.

## Attempts

- Tried: **`az` CLI** to mint a token → not available in the Codespace.
- Tried: **`azure-identity`** (DefaultAzureCredential etc.) → no usable cached credential to
  pick up; dead end without an explicit credential.
- Tried: **`pac auth token`** → **the command does not exist** (verified — `pac auth` has
  `create/list/select/clear`, nothing that prints a token).
- Tried: assuming **client credentials** (`AZURE_CLIENT_SECRET`) like the existing scripts →
  failed because the secret is not present in the Codespace.
- **Worked:** read **PAC's MSAL token cache** directly — deserialize
  `~/.local/share/Microsoft/PowerAppsCli/tokencache_*msalv3.dat` with `msal`,
  `acquire_token_silent` against the cached account, scope `https://<org>.crm.dynamics.com/.default`.

Separately, once authenticated, the `clientdata` template was misread from a compressed
single-line FetchXML/JSON blob (one 400 before fetching a clean definition via REST) — but
that failure mode is already covered by
[`2026-05-21-flow-clientdata-shape-drift.md`](2026-05-21-flow-clientdata-shape-drift.md); this
scenario is specifically about the **token dead-ends**.

## Resolution

**Pick the token path by what's already authenticated, cheapest first — don't default to the
client-credentials path the repo's scripts use.** The canonical order (full detail +
copy-paste snippets in [`../knowledge/dataverse-token-acquisition.md`](../knowledge/dataverse-token-acquisition.md)):

1. `AZURE_CLIENT_SECRET` present → client credentials (CI/unattended path).
2. `az` logged in → `az account get-access-token --resource https://ORG.crm.dynamics.com`.
3. **`pac` authenticated → reuse its MSAL cache via `msal.acquire_token_silent` — reach here
   the moment you see `pac` is working, not after exhausting everything else.**
4. Nothing authenticated → interactive/device-code (`/user_impersonation` scope).

**Two lessons for the next consultant:**

- **The absence of `AZURE_CLIENT_SECRET` is a signal to switch paths, not to keep retrying
  it** — it's normally absent on dev machines / Codespaces and present only in CI. A working
  `pac` session is the fastest token source available in that situation.
- **The MSAL-cache trick is OS-dependent:** the cache is **plaintext on Linux/macOS** (so it
  works cleanly in a Codespace) but **DPAPI-encrypted on Windows** — a raw read on Windows
  returns ciphertext and needs a DPAPI unprotect. Don't assume the Codespace trick ports.

Cross-reference: the operational complement is the decision tree in
[`../knowledge/dataverse-token-acquisition.md`](../knowledge/dataverse-token-acquisition.md);
this scenario is the field-note version that surfaces the *symptom* (PAC works but token
churn) so the next engagement recognizes it before exploring.
