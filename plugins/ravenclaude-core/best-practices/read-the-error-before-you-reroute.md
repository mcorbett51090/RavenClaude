# Read the error before you re-route — the cause selects the alternative, not the symptom

**Status:** Absolute rule
**Domain:** Agent design / Capability Grounding / Error handling
**Applies to:** `ravenclaude-core`

---

## Why this exists

The Capability Grounding Protocol's alternate-methods rule says: when Approach A fails, enumerate alternatives and try the next-easiest. That enumeration is only correct if you know *why* Approach A failed. A blind re-route — switching surfaces without reading the error — guesses at the cause and often picks an alternative that breaks for exactly the same reason. A `401` from an expired token means re-authenticate and retry the same route, not switch to a different surface. A `403` from insufficient scope means find a surface that already holds the scope. A `command not found` means the tool is absent on this host. A deferred MCP tool without a loaded schema means search/await, not "capability absent." Each cause selects a different next move — they are not interchangeable.

## How to apply

Step 0 of the alternate-methods enumeration (before listing alternatives):

**1. Read the status code AND the response body/stderr** — not just the headline. These are already in hand; reading them costs zero additional calls.

**2. Name the specific mechanical cause** — one of these five:

| Status / symptom | Specific cause | Correct next move |
|---|---|---|
| `401` + "token expired" or missing | Authentication failure | Re-authenticate, then **retry Approach A** |
| `403` + "insufficient scope/role" | Authorization failure — wrong surface | Use the surface that already has the scope |
| `404` | Wrong route, resource moved, or renamed | Fix the parameter; retry |
| `command not found` | Tool absent on this host | Find the sanctioned route for this capability on this host |
| `InputValidationError` on an MCP tool | Schema not loaded yet | Run `ToolSearch` to load the schema; then call the tool |

**3. Probe further only when in-hand evidence is ambiguous AND the next route is costly or irreversible** — one targeted diagnostic read, not a hunt.

**4. A diagnosis is never a stopping point** — it obligates the correct next action (retry-after-fix, or the route the cause selects), never a `blocked` report.

**Do:**
- Read the full response body when it's available — the body often names the specific permission or resource that caused the failure.
- Treat "401 = re-authenticate + retry" and "403 = different surface" as distinct, not interchangeable — the distinction saves the round-trip of trying the wrong surface.
- Include the diagnosis in the mandatory-phrasing block if you do eventually reach a blocked report: "[error status + body] → identified cause: [X] → tried [approach matching X's fix] → still blocked because [Y]."

**Don't:**
- Switch surfaces on a `401` without re-authenticating — you will get a `401` on the new surface too, for the same reason.
- Treat any single error as proof the capability is absent — it is evidence about one route at one moment.
- Narrate an analysis when the cause is plain from the body; read and act.

## Edge cases / when the rule does NOT apply

- When the error body is empty or generic (e.g., a raw TCP reset or a blank `500`) and there is no structured error to read, the probe-further step applies: one additional diagnostic call to the same surface to confirm the error is persistent and structural before re-routing.

## See also

- [`./three-epistemic-protocols.md`](./three-epistemic-protocols.md) — the Capability Grounding Protocol of which this rule is step 0.
- [`../CLAUDE.md`](../CLAUDE.md) — "Read the error before you re-route (added 2026-05-31)" section.

## Provenance

Distilled from `plugins/ravenclaude-core/CLAUDE.md` §"Read the error before you re-route (added 2026-05-31)" — the clause that closes the blind-re-route failure mode within the Capability Grounding Protocol.

---

_Last reviewed: 2026-06-05 by `claude`_
