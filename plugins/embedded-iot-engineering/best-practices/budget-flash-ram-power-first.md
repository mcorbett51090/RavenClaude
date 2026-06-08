# Budget flash, RAM, power, and BOM cost first

On a constrained device the resource budget *is* the design. State the flash, RAM, clock, power, and BOM-cost budget up front and account for every consumer against it — static RAM/stack/heap, flash usage, sleep and active current, duty cycle. A design that defers the memory or power budget to "optimize later" on a part with tens of KB of RAM and a coin cell is a prototype, not a product. Hold headroom for the OTA delta and the field fix.
