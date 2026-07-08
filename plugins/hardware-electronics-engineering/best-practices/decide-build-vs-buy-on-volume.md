# Decide build-vs-buy on volume

**Rule.** Choose module/dev-board vs custom PCB against volume × cost × size ×
certification × time-to-market — not preference. At low volume a pre-certified module
usually wins (avoids NRE + a whole EMC campaign); at high volume a custom board's
per-unit cost wins. State the crossover.

**Why.** Build-vs-buy is the highest-leverage hardware decision. A custom board at
prototype volume pays NRE and certification to save per-unit cost that doesn't matter
yet; a module at high volume leaves per-unit margin on the table.

**Smell.** Spinning a custom board for a prototype; designing a discrete radio (own
intentional-radiator certification) instead of using a pre-certified module at low volume.

**Cite:** plugin §4.1; the module-vs-custom tree in
`knowledge/module-vs-custom-pcb-decision-tree.md`.
