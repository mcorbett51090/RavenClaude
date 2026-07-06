---
name: plan-network-change
description: Turn a network change (routing/VLAN/firewall/cutover) into a staged, reversible plan — blast-radius assessment, change window, pre-checks (baseline), the staged steps with verification gates, and a tested rollback — so no change is a big-bang gamble. Reach for this when the user needs to make a risky network change safely or migrate/cut over network infrastructure. Used by `network-operations-engineer` and `network-architect`.
---

# Skill: plan-network-change

> **Invoked by:** `network-operations-engineer` (primary) and `network-architect` (handing a design to implementation).
>
> **When to invoke:** "we need to change <routing config / VLAN / firewall> safely"; "migrate/cut over <network infra>"; any change to a running network.
>
> **Output:** a windowed, reversible change plan. No big-bang cutovers.

## Procedure

1. **Assess the blast radius.** What does this touch, who depends on it, what is the worst case if it goes wrong? A core-routing change ≠ adding an access VLAN. Size the change-control rigor to the blast radius.
2. **Capture a pre-change baseline.** The state you must be able to *return to and compare against*: routing table snapshot, interface/neighbor status, reachability tests, config backup. You can't verify success or roll back cleanly without it.
3. **Pick a change window** appropriate to the blast radius and the business — and notify dependents. Risky changes happen in a maintenance window, not at 2pm on a Tuesday.
4. **Stage the steps** so each is verifiable and the system is in a known state between steps:
   - Prefer **expand/contract** and **parallel-run** over cutover where possible (add the new path, shift traffic, then remove the old) — the network analog of a safe migration.
   - Insert **verification gates** between steps: "confirm neighbor up / route present / reachability holds" before proceeding.
5. **Write the rollback and *test it mentally step-by-step*.** For each forward step, the reverse. A rollback you haven't thought through is not a rollback. Include the trigger ("if reachability test fails at gate 2, execute rollback").
6. **Define success and post-checks** — re-run the baseline tests; compare to pre-change. Only then declare done.
7. **Capture the diff and the why** — an undocumented change is an un-diagnosable future outage.

## House guardrails

- **No change without a tested rollback** — this is the non-negotiable.
- **Baseline before you touch anything** — you can't prove success against a state you never recorded.
- **Verification gates between steps** beat a single end-of-change check — they localize a failure to the step that caused it.
- **Codify the final state in IaC** where the environment supports it → route to `terraform-iac` so the change is repeatable and reviewable.
- **Out-of-band access before a routing/firewall change** — don't change the thing you're connected through without a console/OOB path back in.

## Output contract

```
Change: <what + why>
Blast radius: <scope + worst case> -> change-control rigor: <level>
Baseline / pre-checks: <snapshots + tests to capture first>
Window: <when + who is notified>
Steps: <staged, each with a verification gate; expand/contract where possible>
Rollback: <reverse of each step + the trigger condition>
Post-checks: <success definition = baseline re-run + compare>
Record: <diff + rationale captured where>
```

Then emit the Structured Output Protocol JSON block.
