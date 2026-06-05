> Use this template to document a Microsoft Graph change notification subscription — resource, expiry, renewal strategy, validation endpoint, and the lifecycle handling plan.

# Change Notification Subscription: [Subscription Name]

## Metadata

| Field | Value |
|---|---|
| Subscription name | [Logical name for this subscription] |
| App registration | [App name + client ID] |
| Environment | [Dev / Test / Production] |
| Owner | [Name / Team] |
| Last reviewed | [YYYY-MM-DD] |

---

## Subscription parameters

| Parameter | Value |
|---|---|
| Resource | [e.g., `/me/mailFolders('Inbox')/messages` or `/users/{id}/events`] |
| Change types | [ ] created [ ] updated [ ] deleted |
| Graph version | [ ] v1.0 / [ ] /beta (must flag if /beta — do not ship to production unmarked) |
| Max expiry | [e.g., 4 230 min for mail; 43 200 min for users] `[verify-at-build]` |
| Renew when | [X minutes before expiry — recommended: 60 min] |
| Notification URL | `https://[your-endpoint]/graph/notify` |
| Lifecycle notification URL | `https://[your-endpoint]/graph/lifecycle` |
| Client state | [A secret value your endpoint uses to validate incoming notifications — store in Key Vault] |

---

## Validation endpoint spec

Graph sends a GET request with `validationToken` query param before creating the subscription. Your endpoint must respond within 10 seconds:

```
GET {notificationUrl}?validationToken=<token>
→ HTTP 200
   Content-Type: text/plain
   Body: <exactly the validationToken value>
```

- [ ] Validation handler implemented
- [ ] Response time < 10 s under load
- [ ] Returns `text/plain` (not `application/json`)

---

## Notification payload handling

| Step | Implementation notes |
|---|---|
| Receive POST to notificationUrl | Respond HTTP 202 immediately; process async |
| Validate `clientState` field | Compare to stored secret; reject if mismatch |
| Check `subscriptionId` | Matches a known active subscription; reject unknown |
| Process `value[]` array | One entry per changed resource; process each independently |
| Handle duplicate delivery | Use `changeType` + `resource` + `changeKey` for deduplication |

**Rich notifications (encrypted payload):**
- [ ] Not used for this subscription
- [ ] Used — `encryptionCertificate` registered; decryption key stored in Key Vault; rotation schedule: [X days before cert expiry]

---

## Lifecycle notification handling

Graph sends lifecycle notifications when a subscription is about to expire or has missed events:

| Lifecycle event | Action |
|---|---|
| `subscriptionRemoved` | Re-create the subscription; run a delta-query catch-up |
| `missed` | Run a delta-query catch-up to recover missed events |
| `reauthorizationRequired` | Re-authenticate and renew the subscription |

- [ ] Lifecycle notification URL implemented and tested
- [ ] Delta-query catch-up procedure documented: [Link or procedure]

---

## Renewal strategy

```
Every [30] minutes:
  For each subscription in the subscriptions store:
    If expiry - now < 60 minutes:
      PATCH /subscriptions/{id}
        { "expirationDateTime": "<now + max_expiry>" }
      Update stored expiry on success
      Alert on failure (subscription may have already expired)
```

- [ ] Renewal job scheduled (cron / Azure Function timer / etc.)
- [ ] Alert on renewal failure: [Channel]
- [ ] Alert on subscription not found (already expired): [Channel]

---

## State storage schema

| Field | Type | Description |
|---|---|---|
| `subscription_id` | UUID | Graph subscription ID |
| `resource` | string | Graph resource path |
| `expiration` | datetime | Current expiry (UTC) |
| `client_state` | string (encrypted) | For validating incoming notifications |
| `created_at` | datetime | When the subscription was first created |
| `last_renewed_at` | datetime | Last successful renewal |
| `status` | enum | active / expired / renewal_failed |

---

## Test plan

- [ ] Validation handshake: create the subscription; confirm Graph calls validationUrl and subscription is created.
- [ ] Event delivery: trigger a change on the subscribed resource; confirm notification arrives within [X seconds].
- [ ] Duplicate handling: manually send a duplicate notification payload; confirm idempotent processing.
- [ ] Expiry: let a test subscription expire; confirm `subscriptionRemoved` lifecycle notification is received and re-creation fires.
- [ ] Renewal: advance system clock to within 60 min of expiry (or use a short-lived test subscription); confirm renewal fires.
