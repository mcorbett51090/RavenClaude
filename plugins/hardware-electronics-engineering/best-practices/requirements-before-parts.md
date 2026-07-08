# Requirements before parts

**Rule.** Name what the board must do — peripherals, compute, power envelope, size,
environment, interfaces, volume, schedule, certification — before naming the MCU or any
component. The parts are the conclusion of the requirements, not the premise.

**Why.** A part chosen before the requirements becomes a constraint you fight for the
rest of the design. Requirements-first selection produces a board that fits the product
instead of a product bent around a familiar part.

**Smell.** "Let's use <MCU>" before anyone has stated the peripheral/power/environment
needs; a design bent to fit a part someone already liked.

**Cite:** plugin §4.2; Step 1 of the `scope-a-hardware-design` skill.
