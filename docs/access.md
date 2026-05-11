# Repository access

Running record of who has collaborator access to `mcorbett51090/RavenClaude`, what role they hold, and when access was granted.

This file is the source of truth outside GitHub's UI. When you add or remove a collaborator on GitHub, update this file in the same PR.

---

## Current collaborators

| GitHub handle | Name | Role | Added | Purpose |
|---|---|---|---|---|
| [`@mcorbett51090`](https://github.com/mcorbett51090) | Matt Corbett | Owner (Admin) | 2026-05-09 _(repo creation)_ | Maintainer; merges all PRs to `main` |
| [`@mcorbettbma`](https://github.com/mcorbettbma) | Matt Corbett _(work / secondary account)_ | Write | 2026-05-11 | Lesson contributions and plugin testing from a second workstation |

---

## Role definitions

| GitHub role | What they can do | What they cannot do |
|---|---|---|
| **Owner / Admin** | Everything — merge to protected branches, change settings, manage collaborators, delete repo | _n/a_ |
| **Maintain** | Manage issues + PRs, no settings changes | Change branch protection, manage collaborators |
| **Write** | Push branches, open PRs, comment | Merge to `main` directly (PR + approval required), change settings |
| **Triage** | Manage issues + PRs (label, assign, close) | Push code |
| **Read** | Clone and read everything | Push code, open PRs that touch code |

For RavenClaude, the default for a trusted contributor is **Write**. Reserve **Maintain** for someone who reviews PRs alongside Matt.

---

## How to add a collaborator

1. Go to **Settings → Collaborators → Add people** on GitHub.
2. Enter their GitHub username; pick the role (usually **Write**).
3. GitHub emails them an invite — they must accept before access is live.
4. Once they've accepted, open a PR adding a row to the table above. Include the date and a one-line purpose.
5. Walk them through the onboarding checklist in `CONTRIBUTING.md` so they can install the marketplace plugins on their machine and verify the install works.

## How to remove a collaborator

1. Go to **Settings → Collaborators**, click the **×** next to their name.
2. Open a PR moving their row from the table above to the **Past collaborators** section below, with a removal date and one-line reason.
3. If the removal is for cause (security incident, scope change), also message them in writing asking them to uninstall the plugin from their local Claude Code (`/plugin uninstall ravenclaude-core@ravenclaude` etc.) — GitHub access removal stops further `marketplace update` pulls, but their local cached copy keeps working until they uninstall.

---

## Past collaborators

_None yet._

| GitHub handle | Name | Role held | Added | Removed | Reason |
|---|---|---|---|---|---|
| _—_ | _—_ | _—_ | _—_ | _—_ | _—_ |
