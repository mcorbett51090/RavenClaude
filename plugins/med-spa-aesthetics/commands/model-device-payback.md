---
description: "Model whether a capital aesthetic device pays for itself: device cost + consumables + provider time vs realistic treatment volume and price, against the room-hours it locks up, with the break-even utilization named and the vendor's full-utilization claim re-derived on honest volume (verify-at-use)."
argument-hint: "[device cost + consumable cost + treatment price + realistic weekly volume + room-hours it consumes]"
---

You are running `/med-spa-aesthetics:model-device-payback`. Use `med-spa-operations-lead` + the `service-mix-injectables-devices-memberships` and `treatment-room-and-injector-utilization` skills.

> Operations decision-support, not legal, tax, or medical advice. Vendor payback quotes are a **sales input, not a benchmark** — re-derive on the practice's realistic volume. Any scope/supervision structure the device raises routes to `aesthetics-compliance-advisor`. No patient PHI/PII.

## Steps

1. Capture device cost (financed or cash), per-treatment consumable cost, treatment price, and the practice's **realistic** weekly/monthly treatment volume — not the vendor's full-utilization assumption.
2. Capture the room-hours per treatment and confirm the current room/injector utilization (is the practice even capacity-constrained? — traverse the **add a service or device** tree in `knowledge/med-spa-decision-trees.md`).
3. Compute contribution per treatment (price − consumable − provider time cost) and per room-hour; derive the **break-even utilization** (treatments/period to cover the capital + carrying cost).
4. Compare the device's room-hours against the **alternative use of that capacity** (injectables, other services). An idle device is worse than the hours it displaced.
5. Mark every benchmark/vendor claim `[verify-at-use]`; route any scope/supervision question to the compliance advisor.
6. Emit using `templates/service-and-device-pro-forma.md` + the Structured Output block, with the go/no-go, the break-even utilization, and the two things that would change the answer.
