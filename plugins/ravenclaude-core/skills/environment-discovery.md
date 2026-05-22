---
name: environment-discovery
description: Auto-discover the consumer's environment posture by probing installed CLIs (pac / az / aws / gcloud / gh) with read-only commands at session start, decoding JWTs for role/scope claims, and assembling a draft `.ravenclaude/environment-context.md` for save/edit/skip. Streamlines proposal 2026-05-22-001's permission-awareness mechanism.
---

# Skill: environment-discovery

> **Invoked by:** the Team Lead at session start when `.ravenclaude/environment-context.md` does NOT exist in the consumer's project root. Streamlines the permission-awareness mechanism (proposal `2026-05-22-001`) from "user fills in a template" to "agent infers posture, asks once, saves." Closes the "did you try X?" round-trip on actions the agent has authority to perform.
>
> **When to invoke:** at session start (one-time per engagement), OR when `.ravenclaude/environment-context.md` is older than 90 days (re-discovery), OR when the user explicitly asks ("rediscover my environments").
>
> **Output:** a draft `.ravenclaude/environment-context.md` matching the schema in [`../templates/environment-context.md`](../templates/environment-context.md), surfaced to the user with a save / edit / skip prompt.

## What this skill does (in one paragraph)

Detects which CLIs are authenticated on the consumer's machine (`pac`, `az`, `aws`, `gcloud`, `gh`), runs **read-only** probes against each to enumerate visible environments + the active identity's role in each, decodes any acquired JWTs for role/scope claims, and assembles a draft `.ravenclaude/environment-context.md` mapping (environment → role → pre-authorized action categories → forbidden list). Surfaces the draft to the user for save/edit/skip. The agent NEVER runs a write or state-changing command during discovery.

## The flow

### Step 1 — Confirm scope before probing

Ask the user (use AskUserQuestion) before running any probes:

> "I can auto-discover your environment posture by running read-only probes against your local CLIs (`pac auth list`, `az account show`, etc.). This takes ~30 seconds and writes nothing to your environments. Proceed?"

- **Yes, all CLIs** — run every probe
- **Yes, but only Power Platform / Azure / AWS / GCP / GitHub** — scope to one
- **Skip** — fall back to "create the template by hand" path (point them at [`../templates/environment-context.md`](../templates/environment-context.md))

**Do not probe without confirmation.** Even read-only probes leak telemetry to vendor APIs (audit logs, CLI usage); the user has the right to opt out.

### Step 2 — Detect which CLIs are installed + authenticated

For each potentially-relevant CLI, check `command -v <cli>`. If not in PATH, skip. If in PATH, check auth status with the lowest-impact command:

| CLI | Existence check | Auth check |
|---|---|---|
| Power Platform | `command -v pac` | `pac auth list` (returns active profiles) |
| Azure | `command -v az` | `az account show` (returns active subscription + tenant) |
| AWS | `command -v aws` | `aws sts get-caller-identity` (returns arn + account) |
| GCP | `command -v gcloud` | `gcloud auth list` (returns active accounts) |
| GitHub | `command -v gh` | `gh auth status` (returns authenticated hosts) |

If a CLI is installed but not authenticated, note it ("Power Platform CLI installed but no active auth — skipping") and continue. Do NOT prompt the user to authenticate; that's their choice outside this skill.

### Step 3 — Per-CLI capability probes (READ-ONLY)

For each authenticated CLI, run a sequence of read-only commands and capture the output. Allowed commands per CLI:

#### Power Platform (`pac`)

```bash
pac auth list                                      # active profiles
pac org list                                       # visible orgs / environments
# For each environment if SPN-auth:
pac admin list-app-roles --environment <env-id>    # SPN's roles in that env
# For each environment if user-auth:
pac user list --environment <env-id> --query "[?contains(displayname,'<me>')]"  # my roles
```

JWT inspection: after `pac auth create` or similar acquired a token, the token is cached under `~/.local/share/microsoft/PowerAppsCli/` (Linux) or `%LOCALAPPDATA%\Microsoft\PowerAppsCli\` (Windows). Read + base64-decode the JWT payload section (middle of `aaa.bbb.ccc`) to inspect `roles`, `scp`, `aud`, `tid`. Do NOT print the full token to the user; print only the claim values.

#### Azure (`az`)

```bash
az account show                                                          # active subscription
az account list --output json                                            # all subs visible
az ad signed-in-user show --query "{id:id, upn:userPrincipalName, displayName:displayName}"
az role assignment list --assignee <upn-or-objectid> --output json       # my role assignments
```

For SPN auth (`az login --service-principal`), use `az account show --query "user"` to confirm SPN identity instead of `signed-in-user`.

#### AWS (`aws`)

```bash
aws sts get-caller-identity                                             # who am I (arn + account)
# If user (not assumed role):
aws iam get-user --query "User.UserName"
aws iam list-attached-user-policies --user-name <name>
aws iam list-user-policies --user-name <name>
# If assumed role:
aws iam get-role --role-name <name>
aws iam list-attached-role-policies --role-name <name>
```

#### GCP (`gcloud`)

```bash
gcloud auth list                                                        # active accounts
gcloud config get-value project                                         # current project
gcloud projects list --format="value(projectId)"                        # accessible projects
gcloud projects get-iam-policy <project> --flatten="bindings[].members" \
  --filter="bindings.members:<email>" --format="value(bindings.role)"   # my roles
```

#### GitHub (`gh`)

```bash
gh auth status                                                          # authenticated hosts
gh api user --jq ".login"                                               # my username
# Per repo (if we know which repo):
gh api repos/<owner>/<repo>/collaborators/<me>/permission --jq ".permission"
```

### Step 4 — Synthesize the draft `environment-context.md`

For each (CLI, environment, identity) tuple discovered, build an entry following the template at [`../templates/environment-context.md`](../templates/environment-context.md). Specifically:

- **Environment name + ID/URL** — from the probe (`pac org list` returns names + IDs; `az account list` returns subscription names + IDs; etc.)
- **Role** — inferred from probe results (e.g., `pac admin list-app-roles` returned "System Customizer" → role: System Customizer)
- **Auth mechanism** — from the probe (`pac auth list` says "Service Principal" or "User"; `aws sts get-caller-identity` shows `arn:aws:iam::...:user/X` vs `arn:aws:sts::...:assumed-role/X`)
- **Pre-authorized action categories** — default-conservative inference per role:
  - **System Customizer / sysadmin / Owner / Admin / full IAM perms** → broad set (solution import/export, Web API, pac CLI, programmatic flow creation, env-var/connection-ref edits)
  - **Contributor / write-but-not-admin** → narrower set (Web API reads, scoped writes)
  - **Reader / view-only** → READ ONLY
- **Forbidden** — by default, PROD-named environments get "any write" forbidden. Environments with the substring `prod`, `production`, `live` in the name are flagged PROD even if no explicit naming convention.
- **Default-assumption table** — derived per the template's pattern

**Critical: discovery infers capabilities, not policy.** The agent might find it has Owner role in PROD on the Azure subscription — but the engagement's policy might be "don't write to PROD without explicit approval." The skill's draft is conservative on PROD by default; the user edits if their policy is more permissive.

### Step 5 — Surface the draft + confirm

Show the user the assembled `.ravenclaude/environment-context.md` content with this framing:

> "Here's what I discovered. I'm going to save this to `.ravenclaude/environment-context.md` so future sessions can use it without re-probing. Please review:
>
> [...content...]
>
> **Note:** I inferred pre-authorized action categories conservatively. If your engagement allows broader pre-authorization in DEV/TEST, edit before saving. If PROD writes should require explicit confirmation each time (the safe default), no edit needed."

Then AskUserQuestion:

- **Save as-is** — write the file, return
- **Edit, then save** — open the file in the user's editor (use `$EDITOR` or fall back to displaying a "please edit and save" message) and re-prompt
- **Skip — don't save** — fall back to no-file behavior; agent will keep asking authorization

### Step 6 — Write the file

If user confirmed save:

```bash
mkdir -p .ravenclaude
# Write the file
```

Use the `Write` tool with the assembled content. After the write, confirm with the user and explain what happens next:

> "Saved to `.ravenclaude/environment-context.md`. Future sessions will read this file at session start and stop asking authorization on pre-authorized actions. Refresh quarterly or whenever your environment posture changes (new env, new role grant, retired environment). You can also re-run this discovery anytime by saying 'rediscover my environments'."

## What this skill does NOT do

- **Does not write anything** to your environments, tenants, or repos. Discovery is read-only.
- **Does not store credentials.** The output file contains role-shape only — no client secrets, no JWTs, no plaintext passwords. The scrub step below enforces this.
- **Does not prompt for re-authentication.** If a CLI is installed but not authenticated, the skill skips that surface. The user authenticates outside this skill.
- **Does not infer policy.** The skill discovers *capabilities* (what the agent can do); the user's engagement policy determines what the agent *should* do. PROD defaults are conservative; edit if more permissive.
- **Does not cross-reference multiple engagements.** This skill is per-engagement. If the consumer works across multiple engagements with different postures, each engagement repo gets its own `.ravenclaude/environment-context.md`.

## Scrub before write (mandatory)

Before invoking `Write` on the assembled content, scan for the following patterns and refuse-or-redact:

| Pattern | Action |
|---|---|
| `eyJ` followed by base64-like chars (JWT) | REFUSE — never write a JWT to this file |
| `[A-Za-z0-9]{32,}` strings that look like client secrets | REDACT to `<rotate-and-set-as-env-var>` |
| `-----BEGIN ... PRIVATE KEY-----` | REFUSE |
| Plaintext passwords (preceded by `password:`, `pwd:`, `pass:`) | REFUSE |
| Real client / customer names if the user named them | Ask user if they want to anonymize or keep |
| Bearer tokens, OAuth tokens (anything starting with `Bearer ` or matching token shapes) | REFUSE |

If anything is REFUSED, the skill stops and tells the user what was found + recommends rotation. No partial write with credentials in it — refuse the whole save.

## Failure modes the skill handles

- **No CLIs installed** — return the marketplace template path; suggest the user fill in manually
- **CLIs installed but no auth on any** — same as above; suggest they run `pac auth create` / `az login` / etc. first, then re-run discovery
- **Single-CLI auth** (e.g., only `az`) — discover just that environment surface; note the others were skipped
- **Conflicting identity claims** (multiple `pac` profiles, multiple `az accounts`) — list them all, ask user which is active for this engagement
- **Probe command fails** — log the failure to the user (e.g., "tried `pac admin list-app-roles` — returned permission error; falling back to conservative read-only assumption") and continue
- **JWT decode fails** — skip JWT-derived claims; continue with CLI-output-derived claims only
- **User declines to save** — return cleanly; no file written, no state changed

## When to re-run discovery

- **Every 90 days** (the Researcher's staleness sweep flags this)
- **When the user adds a new environment** (new tenant, new sandbox, new pre-prod)
- **When the user changes auth model** (rotated SPN, switched from user-auth to SPN-auth, etc.)
- **When the user says** "rediscover my environments" explicitly

## Compositional notes

This skill is the **discovery** half of the permission-awareness mechanism. The **consumption** half is the Capability Grounding Protocol's "Pre-action environment-context check" clause (per `CLAUDE.md`). Together they form: discovery (this skill) → file (`.ravenclaude/environment-context.md`) → consumption (CGP clause).

Other plugins do NOT need to invoke this skill directly — it's session-start orientation territory. Plugin-specific agents inherit the consumption side via the CGP clause, which fires on every "I can't do X" / "can you authorize me" moment.

## Anti-patterns this skill flags

- **Running write commands during discovery** — discovery is read-only by contract; any write is a bug
- **Inferring more pre-authorization than the role actually grants** — when in doubt, narrower. The user expands the file if they want broader.
- **Writing JWTs / secrets / passwords to the file** — the scrub step refuses any of these
- **Skipping the user-confirmation step** — discovery surfaces the draft; the user saves. Never auto-save without confirmation.
- **Treating PROD as DEV** — anything named `prod` / `production` / `live` defaults to read-only in the draft. User edits if they have a less-conservative policy.
- **Burning a session every time** — once saved, `.ravenclaude/environment-context.md` is the source of truth; don't re-probe unless explicitly asked or the file is stale (>90 days).

## Refresh triggers for THIS skill (the skill file itself)

- CLI authentication mechanisms change (e.g., `pac auth create` syntax changes, `az login --service-principal` parameter changes)
- New CLIs become relevant (e.g., a new IaC tool gets added to the discovery surface)
- The `environment-context.md` template at `../templates/environment-context.md` schema changes
- Real engagement signal via `/wrap` shows a probe + inference pattern this skill didn't anticipate

## References

- [`../templates/environment-context.md`](../templates/environment-context.md) — the schema this skill produces
- [`../CLAUDE.md`](../CLAUDE.md) §"Pre-action environment-context check (added 2026-05-22)" — the CGP clause that consumes the file this skill produces
- [`../CLAUDE.md`](../CLAUDE.md) §"Session-start environment-context load (added 2026-05-22)" — the Team Lead orientation logic that invokes this skill
- [`../../../docs/proposals/2026-05-22-001-environment-context-permission-posture.md`](../../../docs/proposals/2026-05-22-001-environment-context-permission-posture.md) — the proposal this skill implements the discovery half of
