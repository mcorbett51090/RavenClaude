---
name: sample-app-and-demo-engineering
description: "Build sample apps and demos that survive a real developer — anchor on the job-to-be-done, eliminate magic setup and happy-path-only flows, show one realistic failure-and-recovery, declare versions, and leave behind a runnable artifact that becomes an activation path."
---

# Sample App & Demo Engineering

**Purpose:** produce demos and sample apps that build trust with a technical audience because a real
developer can type along and reproduce them — and that leave behind a runnable artifact which doubles
as an activation path.

---

## Steps

### 1. Anchor on the job-to-be-done

Start from the developer's actual problem, not the product's feature tour. "Add auth to a Next.js
app" beats "explore our auth API." The demo earns attention by solving something the developer
already wants done.

### 2. Kill the magic

The trust-killers in a demo:

| Anti-pattern | Why it destroys trust | Fix |
|---|---|---|
| Pre-warmed/hidden state | Developer can't reproduce it | Start from a clean, declared state |
| Undeclared versions | Breaks on the developer's machine | Pin and declare every version |
| Happy-path-only | Hides where real use breaks | Show one realistic failure + recovery |
| Glossed-over setup | "Setup is left as an exercise" loses people | Make setup part of the demo, timed |

### 3. Show one realistic failure and its recovery

A demo where everything "just works" teaches nothing and reads as sleight of hand. Deliberately
trigger one common error (bad key, missing param, rate limit) and show the recovery. This is where
trust is actually won.

### 4. Keep it runnable and small

The sample app should clone-and-run with declared prerequisites and a single command to first result.
Smaller and reproducible beats comprehensive and fragile. The repo is the deliverable.

### 5. Make the artifact an activation path

End the demo with the runnable repo, a quickstart link, and the next concrete step toward the
developer's own first success — so the demo converts instead of merely informing
(see [`every-artifact-ends-with-an-activation-path`](../../best-practices/every-artifact-ends-with-an-activation-path.md)).

---

## Output

A demo spec (job-to-be-done, the failure-and-recovery beat, declared versions, the runnable artifact)
and the activation path it leaves behind. Pairs with the
[`developer-content-and-advocacy-reference`](../../knowledge/developer-content-and-advocacy-reference.md).
