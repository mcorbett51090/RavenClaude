# Form anti-abuse: the ladder, the honeypot, and what we do not own

**Retrieved / verified:** 2026-08-17.

⛔ **Read this boundary first.** Two adjacent topics are owned by the constitution and are **cited here, never restated**:

- **Upload hardening** — untrusted filenames, path traversal, type validation, size ceilings: [`../../ravenclaude-core/rules/security.md`](../../ravenclaude-core/rules/security.md) §File handling.
- **Challenge-widget mechanics** — token lifetime, the replay rule, server-side verification at submit, hostname scope, and the Access-vs-challenge-vs-WAF boundary: [`../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md`](../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md).

Those files are dated, sourced and carry a `refresh_when:` clause. A copy of them here would rot the moment the upstream vendor moves, and nothing would point at the copy. If you find yourself about to write a sentence that belongs in either, write a link instead.

---

## 1. The bot-defense ladder — reach in this order

Bot defense is a ladder, not a switch. Each rung costs a different currency, and the expensive rungs are only worth buying once the cheap ones are in place.

| Rung | What it costs | What it stops | When it is the wrong tool |
| --- | --- | --- | --- |
| **1. Make the endpoint boring** — no reflected content, no enumeration signal, uniform responses | Design attention | Scrapers looking for a lever | Never wrong; do it first |
| **2. Rate limit by identity, then by network** | A storage decision and a fail-open/fail-closed ruling | Volume abuse, credential stuffing | When the abuse is one submission per actor |
| **3. Honeypot field** | A few lines of markup, and the exemption discipline in §2 | Naive form-filling bots | When your users' assistive tech or password manager can see it |
| **4. Server-side content heuristics** — link counts, language mismatch, disposable-domain checks | False positives against real customers | Spam that is semantically distinctive | When the "spam" is a legitimate terse enquiry |
| **5. A challenge widget** | Third-party dependency, latency, an accessibility question you cannot answer for the user | Automated submission at scale | When the traffic is small enough that a human reviewer is cheaper |
| **6. Human review queue** | Ongoing staff time | Everything, eventually | When volume makes it a bottleneck rather than a control |

**The most common mistake is starting at rung 5.** A challenge widget in front of a form that receives a handful of submissions a week buys a third-party dependency, a latency cost and an unresolved accessibility question in exchange for stopping abuse that a human would have deleted in seconds.

---

## 2. The honeypot, and the two populations it must not catch

A honeypot is a field a human never fills because they never perceive it. It is the cheapest useful rung, and it is cheap **only** if it stays invisible to two populations that are not bots:

1. **Assistive technology.** A field hidden with CSS alone is still in the accessibility tree. A screen-reader user reaches it, hears a plausible label, fills it in, and is silently rejected. This is the failure mode that makes a honeypot worse than nothing: it is invisible to your analytics, indistinguishable from abandonment, and it targets exactly the users least able to work around it.
2. **Password managers and browser autofill.** A field named `email2`, `address`, `phone` or `company` is a magnet for autofill. The user never sees it get filled.

The three properties that make a honeypot safe are in [`../best-practices/a-honeypot-must-be-invisible-to-assistive-tech-and-to-autofill.md`](../best-practices/a-honeypot-must-be-invisible-to-assistive-tech-and-to-autofill.md). The short version: it must be removed from the accessibility tree, removed from the tab order, opted out of autofill, and named something autofill has no heuristic for.

**And it must be observable.** A honeypot that silently drops submissions is a data-loss mechanism you cannot audit. Count rejections; alert when the count moves.

---

## 3. The time-trap, marked as unverified

The time-trap — reject a submission that arrives faster than a human could plausibly complete the form — is widely recommended and, as far as we can establish, **unvalidated against real user populations** `[unverified — premise not disconfirmed; no false-positive-rate study located, open-web search 2026-08-17]`.

The concern is specific and testable: a returning user whose password manager fills every field at once, or a user copying from a prepared document, can complete a short form in well under any plausible human floor. We have not measured this, and we do not know the false-positive rate.

**Ship it hedged or not at all.** If you use it, log the rejections separately from every other rejection class so the false-positive rate becomes measurable rather than assumed. The settling experiment is named: instrument a real form with a threshold, do not reject on it, and measure how often it *would* have fired against sessions you can confirm were human.

---

## 4. The challenge widget's WCAG conformance level is DISPUTED

Mechanics, token lifetime and the replay rule for Turnstile are owned upstream — see [`../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md`](../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md). What upstream does not carry is the following conflict, and this plugin does not resolve it either:

> The vendor's own documentation gives **WCAG 2.2 AA** on its product overview page and **WCAG 2.2 AAA** on its plans page (both retrieved 2026-08-17). We do not repeat either figure unqualified; treat the widget's conformance level as **unestablished pending a VPAT**, and verify independently before relying on it.

This matters because a conformance claim is exactly the kind of statement that gets pasted into an accessibility statement and then defended. Do not put a level in an accessibility statement you cannot source to a document that agrees with itself.

⛔ **Known gap, recorded rather than quietly accepted:** this caveat lives here, in a sibling plugin. A future edit to the upstream concept doc that states one level unqualified would not be caught by this plugin's gate. Moving the caveat upstream is an owner-routed change, not one this plugin makes.

---

## 5. Anti-forgery and anti-duplicate are different problems

They get conflated because both involve a token on a form, and the conflation ships forms that are protected against one and not the other.

| | Cross-site request forgery | Duplicate submission |
| --- | --- | --- |
| **The attacker** | A third-party site making the user's browser submit | Nobody — an impatient user, a flaky network, a back button |
| **What it defeats** | A request the user did not intend | A request the user intended **once** |
| **The mechanism** | A secret the third-party site cannot read (double-submit cookie, `SameSite`, an origin check) | A token the server records as spent, or a natural key it deduplicates on |
| **Failure looks like** | An action taken on the user's behalf | Two support tickets, two charges, two emails |

An anti-forgery token that is accepted twice does not stop a duplicate. A duplicate guard that is readable by a third party does not stop forgery. Both, or name which one you are choosing not to do. See [`../best-practices/every-public-form-post-needs-a-double-submit-guard.md`](../best-practices/every-public-form-post-needs-a-double-submit-guard.md), and route key design to [`../../api-engineering/skills/idempotency-key-design/SKILL.md`](../../api-engineering/skills/idempotency-key-design/SKILL.md).

---

## 6. Degraded defense must be loud

A bot defense that fails open when its secret is unset is a defensible engineering choice: it keeps the form working during a misconfiguration rather than silently rejecting every real customer. **A defense that fails open quietly is not.** The distinction is the whole of [`../best-practices/degraded-bot-defense-must-be-loud.md`](../best-practices/degraded-bot-defense-must-be-loud.md).

---

## 7. What this file does not own

- **Upload handling of any kind** → [`../../ravenclaude-core/rules/security.md`](../../ravenclaude-core/rules/security.md).
- **Challenge-widget wiring, verification and replay** → [`../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md`](../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md).
- **The binding security verdict on any of this** → [`../../ravenclaude-core/agents/security-reviewer.md`](../../ravenclaude-core/agents/security-reviewer.md), zero-exception.
- **API-layer authorization** → [`../../api-engineering/agents/api-security-engineer.md`](../../api-engineering/agents/api-security-engineer.md).
