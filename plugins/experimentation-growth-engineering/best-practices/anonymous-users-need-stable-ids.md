# Give anonymous users stable ids before assigning experiments

**Status:** Absolute rule
**Domain:** Experimentation / identity
**Applies to:** `experimentation-growth-engineering`

---

## Why this exists

An experiment assigned to a session id, a request id, or a new UUID on every
page load re-randomizes on every navigation: the same user may be in control on
one page and treatment on another during the same browsing session. This produces
impossible exposure logs (the same user in both variants), corrupt metric
calculations, and — if the two variants produce different page states — a broken
user experience. Anonymous users need a stable id that persists for at least the
duration of an experiment before any experiment assignment happens.

## How to apply

Generate a stable anonymous id on first visit (a UUID v4 stored in a
first-party cookie or local storage) and use it as the assignment key for all
experiments. The same anonymous id should survive:
- Multiple page loads in the same session.
- Browser refresh and back-navigation.
- Reasonable session gaps (30–90 days is typical — align with your retention
  analysis window).

```javascript
// Client-side anonymous id generation (adapt to your stack)
function getOrCreateAnonymousId(): string {
  const COOKIE_NAME = "anon_id";
  let id = getCookie(COOKIE_NAME);
  if (!id) {
    id = crypto.randomUUID();
    setCookie(COOKIE_NAME, id, { maxAge: 60 * 60 * 24 * 90 }); // 90 days
  }
  return id;
}

// Server-side assignment uses the anon id as the user key
const anonId = req.cookies.anon_id;
const variant = flagClient.variation("experiment-key", { key: anonId }, "control");
```

When the user logs in, run the `identify()` call to stitch the anonymous id to
the known user id — the exposure log entry should carry both to enable
pre-/post-login funnel analysis.

**Do:**
- Set the anonymous id cookie before any experiment evaluation on the first
  request.
- Use the same anonymous id as the assignment key throughout the experiment
  lifecycle.
- Stitch to the known user id on login (`identify()` call with `anonymousId`).

**Don't:**
- Use session ids as experiment assignment keys — they expire and regenerate.
- Use IP addresses as assignment keys — shared IPs split the same user into
  multiple assignment buckets.
- Use new UUIDs generated per request or per component render.

## Edge cases / when the rule does NOT apply

- Authenticated-only experiments: if every user in scope is logged-in, the
  known user id is the correct assignment key and anonymous ids are irrelevant.
- Truly ephemeral experiments (e.g. "show this modal once per visit"): session-
  scoped assignment is intentional — but document that explicitly; it is not a
  standard A/B test.

## See also

- [`../agents/experimentation-architect.md`](../agents/experimentation-architect.md) — owns assignment design
- [`./stitch-identity-across-the-login-boundary.md`](./stitch-identity-across-the-login-boundary.md) — post-login identity stitching completes the anonymous-id lifecycle
- [`./check-srm-before-trusting-a-result.md`](./check-srm-before-trusting-a-result.md) — unstable ids produce SRM; SRM is the diagnostic signal

## Provenance

Standard experimentation infrastructure practice. The stable-anonymous-id
requirement is documented in Amplitude, Segment, and platform-specific A/B
testing SDKs `[verify-at-use]`. The failure mode (session-id assignment) is a
common error described in Kohavi et al. "Trustworthy Online Controlled
Experiments" Ch. 21.

---

_Last reviewed: 2026-06-05 by `claude`_
