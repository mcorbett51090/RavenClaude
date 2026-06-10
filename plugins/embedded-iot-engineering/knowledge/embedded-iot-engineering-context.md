# Embedded & IoT Engineering Benchmarks & Context (2025–2026)

> Orientation for the team. **Every figure and regulatory statement here is `[unverified — training knowledge]`** and varies by geography, segment, and date. Confirm against a current, dated source before any deliverable, and route every professional/legal/regulatory determination to the qualified authority (CLAUDE.md §2, §3 #8).

## Where defensible embedded figures come from

Current draws, timing, memory sizes, and radio ranges are **part- and revision-specific** and drift between datasheet revisions. **Cite the datasheet version + date, mark unsourced figures `[unverified — training knowledge]`, and confirm by bench measurement on the actual board (§3 #7 #8).** The most defensible evidence is a measured current trace and a timing capture on the real hardware — not a datasheet typical value, which is a starting estimate.

## Directional frames (illustrative only — `[unverified — training knowledge]`)

| Area | Directional frame | Must-verify |
|---|---|---|
| Sleep-mode current | Often µA-class; dominates long-life budgets | Datasheet revision + measured (§3 #1 #8) |
| Protocol regimes | LoRa = long-range/low-rate; Wi-Fi = high-rate/high-power | Application data-rate/range need (§3 #6) |
| Memory headroom | Leave margin for stack peaks + dual-bank OTA | Part-specific; measure worst-case stack (§3 #3) |
| Datasheet typical vs max | 'Typical' is not a worst-case guarantee | Design to max/worst-case; measure (§3 #2 #8) |

## Operating rhythm

- **Design-time** — power budget first, then real-time and memory budgets, then protocol and OTA (§3 #1 #2 #3 #5).
- **Bench** — measure current, timing, and RF against the datasheet on the real board/revision (§3 #7 #8).
- **Pre-fielding** — OTA + signed images + rollback verified; certification routed to the lab (§3 #5, §2).

## The standing caution

FCC / CE / UL / radio / safety **certification** is the qualified lab's call (§2 #8) — the team designs to the constraints and routes the sign-off. Datasheet figures are starting estimates, not guarantees: confirm by bench measurement on the specific part and revision (§3 #7 #8). Keep device/telemetry PII (device-to-user linkage, location) out of deliverables and route handling to `ravenclaude-core` `security-reviewer` (§2).
