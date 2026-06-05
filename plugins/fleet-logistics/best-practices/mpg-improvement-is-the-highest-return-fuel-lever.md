# MPG Improvement Is the Highest-Return Fuel Lever

**Status:** Pattern
**Domain:** Fuel management
**Applies to:** `fleet-logistics`

---

## Why this exists

Fuel cost is the largest variable in trucking CPM, and fleet managers frequently focus on pump price (which they cannot control) instead of MPG (which they can). A 1-MPG improvement on a truck running 100,000 miles/year at 6 MPG and $3.80/diesel saves approximately $1,057/truck/year [unverified — training knowledge]. Across a 50-truck fleet, that is $52,800 annually from a behavioral and mechanical investment that costs far less. Speed management, tire pressure, aerodynamic spec, and driver coaching are the levers — none of them require a fuel price break.

## How to apply

Build the MPG improvement case before any fuel-spend conversation:

```
MPG lever quantification template (per truck):
  Annual miles:                        ______
  Current fleet average MPG:           ______
  Diesel cost ($/gallon, dated):       $______

  Baseline fuel cost: (miles / MPG) × $/gal = $______

  Lever analysis:
  Speed reduction (65→60 mph):         +0.3–0.5 MPG [unverified — training knowledge]
  Tire inflation program:              +0.2–0.3 MPG [unverified — training knowledge]
  Aerodynamic fairings/skirts:         +0.4–0.7 MPG [unverified — training knowledge]
  Driver coaching / eco-driving:       +0.3–0.5 MPG [unverified — training knowledge]

  Combined potential: 1.0–2.0 MPG improvement
  Annual savings per truck at target:  $______
```

Implementation sequence:
1. Pull MPG by driver from telematics — the spread between best and worst drivers is typically 1.5–2 MPG; coaching brings laggards toward the median.
2. Verify tire inflation compliance — under-inflation is the cheapest MPG leak to fix.
3. Check spec at next trade cycle for aerodynamic packages.
4. Set a fleet MPG floor and report weekly; regression is easier to catch early.

**Do:**
- Report MPG by driver, not just fleet average — driver-level data is the coaching input.
- Separate highway MPG from city/final-mile MPG; they respond to different levers.
- Model the MPG improvement ROI before any spec-upgrade investment; aerodynamic packages have a payback period that depends on the lane profile.

**Don't:**
- Conflate fuel cost per mile with MPG performance — fuel CPM moves with diesel price whether MPG improves or not; report both independently.
- Treat MPG as a compliance metric rather than a margin metric — framing it as margin improvement drives more driver engagement than framing it as policy.

## Edge cases / when the rule does NOT apply

Last-mile delivery operations with high stop density (dozens of stops per day, speeds rarely above 35 mph) are governed by stop density and idle, not highway MPG levers. The improvement investment calculus shifts toward route density and idle management rather than speed and aerodynamics.

## See also

- [`../agents/fleet-maintenance-specialist.md`](../agents/fleet-maintenance-specialist.md) — owns tire program and mechanical MPG-impact items.
- [`../agents/logistics-cost-analyst.md`](../agents/logistics-cost-analyst.md) — owns the MPG scorecard and fuel CPM decomposition.
- [`./idle-time-is-a-fuel-and-engine-cost-not-just-a-habit.md`](./idle-time-is-a-fuel-and-engine-cost-not-just-a-habit.md) — idle reduction and MPG improvement are complementary fuel levers; run them together.

## Provenance

MPG lever ranges are estimates consistent with DOE SmartWay program data and ATRI fleet fuel economy research; all figures marked `[unverified — training knowledge]` and should be validated against current program data.

---

_Last reviewed: 2026-06-05 by `claude`_
