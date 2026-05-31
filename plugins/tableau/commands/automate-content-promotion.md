---
description: "Set up Tableau Server/Cloud content promotion and automation safely — authenticate with Connected Apps or PATs (never an admin password), promote published content rather than rebuilding it, and remap separated data sources per environment."
argument-hint: "[the automation, e.g. 'promote dashboards from dev to prod via a CI pipeline']"
---

# Automate content promotion

You are running `/tableau:automate-content-promotion`. Design the promotion/automation the user described (`$ARGUMENTS`) so it is credential-safe and structurally sound — the Server/site work the `tableau-admin` agent owns. A pipeline that signs in with a human admin password embeds a long-lived high-privilege secret and breaks the day that person changes it.

## When to use this

You are wiring CI/CD, scheduled REST jobs, or a dev→test→prod promotion flow for Tableau content. NOT for the in-workbook data model or RLS design (those are `/tableau:design-data-source-and-extract` and `/tableau:set-up-rls-and-governance`).

## Steps

1. **Authenticate with PATs or Connected Apps, never a password** (`server-automate-with-connected-apps-and-pats-not-passwords.md`): use a named, revocable, scoped Personal Access Token for scripted/REST automation and a Connected App JWT for app-to-Tableau — either can be revoked the instant it leaks, which a shared password cannot. No `password` field in any automation sign-in.
2. **Promote published content, don't rebuild it** (`server-promote-content-dont-rebuild.md`): move the existing certified content up the environments rather than re-authoring per environment — rebuilding drifts definitions and re-introduces the bugs you already fixed.
3. **Promote against separated published data sources** (`server-publish-with-separated-data-sources.md`): because the data source is published on its own, its connection remaps cleanly per environment on promotion — you can't remap a connection baked into a `.twbx`.
4. **Carry RLS and certification through promotion** (`gov-certified-data-sources-and-governance.md`): the certified source carries its model + RLS into the target environment; confirm the certification and entitlements survive the move.
5. **Land content in the right governance container** (`gov-sites-and-projects-as-the-governance-skeleton.md`, `gov-permissions-via-locked-projects-not-per-workbook.md`): publish into the locked project that grants the right groups, so promoted content inherits permissions instead of needing per-workbook grants.
6. Store the PAT/JWT secret in the CI/vault secret store (never in the script), and verify the pipeline can re-run idempotently.

## Guardrails

- An interactive admin credential in a promotion script is a secret-leak and a single point of failure — headless auth (PAT/Connected App) only.
- Rebuilding content per environment instead of promoting it is how prod silently diverges from dev.
- A connection baked into a workbook can't be remapped on promotion — separate the data source first.
