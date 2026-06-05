# Assign experiments server-side to prevent flicker and assignment leakage

**Status:** Pattern
**Domain:** Experimentation / frontend assignment
**Applies to:** `experimentation-growth-engineering`

---

## Why this exists

Client-side experiment assignment — JavaScript running in the browser after page
load to decide which variant to show — causes two compounding problems. First,
the user briefly sees the control state before the variant renders: the "flicker"
problem, which is a poor UX and an implicit signal that biases click-through rates.
Second, the assignment logic and the full flag payload are visible in the page
source, which leaks information about unreleased features to anyone who inspects
the DOM. Server-side assignment (resolving the variant before the response leaves
the server) eliminates both.

## How to apply

Resolve the variant on the server, inject the pre-decided experience into the
HTML/JSON response, and optionally pass a client-side SDK in a "pre-initialised"
mode that only receives a pre-resolved evaluation (not the full ruleset).

```python
# Server-side Python example
from launchdarkly_client import LDClient  # or your platform's SDK

def get_checkout_variant(user: User) -> str:
    ld = LDClient(sdk_key=os.environ["LD_SDK_KEY"])
    variant = ld.variation("new-checkout-flow", user.to_ld_user(), "control")
    # Log the exposure event at the same time as the decision
    analytics.track(user.id, "Experiment Exposure", {
        "experiment_id": "new-checkout-flow",
        "variant": variant,
    })
    return variant  # "control" | "treatment"

# In the route handler:
variant = get_checkout_variant(current_user)
return render_template("checkout.html", variant=variant)
```

For SPAs and mobile apps where the first render is client-side, use the SDK's
"bootstrap" / "pre-evaluated" mode: send the resolved flags in the initial
server response payload and initialise the SDK from that payload, not from a
fresh evaluation.

**Do:**
- Resolve and log the exposure on the server before sending the response.
- Use the bootstrap/pre-evaluated mode for SPAs rather than a full client-side
  SDK evaluation.
- Treat the flag payload sent to the client as minimal — only the evaluated
  result, not the full ruleset.

**Don't:**
- Resolve flags in a browser `DOMContentLoaded` handler if the variant affects
  above-the-fold content.
- Send the full targeting rule payload to the client (it leaks the unreleased
  feature logic).
- Rely on CSS hiding as a flicker workaround — it hides the flash but still
  leaks the variant content to screen readers and scrapers.

## Edge cases / when the rule does NOT apply

- Personalisation features where the variant is determined entirely by user
  preference data available only on the client (e.g. browser timezone): a
  client-side resolution for that specific dimension is appropriate.
- Low-stakes cosmetic variants (button colour only, no content change): client-
  side with a fast SDK may be acceptable if flicker is sub-100ms.

## See also

- [`../agents/feature-flag-engineer.md`](../agents/feature-flag-engineer.md) — owns SDK integration and assignment
- [`./deterministic-assignment-server-side.md`](./deterministic-assignment-server-side.md) — determinism requirement for the assignment hash
- [`./separate-deploy-from-release.md`](./separate-deploy-from-release.md) — server-side flags enable deploy-dark without flicker

## Provenance

Standard feature-flag engineering practice for flicker prevention. The bootstrap
pattern is documented in LaunchDarkly, Unleash, and similar SDK documentation
`[verify-at-use]`. Assignment leakage concerns are standard security practice for
unreleased feature confidentiality.

---

_Last reviewed: 2026-06-05 by `claude`_
