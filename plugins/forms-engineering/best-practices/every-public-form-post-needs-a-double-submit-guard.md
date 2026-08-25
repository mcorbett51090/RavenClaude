# Every public form POST needs a double-submit guard

**Status:** Absolute rule — anti-forgery is not anti-duplicate. A form that can be submitted twice will be.
**Domain:** Forms engineering — submission integrity
**Applies to:** `forms-engineering`

---

## Why this exists

"We have CSRF protection" is offered constantly as an answer to duplicate submissions, and it is not one. The two mechanisms defend against different adversaries:

| | Cross-site request forgery | Duplicate submission |
| --- | --- | --- |
| **Adversary** | A third-party site making the user's browser submit | Nobody. An impatient user, a slow network, a back button, a mobile browser restoring a page |
| **Defeats** | A request the user never intended | A request the user intended exactly once |
| **Mechanism** | A secret the third-party site cannot read, plus an origin check and cookie policy | A token the server records as **spent**, or a natural key the server deduplicates on |
| **Symptom when absent** | An action taken on the user's behalf | Two tickets, two emails, two charges, two rows |

An anti-forgery token that the server accepts more than once stops forgery and does nothing about duplicates. Both mechanisms can share a token, but only if the server **records the token as consumed** on first acceptance — and that is a deliberate design decision, not a side effect.

Duplicates are not a cosmetic problem. On a support form they are wasted triage. On anything that charges, notifies, or provisions, they are a customer-visible failure, and the second copy usually arrives without the context that would let anyone tell it is a duplicate.

## How to apply

Pick one of two shapes and write down which:

**Server-recorded token.** Issue a token with the form. On POST, atomically move it from issued to spent; if it was already spent, return the **same** result as the first submission rather than an error. A duplicate that returns an error trains users to submit a third time.

**Natural-key deduplication.** Derive a key from the submission's own content plus the actor and a time bucket, and treat a repeat within the window as the same submission. This is the better shape when the form is posted by something other than a browser, because it does not depend on the client holding state.

Then, regardless of shape:

- **Make the response idempotent, not just the write.** The user must see success, not a conflict.
- **Disable the submit control on first submit** as a courtesy — and never as the mechanism. It is client-side and therefore not a guard.
- **Log the duplicate rate.** It is the cheapest available signal that something upstream is slow.

Key construction, window choice and the API-layer contract route to [`../../api-engineering/skills/idempotency-key-design/SKILL.md`](../../api-engineering/skills/idempotency-key-design/SKILL.md).

## The anti-pattern

A redirect-after-POST alone. It stops the browser's refresh from resubmitting and does nothing about a double-click, a retried request, or a client that never saw the response.

## Source

The distinction is drawn in [`../knowledge/form-anti-abuse.md`](../knowledge/form-anti-abuse.md) §5. The observation that generic form POST handlers commonly carry anti-forgery and no duplicate guard is `[unverified — inference from route reading, not an exhaustive sweep]`; the settling probe is a route-by-route sweep keyed on **behaviour** — does the handler deduplicate? — never on the presence of the word "idempotent".
