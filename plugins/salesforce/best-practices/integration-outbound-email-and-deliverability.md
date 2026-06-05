# Configure email deliverability and use Org-Wide Email Addresses for outbound email — not user addresses

**Status:** Pattern
**Domain:** Integration / email
**Applies to:** `salesforce`

---

## Why this exists

Salesforce sends email from the current user's address by default when Apex triggers `Messaging.sendEmail()` without specifying a sender. In production, this means:
1. Every email to a customer appears to come from whichever developer's or admin's account is running the process — confusing to recipients and damaging to brand.
2. The user's personal email address bounces if they leave the company, silently breaking email delivery.
3. Email deliverability is `org-specific` — sandbox orgs are in "No Access" mode by default and will not deliver any email at all until the mode is changed.

Org-Wide Email Addresses (OWEAs) and the `Messaging.SingleEmailMessage.setOrgWideEmailAddressId()` method are the correct primitives for any production outbound email.

## How to apply

Setup:
1. **Deliverability mode** — `Setup → Deliverability → Access Level`. Set to `All Email` in production and sandbox(es) used for integration testing. Default sandbox mode is `No Access` — every email call silently succeeds but delivers nothing.
2. **OWEA** — `Setup → Organization-Wide Email Addresses` → create a shared address (e.g., `noreply@yourdomain.com`) and verify it.

```apex
// Resolve the OWEA ID by address (store in Custom Metadata, not hard-coded)
OrgWideEmailAddress[] oweas = [
    SELECT Id FROM OrgWideEmailAddress
    WHERE Address = :Label.Notification_Sender_Email  // resolved from Custom Label
    LIMIT 1
];

Messaging.SingleEmailMessage email = new Messaging.SingleEmailMessage();
email.setToAddresses(new List<String>{ recipient });
email.setSubject('Your order is ready');
email.setHtmlBody('<p>Hello!</p>');
if (!oweas.isEmpty()) {
    email.setOrgWideEmailAddressId(oweas[0].Id);
} else {
    email.setSenderDisplayName('Support Team');  // fallback: display name only
}

Messaging.sendEmail(new List<Messaging.SingleEmailMessage>{ email });
```

**Do:**
- Store the OWEA address in a Custom Label or Custom Metadata record — not hard-coded in Apex — so it can differ between sandbox and production.
- Confirm deliverability mode is set to `All Email` in every sandbox used for QA or integration testing.
- Check `Messaging.SendEmailResult.isSuccess()` and log failures — `sendEmail()` does not throw an exception for per-message delivery failures; it returns a result array.

**Don't:**
- Use a named user's personal email as the `from` address for automated process emails.
- Run integration tests in a sandbox with the default `No Access` deliverability mode and assume email works — it silently discards every message.
- Send email from an OWEA that hasn't been verified by the receiving mail domain — unverified addresses trigger DMARC failures and are often bounced.

## Edge cases / when the rule does NOT apply

For `Messaging.sendEmail()` calls in a Visualforce-based user-triggered workflow where the user intentionally sends from their own identity (e.g., forwarding a case to a colleague), the current-user address is correct and no OWEA is needed.

## See also

- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns Apex email integration
- [`./integration-named-credentials-not-hardcoded-endpoints.md`](./integration-named-credentials-not-hardcoded-endpoints.md) — the same "no hard-coded config" principle applied to outbound callouts

## Provenance

Codifies standard Salesforce outbound email best practice; Salesforce Deliverability documentation + Org-Wide Email Addresses setup guide.

---

_Last reviewed: 2026-06-05 by `claude`_
