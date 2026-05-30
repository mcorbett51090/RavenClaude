# Secure the Default environment and restrict who can create environments

**Status:** Absolute rule — the Default environment is every user's open sandbox by default, and unrestricted environment creation is how shadow IT proliferates. Both are the #1 governance gaps in an ungoverned tenant.

**Domain:** Governance / Environment strategy

**Applies to:** `power-platform`

---

## Why this exists

Every tenant ships a **Default** environment that *every licensed user* can build in, with no DLP, no sharing limits, and no isolation — and by default, many users can **self-create** new environments at will. Left alone, this is where shadow IT lives: production-critical apps built in the Default env by someone who's since left, premium connectors wired to anything, data flowing out through flows nobody reviewed, and a sprawl of orphaned self-created environments no admin can account for. The two controls that close the gap are cheap and high-leverage: **secure the Default environment** (turn on Managed Environments for it, set sharing limits, apply a strict DLP policy, monitor with tenant analytics) and **restrict environment creation** to admins plus a request process. Do these early — retrofitting governance onto a Default env already full of business-critical apps is far harder than starting locked.

## How to apply

Lock the Default env down to experimentation-grade, and gate environment creation behind a request flow. Both are tenant-settings + DLP + Managed-Environments actions.

```bash
# Inventory first — find what's already living in Default and who can create envs
pac admin list                       # all environments; spot the Default + any sprawl

# Then, in the Power Platform admin center (or via admin PowerShell / Power Platform API):
#  1. Turn ON Managed Environments for the Default environment; set a low sharing limit.
#  2. Apply a STRICT DLP policy to Default (block premium + most non-business connectors).
#  3. Tenant setting: restrict environment creation to admins (disable maker self-create).
#  4. Stand up an environment-request process (PPAC, or the CoE kit env + DLP request flow).
```

**Do:**
- Turn **Managed Environments ON** for the Default env and set a low sharing limit — it's the most-used, least-governed env in the tenant.
- Apply a **strict DLP** to Default (block premium and most non-business connectors) so it's genuinely experimentation-only.
- **Restrict environment creation** to admins and run a lightweight request process, so every real environment is intentional and owned.

**Don't:**
- Leave the Default env unmanaged and assume "nobody builds anything real there" — they do, and it's usually load-bearing by the time you look.
- Let any licensed user self-create production environments — that's how you end up with 200 envs and no inventory.
- Block *everything* in Default — it should still work as a sandbox; lock it to experimentation, don't brick it.

## Edge cases / when the rule does NOT apply

- **Teams environments** auto-provision per Microsoft Team and are a separate (capped) surface — securing Default doesn't govern those; they need their own Dataverse-for-Teams posture.
- **Small/early tenants** (a handful of makers) can run a lighter touch — but the Default-env DLP and the create-restriction are cheap enough that there's rarely a reason to defer them.
- **Migration period:** if the Default env already holds real apps, secure it *and* migrate those apps to dedicated environments — don't just lock it and strand them.

## See also

- [`./gov-environment-strategy-and-isolation.md`](./gov-environment-strategy-and-isolation.md) — where real workloads go *instead of* Default
- [`./gov-managed-environments-and-sharing-limits.md`](./gov-managed-environments-and-sharing-limits.md) — the Managed Environments controls applied here
- [`./gov-dlp-policy-default-deny.md`](./gov-dlp-policy-default-deny.md) — the strict DLP the Default env needs
- [`../knowledge/managed-environments-and-governance-2026.md`](../knowledge/managed-environments-and-governance-2026.md) — "Secure the default environment" + "Restrict environment creation"

## Provenance

Codifies the `power-platform-admin` opinion ("Default environment is for nothing real") and the tenant-hygiene guidance in [`../knowledge/managed-environments-and-governance-2026.md`](../knowledge/managed-environments-and-governance-2026.md) (grounded in Microsoft Learn "Secure the default environment" + "Environment strategy"). `pac admin list` verified against the Microsoft Learn `pac admin` reference, retrieved 2026-05-30. The portal/tenant-setting actions are described, not scripted, because they're PPAC/tenant-setting operations rather than single pac verbs.

---

_Last reviewed: 2026-05-30 by `claude`_
