---
scenario_id: 2026-06-05-agent-not-surfacing-in-copilot
contributed_at: 2026-06-05
plugin: microsoft-365-copilot
product: copilot-governance
product_version: "unknown"
scope: likely-general
tags: [agent-registry, publish, admin-gate, license, conversation-starters, surfacing]
confidence: medium
reviewed: false
---

## Problem

A declarative agent worked perfectly in the developer's sideload, but after "publishing" it **didn't appear for end users** in Copilot. Users couldn't find it, and the few who could couldn't tell what it did or how to start. The team assumed publishing the app package made it live; it didn't.

## Context

- Declarative agent packaged as an M365 app (manifest + icons), submitted to the org catalog. Target: all users in the tenant.
- The package upload succeeded, so the team read "uploaded" as "available" — but org-catalog publish is **admin-gated** (CLAUDE.md §3 #13).
- Some users lacked the license that gates org-data-grounded Copilot agents (§3 #8) — a separate reason a subset never saw it.
- The agent had no conversation starters, so even users who found it had no on-ramp.

## Attempts

- Tried: re-uploading the package and bumping the version. No effect — the artifact was fine; the gate was unopened.
- Tried: traversing the "which admin gate does this change require?" tree in [`../knowledge/copilot-extensibility-decision-trees.md`](../knowledge/copilot-extensibility-decision-trees.md). For an org-catalog (all-users) deploy, the leaf is explicit: an **AI-Admin or Global Admin must approve the agent in the Agent Registry**, and the Agents-tab status must be **Active** before rollout — approval propagation takes minutes to hours. The gate was sitting unapproved.
- Tried (the moves that worked): (a) had the admin approve the agent in the Agent Registry (Agents tab → Active); (b) confirmed the **license story** — the org-data-grounded agent requires the gating Copilot license, so unlicensed users still won't see it (stated as the mandatory `Licensing impact:` line); (c) added **conversation starters** so the agent advertises what it does and gives users an on-ramp (discovery is a real adoption lever, not polish).

## Resolution

"Published" ≠ "available." Three independent gates had to clear: the **Agent Registry admin approval** (status Active), the **license** that gates the agent for each user, and **conversation starters** for discoverability. Once the admin approved the agent and the licensed users had starters to click, surfacing worked.

**Action for the next engineer hitting this pattern:** when an agent works in sideload but not for users, check the gates in order — (1) Agent Registry approval status (Active?) in the M365 admin center, (2) the user's Copilot license for org-data-grounded agents, (3) conversation starters for discoverability. Don't conclude "publish is broken" from a sideload-works/users-don't symptom; it's almost always an unopened admin gate or a license gap, not a packaging defect. State the `Licensing impact:` line on every org-data-grounded recommendation (§3 #8). MCP tools, if the agent uses any, need a **separate** Tools-tab approval (§3 #13).

**Sources (retrieved 2026-06-05):**
- Agent Registry / org-catalog approval lifecycle and admin gate — Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps and the Agent Registry / agent-management docs. `[verify-at-build]`.
- Conversation starters drive discovery; org-data grounding is license-gated — Microsoft Learn declarative-agent + Copilot-licensing docs. `[verify-at-build]`.
