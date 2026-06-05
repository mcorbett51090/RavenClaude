# Module Technology Selection Affects Energy Yield, Not Just Nameplate Wattage

**Status:** Pattern
**Domain:** Solar equipment selection / energy modeling
**Applies to:** `renewable-energy`

---

## Why this exists

Module selection is often made on cost-per-watt (nameplate DC) without modeling the energy yield differential between technologies. Bifacial modules, TOPCon cells, and HJT technology all have different temperature coefficients, bifaciality factors, and low-irradiance performance characteristics that affect actual energy production — independently of nameplate wattage. On a ground-mounted system in a high-irradiance southern US location, the energy yield per dollar of module cost can differ 5–12% between commodity monofacial modules and premium bifacial TOPCon [unverified — training knowledge]. The correct selection criterion is the levelized cost of energy contribution — $/kWh produced over the asset life — not $/W nameplate.

## How to apply

Build the energy yield comparison before finalizing module selection:

```
Module selection energy model (per technology option):
  Module option A: ______  Wp, $______/W, bifacial: yes/no, temp. coefficient: ______%/°C
  Module option B: ______  Wp, $______/W, bifacial: yes/no, temp. coefficient: ______%/°C

  Energy yield inputs (from PVsyst or equivalent model):
    P50 annual yield (kWh/kWp):  A: ______  B: ______
    Bifacial gain (if applicable): A: ______%  B: ______%
    Effective P50 energy (kWh):  A: ______  B: ______

  Module cost contribution to LCOE:
    Module cost ($):             A: ______  B: ______
    Lifetime energy (kWh):       A: ______  B: ______
    Module LCOE contribution:    A: $____/kWh  B: $____/kWh

  Decision: select the module with the lower LCOE contribution, not the lower $/W.
```

Additional factors in the comparison:
- **Temperature coefficient** — high-temperature climates amplify the advantage of lower Pmax/°C modules.
- **Degradation rate** — slower degradation over 25 years compounds into meaningful yield difference; use manufacturer warranty curves.
- **Bankability** — lenders have approved module lists; a premium module that is not on the approved list can delay or block financing.

**Do:**
- Model at least 2 module technology options in every energy model (PVsyst) before procurement.
- Confirm that the selected module is on the lender's approved equipment list before making a procurement commitment.
- Include the module's degradation curve in the 25-year energy model; a module with a better degradation warranty may cost more upfront but yield more over the asset life.

**Don't:**
- Choose module technology purely on $/W nameplate without modeling the yield differential.
- Use generic module specs in the energy model; obtain the PAN file from the manufacturer and use the actual module parameters.

## Edge cases / when the rule does NOT apply

Rooftop residential installations with tight structural space constraints may require high-efficiency modules (HJT, SunPower) on a $/W-per-square-foot basis, not a $/kWh basis — the constraint is physical, not economic. Agrivoltaic systems with intentional shading requirements may prefer lower bifaciality modules to achieve the target crop-light transmission.

## See also

- [`../agents/solar-project-developer.md`](../agents/solar-project-developer.md) — owns the equipment specification and procurement strategy.
- [`../agents/energy-finance-analyst.md`](../agents/energy-finance-analyst.md) — runs the LCOE model that uses the module energy yield inputs.
- [`./a-solar-asset-is-a-25-year-machine-degradation-and-om-are-fi.md`](./a-solar-asset-is-a-25-year-machine-degradation-and-om-are-fi.md) — module degradation over the asset life is the multi-year compounding factor that makes the LCOE comparison the right frame.

## Provenance

Module technology comparison methodology is standard in PV engineering and energy modeling (PVsyst, SAM); the energy yield vs. cost-per-watt distinction is covered in NREL module characterization research and solar project finance guidance.

---

_Last reviewed: 2026-06-05 by `claude`_
