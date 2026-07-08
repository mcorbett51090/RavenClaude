# Read datasheets at the operating point

**Rule.** A datasheet parameter is valid only at its stated voltage, temperature, and
load. Design to worst-case across the actual operating range with margin — never quote
a "typical @ 25°C" number as if it holds at your real conditions.

**Why.** "Typical" hides the worst-case that will actually bite — a regulator's dropout
at temperature, a part's timing at min voltage, a current rating at max ambient.
Designing to typical is designing for the bench, not the field.

**Smell.** A design margin justified by a typical spec; a parameter used without noting
the voltage/temp/load it was specified at.

**Cite:** plugin §4.4; Step 2 of the `select-components-and-bom` skill; the operating-point
note in `knowledge/eda-fab-and-compliance-2026.md`.
