# Environment Context — `<engagement_name>`

> **What this is.** A consumer-authored file at `.ravenclaude/environment-context.md` in your project root that tells the agent what role / authorization it has in each environment it can touch. The Team Lead reads this at session start; the Capability Grounding Protocol consults it before declaring blocked or asking the user "can you authorize X?"
>
> **Why it matters.** Without this file, the agent defaults to "I can't" and pings you for authorization on actions it could just perform itself. Documenting your posture once turns dozens of round-trips into zero.
>
> **Where this file lives.** **Consumer-side**, at `.ravenclaude/environment-context.md` in your project root. **NOT** in the marketplace plugin (privacy — SPN names, env URLs, tenant IDs must not ship in shared content).
>
> **Sensitivity.** Treat this file like any other config that names environments. Don't put secrets here (no client secrets, no JWTs, no plaintext passwords). DO put role / SPN-name / env-name / pre-authorized-action-categories — those are scoped enough to be useful without being credentials.

---

## How to use this template

1. Copy this file to `.ravenclaude/environment-context.md` in your project root
2. Replace placeholders below with your real environment posture
3. Update when environments change (new tenant, new SPN, new permission grant, environment retired)
4. The agent's Team Lead reads this at session start automatically — no other wiring needed

---

## Engagement metadata

- **Engagement name:** `<short slug, e.g., btcsi-flow-rebuild-2026>`
- **Last reviewed:** `<YYYY-MM-DD>` — refresh quarterly OR on env-posture change
- **Owner:** `<name or handle>`

## Active environments

For each environment the agent might touch, name:

- **`<env-name-or-slug>`** (`<env-id-or-URL>`)
  - **Role:** `<sysadmin | System Customizer | Application User | Read-Only | ...>`
  - **Auth mechanism:** `<SPN name | user account | service-principal-via-app-registration | ...>`
  - **Pre-authorized action categories:** `<comma-separated list>`
  - **Forbidden (always require explicit user OK):** `<comma-separated list — e.g., delete-table, drop-database, export-PII>`
  - **Self-serve checks** *(optional — the capability→route map):* for each question you'd otherwise tell the user to "go check manually," one entry with four fields — `check:` the question · `route:` the concrete API/CLI the held credential unlocks · `unlocked_by:` the pre-authorized category it derives from (must match one listed above) · `instead_of:` the manual/portal step it replaces. **Self-serve checks are READ-ONLY** — a write derived from a check's finding still hits the Forbidden list.

### Example posture (delete this section in your real file)

- **DEV** (`btcsi-dev`)
  - **Role:** sysadmin
  - **Auth mechanism:** SPN `raven-claude-dev`
  - **Pre-authorized:** solution import/export, Web API calls (Dataverse + Graph), `pac` CLI operations, programmatic flow creation/update/delete, temp solution lifecycle, plug-in registration, env-var + connection-ref edits
  - **Forbidden:** none (DEV is fully safe)
  - **Self-serve checks:**
    - check: "Did cloud flow &lt;name&gt; succeed or fail? Show its recent run history."
      route: "Dataverse Web API — `GET /api/data/v9.2/flowruns` (the FlowRun table) with SPN raven-claude-dev"
      unlocked_by: "Web API calls (Dataverse)"
      instead_of: "telling the user to open the Power Automate portal → My flows → Run history"
    - check: "Is a Dataverse row present / what's its current field value?"
      route: "Dataverse Web API GET on the table + id with SPN raven-claude-dev"
      unlocked_by: "Web API calls (Dataverse)"
      instead_of: "asking the user to open the maker portal and look the record up"

- **TEST** (`btcsi-test`)
  - **Role:** sysadmin
  - **Auth mechanism:** SPN `raven-claude-test` (same SPN as DEV is fine if your auth model uses one SPN per tenant)
  - **Pre-authorized:** same as DEV
  - **Forbidden:** none

- **PROD** (`btcsi-prod`)
  - **Role:** Read-Only
  - **Auth mechanism:** SPN `raven-claude-prod-readonly`
  - **Pre-authorized:** read-only queries, telemetry pulls, generating reports for the user
  - **Forbidden:** any write (solution import, flow create/update/delete, data write, env-var change) — every PROD write requires explicit per-action user confirmation

## Default-assumption summary

The agent's working assumption per environment:

| Env | Default action posture |
|---|---|
| DEV | Execute pre-authorized actions without asking. Ask before doing anything in the "Forbidden" list. |
| TEST | Execute pre-authorized actions without asking. Ask before doing anything in the "Forbidden" list. |
| PROD | NO writes without explicit per-action user confirmation. Reads are fine. |

> **The bridge to the Capability Grounding Protocol:** before declaring "I can't do X" or asking "can you authorize me to do X?", the agent must check this file. If the action is in the pre-authorized list for the current environment, the agent executes. The Capability Grounding Protocol's reactive alternate-methods rule only fires AFTER the agent has tried and the action failed.

> **`Self-serve checks` → the consult-your-access-inventory clause.** When a `Self-serve checks` map is present, the agent must consult it **before telling you to check/do something manually** (CGP § "Consult your access inventory before telling the user to check or do something"): if it holds the `route`, it runs the check and reports the *answer* instead of sending you to a portal. The SessionStart capability banner surfaces the *count* of entries (never the route/check values — those name SPNs and URLs) as a salience pointer.

> **Keep it honest — verify on staleness.** This map is a *map, not a mirror*: if it's stale, or a listed route unexpectedly returns `401`/`403`, claiming access you no longer hold is worse than asking. Give each credential a cheap READ-ONLY **verify-me** probe (e.g. Dataverse `GET /api/data/v9.2/WhoAmI` → `200` confirms the SPN still works; `401`/`403` means re-confirm before trusting the map) and re-run the `environment-discovery` skill when this file is >90 days old.

## Cross-references

When other RavenClaude artifacts depend on environment posture, link them here:

- **Decision trees** (e.g., `plugins/power-platform/knowledge/programmatic-flow-creation.md`): the agent's pre-authorized list determines which branches of the tree are actually executable without user confirmation.
- **Scenarios bank** (`plugins/<plugin>/scenarios/`): per-scenario `permissions_context` field describes the posture that scenario assumed. Compare against this file to know if the scenario's resolution is applicable to your engagement.

## Refresh triggers

Update this file when:

- A new environment is added (new tenant, new sandbox, new pre-prod)
- An environment is retired
- A role grant changes (new SPN role, revoked permissions)
- An auth mechanism changes (rotated SPN, switched from delegated to application permissions)
- A new pre-authorized action category emerges from real engagement work (the `/wrap` slash command may surface these)

## What NOT to put in this file

- Client secrets, OAuth tokens, JWTs, plaintext passwords (use env vars or Key Vault)
- PII (names of partner users, customer IDs)
- Specific tenant IDs if your engagement context requires them confidential — use a slug instead
- Detailed permission ACLs (those live in the auth system, not in agent priors)

This file is for **role-shape**, not credentials and not detailed access matrices.
