---
description: Harden Power Platform tenant governance — default-deny DLP policies, environment strategy + isolation, secure the default environment, managed environments + sharing limits, and licensing/capacity awareness. The power-platform-admin's tenant-safety checklist.
argument-hint: "[scope, e.g. 'new tenant' or 'audit current DLP']"
---

# Harden environment governance

You are running `/power-platform:harden-environment-governance`. Review or stand up tenant governance for the scope the user named (`$ARGUMENTS`), following this plugin's `power-platform-admin` discipline. Ungoverned Power Platform tenants leak data and sprawl — this is the safety floor.

## When to use this

A new tenant is being set up, or an existing one needs a governance audit (DLP, environments, the wide-open default environment).

## Steps

1. **DLP default-deny** (`gov-dlp-policy-default-deny`): start from deny and allow connectors deliberately — never an allow-all baseline. Separate business vs non-business connector groups.
2. **Secure the default environment** (`gov-secure-the-default-environment`): the default environment is everyone's by default — restrict maker access, apply DLP, and route real work to purpose-built environments.
3. **Environment strategy + isolation** (`gov-environment-strategy-and-isolation`): dev/test/prod separation, per-team or per-app isolation as the org needs; don't let prod and experimentation share an environment.
4. **Managed environments + sharing limits** (`gov-managed-environments-and-sharing-limits`): enable Managed Environments for governed estates; cap app sharing to prevent "shared with the whole org" sprawl.
5. **Licensing + capacity awareness** (`gov-licensing-and-capacity-awareness`): map the capabilities in use to license/capacity so a launch doesn't hit a wall or an unbudgeted bill.

## Guardrails

- A DLP policy that allows everything is no policy — default-deny.
- The default environment is the most common leak path; never leave it wide open.
- These are tenant-wide changes — surface the exact admin-center / `pac admin` steps and leave the apply to the human with the change clearly staged.
