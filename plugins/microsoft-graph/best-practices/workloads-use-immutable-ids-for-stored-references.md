# Use immutable IDs for any stored Outlook reference

**Status:** Absolute rule — persisting a default Outlook item ID is a latent data-corruption bug that surfaces weeks later.

**Domain:** Web API / Outlook workloads

**Applies to:** `microsoft-graph`

---

## Why this exists

The default `id` Graph returns for an Outlook **message** or **event** is **not stable**: it changes when the item moves between folders (including automatic moves — a rule firing, "Archive," a mailbox migration, a focused-inbox shuffle). Code that stores a default ID and looks it up later works in every test (nothing moved yet) and then 404s in production once the item moves. The fix is a one-line request header, `Prefer: IdType="ImmutableId"`, which makes Graph return an ID that survives moves. Use immutable IDs for **anything you persist** (a database row, a webhook correlation key, a stored `eventId`).

## How to apply

Send the `Prefer` header on the request whose IDs you intend to store, and **keep using immutable IDs consistently** — a default ID and an immutable ID for the same item are different strings and are not interchangeable across calls.

```http
GET https://graph.microsoft.com/v1.0/me/messages?$select=id,subject
Prefer: IdType="ImmutableId"
# the returned message.id now survives a folder move; store THIS one
```

**Do:**

- Set `Prefer: IdType="ImmutableId"` on reads whose `id` you will persist (mail, events, contacts).
- Pick one ID type per stored dataset and stay on it — don't mix default and immutable IDs in the same table.
- Re-request with the same header on every subsequent call that takes that stored ID.

**Don't:**

- Store the default `id` for any item that can be moved (essentially all mail/calendar items).
- Assume an ID you got without the header is comparable to one you got with it — they differ.
- Rely on immutable IDs to be portable **across mailboxes** — they are stable within a mailbox, not a tenant-wide GUID.

## Edge cases / when the rule does NOT apply

A transient read you never persist (display a list, act on it, discard) doesn't need immutable IDs. Immutable IDs must be **enabled** for the mailbox/tenant — on some configurations the header is honored only after the feature is on `[verify-at-build]`. Drive items (files) and directory objects (users, groups) use their own stable IDs and are out of scope for this rule — it is specifically the Outlook (`message`/`event`/`contact`) default-ID instability that bites.

## See also

- [`./workloads-calendar-recurrence-and-timezone.md`](./workloads-calendar-recurrence-and-timezone.md) — stored `event` references should be immutable too
- [`../knowledge/workloads-notifications-decision-trees.md`](../knowledge/workloads-notifications-decision-trees.md) — the ID-stability decision tree
- [`../agents/graph-workloads-engineer.md`](../agents/graph-workloads-engineer.md) — owns mail/calendar
- [Get immutable identifiers for Outlook resources](https://learn.microsoft.com/graph/outlook-immutable-id) — authoritative

## Provenance

From the Microsoft Learn "Get immutable identifiers for Outlook resources" page (the documented `Prefer: IdType="ImmutableId"` mechanism), codifying a recurring production failure mode (stored IDs breaking on folder move) the workloads agent had no citable rule for — surfaced by the two-panel coverage audit 2026-06-01. Feature-enablement state is `[verify-at-build]`.

---

_Last reviewed: 2026-06-01 by `claude`_
