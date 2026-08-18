# Degraded bot defense must be loud

**Status:** Absolute rule — failing open when a defense cannot run is defensible. Failing open **quietly** is not.
**Domain:** Forms engineering — anti-abuse operations
**Applies to:** `forms-engineering`

---

## Why this exists

Every anti-abuse layer has a dependency it can lose: a secret that is unset in one environment, a third-party service that is unreachable, a quota that is exhausted, a network path that is blocked. The handler then has to choose:

- **Fail closed** — reject the submission. Correct for a high-value write; catastrophic for a contact form, where it silently blocks every real customer.
- **Fail open** — accept the submission unverified. Correct for a low-value write; it keeps the front door working during a misconfiguration.

**Both are legitimate.** The defect is not the choice. The defect is making the choice **invisible**, because a silently-degraded defense has all of the following properties at once:

- The form works, so nobody reports it.
- Traffic looks normal, so no dashboard moves.
- The defense reports nothing, because it never ran.
- The first signal is a spam wave, weeks later, which then gets diagnosed as "the vendor's filter got worse".

A defense you cannot tell is off is not a defense. It is a belief.

## How to apply

1. **Rule the direction per route, in writing.** Fail-open and fail-closed are both fine; "whatever the code happens to do" is not. Put the ruling in the form spec next to the route.
2. **Emit a distinct, greppable signal on every degraded acceptance** — its own log event with its own name, not a line buried in a request log. Someone must be able to answer "how many submissions were accepted unverified last week?" with one query.
3. **Alert on the transition, not on the volume.** The first degraded acceptance after a period of none is the event worth waking up for.
4. **Surface it where humans already look.** A counter on the operator dashboard beats a log nobody opens.
5. **Make it visible in the environment where it happens most** — a secret set in production and unset in preview is the common shape, and preview is where the silence lasts longest.
6. **Never let a missing secret be indistinguishable from a passing check.** If the verification result and "we did not verify" share a code path, they will be conflated by the next person to read it.

## The anti-pattern

```
if (!SECRET) return { ok: true };   // no log, no metric, no comment
```

Three characters of control flow, no signal, and a form with no bot defense at all in every environment where the secret is unset. The fix is not to change the return value — it is to make the return value **announce itself**.

## Source

Generalised from a real, verified observation of a live handler that fails open on an unset verification secret with no signal emitted, recorded in this plugin's substrate knowledge file (`knowledge/ravenpower-form-substrate.md` — referenced, deliberately not linked, so the substrate layer stays deletable). The rule generalises to any defense with a dependency; the specific posture is described there, not here.
